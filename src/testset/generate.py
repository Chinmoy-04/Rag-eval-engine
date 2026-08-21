"""Ragas synthetic test set generation with JSON cache and SQLite persistence."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config import DATA_DIR, AppConfig, configure_litellm_env, load_config
from src.ingestion.loader import corpus_fingerprint, load_documents
from src.storage.db import init_db, session_scope
from src.storage.models import Run, RunStatus, TestItem

logger = logging.getLogger("rag_eval")

TESTSETS_DIR = DATA_DIR / "testsets"

# Hand-written "should abstain" items — not produced by Ragas synthesizers.
ABSTAIN_ITEMS: list[dict[str, Any]] = [
    {
        "question": "What is HelixForge's current stock price?",
        "ground_truth_answer": (
            "The provided HelixForge handbook does not include stock price information."
        ),
        "reference_contexts": [],
        "question_type": "abstain",
        "synthesizer_name": "handcrafted_abstain",
    },
    {
        "question": "What is the CEO's annual salary at HelixForge?",
        "ground_truth_answer": (
            "The handbook does not publish executive salary figures."
        ),
        "reference_contexts": [],
        "question_type": "abstain",
        "synthesizer_name": "handcrafted_abstain",
    },
]


def _synthesizer_to_question_type(name: str) -> str:
    lowered = (name or "").lower()
    if "multihop" in lowered or "multi_hop" in lowered or "multi-hop" in lowered:
        return "multi_hop"
    if "abstract" in lowered:
        return "reasoning"
    if "singlehop" in lowered or "single_hop" in lowered or "specific" in lowered:
        return "simple"
    return "simple"


def _cache_key(corpus_name: str, n: int, corpus_sha: str) -> str:
    digest = hashlib.sha256(f"{corpus_name}:{n}:{corpus_sha}".encode()).hexdigest()[:12]
    return f"{corpus_name}_n{n}_{digest}.json"


def _cache_path(corpus_name: str, n: int, corpus_sha: str) -> Path:
    TESTSETS_DIR.mkdir(parents=True, exist_ok=True)
    return TESTSETS_DIR / _cache_key(corpus_name, n, corpus_sha)


def _testset_llm_model(config: AppConfig) -> str:
    """Model for Ragas synthesizers.

    Groq free tier is ~8k TPM. ``openai/gpt-oss-*`` spends that budget on
    reasoning tokens and often returns finish_reason=length. Prefer Qwen with
    reasoning disabled for generation (override via TESTSET_LLM_MODEL).
    """
    import os

    override = (os.getenv("TESTSET_LLM_MODEL") or "").strip()
    if override:
        return override
    if config.llm_provider.value == "groq":
        return "qwen/qwen3.6-27b"
    return config.llm_model


def _build_ragas_llm(config: AppConfig):
    from langchain_openai import ChatOpenAI
    from ragas.llms import LangchainLLMWrapper

    configure_litellm_env(config)
    model = _testset_llm_model(config)
    # Keep prompt+completion under free-tier TPM (~8k) while still finishing.
    max_tokens = 2048
    llm_kwargs: dict[str, Any] = {
        "temperature": 0.3,
        "max_tokens": max_tokens,
    }
    if "qwen" in model.lower():
        llm_kwargs["reasoning_effort"] = "none"
    elif "gpt-oss" in model.lower():
        llm_kwargs["reasoning_effort"] = "low"

    if config.llm_provider.value == "groq":
        if not config.groq_api_key:
            raise ValueError("GROQ_API_KEY is required for test set generation")
        llm = ChatOpenAI(
            model=model,
            api_key=config.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
            **llm_kwargs,
        )
    elif config.llm_provider.value == "openai":
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for test set generation")
        llm = ChatOpenAI(
            model=model.removeprefix("openai/"),
            api_key=config.openai_api_key,
            **{k: v for k, v in llm_kwargs.items() if k != "reasoning_effort"},
        )
    elif config.llm_provider.value == "anthropic":
        from langchain_anthropic import ChatAnthropic

        if not config.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for test set generation")
        llm = ChatAnthropic(
            model=model.removeprefix("anthropic/"),
            api_key=config.anthropic_api_key,
            temperature=0.3,
            max_tokens=max_tokens,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {config.llm_provider}")

    logger.info("Ragas generation LLM model=%s max_tokens=%s", model, max_tokens)
    return LangchainLLMWrapper(llm)


def _build_ragas_embeddings():
    from ragas.embeddings import LangchainEmbeddingsWrapper

    from src.testset.embeddings_lc import LocalOnnxLangchainEmbeddings

    return LangchainEmbeddingsWrapper(LocalOnnxLangchainEmbeddings())


def _llamaindex_docs_to_langchain(documents) -> list:
    from langchain_core.documents import Document as LCDocument

    return [
        LCDocument(page_content=doc.text or "", metadata=dict(doc.metadata or {}))
        for doc in documents
        if (doc.text or "").strip()
    ]


def _normalize_ragas_samples(testset) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for sample in testset.samples:
        eval_sample = sample.eval_sample
        synthesizer = getattr(sample, "synthesizer_name", "") or ""
        question = getattr(eval_sample, "user_input", None) or ""
        answer = getattr(eval_sample, "reference", None) or ""
        contexts = getattr(eval_sample, "reference_contexts", None) or []
        if not question or not answer:
            logger.warning("Skipping incomplete Ragas sample: %s", sample)
            continue
        rows.append(
            {
                "question": question.strip(),
                "ground_truth_answer": answer.strip(),
                "reference_contexts": list(contexts),
                "question_type": _synthesizer_to_question_type(synthesizer),
                "synthesizer_name": synthesizer,
            }
        )
    return rows


def _mix_in_abstain(items: list[dict[str, Any]], n: int) -> list[dict[str, Any]]:
    """Replace trailing slots with abstain questions so the set has a difficulty mix."""
    if n <= 0:
        return items
    abstain_budget = min(len(ABSTAIN_ITEMS), max(1, n // 5))
    keep = max(0, n - abstain_budget)
    mixed = items[:keep]
    mixed.extend(ABSTAIN_ITEMS[:abstain_budget])
    # If Ragas returned fewer than keep, still pad abstain up to n when possible.
    while len(mixed) < n and len(mixed) - keep < len(ABSTAIN_ITEMS):
        mixed.append(ABSTAIN_ITEMS[len(mixed) - keep])
    return mixed[:n]


def _save_cache(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    logger.info("Cached test set to %s", path)


def _load_cache(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _persist_run(
    config: AppConfig,
    *,
    corpus_name: str,
    items: list[dict[str, Any]],
    notes: str,
) -> int:
    init_db(config)
    with session_scope(config) as session:
        run = Run(
            pipeline_config_name="baseline",
            corpus_name=corpus_name,
            num_questions=len(items),
            status=RunStatus.READY.value,
            notes=notes,
        )
        session.add(run)
        session.flush()
        for item in items:
            session.add(
                TestItem(
                    run_id=run.id,
                    question=item["question"],
                    ground_truth_answer=item["ground_truth_answer"],
                    reference_contexts=item.get("reference_contexts") or [],
                    question_type=item.get("question_type") or "simple",
                )
            )
        session.flush()
        run_id = int(run.id)
    logger.info("Persisted run_id=%s with %d test items", run_id, len(items))
    return run_id


def generate_with_ragas(config: AppConfig, n: int) -> list[dict[str, Any]]:
    """Call Ragas TestsetGenerator against the local corpus."""
    from src.ragas_compat import ensure_ragas_imports

    ensure_ragas_imports()
    from ragas.run_config import RunConfig
    from ragas.testset import TestsetGenerator
    from ragas.testset.synthesizers.multi_hop.specific import (
        MultiHopSpecificQuerySynthesizer,
    )
    from ragas.testset.synthesizers.single_hop.specific import (
        SingleHopSpecificQuerySynthesizer,
    )

    documents = load_documents()
    lc_docs = _llamaindex_docs_to_langchain(documents)
    if not lc_docs:
        raise RuntimeError("No documents loaded for test set generation")

    # Generate a few extras so abstain mix / dropouts still leave ~n usable items.
    generate_n = max(n, n - max(1, n // 5) + 2)

    llm = _build_ragas_llm(config)
    embeddings = _build_ragas_embeddings()
    generator = TestsetGenerator(llm=llm, embedding_model=embeddings)
    # Prefer specific synthesizers; abstract multi-hop is flakier on small free-tier models.
    query_distribution = [
        (SingleHopSpecificQuerySynthesizer(llm=llm), 0.7),
        (MultiHopSpecificQuerySynthesizer(llm=llm), 0.3),
    ]
    # Serialize LLM calls: free Groq TPM is easy to blow with concurrent workers.
    run_config = RunConfig(max_workers=1, max_retries=5, max_wait=90, timeout=300)

    logger.info(
        "Generating ~%d synthetic questions via Ragas (requested n=%d, distribution=%s)",
        generate_n,
        n,
        [(type(s).__name__, w) for s, w in query_distribution],
    )
    testset = generator.generate_with_langchain_docs(
        documents=lc_docs,
        testset_size=generate_n,
        query_distribution=query_distribution,
        run_config=run_config,
        # One failed transform should not abort the whole Phase 5 smoke run.
        raise_exceptions=False,
    )
    return _normalize_ragas_samples(testset)


def run_testset_generation(
    config: AppConfig | None = None,
    *,
    n: int = 10,
    corpus_name: str = "default",
    force: bool = False,
) -> int:
    """Generate or reload a cached test set, persist TestItems, return run_id."""
    if config is None:
        config = load_config()
    if n < 1:
        raise ValueError("--n must be >= 1")

    corpus_sha = corpus_fingerprint()
    cache_path = _cache_path(corpus_name, n, corpus_sha)
    cached = None if force else _load_cache(cache_path)

    if cached and cached.get("items"):
        items = cached["items"]
        logger.info("Loaded %d cached questions from %s", len(items), cache_path)
        notes = f"Loaded from cache {cache_path.name}"
    else:
        raw = generate_with_ragas(config, n=n)
        if not raw:
            raise RuntimeError(
                "Ragas returned no usable questions. Try again, raise max_tokens, "
                "or switch LLM_MODEL."
            )
        items = _mix_in_abstain(raw, n)
        payload = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "corpus_name": corpus_name,
            "corpus_sha256": corpus_sha,
            "n": n,
            "llm_provider": config.llm_provider.value,
            "llm_model": config.llm_model,
            "testset_llm_model": _testset_llm_model(config),
            "items": items,
        }
        _save_cache(cache_path, payload)
        notes = f"Generated with Ragas; cached as {cache_path.name}"

    return _persist_run(config, corpus_name=corpus_name, items=items, notes=notes)

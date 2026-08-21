"""Ragas metric wrappers for scoring RAG answers."""

from __future__ import annotations

import logging
from typing import Any

from src.config import AppConfig
from src.evaluation.ragas_clients import build_ragas_embeddings, build_ragas_llm

logger = logging.getLogger("rag_eval")

METRIC_COLUMNS = (
    "faithfulness",
    "answer_relevancy",
    "context_precision",
    "context_recall",
)


def score_rag_samples(
    config: AppConfig,
    samples: list[dict[str, Any]],
    *,
    max_workers: int = 2,
) -> list[dict[str, Any]]:
    """Score RAG outputs with core Ragas metrics.

    Each input sample needs:
      - question (str)
      - answer (str) — pipeline response
      - contexts (list[str]) — retrieved chunks
      - ground_truth (str) — reference answer

    Returns one dict per sample with metric floats (or None on failure).
    """
    from src.ragas_compat import ensure_ragas_imports

    ensure_ragas_imports()
    from ragas import evaluate
    from ragas.dataset_schema import EvaluationDataset, SingleTurnSample
    from ragas.metrics import context_precision, context_recall, faithfulness
    from ragas.metrics._answer_relevance import AnswerRelevancy
    from ragas.run_config import RunConfig

    if not samples:
        return []

    dataset = EvaluationDataset(
        samples=[
            SingleTurnSample(
                user_input=s["question"],
                response=s.get("answer") or "",
                retrieved_contexts=list(s.get("contexts") or []),
                reference=s.get("ground_truth") or "",
            )
            for s in samples
        ]
    )

    llm = build_ragas_llm(config, temperature=0.0)
    embeddings = build_ragas_embeddings()
    # Groq rejects OpenAI-style n>1; keep answer_relevancy at strictness=1.
    answer_relevancy = AnswerRelevancy(strictness=1)
    run_config = RunConfig(
        max_workers=max(1, max_workers),
        max_retries=5,
        max_wait=90,
        timeout=300,
    )

    logger.info("Scoring %d samples with Ragas (workers=%d)", len(samples), max_workers)
    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        llm=llm,
        embeddings=embeddings,
        run_config=run_config,
        raise_exceptions=False,
        show_progress=True,
    )

    # EvaluationResult behaves like a table; convert to pandas for stable column access.
    try:
        frame = result.to_pandas()
    except Exception:
        frame = None

    scored: list[dict[str, Any]] = []
    for i in range(len(samples)):
        row: dict[str, Any] = {name: None for name in METRIC_COLUMNS}
        if frame is not None and i < len(frame):
            for name in METRIC_COLUMNS:
                if name in frame.columns:
                    val = frame.iloc[i][name]
                    try:
                        if val is not None and str(val) != "nan":
                            row[name] = float(val)
                    except (TypeError, ValueError):
                        row[name] = None
        scored.append(row)
    return scored

"""Configurable RAG pipeline: retrieve chunks, then generate an answer."""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field

from llama_index.core.schema import NodeWithScore

from src.config import AppConfig, load_config
from src.ingestion.indexer import query_index
from src.llm import generate_completion
from src.rag_pipeline.configs import PipelineConfig, get_pipeline_config

logger = logging.getLogger("rag_eval")

_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "how",
        "i",
        "in",
        "is",
        "it",
        "me",
        "my",
        "of",
        "on",
        "or",
        "our",
        "should",
        "the",
        "to",
        "what",
        "when",
        "where",
        "which",
        "who",
        "with",
    }
)


@dataclass
class RAGResponse:
    """What every pipeline config must return so evaluation can score it."""

    answer: str
    retrieved_contexts: list[str]
    latency_ms: float
    sources: list[str] = field(default_factory=list)
    pipeline_config_name: str = "baseline"


def _format_context(chunks: list[str]) -> str:
    parts: list[str] = []
    for i, chunk in enumerate(chunks, start=1):
        parts.append(f"[{i}]\n{chunk.strip()}")
    return "\n\n".join(parts)


# gpt-oss and similar models sometimes emit browsing-style inline citations
# (e.g. 【2†L9-L12】) when context is numbered. Sources are shown in the UI separately.
_INLINE_CITATION_RE = re.compile(r"【\d+†[^】]*】|\[\d+†[^\]]*\]")


def _strip_inline_citations(text: str) -> str:
    cleaned = _INLINE_CITATION_RE.sub("", text)
    cleaned = re.sub(r"[ \t]+([,.;:!?])", r"\1", cleaned)
    return re.sub(r"  +", " ", cleaned).strip()


def keyword_query(question: str) -> str:
    """Drop stopwords so retrieval can match table/CSV terms more directly."""
    tokens = re.findall(r"[A-Za-z0-9_./-]+", question)
    kept = [tok for tok in tokens if tok.lower() not in _STOPWORDS and len(tok) > 1]
    return " ".join(kept)


def _node_key(hit: NodeWithScore) -> str:
    node = hit.node
    meta = node.metadata or {}
    name = str(meta.get("file_name") or meta.get("filename") or "")
    text = (node.get_content() or "")[:160]
    return f"{name}::{text}"


def _merge_hits(hits: list[NodeWithScore], limit: int) -> list[NodeWithScore]:
    ranked = sorted(hits, key=lambda h: float(h.score or 0.0), reverse=True)
    seen: set[str] = set()
    merged: list[NodeWithScore] = []
    for hit in ranked:
        key = _node_key(hit)
        if key in seen:
            continue
        seen.add(key)
        merged.append(hit)
        if len(merged) >= limit:
            break
    return merged


def _retrieve(question: str, config: AppConfig, k: int) -> list[NodeWithScore]:
    return query_index(question, config=config, top_k=k)


def run_pipeline(
    question: str,
    config: AppConfig | None = None,
    pipeline_config: PipelineConfig | str | None = None,
) -> RAGResponse:
    """Retrieve top-k chunks and ask the LLM to answer from that context only.

    Latency includes retrieval + generation so later eval can compare pipelines
    on speed as well as quality.
    """
    if config is None:
        config = load_config()
    if pipeline_config is None:
        pipe = get_pipeline_config("baseline")
    elif isinstance(pipeline_config, str):
        pipe = get_pipeline_config(pipeline_config)
    else:
        pipe = pipeline_config

    started = time.perf_counter()
    fetch_k = pipe.retrieve_k or pipe.top_k
    hits = _retrieve(question, config, fetch_k)
    if pipe.expand_query:
        alt = keyword_query(question)
        if alt and alt.lower() != question.strip().lower():
            extra = _retrieve(alt, config, fetch_k)
            hits = _merge_hits([*hits, *extra], pipe.top_k)
            logger.info(
                "Pipeline %s merged expanded retrieval (alt=%r) -> %d chunks",
                pipe.name,
                alt[:80],
                len(hits),
            )
    else:
        hits = hits[: pipe.top_k]

    contexts: list[str] = []
    sources: list[str] = []
    for hit in hits:
        node = hit.node
        text = node.get_content().strip()
        if pipe.context_char_limit is not None:
            text = text[: pipe.context_char_limit]
        contexts.append(text)
        meta = node.metadata or {}
        sources.append(str(meta.get("file_name") or meta.get("filename") or "unknown"))

    messages = [
        {"role": "system", "content": pipe.system_prompt},
        {
            "role": "user",
            "content": pipe.user_prompt_template.format(
                context=_format_context(contexts) or "(no context retrieved)",
                question=question.strip(),
            ),
        },
    ]
    answer = _strip_inline_citations(
        generate_completion(
            messages,
            config,
            temperature=pipe.temperature,
            max_tokens=pipe.max_tokens,
        )
    )
    latency_ms = (time.perf_counter() - started) * 1000
    logger.info(
        "Pipeline %s answered in %.0f ms (%d contexts)",
        pipe.name,
        latency_ms,
        len(contexts),
    )
    return RAGResponse(
        answer=answer,
        retrieved_contexts=contexts,
        latency_ms=latency_ms,
        sources=sources,
        pipeline_config_name=pipe.name,
    )

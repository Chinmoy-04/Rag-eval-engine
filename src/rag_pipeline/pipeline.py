"""Configurable RAG pipeline: retrieve chunks, then generate an answer."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

from src.config import AppConfig, load_config
from src.ingestion.indexer import query_index
from src.llm import generate_completion
from src.rag_pipeline.configs import PipelineConfig, get_pipeline_config

logger = logging.getLogger("rag_eval")


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
    hits = query_index(question, config=config, top_k=pipe.top_k)
    contexts: list[str] = []
    sources: list[str] = []
    for hit in hits:
        node = hit.node
        contexts.append(node.get_content().strip())
        meta = node.metadata or {}
        sources.append(str(meta.get("file_name") or meta.get("filename") or "unknown"))

    messages = [
        {"role": "system", "content": pipe.system_prompt},
        {
            "role": "user",
            "content": pipe.user_prompt_template.format(
                context=_format_context(contexts),
                question=question.strip(),
            ),
        },
    ]
    answer = generate_completion(
        messages,
        config,
        temperature=pipe.temperature,
        max_tokens=pipe.max_tokens,
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

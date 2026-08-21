"""Concurrent, rate-limited RAG answer generation for evaluation batches."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from src.config import AppConfig
from src.rag_pipeline.pipeline import RAGResponse, run_pipeline

logger = logging.getLogger("rag_eval")


async def generate_answers_batch(
    config: AppConfig,
    items: list[dict[str, Any]],
    *,
    pipeline_config: str,
    concurrency: int = 2,
) -> list[dict[str, Any]]:
    """Run the RAG pipeline over test items with a concurrency cap.

    Each ``item`` must include ``id`` and ``question``. Returns the same list
    enriched with answer / contexts / latency_ms / error.
    """
    sem = asyncio.Semaphore(max(1, concurrency))

    async def _one(item: dict[str, Any]) -> dict[str, Any]:
        async with sem:
            question = item["question"]
            try:
                result: RAGResponse = await asyncio.to_thread(
                    run_pipeline,
                    question,
                    config,
                    pipeline_config,
                )
                # Small pause so Groq free-tier TPM can recover between items.
                await asyncio.sleep(1.5)
                return {
                    **item,
                    "answer": result.answer,
                    "contexts": result.retrieved_contexts,
                    "sources": result.sources,
                    "latency_ms": result.latency_ms,
                    "error": None,
                }
            except Exception as exc:
                logger.exception("RAG failed for test_item_id=%s", item.get("id"))
                await asyncio.sleep(2.0)
                return {
                    **item,
                    "answer": "",
                    "contexts": [],
                    "sources": [],
                    "latency_ms": None,
                    "error": str(exc),
                }

    logger.info(
        "Generating answers for %d items (pipeline=%s, concurrency=%d)",
        len(items),
        pipeline_config,
        concurrency,
    )
    return list(await asyncio.gather(*[_one(item) for item in items]))


def generate_answers_batch_sync(
    config: AppConfig,
    items: list[dict[str, Any]],
    *,
    pipeline_config: str,
    concurrency: int = 2,
) -> list[dict[str, Any]]:
    """Sync wrapper for CLI / non-async callers."""
    return asyncio.run(
        generate_answers_batch(
            config,
            items,
            pipeline_config=pipeline_config,
            concurrency=concurrency,
        )
    )

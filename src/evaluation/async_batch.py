"""Concurrent, rate-limited RAG answer generation for evaluation batches."""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

from src.config import AppConfig
from src.llm import _is_rate_limit
from src.rag_pipeline.pipeline import RAGResponse, run_pipeline

logger = logging.getLogger("rag_eval")

# Groq free tier needs breathing room between sequential RAG calls.
_INTER_ITEM_SLEEP_S = 2.5
_TPD_RETRY_RE = re.compile(
    r"try again in\s+(?:(\d+)m)?(?:(\d+(?:\.\d+)?)s)?",
    re.IGNORECASE,
)


def _rate_limit_wait_seconds(exc: BaseException, attempt: int) -> int:
    """Parse Groq retry hints; fall back to short exponential backoff."""
    match = _TPD_RETRY_RE.search(str(exc))
    if match:
        minutes = int(match.group(1) or 0)
        seconds = float(match.group(2) or 0)
        parsed = int(minutes * 60 + seconds) + 5
        return min(1200, max(parsed, 15))
    return min(90, 10 * attempt)


def _is_transient_rag_error(exc: BaseException) -> bool:
    msg = str(exc).lower()
    return _is_rate_limit(exc) or (
        "could not connect to tenant" in msg
        or "connection was forcibly closed" in msg
        or "internalservererror" in type(exc).__name__.lower()
        or ("connection" in msg and "chroma" in msg)
    )


async def generate_answers_batch(
    config: AppConfig,
    items: list[dict[str, Any]],
    *,
    pipeline_config: str,
    concurrency: int = 1,
) -> list[dict[str, Any]]:
    """Run the RAG pipeline over test items with a concurrency cap.

    Each ``item`` must include ``id`` and ``question``. Returns the same list
    enriched with answer / contexts / latency_ms / error.
    """
    sem = asyncio.Semaphore(max(1, concurrency))
    max_attempts = max(1, config.eval_max_retries)

    async def _one(item: dict[str, Any]) -> dict[str, Any]:
        async with sem:
            question = item["question"]
            last_exc: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    result: RAGResponse = await asyncio.to_thread(
                        run_pipeline,
                        question,
                        config,
                        pipeline_config,
                    )
                    await asyncio.sleep(_INTER_ITEM_SLEEP_S)
                    return {
                        **item,
                        "answer": result.answer,
                        "contexts": result.retrieved_contexts,
                        "sources": result.sources,
                        "latency_ms": result.latency_ms,
                        "error": None,
                    }
                except Exception as exc:
                    last_exc = exc
                    if attempt < max_attempts and _is_transient_rag_error(exc):
                        wait_s = _rate_limit_wait_seconds(exc, attempt)
                        logger.warning(
                            "RAG retry test_item_id=%s attempt=%d/%d wait=%ds: %s",
                            item.get("id"),
                            attempt,
                            max_attempts,
                            wait_s,
                            exc,
                        )
                        await asyncio.sleep(wait_s)
                        continue
                    logger.exception(
                        "RAG failed for test_item_id=%s after %d attempts",
                        item.get("id"),
                        attempt,
                    )
                    await asyncio.sleep(_INTER_ITEM_SLEEP_S)
                    break

            return {
                **item,
                "answer": "",
                "contexts": [],
                "sources": [],
                "latency_ms": None,
                "error": str(last_exc) if last_exc is not None else "Unknown RAG error",
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

"""Full batch evaluation orchestration: RAG → Ragas → SQLite."""

from __future__ import annotations

import logging
from typing import Any

from sqlmodel import col, select

from src.config import AppConfig, load_config
from src.evaluation.async_batch import generate_answers_batch_sync
from src.evaluation.metrics import METRIC_COLUMNS, score_rag_samples
from src.storage.db import init_db, session_scope
from src.storage.models import EvalResult, Run, RunStatus, TestItem

logger = logging.getLogger("rag_eval")


def run_evaluation(
    config: AppConfig | None = None,
    *,
    run_id: int,
    pipeline_config: str = "baseline",
    concurrency: int | None = None,
) -> dict[str, Any]:
    """Evaluate all TestItems for ``run_id`` and persist EvalResult rows.

    Returns a summary dict with averages and counts.
    """
    if config is None:
        config = load_config()
    init_db(config)
    # Keep concurrency low for Groq free-tier TPM during Phase 6.
    conc = concurrency if concurrency is not None else min(2, config.eval_concurrency)

    with session_scope(config) as session:
        run = session.get(Run, run_id)
        if run is None:
            raise ValueError(f"Run id={run_id} not found. Generate a test set first.")
        items = list(
            session.exec(select(TestItem).where(TestItem.run_id == run_id)).all()
        )
        if not items:
            raise ValueError(f"Run id={run_id} has no test items.")

        payloads = [
            {
                "id": int(item.id),
                "question": item.question,
                "ground_truth": item.ground_truth_answer,
                "question_type": item.question_type or "simple",
            }
            for item in items
        ]
        item_ids = [p["id"] for p in payloads]
        run.status = RunStatus.EVALUATING.value
        run.pipeline_config_name = pipeline_config

        existing = list(
            session.exec(
                select(EvalResult).where(col(EvalResult.test_item_id).in_(item_ids))
            ).all()
        )
        for row in existing:
            session.delete(row)

    logger.info(
        "Evaluating run_id=%d pipeline=%s items=%d concurrency=%d",
        run_id,
        pipeline_config,
        len(payloads),
        conc,
    )

    try:
        answered = generate_answers_batch_sync(
            config,
            payloads,
            pipeline_config=pipeline_config,
            concurrency=conc,
        )

        ok_indices = [i for i, row in enumerate(answered) if not row.get("error")]
        to_score = [
            {
                "question": answered[i]["question"],
                "answer": answered[i].get("answer") or "",
                "contexts": answered[i].get("contexts") or [],
                "ground_truth": answered[i].get("ground_truth") or "",
            }
            for i in ok_indices
        ]
        scores_by_index: dict[int, dict[str, Any]] = {}
        if to_score:
            scored = score_rag_samples(
                config, to_score, max_workers=min(2, max(1, conc))
            )
            for pos, metrics in zip(ok_indices, scored):
                scores_by_index[pos] = metrics

        metric_sums = {name: 0.0 for name in METRIC_COLUMNS}
        metric_counts = {name: 0 for name in METRIC_COLUMNS}

        with session_scope(config) as session:
            run = session.get(Run, run_id)
            if run is None:
                raise ValueError(f"Run id={run_id} disappeared during evaluation.")

            for i, row in enumerate(answered):
                metrics = scores_by_index.get(i, {})
                session.add(
                    EvalResult(
                        test_item_id=row["id"],
                        generated_answer=row.get("answer") or None,
                        retrieved_contexts=list(row.get("contexts") or []),
                        faithfulness=metrics.get("faithfulness"),
                        answer_relevancy=metrics.get("answer_relevancy"),
                        context_precision=metrics.get("context_precision"),
                        context_recall=metrics.get("context_recall"),
                        latency_ms=row.get("latency_ms"),
                        error=row.get("error"),
                    )
                )
                for name in METRIC_COLUMNS:
                    val = metrics.get(name)
                    if isinstance(val, (int, float)):
                        metric_sums[name] += float(val)
                        metric_counts[name] += 1

            run.status = RunStatus.COMPLETED.value
            run.pipeline_config_name = pipeline_config
            note = (
                f"Evaluated pipeline={pipeline_config}; "
                f"{len(answered)} results, "
                f"{sum(1 for r in answered if r.get('error'))} RAG errors"
            )
            run.notes = f"{run.notes} | {note}" if run.notes else note

        averages = {
            name: (metric_sums[name] / metric_counts[name])
            if metric_counts[name]
            else None
            for name in METRIC_COLUMNS
        }
        summary = {
            "run_id": run_id,
            "pipeline": pipeline_config,
            "num_items": len(answered),
            "num_errors": sum(1 for r in answered if r.get("error")),
            "averages": averages,
        }
        logger.info("Evaluation complete: %s", summary)
        return summary

    except Exception:
        with session_scope(config) as session:
            run = session.get(Run, run_id)
            if run is not None:
                run.status = RunStatus.FAILED.value
        raise

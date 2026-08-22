"""Full batch evaluation orchestration: RAG → Ragas → SQLite."""

from __future__ import annotations

import logging
from typing import Any

from sqlmodel import col, select

from src.config import AppConfig, EvalLLMProvider, load_config
from src.evaluation.async_batch import generate_answers_batch_sync
from src.evaluation.metrics import METRIC_COLUMNS, score_rag_samples
from src.rag_pipeline.configs import get_pipeline_config
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
    pipe = get_pipeline_config(pipeline_config)
    pipeline_config = pipe.name
    init_db(config)
    # Default to 1 worker — Groq free-tier TPM and Chroma are happier sequentially.
    conc = concurrency if concurrency is not None else min(1, config.eval_concurrency)

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
                select(EvalResult).where(
                    col(EvalResult.test_item_id).in_(item_ids),
                    EvalResult.pipeline_config_name == pipeline_config,
                )
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
            judge_workers = min(2, max(1, conc))
            if config.eval_llm_provider == EvalLLMProvider.OLLAMA:
                judge_workers = 1
            scored = score_rag_samples(
                config, to_score, max_workers=judge_workers
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
                        pipeline_config_name=pipeline_config,
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


def _latest_eval_results(results: list[EvalResult]) -> list[EvalResult]:
    """Keep the newest EvalResult per (test_item_id, pipeline_config_name)."""
    latest: dict[tuple[int, str], EvalResult] = {}
    for row in results:
        if row.test_item_id is None:
            continue
        key = (int(row.test_item_id), row.pipeline_config_name or "baseline")
        prev = latest.get(key)
        if prev is None or (row.id or 0) > (prev.id or 0):
            latest[key] = row
    return list(latest.values())


def summarize_pipeline_scores(
    config: AppConfig | None = None,
    *,
    run_id: int,
) -> list[dict[str, Any]]:
    """Average Ragas scores per pipeline for a test-set run."""
    if config is None:
        config = load_config()
    init_db(config)

    with session_scope(config) as session:
        items = list(
            session.exec(select(TestItem).where(TestItem.run_id == run_id)).all()
        )
        item_ids = [int(item.id) for item in items if item.id is not None]
        if not item_ids:
            return []
        results = _latest_eval_results(
            list(
                session.exec(
                    select(EvalResult).where(col(EvalResult.test_item_id).in_(item_ids))
                ).all()
            )
        )

        buckets: dict[str, dict[str, Any]] = {}
        for row in results:
            name = row.pipeline_config_name or "baseline"
            bucket = buckets.setdefault(
                name,
                {
                    "pipeline": name,
                    "num_results": 0,
                    "num_errors": 0,
                    "sums": {m: 0.0 for m in METRIC_COLUMNS},
                    "counts": {m: 0 for m in METRIC_COLUMNS},
                    "latency_sum": 0.0,
                    "latency_n": 0,
                },
            )
            bucket["num_results"] += 1
            if row.error:
                bucket["num_errors"] += 1
            for metric in METRIC_COLUMNS:
                val = getattr(row, metric)
                if isinstance(val, (int, float)):
                    bucket["sums"][metric] += float(val)
                    bucket["counts"][metric] += 1
            if isinstance(row.latency_ms, (int, float)):
                bucket["latency_sum"] += float(row.latency_ms)
                bucket["latency_n"] += 1

    order = ("degraded", "baseline", "optimized")
    summaries: list[dict[str, Any]] = []

    def _to_summary(bucket: dict[str, Any]) -> dict[str, Any]:
        averages = {
            m: (bucket["sums"][m] / bucket["counts"][m]) if bucket["counts"][m] else None
            for m in METRIC_COLUMNS
        }
        avg_latency = (
            bucket["latency_sum"] / bucket["latency_n"] if bucket["latency_n"] else None
        )
        return {
            "pipeline": bucket["pipeline"],
            "num_results": bucket["num_results"],
            "num_errors": bucket["num_errors"],
            "averages": averages,
            "avg_latency_ms": avg_latency,
        }

    for name in order:
        if name in buckets:
            summaries.append(_to_summary(buckets.pop(name)))
    summaries.extend(_to_summary(bucket) for bucket in buckets.values())
    return summaries


def list_runs_overview(config: AppConfig | None = None) -> list[dict[str, Any]]:
    """Runs with pipeline coverage and headline metric for the dashboard."""
    if config is None:
        config = load_config()
    init_db(config)

    with session_scope(config) as session:
        runs = list(session.exec(select(Run).order_by(col(Run.id).desc())).all())
        if not runs:
            return []

        run_payloads: list[dict[str, Any]] = []
        all_item_ids: list[int] = []
        items_by_run: dict[int, list[int]] = {}
        for run in runs:
            if run.id is None:
                continue
            run_id = int(run.id)
            item_ids = [
                int(item.id)
                for item in session.exec(
                    select(TestItem).where(TestItem.run_id == run.id)
                ).all()
                if item.id is not None
            ]
            items_by_run[run_id] = item_ids
            all_item_ids.extend(item_ids)
            run_payloads.append(
                {
                    "run_id": run_id,
                    "created_at": run.created_at,
                    "corpus_name": run.corpus_name,
                    "num_questions": run.num_questions,
                    "status": run.status,
                    "notes": run.notes,
                }
            )

        results = _latest_eval_results(
            list(
                session.exec(
                    select(EvalResult).where(col(EvalResult.test_item_id).in_(all_item_ids))
                ).all()
            )
            if all_item_ids
            else []
        )
        result_rows = [
            {
                "test_item_id": int(row.test_item_id),
                "pipeline": row.pipeline_config_name or "baseline",
                "error": bool(row.error),
                "faithfulness": row.faithfulness,
            }
            for row in results
            if row.test_item_id is not None
        ]

    results_by_item: dict[int, list[dict[str, Any]]] = {}
    for row in result_rows:
        results_by_item.setdefault(row["test_item_id"], []).append(row)

    overview: list[dict[str, Any]] = []
    for payload in run_payloads:
        run_id = int(payload["run_id"])
        item_ids = items_by_run.get(run_id, [])
        pipelines: set[str] = set()
        errors = 0
        faith_vals: list[float] = []
        for item_id in item_ids:
            for row in results_by_item.get(item_id, []):
                pipelines.add(row["pipeline"])
                if row["error"]:
                    errors += 1
                if isinstance(row["faithfulness"], (int, float)):
                    faith_vals.append(float(row["faithfulness"]))

        overview.append(
            {
                **payload,
                "pipelines": sorted(pipelines),
                "eval_errors": errors,
                "avg_faithfulness": (
                    sum(faith_vals) / len(faith_vals) if faith_vals else None
                ),
            }
        )
    return overview


def fetch_item_breakdown(
    config: AppConfig | None = None,
    *,
    run_id: int,
) -> list[dict[str, Any]]:
    """Per-question scores for each pipeline (latest result per item)."""
    if config is None:
        config = load_config()
    init_db(config)

    with session_scope(config) as session:
        items = list(
            session.exec(select(TestItem).where(TestItem.run_id == run_id)).all()
        )
        item_ids = [int(item.id) for item in items if item.id is not None]
        if not item_ids:
            return []

        results = _latest_eval_results(
            list(
                session.exec(
                    select(EvalResult).where(col(EvalResult.test_item_id).in_(item_ids))
                ).all()
            )
        )

        by_item: dict[int, dict[str, EvalResult]] = {}
        for row in results:
            by_item.setdefault(int(row.test_item_id), {})[
                row.pipeline_config_name or "baseline"
            ] = row

        rows: list[dict[str, Any]] = []
        for item in items:
            if item.id is None:
                continue
            per_pipe = by_item.get(int(item.id), {})
            entry: dict[str, Any] = {
                "question": item.question,
                "type": item.question_type,
            }
            for pipe in ("degraded", "baseline", "optimized"):
                result = per_pipe.get(pipe)
                if result is None:
                    entry[f"{pipe}_faithfulness"] = None
                    entry[f"{pipe}_error"] = None
                    continue
                entry[f"{pipe}_faithfulness"] = result.faithfulness
                entry[f"{pipe}_error"] = bool(result.error)
            rows.append(entry)
        return rows

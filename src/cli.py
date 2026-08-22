"""CLI entry point for the RAG Evaluation Engine."""

from __future__ import annotations

import subprocess
import sys

import typer

from src.config import PROJECT_ROOT, load_config, setup_logging

app = typer.Typer(
    name="rag-eval",
    help="High-throughput RAG evaluation engine.",
    no_args_is_help=True,
)

logger = setup_logging()


def _configure_stdio() -> None:
    """Avoid UnicodeEncodeError on Windows cp1252 consoles."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


def echo(text: str = "") -> None:
    """Print text, replacing characters the console cannot encode."""
    try:
        typer.echo(text)
    except UnicodeEncodeError:
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        typer.echo(text.encode(encoding, errors="replace").decode(encoding))


@app.command("init-db")
def init_db_cmd() -> None:
    """Create SQLite tables for runs, test items, and eval results."""
    from sqlmodel import select

    from src.storage.db import init_db, session_scope
    from src.storage.models import EvalResult, Run, RunStatus, TestItem

    config = load_config()
    init_db(config)
    with session_scope(config) as session:
        run = Run(
            pipeline_config_name="baseline",
            corpus_name="helixforge",
            num_questions=1,
            status=RunStatus.READY.value,
            notes="Phase 4 schema smoke insert",
        )
        session.add(run)
        session.flush()
        item = TestItem(
            run_id=run.id,
            question="How much PTO do new employees accrue?",
            ground_truth_answer="18 days per fiscal year in the first two years.",
            reference_contexts=["Full-time employees accrue 18 days of PTO..."],
            question_type="simple",
        )
        session.add(item)
        session.flush()
        result = EvalResult(
            test_item_id=item.id,
            generated_answer="18 days",
            retrieved_contexts=["...accrue 18 days of PTO..."],
            faithfulness=1.0,
            answer_relevancy=1.0,
            latency_ms=12.5,
        )
        session.add(result)
        session.flush()
        run_id, item_id, result_id = run.id, item.id, result.id

    with session_scope(config) as session:
        loaded = session.exec(select(Run).where(Run.id == run_id)).one()
        items = session.exec(select(TestItem).where(TestItem.run_id == run_id)).all()
        scores = session.exec(
            select(EvalResult).where(EvalResult.test_item_id == item_id)
        ).all()
        echo(
            f"OK  run_id={loaded.id} status={loaded.status} "
            f"items={len(items)} results={len(scores)} result_id={result_id}"
        )
        # Clean up the smoke rows so the DB stays empty for Phase 5.
        for row in scores:
            session.delete(row)
        for row in items:
            session.delete(row)
        session.delete(loaded)

    logger.info("Database initialized and round-trip verified.")


@app.command()
def ingest(
    rebuild: bool = typer.Option(
        False, "--rebuild", help="Drop and rebuild the vector index."
    ),
) -> None:
    """Ingest documents from data/raw_docs/ and build the Chroma index."""
    from src.ingestion.indexer import run_ingestion

    config = load_config()
    logger.info("Starting ingestion (rebuild=%s)", rebuild)
    result = run_ingestion(config, rebuild=rebuild)
    logger.info(
        "Ingestion %s: %s vectors, embedding=%s",
        result.get("status"),
        result.get("num_vectors"),
        result.get("embedding"),
    )


@app.command()
def query(
    question: str = typer.Argument(..., help="Natural-language question to retrieve for."),
    top_k: int | None = typer.Option(None, "--top-k", help="Number of chunks to return."),
) -> None:
    """Retrieve similar chunks from the index (retrieval only, no LLM)."""
    from src.ingestion.indexer import query_index

    config = load_config()
    hits = query_index(question, config=config, top_k=top_k)
    if not hits:
        typer.echo("No results. Run ingest first: uv run python -m src.cli ingest")
        raise typer.Exit(code=1)

    for i, hit in enumerate(hits, start=1):
        score = getattr(hit, "score", None)
        node = hit.node
        meta = node.metadata or {}
        source = meta.get("file_name") or meta.get("filename", "unknown")
        if score is not None:
            echo(f"[{i}] score={score:.4f} source={source}")
        else:
            echo(f"[{i}] source={source}")
        echo(node.get_content().strip())
        echo("")


@app.command()
def ask(
    question: str = typer.Argument(..., help="Question to answer from the corpus."),
    pipeline_config: str = typer.Option(
        "baseline",
        "--pipeline-config",
        help="Named RAG config: baseline, degraded, or optimized.",
    ),
    show_contexts: bool = typer.Option(
        False, "--show-contexts", help="Print retrieved chunks after the answer."
    ),
) -> None:
    """Run retrieval + LLM generation (full RAG)."""
    from src.rag_pipeline.pipeline import run_pipeline

    config = load_config()
    try:
        result = run_pipeline(question, config=config, pipeline_config=pipeline_config)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    echo(f"pipeline={result.pipeline_config_name}  latency_ms={result.latency_ms:.0f}")
    if result.sources:
        echo("sources: " + ", ".join(result.sources))
    echo("")
    echo(result.answer)
    if show_contexts:
        echo("\n--- retrieved contexts ---")
        for i, chunk in enumerate(result.retrieved_contexts, start=1):
            echo(f"\n[{i}]\n{chunk}")


@app.command()
def smoke() -> None:
    """Run a few hardcoded questions and check that known facts appear in the answer."""
    from src.rag_pipeline.smoke import run_smoke

    config = load_config()
    try:
        results = run_smoke(config)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    failures = 0
    for row in results:
        status = "PASS" if row["passed"] else "FAIL"
        if not row["passed"]:
            failures += 1
        echo(f"[{status}] {row['question']}")
        echo(f"  expected to mention: {', '.join(row['must_contain'])}")
        echo(f"  latency_ms={row['latency_ms']:.0f}  sources={', '.join(row['sources'])}")
        echo(f"  answer: {row['answer']}")
        echo("")

    if failures:
        echo(f"{failures}/{len(results)} smoke cases failed.")
        raise typer.Exit(code=1)
    echo(f"All {len(results)} smoke cases passed.")


@app.command("generate-testset")
def generate_testset(
    n: int = typer.Option(
        10,
        "--n",
        help="Number of test questions (start small; scale to 150–200 later).",
    ),
    corpus: str = typer.Option("helixforge", "--corpus", help="Corpus name label."),
    force: bool = typer.Option(
        False, "--force", help="Ignore JSON cache and regenerate via Ragas."
    ),
) -> None:
    """Generate a synthetic test set using Ragas and store it in SQLite."""
    from sqlmodel import select

    from src.storage.db import session_scope
    from src.storage.models import TestItem
    from src.testset.generate import run_testset_generation

    config = load_config()
    logger.info("Generating test set with n=%d, corpus=%s, force=%s", n, corpus, force)
    try:
        run_id = run_testset_generation(
            config, n=n, corpus_name=corpus, force=force
        )
    except Exception as exc:
        echo(f"Test set generation failed: {exc}")
        raise typer.Exit(code=1) from exc

    with session_scope(config) as session:
        rows = list(session.exec(select(TestItem).where(TestItem.run_id == run_id)))
        previews = [
            {"question_type": item.question_type, "question": item.question}
            for item in rows
        ]
    echo(f"run_id={run_id}  questions={len(previews)}")
    by_type: dict[str, int] = {}
    for item in previews:
        by_type[item["question_type"]] = by_type.get(item["question_type"], 0) + 1
    echo("types: " + ", ".join(f"{k}={v}" for k, v in sorted(by_type.items())))
    for i, item in enumerate(previews[:5], start=1):
        echo(f"[{i}] ({item['question_type']}) {item['question']}")
    if len(previews) > 5:
        echo(f"... and {len(previews) - 5} more")
    logger.info("Test set generation complete. run_id=%s", run_id)


@app.command("build-handauthored-testset")
def build_handauthored_testset(
    corpus: str = typer.Option("helixforge", "--corpus", help="Corpus name label."),
    limit: int | None = typer.Option(
        None,
        "--limit",
        help="Use a balanced subset (e.g. 20) instead of all 40 questions.",
    ),
) -> None:
    """Persist hand-authored (agent-curated) questions as a new run.

    No LLM calls are made — every question/answer was written by reading the
    actual corpus documents, so there is no Groq quota or Ollama JSON-parsing
    risk during generation.
    """
    from src.storage.db import session_scope
    from src.storage.models import Run, RunStatus, TestItem
    from src.testset.handauthored_items import ITEMS, select_balanced_items

    items = select_balanced_items(ITEMS, limit) if limit is not None else ITEMS
    note = (
        f"Hand-authored balanced subset ({len(items)}/{len(ITEMS)}); no LLM used."
        if limit is not None
        else "Hand-authored by agent from the 86-doc corpus; no LLM used for generation."
    )

    config = load_config()
    with session_scope(config) as session:
        run = Run(
            pipeline_config_name="baseline",
            corpus_name=corpus,
            num_questions=len(items),
            status=RunStatus.READY.value,
            notes=note,
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

    by_type: dict[str, int] = {}
    for item in items:
        by_type[item["question_type"]] = by_type.get(item["question_type"], 0) + 1
    echo(f"run_id={run_id}  questions={len(items)}")
    echo("types: " + ", ".join(f"{k}={v}" for k, v in sorted(by_type.items())))
    logger.info("Persisted hand-authored run_id=%s with %d items", run_id, len(items))


@app.command("run-eval")
def run_eval(
    run_id: int = typer.Option(..., "--run-id", help="Run ID to evaluate."),
    pipeline_config: str = typer.Option(
        "baseline",
        "--pipeline-config",
        help="Named RAG config: baseline, degraded, or optimized.",
    ),
    concurrency: int | None = typer.Option(
        None, "--concurrency", help="Max concurrent RAG calls (default: 2)."
    ),
) -> None:
    """Run evaluation against a test set using the selected pipeline config."""
    from src.evaluation.run_eval import run_evaluation
    from src.rag_pipeline.configs import get_pipeline_config

    try:
        pipeline_config = get_pipeline_config(pipeline_config).name
    except ValueError as exc:
        echo(str(exc))
        raise typer.Exit(code=1) from exc

    config = load_config()
    conc = concurrency if concurrency is not None else min(1, config.eval_concurrency)
    logger.info(
        "Starting evaluation run_id=%d, pipeline=%s, concurrency=%d",
        run_id,
        pipeline_config,
        conc,
    )
    try:
        summary = run_evaluation(
            config,
            run_id=run_id,
            pipeline_config=pipeline_config,
            concurrency=conc,
        )
    except Exception as exc:
        echo(f"Evaluation failed: {exc}")
        raise typer.Exit(code=1) from exc

    echo(
        f"run_id={summary['run_id']}  pipeline={summary['pipeline']}  "
        f"items={summary['num_items']}  rag_errors={summary['num_errors']}"
    )
    avgs = summary.get("averages") or {}
    parts = []
    for key, label in (
        ("faithfulness", "faithfulness"),
        ("answer_relevancy", "answer_relevancy"),
        ("context_precision", "context_precision"),
        ("context_recall", "context_recall"),
    ):
        val = avgs.get(key)
        parts.append(f"{label}={val:.3f}" if isinstance(val, float) else f"{label}=n/a")
    echo("averages: " + "  ".join(parts))
    logger.info("Evaluation complete.")


@app.command("compare-eval")
def compare_eval(
    run_id: int = typer.Option(..., "--run-id", help="Test-set run id to summarize."),
) -> None:
    """Print stored Ragas averages per pipeline for one test set."""
    from src.evaluation.run_eval import summarize_pipeline_scores

    config = load_config()
    rows = summarize_pipeline_scores(config, run_id=run_id)
    if not rows:
        echo(f"No eval results for run_id={run_id}.")
        raise typer.Exit(code=1)
    for row in rows:
        avgs = row.get("averages") or {}
        parts = []
        for key in (
            "faithfulness",
            "answer_relevancy",
            "context_precision",
            "context_recall",
        ):
            val = avgs.get(key)
            parts.append(f"{key}={val:.3f}" if isinstance(val, float) else f"{key}=n/a")
        lat = row.get("avg_latency_ms")
        lat_s = f"{lat:.0f}ms" if isinstance(lat, float) else "n/a"
        echo(
            f"{row['pipeline']}: items={row['num_results']} errors={row['num_errors']} "
            f"latency={lat_s}  " + "  ".join(parts)
        )
    logger.info("compare-eval run_id=%d pipelines=%d", run_id, len(rows))


@app.command("serve-api")
def serve_api(
    port: int = typer.Option(8000, "--port", help="FastAPI server port."),
    host: str = typer.Option("127.0.0.1", "--host", help="Bind host."),
) -> None:
    """Launch the FastAPI backend for the React dashboard."""
    import uvicorn

    logger.info("Launching API on http://%s:%d", host, port)
    uvicorn.run(
        "src.api.app:app",
        host=host,
        port=port,
        reload=False,
        factory=False,
    )


@app.command("serve-ui")
def serve_ui(
    port: int = typer.Option(5173, "--port", help="Vite dev server port."),
) -> None:
    """Launch the React dashboard (requires serve-api in another terminal)."""
    web_dir = PROJECT_ROOT / "web"
    if not (web_dir / "package.json").exists():
        typer.echo(f"React app not found at {web_dir}", err=True)
        raise typer.Exit(code=1)

    logger.info("Launching React UI on http://127.0.0.1:%d", port)
    subprocess.run(
        ["npm", "run", "dev", "--", "--port", str(port), "--host"],
        check=True,
        cwd=str(web_dir),
        shell=True,
    )


def main() -> None:
    _configure_stdio()
    app()


if __name__ == "__main__":
    main()

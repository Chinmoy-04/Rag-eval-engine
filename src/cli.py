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
        "baseline", "--pipeline-config", help="Named RAG pipeline config."
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
    n: int = typer.Option(150, "--n", help="Number of test questions to generate."),
    corpus: str = typer.Option("default", "--corpus", help="Corpus name label."),
) -> None:
    """Generate a synthetic test set using Ragas."""
    from src.testset.generate import run_testset_generation

    config = load_config()
    logger.info("Generating test set with n=%d, corpus=%s", n, corpus)
    run_id = run_testset_generation(config, n=n, corpus_name=corpus)
    logger.info("Test set generation complete. run_id=%s", run_id)


@app.command("run-eval")
def run_eval(
    run_id: int = typer.Option(..., "--run-id", help="Run ID to evaluate."),
    pipeline_config: str = typer.Option(
        "baseline", "--pipeline-config", help="Pipeline config name."
    ),
    concurrency: int | None = typer.Option(
        None, "--concurrency", help="Max concurrent evaluations."
    ),
) -> None:
    """Run evaluation against a test set using the selected pipeline config."""
    from src.evaluation.run_eval import run_evaluation

    config = load_config()
    conc = concurrency or config.eval_concurrency
    logger.info(
        "Starting evaluation run_id=%d, pipeline=%s, concurrency=%d",
        run_id,
        pipeline_config,
        conc,
    )
    run_evaluation(config, run_id=run_id, pipeline_config=pipeline_config, concurrency=conc)
    logger.info("Evaluation complete.")


@app.command()
def serve(
    port: int = typer.Option(8501, "--port", help="Streamlit server port."),
) -> None:
    """Launch the Streamlit dashboard."""
    dashboard_path = PROJECT_ROOT / "src" / "dashboard" / "app.py"
    if not dashboard_path.exists():
        typer.echo(f"Dashboard not yet implemented: {dashboard_path}", err=True)
        raise typer.Exit(code=1)

    logger.info("Launching Streamlit dashboard on port %d", port)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(dashboard_path),
            "--server.port",
            str(port),
            "--server.headless",
            "true",
        ],
        check=True,
        cwd=str(PROJECT_ROOT),
    )


def main() -> None:
    _configure_stdio()
    app()


if __name__ == "__main__":
    main()

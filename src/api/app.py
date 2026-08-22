"""FastAPI backend for the HelixForge RAG Eval React UI."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlmodel import select

from src.config import load_config
from src.evaluation.run_eval import (
    fetch_item_breakdown,
    list_runs_overview,
    summarize_pipeline_scores,
)
from src.ingestion.indexer import collection_count
from src.rag_pipeline.configs import PIPELINE_CONFIGS
from src.rag_pipeline.pipeline import run_pipeline
from src.rag_pipeline.questions import SUGGESTED_QUESTIONS
from src.storage.db import session_scope
from src.storage.models import Run

app = FastAPI(title="HelixForge RAG Eval API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    pipeline: str = "baseline"
    show_contexts: bool = True


class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    contexts: list[str]
    latency_ms: float
    pipeline: str


@app.get("/api/health")
def health() -> dict[str, Any]:
    config = load_config()
    return {
        "status": "ok",
        "vectors": collection_count(config),
        "pipelines": sorted(PIPELINE_CONFIGS.keys()),
    }


@app.get("/api/suggested-questions")
def suggested_questions() -> dict[str, list[str]]:
    return SUGGESTED_QUESTIONS


@app.post("/api/ask", response_model=AskResponse)
def ask(body: AskRequest) -> AskResponse:
    config = load_config()
    if body.pipeline not in PIPELINE_CONFIGS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown pipeline '{body.pipeline}'. "
            f"Available: {', '.join(sorted(PIPELINE_CONFIGS))}",
        )
    if collection_count(config) == 0:
        raise HTTPException(
            status_code=503,
            detail="Vector index is empty. Run `uv run python -m src.cli ingest` first.",
        )
    try:
        result = run_pipeline(body.question, config, body.pipeline)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    contexts = list(result.retrieved_contexts) if body.show_contexts else []
    return AskResponse(
        answer=result.answer,
        sources=list(result.sources),
        contexts=contexts,
        latency_ms=float(result.latency_ms),
        pipeline=body.pipeline,
    )


@app.get("/api/runs")
def runs() -> list[dict[str, Any]]:
    config = load_config()
    rows = list_runs_overview(config)
    out: list[dict[str, Any]] = []
    for row in rows:
        created = row.get("created_at")
        out.append(
            {
                **row,
                "created_at": created.isoformat() if created else None,
            }
        )
    return out


@app.get("/api/runs/{run_id}/compare")
def compare_run(run_id: int) -> dict[str, Any]:
    config = load_config()
    with session_scope(config) as session:
        run = session.get(Run, run_id)
        if run is None:
            raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
        num_questions = run.num_questions

    pipelines = summarize_pipeline_scores(config, run_id=run_id)
    if not pipelines:
        raise HTTPException(
            status_code=404,
            detail=f"No eval results for run_id={run_id}",
        )
    breakdown = fetch_item_breakdown(config, run_id=run_id)
    return {
        "run_id": run_id,
        "num_questions": num_questions,
        "pipelines": pipelines,
        "breakdown": breakdown,
    }

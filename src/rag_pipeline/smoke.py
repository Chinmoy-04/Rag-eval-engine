"""Hardcoded Phase 3 checks: retrieval+generation should hit known policy facts."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from src.config import AppConfig, load_config
from src.rag_pipeline.pipeline import run_pipeline


@dataclass(frozen=True)
class SmokeCase:
    question: str
    must_contain: tuple[str, ...]
    notes: str


SMOKE_CASES: tuple[SmokeCase, ...] = (
    SmokeCase(
        question="How much PTO do new full-time employees accrue in their first two years?",
        must_contain=("18",),
        notes="Simple lookup in pto_policy.md",
    ),
    SmokeCase(
        question="What happens to the on-call stipend during parental leave?",
        must_contain=("pause",),
        notes="Fact appears in parental_leave.md and engineering_oncall.md",
    ),
    SmokeCase(
        question="Who is the CEO of HelixForge?",
        must_contain=("mara chen",),
        notes="Simple lookup in company_overview.md",
    ),
)


def _normalize(text: str) -> str:
    """Collapse unicode spaces/punctuation so smoke checks survive model quirks."""
    chars: list[str] = []
    for char in text.lower():
        if unicodedata.category(char) == "Zs" or char in "\n\t\r":
            chars.append(" ")
        else:
            chars.append(char)
    return re.sub(r"\s+", " ", "".join(chars))


def _contains_all(answer: str, needles: tuple[str, ...]) -> bool:
    haystack = _normalize(answer)
    return all(_normalize(needle) in haystack for needle in needles)


def run_smoke(config: AppConfig | None = None) -> list[dict[str, object]]:
    """Run baseline RAG on a few known questions. Returns per-case result dicts."""
    if config is None:
        config = load_config()
    results: list[dict[str, object]] = []
    for case in SMOKE_CASES:
        response = run_pipeline(case.question, config=config, pipeline_config="baseline")
        passed = _contains_all(response.answer, case.must_contain)
        results.append(
            {
                "question": case.question,
                "notes": case.notes,
                "passed": passed,
                "must_contain": case.must_contain,
                "answer": response.answer,
                "latency_ms": response.latency_ms,
                "sources": response.sources,
            }
        )
    return results

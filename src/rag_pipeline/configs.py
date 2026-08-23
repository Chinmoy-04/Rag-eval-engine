"""Named RAG pipeline configurations for comparative evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

RetrievalMode = Literal[
    "vector",
    "hybrid",
    "hybrid_expand",
    "vector_rerank",
    "csv_hybrid",
]


@dataclass(frozen=True)
class PipelineConfig:
    """Knobs for one RAG pipeline under test."""

    name: str
    top_k: int
    temperature: float
    max_tokens: int
    system_prompt: str
    user_prompt_template: str
    retrieval_mode: RetrievalMode = "vector"
    # Fetch this many neighbors, then keep ``top_k`` after merge/dedupe.
    retrieve_k: int | None = None
    # If set, each retrieved chunk is truncated before it reaches the LLM.
    context_char_limit: int | None = None
    # Also retrieve a stopword-stripped query and merge unique chunks (vector mode).
    expand_query: bool = False
    # Pool size before lexical rerank (vector_rerank mode).
    rerank_candidates: int = 16


BASELINE_SYSTEM_PROMPT = (
    "You answer questions about HelixForge internal policies. "
    "Use only the provided context. If the context does not contain the answer, "
    "say you do not know. Do not invent policy details. Be concise. "
    "Do not include citation markers, footnotes, or source tags in your answer."
)

BASELINE_USER_TEMPLATE = """Context:
{context}

Question: {question}

Answer using only the context above."""

DEGRADED_SYSTEM_PROMPT = (
    "You are a helpful internal assistant. Prefer the provided snippets, but if "
    "they look incomplete you may fill gaps from general knowledge of typical "
    "tech-company policy. Be confident. Guess when unsure."
)

DEGRADED_USER_TEMPLATE = """Some possibly related notes:
{context}

Question: {question}

Give a direct answer even if the notes are thin."""

OPTIMIZED_SYSTEM_PROMPT = (
    "You answer questions about HelixForge internal policies using ONLY the "
    "provided context. Prefer concrete numbers, owners, SLAs, and table rows. "
    "If a CSV/table is in context, quote the matching row. If the context does "
    "not contain the answer, say you do not know. Never invent policy details. "
    "Do not include citation markers, footnotes, or source tags in your answer."
)

OPTIMIZED_USER_TEMPLATE = """Context (ranked chunks; tables may appear as CSV rows):
{context}

Question: {question}

Rules:
- Answer only from the context.
- Prefer exact figures, names, and filenames that appear above.
- If multiple chunks conflict, prefer the more specific table/SOP over a summary.
- If the answer is not present, say you do not know."""

BASELINE = PipelineConfig(
    name="baseline",
    top_k=4,
    temperature=0.0,
    max_tokens=400,
    system_prompt=BASELINE_SYSTEM_PROMPT,
    user_prompt_template=BASELINE_USER_TEMPLATE,
    retrieval_mode="vector",
)

DEGRADED = PipelineConfig(
    name="degraded",
    top_k=1,
    temperature=0.85,
    max_tokens=400,
    system_prompt=DEGRADED_SYSTEM_PROMPT,
    user_prompt_template=DEGRADED_USER_TEMPLATE,
    retrieval_mode="vector",
    retrieve_k=1,
    context_char_limit=220,
    expand_query=False,
)

OPTIMIZED = PipelineConfig(
    name="optimized",
    top_k=8,
    temperature=0.0,
    max_tokens=500,
    system_prompt=OPTIMIZED_SYSTEM_PROMPT,
    user_prompt_template=OPTIMIZED_USER_TEMPLATE,
    retrieval_mode="vector",
    retrieve_k=12,
    expand_query=True,
)

HYBRID = PipelineConfig(
    name="hybrid",
    top_k=6,
    temperature=0.0,
    max_tokens=400,
    system_prompt=BASELINE_SYSTEM_PROMPT,
    user_prompt_template=BASELINE_USER_TEMPLATE,
    retrieval_mode="hybrid",
    retrieve_k=12,
)

HYBRID_PLUS = PipelineConfig(
    name="hybrid_plus",
    top_k=8,
    temperature=0.0,
    max_tokens=500,
    system_prompt=OPTIMIZED_SYSTEM_PROMPT,
    user_prompt_template=OPTIMIZED_USER_TEMPLATE,
    retrieval_mode="hybrid_expand",
    retrieve_k=12,
)

RERANK = PipelineConfig(
    name="rerank",
    top_k=6,
    temperature=0.0,
    max_tokens=400,
    system_prompt=BASELINE_SYSTEM_PROMPT,
    user_prompt_template=BASELINE_USER_TEMPLATE,
    retrieval_mode="vector_rerank",
    retrieve_k=16,
    rerank_candidates=16,
)

CSV_ROUTE = PipelineConfig(
    name="csv_route",
    top_k=6,
    temperature=0.0,
    max_tokens=400,
    system_prompt=BASELINE_SYSTEM_PROMPT,
    user_prompt_template=BASELINE_USER_TEMPLATE,
    retrieval_mode="csv_hybrid",
    retrieve_k=12,
)

PIPELINE_CONFIGS: dict[str, PipelineConfig] = {
    BASELINE.name: BASELINE,
    DEGRADED.name: DEGRADED,
    OPTIMIZED.name: OPTIMIZED,
    HYBRID.name: HYBRID,
    HYBRID_PLUS.name: HYBRID_PLUS,
    RERANK.name: RERANK,
    CSV_ROUTE.name: CSV_ROUTE,
}

# Display / compare order: controls first, then experimental retrieval pipelines.
PIPELINE_ORDER: tuple[str, ...] = (
    "degraded",
    "baseline",
    "optimized",
    "hybrid",
    "hybrid_plus",
    "rerank",
    "csv_route",
)


def get_pipeline_config(name: str) -> PipelineConfig:
    """Return a named pipeline config or raise with the available names."""
    key = name.strip().lower()
    try:
        return PIPELINE_CONFIGS[key]
    except KeyError as exc:
        available = ", ".join(sorted(PIPELINE_CONFIGS))
        raise ValueError(
            f"Unknown pipeline config '{name}'. Available: {available}."
        ) from exc


def sorted_pipeline_names(names: set[str] | list[str] | None = None) -> list[str]:
    """Order pipeline names for dashboards (known order, then alphabetical)."""
    if names is None:
        return list(PIPELINE_ORDER)
    remaining = set(names)
    ordered = [name for name in PIPELINE_ORDER if name in remaining]
    ordered.extend(sorted(remaining - set(ordered)))
    return ordered

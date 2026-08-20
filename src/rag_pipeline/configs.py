"""Named RAG pipeline configurations.

Phase 3 implements ``baseline`` only. ``degraded`` and ``optimized`` land in Phase 7
so evaluation can show scores moving when retrieval/generation settings change.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PipelineConfig:
    """Knobs for one RAG pipeline under test."""

    name: str
    top_k: int
    temperature: float
    max_tokens: int
    system_prompt: str
    user_prompt_template: str


BASELINE_SYSTEM_PROMPT = (
    "You answer questions about HelixForge internal policies. "
    "Use only the provided context. If the context does not contain the answer, "
    "say you do not know. Do not invent policy details. Be concise."
)

BASELINE_USER_TEMPLATE = """Context:
{context}

Question: {question}

Answer using only the context above."""

BASELINE = PipelineConfig(
    name="baseline",
    top_k=4,
    temperature=0.0,
    max_tokens=400,
    system_prompt=BASELINE_SYSTEM_PROMPT,
    user_prompt_template=BASELINE_USER_TEMPLATE,
)

PIPELINE_CONFIGS: dict[str, PipelineConfig] = {
    BASELINE.name: BASELINE,
}


def get_pipeline_config(name: str) -> PipelineConfig:
    """Return a named pipeline config or raise with the available names."""
    key = name.strip().lower()
    try:
        return PIPELINE_CONFIGS[key]
    except KeyError as exc:
        available = ", ".join(sorted(PIPELINE_CONFIGS))
        raise ValueError(
            f"Unknown pipeline config '{name}'. Available: {available}. "
            "degraded/optimized are added in Phase 7."
        ) from exc

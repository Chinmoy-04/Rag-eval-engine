"""Thin LLM wrapper via litellm so pipeline code never imports a vendor SDK."""

from __future__ import annotations

import logging

from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from src.config import AppConfig, configure_litellm_env, get_llm_model_name, load_config

logger = logging.getLogger("rag_eval")


def _is_rate_limit(exc: BaseException) -> bool:
    name = type(exc).__name__.lower()
    msg = str(exc).lower()
    return (
        "ratelimit" in name
        or "rate limit" in msg
        or "rate_limit" in msg
        or "tokens per minute" in msg
        or "tpm" in msg
        or "429" in msg
    )


@retry(
    retry=retry_if_exception(_is_rate_limit),
    wait=wait_exponential(multiplier=2, min=10, max=90),
    stop=stop_after_attempt(6),
    reraise=True,
)
def generate_completion(
    messages: list[dict[str, str]],
    config: AppConfig | None = None,
    *,
    temperature: float = 0.0,
    max_tokens: int = 512,
) -> str:
    """Call the configured chat model and return the assistant text."""
    if config is None:
        config = load_config()
    configure_litellm_env(config)
    model = get_llm_model_name(config)

    # Imported here so ingest/query still work without an LLM key.
    from litellm import completion

    logger.info("LLM generate model=%s temperature=%.2f", model, temperature)
    extra: dict[str, object] = {}
    # gpt-oss spends max_tokens on hidden reasoning; without this, content
    # is often empty (especially when a pipeline caps max_tokens tightly).
    if "gpt-oss" in model.lower():
        extra["reasoning_effort"] = "low"
    elif "qwen" in model.lower():
        extra["reasoning_effort"] = "none"

    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            response = completion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **extra,
            )
        except Exception as exc:
            message = str(exc)
            if "model_not_found" in message or "does not exist" in message:
                raise ValueError(
                    f"Groq rejected model '{model}'. "
                    "Set LLM_MODEL=openai/gpt-oss-20b in .env "
                    "(llama-3.1-8b-instant was retired on 2026-08-16)."
                ) from exc
            if extra and "reasoning_effort" in message.lower():
                logger.warning("Provider rejected reasoning_effort; retrying without it")
                extra = {}
                last_error = exc
                continue
            raise

        content = response.choices[0].message.content
        if content and str(content).strip():
            return str(content).strip()
        finish = getattr(response.choices[0], "finish_reason", None)
        logger.warning(
            "Empty LLM content model=%s attempt=%d/%d finish_reason=%s",
            model,
            attempt,
            3,
            finish,
        )
        last_error = RuntimeError(f"Empty LLM response from {model}")

    if last_error is not None:
        raise last_error
    raise RuntimeError(f"Empty LLM response from {model}")

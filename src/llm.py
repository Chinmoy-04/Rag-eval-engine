"""Thin LLM wrapper via litellm so pipeline code never imports a vendor SDK."""

from __future__ import annotations

import logging

from src.config import AppConfig, configure_litellm_env, get_llm_model_name, load_config

logger = logging.getLogger("rag_eval")


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
    try:
        response = completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except Exception as exc:
        message = str(exc)
        if "model_not_found" in message or "does not exist" in message:
            raise ValueError(
                f"Groq rejected model '{model}'. "
                "Set LLM_MODEL=openai/gpt-oss-20b in .env "
                "(llama-3.1-8b-instant was retired on 2026-08-16)."
            ) from exc
        raise

    content = response.choices[0].message.content
    if not content:
        raise RuntimeError(f"Empty LLM response from {model}")
    return str(content).strip()

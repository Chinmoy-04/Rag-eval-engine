"""Shared Ragas LLM / embedding clients for evaluation and (optionally) generation."""

from __future__ import annotations

import logging
import os
from typing import Any

from src.config import AppConfig, configure_litellm_env

logger = logging.getLogger("rag_eval")


def ragas_judge_model(config: AppConfig) -> str:
    """Model used as the Ragas judge (scoring).

    Prefer Qwen with reasoning disabled on Groq free tier (TPM + finish_reason).
    Override with ``EVAL_LLM_MODEL`` or fall back to ``TESTSET_LLM_MODEL``.
    """
    override = (os.getenv("EVAL_LLM_MODEL") or os.getenv("TESTSET_LLM_MODEL") or "").strip()
    if override:
        return override
    if config.llm_provider.value == "groq":
        return "qwen/qwen3.6-27b"
    return config.llm_model


def build_ragas_llm(config: AppConfig, *, temperature: float = 0.0):
    """LangChain chat model wrapped for Ragas."""
    from langchain_openai import ChatOpenAI
    from ragas.llms import LangchainLLMWrapper

    configure_litellm_env(config)
    model = ragas_judge_model(config)
    max_tokens = 2048
    llm_kwargs: dict[str, Any] = {
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if "qwen" in model.lower():
        llm_kwargs["reasoning_effort"] = "none"
    elif "gpt-oss" in model.lower():
        llm_kwargs["reasoning_effort"] = "low"

    if config.llm_provider.value == "groq":
        if not config.groq_api_key:
            raise ValueError("GROQ_API_KEY is required for Ragas evaluation")
        llm = ChatOpenAI(
            model=model,
            api_key=config.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
            **llm_kwargs,
        )
    elif config.llm_provider.value == "openai":
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for Ragas evaluation")
        llm = ChatOpenAI(
            model=model.removeprefix("openai/"),
            api_key=config.openai_api_key,
            **{k: v for k, v in llm_kwargs.items() if k != "reasoning_effort"},
        )
    elif config.llm_provider.value == "anthropic":
        from langchain_anthropic import ChatAnthropic

        if not config.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for Ragas evaluation")
        llm = ChatAnthropic(
            model=model.removeprefix("anthropic/"),
            api_key=config.anthropic_api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {config.llm_provider}")

    logger.info("Ragas judge LLM model=%s temperature=%s", model, temperature)
    return LangchainLLMWrapper(llm)


def build_ragas_embeddings():
    """Local ONNX embeddings wrapped for Ragas (no API key)."""
    from ragas.embeddings import LangchainEmbeddingsWrapper

    from src.testset.embeddings_lc import LocalOnnxLangchainEmbeddings

    return LangchainEmbeddingsWrapper(LocalOnnxLangchainEmbeddings())

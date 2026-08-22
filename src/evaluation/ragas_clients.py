"""Shared Ragas LLM / embedding clients for evaluation and (optionally) generation."""

from __future__ import annotations

import logging
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

from src.config import AppConfig, EvalLLMProvider, configure_litellm_env

logger = logging.getLogger("rag_eval")


def ragas_judge_model(config: AppConfig) -> str:
    """Model used as the Ragas judge (scoring). Independent of Ask/RAG."""
    return config.eval_llm_model


def _require_ollama(base_url: str) -> None:
    tags_url = base_url.rstrip("/") + "/api/tags"
    try:
        with urlopen(tags_url, timeout=3) as resp:
            if getattr(resp, "status", 200) >= 400:
                raise OSError(f"Ollama returned HTTP {resp.status}")
    except (URLError, OSError, TimeoutError) as exc:
        raise ValueError(
            f"Ollama is not reachable at {base_url}. "
            "Install it from https://ollama.com/download, start the app, then run "
            "`ollama pull llama3.1:8b`."
        ) from exc


def _extract_json_payload(text: str) -> str:
    """Keep only the first complete JSON object/array so Ragas can parse 8B output."""
    if not text:
        return text
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.split("\n", 1)[-1]
        if stripped.endswith("```"):
            stripped = stripped[: -3].rstrip()
    start_obj = stripped.find("{")
    start_arr = stripped.find("[")
    starts = [i for i in (start_obj, start_arr) if i >= 0]
    if not starts:
        return stripped
    start = min(starts)
    opener = stripped[start]
    closer = "}" if opener == "{" else "]"
    depth = 0
    in_string = False
    escape = False
    for i, char in enumerate(stripped[start:], start=start):
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
            if depth == 0:
                return stripped[start : i + 1]
    return stripped


def _clean_llm_result(result):
    generations = getattr(result, "generations", None)
    if not generations:
        return result
    for gen_list in generations:
        for gen in gen_list:
            message = getattr(gen, "message", None)
            content = getattr(message, "content", None) if message else None
            if isinstance(content, str) and content:
                cleaned = _extract_json_payload(content)
                message.content = cleaned
                if getattr(gen, "text", None) is not None:
                    gen.text = cleaned
    return result


def _build_ollama_judge(config: AppConfig, *, temperature: float, max_tokens: int):
    from langchain_openai import ChatOpenAI

    class JsonCleaningChatOpenAI(ChatOpenAI):
        def _generate(self, messages, stop=None, run_manager=None, **kwargs):
            result = super()._generate(
                messages, stop=stop, run_manager=run_manager, **kwargs
            )
            return _clean_llm_result(result)

        async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
            result = await super()._agenerate(
                messages, stop=stop, run_manager=run_manager, **kwargs
            )
            return _clean_llm_result(result)

    _require_ollama(config.ollama_base_url)
    model = ragas_judge_model(config)
    base = config.ollama_base_url.rstrip("/")
    num_ctx = 16384
    logger.info(
        "Ragas judge provider=ollama model=%s base_url=%s num_ctx=%d format=json",
        model,
        base,
        num_ctx,
    )
    return JsonCleaningChatOpenAI(
        model=model,
        api_key="ollama",
        base_url=f"{base}/v1",
        temperature=temperature,
        max_tokens=max_tokens,
        extra_body={
            "format": "json",
            "options": {
                "num_ctx": num_ctx,
                "num_predict": max_tokens,
                "temperature": temperature,
            },
        },
    )


def build_ragas_llm(config: AppConfig, *, temperature: float = 0.0):
    """LangChain chat model wrapped for Ragas."""
    from langchain_openai import ChatOpenAI
    from src.ragas_compat import ensure_ragas_imports

    ensure_ragas_imports()
    from ragas.llms import LangchainLLMWrapper

    configure_litellm_env(config)
    model = ragas_judge_model(config)
    max_tokens = 2048
    provider = config.eval_llm_provider

    if provider == EvalLLMProvider.OLLAMA:
        llm = _build_ollama_judge(
            config, temperature=temperature, max_tokens=max_tokens
        )
        return LangchainLLMWrapper(llm)

    llm_kwargs: dict[str, Any] = {
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if "qwen" in model.lower():
        llm_kwargs["reasoning_effort"] = "none"
    elif "gpt-oss" in model.lower():
        llm_kwargs["reasoning_effort"] = "low"

    if provider == EvalLLMProvider.GROQ:
        if not config.groq_api_key:
            raise ValueError("GROQ_API_KEY is required for Ragas evaluation")
        llm = ChatOpenAI(
            model=model,
            api_key=config.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
            **llm_kwargs,
        )
    elif provider == EvalLLMProvider.OPENAI:
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for Ragas evaluation")
        llm = ChatOpenAI(
            model=model.removeprefix("openai/"),
            api_key=config.openai_api_key,
            **{k: v for k, v in llm_kwargs.items() if k != "reasoning_effort"},
        )
    elif provider == EvalLLMProvider.ANTHROPIC:
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
        raise ValueError(f"Unsupported EVAL_LLM_PROVIDER: {provider}")

    logger.info(
        "Ragas judge provider=%s model=%s temperature=%s",
        provider.value,
        model,
        temperature,
    )
    return LangchainLLMWrapper(llm)


def build_ragas_embeddings():
    """Local ONNX embeddings wrapped for Ragas (no API key)."""
    from ragas.embeddings import LangchainEmbeddingsWrapper

    from src.testset.embeddings_lc import LocalOnnxLangchainEmbeddings

    return LangchainEmbeddingsWrapper(LocalOnnxLangchainEmbeddings())

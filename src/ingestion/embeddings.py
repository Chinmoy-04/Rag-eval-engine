"""Embedding model factory for ingestion and retrieval.

Two backends:
- ``local``: Chroma's ONNX MiniLM (all-MiniLM-L6-v2). First run may download
  the ONNX weights into ~/.cache/chroma. No API key.
- ``openai``: OpenAI embeddings API. Requires OPENAI_API_KEY.
"""

from __future__ import annotations

from typing import Any

from llama_index.core.base.embeddings.base import BaseEmbedding, Embedding
from llama_index.core.bridge.pydantic import PrivateAttr

from src.config import AppConfig, EmbeddingProvider, get_embedding_model_name, load_config


class LocalOnnxEmbedding(BaseEmbedding):
    """LlamaIndex wrapper around Chroma's bundled ONNX MiniLM encoder."""

    _encoder: Any = PrivateAttr()

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(model_name="onnx-minilm-l6-v2", **kwargs)
        from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import (
            ONNXMiniLM_L6_V2,
        )

        self._encoder = ONNXMiniLM_L6_V2()

    @classmethod
    def class_name(cls) -> str:
        return "LocalOnnxEmbedding"

    def _encode(self, texts: list[str]) -> list[Embedding]:
        raw = self._encoder(texts)
        return [[float(x) for x in vector] for vector in raw]

    def _get_query_embedding(self, query: str) -> Embedding:
        return self._encode([query])[0]

    async def _aget_query_embedding(self, query: str) -> Embedding:
        return self._get_query_embedding(query)

    def _get_text_embedding(self, text: str) -> Embedding:
        return self._encode([text])[0]

    def _get_text_embeddings(self, texts: list[str]) -> list[Embedding]:
        return self._encode(texts)


def build_embed_model(config: AppConfig | None = None) -> BaseEmbedding:
    """Instantiate the configured LlamaIndex embedding model."""
    if config is None:
        config = load_config()

    if config.embedding_provider == EmbeddingProvider.OPENAI:
        if not config.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai. "
                "Set EMBEDDING_PROVIDER=local to embed offline."
            )
        from llama_index.embeddings.openai import OpenAIEmbedding

        model_name = config.embedding_model.removeprefix("openai/")
        return OpenAIEmbedding(model=model_name, api_key=config.openai_api_key)

    return LocalOnnxEmbedding()


def embedding_fingerprint(config: AppConfig) -> str:
    """Stable id used to detect when the index must be rebuilt."""
    return get_embedding_model_name(config)

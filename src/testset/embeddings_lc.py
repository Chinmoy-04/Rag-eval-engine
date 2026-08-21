"""Local MiniLM embeddings exposed as a LangChain Embeddings object for Ragas."""

from __future__ import annotations

from typing import List

from langchain_core.embeddings import Embeddings


class LocalOnnxLangchainEmbeddings(Embeddings):
    """Wrap Chroma's ONNX MiniLM so Ragas can embed without an API key."""

    def __init__(self) -> None:
        from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import (
            ONNXMiniLM_L6_V2,
        )

        self._encoder = ONNXMiniLM_L6_V2()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        raw = self._encoder(texts)
        return [[float(x) for x in vector] for vector in raw]

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

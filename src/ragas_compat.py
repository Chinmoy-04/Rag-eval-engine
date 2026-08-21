"""Compatibility shims for third-party libraries with broken imports."""

from __future__ import annotations

import sys
from types import ModuleType


def ensure_ragas_imports() -> None:
    """Allow ``import ragas`` when langchain-community no longer ships VertexAI.

    Ragas 0.4.3 still does ``from langchain_community.chat_models.vertexai import
    ChatVertexAI`` at import time. Modern langchain-community removed that module.
    We only need the name for an isinstance() allow-list, so a stub is enough.
    """
    module_name = "langchain_community.chat_models.vertexai"
    if module_name in sys.modules:
        return
    try:
        __import__(module_name)
        return
    except ModuleNotFoundError:
        pass

    stub = ModuleType(module_name)

    class ChatVertexAI:  # noqa: N801 - match upstream symbol name
        """Stub so ragas can import without installing Vertex AI."""

    stub.ChatVertexAI = ChatVertexAI
    sys.modules[module_name] = stub

"""Centralized configuration and LLM/embedding provider abstraction."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from enum import Enum
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DOCS_DIR = DATA_DIR / "raw_docs"
CHROMA_DIR = DATA_DIR / "chroma_db"
LOGS_DIR = PROJECT_ROOT / "logs"


class LLMProvider(str, Enum):
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class EmbeddingProvider(str, Enum):
    """Where embeddings come from.

    ``local`` uses Chroma's bundled ONNX MiniLM model (no API key, good for
    ingest/dev). ``openai`` uses the OpenAI embeddings API.
    """

    LOCAL = "local"
    OPENAI = "openai"


@dataclass(frozen=True)
class AppConfig:
    """Application configuration loaded from environment variables."""

    llm_provider: LLMProvider
    embedding_provider: EmbeddingProvider
    groq_api_key: str | None
    openai_api_key: str | None
    anthropic_api_key: str | None
    llm_model: str
    embedding_model: str
    chroma_collection: str
    chunk_size: int
    chunk_overlap: int
    default_top_k: int
    eval_concurrency: int
    eval_max_retries: int
    database_url: str
    log_level: str
    log_file: str


def _get_env(key: str, default: str | None = None) -> str | None:
    return os.getenv(key, default)


def load_config(env_file: Path | None = None) -> AppConfig:
    """Load configuration from .env and environment variables."""
    if env_file is None:
        env_file = PROJECT_ROOT / ".env"
    load_dotenv(env_file)

    provider_str = (_get_env("LLM_PROVIDER", "groq") or "groq").lower()
    try:
        provider = LLMProvider(provider_str)
    except ValueError as exc:
        raise ValueError(
            f"Invalid LLM_PROVIDER '{provider_str}'. Must be one of: "
            f"{', '.join(p.value for p in LLMProvider)}"
        ) from exc

    embed_provider_str = (_get_env("EMBEDDING_PROVIDER", "local") or "local").lower()
    try:
        embed_provider = EmbeddingProvider(embed_provider_str)
    except ValueError as exc:
        raise ValueError(
            f"Invalid EMBEDDING_PROVIDER '{embed_provider_str}'. Must be one of: "
            f"{', '.join(p.value for p in EmbeddingProvider)}"
        ) from exc

    return AppConfig(
        llm_provider=provider,
        embedding_provider=embed_provider,
        groq_api_key=_get_env("GROQ_API_KEY"),
        openai_api_key=_get_env("OPENAI_API_KEY"),
        anthropic_api_key=_get_env("ANTHROPIC_API_KEY"),
        llm_model=_get_env("LLM_MODEL", "openai/gpt-oss-20b") or "openai/gpt-oss-20b",
        embedding_model=_get_env("EMBEDDING_MODEL", "text-embedding-3-small")
        or "text-embedding-3-small",
        chroma_collection=_get_env("CHROMA_COLLECTION", "rag_eval_corpus")
        or "rag_eval_corpus",
        chunk_size=int(_get_env("CHUNK_SIZE", "512") or "512"),
        chunk_overlap=int(_get_env("CHUNK_OVERLAP", "50") or "50"),
        default_top_k=int(_get_env("DEFAULT_TOP_K", "4") or "4"),
        eval_concurrency=int(_get_env("EVAL_CONCURRENCY", "8") or "8"),
        eval_max_retries=int(_get_env("EVAL_MAX_RETRIES", "3") or "3"),
        database_url=_get_env("DATABASE_URL", "sqlite:///data/rag_eval.db")
        or "sqlite:///data/rag_eval.db",
        log_level=_get_env("LOG_LEVEL", "INFO") or "INFO",
        log_file=_get_env("LOG_FILE", "logs/rag_eval.log") or "logs/rag_eval.log",
    )


def setup_logging(config: AppConfig | None = None) -> logging.Logger:
    """Configure structured logging to console and a rotating log file."""
    if config is None:
        config = load_config()

    logger = logging.getLogger("rag_eval")
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, config.log_level.upper(), logging.INFO))
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    log_path = PROJECT_ROOT / config.log_file
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        log_path, maxBytes=5_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_llm_model_name(config: AppConfig | None = None) -> str:
    """Return the litellm-compatible model identifier for the configured provider."""
    if config is None:
        config = load_config()

    model = config.llm_model
    if config.llm_provider == LLMProvider.GROQ:
        if not config.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY is required when LLM_PROVIDER=groq. "
                "Copy .env.example to .env and paste your key from console.groq.com"
            )
        if not model.startswith("groq/"):
            model = f"groq/{model}"
        return model

    if config.llm_provider == LLMProvider.ANTHROPIC:
        if not config.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when LLM_PROVIDER=anthropic")
        if not model.startswith("anthropic/"):
            model = f"anthropic/{model}"
        return model

    if not config.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
    if not model.startswith("openai/"):
        model = f"openai/{model}"
    return model


def get_embedding_model_name(config: AppConfig | None = None) -> str:
    """Return a human-readable embedding model identifier for logs and fingerprints."""
    if config is None:
        config = load_config()

    if config.embedding_provider == EmbeddingProvider.LOCAL:
        return "local/onnx-minilm-l6-v2"

    if not config.openai_api_key:
        raise ValueError(
            "OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai. "
            "Set EMBEDDING_PROVIDER=local to embed offline."
        )
    model = config.embedding_model
    if not model.startswith("openai/"):
        model = f"openai/{model}"
    return model


def configure_litellm_env(config: AppConfig | None = None) -> None:
    """Set API keys in the environment for litellm."""
    if config is None:
        config = load_config()

    if config.groq_api_key:
        os.environ["GROQ_API_KEY"] = config.groq_api_key
    if config.openai_api_key:
        os.environ["OPENAI_API_KEY"] = config.openai_api_key
    if config.anthropic_api_key:
        os.environ["ANTHROPIC_API_KEY"] = config.anthropic_api_key

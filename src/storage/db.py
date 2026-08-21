"""Database engine and session helpers."""

from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

from src.config import PROJECT_ROOT, AppConfig, load_config

logger = logging.getLogger("rag_eval")

_engine = None


def resolve_database_url(database_url: str, project_root: Path | None = None) -> str:
    """Turn relative sqlite paths into absolute paths under the project root.

    ``sqlite:///data/rag_eval.db`` should always land in the repo's ``data/``,
    regardless of the process cwd.
    """
    root = project_root or PROJECT_ROOT
    if not database_url.startswith("sqlite:///"):
        return database_url

    # sqlite:///relative -> three slashes; sqlite:////abs -> four on Unix
    raw = database_url.removeprefix("sqlite:///")
    if raw.startswith("/") or (len(raw) > 1 and raw[1] == ":"):
        # Absolute path (Unix or Windows drive letter)
        path = Path(raw)
    else:
        path = root / raw

    path.parent.mkdir(parents=True, exist_ok=True)
    # SQLAlchemy wants forward slashes even on Windows
    return f"sqlite:///{path.resolve().as_posix()}"


def get_engine(config: AppConfig | None = None, *, echo: bool = False):
    """Return a process-wide SQLAlchemy engine (created once)."""
    global _engine
    if _engine is None:
        if config is None:
            config = load_config()
        url = resolve_database_url(config.database_url)
        logger.info("Opening database %s", url)
        _engine = create_engine(url, echo=echo, connect_args={"check_same_thread": False})
    return _engine


def reset_engine() -> None:
    """Drop the cached engine (tests / switching DB URLs)."""
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None


def init_db(config: AppConfig | None = None) -> None:
    """Create all tables if they do not already exist."""
    # Import models so SQLModel.metadata is populated.
    from src.storage import models as _models  # noqa: F401

    engine = get_engine(config)
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables ready: %s", ", ".join(SQLModel.metadata.tables))


@contextmanager
def session_scope(config: AppConfig | None = None) -> Iterator[Session]:
    """Yield a session that commits on success and rolls back on error."""
    engine = get_engine(config)
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise


def get_session(config: AppConfig | None = None) -> Session:
    """Return an open session. Prefer ``session_scope`` in application code."""
    return Session(get_engine(config))

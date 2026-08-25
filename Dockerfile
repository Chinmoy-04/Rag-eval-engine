FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY data/raw_docs ./data/raw_docs
# Pre-scored eval campaigns for Runs / Compare (live DB is gitignored).
COPY data/demo_rag_eval.db ./data/rag_eval.db

RUN uv sync --frozen --no-dev

# Rebuild Chroma + BM25 inside the image (chroma_db is gitignored).
ENV EMBEDDING_PROVIDER=local
ENV LLM_PROVIDER=groq
ENV DATABASE_URL=sqlite:///data/rag_eval.db
RUN mkdir -p data logs \
    && uv run python -m src.cli ingest

EXPOSE 8000
CMD ["sh", "-c", "uv run python -m src.cli serve-api --host 0.0.0.0 --port ${PORT:-8000}"]

# HelixForge RAG Eval

RAG evaluation engine for a fictional internal policy corpus (**HelixForge**). Ingest documents, run configurable retrieval pipelines, score answers with Ragas, and compare results in a React dashboard.

**Stack:** Python (Typer CLI, FastAPI, LlamaIndex, Chroma, Ragas, SQLite) + React (Vite, Tailwind v4, Recharts).

## Quick start

```bash
# 1. Install Python deps
uv sync

# 2. Configure environment
cp .env.example .env
# Set GROQ_API_KEY (free at https://console.groq.com/keys)

# 3. Seed corpus + build vector index (first run downloads ~80MB ONNX embed model)
uv run python scripts/seed_sample_corpus.py
uv run python -m src.cli ingest

# 4. Smoke-test RAG from the CLI
uv run python -m src.cli smoke
```

Default embeddings: `EMBEDDING_PROVIDER=local` (no API key). Default LLM: `openai/gpt-oss-20b` on Groq.

## Dashboard (React)

The UI talks to a FastAPI backend that wraps the same RAG and eval code as the CLI.

**Terminal 1 — API (port 8000):**

```bash
uv run python -m src.cli serve-api
```

**Terminal 2 — frontend (port 5173):**

```bash
cd web && npm install   # first time only
npm run dev
```

Or from the repo root:

```bash
uv run python -m src.cli serve-ui
```

Open http://localhost:5173

| Page | Purpose |
|------|---------|
| **Ask** | Live RAG chat with pipeline selector and retrieved contexts |
| **Runs** | Eval campaigns from SQLite (status, pipeline coverage, errors) |
| **Compare** | Ragas metric charts and per-question breakdown |

Production build: `cd web && npm run build` (output in `web/dist/`).

## CLI reference

### Ingestion & RAG

```bash
uv run python -m src.cli ingest [--rebuild]
uv run python -m src.cli query "How much PTO do new employees accrue?"   # retrieval only
uv run python -m src.cli ask "Who is the CEO of HelixForge?" [--show-contexts]
uv run python -m src.cli smoke
```

### Test sets

```bash
# Ragas synthetic generation (uses Groq; caches to data/testsets/)
uv run python -m src.cli generate-testset --n 10
uv run python -m src.cli generate-testset --n 10 --force

# Hand-authored ground-truth set (no LLM cost)
uv run python -m src.cli build-handauthored-testset              # all 40 questions
uv run python -m src.cli build-handauthored-testset --limit 20   # balanced 20-Q subset
```

### Evaluation

Three pipeline configs: `baseline`, `degraded`, `optimized`.

```bash
uv run python -m src.cli run-eval --run-id 5 --pipeline-config baseline --concurrency 1
uv run python -m src.cli run-eval --run-id 5 --pipeline-config degraded --concurrency 1
uv run python -m src.cli run-eval --run-id 5 --pipeline-config optimized --concurrency 1
uv run python -m src.cli compare-eval --run-id 5
```

Ragas scoring uses a local **Ollama** judge (`EVAL_LLM_PROVIDER=ollama`, `llama3.1:8b` by default). Start Ollama and pull the model before eval runs.

**Groq free tier:** use `--concurrency 1` and keep test sets modest (20 questions × 3 pipelines ≈ 60 RAG calls) to stay under the daily token limit.

### Database

```bash
uv run python -m src.cli init-db
```

Creates `data/rag_eval.db` with `runs`, `test_items`, and `eval_results`.

## Project layout

```
src/
  api/           FastAPI backend for the React UI
  ingestion/     Document loading, chunking, Chroma index
  rag_pipeline/  baseline / degraded / optimized configs
  evaluation/    Batch RAG + Ragas scoring → SQLite
  testset/       Synthetic generation + hand-authored items
  cli.py         Typer entry point
web/             React dashboard (Ask, Runs, Compare)
data/raw_docs/   HelixForge policy corpus (~86 docs)
```

## Recommended eval workflow

1. `build-handauthored-testset --limit 20` → note the `run_id`
2. After Groq daily quota resets, run all three pipelines with `--concurrency 1`
3. Open **Compare** in the dashboard for side-by-side Ragas scores

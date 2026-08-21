# RAG Evaluation Engine

High-throughput RAG evaluation with synthetic test sets, Ragas metrics, and a Streamlit dashboard.

## Phase 2 — Ingestion (working now)

```bash
# 1. Seed the demo corpus (HelixForge policy docs)
uv run python scripts/seed_sample_corpus.py

# 2. Build the Chroma vector index (first run downloads ~80MB ONNX embed model)
uv run python -m src.cli ingest

# 3. Test retrieval only — no LLM yet
uv run python -m src.cli query "How much PTO do new employees accrue?"
```

Re-run `ingest` without `--rebuild` skips work when nothing changed. Use `--rebuild` to force a fresh index.

Default embeddings: `EMBEDDING_PROVIDER=local` (no API key). Set `EMBEDDING_PROVIDER=openai` in `.env` for OpenAI embeddings, then `ingest --rebuild`.

## Phase 3 — Baseline RAG (retrieve + generate)

Copy `.env.example` to `.env` and set `GROQ_API_KEY` (free at [console.groq.com](https://console.groq.com/keys)). Keep `EMBEDDING_PROVIDER=local` and `LLM_MODEL=openai/gpt-oss-20b` (Groq retired `llama-3.1-8b-instant` in August 2026).

```bash
# Full RAG: retrieve chunks, then Groq writes an answer from that context
uv run python -m src.cli ask "How much PTO do new employees accrue in their first two years?"

# Same, plus the retrieved chunks
uv run python -m src.cli ask "Who is the CEO of HelixForge?" --show-contexts

# Three hardcoded checks (18 days PTO, stipend pauses, CEO Mara Chen)
uv run python -m src.cli smoke
```

`query` is still retrieval-only. `ask` is the real RAG loop.

## Ask UI (Streamlit)

```bash
uv run python -m src.cli serve
```

Opens a chat UI at http://localhost:8501 with suggested HelixForge questions, sources, latency, and retrieved chunks. Eval comparison charts still come in Phase 9 (after storage + Ragas).

## Phase 4 — Storage (SQLite)

```bash
uv run python -m src.cli init-db
```

Creates `data/rag_eval.db` with `runs`, `test_items`, and `eval_results`, then inserts and deletes a smoke row to prove the schema works.

## Phase 5 — Synthetic test set (Ragas)

```bash
# Start small while debugging (uses Groq + local embeddings; caches to data/testsets/)
uv run python -m src.cli generate-testset --n 10

# Force a fresh generation (ignore cache)
uv run python -m src.cli generate-testset --n 10 --force
```

Writes `TestItem` rows for a new `Run`, mixes simple / multi-hop synthesizers, and adds a couple of handcrafted abstain questions. Re-runs with the same corpus fingerprint reload from JSON cache (no extra API calls).

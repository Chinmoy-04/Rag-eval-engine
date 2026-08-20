# Decisions

Chronological record of why the code looks the way it does.

## 2026-07-10 — Phase 1 scaffold lives in the repo root

The original prompt nested the project under `rag-eval-engine/`. We keep the package in `e:\Projects\RAG` so the workspace is the app, not a wrapper folder.

Config is centralized in `src/config.py`. LLM vendors are selected with `LLM_PROVIDER`; keys never live in source.

## 2026-08-17 — Phase 2 ingestion uses local embeddings by default

Ingestion needs an embedding model before any LLM is involved. There is no `.env` with API keys yet, and Anthropic has no embeddings API.

**Choice:** `EMBEDDING_PROVIDER=local` (Chroma ONNX MiniLM / all-MiniLM-L6-v2) as the default, with `openai` as an opt-in. Same vectors are used at query time so retrieval is actually semantic, not a hash stub.

**Tradeoff:** MiniLM is weaker than `text-embedding-3-small`, but it lets us verify the index offline and keeps demo cost at zero. Switching providers requires `--rebuild` because vector dimensions differ (384 vs 1536).

**Idempotency:** Re-running `ingest` skips work when corpus files, chunk size/overlap, collection name, and embedding backend match `data/chroma_db/ingest_meta.json`. `--rebuild` or a changed fingerprint wipes and rebuilds so we never duplicate vectors.

**Corpus:** Synthetic HelixForge policies (~16 docs) instead of live Wikipedia downloads. Offline, stable facts, and overlapping policies (PTO × on-call, travel × expenses) that later support multi-hop eval questions.

**CLI `query`:** Not in the original command list, but Phase 2 requires proving retrieval works. It returns chunks only — no generator — so we can learn retrieval separately from generation.

## 2026-08-18 — Rebuild must delete the Chroma collection, not the folder

Re-seeding updates file mtimes, so the corpus fingerprint changes and ingest rebuilds. The first rebuild used `shutil.rmtree(..., ignore_errors=True)` after `PersistentClient` already had SQLite open. On Windows that wipe is a silent no-op; LlamaIndex then appended 16 new vectors onto the old 16. Queries returned duplicate chunks with identical scores.

**Fix:** delete the named collection on the same cached client, then insert. Log a warning if `collection.count() != len(nodes)`.

## 2026-08-18 — Phase 3 baseline RAG uses Groq + local embeddings

OpenAI/Anthropic have no reliable free API for this project. Default `LLM_PROVIDER` is `groq` with `openai/gpt-oss-20b`; embeddings stay `local` so ingest does not need a paid embed API.

Groq retired `llama-3.1-8b-instant` and `llama-3.3-70b-versatile` on 2026-08-16 for free/developer tiers. We follow Groq's replacement IDs. LiteLLM receives `groq/openai/gpt-oss-20b`.

Windows cp1252 consoles cannot print some model punctuation (e.g. U+2011). CLI stdout is reconfigured to UTF-8 with replacement so `ask` does not crash after a successful generation.

Smoke checks normalize unicode whitespace. `gpt-oss-20b` emitted a narrow no-break space in "Mara Chen", which made a naive `"mara chen" in answer` fail even though the answer was correct.

Generation goes through `litellm` (`src/llm.py`) so pipeline code is vendor-agnostic. The `baseline` config uses top-k=4, temperature=0, and a grounding prompt that forbids answering outside retrieved context.

CLI: `ask` is retrieve+generate; `query` stays retrieve-only so we can still debug retrieval vs generation. `smoke` checks three known facts before we trust the pipeline.

`degraded` / `optimized` are still Phase 7.

## 2026-08-18 — Early Streamlit Ask UI (not the full Phase 9 dashboard)

The user wanted a real UI to ask questions before eval storage exists. We ship `src/dashboard/app.py` as an Ask chat that calls the same `run_pipeline` as the CLI. Suggested questions live in `src/rag_pipeline/questions.py` so CLI and UI share them later.

Phase 9 still adds run comparison, metric charts, and failure drill-down — those need SQLite eval results from Phases 4–6.

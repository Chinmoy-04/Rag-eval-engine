# Flow

Current execution paths after Phase 3.

## CLI entry

`uv run python -m src.cli <command>` → `src/cli.py` (Typer)

Logging: `setup_logging()` → console + rotating `logs/rag_eval.log`.

## Seed corpus

`uv run python scripts/seed_sample_corpus.py`

- Writes HelixForge policy files into `data/raw_docs/` (`.md` and `.txt`).
- Overwrites by default so the demo corpus stays canonical.

## Ingest (`python -m src.cli ingest [--rebuild]`)

```
cli.ingest
  → load_config()
  → indexer.run_ingestion(config, rebuild=...)
       → current_ingest_signature()  (chunk settings + corpus hash + embedding id)
       → if unchanged and collection non-empty: return skipped
       → else client.delete_collection(...) on the same PersistentClient
       → loader.load_and_chunk()
            → SimpleDirectoryReader (.txt/.md/.pdf)
            → SentenceSplitter(chunk_size, chunk_overlap)
       → get_or_create_collection + VectorStoreIndex(...)
       → write ingest_meta.json
       → warn if vector count != node count
```

Errors: missing corpus raises `FileNotFoundError` with a seed hint. A single failed file does not use `raise_on_error`; LlamaIndex skips unreadable files unless we change that later.

Side effects: creates/replaces `data/chroma_db/`, may download ONNX MiniLM weights to `~/.cache/chroma` on first local embed.

## Query (`python -m src.cli query "..." [--top-k N]`)

```
cli.query
  → indexer.query_index()
       → load_vector_index()  (open existing Chroma collection)
       → embed query with the same embed_model used at ingest
       → retriever.retrieve()  (cosine nearest chunks)
  → print score + source + text
```

No LLM call. Empty index: CLI exits 1 with an ingest hint.

## Ask (`python -m src.cli ask "..." [--pipeline-config baseline] [--show-contexts]`)

```
cli.ask
  → rag_pipeline.run_pipeline()
       → indexer.query_index()          (same retriever as `query`)
       → format chunks into a grounded prompt
       → llm.generate_completion()      (litellm → Groq by default)
  → print answer, latency, sources
```

Errors: missing `GROQ_API_KEY` raises before the HTTP call. Unknown `--pipeline-config` exits 1. Empty LLM content raises `RuntimeError`.

Side effects: one Groq chat completion per question (counts against free-tier RPM).

## Smoke (`python -m src.cli smoke`)

Runs three hardcoded questions through `baseline` and checks the answer text for known facts (18 days PTO, stipend pause, CEO Mara Chen). Exit 1 if any case fails.

## Serve (`python -m src.cli serve`)

```
cli.serve
  → streamlit run src/dashboard/app.py
       → load_config / collection_count
       → chat or suggested question
       → rag_pipeline.run_pipeline()  (same as `ask`)
```

Sidebar: pipeline name, show-chunks toggle, suggested questions. Conversation lives in Streamlit session state (not SQLite yet).

## Not wired yet

`generate-testset`, `run-eval` still import stubs. `degraded` / `optimized` are Phase 7. Eval dashboard views are Phase 9.

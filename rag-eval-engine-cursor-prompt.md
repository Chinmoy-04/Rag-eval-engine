# Cursor Build Prompt: High-Throughput RAG Evaluation Engine

> Paste everything below this line into Cursor (Composer / Agent mode). It's written as a direct instruction to the coding agent.

---

## Role

You are a senior LLMOps / Python engineer. Build a production-grade, end-to-end **RAG Evaluation Engine**: a system that ingests a document corpus, synthetically generates a large test set of Q&A pairs, runs those questions through a configurable RAG pipeline, scores the outputs on standard RAG evaluation metrics, and surfaces the results in a dashboard.

This is a portfolio/demo project, but it should be built like real infrastructure: typed, tested, logged, configurable, and resumable — not a notebook glued together.

Work in **phases**. After each phase, run the code, confirm it actually works (no unhandled exceptions, output looks sane), and only then move to the next phase. Do not generate the entire repository in one pass.

---

## 1. Tech Stack

- **Python 3.11+**, dependency management via `uv` (fallback to `poetry` if `uv` isn't available)
- **LlamaIndex** — document loading, chunking, indexing, and as the retriever/query-engine layer for the RAG pipeline under test
- **ChromaDB** (local, persistent client) — vector store
- **Ragas** — synthetic test set generation *and* evaluation metrics (Faithfulness, Answer Relevancy, Context Precision, Context Recall, Context Entity Recall, Answer Correctness)
- **LLM provider abstraction** — do not hardcode one vendor. Read `LLM_PROVIDER` from `.env` (`openai` or `anthropic`), instantiate the right client accordingly (use `litellm` if it simplifies this, otherwise native SDKs behind a thin interface). Same for the embedding model.
- **SQLModel** (SQLAlchemy) + SQLite — persist runs, questions, retrieved contexts, generated answers, and per-metric scores
- **Streamlit** + **Plotly** — dashboard
- **asyncio + tenacity** — concurrent, rate-limited, retry-safe batch calls to the judge LLM (this is the "high-throughput" part — don't evaluate questions one at a time synchronously)
- **pytest** — tests
- **python-dotenv** — config

**Important:** Ragas' and LlamaIndex's public APIs change fairly often between versions (import paths, class names for test set generation especially). Before writing code against either library, run `pip show ragas` / `pip show llama-index` to confirm the installed version, and check that version's actual API (via `pip show`, installed package source, or docs) rather than assuming a remembered import path. If something doesn't import, don't guess — inspect the installed package.

---

## 2. Repository Structure

```
rag-eval-engine/
├── .env.example
├── pyproject.toml
├── README.md
├── data/
│   ├── raw_docs/                # sample corpus lives here
│   └── chroma_db/                # persisted vector store (gitignored)
├── src/
│   ├── ingestion/
│   │   ├── loader.py             # load & chunk docs via LlamaIndex
│   │   └── indexer.py            # build/persist Chroma index
│   ├── testset/
│   │   └── generate.py           # Ragas synthetic testset generation
│   ├── rag_pipeline/
│   │   ├── pipeline.py           # configurable RAG: retriever + generator
│   │   └── configs.py            # named pipeline configs (see section 5)
│   ├── evaluation/
│   │   ├── run_eval.py           # orchestrates a full batch evaluation run
│   │   ├── metrics.py            # Ragas metric wrappers
│   │   └── async_batch.py        # concurrency, rate limiting, retries, progress
│   ├── storage/
│   │   ├── models.py             # SQLModel schema
│   │   └── db.py                 # engine/session helpers
│   ├── dashboard/
│   │   └── app.py                # Streamlit app
│   ├── config.py                 # env/config loading, provider abstraction
│   └── cli.py                    # `python -m src.cli <command>`
├── scripts/
│   └── seed_sample_corpus.py     # downloads/copies a small demo corpus
└── tests/
    ├── test_ingestion.py
    ├── test_pipeline.py
    ├── test_evaluation.py
    └── test_storage.py
```

---

## 3. Data Model (storage/models.py)

Three related tables, minimum:

- **Run** — `id`, `created_at`, `pipeline_config_name`, `corpus_name`, `num_questions`, `status`, `notes`
- **TestItem** — `id`, `run_id` (FK), `question`, `ground_truth_answer`, `reference_contexts` (JSON list), `question_type` (e.g. simple / multi-hop / reasoning — Ragas' synthetic generator supports evolution types, use them)
- **EvalResult** — `id`, `test_item_id` (FK), `generated_answer`, `retrieved_contexts` (JSON list), `faithfulness`, `answer_relevancy`, `context_precision`, `context_recall`, `context_entity_recall`, `answer_correctness`, `latency_ms`, `error` (nullable)

Store everything — don't just compute an aggregate score and discard the raw generations. The dashboard needs to drill into individual failures.

---

## 4. Module Requirements

### 4.1 Ingestion (`src/ingestion/`)
- Load documents from `data/raw_docs/` (support `.txt`, `.md`, `.pdf` at minimum via LlamaIndex's `SimpleDirectoryReader`)
- Chunk with a configurable chunk size/overlap
- Embed and persist into a local Chroma collection
- Should be idempotent — re-running shouldn't duplicate the index; support a `--rebuild` flag

### 4.2 Synthetic Test Set Generation (`src/testset/generate.py`)
- Use Ragas' test set generator against the ingested document set to produce N question/ground-truth/reference-context triples
- Support a mix of question complexity (simple fact lookup, multi-hop/reasoning, and — if the installed Ragas version supports it — questions designed to have partial/no answer in the corpus, to test whether the RAG system correctly abstains instead of hallucinating)
- Persist the generated test set to the DB (`TestItem` rows) tied to a `Run`, and also cache it to disk as JSON so regenerating test questions doesn't require burning API calls every run
- CLI: `python -m src.cli generate-testset --n 200`

### 4.3 RAG Pipeline Under Test (`src/rag_pipeline/`)
This is the system being evaluated — build it as **swappable named configs**, not one fixed pipeline. At minimum implement:

- `"baseline"` — reasonable defaults: sensible chunk size, top-k retrieval (e.g. k=4), no reranking, a straightforward "answer using only the provided context" prompt
- `"degraded"` — intentionally worse: large/naive chunking, top-k=1, a prompt that doesn't instruct the model to stick to context (encourages hallucination) — this exists so the dashboard has a clear "bad" run to contrast against a "good" run
- `"optimized"` — improved: smaller overlapping chunks, higher top-k with a reranker (cross-encoder or LLM-based rerank), a stricter grounding prompt with explicit "say you don't know if the context doesn't contain the answer" instruction

Each config takes a query and returns `{answer: str, retrieved_contexts: list[str], latency_ms: float}`. This is what makes the "dummy" system meaningfully testable — the whole point of the project is showing that evaluation scores actually move when you change the pipeline.

### 4.4 Evaluation Engine (`src/evaluation/`)
- Take a `Run`'s `TestItem`s, run each question through the selected pipeline config, then score the (question, generated_answer, retrieved_contexts, ground_truth) tuple using Ragas metrics: **Faithfulness, Answer Relevancy, Context Precision, Context Recall** at minimum; add **Context Entity Recall** and **Answer Correctness** if the installed Ragas version supports them cleanly
- **This must be concurrent, not a sequential for-loop.** Use `asyncio` with a bounded semaphore (configurable concurrency, default ~5-10) and `tenacity` retries with exponential backoff for rate limits/transient errors. Show a live progress bar (`tqdm` or Streamlit's own progress element if run from the dashboard).
- Track and log per-item latency and any errors without letting one failed item kill the whole batch — write partial results and mark failed items clearly rather than crashing
- Persist every result to `EvalResult`
- CLI: `python -m src.cli run-eval --run-id <id> --pipeline-config optimized --concurrency 8`

### 4.5 Dashboard (`src/dashboard/app.py`, Streamlit)
Minimum views:
1. **Run overview** — table of all runs with aggregate scores per metric, filterable/sortable, so you can compare `baseline` vs `degraded` vs `optimized` side by side
2. **Metric breakdown** — bar/radar chart of the four-to-six core metrics for a selected run (Plotly)
3. **Trend over time** — line chart if multiple runs of the same config exist
4. **Failure drill-down** — table of individual questions sorted by lowest faithfulness/relevancy, showing question, generated answer, retrieved context, ground truth, and per-metric score, so a viewer can *see* a hallucination and see exactly which metric caught it
5. **Trigger a new run from the UI** — a button to kick off `generate-testset` and/or `run-eval` against a chosen pipeline config, with the async progress visible in the UI

### 4.6 CLI (`src/cli.py`)
Single entry point with subcommands: `ingest`, `generate-testset`, `run-eval`, `serve` (launches Streamlit). Use `click` or `typer`.

---

## 5. Non-Functional Requirements
- All API keys and provider selection via `.env` (ship a `.env.example`); never hardcode keys
- Structured logging (`logging` module, not print statements) to both console and a rotating log file
- Type hints throughout; docstrings on public functions
- Cache LLM/embedding calls where sensible (e.g. don't regenerate the test set or re-embed the corpus if nothing changed) to control cost during development
- Config values (chunk size, top-k, concurrency, model names) centralized in `src/config.py`, not scattered as magic numbers
- Rough cost/latency tracking surfaced somewhere (even just logged per run) — this is an LLMOps project, cost-awareness is part of the pitch

---

## 6. Sample Corpus
Include `scripts/seed_sample_corpus.py` that populates `data/raw_docs/` with a small (~10-20 document) public-domain or synthetic corpus suitable for demoing — e.g. a handful of Wikipedia articles on a coherent topic, or generated company-policy-style documents. Keep it small enough that ingestion + a 100-200 question test set run in a few minutes, not hours.

---

## 7. Testing
- Unit tests for chunking/loading logic, the pipeline configs (mock the LLM calls), and the DB layer
- At least one integration-style test that runs a tiny end-to-end flow (3-5 questions) against a stubbed/mocked LLM so the whole pipeline is exercised without burning real API calls in CI

---

## 8. README
Write a README covering: what the project does and why it matters (the "biggest bottleneck in RAG deployment is proving accuracy" framing), setup instructions, how to run each CLI command, how to launch the dashboard, a screenshot placeholder, and a short section explaining what each Ragas metric measures in plain English (Faithfulness = does the answer avoid contradicting/inventing beyond the retrieved context; Answer Relevancy = does the answer actually address the question; Context Precision/Recall = did retrieval fetch the right, and only the right, information).

---

## 9. Build Order (do this in order, verify each step before continuing)

1. Scaffold repo structure, `pyproject.toml`, `.env.example`, `src/config.py` with provider abstraction. Confirm `python -m src.cli --help` runs.
2. Seed sample corpus + build ingestion module. Confirm a Chroma index gets created and you can manually query it.
3. Build one pipeline config (`baseline`) and confirm it returns sane answers for a few hardcoded test questions.
4. Build the storage layer (SQLModel schema + DB helpers). Confirm tables create correctly.
5. Build synthetic test set generation against the small corpus (start with N=10 to avoid burning tokens while debugging). Confirm generated questions look reasonable and get persisted.
6. Build the evaluation engine against that small test set, sequential first to confirm metrics compute correctly, *then* add the async/concurrent batching.
7. Add the `degraded` and `optimized` pipeline configs. Run all three against the same test set and confirm the scores actually differentiate (if `degraded` doesn't score visibly worse, fix the config until it does — this contrast is the whole demo).
8. Scale the test set generation up to ~150-200 questions and run a full evaluation batch.
9. Build the Streamlit dashboard against the populated DB.
10. Write tests, polish logging/error handling, write the README.

---

## 10. Acceptance Criteria
- [ ] `python -m src.cli ingest` builds a persisted vector index from `data/raw_docs/`
- [ ] `python -m src.cli generate-testset --n 150` produces and stores a mixed-difficulty synthetic test set
- [ ] `python -m src.cli run-eval` executes concurrently (visibly faster than naive sequential — log or display elapsed time) and produces Faithfulness/Answer Relevancy/Context Precision/Context Recall for every item
- [ ] Running eval against `baseline`, `degraded`, and `optimized` configs produces meaningfully different aggregate scores, in the expected direction
- [ ] `python -m src.cli serve` launches a dashboard showing run comparisons, per-metric charts, and a failure drill-down table with real hallucination examples visible
- [ ] `pytest` passes
- [ ] README is complete enough that a stranger could clone and run this in under 10 minutes given API keys

---

Build this now, starting with Phase 1.

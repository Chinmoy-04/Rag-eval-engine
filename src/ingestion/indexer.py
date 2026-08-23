"""Build and persist a Chroma vector index from chunked documents."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import chromadb
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.schema import NodeWithScore, TextNode
from llama_index.vector_stores.chroma import ChromaVectorStore

from src.config import AppConfig, CHROMA_DIR, load_config
from src.ingestion.embeddings import build_embed_model, embedding_fingerprint
from src.ingestion.loader import corpus_fingerprint, load_and_chunk

logger = logging.getLogger("rag_eval")

BM25_NODES_NAME = "nodes_bm25.jsonl"

INGEST_META_NAME = "ingest_meta.json"


def _meta_path(persist_dir: Path) -> Path:
    return persist_dir / INGEST_META_NAME


def _read_meta(persist_dir: Path) -> dict[str, Any] | None:
    path = _meta_path(persist_dir)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_meta(persist_dir: Path, payload: dict[str, Any]) -> None:
    persist_dir.mkdir(parents=True, exist_ok=True)
    _meta_path(persist_dir).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def current_ingest_signature(config: AppConfig) -> dict[str, Any]:
    """Settings + corpus hash that must match for a cached index to be reused."""
    return {
        "chunk_size": config.chunk_size,
        "chunk_overlap": config.chunk_overlap,
        "collection": config.chroma_collection,
        "embedding": embedding_fingerprint(config),
        "corpus_sha256": corpus_fingerprint(),
    }


def _signatures_match(stored: dict[str, Any] | None, current: dict[str, Any]) -> bool:
    if not stored:
        return False
    return all(stored.get(key) == value for key, value in current.items())


def _bm25_nodes_path(persist_dir: Path) -> Path:
    return persist_dir / BM25_NODES_NAME


def write_bm25_nodes(nodes: list[TextNode], persist_dir: Path | None = None) -> None:
    """Persist chunked nodes for BM25 retrieval (id, text, metadata per line)."""
    persist = persist_dir or CHROMA_DIR
    persist.mkdir(parents=True, exist_ok=True)
    path = _bm25_nodes_path(persist)
    with path.open("w", encoding="utf-8") as handle:
        for i, node in enumerate(nodes):
            payload = {
                "id": node.node_id or f"node-{i}",
                "text": node.get_content(),
                "metadata": dict(node.metadata or {}),
            }
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    logger.info("Persisted BM25 node cache (%d nodes) to %s", len(nodes), path)


_bm25_nodes_cache: list[TextNode] | None = None


def get_bm25_nodes(config: AppConfig | None = None) -> list[TextNode]:
    """Load BM25 node cache written during ingest."""
    global _bm25_nodes_cache
    if _bm25_nodes_cache is not None:
        return _bm25_nodes_cache

    if config is None:
        config = load_config()
    path = _bm25_nodes_path(CHROMA_DIR)
    if not path.exists():
        logger.warning("BM25 cache missing at %s — run: uv run python -m src.cli ingest --rebuild", path)
        _bm25_nodes_cache = []
        return _bm25_nodes_cache

    nodes: list[TextNode] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            nodes.append(
                TextNode(
                    text=row.get("text") or "",
                    metadata=row.get("metadata") or {},
                    id_=row.get("id"),
                )
            )
    _bm25_nodes_cache = nodes
    logger.info("Loaded %d BM25 nodes from cache", len(nodes))
    return nodes


def get_chroma_client(persist_dir: Path | None = None):
    """Persistent local Chroma client."""
    path = persist_dir or CHROMA_DIR
    path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(path))


def _delete_collection(client: Any, name: str) -> bool:
    """Drop a collection on an already-open client. Returns True if it existed."""
    try:
        client.delete_collection(name)
        logger.info("Deleted existing collection '%s'", name)
        return True
    except Exception:
        logger.info("Collection '%s' did not exist; nothing to delete", name)
        return False


def get_collection(
    config: AppConfig,
    persist_dir: Path | None = None,
    *,
    rebuild: bool = False,
):
    """Return the Chroma collection, deleting it first when rebuild=True."""
    client = get_chroma_client(persist_dir)
    if rebuild:
        _delete_collection(client, config.chroma_collection)
    return client.get_or_create_collection(name=config.chroma_collection)


def collection_count(config: AppConfig, persist_dir: Path | None = None) -> int:
    client = get_chroma_client(persist_dir)
    try:
        collection = client.get_collection(config.chroma_collection)
    except Exception:
        return 0
    return int(collection.count())


def load_vector_index(config: AppConfig | None = None) -> VectorStoreIndex:
    """Open the persisted Chroma collection as a LlamaIndex VectorStoreIndex."""
    if config is None:
        config = load_config()
    collection = get_collection(config)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    embed_model = build_embed_model(config)
    return VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)


def query_index(
    question: str,
    config: AppConfig | None = None,
    top_k: int | None = None,
) -> list[NodeWithScore]:
    """Retrieve the top-k most similar chunks for a question (no LLM generation)."""
    if config is None:
        config = load_config()
    k = top_k or config.default_top_k
    index = load_vector_index(config)
    retriever = index.as_retriever(similarity_top_k=k)
    results = retriever.retrieve(question)
    logger.info("Retrieved %d chunks for query: %s", len(results), question[:80])
    return results


def run_ingestion(
    config: AppConfig,
    *,
    rebuild: bool = False,
    persist_dir: Path | None = None,
) -> dict[str, Any]:
    """Embed chunks into Chroma. Skip work when the corpus and settings are unchanged."""
    persist = persist_dir or CHROMA_DIR
    signature = current_ingest_signature(config)
    stored = _read_meta(persist)
    existing = collection_count(config, persist)

    if not rebuild and existing > 0 and _signatures_match(stored, signature):
        logger.info(
            "Index already up to date (%d vectors). Pass --rebuild to force.",
            existing,
        )
        return {"status": "skipped", "num_vectors": existing, **signature}

    if existing > 0:
        logger.info(
            "Rebuilding index (was %d vectors, rebuild=%s).",
            existing,
            rebuild,
        )

    # Delete the collection on the *same* PersistentClient. Chroma caches
    # clients per path; wiping the folder with shutil while a client is open
    # often fails on Windows and then new chunks are appended (duplicates).
    client = get_chroma_client(persist)
    if existing > 0:
        _delete_collection(client, config.chroma_collection)

    nodes: list[TextNode] = load_and_chunk(config)
    collection = client.get_or_create_collection(name=config.chroma_collection)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    embed_model = build_embed_model(config)

    logger.info("Embedding %d chunks with %s", len(nodes), signature["embedding"])
    VectorStoreIndex(
        nodes,
        storage_context=storage_context,
        embed_model=embed_model,
        show_progress=True,
    )

    count = int(collection.count())
    if count != len(nodes):
        logger.warning(
            "Vector count %d does not match node count %d — index may contain leftovers",
            count,
            len(nodes),
        )
    meta = {**signature, "num_vectors": count, "num_nodes": len(nodes)}
    write_bm25_nodes(nodes, persist)
    _write_meta(persist, meta)
    logger.info("Persisted %d vectors to %s", count, persist)
    return {"status": "built", **meta}

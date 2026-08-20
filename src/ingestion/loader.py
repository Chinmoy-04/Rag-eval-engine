"""Load and chunk documents from data/raw_docs/ via LlamaIndex."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from llama_index.core import Document, SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode

from src.config import AppConfig, RAW_DOCS_DIR

logger = logging.getLogger("rag_eval")

SUPPORTED_EXTS = {".txt", ".md", ".pdf"}


def list_corpus_files(docs_dir: Path | None = None) -> list[Path]:
    """Return supported corpus files, sorted for stable fingerprints."""
    root = docs_dir or RAW_DOCS_DIR
    if not root.exists():
        return []
    files = [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTS
    ]
    return sorted(files)


def corpus_fingerprint(docs_dir: Path | None = None) -> str:
    """Hash file names, sizes, and mtimes so we can skip unchanged ingests."""
    hasher = hashlib.sha256()
    for path in list_corpus_files(docs_dir):
        stat = path.stat()
        hasher.update(path.name.encode("utf-8"))
        hasher.update(str(stat.st_size).encode("ascii"))
        hasher.update(str(int(stat.st_mtime)).encode("ascii"))
    return hasher.hexdigest()


def load_documents(docs_dir: Path | None = None) -> list[Document]:
    """Load .txt, .md, and .pdf files with LlamaIndex SimpleDirectoryReader."""
    root = docs_dir or RAW_DOCS_DIR
    files = list_corpus_files(root)
    if not files:
        raise FileNotFoundError(
            f"No .txt/.md/.pdf files in {root}. "
            "Run: uv run python scripts/seed_sample_corpus.py"
        )

    logger.info("Loading %d documents from %s", len(files), root)
    reader = SimpleDirectoryReader(
        input_dir=str(root),
        required_exts=sorted(SUPPORTED_EXTS),
        recursive=True,
        filename_as_id=True,
        exclude_hidden=True,
    )
    documents = reader.load_data()
    logger.info("Loaded %d LlamaIndex documents", len(documents))
    return documents


def chunk_documents(
    documents: list[Document],
    chunk_size: int,
    chunk_overlap: int,
) -> list[TextNode]:
    """Split documents into overlapping sentence-aware chunks.

    chunk_size / chunk_overlap are in *tokens* (LlamaIndex SentenceSplitter),
    not characters. Overlap keeps a fact that sits on a chunk boundary
    retrievable from either neighboring chunk.
    """
    splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    nodes = splitter.get_nodes_from_documents(documents)
    logger.info(
        "Chunked %d documents into %d nodes (size=%d, overlap=%d)",
        len(documents),
        len(nodes),
        chunk_size,
        chunk_overlap,
    )
    return nodes


def load_and_chunk(config: AppConfig, docs_dir: Path | None = None) -> list[TextNode]:
    """Load the corpus and return chunk nodes using config chunk settings."""
    documents = load_documents(docs_dir)
    return chunk_documents(documents, config.chunk_size, config.chunk_overlap)

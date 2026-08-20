"""Document loading, chunking, and vector indexing."""

from src.ingestion.indexer import query_index, run_ingestion
from src.ingestion.loader import chunk_documents, load_documents

__all__ = [
    "chunk_documents",
    "load_documents",
    "query_index",
    "run_ingestion",
]

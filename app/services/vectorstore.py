from typing import List
from functools import lru_cache

from pinecone import Pinecone, ServerlessSpec

from app.config import settings
from app.services.embeddings import embed_texts, embed_query

_pc = Pinecone(api_key=settings.pinecone_api_key)


@lru_cache(maxsize=1)
def get_index():
    """Return a handle to the Pinecone index, creating it if needed."""
    existing = [i["name"] for i in _pc.list_indexes()]
    if settings.pinecone_index_name not in existing:
        _pc.create_index(
            name=settings.pinecone_index_name,
            dimension=settings.embedding_dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud=settings.pinecone_cloud, region=settings.pinecone_region),
        )
    return _pc.Index(settings.pinecone_index_name)


def upsert_chunks(session_id: str, chunks: List[str]) -> int:
    """Embed and upsert chunks under a per-session namespace. Returns count stored."""
    if not chunks:
        return 0
    index = get_index()
    vectors = embed_texts(chunks)
    records = [
        {
            "id": f"{session_id}-{i}",
            "values": vec,
            "metadata": {"text": chunk, "chunk_index": i},
        }
        for i, (chunk, vec) in enumerate(zip(chunks, vectors))
    ]
    index.upsert(vectors=records, namespace=session_id)
    return len(records)


def query_chunks(session_id: str, query_text: str, top_k: int = 6) -> List[str]:
    """Semantic search within a session's namespace, returns matched chunk texts."""
    index = get_index()
    vector = embed_query(query_text)
    result = index.query(
        vector=vector,
        top_k=top_k,
        namespace=session_id,
        include_metadata=True,
    )
    matches = sorted(result.get("matches", []), key=lambda m: m["metadata"].get("chunk_index", 0))
    return [m["metadata"]["text"] for m in matches]


def delete_session(session_id: str) -> None:
    index = get_index()
    try:
        index.delete(delete_all=True, namespace=session_id)
    except Exception:
        # namespace may not exist yet / already empty - safe to ignore
        pass

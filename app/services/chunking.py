from typing import List
from functools import lru_cache
import tiktoken


@lru_cache(maxsize=1)
def _get_encoding():
    return tiktoken.get_encoding("cl100k_base")


def chunk_text(text: str, chunk_tokens: int = 700, overlap_tokens: int = 100) -> List[str]:
    """Split text into overlapping token-bounded chunks, good for embeddings."""
    encoding = _get_encoding()
    tokens = encoding.encode(text)
    if not tokens:
        return []

    chunks = []
    start = 0
    n = len(tokens)
    step = max(chunk_tokens - overlap_tokens, 1)

    while start < n:
        end = min(start + chunk_tokens, n)
        chunk = encoding.decode(tokens[start:end])
        if chunk.strip():
            chunks.append(chunk.strip())
        if end == n:
            break
        start += step

    return chunks

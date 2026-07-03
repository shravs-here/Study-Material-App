from typing import List
from openai import OpenAI
from app.config import settings

_client = OpenAI(api_key=settings.openai_api_key)

_BATCH_SIZE = 100


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a list of strings in batches, preserving order."""
    vectors: List[List[float]] = []
    for i in range(0, len(texts), _BATCH_SIZE):
        batch = texts[i : i + _BATCH_SIZE]
        resp = _client.embeddings.create(model=settings.embedding_model, input=batch)
        vectors.extend([d.embedding for d in resp.data])
    return vectors


def embed_query(text: str) -> List[float]:
    return embed_texts([text])[0]

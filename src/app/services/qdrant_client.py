import os
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)
COLLECTION = os.getenv("QDRANT_COLLECTION", "pinkpro_docs")

_client = None
def get_client():
    global _client
    if _client:
        return _client
    _client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    return _client

def ensure_collection(dim: int = 384):
    client = get_client()
    try:
        client.get_collection(COLLECTION)
    except Exception:
        client.recreate_collection(collection_name=COLLECTION, vectors_config={"size": dim, "distance": "Cosine"})

def upsert_documents(vectors: List[List[float]], metadatas: List[dict], ids: List[str]):
    client = get_client()
    points = [PointStruct(id=ids[i], vector=vectors[i], payload=metadatas[i]) for i in range(len(ids))]
    client.upsert(collection_name=COLLECTION, points=points)

def search_similar(query_vector: List[float], top_k: int = 5):
    client = get_client()
    hits = client.search(collection_name=COLLECTION, query_vector=query_vector, limit=top_k)
    # normalize to simple dicts
    out = []
    for h in hits:
        out.append({
            "id": h.id,
            "score": h.score,
            "payload": h.payload
        })
    return out

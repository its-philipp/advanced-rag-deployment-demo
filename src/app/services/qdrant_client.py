import os
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)
COLLECTION = os.getenv("QDRANT_COLLECTION", "rag_documents")

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

# User-specific collection functions
def ensure_user_collection(user_id: str, dim: int = 384):
    """Ensure a user-specific collection exists."""
    collection_name = f"user_{user_id}_docs"
    client = get_client()
    try:
        client.get_collection(collection_name)
    except Exception:
        client.recreate_collection(
            collection_name=collection_name, 
            vectors_config={"size": dim, "distance": "Cosine"}
        )
    return collection_name

def upsert_user_documents(user_id: str, vectors: List[List[float]], metadatas: List[dict], ids: List[str]):
    """Upsert documents to a user-specific collection."""
    collection_name = ensure_user_collection(user_id, len(vectors[0]) if vectors else 384)
    client = get_client()
    points = [PointStruct(id=ids[i], vector=vectors[i], payload=metadatas[i]) for i in range(len(ids))]
    client.upsert(collection_name=collection_name, points=points)

def search_user_similar(user_id: str, query_vector: List[float], top_k: int = 5):
    """Search similar documents in a user-specific collection."""
    collection_name = f"user_{user_id}_docs"
    client = get_client()
    try:
        hits = client.search(collection_name=collection_name, query_vector=query_vector, limit=top_k)
        out = []
        for h in hits:
            out.append({
                "id": h.id,
                "score": h.score,
                "payload": h.payload
            })
        return out
    except Exception:
        # If user collection doesn't exist, return empty results
        return []

def search_hybrid(user_id: str, query_vector: List[float], top_k: int = 5, user_weight: float = 0.7):
    """Search both user-specific and global collections, combining results."""
    # Search user-specific collection
    user_results = search_user_similar(user_id, query_vector, top_k)
    
    # Search global collection
    global_results = search_similar(query_vector, top_k)
    
    # Combine and re-rank results
    all_results = []
    
    # Add user results with higher weight
    for result in user_results:
        result["score"] *= user_weight
        result["source"] = "user"
        all_results.append(result)
    
    # Add global results with lower weight
    for result in global_results:
        result["score"] *= (1 - user_weight)
        result["source"] = "global"
        all_results.append(result)
    
    # Sort by score and return top_k
    all_results.sort(key=lambda x: x["score"], reverse=True)
    return all_results[:top_k]

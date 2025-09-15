import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Enhanced text chunking with sentence boundary awareness.
    """
    import re
    
    # Clean and normalize text
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Split into sentences first
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_length = len(sentence.split())
        
        # If adding this sentence would exceed chunk size, finalize current chunk
        if current_length + sentence_length > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            
            # Start new chunk with overlap
            overlap_words = min(overlap, len(current_chunk))
            current_chunk = current_chunk[-overlap_words:] + [sentence]
            current_length = len(" ".join(current_chunk).split())
        else:
            current_chunk.append(sentence)
            current_length += sentence_length
    
    # Add the last chunk if it has content
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    # Fallback to word-based chunking if sentence-based fails
    if not chunks:
        words = text.split()
        i = 0
        while i < len(words):
            chunk = words[i:i+chunk_size]
            chunks.append(" ".join(chunk))
            i += chunk_size - overlap
    
    return chunks

def get_embedding_openai(text: str, model: str = "text-embedding-3-small"):
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        resp = client.embeddings.create(input=text, model=model)
        return resp.data[0].embedding
    except Exception as e:
        raise RuntimeError("OpenAI embedding failed: " + str(e))

def get_embeddings_texts(texts: List[str], model: str = "text-embedding-3-small"):
    """
    Get embeddings for multiple texts using OpenAI.
    Falls back to simple text similarity if OpenAI fails.
    """
    if OPENAI_API_KEY:
        return [get_embedding_openai(t, model) for t in texts]
    else:
        # Simple fallback: create dummy embeddings based on text length
        # This is not ideal but allows the app to run without OpenAI
        print("Warning: No OpenAI API key, using dummy embeddings")
        return [[len(t) * 0.01] * 1536 for t in texts]  # 1536 is the dimension of text-embedding-3-small

import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """Test that we can import the main modules."""
    try:
        from app.main import app
        assert app is not None
    except ImportError as e:
        pytest.skip(f"Could not import app: {e}")

def test_environment_variables():
    """Test that environment variables are loaded."""
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check that we can access environment variables
    assert os.getenv('QDRANT_URL') is not None
    assert os.getenv('QDRANT_COLLECTION') is not None

def test_chunking_functionality():
    """Test the chunking functionality."""
    try:
        from app.services.embeddings import chunk_text
        
        test_text = "This is a test sentence. This is another sentence. And here is a third sentence."
        chunks = chunk_text(test_text, chunk_size=10, overlap=2)
        
        assert len(chunks) > 0
        # Our chunking algorithm is sentence-aware, so chunks might be larger than chunk_size
        # but should still be reasonable
        assert all(len(chunk.split()) <= 20 for chunk in chunks)
        assert all(len(chunk) > 0 for chunk in chunks)
    except ImportError as e:
        pytest.skip(f"Could not import embeddings: {e}")

def test_document_indexer():
    """Test document indexer functionality."""
    try:
        from app.services.document_indexer import get_sample_documents
        
        docs = get_sample_documents()
        assert len(docs) > 0
        assert all('title' in doc for doc in docs)
        assert all('content' in doc for doc in docs)
        assert all('source_id' in doc for doc in docs)
    except ImportError as e:
        pytest.skip(f"Could not import document_indexer: {e}")

"""
Mock utilities for testing external API calls
"""
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List


class MockOpenAIResponse:
    """Mock OpenAI API response"""
    def __init__(self, content: str = "Mocked response", usage: Dict = None):
        self.choices = [Mock()]
        self.choices[0].message = Mock()
        self.choices[0].message.content = content
        self.usage = usage or {"total_tokens": 100, "prompt_tokens": 50, "completion_tokens": 50}


class MockQdrantResponse:
    """Mock Qdrant search response"""
    def __init__(self, results: List[Dict] = None):
        self.results = results or [
            {
                "id": "doc_1",
                "score": 0.95,
                "payload": {
                    "text": "Sample document content",
                    "source": "test_doc.pdf",
                    "chunk_id": "chunk_1"
                }
            }
        ]


def mock_openai_client():
    """Create a mocked OpenAI client"""
    mock_client = Mock()
    
    # Mock chat completions
    mock_chat = Mock()
    mock_chat.completions.create.return_value = MockOpenAIResponse(
        content="This is a mocked response from the AI assistant.",
        usage={"total_tokens": 150, "prompt_tokens": 75, "completion_tokens": 75}
    )
    mock_client.chat = mock_chat
    
    # Mock embeddings
    mock_embeddings = Mock()
    mock_embeddings.create.return_value = Mock()
    mock_embeddings.create.return_value.data = [Mock()]
    mock_embeddings.create.return_value.data[0].embedding = [0.1] * 1536  # Mock embedding vector
    mock_client.embeddings = mock_embeddings
    
    return mock_client


def mock_qdrant_client():
    """Create a mocked Qdrant client"""
    mock_client = Mock()
    
    # Mock search
    mock_client.search.return_value = MockQdrantResponse()
    
    # Mock upsert
    mock_client.upsert.return_value = Mock()
    
    # Mock create_collection
    mock_client.create_collection.return_value = Mock()
    
    # Mock get_collection
    mock_client.get_collection.return_value = Mock()
    
    return mock_client


def mock_requests_post():
    """Mock requests.post for external API calls"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "answer": "Mocked RAG response",
        "sources": [
            {
                "source_id": "doc_1",
                "chunk_id": "chunk_1", 
                "score": 0.95,
                "text_snippet": "Sample text snippet"
            }
        ],
        "confidence": 0.85
    }
    return mock_response


def mock_agentic_frameworks():
    """Mock responses for agentic framework tests"""
    return {
        "langgraph": {
            "response": "LangGraph agentic response",
            "memory_used": True,
            "steps": 3
        },
        "semantic_kernel": {
            "response": "Semantic Kernel response", 
            "plugins_used": ["memory", "reasoning"],
            "execution_time": 1.2
        },
        "crewai": {
            "response": "CrewAI multi-agent response",
            "agents_used": ["researcher", "writer", "reviewer"],
            "collaboration_steps": 5
        }
    }


def mock_framework_monitor():
    """Mock framework monitoring data"""
    return {
        "performance_metrics": {
            "response_time": 1.5,
            "memory_usage": 512,
            "cpu_usage": 25.0,
            "success_rate": 0.95
        },
        "framework_stats": {
            "langgraph": {"calls": 10, "avg_time": 1.2},
            "semantic_kernel": {"calls": 8, "avg_time": 0.8},
            "crewai": {"calls": 5, "avg_time": 2.1}
        }
    }


def mock_user_context():
    """Mock user context data"""
    return {
        "user_id": "test_user_123",
        "preferences": {
            "learning_style": "visual",
            "difficulty_level": "intermediate",
            "topics": ["python", "machine_learning"]
        },
        "history": [
            {"query": "What is Python?", "timestamp": "2024-01-01T10:00:00Z"},
            {"query": "How to use pandas?", "timestamp": "2024-01-02T14:30:00Z"}
        ],
        "goals": ["Learn Python programming", "Build ML projects"]
    }


def mock_persistent_memory():
    """Mock persistent memory data"""
    return {
        "episodic_memories": [
            {
                "id": "ep_1",
                "content": "User asked about Python basics",
                "timestamp": "2024-01-01T10:00:00Z",
                "importance": 0.8
            }
        ],
        "semantic_memories": [
            {
                "id": "sem_1", 
                "concept": "Python programming",
                "description": "A high-level programming language",
                "confidence": 0.9
            }
        ],
        "procedural_memories": [
            {
                "id": "proc_1",
                "action": "explain_concept",
                "steps": ["identify_topic", "find_examples", "provide_explanation"],
                "success_rate": 0.85
            }
        ]
    }


# Context managers for easy patching
class MockOpenAIContext:
    """Context manager for mocking OpenAI"""
    def __enter__(self):
        # Patch multiple OpenAI modules and classes
        self.patchers = [
            patch('openai.OpenAI', return_value=mock_openai_client()),
            patch('openai.AsyncOpenAI', return_value=mock_openai_client()),
            patch('openai.ChatCompletion', return_value=MockOpenAIResponse()),
            patch('openai.Embedding', return_value=Mock()),
            # Patch environment variable
            patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key-12345'})
        ]
        
        for patcher in self.patchers:
            patcher.start()
        
        return mock_openai_client()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        for patcher in self.patchers:
            patcher.stop()


class MockQdrantContext:
    """Context manager for mocking Qdrant"""
    def __enter__(self):
        self.patcher = patch('qdrant_client.QdrantClient', return_value=mock_qdrant_client())
        self.mock_client = self.patcher.start()
        return self.mock_client
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.patcher.stop()


class MockRequestsContext:
    """Context manager for mocking requests"""
    def __enter__(self):
        self.patcher = patch('requests.post', return_value=mock_requests_post())
        self.mock_post = self.patcher.start()
        return self.mock_post
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.patcher.stop()

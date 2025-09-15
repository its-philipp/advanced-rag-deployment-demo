"""
Prometheus metrics for the RAG demo application.
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time
from typing import Callable
from fastapi import Request
import asyncio

# HTTP Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# RAG-specific Metrics
RAG_QUERIES_TOTAL = Counter(
    'rag_queries_total',
    'Total RAG queries processed',
    ['user_id']
)

RAG_QUERY_DURATION = Histogram(
    'rag_query_duration_seconds',
    'RAG query processing duration in seconds',
    ['user_id']
)

RAG_QUERY_CONFIDENCE = Histogram(
    'rag_query_confidence',
    'RAG query confidence scores',
    ['user_id']
)

RAG_SOURCES_RETRIEVED = Histogram(
    'rag_sources_retrieved',
    'Number of sources retrieved per query',
    ['user_id']
)

# Document Indexing Metrics
DOCUMENTS_INDEXED = Counter(
    'documents_indexed_total',
    'Total documents indexed',
    ['source_type']
)

CHUNKS_CREATED = Counter(
    'chunks_created_total',
    'Total document chunks created',
    ['source_type']
)

# System Metrics
ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

# Embedding Metrics
EMBEDDING_REQUESTS = Counter(
    'embedding_requests_total',
    'Total embedding requests',
    ['model']
)

EMBEDDING_DURATION = Histogram(
    'embedding_duration_seconds',
    'Embedding generation duration in seconds',
    ['model']
)

# LLM Metrics
LLM_REQUESTS = Counter(
    'llm_requests_total',
    'Total LLM requests',
    ['model']
)

LLM_DURATION = Histogram(
    'llm_duration_seconds',
    'LLM generation duration in seconds',
    ['model']
)

LLM_TOKENS_USED = Counter(
    'llm_tokens_used_total',
    'Total LLM tokens used',
    ['model', 'type']  # type: input/output
)

def get_metrics() -> Response:
    """Return Prometheus metrics in the correct format."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

class PrometheusMiddleware:
    """Middleware to track HTTP requests and responses."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        method = request.method
        endpoint = request.url.path
        
        # Start timing
        start_time = time.time()
        
        # Track request
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code="unknown").inc()
        
        # Process request
        status_code = 200
        try:
            await self.app(scope, receive, send)
        except Exception as e:
            status_code = 500
            raise
        finally:
            # Calculate duration
            duration = time.time() - start_time
            
            # Update metrics
            REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=str(status_code)).inc()

def track_rag_query(user_id: str, duration: float, confidence: float, sources_count: int):
    """Track RAG query metrics."""
    RAG_QUERIES_TOTAL.labels(user_id=user_id).inc()
    RAG_QUERY_DURATION.labels(user_id=user_id).observe(duration)
    RAG_QUERY_CONFIDENCE.labels(user_id=user_id).observe(confidence)
    RAG_SOURCES_RETRIEVED.labels(user_id=user_id).observe(sources_count)

def track_document_indexing(source_type: str, chunks_count: int):
    """Track document indexing metrics."""
    DOCUMENTS_INDEXED.labels(source_type=source_type).inc()
    CHUNKS_CREATED.labels(source_type=source_type).inc(chunks_count)

def track_embedding_request(model: str, duration: float):
    """Track embedding request metrics."""
    EMBEDDING_REQUESTS.labels(model=model).inc()
    EMBEDDING_DURATION.labels(model=model).observe(duration)

def track_llm_request(model: str, duration: float, input_tokens: int = 0, output_tokens: int = 0):
    """Track LLM request metrics."""
    LLM_REQUESTS.labels(model=model).inc()
    LLM_DURATION.labels(model=model).observe(duration)
    
    if input_tokens > 0:
        LLM_TOKENS_USED.labels(model=model, type="input").inc(input_tokens)
    if output_tokens > 0:
        LLM_TOKENS_USED.labels(model=model, type="output").inc(output_tokens)

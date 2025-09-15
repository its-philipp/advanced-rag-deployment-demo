import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.app.api.v1 import router as v1_router
from src.app.api.agentic import router as agentic_router
from src.app.metrics import get_metrics, PrometheusMiddleware

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Advanced RAG System",
    description="Production-ready RAG backend with FastAPI and cloud deployment",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Prometheus middleware
app.add_middleware(PrometheusMiddleware)

# Include API routes
app.include_router(v1_router, prefix="/api/v1")
app.include_router(agentic_router, prefix="/api/agentic")

# Add metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return get_metrics()

# Add health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": time.time()}

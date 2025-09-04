import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.app.api.v1 import router as v1_router

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="pinkpro-rag-demo",
    description="RAG-based educational coaching backend",
    version="1.0.0"
)
app.include_router(v1_router, prefix="/api/v1")

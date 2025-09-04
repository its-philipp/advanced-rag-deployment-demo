from fastapi import APIRouter
from pydantic import BaseModel
from src.app.services.rag_service import answer_question
from src.app.services.document_indexer import index_documents, get_sample_documents

router = APIRouter()

class QRequest(BaseModel):
    user_id: str
    query: str
    context_limit: int = 5

class Source(BaseModel):
    source_id: str
    chunk_id: str
    score: float
    text_snippet: str

class QResponse(BaseModel):
    answer: str
    sources: list[Source]
    confidence: float

@router.post("/coach", response_model=QResponse)
async def coach(req: QRequest):
    return await answer_question(req.user_id, req.query, req.context_limit)

@router.post("/index-sample-docs")
async def index_sample_docs():
    """Index sample educational documents for testing."""
    documents = get_sample_documents()
    chunk_count = index_documents(documents)
    return {"message": f"Successfully indexed {chunk_count} chunks from {len(documents)} documents"}

class DocumentRequest(BaseModel):
    title: str
    content: str
    source_id: str = None

@router.post("/index-document")
async def index_document(doc: DocumentRequest):
    """Index a single document."""
    document = {
        "title": doc.title,
        "content": doc.content,
        "source_id": doc.source_id
    }
    chunk_count = index_documents([document])
    return {"message": f"Successfully indexed {chunk_count} chunks from document: {doc.title}"}

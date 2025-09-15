from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from src.app.services.rag_service import answer_question
from src.app.services.document_indexer import index_documents, get_sample_documents
from src.app.services.user_coaching_agent import UserCoachingAgent

router = APIRouter()

# Global agent cache to avoid recreating agents
_agent_cache = {}

def get_user_agent(user_id: str) -> UserCoachingAgent:
    """Get or create a user coaching agent."""
    if user_id not in _agent_cache:
        _agent_cache[user_id] = UserCoachingAgent(user_id)
    return _agent_cache[user_id]

# Original models for backward compatibility
class QRequest(BaseModel):
    user_id: str
    query: str
    context_limit: int = 5

class Source(BaseModel):
    source_id: str
    chunk_id: str
    score: float
    text_snippet: str
    source_type: Optional[str] = "global"

class QResponse(BaseModel):
    answer: str
    sources: List[Source]
    confidence: float
    personalized: Optional[bool] = False
    user_context: Optional[Dict[str, Any]] = None

# New models for personalized coaching
class PersonalizedQRequest(BaseModel):
    user_id: str
    query: str
    context_limit: int = 5
    use_hybrid: bool = True

class UserPreferences(BaseModel):
    learning_style: Optional[str] = None
    subject_focus: Optional[str] = None
    difficulty_level: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class UserProfile(BaseModel):
    user_id: str
    preferences: Dict[str, Any]
    learning_goals: List[str]
    learning_style: Optional[str] = None
    total_sessions: int
    last_active: str

class UserDocumentRequest(BaseModel):
    user_id: str
    title: str
    content: str
    source_id: Optional[str] = None

# Original endpoints (backward compatibility)
@router.post("/coach", response_model=QResponse)
async def coach(req: QRequest):
    """Original coach endpoint - now uses personalized coaching."""
    agent = get_user_agent(req.user_id)
    result = await agent.answer_question(req.query, req.context_limit)
    return QResponse(**result)

# New personalized coaching endpoints
@router.post("/personalized-coach", response_model=QResponse)
async def personalized_coach(req: PersonalizedQRequest):
    """Personalized coaching with user context and preferences."""
    agent = get_user_agent(req.user_id)
    result = await agent.answer_question(req.query, req.context_limit, req.use_hybrid)
    return QResponse(**result)

@router.get("/users/{user_id}/profile", response_model=UserProfile)
async def get_user_profile(user_id: str):
    """Get user profile and preferences."""
    agent = get_user_agent(user_id)
    summary = agent.get_user_summary()
    return UserProfile(**summary)

@router.put("/users/{user_id}/preferences")
async def update_user_preferences(user_id: str, preferences: UserPreferences):
    """Update user preferences and learning style."""
    agent = get_user_agent(user_id)
    
    # Update learning style
    if preferences.learning_style:
        agent.update_learning_style(preferences.learning_style)
    
    # Update other preferences
    prefs_dict = {}
    if preferences.subject_focus:
        prefs_dict["subject_focus"] = preferences.subject_focus
    if preferences.difficulty_level:
        prefs_dict["difficulty_level"] = preferences.difficulty_level
    if preferences.preferences:
        prefs_dict.update(preferences.preferences)
    
    if prefs_dict:
        agent.update_preferences(prefs_dict)
    
    return {"message": "Preferences updated successfully"}

@router.put("/users/{user_id}/learning-goals")
async def update_learning_goals(user_id: str, goals: List[str]):
    """Update user learning goals."""
    agent = get_user_agent(user_id)
    agent.update_learning_goals(goals)
    return {"message": "Learning goals updated successfully"}

@router.post("/users/{user_id}/documents")
async def add_user_document(doc: UserDocumentRequest):
    """Add a document to user's personal collection."""
    agent = get_user_agent(doc.user_id)
    chunk_count = agent.add_user_document(doc.title, doc.content, doc.source_id)
    return {"message": f"Successfully added {chunk_count} chunks to user's personal collection"}

@router.get("/users/{user_id}/context")
async def get_user_context(user_id: str, limit: int = 10):
    """Get user's recent chat context."""
    agent = get_user_agent(user_id)
    recent_context = agent.context.get_recent_context(limit)
    
    return {
        "user_id": user_id,
        "recent_messages": [
            {
                "timestamp": msg.timestamp,
                "role": msg.role,
                "content": msg.content,
                "confidence": msg.confidence
            }
            for msg in recent_context
        ]
    }

# Document indexing endpoints (unchanged)
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

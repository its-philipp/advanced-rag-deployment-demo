"""
Agentic RAG API Endpoints
Provides endpoints for the agentic RAG system with episodic, semantic, and procedural memory.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio

from src.app.services.user_context import UserContext
from src.agents.memory_manager import AgenticMemoryManager
from src.agents.agentic_rag_agent import AgenticRAGAgent
from src.agents.semantic_kernel_agent import SemanticKernelAgenticRAG
from src.agents.langgraph_agent import LangGraphAgenticRAG

router = APIRouter()

# Global instances (in production, use dependency injection)
memory_manager = AgenticMemoryManager()

def get_agentic_agent(user_id: str) -> AgenticRAGAgent:
    """Get agentic agent for a specific user"""
    user_context = UserContext(user_id)
    return AgenticRAGAgent(memory_manager, user_context)

class AgenticQueryRequest(BaseModel):
    user_id: str
    query: str
    context_limit: int = 3
    use_hybrid: bool = True

class AgenticQueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    memory_types_used: List[str]
    reasoning_steps: List[str]
    personalized: bool

class MemoryStatsResponse(BaseModel):
    episodic: Dict[str, int]
    semantic: Dict[str, int]
    procedural: Dict[str, int]

@router.post("/agentic-query", response_model=AgenticQueryResponse)
async def agentic_query(request: AgenticQueryRequest):
    """
    Process a query using agentic RAG with all memory types
    """
    try:
        # Get agentic agent for this user
        agentic_agent = get_agentic_agent(request.user_id)
        
        # Initialize user memories if this is their first interaction
        user_profile = agentic_agent.user_context.profile
        if not user_profile or user_profile.total_sessions == 0:
            await agentic_agent.initialize_user_memories(request.user_id)
        
        # Process the query
        response = await agentic_agent.process_query(
            user_id=request.user_id,
            query=request.query,
            context_limit=request.context_limit,
            use_hybrid=request.use_hybrid
        )
        
        return AgenticQueryResponse(
            answer=response.answer,
            sources=response.sources,
            confidence=response.confidence,
            memory_types_used=response.memory_types_used,
            reasoning_steps=response.reasoning_steps,
            personalized=response.personalized
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing agentic query: {str(e)}")

@router.get("/memory-stats", response_model=MemoryStatsResponse)
async def get_memory_stats():
    """
    Get statistics about stored memories
    """
    try:
        stats = memory_manager.get_memory_stats()
        return MemoryStatsResponse(
            episodic=stats["episodic"],
            semantic=stats["semantic"],
            procedural=stats["procedural"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving memory stats: {str(e)}")

class SemanticMemoryRequest(BaseModel):
    concept: str
    knowledge: Dict[str, Any]
    relationships: Optional[List[str]] = None
    confidence: float = 0.8

@router.post("/store-semantic-memory")
async def store_semantic_memory(request: SemanticMemoryRequest):
    """
    Store semantic memory (facts, concepts, knowledge)
    """
    try:
        memory_id = await memory_manager.store_semantic(
            concept=request.concept,
            knowledge=request.knowledge,
            relationships=request.relationships,
            confidence=request.confidence
        )
        return {"message": "Semantic memory stored successfully", "memory_id": memory_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing semantic memory: {str(e)}")

class ProceduralMemoryRequest(BaseModel):
    skill: str
    steps: List[Dict[str, Any]]
    prerequisites: Optional[List[str]] = None
    success_criteria: Optional[List[str]] = None

@router.post("/store-procedural-memory")
async def store_procedural_memory(request: ProceduralMemoryRequest):
    """
    Store procedural memory (skills, workflows, procedures)
    """
    try:
        memory_id = await memory_manager.store_procedural(
            skill=request.skill,
            steps=request.steps,
            prerequisites=request.prerequisites,
            success_criteria=request.success_criteria
        )
        return {"message": "Procedural memory stored successfully", "memory_id": memory_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing procedural memory: {str(e)}")

@router.get("/episodic-memories/{user_id}")
async def get_episodic_memories(
    user_id: str,
    query: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 10
):
    """
    Retrieve episodic memories for a user
    """
    try:
        memories = await memory_manager.retrieve_episodic(
            user_id=user_id,
            query=query,
            event_type=event_type,
            limit=limit
        )
        
        # Convert to dict format for JSON serialization
        memory_dicts = []
        for memory in memories:
            memory_dicts.append({
                "timestamp": memory.timestamp,
                "user_id": memory.user_id,
                "event_type": memory.event_type,
                "content": memory.content,
                "context": memory.context
            })
        
        return {"memories": memory_dicts, "count": len(memory_dicts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving episodic memories: {str(e)}")

@router.get("/semantic-memories")
async def get_semantic_memories(
    concept: Optional[str] = None,
    relationships: Optional[List[str]] = None
):
    """
    Retrieve semantic memories
    """
    try:
        memories = await memory_manager.retrieve_semantic(
            concept=concept,
            relationships=relationships
        )
        
        # Convert to dict format for JSON serialization
        memory_dicts = []
        for memory in memories:
            memory_dicts.append({
                "concept": memory.concept,
                "knowledge": memory.knowledge,
                "relationships": memory.relationships,
                "confidence": memory.confidence,
                "last_updated": memory.last_updated
            })
        
        return {"memories": memory_dicts, "count": len(memory_dicts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving semantic memories: {str(e)}")

@router.get("/procedural-memories")
async def get_procedural_memories(
    skill: Optional[str] = None,
    prerequisites: Optional[List[str]] = None
):
    """
    Retrieve procedural memories
    """
    try:
        memories = await memory_manager.retrieve_procedural(
            skill=skill,
            prerequisites=prerequisites
        )
        
        # Convert to dict format for JSON serialization
        memory_dicts = []
        for memory in memories:
            memory_dicts.append({
                "skill": memory.skill,
                "steps": memory.steps,
                "prerequisites": memory.prerequisites,
                "success_criteria": memory.success_criteria,
                "last_used": memory.last_used
            })
        
        return {"memories": memory_dicts, "count": len(memory_dicts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving procedural memories: {str(e)}")

@router.post("/initialize-user/{user_id}")
async def initialize_user(user_id: str):
    """
    Initialize default memories for a new user
    """
    try:
        agentic_agent = get_agentic_agent(user_id)
        await agentic_agent.initialize_user_memories(user_id)
        return {"message": f"User {user_id} initialized with default memories"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing user: {str(e)}")

@router.delete("/clear-memories")
async def clear_all_memories():
    """
    Clear all memories (for testing purposes)
    """
    try:
        memory_manager.episodic_memories.clear()
        memory_manager.semantic_memories.clear()
        memory_manager.procedural_memories.clear()
        return {"message": "All memories cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing memories: {str(e)}")

# Production Framework Endpoints

def get_semantic_kernel_agent(user_id: str) -> SemanticKernelAgenticRAG:
    """Get Semantic Kernel agent for a specific user"""
    user_context = UserContext(user_id)
    return SemanticKernelAgenticRAG(memory_manager, user_context)

def get_langgraph_agent(user_id: str) -> LangGraphAgenticRAG:
    """Get LangGraph agent for a specific user"""
    user_context = UserContext(user_id)
    return LangGraphAgenticRAG(memory_manager, user_context)

@router.post("/semantic-kernel-query", response_model=AgenticQueryResponse)
async def semantic_kernel_query(request: AgenticQueryRequest):
    """
    Process a query using Semantic Kernel agentic RAG
    """
    try:
        agent = get_semantic_kernel_agent(request.user_id)
        response = await agent.process_query(
            user_id=request.user_id,
            query=request.query,
            context_limit=request.context_limit,
            use_hybrid=request.use_hybrid
        )
        
        return AgenticQueryResponse(
            answer=response.answer,
            sources=response.sources,
            confidence=response.confidence,
            memory_types_used=response.memory_types_used,
            reasoning_steps=response.reasoning_steps,
            personalized=response.personalized
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing semantic kernel query: {str(e)}")

@router.post("/langgraph-query", response_model=AgenticQueryResponse)
async def langgraph_query(request: AgenticQueryRequest):
    """
    Process a query using LangGraph agentic RAG
    """
    try:
        agent = get_langgraph_agent(request.user_id)
        response = await agent.process_query(
            user_id=request.user_id,
            query=request.query,
            context_limit=request.context_limit,
            use_hybrid=request.use_hybrid
        )
        
        return AgenticQueryResponse(
            answer=response.answer,
            sources=response.sources,
            confidence=response.confidence,
            memory_types_used=response.memory_types_used,
            reasoning_steps=response.reasoning_steps,
            personalized=response.personalized
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing langgraph query: {str(e)}")

@router.post("/compare-frameworks")
async def compare_frameworks(request: AgenticQueryRequest):
    """
    Compare all three frameworks on the same query
    """
    try:
        from src.agents.production_frameworks import ProductionFrameworksComparison
        
        comparison = ProductionFrameworksComparison(memory_manager, UserContext(request.user_id))
        results = await comparison.compare_frameworks(
            user_id=request.user_id,
            query=request.query,
            context_limit=request.context_limit
        )
        
        # Convert results to serializable format
        serializable_results = {}
        for framework_name, result in results.items():
            serializable_results[framework_name] = {
                "framework": result.framework,
                "response_time": result.response_time,
                "answer_quality": result.answer_quality,
                "memory_usage": result.memory_usage,
                "reasoning_steps": result.reasoning_steps,
                "confidence": result.confidence,
                "personalized": result.personalized,
                "error": result.error
            }
        
        return {
            "query": request.query,
            "results": serializable_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing frameworks: {str(e)}")

"""
Agentic RAG Agent
Implements an intelligent agent that uses episodic, semantic, and procedural memory
to provide personalized, context-aware responses.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from .memory_manager import AgenticMemoryManager, EpisodicMemory, SemanticMemory, ProceduralMemory
from src.app.services.embeddings_minimal import get_embedding_openai
from src.app.services.qdrant_client import search_similar
from src.app.services.user_context import UserContext

@dataclass
class AgenticResponse:
    """Response from the agentic RAG system"""
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    memory_types_used: List[str]
    reasoning_steps: List[str]
    personalized: bool

class AgenticRAGAgent:
    """
    An intelligent agent that uses multiple memory types to provide
    personalized, context-aware responses.
    """
    
    def __init__(self, memory_manager: AgenticMemoryManager, user_context: UserContext):
        self.memory_manager = memory_manager
        self.user_context = user_context
        self.reasoning_steps = []
        
    async def process_query(self, user_id: str, query: str, 
                          context_limit: int = 3, use_hybrid: bool = True) -> AgenticResponse:
        """
        Process a query using agentic RAG with all memory types
        
        Args:
            user_id: User identifier
            query: User's question or request
            context_limit: Maximum number of context items to use
            use_hybrid: Whether to use hybrid search (global + user-specific)
            
        Returns:
            AgenticResponse with answer and metadata
        """
        self.reasoning_steps = []
        memory_types_used = []
        
        # Step 1: Retrieve episodic memory (conversation context)
        self.reasoning_steps.append("Retrieving episodic memory for conversation context")
        episodic_context = await self._retrieve_episodic_context(user_id, query, context_limit)
        if episodic_context:
            memory_types_used.append("episodic")
        
        # Step 2: Extract concepts and retrieve semantic memory
        self.reasoning_steps.append("Extracting concepts and retrieving semantic knowledge")
        concepts = await self._extract_concepts(query)
        semantic_context = await self._retrieve_semantic_context(concepts)
        if semantic_context:
            memory_types_used.append("semantic")
        
        # Step 3: Identify required skills and retrieve procedural memory
        self.reasoning_steps.append("Identifying required skills and retrieving procedural knowledge")
        required_skills = await self._identify_required_skills(query)
        procedural_context = await self._retrieve_procedural_context(required_skills)
        if procedural_context:
            memory_types_used.append("procedural")
        
        # Step 4: Retrieve relevant documents using RAG
        self.reasoning_steps.append("Retrieving relevant documents using RAG")
        rag_sources = await self._retrieve_rag_sources(query, use_hybrid, user_id)
        
        # Step 5: Generate personalized response
        self.reasoning_steps.append("Generating personalized response using all memory types")
        response = await self._generate_agentic_response(
            query, episodic_context, semantic_context, procedural_context, rag_sources, user_id
        )
        
        # Step 6: Store this interaction in episodic memory
        await self._store_interaction(user_id, query, response)
        
        return AgenticResponse(
            answer=response["answer"],
            sources=response["sources"],
            confidence=response["confidence"],
            memory_types_used=memory_types_used,
            reasoning_steps=self.reasoning_steps,
            personalized=len(memory_types_used) > 0
        )
    
    async def _retrieve_episodic_context(self, user_id: str, query: str, limit: int) -> List[EpisodicMemory]:
        """Retrieve relevant episodic memories"""
        # Get recent conversations
        recent_memories = await self.memory_manager.retrieve_episodic(
            user_id, query, event_type="conversation", limit=limit
        )
        
        # Get learning progress
        learning_memories = await self.memory_manager.retrieve_episodic(
            user_id, query, event_type="learning", limit=2
        )
        
        return recent_memories + learning_memories
    
    async def _extract_concepts(self, query: str) -> List[str]:
        """Extract key concepts from query for semantic memory lookup"""
        # Simple concept extraction - in production, use NLP libraries
        concepts = []
        
        # Common learning concepts
        learning_concepts = [
            "mathematics", "programming", "language", "science", "history",
            "art", "music", "sports", "cooking", "photography"
        ]
        
        query_lower = query.lower()
        for concept in learning_concepts:
            if concept in query_lower:
                concepts.append(concept)
        
        # Add domain-specific concepts based on query content
        if any(word in query_lower for word in ["learn", "study", "practice", "improve"]):
            concepts.append("learning_methodology")
        
        if any(word in query_lower for word in ["difficult", "hard", "challenge", "struggle"]):
            concepts.append("learning_difficulties")
        
        return concepts
    
    async def _retrieve_semantic_context(self, concepts: List[str]) -> List[SemanticMemory]:
        """Retrieve semantic memories for given concepts"""
        semantic_memories = []
        
        for concept in concepts:
            memories = await self.memory_manager.retrieve_semantic(concept)
            semantic_memories.extend(memories)
        
        return semantic_memories
    
    async def _identify_required_skills(self, query: str) -> List[str]:
        """Identify required skills for procedural memory lookup"""
        skills = []
        query_lower = query.lower()
        
        # Map query patterns to skills
        skill_patterns = {
            "problem_solving": ["solve", "problem", "fix", "debug", "troubleshoot"],
            "learning_planning": ["plan", "schedule", "organize", "structure"],
            "practice_techniques": ["practice", "exercise", "drill", "repetition"],
            "memory_techniques": ["remember", "memorize", "recall", "memory"],
            "time_management": ["time", "schedule", "deadline", "efficient"]
        }
        
        for skill, patterns in skill_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                skills.append(skill)
        
        return skills
    
    async def _retrieve_procedural_context(self, skills: List[str]) -> List[ProceduralMemory]:
        """Retrieve procedural memories for given skills"""
        procedural_memories = []
        
        for skill in skills:
            memories = await self.memory_manager.retrieve_procedural(skill)
            procedural_memories.extend(memories)
        
        return procedural_memories
    
    async def _retrieve_rag_sources(self, query: str, use_hybrid: bool, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve relevant documents using RAG"""
        try:
            if use_hybrid:
                # Use hybrid search (global + user-specific)
                from src.app.services.qdrant_client import search_hybrid
                # Get embedding for the query
                embedding = await get_embedding_openai(query)
                results = search_hybrid(user_id, embedding, top_k=3)
            else:
                # Use global search only
                embedding = await get_embedding_openai(query)
                results = search_similar(embedding, top_k=3)
            
            # Format results as proper source dictionaries
            sources = []
            for result in results:
                payload = result.get("payload", {})
                sources.append({
                    "source_id": result.get("id", ""),
                    "chunk_id": payload.get("chunk_id", ""),
                    "score": result.get("score", 0.0),
                    "text_snippet": payload.get("text", "")[:400],
                    "source_type": result.get("source", "global")
                })
            
            return sources
        except Exception as e:
            print(f"Error retrieving RAG sources: {e}")
            return []
    
    async def _generate_agentic_response(self, query: str, episodic_context: List[EpisodicMemory],
                                       semantic_context: List[SemanticMemory],
                                       procedural_context: List[ProceduralMemory],
                                       rag_sources: List[Dict[str, Any]], user_id: str) -> Dict[str, Any]:
        """Generate personalized response using all memory types"""
        
        # Build context from all memory types
        context_parts = []
        
        # Add episodic context
        if episodic_context:
            context_parts.append("Previous conversations and learning history:")
            for memory in episodic_context[-2:]:  # Last 2 memories
                context_parts.append(f"- {memory.content}")
        
        # Add semantic context
        if semantic_context:
            context_parts.append("Relevant knowledge:")
            for memory in semantic_context:
                context_parts.append(f"- {memory.concept}: {memory.knowledge.get('description', '')}")
        
        # Add procedural context
        if procedural_context:
            context_parts.append("Recommended approaches:")
            for memory in procedural_context:
                context_parts.append(f"- {memory.skill}: {len(memory.steps)} steps available")
        
        # Get user preferences
        user_profile = self.user_context.profile
        preferences = user_profile.preferences if user_profile.preferences else {}
        
        # Build personalized prompt
        system_prompt = f"""You are a personalized AI learning coach. Use the following context to provide a helpful, personalized response.

User Preferences: {json.dumps(preferences, indent=2)}

Context from Memory:
{chr(10).join(context_parts) if context_parts else "No specific context available."}

Available Sources:
{json.dumps(rag_sources, indent=2) if rag_sources else "No additional sources available."}

Provide a comprehensive, personalized response that:
1. Addresses the user's question directly
2. Incorporates relevant context from their learning history
3. Uses appropriate learning methods based on their preferences
4. References specific sources when helpful
5. Suggests next steps for continued learning

Response in the user's preferred language: {preferences.get('preferred_language', 'English')}"""

        # Generate response using OpenAI
        try:
            import openai
            from src.app.services.embeddings_minimal import OPENAI_API_KEY
            
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            
            # Calculate confidence based on available context
            confidence = 0.5  # Base confidence
            if episodic_context:
                confidence += 0.1
            if semantic_context:
                confidence += 0.1
            if procedural_context:
                confidence += 0.1
            if rag_sources:
                confidence += 0.2
            
            confidence = min(confidence, 1.0)
            
            return {
                "answer": answer,
                "sources": rag_sources,
                "confidence": confidence
            }
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                "answer": "I apologize, but I'm having trouble generating a response right now. Please try again later.",
                "sources": rag_sources,
                "confidence": 0.1
            }
    
    async def _store_interaction(self, user_id: str, query: str, response: Dict[str, Any]):
        """Store this interaction in episodic memory"""
        try:
            # Generate embedding for the query
            embedding = await get_embedding_openai(query)
            
            # Store as episodic memory
            await self.memory_manager.store_episodic(
                user_id=user_id,
                event_type="conversation",
                content=query,
                context={
                    "response": response["answer"],
                    "confidence": response["confidence"],
                    "sources_count": len(response["sources"])
                },
                embedding=embedding
            )
            
            # Update user context
            self.user_context.profile.total_sessions += 1
            self.user_context.profile.last_active = time.time()
            
        except Exception as e:
            print(f"Error storing interaction: {e}")
    
    async def initialize_user_memories(self, user_id: str):
        """Initialize default memories for a new user"""
        # Store some basic semantic memories
        await self.memory_manager.store_semantic(
            concept="learning_methodology",
            knowledge={
                "description": "Effective learning strategies and techniques",
                "key_principles": [
                    "Spaced repetition for long-term retention",
                    "Active recall for better understanding",
                    "Interleaving different topics",
                    "Elaborative interrogation"
                ]
            },
            relationships=["learning_difficulties", "memory_techniques"]
        )
        
        # Store basic procedural memories
        await self.memory_manager.store_procedural(
            skill="problem_solving",
            steps=[
                {"step": 1, "action": "Understand the problem", "description": "Read and analyze the problem statement"},
                {"step": 2, "action": "Identify key components", "description": "Break down the problem into smaller parts"},
                {"step": 3, "action": "Generate solutions", "description": "Brainstorm multiple approaches"},
                {"step": 4, "action": "Evaluate options", "description": "Compare pros and cons of each approach"},
                {"step": 5, "action": "Implement solution", "description": "Execute the chosen approach"},
                {"step": 6, "action": "Review and learn", "description": "Reflect on the process and outcomes"}
            ],
            prerequisites=["basic_understanding"],
            success_criteria=["problem_solved", "learning_occurred"]
        )

"""
Simplified Semantic Kernel Agentic RAG Implementation
A working version that focuses on core functionality without complex API issues
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

from .memory_manager import AgenticMemoryManager
from src.app.services.user_context import UserContext
from src.app.services.embeddings_minimal import get_embedding_openai

@dataclass
class SemanticKernelResponse:
    """Response from simplified Semantic Kernel agentic RAG system"""
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    memory_types_used: List[str]
    reasoning_steps: List[str]
    personalized: bool
    execution_plan: Optional[str] = None

class SemanticKernelSimpleRAG:
    """
    Simplified Semantic Kernel agentic RAG that actually works
    """
    
    def __init__(self, memory_manager: AgenticMemoryManager, user_context: UserContext):
        self.memory_manager = memory_manager
        self.user_context = user_context
        self.kernel = self._initialize_kernel()
        self.reasoning_steps = []
        
    def _initialize_kernel(self) -> Kernel:
        """Initialize Semantic Kernel with OpenAI service"""
        kernel = Kernel()
        
        # Add OpenAI chat completion service
        kernel.add_service(OpenAIChatCompletion(
            service_id="openai_chat",
            ai_model_id="gpt-4o-mini",
            api_key=self._get_openai_key()
        ))
        
        return kernel
    
    def _get_openai_key(self) -> str:
        """Get OpenAI API key"""
        import os
        return os.getenv("OPENAI_API_KEY", "")
    
    async def process_query(self, user_id: str, query: str, 
                          context_limit: int = 3, use_hybrid: bool = True) -> SemanticKernelResponse:
        """
        Process query using simplified Semantic Kernel approach
        """
        self.reasoning_steps = []
        memory_types_used = []
        
        # Step 1: Create simple execution plan
        self.reasoning_steps.append("Creating execution plan")
        execution_plan = "1. Analyze query 2. Retrieve memories 3. Generate response 4. Store interaction"
        
        # Step 2: Retrieve memories using our custom memory manager
        self.reasoning_steps.append("Retrieving memories from custom memory manager")
        episodic_context = await self._retrieve_episodic_context(user_id, query, context_limit)
        semantic_context = await self._retrieve_semantic_context(query)
        procedural_context = await self._retrieve_procedural_context(query)
        
        if episodic_context:
            memory_types_used.append("episodic")
        if semantic_context:
            memory_types_used.append("semantic")
        if procedural_context:
            memory_types_used.append("procedural")
        
        # Step 3: Generate response using Semantic Kernel
        self.reasoning_steps.append("Generating response using Semantic Kernel")
        response = await self._generate_response_with_kernel(
            query, episodic_context, semantic_context, procedural_context, user_id
        )
        
        # Step 4: Store interaction
        self.reasoning_steps.append("Storing interaction")
        await self._store_interaction(user_id, query, response)
        
        return SemanticKernelResponse(
            answer=response["answer"],
            sources=response["sources"],
            confidence=response["confidence"],
            memory_types_used=memory_types_used,
            reasoning_steps=self.reasoning_steps,
            personalized=len(memory_types_used) > 0,
            execution_plan=execution_plan
        )
    
    async def _retrieve_episodic_context(self, user_id: str, query: str, limit: int) -> List[Dict[str, Any]]:
        """Retrieve episodic memories using custom memory manager"""
        try:
            memories = await self.memory_manager.retrieve_episodic(
                user_id=user_id,
                query=query,
                event_type="conversation",
                limit=limit
            )
            
            return [
                {
                    "content": memory.content,
                    "timestamp": memory.timestamp,
                    "event_type": memory.event_type
                }
                for memory in memories
            ]
        except Exception as e:
            print(f"Error retrieving episodic context: {e}")
            return []
    
    async def _retrieve_semantic_context(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve semantic memories using custom memory manager"""
        try:
            # Extract concepts from query (simple approach)
            concepts = self._extract_concepts_simple(query)
            
            semantic_context = []
            for concept in concepts:
                memories = await self.memory_manager.retrieve_semantic(concept)
                for memory in memories:
                    semantic_context.append({
                        "concept": memory.concept,
                        "knowledge": memory.knowledge,
                        "confidence": memory.confidence
                    })
            
            return semantic_context
        except Exception as e:
            print(f"Error retrieving semantic context: {e}")
            return []
    
    async def _retrieve_procedural_context(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve procedural memories using custom memory manager"""
        try:
            # Identify required skills (simple approach)
            skills = self._identify_skills_simple(query)
            
            procedural_context = []
            for skill in skills:
                memories = await self.memory_manager.retrieve_procedural(skill)
                for memory in memories:
                    procedural_context.append({
                        "skill": memory.skill,
                        "steps": memory.steps,
                        "prerequisites": memory.prerequisites
                    })
            
            return procedural_context
        except Exception as e:
            print(f"Error retrieving procedural context: {e}")
            return []
    
    def _extract_concepts_simple(self, query: str) -> List[str]:
        """Extract concepts using simple keyword matching"""
        concepts = []
        query_lower = query.lower()
        
        # Simple keyword matching
        if "machine learning" in query_lower or "ml" in query_lower:
            concepts.append("machine_learning")
        if "neural network" in query_lower or "deep learning" in query_lower:
            concepts.append("neural_networks")
        if "problem solving" in query_lower or "problem-solving" in query_lower:
            concepts.append("problem_solving")
        if "learning" in query_lower:
            concepts.append("learning_methodology")
        
        return concepts
    
    def _identify_skills_simple(self, query: str) -> List[str]:
        """Identify required skills using simple keyword matching"""
        skills = []
        query_lower = query.lower()
        
        # Simple keyword matching
        if "learn" in query_lower or "learning" in query_lower:
            skills.append("learning_machine_learning")
        if "problem" in query_lower or "solve" in query_lower:
            skills.append("problem_solving")
        if "code" in query_lower or "programming" in query_lower:
            skills.append("programming")
        
        return skills
    
    async def _generate_response_with_kernel(self, query: str, episodic_context: List[Dict], 
                                           semantic_context: List[Dict], procedural_context: List[Dict], 
                                           user_id: str) -> Dict[str, Any]:
        """Generate response using Semantic Kernel"""
        try:
            # Get user preferences
            user_profile = self.user_context.profile
            preferences = user_profile.preferences if user_profile.preferences else {}
            
            # Build context string
            context_parts = []
            
            if episodic_context:
                context_parts.append("Previous conversations:")
                for memory in episodic_context:
                    context_parts.append(f"- {memory['content']}")
            
            if semantic_context:
                context_parts.append("Relevant knowledge:")
                for memory in semantic_context:
                    context_parts.append(f"- {memory['concept']}: {memory['knowledge'].get('description', '')}")
            
            if procedural_context:
                context_parts.append("Available skills:")
                for memory in procedural_context:
                    context_parts.append(f"- {memory['skill']}: {len(memory['steps'])} steps available")
            
            context_string = "\n".join(context_parts) if context_parts else "No specific context available."
            
            # Create a simple prompt
            prompt = f"""
            You are an advanced AI learning coach with access to multiple types of memory.
            
            User Query: {query}
            
            User Preferences: {json.dumps(preferences, indent=2)}
            
            Context:
            {context_string}
            
            Generate a comprehensive, personalized response that:
            1. Directly addresses the user's query
            2. Incorporates relevant context from all memory types
            3. Provides actionable advice or next steps
            4. Shows understanding of the user's learning journey
            5. References specific sources when helpful
            
            Be conversational, helpful, and personalized based on the user's context.
            """
            
            # Use Semantic Kernel to generate response
            from semantic_kernel.contents import ChatHistory
            
            chat_history = ChatHistory()
            chat_history.add_user_message(prompt)
            
            # Get the chat completion service
            chat_service = self.kernel.get_service(type=OpenAIChatCompletion)
            
            # Generate response
            response = await chat_service.get_chat_message_contents(
                chat_history=chat_history,
                settings=chat_service.get_prompt_execution_settings_class()(
                    max_tokens=1000,
                    temperature=0.7
                )
            )
            
            # Extract the response text
            answer = response[0].content if response else "I apologize, but I'm having trouble processing your request right now."
            
            # Calculate confidence
            confidence = 0.5  # Base confidence
            if episodic_context:
                confidence += 0.1
            if semantic_context:
                confidence += 0.1
            if procedural_context:
                confidence += 0.1
            
            confidence = min(confidence, 1.0)
            
            return {
                "answer": answer,
                "sources": [],  # Could be enhanced to include actual sources
                "confidence": confidence
            }
            
        except Exception as e:
            print(f"Error generating response with kernel: {e}")
            return {
                "answer": "I apologize, but I'm having trouble processing your request right now. Please try again later.",
                "sources": [],
                "confidence": 0.1
            }
    
    async def _store_interaction(self, user_id: str, query: str, response: Dict[str, Any]):
        """Store interaction in custom memory manager"""
        try:
            # Store in our custom memory manager
            embedding = await get_embedding_openai(query)
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
        try:
            # Initialize in our custom memory manager
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
            
        except Exception as e:
            print(f"Error initializing user memories: {e}")

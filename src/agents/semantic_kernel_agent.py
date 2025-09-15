"""
Semantic Kernel Agentic RAG Implementation
Uses Microsoft Semantic Kernel for production-grade agentic RAG with memory management.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.memory import VolatileMemoryStore
from semantic_kernel.functions import KernelFunction

from .memory_manager import AgenticMemoryManager
from src.app.services.user_context import UserContext
from src.app.services.embeddings_minimal import get_embedding_openai

@dataclass
class SemanticKernelResponse:
    """Response from Semantic Kernel agentic RAG system"""
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    memory_types_used: List[str]
    reasoning_steps: List[str]
    personalized: bool
    execution_plan: Optional[str] = None

class SemanticKernelAgenticRAG:
    """
    Production-grade agentic RAG using Microsoft Semantic Kernel
    """
    
    def __init__(self, memory_manager: AgenticMemoryManager, user_context: UserContext):
        self.memory_manager = memory_manager
        self.user_context = user_context
        self.kernel = self._initialize_kernel()
        self.memory_store = VolatileMemoryStore()
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
        Process query using Semantic Kernel agentic RAG
        """
        self.reasoning_steps = []
        memory_types_used = []
        
        # Step 1: Create execution plan
        self.reasoning_steps.append("Creating execution plan using Semantic Kernel planner")
        execution_plan = await self._create_execution_plan(query, user_id)
        
        # Step 2: Retrieve memories
        self.reasoning_steps.append("Retrieving episodic, semantic, and procedural memories")
        episodic_context = await self._retrieve_episodic_context(user_id, query, context_limit)
        semantic_context = await self._retrieve_semantic_context(query)
        procedural_context = await self._retrieve_procedural_context(query)
        
        if episodic_context:
            memory_types_used.append("episodic")
        if semantic_context:
            memory_types_used.append("semantic")
        if procedural_context:
            memory_types_used.append("procedural")
        
        # Step 3: Build context for the kernel
        self.reasoning_steps.append("Building context for Semantic Kernel execution")
        context = await self._build_kernel_context(
            query, episodic_context, semantic_context, procedural_context, user_id
        )
        
        # Step 4: Execute using Semantic Kernel
        self.reasoning_steps.append("Executing agentic workflow using Semantic Kernel")
        response = await self._execute_kernel_workflow(query, context, execution_plan)
        
        # Step 5: Store interaction
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
    
    async def _create_execution_plan(self, query: str, user_id: str) -> str:
        """Create execution plan using Semantic Kernel"""
        try:
            # Create a simple execution plan using kernel function
            plan_function = KernelFunction.from_prompt(
                function_name="create_execution_plan",
                plugin_name="agentic_rag",
                prompt_template="""
                Create an execution plan for processing this user query:
                
                Query: {{$query}}
                User ID: {{$user_id}}
                
                Steps to follow:
                1. Analyze the query to understand the user's intent
                2. Retrieve relevant memories (episodic, semantic, procedural)
                3. Generate a personalized response using the retrieved context
                4. Provide actionable next steps if appropriate
                5. Store the interaction for future reference
                
                Return a clear, step-by-step execution plan.
                """,
                description="Create execution plan for agentic RAG processing"
            )
            
            # Execute the function
            result = await self.kernel.invoke_async(plan_function, query=query, user_id=user_id)
            return str(result)
            
        except Exception as e:
            print(f"Error creating execution plan: {e}")
            return "Basic execution plan: Analyze query, retrieve context, generate response"
    
    async def _retrieve_episodic_context(self, user_id: str, query: str, limit: int) -> List[Dict[str, Any]]:
        """Retrieve episodic memories using Semantic Kernel memory"""
        try:
            # Use Semantic Kernel memory store
            memories = await self.memory_store.get_nearest_matches(
                collection_name=f"episodic_{user_id}",
                query=query,
                limit=limit
            )
            
            # Convert to our format
            episodic_context = []
            for memory in memories:
                episodic_context.append({
                    "content": memory.text if hasattr(memory, 'text') else str(memory),
                    "timestamp": memory.metadata.get("timestamp", "") if hasattr(memory, 'metadata') else "",
                    "event_type": memory.metadata.get("event_type", "") if hasattr(memory, 'metadata') else ""
                })
            
            return episodic_context
            
        except Exception as e:
            print(f"Error retrieving episodic context: {e}")
            return []
    
    async def _retrieve_semantic_context(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve semantic memories"""
        try:
            # Extract concepts from query
            concepts = await self._extract_concepts_with_kernel(query)
            
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
        """Retrieve procedural memories"""
        try:
            # Identify required skills
            skills = await self._identify_skills_with_kernel(query)
            
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
    
    async def _extract_concepts_with_kernel(self, query: str) -> List[str]:
        """Extract concepts using Semantic Kernel"""
        try:
            # Create a function to extract concepts
            concept_extraction_function = KernelFunction.from_prompt(
                function_name="extract_concepts",
                plugin_name="agentic_rag",
                prompt_template="""
                Extract key concepts from the following query that would be useful for semantic memory lookup.
                
                Query: {{$query}}
                
                Return a JSON list of concepts.
                """,
                description="Extract key concepts from a query"
            )
            
            # Execute the function
            result = await self.kernel.invoke_async(concept_extraction_function, query=query)
            
            # Parse the result
            try:
                concepts = json.loads(str(result))
                return concepts if isinstance(concepts, list) else []
            except:
                return []
                
        except Exception as e:
            print(f"Error extracting concepts: {e}")
            return []
    
    async def _identify_skills_with_kernel(self, query: str) -> List[str]:
        """Identify required skills using Semantic Kernel"""
        try:
            # Create a function to identify skills
            skill_identification_function = KernelFunction.from_prompt(
                function_name="identify_skills",
                plugin_name="agentic_rag",
                prompt_template="""
                Identify the skills or procedures that would be helpful for answering this query.
                
                Query: {{$query}}
                
                Return a JSON list of skill names.
                """,
                description="Identify required skills for a query"
            )
            
            # Execute the function
            result = await self.kernel.invoke_async(skill_identification_function, query=query)
            
            # Parse the result
            try:
                skills = json.loads(str(result))
                return skills if isinstance(skills, list) else []
            except:
                return []
                
        except Exception as e:
            print(f"Error identifying skills: {e}")
            return []
    
    async def _build_kernel_context(self, query: str, episodic_context: List[Dict], 
                                  semantic_context: List[Dict], procedural_context: List[Dict], 
                                  user_id: str) -> Dict[str, Any]:
        """Build context for Semantic Kernel execution"""
        
        # Get user preferences
        user_profile = self.user_context.profile
        preferences = user_profile.preferences if user_profile.preferences else {}
        
        context = {
            "query": query,
            "user_id": user_id,
            "preferences": preferences,
            "episodic_context": episodic_context,
            "semantic_context": semantic_context,
            "procedural_context": procedural_context,
            "timestamp": datetime.now().isoformat()
        }
        
        return context
    
    async def _execute_kernel_workflow(self, query: str, context: Dict[str, Any], 
                                     execution_plan: str) -> Dict[str, Any]:
        """Execute the agentic workflow using Semantic Kernel"""
        try:
            # Create the main response generation function
            response_function = KernelFunction.from_prompt(
                function_name="generate_agentic_response",
                plugin_name="agentic_rag",
                prompt_template="""
                You are an advanced AI learning coach with access to multiple types of memory.
                
                User Query: {{$query}}
                
                User Preferences: {{$preferences}}
                
                Episodic Context (conversation history):
                {{#each episodic_context}}
                - {{content}} ({{event_type}}, {{timestamp}})
                {{/each}}
                
                Semantic Context (domain knowledge):
                {{#each semantic_context}}
                - {{concept}}: {{knowledge.description}} (confidence: {{confidence}})
                {{/each}}
                
                Procedural Context (skills and workflows):
                {{#each procedural_context}}
                - {{skill}}: {{steps.length}} steps available
                {{/each}}
                
                Execution Plan: {{$execution_plan}}
                
                Generate a comprehensive, personalized response that:
                1. Directly addresses the user's query
                2. Incorporates relevant context from all memory types
                3. Provides actionable advice or next steps
                4. Shows understanding of the user's learning journey
                5. References specific sources when helpful
                
                Be conversational, helpful, and personalized based on the user's context.
                """,
                description="Generate personalized agentic response using all memory types"
            )
            
            # Execute the function
            result = await self.kernel.invoke_async(
                response_function,
                query=query,
                preferences=json.dumps(context["preferences"]),
                episodic_context=context["episodic_context"],
                semantic_context=context["semantic_context"],
                procedural_context=context["procedural_context"],
                execution_plan=execution_plan
            )
            
            # Calculate confidence based on available context
            confidence = 0.5  # Base confidence
            if context["episodic_context"]:
                confidence += 0.1
            if context["semantic_context"]:
                confidence += 0.1
            if context["procedural_context"]:
                confidence += 0.1
            
            confidence = min(confidence, 1.0)
            
            return {
                "answer": str(result),
                "sources": [],  # Could be enhanced to include actual sources
                "confidence": confidence
            }
            
        except Exception as e:
            print(f"Error executing kernel workflow: {e}")
            return {
                "answer": "I apologize, but I'm having trouble processing your request right now. Please try again later.",
                "sources": [],
                "confidence": 0.1
            }
    
    async def _store_interaction(self, user_id: str, query: str, response: Dict[str, Any]):
        """Store interaction in Semantic Kernel memory and our custom memory"""
        try:
            # Store in Semantic Kernel memory
            await self.memory_store.create_collection(f"episodic_{user_id}")
            await self.memory_store.get(
                collection_name=f"episodic_{user_id}",
                key=f"interaction_{datetime.now().timestamp()}",
                query=query
            )
            
            # Also store in our custom memory manager
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
        """Initialize default memories for a new user using Semantic Kernel"""
        try:
            # Store basic semantic memories using Semantic Kernel
            await self.memory_store.create_collection(f"semantic_{user_id}")
            await self.memory_store.create_collection(f"procedural_{user_id}")
            
            # Also initialize in our custom memory manager
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

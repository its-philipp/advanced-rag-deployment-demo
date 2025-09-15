"""
LangGraph Agentic RAG Implementation
Uses LangGraph for advanced agent orchestration and state management.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool

from .memory_manager import AgenticMemoryManager
from src.app.services.user_context import UserContext
from src.app.services.embeddings_minimal import get_embedding_openai

class AgentState(TypedDict):
    """State for the LangGraph agent"""
    messages: Annotated[List[Any], "Chat messages"]
    user_id: str
    query: str
    episodic_context: List[Dict[str, Any]]
    semantic_context: List[Dict[str, Any]]
    procedural_context: List[Dict[str, Any]]
    reasoning_steps: List[str]
    memory_types_used: List[str]
    confidence: float
    final_answer: str
    sources: List[Dict[str, Any]]

@dataclass
class LangGraphResponse:
    """Response from LangGraph agentic RAG system"""
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    memory_types_used: List[str]
    reasoning_steps: List[str]
    personalized: bool
    agent_state: Optional[Dict[str, Any]] = None

class LangGraphAgenticRAG:
    """
    Advanced agentic RAG using LangGraph for agent orchestration
    """
    
    def __init__(self, memory_manager: AgenticMemoryManager, user_context: UserContext):
        self.memory_manager = memory_manager
        self.user_context = user_context
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        self.graph = self._build_agent_graph()
        
    def _build_agent_graph(self) -> StateGraph:
        """Build the LangGraph agent workflow"""
        
        # Define the workflow
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("memory_retrieval", self._memory_retrieval_node)
        workflow.add_node("context_analysis", self._context_analysis_node)
        workflow.add_node("response_generation", self._response_generation_node)
        workflow.add_node("memory_storage", self._memory_storage_node)
        
        # Add edges
        workflow.set_entry_point("memory_retrieval")
        workflow.add_edge("memory_retrieval", "context_analysis")
        workflow.add_edge("context_analysis", "response_generation")
        workflow.add_edge("response_generation", "memory_storage")
        workflow.add_edge("memory_storage", END)
        
        return workflow.compile()
    
    async def process_query(self, user_id: str, query: str, 
                          context_limit: int = 3, use_hybrid: bool = True) -> LangGraphResponse:
        """
        Process query using LangGraph agentic RAG
        """
        # Initialize state
        initial_state = AgentState(
            messages=[HumanMessage(content=query)],
            user_id=user_id,
            query=query,
            episodic_context=[],
            semantic_context=[],
            procedural_context=[],
            reasoning_steps=[],
            memory_types_used=[],
            confidence=0.0,
            final_answer="",
            sources=[]
        )
        
        # Execute the graph
        final_state = await self.graph.ainvoke(initial_state)
        
        return LangGraphResponse(
            answer=final_state["final_answer"],
            sources=final_state["sources"],
            confidence=final_state["confidence"],
            memory_types_used=final_state["memory_types_used"],
            reasoning_steps=final_state["reasoning_steps"],
            personalized=len(final_state["memory_types_used"]) > 0,
            agent_state=final_state
        )
    
    async def _memory_retrieval_node(self, state: AgentState) -> AgentState:
        """Retrieve memories from all types"""
        reasoning_steps = state["reasoning_steps"]
        reasoning_steps.append("Retrieving episodic, semantic, and procedural memories")
        
        user_id = state["user_id"]
        query = state["query"]
        
        # Retrieve episodic memories
        episodic_context = await self._retrieve_episodic_memories(user_id, query)
        
        # Retrieve semantic memories
        semantic_context = await self._retrieve_semantic_memories(query)
        
        # Retrieve procedural memories
        procedural_context = await self._retrieve_procedural_memories(query)
        
        # Update memory types used
        memory_types_used = []
        if episodic_context:
            memory_types_used.append("episodic")
        if semantic_context:
            memory_types_used.append("semantic")
        if procedural_context:
            memory_types_used.append("procedural")
        
        return {
            **state,
            "episodic_context": episodic_context,
            "semantic_context": semantic_context,
            "procedural_context": procedural_context,
            "memory_types_used": memory_types_used,
            "reasoning_steps": reasoning_steps
        }
    
    async def _context_analysis_node(self, state: AgentState) -> AgentState:
        """Analyze the retrieved context"""
        reasoning_steps = state["reasoning_steps"]
        reasoning_steps.append("Analyzing retrieved context and user preferences")
        
        # Get user preferences
        user_profile = self.user_context.profile
        preferences = user_profile.preferences if user_profile.preferences else {}
        
        # Create analysis prompt
        analysis_prompt = f"""
        Analyze the following context for the user query: "{state['query']}"
        
        User Preferences: {json.dumps(preferences, indent=2)}
        
        Episodic Context (conversation history):
        {json.dumps(state['episodic_context'], indent=2)}
        
        Semantic Context (domain knowledge):
        {json.dumps(state['semantic_context'], indent=2)}
        
        Procedural Context (skills and workflows):
        {json.dumps(state['procedural_context'], indent=2)}
        
        Provide a brief analysis of:
        1. Most relevant context pieces
        2. User's learning style and preferences
        3. Appropriate response approach
        """
        
        # Get analysis from LLM
        analysis_messages = [
            SystemMessage(content="You are an expert at analyzing learning contexts and user preferences."),
            HumanMessage(content=analysis_prompt)
        ]
        
        analysis_response = await self.llm.ainvoke(analysis_messages)
        reasoning_steps.append(f"Context analysis: {analysis_response.content[:200]}...")
        
        return {
            **state,
            "reasoning_steps": reasoning_steps
        }
    
    async def _response_generation_node(self, state: AgentState) -> AgentState:
        """Generate the final response"""
        reasoning_steps = state["reasoning_steps"]
        reasoning_steps.append("Generating personalized response using all context")
        
        # Get user preferences
        user_profile = self.user_context.profile
        preferences = user_profile.preferences if user_profile.preferences else {}
        
        # Create response generation prompt
        response_prompt = f"""
        You are an advanced AI learning coach with access to multiple types of memory.
        
        User Query: {state['query']}
        
        User Preferences: {json.dumps(preferences, indent=2)}
        
        Episodic Context (conversation history):
        {json.dumps(state['episodic_context'], indent=2)}
        
        Semantic Context (domain knowledge):
        {json.dumps(state['semantic_context'], indent=2)}
        
        Procedural Context (skills and workflows):
        {json.dumps(state['procedural_context'], indent=2)}
        
        Generate a comprehensive, personalized response that:
        1. Directly addresses the user's query
        2. Incorporates relevant context from all memory types
        3. Provides actionable advice or next steps
        4. Shows understanding of the user's learning journey
        5. References specific sources when helpful
        
        Be conversational, helpful, and personalized based on the user's context.
        """
        
        # Generate response
        response_messages = [
            SystemMessage(content="You are a personalized AI learning coach with advanced memory capabilities."),
            HumanMessage(content=response_prompt)
        ]
        
        response = await self.llm.ainvoke(response_messages)
        
        # Calculate confidence
        confidence = 0.5  # Base confidence
        if state["episodic_context"]:
            confidence += 0.1
        if state["semantic_context"]:
            confidence += 0.1
        if state["procedural_context"]:
            confidence += 0.1
        
        confidence = min(confidence, 1.0)
        
        return {
            **state,
            "final_answer": response.content,
            "confidence": confidence,
            "sources": [],  # Could be enhanced to include actual sources
            "reasoning_steps": reasoning_steps
        }
    
    async def _memory_storage_node(self, state: AgentState) -> AgentState:
        """Store the interaction in memory"""
        reasoning_steps = state["reasoning_steps"]
        reasoning_steps.append("Storing interaction in memory systems")
        
        user_id = state["user_id"]
        query = state["query"]
        
        try:
            # Store in episodic memory
            embedding = await get_embedding_openai(query)
            await self.memory_manager.store_episodic(
                user_id=user_id,
                event_type="conversation",
                content=query,
                context={
                    "response": state["final_answer"],
                    "confidence": state["confidence"],
                    "sources_count": len(state["sources"])
                },
                embedding=embedding
            )
            
            # Update user context
            self.user_context.profile.total_sessions += 1
            self.user_context.profile.last_active = time.time()
            
        except Exception as e:
            print(f"Error storing interaction: {e}")
        
        return {
            **state,
            "reasoning_steps": reasoning_steps
        }
    
    async def _retrieve_episodic_memories(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """Retrieve episodic memories"""
        try:
            memories = await self.memory_manager.retrieve_episodic(
                user_id=user_id,
                query=query,
                event_type="conversation",
                limit=3
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
            print(f"Error retrieving episodic memories: {e}")
            return []
    
    async def _retrieve_semantic_memories(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve semantic memories"""
        try:
            # Extract concepts from query
            concepts = await self._extract_concepts_with_llm(query)
            
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
            print(f"Error retrieving semantic memories: {e}")
            return []
    
    async def _retrieve_procedural_memories(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve procedural memories"""
        try:
            # Identify required skills
            skills = await self._identify_skills_with_llm(query)
            
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
            print(f"Error retrieving procedural memories: {e}")
            return []
    
    async def _extract_concepts_with_llm(self, query: str) -> List[str]:
        """Extract concepts using LLM"""
        try:
            concept_prompt = f"""
            Extract key concepts from the following query that would be useful for semantic memory lookup.
            
            Query: {query}
            
            Return a JSON list of concepts.
            """
            
            messages = [
                SystemMessage(content="You are an expert at extracting key concepts from queries."),
                HumanMessage(content=concept_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            try:
                concepts = json.loads(response.content)
                return concepts if isinstance(concepts, list) else []
            except:
                return []
                
        except Exception as e:
            print(f"Error extracting concepts: {e}")
            return []
    
    async def _identify_skills_with_llm(self, query: str) -> List[str]:
        """Identify required skills using LLM"""
        try:
            skill_prompt = f"""
            Identify the skills or procedures that would be helpful for answering this query.
            
            Query: {query}
            
            Return a JSON list of skill names.
            """
            
            messages = [
                SystemMessage(content="You are an expert at identifying required skills for queries."),
                HumanMessage(content=skill_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            try:
                skills = json.loads(response.content)
                return skills if isinstance(skills, list) else []
            except:
                return []
                
        except Exception as e:
            print(f"Error identifying skills: {e}")
            return []
    
    async def initialize_user_memories(self, user_id: str):
        """Initialize default memories for a new user"""
        try:
            # Store basic semantic memories
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
            
            # Store procedural memories
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

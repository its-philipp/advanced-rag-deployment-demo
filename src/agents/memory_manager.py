"""
Agentic RAG Memory Manager
Implements episodic, semantic, and procedural memory for agentic RAG systems.
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class MemoryType(Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"

@dataclass
class EpisodicMemory:
    """Represents an episodic memory entry"""
    timestamp: str
    user_id: str
    event_type: str
    content: str
    context: Dict[str, Any]
    embedding: Optional[List[float]] = None

@dataclass
class SemanticMemory:
    """Represents a semantic memory entry"""
    concept: str
    knowledge: Dict[str, Any]
    relationships: List[str]
    confidence: float
    last_updated: str

@dataclass
class ProceduralMemory:
    """Represents a procedural memory entry"""
    skill: str
    steps: List[Dict[str, Any]]
    prerequisites: List[str]
    success_criteria: List[str]
    last_used: str

class AgenticMemoryManager:
    """
    Manages episodic, semantic, and procedural memory for agentic RAG systems.
    """
    
    def __init__(self, qdrant_client=None):
        self.qdrant_client = qdrant_client
        self.episodic_memories: Dict[str, List[EpisodicMemory]] = {}
        self.semantic_memories: Dict[str, SemanticMemory] = {}
        self.procedural_memories: Dict[str, ProceduralMemory] = {}
        
    async def store_episodic(self, user_id: str, event_type: str, content: str, 
                           context: Dict[str, Any] = None, embedding: List[float] = None) -> str:
        """
        Store episodic memory (conversations, events, experiences)
        
        Args:
            user_id: User identifier
            event_type: Type of event (conversation, learning, interaction)
            content: Content of the memory
            context: Additional context information
            embedding: Vector embedding for similarity search
            
        Returns:
            Memory ID
        """
        if user_id not in self.episodic_memories:
            self.episodic_memories[user_id] = []
        
        memory = EpisodicMemory(
            timestamp=datetime.now().isoformat(),
            user_id=user_id,
            event_type=event_type,
            content=content,
            context=context or {},
            embedding=embedding
        )
        
        self.episodic_memories[user_id].append(memory)
        
        # Store in vector database if available
        if self.qdrant_client and embedding:
            await self._store_episodic_vector(memory, embedding)
        
        return f"episodic_{user_id}_{len(self.episodic_memories[user_id])}"
    
    async def store_semantic(self, concept: str, knowledge: Dict[str, Any], 
                           relationships: List[str] = None, confidence: float = 0.8) -> str:
        """
        Store semantic memory (facts, concepts, knowledge)
        
        Args:
            concept: The concept or topic
            knowledge: Knowledge about the concept
            relationships: Related concepts
            confidence: Confidence in the knowledge
            
        Returns:
            Memory ID
        """
        memory = SemanticMemory(
            concept=concept,
            knowledge=knowledge,
            relationships=relationships or [],
            confidence=confidence,
            last_updated=datetime.now().isoformat()
        )
        
        self.semantic_memories[concept] = memory
        return f"semantic_{concept}"
    
    async def store_procedural(self, skill: str, steps: List[Dict[str, Any]], 
                             prerequisites: List[str] = None, 
                             success_criteria: List[str] = None) -> str:
        """
        Store procedural memory (skills, workflows, procedures)
        
        Args:
            skill: Name of the skill or procedure
            steps: List of steps in the procedure
            prerequisites: Required prerequisites
            success_criteria: Criteria for successful completion
            
        Returns:
            Memory ID
        """
        memory = ProceduralMemory(
            skill=skill,
            steps=steps,
            prerequisites=prerequisites or [],
            success_criteria=success_criteria or [],
            last_used=datetime.now().isoformat()
        )
        
        self.procedural_memories[skill] = memory
        return f"procedural_{skill}"
    
    async def retrieve_episodic(self, user_id: str, query: str = None, 
                              event_type: str = None, limit: int = 5) -> List[EpisodicMemory]:
        """
        Retrieve episodic memories for a user
        
        Args:
            user_id: User identifier
            query: Search query for content similarity
            event_type: Filter by event type
            limit: Maximum number of memories to return
            
        Returns:
            List of episodic memories
        """
        if user_id not in self.episodic_memories:
            return []
        
        memories = self.episodic_memories[user_id]
        
        # Filter by event type if specified
        if event_type:
            memories = [m for m in memories if m.event_type == event_type]
        
        # Simple text search if no vector search available
        if query and not self.qdrant_client:
            memories = [m for m in memories if query.lower() in m.content.lower()]
        
        # Return most recent memories
        return sorted(memories, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    async def retrieve_semantic(self, concept: str = None, 
                              relationships: List[str] = None) -> List[SemanticMemory]:
        """
        Retrieve semantic memories
        
        Args:
            concept: Specific concept to retrieve
            relationships: Concepts related to these terms
            
        Returns:
            List of semantic memories
        """
        if concept:
            return [self.semantic_memories[concept]] if concept in self.semantic_memories else []
        
        if relationships:
            related = []
            for concept, memory in self.semantic_memories.items():
                if any(rel in memory.relationships for rel in relationships):
                    related.append(memory)
            return related
        
        return list(self.semantic_memories.values())
    
    async def retrieve_procedural(self, skill: str = None, 
                                prerequisites: List[str] = None) -> List[ProceduralMemory]:
        """
        Retrieve procedural memories
        
        Args:
            skill: Specific skill to retrieve
            prerequisites: Skills that meet these prerequisites
            
        Returns:
            List of procedural memories
        """
        if skill:
            return [self.procedural_memories[skill]] if skill in self.procedural_memories else []
        
        if prerequisites:
            matching = []
            for skill, memory in self.procedural_memories.items():
                if all(prereq in memory.prerequisites for prereq in prerequisites):
                    matching.append(memory)
            return matching
        
        return list(self.procedural_memories.values())
    
    async def _store_episodic_vector(self, memory: EpisodicMemory, embedding: List[float]):
        """Store episodic memory in vector database"""
        if not self.qdrant_client:
            return
        
        # Implementation would depend on your vector database setup
        # This is a placeholder for Qdrant integration
        pass
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about stored memories"""
        return {
            "episodic": {
                "total_users": len(self.episodic_memories),
                "total_memories": sum(len(memories) for memories in self.episodic_memories.values())
            },
            "semantic": {
                "total_concepts": len(self.semantic_memories)
            },
            "procedural": {
                "total_skills": len(self.procedural_memories)
            }
        }

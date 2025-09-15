#!/usr/bin/env python3
"""
Minimal Test for Production Frameworks
Tests basic functionality before running comprehensive tests
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

async def test_imports():
    """Test if all imports work"""
    print("🔍 Testing imports...")
    
    try:
        from src.agents.memory_manager import AgenticMemoryManager
        print("✅ Memory manager import successful")
    except Exception as e:
        print(f"❌ Memory manager import failed: {e}")
        return False
    
    try:
        from src.app.services.user_context import UserContext
        print("✅ User context import successful")
    except Exception as e:
        print(f"❌ User context import failed: {e}")
        return False
    
    try:
        from src.agents.agentic_rag_agent import AgenticRAGAgent
        print("✅ Custom agent import successful")
    except Exception as e:
        print(f"❌ Custom agent import failed: {e}")
        return False
    
    try:
        from src.agents.semantic_kernel_agent import SemanticKernelAgenticRAG
        print("✅ Semantic Kernel agent import successful")
    except Exception as e:
        print(f"❌ Semantic Kernel agent import failed: {e}")
        return False
    
    try:
        from src.agents.langgraph_agent import LangGraphAgenticRAG
        print("✅ LangGraph agent import successful")
    except Exception as e:
        print(f"❌ LangGraph agent import failed: {e}")
        return False
    
    return True

async def test_basic_functionality():
    """Test basic functionality of each framework"""
    print("\n🧪 Testing basic functionality...")
    
    # Initialize components
    from src.agents.memory_manager import AgenticMemoryManager
    from src.app.services.user_context import UserContext
    
    memory_manager = AgenticMemoryManager()
    user_context = UserContext("test_user")
    
    # Initialize user context
    user_context.update_preferences({"learning_style": "visual"})
    user_context.update_learning_goals(["Learn AI"])
    
    # Test Custom Implementation
    print("\n📝 Testing Custom Implementation...")
    try:
        from src.agents.agentic_rag_agent import AgenticRAGAgent
        custom_agent = AgenticRAGAgent(memory_manager, user_context)
        await custom_agent.initialize_user_memories("test_user")
        
        response = await custom_agent.process_query(
            user_id="test_user",
            query="What is machine learning?",
            context_limit=3
        )
        print(f"✅ Custom agent response: {response.answer[:100]}...")
    except Exception as e:
        print(f"❌ Custom agent failed: {e}")
    
    # Test Semantic Kernel (if available)
    print("\n📝 Testing Semantic Kernel...")
    try:
        from src.agents.semantic_kernel_agent import SemanticKernelAgenticRAG
        semantic_agent = SemanticKernelAgenticRAG(memory_manager, user_context)
        await semantic_agent.initialize_user_memories("test_user")
        
        response = await semantic_agent.process_query(
            user_id="test_user",
            query="What is machine learning?",
            context_limit=3
        )
        print(f"✅ Semantic Kernel response: {response.answer[:100]}...")
    except Exception as e:
        print(f"❌ Semantic Kernel failed: {e}")
    
    # Test LangGraph (if available)
    print("\n📝 Testing LangGraph...")
    try:
        from src.agents.langgraph_agent import LangGraphAgenticRAG
        langgraph_agent = LangGraphAgenticRAG(memory_manager, user_context)
        await langgraph_agent.initialize_user_memories("test_user")
        
        response = await langgraph_agent.process_query(
            user_id="test_user",
            query="What is machine learning?",
            context_limit=3
        )
        print(f"✅ LangGraph response: {response.answer[:100]}...")
    except Exception as e:
        print(f"❌ LangGraph failed: {e}")

async def main():
    """Main test function"""
    print("🚀 Minimal Production Frameworks Test")
    print("=" * 50)
    
    # Test imports
    if not await test_imports():
        print("\n❌ Import tests failed. Please fix import issues first.")
        return
    
    # Test basic functionality
    await test_basic_functionality()
    
    print("\n✨ Minimal testing completed!")

if __name__ == "__main__":
    asyncio.run(main())

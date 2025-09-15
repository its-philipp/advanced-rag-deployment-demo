#!/usr/bin/env python3
"""
Enhanced Production Frameworks Test
With comprehensive monitoring, persistence, and performance analysis
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from src.agents.framework_monitor import FrameworkMonitor
from src.agents.persistent_memory import PersistentMemoryManager
from src.agents.memory_manager import AgenticMemoryManager
from src.agents.agentic_rag_agent import AgenticRAGAgent
from src.agents.langgraph_agent import LangGraphAgenticRAG
from src.agents.semantic_kernel_simple import SemanticKernelSimpleRAG
from src.app.services.user_context import UserContext

async def test_enhanced_frameworks():
    """Test enhanced frameworks with monitoring and persistence"""
    print("🚀 Enhanced Production Frameworks Test")
    print("=" * 60)
    
    # Initialize components
    print("🔧 Initializing enhanced components...")
    
    # Persistent memory manager
    persistent_memory = PersistentMemoryManager()
    
    # Framework monitor
    monitor = FrameworkMonitor("enhanced_framework_monitor.log")
    
    # Memory manager (in-memory for now, can be enhanced with persistence)
    memory_manager = AgenticMemoryManager()
    
    # User context
    user_context = UserContext("enhanced_test_user")
    user_context.update_preferences({"learning_style": "visual", "difficulty": "intermediate"})
    user_context.update_learning_goals(["Learn AI", "Master machine learning"])
    
    # Initialize frameworks
    print("🤖 Initializing frameworks...")
    
    frameworks = {
        "Custom Implementation": AgenticRAGAgent(memory_manager, user_context),
        "LangGraph Implementation": LangGraphAgenticRAG(memory_manager, user_context),
        "Semantic Kernel Implementation": SemanticKernelSimpleRAG(memory_manager, user_context)
    }
    
    # Initialize memories for all frameworks
    print("🧠 Initializing memories...")
    
    # Store in persistent memory
    await persistent_memory.store_semantic(
        concept="machine_learning",
        knowledge={
            "description": "Machine learning is a subset of artificial intelligence",
            "key_concepts": ["supervised learning", "unsupervised learning", "neural networks"],
            "applications": ["image recognition", "natural language processing", "predictive analytics"]
        },
        relationships=["artificial_intelligence", "data_science"]
    )
    
    await persistent_memory.store_procedural(
        skill="learning_machine_learning",
        steps=[
            {"step": 1, "action": "Learn Python basics", "description": "Master Python programming fundamentals"},
            {"step": 2, "action": "Study mathematics", "description": "Learn linear algebra, calculus, and statistics"},
            {"step": 3, "action": "Practice with datasets", "description": "Work with real-world datasets"},
            {"step": 4, "action": "Build projects", "description": "Create end-to-end ML projects"}
        ],
        prerequisites=["basic_programming", "high_school_math"],
        success_criteria=["can_build_ml_models", "understands_algorithms"]
    )
    
    # Store user profile
    await persistent_memory.store_user_profile(
        user_id="enhanced_test_user",
        preferences={"learning_style": "visual", "difficulty": "intermediate"},
        learning_goals=["Learn AI", "Master machine learning"],
        learning_style="visual"
    )
    
    # Initialize frameworks with memories
    for framework_name, framework in frameworks.items():
        await framework.initialize_user_memories("enhanced_test_user")
    
    print("✅ Enhanced components initialized!")
    
    # Test queries
    test_queries = [
        "What is machine learning and how should I learn it?",
        "I'm struggling with understanding neural networks. Can you help?",
        "What are the best strategies for learning machine learning?",
        "How can I improve my problem-solving skills?",
        "What's the difference between supervised and unsupervised learning?"
    ]
    
    # Run comprehensive tests
    print("\n🧪 Running comprehensive enhanced tests...")
    results = await monitor.run_comprehensive_test(
        frameworks=frameworks,
        user_id="enhanced_test_user",
        test_queries=test_queries
    )
    
    # Store performance metrics in persistent memory
    print("\n💾 Storing performance metrics...")
    for query_key, query_data in results.items():
        query = query_data["query"]
        comparison = query_data["results"]
        
        for framework_name, metrics in comparison.results.items():
            await persistent_memory.store_performance_metrics(
                framework=framework_name,
                query=query,
                response_time=metrics.response_time,
                confidence=metrics.confidence,
                memory_types_used=metrics.memory_types_used,
                personalized=metrics.personalized,
                success=metrics.success
            )
    
    # Get performance summary from persistent memory
    print("\n📊 Performance Summary from Persistent Memory:")
    print("-" * 50)
    
    performance_summary = await persistent_memory.get_performance_summary()
    for framework, stats in performance_summary.items():
        print(f"\n🔧 {framework}")
        print(f"   Total Queries: {stats['total_queries']}")
        print(f"   Success Rate: {stats['success_rate']:.1%}")
        print(f"   Avg Response Time: {stats['avg_response_time']:.2f}s")
        print(f"   Avg Confidence: {stats['avg_confidence']:.2f}")
        print(f"   Personalization Rate: {stats['personalization_rate']:.1%}")
    
    # Database statistics
    print("\n💾 Database Statistics:")
    print("-" * 30)
    
    db_stats = persistent_memory.get_database_stats()
    for key, value in db_stats.items():
        if key.endswith('_count'):
            print(f"   {key.replace('_count', '').title()}: {value}")
        else:
            print(f"   {key}: {value:.2f}MB")
    
    # Test persistent memory retrieval
    print("\n🔍 Testing Persistent Memory Retrieval:")
    print("-" * 40)
    
    # Test semantic memory retrieval
    semantic_memories = await persistent_memory.retrieve_semantic("machine_learning")
    print(f"   Semantic memories for 'machine_learning': {len(semantic_memories)}")
    
    # Test procedural memory retrieval
    procedural_memories = await persistent_memory.retrieve_procedural("learning")
    print(f"   Procedural memories for 'learning': {len(procedural_memories)}")
    
    # Test user profile retrieval
    user_profile = await persistent_memory.get_user_profile("enhanced_test_user")
    if user_profile:
        print(f"   User profile loaded: {user_profile['learning_style']} learner")
    
    # Memory usage analysis
    print("\n🧠 Memory Usage Analysis:")
    print("-" * 30)
    
    # Get memory counts
    episodic_count = db_stats['episodic_memories_count']
    semantic_count = db_stats['semantic_memories_count']
    procedural_count = db_stats['procedural_memories_count']
    
    total_memories = episodic_count + semantic_count + procedural_count
    print(f"   Total Memories: {total_memories}")
    print(f"   Episodic: {episodic_count} ({episodic_count/total_memories*100:.1f}%)")
    print(f"   Semantic: {semantic_count} ({semantic_count/total_memories*100:.1f}%)")
    print(f"   Procedural: {procedural_count} ({procedural_count/total_memories*100:.1f}%)")
    
    # Performance recommendations
    print("\n🎯 PERFORMANCE RECOMMENDATIONS")
    print("=" * 40)
    
    if performance_summary:
        # Find best performing framework
        best_framework = max(performance_summary.items(), 
                           key=lambda x: x[1]['success_rate'] * x[1]['avg_confidence'])
        
        print(f"🏆 Best Overall: {best_framework[0]}")
        print(f"   Success Rate: {best_framework[1]['success_rate']:.1%}")
        print(f"   Confidence: {best_framework[1]['avg_confidence']:.2f}")
        
        # Find fastest framework
        fastest_framework = min(performance_summary.items(), 
                              key=lambda x: x[1]['avg_response_time'])
        
        print(f"🚀 Fastest: {fastest_framework[0]}")
        print(f"   Response Time: {fastest_framework[1]['avg_response_time']:.2f}s")
        
        # Find most personalized framework
        most_personalized = max(performance_summary.items(), 
                              key=lambda x: x[1]['personalization_rate'])
        
        print(f"🎨 Most Personalized: {most_personalized[0]}")
        print(f"   Personalization Rate: {most_personalized[1]['personalization_rate']:.1%}")
    
    # Cleanup recommendations
    print(f"\n🧹 Cleanup Recommendations:")
    print(f"   - Database size: {db_stats['database_size_mb']:.2f}MB")
    if db_stats['database_size_mb'] > 100:
        print(f"   - Consider running cleanup (data older than 90 days)")
        await persistent_memory.cleanup_old_data()
    
    print("\n✨ Enhanced framework testing completed!")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    asyncio.run(test_enhanced_frameworks())

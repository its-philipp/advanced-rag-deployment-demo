#!/usr/bin/env python3
"""
Test Production Frameworks for Agentic RAG
Compares Custom Implementation vs Semantic Kernel vs LangGraph
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from src.agents.production_frameworks import ProductionFrameworksComparison
from src.agents.memory_manager import AgenticMemoryManager
from src.app.services.user_context import UserContext

async def test_production_frameworks():
    """Test all production frameworks"""
    print("🚀 Testing Production Frameworks for Agentic RAG")
    print("=" * 60)
    
    # Initialize components
    print("🔧 Initializing components...")
    memory_manager = AgenticMemoryManager()
    user_context = UserContext("production_test_user")
    
    # Initialize user
    await user_context.initialize_user("production_test_user", {
        "preferences": {
            "learning_style": "visual",
            "difficulty_level": "intermediate",
            "topics": ["machine_learning", "programming", "problem_solving"]
        },
        "goals": ["Learn machine learning", "Improve problem-solving skills"],
        "total_sessions": 0
    })
    
    # Initialize comparison framework
    comparison = ProductionFrameworksComparison(memory_manager, user_context)
    
    # Initialize memories for all frameworks
    print("🧠 Initializing memories for all frameworks...")
    await comparison.custom_agent.initialize_user_memories("production_test_user")
    await comparison.semantic_kernel_agent.initialize_user_memories("production_test_user")
    await comparison.langgraph_agent.initialize_user_memories("production_test_user")
    
    # Store some test memories
    print("📝 Storing test memories...")
    
    # Semantic memories
    await memory_manager.store_semantic(
        concept="machine_learning",
        knowledge={
            "description": "Machine learning is a subset of artificial intelligence",
            "key_concepts": ["supervised learning", "unsupervised learning", "neural networks"],
            "applications": ["image recognition", "natural language processing", "predictive analytics"]
        },
        relationships=["artificial_intelligence", "data_science"]
    )
    
    await memory_manager.store_semantic(
        concept="neural_networks",
        knowledge={
            "description": "Neural networks are computing systems inspired by biological neural networks",
            "key_components": ["neurons", "layers", "weights", "activation_functions"],
            "types": ["feedforward", "recurrent", "convolutional"]
        },
        relationships=["machine_learning", "deep_learning"]
    )
    
    # Procedural memories
    await memory_manager.store_procedural(
        skill="learning_machine_learning",
        steps=[
            {"step": 1, "action": "Learn Python basics", "description": "Master Python programming fundamentals"},
            {"step": 2, "action": "Study mathematics", "description": "Learn linear algebra, calculus, and statistics"},
            {"step": 3, "action": "Practice with datasets", "description": "Work with real-world datasets"},
            {"step": 4, "action": "Build projects", "description": "Create end-to-end ML projects"},
            {"step": 5, "action": "Join community", "description": "Participate in ML communities and competitions"}
        ],
        prerequisites=["basic_programming", "high_school_math"],
        success_criteria=["can_build_ml_models", "understands_algorithms"]
    )
    
    # Episodic memories
    await memory_manager.store_episodic(
        user_id="production_test_user",
        event_type="conversation",
        content="I want to learn machine learning but don't know where to start",
        context={"topic": "learning_path", "difficulty": "beginner"},
        embedding=[0.1] * 1536  # Dummy embedding
    )
    
    await memory_manager.store_episodic(
        user_id="production_test_user",
        event_type="conversation",
        content="I'm particularly interested in neural networks and deep learning",
        context={"topic": "neural_networks", "interest": "high"},
        embedding=[0.2] * 1536  # Dummy embedding
    )
    
    print("✅ Memories initialized successfully!")
    
    # Run comprehensive tests
    print("\n🧪 Running comprehensive framework comparison...")
    all_results = await comparison.run_comprehensive_test("production_test_user")
    
    # Print final summary
    print("\n🏆 FINAL SUMMARY")
    print("=" * 60)
    
    # Calculate average performance metrics
    framework_stats = {}
    
    for query_key, query_data in all_results.items():
        for framework_name, result in query_data["results"].items():
            if framework_name not in framework_stats:
                framework_stats[framework_name] = {
                    "total_time": 0,
                    "total_confidence": 0,
                    "total_queries": 0,
                    "successful_queries": 0,
                    "total_memory_types": 0
                }
            
            if not result.error:
                framework_stats[framework_name]["total_time"] += result.response_time
                framework_stats[framework_name]["total_confidence"] += result.confidence
                framework_stats[framework_name]["total_memory_types"] += len(result.memory_usage)
                framework_stats[framework_name]["successful_queries"] += 1
            
            framework_stats[framework_name]["total_queries"] += 1
    
    # Print statistics
    for framework_name, stats in framework_stats.items():
        if stats["successful_queries"] > 0:
            avg_time = stats["total_time"] / stats["successful_queries"]
            avg_confidence = stats["total_confidence"] / stats["successful_queries"]
            avg_memory_types = stats["total_memory_types"] / stats["successful_queries"]
            success_rate = stats["successful_queries"] / stats["total_queries"]
            
            print(f"\n📊 {framework_name.upper()}")
            print(f"   Success Rate: {success_rate:.1%}")
            print(f"   Avg Response Time: {avg_time:.2f}s")
            print(f"   Avg Confidence: {avg_confidence:.2f}")
            print(f"   Avg Memory Types: {avg_memory_types:.1f}")
    
    print("\n🎯 RECOMMENDATIONS")
    print("-" * 30)
    
    # Find best framework for different criteria
    if framework_stats:
        best_time = min(framework_stats.items(), key=lambda x: x[1]["total_time"] / max(x[1]["successful_queries"], 1))
        best_confidence = max(framework_stats.items(), key=lambda x: x[1]["total_confidence"] / max(x[1]["successful_queries"], 1))
        best_success = max(framework_stats.items(), key=lambda x: x[1]["successful_queries"] / x[1]["total_queries"])
        
        print(f"🚀 Fastest: {best_time[0]} (avg {best_time[1]['total_time'] / max(best_time[1]['successful_queries'], 1):.2f}s)")
        print(f"🎯 Most Confident: {best_confidence[0]} (avg {best_confidence[1]['total_confidence'] / max(best_confidence[1]['successful_queries'], 1):.2f})")
        print(f"✅ Most Reliable: {best_success[0]} ({best_success[1]['successful_queries'] / best_success[1]['total_queries']:.1%} success rate)")
    
    print("\n✨ Production frameworks testing completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_production_frameworks())

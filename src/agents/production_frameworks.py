"""
Production Frameworks Comparison
Compares custom implementation vs Semantic Kernel vs LangGraph
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .agentic_rag_agent import AgenticRAGAgent
from .semantic_kernel_agent import SemanticKernelAgenticRAG
from .langgraph_agent import LangGraphAgenticRAG
from .memory_manager import AgenticMemoryManager
from src.app.services.user_context import UserContext

@dataclass
class FrameworkComparison:
    """Results from comparing different frameworks"""
    framework: str
    response_time: float
    answer_quality: str
    memory_usage: List[str]
    reasoning_steps: List[str]
    confidence: float
    personalized: bool
    error: Optional[str] = None

class ProductionFrameworksComparison:
    """
    Compare custom implementation vs production frameworks
    """
    
    def __init__(self, memory_manager: AgenticMemoryManager, user_context: UserContext):
        self.memory_manager = memory_manager
        self.user_context = user_context
        
        # Initialize all frameworks
        self.custom_agent = AgenticRAGAgent(memory_manager, user_context)
        self.semantic_kernel_agent = SemanticKernelAgenticRAG(memory_manager, user_context)
        self.langgraph_agent = LangGraphAgenticRAG(memory_manager, user_context)
    
    async def compare_frameworks(self, user_id: str, query: str, 
                               context_limit: int = 3) -> Dict[str, FrameworkComparison]:
        """
        Compare all three frameworks on the same query
        """
        results = {}
        
        # Test Custom Implementation
        print("🧪 Testing Custom Implementation...")
        custom_result = await self._test_custom_implementation(user_id, query, context_limit)
        results["custom"] = custom_result
        
        # Test Semantic Kernel
        print("🧪 Testing Semantic Kernel...")
        semantic_kernel_result = await self._test_semantic_kernel(user_id, query, context_limit)
        results["semantic_kernel"] = semantic_kernel_result
        
        # Test LangGraph
        print("🧪 Testing LangGraph...")
        langgraph_result = await self._test_langgraph(user_id, query, context_limit)
        results["langgraph"] = langgraph_result
        
        return results
    
    async def _test_custom_implementation(self, user_id: str, query: str, 
                                       context_limit: int) -> FrameworkComparison:
        """Test custom implementation"""
        start_time = time.time()
        
        try:
            response = await self.custom_agent.process_query(
                user_id=user_id,
                query=query,
                context_limit=context_limit,
                use_hybrid=True
            )
            
            end_time = time.time()
            
            return FrameworkComparison(
                framework="Custom Implementation",
                response_time=end_time - start_time,
                answer_quality=response.answer,
                memory_usage=response.memory_types_used,
                reasoning_steps=response.reasoning_steps,
                confidence=response.confidence,
                personalized=response.personalized
            )
            
        except Exception as e:
            return FrameworkComparison(
                framework="Custom Implementation",
                response_time=0.0,
                answer_quality="",
                memory_usage=[],
                reasoning_steps=[],
                confidence=0.0,
                personalized=False,
                error=str(e)
            )
    
    async def _test_semantic_kernel(self, user_id: str, query: str, 
                                  context_limit: int) -> FrameworkComparison:
        """Test Semantic Kernel implementation"""
        start_time = time.time()
        
        try:
            response = await self.semantic_kernel_agent.process_query(
                user_id=user_id,
                query=query,
                context_limit=context_limit,
                use_hybrid=True
            )
            
            end_time = time.time()
            
            return FrameworkComparison(
                framework="Semantic Kernel",
                response_time=end_time - start_time,
                answer_quality=response.answer,
                memory_usage=response.memory_types_used,
                reasoning_steps=response.reasoning_steps,
                confidence=response.confidence,
                personalized=response.personalized
            )
            
        except Exception as e:
            return FrameworkComparison(
                framework="Semantic Kernel",
                response_time=0.0,
                answer_quality="",
                memory_usage=[],
                reasoning_steps=[],
                confidence=0.0,
                personalized=False,
                error=str(e)
            )
    
    async def _test_langgraph(self, user_id: str, query: str, 
                            context_limit: int) -> FrameworkComparison:
        """Test LangGraph implementation"""
        start_time = time.time()
        
        try:
            response = await self.langgraph_agent.process_query(
                user_id=user_id,
                query=query,
                context_limit=context_limit,
                use_hybrid=True
            )
            
            end_time = time.time()
            
            return FrameworkComparison(
                framework="LangGraph",
                response_time=end_time - start_time,
                answer_quality=response.answer,
                memory_usage=response.memory_types_used,
                reasoning_steps=response.reasoning_steps,
                confidence=response.confidence,
                personalized=response.personalized
            )
            
        except Exception as e:
            return FrameworkComparison(
                framework="LangGraph",
                response_time=0.0,
                answer_quality="",
                memory_usage=[],
                reasoning_steps=[],
                confidence=0.0,
                personalized=False,
                error=str(e)
            )
    
    def print_comparison_results(self, results: Dict[str, FrameworkComparison]):
        """Print formatted comparison results"""
        print("\n" + "="*80)
        print("🏆 PRODUCTION FRAMEWORKS COMPARISON RESULTS")
        print("="*80)
        
        for framework_name, result in results.items():
            print(f"\n📊 {result.framework.upper()}")
            print("-" * 50)
            
            if result.error:
                print(f"❌ Error: {result.error}")
                continue
            
            print(f"⏱️  Response Time: {result.response_time:.2f}s")
            print(f"🎯 Confidence: {result.confidence:.2f}")
            print(f"🧠 Memory Types Used: {', '.join(result.memory_usage) if result.memory_usage else 'None'}")
            print(f"🤖 Personalized: {'Yes' if result.personalized else 'No'}")
            print(f"📝 Answer Preview: {result.answer_quality[:200]}...")
            print(f"🔍 Reasoning Steps: {len(result.reasoning_steps)} steps")
            
            if result.reasoning_steps:
                print("   Steps:")
                for i, step in enumerate(result.reasoning_steps[:3], 1):
                    print(f"   {i}. {step}")
                if len(result.reasoning_steps) > 3:
                    print(f"   ... and {len(result.reasoning_steps) - 3} more")
        
        # Performance summary
        print(f"\n📈 PERFORMANCE SUMMARY")
        print("-" * 30)
        
        successful_results = {k: v for k, v in results.items() if not v.error}
        
        if successful_results:
            fastest = min(successful_results.values(), key=lambda x: x.response_time)
            most_confident = max(successful_results.values(), key=lambda x: x.confidence)
            most_personalized = max(successful_results.values(), key=lambda x: len(x.memory_usage))
            
            print(f"🚀 Fastest: {fastest.framework} ({fastest.response_time:.2f}s)")
            print(f"🎯 Most Confident: {most_confident.framework} ({most_confident.confidence:.2f})")
            print(f"🧠 Most Personalized: {most_personalized.framework} ({len(most_personalized.memory_usage)} memory types)")
        
        print("\n" + "="*80)
    
    async def run_comprehensive_test(self, user_id: str) -> Dict[str, Any]:
        """Run comprehensive tests across all frameworks"""
        test_queries = [
            "What are the best strategies for learning machine learning?",
            "I'm struggling with understanding neural networks. Can you help?",
            "What was the first step you mentioned for learning machine learning?",
            "How can I improve my problem-solving skills?",
            "What's the difference between supervised and unsupervised learning?"
        ]
        
        all_results = {}
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🧪 Test Query {i}/{len(test_queries)}: {query}")
            print("-" * 60)
            
            results = await self.compare_frameworks(user_id, query)
            all_results[f"query_{i}"] = {
                "query": query,
                "results": results
            }
            
            # Print results for this query
            self.print_comparison_results(results)
        
        return all_results

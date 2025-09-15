"""
Framework Performance Monitor
Comprehensive monitoring and comparison system for all agentic RAG frameworks
"""

import asyncio
import time
import json
import psutil
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class PerformanceMetrics:
    """Performance metrics for a framework"""
    framework: str
    response_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    confidence: float
    memory_types_used: List[str]
    reasoning_steps_count: int
    personalized: bool
    error_count: int
    success: bool
    timestamp: str

@dataclass
class FrameworkComparison:
    """Comparison results between frameworks"""
    query: str
    results: Dict[str, PerformanceMetrics]
    best_performance: str
    most_confident: str
    most_personalized: str
    fastest: str
    most_reliable: str

class FrameworkMonitor:
    """
    Comprehensive monitoring system for agentic RAG frameworks
    """
    
    def __init__(self, log_file: str = "framework_monitor.log"):
        self.log_file = Path(log_file)
        self.metrics_history: List[PerformanceMetrics] = []
        self.comparison_history: List[FrameworkComparison] = []
        
    async def measure_framework_performance(self, framework_name: str, 
                                         query_func, *args, **kwargs) -> PerformanceMetrics:
        """Measure performance of a framework execution"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        start_cpu = psutil.cpu_percent()
        
        error_count = 0
        success = True
        result = None
        
        try:
            result = await query_func(*args, **kwargs)
        except Exception as e:
            error_count += 1
            success = False
            print(f"Error in {framework_name}: {e}")
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        end_cpu = psutil.cpu_percent()
        
        # Extract metrics from result
        response_time = end_time - start_time
        memory_usage = end_memory - start_memory
        cpu_usage = end_cpu - start_cpu
        
        confidence = result.confidence if result and hasattr(result, 'confidence') else 0.0
        memory_types_used = result.memory_types_used if result and hasattr(result, 'memory_types_used') else []
        reasoning_steps_count = len(result.reasoning_steps) if result and hasattr(result, 'reasoning_steps') else 0
        personalized = result.personalized if result and hasattr(result, 'personalized') else False
        
        metrics = PerformanceMetrics(
            framework=framework_name,
            response_time=response_time,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            confidence=confidence,
            memory_types_used=memory_types_used,
            reasoning_steps_count=reasoning_steps_count,
            personalized=personalized,
            error_count=error_count,
            success=success,
            timestamp=datetime.now().isoformat()
        )
        
        self.metrics_history.append(metrics)
        await self._log_metrics(metrics)
        
        return metrics
    
    async def compare_frameworks(self, query: str, frameworks: Dict[str, Any], 
                               user_id: str, context_limit: int = 3) -> FrameworkComparison:
        """Compare multiple frameworks on the same query"""
        results = {}
        
        for framework_name, framework_instance in frameworks.items():
            print(f"🧪 Testing {framework_name}...")
            
            async def run_framework():
                return await framework_instance.process_query(
                    user_id=user_id,
                    query=query,
                    context_limit=context_limit,
                    use_hybrid=True
                )
            
            metrics = await self.measure_framework_performance(
                framework_name, run_framework
            )
            results[framework_name] = metrics
        
        # Determine best performers
        successful_results = {k: v for k, v in results.items() if v.success}
        
        if successful_results:
            best_performance = max(successful_results.items(), 
                                key=lambda x: x[1].confidence * (1.0 / max(x[1].response_time, 0.001)))[0]
            most_confident = max(successful_results.items(), 
                               key=lambda x: x[1].confidence)[0]
            most_personalized = max(successful_results.items(), 
                                  key=lambda x: len(x[1].memory_types_used))[0]
            fastest = min(successful_results.items(), 
                         key=lambda x: x[1].response_time)[0]
            most_reliable = max(successful_results.items(), 
                              key=lambda x: 1.0 / max(x[1].error_count + 1, 1))[0]
        else:
            best_performance = most_confident = most_personalized = fastest = most_reliable = "none"
        
        comparison = FrameworkComparison(
            query=query,
            results=results,
            best_performance=best_performance,
            most_confident=most_confident,
            most_personalized=most_personalized,
            fastest=fastest,
            most_reliable=most_reliable
        )
        
        self.comparison_history.append(comparison)
        await self._log_comparison(comparison)
        
        return comparison
    
    async def _log_metrics(self, metrics: PerformanceMetrics):
        """Log metrics to file"""
        log_entry = {
            "type": "metrics",
            "data": asdict(metrics)
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    async def _log_comparison(self, comparison: FrameworkComparison):
        """Log comparison to file"""
        log_entry = {
            "type": "comparison",
            "data": asdict(comparison)
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary across all frameworks"""
        if not self.metrics_history:
            return {"message": "No metrics available"}
        
        # Group by framework
        framework_metrics = {}
        for metrics in self.metrics_history:
            if metrics.framework not in framework_metrics:
                framework_metrics[metrics.framework] = []
            framework_metrics[metrics.framework].append(metrics)
        
        summary = {}
        for framework, metrics_list in framework_metrics.items():
            successful_metrics = [m for m in metrics_list if m.success]
            
            if successful_metrics:
                summary[framework] = {
                    "total_tests": len(metrics_list),
                    "successful_tests": len(successful_metrics),
                    "success_rate": len(successful_metrics) / len(metrics_list),
                    "avg_response_time": sum(m.response_time for m in successful_metrics) / len(successful_metrics),
                    "avg_confidence": sum(m.confidence for m in successful_metrics) / len(successful_metrics),
                    "avg_memory_usage": sum(m.memory_usage_mb for m in successful_metrics) / len(successful_metrics),
                    "avg_cpu_usage": sum(m.cpu_usage_percent for m in successful_metrics) / len(successful_metrics),
                    "avg_reasoning_steps": sum(m.reasoning_steps_count for m in successful_metrics) / len(successful_metrics),
                    "personalization_rate": sum(1 for m in successful_metrics if m.personalized) / len(successful_metrics)
                }
            else:
                summary[framework] = {
                    "total_tests": len(metrics_list),
                    "successful_tests": 0,
                    "success_rate": 0.0,
                    "error": "No successful tests"
                }
        
        return summary
    
    def print_performance_report(self):
        """Print a comprehensive performance report"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE FRAMEWORK PERFORMANCE REPORT")
        print("="*80)
        
        summary = self.get_performance_summary()
        
        for framework, stats in summary.items():
            print(f"\n🔧 {framework.upper()}")
            print("-" * 50)
            
            if "error" in stats:
                print(f"❌ {stats['error']}")
                continue
            
            print(f"📈 Success Rate: {stats['success_rate']:.1%}")
            print(f"⏱️  Avg Response Time: {stats['avg_response_time']:.2f}s")
            print(f"🎯 Avg Confidence: {stats['avg_confidence']:.2f}")
            print(f"🧠 Avg Memory Usage: {stats['avg_memory_usage']:.1f}MB")
            print(f"💻 Avg CPU Usage: {stats['avg_cpu_usage']:.1f}%")
            print(f"🔍 Avg Reasoning Steps: {stats['avg_reasoning_steps']:.1f}")
            print(f"🎨 Personalization Rate: {stats['personalization_rate']:.1%}")
            print(f"📊 Total Tests: {stats['total_tests']}")
        
        # Overall recommendations
        print(f"\n🏆 RECOMMENDATIONS")
        print("-" * 30)
        
        if summary:
            best_success = max(summary.items(), key=lambda x: x[1].get('success_rate', 0))
            fastest = min(summary.items(), key=lambda x: x[1].get('avg_response_time', float('inf')))
            most_confident = max(summary.items(), key=lambda x: x[1].get('avg_confidence', 0))
            
            print(f"✅ Most Reliable: {best_success[0]} ({best_success[1]['success_rate']:.1%} success rate)")
            print(f"🚀 Fastest: {fastest[0]} ({fastest[1]['avg_response_time']:.2f}s avg)")
            print(f"🎯 Most Confident: {most_confident[0]} ({most_confident[1]['avg_confidence']:.2f} avg confidence)")
        
        print("\n" + "="*80)
    
    async def run_comprehensive_test(self, frameworks: Dict[str, Any], 
                                   user_id: str, test_queries: List[str]) -> Dict[str, Any]:
        """Run comprehensive tests across all frameworks"""
        print("🚀 Running Comprehensive Framework Tests")
        print("=" * 60)
        
        all_results = {}
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🧪 Test Query {i}/{len(test_queries)}: {query}")
            print("-" * 60)
            
            comparison = await self.compare_frameworks(query, frameworks, user_id)
            all_results[f"query_{i}"] = {
                "query": query,
                "results": comparison
            }
            
            # Print results for this query
            self._print_query_results(comparison)
        
        # Print overall summary
        self.print_performance_report()
        
        return all_results
    
    def _print_query_results(self, comparison: FrameworkComparison):
        """Print results for a single query"""
        print(f"\n📊 Results for: {comparison.query[:50]}...")
        print("-" * 40)
        
        for framework, metrics in comparison.results.items():
            status = "✅" if metrics.success else "❌"
            print(f"{status} {framework}: {metrics.response_time:.2f}s, "
                  f"confidence: {metrics.confidence:.2f}, "
                  f"memory: {len(metrics.memory_types_used)} types")
        
        print(f"\n🏆 Best: {comparison.best_performance} | "
              f"Fastest: {comparison.fastest} | "
              f"Most Confident: {comparison.most_confident}")

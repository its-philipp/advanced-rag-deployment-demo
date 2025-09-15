#!/usr/bin/env python3
"""
Test script for the RAG demo with monitoring.
"""
import requests
import time
import json

def test_api_endpoints():
    """Test all API endpoints and generate metrics."""
    base_url = "http://localhost:8080"
    
    print("🚀 Testing RAG Demo API with Monitoring...")
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   ✅ Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return
    
    # Test metrics endpoint
    print("\n2. Testing metrics endpoint...")
    try:
        response = requests.get(f"{base_url}/metrics")
        print(f"   ✅ Metrics endpoint: {response.status_code}")
        print(f"   📊 Metrics preview: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Metrics endpoint failed: {e}")
        return
    
    # Index sample documents
    print("\n3. Indexing sample documents...")
    try:
        response = requests.post(f"{base_url}/api/v1/index-sample-docs")
        print(f"   ✅ Document indexing: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"   ❌ Document indexing failed: {e}")
        return
    
    # Test RAG queries
    print("\n4. Testing RAG queries...")
    test_queries = [
        "Wie verbessere ich meine Lernroutine?",
        "Was sind effektive Gedächtnistechniken?",
        "Wie kann ich mein Zeitmanagement verbessern?",
        "Welche Lernstrategien gibt es für Mathematik?",
        "Wie funktioniert Spaced Repetition?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"   Query {i}: {query}")
        try:
            response = requests.post(
                f"{base_url}/api/v1/coach",
                json={
                    "user_id": f"test_user_{i}",
                    "query": query,
                    "context_limit": 3
                }
            )
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Response: {data['answer'][:100]}...")
                print(f"   📊 Confidence: {data['confidence']:.2f}, Sources: {len(data['sources'])}")
            else:
                print(f"   ❌ Query failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Query error: {e}")
        
        # Small delay between queries
        time.sleep(1)
    
    print("\n5. Testing metrics after queries...")
    try:
        response = requests.get(f"{base_url}/metrics")
        print(f"   ✅ Final metrics: {response.status_code}")
        
        # Count some key metrics
        metrics_text = response.text
        rag_queries = metrics_text.count('rag_queries_total')
        http_requests = metrics_text.count('http_requests_total')
        documents_indexed = metrics_text.count('documents_indexed_total')
        
        print(f"   📊 RAG queries tracked: {rag_queries}")
        print(f"   📊 HTTP requests tracked: {http_requests}")
        print(f"   📊 Documents indexed tracked: {documents_indexed}")
        
    except Exception as e:
        print(f"   ❌ Final metrics failed: {e}")
    
    print("\n🎉 Testing completed!")
    print("\n📊 Monitoring URLs:")
    print(f"   • Prometheus: http://localhost:9090")
    print(f"   • Grafana: http://localhost:3000 (admin/admin)")
    print(f"   • API Docs: http://localhost:8080/docs")
    print(f"   • Metrics: http://localhost:8080/metrics")

if __name__ == "__main__":
    test_api_endpoints()

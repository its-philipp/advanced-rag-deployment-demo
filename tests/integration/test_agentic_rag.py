#!/usr/bin/env python3
"""
Test script for Agentic RAG system
Tests episodic, semantic, and procedural memory functionality
"""

import asyncio
import json
import requests
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8080"
AGENTIC_BASE_URL = f"{BASE_URL}/api/agentic"

def test_agentic_rag_system():
    """Test the complete agentic RAG system"""
    print("🧠 Testing Agentic RAG System")
    print("=" * 50)
    
    # Test 1: Initialize a user
    print("\n1. Initializing user...")
    user_id = "test_user_agentic"
    response = requests.post(f"{AGENTIC_BASE_URL}/initialize-user/{user_id}")
    if response.status_code == 200:
        print("✅ User initialized successfully")
    else:
        print(f"❌ Failed to initialize user: {response.text}")
        return
    
    # Test 2: Store semantic memory
    print("\n2. Storing semantic memory...")
    semantic_data = {
        "concept": "python_programming",
        "knowledge": {
            "description": "Python is a high-level programming language",
            "key_features": ["Simple syntax", "Large standard library", "Cross-platform"],
            "use_cases": ["Web development", "Data science", "AI/ML"]
        },
        "relationships": ["programming", "software_development"],
        "confidence": 0.9
    }
    
    response = requests.post(
        f"{AGENTIC_BASE_URL}/store-semantic-memory",
        json=semantic_data
    )
    
    if response.status_code == 200:
        print("✅ Semantic memory stored successfully")
    else:
        print(f"❌ Failed to store semantic memory: {response.text}")
    
    # Test 3: Store procedural memory
    print("\n3. Storing procedural memory...")
    procedural_data = {
        "skill": "debugging_python",
        "steps": [
            {"step": 1, "action": "Read error message", "description": "Carefully read the error message"},
            {"step": 2, "action": "Check syntax", "description": "Look for syntax errors in the code"},
            {"step": 3, "action": "Add print statements", "description": "Add debug prints to trace execution"},
            {"step": 4, "action": "Use debugger", "description": "Step through code with pdb or IDE debugger"},
            {"step": 5, "action": "Test fix", "description": "Test the fix with various inputs"}
        ],
        "prerequisites": ["basic_python", "problem_solving"],
        "success_criteria": ["error_resolved", "code_works_correctly"]
    }
    
    response = requests.post(
        f"{AGENTIC_BASE_URL}/store-procedural-memory",
        json=procedural_data
    )
    
    if response.status_code == 200:
        print("✅ Procedural memory stored successfully")
    else:
        print(f"❌ Failed to store procedural memory: {response.text}")
    
    # Test 4: Test agentic query
    print("\n4. Testing agentic query...")
    query_data = {
        "user_id": user_id,
        "query": "I'm having trouble debugging my Python code. Can you help me?",
        "context_limit": 3,
        "use_hybrid": True
    }
    
    response = requests.post(
        f"{AGENTIC_BASE_URL}/agentic-query",
        json=query_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Agentic query processed successfully")
        print(f"   Answer: {result['answer'][:200]}...")
        print(f"   Memory types used: {result['memory_types_used']}")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Personalized: {result['personalized']}")
        print(f"   Reasoning steps: {len(result['reasoning_steps'])}")
    else:
        print(f"❌ Failed to process agentic query: {response.text}")
    
    # Test 5: Test follow-up query (episodic memory)
    print("\n5. Testing follow-up query (episodic memory)...")
    followup_data = {
        "user_id": user_id,
        "query": "What was the first step you mentioned for debugging?",
        "context_limit": 3,
        "use_hybrid": True
    }
    
    response = requests.post(
        f"{AGENTIC_BASE_URL}/agentic-query",
        json=followup_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Follow-up query processed successfully")
        print(f"   Answer: {result['answer'][:200]}...")
        print(f"   Memory types used: {result['memory_types_used']}")
        print(f"   Personalized: {result['personalized']}")
    else:
        print(f"❌ Failed to process follow-up query: {response.text}")
    
    # Test 6: Get memory statistics
    print("\n6. Getting memory statistics...")
    response = requests.get(f"{AGENTIC_BASE_URL}/memory-stats")
    
    if response.status_code == 200:
        stats = response.json()
        print("✅ Memory statistics retrieved")
        print(f"   Episodic memories: {stats['episodic']['total_memories']} across {stats['episodic']['total_users']} users")
        print(f"   Semantic memories: {stats['semantic']['total_concepts']} concepts")
        print(f"   Procedural memories: {stats['procedural']['total_skills']} skills")
    else:
        print(f"❌ Failed to get memory statistics: {response.text}")
    
    # Test 7: Test different types of queries
    print("\n7. Testing different query types...")
    
    test_queries = [
        {
            "query": "How do I learn Python effectively?",
            "description": "Learning methodology query"
        },
        {
            "query": "What are the best practices for code organization?",
            "description": "Best practices query"
        },
        {
            "query": "I want to improve my problem-solving skills",
            "description": "Skill development query"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n   Test {i}: {test_case['description']}")
        query_data = {
            "user_id": user_id,
            "query": test_case["query"],
            "context_limit": 3,
            "use_hybrid": True
        }
        
        response = requests.post(
            f"{AGENTIC_BASE_URL}/agentic-query",
            json=query_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Query processed - Memory types: {result['memory_types_used']}")
        else:
            print(f"   ❌ Query failed: {response.text}")
    
    print("\n" + "=" * 50)
    print("🎉 Agentic RAG testing completed!")

def test_memory_retrieval():
    """Test memory retrieval endpoints"""
    print("\n🔍 Testing Memory Retrieval")
    print("=" * 30)
    
    # Test episodic memory retrieval
    print("\n1. Testing episodic memory retrieval...")
    response = requests.get(f"{AGENTIC_BASE_URL}/episodic-memories/test_user_agentic")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Retrieved {result['count']} episodic memories")
    else:
        print(f"❌ Failed to retrieve episodic memories: {response.text}")
    
    # Test semantic memory retrieval
    print("\n2. Testing semantic memory retrieval...")
    response = requests.get(f"{AGENTIC_BASE_URL}/semantic-memories")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Retrieved {result['count']} semantic memories")
    else:
        print(f"❌ Failed to retrieve semantic memories: {response.text}")
    
    # Test procedural memory retrieval
    print("\n3. Testing procedural memory retrieval...")
    response = requests.get(f"{AGENTIC_BASE_URL}/procedural-memories")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Retrieved {result['count']} procedural memories")
    else:
        print(f"❌ Failed to retrieve procedural memories: {response.text}")

if __name__ == "__main__":
    print("🚀 Starting Agentic RAG System Tests")
    print("Make sure the server is running on http://localhost:8080")
    print("Press Enter to continue...")
    input()
    
    try:
        # Test if server is running
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Server is not running. Please start the server first.")
            exit(1)
        
        # Run tests
        test_agentic_rag_system()
        test_memory_retrieval()
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please make sure it's running on http://localhost:8080")
    except Exception as e:
        print(f"❌ Error during testing: {e}")

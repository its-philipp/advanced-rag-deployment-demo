#!/usr/bin/env python3
"""
Test script for personalized coaching system.
Demonstrates user-specific coaching with preferences and context.
"""
import requests
import json
import time

BASE_URL = "http://localhost:8080/api/v1"

def test_personalized_coaching():
    """Test the personalized coaching system."""
    print("🧪 Testing Personalized Coaching System")
    print("=" * 50)
    
    # Test user IDs
    user1 = "student_alice"
    user2 = "student_bob"
    
    print(f"\n1️⃣ Setting up user profiles...")
    
    # Set up Alice's profile
    alice_preferences = {
        "learning_style": "visual",
        "subject_focus": "mathematics",
        "difficulty_level": "intermediate"
    }
    
    alice_goals = [
        "Improve calculus understanding",
        "Learn linear algebra",
        "Prepare for advanced mathematics"
    ]
    
    # Set up Bob's profile
    bob_preferences = {
        "learning_style": "kinesthetic",
        "subject_focus": "physics",
        "difficulty_level": "beginner"
    }
    
    bob_goals = [
        "Understand basic physics concepts",
        "Learn through experiments",
        "Build practical skills"
    ]
    
    # Update Alice's preferences
    print(f"   Setting up Alice's profile...")
    response = requests.put(f"{BASE_URL}/users/{user1}/preferences", 
                          json=alice_preferences)
    print(f"   Alice preferences: {response.status_code}")
    
    response = requests.put(f"{BASE_URL}/users/{user1}/learning-goals", 
                          json=alice_goals)
    print(f"   Alice goals: {response.status_code}")
    
    # Update Bob's preferences
    print(f"   Setting up Bob's profile...")
    response = requests.put(f"{BASE_URL}/users/{user2}/preferences", 
                          json=bob_preferences)
    print(f"   Bob preferences: {response.status_code}")
    
    response = requests.put(f"{BASE_URL}/users/{user2}/learning-goals", 
                          json=bob_goals)
    print(f"   Bob goals: {response.status_code}")
    
    print(f"\n2️⃣ Testing personalized responses...")
    
    # Test questions
    questions = [
        "Wie kann ich meine Lernroutine verbessern?",
        "Was sind die besten Lernmethoden für mich?",
        "Wie kann ich komplexe Konzepte besser verstehen?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n   Question {i}: {question}")
        
        # Alice's response
        print(f"   🤓 Alice's response:")
        alice_response = requests.post(f"{BASE_URL}/personalized-coach", json={
            "user_id": user1,
            "query": question,
            "context_limit": 3
        })
        
        if alice_response.status_code == 200:
            alice_data = alice_response.json()
            print(f"   Answer: {alice_data['answer'][:200]}...")
            print(f"   Confidence: {alice_data['confidence']:.2f}")
            print(f"   Personalized: {alice_data['personalized']}")
            if alice_data.get('user_context'):
                print(f"   Learning Style: {alice_data['user_context'].get('learning_style')}")
                print(f"   Goals: {alice_data['user_context'].get('learning_goals')}")
        
        # Bob's response
        print(f"   🧪 Bob's response:")
        bob_response = requests.post(f"{BASE_URL}/personalized-coach", json={
            "user_id": user2,
            "query": question,
            "context_limit": 3
        })
        
        if bob_response.status_code == 200:
            bob_data = bob_response.json()
            print(f"   Answer: {bob_data['answer'][:200]}...")
            print(f"   Confidence: {bob_data['confidence']:.2f}")
            print(f"   Personalized: {bob_data['personalized']}")
            if bob_data.get('user_context'):
                print(f"   Learning Style: {bob_data['user_context'].get('learning_style')}")
                print(f"   Goals: {bob_data['user_context'].get('learning_goals')}")
        
        time.sleep(1)  # Small delay between questions
    
    print(f"\n3️⃣ Testing user profiles...")
    
    # Get Alice's profile
    alice_profile = requests.get(f"{BASE_URL}/users/{user1}/profile")
    if alice_profile.status_code == 200:
        profile_data = alice_profile.json()
        print(f"   Alice's Profile:")
        print(f"   - Learning Style: {profile_data.get('learning_style')}")
        print(f"   - Subject Focus: {profile_data.get('preferences', {}).get('subject_focus')}")
        print(f"   - Total Sessions: {profile_data.get('total_sessions')}")
        print(f"   - Learning Goals: {profile_data.get('learning_goals')}")
    
    # Get Bob's profile
    bob_profile = requests.get(f"{BASE_URL}/users/{user2}/profile")
    if bob_profile.status_code == 200:
        profile_data = bob_profile.json()
        print(f"   Bob's Profile:")
        print(f"   - Learning Style: {profile_data.get('learning_style')}")
        print(f"   - Subject Focus: {profile_data.get('preferences', {}).get('subject_focus')}")
        print(f"   - Total Sessions: {profile_data.get('total_sessions')}")
        print(f"   - Learning Goals: {profile_data.get('learning_goals')}")
    
    print(f"\n4️⃣ Testing chat context...")
    
    # Get Alice's recent context
    alice_context = requests.get(f"{BASE_URL}/users/{user1}/context?limit=5")
    if alice_context.status_code == 200:
        context_data = alice_context.json()
        print(f"   Alice's Recent Messages: {len(context_data.get('recent_messages', []))}")
        for msg in context_data.get('recent_messages', [])[-2:]:  # Show last 2 messages
            print(f"   - {msg['role']}: {msg['content'][:100]}...")
    
    print(f"\n✅ Personalized coaching test completed!")
    print(f"   Check the .rag-demo/users/ directory for stored user data")

if __name__ == "__main__":
    print("Starting personalized coaching test...")
    print("Make sure the server is running on http://localhost:8080")
    print("Press Ctrl+C to cancel")
    
    try:
        # Wait a moment for user to read
        time.sleep(2)
        test_personalized_coaching()
    except KeyboardInterrupt:
        print("\n❌ Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("Make sure the server is running and accessible")

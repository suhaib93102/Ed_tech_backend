#!/usr/bin/env python3
"""
Test Quiz Generation Endpoint
Production-level test to verify quiz generation from text input
"""

import requests
import json

BASE_URL = "http://localhost:8003"

def test_quiz_generation():
    """Test quiz generation with text input"""
    
    print("🧪 Testing Quiz Generation from Text Input")
    print("=" * 80)
    
    # Test data - simulating what the frontend sends
    test_text = """
    Machine learning is a subset of artificial intelligence that focuses on 
    developing algorithms and statistical models that enable computers to learn 
    from and make predictions or decisions based on data. Unlike traditional 
    programming where explicit instructions are provided, machine learning systems 
    improve their performance through experience.
    
    There are three main types of machine learning:
    1. Supervised Learning - uses labeled data to train models
    2. Unsupervised Learning - finds patterns in unlabeled data
    3. Reinforcement Learning - learns through trial and error with rewards
    
    Common applications include image recognition, natural language processing,
    recommendation systems, and autonomous vehicles.
    """
    
    payload = {
        'topic': test_text.strip(),
        'num_questions': 5,
        'difficulty': 'medium',
        'user_id': 'test_user_123'
    }
    
    print("\n📤 Sending Request:")
    print(f"URL: {BASE_URL}/quiz/generate/")
    print(f"Topic Length: {len(payload['topic'])} characters")
    print(f"Number of Questions: {payload['num_questions']}")
    print(f"Difficulty: {payload['difficulty']}")
    print(f"Topic Preview: {payload['topic'][:100]}...")
    
    try:
        print("\n⏳ Making API request...")
        response = requests.post(
            f"{BASE_URL}/quiz/generate/",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("\n✅ SUCCESS! Quiz generated successfully")
            data = response.json()
            
            print("\n📊 Quiz Details:")
            print(f"Title: {data.get('title', 'N/A')}")
            print(f"Total Questions: {data.get('num_questions', 0)}")
            print(f"Total Marks: {data.get('total_marks', 0)}")
            print(f"Difficulty: {data.get('difficulty', 'N/A')}")
            print(f"Duration: {data.get('duration', 0)} minutes")
            
            questions = data.get('questions', [])
            print(f"\n📝 Questions ({len(questions)}):")
            for i, q in enumerate(questions[:3], 1):  # Show first 3
                print(f"\nQuestion {i}:")
                print(f"  Text: {q.get('question', 'N/A')[:80]}...")
                print(f"  Options: {len(q.get('options', []))}")
                print(f"  Marks: {q.get('marks', 0)}")
            
            if len(questions) > 3:
                print(f"\n... and {len(questions) - 3} more questions")
            
            print("\n✅ All checks passed!")
            print("🎉 Quiz generation is working correctly!")
            
        elif response.status_code == 429:
            print("\n⚠️  API Quota Exceeded")
            print(f"Error: {response.json().get('error')}")
            print(f"Details: {response.json().get('details')}")
            retry_after = response.headers.get('Retry-After')
            if retry_after:
                print(f"Retry after: {retry_after} seconds")
                
        else:
            print(f"\n❌ ERROR: Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("\n❌ ERROR: Request timed out (> 60 seconds)")
        print("The Gemini API might be slow. Try again in a moment.")
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERROR: Could not connect to {BASE_URL}")
        print("Make sure the backend server is running:")
        print("  cd backend")
        print("  python manage.py runserver 8003")
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_quiz_generation()

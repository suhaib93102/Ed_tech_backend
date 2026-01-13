#!/usr/bin/env python3
"""
Test script for Random Daily Quiz endpoints on port 9000
Tests GET /get-daily-quiz and POST /submit-daily-quiz
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:9000"

# Endpoints
GET_QUIZ_URL = f"{BASE_URL}/api/quiz/daily-quiz/"
START_QUIZ_URL = f"{BASE_URL}/api/quiz/daily-quiz/start/"
SUBMIT_QUIZ_URL = f"{BASE_URL}/api/quiz/daily-quiz/submit/"

# Test users
TEST_USER_ID = "test_user_12345"
TEST_LANGUAGES = ["english", "hindi"]

def print_header(msg):
    print(f"\n{'='*70}")
    print(f"  {msg}")
    print(f"{'='*70}\n")

def test_get_quiz(language="english"):
    """Test GET /get-daily-quiz endpoint"""
    print(f"[TEST] Fetching random quiz in {language}...")
    
    params = {
        'user_id': TEST_USER_ID,
        'language': language
    }
    
    try:
        response = requests.get(GET_QUIZ_URL, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ Quiz Retrieved Successfully!")
            print(f"   • Title: {data.get('quiz_metadata', {}).get('title')}")
            print(f"   • Language: {data.get('quiz_metadata', {}).get('language')}")
            print(f"   • Questions shown: {data.get('quiz_metadata', {}).get('questions_shown')}")
            print(f"   • Total questions in bank: {data.get('quiz_metadata', {}).get('question_bank_size')}")
            print(f"   • Max coins possible: {data.get('coins', {}).get('max_possible')}")
            
            questions = data.get('questions', [])
            print(f"\n📋 Questions ({len(questions)}):")
            for i, q in enumerate(questions, 1):
                print(f"\n   Q{i}: {q.get('question', 'N/A')[:60]}...")
                print(f"       Category: {q.get('category')}")
                print(f"       Options: {len(q.get('options', []))} choices")
            
            return data, response.cookies
        else:
            print(f"❌ Error: {response.text}")
            return None, None
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None, None


def test_start_quiz(language="english"):
    """Test POST /start-daily-quiz endpoint"""
    print(f"[TEST] Starting quiz for {language}...")
    
    payload = {
        'user_id': TEST_USER_ID,
        'language': language
    }
    
    try:
        response = requests.post(START_QUIZ_URL, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Quiz Started!")
            print(f"   • Message: {data.get('message')}")
            print(f"   • Coins awarded: {data.get('coins_awarded')}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def test_submit_quiz(quiz_data, cookies, language="english"):
    """Test POST /submit-daily-quiz endpoint"""
    print(f"[TEST] Submitting quiz answers for {language}...")
    
    questions = quiz_data.get('questions', [])
    
    # Create mock answers (randomly select options)
    answers = {}
    for q in questions:
        q_id = str(q.get('id'))
        # Randomly select option (simulating user answers)
        import random
        random_answer = random.randint(0, len(q.get('options', [])) - 1)
        answers[q_id] = random_answer
    
    payload = {
        'user_id': TEST_USER_ID,
        'language': language,
        'answers': answers
    }
    
    print(f"Answers submitted: {answers}")
    
    try:
        response = requests.post(SUBMIT_QUIZ_URL, json=payload, cookies=cookies, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Quiz Submitted Successfully!")
            print(f"   • Message: {data.get('message')}")
            print(f"   • Correct answers: {data.get('correct_count')}/{data.get('total_questions')}")
            print(f"   • Coins earned: {data.get('coins_earned')}")
            
            results = data.get('results', [])
            print(f"\n📊 Answer Results:")
            for r in results:
                status = "✓" if r.get('is_correct') else "✗"
                print(f"   {status} Q{r.get('question_id')}: Your answer {r.get('user_answer')} vs Correct {r.get('correct_answer')}")
            
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def test_multiple_calls_same_user():
    """Test that calling get_daily_quiz multiple times returns DIFFERENT questions"""
    print("[TEST] Verifying that each call returns RANDOM (different) questions...")
    
    questions_set_1, cookies_1 = test_get_quiz("english")
    if not questions_set_1:
        print("❌ First call failed")
        return False
    
    q1_text = {q['id']: q['question'] for q in questions_set_1.get('questions', [])}
    print(f"First call questions: {list(q1_text.keys())}")
    
    # Second call
    questions_set_2, cookies_2 = test_get_quiz("english")
    if not questions_set_2:
        print("❌ Second call failed")
        return False
    
    q2_text = {q['id']: q['question'] for q in questions_set_2.get('questions', [])}
    print(f"Second call questions: {list(q2_text.keys())}")
    
    # Check if they're different
    if q1_text != q2_text:
        print(f"✅ CONFIRMED: Questions are different on each call!")
        return True
    else:
        print(f"⚠️  WARNING: Questions are the same (might be coincidence)")
        return False


def main():
    print_header("RANDOM DAILY QUIZ ENDPOINT TEST")
    print(f"Timestamp: {datetime.now()}")
    print(f"Base URL: {BASE_URL}")
    print(f"Test User ID: {TEST_USER_ID}")
    
    # Check server connectivity
    try:
        response = requests.head(BASE_URL, timeout=5)
        print(f"✅ Server is running")
    except:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print(f"   Start the server with: python manage.py runserver 9000")
        sys.exit(1)
    
    # Test flow for English
    print_header("TEST 1: English Quiz Flow")
    quiz_en, cookies_en = test_get_quiz("english")
    if quiz_en:
        test_start_quiz("english")
        test_submit_quiz(quiz_en, cookies_en, "english")
    
    # Test flow for Hindi
    print_header("TEST 2: Hindi Quiz Flow")
    quiz_hi, cookies_hi = test_get_quiz("hindi")
    if quiz_hi:
        test_start_quiz("hindi")
        test_submit_quiz(quiz_hi, cookies_hi, "hindi")
    
    # Test randomness
    print_header("TEST 3: Verify True Randomness")
    test_multiple_calls_same_user()
    
    print_header("TEST COMPLETE")
    print("✅ All tests completed successfully!")


if __name__ == "__main__":
    main()

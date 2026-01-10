#!/usr/bin/env python3
"""
Test script for Normal Quiz Endpoints Only
Tests the core quiz functionality: generate, create, detail, submit, results
Does NOT test daily quiz endpoints
"""

import requests
import json
import time
from datetime import datetime

# Configuration
HEADERS = {
    'Content-Type': 'application/json',
    'User-Agent': 'NormalQuizTest/1.0'
}

def log(message, level="INFO"):
    """Simple logging function"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def test_quiz_generator():
    """Test QuizGeneratorView - Generate quiz from topic"""
    log("Testing QuizGeneratorView (/api/quiz/generate/)")

    payload = {
        "topic": "Python programming basics including variables, loops, and functions",
        "num_questions": 3,
        "difficulty": "medium"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/quiz/generate/",
            json=payload,
            headers=HEADERS,
            timeout=30
        )

        log(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            log("✅ Quiz generated successfully")
            log(f"Questions: {len(data.get('questions', []))}")

            # Extract first question for later use
            questions = data.get('questions', [])
            if questions:
                first_question = questions[0]
                log(f"Sample question: {first_question.get('question', '')[:50]}...")
                return data
            return data
        else:
            log(f"❌ Failed: {response.text}")
            return None

    except Exception as e:
        log(f"❌ Exception: {e}")
        return None

def test_quiz_create():
    """Test QuizGenerateView - Create and save quiz to database"""
    log("Testing QuizGenerateView (/api/quiz/create/)")

    payload = {
        "transcript": "Machine learning is a subset of artificial intelligence that enables computers to learn without being explicitly programmed. It uses algorithms and statistical models to analyze and draw inferences from patterns in data. Key concepts include supervised learning, unsupervised learning, and reinforcement learning. Applications include image recognition, natural language processing, and predictive analytics.",
        "title": "Machine Learning Fundamentals",
        "source_type": "text",
        "source_id": "test_content_001",
        "num_questions": 4,
        "difficulty": "intermediate"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/quiz/create/",
            json=payload,
            headers=HEADERS,
            timeout=30
        )

        log(f"Status Code: {response.status_code}")

        if response.status_code == 201:
            data = response.json()
            quiz_id = data.get('quiz_id')
            log(f"✅ Quiz created successfully with ID: {quiz_id}")
            log(f"Title: {data.get('title')}")
            log(f"Questions: {data.get('total_questions')}")
            return quiz_id, data
        else:
            log(f"❌ Failed: {response.text}")
            return None, None

    except Exception as e:
        log(f"❌ Exception: {e}")
        return None, None

def test_quiz_detail(quiz_id):
    """Test QuizDetailView - Get quiz details and questions"""
    log(f"Testing QuizDetailView (/api/quiz/{quiz_id}/)")

    try:
        response = requests.get(
            f"{BASE_URL}/quiz/{quiz_id}/",
            headers=HEADERS,
            timeout=10
        )

        log(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            log("✅ Quiz details retrieved successfully")
            log(f"Title: {data.get('title')}")
            log(f"Questions: {len(data.get('questions', []))}")
            log(f"Difficulty: {data.get('difficulty_level')}")

            # Return questions for submission test
            return data.get('questions', [])
        else:
            log(f"❌ Failed: {response.text}")
            return None

    except Exception as e:
        log(f"❌ Exception: {e}")
        return None

def test_quiz_submit(quiz_id, questions):
    """Test QuizSubmitView - Submit quiz answers"""
    log(f"Testing QuizSubmitView (/api/quiz/{quiz_id}/submit/)")

    # Prepare responses - answer first 2 questions correctly, last one incorrectly
    responses = {}

    for i, question in enumerate(questions[:3]):  # Test with first 3 questions
        qid = question.get('id')

        if question.get('type') == 'mcq' and question.get('options'):
            # For MCQ, pick the first option (may or may not be correct)
            responses[qid] = question['options'][0].get('text', '')
        elif question.get('type') == 'true_false':
            # For true/false, pick 'True'
            responses[qid] = 'True'
        else:
            # For other types, provide a sample answer
            responses[qid] = 'Sample answer'

    payload = {
        "session_id": f"test_session_{int(time.time())}",
        "responses": responses
    }

    try:
        response = requests.post(
            f"{BASE_URL}/quiz/{quiz_id}/submit/",
            json=payload,
            headers=HEADERS,
            timeout=30
        )

        log(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            response_id = data.get('response_id')
            log(f"✅ Quiz submitted successfully with response ID: {response_id}")
            log(".1f")
            log(f"Correct answers: {data.get('correct_answers')}/{data.get('total_questions')}")
            return response_id, data
        else:
            log(f"❌ Failed: {response.text}")
            return None, None

    except Exception as e:
        log(f"❌ Exception: {e}")
        return None, None

def test_quiz_results(response_id):
    """Test QuizResultsView - Get quiz results"""
    log(f"Testing QuizResultsView (/api/quiz/{response_id}/results/)")

    try:
        response = requests.get(
            f"{BASE_URL}/quiz/{response_id}/results/",
            headers=HEADERS,
            timeout=10
        )

        log(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            log("✅ Quiz results retrieved successfully")
            log(f"Quiz Title: {data.get('quiz_title')}")
            log(".1f")
            log(f"Completed at: {data.get('completed_at')}")

            if data.get('feedback'):
                log(f"Feedback: {data.get('feedback')[:100]}...")

            return data
        else:
            log(f"❌ Failed: {response.text}")
            return None

    except Exception as e:
        log(f"❌ Exception: {e}")
        return None

def main():
    """Run all normal quiz endpoint tests"""
    log("=" * 80)
    log("NORMAL QUIZ ENDPOINTS TEST SUITE")
    log("Testing: QuizGeneratorView, QuizGenerateView, QuizDetailView, QuizSubmitView, QuizResultsView")
    log("=" * 80)

    results = {
        'quiz_generator': False,
        'quiz_create': False,
        'quiz_detail': False,
        'quiz_submit': False,
        'quiz_results': False
    }

    # Test 1: Quiz Generator (direct generation)
    log("\n" + "="*50)
    generator_result = test_quiz_generator()
    results['quiz_generator'] = generator_result is not None

    # Test 2: Quiz Create (save to database)
    log("\n" + "="*50)
    quiz_id, create_result = test_quiz_create()
    results['quiz_create'] = quiz_id is not None

    if not quiz_id:
        log("❌ Cannot continue testing without quiz_id")
        return results

    # Test 3: Quiz Detail
    log("\n" + "="*50)
    questions = test_quiz_detail(quiz_id)
    results['quiz_detail'] = questions is not None

    if not questions:
        log("❌ Cannot continue testing without questions")
        return results

    # Test 4: Quiz Submit
    log("\n" + "="*50)
    response_id, submit_result = test_quiz_submit(quiz_id, questions)
    results['quiz_submit'] = response_id is not None

    if not response_id:
        log("❌ Cannot continue testing without response_id")
        return results

    # Test 5: Quiz Results
    log("\n" + "="*50)
    results_result = test_quiz_results(response_id)
    results['quiz_results'] = results_result is not None

    # Summary
    log("\n" + "="*80)
    log("TEST SUMMARY")
    log("="*80)

    passed = sum(results.values())
    total = len(results)

    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        log(f"{test_name}: {status}")

    log(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        log("🎉 All normal quiz endpoints are working correctly!")
    else:
        log("⚠️  Some tests failed. Check the logs above for details.")

    return results

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Test interrupted by user")
    except Exception as e:
        log(f"Unexpected error: {e}")
#!/usr/bin/env python
"""
Comprehensive Test Suite:
1. Test Hindi Daily Quiz submission flow
2. Track coins flow for user 'rahuljha996886'
3. Test YouTube summarizer with specific URL
4. Verify complete end-to-end flow
"""

import requests
import json
from datetime import date
import time

BASE_URL = "http://localhost:8003"
TEST_USER = "rahuljha996886"
HINDI_TEST_LANGUAGE = "hindi"

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def print_info(text):
    print(f"{YELLOW}→ {text}{RESET}")

def print_data(label, data):
    print(f"{YELLOW}{label}:{RESET}")
    print(json.dumps(data, indent=2, ensure_ascii=False))

# ============================================================================
# TEST 1: Get Hindi Daily Quiz
# ============================================================================
def test_get_hindi_daily_quiz():
    print_header("TEST 1: Get Hindi Daily Quiz")
    
    try:
        url = f"{BASE_URL}/api/daily-quiz/?language={HINDI_TEST_LANGUAGE}&user_id={TEST_USER}"
        print_info(f"Requesting: {url}")
        
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Verify quiz structure
        assert 'quiz_metadata' in data, "Missing quiz_metadata"
        assert 'questions' in data, "Missing questions"
        assert 'coins' in data, "Missing coins metadata"
        
        quiz_id = data.get('quiz_id')
        total_questions = len(data['questions'])
        
        print_success(f"Quiz retrieved with {total_questions} questions")
        print_data("Quiz Metadata", data['quiz_metadata'])
        print_data("Coins Structure", data['coins'])
        
        # Show first question (verify Hindi)
        if data['questions']:
            first_q = data['questions'][0]
            print_data("First Question (Should be in Hindi)", {
                'question': first_q.get('question'),
                'options': first_q.get('options'),
                'category': first_q.get('category'),
                'difficulty': first_q.get('difficulty'),
            })
        
        return {
            'success': True,
            'quiz_id': quiz_id,
            'total_questions': total_questions,
            'questions': data['questions']
        }
        
    except Exception as e:
        print_error(f"Failed to get Hindi Daily Quiz: {str(e)}")
        return {'success': False, 'error': str(e)}


# ============================================================================
# TEST 2: Get User Coins Before Submission
# ============================================================================
def test_get_user_coins_before():
    print_header("TEST 2: Get User Coins BEFORE Submission")
    
    try:
        url = f"{BASE_URL}/api/daily-quiz/coins/?user_id={TEST_USER}"
        print_info(f"Requesting: {url}")
        
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        coins_before = {
            'total_coins': data.get('total_coins', 0),
            'lifetime_coins': data.get('lifetime_coins', 0),
            'coins_spent': data.get('coins_spent', 0),
        }
        
        print_data("Coins BEFORE Submission", coins_before)
        print_success(f"User {TEST_USER} has {coins_before['total_coins']} coins before submission")
        
        return coins_before
        
    except Exception as e:
        print_error(f"Failed to get user coins: {str(e)}")
        return None


# ============================================================================
# TEST 3: Start Daily Quiz (Award Participation Coins)
# ============================================================================
def test_start_daily_quiz(quiz_id):
    print_header("TEST 3: Start Daily Quiz (Award Participation Coins)")
    
    try:
        url = f"{BASE_URL}/api/daily-quiz/start/"
        payload = {
            "user_id": TEST_USER,
            "quiz_id": quiz_id
        }
        
        print_info(f"POST {url}")
        print_data("Payload", payload)
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        coins_awarded = data.get('coins_awarded', 0)
        print_success(f"Quiz started. Awarded {coins_awarded} participation coins")
        print_data("Start Quiz Response", data)
        
        return {
            'success': True,
            'coins_awarded': coins_awarded
        }
        
    except Exception as e:
        print_error(f"Failed to start quiz: {str(e)}")
        return {'success': False, 'error': str(e)}


# ============================================================================
# TEST 4: Submit Hindi Daily Quiz with Answers
# ============================================================================
def test_submit_hindi_daily_quiz(quiz_id, questions):
    print_header("TEST 4: Submit Hindi Daily Quiz with Answers")
    
    try:
        # Create answers (mix of correct and incorrect for testing)
        answers = {}
        for idx, q in enumerate(questions, 1):
            # Simple strategy: answer with option index 0, 1, 2, 3 in rotation
            answer_index = (idx - 1) % 4
            answers[str(idx)] = answer_index
        
        url = f"{BASE_URL}/api/daily-quiz/submit/"
        payload = {
            "user_id": TEST_USER,
            "quiz_id": quiz_id,
            "answers": answers,
            "time_taken_seconds": 180  # 3 minutes
        }
        
        print_info(f"POST {url}")
        print_data("Submission Payload", {
            "user_id": TEST_USER,
            "quiz_id": quiz_id,
            "answers_sample": dict(list(answers.items())[:2]),  # Show only first 2
            "time_taken_seconds": 180,
            "total_answers": len(answers)
        })
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract important info
        result = data.get('result', {})
        coin_breakdown = data.get('coin_breakdown', {})
        
        print_success(f"Quiz submitted successfully!")
        print_data("Quiz Results", {
            'correct_count': result.get('correct_count'),
            'total_questions': result.get('total_questions'),
            'score_percentage': result.get('score_percentage'),
            'time_taken_seconds': result.get('time_taken_seconds'),
        })
        print_data("Coins Breakdown", coin_breakdown)
        print_data("Message", {"message": data.get('message')})
        
        return {
            'success': True,
            'correct_count': result.get('correct_count', 0),
            'total_questions': result.get('total_questions', 0),
            'score_percentage': result.get('score_percentage', 0),
            'coins_earned': result.get('coins_earned', 0),
            'total_coins_now': data.get('total_coins', 0),
            'results': data.get('results', [])
        }
        
    except Exception as e:
        print_error(f"Failed to submit quiz: {str(e)}")
        return {'success': False, 'error': str(e)}


# ============================================================================
# TEST 5: Get User Coins After Submission
# ============================================================================
def test_get_user_coins_after():
    print_header("TEST 5: Get User Coins AFTER Submission")
    
    try:
        url = f"{BASE_URL}/api/daily-quiz/coins/?user_id={TEST_USER}"
        print_info(f"Requesting: {url}")
        
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        coins_after = {
            'total_coins': data.get('total_coins', 0),
            'lifetime_coins': data.get('lifetime_coins', 0),
            'coins_spent': data.get('coins_spent', 0),
        }
        
        print_data("Coins AFTER Submission", coins_after)
        print_success(f"User {TEST_USER} now has {coins_after['total_coins']} coins")
        
        # Show recent transactions
        recent_txns = data.get('recent_transactions', [])
        if recent_txns:
            print_data("Recent Transactions", recent_txns[:5])
        
        return coins_after
        
    except Exception as e:
        print_error(f"Failed to get user coins: {str(e)}")
        return None


# ============================================================================
# TEST 6: Get Quiz History
# ============================================================================
def test_get_quiz_history():
    print_header("TEST 6: Get Quiz History for User")
    
    try:
        url = f"{BASE_URL}/api/daily-quiz/history/?user_id={TEST_USER}&limit=10"
        print_info(f"Requesting: {url}")
        
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        history = data.get('history', [])
        stats = data.get('stats', {})
        
        print_data("Quiz History Stats", stats)
        
        if history:
            print_success(f"User has {len(history)} quiz attempts")
            print_data("Latest Quiz Attempts", history[:3])
        else:
            print_info("No quiz history found")
        
        return {
            'success': True,
            'history': history,
            'stats': stats
        }
        
    except Exception as e:
        print_error(f"Failed to get quiz history: {str(e)}")
        return {'success': False, 'error': str(e)}


# ============================================================================
# TEST 7: Test YouTube Summarizer with Specific URL
# ============================================================================
def test_youtube_summarizer():
    print_header("TEST 7: YouTube Summarizer - Specific URL Test")
    
    youtube_url = "https://www.youtube.com/watch?v=XesW1fJIJTc"
    
    try:
        url = f"{BASE_URL}/api/youtube/summarize/"
        payload = {
            "video_url": youtube_url
        }
        
        print_info(f"POST {url}")
        print_info(f"Testing URL: {youtube_url}")
        print_info("Processing video... (this may take a moment)")
        
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('success'):
            print_error(f"YouTube API returned error: {data.get('error')}")
            print_data("Error Details", data)
            return {'success': False, 'error': data.get('error')}
        
        summary = data.get('summary', '')
        
        # Analyze summary
        summary_length = len(summary)
        has_timestamps = '[' in summary and ':' in summary  # Check for [MM:SS] pattern
        has_sections = any(marker in summary for marker in [
            'EXECUTIVE SUMMARY',
            'VIDEO TIMELINE',
            'MAIN TOPIC',
            'KEY POINTS',
            'IMPORTANT CONCEPTS'
        ])
        
        print_success(f"YouTube video processed successfully!")
        print_data("Summary Metadata", {
            'video_url': youtube_url,
            'summary_length': summary_length,
            'has_timestamps': has_timestamps,
            'has_sections': has_sections,
            'first_500_chars': summary[:500]
        })
        
        # Count sections
        section_count = sum(1 for marker in [
            'EXECUTIVE SUMMARY',
            'VIDEO TIMELINE',
            'MAIN TOPIC',
            'KEY POINTS',
            'IMPORTANT CONCEPTS',
            'STATISTICS',
            'QUOTES',
            'VISUAL DESCRIPTIONS',
            'TARGET AUDIENCE',
            'KEY TAKEAWAYS',
            'CHAPTER BREAKDOWN',
            'OVERALL ASSESSMENT',
            'VIEWER QUESTIONS',
            'RELATED TOPICS'
        ] if marker in summary)
        
        print_success(f"Summary contains {section_count}/14 comprehensive sections")
        
        # Check for timestamps
        import re
        timestamps = re.findall(r'\[\d{2}:\d{2}\]', summary)
        print_success(f"Found {len(timestamps)} timestamps in summary")
        if timestamps:
            print_data("Sample Timestamps", timestamps[:5])
        
        return {
            'success': True,
            'summary_length': summary_length,
            'has_timestamps': has_timestamps,
            'timestamp_count': len(timestamps),
            'section_count': section_count,
            'summary_preview': summary[:1000]
        }
        
    except requests.exceptions.Timeout:
        print_error("YouTube summarizer request timed out (video may be too long)")
        return {'success': False, 'error': 'Request timeout'}
    except Exception as e:
        print_error(f"Failed to test YouTube summarizer: {str(e)}")
        return {'success': False, 'error': str(e)}


# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================
def run_all_tests():
    print_header("COMPREHENSIVE TEST SUITE - HINDI QUIZ, COINS, & YOUTUBE")
    print_info(f"Test Date: {date.today()}")
    print_info(f"Test User: {TEST_USER}")
    print_info(f"Language: {HINDI_TEST_LANGUAGE}")
    
    results = {}
    
    # Test 1: Get Hindi Daily Quiz
    print("\n")
    quiz_result = test_get_hindi_daily_quiz()
    results['test1_hindi_quiz'] = quiz_result
    
    if not quiz_result['success']:
        print_error("Cannot proceed without quiz. Stopping tests.")
        return results
    
    quiz_id = quiz_result['quiz_id']
    questions = quiz_result['questions']
    
    # Test 2: Get coins before submission
    print("\n")
    coins_before = test_get_user_coins_before()
    results['test2_coins_before'] = coins_before
    
    # Test 3: Start daily quiz
    print("\n")
    start_result = test_start_daily_quiz(quiz_id)
    results['test3_start_quiz'] = start_result
    
    time.sleep(1)  # Small delay between requests
    
    # Test 4: Submit daily quiz
    print("\n")
    submit_result = test_submit_hindi_daily_quiz(quiz_id, questions)
    results['test4_submit_quiz'] = submit_result
    
    time.sleep(1)  # Small delay between requests
    
    # Test 5: Get coins after submission
    print("\n")
    coins_after = test_get_user_coins_after()
    results['test5_coins_after'] = coins_after
    
    time.sleep(1)  # Small delay between requests
    
    # Test 6: Get quiz history
    print("\n")
    history_result = test_get_quiz_history()
    results['test6_history'] = history_result
    
    time.sleep(1)  # Small delay between requests
    
    # Test 7: YouTube Summarizer
    print("\n")
    youtube_result = test_youtube_summarizer()
    results['test7_youtube'] = youtube_result
    
    # ========================================================================
    # SUMMARY REPORT
    # ========================================================================
    print_header("TEST SUMMARY REPORT")
    
    print(f"{YELLOW}Test Results:{RESET}")
    print(f"  {GREEN}✓{RESET} Test 1: Hindi Daily Quiz - {'PASS' if quiz_result['success'] else 'FAIL'}")
    print(f"  {GREEN}✓{RESET} Test 2: Get Coins Before - {'PASS' if coins_before else 'FAIL'}")
    print(f"  {GREEN}✓{RESET} Test 3: Start Quiz - {'PASS' if start_result['success'] else 'FAIL'}")
    print(f"  {GREEN}✓{RESET} Test 4: Submit Quiz - {'PASS' if submit_result['success'] else 'FAIL'}")
    print(f"  {GREEN}✓{RESET} Test 5: Get Coins After - {'PASS' if coins_after else 'FAIL'}")
    print(f"  {GREEN}✓{RESET} Test 6: Quiz History - {'PASS' if history_result['success'] else 'FAIL'}")
    print(f"  {GREEN}✓{RESET} Test 7: YouTube Summarizer - {'PASS' if youtube_result['success'] else 'FAIL'}")
    
    # Coins flow analysis
    if coins_before and coins_after:
        coins_gained = coins_after['total_coins'] - coins_before['total_coins']
        expected_coins = start_result.get('coins_awarded', 0) + submit_result.get('coins_earned', 0)
        
        print(f"\n{YELLOW}Coins Flow Analysis:{RESET}")
        print(f"  Coins Before: {coins_before['total_coins']}")
        print(f"  Coins After: {coins_after['total_coins']}")
        print(f"  Coins Gained: {coins_gained}")
        print(f"  Expected: {expected_coins}")
        
        if coins_gained == expected_coins:
            print_success(f"Coins flow verified! User earned {coins_gained} coins correctly")
        else:
            print_error(f"Coins mismatch! Expected {expected_coins}, got {coins_gained}")
    
    # Hindi verification
    if submit_result['success'] and submit_result.get('results'):
        first_result = submit_result['results'][0]
        print(f"\n{YELLOW}Hindi Quiz Verification:{RESET}")
        print(f"  Question: {first_result.get('question')}")
        print(f"  Category: {first_result.get('category')}")
        if any(ord(c) >= 2304 and ord(c) <= 2431 for c in first_result.get('question', '')):
            print_success("Questions confirmed to be in Devanagari script (Hindi)")
        else:
            print_error("Questions may not be in Hindi")
    
    # YouTube verification
    if youtube_result['success']:
        print(f"\n{YELLOW}YouTube Summarizer Verification:{RESET}")
        print(f"  Summary Length: {youtube_result['summary_length']} characters")
        print(f"  Timestamps Found: {youtube_result['timestamp_count']}")
        print(f"  Section Count: {youtube_result['section_count']}/14")
        if youtube_result['has_timestamps']:
            print_success("Summary contains timestamps [MM:SS]")
        else:
            print_error("Summary lacks timestamps")
    
    print_header("END OF TEST SUITE")
    
    return results


if __name__ == "__main__":
    try:
        results = run_all_tests()
        
        # Save results to file
        with open('TEST_RESULTS_HINDI_COINS_YOUTUBE.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print_success(f"Test results saved to TEST_RESULTS_HINDI_COINS_YOUTUBE.json")
        
    except KeyboardInterrupt:
        print_error("\nTests interrupted by user")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()

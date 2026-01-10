#!/usr/bin/env python3
"""
Comprehensive Production API Endpoint Testing Suite
Tests all endpoints and validates responses
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8003"
USER_ID = "rahuljha996886"

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

test_results = {
    'passed': 0,
    'failed': 0,
    'errors': []
}

def print_header(text):
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{text.center(80)}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

def print_success(test_name, status_code, response_size):
    global test_results
    test_results['passed'] += 1
    print(f"{GREEN}✓ PASS{RESET} | {test_name} (HTTP {status_code}, {response_size} bytes)")

def print_error(test_name, error_msg):
    global test_results
    test_results['failed'] += 1
    print(f"{RED}✗ FAIL{RESET} | {test_name}")
    print(f"  {RED}Error: {error_msg}{RESET}")
    test_results['errors'].append({'test': test_name, 'error': error_msg})

def validate_response(response, expected_status=200, has_data=True):
    """Validate response structure and status"""
    if response.status_code != expected_status:
        return False, f"Expected {expected_status}, got {response.status_code}"
    
    try:
        data = response.json()
        if has_data and not data:
            return False, "Empty response body"
        return True, data
    except Exception as e:
        return False, f"Invalid JSON: {str(e)}"

# ============================================================================
# TEST 1: DAILY QUIZ ENDPOINTS
# ============================================================================
print_header("TEST 1: DAILY QUIZ ENDPOINTS")

# 1.1 Get Hindi Quiz
print("1.1 Getting Hindi Daily Quiz...")
try:
    response = requests.get(
        f"{BASE_URL}/api/daily-quiz/?language=hindi&user_id={USER_ID}",
        timeout=10
    )
    valid, result = validate_response(response, 200, True)
    if valid:
        quiz_id = result.get('quiz_id')
        questions_count = len(result.get('questions', []))
        print_success("Get Hindi Quiz", response.status_code, len(response.text))
        print(f"  Quiz ID: {quiz_id}")
        print(f"  Questions: {questions_count}")
    else:
        print_error("Get Hindi Quiz", result)
except Exception as e:
    print_error("Get Hindi Quiz", str(e))

# 1.2 Get English Quiz
print("\n1.2 Getting English Daily Quiz...")
try:
    response = requests.get(
        f"{BASE_URL}/api/daily-quiz/?language=english&user_id={USER_ID}",
        timeout=10
    )
    valid, result = validate_response(response, 200, True)
    if valid:
        print_success("Get English Quiz", response.status_code, len(response.text))
        quiz_id = result.get('quiz_id')
        print(f"  Quiz ID: {quiz_id}")
    else:
        print_error("Get English Quiz", result)
except Exception as e:
    print_error("Get English Quiz", str(e))

# 1.3 Submit Quiz
print("\n1.3 Submitting Daily Quiz...")
try:
    payload = {
        "user_id": USER_ID,
        "quiz_id": quiz_id,
        "answers": {"1": 0, "2": 1, "3": 2, "4": 3, "5": 0},
        "time_taken_seconds": 180
    }
    response = requests.post(
        f"{BASE_URL}/api/daily-quiz/submit/",
        json=payload,
        timeout=10
    )
    valid, result = validate_response(response, 200, True)
    if valid:
        coins_earned = result.get('result', {}).get('coins_earned', 0)
        score = result.get('result', {}).get('score_percentage', 0)
        print_success("Submit Quiz", response.status_code, len(response.text))
        print(f"  Score: {score}%")
        print(f"  Coins Earned: {coins_earned}")
        print(f"  Total Coins: {result.get('total_coins', 0)}")
    else:
        print_error("Submit Quiz", result)
except Exception as e:
    print_error("Submit Quiz", str(e))

# 1.4 Get Coins Balance
print("\n1.4 Getting User Coins Balance...")
try:
    response = requests.get(
        f"{BASE_URL}/api/daily-quiz/coins/?user_id={USER_ID}",
        timeout=10
    )
    valid, result = validate_response(response, 200, True)
    if valid:
        total_coins = result.get('total_coins', 0)
        transactions = len(result.get('recent_transactions', []))
        print_success("Get Coins Balance", response.status_code, len(response.text))
        print(f"  Total Coins: {total_coins}")
        print(f"  Recent Transactions: {transactions}")
    else:
        print_error("Get Coins Balance", result)
except Exception as e:
    print_error("Get Coins Balance", str(e))

# 1.5 Get Quiz History
print("\n1.5 Getting Quiz History...")
try:
    response = requests.get(
        f"{BASE_URL}/api/daily-quiz/history/?user_id={USER_ID}&limit=5",
        timeout=10
    )
    valid, result = validate_response(response, 200, True)
    if valid:
        attempts = len(result.get('history', []))
        stats = result.get('stats', {})
        print_success("Get Quiz History", response.status_code, len(response.text))
        print(f"  Total Attempts: {stats.get('total_attempts', 0)}")
        print(f"  Average Score: {stats.get('average_score', 0):.2f}%")
        print(f"  Total Coins Earned: {stats.get('total_coins_earned', 0)}")
    else:
        print_error("Get Quiz History", result)
except Exception as e:
    print_error("Get Quiz History", str(e))

# ============================================================================
# TEST 2: FLASHCARDS ENDPOINTS
# ============================================================================
print_header("TEST 2: FLASHCARDS ENDPOINTS")

print("2.1 Generating Flashcards...")
try:
    payload = {
        "topic": "World History",
        "num_cards": 5,
        "language": "english",
        "difficulty": "medium"
    }
    response = requests.post(
        f"{BASE_URL}/api/flashcards/generate/",
        json=payload,
        timeout=30
    )
    valid, result = validate_response(response, 200, True)
    if valid:
        cards = result.get('data', {}).get('cards', [])
        print_success("Generate Flashcards", response.status_code, len(response.text))
        print(f"  Cards Generated: {len(cards)}")
        if cards:
            print(f"  First Card Question: {cards[0].get('question', '')[:60]}...")
    else:
        print_error("Generate Flashcards", result)
except requests.exceptions.Timeout:
    print_error("Generate Flashcards", "Request timeout - Gemini API slow")
except Exception as e:
    print_error("Generate Flashcards", str(e))

# ============================================================================
# TEST 3: PREDICTED QUESTIONS ENDPOINTS
# ============================================================================
print_header("TEST 3: PREDICTED QUESTIONS ENDPOINTS")

print("3.1 Generating Predicted Questions...")
try:
    payload = {
        "topic": "Science",
        "user_id": USER_ID,
        "difficulty": "medium",
        "num_questions": 3
    }
    response = requests.post(
        f"{BASE_URL}/api/predicted-questions/generate/",
        json=payload,
        timeout=45
    )
    valid, result = validate_response(response, 200, True)
    if valid:
        questions = result.get('data', {}).get('questions', [])
        confidence = result.get('data', {}).get('confidence_score', 0)
        print_success("Generate Predicted Questions", response.status_code, len(response.text))
        print(f"  Questions Generated: {len(questions)}")
        print(f"  Confidence Score: {confidence:.2f}")
    else:
        print_error("Generate Predicted Questions", result)
except requests.exceptions.Timeout:
    print_error("Generate Predicted Questions", "Request timeout - Gemini API slow")
except Exception as e:
    print_error("Generate Predicted Questions", str(e))

# ============================================================================
# TEST 4: YOUTUBE SUMMARIZER
# ============================================================================
print_header("TEST 4: YOUTUBE SUMMARIZER")

print("4.1 Summarizing YouTube Video...")
try:
    payload = {
        "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    }
    response = requests.post(
        f"{BASE_URL}/api/youtube/summarize/",
        json=payload,
        timeout=60
    )
    valid, result = validate_response(response, 200, True)
    if valid:
        metadata = result.get('metadata', {})
        summary = result.get('summary', '')
        print_success("Summarize Video", response.status_code, len(response.text))
        print(f"  Summary Length: {len(summary)} chars")
        print(f"  Timestamps Found: {metadata.get('timestamp_count', 0)}")
        print(f"  Sections: {result.get('sections', 0)}/14")
    else:
        print_error("Summarize Video", result)
except requests.exceptions.Timeout:
    print_error("Summarize Video", "Request timeout - Video processing slow")
except Exception as e:
    print_error("Summarize Video", str(e))

# ============================================================================
# TEST 5: ERROR HANDLING
# ============================================================================
print_header("TEST 5: ERROR HANDLING")

# 5.1 Invalid Quiz ID
print("5.1 Testing Invalid Quiz ID...")
try:
    payload = {
        "user_id": USER_ID,
        "quiz_id": "invalid-quiz-id",
        "answers": {"1": 0},
        "time_taken_seconds": 60
    }
    response = requests.post(
        f"{BASE_URL}/api/daily-quiz/submit/",
        json=payload,
        timeout=10
    )
    if response.status_code == 404:
        print_success("Invalid Quiz ID Handling", response.status_code, len(response.text))
    else:
        print_error("Invalid Quiz ID Handling", f"Expected 404, got {response.status_code}")
except Exception as e:
    print_error("Invalid Quiz ID Handling", str(e))

# 5.2 Missing Required Fields
print("\n5.2 Testing Missing Required Fields...")
try:
    payload = {"user_id": USER_ID}  # Missing quiz_id
    response = requests.post(
        f"{BASE_URL}/api/daily-quiz/submit/",
        json=payload,
        timeout=10
    )
    if response.status_code == 400:
        print_success("Missing Fields Handling", response.status_code, len(response.text))
    else:
        print_error("Missing Fields Handling", f"Expected 400, got {response.status_code}")
except Exception as e:
    print_error("Missing Fields Handling", str(e))

# ============================================================================
# TEST SUMMARY
# ============================================================================
print_header("TEST SUMMARY REPORT")

total_tests = test_results['passed'] + test_results['failed']
pass_rate = (test_results['passed'] / total_tests * 100) if total_tests > 0 else 0

print(f"\n{YELLOW}Overall Results:{RESET}")
print(f"  {GREEN}Passed: {test_results['passed']}{RESET}")
print(f"  {RED}Failed: {test_results['failed']}{RESET}")
print(f"  Total: {total_tests}")
print(f"  Pass Rate: {pass_rate:.1f}%")

if test_results['errors']:
    print(f"\n{YELLOW}Failed Tests:{RESET}")
    for error in test_results['errors']:
        print(f"  • {error['test']}: {error['error']}")

print(f"\n{BLUE}{'='*80}{RESET}")
if test_results['failed'] == 0:
    print(f"{GREEN}✓ ALL TESTS PASSED - READY FOR PRODUCTION{RESET}".center(80))
else:
    print(f"{YELLOW}⚠ SOME TESTS FAILED - REVIEW ERRORS{RESET}".center(80))
print(f"{BLUE}{'='*80}{RESET}")

# Save results to file
results_file = '/Users/vishaljha/Ed_tech_backend/PRODUCTION_TEST_RESULTS.json'
with open(results_file, 'w') as f:
    json.dump({
        'timestamp': datetime.now().isoformat(),
        'total_tests': total_tests,
        'passed': test_results['passed'],
        'failed': test_results['failed'],
        'pass_rate': pass_rate,
        'errors': test_results['errors']
    }, f, indent=2)

print(f"\n✅ Results saved to: {results_file}")

sys.exit(0 if test_results['failed'] == 0 else 1)

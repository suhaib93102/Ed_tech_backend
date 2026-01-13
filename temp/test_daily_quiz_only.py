#!/usr/bin/env python3
"""
Focused Daily Quiz Test Script
Tests only the daily quiz endpoints with real data
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"
USER_ID = "rahuljha996886"

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text, details=""):
    print(f"{GREEN}✓ {text}{RESET}")
    if details:
        print(f"  {details}")

def print_error(text, error=""):
    print(f"{RED}✗ {text}{RESET}")
    if error:
        print(f"  {RED}Error: {error}{RESET}")

def test_get_hindi_quiz():
    """Test getting Hindi daily quiz"""
    print("Testing: Get Hindi Daily Quiz")
    try:
        url = f"{BASE_URL}/api/daily-quiz/?language=hindi&user_id={USER_ID}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            quiz_id = data.get('quiz_id')
            questions = data.get('questions', [])
            coins = data.get('coins', {})

            print_success("Hindi Quiz Retrieved",
                         f"Quiz ID: {quiz_id}, Questions: {len(questions)}, "
                         f"Bonus: {coins.get('attempt_bonus', 0)} coins")

            # Show first question
            if questions:
                q1 = questions[0]
                print(f"  Sample Question: {q1.get('question', '')[:50]}...")

            return quiz_id
        else:
            print_error("Hindi Quiz Failed", f"HTTP {response.status_code}")
            return None

    except Exception as e:
        print_error("Hindi Quiz Error", str(e))
        return None

def test_get_english_quiz():
    """Test getting English daily quiz"""
    print("\nTesting: Get English Daily Quiz")
    try:
        url = f"{BASE_URL}/api/daily-quiz/?language=english&user_id={USER_ID}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            quiz_id = data.get('quiz_id')
            questions = data.get('questions', [])

            print_success("English Quiz Retrieved",
                         f"Quiz ID: {quiz_id}, Questions: {len(questions)}")

            # Show first question
            if questions:
                q1 = questions[0]
                print(f"  Sample Question: {q1.get('question', '')[:50]}...")

            return quiz_id
        else:
            print_error("English Quiz Failed", f"HTTP {response.status_code}")
            return None

    except Exception as e:
        print_error("English Quiz Error", str(e))
        return None

def test_submit_quiz(quiz_id):
    """Test submitting quiz answers"""
    print("\nTesting: Submit Quiz Answers")
    try:
        payload = {
            "user_id": USER_ID,
            "quiz_id": quiz_id,
            "answers": {
                "1": 0,  # Answer A for question 1
                "2": 1,  # Answer B for question 2
                "3": 2,  # Answer C for question 3
                "4": 3,  # Answer D for question 4
                "5": 0   # Answer A for question 5
            },
            "time_taken_seconds": 180
        }

        response = requests.post(
            f"{BASE_URL}/api/daily-quiz/submit/",
            json=payload,
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            result = data.get('result', {})
            coin_breakdown = data.get('coin_breakdown', {})

            correct = result.get('correct_count', 0)
            total = result.get('total_questions', 0)
            score = result.get('score_percentage', 0)
            coins_earned = result.get('coins_earned', 0)
            total_coins = data.get('total_coins', 0)

            print_success("Quiz Submitted Successfully",
                         f"Score: {correct}/{total} ({score}%), "
                         f"Coins Earned: {coins_earned}, "
                         f"Total Balance: {total_coins}")

            print(f"  Coin Breakdown:")
            print(f"    Attempt Bonus: {coin_breakdown.get('attempt_bonus', 0)}")
            print(f"    Correct Answers: {coin_breakdown.get('correct_answers', 0)} × {coin_breakdown.get('coins_per_correct', 0)} = {coin_breakdown.get('correct_answer_coins', 0)}")
            print(f"    Total Earned: {coin_breakdown.get('total_earned', 0)}")

            return True
        else:
            print_error("Quiz Submission Failed", f"HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"  Error Details: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"  Response: {response.text[:200]}...")
            return False

    except Exception as e:
        print_error("Quiz Submission Error", str(e))
        return False

def test_get_coins_balance():
    """Test getting user coins balance"""
    print("\nTesting: Get Coins Balance")
    try:
        url = f"{BASE_URL}/api/daily-quiz/coins/?user_id={USER_ID}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            total_coins = data.get('total_coins', 0)
            lifetime_coins = data.get('lifetime_coins', 0)
            coins_spent = data.get('coins_spent', 0)
            transactions = data.get('recent_transactions', [])

            print_success("Coins Balance Retrieved",
                         f"Total: {total_coins}, Lifetime: {lifetime_coins}, "
                         f"Spent: {coins_spent}, Recent TX: {len(transactions)}")

            # Show recent transactions
            if transactions:
                print("  Recent Transactions:")
                for tx in transactions[:3]:  # Show last 3
                    amount = tx.get('amount', 0)
                    reason = tx.get('reason', '')[:40]
                    created = tx.get('created_at', '')[:19]
                    print(f"    {amount:+d} coins - {reason}... ({created})")

            return total_coins
        else:
            print_error("Coins Balance Failed", f"HTTP {response.status_code}")
            return None

    except Exception as e:
        print_error("Coins Balance Error", str(e))
        return None

def test_get_quiz_history():
    """Test getting quiz attempt history"""
    print("\nTesting: Get Quiz History")
    try:
        url = f"{BASE_URL}/api/daily-quiz/history/?user_id={USER_ID}&limit=5"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            stats = data.get('stats', {})
            history = data.get('history', [])

            total_attempts = stats.get('total_attempts', 0)
            avg_score = stats.get('average_score', 0)
            total_coins_earned = stats.get('total_coins_earned', 0)

            print_success("Quiz History Retrieved",
                         f"Total Attempts: {total_attempts}, "
                         f"Avg Score: {avg_score:.1f}%, "
                         f"Total Coins Earned: {total_coins_earned}")

            # Show recent attempts
            if history:
                print("  Recent Attempts:")
                for attempt in history[:3]:  # Show last 3
                    date = attempt.get('date', '')
                    correct = attempt.get('correct_count', 0)
                    total = attempt.get('total_questions', 0)
                    score = attempt.get('score_percentage', 0)
                    coins = attempt.get('coins_earned', 0)
                    print(f"    {date}: {correct}/{total} ({score:.1f}%) - {coins} coins")

            return True
        else:
            print_error("Quiz History Failed", f"HTTP {response.status_code}")
            return False

    except Exception as e:
        print_error("Quiz History Error", str(e))
        return False

def main():
    print_header("DAILY QUIZ TEST SUITE")
    print(f"Server: {BASE_URL}")
    print(f"User ID: {USER_ID}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Track results
    results = {
        'tests_run': 0,
        'tests_passed': 0,
        'tests_failed': 0
    }

    # Test 1: Get Hindi Quiz
    results['tests_run'] += 1
    quiz_id_hindi = test_get_hindi_quiz()
    if quiz_id_hindi:
        results['tests_passed'] += 1
    else:
        results['tests_failed'] += 1

    # Test 2: Get English Quiz
    results['tests_run'] += 1
    quiz_id_english = test_get_english_quiz()
    if quiz_id_english:
        results['tests_passed'] += 1
    else:
        results['tests_failed'] += 1

    # Test 3: Submit Quiz (use Hindi quiz ID)
    results['tests_run'] += 1
    quiz_id_to_submit = quiz_id_hindi or quiz_id_english
    if quiz_id_to_submit and test_submit_quiz(quiz_id_to_submit):
        results['tests_passed'] += 1
    else:
        results['tests_failed'] += 1

    # Test 4: Get Coins Balance
    results['tests_run'] += 1
    coins_balance = test_get_coins_balance()
    if coins_balance is not None:
        results['tests_passed'] += 1
    else:
        results['tests_failed'] += 1

    # Test 5: Get Quiz History
    results['tests_run'] += 1
    if test_get_quiz_history():
        results['tests_passed'] += 1
    else:
        results['tests_failed'] += 1

    # Summary
    print_header("TEST SUMMARY")

    pass_rate = (results['tests_passed'] / results['tests_run'] * 100) if results['tests_run'] > 0 else 0

    print(f"\n{YELLOW}Results:{RESET}")
    print(f"  Tests Run: {results['tests_run']}")
    print(f"  {GREEN}Passed: {results['tests_passed']}{RESET}")
    print(f"  {RED}Failed: {results['tests_failed']}{RESET}")
    print(f"  Pass Rate: {pass_rate:.1f}%")

    if results['tests_failed'] == 0:
        print(f"\n{GREEN}🎉 ALL QUIZ TESTS PASSED!{RESET}")
        print(f"{GREEN}Daily Quiz system is working correctly.{RESET}")
    else:
        print(f"\n{RED}⚠ Some tests failed. Check the errors above.{RESET}")

    # Save results
    results_file = '/Users/vishaljha/Ed_tech_backend/QUIZ_TEST_RESULTS.json'
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'user_id': USER_ID,
            'results': results,
            'pass_rate': pass_rate
        }, f, indent=2)

    print(f"\n✅ Results saved to: {results_file}")

    return results['tests_failed'] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
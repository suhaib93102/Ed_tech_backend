#!/usr/bin/env python3
"""
Comprehensive test for coin storage and retrieval with Hindi language support
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:9000/api/quiz"
USER_ID = f"test_user_coins_{int(datetime.now().timestamp())}"

print("\n" + "="*80)
print("COMPREHENSIVE COIN STORAGE TEST - HINDI LANGUAGE")
print("="*80)
print(f"User ID: {USER_ID}\n")

# Create a session to maintain cookies across requests
session = requests.Session()

# TEST 0: Check initial coin balance
print("[TEST 0] Check Initial Coin Balance")
print("-" * 80)
resp_initial = session.get(f"{BASE_URL}/daily-quiz/coins/", params={"user_id": USER_ID})
print(f"Status: {resp_initial.status_code}")
initial_data = resp_initial.json()
print(f"Total Coins: {initial_data.get('total_coins', 0)}")
print(f"Lifetime Coins: {initial_data.get('lifetime_coins', 0)}")
print(f"Coins Spent: {initial_data.get('coins_spent', 0)}")
initial_coins = initial_data.get('total_coins', 0)
print()

# TEST 1: Fetch Hindi Quiz (Call 1)
print("[TEST 1] Fetch Hindi Quiz - Call 1")
print("-" * 80)
params_hindi_1 = {"user_id": USER_ID, "language": "hindi"}
resp_hindi_1 = session.get(f"{BASE_URL}/daily-quiz/", params=params_hindi_1)
print(f"Status: {resp_hindi_1.status_code}")
data_hindi_1 = resp_hindi_1.json()
print(f"Language: {data_hindi_1['quiz_metadata'].get('language', 'N/A')}")
print(f"Total Questions: {len(data_hindi_1.get('questions', []))}")
print(f"Coins per Correct: {data_hindi_1.get('coins', {}).get('per_correct_answer', 'N/A')}")
print(f"Max Possible Coins: {data_hindi_1.get('coins', {}).get('max_possible', 'N/A')}")

if len(data_hindi_1.get('questions', [])) > 0:
    print(f"\nQuestions (Hindi):")
    for idx, q in enumerate(data_hindi_1.get('questions', [])[:3], 1):
        print(f"  Q{idx}: {q.get('question', 'N/A')[:70]}...")
        options = q.get('options', [])
        for opt_idx, opt in enumerate(options):
            print(f"        {opt_idx}: {opt}")
print()

# TEST 2: Fetch Hindi Quiz (Call 2 - verify randomness)
print("[TEST 2] Fetch Hindi Quiz - Call 2 (Randomness Check)")
print("-" * 80)
params_hindi_2 = {"user_id": USER_ID, "language": "hindi"}
resp_hindi_2 = session.get(f"{BASE_URL}/daily-quiz/", params=params_hindi_2)
print(f"Status: {resp_hindi_2.status_code}")
data_hindi_2 = resp_hindi_2.json()
print(f"Total Questions: {len(data_hindi_2.get('questions', []))}")

q1_text_1 = data_hindi_1['questions'][0]['question'] if len(data_hindi_1.get('questions', [])) > 0 else "N/A"
q1_text_2 = data_hindi_2['questions'][0]['question'] if len(data_hindi_2.get('questions', [])) > 0 else "N/A"

if q1_text_1 != q1_text_2:
    print("✅ RANDOMNESS VERIFIED: Different Hindi questions on each call!")
else:
    print("⚠️  Same first question (might be coincidence)")
print()

# TEST 3: Start Quiz
print("[TEST 3] Start Quiz")
print("-" * 80)
start_payload = {"user_id": USER_ID, "language": "hindi"}
resp_start = session.post(f"{BASE_URL}/daily-quiz/start/", json=start_payload)
print(f"Status: {resp_start.status_code}")
start_data = resp_start.json()
print(f"Message: {start_data.get('message', 'N/A')}")
print()

# TEST 4: Submit Hindi Quiz Answers
print("[TEST 4] Submit Hindi Quiz Answers")
print("-" * 80)
submit_payload = {
    "user_id": USER_ID,
    "language": "hindi",
    "answers": {
        "1": "0",  # First option
        "2": "1",  # Second option
        "3": "2",  # Third option
        "4": "3",  # Fourth option
        "5": "0",  # First option
    }
}
resp_submit = session.post(f"{BASE_URL}/daily-quiz/submit/", json=submit_payload)
print(f"Status: {resp_submit.status_code}")
submit_data = resp_submit.json()

if resp_submit.status_code == 200:
    print(f"Message: {submit_data.get('message', 'N/A')}")
    print(f"Correct Count: {submit_data.get('correct_count', 'N/A')}/5")
    print(f"Coins Earned: {submit_data.get('coins_earned', 'N/A')}")
    coins_earned_1 = submit_data.get('coins_earned', 0)
else:
    print(f"Error: {submit_data.get('error', 'N/A')}")
    coins_earned_1 = 0

print()

# TEST 5: Check coin balance after submission
print("[TEST 5] Check Coin Balance After Submission")
print("-" * 80)
resp_after_1 = session.get(f"{BASE_URL}/daily-quiz/coins/", params={"user_id": USER_ID})
print(f"Status: {resp_after_1.status_code}")
after_data_1 = resp_after_1.json()
total_coins_1 = after_data_1.get('total_coins', 0)
lifetime_coins_1 = after_data_1.get('lifetime_coins', 0)

print(f"Total Coins: {total_coins_1}")
print(f"Lifetime Coins: {lifetime_coins_1}")
print(f"Coins Spent: {after_data_1.get('coins_spent', 0)}")

print(f"\n📊 Coin Tracking:")
print(f"  Initial: {initial_coins}")
print(f"  Earned: {coins_earned_1}")
print(f"  Current: {total_coins_1}")
print(f"  Match: {'✅ YES' if total_coins_1 == initial_coins + coins_earned_1 else '❌ NO'}")

print(f"\n💰 Transaction History:")
transactions = after_data_1.get('recent_transactions', [])
if transactions:
    for idx, txn in enumerate(transactions[:5], 1):
        print(f"  {idx}. {txn.get('type', 'N/A')} - {txn.get('amount', 0)} coins - {txn.get('reason', 'N/A')}")
        print(f"     Time: {txn.get('created_at', 'N/A')}")
else:
    print("  No transactions found")

print()

# TEST 6: Attempt 2 - Second Hindi Quiz to verify coins accumulate
print("[TEST 6] Second Quiz Attempt - Verify Coins Accumulate")
print("-" * 80)
resp_hindi_3 = session.get(f"{BASE_URL}/daily-quiz/", params={"user_id": USER_ID, "language": "hindi"})
print(f"Status: {resp_hindi_3.status_code}")
print(f"Questions: {len(resp_hindi_3.json().get('questions', []))}")

submit_payload_2 = {
    "user_id": USER_ID,
    "language": "hindi",
    "answers": {
        "1": "1",
        "2": "2",
        "3": "3",
        "4": "0",
        "5": "1",
    }
}
resp_submit_2 = session.post(f"{BASE_URL}/daily-quiz/submit/", json=submit_payload_2)
print(f"Submit Status: {resp_submit_2.status_code}")
if resp_submit_2.status_code == 200:
    submit_data_2 = resp_submit_2.json()
    print(f"Coins Earned: {submit_data_2.get('coins_earned', 'N/A')}")
    coins_earned_2 = submit_data_2.get('coins_earned', 0)
else:
    coins_earned_2 = 0

print()

# TEST 7: Final coin balance check
print("[TEST 7] Final Coin Balance - After Multiple Attempts")
print("-" * 80)
resp_final = session.get(f"{BASE_URL}/daily-quiz/coins/", params={"user_id": USER_ID})
print(f"Status: {resp_final.status_code}")
final_data = resp_final.json()
final_coins = final_data.get('total_coins', 0)
lifetime_coins_final = final_data.get('lifetime_coins', 0)

print(f"Total Coins: {final_coins}")
print(f"Lifetime Coins: {lifetime_coins_final}")

print(f"\n📊 Coin Accumulation Summary:")
print(f"  Initial Coins: {initial_coins}")
print(f"  Quiz 1 Earned: {coins_earned_1}")
print(f"  Quiz 2 Earned: {coins_earned_2}")
print(f"  Total Expected: {initial_coins + coins_earned_1 + coins_earned_2}")
print(f"  Total Actual: {final_coins}")
print(f"  Lifetime Total: {lifetime_coins_final}")
print(f"  Status: {'✅ COINS STORED CORRECTLY' if final_coins == initial_coins + coins_earned_1 + coins_earned_2 else '❌ MISMATCH'}")

print(f"\n💾 Full Transaction History:")
transactions_final = final_data.get('recent_transactions', [])
if transactions_final:
    for idx, txn in enumerate(transactions_final, 1):
        print(f"  {idx}. {txn.get('type', 'N/A').upper():8} | {txn.get('amount', 0):3} coins | {txn.get('reason', 'N/A')[:60]}")
else:
    print("  No transactions found")

print("\n" + "="*80)
print("TEST COMPLETED")
print("="*80 + "\n")

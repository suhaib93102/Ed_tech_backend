#!/usr/bin/env python3
"""
Test daily quiz endpoint with proper session handling
"""
import requests
import json
from pprint import pprint

BASE_URL = "http://localhost:9000/api/quiz"
USER_ID = f"test_user_{1768313223}"

print("\n" + "="*80)
print("DAILY QUIZ ENDPOINT TEST WITH SESSION HANDLING")
print("="*80)

# Create a session to maintain cookies across requests
session = requests.Session()

# TEST 1: Get English Quiz (Call 1)
print("\n[TEST 1] Fetch English Quiz - Call 1 (Randomness Check)")
print("-" * 80)
params_1 = {"user_id": USER_ID, "language": "english"}
resp_1 = session.get(f"{BASE_URL}/daily-quiz/", params=params_1)
print(f"Status: {resp_1.status_code}")
data_1 = resp_1.json()
q1_text = data_1['questions'][0]['question'] if 'questions' in data_1 and len(data_1['questions']) > 0 else "N/A"
print(f"Total Questions: {len(data_1.get('questions', []))}")
print(f"Q1 (Call 1): {q1_text[:80]}...")

# TEST 2: Get English Quiz (Call 2 - Different call should give different random questions)
print("\n[TEST 2] Fetch English Quiz - Call 2 (Randomness Check)")
print("-" * 80)
params_2 = {"user_id": USER_ID, "language": "english"}
resp_2 = session.get(f"{BASE_URL}/daily-quiz/", params=params_2)
print(f"Status: {resp_2.status_code}")
data_2 = resp_2.json()
q1_text_2 = data_2['questions'][0]['question'] if 'questions' in data_2 and len(data_2['questions']) > 0 else "N/A"
print(f"Total Questions: {len(data_2.get('questions', []))}")
print(f"Q1 (Call 2): {q1_text_2[:80]}...")

# Check if questions are different (true randomness)
if q1_text != q1_text_2:
    print("✅ RANDOMNESS VERIFIED: Different questions on each call!")
else:
    print("⚠️  Same first question (could be coincidence - both are random)")

# TEST 3: Get Hindi Quiz
print("\n[TEST 3] Fetch Hindi Quiz")
print("-" * 80)
params_3 = {"user_id": USER_ID, "language": "hindi"}
resp_3 = session.get(f"{BASE_URL}/daily-quiz/", params=params_3)
print(f"Status: {resp_3.status_code}")
data_3 = resp_3.json()
print(f"Total Questions: {len(data_3.get('questions', []))}")
print(f"Language: {data_3['quiz_metadata'].get('language', 'N/A')}")
if len(data_3.get('questions', [])) > 0:
    print(f"Q1 (Hindi): {data_3['questions'][0]['question'][:80]}...")

# TEST 4: Start Quiz (Award participation coins)
print("\n[TEST 4] Start Quiz (Award Coins for Participation)")
print("-" * 80)
start_payload = {"user_id": USER_ID, "language": "english"}
resp_4 = session.post(f"{BASE_URL}/daily-quiz/start/", json=start_payload)
print(f"Status: {resp_4.status_code}")
data_4 = resp_4.json()
print(f"Message: {data_4.get('message', 'N/A')}")
print(f"Coins Awarded: {data_4.get('coins_awarded', 'N/A')}")

# TEST 5: Submit Quiz Answers
print("\n[TEST 5] Submit Quiz Answers")
print("-" * 80)
submit_payload = {
    "user_id": USER_ID,
    "language": "english",
    "answers": {
        "1": "0",
        "2": "1",
        "3": "2",
        "4": "3",
        "5": "0"
    }
}
resp_5 = session.post(f"{BASE_URL}/daily-quiz/submit/", json=submit_payload)
print(f"Status: {resp_5.status_code}")
data_5 = resp_5.json()
if resp_5.status_code == 200:
    print(f"Score: {data_5.get('score', 'N/A')}/{data_5.get('total_questions', 'N/A')}")
    print(f"Coins Earned: {data_5.get('coins_earned', 'N/A')}")
    print(f"Message: {data_5.get('message', 'N/A')}")
else:
    print(f"Error: {data_5.get('error', 'N/A')}")
    print(f"Details: {data_5.get('details', data_5.get('message', 'N/A'))}")

# TEST 6: Get User Coins
print("\n[TEST 6] Check User Coins")
print("-" * 80)
resp_6 = session.get(f"{BASE_URL}/daily-quiz/coins/", params={"user_id": USER_ID})
print(f"Status: {resp_6.status_code}")
if resp_6.status_code == 200:
    data_6 = resp_6.json()
    print(f"Total Coins: {data_6.get('total_coins', 'N/A')}")
    print(f"Lifetime Coins: {data_6.get('lifetime_coins', 'N/A')}")

print("\n" + "="*80)
print("TEST COMPLETED")
print("="*80 + "\n")

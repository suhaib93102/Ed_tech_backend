#!/usr/bin/env python3

import jwt
from datetime import datetime, timedelta
import subprocess
import json

SECRET_KEY = "4f5e2bac434c38bcf80b3f71df16ad50"
payload = {
    "user_id": 8,
    "username": "user8",
    "email": "user8@example.com",
    "exp": datetime.utcnow() + timedelta(hours=24),
    "iat": datetime.utcnow()
}

token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

print("=" * 70)
print("CURL COMMAND FOR USER 8 - DAILY QUIZ")
print("=" * 70)
print()
print("TOKEN:")
print(token)
print()
print("CURL COMMAND:")
print(f"curl -X GET 'http://127.0.0.1:8000/api/quiz/daily-quiz/?user_id=8&language=english' \\")
print(f"  -H 'Authorization: Bearer {token}' \\")
print(f"  -H 'Content-Type: application/json'")
print()
print("=" * 70)
print("RESPONSE:")
print("=" * 70)
print()

result = subprocess.run([
    'curl', '-s', '-X', 'GET',
    'http://127.0.0.1:8000/api/quiz/daily-quiz/?user_id=8&language=english',
    '-H', f'Authorization: Bearer {token}',
    '-H', 'Content-Type: application/json'
], capture_output=True, text=True)

try:
    data = json.loads(result.stdout)
    print(json.dumps(data, indent=2))
    
    if 'quiz_id' in data:
        quiz_id = data['quiz_id']
        print()
        print("=" * 70)
        print(f"✅ SUCCESS! Quiz ID is present in response:")
        print(f"   Quiz ID: {quiz_id}")
        print("=" * 70)
        print()
        print("This quiz_id should be used when submitting answers:")
        print(f"  curl -X POST 'http://127.0.0.1:8000/api/quiz/submit-daily-quiz/' \\")
        print(f"    -H 'Authorization: Bearer {token}' \\")
        print(f"    -H 'Content-Type: application/json' \\")
        submit_data = {"user_id": 8, "quiz_id": quiz_id, "language": "english", "answers": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}}
        print(f"    -d '{json.dumps(submit_data)}'")
    else:
        print()
        print("=" * 70)
        print("❌ QUIZ_ID NOT FOUND IN RESPONSE")
        print("Available keys:", list(data.keys()))
        print("=" * 70)
        
except json.JSONDecodeError as e:
    print(f"Error parsing response: {e}")
    print("Raw output:")
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)

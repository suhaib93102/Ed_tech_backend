#!/usr/bin/env python
import requests
import json

# Test the withdrawal endpoint directly
url = "http://localhost:8003/api/wallet/withdraw/"
headers = {'Content-Type': 'application/json'}

# Test data
data = {
    "upi_id": "testuser@paytm",
    "coins": 200,
    "user_id": "5"  # String as expected
}

print(f"Making request to: {url}")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
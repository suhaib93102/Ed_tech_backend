#!/usr/bin/env python3
"""
Direct API testing script that doesn't rely on curl
"""
import requests
import json
import time

API_BASE = "http://localhost:8000"

def print_test(num, desc):
    print(f"\n{'='*70}")
    print(f"TEST {num}: {desc}")
    print('='*70)

def print_result(success, data):
    if success:
        print("✅ PASS")
    else:
        print("❌ FAIL")
    print(json.dumps(data, indent=2))

# Test 1: Valid withdrawal
print_test(1, "Valid Withdrawal - 200 coins (minimum)")
try:
    r = requests.post(f"{API_BASE}/api/wallet/withdraw/",
                     json={"user_id": "test_user_min_coins", "upi_id": "test@paytm", "coins": 200},
                     timeout=10)
    data = r.json()
    print_result(data.get('success'), data)
except Exception as e:
    print(f"❌ ERROR: {e}")

time.sleep(1)

# Test 2: Below minimum
print_test(2, "Below Minimum - 150 coins (should FAIL)")
try:
    r = requests.post(f"{API_BASE}/api/wallet/withdraw/",
                     json={"user_id": "test_user_below_min", "upi_id": "test@paytm", "coins": 150},
                     timeout=10)
    data = r.json()
    print_result(not data.get('success'), data)
except Exception as e:
    print(f"❌ ERROR: {e}")

time.sleep(1)

# Test 3: Balance check
print_test(3, "Balance Check - remaining < 100 (should FAIL)")
try:
    r = requests.post(f"{API_BASE}/api/wallet/withdraw/",
                     json={"user_id": "test_user_balance_check", "upi_id": "test@paytm", "coins": 300},
                     timeout=10)
    data = r.json()
    print_result(not data.get('success'), data)
except Exception as e:
    print(f"❌ ERROR: {e}")

time.sleep(1)

# Test 4: Invalid UPI
print_test(4, "Invalid UPI ID (should FAIL)")
try:
    r = requests.post(f"{API_BASE}/api/wallet/withdraw/",
                     json={"user_id": "test_user_valid", "upi_id": "invalidupi", "coins": 200},
                     timeout=10)
    data = r.json()
    print_result(not data.get('success'), data)
except Exception as e:
    print(f"❌ ERROR: {e}")

time.sleep(1)

# Test 5: Valid large withdrawal
print_test(5, "Valid Large Withdrawal - 500 coins")
try:
    r = requests.post(f"{API_BASE}/api/wallet/withdraw/",
                     json={"user_id": "test_user_valid", "upi_id": "test@phonepe", "coins": 500},
                     timeout=10)
    data = r.json()
    print_result(data.get('success'), data)
except Exception as e:
    print(f"❌ ERROR: {e}")

time.sleep(1)

# Test 6: Check balance
print_test(6, "Verify Coin Deduction")
try:
    r = requests.get(f"{API_BASE}/api/daily-quiz/coins/?user_id=test_user_min_coins", timeout=10)
    data = r.json()
    expected = 800  # 1000 - 200
    actual = data.get('total_coins', 0)
    print(f"Expected: {expected}, Actual: {actual}")
    print_result(actual == expected, data)
except Exception as e:
    print(f"❌ ERROR: {e}")

time.sleep(1)

# Test 7: Withdrawal history
print_test(7, "Withdrawal History")
try:
    r = requests.get(f"{API_BASE}/api/wallet/withdrawals/?user_id=test_user_min_coins", timeout=10)
    data = r.json()
    print_result(data.get('success') and len(data.get('withdrawals', [])) > 0, data)
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "="*70)
print("ALL TESTS COMPLETE")
print("="*70)

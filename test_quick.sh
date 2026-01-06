#!/bin/bash

# Quick production test - focused on key validation
set -e

API_URL="http://localhost:8000"

echo "========================================="
echo "🧪 WITHDRAWAL SYSTEM - PRODUCTION TESTS"
echo "========================================="
echo ""

# Test 1: Valid withdrawal
echo "TEST 1: Valid Withdrawal (200 coins)"
echo "--------------------------------------"
curl -s -X POST "${API_URL}/api/wallet/withdraw/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user_min_coins", "upi_id": "test@paytm", "coins": 200}' | python3 -m json.tool
echo ""
echo ""

# Check balance after
echo "Checking balance after withdrawal:"
curl -s -X GET "${API_URL}/api/daily-quiz/coins/?user_id=test_user_min_coins" | python3 -m json.tool
echo ""
echo ""

# Test 2: Below minimum
echo "TEST 2: Below Minimum (should FAIL)"
echo "--------------------------------------"
curl -s -X POST "${API_URL}/api/wallet/withdraw/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user_below_min", "upi_id": "test@paytm", "coins": 150}' | python3 -m json.tool
echo ""
echo ""

# Test 3: Balance check
echo "TEST 3: Balance Check (should FAIL)"
echo "--------------------------------------"
curl -s -X POST "${API_URL}/api/wallet/withdraw/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user_balance_check", "upi_id": "test@paytm", "coins": 300}' | python3 -m json.tool
echo ""
echo ""

# Test 4: Invalid UPI
echo "TEST 4: Invalid UPI (should FAIL)"
echo "--------------------------------------"
curl -s -X POST "${API_URL}/api/wallet/withdraw/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user_valid", "upi_id": "invalidupi", "coins": 200}' | python3 -m json.tool
echo ""
echo ""

# Test 5: Valid large withdrawal
echo "TEST 5: Valid Large Withdrawal (500 coins)"
echo "--------------------------------------"
curl -s -X POST "${API_URL}/api/wallet/withdraw/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user_valid", "upi_id": "test@phonepe", "coins": 500}' | python3 -m json.tool
echo ""
echo ""

# Get withdrawal history
echo "TEST 6: Withdrawal History"
echo "--------------------------------------"
curl -s -X GET "${API_URL}/api/wallet/withdrawals/?user_id=test_user_min_coins" | python3 -m json.tool
echo ""
echo ""

echo "========================================="
echo "✅ TESTS COMPLETE"
echo "========================================="
echo ""
echo "Next: Check Admin Dashboard"
echo "URL: http://localhost:8000/admin/question_solver/coinwithdrawal/"
echo ""

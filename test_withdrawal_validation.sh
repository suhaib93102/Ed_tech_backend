#!/bin/bash

# Withdrawal System Test Script
# Tests all withdrawal validation rules and admin dashboard

echo "🧪 Testing Withdrawal System..."
echo "================================"

# Configuration
API_URL="http://localhost:8000"
USER_ID="test_user_123"
TOKEN="YOUR_AUTH_TOKEN_HERE"

echo ""
echo "📋 Test Cases:"
echo "1. Valid withdrawal (200 coins)"
echo "2. Invalid - below minimum (150 coins)"
echo "3. Invalid - balance too low after withdrawal"
echo "4. Invalid - invalid UPI ID"
echo "5. Valid withdrawal (500 coins)"
echo ""

# Test 1: Valid withdrawal - 200 coins (minimum)
echo "Test 1: Valid withdrawal - 200 coins (minimum)"
echo "----------------------------------------------"
curl -X POST "${API_URL}/api/wallet/withdraw/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "'${USER_ID}'",
    "upi_id": "test@paytm",
    "coins": 200
  }' \
  -w "\n\nStatus: %{http_code}\n\n"

sleep 2

# Test 2: Invalid - below minimum (150 coins)
echo "Test 2: Invalid - below minimum (150 coins)"
echo "--------------------------------------------"
curl -X POST "${API_URL}/api/wallet/withdraw/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "'${USER_ID}'",
    "upi_id": "test@paytm",
    "coins": 150
  }' \
  -w "\n\nStatus: %{http_code}\n\n"

sleep 2

# Test 3: Invalid - balance too low (user has 300, withdraws 250, remaining 50 < 100)
echo "Test 3: Invalid - balance too low after withdrawal"
echo "---------------------------------------------------"
curl -X POST "${API_URL}/api/wallet/withdraw/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "'${USER_ID}'",
    "upi_id": "test@paytm",
    "coins": 250
  }' \
  -w "\n\nStatus: %{http_code}\n\n"

sleep 2

# Test 4: Invalid UPI ID
echo "Test 4: Invalid - invalid UPI ID format"
echo "----------------------------------------"
curl -X POST "${API_URL}/api/wallet/withdraw/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "'${USER_ID}'",
    "upi_id": "invalidupi",
    "coins": 200
  }' \
  -w "\n\nStatus: %{http_code}\n\n"

sleep 2

# Test 5: Valid withdrawal - 500 coins
echo "Test 5: Valid withdrawal - 500 coins"
echo "-------------------------------------"
curl -X POST "${API_URL}/api/wallet/withdraw/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "'${USER_ID}'",
    "upi_id": "user@phonepe",
    "coins": 500
  }' \
  -w "\n\nStatus: %{http_code}\n\n"

sleep 2

# Get withdrawal history
echo "📊 Getting withdrawal history..."
echo "--------------------------------"
curl -X GET "${API_URL}/api/wallet/withdrawals/?user_id=${USER_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -w "\n\nStatus: %{http_code}\n\n"

echo ""
echo "✅ Tests completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Check Django admin dashboard: ${API_URL}/admin/question_solver/coinwithdrawal/"
echo "2. Verify withdrawals appear with UPI IDs"
echo "3. Confirm auto-refresh is working (30s)"
echo "4. Test marking withdrawal as completed"
echo ""
echo "🎯 Admin Dashboard Features to Verify:"
echo "- Live update indicator (🔄 Live Updates 30s)"
echo "- UPI ID display in code format"
echo "- Color-coded status badges"
echo "- Pending withdrawal count"
echo "- Total pending amount"
echo ""

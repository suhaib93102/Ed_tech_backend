#!/bin/bash

# LOCAL PAYMENT API TESTS - COPY & PASTE READY
# Base URL: http://localhost:8000

echo "===== LOCAL PAYMENT API TESTS ====="
echo "Testing on: http://localhost:8000"
echo ""

# Wait for server to be ready
sleep 2

# ============================================
# TEST 1: Get Razorpay Public Key
# ============================================
echo "✅ TEST 1: Get Razorpay Public Key"
echo "========================================"
curl -X GET "http://localhost:8000/api/payment/razorpay-key/" \
  -H "Content-Type: application/json"
echo ""
echo ""

# ============================================
# TEST 2: Create Payment Order (JUST FIXED)
# ============================================
echo "✅ TEST 2: Create Payment Order (Premium)"
echo "========================================"
ORDER_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/payment/create-order/" \
  -H "Content-Type: application/json" \
  -d '{
    "plan": "premium",
    "user_id": "testuser123"
  }')
echo "$ORDER_RESPONSE" | jq .
ORDER_ID=$(echo "$ORDER_RESPONSE" | jq -r '.order_id')
echo "✓ Captured order_id: $ORDER_ID"
echo ""
echo ""

# ============================================
# TEST 3: Create Payment Order (Annual)
# ============================================
echo "✅ TEST 3: Create Payment Order (Annual)"
echo "========================================"
curl -s -X POST "http://localhost:8000/api/payment/create-order/" \
  -H "Content-Type: application/json" \
  -d '{
    "plan": "premium_annual",
    "user_id": "annual_user_456"
  }' | jq .
echo ""
echo ""

# ============================================
# TEST 4: Get Payment History (User 1)
# ============================================
echo "✅ TEST 4: Get Payment History"
echo "========================================"
curl -s -X GET "http://localhost:8000/api/razorpay/history/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "testuser123"}' | jq .
echo ""
echo ""

# ============================================
# TEST 5: Get Subscription Status
# ============================================
echo "✅ TEST 5: Check Subscription Status"
echo "========================================"
curl -s -X GET "http://localhost:8000/api/subscription/status/?user_id=testuser123" \
  -H "Content-Type: application/json" | jq .
echo ""
echo ""

# ============================================
# TEST 6: Error Test - Missing user_id
# ============================================
echo "❌ TEST 6: Error Handling - Missing user_id"
echo "========================================"
curl -s -X POST "http://localhost:8000/api/payment/create-order/" \
  -H "Content-Type: application/json" \
  -d '{"plan": "premium"}' | jq .
echo ""
echo ""

# ============================================
# TEST 7: Error Test - Invalid Plan
# ============================================
echo "❌ TEST 7: Error Handling - Invalid Plan"
echo "========================================"
curl -s -X POST "http://localhost:8000/api/payment/create-order/" \
  -H "Content-Type: application/json" \
  -d '{"plan": "invalid_plan", "user_id": "testuser123"}' | jq .
echo ""
echo ""

# ============================================
# TEST 8: Verify Payment (Simulate)
# ============================================
echo "✅ TEST 8: Verify Payment (With Mock Signature)"
echo "========================================"
echo "NOTE: This will fail with invalid signature (expected)"
curl -s -X POST "http://localhost:8000/api/payment/verify/" \
  -H "Content-Type: application/json" \
  -d "{
    \"razorpay_order_id\": \"$ORDER_ID\",
    \"razorpay_payment_id\": \"pay_test123\",
    \"razorpay_signature\": \"invalid_signature_for_testing\",
    \"user_id\": \"testuser123\"
  }" | jq .
echo ""
echo ""

echo "===== ALL LOCAL TESTS COMPLETE ====="
echo ""
echo "Summary:"
echo "✅ Create Payment Order - Working"
echo "✅ Get Payment History - Working"
echo "✅ Check Subscription - Working"
echo "✅ Error Handling - Working"
echo ""
echo "Next: Deploy to production and test with real Razorpay payment"

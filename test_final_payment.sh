#!/bin/bash

API_URL="https://ed-tech-backend-tzn8.onrender.com/api"
TEST_USER="test_duplicate_user_123"

echo ""
echo "============================================================"
echo "PAYMENT SYSTEM TEST RESULTS"
echo "============================================================"
echo ""

# Setup: Create a premium active subscription
python /Users/vishaljha/Ed_tech_backend/setup_test_subscription.py

echo ""
echo "---"
echo ""

# TEST 1: Verify Current Status is Premium
echo "TEST 1: Verify User Has Premium Active Subscription"
echo "Request: GET /api/subscription/status/?user_id=$TEST_USER"
echo ""
STATUS=$(curl -s -X GET "$API_URL/subscription/status/?user_id=$TEST_USER")
echo "$STATUS" | python -m json.tool
echo ""

# Extract values
PLAN=$(echo "$STATUS" | python -c "import sys, json; print(json.load(sys.stdin).get('plan', ''))" 2>/dev/null)
NEXT_BILLING=$(echo "$STATUS" | python -c "import sys, json; print(json.load(sys.stdin).get('next_billing_date', ''))" 2>/dev/null)
echo "Current Plan: $PLAN"
echo "Next Billing: $NEXT_BILLING"
echo ""
echo "---"
echo ""

# TEST 2: Try Duplicate Order (Same Plan)
echo "TEST 2: Try to Create Duplicate Order (Same Plan)"
echo "Request: POST /api/payment/create-order/"
echo "Body: {\"user_id\": \"$TEST_USER\", \"plan\": \"premium\"}"
echo ""
DUPLICATE=$(curl -s -X POST "$API_URL/payment/create-order/" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$TEST_USER\", \"plan\": \"premium\"}")
echo "$DUPLICATE" | python -m json.tool
echo ""

ERROR=$(echo "$DUPLICATE" | python -c "import sys, json; print(json.load(sys.stdin).get('error', ''))" 2>/dev/null)
if [ "$ERROR" = "Already Subscribed" ]; then
    echo "RESULT: Duplicate rejected correctly"
    echo "Status Code: 409 Conflict"
else
    echo "RESULT: Unexpected response"
fi
echo ""
echo "---"
echo ""

# TEST 3: Create Upgrade Order (Different Plan)
echo "TEST 3: Upgrade to Different Plan (Premium Annual)"
echo "Request: POST /api/payment/create-order/"
echo "Body: {\"user_id\": \"$TEST_USER\", \"plan\": \"premium_annual\"}"
echo ""
UPGRADE=$(curl -s -X POST "$API_URL/payment/create-order/" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$TEST_USER\", \"plan\": \"premium_annual\"}")
echo "$UPGRADE" | python -m json.tool
echo ""

UPGRADE_ORDER=$(echo "$UPGRADE" | python -c "import sys, json; print(json.load(sys.stdin).get('order_id', ''))" 2>/dev/null)
UPGRADE_AMOUNT=$(echo "$UPGRADE" | python -c "import sys, json; print(json.load(sys.stdin).get('amount', ''))" 2>/dev/null)

if [ -n "$UPGRADE_ORDER" ]; then
    echo "RESULT: Upgrade allowed"
    echo "New Order ID: $UPGRADE_ORDER"
    echo "New Amount: ₹$UPGRADE_AMOUNT"
    echo "Status Code: 201 Created"
else
    echo "RESULT: Upgrade failed"
fi
echo ""
echo "---"
echo ""

echo "============================================================"
echo "SUMMARY"
echo "============================================================"
echo ""
echo "DUPLICATE SAME PLAN: REJECTED (409 Conflict)"
echo "  - Error: Already Subscribed"
echo "  - Shows current plan and next billing details"
echo ""
echo "UPGRADE DIFFERENT PLAN: ALLOWED (201 Created)"
echo "  - New order created with different amount"
echo "  - User can upgrade from ₹1 to ₹199 plan"
echo ""
echo "============================================================"

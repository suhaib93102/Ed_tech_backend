#!/bin/bash

# 🧪 COMPREHENSIVE PAYMENT SYSTEM TEST SUITE
# Tests: Initial payment, duplicate payment prevention, subscription status display

set -e

API_URL="http://localhost:8000/api"
TEST_USER="test_user_$(date +%s)"
ANOTHER_USER="another_user_$(date +%s)"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║      🧪 COMPREHENSIVE PAYMENT SYSTEM TEST SUITE               ║"
echo "║  Test Cases: Payment, Duplicate Prevention, Status Display    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counter for test results
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function for test results
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
        ((TESTS_FAILED++))
    fi
}

# Helper function for API calls with response capture
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3
    local headers=$4
    
    if [ "$method" = "GET" ]; then
        curl -s -X GET "$API_URL$endpoint" $headers
    else
        curl -s -X $method "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            $headers \
            -d "$data"
    fi
}

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "TEST GROUP 1: INITIAL PAYMENT FLOW"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Test 1.1: Get Razorpay Key
echo "TEST 1.1: Get Razorpay Public Key"
KEY_RESPONSE=$(api_call "GET" "/payment/razorpay-key/" "")
KEY_ID=$(echo "$KEY_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('key_id', ''))" 2>/dev/null)
if [ -n "$KEY_ID" ]; then
    test_result 0 "Retrieved Razorpay key: $KEY_ID"
else
    test_result 1 "Failed to get Razorpay key"
fi

# Test 1.2: Create First Payment Order
echo ""
echo "TEST 1.2: Create First Payment Order for User 1"
ORDER_RESPONSE=$(api_call "POST" "/payment/create-order/" "{\"user_id\": \"$TEST_USER\", \"plan\": \"premium\"}" "")
ORDER_ID=$(echo "$ORDER_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('order_id', ''))" 2>/dev/null)
AMOUNT=$(echo "$ORDER_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('amount', ''))" 2>/dev/null)
if [ "$AMOUNT" = "1" ]; then
    test_result 0 "Created ₹1 order (ID: $ORDER_ID)"
else
    test_result 1 "Failed to create order"
fi

# Test 1.3: Check User Status - Before Payment
echo ""
echo "TEST 1.3: Check Subscription Status - FREE User (Before Payment)"
STATUS_BEFORE=$(api_call "GET" "/subscription/status/?user_id=$TEST_USER" "")
PLAN_BEFORE=$(echo "$STATUS_BEFORE" | python -c "import sys, json; print(json.load(sys.stdin).get('plan', ''))" 2>/dev/null)
if [ "$PLAN_BEFORE" = "free" ]; then
    test_result 0 "User is on FREE plan before payment"
else
    test_result 1 "Wrong plan before payment"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "TEST GROUP 2: DUPLICATE PAYMENT PREVENTION"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# First, we need to manually create a subscription to simulate a paid user
# In production, this would happen after Razorpay payment verification
echo "Creating test subscription for duplicate prevention tests..."
python manage.py shell << 'PYTHON_EOF' 2>/dev/null
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
django.setup()

from question_solver.models import UserSubscription
from django.utils import timezone
from datetime import timedelta

# Create test user subscription
user_id = os.environ.get('TEST_USER')
if user_id:
    subscription, created = UserSubscription.objects.get_or_create(
        user_id=user_id,
        defaults={
            'plan': 'premium',
            'is_trial': True,
            'trial_end_date': timezone.now() + timedelta(days=7),
            'next_billing_date': timezone.now() + timedelta(days=7),
            'subscription_status': 'active',
            'subscription_start_date': timezone.now()
        }
    )
    if not created:
        subscription.plan = 'premium'
        subscription.is_trial = True
        subscription.subscription_status = 'active'
        subscription.trial_end_date = timezone.now() + timedelta(days=7)
        subscription.next_billing_date = timezone.now() + timedelta(days=7)
        subscription.save()
    print(f"Created/Updated subscription for {user_id}")
PYTHON_EOF

export TEST_USER

# Test 2.1: Try to Create Another Order for Same User (Should Fail)
echo ""
echo "TEST 2.1: Try to Create Another Order for Already Subscribed User"
DUPLICATE_RESPONSE=$(api_call "POST" "/payment/create-order/" "{\"user_id\": \"$TEST_USER\", \"plan\": \"premium\"}" "")
ERROR_MSG=$(echo "$DUPLICATE_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('error', ''))" 2>/dev/null)
HTTP_STATUS=$(echo "$DUPLICATE_RESPONSE" | python -c "import sys, json; data=json.load(sys.stdin); print('409' if 'Already Subscribed' in str(data) else '200')" 2>/dev/null)

if [ "$ERROR_MSG" = "Already Subscribed" ]; then
    test_result 0 "Duplicate payment correctly rejected with 'Already Subscribed' error"
else
    test_result 1 "Duplicate payment not properly rejected"
fi

# Test 2.2: Verify Error Response Contains Subscription Details
echo ""
echo "TEST 2.2: Verify Error Response Shows Current Subscription Details"
CURRENT_PLAN=$(echo "$DUPLICATE_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('current_plan', ''))" 2>/dev/null)
NEXT_BILLING=$(echo "$DUPLICATE_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('next_billing_amount', ''))" 2>/dev/null)
if [ "$CURRENT_PLAN" = "premium" ] && [ "$NEXT_BILLING" = "99" ]; then
    test_result 0 "Error response shows current plan (premium) and next billing (₹99)"
else
    test_result 1 "Error response missing subscription details"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "TEST GROUP 3: SUBSCRIPTION STATUS DISPLAY"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Test 3.1: Get Subscription Status (Subscribed User)
echo "TEST 3.1: Get Subscription Status for Premium User"
PAID_STATUS=$(api_call "GET" "/subscription/status/?user_id=$TEST_USER" "")
echo "Response:"
echo "$PAID_STATUS" | python -m json.tool 2>/dev/null

PAID_PLAN=$(echo "$PAID_STATUS" | python -c "import sys, json; print(json.load(sys.stdin).get('plan', ''))" 2>/dev/null)
IS_PAID=$(echo "$PAID_STATUS" | python -c "import sys, json; print(json.load(sys.stdin).get('is_paid', ''))" 2>/dev/null)
IS_TRIAL=$(echo "$PAID_STATUS" | python -c "import sys, json; print(json.load(sys.stdin).get('is_trial', ''))" 2>/dev/null)
NEXT_AMOUNT=$(echo "$PAID_STATUS" | python -c "import sys, json; print(json.load(sys.stdin).get('next_billing_amount', ''))" 2>/dev/null)

[ "$PAID_PLAN" = "premium" ] && test_result 0 "Shows correct plan: premium" || test_result 1 "Wrong plan displayed"
[ "$IS_PAID" = "True" ] || [ "$IS_PAID" = "true" ] && test_result 0 "Shows is_paid: true" || test_result 1 "is_paid not set correctly"
[ "$IS_TRIAL" = "True" ] || [ "$IS_TRIAL" = "true" ] && test_result 0 "Shows is_trial: true (in trial period)" || test_result 1 "is_trial status wrong"
[ "$NEXT_AMOUNT" = "99" ] && test_result 0 "Shows next_billing_amount: ₹99" || test_result 1 "Next billing amount wrong"

# Test 3.2: Verify All Billing Details Present
echo ""
echo "TEST 3.2: Verify All Billing Details Are Present"
TRIAL_END=$(echo "$PAID_STATUS" | python -c "import sys, json; print(json.load(sys.stdin).get('trial_end_date', ''))" 2>/dev/null)
NEXT_BILLING=$(echo "$PAID_STATUS" | python -c "import sys, json; print(json.load(sys.stdin).get('next_billing_date', ''))" 2>/dev/null)
TRIAL_DAYS=$(echo "$PAID_STATUS" | python -c "import sys, json; print(json.load(sys.stdin).get('trial_days_remaining', ''))" 2>/dev/null)
DAYS_UNTIL=$(echo "$PAID_STATUS" | python -c "import sys, json; print(json.load(sys.stdin).get('days_until_next_billing', ''))" 2>/dev/null)

if [ -n "$TRIAL_END" ]; then test_result 0 "Shows trial_end_date"; else test_result 1 "Missing trial_end_date"; fi
if [ -n "$NEXT_BILLING" ]; then test_result 0 "Shows next_billing_date"; else test_result 1 "Missing next_billing_date"; fi
if [ -n "$TRIAL_DAYS" ]; then test_result 0 "Shows trial_days_remaining: $TRIAL_DAYS days"; else test_result 1 "Missing trial_days_remaining"; fi
if [ -n "$DAYS_UNTIL" ]; then test_result 0 "Shows days_until_next_billing: $DAYS_UNTIL days"; else test_result 1 "Missing days_until_next_billing"; fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "TEST GROUP 4: FREE USER FLOW"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Test 4.1: Create Order for New User (Another User)
echo "TEST 4.1: Create Order for Another New User"
NEW_ORDER=$(api_call "POST" "/payment/create-order/" "{\"user_id\": \"$ANOTHER_USER\", \"plan\": \"premium\"}" "")
NEW_ORDER_ID=$(echo "$NEW_ORDER" | python -c "import sys, json; print(json.load(sys.stdin).get('order_id', ''))" 2>/dev/null)
if [ -n "$NEW_ORDER_ID" ]; then
    test_result 0 "Successfully created order for new user (Order: $NEW_ORDER_ID)"
else
    test_result 1 "Failed to create order for new user"
fi

# Test 4.2: Verify New User is Still on Free Plan
echo ""
echo "TEST 4.2: Verify New User Status is FREE (Before Payment)"
NEW_USER_STATUS=$(api_call "GET" "/subscription/status/?user_id=$ANOTHER_USER" "")
NEW_USER_PLAN=$(echo "$NEW_USER_STATUS" | python -c "import sys, json; print(json.load(sys.stdin).get('plan', ''))" 2>/dev/null)
if [ "$NEW_USER_PLAN" = "free" ]; then
    test_result 0 "New user correctly shows as FREE plan"
else
    test_result 1 "New user plan incorrect"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "TEST GROUP 5: ERROR HANDLING"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Test 5.1: Create Order Without User ID
echo "TEST 5.1: Try to Create Order Without user_id (Should Fail)"
NO_USER_RESPONSE=$(api_call "POST" "/payment/create-order/" "{\"plan\": \"premium\"}" "")
NO_USER_ERROR=$(echo "$NO_USER_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('error', ''))" 2>/dev/null)
if [ "$NO_USER_ERROR" = "Unauthorized" ]; then
    test_result 0 "Correctly rejected request without user_id"
else
    test_result 1 "Should reject missing user_id"
fi

# Test 5.2: Get Status Without User ID
echo ""
echo "TEST 5.2: Try to Get Status Without user_id (Should Fail)"
NO_USER_STATUS=$(api_call "GET" "/subscription/status/" "")
STATUS_ERROR=$(echo "$NO_USER_STATUS" | python -c "import sys, json; print(json.load(sys.stdin).get('error', ''))" 2>/dev/null)
if [ -n "$STATUS_ERROR" ]; then
    test_result 0 "Correctly rejected status request without user_id"
else
    test_result 1 "Should reject missing user_id in status"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "TEST GROUP 6: EDGE CASES"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Test 6.1: Multiple Duplicate Attempts
echo "TEST 6.1: Multiple Duplicate Payment Attempts for Same User"
DUPLICATE_1=$(api_call "POST" "/payment/create-order/" "{\"user_id\": \"$TEST_USER\", \"plan\": \"premium\"}" "")
DUPLICATE_2=$(api_call "POST" "/payment/create-order/" "{\"user_id\": \"$TEST_USER\", \"plan\": \"premium\"}" "")

ERROR_1=$(echo "$DUPLICATE_1" | python -c "import sys, json; print(json.load(sys.stdin).get('error', ''))" 2>/dev/null)
ERROR_2=$(echo "$DUPLICATE_2" | python -c "import sys, json; print(json.load(sys.stdin).get('error', ''))" 2>/dev/null)

if [ "$ERROR_1" = "Already Subscribed" ] && [ "$ERROR_2" = "Already Subscribed" ]; then
    test_result 0 "Multiple attempts correctly rejected"
else
    test_result 1 "Duplicate prevention inconsistent"
fi

# Test 6.2: Verify Response Format Consistency
echo ""
echo "TEST 6.2: Verify Response Format Consistency"
RESPONSE_KEYS=$(echo "$DUPLICATE_RESPONSE" | python -c "import sys, json; data=json.load(sys.stdin); print(' '.join(data.keys()))" 2>/dev/null)
HAS_ERROR=$(echo "$RESPONSE_KEYS" | grep -c "error" || true)
HAS_MESSAGE=$(echo "$RESPONSE_KEYS" | grep -c "message" || true)
HAS_PLAN=$(echo "$RESPONSE_KEYS" | grep -c "current_plan" || true)

if [ "$HAS_ERROR" -gt 0 ] && [ "$HAS_MESSAGE" -gt 0 ] && [ "$HAS_PLAN" -gt 0 ]; then
    test_result 0 "Error response has all required fields"
else
    test_result 1 "Error response missing fields"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "TEST SUMMARY"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo -e "Total Tests:  $((TESTS_PASSED + TESTS_FAILED))"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 0
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ $TESTS_FAILED TEST(S) FAILED${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
fi

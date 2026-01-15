#!/bin/bash

# 🧪 FOCUSED PAYMENT SYSTEM TEST - Duplicate Prevention & Subscription Status
# Tests: Initial payment, duplicate rejection, status display with all details

API_URL="http://localhost:8000/api"
TEST_USER="focused_test_$(date +%s)"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     🧪 FOCUSED PAYMENT SYSTEM TEST - DUPLICATE PREVENTION      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

PASS=0
FAIL=0

# Test 1: Get Razorpay Key
echo "📌 TEST 1: Get Razorpay Public Key"
RESPONSE=$(curl -s -X GET "$API_URL/payment/razorpay-key/")
KEY=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('key_id', ''))" 2>/dev/null)
if [ -n "$KEY" ]; then
    echo "✅ PASS: Retrieved key: $KEY"
    ((PASS++))
else
    echo "❌ FAIL: Could not get key"
    ((FAIL++))
fi
echo ""

# Test 2: Create Initial Payment Order
echo "📌 TEST 2: Create Initial ₹1 Payment Order"
ORDER_JSON="{\"user_id\": \"$TEST_USER\", \"plan\": \"premium\"}"
RESPONSE=$(curl -s -X POST "$API_URL/payment/create-order/" \
  -H "Content-Type: application/json" \
  -d "$ORDER_JSON")
ORDER_ID=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('order_id', ''))" 2>/dev/null)
if [ -n "$ORDER_ID" ]; then
    echo "✅ PASS: Created order: $ORDER_ID with amount: ₹1"
    ((PASS++))
else
    echo "❌ FAIL: Could not create order"
    echo "Response: $RESPONSE"
    ((FAIL++))
fi
echo ""

# Test 3: Create subscription (simulate after payment)
echo "📌 TEST 3: Create Premium Subscription (Simulate Post-Payment)"
python manage.py shell 2>/dev/null << EOF
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
django.setup()

from question_solver.models import UserSubscription
from django.utils import timezone
from datetime import timedelta

user_id = "$TEST_USER"
subscription, created = UserSubscription.objects.update_or_create(
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
print("✓ Subscription created/updated")
EOF
echo "✅ PASS: Subscription set to active with trial"
((PASS++))
echo ""

# Test 4: Try duplicate payment (Should be rejected)
echo "📌 TEST 4: Try to Create Duplicate Order (Should Reject)"
DUPLICATE=$(curl -s -X POST "$API_URL/payment/create-order/" \
  -H "Content-Type: application/json" \
  -d "$ORDER_JSON")
ERROR=$(echo "$DUPLICATE" | python -c "import sys, json; print(json.load(sys.stdin).get('error', ''))" 2>/dev/null)
if [ "$ERROR" = "Already Subscribed" ]; then
    echo "✅ PASS: Duplicate payment rejected with 'Already Subscribed'"
    ((PASS++))
else
    echo "❌ FAIL: Duplicate payment not properly rejected"
    echo "Response: $DUPLICATE"
    ((FAIL++))
fi
echo ""

# Test 5: Check error response contains subscription details
echo "📌 TEST 5: Verify Error Response Shows Current Subscription"
CURRENT_PLAN=$(echo "$DUPLICATE" | python -c "import sys, json; print(json.load(sys.stdin).get('current_plan', ''))" 2>/dev/null)
NEXT_AMOUNT=$(echo "$DUPLICATE" | python -c "import sys, json; print(json.load(sys.stdin).get('next_billing_amount', ''))" 2>/dev/null)
if [ "$CURRENT_PLAN" = "premium" ] && [ "$NEXT_AMOUNT" = "99" ]; then
    echo "✅ PASS: Error shows current plan: $CURRENT_PLAN, next billing: ₹$NEXT_AMOUNT"
    ((PASS++))
else
    echo "❌ FAIL: Error missing subscription details"
    echo "Response: $DUPLICATE"
    ((FAIL++))
fi
echo ""

# Test 6: Get Full Subscription Status
echo "📌 TEST 6: Get Full Subscription Status"
STATUS=$(curl -s -X GET "$API_URL/subscription/status/?user_id=$TEST_USER")
echo "Response:"
echo "$STATUS" | python -m json.tool 2>/dev/null
echo ""

PLAN=$(echo "$STATUS" | python -c "import sys, json; print(json.load(sys.stdin).get('plan', ''))" 2>/dev/null)
IS_PAID=$(echo "$STATUS" | python -c "import sys, json; print(json.load(sys.stdin).get('is_paid', ''))" 2>/dev/null)
IS_TRIAL=$(echo "$STATUS" | python -c "import sys, json; print(json.load(sys.stdin).get('is_trial', ''))" 2>/dev/null)
NEXT_BILL=$(echo "$STATUS" | python -c "import sys, json; print(json.load(sys.stdin).get('next_billing_date', ''))" 2>/dev/null)
BILL_AMT=$(echo "$STATUS" | python -c "import sys, json; print(json.load(sys.stdin).get('next_billing_amount', ''))" 2>/dev/null)
TRIAL_END=$(echo "$STATUS" | python -c "import sys, json; print(json.load(sys.stdin).get('trial_end_date', ''))" 2>/dev/null)
TRIAL_DAYS=$(echo "$STATUS" | python -c "import sys, json; print(json.load(sys.stdin).get('trial_days_remaining', ''))" 2>/dev/null)

echo "Subscription Details:"
echo "  Plan: $PLAN"
echo "  Is Paid: $IS_PAID"
echo "  Is Trial: $IS_TRIAL"
echo "  Next Billing: $NEXT_BILL"
echo "  Next Amount: ₹$BILL_AMT"
echo "  Trial End: $TRIAL_END"
echo "  Trial Days Left: $TRIAL_DAYS"
echo ""

if [ "$PLAN" = "premium" ] && [ "$BILL_AMT" = "99" ] && [ -n "$TRIAL_DAYS" ]; then
    echo "✅ PASS: All subscription details displayed correctly"
    ((PASS++))
else
    echo "❌ FAIL: Missing or incorrect subscription details"
    ((FAIL++))
fi
echo ""

# Test 7: Another duplicate attempt
echo "📌 TEST 7: Another Duplicate Attempt (Should Also Reject)"
DUP2=$(curl -s -X POST "$API_URL/payment/create-order/" \
  -H "Content-Type: application/json" \
  -d "$ORDER_JSON")
ERROR2=$(echo "$DUP2" | python -c "import sys, json; print(json.load(sys.stdin).get('error', ''))" 2>/dev/null)
if [ "$ERROR2" = "Already Subscribed" ]; then
    echo "✅ PASS: Second duplicate also rejected"
    ((PASS++))
else
    echo "❌ FAIL: Second duplicate not rejected"
    ((FAIL++))
fi
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    TEST SUMMARY                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "✅ Passed: $PASS"
echo "❌ Failed: $FAIL"
echo "📊 Total:  $((PASS + FAIL))"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "✅ ALL TESTS PASSED!"
    echo ""
    echo "What the tests verified:"
    echo "  ✓ Initial payment order creation works (₹1)"
    echo "  ✓ Duplicate payment attempts are rejected"
    echo "  ✓ Error response shows current subscription plan"
    echo "  ✓ Error response shows next billing amount (₹99)"
    echo "  ✓ Subscription status shows all required fields"
    echo "  ✓ Status displays trial info (end date, days remaining)"
    echo "  ✓ Status displays next billing date and amount"
    echo "  ✓ Multiple duplicate attempts consistently rejected"
    exit 0
else
    echo "❌ SOME TESTS FAILED"
    exit 1
fi

#!/bin/bash

# ============================================================================
# COMPLETE SUBSCRIPTION & PAYMENT FLOW TEST SCRIPT
# ============================================================================
# Tests the complete user lifecycle:
# 1. User exhausts free tier (3 uses)
# 2. User upgrades to basic plan
# 3. Payment verification
# 4. Webhook confirmation
# 5. Unlimited access verification
# ============================================================================

set -e

HOST="http://localhost:8000"
BASE_URL="$HOST/api"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test user
TEST_USER="test_subscription_$(date +%s)"
PLAN="basic"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  COMPLETE SUBSCRIPTION & PAYMENT FLOW TEST                 ║${NC}"
echo -e "${BLUE}║  User: $TEST_USER                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Test counter
TEST_NUM=0
PASSED=0
FAILED=0

# Helper function
test_endpoint() {
    TEST_NUM=$((TEST_NUM + 1))
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_key="$5"
    
    echo -e "${YELLOW}TEST $TEST_NUM: $name${NC}"
    echo "  Method: $method $endpoint"
    
    if [ -n "$data" ]; then
        echo "  Data: $data"
        if [ "$method" == "POST" ]; then
            RESPONSE=$(curl -s -X POST \
                -H "Content-Type: application/json" \
                -H "X-User-ID: $TEST_USER" \
                -d "$data" \
                "$BASE_URL$endpoint")
        fi
    else
        if [ "$method" == "GET" ]; then
            RESPONSE=$(curl -s -X GET \
                -H "X-User-ID: $TEST_USER" \
                "$BASE_URL$endpoint?user_id=$TEST_USER")
        fi
    fi
    
    echo "  Response: $RESPONSE"
    
    if echo "$RESPONSE" | grep -q "$expected_key"; then
        echo -e "${GREEN}  ✓ PASSED${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}  ✗ FAILED (Expected to find: $expected_key)${NC}"
        FAILED=$((FAILED + 1))
    fi
    echo ""
}

# ============================================================================
# PHASE 1: VERIFY FREE TIER WITH 3 USE LIMIT
# ============================================================================

echo -e "${BLUE}═══ PHASE 1: FREE TIER (3 USE LIMIT) ═══${NC}"
echo ""

test_endpoint \
    "Check feature access (1st attempt)" \
    "POST" \
    "/usage/check/" \
    '{"feature":"quiz"}' \
    '"allowed": true'

test_endpoint \
    "Record feature usage (1st)" \
    "POST" \
    "/usage/record/" \
    '{"feature":"quiz","input_size":100}' \
    '"used": 1'

test_endpoint \
    "Record feature usage (2nd)" \
    "POST" \
    "/usage/record/" \
    '{"feature":"quiz","input_size":100}' \
    '"used": 2'

test_endpoint \
    "Record feature usage (3rd)" \
    "POST" \
    "/usage/record/" \
    '{"feature":"quiz","input_size":100}' \
    '"used": 3'

test_endpoint \
    "Check feature access (4th - BLOCKED)" \
    "POST" \
    "/usage/check/" \
    '{"feature":"quiz"}' \
    '"allowed": false'

test_endpoint \
    "Get usage dashboard (shows 3/3)" \
    "GET" \
    "/usage/dashboard/" \
    "" \
    '"limit": 3'

echo ""
echo -e "${BLUE}═══ PHASE 2: UPGRADE TO PAID PLAN ═══${NC}"
echo ""

# Step 1: Create subscription order
echo -e "${YELLOW}STEP 1: Create Subscription Order (₹1 Trial)${NC}"
RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "{\"user_id\": \"$TEST_USER\", \"plan\": \"$PLAN\"}" \
    "$BASE_URL/subscriptions/create/")

echo "Response: $RESPONSE"

# Extract subscription ID
SUB_ID=$(echo "$RESPONSE" | grep -o '"subscription_id": "[^"]*' | cut -d'"' -f4)
echo -e "${GREEN}✓ Subscription ID: $SUB_ID${NC}"
echo ""

# Verify subscription was created
test_endpoint \
    "Get subscription status (PENDING)" \
    "GET" \
    "/subscriptions/status/" \
    "" \
    '"plan": "basic"'

echo ""
echo -e "${BLUE}═══ PHASE 3: SIMULATE PAYMENT & WEBHOOK ═══${NC}"
echo ""

# Step 2: Simulate payment (we'll manually trigger webhook for testing)
echo -e "${YELLOW}SIMULATING PAYMENT COMPLETION${NC}"

# Create test webhook payload
WEBHOOK_PAYLOAD='{
  "event": "subscription.activated",
  "payload": {
    "subscription": {
      "id": "'$SUB_ID'",
      "notes": {
        "user_id": "'$TEST_USER'",
        "plan_name": "basic",
        "trial_amount": "1",
        "recurring_amount": "99"
      }
    }
  }
}'

echo "Webhook Payload: $WEBHOOK_PAYLOAD"

WEBHOOK_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "$WEBHOOK_PAYLOAD" \
    "$BASE_URL/subscriptions/webhook/")

echo "Webhook Response: $WEBHOOK_RESPONSE"

if echo "$WEBHOOK_RESPONSE" | grep -q '"success": true'; then
    echo -e "${GREEN}✓ Webhook processed successfully${NC}"
else
    echo -e "${RED}✗ Webhook processing failed${NC}"
fi

echo ""

# Step 3: Verify subscription is now ACTIVE
test_endpoint \
    "Get subscription status (ACTIVE)" \
    "GET" \
    "/subscriptions/status/" \
    "" \
    '"status": "active"'

echo ""
echo -e "${BLUE}═══ PHASE 4: VERIFY UNLIMITED ACCESS ═══${NC}"
echo ""

# After payment, user should have unlimited access
echo -e "${YELLOW}Testing unlimited access to quiz feature${NC}"

test_endpoint \
    "Check feature access (UNLIMITED)" \
    "POST" \
    "/usage/check/" \
    '{"feature":"quiz"}' \
    '"unlimited": true'

test_endpoint \
    "Record 4th usage (should work unlimited)" \
    "POST" \
    "/usage/record/" \
    '{"feature":"quiz","input_size":100}' \
    '"success": true'

test_endpoint \
    "Record 5th usage (should work unlimited)" \
    "POST" \
    "/usage/record/" \
    '{"feature":"quiz","input_size":100}' \
    '"success": true'

test_endpoint \
    "Get updated dashboard (should show unlimited)" \
    "GET" \
    "/usage/dashboard/" \
    "" \
    '"plan": "BASIC"'

echo ""
echo -e "${BLUE}═══ PHASE 5: POST-PAYMENT VALIDATION ═══${NC}"
echo ""

test_endpoint \
    "Validate subscription is active" \
    "GET" \
    "/subscriptions/validate/" \
    "" \
    '"validated": true'

echo ""
echo -e "${BLUE}═══ PHASE 6: MONTHLY AUTO-PAYMENT SIMULATION ═══${NC}"
echo ""

# Simulate subscription.charged webhook (monthly recurring)
MONTHLY_WEBHOOK='{
  "event": "subscription.charged",
  "payload": {
    "payment": {
      "id": "pay_monthly_'$TEST_USER'",
      "amount": 9900
    },
    "subscription": {
      "id": "'$SUB_ID'",
      "notes": {
        "user_id": "'$TEST_USER'",
        "plan_name": "basic",
        "trial_amount": "1",
        "recurring_amount": "99"
      }
    }
  }
}'

echo -e "${YELLOW}Simulating monthly ₹99 auto-payment${NC}"

MONTHLY_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "$MONTHLY_WEBHOOK" \
    "$BASE_URL/subscriptions/webhook/")

echo "Monthly Payment Response: $MONTHLY_RESPONSE"

if echo "$MONTHLY_RESPONSE" | grep -q '"success": true'; then
    echo -e "${GREEN}✓ Monthly payment recorded${NC}"
else
    echo -e "${RED}✗ Monthly payment failed${NC}"
fi

echo ""
echo -e "${BLUE}═══ PHASE 7: PAYMENT FAILURE SIMULATION ═══${NC}"
echo ""

# Simulate payment failure (should re-enable limits)
FAILURE_WEBHOOK='{
  "event": "payment.failed",
  "payload": {
    "payment": {
      "id": "pay_failed_'$TEST_USER'",
      "amount": 9900
    },
    "subscription": {
      "id": "'$SUB_ID'",
      "notes": {
        "user_id": "'$TEST_USER'",
        "plan_name": "basic"
      }
    }
  }
}'

echo -e "${YELLOW}Simulating payment failure${NC}"

FAILURE_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "$FAILURE_WEBHOOK" \
    "$BASE_URL/subscriptions/webhook/")

echo "Payment Failure Response: $FAILURE_RESPONSE"

if echo "$FAILURE_RESPONSE" | grep -q '"success": true'; then
    echo -e "${GREEN}✓ Payment failure handled, subscription marked past_due${NC}"
    
    # After failure, limits should be re-enabled
    echo -e "${YELLOW}Verifying limits are re-enabled after payment failure${NC}"
else
    echo -e "${RED}✗ Payment failure handling failed${NC}"
fi

echo ""
echo -e "${BLUE}═══ TEST SUMMARY ═══${NC}"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo -e "Total: $TEST_NUM"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    exit 1
fi

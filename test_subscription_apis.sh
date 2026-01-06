#!/bin/bash
# Test Script for Premium Subscription APIs
# Run this script to test all subscription endpoints

API_URL="http://127.0.0.1:8003/api"
USER_ID="test_user_$(date +%s)"

echo "🚀 Testing Premium Subscription APIs"
echo "===================================="
echo ""
echo "Using User ID: $USER_ID"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test 1: Get Available Plans
echo -e "${BLUE}Test 1: Get Available Plans${NC}"
echo "GET $API_URL/subscription/plans/"
curl -s "$API_URL/subscription/plans/" | python3 -m json.tool
echo ""
echo ""

# Test 2: Check Subscription Status (New User - Free Plan)
echo -e "${BLUE}Test 2: Check Subscription Status (Free Plan)${NC}"
echo "GET $API_URL/subscription/status/?user_id=$USER_ID"
curl -s "$API_URL/subscription/status/?user_id=$USER_ID" | python3 -m json.tool
echo ""
echo ""

# Test 3: Check Feature Access
echo -e "${BLUE}Test 3: Check Feature Access (Quiz)${NC}"
echo "GET $API_URL/subscription/feature-access/?user_id=$USER_ID&feature=quiz"
curl -s "$API_URL/subscription/feature-access/?user_id=$USER_ID&feature=quiz" | python3 -m json.tool
echo ""
echo ""

# Test 4: Create Subscription Order (Razorpay)
echo -e "${BLUE}Test 4: Create Subscription Order${NC}"
echo "POST $API_URL/subscription/create-order/"
ORDER_RESPONSE=$(curl -s -X POST "$API_URL/subscription/create-order/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "'$USER_ID'",
    "plan_name": "premium"
  }')
echo "$ORDER_RESPONSE" | python3 -m json.tool
echo ""

# Extract order_id from response
ORDER_ID=$(echo "$ORDER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('order_id', ''))" 2>/dev/null)

if [ -n "$ORDER_ID" ]; then
  echo -e "${GREEN}✓ Order created successfully: $ORDER_ID${NC}"
else
  echo -e "${RED}✗ Failed to create order${NC}"
fi
echo ""
echo ""

# Test 5: Test Feature Usage Limit (Free User)
echo -e "${BLUE}Test 5: Test Feature Usage Limits${NC}"
echo "Simulating 4 quiz uses (should fail on 4th)"
for i in {1..4}; do
  echo "Attempt $i:"
  curl -s -X POST "$API_URL/subscription/log-usage/" \
    -H "Content-Type: application/json" \
    -d '{
      "user_id": "'$USER_ID'",
      "feature": "quiz",
      "type": "text",
      "input_size": 100
    }' | python3 -m json.tool
  echo ""
done
echo ""

# Test 6: Check Updated Subscription Status
echo -e "${BLUE}Test 6: Check Updated Status After Usage${NC}"
curl -s "$API_URL/subscription/status/?user_id=$USER_ID" | python3 -m json.tool
echo ""
echo ""

# Test 7: Try to Access Feature Beyond Limit
echo -e "${BLUE}Test 7: Try Quiz Feature (Should be blocked)${NC}"
echo "GET $API_URL/subscription/feature-access/?user_id=$USER_ID&feature=quiz"
curl -s "$API_URL/subscription/feature-access/?user_id=$USER_ID&feature=quiz" | python3 -m json.tool
echo ""
echo ""

# Test 8: Billing History
echo -e "${BLUE}Test 8: Get Billing History${NC}"
echo "GET $API_URL/subscription/billing-history/?user_id=$USER_ID"
curl -s "$API_URL/subscription/billing-history/?user_id=$USER_ID" | python3 -m json.tool
echo ""
echo ""

# Summary
echo "===================================="
echo -e "${GREEN}✓ All API tests completed!${NC}"
echo ""
echo "Next Steps:"
echo "1. Open Razorpay Dashboard to verify order creation"
echo "2. Test payment flow with Razorpay test cards"
echo "3. Verify payment with POST /api/subscription/verify-payment/"
echo "4. Check premium features are unlocked"
echo ""
echo "Test Cards: https://razorpay.com/docs/payments/payments/test-card-details/"
echo ""

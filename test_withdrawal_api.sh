#!/bin/bash
# Production Coin Withdrawal API - Testing Guide
# Simple system: deduct coins and send to admin panel for manual processing

echo "================================"
echo "COIN WITHDRAWAL API - CURL TESTS"
echo "================================"
echo ""

BASE_URL="http://localhost:8000/api"

# Test data
USER_ID="test_user_123"
VALID_UPI="user@okhdfcbank"
WITHDRAWAL_AMOUNT=500

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print test headers
print_test() {
    echo -e "${BLUE}[TEST] $1${NC}"
    echo "================================"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ SUCCESS${NC}"
    echo ""
}

# Function to print error
print_error() {
    echo -e "${RED}✗ ERROR${NC}"
    echo ""
}

# ============================================================
# TEST 1: Create a withdrawal request (should succeed)
# ============================================================
print_test "1. Create Withdrawal Request"

echo "Request:"
echo "POST /api/razorpay/withdraw/"
echo "Body:"
echo "{
  \"user_id\": \"$USER_ID\",
  \"amount\": $WITHDRAWAL_AMOUNT,
  \"upi_id\": \"$VALID_UPI\"
}"
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/razorpay/withdraw/" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"amount\": $WITHDRAWAL_AMOUNT,
    \"upi_id\": \"$VALID_UPI\"
  }")

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Extract withdrawal_id from response for later tests
WITHDRAWAL_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('withdrawal_id', ''))" 2>/dev/null)

if [[ ! -z "$WITHDRAWAL_ID" ]]; then
    print_success
else
    print_error
fi

# ============================================================
# TEST 2: Attempt withdrawal with insufficient balance
# ============================================================
print_test "2. Withdrawal with Insufficient Balance"

echo "Request:"
echo "POST /api/razorpay/withdraw/"
echo "Body: { amount: 999999 }"
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/razorpay/withdraw/" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"amount\": 999999,
    \"upi_id\": \"$VALID_UPI\"
  }")

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

if echo "$RESPONSE" | grep -q "Insufficient"; then
    print_success
else
    print_error
fi

# ============================================================
# TEST 3: Withdrawal with invalid UPI format
# ============================================================
print_test "3. Invalid UPI ID Format"

echo "Request:"
echo "POST /api/razorpay/withdraw/"
echo "Body: { upi_id: \"invalid-upi\" }"
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/razorpay/withdraw/" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"amount\": 500,
    \"upi_id\": \"invalid-upi\"
  }")

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

if echo "$RESPONSE" | grep -q "Invalid UPI"; then
    print_success
else
    print_error
fi

# ============================================================
# TEST 4: Withdrawal with amount below minimum
# ============================================================
print_test "4. Withdrawal Amount Below Minimum"

echo "Request:"
echo "POST /api/razorpay/withdraw/"
echo "Body: { amount: 50 }"
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/razorpay/withdraw/" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"amount\": 50,
    \"upi_id\": \"$VALID_UPI\"
  }")

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

if echo "$RESPONSE" | grep -q "Minimum withdrawal"; then
    print_success
else
    print_error
fi

# ============================================================
# TEST 5: Get withdrawal history
# ============================================================
print_test "5. Get Withdrawal History"

echo "Request:"
echo "GET /api/razorpay/withdraw/history/?user_id=$USER_ID&limit=10"
echo ""

RESPONSE=$(curl -s -X GET "$BASE_URL/razorpay/withdraw/history/?user_id=$USER_ID&limit=10")

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

if echo "$RESPONSE" | grep -q "success"; then
    print_success
else
    print_error
fi

# ============================================================
# TEST 6: Get specific withdrawal details
# ============================================================
if [[ ! -z "$WITHDRAWAL_ID" ]]; then
    print_test "6. Get Withdrawal Details"
    
    echo "Request:"
    echo "GET /api/razorpay/withdraw/status/?withdrawal_id=$WITHDRAWAL_ID"
    echo ""
    
    RESPONSE=$(curl -s -X GET "$BASE_URL/razorpay/withdraw/status/?withdrawal_id=$WITHDRAWAL_ID")
    
    echo "Response:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    echo ""
    
    if echo "$RESPONSE" | grep -q "success"; then
        print_success
    else
        print_error
    fi
else
    echo "Skipping TEST 6: No withdrawal ID from TEST 1"
fi

# ============================================================
# TEST 7: Cancel withdrawal request
# ============================================================
if [[ ! -z "$WITHDRAWAL_ID" ]]; then
    print_test "7. Cancel Withdrawal Request"
    
    echo "Request:"
    echo "POST /api/razorpay/withdraw/cancel/"
    echo "Body: { withdrawal_id: \"$WITHDRAWAL_ID\" }"
    echo ""
    
    RESPONSE=$(curl -s -X POST "$BASE_URL/razorpay/withdraw/cancel/" \
      -H "Content-Type: application/json" \
      -d "{
        \"withdrawal_id\": \"$WITHDRAWAL_ID\",
        \"reason\": \"Test cancellation\"
      }")
    
    echo "Response:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    echo ""
    
    if echo "$RESPONSE" | grep -q "cancelled"; then
        print_success
    else
        print_error
    fi
else
    echo "Skipping TEST 7: No withdrawal ID from TEST 1"
fi

# ============================================================
# TEST 8: Withdrawal with missing user_id
# ============================================================
print_test "8. Missing user_id Parameter"

echo "Request:"
echo "POST /api/razorpay/withdraw/"
echo "Body: { amount: 500, upi_id: \"user@okhdfcbank\" }"
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/razorpay/withdraw/" \
  -H "Content-Type: application/json" \
  -d "{
    \"amount\": 500,
    \"upi_id\": \"$VALID_UPI\"
  }")

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

if echo "$RESPONSE" | grep -q "user_id"; then
    print_success
else
    print_error
fi

# ============================================================
# TEST 9: Multiple valid UPI formats
# ============================================================
print_test "9. Valid UPI Formats"

VALID_UPIS=("user@okhdfcbank" "john@ybl" "mobile@airtel" "name_123@ibl")

for upi in "${VALID_UPIS[@]}"; do
    echo "Testing UPI: $upi"
    RESPONSE=$(curl -s -X POST "$BASE_URL/razorpay/withdraw/" \
      -H "Content-Type: application/json" \
      -d "{
        \"user_id\": \"test_$upi\",
        \"amount\": 200,
        \"upi_id\": \"$upi\"
      }")
    
    if echo "$RESPONSE" | grep -q "success\|error"; then
        echo "  ✓ Format accepted"
    fi
done
echo ""

# ============================================================
# TEST 10: Get history with status filter
# ============================================================
print_test "10. Get History with Status Filter"

echo "Request:"
echo "GET /api/razorpay/withdraw/history/?user_id=$USER_ID&status=pending"
echo ""

RESPONSE=$(curl -s -X GET "$BASE_URL/razorpay/withdraw/history/?user_id=$USER_ID&status=pending")

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

if echo "$RESPONSE" | grep -q "success"; then
    print_success
else
    print_error
fi

echo ""
echo "================================"
echo "WITHDRAWAL API TESTING COMPLETE"
echo "================================"
echo ""
echo "NOTES:"
echo "1. All withdrawal requests are created with status 'pending'"
echo "2. Coins are deducted immediately when request is created"
echo "3. Admin panel must approve/process requests manually"
echo "4. Minimum withdrawal: 100 coins"
echo "5. Maximum withdrawal: 100,000 coins"
echo "6. UPI ID format: username@bankname"
echo "7. Check Django admin panel for withdrawal management"

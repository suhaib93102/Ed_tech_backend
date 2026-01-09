#!/bin/bash

# Test script for multiple daily quiz attempts
# This script tests that users can attempt the daily quiz multiple times per day
# and that coins accumulate properly

API_BASE_URL="https://ed-tech-backend-tzn8.onrender.com"
TEST_USER="test_multiple_attempts_$(date +%s)"

echo "🧪 Testing Multiple Daily Quiz Attempts"
echo "========================================"
echo "Test User: $TEST_USER"
echo ""

# Function to make API calls
call_api() {
    local method=$1
    local endpoint=$2
    local data=$3

    if [ "$method" = "GET" ]; then
        curl -s -X GET "$API_BASE_URL$endpoint"
    else
        curl -s -X POST "$API_BASE_URL$endpoint" \
             -H "Content-Type: application/json" \
             -d "$data"
    fi
}

# Function to extract JSON values
extract_json() {
    local json=$1
    local key=$2
    echo "$json" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('$key', 'NOT_FOUND'))"
}

# Function to extract nested JSON values
extract_nested_json() {
    local json=$1
    local key1=$2
    local key2=$3
    echo "$json" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('$key1', {}).get('$key2', 'NOT_FOUND'))"
}

echo "📋 Test 1: Get Daily Quiz (First time)"
echo "--------------------------------------"
QUIZ_RESPONSE=$(call_api "GET" "/api/daily-quiz/?user_id=$TEST_USER")
QUIZ_ID=$(extract_json "$QUIZ_RESPONSE" "quiz_id")
ALREADY_ATTEMPTED=$(extract_json "$QUIZ_RESPONSE" "already_attempted")

echo "Quiz ID: $QUIZ_ID"
echo "Already Attempted: $ALREADY_ATTEMPTED"
echo ""

if [ "$ALREADY_ATTEMPTED" != "False" ]; then
    echo "❌ FAIL: Expected already_attempted to be False for first attempt"
    exit 1
fi

echo "✅ PASS: Quiz allows first attempt"
echo ""

echo "📋 Test 2: Submit Quiz (First attempt)"
echo "--------------------------------------"
SUBMIT_DATA="{
    \"user_id\": \"$TEST_USER\",
    \"quiz_id\": \"$QUIZ_ID\",
    \"answers\": {\"1\": 1, \"2\": 2, \"3\": 3, \"4\": 2, \"5\": 2},
    \"time_taken_seconds\": 45
}"

SUBMIT_RESPONSE=$(call_api "POST" "/api/daily-quiz/submit/" "$SUBMIT_DATA")
SUCCESS=$(extract_json "$SUBMIT_RESPONSE" "success")
COINS_EARNED_1=$(extract_nested_json "$SUBMIT_RESPONSE" "result" "coins_earned")
TOTAL_COINS_1=$(extract_json "$SUBMIT_RESPONSE" "total_coins")

echo "Success: $SUCCESS"
echo "Coins Earned: $COINS_EARNED_1"
echo "Total Coins: $TOTAL_COINS_1"
echo ""

if [ "$SUCCESS" != "True" ]; then
    echo "❌ FAIL: First submission failed"
    exit 1
fi

echo "✅ PASS: First submission successful"
echo ""

echo "📋 Test 3: Get Daily Quiz (After first attempt)"
echo "-----------------------------------------------"
QUIZ_RESPONSE_2=$(call_api "GET" "/api/daily-quiz/?user_id=$TEST_USER")
ALREADY_ATTEMPTED_2=$(extract_json "$QUIZ_RESPONSE_2" "already_attempted")

echo "Already Attempted: $ALREADY_ATTEMPTED_2"
echo ""

if [ "$ALREADY_ATTEMPTED_2" != "False" ]; then
    echo "❌ FAIL: Expected already_attempted to be False to allow multiple attempts"
    exit 1
fi

echo "✅ PASS: Quiz allows second attempt"
echo ""

echo "📋 Test 4: Submit Quiz (Second attempt)"
echo "---------------------------------------"
SUBMIT_DATA_2="{
    \"user_id\": \"$TEST_USER\",
    \"quiz_id\": \"$QUIZ_ID\",
    \"answers\": {\"1\": 2, \"2\": 1, \"3\": 0, \"4\": 3, \"5\": 1},
    \"time_taken_seconds\": 38
}"

SUBMIT_RESPONSE_2=$(call_api "POST" "/api/daily-quiz/submit/" "$SUBMIT_DATA_2")
SUCCESS_2=$(extract_json "$SUBMIT_RESPONSE_2" "success")
COINS_EARNED_2=$(extract_nested_json "$SUBMIT_RESPONSE_2" "result" "coins_earned")
TOTAL_COINS_2=$(extract_json "$SUBMIT_RESPONSE_2" "total_coins")

echo "Success: $SUCCESS_2"
echo "Coins Earned: $COINS_EARNED_2"
echo "Total Coins: $TOTAL_COINS_2"
echo ""

if [ "$SUCCESS_2" != "True" ]; then
    echo "❌ FAIL: Second submission failed"
    exit 1
fi

echo "✅ PASS: Second submission successful"
echo ""

echo "📋 Test 5: Verify Coin Accumulation"
echo "-----------------------------------"
EXPECTED_TOTAL=$((TOTAL_COINS_1 + COINS_EARNED_2))

echo "Expected Total Coins: $EXPECTED_TOTAL"
echo "Actual Total Coins: $TOTAL_COINS_2"

if [ "$TOTAL_COINS_2" -ne "$EXPECTED_TOTAL" ]; then
    echo "❌ FAIL: Coins did not accumulate properly"
    echo "Expected: $EXPECTED_TOTAL, Got: $TOTAL_COINS_2"
    exit 1
fi

echo "✅ PASS: Coins accumulated correctly"
echo ""

echo "📋 Test 6: Get Daily Quiz (After second attempt)"
echo "------------------------------------------------"
QUIZ_RESPONSE_3=$(call_api "GET" "/api/daily-quiz/?user_id=$TEST_USER")
ALREADY_ATTEMPTED_3=$(extract_json "$QUIZ_RESPONSE_3" "already_attempted")

echo "Already Attempted: $ALREADY_ATTEMPTED_3"
echo ""

if [ "$ALREADY_ATTEMPTED_3" != "False" ]; then
    echo "❌ FAIL: Expected already_attempted to be False to allow unlimited attempts"
    exit 1
fi

echo "✅ PASS: Quiz allows unlimited attempts"
echo ""

echo "🎉 ALL TESTS PASSED!"
echo "==================="
echo "✅ Multiple attempts allowed"
echo "✅ Coins accumulate properly"
echo "✅ Quiz data always available"
echo ""
echo "Summary:"
echo "- Attempt 1: $COINS_EARNED_1 coins"
echo "- Attempt 2: $COINS_EARNED_2 coins"
echo "- Total Coins: $TOTAL_COINS_2 coins"
echo ""
echo "The daily quiz now supports unlimited attempts per day with coin accumulation!"
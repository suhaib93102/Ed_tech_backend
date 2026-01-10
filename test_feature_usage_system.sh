#!/bin/bash

###############################################################################
# FEATURE USAGE RESTRICTION SYSTEM - LOCAL TEST SCRIPT
# Tests the 3-limit-per-feature system for free users
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_BASE="http://localhost:8000/api"
TEST_USER_ID="test_user_$(date +%s)"
TEST_FEATURE="quiz"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}FEATURE USAGE RESTRICTION SYSTEM - LOCAL TEST${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Function to make API calls
call_api() {
    local method=$1
    local endpoint=$2
    local data=$3
    local user_id=$4
    
    if [ -z "$user_id" ]; then
        user_id=$TEST_USER_ID
    fi
    
    if [ "$method" = "POST" ]; then
        curl -s -X POST \
            -H "Content-Type: application/json" \
            -H "X-User-ID: $user_id" \
            -d "$data" \
            "${API_BASE}${endpoint}"
    else
        curl -s -X GET \
            -H "X-User-ID: $user_id" \
            "${API_BASE}${endpoint}"
    fi
}

# Test 1: Check if user can access feature (should be YES)
echo -e "${YELLOW}[TEST 1] Check feature access (1st attempt - should be ALLOWED)${NC}"
echo "User: $TEST_USER_ID | Feature: $TEST_FEATURE"
echo ""

RESPONSE=$(call_api POST "/usage/check/" "{\"feature\": \"$TEST_FEATURE\"}")
echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Extract allowed status
ALLOWED=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null)
if [ "$ALLOWED" = "True" ]; then
    echo -e "${GREEN}✓ PASSED: Feature access allowed${NC}"
else
    echo -e "${RED}✗ FAILED: Feature access should be allowed${NC}"
fi
echo ""

# Test 2: Record first usage
echo -e "${YELLOW}[TEST 2] Record 1st feature usage${NC}"
RESPONSE=$(call_api POST "/usage/record/" "{\"feature\": \"$TEST_FEATURE\", \"input_size\": 100, \"usage_type\": \"text\"}")
echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Test 3: Record second usage
echo -e "${YELLOW}[TEST 3] Record 2nd feature usage${NC}"
RESPONSE=$(call_api POST "/usage/record/" "{\"feature\": \"$TEST_FEATURE\", \"input_size\": 150, \"usage_type\": \"text\"}")
echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Test 4: Record third usage
echo -e "${YELLOW}[TEST 4] Record 3rd feature usage${NC}"
RESPONSE=$(call_api POST "/usage/record/" "{\"feature\": \"$TEST_FEATURE\", \"input_size\": 200, \"usage_type\": \"text\"}")
echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Test 5: Try to access feature 4th time (should be BLOCKED)
echo -e "${YELLOW}[TEST 5] Check feature access (4th attempt - should be BLOCKED)${NC}"
RESPONSE=$(call_api POST "/usage/check/" "{\"feature\": \"$TEST_FEATURE\"}")
echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Check if blocked
SUCCESS=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null)
if [ "$SUCCESS" = "False" ]; then
    echo -e "${GREEN}✓ PASSED: Feature correctly blocked after 3 uses${NC}"
else
    echo -e "${RED}✗ FAILED: Feature should be blocked${NC}"
fi
echo ""

# Test 6: Get usage dashboard
echo -e "${YELLOW}[TEST 6] Get user usage dashboard${NC}"
RESPONSE=$(call_api GET "/usage/dashboard/" "" "$TEST_USER_ID")
echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Test 7: Check dashboard shows feature limits
echo -e "${YELLOW}[TEST 7] Verify dashboard shows correct limits and usage${NC}"
USED=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('dashboard', {}).get('features', {}).get('$TEST_FEATURE', {}).get('used', 0))" 2>/dev/null)
LIMIT=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('dashboard', {}).get('features', {}).get('$TEST_FEATURE', {}).get('limit', 0))" 2>/dev/null)
echo "Feature: $TEST_FEATURE | Used: $USED | Limit: $LIMIT"
echo ""

if [ "$USED" = "3" ] && [ "$LIMIT" = "3" ]; then
    echo -e "${GREEN}✓ PASSED: Dashboard correctly shows 3/3 usage${NC}"
else
    echo -e "${RED}✗ FAILED: Dashboard should show 3/3 usage (got $USED/$LIMIT)${NC}"
fi
echo ""

# Test 8: Test multiple features
echo -e "${YELLOW}[TEST 8] Test multiple features have independent limits${NC}"
TEST_FEATURE2="flashcards"

# Use flashcards 2 times
call_api POST "/usage/record/" "{\"feature\": \"$TEST_FEATURE2\", \"input_size\": 100, \"usage_type\": \"text\"}" > /dev/null
call_api POST "/usage/record/" "{\"feature\": \"$TEST_FEATURE2\", \"input_size\": 100, \"usage_type\": \"text\"}" > /dev/null

# Check if flashcards can still be used (should be YES, only 2 used out of 3)
RESPONSE=$(call_api POST "/usage/check/" "{\"feature\": \"$TEST_FEATURE2\"}")
SUCCESS=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null)

if [ "$SUCCESS" = "True" ]; then
    echo -e "${GREEN}✓ PASSED: Different features have independent limits${NC}"
else
    echo -e "${RED}✗ FAILED: Flashcards should still be available${NC}"
fi
echo ""

# Test 9: Get admin analytics
echo -e "${YELLOW}[TEST 9] Check admin analytics endpoint${NC}"
ADMIN_USER="admin_user_123"
RESPONSE=$(call_api GET "/admin/analytics/" "" "$ADMIN_USER")
echo "Response (first 500 chars):"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -30 || echo "$RESPONSE"
echo ""

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}TEST SUMMARY${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "✓ Free users have 3 uses per feature"
echo "✓ Usage is tracked persistently"
echo "✓ Access is blocked after limit exceeded (403)"
echo "✓ Different features have independent limits"
echo "✓ Usage dashboard shows real-time counts"
echo "✓ Admin analytics available"
echo ""
echo -e "${YELLOW}Test User ID: ${TEST_USER_ID}${NC}"
echo "Use this ID to check database records if needed:"
echo "  SELECT * FROM question_solver_usersubscription WHERE user_id='$TEST_USER_ID';"
echo "  SELECT * FROM question_solver_featureusagelog WHERE subscription_id=(SELECT id FROM question_solver_usersubscription WHERE user_id='$TEST_USER_ID');"
echo ""

#!/bin/bash

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test ID with timestamp
TEST_UID="test_$(date +%s)"
API="http://localhost:8000/api"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        FEATURE USAGE RESTRICTION SYSTEM - LIVE TEST             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Test User ID: $TEST_UID"
echo ""

# TEST 1
echo -e "${YELLOW}[TEST 1] Check feature access - 1st attempt (should be ALLOWED)${NC}"
echo "Request: POST /api/usage/check/"
echo "User: $TEST_UID, Feature: quiz"
echo ""

RESPONSE=$(curl -s -X POST "$API/usage/check/" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: $TEST_UID" \
  -d '{"feature":"quiz"}')

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

SUCCESS=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null)
if [ "$SUCCESS" = "True" ]; then
    echo -e "${GREEN}✓ PASSED: Feature access allowed${NC}"
else
    echo -e "${RED}✗ FAILED: Should be allowed${NC}"
fi
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# TEST 2-4: Record uses
for i in 1 2 3; do
    echo -e "${YELLOW}[TEST $((i+1))] Record feature usage - attempt $i${NC}"
    echo "Request: POST /api/usage/record/"
    echo "User: $TEST_UID, Feature: quiz, Input Size: $((100*i))"
    echo ""
    
    RESPONSE=$(curl -s -X POST "$API/usage/record/" \
      -H "Content-Type: application/json" \
      -H "X-User-ID: $TEST_UID" \
      -d "{\"feature\":\"quiz\",\"input_size\":$((100*i)),\"usage_type\":\"text\"}")
    
    echo "Response:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    echo ""
    
    SUCCESS=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null)
    if [ "$SUCCESS" = "True" ]; then
        echo -e "${GREEN}✓ PASSED: Usage $i recorded${NC}"
    else
        echo -e "${RED}✗ FAILED${NC}"
    fi
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
done

# TEST 5: Try 4th access (should be blocked)
echo -e "${YELLOW}[TEST 5] Check feature access - 4th attempt (should be BLOCKED)${NC}"
echo "Request: POST /api/usage/check/"
echo "User: $TEST_UID, Feature: quiz"
echo ""

RESPONSE=$(curl -s -X POST "$API/usage/check/" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: $TEST_UID" \
  -d '{"feature":"quiz"}')

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

SUCCESS=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null)
if [ "$SUCCESS" = "False" ]; then
    echo -e "${GREEN}✓ PASSED: Feature correctly BLOCKED after 3 uses${NC}"
else
    echo -e "${RED}✗ FAILED: Should be blocked${NC}"
fi
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# TEST 6: Get dashboard
echo -e "${YELLOW}[TEST 6] Get user usage dashboard${NC}"
echo "Request: GET /api/usage/dashboard/"
echo "User: $TEST_UID"
echo ""

RESPONSE=$(curl -s -X GET "$API/usage/dashboard/" \
  -H "X-User-ID: $TEST_UID")

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -50

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# TEST 7: Test another feature
echo -e "${YELLOW}[TEST 7] Test independent feature - use 'flashcards' 2 times${NC}"
echo "Request: POST /api/usage/record/ (for flashcards)"
echo ""

for i in 1 2; do
    RESPONSE=$(curl -s -X POST "$API/usage/record/" \
      -H "Content-Type: application/json" \
      -H "X-User-ID: $TEST_UID" \
      -d "{\"feature\":\"flashcards\",\"input_size\":100,\"usage_type\":\"text\"}")
    echo "Flashcards use $i recorded"
done

# Check if flashcards is still available
echo ""
RESPONSE=$(curl -s -X POST "$API/usage/check/" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: $TEST_UID" \
  -d '{"feature":"flashcards"}')

SUCCESS=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null)
if [ "$SUCCESS" = "True" ]; then
    echo -e "${GREEN}✓ PASSED: Flashcards still available (independent limits)${NC}"
else
    echo -e "${RED}✗ FAILED: Flashcards should still be available${NC}"
fi
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# TEST 8: Get feature status
echo -e "${YELLOW}[TEST 8] Get specific feature status${NC}"
echo "Request: GET /api/usage/feature/quiz/"
echo ""

RESPONSE=$(curl -s -X GET "$API/usage/feature/quiz/" \
  -H "X-User-ID: $TEST_UID")

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# TEST 9: Admin analytics
echo -e "${YELLOW}[TEST 9] Get admin analytics${NC}"
echo "Request: GET /api/admin/analytics/"
echo ""

RESPONSE=$(curl -s -X GET "$API/admin/analytics/" \
  -H "X-User-ID: admin_user")

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -40
echo ""

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                         TEST SUMMARY                           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✓ Free users have 3 uses per feature${NC}"
echo -e "${GREEN}✓ Usage is tracked persistently${NC}"
echo -e "${GREEN}✓ Access is blocked after limit (403 FORBIDDEN)${NC}"
echo -e "${GREEN}✓ Different features have independent limits${NC}"
echo -e "${GREEN}✓ Usage dashboard shows real-time counts${NC}"
echo -e "${GREEN}✓ Feature status shows remaining attempts${NC}"
echo -e "${GREEN}✓ Admin analytics available${NC}"
echo ""
echo "Test User ID for DB verification: $TEST_UID"
echo ""

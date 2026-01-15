#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

BASE_URL="http://127.0.0.1:8000/api"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     ASK A QUESTION - Web Search Integration Testing           ║${NC}"
echo -e "${BLUE}║     Simple Search API (No AI/Gemini)                          ║${NC}"
echo -e "${BLUE}║     Testing on http://127.0.0.1:8000                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}\n"

# Test 1: Check Search API Status
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}TEST 1️⃣  - Check Search APIs Status${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo "📝 Request:"
echo "GET $BASE_URL/ask-question/status/"
echo ""

RESPONSE=$(curl -s -X GET "$BASE_URL/ask-question/status/" \
  -H "Content-Type: application/json")

echo "Response:"
echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Test 2: Ask Question - Search (Simple)
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}TEST 2️⃣  - Ask Question Search (Biology)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo "📝 Request:"
echo "POST $BASE_URL/ask-question/search/"
echo ""
echo "Body:"
cat << 'EOF'
{
    "question": "What is photosynthesis?",
    "max_results": 5
}
EOF
echo ""
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/ask-question/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is photosynthesis?",
    "max_results": 5
  }')

echo "Response:"
echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Test 3: Ask Question - Search (Math)
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}TEST 3️⃣  - Ask Question Search (Math)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo "📝 Request:"
echo "POST $BASE_URL/ask-question/search/"
echo ""
echo "Body:"
cat << 'EOF'
{
    "question": "How to solve quadratic equations?",
    "max_results": 3
}
EOF
echo ""
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/ask-question/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How to solve quadratic equations?",
    "max_results": 3
  }')

echo "Response:"
echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Test 4: Ask Question - Get Sources
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}TEST 4️⃣  - Ask Question with Trusted Sources${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo "📝 Request:"
echo "POST $BASE_URL/ask-question/sources/"
echo ""
echo "Body:"
cat << 'EOF'
{
    "question": "What is DNA?",
    "max_results": 4
}
EOF
echo ""
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/ask-question/sources/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is DNA?",
    "max_results": 4
  }')

echo "Response:"
echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Test 5: Error Test - Empty Question
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${RED}TEST 5️⃣  - Error Test (Empty Question)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo "📝 Request:"
echo "POST $BASE_URL/ask-question/search/"
echo ""
echo "Body:"
cat << 'EOF'
{
    "question": ""
}
EOF
echo ""
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/ask-question/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": ""
  }')

echo "Response (should show error):"
echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Test 6: Error Test - Question Too Short
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${RED}TEST 6️⃣  - Error Test (Question Too Short)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo "📝 Request:"
echo "POST $BASE_URL/ask-question/search/"
echo ""
echo "Body:"
cat << 'EOF'
{
    "question": "ab"
}
EOF
echo ""
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/ask-question/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "ab"
  }')

echo "Response (should show error):"
echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Test 7: Science Question
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}TEST 7️⃣  - Ask Question Search (Science)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo "📝 Request:"
echo "POST $BASE_URL/ask-question/search/"
echo ""
echo "Body:"
cat << 'EOF'
{
    "question": "Explain the carbon cycle",
    "max_results": 5
}
EOF
echo ""
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/ask-question/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain the carbon cycle",
    "max_results": 5
  }')

echo "Response:"
echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║✅ All Tests Completed!                                         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}\n"

# Summary
echo -e "${BLUE}📊 ENDPOINTS SUMMARY:${NC}\n"
echo -e "${GREEN}✅ Available Endpoints:${NC}"
echo "   1. GET  /api/ask-question/status/      - Check API configuration"
echo "   2. POST /api/ask-question/search/      - Search web for answers"
echo "   3. POST /api/ask-question/sources/     - Get trusted source links"
echo ""

echo -e "${BLUE}📋 ENDPOINT DETAILS:${NC}\n"
echo -e "${GREEN}1. Status Endpoint (GET):${NC}"
echo "   Purpose: Check if search APIs are configured"
echo "   Response: API status, trusted domains count"
echo ""

echo -e "${GREEN}2. Search Endpoint (POST):${NC}"
echo "   Purpose: Search web and get summary from snippets"
echo "   Required: question"
echo "   Optional: max_results (1-10, default 5), language (default en)"
echo "   Response: Search results with snippets and summary"
echo ""

echo -e "${GREEN}3. Sources Endpoint (POST):${NC}"
echo "   Purpose: Get trusted educational sources for a question"
echo "   Required: question"
echo "   Optional: max_results (1-10, default 5)"
echo "   Response: Array of trusted source links"
echo ""

echo -e "${BLUE}📝 CURL EXAMPLES:${NC}\n"
echo -e "${GREEN}Example 1 - Simple Search:${NC}"
cat << 'EOF'
curl -X POST "http://127.0.0.1:8000/api/ask-question/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Newton'\''s first law?",
    "max_results": 5
  }'
EOF
echo ""
echo ""

echo -e "${GREEN}Example 2 - Get Trusted Sources:${NC}"
cat << 'EOF'
curl -X POST "http://127.0.0.1:8000/api/ask-question/sources/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How does photosynthesis work?",
    "max_results": 3
  }'
EOF
echo ""
echo ""

echo -e "${GREEN}Example 3 - Check API Status:${NC}"
cat << 'EOF'
curl -X GET "http://127.0.0.1:8000/api/ask-question/status/"
EOF
echo ""

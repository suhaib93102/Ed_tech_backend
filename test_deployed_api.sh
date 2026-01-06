#!/bin/bash
# Comprehensive API Testing Script for EdTech Backend
# Run this after redeploying to Render

BASE_URL="https://ed-tech-05bu.onrender.com/api"
YOUTUBE_BASE_URL="https://ed-tech-05bu.onrender.com/api/youtube"

echo "🚀 Starting comprehensive API testing..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test endpoint
test_endpoint() {
    local url=$1
    local method=${2:-GET}
    local data=$3
    local expected_status=${4:-200}

    echo -n "Testing $method $url ... "

    if [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "$data" "$url")
    else
        response=$(curl -s -w "\n%{http_code}" "$url")
    fi

    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)

    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (Status: $status_code)"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (Status: $status_code, Expected: $expected_status)"
        echo "Response: $body"
        return 1
    fi
}

# Health Checks
echo -e "\n${YELLOW}=== Health Checks ===${NC}"
test_endpoint "$BASE_URL/health/"
test_endpoint "$YOUTUBE_BASE_URL/health/"

# Service Status
echo -e "\n${YELLOW}=== Service Status ===${NC}"
test_endpoint "$BASE_URL/status/"

# Authentication endpoints (basic checks)
echo -e "\n${YELLOW}=== Authentication Endpoints ===${NC}"
test_endpoint "$BASE_URL/auth/login/" POST '{"email":"test@example.com","password":"test"}' 400
test_endpoint "$BASE_URL/auth/register/" POST '{"email":"test@example.com","password":"test123","username":"testuser"}' 400

# Quiz endpoints
echo -e "\n${YELLOW}=== Quiz Endpoints ===${NC}"
test_endpoint "$BASE_URL/quiz/settings/"

# Daily Quiz endpoints
echo -e "\n${YELLOW}=== Daily Quiz Endpoints ===${NC}"
test_endpoint "$BASE_URL/daily-quiz/" 401  # Should require auth

# Subscription endpoints
echo -e "\n${YELLOW}=== Subscription Endpoints ===${NC}"
test_endpoint "$BASE_URL/subscription/plans/"
test_endpoint "$BASE_URL/subscriptions/plans/"

# Payment endpoints (basic checks)
echo -e "\n${YELLOW}=== Payment Endpoints ===${NC}"
test_endpoint "$BASE_URL/payment/razorpay-key/" 401  # Should require auth

# YouTube endpoints
echo -e "\n${YELLOW}=== YouTube Endpoints ===${NC}"
test_endpoint "$YOUTUBE_BASE_URL/summarize/" POST '{"url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ"}' 401

# Admin endpoint
echo -e "\n${YELLOW}=== Admin Endpoints ===${NC}"
test_endpoint "https://ed-tech-05bu.onrender.com/admin/" 302  # Should redirect to login

echo -e "\n${GREEN}=== Testing Complete ===${NC}"
echo "Note: Some endpoints require authentication. Test with proper tokens for full functionality."
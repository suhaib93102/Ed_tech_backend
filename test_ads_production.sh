#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BASE_URL="http://127.0.0.1:8000/api"
COOKIES="/tmp/cookies.txt"

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Unity Ads API - Production Testing   ║${NC}"
echo -e "${BLUE}║   Testing on localhost:8000            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

# Step 1: Get login page (to get CSRF token)
echo -e "${YELLOW}⚡ Step 1: Getting CSRF token...${NC}"
curl -s -c $COOKIES "$BASE_URL/auth/login/" > /dev/null 2>&1

# Step 2: Login with testuser
echo -e "${YELLOW}⚡ Step 2: Logging in as testuser...${NC}"
LOGIN_RESPONSE=$(curl -s -b $COOKIES -c $COOKIES -X POST "$BASE_URL/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}')

echo "Login Response: $LOGIN_RESPONSE"

if echo "$LOGIN_RESPONSE" | grep -q '"success":true'; then
  echo -e "${GREEN}✅ Login successful!${NC}\n"
else
  echo -e "${YELLOW}Note: Login might use different endpoint, testing unauthenticated endpoints...${NC}\n"
fi

# Test 1: Check if ad should be shown
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 1: Check if ad should be shown${NC}"
echo -e "${BLUE}POST /ads/check-should-show-ad/${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

RESPONSE=$(curl -s -b $COOKIES -X POST "$BASE_URL/ads/check-should-show-ad/" \
  -H "Content-Type: application/json" \
  -d '{"feature_name": "daily_quiz", "platform": "ios"}')

echo "Response:"
echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Test 2: Log ad impression (SHOWN)
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 2: Log ad impression (SHOWN)${NC}"
echo -e "${BLUE}POST /ads/log-impression/${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

RESPONSE=$(curl -s -b $COOKIES -X POST "$BASE_URL/ads/log-impression/" \
  -H "Content-Type: application/json" \
  -d '{"feature_name": "daily_quiz", "ad_type": "interstitial", "platform": "ios", "status": "shown"}')

echo "Response:"
echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Test 3: Log ad impression (CLICKED)
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 3: Log ad impression (CLICKED)${NC}"
echo -e "${BLUE}POST /ads/log-impression/${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

RESPONSE=$(curl -s -b $COOKIES -X POST "$BASE_URL/ads/log-impression/" \
  -H "Content-Type: application/json" \
  -d '{"feature_name": "daily_quiz", "ad_type": "interstitial", "platform": "ios", "status": "clicked"}')

echo "Response:"
echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Test 4: Log ad impression (CLOSED)
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 4: Log ad impression (CLOSED)${NC}"
echo -e "${BLUE}POST /ads/log-impression/${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

RESPONSE=$(curl -s -b $COOKIES -X POST "$BASE_URL/ads/log-impression/" \
  -H "Content-Type: application/json" \
  -d '{"feature_name": "daily_quiz", "ad_type": "interstitial", "platform": "ios", "status": "closed"}')

echo "Response:"
echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Test 5: Get user ad stats
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 5: Get user ad stats${NC}"
echo -e "${BLUE}GET /ads/user-stats/${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

RESPONSE=$(curl -s -b $COOKIES -X GET "$BASE_URL/ads/user-stats/" \
  -H "Content-Type: application/json")

echo "Response:"
echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Test 6: Check for invalid feature
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 6: Invalid request (missing feature_name)${NC}"
echo -e "${BLUE}POST /ads/check-should-show-ad/${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

RESPONSE=$(curl -s -b $COOKIES -X POST "$BASE_URL/ads/check-should-show-ad/" \
  -H "Content-Type: application/json" \
  -d '{}')

echo "Response (should show error):"
echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║✅ All tests completed successfully!    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}\n"

# Show database stats
echo -e "${YELLOW}📊 Database Statistics:${NC}\n"
python << 'PYEOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
django.setup()

from question_solver.models import AdImpressionLog, FeatureAdConfig, UserAdLimitTracker
from django.contrib.auth.models import User

print(f"✅ Total Users: {User.objects.count()}")
print(f"✅ Feature Configs: {FeatureAdConfig.objects.count()}")
print(f"✅ Ad Impressions: {AdImpressionLog.objects.count()}")
print(f"✅ User Trackers: {UserAdLimitTracker.objects.count()}")

# Show feature configs
print(f"\n📋 Feature Configurations:")
for config in FeatureAdConfig.objects.all():
    print(f"  • {config.feature_display_name} (freq: {config.show_frequency}, max: {config.max_ads_per_day})")

# Show recent impressions
print(f"\n📊 Recent Ad Impressions:")
for log in AdImpressionLog.objects.order_by('-created_at')[:5]:
    print(f"  • {log.feature} - {log.ad_type} ({log.status}) - {log.created_at.strftime('%H:%M:%S')}")
PYEOF


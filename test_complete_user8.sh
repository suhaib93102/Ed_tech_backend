#!/bin/bash

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Complete Daily Quiz Flow for User 8${NC}"
echo -e "${BLUE}========================================${NC}"

# Step 1: Generate token
echo -e "\n${YELLOW}Step 1: Generate JWT Token for User 8${NC}"

TOKEN=$(python3 << 'PYEOF'
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "4f5e2bac434c38bcf80b3f71df16ad50"
payload = {
    "user_id": 8,
    "username": "user8",
    "email": "user8@example.com",
    "exp": datetime.utcnow() + timedelta(hours=24),
    "iat": datetime.utcnow()
}

token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
print(token)
PYEOF
)

echo -e "${GREEN}✅ Token Generated${NC}"
echo "Token: $TOKEN"

# Step 2: Fetch daily quiz
echo -e "\n${YELLOW}Step 2: Fetch Daily Quiz${NC}"

QUIZ_RESPONSE=$(curl -s -X GET "http://127.0.0.1:8000/api/quiz/daily-quiz/?user_id=8&language=english" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

QUIZ_ID=$(echo "$QUIZ_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('quiz_id', ''))")
QUESTION_COUNT=$(echo "$QUIZ_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('questions', [])))")

echo -e "${GREEN}✅ Daily Quiz Fetched${NC}"
echo "Quiz ID: $QUIZ_ID"
echo "Questions: $QUESTION_COUNT"

# Step 3: Start Quiz
echo -e "\n${YELLOW}Step 3: Start Quiz Session${NC}"

START_RESPONSE=$(curl -s -X POST "http://127.0.0.1:8000/api/quiz/start-daily-quiz/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 8, "language": "english"}')

echo -e "${GREEN}✅ Quiz Session Started${NC}"

# Step 4: Submit Answers
echo -e "\n${YELLOW}Step 4: Submit Quiz Answers${NC}"
echo "Using Quiz ID: $QUIZ_ID"

SUBMIT_RESPONSE=$(curl -s -X POST "http://127.0.0.1:8000/api/quiz/submit-daily-quiz/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": 8,
    \"quiz_id\": \"$QUIZ_ID\",
    \"language\": \"english\",
    \"answers\": {
      \"1\": 2,
      \"2\": 1,
      \"3\": 1,
      \"4\": 1,
      \"5\": 1
    }
  }")

echo -e "${GREEN}✅ Quiz Submitted${NC}"
echo ""
echo -e "${BLUE}Submit Response:${NC}"
echo "$SUBMIT_RESPONSE" | python3 -m json.tool

# Check success
SUCCESS=$(echo "$SUBMIT_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('success', False))")

if [ "$SUCCESS" = "True" ]; then
  SCORE=$(echo "$SUBMIT_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('score', 0))")
  COINS=$(echo "$SUBMIT_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('coins_earned', 0))")
  echo -e "\n${GREEN}✅✅✅ QUIZ SUBMISSION SUCCESSFUL! ✅✅✅${NC}"
  echo -e "Score: ${YELLOW}$SCORE${NC}"
  echo -e "Coins Earned: ${YELLOW}$COINS${NC}"
else
  echo -e "\n${RED}❌ Submission Issue${NC}"
fi

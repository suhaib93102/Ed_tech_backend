# Language Endpoints Testing Guide

Complete testing guide for all language-enabled endpoints with production error fixes.

---

## 1. Daily Quiz Endpoint - Language Testing

### 1.1 Local Testing - English (Query Parameter)

```bash
# Test English Daily Quiz
curl -s "http://localhost:8000/api/daily-quiz/?language=english&user_id=test_user" \
  -H "Content-Type: application/json" | jq '.'

# Expected Response (200 OK):
{
  "success": true,
  "data": {
    "quiz_id": "daily_q_20250106",
    "language": "english",
    "date": "2025-01-06",
    "questions": [
      {
        "id": 1,
        "question": "What is the capital of India?",
        "options": ["Mumbai", "New Delhi", "Bangalore", "Kolkata"],
        "category": "geography"
      },
      ...
    ]
  }
}
```

### 1.2 Local Testing - Hindi (Query Parameter)

```bash
# Test Hindi Daily Quiz
curl -s "http://localhost:8000/api/daily-quiz/?language=hindi&user_id=test_user" \
  -H "Content-Type: application/json" | jq '.'

# Expected Response (200 OK):
{
  "success": true,
  "data": {
    "quiz_id": "daily_q_20250106",
    "language": "hindi",
    "date": "2025-01-06",
    "questions": [
      {
        "id": 1,
        "question": "भारत की राजधानी कौन सी है?",
        "options": ["मुंबई", "नई दिल्ली", "बेंगलुरु", "कोलकाता"],
        "category": "भूगोल"
      },
      ...
    ]
  }
}
```

### 1.3 Local Testing - Default Language (No parameter)

```bash
# Test Daily Quiz without language parameter (should default to English)
curl -s "http://localhost:8000/api/daily-quiz/?user_id=test_user" \
  -H "Content-Type: application/json" | jq '.'

# Expected: English questions (default behavior)
```

### 1.4 Production Testing - English

```bash
# Test production server - English
curl -s "https://ed-tech-backend-tzn8.onrender.com/api/daily-quiz/?language=english&user_id=test_user" \
  -H "Content-Type: application/json" | jq '.'

# Monitor response time: should be < 3 seconds
time curl -s "https://ed-tech-backend-tzn8.onrender.com/api/daily-quiz/?language=english&user_id=test_user" -o /dev/null
```

### 1.5 Production Testing - Hindi

```bash
# Test production server - Hindi
curl -s "https://ed-tech-backend-tzn8.onrender.com/api/daily-quiz/?language=hindi&user_id=test_user" \
  -H "Content-Type: application/json" | jq '.'
```

### 1.6 Error Testing - Invalid Language

```bash
# Test with invalid language (should default to English or return error)
curl -s "http://localhost:8000/api/daily-quiz/?language=spanish&user_id=test_user" \
  -H "Content-Type: application/json" | jq '.'

# Expected: Either fallback to English or 400 Bad Request with helpful message
```

---

## 2. Flashcards Endpoint - Language Testing

### 2.1 Local Testing - English

```bash
# Generate 10 flashcards in English
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Indian Constitutional Law",
    "num_cards": 10,
    "language": "english"
  }' | jq '.'

# Expected Response (200 OK):
{
  "success": true,
  "data": {
    "topic": "Indian Constitutional Law",
    "language": "english",
    "total_cards": 10,
    "flashcards": [
      {
        "id": 1,
        "question": "What is the fundamental right to equality?",
        "answer": "Article 14 of the Indian Constitution guarantees the right to equality before law...",
        "category": "fundamental_rights"
      },
      ...
    ]
  }
}
```

### 2.2 Local Testing - Hindi

```bash
# Generate flashcards in Hindi
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "भारतीय संविधान",
    "num_cards": 10,
    "language": "hindi"
  }' | jq '.'

# Expected Response (200 OK):
{
  "success": true,
  "data": {
    "topic": "भारतीय संविधान",
    "language": "hindi",
    "total_cards": 10,
    "flashcards": [
      {
        "id": 1,
        "question": "समानता का मौलिक अधिकार क्या है?",
        "answer": "भारतीय संविधान के अनुच्छेद 14 में कानून के समक्ष समानता का अधिकार दिया गया है...",
        "category": "मौलिक_अधिकार"
      },
      ...
    ]
  }
}
```

### 2.3 Local Testing - Default Parameters

```bash
# Test with default num_cards (should default to 5-10)
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Indian Constitution"
  }' | jq '.'
```

### 2.4 Error Testing - Missing Topic

```bash
# Test missing topic parameter (400 Bad Request)
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "num_cards": 10,
    "language": "english"
  }' | jq '.'

# Expected (400 Bad Request):
{
  "success": false,
  "error": "Please provide a topic",
  "message": "Topic field is required for generating flashcards"
}
```

### 2.5 Error Testing - Invalid num_cards

```bash
# Test with invalid num_cards (should be clamped to valid range)
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Indian Constitution",
    "num_cards": 200,
    "language": "english"
  }' | jq '.'

# Expected: num_cards clamped to max (usually 50)
```

### 2.6 Production Testing - English

```bash
# Test production endpoint - English
curl -X POST "https://ed-tech-backend-tzn8.onrender.com/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Indian Constitutional Law",
    "num_cards": 5,
    "language": "english"
  }' | jq '.'
```

### 2.7 Production Testing - Hindi

```bash
# Test production endpoint - Hindi
curl -X POST "https://ed-tech-backend-tzn8.onrender.com/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "भारतीय संविधान",
    "num_cards": 5,
    "language": "hindi"
  }' | jq '.'
```

---

## 3. Predicted Questions Endpoint - Language Testing & 400 Error Fix

### 3.1 CRITICAL: Fix for 400 Error

**Problem:** POST `/api/predicted-questions/generate/` returns 400 Bad Request
**Root Cause:** Missing validation for required parameters (topic or document)
**Solution:** Implement proper validation with helpful error messages

**Fixed Implementation:**
```python
# In views.py PredictedQuestionsView.post()
if not topic and 'document' not in request.FILES:
    logger.warning("[PREDICTED_Q] Missing topic and no document provided")
    return Response({
        'success': False,
        'error': 'Please provide either a topic or document',
        'message': 'Submit text in the topic field or upload a document file (.txt, .pdf, .jpg)',
        'example_topic': 'Indian Constitutional Law',
        'supported_formats': ['.txt', '.md', '.pdf', '.jpg', '.jpeg', '.png']
    }, status=status.HTTP_400_BAD_REQUEST)
```

### 3.2 Local Testing - With Topic (English)

```bash
# Generate predicted questions with topic (English)
curl -X POST "http://localhost:8000/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Indian Polity and Constitutional Law",
    "exam_type": "UPSC",
    "num_questions": 5,
    "language": "english"
  }' | jq '.'

# Expected Response (200 OK):
{
  "success": true,
  "data": {
    "topic": "Indian Polity and Constitutional Law",
    "exam_type": "UPSC",
    "language": "english",
    "total_questions": 5,
    "key_definitions": [
      {
        "term": "Federalism",
        "definition": "Distribution of power between central and state governments",
        "explanation": "Indian federalism is characterized by...",
        "example": "The division of powers in the Constitution..."
      }
    ],
    "questions": [
      {
        "id": 1,
        "question": "Explain the federal structure of the Indian Constitution with specific examples",
        "difficulty": "Hard",
        "importance": "High",
        "question_type": "Analysis",
        "sample_answer": "The Indian Constitution establishes a federal system where...",
        "why_important": "Federal structure is crucial for UPSC mains paper on Polity",
        "key_concepts": ["Federalism", "Division of Powers", "State Autonomy"]
      },
      ...
    ]
  }
}
```

### 3.3 Local Testing - With Topic (Hindi)

```bash
# Generate predicted questions with topic (Hindi)
curl -X POST "http://localhost:8000/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "भारतीय राजनीति और संविधान कानून",
    "exam_type": "UPSC",
    "num_questions": 5,
    "language": "hindi"
  }' | jq '.'

# Expected: Hindi questions with Hindi explanations
```

### 3.4 Local Testing - With Document Upload (PDF)

```bash
# Upload PDF document for predicted questions (English)
curl -X POST "http://localhost:8000/api/predicted-questions/generate/" \
  -F 'document=@/path/to/document.pdf' \
  -F 'exam_type=UPSC' \
  -F 'num_questions=5' \
  -F 'language=english' | jq '.'

# Expected: Extract text from PDF and generate predicted questions
```

### 3.5 Local Testing - With Image Upload (OCR)

```bash
# Upload image for text extraction via OCR (English)
curl -X POST "http://localhost:8000/api/predicted-questions/generate/" \
  -F 'document=@/path/to/image.jpg' \
  -F 'exam_type=UPSC' \
  -F 'num_questions=5' \
  -F 'language=english' | jq '.'

# Expected: Extract text via OCR and generate predicted questions
```

### 3.6 Error Testing - Missing Topic AND Document (400 Error Fix Test)

```bash
# THIS IS THE FIX FOR THE 400 ERROR
# Send request without topic or document
curl -X POST "http://localhost:8000/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "exam_type": "UPSC",
    "num_questions": 5,
    "language": "english"
  }' | jq '.'

# Expected (400 Bad Request - FIXED):
{
  "success": false,
  "error": "Please provide either a topic or document",
  "message": "Submit text in the topic field or upload a document file (.txt, .pdf, .jpg)",
  "example_topic": "Indian Constitutional Law",
  "supported_formats": [".txt", ".md", ".pdf", ".jpg", ".jpeg", ".png"]
}

# BEFORE FIX: Would return 500 Internal Server Error or cryptic 400
# AFTER FIX: Returns 400 with helpful instructions
```

### 3.7 Error Testing - Invalid Document Type

```bash
# Test with unsupported document type (.zip)
curl -X POST "http://localhost:8000/api/predicted-questions/generate/" \
  -F 'document=@/path/to/file.zip' \
  -F 'exam_type=UPSC' \
  -F 'num_questions=5' \
  -F 'language=english' | jq '.'

# Expected (400 Bad Request):
{
  "success": false,
  "error": "Unsupported document type: file.zip",
  "supported_formats": [".txt", ".md", ".pdf", ".jpg", ".jpeg", ".png"]
}
```

### 3.8 Error Testing - Empty Document

```bash
# Test with empty text document
curl -X POST "http://localhost:8000/api/predicted-questions/generate/" \
  -F 'document=@/path/to/empty.txt' \
  -F 'exam_type=UPSC' \
  -F 'num_questions=5' \
  -F 'language=english' | jq '.'

# Expected (400 Bad Request):
{
  "success": false,
  "error": "Could not extract text from document",
  "message": "Please ensure the document contains readable text"
}
```

### 3.9 Error Testing - OCR Failure on Image

```bash
# Test OCR failure (unreadable image)
curl -X POST "http://localhost:8000/api/predicted-questions/generate/" \
  -F 'document=@/path/to/blurry_image.jpg' \
  -F 'exam_type=UPSC' \
  -F 'num_questions=5' \
  -F 'language=english' | jq '.'

# Expected (400 Bad Request):
{
  "success": false,
  "error": "Failed to extract text from image",
  "details": "OCR processing failed"
}
```

### 3.10 Error Testing - Invalid num_questions

```bash
# Test with invalid num_questions
curl -X POST "http://localhost:8000/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Indian Constitution",
    "exam_type": "UPSC",
    "num_questions": "invalid",
    "language": "english"
  }' | jq '.'

# Expected (400 Bad Request):
{
  "success": false,
  "error": "Invalid number of questions",
  "message": "num_questions must be a number between 1 and 20",
  "suggestion": "Use integer values like 5, 10, 15"
}
```

### 3.11 Error Testing - Gemini API Failure (500 Error)

```bash
# Simulate by sending problematic content that causes Gemini to fail
curl -X POST "http://localhost:8000/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "a" * 10000,
    "exam_type": "UPSC",
    "num_questions": 5,
    "language": "english"
  }' | jq '.'

# Expected (500 Internal Server Error with helpful message):
{
  "success": false,
  "error": "Failed to generate predicted questions",
  "details": "[Original error message from Gemini]",
  "suggestion": "Check your AI service API key and quota"
}
```

### 3.12 Production Testing - English (400 Error Fix Test)

```bash
# THIS TESTS THE PRODUCTION FIX
# Send request without topic to production
curl -X POST "https://ed-tech-backend-tzn8.onrender.com/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "exam_type": "UPSC",
    "num_questions": 5
  }' | jq '.'

# Expected (400 Bad Request - Should now have helpful message):
{
  "success": false,
  "error": "Please provide either a topic or document",
  "message": "Submit text in the topic field or upload a document file (.txt, .pdf, .jpg)",
  "example_topic": "Indian Constitutional Law",
  "supported_formats": [".txt", ".md", ".pdf", ".jpg", ".jpeg", ".png"]
}

# VERIFICATION: Response should have status 400 (not 500), with helpful message
```

### 3.13 Production Testing - With Valid Topic (English)

```bash
# Test production with valid topic
curl -X POST "https://ed-tech-backend-tzn8.onrender.com/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Indian Constitutional Law",
    "exam_type": "UPSC",
    "num_questions": 5,
    "language": "english"
  }' | jq '.'
```

### 3.14 Production Testing - With Valid Topic (Hindi)

```bash
# Test production with valid Hindi topic
curl -X POST "https://ed-tech-backend-tzn8.onrender.com/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "भारतीय संविधान और राजनीति",
    "exam_type": "UPSC",
    "num_questions": 5,
    "language": "hindi"
  }' | jq '.'
```

---

## 4. JavaScript Testing Examples

### 4.1 Daily Quiz - English (JavaScript)

```javascript
// Test Daily Quiz with English language
async function testDailyQuizEnglish() {
  try {
    const response = await fetch('http://localhost:8000/api/daily-quiz/?language=english&user_id=test_user', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      console.error('Error:', response.status, response.statusText);
      return;
    }
    
    const data = await response.json();
    console.log('Daily Quiz (English):', data);
    console.log('Questions:', data.data.questions.length);
    console.log('First question:', data.data.questions[0].question);
  } catch (error) {
    console.error('Fetch error:', error);
  }
}

testDailyQuizEnglish();
```

### 4.2 Daily Quiz - Hindi (JavaScript)

```javascript
// Test Daily Quiz with Hindi language
async function testDailyQuizHindi() {
  try {
    const response = await fetch('http://localhost:8000/api/daily-quiz/?language=hindi&user_id=test_user', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    const data = await response.json();
    console.log('Daily Quiz (Hindi):', data);
    console.log('First question (Hindi):', data.data.questions[0].question);
  } catch (error) {
    console.error('Fetch error:', error);
  }
}

testDailyQuizHindi();
```

### 4.3 Flashcards - English (JavaScript)

```javascript
// Test Flashcards generation - English
async function testFlashcardsEnglish() {
  try {
    const response = await fetch('http://localhost:8000/api/flashcards/generate/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        topic: 'Indian Constitutional Law',
        num_cards: 5,
        language: 'english'
      })
    });
    
    const data = await response.json();
    console.log('Flashcards (English):', data);
    if (data.success) {
      console.log('Total cards:', data.data.total_cards);
      console.log('First card:', data.data.flashcards[0]);
    } else {
      console.error('Error:', data.error);
    }
  } catch (error) {
    console.error('Fetch error:', error);
  }
}

testFlashcardsEnglish();
```

### 4.4 Flashcards - Hindi (JavaScript)

```javascript
// Test Flashcards generation - Hindi
async function testFlashcardsHindi() {
  try {
    const response = await fetch('http://localhost:8000/api/flashcards/generate/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        topic: 'भारतीय संविधान',
        num_cards: 5,
        language: 'hindi'
      })
    });
    
    const data = await response.json();
    console.log('Flashcards (Hindi):', data);
    if (data.success) {
      console.log('First card (Hindi):', data.data.flashcards[0].question);
    }
  } catch (error) {
    console.error('Fetch error:', error);
  }
}

testFlashcardsHindi();
```

### 4.5 Predicted Questions - English (JavaScript)

```javascript
// Test Predicted Questions - English
async function testPredictedQuestionsEnglish() {
  try {
    const response = await fetch('http://localhost:8000/api/predicted-questions/generate/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        topic: 'Indian Polity and Constitutional Law',
        exam_type: 'UPSC',
        num_questions: 3,
        language: 'english'
      })
    });
    
    const data = await response.json();
    console.log('Predicted Questions (English):', data);
    if (data.success) {
      console.log('Total questions:', data.data.total_questions);
      console.log('First question:', data.data.questions[0].question);
    } else {
      console.error('Error:', data.error);
    }
  } catch (error) {
    console.error('Fetch error:', error);
  }
}

testPredictedQuestionsEnglish();
```

### 4.6 Predicted Questions - Hindi (JavaScript)

```javascript
// Test Predicted Questions - Hindi
async function testPredictedQuestionsHindi() {
  try {
    const response = await fetch('http://localhost:8000/api/predicted-questions/generate/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        topic: 'भारतीय राजनीति और संविधान कानून',
        exam_type: 'UPSC',
        num_questions: 3,
        language: 'hindi'
      })
    });
    
    const data = await response.json();
    console.log('Predicted Questions (Hindi):', data);
    if (data.success) {
      console.log('First question (Hindi):', data.data.questions[0].question);
    }
  } catch (error) {
    console.error('Fetch error:', error);
  }
}

testPredictedQuestionsHindi();
```

### 4.7 Error Handling Test (JavaScript)

```javascript
// Test 400 error handling - Missing topic
async function testErrorHandling() {
  try {
    const response = await fetch('http://localhost:8000/api/predicted-questions/generate/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        exam_type: 'UPSC',
        num_questions: 5,
        language: 'english'
      })
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      console.log('Status Code:', response.status);
      console.log('Error Message:', data.error);
      console.log('Helpful Message:', data.message);
      console.log('Supported Formats:', data.supported_formats);
    }
  } catch (error) {
    console.error('Fetch error:', error);
  }
}

testErrorHandling();
```

### 4.8 Document Upload Test (JavaScript)

```javascript
// Test document upload for predicted questions
async function testDocumentUpload(filePath) {
  try {
    const fileInput = document.getElementById('documentInput');
    const file = fileInput.files[0];
    
    const formData = new FormData();
    formData.append('document', file);
    formData.append('exam_type', 'UPSC');
    formData.append('num_questions', 5);
    formData.append('language', 'english');
    
    const response = await fetch('http://localhost:8000/api/predicted-questions/generate/', {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    console.log('Response:', data);
    
    if (!response.ok) {
      console.error('Error:', data.error);
      console.error('Details:', data.details);
    } else {
      console.log('Questions generated:', data.data.total_questions);
    }
  } catch (error) {
    console.error('Fetch error:', error);
  }
}

// Usage: Attach to file input change event
// document.getElementById('documentInput').addEventListener('change', testDocumentUpload);
```

---

## 5. Bash Testing Matrix

### 5.1 Complete Testing Script

```bash
#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
LOCAL_URL="http://localhost:8000"
PROD_URL="https://ed-tech-backend-tzn8.onrender.com"
TIMEOUT=10

# Counters
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function for HTTP requests
test_endpoint() {
  local method=$1
  local endpoint=$2
  local data=$3
  local expected_status=$4
  local env=$5
  
  if [ "$env" = "prod" ]; then
    URL=$PROD_URL
  else
    URL=$LOCAL_URL
  fi
  
  echo -e "${BLUE}Testing: ${method} ${endpoint}${NC}"
  
  if [ "$method" = "POST" ]; then
    response=$(curl -s -w "\n%{http_code}" -X POST "${URL}${endpoint}" \
      -H "Content-Type: application/json" \
      -d "$data" \
      --connect-timeout $TIMEOUT)
  else
    response=$(curl -s -w "\n%{http_code}" -X GET "${URL}${endpoint}" \
      --connect-timeout $TIMEOUT)
  fi
  
  status_code=$(echo "$response" | tail -n 1)
  body=$(echo "$response" | head -n -1)
  
  if [ "$status_code" = "$expected_status" ]; then
    echo -e "${GREEN}✓ PASS${NC} (Status: $status_code)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗ FAIL${NC} (Expected: $expected_status, Got: $status_code)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
  
  echo "Response: $body" | jq '.' 2>/dev/null || echo "Response: $body"
  echo ""
}

# Run tests
echo -e "${YELLOW}=== Starting Comprehensive Language Endpoints Testing ===${NC}\n"

# Daily Quiz Tests
echo -e "${YELLOW}--- Daily Quiz Tests (Local) ---${NC}"
test_endpoint "GET" "/api/daily-quiz/?language=english&user_id=test" "" "200" "local"
test_endpoint "GET" "/api/daily-quiz/?language=hindi&user_id=test" "" "200" "local"

# Flashcards Tests
echo -e "${YELLOW}--- Flashcards Tests (Local) ---${NC}"
test_endpoint "POST" "/api/flashcards/generate/" '{"topic":"Indian Constitution","num_cards":5,"language":"english"}' "200" "local"
test_endpoint "POST" "/api/flashcards/generate/" '{"topic":"भारतीय संविधान","num_cards":5,"language":"hindi"}' "200" "local"
test_endpoint "POST" "/api/flashcards/generate/" '{"num_cards":5,"language":"english"}' "400" "local"

# Predicted Questions Tests
echo -e "${YELLOW}--- Predicted Questions Tests (Local) ---${NC}"
test_endpoint "POST" "/api/predicted-questions/generate/" '{"topic":"Indian Constitution","exam_type":"UPSC","num_questions":3,"language":"english"}' "200" "local"
test_endpoint "POST" "/api/predicted-questions/generate/" '{"topic":"भारतीय संविधान","exam_type":"UPSC","num_questions":3,"language":"hindi"}' "200" "local"
test_endpoint "POST" "/api/predicted-questions/generate/" '{"exam_type":"UPSC","num_questions":3,"language":"english"}' "400" "local"

# Production Tests
echo -e "${YELLOW}--- Production Tests ---${NC}"
test_endpoint "GET" "/api/daily-quiz/?language=english&user_id=test" "" "200" "prod"
test_endpoint "GET" "/api/daily-quiz/?language=hindi&user_id=test" "" "200" "prod"
test_endpoint "POST" "/api/predicted-questions/generate/" '{"exam_type":"UPSC","num_questions":3}' "400" "prod"

# Summary
echo -e "${YELLOW}=== Test Summary ===${NC}"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
  echo -e "${GREEN}✓ All tests passed!${NC}"
else
  echo -e "${RED}✗ Some tests failed${NC}"
fi
```

### 5.2 Quick Test (5 minute check)

```bash
#!/bin/bash

echo "=== Quick Language Endpoints Test ==="
echo ""

# 1. Daily Quiz English
echo "1. Daily Quiz (English):"
curl -s "http://localhost:8000/api/daily-quiz/?language=english&user_id=test" | jq '.success'

# 2. Daily Quiz Hindi
echo "2. Daily Quiz (Hindi):"
curl -s "http://localhost:8000/api/daily-quiz/?language=hindi&user_id=test" | jq '.success'

# 3. Flashcards English
echo "3. Flashcards (English):"
curl -s -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{"topic":"Indian Constitution","num_cards":3,"language":"english"}' | jq '.success'

# 4. Flashcards Hindi
echo "4. Flashcards (Hindi):"
curl -s -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{"topic":"भारतीय संविधान","num_cards":3,"language":"hindi"}' | jq '.success'

# 5. Predicted Questions Error Test (400)
echo "5. Predicted Questions (Missing Topic - should be 400):"
curl -s -w "\nStatus: %{http_code}\n" -X POST "http://localhost:8000/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -d '{"exam_type":"UPSC"}' | jq '.error'

echo ""
echo "=== Quick Test Complete ==="
```

---

## 6. Verification Checklist

### ✅ Local Testing Checklist

- [ ] Daily Quiz English (GET /api/daily-quiz/?language=english)
- [ ] Daily Quiz Hindi (GET /api/daily-quiz/?language=hindi)
- [ ] Daily Quiz Default (GET /api/daily-quiz/ - should default to English)
- [ ] Flashcards English (POST /api/flashcards/generate/)
- [ ] Flashcards Hindi (POST /api/flashcards/generate/)
- [ ] Flashcards Missing Topic (400 error)
- [ ] Predicted Questions English with Topic (200 OK)
- [ ] Predicted Questions Hindi with Topic (200 OK)
- [ ] Predicted Questions Missing Topic (400 error - FIXED)
- [ ] Predicted Questions with PDF Upload (200 OK)
- [ ] Predicted Questions with Image Upload (200 OK)
- [ ] Predicted Questions Invalid Language (400 or 200 with default)

### ✅ Production Testing Checklist

- [ ] Daily Quiz English on production
- [ ] Daily Quiz Hindi on production
- [ ] Flashcards English on production
- [ ] Flashcards Hindi on production
- [ ] Predicted Questions with valid topic on production
- [ ] **Predicted Questions Missing Topic on production (should return 400 with helpful message)**
- [ ] Response times < 3 seconds

### ✅ Error Handling Checklist

- [ ] 400 error for missing topic/document (has helpful message)
- [ ] 400 error for unsupported document type
- [ ] 400 error for empty document
- [ ] 400 error for missing topic in flashcards
- [ ] 500 error for Gemini API failures (has helpful message)
- [ ] All error responses have 'success': false
- [ ] All error responses have 'error' field
- [ ] All error responses have 'message' field with helpful info

---

## 7. Production Deployment Steps

### Before Deployment

1. **Run all local tests**
   ```bash
   bash LANGUAGE_ENDPOINTS_COMPREHENSIVE_TESTING.md # Run test script
   ```

2. **Verify error handling**
   ```bash
   # Test missing topic error
   curl -X POST "http://localhost:8000/api/predicted-questions/generate/" \
     -H "Content-Type: application/json" \
     -d '{"exam_type":"UPSC","num_questions":5}'
   
   # Should return 400 with helpful message
   ```

3. **Check logs**
   ```bash
   tail -f logs/django.log  # Monitor for errors
   ```

### Deployment

```bash
# 1. Commit changes
git add .
git commit -m "Fix: Language support for all endpoints + 400 error handling"

# 2. Push to production
git push origin main

# 3. Render.com will auto-deploy

# 4. Monitor deployment
# Check https://dashboard.render.com
```

### Post-Deployment Verification

```bash
# Test production endpoints
curl -X POST "https://ed-tech-backend-tzn8.onrender.com/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -d '{"exam_type":"UPSC","num_questions":5}'

# Expected: 400 Bad Request with helpful message

# Test with valid topic
curl -X POST "https://ed-tech-backend-tzn8.onrender.com/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -d '{"topic":"Indian Constitution","exam_type":"UPSC","num_questions":5,"language":"english"}'

# Expected: 200 OK with generated questions
```

---

## 8. Summary

| Endpoint | English | Hindi | Error Handling | Document Upload |
|----------|---------|-------|-----------------|-----------------|
| Daily Quiz | ✓ | ✓ | Query param validation | N/A |
| Flashcards | ✓ | ✓ | Topic required | N/A |
| Predicted Questions | ✓ | ✓ | 400 if no topic/doc | ✓ PDF, TXT, Images |

**Critical Fix:** 
- **Before:** POST /api/predicted-questions/generate/ returns 500 or unclear 400
- **After:** Returns clear 400 with "Please provide either a topic or document" message

All endpoints now support both English and Hindi with proper validation and error messages!

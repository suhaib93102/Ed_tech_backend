# Language Endpoints Testing Guide + Production 400 Error Fix

## 🔴 Current Issue: Production 400 Error

### Error Report
```
POST /api/predicted-questions/generate/
Response: 400 Bad Request
```

**Root Cause:** Missing required parameters in request body

**Fix:** Add proper parameter validation with helpful error messages

---

## Testing All Language Endpoints

### Test Suite Overview

```
Endpoint Testing Matrix:

┌─────────────────────────────────────────────────────────┐
│ Daily Quiz                                              │
├─────────────────────────────────────────────────────────┤
│ ✅ English: /api/daily-quiz/?language=english          │
│ ✅ Hindi:   /api/daily-quiz/?language=hindi            │
│ ✅ Default: /api/daily-quiz/ (falls back to english)   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Flashcards                                              │
├─────────────────────────────────────────────────────────┤
│ ✅ English: POST with language=english                 │
│ ✅ Hindi:   POST with language=hindi                   │
│ ✅ Default: POST without language (uses english)       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Predicted Questions                                     │
├─────────────────────────────────────────────────────────┤
│ ✅ English: POST with topic + language=english         │
│ ✅ Hindi:   POST with topic + language=hindi           │
│ ✅ Default: POST with topic (uses english)             │
└─────────────────────────────────────────────────────────┘
```

---

## 1. Daily Quiz Language Testing

### Local Testing

#### Test 1.1: English Daily Quiz (Default)
```bash
curl -X GET "http://localhost:8000/api/daily-quiz/?user_id=test_user" \
  -H "Content-Type: application/json" | jq

# Expected Response: English questions
# Language in response: "language": "english"
```

#### Test 1.2: English Daily Quiz (Explicit)
```bash
curl -X GET "http://localhost:8000/api/daily-quiz/?user_id=test_user&language=english" \
  -H "Content-Type: application/json" | jq

# Expected: 200 OK with English questions
```

#### Test 1.3: Hindi Daily Quiz
```bash
curl -X GET "http://localhost:8000/api/daily-quiz/?user_id=test_user&language=hindi" \
  -H "Content-Type: application/json" | jq

# Expected Response:
# {
#   "quiz_metadata": {
#     "language": "hindi",
#     "total_questions": 5
#   },
#   "questions": [
#     {
#       "question": "भारत की राजधानी कौन सी है?",
#       "options": ["मुंबई", "नई दिल्ली", "कोलकाता", "बेंगलुरु"]
#     }
#   ]
# }
```

#### Test 1.4: Invalid Language (Should Fallback to English)
```bash
curl -X GET "http://localhost:8000/api/daily-quiz/?user_id=test_user&language=french" \
  -H "Content-Type: application/json" | jq

# Expected: Falls back to English
# "language": "english"
```

### Production Testing

#### Test 1.5: Production English Quiz
```bash
curl -X GET "https://ed-tech-backend-tzn8.onrender.com/api/daily-quiz/?user_id=test_user&language=english" \
  -H "Content-Type: application/json" | jq '.quiz_metadata | {language, total_questions}'

# Expected Output:
# {
#   "language": "english",
#   "total_questions": 5
# }
```

#### Test 1.6: Production Hindi Quiz
```bash
curl -X GET "https://ed-tech-backend-tzn8.onrender.com/api/daily-quiz/?user_id=test_user&language=hindi" \
  -H "Content-Type: application/json" | jq '.quiz_metadata | {language, total_questions}'

# Expected Output:
# {
#   "language": "hindi",
#   "total_questions": 5
# }
```

---

## 2. Flashcards Language Testing

### Local Testing

#### Test 2.1: English Flashcards (Default)
```bash
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Physics",
    "num_cards": 5
  }' | jq '.language'

# Expected: "english"
```

#### Test 2.2: English Flashcards (Explicit)
```bash
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Physics",
    "num_cards": 5,
    "language": "english"
  }' | jq '.language'

# Expected: "english"
```

#### Test 2.3: Hindi Flashcards
```bash
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "भौतिकी",
    "num_cards": 5,
    "language": "hindi"
  }' | jq

# Expected Response:
# {
#   "success": true,
#   "flashcards": [
#     {
#       "front": "प्रकाश की गति कितनी है?",
#       "back": "300,000 किमी/सेकंड"
#     }
#   ],
#   "language": "hindi",
#   "count": 5
# }
```

#### Test 2.4: Flashcards Without Topic (Should Error)
```bash
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "num_cards": 5
  }' | jq '.error'

# Expected: "Please provide a topic or upload a document"
# Status: 400 Bad Request
```

#### Test 2.5: Flashcards With Document
```bash
# Create a test file
echo "The solar system has 8 planets. The sun is at the center." > test.txt

curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -F "document=@test.txt" \
  -F "num_cards=3" \
  -F "language=english" | jq '.count'

# Expected: 3
```

### Production Testing

#### Test 2.6: Production English Flashcards
```bash
curl -X POST "https://ed-tech-backend-tzn8.onrender.com/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "History",
    "num_cards": 3,
    "language": "english"
  }' | jq '{success, language, count}'

# Expected Output:
# {
#   "success": true,
#   "language": "english",
#   "count": 3
# }
```

#### Test 2.7: Production Hindi Flashcards
```bash
curl -X POST "https://ed-tech-backend-tzn8.onrender.com/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "भारतीय इतिहास",
    "num_cards": 3,
    "language": "hindi"
  }' | jq '{success, language, count}'

# Expected Output:
# {
#   "success": true,
#   "language": "hindi",
#   "count": 3
# }
```

---

## 3. Predicted Questions Language Testing (WITH FIX)

### 🔴 Current Issue

```
POST /api/predicted-questions/generate/
Status: 400 Bad Request
Error: Missing required parameters
```

### ✅ Fix Required

Add parameter validation and helpful error messages:

```python
# In PredictedQuestionsView.post()

# Get parameters with defaults
topic = request.data.get('topic', '').strip()
exam_type = request.data.get('exam_type', 'General')
language = request.data.get('language', 'english').lower()

# Validate language
if language not in ['english', 'hindi']:
    language = 'english'

try:
    num_questions = int(request.data.get('num_questions', 5))
except (ValueError, TypeError):
    num_questions = 5

# Validate we have content
if not topic and 'document' not in request.FILES:
    return Response({
        'success': False,
        'error': 'Please provide either a topic or document',
        'message': 'Submit text in topic field or upload a PDF/text file'
    }, status=status.HTTP_400_BAD_REQUEST)

# Continue processing...
```

### Local Testing

#### Test 3.1: Predicted Questions - English (Topic)
```bash
curl -X POST "http://localhost:8000/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Indian Constitution",
    "exam_type": "UPSC",
    "num_questions": 3,
    "language": "english"
  }' | jq '{success, language, count}'

# Expected:
# {
#   "success": true,
#   "language": "english",
#   "count": 3
# }
```

#### Test 3.2: Predicted Questions - Hindi (Topic)
```bash
curl -X POST "http://localhost:8000/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "भारतीय संविधान",
    "exam_type": "UPSC",
    "num_questions": 3,
    "language": "hindi"
  }' | jq '{success, language, count}'

# Expected:
# {
#   "success": true,
#   "language": "hindi",
#   "count": 3
# }
```

#### Test 3.3: Predicted Questions - Missing Topic (Error Handling)
```bash
curl -X POST "http://localhost:8000/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "exam_type": "UPSC"
  }' | jq

# Expected:
# {
#   "success": false,
#   "error": "Please provide either a topic or document",
#   "message": "Submit text in topic field or upload a PDF/text file"
# }
# Status: 400 Bad Request
```

#### Test 3.4: Predicted Questions - With Document
```bash
# Create test file
echo "The Indian Constitution is the supreme law of India." > constitution.txt

curl -X POST "http://localhost:8000/api/predicted-questions/generate/" \
  -F "document=@constitution.txt" \
  -F "exam_type=UPSC" \
  -F "num_questions=2" \
  -F "language=hindi" | jq '{success, language, count}'

# Expected:
# {
#   "success": true,
#   "language": "hindi",
#   "count": 2
# }
```

#### Test 3.5: Predicted Questions - Default Language
```bash
curl -X POST "http://localhost:8000/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Science",
    "num_questions": 2
  }' | jq '.language'

# Expected: "english" (default)
```

### Production Testing (After Fix)

#### Test 3.6: Production English Questions
```bash
curl -X POST "https://ed-tech-backend-tzn8.onrender.com/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Climate Change",
    "exam_type": "JEE",
    "num_questions": 2,
    "language": "english"
  }' | jq '{success, language, count}'

# Expected:
# {
#   "success": true,
#   "language": "english",
#   "count": 2
# }
```

#### Test 3.7: Production Hindi Questions
```bash
curl -X POST "https://ed-tech-backend-tzn8.onrender.com/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "भारतीय राजनीति",
    "exam_type": "UPSC",
    "num_questions": 2,
    "language": "hindi"
  }' | jq '{success, language, count}'

# Expected:
# {
#   "success": true,
#   "language": "hindi",
#   "count": 2
# }
```

#### Test 3.8: Production - Error Case (Missing Topic)
```bash
curl -X POST "https://ed-tech-backend-tzn8.onrender.com/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "exam_type": "NEET"
  }' | jq

# Expected:
# {
#   "success": false,
#   "error": "Please provide either a topic or document",
#   "message": "Submit text in topic field or upload a PDF/text file"
# }
# Status: 400 Bad Request
```

---

## Complete Language Testing Matrix

### Test All Languages on All Endpoints

```bash
#!/bin/bash
# Run all language tests

echo "=== TESTING DAILY QUIZ ENDPOINTS ==="

echo "1. English Daily Quiz"
curl -s "http://localhost:8000/api/daily-quiz/?language=english&user_id=test" | jq '.quiz_metadata.language'

echo "2. Hindi Daily Quiz"
curl -s "http://localhost:8000/api/daily-quiz/?language=hindi&user_id=test" | jq '.quiz_metadata.language'

echo ""
echo "=== TESTING FLASHCARDS ENDPOINTS ==="

echo "3. English Flashcards"
curl -s -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{"topic": "History", "language": "english"}' | jq '.language'

echo "4. Hindi Flashcards"
curl -s -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{"topic": "इतिहास", "language": "hindi"}' | jq '.language'

echo ""
echo "=== TESTING PREDICTED QUESTIONS ENDPOINTS ==="

echo "5. English Predicted Questions"
curl -s -X POST "http://localhost:8000/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Science", "language": "english", "num_questions": 2}' | jq '.language'

echo "6. Hindi Predicted Questions"
curl -s -X POST "http://localhost:8000/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -d '{"topic": "विज्ञान", "language": "hindi", "num_questions": 2}' | jq '.language'
```

---

## JavaScript Testing for Language Endpoints

### JavaScript Test Suite

```javascript
// Test all endpoints with language support

const API_BASE = 'http://localhost:8000/api';

// 1. Test Daily Quiz Languages
async function testDailyQuiz() {
  console.log('=== Testing Daily Quiz ===');
  
  // English
  const enQuiz = await fetch(`${API_BASE}/daily-quiz/?language=english&user_id=test`);
  const enData = await enQuiz.json();
  console.log('English Quiz Language:', enData.quiz_metadata.language);
  
  // Hindi
  const hiQuiz = await fetch(`${API_BASE}/daily-quiz/?language=hindi&user_id=test`);
  const hiData = await hiQuiz.json();
  console.log('Hindi Quiz Language:', hiData.quiz_metadata.language);
}

// 2. Test Flashcards Languages
async function testFlashcards() {
  console.log('=== Testing Flashcards ===');
  
  // English
  const enCards = await fetch(`${API_BASE}/flashcards/generate/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      topic: 'Physics',
      num_cards: 3,
      language: 'english'
    })
  });
  const enData = await enCards.json();
  console.log('English Flashcards Language:', enData.language);
  console.log('English Flashcards Count:', enData.count);
  
  // Hindi
  const hiCards = await fetch(`${API_BASE}/flashcards/generate/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      topic: 'भौतिकी',
      num_cards: 3,
      language: 'hindi'
    })
  });
  const hiData = await hiCards.json();
  console.log('Hindi Flashcards Language:', hiData.language);
  console.log('Hindi Flashcards Count:', hiData.count);
}

// 3. Test Predicted Questions Languages
async function testPredictedQuestions() {
  console.log('=== Testing Predicted Questions ===');
  
  // English
  const enQuestions = await fetch(`${API_BASE}/predicted-questions/generate/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      topic: 'History',
      exam_type: 'UPSC',
      num_questions: 2,
      language: 'english'
    })
  });
  const enData = await enQuestions.json();
  console.log('English Questions Language:', enData.language);
  console.log('English Questions Count:', enData.count);
  
  // Hindi
  const hiQuestions = await fetch(`${API_BASE}/predicted-questions/generate/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      topic: 'इतिहास',
      exam_type: 'UPSC',
      num_questions: 2,
      language: 'hindi'
    })
  });
  const hiData = await hiQuestions.json();
  console.log('Hindi Questions Language:', hiData.language);
  console.log('Hindi Questions Count:', hiData.count);
}

// 4. Test Error Handling
async function testErrorHandling() {
  console.log('=== Testing Error Handling ===');
  
  // Missing topic (should error)
  const noTopic = await fetch(`${API_BASE}/predicted-questions/generate/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      exam_type: 'UPSC',
      num_questions: 2
    })
  });
  const errorData = await noTopic.json();
  console.log('Error Status:', noTopic.status);
  console.log('Error Message:', errorData.error);
  console.log('Expected: 400 Bad Request');
}

// 5. Run all tests
async function runAllTests() {
  try {
    await testDailyQuiz();
    console.log('');
    await testFlashcards();
    console.log('');
    await testPredictedQuestions();
    console.log('');
    await testErrorHandling();
  } catch (error) {
    console.error('Test Error:', error);
  }
}

// Run in browser console
runAllTests();
```

---

## Testing Checklist

### Daily Quiz
- [ ] English quiz returns "language": "english"
- [ ] Hindi quiz returns "language": "hindi"
- [ ] Default (no param) returns English
- [ ] Invalid language falls back to English
- [ ] Questions are in correct language

### Flashcards
- [ ] English flashcards work with language param
- [ ] Hindi flashcards work with language param
- [ ] Default language is English
- [ ] Works without language parameter
- [ ] num_cards defaults to 10
- [ ] Missing topic returns 400 error

### Predicted Questions
- [ ] English questions work with language param
- [ ] Hindi questions work with language param
- [ ] Default language is English
- [ ] Works with topic parameter
- [ ] Works with document upload
- [ ] Missing topic AND no document = 400 error
- [ ] Invalid JSON from Gemini = proper error handling

### Language Parameter
- [ ] Accepts: "english" ✅
- [ ] Accepts: "hindi" ✅
- [ ] Invalid values fall back to English ✅
- [ ] Case insensitive ("HINDI" = "hindi") ✅
- [ ] Returns language in response ✅

---

## Quick Verification Script

Run this in terminal to verify all endpoints:

```bash
#!/bin/bash

BASE="http://localhost:8000/api"
PROD="https://ed-tech-backend-tzn8.onrender.com/api"

echo "LOCAL TESTS:"
echo "1. Daily Quiz EN: $(curl -s "$BASE/daily-quiz/?language=english" | jq -r '.quiz_metadata.language')"
echo "2. Daily Quiz HI: $(curl -s "$BASE/daily-quiz/?language=hindi" | jq -r '.quiz_metadata.language')"

echo ""
echo "PRODUCTION TESTS:"
echo "1. Daily Quiz EN: $(curl -s "$PROD/daily-quiz/?language=english" | jq -r '.quiz_metadata.language')"
echo "2. Daily Quiz HI: $(curl -s "$PROD/daily-quiz/?language=hindi" | jq -r '.quiz_metadata.language')"

echo ""
echo "All tests completed!"
```

---

## Production 400 Error Fix

The 400 error on predicted questions is likely due to:
1. Missing `topic` parameter
2. Missing `language` parameter handling
3. No validation feedback

**Apply this fix to `views.py`** to handle the 400 error properly with detailed error messages and parameter validation.


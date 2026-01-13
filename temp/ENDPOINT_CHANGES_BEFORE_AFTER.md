# API Endpoints - Before & After

## Daily Quiz Endpoint

### Before
```
GET /api/daily-quiz/?user_id=abc123
```

**Request Parameters:**
- user_id (required)

**Response (English Only):**
```json
{
  "quiz_metadata": {
    "language": "english",
    "total_questions": 5,
    "questions": [
      {
        "question": "What is the capital of India?",
        "options": ["Mumbai", "Delhi", "Kolkata", "Bangalore"],
        "category": "geography"
      }
    ]
  }
}
```

### After
```
GET /api/daily-quiz/?user_id=abc123&language=hindi
```

**Request Parameters:**
- user_id (required)
- language (optional: "english" or "hindi", default: "english")

**Response (English):**
```json
{
  "quiz_metadata": {
    "language": "english",
    "total_questions": 5,
    "questions": [...]
  }
}
```

**Response (Hindi):**
```json
{
  "quiz_metadata": {
    "language": "hindi",
    "total_questions": 5,
    "questions": [
      {
        "question": "भारत की राजधानी कौन सी है?",
        "options": ["मुंबई", "नई दिल्ली", "कोलकाता", "बेंगलुरु"],
        "category": "geography"
      }
    ]
  }
}
```

---

## Flashcards Endpoint

### Before
```
POST /api/flashcards/generate/
```

**Request Body:**
```json
{
  "topic": "History"
}
```

**Response:**
```
400 Bad Request - Missing required parameter: num_cards
```

### After
```
POST /api/flashcards/generate/
```

**Request Body (With Explicit Parameter):**
```json
{
  "topic": "History",
  "num_cards": 10,
  "language": "english"
}
```

**Request Body (With Defaults):**
```json
{
  "topic": "History"
  // num_cards defaults to 10
  // language defaults to "english"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "flashcards": [
    {
      "front": "Who was the first President of India?",
      "back": "Dr. Rajendra Prasad"
    },
    ...
  ],
  "count": 10,
  "language": "english"
}
```

**Hindi Response:**
```json
{
  "success": true,
  "flashcards": [
    {
      "front": "भारत के पहले राष्ट्रपति कौन थे?",
      "back": "डॉ राजेंद्र प्रसाद"
    }
  ],
  "count": 10,
  "language": "hindi"
}
```

**Error Response (400):**
```json
{
  "success": false,
  "error": "Please provide a topic or upload a document",
  "message": "Either submit text in the topic field or upload a file"
}
```

---

## Predicted Questions Endpoint

### Before
```
POST /api/predicted-questions/generate/
```

**Request Body:**
```json
{
  "topic": "Constitutional Law",
  "exam_type": "UPSC",
  "num_questions": 5
}
```

**Response:**
```
500 Internal Server Error - Failed to parse AI response
```

### After
```
POST /api/predicted-questions/generate/
```

**Request Body:**
```json
{
  "topic": "Constitutional Law",
  "exam_type": "UPSC",
  "num_questions": 5,
  "language": "hindi"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "title": "Constitutional Law",
  "summary": "Overview of constitutional topics",
  "questions": [
    {
      "question": "भारतीय संविधान कब लागू हुआ?",
      "options": [
        {"text": "15 अगस्त 1947"},
        {"text": "26 जनवरी 1950"},
        {"text": "26 जनवरी 1951"},
        {"text": "14 अगस्त 1949"}
      ],
      "correct_answer": "26 जनवरी 1950",
      "explanation": "भारतीय संविधान 26 जनवरी 1950 को लागू किया गया।",
      "difficulty": "medium"
    }
  ],
  "count": 5,
  "language": "hindi"
}
```

**Error Response (400):**
```json
{
  "success": false,
  "error": "Please provide either a topic or document",
  "message": "Submit text in topic field or upload a document file"
}
```

**Error Response (500) - Now Fixed:**
```json
{
  "success": false,
  "error": "Failed to parse AI response",
  "details": "Please try again with different input"
}
```

---

## Complete Request/Response Examples

### Example 1: Get Hindi Daily Quiz

**Request:**
```bash
curl -X GET "http://localhost:8000/api/daily-quiz/?user_id=student_123&language=hindi" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: student_123"
```

**Response:**
```json
{
  "quiz_metadata": {
    "quiz_type": "daily_coin_quiz",
    "total_questions": 5,
    "difficulty": "medium",
    "date": "2026-01-10",
    "language": "hindi",
    "title": "Daily GK Quiz - January 10, 2026",
    "description": "Test your general knowledge with AI-generated questions!"
  },
  "coins": {
    "attempt_bonus": 10,
    "per_correct_answer": 5,
    "max_possible": 35
  },
  "questions": [
    {
      "id": 1,
      "question": "भारत की राजधानी कौन सी है?",
      "options": ["मुंबई", "नई दिल्ली", "कोलकाता", "बेंगलुरु"],
      "category": "geography",
      "difficulty": "easy"
    },
    {
      "id": 2,
      "question": "गंगा नदी की लंबाई कितनी है?",
      "options": ["1500 किमी", "2000 किमी", "2525 किमी", "3000 किमी"],
      "category": "geography",
      "difficulty": "medium"
    }
  ],
  "quiz_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Example 2: Generate Hindi Flashcards

**Request:**
```bash
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: student_123" \
  -d '{
    "topic": "भारतीय स्वतंत्रता संग्राम",
    "num_cards": 5,
    "language": "hindi"
  }'
```

**Response:**
```json
{
  "success": true,
  "flashcards": [
    {
      "front": "महात्मा गांधी का जन्म कहाँ हुआ था?",
      "back": "पोरबंदर, गुजरात में"
    },
    {
      "front": "भारत को स्वतंत्रता कब मिली?",
      "back": "15 अगस्त 1947"
    },
    {
      "front": "राष्ट्रगीत 'जन गण मन' के रचयिता कौन हैं?",
      "back": "रवीन्द्रनाथ टैगोर"
    },
    {
      "front": "आजाद हिंद फौज के संस्थापक कौन थे?",
      "back": "सुभाष चंद्र बोस"
    },
    {
      "front": "भारतीय राष्ट्रीय कांग्रेस की स्थापना कब हुई?",
      "back": "1885 में"
    }
  ],
  "count": 5,
  "language": "hindi"
}
```

### Example 3: Generate Predicted Questions

**Request:**
```bash
curl -X POST "http://localhost:8000/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: student_123" \
  -d '{
    "topic": "भारतीय संविधान",
    "exam_type": "UPSC",
    "num_questions": 3,
    "language": "hindi"
  }'
```

**Response:**
```json
{
  "success": true,
  "title": "भारतीय संविधान",
  "summary": "भारतीय संविधान विश्व का सबसे लंबा संविधान है।",
  "questions": [
    {
      "question": "भारतीय संविधान कब लागू हुआ?",
      "options": [
        {"text": "15 अगस्त 1947"},
        {"text": "26 जनवरी 1950"},
        {"text": "26 जनवरी 1951"},
        {"text": "14 अगस्त 1949"}
      ],
      "correct_answer": "26 जनवरी 1950",
      "explanation": "भारतीय संविधान 26 जनवरी 1950 को लागू किया गया।",
      "difficulty": "easy"
    },
    {
      "question": "भारतीय संविधान के मुख्य संरचक कौन थे?",
      "options": [
        {"text": "डॉ भीमराव अंबेडकर"},
        {"text": "पंडित नेहरू"},
        {"text": "सरदार पटेल"},
        {"text": "राजेंद्र प्रसाद"}
      ],
      "correct_answer": "डॉ भीमराव अंबेडकर",
      "explanation": "डॉ भीमराव अंबेडकर को संविधान निर्मातृ समिति का अध्यक्ष नियुक्त किया गया था।",
      "difficulty": "medium"
    },
    {
      "question": "भारतीय संविधान में कितने भाग हैं?",
      "options": [
        {"text": "20"},
        {"text": "22"},
        {"text": "25"},
        {"text": "30"}
      ],
      "correct_answer": "22",
      "explanation": "भारतीय संविधान में 22 भाग हैं।",
      "difficulty": "medium"
    }
  ],
  "count": 3,
  "language": "hindi"
}
```

---

## JavaScript Frontend Code

### Fetch Hindi Quiz
```javascript
async function getHindiQuiz(userId) {
  const response = await fetch(
    `http://localhost:8000/api/daily-quiz/?user_id=${userId}&language=hindi`,
    {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-User-ID': userId
      },
      mode: 'cors'
    }
  );
  
  if (!response.ok) {
    console.error('Error:', response.status);
    return null;
  }
  
  return await response.json();
}

// Usage
const quiz = await getHindiQuiz('student_123');
console.log(quiz.questions);
```

### Generate Hindi Flashcards
```javascript
async function generateHindiFlashcards(topic, userId) {
  const response = await fetch(
    'http://localhost:8000/api/flashcards/generate/',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-ID': userId
      },
      mode: 'cors',
      body: JSON.stringify({
        topic: topic,
        num_cards: 10,
        language: 'hindi'
      })
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    console.error('Error:', error);
    return null;
  }
  
  return await response.json();
}

// Usage
const flashcards = await generateHindiFlashcards('भारतीय इतिहास', 'student_123');
console.log(flashcards.flashcards);
```

---

## Summary Table

| Feature | Before | After |
|---------|--------|-------|
| Language Support | English only | English + Hindi |
| Daily Quiz | 1 per day | 1 per day per language |
| Flashcards `num_cards` | Required | Optional (default: 10) |
| Error Handling | Generic 500 errors | Specific error messages |
| Validation | Minimal | Comprehensive |
| Parameter Docs | Incomplete | Complete with examples |

---

## Deployment Checklist

- [ ] Update `gemini_service.py` with language parameter
- [ ] Update `daily_quiz_views.py` to accept language
- [ ] Update DailyQuiz model with language field
- [ ] Update FlashcardGeneratorView with defaults
- [ ] Update PredictedQuestionsView with error handling
- [ ] Run: `python manage.py makemigrations`
- [ ] Run: `python manage.py migrate`
- [ ] Test locally with curl commands
- [ ] Deploy to Render
- [ ] Verify production with curl
- [ ] Update frontend code with new parameter

---

**Status**: Documentation Complete ✅
**Next Step**: Apply code changes to your repository

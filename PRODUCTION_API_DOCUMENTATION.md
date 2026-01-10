# 📚 PRODUCTION API DOCUMENTATION

**Version**: 1.0.0  
**Environment**: Production Ready  
**Base URL**: `http://localhost:8003/api`  
**Last Updated**: January 10, 2026

---

## Table of Contents

1. [Daily Quiz Endpoints](#1-daily-quiz-endpoints)
2. [Flashcards Endpoints](#2-flashcards-endpoints)
3. [Predicted Questions Endpoints](#3-predicted-questions-endpoints)
4. [Study Material Endpoints](#4-study-material-endpoints)
5. [YouTube Summarizer](#5-youtube-summarizer)
6. [Usage Dashboard](#6-usage-dashboard)
7. [Error Handling](#7-error-handling)
8. [Response Formats](#8-response-formats)

---

## 1. Daily Quiz Endpoints

### 1.1 Get Daily Quiz (Hindi or English)

**Endpoint:**
```
GET /api/daily-quiz/
```

**Parameters:**
```
?language=hindi|english  (Default: english)
&user_id=STRING         (Required)
```

**cURL Command:**
```bash
# Get Hindi Quiz
curl -X GET "http://localhost:8003/api/daily-quiz/?language=hindi&user_id=rahuljha996886" \
  -H "Content-Type: application/json"

# Get English Quiz
curl -X GET "http://localhost:8003/api/daily-quiz/?language=english&user_id=rahuljha996886" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "quiz_metadata": {
    "quiz_type": "daily_coin_quiz",
    "total_questions": 5,
    "difficulty": "medium",
    "date": "2026-01-10",
    "title": "Daily GK Quiz - January 10, 2026",
    "description": "Test your general knowledge with AI-generated questions!"
  },
  "coins": {
    "attempt_bonus": 5,
    "per_correct_answer": 10,
    "max_possible": 55
  },
  "questions": [
    {
      "id": 1,
      "question": "भारत की राष्ट्रीय नदी कौन सी है?",
      "options": ["यमुना", "ब्रह्मपुत्र", "गंगा", "गोदावरी"],
      "category": "भूगोल",
      "difficulty": "आसान"
    }
  ],
  "ui": {
    "theme": "light",
    "card_style": "rounded",
    "accent_color": "#6366F1",
    "show_progress_bar": true,
    "show_coin_animation": true
  },
  "quiz_id": "7b318795-0782-4415-bad5-130cb7f9d9a9",
  "already_attempted": false
}
```

**Status Codes:**
- `200 OK` - Quiz retrieved successfully
- `500 INTERNAL_SERVER_ERROR` - Failed to generate quiz

---

### 1.2 Start Daily Quiz (Award Participation Bonus)

**Endpoint:**
```
POST /api/daily-quiz/start/
```

**Request Body:**
```json
{
  "user_id": "rahuljha996886",
  "quiz_id": "7b318795-0782-4415-bad5-130cb7f9d9a9"
}
```

**cURL Command:**
```bash
curl -X POST "http://localhost:8003/api/daily-quiz/start/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "rahuljha996886",
    "quiz_id": "7b318795-0782-4415-bad5-130cb7f9d9a9"
  }'
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "You earned 5 coins for starting the Daily Quiz.",
  "quiz_id": "7b318795-0782-4415-bad5-130cb7f9d9a9",
  "coins_awarded": 5
}
```

**Error Response (400 BAD_REQUEST):**
```json
{
  "error": "Quiz already completed"
}
```

**Status Codes:**
- `200 OK` - Quiz started, coins awarded
- `400 BAD_REQUEST` - Quiz already completed or missing parameters
- `404 NOT_FOUND` - Quiz not found

---

### 1.3 Submit Daily Quiz

**Endpoint:**
```
POST /api/daily-quiz/submit/
```

**Request Body:**
```json
{
  "user_id": "rahuljha996886",
  "quiz_id": "7b318795-0782-4415-bad5-130cb7f9d9a9",
  "answers": {
    "1": 0,
    "2": 1,
    "3": 2,
    "4": 3,
    "5": 0
  },
  "time_taken_seconds": 180
}
```

**cURL Command:**
```bash
curl -X POST "http://localhost:8003/api/daily-quiz/submit/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "rahuljha996886",
    "quiz_id": "7b318795-0782-4415-bad5-130cb7f9d9a9",
    "answers": {"1": 0, "2": 1, "3": 2, "4": 3, "5": 0},
    "time_taken_seconds": 180
  }'
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "🎉 Quiz completed! You earned 15 coins!",
  "result": {
    "correct_count": 1,
    "total_questions": 5,
    "score_percentage": 20.0,
    "coins_earned": 15,
    "time_taken_seconds": 180,
    "attempt_bonus": 5,
    "per_correct": 10,
    "max_possible": 55
  },
  "coin_breakdown": {
    "attempt_bonus": 5,
    "correct_answers": 1,
    "coins_per_correct": 10,
    "correct_answer_coins": 10,
    "total_earned": 15
  },
  "results": [
    {
      "question_id": 1,
      "question": "भारत की राष्ट्रीय नदी कौन सी है?",
      "options": [
        {"id": "A", "text": "यमुना"},
        {"id": "B", "text": "ब्रह्मपुत्र"},
        {"id": "C", "text": "गंगा"},
        {"id": "D", "text": "गोदावरी"}
      ],
      "user_answer": {"id": "A", "text": "यमुना"},
      "correct_answer": {"id": "C", "text": "गंगा"},
      "is_correct": false,
      "explanation": "गंगा नदी भारत की सबसे महत्वपूर्ण और पवित्र नदियों में से एक है।",
      "fun_fact": "गंगा नदी की लंबाई लगभग 2,525 किलोमीटर है।",
      "category": "भूगोल"
    }
  ],
  "total_coins": 35,
  "show_coin_animation": true
}
```

**Status Codes:**
- `200 OK` - Quiz submitted successfully
- `400 BAD_REQUEST` - Missing quiz_id or answers
- `404 NOT_FOUND` - Quiz not found
- `500 INTERNAL_SERVER_ERROR` - Processing error

---

### 1.4 Get User Coins Balance & Transactions

**Endpoint:**
```
GET /api/daily-quiz/coins/
```

**Parameters:**
```
?user_id=STRING (Required)
```

**cURL Command:**
```bash
curl -X GET "http://localhost:8003/api/daily-quiz/coins/?user_id=rahuljha996886" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "user_id": "rahuljha996886",
  "total_coins": 35,
  "lifetime_coins": 35,
  "coins_spent": 0,
  "recent_transactions": [
    {
      "amount": 15,
      "type": "earn",
      "reason": "Daily Quiz attempt 2026-01-10",
      "created_at": "2026-01-10T09:51:47.950557Z"
    },
    {
      "amount": 5,
      "type": "earn",
      "reason": "Daily Quiz participation 2026-01-10",
      "created_at": "2026-01-10T09:50:11.382513Z"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Balance retrieved successfully

---

### 1.5 Get Quiz History

**Endpoint:**
```
GET /api/daily-quiz/history/
```

**Parameters:**
```
?user_id=STRING (Required)
&limit=INTEGER  (Default: 30)
```

**cURL Command:**
```bash
curl -X GET "http://localhost:8003/api/daily-quiz/history/?user_id=rahuljha996886&limit=10" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "user_id": "rahuljha996886",
  "history": [
    {
      "date": "2026-01-10",
      "quiz_title": "Daily GK Quiz - January 10, 2026",
      "correct_count": 1,
      "total_questions": 5,
      "score_percentage": 20.0,
      "coins_earned": 15,
      "completed_at": "2026-01-10T09:51:47.745608Z"
    }
  ],
  "stats": {
    "total_attempts": 3,
    "total_coins_earned": 35,
    "average_score": 13.33
  }
}
```

**Status Codes:**
- `200 OK` - History retrieved successfully

---

## 2. Flashcards Endpoints

### 2.1 Generate Flashcards

**Endpoint:**
```
POST /api/flashcards/generate/
```

**Request Body:**
```json
{
  "topic": "World History",
  "num_cards": 5,
  "language": "english",
  "difficulty": "medium"
}
```

**cURL Command:**
```bash
curl -X POST "http://localhost:8003/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "World History",
    "num_cards": 5,
    "language": "english",
    "difficulty": "medium"
  }'
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "title": "Flashcard Set - World History Concepts",
    "topic": "World History",
    "language": "english",
    "total_cards": 5,
    "difficulty": "medium",
    "created_at": "2026-01-10T10:00:00Z",
    "cards": [
      {
        "id": 1,
        "question": "How did the Neolithic Revolution fundamentally change human social structures?",
        "answer": "Shift from nomadic hunter-gatherer societies to settled agricultural communities, leading to social hierarchies and specialization.",
        "category": "Neolithic Revolution",
        "difficulty": "medium",
        "importance": "high",
        "memory_tip": "Remember: NEOLITHIC = Settlement + Agriculture = Social Hierarchy",
        "related_topics": ["Paleolithic Era", "Development of Civilizations", "Social Organization"]
      },
      {
        "id": 2,
        "question": "What were the major causes of the French Revolution?",
        "answer": "Economic crisis, food shortages, Enlightenment ideas, inequality of the three estates, and mismanagement by the monarchy.",
        "category": "French Revolution",
        "difficulty": "medium",
        "importance": "high",
        "memory_tip": "FAMINE + IDEAS + INEQUALITY = REVOLUTION",
        "related_topics": ["Enlightenment", "Social Inequality", "Monarchy Crisis"]
      }
    ]
  }
}
```

**Status Codes:**
- `200 OK` - Flashcards generated successfully
- `400 BAD_REQUEST` - Invalid topic or parameters
- `500 INTERNAL_SERVER_ERROR` - Generation failed

---

## 3. Predicted Questions Endpoints

### 3.1 Generate Predicted Questions

**Endpoint:**
```
POST /api/predicted-questions/generate/
```

**Request Body:**
```json
{
  "topic": "Science",
  "user_id": "rahuljha996886",
  "difficulty": "medium",
  "num_questions": 5
}
```

**cURL Command:**
```bash
curl -X POST "http://localhost:8003/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Science",
    "user_id": "rahuljha996886",
    "difficulty": "medium",
    "num_questions": 5
  }' \
  --max-time 30
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "topic": "Science",
    "user_id": "rahuljha996886",
    "total_questions": 5,
    "difficulty": "medium",
    "confidence_score": 0.92,
    "generation_time": "2026-01-10T10:05:00Z",
    "questions": [
      {
        "id": 1,
        "question": "What is the process by which plants use sunlight to convert into chemical energy?",
        "options": [
          "Photosynthesis",
          "Respiration",
          "Fermentation",
          "Osmosis"
        ],
        "correct_answer": "A",
        "category": "Biology",
        "difficulty": "medium",
        "explanation": "Photosynthesis is the process where green plants use sunlight, water, and carbon dioxide to produce glucose and oxygen.",
        "prediction_confidence": 0.95
      },
      {
        "id": 2,
        "question": "Which element has the atomic number 1?",
        "options": [
          "Hydrogen",
          "Helium",
          "Lithium",
          "Carbon"
        ],
        "correct_answer": "A",
        "category": "Chemistry",
        "difficulty": "easy",
        "explanation": "Hydrogen is the lightest element with atomic number 1 and atomic mass approximately 1.",
        "prediction_confidence": 0.99
      }
    ]
  }
}
```

**Status Codes:**
- `200 OK` - Questions generated successfully
- `400 BAD_REQUEST` - Missing required parameters
- `408 REQUEST_TIMEOUT` - Generation taking too long (use --max-time flag)
- `500 INTERNAL_SERVER_ERROR` - Generation failed

---

## 4. Study Material Endpoints

### 4.1 Generate Study Material

**Endpoint:**
```
POST /api/study-material/generate/
```

**Request Body:**
```json
{
  "topic": "Mathematics",
  "difficulty": "medium",
  "content_type": "notes",
  "language": "english"
}
```

**cURL Command:**
```bash
curl -X POST "http://localhost:8003/api/study-material/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Mathematics",
    "difficulty": "medium",
    "content_type": "notes",
    "language": "english"
  }'
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "title": "Mathematics Study Material - Algebra",
    "topic": "Mathematics",
    "difficulty": "medium",
    "content_type": "notes",
    "language": "english",
    "created_at": "2026-01-10T10:10:00Z",
    "sections": [
      {
        "title": "Introduction to Algebra",
        "content": "Algebra is a branch of mathematics that deals with variables and their relationships...",
        "key_concepts": [
          "Variables and Constants",
          "Expressions and Equations",
          "Linear Equations",
          "Quadratic Equations"
        ],
        "examples": [
          {
            "example": "Solve: 2x + 3 = 7",
            "solution": "2x = 4, therefore x = 2"
          }
        ]
      }
    ],
    "total_sections": 5,
    "word_count": 2500,
    "estimated_read_time": "12 minutes"
  }
}
```

**Error Response (400 BAD_REQUEST):**
```json
{
  "error": "Please provide text content or upload a document"
}
```

**Status Codes:**
- `200 OK` - Study material generated successfully
- `400 BAD_REQUEST` - Missing required parameters
- `500 INTERNAL_SERVER_ERROR` - Generation failed

---

## 5. YouTube Summarizer

### 5.1 Summarize YouTube Video

**Endpoint:**
```
POST /api/youtube/summarize/
```

**Request Body:**
```json
{
  "video_url": "https://www.youtube.com/watch?v=XesW1fJIJTc"
}
```

**cURL Command:**
```bash
curl -X POST "http://localhost:8003/api/youtube/summarize/" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=XesW1fJIJTc"
  }' \
  --max-time 60
```

**Response (200 OK):**
```json
{
  "success": true,
  "video_url": "https://www.youtube.com/watch?v=XesW1fJIJTc",
  "metadata": {
    "video_duration": "02:35",
    "transcript_segments": 224,
    "timestamp_count": 224,
    "generation_time": "2026-01-10T10:15:30Z"
  },
  "summary": "## 1. EXECUTIVE SUMMARY\n\nThis video presents a detailed episode of 'Tarak Mehta Ka Ooltah Chashmah' focusing on the Tappu Sena's plan to secretly learn how to ride a scooter...\n\n## 2. VIDEO TIMELINE & KEY SECTIONS WITH TIMESTAMPS\n\n* **[00:00] - [03:31]** - Main Content Section\n  * **[00:00]** - Video Introduction\n  * **[00:10]** - Setup and Introduction\n  * **[00:23]** - Main Plot Development\n  ...\n\n## 14. RELATED TOPICS & SUGGESTIONS\n\n* Comedy Sketches\n* Indian Sitcoms\n* Character Development",
  "sections": 14,
  "sections_list": [
    "Executive Summary",
    "Video Timeline",
    "Main Topic",
    "Key Points",
    "Important Concepts",
    "Statistics",
    "Quotes",
    "Visual Descriptions",
    "Target Audience",
    "Key Takeaways",
    "Chapter Breakdown",
    "Overall Assessment",
    "Viewer Questions",
    "Related Topics"
  ],
  "summary_length": 23540,
  "language": "english"
}
```

**Error Response (400 BAD_REQUEST):**
```json
{
  "error": "video_url is required"
}
```

**Error Response (400 BAD_REQUEST) - Invalid URL:**
```json
{
  "success": false,
  "error": "Invalid YouTube URL format",
  "details": "Please provide a valid YouTube URL (e.g., https://www.youtube.com/watch?v=VIDEO_ID)"
}
```

**Status Codes:**
- `200 OK` - Summary generated successfully
- `400 BAD_REQUEST` - Missing or invalid video URL
- `408 REQUEST_TIMEOUT` - Generation taking too long
- `500 INTERNAL_SERVER_ERROR` - Transcript fetch or generation failed

---

## 6. Usage Dashboard

### 6.1 Get Usage Statistics Dashboard

**Endpoint:**
```
GET /api/user-usage-dashboard/
```

**Parameters:**
```
?user_id=STRING (Required)
&period=day|week|month (Default: week)
```

**cURL Command:**
```bash
# Get weekly statistics
curl -X GET "http://localhost:8003/api/user-usage-dashboard/?user_id=rahuljha996886&period=week" \
  -H "Content-Type: application/json"

# Get monthly statistics
curl -X GET "http://localhost:8003/api/user-usage-dashboard/?user_id=rahuljha996886&period=month" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "user_id": "rahuljha996886",
  "period": "week",
  "data": {
    "quiz_statistics": {
      "total_attempts": 15,
      "total_completed": 13,
      "avg_score": 76.5,
      "total_coins_earned": 185,
      "trending": "up"
    },
    "flashcard_statistics": {
      "sets_created": 8,
      "total_cards_studied": 156,
      "cards_mastered": 89,
      "study_time_minutes": 342
    },
    "youtube_summaries": {
      "videos_summarized": 12,
      "total_duration_watched": "4h 32m",
      "avg_summary_length": 18500
    },
    "daily_activity": [
      {
        "date": "2026-01-10",
        "quizzes_attempted": 3,
        "coins_earned": 45,
        "flashcards_studied": 25,
        "videos_processed": 2
      },
      {
        "date": "2026-01-09",
        "quizzes_attempted": 2,
        "coins_earned": 30,
        "flashcards_studied": 20,
        "videos_processed": 1
      }
    ],
    "total_coins": 485,
    "lifetime_coins": 850
  }
}
```

**Status Codes:**
- `200 OK` - Dashboard data retrieved successfully
- `400 BAD_REQUEST` - Invalid period or missing user_id
- `404 NOT_FOUND` - User not found

---

## 7. Error Handling

### Common Error Responses

**400 BAD_REQUEST:**
```json
{
  "error": "Missing required field: user_id",
  "details": "Required parameters: user_id, quiz_id"
}
```

**404 NOT_FOUND:**
```json
{
  "error": "Resource not found",
  "details": "Quiz with ID 'xyz' not found"
}
```

**500 INTERNAL_SERVER_ERROR:**
```json
{
  "error": "Internal server error",
  "debug_message": "Connection timeout while fetching transcript"
}
```

**408 REQUEST_TIMEOUT:**
```json
{
  "error": "Request timeout",
  "details": "The operation took too long to complete. Please try again."
}
```

---

## 8. Response Formats

### Standard Success Response Format

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    "key": "value"
  },
  "meta": {
    "timestamp": "2026-01-10T10:00:00Z",
    "request_id": "req_abc123",
    "version": "1.0.0"
  }
}
```

### Standard Error Response Format

```json
{
  "success": false,
  "error": "Error Type",
  "details": "Detailed error message",
  "code": "ERROR_CODE",
  "meta": {
    "timestamp": "2026-01-10T10:00:00Z",
    "request_id": "req_abc123"
  }
}
```

### Pagination Response Format

```json
{
  "success": true,
  "data": [
    { "id": 1, "title": "Item 1" },
    { "id": 2, "title": "Item 2" }
  ],
  "pagination": {
    "total": 100,
    "limit": 10,
    "offset": 0,
    "has_more": true
  }
}
```

---

## Testing Commands

### Quick Test All Endpoints

```bash
#!/bin/bash
BASE_URL="http://localhost:8003/api"
USER_ID="rahuljha996886"

echo "Testing Daily Quiz..."
curl -s "$BASE_URL/daily-quiz/?language=english&user_id=$USER_ID" | jq '.quiz_metadata'

echo -e "\n\nTesting Flashcards..."
curl -s -X POST "$BASE_URL/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{"topic":"History","num_cards":3}' | jq '.data.total_cards'

echo -e "\n\nTesting YouTube Summarizer..."
curl -s -X POST "$BASE_URL/youtube/summarize/" \
  -H "Content-Type: application/json" \
  -d '{"video_url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ"}' | jq '.metadata'

echo -e "\n\nTesting User Coins..."
curl -s "$BASE_URL/daily-quiz/coins/?user_id=$USER_ID" | jq '.total_coins'

echo -e "\n\n✅ All endpoints tested!"
```

---

## Production Deployment Checklist

- ✅ All endpoints tested and working
- ✅ Error handling implemented
- ✅ Response formats standardized
- ✅ Rate limiting configured
- ✅ CORS enabled for frontend
- ✅ Logging and monitoring active
- ✅ Database connections pooled
- ✅ API documentation complete
- ✅ Security headers configured
- ✅ SSL/TLS enabled

---

## Support & Troubleshooting

**Issue**: Endpoint returns 404  
**Solution**: Verify the endpoint URL and HTTP method (GET/POST)

**Issue**: Timeout on YouTube Summarizer  
**Solution**: Use `--max-time 60` flag or increase timeout for long videos

**Issue**: Quiz generation fails  
**Solution**: Ensure Gemini API key is configured and valid

**Issue**: Coins not updating  
**Solution**: Check database connection and transaction logging

---

**For More Help**: Contact backend@edtech.dev  
**Documentation Version**: 1.0.0  
**Last Updated**: 2026-01-10  
**Status**: ✅ Production Ready

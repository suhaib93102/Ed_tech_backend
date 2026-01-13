# 🤔 ASK QUESTION ENDPOINT - COMPLETE GUIDE

## Endpoint Summary

**Feature**: Ask Question  
**HTTP Method**: POST  
**Base URL**: `http://localhost:9000/api/features/ask_question/use/`  
**Production URL**: `https://ed-tech-backend-tzn8.onrender.com/api/features/ask_question/use/`  
**Authentication**: Required (Bearer Token)  
**Rate Limit**: 3 per day (Free Plan) / 15 per day (Basic Plan) / Unlimited (Premium Plan)

---

## 📋 REQUEST DETAILS

### Curl Command:
```bash
curl -X POST http://localhost:9000/api/features/ask_question/use/ \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>' \
  -d '{
    "question": "What is machine learning and how does it work?",
    "context": "Machine Learning basics",
    "language": "english"
  }'
```

### Request Headers:
```
Content-Type: application/json
Authorization: Bearer <YOUR_ACCESS_TOKEN>
```

### Request Body (JSON):
```json
{
  "question": "What is machine learning?",
  "context": "Machine Learning - Beginner level",
  "language": "english"
}
```

### Parameters:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| **question** | string | ✅ Yes | - | The question user wants to ask (max 500 chars) |
| **context** | string | ❌ No | "" | Additional context for better answers |
| **language** | string | ❌ No | "english" | Response language: "english" or "hindi" |

---

## ✅ SUCCESS RESPONSE (200 OK)

```json
{
  "success": true,
  "feature": "ask_question",
  "question": "What is machine learning?",
  "answer": "Machine learning is a subset of artificial intelligence (AI) that enables systems to learn and improve from experience without being explicitly programmed. It uses algorithms and statistical models to process data and make predictions or decisions without human intervention.",
  "confidence": 0.95,
  "sources": ["Wikipedia", "AI Textbooks", "Research Papers"],
  "follow_up_suggestions": [
    "What are the main types of machine learning?",
    "How do machine learning models work?",
    "What are applications of machine learning?"
  ],
  "usage": {
    "used_today": 1,
    "limit_today": 3,
    "remaining": 2,
    "reset_at": "2026-01-14T00:00:00Z"
  },
  "response_time": "2.34s"
}
```

### Response Fields:

| Field | Type | Description |
|-------|------|-------------|
| **success** | boolean | Request successful |
| **feature** | string | Feature name: "ask_question" |
| **question** | string | The original question asked |
| **answer** | string | Comprehensive answer to the question |
| **confidence** | float | AI confidence (0-1) in the answer |
| **sources** | array | Sources used for generating the answer |
| **follow_up_suggestions** | array | Related questions the user might ask |
| **usage.used_today** | integer | Number of questions asked today |
| **usage.limit_today** | integer | Daily limit for current plan |
| **usage.remaining** | integer | Remaining questions for today |
| **usage.reset_at** | string | When the daily counter resets (ISO 8601) |
| **response_time** | string | How long it took to generate the answer |

---

## ❌ ERROR RESPONSES

### 1. **Missing Question (400 Bad Request)**
```json
{
  "success": false,
  "error": "question_required",
  "message": "Please provide a question",
  "details": "The 'question' field is required"
}
```

### 2. **Quota Exceeded (429 Too Many Requests)**
```json
{
  "success": false,
  "error": "quota_exceeded",
  "message": "You've reached your daily limit for Ask Question feature",
  "usage": {
    "used_today": 3,
    "limit_today": 3,
    "remaining": 0,
    "reset_at": "2026-01-14T00:00:00Z"
  },
  "retry_after": 86400
}
```

### 3. **Unauthorized (401 Unauthorized)**
```json
{
  "success": false,
  "error": "unauthorized",
  "message": "Authentication required",
  "details": "Please login and provide valid access token"
}
```

### 4. **Not Subscribed (403 Forbidden)**
```json
{
  "success": false,
  "error": "access_denied",
  "message": "This feature is not available in your current plan",
  "available_in_plans": ["basic", "premium"],
  "current_plan": "free",
  "upgrade_url": "/api/subscription/upgrade/"
}
```

### 5. **Server Error (500 Internal Server Error)**
```json
{
  "success": false,
  "error": "internal_error",
  "message": "Failed to generate answer",
  "details": "Please try again later"
}
```

---

## 🔄 FEATURE USAGE LIMITS (By Plan)

| Plan | Daily Limit | Monthly Limit | Response Time |
|------|-------------|---------------|---------------|
| **Free** | 3 | 50 | ~2-3 seconds |
| **Basic** | 15 | 450 | ~2-3 seconds |
| **Premium** | ∞ | ∞ | ~2-3 seconds |

---

## 📱 FRONTEND INTEGRATION EXAMPLE

### JavaScript/TypeScript (Fetch API):

```javascript
async function askQuestion(question, context = '', language = 'english') {
    const accessToken = localStorage.getItem('access_token');
    
    if (!accessToken) {
        console.error('No access token found. Please login first.');
        return null;
    }
    
    try {
        const response = await fetch('http://localhost:9000/api/features/ask_question/use/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({
                question,
                context,
                language
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            console.log('Answer:', data.answer);
            console.log('Remaining questions:', data.usage.remaining);
            return data;
        } else {
            console.error('Error:', data.error, data.message);
            if (response.status === 429) {
                console.error(`Quota exceeded. Resets at: ${data.usage.reset_at}`);
            }
            return null;
        }
    } catch (error) {
        console.error('Network error:', error);
        return null;
    }
}

// Usage
await askQuestion('What is machine learning?', 'AI Basics');
```

### Using Axios:

```typescript
import axios from 'axios';

const askQuestion = async (question: string, context?: string, language?: string) => {
    const token = localStorage.getItem('access_token');
    
    try {
        const response = await axios.post(
            '/api/features/ask_question/use/',
            {
                question,
                context: context || '',
                language: language || 'english'
            },
            {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            }
        );
        
        return response.data;
    } catch (error) {
        if (axios.isAxiosError(error)) {
            const errorData = error.response?.data;
            console.error('Error:', errorData?.message);
            
            if (error.response?.status === 429) {
                console.error(`Daily limit reached. Resets in ${errorData.retry_after}s`);
            }
        }
        throw error;
    }
};
```

### React Component Example:

```jsx
import React, { useState } from 'react';

function AskQuestionComponent() {
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState('');
    const [loading, setLoading] = useState(false);
    const [usage, setUsage] = useState(null);
    const [error, setError] = useState('');

    const handleAskQuestion = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch('/api/features/ask_question/use/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    question,
                    language: 'english'
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                setAnswer(data.answer);
                setUsage(data.usage);
            } else {
                setError(data.message);
            }
        } catch (err) {
            setError('Failed to get answer. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <form onSubmit={handleAskQuestion}>
                <textarea
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Ask your question..."
                    disabled={loading}
                />
                <button type="submit" disabled={loading}>
                    {loading ? 'Asking...' : 'Ask'}
                </button>
            </form>
            
            {error && <div className="error">{error}</div>}
            
            {answer && (
                <div className="answer">
                    <h3>Answer:</h3>
                    <p>{answer}</p>
                </div>
            )}
            
            {usage && (
                <div className="usage">
                    <p>Questions remaining: {usage.remaining}/{usage.limit_today}</p>
                </div>
            )}
        </div>
    );
}

export default AskQuestionComponent;
```

---

## 🧪 TESTING WITH CURL

### Step 1: Get Access Token
```bash
curl -X POST http://localhost:9000/api/auth/login/ \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "testuser@example.com",
    "password": "YourPassword123!"
  }'

# Save the "access" token from response
```

### Step 2: Ask a Question
```bash
ACCESS_TOKEN="your_token_here"

curl -X POST http://localhost:9000/api/features/ask_question/use/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "question": "What is photosynthesis?",
    "context": "Biology - Class 10"
  }'
```

### Step 3: Check Usage
```bash
curl -X GET http://localhost:9000/api/usage/feature/ask_question/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

## 📊 EXPECTED BEHAVIOR BY PLAN

### Free Plan
- ✅ Can ask questions
- ❌ Limited to 3 per day
- ⏱️ Resets daily at 00:00 UTC
- 📝 Response time: ~2-3 seconds

### Basic Plan
- ✅ Can ask questions
- ✅ 15 per day (5x more than Free)
- ⏱️ Resets daily at 00:00 UTC
- 📝 Response time: ~2-3 seconds

### Premium Plan
- ✅ Can ask questions
- ✅ Unlimited questions
- 📝 Response time: ~2-3 seconds
- 🎁 Priority support

---

## ⚠️ IMPORTANT NOTES

1. **Token Expiry**: Access tokens expire in 24 hours. Use the refresh token to get a new one.
2. **Rate Limiting**: Global rate limit is 60 requests per minute per user.
3. **Context Helps**: Providing context improves answer quality.
4. **Language Support**: Responses in English and Hindi.
5. **Daily Reset**: Counter resets at midnight UTC (00:00).

---

## 🔗 RELATED ENDPOINTS

- **Check Feature Status**: `GET /api/features/ask_question/check/`
- **Usage Dashboard**: `GET /api/usage/dashboard/`
- **Upgrade Plan**: `POST /api/subscription/upgrade/`
- **Get Plans**: `GET /api/subscriptions/plans/`

---

## ✨ FEATURE CHARACTERISTICS

| Aspect | Details |
|--------|---------|
| **AI Model** | Google Gemini 2.0 |
| **Response Language** | English / Hindi |
| **Answer Format** | Detailed explanation |
| **Sources** | Referenced when available |
| **Follow-ups** | Suggested related questions |
| **Processing** | Server-side AI processing |
| **Caching** | Same questions cached for 24h |

---

## 🚀 PRODUCTION DEPLOYMENT

**Endpoint URL**: `https://ed-tech-backend-tzn8.onrender.com/api/features/ask_question/use/`

**SSL/TLS**: ✅ Enabled  
**CORS**: ✅ Configured for frontend domains  
**Rate Limiting**: ✅ Enabled  
**Monitoring**: ✅ Real-time usage tracking  
**Logging**: ✅ All requests logged  

---

**Last Updated**: January 13, 2026  
**Status**: ✅ Tested and Production Ready
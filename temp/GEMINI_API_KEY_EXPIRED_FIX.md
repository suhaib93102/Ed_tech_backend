# 🔑 GEMINI API KEY EXPIRED - DAILY QUIZ 500 ERROR FIX

## 🚨 ISSUE IDENTIFIED

**Error**: `500 Internal Server Error` on Daily Quiz endpoint
**Root Cause**: Gemini API key has expired
**Error Message**: `"API key expired. Please renew the API key."`

---

## 📋 PROBLEM DETAILS

### Frontend Error Logs:
```
Failed to load resource: the server responded with a status of 500 ()
Server error: {error: 'Failed to generate quiz', message: "Unable to create today's quiz. Please try again later."}
getDailyQuiz error: {status: 500, message: 'Failed to generate quiz'}
CRITICAL: Cannot load daily quiz from API
Error details: Failed to generate quiz
```

### Backend Error (from testing):
```
ERROR: 400 API key expired. Please renew the API key. [reason: "API_KEY_INVALID"]
Daily quiz generation result: {'success': False, 'error': 'Failed to generate Daily Quiz', 'details': '400 API key expired...'}
```

---

## 🔧 SOLUTION: RENEW GEMINI API KEY

### Step 1: Get New Gemini API Key

1. **Go to Google AI Studio**: https://makersuite.google.com/app/apikey
2. **Sign in** with your Google account
3. **Create a new API key** or **renew existing one**
4. **Copy the new API key**

### Step 2: Update Environment Variables

#### For Local Development:
```bash
# Update your .env file
echo "GEMINI_API_KEY=your_new_api_key_here" > .env
```

#### For Render.com Production:
1. **Go to Render Dashboard**: https://dashboard.render.com/
2. **Select your service**: `ed-tech-backend`
3. **Go to Environment**: Settings → Environment
4. **Update GEMINI_API_KEY**: Replace with new key
5. **Redeploy**: The service will auto-redeploy

---

## 🧪 TESTING THE FIX

### Test 1: Local Testing
```bash
cd /Users/vishaljha/Ed_tech_backend

# Test Gemini service directly
python manage.py shell -c "
from question_solver.services.gemini_service import gemini_service
result = gemini_service.generate_daily_quiz(num_questions=2, language='english')
print('Success:', result.get('success'))
print('Questions generated:', len(result.get('questions', [])))
"
```

**Expected Output:**
```
Success: True
Questions generated: 2
```

### Test 2: API Endpoint Testing
```bash
# Test daily quiz endpoint
curl -s "http://localhost:9000/api/daily-quiz/?language=english&user_id=test" | jq '.quiz_metadata'
```

**Expected Response:**
```json
{
  "quiz_type": "daily_coin_quiz",
  "total_questions": 5,
  "difficulty": "medium",
  "date": "2026-01-13",
  "title": "Daily GK Quiz - January 13, 2026",
  "description": "Test your general knowledge with AI-generated questions!",
  "language": "english",
  "question_bank_size": 20,
  "questions_shown": 5
}
```

### Test 3: Production Testing
```bash
# Test production endpoint
curl -s "https://ed-tech-backend-tzn8.onrender.com/api/daily-quiz/?language=english&user_id=test" | jq '.quiz_metadata'
```

---

## 📊 WHAT HAPPENS WHEN API KEY EXPIRES

### Affected Features:
- ✅ **Daily Quiz** (currently failing)
- ✅ **Predicted Questions** (will fail if used)
- ✅ **Flashcards** (will fail if used)
- ✅ **Quiz Generation** (will fail if used)
- ✅ **Ask Question** (will fail if used)

### Error Flow:
1. **Frontend requests** daily quiz
2. **Backend calls** `gemini_service.generate_daily_quiz()`
3. **Gemini API rejects** with "API key expired"
4. **Backend returns** 500 error
5. **Frontend shows** "Failed to generate quiz"

---

## 🔄 ALTERNATIVE SOLUTIONS (if Gemini key unavailable)

### Option 1: Use Static Questions (Quick Fix)
Create a fallback system with pre-written questions:

```python
# In daily_quiz_views.py
def create_or_get_daily_quiz(language='english'):
    # ... existing code ...
    
    # If Gemini fails, use static questions
    if not result.get('success'):
        logger.warning("Gemini failed, using static questions")
        return create_static_daily_quiz(language)
```

### Option 2: Switch to OpenAI (Alternative AI)
Replace Gemini with OpenAI GPT:

```python
# In gemini_service.py
import openai

class OpenAIService:
    def generate_daily_quiz(self, num_questions=10, language='english'):
        # Use OpenAI API instead
        pass
```

### Option 3: Disable AI Features Temporarily
Return static responses until API key is renewed.

---

## 🚀 IMMEDIATE ACTION PLAN

### Priority 1: Fix API Key (Recommended)
1. **Get new Gemini API key** from Google AI Studio
2. **Update environment variable** in Render dashboard
3. **Wait for auto-redeploy** (2-3 minutes)
4. **Test endpoints** work again

### Priority 2: Add Error Handling (Backup)
Add better error handling to prevent 500 errors:

```python
# In daily_quiz_views.py
def get_daily_quiz(request):
    try:
        daily_quiz = create_or_get_daily_quiz(language=language)
        
        if not daily_quiz:
            # Return user-friendly error instead of 500
            return Response({
                'error': 'Service temporarily unavailable',
                'message': 'Daily quiz generation is currently unavailable. Please try again later.',
                'retry_after': 3600  # 1 hour
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception as e:
        logger.error(f"Daily quiz error: {e}")
        return Response({
            'error': 'Service error',
            'message': 'Unable to load daily quiz. Please try again later.'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
```

---

## 📞 SUPPORT INFORMATION

### API Key Renewal:
- **Google AI Studio**: https://makersuite.google.com/app/apikey
- **Free Tier**: 60 requests/minute, 1000 requests/day
- **Cost**: Free for basic usage

### Environment Variables:
- **Local**: `.env` file
- **Production**: Render dashboard → Service → Environment

### Monitoring:
- **Check API usage**: Google Cloud Console
- **Monitor errors**: Render logs
- **Test endpoints**: Use curl commands above

---

## ✅ VERIFICATION CHECKLIST

- [ ] **New API key obtained** from Google AI Studio
- [ ] **Environment variable updated** in Render dashboard
- [ ] **Service redeployed** automatically
- [ ] **Daily quiz endpoint tested** successfully
- [ ] **Other AI features tested** (flashcards, predicted questions)
- [ ] **Frontend working** without 500 errors

---

## 🎯 EXPECTED RESULTS AFTER FIX

### Before Fix:
```
❌ POST /api/daily-quiz/ → 500 Internal Server Error
❌ Frontend: "Failed to generate quiz"
❌ Backend: "API key expired"
```

### After Fix:
```
✅ POST /api/daily-quiz/ → 200 OK
✅ Frontend: Quiz loads successfully
✅ Backend: "Successfully generated 20 Daily Quiz questions"
```

---

**Time to Fix**: 5-10 minutes  
**Impact**: Restores all AI-powered features  
**Risk Level**: LOW (just updating API key)

**Next Step**: Get new Gemini API key and update Render environment! 🚀
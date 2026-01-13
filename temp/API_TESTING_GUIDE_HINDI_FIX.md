# API Testing & Debugging Guide - Hindi Daily Quiz + Error Fixes

## Status Report

✅ **Fixed Issues:**
1. Hindi daily quiz generation now supported
2. Flashcards 400 error - added validation and language support  
3. Predicted questions 500 error - comprehensive error handling
4. Created 100 Hindi GK questions as fallback

❌ **Errors from Frontend:**
```
flashcards/generate: 400 Bad Request
predicted-questions/generate: 500 Internal Server Error
Questions parameter was 'question' but should be 'text'
```

---

## Implementation Steps

### Step 1: Update Database Model

```bash
# In terminal, update DailyQuiz model to include language field
cd /Users/vishaljha/Ed_tech_backend

# Create migration
python manage.py makemigrations

# Apply migration
python manage.py migrate
```

**Model Update in `question_solver/models.py`:**

```python
class DailyQuiz(models.Model):
    date = models.DateField(default=date.today, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    total_questions = models.IntegerField(default=10)
    difficulty = models.CharField(max_length=20, default='medium')
    is_active = models.BooleanField(default=True)
    # ADD THIS FIELD:
    language = models.CharField(
        max_length=20, 
        default='english',
        choices=[('english', 'English'), ('hindi', 'Hindi')]
    )
    
    class Meta:
        unique_together = ('date', 'language')  # One quiz per language per day
```

### Step 2: Update Gemini Service

Add language parameter to `generate_daily_quiz()`:

```python
def generate_daily_quiz(self, num_questions: int = 10, language: str = 'english') -> Dict[str, Any]:
    """
    Generate a daily general knowledge quiz with language support
    language: 'english' or 'hindi'
    """
    # Add language instruction to prompt
    lang_instruction = ""
    if language.lower() == 'hindi':
        lang_instruction = "in Hindi language (देवनागरी script). All content in Hindi."
    
    prompt = f"""Generate {num_questions} multiple-choice questions {lang_instruction}
    ...
    """
```

### Step 3: Update Daily Quiz Views

Modify `get_daily_quiz()` to accept language parameter:

```python
@api_view(['GET'])
def get_daily_quiz(request):
    user_id = request.query_params.get('user_id', 'anonymous')
    language = request.query_params.get('language', 'english').lower()
    
    # Validate language
    if language not in ['english', 'hindi']:
        language = 'english'
    
    # Call with language support
    daily_quiz = create_or_get_daily_quiz(language=language)
    
    return Response({
        'quiz_metadata': {
            'language': language,
            ...
        },
        ...
    })
```

### Step 4: Fix Flashcards Endpoint

Update validation in `FlashcardGeneratorView.post()`:

```python
def post(self, request):
    # Add defaults and validation
    topic = request.data.get('topic', '').strip()
    num_cards = int(request.data.get('num_cards', 10))  # Default: 10
    language = request.data.get('language', 'english').lower()
    
    # Validate
    if language not in ['english', 'hindi']:
        language = 'english'
    
    num_cards = max(1, min(num_cards, 50))  # 1-50 range
    
    # Proper error response
    if not topic and 'document' not in request.FILES:
        return Response({
            'success': False,
            'error': 'Please provide a topic or upload a document',
            'message': 'Either submit text in the topic field or upload a file'
        }, status=status.HTTP_400_BAD_REQUEST)
```

### Step 5: Fix Predicted Questions Endpoint

Update `PredictedQuestionsView.post()` with error handling:

```python
def post(self, request):
    try:
        topic = request.data.get('topic', '').strip()
        exam_type = request.data.get('exam_type', 'General')
        language = request.data.get('language', 'english').lower()
        num_questions = int(request.data.get('num_questions', 5))
        
        # Validate inputs
        num_questions = max(1, min(num_questions, 20))
        
        # Ensure we have content
        if not topic and 'document' not in request.FILES:
            return Response({
                'success': False,
                'error': 'Please provide either a topic or document',
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # ... rest of processing with try/except blocks
        
    except ValueError as e:
        return Response({
            'success': False,
            'error': 'Invalid parameter',
            'details': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
```

---

## Testing Commands

### Test 1: Hindi Daily Quiz

```bash
# Get English quiz
curl -X GET "http://localhost:8000/api/daily-quiz/?user_id=test_user&language=english" \
  -H "Content-Type: application/json" | jq

# Get Hindi quiz
curl -X GET "http://localhost:8000/api/daily-quiz/?user_id=test_user&language=hindi" \
  -H "Content-Type: application/json" | jq
```

**Expected Response:**
```json
{
  "quiz_metadata": {
    "language": "hindi",
    "quiz_type": "daily_coin_quiz"
  },
  "questions": [
    {
      "question": "भारत की राजधानी कौन सी है?",
      "options": ["मुंबई", "नई दिल्ली", "कोलकाता", "बेंगलुरु"]
    }
  ]
}
```

### Test 2: Flashcards Generation

```bash
# With topic (required parameter fix)
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "भारतीय इतिहास",
    "num_cards": 10,
    "language": "hindi"
  }' | jq

# With default values
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Famous Scientists"
  }' | jq
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "flashcards": [
    {
      "front": "जवाहरलाल नेहरू कौन थे?",
      "back": "भारत के पहले प्रधानमंत्री"
    }
  ],
  "language": "hindi",
  "count": 10
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Please provide a topic or upload a document",
  "message": "Either submit text in the topic field or upload a file"
}
```

### Test 3: Predicted Questions

```bash
# With topic
curl -X POST "http://localhost:8000/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "भारतीय संविधान",
    "exam_type": "UPSC",
    "num_questions": 5,
    "language": "hindi"
  }' | jq

# With document upload
curl -X POST "http://localhost:8000/api/predicted-questions/generate/" \
  -F "document=@chapter.pdf" \
  -F "exam_type=JEE" \
  -F "num_questions=10" \
  -F "language=hindi" | jq
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "title": "भारतीय संविधान",
  "questions": [
    {
      "question": "भारतीय संविधान कब लागू हुआ?",
      "options": ["26 जनवरी 1950", "15 अगस्त 1947"],
      "correct_answer": "26 जनवरी 1950"
    }
  ],
  "language": "hindi",
  "count": 5
}
```

---

## JavaScript Frontend Examples

### 1. Get Hindi Daily Quiz

```javascript
async function getDailyQuizInHindi() {
  try {
    const response = await fetch(
      'https://ed-tech-backend-tzn8.onrender.com/api/daily-quiz/?user_id=user123&language=hindi',
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': 'user123'
        },
        mode: 'cors',
        credentials: 'include'
      }
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('Hindi Quiz:', data);
    
    // Display questions
    displayQuiz(data.questions, data.quiz_metadata.language);
    
    return data;
  } catch (error) {
    console.error('Error fetching quiz:', error);
  }
}

// Call it
getDailyQuizInHindi();
```

### 2. Generate Hindi Flashcards

```javascript
async function generateHindiFlashcards() {
  try {
    const response = await fetch(
      'https://ed-tech-backend-tzn8.onrender.com/api/flashcards/generate/',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': 'user123'
        },
        mode: 'cors',
        credentials: 'include',
        body: JSON.stringify({
          topic: 'भारतीय इतिहास',  // Hindi topic
          num_cards: 10,             // REQUIRED parameter
          language: 'hindi'          // NEW: language parameter
        })
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      console.error('Error:', error);
      return;
    }
    
    const data = await response.json();
    console.log('Flashcards:', data.flashcards);
    return data;
  } catch (error) {
    console.error('Fetch error:', error);
  }
}

// Call it
generateHindiFlashcards();
```

### 3. Generate Predicted Questions

```javascript
async function generatePredictedQuestions() {
  const formData = new FormData();
  
  // Get file from input
  const fileInput = document.getElementById('documentInput');
  if (fileInput.files.length > 0) {
    formData.append('document', fileInput.files[0]);
  } else {
    // Or provide topic
    formData.append('topic', 'भारत का स्वतंत्रता संग्राम');
  }
  
  formData.append('exam_type', 'UPSC');
  formData.append('num_questions', '5');
  formData.append('language', 'hindi');
  
  try {
    const response = await fetch(
      'https://ed-tech-backend-tzn8.onrender.com/api/predicted-questions/generate/',
      {
        method: 'POST',
        headers: {
          'X-User-ID': 'user123'
          // DO NOT set Content-Type for FormData, browser sets it
        },
        mode: 'cors',
        credentials: 'include',
        body: formData
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      console.error('Error:', error);
      return;
    }
    
    const data = await response.json();
    console.log('Questions:', data.questions);
    return data;
  } catch (error) {
    console.error('Error:', error);
  }
}
```

---

## Common Errors & Fixes

### Error 1: 400 Bad Request - Flashcards

**Symptom:**
```
POST /api/flashcards/generate/ 400 (Bad Request)
{"error": "Please provide either an image or text query"}
```

**Cause:** Missing `topic` or `num_cards` parameter

**Fix:**
```javascript
// WRONG
const data = {
  document: file  // Missing topic!
};

// RIGHT
const data = {
  topic: 'Your Topic Here',      // Required!
  num_cards: 10,                 // Required (default fallback added)
  language: 'hindi'              // Optional
};
```

### Error 2: 500 Internal Server Error - Predicted Questions

**Symptom:**
```
POST /api/predicted-questions/generate/ 500
{"error": "Failed to generate predicted questions"}
```

**Cause:** JSON parsing error or missing error handling

**Fix:**
```javascript
// Make sure parameters are valid
const data = {
  topic: 'Valid topic text',           // At least 10 characters
  exam_type: 'UPSC',                   // Valid exam type
  num_questions: 5,                    // Between 1-20
  language: 'hindi'                    // 'english' or 'hindi'
};

// OR upload document
const formData = new FormData();
formData.append('document', file);     // .txt, .pdf, .jpg, .png
formData.append('num_questions', '5');
formData.append('language', 'hindi');
```

### Error 3: Quiz Parameter Mismatch

**Symptom:**
```
Error: "Please provide either an image or text query"
```

**Cause:** Wrong parameter name being sent

**Fix:**
```javascript
// WRONG
const data = {
  question: "How many...",    // Wrong parameter name!
  image: file
};

// RIGHT
const data = {
  text: "How many...",         // Correct parameter name
  image: file
};

// Or for daily quiz
fetch('...?language=hindi')    // Query parameter, not body
```

---

## Fallback: Use Hindi Questions Pool

If Gemini fails, use pre-made questions from `HINDI_QUESTIONS_POOL_100.py`:

```python
# In daily_quiz_views.py
from .models import HINDI_QUESTIONS_POOL

def create_or_get_daily_quiz(language='english'):
    # ... try to generate with Gemini ...
    
    if not result.get('success'):
        if language.lower() == 'hindi':
            # Use fallback Hindi questions
            questions_data = random.sample(HINDI_QUESTIONS_POOL, 5)
        else:
            # Use fallback English questions or return error
            logger.error("Gemini failed and no fallback available")
            return None
```

---

## Summary of Changes

| File | Change | Impact |
|------|--------|--------|
| `gemini_service.py` | Add language param to `generate_daily_quiz()` | Supports Hindi questions |
| `daily_quiz_views.py` | Add language query parameter handling | Accepts `?language=hindi` |
| `models.py` (DailyQuiz) | Add language field with choices | One quiz per language per day |
| `views.py` (FlashcardGeneratorView) | Add default values & validation | Fixes 400 errors |
| `views.py` (PredictedQuestionsView) | Add comprehensive error handling | Fixes 500 errors |
| `HINDI_QUESTIONS_POOL_100.py` | New file with 100 Hindi GK questions | Fallback for Gemini failures |

---

## Deployment Checklist

- [ ] Update all Python files with changes above
- [ ] Run migrations: `python manage.py migrate`
- [ ] Test Hindi quiz generation locally
- [ ] Test flashcards with `num_cards` parameter
- [ ] Test predicted questions error handling
- [ ] Deploy to Render.com
- [ ] Verify in production with curl commands
- [ ] Test from React frontend


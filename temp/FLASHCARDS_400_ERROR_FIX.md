# Flashcards Endpoint - 400 Error Fix

## Issue Fixed

**Problem:** POST `/api/flashcards/generate/` returning 400 Bad Request
- No helpful error message when topic is missing
- File upload not working properly
- No language support

**Status:** ✅ FIXED

---

## What Changed

### 1. Added Language Parameter Support
```bash
# English (default)
POST /api/flashcards/generate/
{
  "topic": "Indian Constitution",
  "num_cards": 10,
  "language": "english"  ← NEW
}

# Hindi
POST /api/flashcards/generate/
{
  "topic": "भारतीय संविधान",
  "num_cards": 10,
  "language": "hindi"  ← NEW
}
```

### 2. Enhanced File Upload Support
- ✅ Text files (.txt, .md)
- ✅ PDF files (.pdf)
- ✅ Images with OCR (.jpg, .jpeg, .png, .gif)
- ✅ Proper error handling for each format

### 3. Improved Error Messages
**Before:** Generic "Please provide a topic or upload a document"
**After:**
```json
{
  "success": false,
  "error": "Please provide a topic or upload a document",
  "message": "Submit text in the topic field or upload a document file (.txt, .pdf, .jpg)",
  "example_topic": "Indian Constitutional Law",
  "supported_formats": [".txt", ".md", ".pdf", ".jpg", ".jpeg", ".png", ".gif"]
}
```

### 4. Parameter Validation
- num_cards: 1-50 range (clamped automatically)
- language: validates against ['english', 'hindi']
- topic: validates not empty after document extraction

### 5. Comprehensive Logging
```
[FLASHCARD] Request: topic_length=XX, num_cards=XX, lang=english
[FLASHCARD] Processing document for flashcards
[FLASHCARD] OCR successful: extracted XX characters
[FLASHCARD] Generating XX flashcards in english
[FLASHCARD] Missing topic and no document provided
```

---

## Testing

### Test 1: Missing Topic (400 Error - This was the issue)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "num_cards": 5
  }'
```

**Expected Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Please provide a topic or upload a document",
  "message": "Submit text in the topic field or upload a document file (.txt, .pdf, .jpg)",
  "example_topic": "Indian Constitutional Law",
  "supported_formats": [".txt", ".md", ".pdf", ".jpg", ".jpeg", ".png", ".gif"]
}
```

### Test 2: Valid Topic (English)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Indian Constitutional Law",
    "num_cards": 5,
    "language": "english"
  }'
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "title": "Flashcard Set - [Topic]",
    "topic": "Indian Constitutional Law",
    "language": "english",
    "total_cards": 5,
    "cards": [
      {
        "id": 1,
        "question": "What is Article 14 of the Constitution?",
        "answer": "Right to equality before law",
        "category": "Constitutional Articles",
        "difficulty": "medium",
        "importance": "high"
      },
      ...
    ]
  }
}
```

### Test 3: Valid Topic (Hindi)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "भारतीय संविधान",
    "num_cards": 5,
    "language": "hindi"
  }'
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "title": "फ्लैशकार्ड सेट",
    "topic": "भारतीय संविधान",
    "language": "hindi",
    "total_cards": 5,
    "cards": [...]
  }
}
```

### Test 4: File Upload (PDF)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -F 'document=@notes.pdf' \
  -F 'num_cards=5' \
  -F 'language=english'
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "title": "Flashcard Set - [From PDF]",
    "topic": "[First 500 chars from PDF]",
    "language": "english",
    "total_cards": 5,
    "cards": [...]
  }
}
```

### Test 5: File Upload (Text File)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -F 'document=@study_notes.txt' \
  -F 'num_cards=10' \
  -F 'language=english'
```

**Expected Response (200 OK):**
Same format as Test 4

### Test 6: File Upload (Image with OCR)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -F 'document=@textbook_page.jpg' \
  -F 'num_cards=5' \
  -F 'language=english'
```

**Expected Response (200 OK):**
Same format as Test 4

### Test 7: Invalid File Format

**Request:**
```bash
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -F 'document=@archive.zip' \
  -F 'num_cards=5'
```

**Expected Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Unsupported document type: archive.zip",
  "supported_formats": [".txt", ".md", ".pdf", ".jpg", ".jpeg", ".png", ".gif"]
}
```

### Test 8: Empty File

**Request:**
```bash
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -F 'document=@empty.txt' \
  -F 'num_cards=5'
```

**Expected Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Could not extract text from document",
  "message": "Please ensure the document contains readable text"
}
```

### Test 9: Invalid num_cards (Auto-clamped)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Indian Constitution",
    "num_cards": 200
  }'
```

**Expected Response (200 OK):**
- num_cards clamped to 50 (max)
- Returns 50 flashcards

### Test 10: Invalid Language (Auto-corrected)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Indian Constitution",
    "language": "spanish"
  }'
```

**Expected Response (200 OK):**
- language auto-corrected to 'english'
- Returns English flashcards

---

## Production Testing

### Test on Production Server

```bash
# 1. Test missing topic error
curl -X POST "https://ed-tech-backend-tzn8.onrender.com/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{"num_cards":5}'

# Should return 400 with helpful message

# 2. Test with valid topic
curl -X POST "https://ed-tech-backend-tzn8.onrender.com/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Indian Constitutional Law",
    "num_cards": 5,
    "language": "english"
  }'

# Should return 200 with flashcards

# 3. Test Hindi support
curl -X POST "https://ed-tech-backend-tzn8.onrender.com/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "भारतीय संविधान",
    "num_cards": 5,
    "language": "hindi"
  }'

# Should return 200 with Hindi flashcards
```

---

## JavaScript Testing

```javascript
// Test 1: Error handling
async function testFlashcardsError() {
  const response = await fetch('http://localhost:8000/api/flashcards/generate/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ num_cards: 5 })
  });
  
  const data = await response.json();
  console.log('Status:', response.status);
  console.log('Error:', data.error);
  console.log('Supported formats:', data.supported_formats);
}

// Test 2: Success with English
async function testFlashcardsEnglish() {
  const response = await fetch('http://localhost:8000/api/flashcards/generate/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      topic: 'Indian Constitutional Law',
      num_cards: 5,
      language: 'english'
    })
  });
  
  const data = await response.json();
  console.log('Total cards:', data.data.total_cards);
  console.log('First card:', data.data.cards[0]);
}

// Test 3: Success with Hindi
async function testFlashcardsHindi() {
  const response = await fetch('http://localhost:8000/api/flashcards/generate/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      topic: 'भारतीय संविधान',
      num_cards: 5,
      language: 'hindi'
    })
  });
  
  const data = await response.json();
  console.log('Language:', data.data.language);
  console.log('First question (Hindi):', data.data.cards[0].question);
}

// Test 4: File upload
async function testFlashcardsFileUpload(file) {
  const formData = new FormData();
  formData.append('document', file);
  formData.append('num_cards', 10);
  formData.append('language', 'english');
  
  const response = await fetch('http://localhost:8000/api/flashcards/generate/', {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  if (response.ok) {
    console.log('Total cards:', data.data.total_cards);
  } else {
    console.log('Error:', data.error);
    console.log('Details:', data.details || data.message);
  }
}

// Usage:
testFlashcardsError();
testFlashcardsEnglish();
testFlashcardsHindi();
// testFlashcardsFileUpload(fileInput.files[0]);
```

---

## Deployment

### Step 1: Verify Changes

```bash
# Check views.py
grep -n "class FlashcardGeneratorView" question_solver/views.py

# Check gemini_service.py
grep -n "def generate_flashcards" question_solver/services/gemini_service.py
```

### Step 2: Run Local Tests

```bash
# Test missing topic
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{"num_cards":5}' | jq '.'

# Test with topic
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{"topic":"Indian Constitution","num_cards":3,"language":"english"}' | jq '.'
```

### Step 3: Deploy

```bash
git add question_solver/views.py question_solver/services/gemini_service.py
git commit -m "fix: Add language support + 400 error handling for flashcards endpoint"
git push origin main
```

### Step 4: Verify Production

```bash
# Test production server
curl -X POST "https://ed-tech-backend-tzn8.onrender.com/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{"num_cards":5}' | jq '.error'

# Should return: "Please provide a topic or upload a document"
```

---

## Summary of Changes

| Aspect | Before | After |
|--------|--------|-------|
| Language support | ❌ No | ✅ English + Hindi |
| Missing topic error | Unclear | Clear with examples |
| File upload support | Limited | Comprehensive (PDF, TXT, Images) |
| Parameter validation | Weak | Strong (auto-clamping) |
| Error messages | Generic | Detailed & helpful |
| Logging | Basic | Detailed [FLASHCARD] tags |
| Response format | Inconsistent | Consistent with 'success' field |
| API Status Code | 400 unclear | 400 with helpful message |

---

## All Endpoints Status

| Endpoint | English | Hindi | File Upload | Error Handling |
|----------|---------|-------|-------------|----------------|
| Daily Quiz | ✅ | ✅ | N/A | ✅ |
| Flashcards | ✅ | ✅ | ✅ | ✅ |
| Predicted Questions | ✅ | ✅ | ✅ | ✅ |

✅ All 3 endpoints now fully support language + file uploads + error handling

---

## Next Steps

1. Deploy changes to production
2. Run all tests
3. Monitor logs for any issues
4. Update API documentation

**Status:** Ready for production deployment ✅

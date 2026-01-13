# 5-Minute Deployment Guide - Flashcards 400 Error Fix

## What Was Fixed

**Problem:** Flashcards endpoint returning 400 error with no helpful message
**Solution:** 
- ✅ Added language parameter support (English/Hindi)
- ✅ Fixed 400 error with helpful message
- ✅ Added file upload support (PDF, TXT, Images)
- ✅ Added comprehensive error handling

---

## Quick Verification (2 minutes)

### Test Locally First
```bash
# Test 1: Error (was the issue)
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{"num_cards":5}'
# Expected: 400 with "Please provide a topic or upload a document"

# Test 2: English (should work)
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{"topic":"Indian Constitution","num_cards":3,"language":"english"}'
# Expected: 200 with flashcards

# Test 3: Hindi (should work)
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{"topic":"भारतीय संविधान","num_cards":3,"language":"hindi"}'
# Expected: 200 with Hindi flashcards
```

---

## Deploy to Production (3 minutes)

```bash
# Step 1: Commit changes
git add question_solver/views.py question_solver/services/gemini_service.py
git commit -m "fix: Flashcards - Add language support + 400 error handling"

# Step 2: Push to production
git push origin main

# Wait 1-2 minutes for Render.com auto-deploy...

# Step 3: Verify production
curl -X POST "https://ed-tech-backend-tzn8.onrender.com/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{"num_cards":5}' | jq '.error'

# Expected: "Please provide a topic or upload a document"
```

---

## What Changed

### In question_solver/views.py (FlashcardGeneratorView)

**Added:**
- Language parameter validation (english/hindi)
- Topic/document validation with helpful 400 error
- Document upload support (PDF, TXT, Images with OCR)
- Comprehensive error handling
- Detailed logging with [FLASHCARD] tags

**Response Format (before/after):**

Before:
```json
{
  "error": "Please provide a topic or upload a document"
}
```

After:
```json
{
  "success": false,
  "error": "Please provide a topic or upload a document",
  "message": "Submit text in the topic field or upload a document file (.txt, .pdf, .jpg)",
  "example_topic": "Indian Constitutional Law",
  "supported_formats": [".txt", ".md", ".pdf", ".jpg", ".jpeg", ".png", ".gif"]
}
```

### In question_solver/services/gemini_service.py (generate_flashcards)

**Added:**
- Language parameter to method signature
- Language-specific prompts for Gemini
- Hindi support with देवनागरी script instructions
- Language field in response

---

## Parameters Reference

### Request Parameters

```json
{
  "topic": "String (required unless document provided)",
  "document": "File (optional - .txt, .pdf, .jpg, .png, .gif)",
  "num_cards": "Integer (1-50, default: 10)",
  "language": "String ('english' or 'hindi', default: 'english')"
}
```

### Example Requests

**Minimal (English - default):**
```bash
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{"topic":"Indian Constitution"}'
```

**With all parameters (English):**
```bash
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Indian Constitutional Law",
    "num_cards": 15,
    "language": "english"
  }'
```

**With all parameters (Hindi):**
```bash
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "भारतीय संविधान",
    "num_cards": 15,
    "language": "hindi"
  }'
```

**With file upload:**
```bash
curl -X POST "http://localhost:8000/api/flashcards/generate/" \
  -F 'document=@notes.pdf' \
  -F 'num_cards=10' \
  -F 'language=english'
```

---

## All Endpoints Status

```
✅ Daily Quiz
   GET /api/daily-quiz/?language=english
   GET /api/daily-quiz/?language=hindi

✅ Flashcards  
   POST /api/flashcards/generate/
   Language: english, hindi
   File Upload: pdf, txt, jpg, png, gif

✅ Predicted Questions
   POST /api/predicted-questions/generate/
   Language: english, hindi
   File Upload: pdf, txt, jpg, png, gif
```

---

## Error Codes

| Status | When | Fix |
|--------|------|-----|
| 400 | Missing topic & document | Add topic or upload file |
| 400 | Unsupported file format | Use .txt, .pdf, or image |
| 400 | Empty document | Upload readable file |
| 429 | Quota exceeded | Retry after delay |
| 500 | API failure | Check logs, retry |

---

## Logs to Monitor

After deployment, watch logs for:

```
[FLASHCARD] Request: topic_length=XX, num_cards=XX, lang=english
[FLASHCARD] Processing document for flashcards
[FLASHCARD] Generating XX flashcards in english
[FLASHCARD] Missing topic and no document provided
```

---

## Success Criteria

After deployment, all of these should work:

- [ ] Missing topic returns 400 with helpful message
- [ ] English topic returns 200 with flashcards
- [ ] Hindi topic returns 200 with Hindi flashcards
- [ ] PDF upload returns 200 with flashcards
- [ ] TXT upload returns 200 with flashcards
- [ ] Image upload returns 200 with flashcards
- [ ] Invalid file returns 400 error

---

## Rollback (if needed)

```bash
git revert HEAD
git push origin main
# Render auto-redeploys in 1-2 minutes
```

---

## Production Checklist

- [ ] Code reviewed
- [ ] Local tests pass
- [ ] Git commit created
- [ ] Changes pushed to main
- [ ] Render deployment started
- [ ] Deployment completed (check dashboard)
- [ ] Production endpoints tested
- [ ] Logs show [FLASHCARD] entries
- [ ] No error spikes in logs
- [ ] Response times normal

---

## Summary

✅ Fixed flashcards 400 error
✅ Added language support
✅ Added file upload support
✅ Consistent with other endpoints
✅ Ready for production

**Deployment Time:** 5 minutes
**Risk:** LOW
**Status:** READY 🚀

---

## Files Modified

1. **question_solver/views.py** - FlashcardGeneratorView class
2. **question_solver/services/gemini_service.py** - generate_flashcards method

Both files have comprehensive error handling and logging!

---

Deploy and enjoy working flashcards! 🎉

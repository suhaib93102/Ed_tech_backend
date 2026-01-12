# FRONTEND API FIXES - Form Data Requirement

## Issue Summary
The backend endpoints require **multipart/form-data** with file uploads, but the frontend is sending **JSON** without files.

### Error Examples from Browser Console:
```
POST /api/quiz/generate/ - Payload: 
{userId: 8, numQuestions: 10, difficulty: 'medium', subject: undefined}
↑ WRONG: JSON without file

Error: Please provide a topic or upload a document
↑ Backend response when no 'document' field found
```

---

## ✅ CORRECT IMPLEMENTATION

### 1. Quiz Generation (quiz.ts)

**WRONG ❌ (Current Implementation):**
```typescript
// quiz.ts - Line 82
const payload = {
    userId: 8,
    numQuestions: 10,
    difficulty: 'medium',
    subject: undefined
};

const response = await axios.post('/api/quiz/generate/', payload, {
    headers: { 'Content-Type': 'application/json' }
});
```

**CORRECT ✅ (Required Implementation):**
```typescript
// quiz.ts - generateQuiz function
async function generateQuiz(file: File, userId: number, numQuestions: number, difficulty: string, subject?: string) {
    const formData = new FormData();
    
    // CRITICAL: Add the document file
    formData.append('document', file);
    
    // Add parameters with correct field names (snake_case, not camelCase)
    formData.append('user_id', userId.toString());
    formData.append('num_questions', numQuestions.toString());
    formData.append('difficulty', difficulty);
    
    if (subject) {
        formData.append('subject', subject);
    }

    try {
        const response = await axios.post('/api/quiz/generate/', formData, {
            headers: {
                // CRITICAL: Do NOT set Content-Type, let axios set it automatically
                // This ensures the multipart boundary is included
            }
        });
        
        return response.data;
    } catch (error) {
        if (axios.isAxiosError(error)) {
            console.error('[Quiz Service] generateQuiz error:', {
                endpoint: 'POST /api/quiz/generate/',
                status: error.response?.status,
                message: error.response?.statusText,
                responseData: error.response?.data
            });
            
            // Handle error based on response
            if (error.response?.status === 400) {
                const errorData = error.response.data;
                throw new Error(errorData.error || 'Failed to generate quiz');
            }
        }
        throw error;
    }
}
```

---

### 2. Flashcards Generation (api.ts)

**WRONG ❌ (Current Implementation):**
```typescript
// api.ts - generateFlashcardsFromFile
const payload = {
    userId: user_id,
    numCards: num_cards,
    language: language
};

const response = await axios.post('/api/flashcards/generate/', payload);
```

**CORRECT ✅ (Required Implementation):**
```typescript
// api.ts - generateFlashcardsFromFile
async function generateFlashcardsFromFile(
    file: File,
    user_id: number,
    num_cards: number = 10,
    language: string = 'english'
) {
    const formData = new FormData();
    
    // CRITICAL: Add the document file
    formData.append('document', file);
    
    // Add parameters with correct field names
    formData.append('user_id', user_id.toString());
    formData.append('num_cards', num_cards.toString());
    formData.append('language', language);

    try {
        const response = await axios.post('/api/flashcards/generate/', formData);
        return response.data;
    } catch (error) {
        if (axios.isAxiosError(error)) {
            console.error('[Flashcards] Error generating from file:', {
                endpoint: 'POST /flashcards/generate/',
                status: error.response?.status,
                message: error.response?.statusText,
                responseData: error.response?.data
            });
            
            if (error.response?.status === 400) {
                const errorData = error.response.data;
                throw new Error(errorData.error || 'Failed to extract text from image');
            }
        }
        throw error;
    }
}
```

---

### 3. Predicted Questions Generation (api.ts)

**WRONG ❌ (Current Implementation):**
```typescript
// api.ts - generatePredictedQuestionsFromFile
const payload = {
    userId: user_id,
    numQuestions: num_questions,
    examType: exam_type,
    language: language
};

const response = await axios.post('/api/predicted-questions/generate/', payload);
```

**CORRECT ✅ (Required Implementation):**
```typescript
// api.ts - generatePredictedQuestionsFromFile
async function generatePredictedQuestionsFromFile(
    file: File,
    user_id: number,
    exam_type?: string,
    num_questions: number = 5,
    language: string = 'english'
) {
    const formData = new FormData();
    
    // CRITICAL: Add the document file
    formData.append('document', file);
    
    // Add parameters with correct field names
    formData.append('user_id', user_id.toString());
    formData.append('num_questions', num_questions.toString());
    formData.append('language', language);
    
    if (exam_type) {
        formData.append('exam_type', exam_type);
    }

    try {
        const response = await axios.post('/api/predicted-questions/generate/', formData);
        return response.data;
    } catch (error) {
        if (axios.isAxiosError(error)) {
            console.error('[PredictedQuestions] Error generating from file:', {
                endpoint: 'POST /predicted-questions/generate/',
                status: error.response?.status,
                message: error.response?.statusText,
                responseData: error.response?.data
            });
            
            if (error.response?.status === 400) {
                const errorData = error.response.data;
                throw new Error(errorData.error || 'Failed to extract text from image');
            }
        }
        throw error;
    }
}
```

---

## 🔑 KEY DIFFERENCES

| Aspect | WRONG (Current) | CORRECT (Required) |
|--------|-----------------|-------------------|
| **Content-Type** | `application/json` | `multipart/form-data` (auto) |
| **Body Format** | JSON object | FormData |
| **File Field** | ❌ Not sent | ✅ `formData.append('document', file)` |
| **Field Names** | camelCase (userId) | snake_case (user_id) |
| **Headers Set** | Yes, explicit | No, let axios set it |
| **Backend Error** | 400: "No topic provided" | 400: "Please provide a document" |

---

## 📋 FIELD NAME MAPPING

### Quiz Endpoint
```
Frontend → Backend (CORRECT)
userId → user_id
numQuestions → num_questions
difficulty → difficulty ✓
subject → subject ✓
[NEW] document → document (FILE)
```

### Flashcards Endpoint
```
Frontend → Backend (CORRECT)
userId → user_id
numCards → num_cards
language → language ✓
[NEW] document → document (FILE)
```

### Predicted Questions Endpoint
```
Frontend → Backend (CORRECT)
userId → user_id
numQuestions → num_questions
examType → exam_type
language → language ✓
[NEW] document → document (FILE)
```

---

## ⚡ IMPLEMENTATION CHECKLIST

- [ ] **api.ts**: Update `generatePredictedQuestionsFromFile()` to use FormData with file
- [ ] **api.ts**: Update `generateFlashcardsFromFile()` to use FormData with file
- [ ] **quiz.ts**: Update `generateQuiz()` to use FormData with file
- [ ] **All files**: Replace camelCase with snake_case field names
- [ ] **All files**: Remove explicit `Content-Type: application/json` headers
- [ ] **Test**: Upload image file and verify OCR works
- [ ] **Test**: Check browser console for proper multipart requests

---

## 🧪 QUICK TEST (Browser Console)

```javascript
// Create FormData correctly
const formData = new FormData();
formData.append('document', fileInput.files[0]);
formData.append('user_id', '8');
formData.append('num_questions', '10');
formData.append('difficulty', 'medium');

// Send request
const response = await fetch('/api/quiz/generate/', {
    method: 'POST',
    body: formData
    // DON'T set Content-Type header!
});

const data = await response.json();
console.log(data);
```

---

## 🚀 Production Deployment Status

**Backend Changes** ✅ COMPLETE:
- [x] ocr_service.py - Uses Tesseract OCR only (no Google Vision)
- [x] Dockerfile - Installs tesseract-ocr system dependency
- [x] render.yaml - Uses Docker build (supports system packages)

**Frontend Changes** ⏳ IN PROGRESS:
- [ ] api.ts - Fix Form Data requests
- [ ] quiz.ts - Fix Form Data requests
- [ ] Update all field names (camelCase → snake_case)
- [ ] Remove JSON Content-Type headers

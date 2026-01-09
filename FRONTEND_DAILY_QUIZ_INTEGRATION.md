# 🎯 Daily Quiz Submit Feature - Frontend Integration Guide

## � URGENT: Your Submit Request is Failing

**Your Current Request (FAILING):**
```json
{
  "user_id": "guest_1767931445310",
  "quiz_id": "f1b5ddeb-5424-40b4-9890-2383ff2b87c3",  // ❌ WRONG - This ID doesn't exist
  "answers": {1: 3, 2: 3, 3: 3, 4: 3, 5: 3, 6: 3, 7: 3, 8: 3, 9: 3, 10: 3, 11: 3, 12: 3, 13: 3, 14: 3, 15: 3, 16: 3},
  "time_taken_seconds": 20
}
```

**API Response:** `{"error":"Quiz not found"}`

**Why It's Failing:**
1. **Quiz ID Mismatch**: You're using `f1b5ddeb-5424-40b4-9890-2383ff2b87c3` but today's quiz ID is `323f3963-6e74-4401-80e1-5a2a52eababc`
2. **Too Many Answers**: You're sending 16 answers but the quiz only has 5 questions
3. **Not Fetching from API**: You're still using local/hardcoded data instead of the API

---

## 🔄 Complete Flow: Create Quiz → Submit Quiz

### **Phase 1: Create/Fetch Quiz (GET Request)**

**API Endpoint:** `GET /api/daily-quiz/?user_id={user_id}`

**What Backend Does:**
1. Checks if user already attempted today's quiz
2. If not attempted: Generates new quiz with UUID
3. Returns quiz data with current `quiz_id`

**Current API Response (Working):**
```json
{
  "quiz_id": "323f3963-6e74-4401-80e1-5a2a52eababc",  // ✅ Today's real quiz ID
  "already_attempted": false,
  "questions": [
    {"id": 1, "question": "Which planet...", "options": ["Venus", "Mars", "Jupiter", "Saturn"]},
    {"id": 2, "question": "The Great Pyramid...", "options": ["Tutankhamun", "Ramesses II", "Khufu", "Akhenaten"]},
    {"id": 3, "question": "What is the capital...", "options": ["Toronto", "Vancouver", "Montreal", "Ottawa"]},
    {"id": 4, "question": "In J.R.R. Tolkien's...", "options": ["Glaurung", "Ancalagon", "Smaug", "Drogon"]},
    {"id": 5, "question": "What does WWW stand for?", "options": ["Wireless Web Works", "World Web Wonders", "World Wide Web", "Western World Web"]}
  ],
  "coins": {"attempt_bonus": 5, "per_correct_answer": 10, "max_possible": 55}
}
```

### **Phase 2: User Answers Questions**

**Frontend Logic:**
```typescript
// ✅ CORRECT - Store answers as user selects
const [userAnswers, setUserAnswers] = useState<Record<string, number>>({});

// When user selects answer for question 1, option 2:
setUserAnswers(prev => ({ ...prev, "1": 2 }));  // Question 1: option index 2

// Final answers object should be:
{
  "1": 2,  // Question 1: Mars (option 2)
  "2": 2,  // Question 2: Khufu (option 2) 
  "3": 3,  // Question 3: Ottawa (option 3)
  "4": 2,  // Question 4: Smaug (option 2)
  "5": 2   // Question 5: World Wide Web (option 2)
}
```

### **Phase 3: Submit Quiz (POST Request)**

**API Endpoint:** `POST /api/daily-quiz/submit/`

**Required Request Format:**
```json
{
  "user_id": "guest_1767931445310",
  "quiz_id": "323f3963-6e74-4401-80e1-5a2a52eababc",  // ✅ MUST match API's quiz_id
  "answers": {
    "1": 2,  // ✅ String keys, number values (0-3)
    "2": 2,
    "3": 3,
    "4": 2,
    "5": 2
  },
  "time_taken_seconds": 120
}
```

**What Backend Does:**
1. Validates `quiz_id` exists in database
2. Checks user hasn't already attempted
3. Grades answers against correct answers
4. Calculates coins earned
5. Saves attempt to database
6. Returns detailed results

---

## 📊 Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND                                │
├─────────────────────────────────────────────────────────────┤
│ 1. User Opens Daily Quiz Screen                            │
│    → Call loadQuiz()                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    API CALL                                │
├─────────────────────────────────────────────────────────────┤
│ 2. GET /api/daily-quiz/?user_id=guest_123                  │
│    Headers: Accept: application/json                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND                                 │
├─────────────────────────────────────────────────────────────┤
│ 3. Backend Processing:                                     │
│    • Check if quiz exists for today                        │
│    • Generate new quiz if needed                           │
│    • Return quiz_id, questions, coins                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND                                │
├─────────────────────────────────────────────────────────────┤
│ 4. Store API Response:                                     │
│    • quizId = response.quiz_id                             │
│    • questions = response.questions                        │
│    • coins = response.coins                                │
│    • already_attempted = response.already_attempted        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND                                │
├─────────────────────────────────────────────────────────────┤
│ 5. User Answers Questions:                                 │
│    • Track selected options: { "1": 2, "2": 0, ... }       │
│    • Store in userAnswers state                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND                                │
├─────────────────────────────────────────────────────────────┤
│ 6. User Clicks Submit                                       │
│    → Call submitQuiz()                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    API CALL                                │
├─────────────────────────────────────────────────────────────┤
│ 7. POST /api/daily-quiz/submit/                            │
│    Body: {                                                 │
│      user_id: "guest_123",                                 │
│      quiz_id: "323f3963-6e74-4401-80e1-5a2a52eababc",    │
│      answers: {"1": 2, "2": 0, "3": 1, "4": 3, "5": 0},   │
│      time_taken_seconds: 120                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND                                 │
├─────────────────────────────────────────────────────────────┤
│ 8. Backend Processing:                                     │
│    • Validate quiz_id exists                               │
│    • Check not already attempted                           │
│    • Grade answers                                         │
│    • Calculate coins                                       │
│    • Save to database                                      │
│    • Return results                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND                                │
├─────────────────────────────────────────────────────────────┤
│ 9. Handle Response:                                        │
│    • Show results                                          │
│    • Animate coins                                         │
│    • Update user balance                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚨 Your Current Problem (Visual)

**What You're Doing (BROKEN):**
```
Frontend                    API                     Database
   │                          │                          │
   │  Uses local JSON        │                          │
   │  quiz_id: "f1b5ddeb..."  │                          │
   │                          │                          │
   │  POST submit             │  ──────────────────────► │
   │  quiz_id not found       │                          │
   │                          │  ◄────────────────────── │
   │  404 "Quiz not found"    │                          │
```

**What You Need to Do (WORKING):**
```
Frontend                    API                     Database
   │                          │                          │
   │  GET daily-quiz          │  ──────────────────────► │
   │                          │  Generate quiz           │
   │  ◄────────────────────── │  quiz_id: "323f3963..."  │
   │  Store quiz_id           │                          │
   │                          │                          │
   │  POST submit             │  ──────────────────────► │
   │  quiz_id found           │  Validate & grade        │
   │                          │                          │
   │  ◄────────────────────── │  ◄────────────────────── │
   │  200 Success + coins     │                          │
```

---

## 🛠️ Exact Code Changes Needed

### **File: `DailyQuizScreen.tsx` (or equivalent)**

**REMOVE this (if exists):**
```typescript
// ❌ DELETE - Don't load from local files
import DailyQuizData from './DailyQuiz.json';
const questions = DailyQuizData.questions;
const quizId = 'f1b5ddeb-5424-40b4-9890-2383ff2b87c3'; // Hardcoded
```

**ADD this:**
```typescript
// ✅ ADD - Fetch from API
const [quizId, setQuizId] = useState<string>('');
const [questions, setQuestions] = useState([]);
const [alreadyAttempted, setAlreadyAttempted] = useState(false);

useEffect(() => {
  loadQuiz();
}, []);

const loadQuiz = async () => {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/api/daily-quiz/`,
      { params: { user_id: userId } }
    );
    
    setQuizId(response.data.quiz_id);  // ✅ Store the real quiz_id
    setQuestions(response.data.questions);
    setAlreadyAttempted(response.data.already_attempted);
    
    console.log('Loaded quiz_id:', response.data.quiz_id);
  } catch (error) {
    console.error('Failed to load quiz:', error);
  }
};
```

### **File: `api.ts` or service file**

**ADD submit function:**
```typescript
export const submitDailyQuiz = async (
  userId: string,
  quizId: string,  // From API, not hardcoded
  answers: Record<string, number>,
  timeTaken: number
) => {
  const response = await axios.post(
    `${API_BASE_URL}/api/daily-quiz/submit/`,
    {
      user_id: userId,
      quiz_id: quizId,  // ✅ Use the quiz_id from loadQuiz
      answers: answers,  // ✅ Only 5 answers, string keys
      time_taken_seconds: timeTaken
    }
  );
  return response.data;
};
```

---

## 🧪 Test Your Fix

**1. Check Console After Loading Quiz:**
```javascript
console.log('Quiz ID:', quizId);
// Should show: "323f3963-6e74-4401-80e1-5a2a52eababc"
```

**2. Check Answers Format:**
```javascript
console.log('Answers:', userAnswers);
// Should show: {"1": 2, "2": 0, "3": 1, "4": 3, "5": 0}
```

**3. Test Submit Request:**
```javascript
// Should send POST to /api/daily-quiz/submit/ with:
// quiz_id: "323f3963-6e74-4401-80e1-5a2a52eababc" ✅
// answers: {"1": 2, "2": 0, "3": 1, "4": 3, "5": 0} ✅
```

**4. Expected Response:**
```json
{
  "success": true,
  "message": "🎉 Quiz completed! You earned 25 coins!",
  "result": {
    "correct_count": 2,
    "total_questions": 5,
    "score_percentage": 40.0,
    "coins_earned": 25
  }
}
```

---

## 🎯 Summary

**The Issue:** You're using a quiz_id that doesn't exist in the database.

**The Fix:** Always fetch the quiz from the API first, then use that quiz_id for submission.

**Key Changes:**
1. Remove local JSON loading
2. Add API call to get daily quiz
3. Store the returned quiz_id
4. Use that quiz_id in submit request
5. Ensure answers format matches (5 questions, string keys)

**Backend is working perfectly** - this is purely a frontend integration issue.

---

## 🔧 Required Frontend Changes

### **1. Fix Quiz ID Format Issue** ⚠️ CRITICAL

**Current Problem:**
```typescript
// ❌ WRONG - Frontend is generating custom quiz IDs
const quizId = `daily-quiz-${Date.now()}`; // "daily-quiz-1767872306515"
```

**Backend Expects:**
```typescript
// ✅ CORRECT - Use the UUID returned from the API
const quizId = "f499b520-4798-4b06-9061-3cb0ca14d3d2"; // UUID format
```

**Fix Location:** `DailyQuizScreen.tsx` or wherever quiz state is initialized

**Step-by-Step Fix:**

1. **When you fetch the quiz**, extract the `quiz_id` from the API response:
```typescript
// Example: api.ts or mockTestService.ts
export const getDailyQuiz = async (userId: string) => {
  const response = await axios.get(`${API_BASE_URL}/api/daily-quiz/`, {
    params: { user_id: userId }
  });
  
  return response.data; // Contains quiz_id, questions, coins, etc.
};
```

2. **In DailyQuizScreen.tsx**, store the quiz_id from API response:
```typescript
const loadQuiz = async () => {
  try {
    const quizData = await getDailyQuiz(userId);
    
    // ✅ CORRECT - Use the quiz_id from API
    setQuizId(quizData.quiz_id); // This is the UUID
    setQuestions(quizData.questions);
    setCoinsInfo(quizData.coins);
    
    console.log('Quiz ID from API:', quizData.quiz_id); // Should be UUID format
  } catch (error) {
    console.error('Failed to load quiz:', error);
  }
};
```

3. **Never generate your own quiz ID** - Always use what the API returns

---

### **2. Correct Submit Request Format**

**API Contract:**
```typescript
interface SubmitDailyQuizRequest {
  user_id: string;              // Required: User identifier
  quiz_id: string;               // Required: UUID from GET /api/daily-quiz/
  answers: Record<string, number>; // Required: {"1": 0, "2": 2, "3": 1, ...}
  time_taken_seconds?: number;   // Optional: Time in seconds
}
```

**Example Implementation:**
```typescript
// api.ts or mockTestService.ts
export const submitDailyQuiz = async (
  userId: string,
  quizId: string,  // ⚠️ This MUST be the UUID from the API, not custom generated
  answers: Record<string, number>,
  timeTaken: number
) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/api/daily-quiz/submit/`,
      {
        user_id: userId,
        quiz_id: quizId,  // ✅ UUID from API
        answers: answers,  // {"1": 0, "2": 2, "3": 1, ...}
        time_taken_seconds: timeTaken
      },
      {
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
    
    return response.data;
  } catch (error) {
    console.error('Submit error:', error.response?.data || error.message);
    throw error;
  }
};
```

**Answers Format:**
```typescript
// ✅ CORRECT - String keys, number values (option index 0-3)
const answers = {
  "1": 2,  // Question 1: Selected option index 2 (third option)
  "2": 0,  // Question 2: Selected option index 0 (first option)
  "3": 3,  // Question 3: Selected option index 3 (fourth option)
  "4": 1,  // Question 4: Selected option index 1 (second option)
  "5": 0   // Question 5: Selected option index 0 (first option)
};

// ❌ WRONG - Don't use these formats
const wrongAnswers1 = { 1: "A", 2: "B" };  // Wrong: letter answers
const wrongAnswers2 = { "q1": 0 };         // Wrong: custom keys
```

---

### **3. Handle API Response Correctly**

**Success Response Structure:**
```typescript
interface SubmitSuccessResponse {
  success: true;
  message: string;  // "🎉 Quiz completed! You earned 15 coins!"
  result: {
    correct_count: number;      // How many correct
    total_questions: number;    // Total questions (always 5)
    score_percentage: number;   // 0-100
    coins_earned: number;       // Total coins earned
    time_taken_seconds: number;
    attempt_bonus: number;      // Bonus for attempting (5 coins)
    per_correct: number;        // Coins per correct answer (10 coins)
    max_possible: number;       // Max coins possible (55)
  };
  coin_breakdown: {
    attempt_bonus: number;
    correct_answers: number;
    coins_per_correct: number;
    correct_answer_coins: number;
    total_earned: number;
  };
  results: Array<{
    question_id: number;
    question: string;
    options: Array<{ id: string; text: string }>;
    user_answer: { id: string; text: string };
    correct_answer: { id: string; text: string };
    is_correct: boolean;
    explanation: string;
    fun_fact: string;
    category: string;
  }>;
  total_coins: number;
  show_coin_animation: boolean;
}
```

**Error Response Structure:**
```typescript
interface SubmitErrorResponse {
  error: string;
  message?: string;
  debug_message?: string;
}

// Common errors:
// - "quiz_id and answers are required"
// - "Quiz already attempted"
// - "Quiz not found"
// - "Invalid UUID format"
```

**Implementation:**
```typescript
// DailyQuizScreen.tsx
const submitQuiz = async () => {
  try {
    const result = await submitDailyQuiz(
      userId,
      quizId,  // ✅ UUID from API, not custom generated
      userAnswers,
      timeTaken
    );
    
    if (result.success) {
      // Show success UI
      setCoinsEarned(result.result.coins_earned);
      setQuizResults(result.results);
      showCelebration();
    }
  } catch (error: any) {
    if (error.response?.status === 400) {
      // Quiz already attempted
      alert(error.response.data.message);
    } else if (error.response?.status === 500) {
      // Check debug_message for UUID validation errors
      console.error('Server error:', error.response.data);
    }
  }
};
```

---

### **4. Complete Flow Diagram**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User Opens Daily Quiz Screen                             │
└────────────────────┬────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. GET /api/daily-quiz/?user_id={userId}                   │
│    Response: {                                               │
│      quiz_id: "f499b520-4798-4b06-9061-3cb0ca14d3d2", ✅   │
│      questions: [...],                                       │
│      coins: { attempt_bonus: 5, per_correct_answer: 10 }    │
│    }                                                         │
└────────────────────┬────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Store quiz_id in State                                   │
│    const [quizId, setQuizId] = useState("");                │
│    setQuizId(response.quiz_id); // ✅ UUID from API         │
└────────────────────┬────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. User Answers Questions                                   │
│    Store answers: { "1": 2, "2": 0, "3": 1, "4": 3, "5": 0 }│
└────────────────────┬────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. User Clicks Submit                                        │
│    POST /api/daily-quiz/submit/                             │
│    Body: {                                                   │
│      user_id: "guest_1767872304915",                        │
│      quiz_id: "f499b520-4798-4b06-9061-3cb0ca14d3d2", ✅   │
│      answers: {"1": 2, "2": 0, "3": 1, "4": 3, "5": 0},    │
│      time_taken_seconds: 120                                │
│    }                                                         │
└────────────────────┬────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Display Results & Coins Earned                           │
│    - Show correct/incorrect answers                         │
│    - Animate coin rewards                                   │
│    - Show explanations & fun facts                          │
└─────────────────────────────────────────────────────────────┘
```

---

### **5. Common Issues & Solutions**

| Issue | Cause | Solution |
|-------|-------|----------|
| 404 Not Found | Wrong URL endpoint | Use `/api/daily-quiz/submit/` exactly |
| **404 "Quiz not found"** ⚠️ | **Quiz ID from local JSON, not API** | **MUST fetch quiz from API, not use local questions** |
| 500 "not a valid UUID" | Custom quiz ID format | Use `quiz_id` from API response |
| Quiz already attempted | User submitted before | Check `already_attempted` field in GET response |
| CORS error | Missing headers | Backend already configured, should work |
| Empty response | Network timeout | Add retry logic and loading states |

---

### **6. Testing Checklist**

```typescript
// Test 1: Verify quiz_id format
console.log('Quiz ID format:', quizId);
// ✅ Should be: "f499b520-4798-4b06-9061-3cb0ca14d3d2"
// ❌ Should NOT be: "daily-quiz-1767872306515"

// Test 2: Verify answers format
console.log('Answers:', answers);
// ✅ Should be: {"1": 2, "2": 0, "3": 1, "4": 3, "5": 0}
// ❌ Should NOT be: {q1: "A", q2: "B"}

// Test 3: Check API endpoint
console.log('Submit URL:', `${API_BASE_URL}/api/daily-quiz/submit/`);
// ✅ Should be: "https://ed-tech-backend-tzn8.onrender.com/api/daily-quiz/submit/"

// Test 4: Verify request headers
console.log('Headers:', headers);
// ✅ Should include: { 'Content-Type': 'application/json' }

// Test 5: Check user_id
console.log('User ID:', userId);
// ✅ Should be: "guest_1767872304915" or similar
```

---

### **7. Code Files to Modify**

#### **File 1: `api.ts` or `mockTestService.ts`**
```typescript
// Add/Update this function
export const submitDailyQuiz = async (
  userId: string,
  quizId: string,  // ⚠️ Must be UUID from API
  answers: Record<string, number>,
  timeTaken: number
) => {
  const response = await axios.post(
    `${API_BASE_URL}/api/daily-quiz/submit/`,
    {
      user_id: userId,
      quiz_id: quizId,
      answers: answers,
      time_taken_seconds: timeTaken
    }
  );
  return response.data;
};
```

#### **File 2: `DailyQuizScreen.tsx`**
```typescript
// Update state management
const [quizId, setQuizId] = useState<string>("");  // Store UUID

// Update loadQuiz function
const loadQuiz = async () => {
  const data = await getDailyQuiz(userId);
  setQuizId(data.quiz_id);  // ✅ Use API's quiz_id
  setQuestions(data.questions);
};

// Update submitQuiz function
const submitQuiz = async () => {
  await submitDailyQuiz(userId, quizId, answers, timeTaken);
  // Handle response...
};
```

---

### **8. Verification Steps**

1. **Open Browser DevTools** → Network tab
2. **Load Daily Quiz** and verify:
   - GET request to `/api/daily-quiz/` succeeds
   - Response contains `quiz_id` (UUID format)
3. **Answer questions** and click Submit
4. **Check POST request** to `/api/daily-quiz/submit/`:
   - Request payload has correct `quiz_id` (UUID)
   - Request payload has correct `answers` format
   - Status code is 200 (success) not 404/500
5. **Verify response** contains:
   - `success: true`
   - `result` with coins earned
   - `results` array with detailed feedback

---

### **9. Example Working Request**

```bash
# This curl command works - verify your frontend matches this:
curl -X POST https://ed-tech-backend-tzn8.onrender.com/api/daily-quiz/submit/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "guest_test_user",
    "quiz_id": "f499b520-4798-4b06-9061-3cb0ca14d3d2",
    "answers": {"1": 2, "2": 0, "3": 3, "4": 1, "5": 2},
    "time_taken_seconds": 120
  }'

# Expected Response:
{
  "success": true,
  "message": "🎉 Quiz completed! You earned 25 coins!",
  "result": {
    "correct_count": 2,
    "total_questions": 5,
    "score_percentage": 40.0,
    "coins_earned": 25,
    ...
  }
}
```

---

## 🚀 Quick Fix Summary

**CRITICAL FIX - Your Specific Issue:**
```typescript
// ❌ WRONG - You're doing this (loading from local file)
const questions = require('./DailyQuiz.json');
const quizId = '7be50129-0ae0-4aeb-8802-7ea1b3c5f79d'; // Static UUID from file

// ✅ CORRECT - Do this instead (fetch from API)
const { quiz_id, questions } = await fetch(
  'https://ed-tech-backend-tzn8.onrender.com/api/daily-quiz/?user_id=' + userId
).then(r => r.json());
const quizId = quiz_id; // Dynamic UUID from today's quiz
```

**If you only do ONE thing, do this:**
```typescript
// ❌ REMOVE THIS (if it exists)
const quizId = `daily-quiz-${Date.now()}`;

// ✅ REPLACE WITH THIS
const quizData = await getDailyQuiz(userId);
const quizId = quizData.quiz_id;  // Use the UUID from API
```

**Additional Check - Verify you're NOT using local JSON:**
```typescript
// ❌ DELETE/REMOVE these patterns if you find them:
import DailyQuizQuestions from './DailyQuiz.json';
const questions = DailyQuizJSON.questions;
const questions = mockQuestions;
loadQuestionsFromFile();
```

---

## ⚠️ CRITICAL: "Quiz not found" Error (404)

**Your Error:**
```json
{
  "user_id": "guest_1767931445310",
  "quiz_id": "7be50129-0ae0-4aeb-8802-7ea1b3c5f79d",
  "answers": {1: 3, 2: 3, ...}
}
Response: {"error":"Quiz not found"}
```

**Root Cause:**
You are using questions from a **local JSON file** (like `DailyQuiz.json`) instead of fetching from the API. The `quiz_id` you're using doesn't exist in the database.

**Why This Happens:**
```typescript
// ❌ WRONG - Loading from local file
const questions = await loadQuestionsFromJSON('DailyQuiz.json');
const quizId = generateRandomUUID(); // This ID doesn't exist in database!
```

**The Fix:**
```typescript
// ✅ CORRECT - Always fetch from API
const getDailyQuiz = async (userId: string) => {
  const response = await axios.get(
    `https://ed-tech-backend-tzn8.onrender.com/api/daily-quiz/`,
    { params: { user_id: userId } }
  );
  
  return {
    quizId: response.data.quiz_id,      // Real UUID from database
    questions: response.data.questions,  // Real questions from database
    coins: response.data.coins
  };
};
```

**What You Need to Change:**

1. **Remove all local JSON file loading:**
```typescript
// ❌ DELETE these lines
import DailyQuizJSON from './DailyQuiz.json';
const questions = DailyQuizJSON.questions;
const quizId = `daily-quiz-${Date.now()}`;
```

2. **Always use the API:**
```typescript
// ✅ ADD this instead
useEffect(() => {
  const loadQuiz = async () => {
    try {
      const apiQuiz = await getDailyQuiz(userId);
      setQuizId(apiQuiz.quizId);           // From API
      setQuestions(apiQuiz.questions);      // From API
      setCoinsInfo(apiQuiz.coins);         // From API
    } catch (error) {
      console.error('Failed to load quiz:', error);
    }
  };
  
  loadQuiz();
}, [userId]);
```

3. **Verify in console:**
```typescript
console.log('Quiz ID from API:', quizId);
// Should output: "f499b520-4798-4b06-9061-3cb0ca14d3d2" (changes daily)
// NOT: "7be50129-0ae0-4aeb-8802-7ea1b3c5f79d" (from your local file)
```

**Key Point:**
- The backend generates a NEW quiz daily with a NEW UUID
- Your local JSON file has a static UUID that doesn't match today's quiz
- You MUST fetch from `/api/daily-quiz/` to get the current quiz ID

---

## 📞 Support

If issues persist after these changes:
1. Check browser console for errors
2. Verify network tab shows correct request format
3. Ensure API_BASE_URL is correct
4. Test with curl command above to verify backend is working

**Backend is confirmed working** - all issues are frontend integration problems.

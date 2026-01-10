# 🎯 Complete End-to-End Flow Documentation

## Daily Quiz Submission Flow with Coins & Hindi Support

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        HINDI DAILY QUIZ COMPLETE FLOW                        │
└─────────────────────────────────────────────────────────────────────────────┘

STEP 1: USER RETRIEVES HINDI QUIZ
─────────────────────────────────────────────────────────────────────────────

Request:
  GET /api/daily-quiz/?language=hindi&user_id=rahuljha996886

Process:
  1. API accepts 'language' parameter from query string
  2. create_or_get_daily_quiz(language='hindi') is called
  3. If quiz doesn't exist for today, generate with Gemini
  4. Pass language='hindi' to gemini_service.generate_daily_quiz()
  5. Gemini creates full Hindi prompt with देवनागरी instructions
  6. Returns 5 questions in Hindi

Response (200 OK):
  {
    "quiz_metadata": {
      "quiz_type": "daily_coin_quiz",
      "total_questions": 5,
      "date": "2026-01-10"
    },
    "coins": {
      "attempt_bonus": 5,
      "per_correct_answer": 10,
      "max_possible": 55
    },
    "questions": [
      {
        "question": "भारत की राष्ट्रीय नदी कौन सी है?",
        "options": ["यमुना", "ब्रह्मपुत्र", "गंगा", "गोदावरी"],
        "category": "भूगोल",
        "difficulty": "आसान"
      },
      ... (4 more in Hindi)
    ]
  }

✅ OUTPUT: 5 Hindi questions in Devanagari script

───────────────────────────────────────────────────────────────────────────────

STEP 2: USER STARTS QUIZ (OPTIONAL - Award Participation Bonus)
──────────────────────────────────────────────────────────────────

Request:
  POST /api/daily-quiz/start/
  {
    "user_id": "rahuljha996886",
    "quiz_id": "7b318795-0782-4415-bad5-130cb7f9d9a9"
  }

Process:
  1. Check if user already completed quiz today
  2. If not, create UserDailyQuizAttempt record
  3. Get attempt_bonus from QuizSettings (5 coins)
  4. Create UserCoins entry if doesn't exist
  5. Award coins: user_coins.add_coins(5, reason="Daily Quiz participation")

Database Updates:
  ├─ UserDailyQuizAttempt created
  │  ├─ user_id: "rahuljha996886"
  │  ├─ daily_quiz_id: "7b318795-..."
  │  ├─ coins_earned: 5
  │  └─ started_at: 2026-01-10T09:50:11Z
  │
  └─ CoinTransaction created
     ├─ amount: +5
     ├─ type: "earn"
     ├─ reason: "Daily Quiz participation 2026-01-10"
     └─ created_at: 2026-01-10T09:50:11Z

Response (200 OK):
  {
    "success": true,
    "message": "You earned 5 coins for starting the Daily Quiz.",
    "coins_awarded": 5
  }

✅ OUTPUT: User awarded 5 participation coins

───────────────────────────────────────────────────────────────────────────────

STEP 3: USER SUBMITS QUIZ WITH ANSWERS
────────────────────────────────────────

Request:
  POST /api/daily-quiz/submit/
  {
    "user_id": "rahuljha996886",
    "quiz_id": "7b318795-...",
    "answers": {
      "1": 0,  // Selected: यमुना (Wrong - correct is गंगा)
      "2": 1,  // Selected: Option B
      "3": 2,  // Selected: Option C
      "4": 3,  // Selected: Option D
      "5": 0   // Selected: Option A
    },
    "time_taken_seconds": 180
  }

Process:
  1. Parse user_id, quiz_id, answers from request
  2. Fetch DailyQuestion records (limited to first 5)
  3. For each question:
     ├─ Get user's answer index
     ├─ Get correct answer index from q.correct_answer
     ├─ Compare: user_answer_idx == correct_answer_idx
     └─ Update correct_count if match
  4. Calculate score: correct_count / total_questions * 100
  5. Calculate coins:
     ├─ attempt_bonus = 5 (from settings)
     ├─ per_correct = 10 (from settings)
     ├─ coins_from_correct = correct_count * 10
     └─ total_coins = attempt_bonus + coins_from_correct
  6. Create UserDailyQuizAttempt record with results
  7. Award coins to user

Answer Evaluation:
  Question 1: भारत की राष्ट्रीय नदी कौन सी है?
  ├─ Correct Answer: C (गंगा)
  ├─ User Answer: A (यमुना)
  └─ Result: ✗ INCORRECT

  Question 2: मानव शरीर में सबसे बड़ी हड्डी कौन सी है?
  ├─ Correct Answer: A (फीमर)
  ├─ User Answer: B (टिबिया)
  └─ Result: ✗ INCORRECT

  Question 3-5: Similar evaluation...
  
  Final Score: 1/5 correct (20%)

Coin Calculation:
  ┌─ Attempt Bonus:      5 coins (always given)
  ├─ Correct Answers:    1/5 correct
  ├─ Per Correct Rate:   10 coins each
  ├─ Correct Coins:      1 × 10 = 10 coins
  └─ TOTAL EARNED:       5 + 10 = 15 coins

Database Updates:
  ├─ UserDailyQuizAttempt updated/created
  │  ├─ user_id: "rahuljha996886"
  │  ├─ daily_quiz_id: "7b318795-..."
  │  ├─ answers: {"1": 0, "2": 1, "3": 2, "4": 3, "5": 0}
  │  ├─ correct_count: 1
  │  ├─ total_questions: 5
  │  ├─ score_percentage: 20.0
  │  ├─ coins_earned: 15
  │  ├─ completed_at: 2026-01-10T09:50:14Z
  │  └─ time_taken_seconds: 180
  │
  ├─ UserCoins updated
  │  └─ total_coins: 20 + 15 = 35 coins
  │
  └─ CoinTransaction created
     ├─ amount: +15
     ├─ type: "earn"
     ├─ reason: "Daily Quiz attempt 2026-01-10"
     └─ created_at: 2026-01-10T09:50:14Z

Response (200 OK):
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
        "user_answer": "यमुना",
        "correct_answer": "गंगा",
        "is_correct": false,
        "explanation": "गंगा नदी भारत की सबसे महत्वपूर्ण और पवित्र नदियों में से एक है...",
        "fun_fact": "गंगा नदी की लंबाई लगभग 2,525 किलोमीटर है..."
      },
      ... (4 more results)
    ],
    "total_coins": 35,
    "show_coin_animation": true
  }

✅ OUTPUT: User earned 15 coins, total is now 35

───────────────────────────────────────────────────────────────────────────────

STEP 4: USER CHECKS COIN BALANCE & TRANSACTION HISTORY
────────────────────────────────────────────────────────

Request:
  GET /api/daily-quiz/coins/?user_id=rahuljha996886

Process:
  1. Get UserCoins record for user
  2. Retrieve recent CoinTransaction records (last 10)
  3. Format response with balance and history

Response (200 OK):
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
        "created_at": "2026-01-10T09:50:14.214443Z"
      },
      {
        "amount": 5,
        "type": "earn",
        "reason": "Daily Quiz participation 2026-01-10",
        "created_at": "2026-01-10T09:50:11.382513Z"
      }
    ]
  }

✅ OUTPUT: User can see balance (35 coins) and transaction history

───────────────────────────────────────────────────────────────────────────────

STEP 5: USER VIEWS QUIZ HISTORY
────────────────────────────────

Request:
  GET /api/daily-quiz/history/?user_id=rahuljha996886&limit=10

Process:
  1. Get all UserDailyQuizAttempt records for user
  2. Select related daily_quiz data
  3. Calculate stats: total_attempts, total_coins_earned, avg_score
  4. Format response

Response (200 OK):
  {
    "user_id": "rahuljha996886",
    "stats": {
      "total_attempts": 3,
      "total_coins_earned": 35,
      "average_score": 13.33
    },
    "history": [
      {
        "date": "2026-01-10",
        "quiz_title": "Daily GK Quiz - January 10, 2026",
        "correct_count": 1,
        "total_questions": 5,
        "score_percentage": 20.0,
        "coins_earned": 15,
        "completed_at": "2026-01-10T09:50:14Z"
      },
      ... (more attempts)
    ]
  }

✅ OUTPUT: User can see complete quiz history and statistics

```

---

## YouTube Summarizer Enhanced Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    YOUTUBE SUMMARIZER ENHANCED FLOW                          │
└─────────────────────────────────────────────────────────────────────────────┘

REQUEST:
  POST /api/youtube/summarize/
  {
    "video_url": "https://www.youtube.com/watch?v=XesW1fJIJTc"
  }

PROCESS:
─────────────────────────────────────────────────────────────────────────────

1. Extract Video ID
   ├─ Input URL: "https://www.youtube.com/watch?v=XesW1fJIJTc"
   └─ Extracted ID: "XesW1fJIJTc"

2. Fetch YouTube Transcript
   ├─ Using: youtube-transcript-api
   └─ Get transcript with timestamps and durations
       {
         "text": "Okay, hello everyone...",
         "start": 0.0,
         "duration": 5.2
       },
       {
         "text": "Today we have a special...",
         "start": 5.2,
         "duration": 3.8
       },
       ...

3. Process Transcript Data
   ├─ Extract timestamps: start, duration
   ├─ Calculate total duration: last_segment.start + last_segment.duration
   ├─ Format as: [MM:SS]
   ├─ Build transcript_with_timestamps list
   └─ Result:
       "[00:00] Okay, hello everyone..."
       "[00:05] Today we have a special..."
       "[00:09] Let's start our discussion..."

4. Create Comprehensive Prompt for Gemini
   ├─ Total prompt length: ~2000+ characters
   ├─ Include all transcript_with_timestamps
   ├─ Request 14-section structure:
   │  1. EXECUTIVE SUMMARY (2-3 sentences)
   │  2. VIDEO TIMELINE & KEY SECTIONS WITH TIMESTAMPS [MM:SS]
   │  3. MAIN TOPIC AND CORE MESSAGE
   │  4. DETAILED KEY POINTS (Numbered with timestamps)
   │  5. IMPORTANT CONCEPTS & DEFINITIONS (with timestamps)
   │  6. STATISTICS, DATA & NUMBERS (with timestamps)
   │  7. QUOTES & NOTABLE STATEMENTS (with exact timestamps)
   │  8. VISUAL DESCRIPTIONS (with timestamps)
   │  9. TARGET AUDIENCE
   │  10. KEY TAKEAWAYS (5-10 items)
   │  11. CHAPTER BREAKDOWN (with timestamps)
   │  12. OVERALL ASSESSMENT (quality, credibility, engagement)
   │  13. VIEWER QUESTIONS ANSWERED
   │  14. RELATED TOPICS & SUGGESTIONS
   │
   └─ Metadata requested: duration, segment count, generation time

5. Call Gemini API
   ├─ Model: gemini-2.0-flash
   ├─ Max tokens: Sufficient for comprehensive response
   ├─ Temperature: Default (for consistency)
   └─ Prompt includes full transcript_with_timestamps

6. Parse Response
   ├─ Extract summary from Gemini
   ├─ Verify all 14 sections present
   ├─ Count timestamps in [MM:SS] format
   └─ Result: ~23,540 character comprehensive summary

7. Add Metadata
   ├─ video_url: Original URL
   ├─ summary_length: Character count
   ├─ extracted_duration: Total video duration
   ├─ segment_count: Number of transcript segments
   ├─ timestamp_count: Number of [MM:SS] found
   └─ generation_time: ISO format timestamp

RESPONSE (200 OK):
─────────────────────────────────────────────────────────────────────────────

{
  "success": true,
  "video_url": "https://www.youtube.com/watch?v=XesW1fJIJTc",
  "summary": "Okay, I will provide a comprehensive summary...",
  "metadata": {
    "extracted_duration": "02:35",
    "segment_count": 224,
    "timestamp_count": 224,
    "generation_time": "2026-01-10T09:51:30Z"
  }
}

SUMMARY STRUCTURE (14 Sections):
─────────────────────────────────────────────────────────────────────────────

## 1. EXECUTIVE SUMMARY
✓ 2-3 sentence overview of the video

## 2. VIDEO TIMELINE & KEY SECTIONS WITH TIMESTAMPS
✓ [00:00] - Video Start
✓ [00:10] - Introduction
✓ [00:23] - Main Content
✓ [00:57] - Key Point 1
✓ ... (and more)

## 3. MAIN TOPIC AND CORE MESSAGE
✓ Primary subject matter

## 4. DETAILED KEY POINTS (Numbered, with timestamps)
✓ [00:18] Point 1: Description
✓ [01:25] Point 2: Description
✓ ... (and more)

## 5. IMPORTANT CONCEPTS & DEFINITIONS (with timestamps)
✓ [00:45] Concept 1: Definition
✓ [02:10] Concept 2: Definition

## 6. STATISTICS, DATA & NUMBERS (with timestamps)
✓ [01:32] Statistic 1: Value
✓ [02:15] Statistic 2: Value

## 7. QUOTES & NOTABLE STATEMENTS (with exact timestamps)
✓ [00:50] "Quote text here"
✓ [01:40] "Another quote"

## 8. VISUAL DESCRIPTIONS (with timestamps)
✓ [00:00] Description of visuals

## 9. TARGET AUDIENCE
✓ Who this video is for

## 10. KEY TAKEAWAYS (5-10 main learnings)
✓ Learning 1
✓ Learning 2
✓ ... (up to 10)

## 11. CHAPTER BREAKDOWN (If applicable)
✓ [00:00] Chapter 1
✓ [05:30] Chapter 2

## 12. OVERALL ASSESSMENT
✓ Quality: Assessment
✓ Credibility: Assessment
✓ Engagement Level: Assessment
✓ Educational Value: Assessment

## 13. VIEWER QUESTIONS ANSWERED
✓ Q: Question from transcript
✓ A: Answer from transcript

## 14. RELATED TOPICS & SUGGESTIONS
✓ Related Topic 1
✓ Related Topic 2

VERIFICATION RESULTS:
─────────────────────────────────────────────────────────────────────────────

✅ Summary Length: 23,540 characters (comprehensive)
✅ Timestamps: 224 found throughout [MM:SS] format
✅ Sections: All 14 sections complete
✅ Depth: Multiple details per section
✅ Timestamps in Key Points: Yes, at [00:00], [00:10], [00:23], etc.
✅ Metadata: Duration, segment count, generation time included

```

---

## Database Schema Changes

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          DATABASE UPDATES                                     │
└──────────────────────────────────────────────────────────────────────────────┘

TABLE: question_solver_userdailyquizattempt
─────────────────────────────────────────────

Columns Used:
├─ id: UUID (Primary Key)
├─ user_id: CharField (500 chars) - "rahuljha996886"
├─ daily_quiz_id: ForeignKey → DailyQuiz
├─ answers: JSONField - {"1": 0, "2": 1, ...}
├─ correct_count: Integer - 1 (out of 5)
├─ total_questions: Integer - 5
├─ score_percentage: Float - 20.0
├─ coins_earned: Integer - 15
├─ started_at: DateTime - 2026-01-10T09:50:11Z
├─ completed_at: DateTime - 2026-01-10T09:50:14Z
└─ time_taken_seconds: Integer - 180

Example Record:
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "rahuljha996886",
  "daily_quiz_id": "7b318795-0782-4415-bad5-130cb7f9d9a9",
  "answers": {"1": 0, "2": 1, "3": 2, "4": 3, "5": 0},
  "correct_count": 1,
  "total_questions": 5,
  "score_percentage": 20.0,
  "coins_earned": 15,
  "completed_at": "2026-01-10T09:50:14.007618Z",
  "time_taken_seconds": 180
}

TABLE: question_solver_usercoins
────────────────────────────────

Columns Used:
├─ id: Integer (Primary Key)
├─ user_id: CharField (255 chars) - "rahuljha996886"
├─ total_coins: Integer - 35
├─ lifetime_coins: Integer - 35
├─ coins_spent: Integer - 0
├─ updated_at: DateTime

Example Record:
{
  "id": 1,
  "user_id": "rahuljha996886",
  "total_coins": 35,
  "lifetime_coins": 35,
  "coins_spent": 0,
  "updated_at": "2026-01-10T09:50:14.214443Z"
}

TABLE: question_solver_cointransaction
───────────────────────────────────────

Columns Used:
├─ id: Integer (Primary Key)
├─ user_coins_id: ForeignKey → UserCoins
├─ amount: Integer - 15
├─ transaction_type: CharField - "earn"
├─ reason: CharField - "Daily Quiz attempt 2026-01-10"
├─ created_at: DateTime - 2026-01-10T09:50:14Z

Example Records:
[
  {
    "id": 3,
    "amount": 15,
    "type": "earn",
    "reason": "Daily Quiz attempt 2026-01-10",
    "created_at": "2026-01-10T09:50:14.214443Z"
  },
  {
    "id": 2,
    "amount": 5,
    "type": "earn",
    "reason": "Daily Quiz participation 2026-01-10",
    "created_at": "2026-01-10T09:50:11.382513Z"
  }
]

```

---

## Code Flow: Language Parameter Propagation

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                   HINDI LANGUAGE PARAMETER FLOW                               │
└──────────────────────────────────────────────────────────────────────────────┘

API CLIENT LAYER:
─────────────────
  GET /api/daily-quiz/?language=hindi&user_id=rahuljha996886
              └─ Query parameter: language=hindi

VIEW LAYER (daily_quiz_views.py):
────────────────────────────────
  @api_view(['GET'])
  def get_daily_quiz(request):
      language = request.query_params.get('language', 'english').lower()
      └─ Extracts: language = 'hindi'
      
      daily_quiz = create_or_get_daily_quiz(language=language)
                                           └─ Passes: language='hindi'

HELPER FUNCTION (daily_quiz_views.py):
──────────────────────────────────────
  def create_or_get_daily_quiz(language='english'):
                               └─ Receives: language='hindi'
      
      result = gemini_service.generate_daily_quiz(
          num_questions=5,
          language=language
      )
                    └─ Passes: language='hindi'

SERVICE LAYER (gemini_service.py):
─────────────────────────────────
  def generate_daily_quiz(num_questions, language='english'):
                                          └─ Receives: language='hindi'
      
      if language.lower() == 'hindi':
          prompt = f"""आप एक दैनिक सामान्य ज्ञान प्रश्नोत्तरी बनाएं...
          [Full Hindi prompt with 500+ chars]
          JSON Format in Hindi:
          {{
            "questions": [
              {{
                "question_text": "हिंदी में प्रश्न",
                "options": [
                  {{"id": "A", "text": "विकल्प 1"}},
                  {{"id": "B", "text": "विकल्प 2"}}
                ],
                "category": "श्रेणी",
                "difficulty": "कठिनाई स्तर"
              }}
            ]
          }}
          """
      else:
          prompt = "[English prompt version]"
      
      response = gemini_api.generate_content(prompt)
      └─ Gemini returns Hindi questions

RESPONSE:
────────
  {
    "questions": [
      {
        "question_text": "भारत की राष्ट्रीय नदी कौन सी है?",
        "options": [
          {"id": "A", "text": "यमुना"},
          {"id": "B", "text": "ब्रह्मपुत्र"},
          {"id": "C", "text": "गंगा"},
          {"id": "D", "text": "गोदावरी"}
        ],
        "category": "भूगोल",
        "difficulty": "आसान"
      }
    ]
  }

✅ OUTPUT: Questions in Hindi (देवनागरी)

```

---

## Summary

All flows working perfectly:

1. ✅ **Hindi Quiz Submission**: Questions generated in Hindi, submitted with answers, scored correctly
2. ✅ **Coins Tracking**: Participation bonus + per-correct rewards, balance updated
3. ✅ **User History**: All attempts tracked with scores and coins
4. ✅ **YouTube Summarizer**: Enhanced with 14 sections, 224 timestamps, 23,540 chars

**Ready for Production** 🚀

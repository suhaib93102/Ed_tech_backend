# Comprehensive Test Guide: All Features, Password Reset, YouTube Summarizer

## Overview

This guide provides step-by-step instructions to test all features of your EdTech platform with:
- ✅ All 10 features (Quiz, Mock Test, Flashcards, Pair Quiz, etc.)
- ✅ Forget Password functionality
- ✅ YouTube Summarizer
- ✅ Usage endpoint verification
- ✅ Subscription plan upgrades (FREE → BASIC → PREMIUM)
- ✅ Admin dashboard
- ✅ Complete response logging in `response.json`

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup Instructions](#setup-instructions)
3. [Running the Tests](#running-the-tests)
4. [Understanding the Results](#understanding-the-results)
5. [API Endpoints Reference](#api-endpoints-reference)
6. [Feature Details](#feature-details)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- macOS, Linux, or Windows (WSL)
- `curl` command-line tool (pre-installed on most systems)
- `jq` (optional, for JSON parsing)
- Running backend server

### Backend Requirements
- Django 5.0.0+ running on http://localhost:8000
- Database initialized (SQLite)
- All migrations applied
- Subscription plans initialized
- JWT authentication enabled

### Verification Commands
```bash
# Check if backend is running
curl http://localhost:8000/api/status/

# Check Django version
python manage.py --version

# Check database migrations
python manage.py showmigrations

# Check subscription plans
python manage.py shell
>>> from question_solver.models import SubscriptionPlan
>>> SubscriptionPlan.objects.all()
```

---

## Setup Instructions

### Step 1: Start the Backend Server

```bash
# Navigate to backend directory
cd /Users/vishaljha/Desktop/Government-welfare-Schemes/backend

# Run migrations (if not already done)
python manage.py migrate

# Initialize subscription plans
python manage.py shell
>>> from question_solver.models import SubscriptionPlan
>>> SubscriptionPlan.initialize_default_plans()
>>> exit()

# Start Django development server
python manage.py runserver
```

**Expected Output:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### Step 2: Prepare Test Script

```bash
# Navigate to backend directory
cd /Users/vishaljha/Desktop/Government-welfare-Schemes/backend

# Make test script executable
chmod +x test_all_features_curl.sh

# Verify script is ready
ls -la test_all_features_curl.sh
```

### Step 3: Ensure Database is Ready

```bash
# Check if database exists
ls -la db.sqlite3

# If needed, reset database
python manage.py flush
python manage.py migrate

# Create superuser for admin access (optional)
python manage.py createsuperuser
```

---

## Running the Tests

### Method 1: Run Complete Test Suite

```bash
# Run the full comprehensive test
./test_all_features_curl.sh

# The script will:
# 1. Create test user
# 2. Test all 10 features
# 3. Test password reset
# 4. Test YouTube summarizer
# 5. Check usage endpoints
# 6. Test subscription upgrades
# 7. Test admin dashboard
# 8. Save all responses to response.json
```

**Expected Runtime:** 2-3 minutes

### Method 2: Run Individual Tests via curl

#### Test 1: User Registration
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPassword123!",
    "username": "testuser",
    "name": "Test User"
  }'
```

**Expected Response:**
```json
{
  "user_id": 1,
  "email": "testuser@example.com",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Test 2: Quiz Feature
```bash
JWT_TOKEN="your_token_here"

curl -X POST http://localhost:8000/api/features/quiz/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "subject": "Math",
    "difficulty": "medium"
  }'
```

#### Test 3: Check Feature Usage
```bash
curl -X POST http://localhost:8000/api/usage/check/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{"feature": "quiz"}'
```

**Expected Response:**
```json
{
  "feature": "quiz",
  "current_usage": 1,
  "limit": 3,
  "remaining": 2,
  "allowed": true,
  "plan": "FREE"
}
```

#### Test 4: Forget Password - Request Reset
```bash
curl -X POST http://localhost:8000/api/auth/request-password-reset/ \
  -H "Content-Type: application/json" \
  -d '{"email": "testuser@example.com"}'
```

**Expected Response:**
```json
{
  "message": "Password reset link sent to your email",
  "token": "reset_token_here"
}
```

#### Test 5: Forget Password - Verify Token
```bash
RESET_TOKEN="token_from_email"

curl -X POST http://localhost:8000/api/auth/verify-reset-token/ \
  -H "Content-Type: application/json" \
  -d '{"token": "'$RESET_TOKEN'"}'
```

**Expected Response:**
```json
{
  "valid": true,
  "message": "Token is valid"
}
```

#### Test 6: Forget Password - Reset Password
```bash
curl -X POST http://localhost:8000/api/auth/reset-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "'$RESET_TOKEN'",
    "new_password": "NewPassword123!"
  }'
```

**Expected Response:**
```json
{
  "message": "Password has been reset successfully",
  "email": "testuser@example.com"
}
```

#### Test 7: YouTube Summarizer
```bash
curl -X POST http://localhost:8000/api/youtube/summarize/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  }'
```

**Expected Response:**
```json
{
  "title": "Video Title",
  "summary": "Video summary...",
  "duration": 212,
  "keywords": ["keyword1", "keyword2"],
  "transcript": "..."
}
```

#### Test 8: Check Usage Dashboard
```bash
curl -X GET http://localhost:8000/api/usage/dashboard/ \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Expected Response:**
```json
{
  "current_plan": "FREE",
  "features": {
    "quiz": {"usage": 1, "limit": 3, "remaining": 2},
    "mock_test": {"usage": 0, "limit": 3, "remaining": 3},
    ...
  },
  "total_features": 10,
  "billing_info": {...}
}
```

#### Test 9: Upgrade Subscription
```bash
# Upgrade to BASIC (plan_id: 2)
curl -X POST http://localhost:8000/api/subscriptions/upgrade/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{"plan_id": 2}'
```

**Expected Response:**
```json
{
  "message": "Subscription upgraded successfully",
  "plan": "BASIC",
  "amount": 1,
  "currency": "INR",
  "renewal_date": "2026-02-06"
}
```

#### Test 10: Admin Dashboard
```bash
# Get all users (requires admin token)
curl -X GET http://localhost:8000/api/admin/users/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## Understanding the Results

### Response File Structure (`response.json`)

```json
{
  "test_metadata": {
    "timestamp": "2026-01-06T10:30:00Z",
    "api_url": "http://localhost:8000",
    "test_user_email": "testuser_20260106_103000@example.com",
    "test_user_id": 1
  },
  "test_summary": {
    "total_tests": 35,
    "tests_passed": 35,
    "tests_failed": 0,
    "success_rate": "100%"
  },
  "authentication": {
    "user_registration": {...},
    "password_reset": {...}
  },
  "features": {
    "description": "All 10 features tested",
    "features_list": [
      "quiz",
      "mock_test",
      "flashcards",
      "pair_quiz",
      "predicted_questions",
      "ask_question",
      "youtube_summarizer",
      "pyqs",
      "previous_papers",
      "daily_quiz"
    ]
  },
  "usage_endpoints": {...},
  "youtube_summarizer": {...},
  "subscription_plans": {...},
  "admin_dashboard": {...}
}
```

### Key Metrics to Check

1. **Test Summary**
   - Success Rate should be 100% or close to it
   - Tests Passed should equal or exceed Tests Failed

2. **Authentication**
   - JWT Token should be generated
   - User ID should be assigned
   - Password reset flow should complete

3. **Features**
   - All 10 features should be tested
   - Feature usage should increment

4. **Subscription Plans**
   - Initial plan should be "FREE"
   - Limits should increase on upgrade to BASIC
   - All limits should be unlimited on PREMIUM

5. **Usage Endpoints**
   - Dashboard should show all features with limits
   - Feature usage should be accurate
   - Stats should match dashboard data

---

## API Endpoints Reference

### Authentication Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login user |
| POST | `/api/auth/logout/` | Logout user |
| POST | `/api/auth/request-password-reset/` | Request password reset |
| POST | `/api/auth/verify-reset-token/` | Verify reset token |
| POST | `/api/auth/reset-password/` | Reset password with token |

### Feature Endpoints (All require JWT)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/features/quiz/` | Quiz feature |
| POST | `/api/features/mock_test/` | Mock test feature |
| POST | `/api/features/flashcards/` | Flashcards feature |
| POST | `/api/features/pair_quiz/` | Pair quiz feature |
| POST | `/api/features/predicted_questions/` | Predicted questions |
| POST | `/api/features/ask_question/` | Ask question feature |
| POST | `/api/features/youtube_summarizer/` | YouTube summarizer |
| POST | `/api/features/pyqs/` | Previous year questions |
| POST | `/api/features/previous_papers/` | Previous papers |
| POST | `/api/features/daily_quiz/` | Daily quiz |

### Usage Endpoints (All require JWT)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/usage/dashboard/` | Get usage dashboard |
| GET | `/api/usage/feature/<feature_name>/` | Get specific feature usage |
| POST | `/api/usage/check/` | Check if feature available |
| POST | `/api/usage/record/` | Record feature usage |
| GET | `/api/usage/stats/` | Get usage statistics |
| GET | `/api/usage/subscription/` | Get current subscription |

### Subscription Endpoints (All require JWT)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/subscriptions/plans/` | Get all plans |
| POST | `/api/subscriptions/upgrade/` | Upgrade plan |
| GET | `/api/subscriptions/current/` | Get current subscription |
| POST | `/api/subscriptions/cancel/` | Cancel subscription |

### YouTube Endpoints (Requires JWT)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/youtube/summarize/` | Summarize YouTube video |
| POST | `/api/youtube/get-transcript/` | Get video transcript |
| POST | `/api/youtube/search/` | Search YouTube |

### Admin Endpoints (Requires Admin Token)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/users/` | Get all users |
| GET | `/api/admin/subscriptions/` | Get all subscriptions |
| GET | `/api/admin/usage-logs/` | Get all usage logs |
| GET | `/api/admin/revenue/` | Get revenue stats |

---

## Feature Details

### Feature 1: Quiz (Q&A)
- **Description:** Answer multiple-choice questions
- **Request:**
```json
{
  "subject": "Math",
  "difficulty": "medium"
}
```
- **Limits:** FREE: 3, BASIC: 20, PREMIUM: ∞
- **Use Case:** Daily practice, learning

### Feature 2: Mock Test
- **Description:** Full-length practice exams
- **Request:**
```json
{
  "exam_type": "JEE",
  "duration": 180
}
```
- **Limits:** FREE: 3, BASIC: 10, PREMIUM: ∞
- **Use Case:** Full exam simulation

### Feature 3: Flashcards
- **Description:** Study using flashcard sets
- **Request:**
```json
{
  "topic": "Algebra",
  "count": 10
}
```
- **Limits:** FREE: 3, BASIC: 50, PREMIUM: ∞
- **Use Case:** Quick revision

### Feature 4: Pair Quiz (Multiplayer)
- **Description:** Real-time quiz with other users
- **Request:**
```json
{
  "opponent_id": 2,
  "question_count": 5
}
```
- **Limits:** FREE: 0, BASIC: 0, PREMIUM: ∞
- **Use Case:** Competitive learning

### Feature 5: Predicted Questions
- **Description:** Questions predicted to come in exams
- **Request:**
```json
{
  "exam": "JEE_MAIN",
  "topic": "Thermodynamics"
}
```
- **Limits:** FREE: 3, BASIC: 10, PREMIUM: ∞
- **Use Case:** Exam preparation

### Feature 6: Ask Question
- **Description:** Ask experts for help
- **Request:**
```json
{
  "question": "How to solve this problem?",
  "subject": "Math"
}
```
- **Limits:** FREE: 3, BASIC: 15, PREMIUM: ∞
- **Use Case:** Personalized help

### Feature 7: YouTube Summarizer
- **Description:** Summarize YouTube educational videos
- **Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```
- **Limits:** FREE: 3, BASIC: 8, PREMIUM: ∞
- **Use Case:** Quick learning from videos

### Feature 8: PYQs (Previous Year Questions)
- **Description:** Previous years' exam questions
- **Request:**
```json
{
  "exam": "JEE",
  "year": 2023
}
```
- **Limits:** FREE: 3, BASIC: 30, PREMIUM: ∞
- **Use Case:** Exam pattern understanding

### Feature 9: Previous Papers
- **Description:** Full previous year papers
- **Request:**
```json
{
  "exam": "NEET",
  "year": 2022
}
```
- **Limits:** FREE: 0, BASIC: 0, PREMIUM: ∞
- **Use Case:** Complete exam practice

### Feature 10: Daily Quiz
- **Description:** Daily questions for continuous learning
- **Request:**
```json
{
  "category": "General Knowledge"
}
```
- **Limits:** FREE: 0, BASIC: 0, PREMIUM: ∞
- **Use Case:** Daily practice routine

---

## Troubleshooting

### Issue: Backend not responding
```bash
# Check if Django is running
ps aux | grep "python manage.py runserver"

# If not running, start it
python manage.py runserver

# Check port 8000 is listening
lsof -i :8000
```

### Issue: JWT token invalid
```bash
# Verify token format starts with "eyJ"
echo $JWT_TOKEN

# Check token hasn't expired
# If expired, register new user to get new token

# Ensure header is correct: "Authorization: Bearer TOKEN"
```

### Issue: Feature endpoint returns 404
```bash
# Check all URLs are registered
python manage.py show_urls | grep api

# Check feature endpoints are in urls.py
grep -r "api/features" question_solver/

# Restart Django if changes made
```

### Issue: YouTube Summarizer fails
```bash
# Check YouTube API key is configured
python manage.py shell
>>> from django.conf import settings
>>> print(settings.YOUTUBE_API_KEY)

# Check URL is valid YouTube URL
# Format: https://www.youtube.com/watch?v=VIDEO_ID

# Check internet connection
curl https://www.youtube.com/
```

### Issue: Database error
```bash
# Check SQLite file exists
ls -la db.sqlite3

# Check migrations are applied
python manage.py showmigrations

# If needed, reset and re-migrate
python manage.py flush
python manage.py migrate
```

### Issue: Permission denied on test script
```bash
# Make script executable
chmod +x test_all_features_curl.sh

# Run again
./test_all_features_curl.sh
```

### Issue: response.json is empty or incomplete
```bash
# Check if curl is installed
which curl

# Check API is responding
curl http://localhost:8000/

# Check logs for errors
cat test_log_*.txt | tail -50

# Run script with verbose output
bash -x test_all_features_curl.sh
```

---

## Success Criteria

Your test is successful when:

✅ **Authentication**
- User registration works
- JWT token is generated
- Password reset flow completes

✅ **Features**
- All 10 features are tested
- Each feature returns valid response
- Usage is tracked for each feature

✅ **Forget Password**
- Reset token is generated
- Token can be verified
- Password can be reset with token

✅ **YouTube Summarizer**
- Valid YouTube URLs are summarized
- Invalid URLs return error
- Usage is tracked

✅ **Usage Tracking**
- Dashboard shows all features
- Limits are enforced
- Usage increments correctly

✅ **Subscriptions**
- Initial plan is FREE
- Can upgrade to BASIC
- Can upgrade to PREMIUM
- Limits change on upgrade

✅ **Response File**
- response.json contains all responses
- All endpoints documented
- Instructions included

---

## Next Steps

1. ✅ Run the comprehensive test script
2. ✅ Review response.json for all results
3. ✅ Verify all features are working
4. ✅ Check subscription plan limits
5. ✅ Test admin dashboard
6. ✅ Deploy to production when ready
7. ✅ Monitor usage and revenue

---

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review test logs in `test_log_*.txt`
3. Check Django server logs
4. Verify database is initialized
5. Ensure all migrations are applied
6. Check API endpoints are implemented

---

**Last Updated:** January 6, 2026  
**Version:** 1.0  
**Status:** Complete and Ready for Testing

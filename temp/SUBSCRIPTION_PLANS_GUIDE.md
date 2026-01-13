# Subscription Plans & Usage Tracking System - Complete Documentation

## Overview

This system implements three subscription plans with feature usage limits, payment integration, and automatic monthly resets.

### Three Subscription Plans:

#### 1. **FREE Plan** (Default - No Payment Required)
- **Cost**: ₹0 (Forever free)
- **Feature Limits**: 3 uses per feature per month
- **Included Features**:
  - Mock Test: 3/month
  - Quiz: 3/month
  - Flashcards: 3/month
  - Ask Question: 3/month
  - Predicted Questions: 3/month
  - YouTube Summarizer: 3/month
  - Previous Year Questions (PYQ): 3/month
- **Excluded Features**: Pair Quiz, Previous Papers, Daily Quiz
- **Best For**: Students trying the platform, casual learners

#### 2. **BASIC Plan** (Affordable Option)
- **Cost**: ₹1 for first month, then ₹99/month
- **Billing**: Automatic monthly debit (can cancel anytime)
- **Feature Limits** (per month):
  - Mock Test: 10 uses
  - Quiz: 20 uses
  - Flashcards: 50 uses
  - Ask Question: 15 uses
  - Predicted Questions: 10 uses
  - YouTube Summarizer: 8 uses
  - Previous Year Questions: 30 uses
- **Excluded Features**: Pair Quiz, Previous Papers, Daily Quiz
- **Best For**: Regular students wanting more features

#### 3. **PREMIUM Plan** (Full Access)
- **Cost**: ₹199 for first month, then ₹499/month
- **Billing**: Automatic monthly debit (can cancel anytime)
- **All Features**: **UNLIMITED** uses per month
- **Included**:
  - All 7 featured tools with unlimited uses
  - Priority support
  - Advanced analytics
  - Early access to new features
- **Best For**: Serious students, exam preparation, competitive exams

---

## API Endpoints

### 1. Get Available Subscription Plans
```bash
GET /api/subscriptions/plans/

# Response:
{
  "plans": [
    {
      "name": "free",
      "display_name": "FREE Plan",
      "first_month_price": 0,
      "recurring_price": 0,
      "features": { ... },
      "description": "Free forever · Limited features · 3 uses per feature per month"
    },
    {
      "name": "basic",
      "display_month_price": 1,
      "recurring_price": 99,
      ...
    },
    {
      "name": "premium",
      "first_month_price": 199,
      "recurring_price": 499,
      ...
    }
  ]
}
```

### 2. Get User's Usage Dashboard
Shows current usage of all features with limits and remaining quota.

```bash
GET /api/usage/dashboard/
Authorization: Bearer {user_token}

# Response:
{
  "success": true,
  "dashboard": {
    "user_id": "user123",
    "plan": "BASIC",
    "subscription_id": "sub_abc123",
    "features": {
      "quiz": {
        "display_name": "Quiz",
        "limit": 20,
        "used": 5,
        "remaining": 15,
        "unlimited": false,
        "percentage_used": 25
      },
      "mock_test": {
        "limit": 10,
        "used": 3,
        "remaining": 7,
        "unlimited": false,
        "percentage_used": 30
      },
      ...
    },
    "billing": {
      "first_month_price": 1,
      "recurring_price": 99,
      "is_trial": true,
      "trial_end_date": "2026-02-06T...",
      "subscription_start_date": "2026-01-06T...",
      "next_billing_date": "2026-02-06T...",
      "subscription_status": "active"
    }
  }
}
```

### 3. Check if Feature is Available
Before using a feature, check if user has remaining quota.

```bash
POST /api/usage/check/
Authorization: Bearer {user_token}
Content-Type: application/json

{
  "feature": "quiz"
}

# Response:
{
  "success": true,
  "feature": "quiz",
  "status": {
    "allowed": true,
    "reason": "Within limit (5/20)",
    "limit": 20,
    "used": 5,
    "remaining": 15
  }
}

# If limit exceeded:
{
  "success": false,
  "error": "Monthly limit reached (20/20 used)",
  "status": {
    "allowed": false,
    "reason": "Monthly limit reached (20/20 used)",
    "limit": 20,
    "used": 20
  }
}
```

### 4. Record Feature Usage
Call this after user successfully uses a feature. Increments the usage counter.

```bash
POST /api/usage/record/
Authorization: Bearer {user_token}
Content-Type: application/json

{
  "feature": "quiz",
  "input_size": 1500,
  "usage_type": "text"
}

# Response:
{
  "success": true,
  "message": "Feature 'quiz' usage recorded",
  "usage": {
    "feature": "quiz",
    "limit": 20,
    "used": 6,
    "remaining": 14
  }
}
```

### 5. Get Specific Feature Status
Get detailed information about a single feature's usage.

```bash
GET /api/usage/feature/{feature_name}/
Authorization: Bearer {user_token}

# Example:
GET /api/usage/feature/quiz/

# Response:
{
  "success": true,
  "feature": "quiz",
  "status": {
    "allowed": true,
    "reason": "Within limit (6/20)",
    "limit": 20,
    "used": 6,
    "remaining": 14
  }
}
```

### 6. Get Subscription Status
Get current subscription information.

```bash
GET /api/usage/subscription/
Authorization: Bearer {user_token}

# Response:
{
  "success": true,
  "subscription": {
    "id": "sub_abc123",
    "plan": "BASIC",
    "is_active": true,
    "status": "active",
    "is_trial": true,
    "trial_end_date": "2026-02-06T...",
    "subscription_start_date": "2026-01-06T...",
    "next_billing_date": "2026-02-06T...",
    "last_payment_date": "2026-01-06T..."
  }
}
```

### 7. Get Usage Statistics
Get overall usage trends and statistics.

```bash
GET /api/usage/stats/
Authorization: Bearer {user_token}

# Response:
{
  "success": true,
  "stats": {
    "total_limit": 150,      // Sum of all feature limits
    "total_used": 28,        // Total uses across all features
    "total_logs": 28,        // Total log entries
    "latest_usage": "2026-01-06T14:30:00+00:00",
    "plan": "basic"
  }
}
```

### 8. Create Subscription (Upgrade Plan)
Start a new subscription to a paid plan. This creates a Razorpay order for payment.

```bash
POST /api/subscriptions/create/
Content-Type: application/json

{
  "user_id": "user123",
  "plan": "basic"  // or "premium"
}

# Response:
{
  "success": true,
  "subscription_id": "sub_123abc",
  "payment_url": "https://rzp.io/l/short_url",
  "razorpay_key": "rzp_live_XXXXX",
  "first_payment": "₹1",
  "recurring_payment": "₹99",
  "message": "BASIC subscription created. First month only ₹1"
}
```

### 9. Verify Payment
Called after user completes payment on Razorpay. Updates subscription status and unlocks features.

```bash
POST /api/subscriptions/verify-payment/
Content-Type: application/json

{
  "razorpay_payment_id": "pay_123abc",
  "razorpay_order_id": "order_123abc",
  "razorpay_signature": "signature_hash"
}

# Response:
{
  "success": true,
  "message": "Payment verified successfully",
  "subscription": {
    "id": "sub_123abc",
    "plan": "basic",
    "status": "active"
  },
  "message": "Features unlocked! Your BASIC plan is now active."
}
```

### 10. Get Subscription Info
Get subscription details including billing dates and status.

```bash
GET /api/subscriptions/status/
Authorization: Bearer {user_token}

# Response:
{
  "success": true,
  "subscription": {
    "id": "sub_123abc",
    "plan": "BASIC",
    "status": "active",
    "is_trial": true,
    "trial_end_date": "2026-02-06",
    "next_payment": "₹99",
    "next_payment_date": "2026-02-06"
  }
}
```

---

## Feature Usage Workflow

### Scenario 1: Free User Trying Quiz Feature

```
1. User registers
   └─> Automatically assigned to FREE plan
       └─> 3 quiz uses per month

2. User attempts quiz
   └─> Check: GET /api/usage/check/ {"feature": "quiz"}
       └─> Response: allowed=true, used=0/3

3. User completes quiz
   └─> Record: POST /api/usage/record/ {"feature": "quiz"}
       └─> Usage updated: 1/3

4. User completes 2 more quizzes
   └─> Usage updated: 3/3 (limit reached)

5. User tries 4th quiz
   └─> Check: GET /api/usage/check/ {"feature": "quiz"}
       └─> Response: allowed=false, error="Monthly limit reached (3/3 used)"
       └─> User must upgrade to continue

6. User upgrades to BASIC plan
   └─> POST /api/subscriptions/create/ {"plan": "basic"}
       └─> Razorpay payment initiated (₹1)

7. User completes payment
   └─> POST /api/subscriptions/verify-payment/
       └─> Subscription activated
       └─> Features unlocked: 20 quiz uses per month
       └─> Usage counter reset: 0/20

8. User can now use quiz features
   └─> Usage updates from 0 to whatever they use
```

### Scenario 2: Billing & Monthly Reset

```
User on BASIC plan (₹1 first month, then ₹99)

Day 1: Subscription starts
└─> next_billing_date = Day 31

Day 10: User uses features
└─> Usage: quiz 5/20, mock_test 3/10, etc.

Day 31 (Billing date):
├─> Automatic payment of ₹99 collected
├─> Trial flag changed: is_trial = false
├─> next_billing_date = Day 61
└─> Monthly usage counters RESET (automatically)
    └─> quiz: 5 → 0
    └─> mock_test: 3 → 0
    └─> etc.

Day 32: User sees fresh quota
└─> Dashboard shows: 0/20 quiz uses, 0/10 mock_test, etc.
```

### Scenario 3: Premium Unlimited

```
User upgrades to PREMIUM (₹199 first month, ₹499 after)

1. POST /api/subscriptions/create/ {"plan": "premium"}
   └─> Razorpay order for ₹199

2. User completes payment
   └─> POST /api/subscriptions/verify-payment/
       └─> Subscription activated

3. Features unlocked
   └─> All limits set to NULL (unlimited)
   └─> Dashboard shows:
       {
         "quiz": {"limit": null, "unlimited": true, "used": X},
         "mock_test": {"limit": null, "unlimited": true, "used": X},
         ...
       }

4. User can use features infinitely
   └─> No limit enforcement
   └─> Still logs usage for analytics
```

---

## Integration with Feature Endpoints

When a feature endpoint (quiz, ask_question, etc.) is called:

### Best Practice Flow:

```python
# 1. In your feature endpoint, before processing:
status = FeatureUsageService.check_feature_available(user_id, "quiz")
if not status['allowed']:
    return JsonResponse({
        'success': False,
        'error': status['reason'],  # "Monthly limit reached (20/20)"
    }, status=403)

# 2. Process the feature (generate quiz, etc.)
quiz = generate_quiz(params)

# 3. After successful completion, record usage:
FeatureUsageService.use_feature(
    user_id=user_id,
    feature_name="quiz",
    input_size=len(quiz_data),
    usage_type="text"
)

# 4. Return response with usage info:
return JsonResponse({
    'success': True,
    'data': quiz,
    'usage': {
        'feature': 'quiz',
        'used': 6,
        'limit': 20,
        'remaining': 14,
    }
})
```

---

## Testing with curl

### 1. Register User
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "Password123!"}'
```

### 2. Get Plans
```bash
curl -X GET http://localhost:8000/api/subscriptions/plans/
```

### 3. Check Usage Dashboard
```bash
curl -X GET http://localhost:8000/api/usage/dashboard/ \
  -H "Authorization: Bearer USER_TOKEN"
```

### 4. Check Feature Availability
```bash
curl -X POST http://localhost:8000/api/usage/check/ \
  -H "Authorization: Bearer USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"feature": "quiz"}'
```

### 5. Record Feature Usage
```bash
curl -X POST http://localhost:8000/api/usage/record/ \
  -H "Authorization: Bearer USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"feature": "quiz", "input_size": 1000, "usage_type": "text"}'
```

### 6. Upgrade to BASIC Plan
```bash
curl -X POST http://localhost:8000/api/subscriptions/create/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER_ID", "plan": "basic"}'
```

### 7. Upgrade to PREMIUM Plan
```bash
curl -X POST http://localhost:8000/api/subscriptions/create/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER_ID", "plan": "premium"}'
```

### 8. Get Subscription Status
```bash
curl -X GET http://localhost:8000/api/usage/subscription/ \
  -H "Authorization: Bearer USER_TOKEN"
```

### 9. Get Usage Statistics
```bash
curl -X GET http://localhost:8000/api/usage/stats/ \
  -H "Authorization: Bearer USER_TOKEN"
```

### 10. Run Complete Test Suite
```bash
bash test_subscription_plans.sh
```

---

## Database Tables

### SubscriptionPlan (Plans Configuration)
- `id` (UUID): Primary key
- `name`: free, basic, premium
- `display_name`: User-friendly name
- `first_month_price`: ₹0, ₹1, ₹199
- `recurring_price`: ₹0, ₹99, ₹499
- `mock_test_limit`: 3, 10, null
- `quiz_limit`: 3, 20, null
- `flashcards_limit`: 3, 50, null
- ... (8 more features)

### UserSubscription (User's Subscription)
- `id` (UUID): Primary key
- `user_id`: Unique user identifier
- `plan`: free, basic, premium
- `subscription_plan`: FK to SubscriptionPlan
- `mock_test_used`: Usage counter (0-limit)
- `quiz_used`: Usage counter (0-limit)
- ... (8 more feature counters)
- `is_trial`: Boolean
- `trial_end_date`: First month ends
- `next_billing_date`: When to charge next
- `subscription_status`: active, cancelled, paused
- `subscription_start_date`: When subscription started
- `usage_reset_date`: When monthly reset happened

### FeatureUsageLog (Audit Trail)
- `id` (UUID): Primary key
- `subscription`: FK to UserSubscription
- `feature_name`: quiz, mock_test, etc.
- `usage_type`: text, file, image
- `input_size`: Size of request
- `created_at`: Timestamp

### Payment (Billing Records)
- `id` (UUID): Primary key
- `subscription`: FK to UserSubscription
- `amount`: ₹1, ₹99, ₹199, ₹499
- `status`: pending, completed, failed, refunded
- `razorpay_payment_id`: For tracking
- `razorpay_order_id`: For tracking
- `razorpay_signature`: For verification
- `billing_cycle_start/end`: Dates
- `created_at`: When payment was made

---

## Key Features

✅ **Three Plans**: FREE (3 uses), BASIC (10-50 uses), PREMIUM (unlimited)  
✅ **Automatic Limits**: Features restricted based on plan  
✅ **Usage Dashboard**: See quota and remaining uses  
✅ **Payment Integration**: ₹1 trial for first month  
✅ **Auto-Billing**: Monthly recurring on Razorpay  
✅ **Monthly Reset**: Counters reset automatically  
✅ **Trial Period**: 30-day trial before recurring charge  
✅ **Cancelable**: Users can cancel anytime  
✅ **Audit Trail**: All usage logged for analytics  
✅ **Status Tracking**: See subscription and payment status  

---

## Error Handling

### Limit Exceeded Response
```json
{
  "success": false,
  "error": "Monthly limit reached (20/20 used)",
  "feature": "quiz",
  "status": {
    "allowed": false,
    "limit": 20,
    "used": 20
  }
}
```

### Invalid Feature Response
```json
{
  "success": false,
  "error": "Feature 'invalid_feature' not found",
  "status": {
    "allowed": false,
    "reason": "Feature not found"
  }
}
```

### Subscription Not Active
```json
{
  "success": false,
  "error": "Subscription not active",
  "subscription_status": "cancelled"
}
```

---

## Troubleshooting

**Q: User still sees FREE plan limits after upgrading**  
A: Run monthly reset or check if payment verification was successful

**Q: Usage counter not updating**  
A: Make sure to call POST /api/usage/record/ after feature usage

**Q: Can't verify payment**  
A: Check Razorpay signature and ensure payment_id/order_id match

**Q: Monthly reset not happening**  
A: Use management command or call reset endpoint manually

---

## Next Steps

1. ✅ Three plans configured with limits
2. ✅ Usage tracking endpoints created
3. ✅ Payment integration ready
4. 🔄 **Production**: Run migrations and deploy
5. 🔄 **Frontend**: Integrate dashboard UI
6. 🔄 **Monitoring**: Track subscription metrics

---

## Files Modified

1. **question_solver/models.py**
   - Updated SubscriptionPlan model with 3 plans
   - Updated UserSubscription with all 10 features
   - Updated Payment and FeatureUsageLog models

2. **question_solver/feature_usage_service.py** (NEW)
   - Service to check and track feature usage
   - Methods for checking limits, recording usage, resetting counters

3. **question_solver/usage_api_views.py** (NEW)
   - 6 API endpoints for usage tracking and dashboard
   - Feature availability checking
   - Subscription status

4. **question_solver/urls.py**
   - Added 6 new usage API endpoint routes

5. **test_subscription_plans.sh** (NEW)
   - Comprehensive curl test script for all plans
   - Tests upgrade flow, payment, and feature restrictions

---

## Support & Documentation

For more details, see:
- `SUBSCRIPTION_USAGE_GUIDE.md` - User-facing guide
- `test_subscription_plans.sh` - Test cases
- API documentation in each view function

# Complete Usage Flow, Endpoints & Subscription Lifecycle

## Executive Summary

This document defines the complete flow for feature usage tracking, endpoint interactions, database storage, subscription management, and automatic monthly renewal. This ensures users have proper quota tracking with real-time updates, restrictions are enforced per plan, and subscriptions automatically renew monthly.

---

## Table of Contents

1. [User Feature Usage Flow](#user-feature-usage-flow)
2. [Endpoint Usage & Interactions](#endpoint-usage--interactions)
3. [Database Storage & Schema](#database-storage--schema)
4. [Subscription Lifecycle](#subscription-lifecycle)
5. [Real-Time Quota Tracking](#real-time-quota-tracking)
6. [Restriction Enforcement](#restriction-enforcement)
7. [Monthly Renewal Process](#monthly-renewal-process)
8. [Implementation Requirements](#implementation-requirements)

---

## User Feature Usage Flow

### **Phase 1: User Initiates Feature (Before Using)**

```
┌─────────────────────────────────────────────────────────────┐
│ USER WANTS TO USE A FEATURE (e.g., Create Quiz)             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND: Check Feature Availability                         │
│ POST /api/usage/check/                                       │
│ {                                                             │
│   "feature": "quiz",                                         │
│   "input_size": 5000                                         │
│ }                                                             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ BACKEND: Check User's Subscription & Quota                  │
│ 1. Get UserSubscription for user_id                         │
│ 2. Get feature limits based on subscription_status          │
│ 3. Query FeatureUsageLog to count current usage             │
│ 4. Compare: current_usage < limit ?                         │
└─────────────────────────────────────────────────────────────┘
                           ↓
                    ┌──────┴──────┐
                    ↓             ↓
           ✅ ALLOWED        ❌ RESTRICTED
           (200 OK)          (403 FORBIDDEN)
                |                 |
                ↓                 ↓
    Proceed to Phase 2    Show Upgrade Modal
                          └─→ "Plan Limit Reached"
```

### **Phase 2: User Uses Feature (During Usage)**

```
┌─────────────────────────────────────────────────────────────┐
│ FEATURE IS BEING USED BY USER                               │
│ (Quiz is being created, data processed, etc.)               │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ BACKEND: Execute Feature Logic                              │
│ - Process user input                                        │
│ - Generate quiz, analyze data, etc.                         │
│ - Store feature output in respective tables                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
                    ✅ SUCCESS / ❌ ERROR
                           ↓
                   (Only if SUCCESS → Phase 3)
```

### **Phase 3: Record Usage (After Using)**

```
┌─────────────────────────────────────────────────────────────┐
│ BACKEND: Record Usage in Database                           │
│ POST /api/usage/record/                                     │
│ {                                                             │
│   "feature": "quiz",                                        │
│   "input_size": 5000,                                       │
│   "usage_type": "text",                                     │
│   "output_data": {...}  (optional)                          │
│ }                                                             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ DATABASE OPERATIONS:                                        │
│                                                              │
│ 1. Get UserSubscription(user_id)                            │
│ 2. Create FeatureUsageLog entry:                            │
│    ├─ subscription = UserSubscription                       │
│    ├─ feature_name = "quiz"                                │
│    ├─ input_size = 5000                                    │
│    ├─ usage_type = "text"                                  │
│    ├─ created_at = NOW()                                   │
│    └─ status = "completed"                                 │
│                                                              │
│ 3. Update UserSubscription.last_usage_date = NOW()         │
│                                                              │
│ 4. Update UserSubscription.total_usage_count++             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ RESPONSE: Usage Recorded + Updated Quota Info               │
│ {                                                             │
│   "success": true,                                          │
│   "feature": "quiz",                                        │
│   "usage_recorded": true,                                   │
│   "current_quota": {                                        │
│     "used": 2,                                              │
│     "limit": 3,                                             │
│     "remaining": 1,                                         │
│     "percentage": 66.67                                     │
│   }                                                          │
│ }                                                             │
└─────────────────────────────────────────────────────────────┘
```

### **Phase 4: Display Updated Dashboard**

```
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND: Show Updated Usage Dashboard                      │
│ GET /api/usage/real-time/                                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ BACKEND: Fetch Latest Quota Status                          │
│ 1. Query all FeatureUsageLog entries for user               │
│   (Last 30 days, grouped by feature)                        │
│ 2. Calculate usage per feature                              │
│ 3. Get limits from UserSubscription.plan                    │
│ 4. Calculate remaining quotas                               │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ RESPONSE: Real-Time Usage Dashboard                         │
│ {                                                             │
│   "success": true,                                          │
│   "timestamp": "2026-01-10T15:30:00Z",                      │
│   "plan": "free",                                           │
│   "subscription_status": "active",                          │
│   "feature_usage": {                                        │
│     "quiz": {                                               │
│       "used": 2,                                            │
│       "limit": 3,                                           │
│       "remaining": 1,                                       │
│       "percentage": 66.67,                                  │
│       "allowed": true                                       │
│     },                                                       │
│     "flashcards": {                                         │
│       "used": 3,                                            │
│       "limit": 3,                                           │
│       "remaining": 0,                                       │
│       "percentage": 100,                                    │
│       "allowed": false                                      │
│     }                                                        │
│   },                                                         │
│   "summary": {                                              │
│     "total_features": 10,                                   │
│     "available": 8,                                         │
│     "exhausted": 2                                          │
│   }                                                          │
│ }                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Endpoint Usage & Interactions

### **1. Pre-Usage Validation Endpoint**

**Purpose:** Check if user can use a feature before attempting it

```http
POST /api/usage/check/
Header: X-User-ID: user123
Content-Type: application/json

Request:
{
  "feature": "quiz",
  "input_size": 5000
}

Response (200 - Feature Available):
{
  "success": true,
  "feature": "quiz",
  "allowed": true,
  "remaining": 1,
  "message": "Feature available. 1 use remaining."
}

Response (403 - Feature Quota Exhausted):
{
  "success": false,
  "feature": "quiz",
  "allowed": false,
  "reason": "Feature limit exhausted for free plan",
  "upgrade_message": "Upgrade to Premium to get unlimited uses",
  "limit": 3,
  "used": 3,
  "remaining": 0
}
```

### **2. Record Usage Endpoint**

**Purpose:** Record that user has used a feature (called after feature is completed)

```http
POST /api/usage/record/
Header: X-User-ID: user123
Content-Type: application/json

Request:
{
  "feature": "quiz",
  "input_size": 5000,
  "usage_type": "text",
  "output_data": {
    "quiz_id": "q123",
    "questions": 10,
    "duration": 30
  }
}

Response (200 - Usage Recorded):
{
  "success": true,
  "feature": "quiz",
  "usage_recorded": true,
  "current_quota": {
    "used": 2,
    "limit": 3,
    "remaining": 1,
    "percentage": 66.67
  },
  "message": "Usage recorded successfully"
}
```

### **3. Real-Time Usage Tracking Endpoint**

**Purpose:** Get current usage status for all features

```http
GET /api/usage/real-time/
Header: X-User-ID: user123

Response (200):
{
  "success": true,
  "timestamp": "2026-01-10T15:30:00Z",
  "plan": "free",
  "subscription_status": "active",
  "subscription_end_date": "2026-02-10",
  "feature_usage": {
    "quiz": {
      "name": "Quiz Generator",
      "used": 2,
      "limit": 3,
      "remaining": 1,
      "percentage": 66.67,
      "allowed": true,
      "last_used": "2026-01-10T14:20:00Z"
    },
    "flashcards": {
      "name": "Flashcard Creator",
      "used": 3,
      "limit": 3,
      "remaining": 0,
      "percentage": 100,
      "allowed": false,
      "last_used": "2026-01-09T10:15:00Z"
    },
    "pair_quiz": {
      "name": "Pair Quiz",
      "used": 0,
      "limit": 1,
      "remaining": 1,
      "percentage": 0,
      "allowed": true,
      "last_used": null
    }
  },
  "summary": {
    "total_features": 10,
    "features_available": 8,
    "features_exhausted": 2
  }
}
```

### **4. Feature Restriction Details Endpoint**

**Purpose:** Get detailed info about why a feature is restricted

```http
GET /api/usage/restriction/quiz/
Header: X-User-ID: user123

Response (200 - Feature Allowed):
{
  "success": true,
  "feature": "quiz",
  "allowed": true,
  "remaining": 1,
  "used": 2,
  "limit": 3,
  "plan": "free",
  "restriction": null,
  "message": "Feature is available for your current plan"
}

Response (200 - Feature Restricted):
{
  "success": true,
  "feature": "flashcards",
  "allowed": false,
  "remaining": 0,
  "used": 3,
  "limit": 3,
  "plan": "free",
  "restriction": {
    "reason": "Feature limit exhausted for free plan",
    "description": "You have used 3/3 flashcards allowed on the free plan",
    "unlock_option": "Upgrade to Premium Plan",
    "upgrade_benefits": [
      "Unlimited flashcards",
      "All features unlocked",
      "Priority support"
    ],
    "pricing": "$9.99/month"
  },
  "message": "Feature is restricted. Upgrade to unlock."
}
```

### **5. Usage History Endpoint**

**Purpose:** Get historical usage data

```http
GET /api/usage/history/?days=7&feature=quiz
Header: X-User-ID: user123

Response (200):
{
  "success": true,
  "filters": {
    "days": 7,
    "feature": "quiz"
  },
  "history": [
    {
      "id": 1,
      "feature": "quiz",
      "input_size": 5000,
      "usage_type": "text",
      "created_at": "2026-01-10T14:20:00Z",
      "status": "completed"
    },
    {
      "id": 2,
      "feature": "quiz",
      "input_size": 3000,
      "usage_type": "text",
      "created_at": "2026-01-09T10:15:00Z",
      "status": "completed"
    }
  ],
  "total_count": 2,
  "total_input_size": 8000
}
```

### **6. Enforce Check Endpoint (Strict Enforcement)**

**Purpose:** Strict enforcement - returns 403 if quota exceeded

```http
POST /api/usage/enforce-check/
Header: X-User-ID: user123
Content-Type: application/json

Request:
{
  "feature": "quiz"
}

Response (200 - Allowed):
{
  "success": true,
  "message": "Feature access granted",
  "feature": "quiz",
  "remaining": 1
}

Response (403 - Forbidden):
{
  "success": false,
  "error": "Feature access denied: Feature limit exhausted for free plan",
  "feature": "quiz",
  "status": {
    "allowed": false,
    "reason": "Feature limit exhausted for free plan",
    "limit": 3,
    "used": 3
  }
}
```

---

## Database Storage & Schema

### **FeatureUsageLog Model**

**Purpose:** Store every feature usage with complete details

```python
class FeatureUsageLog(models.Model):
    # Relations
    subscription = models.ForeignKey(
        UserSubscription, 
        on_delete=models.CASCADE,
        related_name='usage_logs'
    )
    
    # Feature Information
    feature_name = models.CharField(
        max_length=100,
        choices=[
            ('quiz', 'Quiz'),
            ('flashcards', 'Flashcards'),
            ('pair_quiz', 'Pair Quiz'),
            ('ask_question', 'Ask Question'),
            ('predicted_questions', 'Predicted Questions'),
            ('previous_papers', 'Previous Papers'),
            ('pyqs', 'PYQs'),
            ('youtube_summarizer', 'YouTube Summarizer'),
            ('daily_quiz', 'Daily Quiz'),
            ('mock_test', 'Mock Test'),
        ]
    )
    
    # Usage Details
    input_size = models.IntegerField(default=0)  # Size of input (characters/bytes)
    usage_type = models.CharField(
        max_length=50,
        choices=[
            ('text', 'Text'),
            ('file', 'File'),
            ('link', 'Link'),
            ('api', 'API Call'),
        ],
        default='text'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='completed'
    )
    
    # Indexing for performance
    class Meta:
        indexes = [
            models.Index(fields=['subscription', 'feature_name']),
            models.Index(fields=['created_at']),
            models.Index(fields=['subscription', 'created_at']),
        ]
```

### **UserSubscription Model (Enhanced)**

**Purpose:** Store subscription status and tracking information

```python
class UserSubscription(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free Plan'),
        ('premium', 'Premium Plan'),
        ('pro', 'Pro Plan'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('pending_renewal', 'Pending Renewal'),
    ]
    
    # User and Plan
    user_id = models.CharField(max_length=255, unique=True)
    plan = models.CharField(max_length=50, choices=PLAN_CHOICES, default='free')
    
    # Subscription Status
    subscription_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='inactive'
    )
    
    # Subscription Dates
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Renewal Information
    renewal_date = models.DateTimeField(null=True, blank=True)
    auto_renewal = models.BooleanField(default=True)
    
    # Last Activity
    last_usage_date = models.DateTimeField(null=True, blank=True)
    total_usage_count = models.IntegerField(default=0)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['subscription_status']),
            models.Index(fields=['end_date']),
            models.Index(fields=['renewal_date']),
        ]
```

### **Database Queries for Usage Tracking**

```python
# Query 1: Get total usage for a specific feature in last 30 days
def get_feature_usage_count(user_id, feature_name):
    subscription = UserSubscription.objects.get(user_id=user_id)
    start_date = now() - timedelta(days=30)
    
    count = FeatureUsageLog.objects.filter(
        subscription=subscription,
        feature_name=feature_name,
        created_at__gte=start_date,
        status='completed'
    ).count()
    
    return count

# Query 2: Get all usage logs for a user in last 7 days
def get_user_usage_history(user_id, days=7):
    subscription = UserSubscription.objects.get(user_id=user_id)
    start_date = now() - timedelta(days=days)
    
    logs = FeatureUsageLog.objects.filter(
        subscription=subscription,
        created_at__gte=start_date
    ).order_by('-created_at')
    
    return logs

# Query 3: Get usage grouped by feature
def get_usage_by_feature(user_id):
    subscription = UserSubscription.objects.get(user_id=user_id)
    start_date = now() - timedelta(days=30)
    
    usage = FeatureUsageLog.objects.filter(
        subscription=subscription,
        created_at__gte=start_date,
        status='completed'
    ).values('feature_name').annotate(
        total_uses=Count('id'),
        total_input=Sum('input_size')
    )
    
    return usage

# Query 4: Record a new usage
def record_feature_usage(user_id, feature_name, input_size, usage_type):
    subscription = UserSubscription.objects.get(user_id=user_id)
    
    log = FeatureUsageLog.objects.create(
        subscription=subscription,
        feature_name=feature_name,
        input_size=input_size,
        usage_type=usage_type,
        status='completed'
    )
    
    # Update subscription last usage date
    subscription.last_usage_date = now()
    subscription.total_usage_count += 1
    subscription.save()
    
    return log
```

---

## Subscription Lifecycle

### **1. User Signs Up (Free Plan)**

```
┌─────────────────────────────────────────────────────────────┐
│ NEW USER REGISTRATION                                        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ CREATE UserSubscription Entry                               │
│ {                                                             │
│   user_id: "new_user_123",                                  │
│   plan: "free",                                             │
│   subscription_status: "active",                            │
│   start_date: NOW(),                                        │
│   end_date: null,                                           │
│   renewal_date: null,                                       │
│   auto_renewal: false,                                      │
│   last_usage_date: null,                                    │
│   total_usage_count: 0                                      │
│ }                                                             │
└─────────────────────────────────────────────────────────────┘
                           ↓
        User can now use FEATURES with LIMITS:
        • Quiz: 3 uses
        • Flashcards: 3 uses
        • Pair Quiz: 1 use
        • Ask Question: 5 uses
        • Predicted Questions: 3 uses
        • Previous Papers: Limited
        • PYQs: Limited
        • YouTube Summarizer: 2 uses
        • Daily Quiz: Unlimited
        • Mock Test: 3 uses
```

### **2. User Purchases Subscription (Free → Premium)**

```
┌─────────────────────────────────────────────────────────────┐
│ USER INITIATES PAYMENT                                       │
│ Razorpay/Payment Gateway                                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PAYMENT VERIFICATION                                         │
│ 1. Verify payment status from Razorpay                      │
│ 2. Check if payment is successful                           │
│ 3. Get subscription plan (premium/pro)                      │
└─────────────────────────────────────────────────────────────┘
                           ↓
                    ✅ Payment Successful
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ UPDATE UserSubscription Entry                               │
│                                                              │
│ subscription.plan = "premium"                              │
│ subscription.subscription_status = "active"                │
│ subscription.start_date = NOW()                            │
│ subscription.end_date = NOW() + 30 days                    │
│ subscription.renewal_date = NOW() + 30 days                │
│ subscription.auto_renewal = true                           │
│                                                              │
│ Result:                                                      │
│ ✅ All feature restrictions REMOVED                        │
│ ✅ All features get UNLIMITED quota                        │
│ ✅ Auto-renewal enabled                                    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ UPDATE FEATURE RESTRICTIONS                                  │
│                                                              │
│ For ALL features:                                           │
│ • quiz.limit = UNLIMITED                                   │
│ • flashcards.limit = UNLIMITED                             │
│ • pair_quiz.limit = UNLIMITED                              │
│ • ask_question.limit = UNLIMITED                           │
│ • ... (all features)                                        │
│                                                              │
│ Users can now:                                              │
│ ✅ Create unlimited quizzes                                │
│ ✅ Create unlimited flashcards                             │
│ ✅ Use all features freely                                 │
│ ✅ No "upgrade" prompts shown                              │
└─────────────────────────────────────────────────────────────┘
                           ↓
        Send confirmation email with:
        • Subscription activated
        • Features unlocked
        • Renewal date (in 30 days)
        • How to manage subscription
```

### **3. Monthly Renewal (Automatic)**

```
┌─────────────────────────────────────────────────────────────┐
│ SCHEDULED TASK: Check Renewals (Every Hour)                │
│ Runs: celery beat / cron job / AWS Lambda                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ CHECK EXPIRING SUBSCRIPTIONS                                │
│ Query: UserSubscription where:                              │
│ • subscription_status = "active"                            │
│ • renewal_date <= TODAY                                     │
│ • auto_renewal = true                                       │
└─────────────────────────────────────────────────────────────┘
                           ↓
                    For each expiring subscription:
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ RENEWAL PROCESS                                              │
│                                                              │
│ 1. Check if auto_renewal is enabled                         │
│ 2. Get payment method from user's profile                   │
│ 3. Initiate automatic charge via Razorpay                  │
│ 4. Wait for payment confirmation                            │
└─────────────────────────────────────────────────────────────┘
                           ↓
                    ┌──────┴──────┐
                    ↓             ↓
           ✅ RENEWAL SUCCESS  ❌ RENEWAL FAILED
                    |             |
                    ↓             ↓
          Update subscription:  Set status to
          • end_date += 30 days  "pending_renewal"
          • renewal_date += 30 days
          • status = "active"    (Notify user to
                                  manually renew)
```

### **4. Subscription Expiration & Grace Period**

```
┌─────────────────────────────────────────────────────────────┐
│ RENEWAL FAILED or USER CANCELS                              │
│ (e.g., payment declined, insufficient funds)                │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ SET GRACE PERIOD (3 days)                                   │
│                                                              │
│ subscription.subscription_status = "expired"               │
│ subscription.end_date = NOW()                              │
│ grace_period_end = NOW() + 3 days                          │
│                                                              │
│ During grace period:                                        │
│ • User CAN still access premium features                   │
│ • Show warning: "Subscription Expired - Renew Now"         │
│ • Features will be restricted in 3 days                    │
└─────────────────────────────────────────────────────────────┘
                           ↓
        After 3 days grace period expires:
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ RESTORE FREE PLAN RESTRICTIONS                              │
│                                                              │
│ subscription.plan = "free"                                 │
│ subscription.subscription_status = "inactive"              │
│                                                              │
│ Feature limits restored:                                    │
│ • quiz: 3 uses → 0 remaining (if already used 3)           │
│ • flashcards: 3 uses → 0 remaining                         │
│ • pair_quiz: 1 use → 0 remaining                           │
│ • ... (all features reset to free limits)                  │
│                                                              │
│ User sees:                                                   │
│ ❌ All premium features now restricted                     │
│ ❌ "Upgrade to Premium" prompts show                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Real-Time Quota Tracking

### **How Real-Time Tracking Works**

```
SCENARIO: User has 2/3 quiz uses remaining

Step 1: User clicks "Create Quiz"
        ↓
        /api/usage/check/ → Returns: remaining=1, allowed=true
        
Step 2: User submits quiz parameters
        ↓
        Backend processes the request
        
Step 3: Quiz created successfully
        ↓
        /api/usage/record/ is called
        
        DATABASE UPDATE:
        • New FeatureUsageLog entry created
        • used_count: 2 → 3
        • remaining: 1 → 0
        
Step 4: Next request to /api/usage/real-time/
        ↓
        Returns: 
        {
          "quiz": {
            "used": 3,
            "limit": 3,
            "remaining": 0,
            "allowed": false ← UPDATED!
          }
        }
        
Step 5: Frontend displays:
        ❌ "Quiz limit reached. Upgrade to create more."
```

### **Real-Time Update Timing**

| Action | Endpoint | Response Time | Database Update |
|--------|----------|---------------|-----------------|
| Check availability | `/api/usage/check/` | < 50ms | No DB write |
| Record usage | `/api/usage/record/` | < 100ms | Yes - Create log |
| Get dashboard | `/api/usage/real-time/` | < 100ms | No DB write |
| Get history | `/api/usage/history/` | < 200ms | No DB write |

**Key Point:** All reads are instant because:
- Query FeatureUsageLog for count
- Compare with limits in memory
- No complex calculations needed

---

## Restriction Enforcement

### **Free Plan Feature Limits**

```python
FEATURE_LIMITS = {
    'free': {
        'quiz': 3,
        'flashcards': 3,
        'pair_quiz': 1,
        'ask_question': 5,
        'predicted_questions': 3,
        'previous_papers': 10,
        'pyqs': 10,
        'youtube_summarizer': 2,
        'daily_quiz': -1,  # -1 = unlimited
        'mock_test': 3,
    },
    'premium': {
        'quiz': -1,
        'flashcards': -1,
        'pair_quiz': -1,
        'ask_question': -1,
        'predicted_questions': -1,
        'previous_papers': -1,
        'pyqs': -1,
        'youtube_summarizer': -1,
        'daily_quiz': -1,
        'mock_test': -1,
    },
    'pro': {
        'quiz': -1,
        'flashcards': -1,
        'pair_quiz': -1,
        'ask_question': -1,
        'predicted_questions': -1,
        'previous_papers': -1,
        'pyqs': -1,
        'youtube_summarizer': -1,
        'daily_quiz': -1,
        'mock_test': -1,
    }
}
```

### **Enforcement Logic**

```python
def check_feature_access(user_id, feature_name):
    """
    Returns: (allowed: bool, remaining: int, reason: str)
    """
    subscription = UserSubscription.objects.get(user_id=user_id)
    
    # If premium/pro with active subscription → unlimited
    if (subscription.plan in ['premium', 'pro'] and 
        subscription.subscription_status == 'active'):
        return True, -1, "Unlimited access (Premium/Pro)"
    
    # For free plan → check limits
    if subscription.plan == 'free':
        limit = FEATURE_LIMITS['free'].get(feature_name, 0)
        
        if limit == -1:  # Unlimited
            return True, -1, "Unlimited access (Free plan)"
        
        # Count current usage
        current_usage = FeatureUsageLog.objects.filter(
            subscription=subscription,
            feature_name=feature_name,
            created_at__gte=now() - timedelta(days=30),
            status='completed'
        ).count()
        
        remaining = max(0, limit - current_usage)
        
        if remaining > 0:
            return True, remaining, f"{remaining} uses remaining"
        else:
            return False, 0, "Feature limit exhausted"
    
    return False, 0, "Invalid subscription status"
```

---

## Monthly Renewal Process

### **Automated Renewal System**

**Implementation Using Celery Beat (Scheduled Tasks)**

```python
# celery.py
from celery import shared_task
from celery.schedules import crontab

@shared_task
def renew_subscriptions():
    """
    Run daily at 2 AM UTC
    Checks and renews expiring subscriptions
    """
    subscriptions_to_renew = UserSubscription.objects.filter(
        subscription_status='active',
        renewal_date__lte=now(),
        auto_renewal=True
    )
    
    for sub in subscriptions_to_renew:
        attempt_subscription_renewal(sub)

def attempt_subscription_renewal(subscription):
    """
    Attempt to renew a user's subscription
    """
    try:
        # Get payment method
        payment_method = get_user_payment_method(subscription.user_id)
        
        if not payment_method:
            # No payment method on file
            mark_subscription_expired(subscription)
            notify_user_renewal_failed(subscription.user_id)
            return False
        
        # Charge the payment
        amount = get_plan_price(subscription.plan)  # e.g., 999 (in paise)
        
        charge_result = razorpay_client.charge(
            customer_id=subscription.user_id,
            amount=amount,
            currency='INR'
        )
        
        if charge_result.status == 'success':
            # Update subscription
            subscription.subscription_status = 'active'
            subscription.end_date = now() + timedelta(days=30)
            subscription.renewal_date = now() + timedelta(days=30)
            subscription.save()
            
            # Send confirmation email
            send_renewal_confirmation_email(
                subscription.user_id,
                subscription.plan,
                subscription.end_date
            )
            
            return True
        else:
            # Payment failed
            mark_subscription_pending_renewal(subscription)
            notify_user_renewal_failed(subscription.user_id)
            return False
            
    except Exception as e:
        logger.error(f"Renewal failed for {subscription.user_id}: {e}")
        mark_subscription_pending_renewal(subscription)
        return False

def mark_subscription_expired(subscription):
    """Mark subscription as expired and start grace period"""
    subscription.subscription_status = 'expired'
    subscription.plan = 'free'
    subscription.end_date = now()
    subscription.grace_period_end = now() + timedelta(days=3)
    subscription.save()

def mark_subscription_pending_renewal(subscription):
    """Mark subscription as pending renewal (payment failed)"""
    subscription.subscription_status = 'pending_renewal'
    subscription.save()
```

### **Renewal Reminder System**

```python
@shared_task
def send_renewal_reminders():
    """
    Send reminders 7 days before renewal
    """
    reminder_date = now() + timedelta(days=7)
    
    subscriptions = UserSubscription.objects.filter(
        renewal_date__date=reminder_date.date(),
        subscription_status='active',
        plan__in=['premium', 'pro']
    )
    
    for sub in subscriptions:
        send_renewal_reminder_email(
            user_id=sub.user_id,
            plan=sub.plan,
            renewal_date=sub.renewal_date
        )

@shared_task
def restore_free_plan_after_grace_period():
    """
    Restore free plan restrictions after 3-day grace period
    """
    expired_subs = UserSubscription.objects.filter(
        subscription_status='expired',
        grace_period_end__lte=now()
    )
    
    for sub in expired_subs:
        sub.plan = 'free'
        sub.subscription_status = 'inactive'
        sub.save()
        
        # Notify user
        notify_features_restricted(sub.user_id)
```

### **Renewal Configuration**

```python
# settings.py
CELERY_BEAT_SCHEDULE = {
    'renew-subscriptions-daily': {
        'task': 'tasks.renew_subscriptions',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
    'send-renewal-reminders': {
        'task': 'tasks.send_renewal_reminders',
        'schedule': crontab(hour=9, minute=0),  # 9 AM daily
    },
    'restore-free-plan': {
        'task': 'tasks.restore_free_plan_after_grace_period',
        'schedule': crontab(hour=3, minute=0),  # 3 AM daily
    },
}

# Subscription Configuration
SUBSCRIPTION_DURATION_DAYS = 30
GRACE_PERIOD_DAYS = 3
RENEWAL_REMINDER_DAYS = 7

PLAN_PRICING = {
    'premium': 999,  # ₹9.99 in paise
    'pro': 1999,     # ₹19.99 in paise
}
```

---

## Implementation Requirements

### **Required Components**

#### **1. Database Models**
- ✅ `UserSubscription` - Track subscription status, dates, renewal info
- ✅ `FeatureUsageLog` - Log every feature usage
- ✅ `PaymentMethod` - Store payment methods for auto-renewal
- ✅ `SubscriptionRenewalLog` - Log all renewal attempts

#### **2. API Endpoints**
- ✅ `POST /api/usage/check/` - Pre-usage validation
- ✅ `POST /api/usage/record/` - Post-usage recording
- ✅ `GET /api/usage/real-time/` - Real-time dashboard
- ✅ `GET /api/usage/restriction/<feature>/` - Restriction details
- ✅ `GET /api/usage/history/` - Usage history
- ✅ `POST /api/usage/enforce-check/` - Strict enforcement

#### **3. Subscription Management**
- ✅ Purchase flow (Free → Premium)
- ✅ Automatic monthly renewal
- ✅ Grace period (3 days)
- ✅ Restriction restoration after expiry
- ✅ Renewal reminders

#### **4. Scheduled Tasks (Celery)**
- ✅ Daily subscription renewal check
- ✅ Renewal reminder (7 days before)
- ✅ Restore free plan (grace period end)
- ✅ Failed renewal notifications

#### **5. Email Notifications**
- ✅ Subscription activated
- ✅ Renewal reminder (7 days before)
- ✅ Renewal successful
- ✅ Renewal failed
- ✅ Subscription expired
- ✅ Features restricted

#### **6. Admin Dashboard**
- ✅ View all subscriptions
- ✅ Manual renewal/cancellation
- ✅ Usage analytics
- ✅ Renewal status tracking

### **Security Requirements**

```python
# Authentication for all endpoints
@require_user_id_header
def api_endpoint(request):
    user_id = request.headers.get('X-User-ID')
    subscription = UserSubscription.objects.get(user_id=user_id)
    # ... process

# Data isolation
- All queries filtered by user_id
- No cross-user data access
- Subscription verification on every request

# Payment security
- Never store full credit card numbers
- Use Razorpay tokenization
- Encrypted payment method storage
- PCI-DSS compliance
```

### **Performance Requirements**

```
Endpoint Response Times:
- /api/usage/check/ → < 50ms
- /api/usage/record/ → < 100ms
- /api/usage/real-time/ → < 100ms
- /api/usage/history/ → < 200ms

Database Indexes:
- subscription_id
- feature_name
- created_at
- subscription + feature_name
- subscription + created_at
```

---

## Complete User Journey Example

### **User Story: Alice's Feature Usage**

**Day 1: Alice Signs Up**
```
1. Alice creates account
2. UserSubscription created:
   - plan: "free"
   - subscription_status: "active"
   - All features get free limits (Quiz: 3, Flashcards: 3, etc.)
```

**Day 2: Alice Uses Quiz (1/3)**
```
1. Alice clicks "Create Quiz"
2. Frontend: POST /api/usage/check/ → ✅ Allowed (3 remaining)
3. Alice submits quiz data
4. Backend: Creates quiz
5. Backend: POST /api/usage/record/ 
   - Creates FeatureUsageLog entry
   - Updates UserSubscription.last_usage_date
   - Updates UserSubscription.total_usage_count
6. Response: "Quiz created! 2 uses remaining"
```

**Day 5: Alice Uses Quiz (3/3 - EXHAUSTED)**
```
1. Alice clicks "Create Quiz" again (3rd time)
2. Frontend: POST /api/usage/check/ → ✅ Allowed (1 remaining)
3. Alice submits quiz data
4. Backend: Creates quiz
5. Backend: POST /api/usage/record/ 
   - Creates FeatureUsageLog entry
   - Now: used_count = 3
6. Next check: POST /api/usage/check/ → ❌ Denied (0 remaining)
   - "Quota exhausted. Upgrade to create more quizzes."
```

**Day 10: Alice Buys Premium**
```
1. Alice clicks "Upgrade to Premium" ($9.99/month)
2. Razorpay payment gateway
3. Payment successful
4. Backend: Update UserSubscription
   - plan: "free" → "premium"
   - subscription_status: "active"
   - end_date: NOW() + 30 days
   - renewal_date: NOW() + 30 days
   - auto_renewal: true
5. All feature restrictions REMOVED
6. Alice can now: Create unlimited quizzes, flashcards, etc.
7. Email: "Welcome to Premium! All features unlocked."
```

**Day 40: Auto-Renewal Triggers**
```
1. Scheduled task: renew_subscriptions()
2. Found Alice's subscription (renewal_date = today)
3. Automatic charge: ₹9.99 via Razorpay
4. Payment successful
5. Update:
   - end_date: NOW() + 30 days
   - renewal_date: NOW() + 30 days
6. Email: "Subscription renewed! Premium active for 30 more days."
```

**Day 71: Subscription Expires (Renewal Failed)**
```
1. Scheduled task: renew_subscriptions()
2. Automatic charge: ₹9.99 FAILS (insufficient funds)
3. mark_subscription_pending_renewal()
4. subscription_status: "pending_renewal"
5. Email: "Renewal failed. Update payment method to continue."
6. Grace period: 3 days (features still work)
```

**Day 74: Grace Period Ends**
```
1. Scheduled task: restore_free_plan_after_grace_period()
2. subscription_status: "expired" → "inactive"
3. plan: "premium" → "free"
4. Feature restrictions restored:
   - Quiz: unlimited → 3
   - Flashcards: unlimited → 3
   - etc.
5. Email: "Subscription expired. Features restricted."
6. Next quiz attempt: ❌ "1/3 uses remaining"
```

---

## Summary & Key Takeaways

### ✅ Complete Implementation Checklist

- [x] **Feature Usage Tracking** - Every use recorded with full details
- [x] **Real-Time Quota Updates** - Instant quota display after use
- [x] **Database Storage** - FeatureUsageLog + UserSubscription
- [x] **Subscription Management** - Purchase, activate, track
- [x] **Automatic Monthly Renewal** - Celery task every 24 hours
- [x] **Restriction Enforcement** - 403 on quota exceeded
- [x] **Grace Period** - 3 days after expiry before restriction
- [x] **Email Notifications** - All important events
- [x] **Scheduled Tasks** - Renewal, reminders, grace period
- [x] **Security** - User isolation, encrypted payments

### 📊 Feature Quota Structure

**Free Plan:**
- Quiz: 3 uses/month
- Flashcards: 3 uses/month
- Pair Quiz: 1 use/month
- Ask Question: 5 uses/month
- Predicted Questions: 3 uses/month
- YouTube Summarizer: 2 uses/month
- Daily Quiz: Unlimited
- Mock Test: 3 uses/month
- Previous Papers: Limited
- PYQs: Limited

**Premium/Pro Plan:**
- All features: Unlimited

### 🔄 Key Flows

1. **Feature Usage**: Check → Use → Record → Update Dashboard
2. **Subscription Purchase**: Payment → Activate → Remove Restrictions
3. **Monthly Renewal**: Check → Charge → Succeed/Fail → Notify
4. **Expiration**: End Date → Grace Period (3 days) → Restore Free Plan

### 📱 Frontend Integration

```javascript
// Before using a feature
const checkFeature = async (feature) => {
  const response = await fetch('/api/usage/check/', {
    method: 'POST',
    headers: { 'X-User-ID': userId },
    body: JSON.stringify({ feature })
  });
  
  if (response.status === 403) {
    showUpgradeModal(); // Feature exhausted
  } else {
    proceedWithFeature(); // Feature available
  }
};

// After feature is used
const recordUsage = async (feature, inputSize) => {
  await fetch('/api/usage/record/', {
    method: 'POST',
    headers: { 'X-User-ID': userId },
    body: JSON.stringify({ feature, input_size: inputSize })
  });
  
  updateDashboard(); // Refresh quota display
};

// Show dashboard
const showDashboard = async () => {
  const response = await fetch('/api/usage/real-time/', {
    headers: { 'X-User-ID': userId }
  });
  const data = await response.json();
  displayUsageStats(data.feature_usage);
};
```

---

## Next Steps

1. ✅ **Review this document** - Understand the complete flow
2. ✅ **Implement models** - Update UserSubscription and FeatureUsageLog
3. ✅ **Create endpoints** - Implement all 6 API endpoints
4. ✅ **Set up Celery** - Configure renewal tasks
5. ✅ **Add emails** - Send renewal reminders and notifications
6. ✅ **Test thoroughly** - Verify all scenarios (free → premium → expiry)
7. ✅ **Deploy** - Production deployment with monitoring

---

**Document Version:** 1.0  
**Last Updated:** January 10, 2026  
**Status:** Complete & Ready for Implementation

# Usage Flow Visual Diagrams & Quick Reference

## 1. Complete User Journey Timeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     ALICE'S COMPLETE JOURNEY                            │
└─────────────────────────────────────────────────────────────────────────┘

DAY 1: SIGN UP
═════════════════════════════════════════════════════════════════════════
  Alice creates account
  └─→ UserSubscription(plan='free', status='active')
      • Quiz: 3/3 ✓
      • Flashcards: 3/3 ✓
      • Pair Quiz: 1/1 ✓
      • Ask Question: 5/5 ✓
      • Daily Quiz: ∞ ✓


DAY 2-4: USES QUIZ (1/3)
═════════════════════════════════════════════════════════════════════════
  Day 2:
    POST /api/usage/check/ → ✅ (3 remaining)
    Create Quiz → SUCCESS
    POST /api/usage/record/ → RECORDED
    Dashboard: Quiz 1/3 ✓

  Day 3:
    POST /api/usage/check/ → ✅ (2 remaining)
    Create Quiz → SUCCESS
    POST /api/usage/record/ → RECORDED
    Dashboard: Quiz 2/3 ✓

  Day 4:
    POST /api/usage/check/ → ✅ (1 remaining)
    Create Quiz → SUCCESS
    POST /api/usage/record/ → RECORDED
    Dashboard: Quiz 3/3 ✓ EXHAUSTED


DAY 5: TRIES TO USE QUIZ AGAIN (QUOTA EXHAUSTED)
═════════════════════════════════════════════════════════════════════════
  POST /api/usage/check/ → ❌ 403 FORBIDDEN
  └─→ "Quota exhausted. Upgrade to create more."
      Button: "UPGRADE TO PREMIUM"


DAY 10: PURCHASES PREMIUM SUBSCRIPTION
═════════════════════════════════════════════════════════════════════════
  Click "UPGRADE TO PREMIUM" ($9.99/month)
    ↓
  Razorpay Payment Gateway
    ↓
  ✅ Payment Successful
    ↓
  UPDATE UserSubscription:
  • plan: 'free' → 'premium'
  • status: 'active'
  • end_date: 2026-02-10
  • renewal_date: 2026-02-10
  • auto_renewal: true
    ↓
  ALL RESTRICTIONS REMOVED:
  • Quiz: ∞ (unlimited)
  • Flashcards: ∞
  • Pair Quiz: ∞
  • Ask Question: ∞
  • Daily Quiz: ∞
  • All other features: ∞
    ↓
  Email: "Welcome to Premium! All features unlocked."


DAY 20: USES FEATURES FREELY
═════════════════════════════════════════════════════════════════════════
  Now Alice can:
  ✅ Create unlimited quizzes
  ✅ Create unlimited flashcards
  ✅ Use all features without limits
  ✅ No "upgrade" prompts shown


DAY 40: AUTO-RENEWAL TRIGGERS
═════════════════════════════════════════════════════════════════════════
  ⏰ Scheduled Task: renew_subscriptions() (2 AM)
    ↓
  Found: UserSubscription where renewal_date <= TODAY
    ↓
  AUTO CHARGE: ₹9.99 via Razorpay
    ↓
  ✅ Payment Successful
    ↓
  UPDATE:
  • end_date: 2026-03-12
  • renewal_date: 2026-03-12
  • subscription_status: 'active'
    ↓
  Email: "Subscription renewed! Premium active for 30 more days."


DAY 65: AUTO-RENEWAL ATTEMPTED (BUT FAILS)
═════════════════════════════════════════════════════════════════════════
  ⏰ Scheduled Task: renew_subscriptions()
    ↓
  AUTO CHARGE: ₹9.99 FAILS
  └─→ (Insufficient funds / Card declined)
    ↓
  SET STATUS: 'pending_renewal' (GRACE PERIOD: 3 days)
    ↓
  Email: "Renewal failed. Update payment method."
    ↓
  Features: Still work for 3 days


DAY 68: GRACE PERIOD ENDS (No Renewal Made)
═════════════════════════════════════════════════════════════════════════
  ⏰ Scheduled Task: restore_free_plan_after_grace_period()
    ↓
  UPDATE UserSubscription:
  • plan: 'premium' → 'free'
  • status: 'inactive'
    ↓
  RESTORE FREE PLAN RESTRICTIONS:
  • Quiz: ∞ → 0/3 remaining
  • Flashcards: ∞ → 0/3 remaining
  • Pair Quiz: ∞ → 0/1 remaining
  • Ask Question: ∞ → 0/5 remaining
    ↓
  Email: "Subscription expired. Features restricted."
    ↓
  Dashboard: Shows "0 uses remaining" with Upgrade button


DAY 69: TRIES TO USE QUIZ
═════════════════════════════════════════════════════════════════════════
  POST /api/usage/check/ → ❌ 403 FORBIDDEN
  └─→ "Quota exhausted. Upgrade to Premium."
      (Even though quota could reset at month end)

```

---

## 2. Feature Usage Flow (Detailed)

```
┌──────────────────────────────────────────────────────────────────┐
│                  FEATURE USAGE FLOW (DETAILED)                   │
└──────────────────────────────────────────────────────────────────┘

STEP 1: PRE-USAGE CHECK
═══════════════════════════════════════════════════════════════════
  USER ACTION: Clicks "Create Quiz" button
       ↓
  FRONTEND: Sends POST /api/usage/check/
       ↓
       Headers:
       • X-User-ID: alice_123
       
       Body:
       {
         "feature": "quiz",
         "input_size": 5000
       }
       ↓
  BACKEND PROCESSING:
       ├─ 1. Get UserSubscription(user_id='alice_123')
       │      subscription = {
       │        plan: 'free',
       │        status: 'active'
       │      }
       │
       ├─ 2. Get feature limits for plan
       │      limits['free']['quiz'] = 3
       │
       ├─ 3. Query FeatureUsageLog for past 30 days
       │      SELECT COUNT(*) FROM FeatureUsageLog
       │      WHERE subscription_id = 1
       │      AND feature_name = 'quiz'
       │      AND created_at >= NOW() - 30 days
       │      COUNT = 2 (used 2 times already)
       │
       └─ 4. Calculate remaining
              limit: 3
              used: 2
              remaining: 3 - 2 = 1
              allowed: remaining > 0 ✓
       ↓
  RESPONSE: 200 OK
  {
    "success": true,
    "feature": "quiz",
    "allowed": true,
    "used": 2,
    "limit": 3,
    "remaining": 1,
    "message": "Feature available. 1 use remaining."
  }
       ↓
  FRONTEND: Show message "1 quiz remaining this month"
            ENABLE "Create Quiz" button


STEP 2: FEATURE EXECUTION
═══════════════════════════════════════════════════════════════════
  USER ACTION: Fills quiz details → Clicks "Generate"
       ↓
  FRONTEND: Sends quiz parameters to backend
       ↓
  BACKEND:
       ├─ Parse quiz parameters
       ├─ Generate quiz questions (using Gemini API)
       ├─ Store quiz in Quiz table
       ├─ Create Quiz metadata
       └─ ✅ SUCCESS (or ❌ ERROR)
       
  (Note: Only proceed to STEP 3 if SUCCESS)


STEP 3: POST-USAGE RECORDING
═══════════════════════════════════════════════════════════════════
  BACKEND: After quiz creation succeeds
       ↓
  BACKEND CALLS: POST /api/usage/record/
       ↓
       Headers:
       • X-User-ID: alice_123
       
       Body:
       {
         "feature": "quiz",
         "input_size": 5000,
         "usage_type": "text",
         "output_data": {
           "quiz_id": "q_12345",
           "questions": 10,
           "duration": 30
         }
       }
       ↓
  DATABASE OPERATIONS:
       ├─ 1. Get UserSubscription(user_id='alice_123')
       │      subscription = UserSubscription(id=1)
       │
       ├─ 2. Create FeatureUsageLog entry:
       │      INSERT INTO FeatureUsageLog:
       │      {
       │        subscription_id: 1,
       │        feature_name: 'quiz',
       │        input_size: 5000,
       │        usage_type: 'text',
       │        created_at: NOW(),
       │        status: 'completed'
       │      }
       │
       ├─ 3. Update UserSubscription:
       │      UPDATE UserSubscription
       │      SET last_usage_date = NOW(),
       │          total_usage_count = total_usage_count + 1
       │      WHERE id = 1
       │
       └─ 4. Calculate new quota
              SELECT COUNT(*) FROM FeatureUsageLog
              WHERE subscription_id = 1
              AND feature_name = 'quiz'
              COUNT = 3 (now 3 uses total)
              remaining = 3 - 3 = 0
       ↓
  RESPONSE: 200 OK
  {
    "success": true,
    "feature": "quiz",
    "usage_recorded": true,
    "current_quota": {
      "used": 3,
      "limit": 3,
      "remaining": 0,
      "percentage": 100
    },
    "message": "Usage recorded. No quizzes remaining this month."
  }
       ↓
  FRONTEND: Display "Quiz created! Quota exhausted."
            DISABLE "Create Quiz" button
            SHOW "Upgrade to Premium" button


STEP 4: REAL-TIME DASHBOARD UPDATE
═══════════════════════════════════════════════════════════════════
  FRONTEND: GET /api/usage/real-time/
       ↓
  BACKEND QUERIES:
       ├─ Get all FeatureUsageLog entries (last 30 days)
       ├─ Group by feature_name
       ├─ Count uses per feature
       ├─ Get limits from UserSubscription.plan
       └─ Calculate remaining for each
       ↓
  RESPONSE: 200 OK
  {
    "success": true,
    "timestamp": "2026-01-10T10:30:00Z",
    "plan": "free",
    "subscription_status": "active",
    "feature_usage": {
      "quiz": {
        "name": "Quiz",
        "used": 3,
        "limit": 3,
        "remaining": 0,
        "percentage": 100,
        "allowed": false,
        "last_used": "2026-01-10T10:25:00Z"
      },
      "flashcards": {
        "name": "Flashcards",
        "used": 1,
        "limit": 3,
        "remaining": 2,
        "percentage": 33,
        "allowed": true,
        "last_used": "2026-01-09T15:20:00Z"
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
       ↓
  FRONTEND: Update dashboard
       ├─ Quiz: 3/3 (RED) ❌
       ├─ Flashcards: 1/3 (GREEN) ✓
       ├─ Pair Quiz: 0/1 (GREEN) ✓
       └─ "Upgrade to Premium to get unlimited uses"

```

---

## 3. Subscription Lifecycle

```
┌──────────────────────────────────────────────────────────────────┐
│            SUBSCRIPTION LIFECYCLE (STATE MACHINE)                │
└──────────────────────────────────────────────────────────────────┘

                           ┌─────────────┐
                           │   SIGN UP   │
                           │ (FREE PLAN) │
                           └──────┬──────┘
                                  │
                          ┌───────┴────────┐
                          ↓                │
                     ┌─────────┐          │
                     │  ACTIVE │◄─────────┘
                     │  (FREE) │
                     └────┬────┘
                          │
                   ┌──────┴──────┐
                   │             │
                   ↓ (Buy)       │
              ┌─────────┐        │
              │ CHARGING        │
              └────┬────┘        │
                   │             │
            ┌──────┴──────┐      │
            │             │      │
       ✅ SUCCESS    ❌ FAIL    │
            │             │      │
            ↓             ↓      │
      ┌──────────┐  ┌────────────┼─────┐
      │  ACTIVE  │  │  EXPIRED/  │     │
      │ (PREMIUM)│  │  PENDING   │     │
      └────┬─────┘  │            │     │
           │        └────────────┘     │
           │                           │
      (Every 30 days)             (Auto-renew
      Auto-renew triggers)        disabled)
           │                           │
           ↓                           │
      ┌──────────┐                     │
      │ CHARGING │                     │
      └────┬─────┘                     │
           │                           │
        ┌──┴────┬─────────┐            │
        │       │         │            │
    ✅ RENEW  FAIL    ❌ FAIL       │
        │       │      (Too many)     │
        │       │         │            │
        ↓       ↓         ↓            ↓
      LOOP   GRACE    EXPIRED      CANCELLED
            PERIOD
              (3d)
               │
               ↓
            EXPIRED


STATE TRANSITIONS:
═════════════════════════════════════════════════════════════════

1. FREE → PREMIUM (User buys subscription)
   ├─ Payment success → ACTIVE (premium)
   └─ Payment fail → Stays ACTIVE (free)

2. ACTIVE (PREMIUM) → CHARGING → ACTIVE (every 30 days)
   ├─ Auto-charge successful → extends end_date
   └─ Auto-charge fails → PENDING_RENEWAL (grace period 3d)

3. PENDING_RENEWAL → EXPIRED (grace period ends, no manual renewal)
   └─ All restrictions restored

4. ACTIVE (PREMIUM) → CANCELLED (user manually cancels)
   └─ Immediate expiration, no grace period

5. EXPIRED → ACTIVE (PREMIUM) (user re-subscribes)
   ├─ Payment success → Back to ACTIVE
   └─ New cycle starts


```

---

## 4. Database Schema Relationships

```
┌────────────────────────────────────────────────────────────┐
│                    DATABASE SCHEMA                         │
└────────────────────────────────────────────────────────────┘

┌─────────────────────────────────┐
│     UserSubscription            │
├─────────────────────────────────┤
│ id (PK)                         │
│ user_id (UNIQUE)                │◄──────────────────┐
│ plan (free/premium/pro)         │                   │
│ subscription_status (active/...) │                   │
│ start_date                      │                   │
│ end_date                        │                   │
│ renewal_date                    │                   │
│ auto_renewal (boolean)          │                   │
│ last_usage_date                 │                   │
│ total_usage_count               │                   │
│ created_at                      │                   │
│ updated_at                      │                   │
└─────────────────────────────────┘                   │
          ▲                                           │
          │ (1 subscription per user)                 │
          │                                           │
          │                                           │
┌─────────────────────────────────┐                   │
│   FeatureUsageLog (FK)          │                   │
├─────────────────────────────────┤                   │
│ id (PK)                         │                   │
│ subscription_id (FK)────────────┼───────────────────┘
│ feature_name                    │
│   ├─ quiz                       │
│   ├─ flashcards                 │
│   ├─ pair_quiz                  │
│   ├─ ask_question               │
│   ├─ predicted_questions        │
│   ├─ previous_papers            │
│   ├─ pyqs                       │
│   ├─ youtube_summarizer         │
│   ├─ daily_quiz                 │
│   └─ mock_test                  │
│ input_size                      │
│ usage_type (text/file/link/api) │
│ created_at                      │
│ status (pending/completed/...)  │
└─────────────────────────────────┘


KEY RELATIONSHIPS:
═════════════════════════════════════════════════════════════

1. One User ↔ One UserSubscription
   ├─ Tracks current subscription status
   ├─ Tracks subscription dates
   └─ Tracks renewal info

2. One UserSubscription ↔ Many FeatureUsageLog entries
   ├─ Each usage creates a log entry
   ├─ Queries grouped by subscription
   └─ Indexed for fast lookups

3. FeatureUsageLog indexed by:
   ├─ subscription_id (FK)
   ├─ feature_name
   ├─ created_at
   └─ (subscription_id, feature_name)


QUERY PATTERNS:
═════════════════════════════════════════════════════════════

Get usage count for feature:
  SELECT COUNT(*) FROM FeatureUsageLog
  WHERE subscription_id = ?
  AND feature_name = 'quiz'
  AND created_at >= NOW() - INTERVAL 30 DAYS

Get all usage history:
  SELECT * FROM FeatureUsageLog
  WHERE subscription_id = ?
  ORDER BY created_at DESC
  LIMIT 100

Get usage grouped by feature:
  SELECT feature_name, COUNT(*) as count
  FROM FeatureUsageLog
  WHERE subscription_id = ?
  AND created_at >= NOW() - INTERVAL 30 DAYS
  GROUP BY feature_name

```

---

## 5. Quota Reset Logic

```
┌────────────────────────────────────────────────────────────┐
│               QUOTA RESET & RENEWAL LOGIC                  │
└────────────────────────────────────────────────────────────┘

SCENARIO 1: Free Plan User (No Subscription Renewal)
═════════════════════════════════════════════════════════════

Month 1 (Jan 1-31):
  ├─ Quiz: 0/3
  ├─ Flashcards: 0/3
  ├─ Pair Quiz: 0/1
  └─ ...

User uses Quiz 3 times:
  ├─ Day 5: Quiz 1/3
  ├─ Day 10: Quiz 2/3
  ├─ Day 15: Quiz 3/3 (EXHAUSTED)
  └─ Day 20: Quiz usage remains 3/3

On Feb 1 (New Month):
  OPTION A: Manual reset required (user action)
    └─ Admin endpoint or user clicks "Reset" button
  
  OPTION B: Automatic reset via scheduled task
    └─ Scheduled task runs on midnight Feb 1
       └─ FeatureUsageLog records with created_at < Feb 1
          are NOT counted anymore (only last 30 days)
       └─ /api/usage/real-time/ shows fresh quotas


SCENARIO 2: Premium User (Subscription Renewal)
═════════════════════════════════════════════════════════════

Premium user with 30-day subscription:
  Subscription:
    start_date: Jan 10
    end_date: Feb 10
    renewal_date: Feb 10
    plan: premium

  Jan 10 - Feb 9:
    └─ All features UNLIMITED
    └─ Usage recorded in FeatureUsageLog
    └─ But quotas don't apply (premium)

  Feb 10: Auto-renewal triggers
    ├─ Charge: ₹9.99
    ├─ ✅ Successful
    └─ Update:
       ├─ start_date: Feb 10
       ├─ end_date: Mar 12
       ├─ renewal_date: Mar 12
       └─ plan: premium (continues)

  Feb 10 - Mar 11:
    └─ All features UNLIMITED (continues)


SCENARIO 3: User Switches Free → Premium → Free
═════════════════════════════════════════════════════════════

Month 1 (Jan 1-31):
  FREE PLAN:
  └─ Quiz: 3/3 (exhausted)

Jan 20: User buys premium ($9.99)
  └─ Query doesn't reset!
  └─ FeatureUsageLog records remain
  └─ But quotas don't apply anymore

Jan 25 - Feb 9: Uses unlimited quizzes
  └─ 10 more quizzes created (14 total in FeatureUsageLog)

Feb 10: Subscription expires
  └─ Auto-renewal failed
  └─ Grace period: 3 days

Feb 13: Grace period ends
  └─ Plan: premium → free
  └─ NOW what happens?

SOLUTION:
  After grace period ends:
  ├─ Count FeatureUsageLog entries
  │  └─ Created in last 30 days
  │  └─ For the feature 'quiz'
  │  └─ Count = 14
  ├─ Remaining = 3 - 14 = -11 (negative!)
  ├─ UI shows: 0/3 remaining (0 uses left)
  └─ User CANNOT use quota until next month


IMPLEMENTATION:
═════════════════════════════════════════════════════════════

Option 1: Rolling 30-day window (RECOMMENDED)
  └─ Each feature resets 30 days after first use
     Quiz used on Jan 5:
     ├─ Quotas: Jan 5 - Feb 4
     ├─ On Feb 5: Fresh quota starts
     └─ Advantages: Fairer to users, but complex

Option 2: Calendar month reset
  └─ All features reset on 1st of every month
     ├─ Jan 1-31: 3 quizzes
     ├─ Feb 1: Fresh 3 quizzes
     └─ Advantages: Simple to understand

Option 3: Subscription cycle reset (Premium only)
  └─ For premium: resets on renewal date
     ├─ Premium Jan 10 - Feb 9: unlimited
     ├─ Premium Feb 10 - Mar 11: unlimited
     └─ For free: no reset (quota exhausted forever)

RECOMMENDATION: Option 2 (Calendar month reset)
  └─ Simplest to implement
  └─ Most user-friendly
  └─ Most common in SaaS

IMPLEMENTATION CODE:
  def get_current_month_start():
    now = datetime.now()
    return datetime(now.year, now.month, 1)

  def get_feature_usage_count(user_id, feature_name):
    subscription = UserSubscription.objects.get(user_id=user_id)
    month_start = get_current_month_start()
    
    count = FeatureUsageLog.objects.filter(
        subscription=subscription,
        feature_name=feature_name,
        created_at__gte=month_start
    ).count()
    
    return count

```

---

## 6. Email Notification Templates

```
┌────────────────────────────────────────────────────────────┐
│            EMAIL NOTIFICATION TEMPLATES                    │
└────────────────────────────────────────────────────────────┘

1. SUBSCRIPTION ACTIVATED
═════════════════════════════════════════════════════════════

Subject: 🎉 Welcome to Premium! All Features Unlocked

Body:
  Hi Alice,

  Welcome to Premium! Your subscription is now active.

  ✅ WHAT'S UNLOCKED:
  • Unlimited Quizzes
  • Unlimited Flashcards
  • Unlimited Pair Quiz
  • Unlimited Ask Question
  • All other features unlocked

  📅 SUBSCRIPTION DETAILS:
  • Plan: Premium
  • Renewal Date: 2026-02-10
  • Price: ₹9.99/month (auto-renewing)

  🔐 MANAGE YOUR SUBSCRIPTION:
  [Link: /account/subscription/]

  Questions? Contact us at support@edtech.com

  Best regards,
  EdTech Team


2. RENEWAL REMINDER (7 days before)
═════════════════════════════════════════════════════════════

Subject: ⏰ Your subscription renews in 7 days

Body:
  Hi Alice,

  Your Premium subscription will renew on 2026-02-10.
  We'll automatically charge ₹9.99 to your account.

  ✅ YOUR CURRENT BENEFITS:
  • Unlimited feature access
  • Priority support
  • Exclusive updates

  💳 UPDATE PAYMENT METHOD:
  If you need to update your payment method, please do so now:
  [Link: /account/payment-method/]

  ❌ CANCEL ANYTIME:
  If you'd like to cancel, you have until 2026-02-09:
  [Link: /account/cancel-subscription/]

  Thank you for being a premium member!

  Best regards,
  EdTech Team


3. RENEWAL SUCCESSFUL
═════════════════════════════════════════════════════════════

Subject: ✅ Subscription Renewed - Premium Active

Body:
  Hi Alice,

  Great news! Your subscription has been renewed successfully.

  💰 CHARGE DETAILS:
  • Amount: ₹9.99
  • Date: 2026-02-10
  • Next Renewal: 2026-03-12

  ✅ YOUR BENEFITS CONTINUE:
  • Unlimited Quizzes
  • Unlimited Flashcards
  • All premium features

  📄 VIEW RECEIPT:
  [Link: /account/receipts/renewal-2026-02-10/]

  Thanks for continuing with us!

  Best regards,
  EdTech Team


4. RENEWAL FAILED
═════════════════════════════════════════════════════════════

Subject: ⚠️ Subscription Renewal Failed - Action Required

Body:
  Hi Alice,

  We attempted to renew your subscription on 2026-02-10,
  but the payment failed.

  ❌ FAILURE REASON:
  • Insufficient funds on card
  • (or other reason from Razorpay)

  🔧 WHAT HAPPENS NOW:
  • Your premium features still work for 3 more days
  • After 3 days, your account will revert to Free Plan
  • Free plan quotas will apply

  💳 FIX IT NOW:
  Please update your payment method:
  [Link: /account/payment-method/]

  Once updated, we'll retry the charge automatically.

  Questions? Contact support@edtech.com

  Best regards,
  EdTech Team


5. SUBSCRIPTION EXPIRED (Grace period ended)
═════════════════════════════════════════════════════════════

Subject: 😢 Your Premium Subscription Has Expired

Body:
  Hi Alice,

  Your Premium subscription has expired, and the grace period
  has ended. Your account has reverted to the Free Plan.

  ❌ PREMIUM BENEFITS REMOVED:
  • Quiz: Limited to 3/month
  • Flashcards: Limited to 3/month
  • All features now have limits

  ✨ GET PREMIUM AGAIN:
  Unlock unlimited features again:
  [Button: UPGRADE TO PREMIUM]

  We have special offers available:
  • First month: 50% off
  • Annual plan: 20% savings

  [Link: /plans/]

  We miss you!

  Best regards,
  EdTech Team


6. FEATURE QUOTA EXHAUSTED
═════════════════════════════════════════════════════════════

Subject: You've Used All Your Quizzes This Month

Body:
  Hi Alice,

  You've used all 3 quizzes available on your Free Plan
  this month.

  📊 YOUR USAGE:
  • Quizzes: 3/3 (Exhausted)
  • Flashcards: 1/3 (Available)
  • Other features: Available

  🚀 UNLOCK UNLIMITED:
  Upgrade to Premium to create unlimited quizzes:
  [Button: UPGRADE NOW]

  Start with 50% off your first month!

  [Link: /plans/premium/]

  Best regards,
  EdTech Team

```

---

## 7. Monitoring & Alert Thresholds

```
┌────────────────────────────────────────────────────────────┐
│        MONITORING & ALERT THRESHOLDS                       │
└────────────────────────────────────────────────────────────┘

SYSTEM HEALTH METRICS:
═════════════════════════════════════════════════════════════

1. Subscription Renewal Success Rate
   └─ Target: ≥ 95%
   └─ Alert: < 90%
   └─ Action: Check payment gateway status

2. Feature Usage Recording Latency
   └─ Target: < 100ms
   └─ Alert: > 500ms
   └─ Action: Optimize database queries

3. API Endpoint Response Times
   └─ /api/usage/check/: < 50ms
   └─ /api/usage/record/: < 100ms
   └─ /api/usage/real-time/: < 100ms
   └─ Alert: Exceeds threshold
   └─ Action: Scale database/cache

4. Auto-Renewal Task Success
   └─ Daily at 2 AM
   └─ Target: 100% completion
   └─ Alert: Task fails or times out
   └─ Action: Check Celery worker status

5. Database Backup Status
   └─ Daily backups
   └─ Target: 100% success
   └─ Alert: Backup fails
   └─ Action: Manual review


USER BEHAVIOR METRICS:
═════════════════════════════════════════════════════════════

1. Free → Premium Conversion Rate
   └─ Target: 5-10%
   └─ Low: < 2% (investigate pricing)
   └─ High: > 20% (pricing might be too low)

2. Premium Churn Rate (Cancellation)
   └─ Target: < 5% per month
   └─ Alert: > 10%
   └─ Action: Email users, offer discounts

3. Renewal Failure Handling
   └─ Retry: 2-3 times before expiry
   └─ Grace Period: 3 days
   └─ Monitor: High failure rate → check payments

4. Feature Usage Distribution
   └─ Quiz: Most popular
   └─ Flashcards: 2nd popular
   └─ Others: Track engagement

5. Quota Exhaustion Rate
   └─ High: Many users hitting free limits
   └─ Good: Indicates high engagement
   └─ Low: Users might not need features


AUTOMATED ALERTS:
═════════════════════════════════════════════════════════════

Alert 1: Renewal Task Failed
  └─ Condition: renew_subscriptions() failed
  └─ Severity: HIGH
  └─ Action: Slack notification + retry
  └─ Escalate: If fails 3 times in a row

Alert 2: High Failed Renewals
  └─ Condition: > 10% renewal failures
  └─ Severity: MEDIUM
  └─ Action: Email affected users
  └─ Analysis: Payment gateway issues?

Alert 3: Database Query Timeout
  └─ Condition: Query > 1 second
  └─ Severity: MEDIUM
  └─ Action: Add database index
  └─ Monitor: Query performance

Alert 4: Feature Overuse Detected
  └─ Condition: User exceeds quota by >20%
  └─ Severity: LOW
  └─ Action: Log for review
  └─ Analysis: Possible API abuse?

```

---

## Quick Command Reference

```bash
# Check subscription status
curl -H "X-User-ID: alice_123" http://localhost:8000/api/usage/subscription/

# Get real-time usage
curl -H "X-User-ID: alice_123" http://localhost:8000/api/usage/real-time/

# Check if feature available before use
curl -X POST -H "X-User-ID: alice_123" \
  -H "Content-Type: application/json" \
  -d '{"feature": "quiz"}' \
  http://localhost:8000/api/usage/check/

# Record usage after feature is used
curl -X POST -H "X-User-ID: alice_123" \
  -H "Content-Type: application/json" \
  -d '{
    "feature": "quiz",
    "input_size": 5000,
    "usage_type": "text"
  }' \
  http://localhost:8000/api/usage/record/

# Get usage history
curl -H "X-User-ID: alice_123" \
  'http://localhost:8000/api/usage/history/?days=7&feature=quiz'

# Get feature restriction details
curl -H "X-User-ID: alice_123" \
  http://localhost:8000/api/usage/restriction/quiz/

# Force check (strict enforcement)
curl -X POST -H "X-User-ID: alice_123" \
  -H "Content-Type: application/json" \
  -d '{"feature": "quiz"}' \
  http://localhost:8000/api/usage/enforce-check/

# Admin: View all subscriptions
curl -H "Authorization: Bearer admin_token" \
  http://localhost:8000/api/admin/subscriptions/

# Admin: Manually renew subscription
curl -X POST -H "Authorization: Bearer admin_token" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "alice_123"}' \
  http://localhost:8000/api/admin/renew-subscription/
```

---

**Document Version:** 1.0  
**Last Updated:** January 10, 2026  
**Status:** Complete Reference

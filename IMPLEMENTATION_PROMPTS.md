# Implementation Prompts & Developer Requirements

## Overview

This document contains detailed implementation prompts that define the **complete requirements** for the usage tracking, subscription management, and quota enforcement system. Use these prompts to guide development and ensure all requirements are met.

---

## PROMPT 1: Feature Usage Tracking System

### Context
You are building a comprehensive feature usage tracking system for an EdTech platform that tracks how many times users can use features based on their subscription plan.

### Requirements

**1. Database Models**
Create or enhance the following models:

```
UserSubscription Model:
- Fields:
  * user_id (unique identifier for user)
  * plan (free, premium, pro)
  * subscription_status (active, inactive, expired, pending_renewal)
  * start_date (when subscription started)
  * end_date (when subscription expires)
  * renewal_date (when next auto-renewal will occur)
  * auto_renewal (boolean - whether to auto-renew)
  * last_usage_date (last time user used any feature)
  * total_usage_count (total features used)
  * created_at, updated_at
- Indexes:
  * user_id (unique)
  * subscription_status
  * renewal_date
  * end_date

FeatureUsageLog Model:
- Fields:
  * subscription (foreign key to UserSubscription)
  * feature_name (quiz, flashcards, pair_quiz, ask_question, etc.)
  * input_size (size of input in bytes/characters)
  * usage_type (text, file, link, api)
  * created_at (timestamp of usage)
  * status (pending, completed, failed)
- Indexes:
  * (subscription_id, feature_name)
  * created_at
  * (subscription_id, created_at)
```

**2. Feature Limits Dictionary**
Define quotas for each plan:

```
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
    'premium': {  # All unlimited
        'quiz': -1,
        'flashcards': -1,
        # ... all features unlimited
    },
    'pro': {  # All unlimited
        'quiz': -1,
        # ... all features unlimited
    }
}
```

**3. Service Layer**
Create a `FeatureUsageService` class with methods:

```
- check_feature_access(user_id, feature_name) → (allowed: bool, remaining: int)
- record_feature_usage(user_id, feature_name, input_size, usage_type) → log_entry
- get_feature_usage_count(user_id, feature_name) → count
- get_user_all_features_usage(user_id) → dict with all features
- get_remaining_quota(user_id, feature_name) → remaining_count
```

### Acceptance Criteria
- ✅ Models created with proper fields and indexes
- ✅ All quota limits defined for each plan
- ✅ Service methods implemented and tested
- ✅ Usage logs created on every feature use
- ✅ Real-time quota tracking accurate

---

## PROMPT 2: Real-Time Usage Tracking Endpoints

### Context
Build REST API endpoints to track real-time feature usage, check quotas, and record usage.

### Requirements

**1. POST /api/usage/check/ (Pre-Usage Validation)**
Purpose: Check if user can use a feature BEFORE using it

Request:
```json
{
  "feature": "quiz",
  "input_size": 5000
}
```

Response (200 - Allowed):
```json
{
  "success": true,
  "feature": "quiz",
  "allowed": true,
  "used": 2,
  "limit": 3,
  "remaining": 1,
  "message": "Feature available. 1 use remaining."
}
```

Response (403 - Quota Exhausted):
```json
{
  "success": false,
  "feature": "quiz",
  "allowed": false,
  "reason": "Feature limit exhausted for free plan",
  "limit": 3,
  "used": 3,
  "remaining": 0
}
```

**2. POST /api/usage/record/ (Post-Usage Recording)**
Purpose: Record that feature was used (call after feature completes)

Request:
```json
{
  "feature": "quiz",
  "input_size": 5000,
  "usage_type": "text",
  "output_data": {}  // optional
}
```

Response (200):
```json
{
  "success": true,
  "feature": "quiz",
  "usage_recorded": true,
  "current_quota": {
    "used": 3,
    "limit": 3,
    "remaining": 0,
    "percentage": 100
  }
}
```

**3. GET /api/usage/real-time/ (Dashboard)**
Purpose: Get current usage for ALL features

Response (200):
```json
{
  "success": true,
  "timestamp": "2026-01-10T15:30:00Z",
  "plan": "free",
  "subscription_status": "active",
  "feature_usage": {
    "quiz": {
      "used": 2,
      "limit": 3,
      "remaining": 1,
      "percentage": 66.67,
      "allowed": true
    },
    "flashcards": {
      "used": 3,
      "limit": 3,
      "remaining": 0,
      "percentage": 100,
      "allowed": false
    }
  },
  "summary": {
    "total_features": 10,
    "features_available": 8,
    "features_exhausted": 2
  }
}
```

**4. GET /api/usage/history/ (Usage History)**
Purpose: Get historical usage with filtering

Query Params: `days=7&feature=quiz`

Response (200):
```json
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
    }
  ],
  "total_count": 2
}
```

**5. GET /api/usage/restriction/<feature>/ (Restriction Details)**
Purpose: Get detailed restriction info for a feature

Response (200 - If Restricted):
```json
{
  "success": true,
  "feature": "flashcards",
  "allowed": false,
  "used": 3,
  "limit": 3,
  "plan": "free",
  "restriction": {
    "reason": "Feature limit exhausted for free plan",
    "description": "You have used 3/3 flashcards allowed on the free plan",
    "unlock_option": "Upgrade to Premium Plan",
    "upgrade_benefits": [
      "Unlimited flashcards",
      "All features unlocked"
    ]
  }
}
```

### Acceptance Criteria
- ✅ All 5 endpoints implemented
- ✅ Authentication via X-User-ID header
- ✅ Proper error responses (403 for quota exceeded)
- ✅ Real-time quota calculations
- ✅ Response times < 100ms
- ✅ Comprehensive error handling

---

## PROMPT 3: Subscription Management System

### Context
Build a subscription management system that handles:
1. User purchasing subscriptions
2. Automatic monthly renewal
3. Expiration handling with grace period
4. Feature restriction restoration

### Requirements

**1. Purchase Flow**
When user buys subscription:

```python
def handle_subscription_purchase(user_id, plan, payment_token):
    """
    Flow:
    1. Process payment via Razorpay
    2. If successful:
       - Create/update UserSubscription
       - Set plan to purchased plan
       - Set subscription_status to 'active'
       - Set end_date = NOW() + 30 days
       - Set renewal_date = NOW() + 30 days
       - Set auto_renewal = true
    3. Remove all feature restrictions
    4. Send confirmation email
    5. Return success response
    """
```

**2. Automatic Monthly Renewal (Celery Task)**
Run daily at 2 AM:

```python
@task
def renew_subscriptions():
    """
    Find subscriptions where:
    - subscription_status = 'active'
    - renewal_date <= TODAY
    - auto_renewal = true
    
    For each subscription:
    1. Charge payment
    2. If successful:
       - Extend end_date by 30 days
       - Extend renewal_date by 30 days
       - Send success email
    3. If failed:
       - Set status to 'pending_renewal'
       - Start 3-day grace period
       - Send failure email
    """
```

**3. Grace Period (3 days after renewal fails)**
Features still work but:
- Warning banner shown
- "Renew Now" button in UI
- After 3 days: automatic restoration to free plan

**4. Subscription Expiration & Restoration**
After grace period ends:

```python
def restore_free_plan_after_grace():
    """
    Find expired subscriptions (grace_period_end <= NOW())
    
    For each:
    1. Update UserSubscription:
       - plan = 'free'
       - subscription_status = 'inactive'
    2. Feature restrictions re-applied
    3. Send notification email
    """
```

**5. Email Notifications Required**
- ✅ Subscription activated
- ✅ Renewal reminder (7 days before)
- ✅ Renewal successful
- ✅ Renewal failed
- ✅ Subscription expired
- ✅ Features restricted

### Acceptance Criteria
- ✅ Purchase flow working
- ✅ Auto-renewal runs daily
- ✅ Failed renewal handled with grace period
- ✅ Free plan restrictions restored correctly
- ✅ All emails sent
- ✅ Subscription dates accurate
- ✅ User data isolated (no cross-user access)

---

## PROMPT 4: Feature Restriction Enforcement

### Context
Implement strict enforcement that prevents users from using features when quota is exhausted.

### Requirements

**1. Pre-Usage Check**
Before ANY feature execution:

```python
def enforce_feature_access(user_id, feature_name):
    """
    1. Get UserSubscription for user
    2. Check if premium/pro with active status → allow (unlimited)
    3. For free plan:
       - Get feature limit from FEATURE_LIMITS
       - Count FeatureUsageLog for past 30 days
       - If count >= limit → return False (403)
       - Else → return True (200)
    """
```

**2. Strict Enforcement Endpoint**
POST /api/usage/enforce-check/

Returns:
- ✅ 200 OK: Feature allowed
- ❌ 403 FORBIDDEN: Feature quota exhausted (cannot proceed)

**3. Frontend Integration**
```
STEP 1: User clicks feature button
STEP 2: Frontend calls /api/usage/check/
STEP 3a: If 403 → Show "Upgrade" button (don't proceed)
STEP 3b: If 200 → Let user proceed to feature
STEP 4: After feature completes → Call /api/usage/record/
STEP 5: Update dashboard with new quota
```

**4. Permission Decorators**
Create Django decorator:

```python
@require_feature_access(feature='quiz')
def create_quiz_view(request):
    # This view is only called if user has access
    # If not → 403 FORBIDDEN returned automatically
```

### Acceptance Criteria
- ✅ Users cannot exceed free plan quota
- ✅ Premium users can use features unlimited
- ✅ 403 response when quota exhausted
- ✅ Quota cannot be bypassed
- ✅ Clear error messages to users

---

## PROMPT 5: Scheduled Tasks & Celery Configuration

### Context
Implement automated background tasks for subscription renewal and maintenance.

### Requirements

**1. Celery Beat Configuration**
In settings.py:

```python
CELERY_BEAT_SCHEDULE = {
    'renew-subscriptions': {
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
```

**2. Task 1: Daily Renewal**
```python
@shared_task
def renew_subscriptions():
    # Query: subscriptions where renewal_date <= TODAY
    # Process each subscription
    # Handle success and failures
    # Send emails
```

**3. Task 2: Renewal Reminders**
```python
@shared_task
def send_renewal_reminders():
    # Query: subscriptions where renewal_date = TODAY + 7 days
    # Send reminder emails
```

**4. Task 3: Grace Period Restoration**
```python
@shared_task
def restore_free_plan_after_grace_period():
    # Query: subscriptions where grace_period_end <= TODAY
    # Restore to free plan
    # Send notification
```

**5. Error Handling**
- Retry failed tasks
- Log all attempts
- Alert admin on repeated failures
- Fallback for payment gateway issues

### Acceptance Criteria
- ✅ All tasks run on schedule
- ✅ Error handling robust
- ✅ Logs comprehensive
- ✅ Admin alerts working
- ✅ Failed renewals retried

---

## PROMPT 6: Email Notification System

### Context
Send email notifications for all subscription and usage events.

### Requirements

**1. Email Template Structure**
Create templates for:
- Subscription activated
- Renewal reminder (7 days)
- Renewal successful
- Renewal failed
- Subscription expired
- Features restricted
- Usage exceeded

**2. Email Sending Service**
```python
class EmailService:
    def send_subscription_activated(user_id, plan, renewal_date)
    def send_renewal_reminder(user_id, renewal_date)
    def send_renewal_successful(user_id, plan, new_end_date)
    def send_renewal_failed(user_id, reason)
    def send_subscription_expired(user_id)
    def send_features_restricted(user_id)
```

**3. Dynamic Variables in Emails**
- User name
- Plan name
- Dates (renewal, expiry)
- Amount charged
- Features unlocked
- Support link
- Account management link

**4. Email Scheduling**
- Send immediately for important events (payment, expiry)
- Batch send for reminders
- Queue via Celery for reliability

### Acceptance Criteria
- ✅ All emails sent correctly
- ✅ Dynamic content accurate
- ✅ Professional formatting
- ✅ Unsubscribe option available
- ✅ Bounce handling

---

## PROMPT 7: Admin Dashboard & Monitoring

### Context
Build admin tools to monitor subscriptions, usage, and system health.

### Requirements

**1. Admin Endpoints**
```
GET /api/admin/subscriptions/
  └─ View all subscriptions with status
  
GET /api/admin/subscriptions/<user_id>/
  └─ View specific user subscription details
  
GET /api/admin/usage/analytics/
  └─ Usage statistics across all users
  
POST /api/admin/subscriptions/<user_id>/renew/
  └─ Manually renew subscription
  
POST /api/admin/subscriptions/<user_id>/cancel/
  └─ Manually cancel subscription
  
GET /api/admin/renewals/status/
  └─ View latest renewal attempts and results
```

**2. Metrics to Track**
- Total active subscriptions
- Renewal success rate
- Churn rate (cancellations)
- Usage by feature
- Free vs premium user ratio
- Revenue statistics

**3. Alert Configuration**
- Renewal failure rate > 10%
- API response time > 500ms
- Database errors
- Task execution failures

### Acceptance Criteria
- ✅ All endpoints working
- ✅ Accurate metrics
- ✅ Real-time data
- ✅ Admin authentication required
- ✅ Audit logs for all actions

---

## PROMPT 8: Security & Data Isolation

### Context
Ensure user data is properly isolated and payments are secure.

### Requirements

**1. Authentication**
- All endpoints require X-User-ID header
- Verify user_id matches request
- No cross-user data access

**2. Authorization**
```python
@require_authentication
def api_endpoint(request):
    user_id = request.headers.get('X-User-ID')
    # Verify this user can access this data
    subscription = UserSubscription.objects.get(user_id=user_id)
    # Process
```

**3. Data Isolation**
- All queries filtered by user_id
- Usage logs only show user's own data
- Admin can see all (with special permission)

**4. Payment Security**
- Never store full card numbers
- Use Razorpay tokenization
- Encrypt payment tokens
- PCI-DSS compliance

**5. Logging & Audit**
- Log all subscription changes
- Log all payment attempts
- Log all feature access denials
- Audit trail for admin actions

### Acceptance Criteria
- ✅ No data leakage between users
- ✅ Payments secure
- ✅ Audit logs comprehensive
- ✅ Rate limiting implemented
- ✅ SQL injection prevention

---

## PROMPT 9: Testing Strategy

### Context
Ensure all functionality is thoroughly tested.

### Requirements

**1. Unit Tests**
- Test feature limit logic
- Test quota calculations
- Test subscription state transitions
- Test email generation

**2. Integration Tests**
- Test full feature usage flow
- Test subscription purchase
- Test renewal process
- Test grace period
- Test free plan restoration

**3. End-to-End Tests**
- User signs up → uses feature 3 times → tries 4th time
- User upgrades subscription → features unlimited
- Subscription renewal triggers → success
- Subscription renewal fails → grace period → restoration

**4. Performance Tests**
- /api/usage/check/ response time < 50ms
- /api/usage/record/ response time < 100ms
- /api/usage/real-time/ response time < 100ms
- Bulk user queries (1000+ users)

**5. Edge Cases**
- User with no subscription
- User with expired subscription
- Concurrent feature usage
- Timezone handling
- Payment failure scenarios

### Acceptance Criteria
- ✅ > 90% code coverage
- ✅ All flows tested
- ✅ Performance meets requirements
- ✅ Edge cases handled
- ✅ All tests passing

---

## PROMPT 10: Deployment Checklist

### Context
Prepare for production deployment.

### Requirements

**1. Pre-Deployment**
- [ ] All tests passing (unit, integration, e2e)
- [ ] Database migrations tested
- [ ] Celery tasks configured
- [ ] Email templates created
- [ ] Admin panel functional
- [ ] Monitoring alerts configured
- [ ] Rollback plan documented

**2. Database Setup**
- [ ] Run migrations: `python manage.py migrate`
- [ ] Verify indexes created
- [ ] Backup strategy in place
- [ ] Query performance tested

**3. Celery Configuration**
- [ ] Redis/RabbitMQ configured
- [ ] Celery beat running
- [ ] Task retries configured
- [ ] Task monitoring enabled

**4. Payment Gateway**
- [ ] Razorpay API keys configured
- [ ] Test mode verified
- [ ] Webhook handling working
- [ ] Refund process documented

**5. Email Service**
- [ ] Email provider configured (SendGrid/AWS SES)
- [ ] Templates tested
- [ ] Bounce handling
- [ ] Unsubscribe management

**6. Monitoring**
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring (New Relic/DataDog)
- [ ] Log aggregation (CloudWatch/ELK)
- [ ] Alerting configured

**7. Documentation**
- [ ] API documentation complete
- [ ] Admin guide created
- [ ] User guide created
- [ ] Troubleshooting guide

**8. Post-Deployment**
- [ ] Smoke test all endpoints
- [ ] Verify emails sending
- [ ] Check database integrity
- [ ] Monitor system health
- [ ] User communication sent

### Acceptance Criteria
- ✅ All checklist items complete
- ✅ Zero errors on first day
- ✅ Smooth user experience
- ✅ Admin tools working
- ✅ All alerts functional

---

## Summary

### What You're Building
A complete feature quota and subscription management system that:

1. **Tracks usage** - Every feature use is recorded
2. **Enforces quotas** - Free plan users have limits (3 quizzes, 3 flashcards, etc.)
3. **Manages subscriptions** - Users can upgrade to premium
4. **Auto-renews** - Monthly subscriptions renew automatically
5. **Handles expiry** - Grace period (3 days) before restrictions restored
6. **Provides real-time updates** - Dashboard shows current quota instantly
7. **Sends notifications** - Email alerts for all important events
8. **Maintains security** - Proper user isolation and data protection

### Key Flows to Implement
1. ✅ User uses feature → /api/usage/check/ → /api/usage/record/
2. ✅ User upgrades → Purchase → Restrictions removed
3. ✅ User subscription expires → Grace period → Free plan restored
4. ✅ Auto-renewal → Daily task checks and renews subscriptions
5. ✅ Dashboard → Real-time quota display

### Success Criteria
- All endpoints working
- Tests passing
- Quota properly enforced
- Emails sending
- Celery tasks running
- Admin tools functional
- Zero security issues
- Performance targets met

---

**Document Version:** 1.0  
**Created:** January 10, 2026  
**Status:** Ready for Implementation

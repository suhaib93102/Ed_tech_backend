# Subscription System - Deployment Checklist

**Date**: January 6, 2026  
**System**: EdTech Platform  
**Status**: Ready for Deployment  

---

## ✅ Pre-Deployment Verification

### Code Quality
- [x] Feature usage service created and tested
- [x] API endpoints implemented and documented
- [x] Models updated with all features
- [x] URL routes configured
- [x] All imports verified
- [x] No syntax errors in code
- [x] Documentation complete

### Testing
- [x] Automated test script created
- [x] Curl examples provided
- [x] Three plans tested
- [x] Payment flow documented
- [x] Usage tracking verified
- [x] Limit enforcement tested
- [x] Dashboard endpoints working

### Documentation
- [x] Technical guide (SUBSCRIPTION_PLANS_GUIDE.md)
- [x] Curl reference (SUBSCRIPTION_PLANS_CURL_REFERENCE.md)
- [x] Visual guide (SUBSCRIPTION_PLANS_VISUAL.md)
- [x] Implementation summary (SUBSCRIPTION_IMPLEMENTATION_SUMMARY.md)
- [x] README (README_SUBSCRIPTION_SYSTEM.md)
- [x] Test script (test_subscription_plans.sh)

---

## 🚀 Deployment Checklist

### Step 1: Code Deployment

#### Local Testing First
```bash
# 1. Verify no syntax errors
python -m py_compile question_solver/feature_usage_service.py
python -m py_compile question_solver/usage_api_views.py
python -m py_compile question_solver/models.py

# 2. Check imports work
python -c "from question_solver.feature_usage_service import FeatureUsageService; print('✓ Imports OK')"

# 3. Run migrations locally
python manage.py makemigrations
python manage.py migrate

# 4. Test endpoints locally
python manage.py runserver &
bash test_subscription_plans.sh
```

#### Git Commit
```bash
# Stage files
git add question_solver/feature_usage_service.py
git add question_solver/usage_api_views.py
git add question_solver/models.py
git add question_solver/urls.py
git add test_subscription_plans.sh
git add SUBSCRIPTION_PLANS_GUIDE.md
git add SUBSCRIPTION_PLANS_CURL_REFERENCE.md
git add SUBSCRIPTION_PLANS_VISUAL.md
git add SUBSCRIPTION_IMPLEMENTATION_SUMMARY.md
git add README_SUBSCRIPTION_SYSTEM.md

# Commit with message
git commit -m "feat: Add subscription plans and usage tracking system

- Implement three subscription plans (FREE, BASIC, PREMIUM)
- Add feature usage tracking with real-time limits
- Create usage dashboard API endpoints
- Add monthly usage reset and billing integration
- Prevent over-usage with limit enforcement
- Support Razorpay payment integration
- Include comprehensive documentation and tests"

# Push to server
git push origin master
```

### Step 2: Production Environment Setup

#### Update .env on Production Server
```bash
# Ensure these are set in production .env:
RAZORPAY_KEY_ID=rzp_live_XXXXX
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
JWT_SECRET=production-secret-key-minimum-32-characters-long
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DEBUG=False
```

#### Deploy Code
```bash
# On Render or your hosting platform
# The automated deployment will:
# 1. Pull latest code from git
# 2. Run migrations automatically
# 3. Restart Django server
# 4. Update service
```

### Step 3: Database Migrations

#### Create Migrations (if not auto-created)
```bash
python manage.py makemigrations question_solver
```

#### Apply Migrations
```bash
python manage.py migrate
```

#### Verify Migrations
```bash
python manage.py showmigrations
# Should show all question_solver migrations as applied [X]
```

### Step 4: Initialize Default Plans

#### SSH into Production Server
```bash
# Connect to production
ssh your-server

# Navigate to project
cd /path/to/backend

# Start Django shell
python manage.py shell
```

#### Initialize Plans
```python
from question_solver.models import SubscriptionPlan

# Create plans
SubscriptionPlan.initialize_default_plans()

# Verify plans created
plans = SubscriptionPlan.objects.all()
for plan in plans:
    print(f"{plan.name}: {plan.display_name} - ₹{plan.first_month_price}/{plan.recurring_price}")

# Should see:
# free: FREE Plan - ₹0.00/0.00
# basic: BASIC Plan - ₹1.00/99.00
# premium: PREMIUM Plan - ₹199.00/499.00

exit()
```

### Step 5: Verify Endpoints are Accessible

#### Test Production Endpoints
```bash
# Test with production URL (replace with actual domain)
export PROD_URL="https://yourdomain.com"

# 1. Get plans
curl -X GET "$PROD_URL/api/subscriptions/plans/"

# 2. Register test user
curl -X POST "$PROD_URL/api/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{"email": "test-prod@example.com", "password": "TestPass123!"}'

# 3. Check dashboard (requires token from step 2)
curl -X GET "$PROD_URL/api/usage/dashboard/" \
  -H "Authorization: Bearer TOKEN"

# All should return 200 OK with proper JSON responses
```

### Step 6: Monitoring & Logging

#### Check Logs
```bash
# View recent logs
journalctl -u django-server -n 50

# Or check application logs
tail -f /var/log/app.log

# Look for any errors related to subscription or usage endpoints
```

#### Verify Database
```bash
# Connect to production database
python manage.py dbshell

# Check plans exist
SELECT * FROM question_solver_subscriptionplan;

# Check test user created
SELECT * FROM question_solver_usersubscription ORDER BY created_at DESC LIMIT 5;

# Check no errors
SELECT * FROM question_solver_payment WHERE status='failed';
```

#### Performance Check
```bash
# Measure endpoint response times
time curl -s "$PROD_URL/api/usage/dashboard/" \
  -H "Authorization: Bearer TOKEN" > /dev/null

# Should be under 500ms
```

### Step 7: Security Check

#### Verify Authentication
```bash
# Test endpoint without token (should fail)
curl -X GET "$PROD_URL/api/usage/dashboard/"
# Should return 401 Unauthorized

# Test with invalid token (should fail)
curl -X GET "$PROD_URL/api/usage/dashboard/" \
  -H "Authorization: Bearer invalid_token"
# Should return 401 Unauthorized

# Test with valid token (should succeed)
curl -X GET "$PROD_URL/api/usage/dashboard/" \
  -H "Authorization: Bearer VALID_TOKEN"
# Should return 200 OK with data
```

#### Verify Payment Security
```bash
# Check Razorpay signature verification is in place
grep -r "razorpay_signature" question_solver/
# Should find signature verification code

# Check JWT secret is strong
grep "JWT_SECRET" edtech_project/settings.py
# Should be at least 32 characters
```

### Step 8: Documentation Deployment

#### Upload Documentation
```bash
# Copy documentation files to accessible location
# For public wiki/docs site:
cp SUBSCRIPTION_PLANS_GUIDE.md /var/www/docs/
cp SUBSCRIPTION_PLANS_CURL_REFERENCE.md /var/www/docs/
cp SUBSCRIPTION_PLANS_VISUAL.md /var/www/docs/
cp README_SUBSCRIPTION_SYSTEM.md /var/www/docs/

# Or in project repository
# (already committed with git push)
```

#### Update API Documentation
```bash
# Update your API docs (OpenAPI/Swagger if applicable)
# Add these new endpoints:
# - GET /api/usage/dashboard/
# - GET /api/usage/feature/{name}/
# - POST /api/usage/check/
# - POST /api/usage/record/
# - GET /api/usage/subscription/
# - GET /api/usage/stats/
```

---

## 🧪 Post-Deployment Testing

### Smoke Tests (Quick Verification)

```bash
# Test 1: All endpoints accessible
curl -s "$PROD_URL/api/subscriptions/plans/" | grep -q "plans" && echo "✓ Plans endpoint OK"
curl -s "$PROD_URL/api/usage/stats/" -H "Authorization: Bearer TEST_TOKEN" | grep -q "stats" && echo "✓ Stats endpoint OK"

# Test 2: Database connected
curl -s "$PROD_URL/api/subscriptions/plans/" | jq '.plans | length' 
# Should return 3 (three plans)

# Test 3: Payment integration available
curl -s "$PROD_URL/api/subscriptions/plans/" | grep -q "razorpay" && echo "✓ Payment integration ready"
```

### Full Integration Tests

```bash
# Run complete test suite
bash test_subscription_plans.sh

# All 14 tests should PASS
# Look for: ✓ Test 1-14 PASSED
```

### Load Testing (Optional)

```bash
# Test with moderate traffic
# Using Apache Bench (ab) or similar:
ab -n 100 -c 10 "$PROD_URL/api/subscriptions/plans/"

# Should handle without errors
# Response time < 1 second per request
```

---

## 📊 Monitoring Setup

### Application Monitoring

#### Set Up Alerts For:
- [ ] High error rate (>5% errors)
- [ ] Slow endpoints (>2s response time)
- [ ] Database connection failures
- [ ] Payment failures
- [ ] Subscription activation failures

#### Daily Checks:
```bash
# Check for errors
grep "ERROR" /var/log/app.log | wc -l  # Should be 0

# Check failed payments
select count(*) from question_solver_payment where status='failed';  # Should be 0

# Check failed subscriptions
select count(*) from question_solver_usersubscription where subscription_status='failed';  # Should be 0
```

### User Monitoring

#### Track These Metrics:
- Number of users per plan
- Upgrade conversion rate (FREE → BASIC)
- Monthly recurring revenue (MRR)
- Feature usage trends
- Cancellation rate

#### Sample Queries:
```sql
-- Users per plan
SELECT plan, COUNT(*) as count FROM question_solver_usersubscription GROUP BY plan;

-- Recent upgrades
SELECT * FROM question_solver_usersubscription 
WHERE plan IN ('basic', 'premium') 
ORDER BY created_at DESC LIMIT 10;

-- MRR estimate
SELECT 
  SUM(CASE WHEN plan='basic' THEN 99 
           WHEN plan='premium' THEN 499 
           ELSE 0 END) as estimated_mrr
FROM question_solver_usersubscription
WHERE subscription_status='active';
```

---

## 🔄 Rollback Plan

If something goes wrong:

### Option 1: Quick Fix
```bash
# If just a code issue:
git revert <commit-hash>
git push origin master
# Server auto-deploys new code within 1 minute
```

### Option 2: Database Rollback
```bash
# If data issue:
# Restore from backup
pg_restore -d database_name backup_file.sql

# Then verify:
SELECT COUNT(*) FROM question_solver_subscriptionplan;
# Should return 3
```

### Option 3: Feature Flag Disable
```python
# Temporarily disable endpoint
@require_http_methods(["GET"])
def usage_dashboard(request):
    # Check feature flag
    if not settings.SUBSCRIPTION_ENABLED:
        return JsonResponse({
            'success': False,
            'error': 'Feature temporarily disabled'
        }, status=503)
    
    # Rest of logic...
```

---

## ✅ Sign-Off Checklist

### Development Team
- [ ] Code reviewed and approved
- [ ] All tests passing locally
- [ ] Documentation complete
- [ ] No known issues or TODOs

### QA Team
- [ ] All test cases passed
- [ ] No critical bugs found
- [ ] Performance acceptable
- [ ] Security verified

### DevOps/Deployment
- [ ] Infrastructure ready
- [ ] Backups configured
- [ ] Monitoring setup
- [ ] Rollback plan documented

### Product/Stakeholders
- [ ] Requirements met
- [ ] Documentation reviewed
- [ ] User communication ready
- [ ] Success metrics defined

---

## 📈 Success Metrics

After deployment, measure:

```
1. Adoption Rate
   Goal: 10%+ of users upgrade within 30 days
   Measure: COUNT(plan='basic' OR plan='premium') / COUNT(*)

2. Feature Usage
   Goal: Average 5+ features used per active user
   Measure: COUNT(DISTINCT feature_name) per user

3. Payment Success
   Goal: <5% payment failure rate
   Measure: failed_payments / total_payments

4. Monthly Recurring Revenue
   Goal: $5,000+ MRR within 60 days
   Measure: SUM(plan_price) for active subscriptions

5. Customer Satisfaction
   Goal: 4.5+ stars rating
   Measure: Survey feedback
```

---

## 📞 Support & Handoff

### Documentation for Support Team
1. Provide all documentation files
2. Run through system once together
3. Explain how to handle common issues
4. Provide escalation contacts

### Common Support Questions

**Q: User says they can't use quiz anymore**
A: Check if limit reached:
```sql
SELECT quiz_used, plan FROM question_solver_usersubscription WHERE user_id='XXX';
```
If limit hit, suggest upgrade.

**Q: Payment shows pending but not charged**
A: Check Razorpay webhook status
```sql
SELECT * FROM question_solver_payment WHERE status='pending';
```
May need manual verification.

**Q: User wants refund**
A: Check subscription status
```sql
SELECT * FROM question_solver_usersubscription WHERE user_id='XXX';
```
If within 30 days, can refund the charge.

---

## 🎯 Next Steps (Post-Deployment)

### Week 1
- [ ] Monitor error rates
- [ ] Watch first payments come in
- [ ] Collect user feedback
- [ ] Fix any critical issues

### Week 2-4
- [ ] Analyze usage patterns
- [ ] Optimize based on data
- [ ] Add more features if needed
- [ ] Scale if needed

### Month 2
- [ ] Enable discount/coupon system
- [ ] Add more plans if needed
- [ ] Implement admin dashboard
- [ ] Plan next features

---

## 📝 Deployment Summary

**What's Being Deployed**:
- Subscription system with 3 plans
- Usage tracking and limits
- Payment integration ready
- Dashboard and analytics
- Complete documentation

**Why It Matters**:
- Monetizes platform
- Improves user retention
- Provides feature access control
- Enables growth metrics

**Timeline**:
- Deployment: 1-2 hours
- Post-deployment testing: 30 mins
- Full verification: 1 day
- Monitor for issues: 1 week

**Support Level**:
- Critical: 24/7 (payment failures)
- High: 4 hours (user subscription issues)  
- Medium: 1 day (feature requests)
- Low: 1 week (documentation)

---

**Status**: ✅ Ready for Deployment

**Date**: January 6, 2026  
**Version**: 1.0  
**Deployment Manager**: [Your Name]  
**Approved By**: [Manager/Lead]

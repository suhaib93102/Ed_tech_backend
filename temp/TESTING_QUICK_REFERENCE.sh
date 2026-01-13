#!/bin/bash

# QUICK REFERENCE: How to Run and Test the Subscription System
# ============================================================================

echo "
╔════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║          SUBSCRIPTION SYSTEM - QUICK TESTING REFERENCE GUIDE           ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝

🚀 QUICK START
═════════════════════════════════════════════════════════════════════════

1. RUN THE SERVER
   $ python manage.py runserver

2. RUN ALL TESTS (14 tests, all passing)
   $ python test_subscription_complete.py

3. VERIFY PLANS ARE INITIALIZED
   $ python manage.py shell << EOF
   from question_solver.models import SubscriptionPlan
   for p in SubscriptionPlan.objects.all():
       print(f'{p.name}: ₹{p.first_month_price} → ₹{p.recurring_price}')
   EOF

4. TEST API ENDPOINT (after running server)
   $ curl -H 'Authorization: Bearer YOUR_TOKEN' \\
           http://localhost:8000/api/usage/dashboard/


📊 TEST RESULTS
═════════════════════════════════════════════════════════════════════════

Test File: test_subscription_complete.py
Total Tests: 14
Status: ALL PASSING ✅

Test Coverage:
  ✓ Subscription plan creation & retrieval
  ✓ User registration with FREE plan assignment
  ✓ Usage dashboard with correct limits
  ✓ Feature availability checking
  ✓ Usage recording & tracking
  ✓ Dashboard updates
  ✓ Plan upgrades (FREE → BASIC)
  ✓ Limit changes per plan
  ✓ Multiple usage recording
  ✓ Plan upgrades (BASIC → PREMIUM)
  ✓ Unlimited features verification
  ✓ Feature status retrieval
  ✓ Usage statistics
  ✓ Monthly usage reset


💰 PRICING VERIFIED
═════════════════════════════════════════════════════════════════════════

✓ FREE Plan: ₹0/month (3 uses per feature)
✓ BASIC Plan: ₹1 → ₹99/month (10-50 uses per feature)
✓ PREMIUM Plan: ₹199 → ₹499/month (UNLIMITED)


🔌 API ENDPOINTS READY
═════════════════════════════════════════════════════════════════════════

All 6 endpoints working with JWT authentication:

1. GET /api/usage/dashboard/
   → Complete usage dashboard with all features, limits, billing

2. GET /api/usage/feature/<feature_name>/
   → Specific feature status (allowed, limit, usage, remaining)

3. POST /api/usage/check/
   → Pre-check if feature available before use

4. POST /api/usage/record/
   → Record feature usage after successful completion

5. GET /api/usage/subscription/
   → User subscription status and billing info

6. GET /api/usage/stats/
   → Aggregated usage statistics


🧪 TO RUN TESTS
═════════════════════════════════════════════════════════════════════════

Run All Tests:
  $ cd /Users/vishaljha/Desktop/Government-welfare-Schemes/backend
  $ python test_subscription_complete.py

Expected Output:
  === TEST: Get All Subscription Plans ===
  ✓ Found 3 plans: FREE, BASIC, PREMIUM
  
  [... 12 more tests ...]
  
  ✓ ALL 14 TESTS PASSED
  SUCCESS! Complete subscription system working perfectly!

Run Specific Test:
  $ python -c \"
  import os, django
  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
  django.setup()
  from question_solver.models import SubscriptionPlan
  for p in SubscriptionPlan.objects.all():
      print(f'{p.name.upper()}: ₹{p.first_month_price}')
  \"


📋 MANUAL API TESTING WITH CURL
═════════════════════════════════════════════════════════════════════════

Step 1: Get a valid JWT token by registering a user:
  $ curl -X POST http://localhost:8000/api/auth/register/ \\
         -H 'Content-Type: application/json' \\
         -d '{
           \"username\": \"testuser\",
           \"email\": \"test@example.com\",
           \"password\": \"TestPass123!\"
         }'

Step 2: Get token from response, then test dashboard:
  $ curl -H 'Authorization: Bearer <YOUR_TOKEN>' \\
         http://localhost:8000/api/usage/dashboard/

Step 3: Check a specific feature:
  $ curl -H 'Authorization: Bearer <YOUR_TOKEN>' \\
         http://localhost:8000/api/usage/feature/quiz/

Step 4: Pre-check before using feature:
  $ curl -X POST http://localhost:8000/api/usage/check/ \\
         -H 'Authorization: Bearer <YOUR_TOKEN>' \\
         -H 'Content-Type: application/json' \\
         -d '{\"feature\": \"quiz\"}'

Step 5: Record usage after successful use:
  $ curl -X POST http://localhost:8000/api/usage/record/ \\
         -H 'Authorization: Bearer <YOUR_TOKEN>' \\
         -H 'Content-Type: application/json' \\
         -d '{
           \"feature\": \"quiz\",
           \"input_size\": 500,
           \"usage_type\": \"text\"
         }'


🔍 VERIFY DATABASE
═════════════════════════════════════════════════════════════════════════

Check subscription plans:
  $ python manage.py shell << EOF
  from question_solver.models import SubscriptionPlan
  for p in SubscriptionPlan.objects.all():
      print(f'{p.name}: quiz={p.quiz_limit}, mock_test={p.mock_test_limit}')
  EOF

Check user subscriptions:
  $ python manage.py shell << EOF
  from question_solver.models import UserSubscription
  for u in UserSubscription.objects.all():
      print(f'User {u.user_id}: {u.plan} plan, quiz_used={u.quiz_used}')
  EOF

Check feature usage logs:
  $ python manage.py shell << EOF
  from question_solver.models import FeatureUsageLog
  for log in FeatureUsageLog.objects.all()[:5]:
      print(f'{log.user_id}: {log.feature} - {log.usage_type}')
  EOF


✅ WHAT TO EXPECT
═════════════════════════════════════════════════════════════════════════

When you run test_subscription_complete.py:

✓ Test 1:  Get All Subscription Plans ......... Should find 3 plans
✓ Test 2:  Register User ..................... User created, FREE plan assigned
✓ Test 3:  FREE Plan Dashboard .............. Shows 3 uses per feature
✓ Test 4:  Check Feature Availability ........ Feature available (0/3)
✓ Test 5:  Record Feature Usage .............. Usage recorded (1/3)
✓ Test 6:  Verify Dashboard Updated .......... Shows 1/3 used
✓ Test 7:  Upgrade to BASIC ................. Plan changed to BASIC
✓ Test 8:  BASIC Plan Limits ................ Shows 20 for quiz
✓ Test 9:  Record Multiple Uses ............. Total 3 uses recorded
✓ Test 10: Upgrade to PREMIUM ............... Plan changed to PREMIUM
✓ Test 11: PREMIUM Unlimited ................ Limit shows None
✓ Test 12: Get Feature Status ............... PREMIUM shows unlimited
✓ Test 13: Get Usage Statistics ............. Stats retrieved
✓ Test 14: Monthly Reset .................... Reset verified

Final Result: ALL 14 TESTS PASSED ✅


🚨 TROUBLESHOOTING
═════════════════════════════════════════════════════════════════════════

Server not running:
  $ python manage.py runserver 0.0.0.0:8000

Migrations not applied:
  $ python manage.py migrate

Plans not initialized:
  $ python manage.py shell << EOF
  from question_solver.models import SubscriptionPlan
  SubscriptionPlan.objects.all().delete()
  SubscriptionPlan.initialize_default_plans()
  EOF

Tests failing with auth error:
  → Make sure to use Bearer token from registration response
  → Token must be valid JWT
  → Include Authorization header

Tests failing with database error:
  → Run migrations: python manage.py migrate
  → Initialize plans: python manage.py shell (run code above)


📚 DOCUMENTATION
═════════════════════════════════════════════════════════════════════════

Quick Overview:
  - SUBSCRIPTION_COMPLETE.md

Technical Reference:
  - SUBSCRIPTION_PLANS_GUIDE.md
  - README_SUBSCRIPTION_SYSTEM.md

API Examples:
  - SUBSCRIPTION_PLANS_CURL_REFERENCE.md

Visual Guides:
  - SUBSCRIPTION_PLANS_VISUAL.md

Deployment:
  - DEPLOYMENT_CHECKLIST.md

All Tests:
  - test_subscription_complete.py (14 tests)
  - test_subscription_plans.sh (bash version)


🎯 NEXT STEPS
═════════════════════════════════════════════════════════════════════════

1. ✓ All tests passing
2. → Integrate with your feature endpoints
3. → Deploy to production
4. → Start processing payments
5. → Monitor usage and billing


═════════════════════════════════════════════════════════════════════════

Questions? Check:
  - DOCUMENTATION_INDEX.md (navigation guide)
  - SUBSCRIPTION_IMPLEMENTATION_SUMMARY.md (technical details)
  - README_SUBSCRIPTION_SYSTEM.md (quick start)

═════════════════════════════════════════════════════════════════════════
"

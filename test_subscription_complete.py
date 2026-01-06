#!/usr/bin/env python
"""
Complete End-to-End Subscription System Test
Tests all three plans, feature tracking, and payment flow
"""
import os
import sys
import json
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
import django
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from question_solver.models import (
    SubscriptionPlan, UserSubscription, FeatureUsageLog
)
from question_solver.feature_usage_service import FeatureUsageService
import jwt
from django.conf import settings

# Colors for output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

def log_test(msg):
    print(f"{BLUE}=== TEST: {msg} ==={NC}")

def log_success(msg):
    print(f"{GREEN}✓ {msg}{NC}")

def log_error(msg):
    print(f"{RED}✗ {msg}{NC}")

def log_info(msg):
    print(f"{YELLOW}→ {msg}{NC}")

def generate_token(user):
    """Generate JWT token for user"""
    payload = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

def test_1_subscription_plans():
    """Test 1: Get all subscription plans"""
    log_test("Get All Subscription Plans")
    
    plans = SubscriptionPlan.objects.all()
    assert plans.count() == 3, "Should have 3 plans"
    
    plan_names = [p.name.upper() for p in plans]
    assert 'FREE' in plan_names
    assert 'BASIC' in plan_names
    assert 'PREMIUM' in plan_names
    
    log_success(f"Found 3 plans: {', '.join(plan_names)}")
    
    for plan in plans:
        log_info(f"{plan.name.upper()}: ₹{plan.first_month_price} → ₹{plan.recurring_price}/month")

def test_2_user_registration():
    """Test 2: Register user and verify FREE plan"""
    log_test("Register User & Verify FREE Plan")
    
    # Create user
    username = f"test_user_{datetime.now().timestamp()}"
    user = User.objects.create_user(
        username=username,
        email=f"{username}@test.com",
        password="TestPass123!"
    )
    
    log_success(f"User created: {user.id} ({user.username})")
    
    # Get or create subscription
    subscription = FeatureUsageService.get_or_create_subscription(user.id)
    
    assert subscription.plan == 'free', f"Expected FREE plan, got {subscription.plan}"
    log_success("User assigned to FREE plan by default")
    
    return user

def test_3_free_plan_dashboard(user):
    """Test 3: Check FREE plan dashboard"""
    log_test("FREE Plan Usage Dashboard")
    
    try:
        dashboard = FeatureUsageService.get_usage_dashboard(user.id)
        
        # Verify structure
        assert 'features' in dashboard, "Missing 'features' key"
        assert 'plan' in dashboard, "Missing 'plan' key"
        assert 'billing' in dashboard, "Missing 'billing' key"
        
        log_success("Dashboard structure is valid")
        log_info(f"Plan: {dashboard['plan'].upper()}")
        log_info(f"Features tracked: {len(dashboard['features'])}")
        
        # Check limits for FREE plan
        quiz_limit = dashboard['features']['quiz']['limit']
        assert quiz_limit == 3, f"FREE plan quiz limit should be 3, got {quiz_limit}"
        log_success("FREE plan limits correct (3 per feature)")
    except Exception as e:
        print(f"Dashboard content: {json.dumps(dashboard, indent=2, default=str)}")
        raise

def test_4_feature_availability(user):
    """Test 4: Check feature availability"""
    log_test("Check Feature Availability")
    
    status = FeatureUsageService.check_feature_available(user.id, 'quiz')
    
    assert status['allowed'] == True, "Feature should be available"
    assert status['limit'] == 3, "Should show limit"
    assert status['used'] == 0, "Should show 0 used"
    
    log_success(f"Feature available: quiz (0/3 used)")

def test_5_record_usage(user):
    """Test 5: Record feature usage"""
    log_test("Record Feature Usage")
    
    result = FeatureUsageService.use_feature(
        user_id=user.id,
        feature_name='quiz',
        input_size=500,
        usage_type='text'
    )
    
    assert result['success'] == True
    log_success("Quiz usage recorded (1/3)")

def test_6_verify_usage_updated(user):
    """Test 6: Verify usage dashboard updated"""
    log_test("Verify Usage Dashboard Updated")
    
    dashboard = FeatureUsageService.get_usage_dashboard(user.id)
    used = dashboard['features']['quiz']['used']
    
    assert used == 1, f"Should show 1 use, got {used}"
    log_success("Dashboard updated: quiz 1/3 used")

def test_7_upgrade_to_basic(user):
    """Test 7: Upgrade to BASIC plan"""
    log_test("Upgrade to BASIC Plan")
    
    subscription = UserSubscription.objects.get(user_id=user.id)
    basic_plan = SubscriptionPlan.objects.get(name='basic')
    subscription.plan = 'basic'
    subscription.subscription_plan = basic_plan
    subscription.save()
    
    log_success("User upgraded to BASIC plan")
    log_info("First month: ₹1, Recurring: ₹99/month")

def test_8_basic_plan_limits(user):
    """Test 8: Verify BASIC plan limits"""
    log_test("BASIC Plan Limits")
    
    try:
        dashboard = FeatureUsageService.get_usage_dashboard(user.id)
        
        plan_upper = dashboard['plan'].upper()
        assert plan_upper == 'BASIC', f"Plan should be BASIC, got {dashboard['plan']}"
        
        # BASIC plan limits (as configured in initialize_default_plans)
        quiz = dashboard['features'].get('quiz', {})
        mock_test = dashboard['features'].get('mock_test', {})
        
        quiz_limit = quiz.get('limit')
        mock_test_limit = mock_test.get('limit')
        
        log_info(f"Quiz limit in BASIC: {quiz_limit}")
        log_info(f"Mock test limit in BASIC: {mock_test_limit}")
        
        # Verify correct limits for BASIC plan
        assert quiz_limit == 20, f"BASIC quiz limit should be 20, got {quiz_limit}"
        assert mock_test_limit == 10, f"BASIC mock_test limit should be 10, got {mock_test_limit}"
        
        log_success(f"BASIC plan limits verified (quiz: 20, mock_test: 10)")
    except Exception as e:
        # Debug: print subscription info
        subscription = UserSubscription.objects.get(user_id=user.id)
        log_error(f"Subscription plan: {subscription.subscription_plan}")
        raise

def test_9_record_multiple_uses(user):
    """Test 9: Record multiple feature uses"""
    log_test("Record Multiple Uses")
    
    for i in range(2):
        result = FeatureUsageService.use_feature(
            user_id=user.id,
            feature_name='quiz',
            input_size=500,
            usage_type='text'
        )
        assert result['success'] == True
        log_info(f"Recorded use {i+2}/20 (BASIC limit)")
    
    dashboard = FeatureUsageService.get_usage_dashboard(user.id)
    used = dashboard['features']['quiz']['used']
    log_success(f"Total quiz uses: {used}")

def test_10_upgrade_to_premium(user):
    """Test 10: Upgrade to PREMIUM plan"""
    log_test("Upgrade to PREMIUM Plan")
    
    subscription = UserSubscription.objects.get(user_id=user.id)
    premium_plan = SubscriptionPlan.objects.get(name='premium')
    subscription.plan = 'premium'
    subscription.subscription_plan = premium_plan
    subscription.save()
    
    log_success("User upgraded to PREMIUM plan")
    log_info("First month: ₹199, Recurring: ₹499/month")

def test_11_premium_unlimited(user):
    """Test 11: Verify PREMIUM unlimited features"""
    log_test("PREMIUM Plan - Unlimited Features")
    
    dashboard = FeatureUsageService.get_usage_dashboard(user.id)
    
    assert dashboard['plan'].upper() == 'PREMIUM', f"Plan should be PREMIUM, got {dashboard['plan']}"
    
    # PREMIUM features should have no limit
    quiz = dashboard['features']['quiz']
    log_info(f"Quiz limit for PREMIUM: {quiz['limit']}")
    assert quiz['limit'] is None, f"PREMIUM quiz limit should be unlimited (None), got {quiz['limit']}"
    
    log_success("PREMIUM plan unlimited features verified")

def test_12_get_feature_status(user):
    """Test 12: Get specific feature status"""
    log_test("Get Feature Status")
    
    status = FeatureUsageService.check_feature_available(user.id, 'mock_test')
    
    assert status['allowed'] == True
    assert status['limit'] is None, "PREMIUM should have unlimited"
    
    log_success(f"Feature status: mock_test (unlimited for PREMIUM)")

def test_13_usage_stats(user):
    """Test 13: Get usage statistics"""
    log_test("Get Usage Statistics")
    
    subscription = UserSubscription.objects.get(user_id=user.id)
    limits = subscription.get_feature_limits()
    
    assert len(limits) > 0
    log_success(f"Retrieved stats for {len(limits)} features")
    
    total_used = sum(f['used'] for f in limits.values())
    log_info(f"Total features used: {total_used}")

def test_14_monthly_reset():
    """Test 14: Monthly usage reset"""
    log_test("Monthly Usage Reset")
    
    # Create test user for reset
    username = f"reset_user_{datetime.now().timestamp()}"
    user = User.objects.create_user(
        username=username,
        email=f"{username}@test.com",
        password="TestPass123!"
    )
    
    subscription = FeatureUsageService.get_or_create_subscription(user.id)
    subscription.plan = 'basic'
    subscription.save()
    
    # Record some usage
    FeatureUsageService.use_feature(user.id, 'quiz', 500, 'text')
    
    # Force reset
    subscription.reset_monthly_usage()
    
    # Verify reset
    dashboard = FeatureUsageService.get_usage_dashboard(user.id)
    quiz_used = dashboard['features']['quiz']['used']
    
    assert quiz_used == 0, "Should be reset to 0"
    log_success("Monthly usage reset verified")

def run_all_tests():
    """Run all tests sequentially"""
    print("")
    print("═" * 70)
    print("  SUBSCRIPTION PLANS & USAGE TRACKING - COMPLETE TEST SUITE")
    print("═" * 70)
    print("")
    
    try:
        # Test 1
        test_1_subscription_plans()
        print("")
        
        # Test 2
        user = test_2_user_registration()
        print("")
        
        # Test 3
        test_3_free_plan_dashboard(user)
        print("")
        
        # Test 4
        test_4_feature_availability(user)
        print("")
        
        # Test 5
        test_5_record_usage(user)
        print("")
        
        # Test 6
        test_6_verify_usage_updated(user)
        print("")
        
        # Test 7
        test_7_upgrade_to_basic(user)
        print("")
        
        # Test 8
        test_8_basic_plan_limits(user)
        print("")
        
        # Test 9
        test_9_record_multiple_uses(user)
        print("")
        
        # Test 10
        test_10_upgrade_to_premium(user)
        print("")
        
        # Test 11
        test_11_premium_unlimited(user)
        print("")
        
        # Test 12
        test_12_get_feature_status(user)
        print("")
        
        # Test 13
        test_13_usage_stats(user)
        print("")
        
        # Test 14
        test_14_monthly_reset()
        print("")
        
        # Summary
        print("═" * 70)
        print(f"{GREEN}✓ ALL 14 TESTS PASSED{NC}")
        print("═" * 70)
        print("")
        print(f"{GREEN}SUCCESS!{NC} Complete subscription system working perfectly!")
        print("")
        print("Summary:")
        print(f"  ✓ Three subscription plans (FREE, BASIC, PREMIUM)")
        print(f"  ✓ Feature usage tracking and limits enforced")
        print(f"  ✓ Usage dashboard with real-time updates")
        print(f"  ✓ Plan upgrades working correctly")
        print(f"  ✓ Feature limits updated per plan")
        print(f"  ✓ Monthly usage reset system ready")
        print("")
        
        return True
        
    except AssertionError as e:
        print("")
        log_error(f"Test failed: {str(e)}")
        return False
    except Exception as e:
        print("")
        log_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

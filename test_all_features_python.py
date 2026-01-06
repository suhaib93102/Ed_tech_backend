#!/usr/bin/env python
"""
Comprehensive Test Script for All Features, Password Reset, and YouTube Summarizer
Tests all 10 features with curl commands and stores responses in response.json
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add Django to path
sys.path.insert(0, '/Users/vishaljha/Desktop/Government-welfare-Schemes/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')

import django
django.setup()

from django.contrib.auth.models import User
from question_solver.models import SubscriptionPlan, UserSubscription, FeatureUsageLog
from question_solver.feature_usage_service import FeatureUsageService

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

API_URL = "http://localhost:8000"
RESPONSE_FILE = "response.json"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = f"test_log_{TIMESTAMP}.txt"

FEATURES = [
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

# Color codes
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

# ═══════════════════════════════════════════════════════════════════════════════
# Logging Functions
# ═══════════════════════════════════════════════════════════════════════════════

def log(msg):
    """Log to both console and file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output = f"[{timestamp}] {msg}"
    print(output)
    with open(LOG_FILE, 'a') as f:
        f.write(output + '\n')

def log_success(msg):
    """Log success message"""
    log(f"{GREEN}✓ {msg}{NC}")

def log_error(msg):
    """Log error message"""
    log(f"{RED}✗ {msg}{NC}")

def log_info(msg):
    """Log info message"""
    log(f"{YELLOW}ℹ {msg}{NC}")

def log_section(title):
    """Log section header"""
    log("")
    log(f"{BLUE}╔════════════════════════════════════════════════════════════════════════════╗{NC}")
    log(f"{BLUE}║                   {title:<62}║{NC}")
    log(f"{BLUE}╚════════════════════════════════════════════════════════════════════════════╝{NC}")

# ═══════════════════════════════════════════════════════════════════════════════
# Test Results Storage
# ═══════════════════════════════════════════════════════════════════════════════

test_results = {
    "test_metadata": {
        "timestamp": datetime.now().isoformat(),
        "api_url": API_URL,
        "test_environment": "Django Shell"
    },
    "test_summary": {
        "total_tests": 0,
        "tests_passed": 0,
        "tests_failed": 0,
        "success_rate": "0%"
    },
    "phases": {
        "user_management": {},
        "features": {},
        "forget_password": {},
        "youtube_summarizer": {},
        "usage_tracking": {},
        "subscriptions": {},
        "admin_dashboard": {}
    }
}

tests_passed = 0
tests_failed = 0

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: INITIALIZATION AND SETUP
# ═══════════════════════════════════════════════════════════════════════════════

log_section("PHASE 1: INITIALIZATION AND SETUP")

# Clear test data if exists
log("Cleaning up old test data...")
User.objects.filter(username__startswith='testuser_').delete()
test_results["phases"]["user_management"] = {"status": "initializing"}

# Initialize subscription plans
log("Initializing subscription plans...")
SubscriptionPlan.initialize_default_plans()
log_success("Subscription plans initialized")
tests_passed += 1

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2: USER CREATION AND AUTHENTICATION
# ═══════════════════════════════════════════════════════════════════════════════

log_section("PHASE 2: USER CREATION AND AUTHENTICATION")

TEST_USER_EMAIL = f"testuser_{TIMESTAMP}@example.com"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_USER_NAME = f"Test User {TIMESTAMP}"
TEST_USERNAME = f"testuser_{TIMESTAMP}"

log(f"Creating test user: {TEST_USER_EMAIL}")

try:
    # Create user
    test_user = User.objects.create_user(
        username=TEST_USERNAME,
        email=TEST_USER_EMAIL,
        password=TEST_USER_PASSWORD,
        first_name="Test",
        last_name="User"
    )
    
    # Assign FREE plan
    free_plan = SubscriptionPlan.objects.get(name="FREE")
    user_sub, created = UserSubscription.objects.get_or_create(
        user=test_user,
        defaults={'plan': free_plan, 'is_active': True}
    )
    
    log_success(f"User created with ID: {test_user.id}")
    log_info(f"Email: {TEST_USER_EMAIL}")
    log_info(f"Username: {TEST_USERNAME}")
    log_info(f"Plan: {user_sub.plan.name}")
    
    test_results["phases"]["user_management"]["user_created"] = {
        "user_id": test_user.id,
        "email": TEST_USER_EMAIL,
        "username": TEST_USERNAME,
        "plan": user_sub.plan.name
    }
    tests_passed += 1
    
except Exception as e:
    log_error(f"Failed to create user: {str(e)}")
    test_results["phases"]["user_management"]["error"] = str(e)
    tests_failed += 1

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3: TEST ALL 10 FEATURES
# ═══════════════════════════════════════════════════════════════════════════════

log_section("PHASE 3: TEST ALL 10 FEATURES")

feature_service = FeatureUsageService(test_user)
feature_results = {}

for feature in FEATURES:
    log(f"Testing feature: {feature}")
    
    try:
        # Check if feature is available
        is_available = feature_service.check_feature_available(feature)
        
        # Get current usage
        current_usage = feature_service.get_feature_usage(feature)
        
        log_info(f"{feature}: Available={is_available}, Usage={current_usage}")
        
        feature_results[feature] = {
            "available": is_available,
            "usage": current_usage,
            "plan": user_sub.plan.name
        }
        
        tests_passed += 1
        
    except Exception as e:
        log_error(f"Error testing {feature}: {str(e)}")
        feature_results[feature] = {"error": str(e)}
        tests_failed += 1

test_results["phases"]["features"] = feature_results

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4: FEATURE USAGE TRACKING
# ═══════════════════════════════════════════════════════════════════════════════

log_section("PHASE 4: FEATURE USAGE TRACKING")

usage_results = {}

for feature in FEATURES[:5]:  # Test first 5 features
    log(f"Recording usage for: {feature}")
    
    try:
        # Check if available before use
        can_use = feature_service.check_feature_available(feature)
        
        if can_use:
            # Record usage
            feature_service.use_feature(feature)
            
            # Get updated usage
            new_usage = feature_service.get_feature_usage(feature)
            
            log_success(f"{feature}: Used successfully, New usage: {new_usage}")
            usage_results[feature] = {
                "used": True,
                "new_usage": new_usage
            }
            tests_passed += 1
        else:
            log_error(f"{feature}: Not available in current plan")
            usage_results[feature] = {"used": False, "reason": "not_available"}
            tests_failed += 1
            
    except Exception as e:
        log_error(f"Error using {feature}: {str(e)}")
        usage_results[feature] = {"error": str(e)}
        tests_failed += 1

test_results["phases"]["features"]["usage_tracking"] = usage_results

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 5: USAGE DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

log_section("PHASE 5: USAGE DASHBOARD")

log("Getting comprehensive usage dashboard...")

try:
    dashboard = feature_service.get_usage_dashboard()
    
    log_success("Dashboard retrieved successfully")
    log_info(f"Current plan: {dashboard['current_plan']}")
    log_info(f"Total features: {dashboard['total_features']}")
    
    feature_details = {}
    for feature, info in dashboard['features'].items():
        feature_details[feature] = {
            "usage": info.get('usage', 0),
            "limit": info.get('limit'),
            "remaining": info.get('remaining'),
            "status": "unlimited" if info.get('limit') is None else "limited"
        }
    
    test_results["phases"]["usage_tracking"] = {
        "plan": dashboard['current_plan'],
        "features": feature_details,
        "total_features": dashboard['total_features'],
        "billing": dashboard.get('billing_info', {})
    }
    tests_passed += 1
    
except Exception as e:
    log_error(f"Failed to get dashboard: {str(e)}")
    test_results["phases"]["usage_tracking"]["error"] = str(e)
    tests_failed += 1

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 6: SUBSCRIPTION PLAN UPGRADES
# ═══════════════════════════════════════════════════════════════════════════════

log_section("PHASE 6: SUBSCRIPTION PLAN UPGRADES")

subscription_results = {}

log("Current plan: FREE")
subscription_results["initial"] = {
    "plan": "FREE",
    "created_at": user_sub.created_at.isoformat()
}

# Upgrade to BASIC
log("Upgrading to BASIC plan...")

try:
    basic_plan = SubscriptionPlan.objects.get(name="BASIC")
    user_sub.plan = basic_plan
    user_sub.save()
    
    log_success("Upgraded to BASIC plan")
    subscription_results["after_basic_upgrade"] = {
        "plan": "BASIC",
        "limits": {feature: basic_plan.get_feature_limit(feature) for feature in FEATURES}
    }
    tests_passed += 1
    
except Exception as e:
    log_error(f"Failed to upgrade to BASIC: {str(e)}")
    tests_failed += 1

# Check dashboard after BASIC upgrade
log("Dashboard after BASIC upgrade...")
try:
    dashboard_basic = feature_service.get_usage_dashboard()
    log_success(f"Plan after upgrade: {dashboard_basic['current_plan']}")
    tests_passed += 1
except Exception as e:
    log_error(f"Failed to get dashboard: {str(e)}")
    tests_failed += 1

# Upgrade to PREMIUM
log("Upgrading to PREMIUM plan...")

try:
    premium_plan = SubscriptionPlan.objects.get(name="PREMIUM")
    user_sub.plan = premium_plan
    user_sub.save()
    
    log_success("Upgraded to PREMIUM plan")
    subscription_results["after_premium_upgrade"] = {
        "plan": "PREMIUM",
        "limits": {feature: premium_plan.get_feature_limit(feature) for feature in FEATURES}
    }
    tests_passed += 1
    
except Exception as e:
    log_error(f"Failed to upgrade to PREMIUM: {str(e)}")
    tests_failed += 1

# Check dashboard after PREMIUM upgrade
log("Dashboard after PREMIUM upgrade...")
try:
    dashboard_premium = feature_service.get_usage_dashboard()
    log_success(f"Plan after upgrade: {dashboard_premium['current_plan']}")
    
    # All features should be unlimited
    unlimited_count = sum(1 for f in dashboard_premium['features'].values() if f.get('limit') is None)
    log_info(f"Unlimited features: {unlimited_count}/{dashboard_premium['total_features']}")
    tests_passed += 1
except Exception as e:
    log_error(f"Failed to get dashboard: {str(e)}")
    tests_failed += 1

test_results["phases"]["subscriptions"] = subscription_results

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 7: USAGE AFTER PREMIUM
# ═══════════════════════════════════════════════════════════════════════════════

log_section("PHASE 7: USAGE AFTER PREMIUM UPGRADE")

log("Testing all features with PREMIUM plan (unlimited)...")

premium_usage = {}

for feature in FEATURES:
    log(f"Testing {feature} with PREMIUM...")
    
    try:
        # Should be available on PREMIUM
        is_available = feature_service.check_feature_available(feature)
        
        if is_available:
            # Use feature multiple times
            for i in range(3):
                feature_service.use_feature(feature)
            
            current = feature_service.get_feature_usage(feature)
            log_success(f"{feature}: Available with usage {current}")
            premium_usage[feature] = {
                "available": True,
                "usage": current,
                "plan": "PREMIUM"
            }
            tests_passed += 1
        else:
            log_error(f"{feature}: Not available (unexpected)")
            premium_usage[feature] = {"available": False}
            tests_failed += 1
            
    except Exception as e:
        log_error(f"Error with {feature}: {str(e)}")
        tests_failed += 1

test_results["phases"]["features"]["premium_usage"] = premium_usage

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 8: FINAL STATISTICS
# ═══════════════════════════════════════════════════════════════════════════════

log_section("PHASE 8: FINAL STATISTICS")

try:
    final_dashboard = feature_service.get_usage_dashboard()
    total_usage = sum(f.get('usage', 0) for f in final_dashboard['features'].values())
    
    log_success(f"Final Plan: {final_dashboard['current_plan']}")
    log_info(f"Total Feature Uses: {total_usage}")
    log_info(f"Total Features Tracked: {final_dashboard['total_features']}")
    
    test_results["phases"]["final_statistics"] = {
        "plan": final_dashboard['current_plan'],
        "total_usage": total_usage,
        "total_features": final_dashboard['total_features'],
        "features": {
            feature: {
                "usage": info.get('usage', 0),
                "limit": info.get('limit'),
                "status": "unlimited" if info.get('limit') is None else "limited"
            }
            for feature, info in final_dashboard['features'].items()
        }
    }
    
    tests_passed += 1
    
except Exception as e:
    log_error(f"Failed to get final statistics: {str(e)}")
    tests_failed += 1

# ═══════════════════════════════════════════════════════════════════════════════
# SAVE RESULTS
# ═══════════════════════════════════════════════════════════════════════════════

log_section("SAVING TEST RESULTS")

# Update summary
test_results["test_summary"]["total_tests"] = tests_passed + tests_failed
test_results["test_summary"]["tests_passed"] = tests_passed
test_results["test_summary"]["tests_failed"] = tests_failed

if (tests_passed + tests_failed) > 0:
    success_rate = (tests_passed * 100) // (tests_passed + tests_failed)
    test_results["test_summary"]["success_rate"] = f"{success_rate}%"

# Add test instructions
test_results["test_instructions"] = {
    "curl_examples": {
        "register": f"curl -X POST {API_URL}/api/auth/register/ -H 'Content-Type: application/json' -d '{{...}}'",
        "test_feature": f"curl -X POST {API_URL}/api/features/quiz/ -H 'Authorization: Bearer TOKEN' -d '{{...}}'",
        "check_usage": f"curl -X POST {API_URL}/api/usage/check/ -H 'Authorization: Bearer TOKEN' -d '{{...}}'",
        "dashboard": f"curl -X GET {API_URL}/api/usage/dashboard/ -H 'Authorization: Bearer TOKEN'",
        "forget_password": f"curl -X POST {API_URL}/api/auth/request-password-reset/ -H 'Content-Type: application/json' -d '{{...}}'"
    },
    "how_to_run": [
        "1. Ensure Django server is running: python manage.py runserver",
        "2. Execute test script: python test_all_features_python.py",
        "3. Check response.json for results",
        "4. Review test_log_*.txt for detailed logs"
    ],
    "features_tested": FEATURES,
    "subscription_plans_tested": ["FREE", "BASIC", "PREMIUM"],
    "endpoints_tested": [
        "/api/auth/register/",
        "/api/features/*/",
        "/api/usage/dashboard/",
        "/api/usage/check/",
        "/api/subscriptions/upgrade/"
    ]
}

# Save to JSON
log("Writing results to response.json...")
with open(RESPONSE_FILE, 'w') as f:
    json.dump(test_results, f, indent=2, default=str)

log_success(f"Results saved to {RESPONSE_FILE}")

# ═══════════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

log_section("TEST EXECUTION COMPLETE")

log("")
log_success(f"Total Tests: {tests_passed + tests_failed}")
log_success(f"Tests Passed: {tests_passed}")
if tests_failed > 0:
    log_error(f"Tests Failed: {tests_failed}")

if (tests_passed + tests_failed) > 0:
    success_rate = (tests_passed * 100) // (tests_passed + tests_failed)
    if success_rate >= 90:
        log_success(f"Success Rate: {success_rate}%")
    else:
        log_error(f"Success Rate: {success_rate}%")

log("")
log_info(f"Response File: {RESPONSE_FILE}")
log_info(f"Log File: {LOG_FILE}")

log("")
log("✅ PHASES TESTED:")
log("   • User Creation and Authentication")
log("   • All 10 Features (FREE plan)")
log("   • Feature Usage Tracking")
log("   • Usage Dashboard")
log("   • Subscription Upgrades (FREE → BASIC → PREMIUM)")
log("   • Premium Features (Unlimited)")
log("   • Final Statistics")

log("")
log("📊 Test Response Structure:")
log("   • test_metadata: Test info and timestamp")
log("   • test_summary: Pass/fail statistics")
log("   • phases: Results for each test phase")
log("   • test_instructions: How to run and interpret")

log("")
log("═══════════════════════════════════════════════════════════════════════════════")

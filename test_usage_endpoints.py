#!/usr/bin/env python3
"""
Test script for Usage Tracking and Feature Restriction Endpoints
Tests real-time usage tracking, restrictions, and enforcement
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api"

# Test user ID for authentication
TEST_USER_ID = "test_user_123"

HEADERS = {
    'Content-Type': 'application/json',
    'User-Agent': 'UsageTest/1.0',
    'X-User-ID': TEST_USER_ID  # Add user ID header for authentication
}

def log(message, level="INFO"):
    """Simple logging function"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def test_real_time_usage():
    """Test real-time usage endpoint"""
    log("Testing Real-Time Usage Endpoint (/api/usage/real-time/)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/usage/real-time/",
            headers=HEADERS,
            timeout=10
        )
        
        log(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            log("✅ Real-time usage retrieved successfully")
            
            if 'feature_usage' in data:
                log(f"Plan: {data.get('plan')}")
                log(f"Subscription Status: {data.get('subscription_status')}")
                log(f"Features Tracked: {data.get('summary', {}).get('total_features')}")
                log(f"Features Available: {data.get('summary', {}).get('features_available')}")
                log(f"Features Exhausted: {data.get('summary', {}).get('features_exhausted')}")
            
            return data
        else:
            log(f"❌ Failed: {response.text}")
            return None
    
    except Exception as e:
        log(f"❌ Exception: {e}")
        return None

def test_usage_history():
    """Test usage history endpoint"""
    log("\nTesting Usage History Endpoint (/api/usage/history/)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/usage/history/?days=7",
            headers=HEADERS,
            timeout=10
        )
        
        log(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            log("✅ Usage history retrieved successfully")
            log(f"Query Period: {data.get('query_period_days')} days")
            log(f"Total Entries: {data.get('total_entries')}")
            
            if data.get('history'):
                for feature, logs in list(data.get('history', {}).items())[:3]:
                    log(f"  {feature}: {len(logs)} entries")
            
            return data
        else:
            log(f"❌ Failed: {response.text}")
            return None
    
    except Exception as e:
        log(f"❌ Exception: {e}")
        return None

def test_feature_restriction(feature_name="quiz"):
    """Test feature restriction endpoint"""
    log(f"\nTesting Feature Restriction Details (/api/usage/restriction/{feature_name}/)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/usage/restriction/{feature_name}/",
            headers=HEADERS,
            timeout=10
        )
        
        log(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            log("✅ Restriction details retrieved successfully")
            
            details = data.get('restriction_details', {})
            log(f"Feature: {details.get('feature_display_name')}")
            log(f"Allowed: {details.get('allowed')}")
            log(f"Plan: {details.get('plan')}")
            
            if 'usage' in details:
                log(f"Usage: {details.get('usage')}/{details.get('limit')}")
                log(f"Remaining: {details.get('remaining')}")
                log(f"Percentage Used: {details.get('percentage_used')}%")
            elif details.get('unlimited'):
                log("Usage: Unlimited")
            
            return data
        else:
            log(f"❌ Failed: {response.text}")
            return None
    
    except Exception as e:
        log(f"❌ Exception: {e}")
        return None

def test_restriction_enforcement(feature_name="quiz"):
    """Test enforcement check endpoint"""
    log(f"\nTesting Enforcement Check (/api/usage/enforce-check/)")
    
    payload = {
        "feature": feature_name
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/usage/enforce-check/",
            json=payload,
            headers=HEADERS,
            timeout=10
        )
        
        log(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 403]:
            data = response.json()
            
            if response.status_code == 200:
                log(f"✅ Feature access ALLOWED for {feature_name}")
                log(f"Remaining uses: {data.get('remaining')}")
            else:
                log(f"❌ Feature access DENIED for {feature_name}")
                log(f"Reason: {data.get('error')}")
            
            return data
        else:
            log(f"❌ Unexpected status: {response.text}")
            return None
    
    except Exception as e:
        log(f"❌ Exception: {e}")
        return None

def test_all_features():
    """Test all features for restrictions"""
    log("\nTesting All Features Restrictions (/api/usage/test/all-features/)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/usage/test/all-features/",
            headers=HEADERS,
            timeout=10
        )
        
        log(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            log("✅ All features tested successfully")
            
            summary = data.get('test_results', {}).get('summary', {})
            log(f"Total Features: {summary.get('total_features')}")
            log(f"Features Available: {summary.get('features_available')}")
            log(f"Features Restricted: {summary.get('features_restricted')}")
            log(f"Features Unlimited: {summary.get('features_unlimited')}")
            
            # Show restricted features
            features = data.get('test_results', {}).get('features_tested', {})
            restricted = [f for f, info in features.items() if not info.get('allowed')]
            
            if restricted:
                log(f"⚠️  Restricted Features: {', '.join(restricted)}")
            
            return data
        else:
            log(f"❌ Failed: {response.text}")
            return None
    
    except Exception as e:
        log(f"❌ Exception: {e}")
        return None

def test_restriction_simulation(feature_name="quiz"):
    """Test feature restriction with simulation"""
    log(f"\nTesting Restriction Simulation for {feature_name}")
    
    payload = {
        "feature": feature_name,
        "simulate_quota_exhausted": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/usage/test/restriction/",
            json=payload,
            headers=HEADERS,
            timeout=10
        )
        
        log(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            log("✅ Restriction simulation successful")
            
            test_type = data.get('test_type')
            current = data.get('current_usage', {})
            
            log(f"Test Type: {test_type}")
            log(f"Usage: {current.get('used')}/{current.get('limit')}")
            log(f"Would Be Allowed: {data.get('would_be_allowed')}")
            
            return data
        else:
            log(f"❌ Failed: {response.text}")
            return None
    
    except Exception as e:
        log(f"❌ Exception: {e}")
        return None

def test_check_before_usage(feature_name="quiz"):
    """Test checking feature before making actual request"""
    log(f"\nTesting Feature Check Before Usage ({feature_name})")
    
    payload = {
        "feature": feature_name
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/usage/check/",
            json=payload,
            headers=HEADERS,
            timeout=10
        )
        
        log(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 403]:
            data = response.json()
            
            if response.status_code == 200:
                log(f"✅ {feature_name} is available for use")
            else:
                log(f"❌ {feature_name} is NOT available")
                log(f"Reason: {data.get('error')}")
                if 'status' in data:
                    log(f"Details: {data.get('status')}")
            
            return data
        else:
            log(f"❌ Unexpected status: {response.text}")
            return None
    
    except Exception as e:
        log(f"❌ Exception: {e}")
        return None

def test_record_usage(feature_name="quiz"):
    """Test recording feature usage"""
    log(f"\nTesting Record Usage ({feature_name})")
    
    payload = {
        "feature": feature_name,
        "input_size": 1000,
        "usage_type": "test"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/usage/record/",
            json=payload,
            headers=HEADERS,
            timeout=10
        )
        
        log(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            log(f"✅ Usage recorded successfully")
            log(f"Success: {data.get('success')}")
            
            return data
        else:
            log(f"❌ Failed: {response.text}")
            return None
    
    except Exception as e:
        log(f"❌ Exception: {e}")
        return None

def main():
    """Run all usage endpoint tests"""
    log("=" * 80)
    log("USAGE TRACKING & FEATURE RESTRICTION TESTS")
    log("=" * 80)
    
    results = {
        'real_time_usage': False,
        'usage_history': False,
        'feature_restriction': False,
        'enforcement_check': False,
        'all_features_test': False,
        'restriction_simulation': False,
        'check_before_usage': False,
        'record_usage': False,
    }
    
    # Test 1: Real-time usage
    log("\n" + "=" * 80)
    log("TEST 1: REAL-TIME USAGE TRACKING")
    log("=" * 80)
    rt_data = test_real_time_usage()
    results['real_time_usage'] = rt_data is not None
    
    # Test 2: Usage history
    log("\n" + "=" * 80)
    log("TEST 2: USAGE HISTORY")
    log("=" * 80)
    hist_data = test_usage_history()
    results['usage_history'] = hist_data is not None
    
    # Test 3: Feature restriction details
    log("\n" + "=" * 80)
    log("TEST 3: FEATURE RESTRICTION DETAILS")
    log("=" * 80)
    rest_data = test_feature_restriction("quiz")
    results['feature_restriction'] = rest_data is not None
    
    # Test 4: Enforcement check
    log("\n" + "=" * 80)
    log("TEST 4: ENFORCEMENT CHECK")
    log("=" * 80)
    enf_data = test_restriction_enforcement("quiz")
    results['enforcement_check'] = enf_data is not None
    
    # Test 5: All features test
    log("\n" + "=" * 80)
    log("TEST 5: ALL FEATURES RESTRICTIONS")
    log("=" * 80)
    all_data = test_all_features()
    results['all_features_test'] = all_data is not None
    
    # Test 6: Restriction simulation
    log("\n" + "=" * 80)
    log("TEST 6: RESTRICTION SIMULATION")
    log("=" * 80)
    sim_data = test_restriction_simulation("quiz")
    results['restriction_simulation'] = sim_data is not None
    
    # Test 7: Check before usage
    log("\n" + "=" * 80)
    log("TEST 7: CHECK FEATURE BEFORE USAGE")
    log("=" * 80)
    check_data = test_check_before_usage("quiz")
    results['check_before_usage'] = check_data is not None
    
    # Test 8: Record usage
    log("\n" + "=" * 80)
    log("TEST 8: RECORD USAGE")
    log("=" * 80)
    record_data = test_record_usage("quiz")
    results['record_usage'] = record_data is not None
    
    # Summary
    log("\n" + "=" * 80)
    log("TEST SUMMARY")
    log("=" * 80)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        log(f"{test_name}: {status}")
    
    log(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        log("🎉 All usage tracking endpoints are working correctly!")
    else:
        log("⚠️  Some tests failed. Check the logs above for details.")
    
    return results

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Test interrupted by user")
    except Exception as e:
        log(f"Unexpected error: {e}")

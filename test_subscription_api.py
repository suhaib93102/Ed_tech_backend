"""
Test script for Razorpay Subscription API
Tests all endpoints without actual payment
"""
import requests
import json

BASE_URL = "http://localhost:8003/api"

def test_get_plans():
    """Test getting available plans"""
    print("\n=== Testing: Get Plans ===")
    response = requests.get(f"{BASE_URL}/subscriptions/plans/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✓ Plans retrieved successfully")
            for plan in data.get('plans', []):
                print(f"  - {plan['display_name']}: ₹{plan['first_month_price']} → ₹{plan['recurring_price']}/month")
        else:
            print("✗ Failed:", data.get('error'))
    else:
        print("✗ HTTP Error")

def test_get_subscription_status(user_id="test_user_123"):
    """Test getting subscription status"""
    print(f"\n=== Testing: Get Subscription Status (user_id={user_id}) ===")
    response = requests.get(f"{BASE_URL}/subscriptions/status/?user_id={user_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            sub = data.get('subscription', {})
            print("✓ Subscription status retrieved")
            print(f"  Plan: {sub.get('plan_name')}")
            print(f"  Status: {sub.get('status')}")
            print(f"  Trial: {sub.get('is_trial')}")
        else:
            print("✗ Failed:", data.get('error'))
    else:
        print("✗ HTTP Error")

def test_create_subscription(user_id="test_user_123", plan="basic"):
    """Test creating a subscription (won't actually charge in test mode)"""
    print(f"\n=== Testing: Create Subscription (user_id={user_id}, plan={plan}) ===")
    response = requests.post(
        f"{BASE_URL}/subscriptions/create/",
        json={"user_id": user_id, "plan": plan}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✓ Subscription created successfully")
            print(f"  Subscription ID: {data.get('subscription_id')}")
            print(f"  First Payment: {data.get('first_payment')}")
            print(f"  Recurring: {data.get('recurring_payment')}")
            print(f"  Message: {data.get('message')}")
            print(f"  Payment URL: {data.get('payment_url')}")
        else:
            print("✗ Failed:", data.get('error'))
    else:
        print("✗ HTTP Error")
        print(response.text)

def test_invalid_plan():
    """Test creating subscription with invalid plan"""
    print("\n=== Testing: Invalid Plan ===")
    response = requests.post(
        f"{BASE_URL}/subscriptions/create/",
        json={"user_id": "test_user", "plan": "invalid"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print("✓ Correctly rejected invalid plan")
    else:
        print("✗ Should have returned 400 error")

def test_missing_user_id():
    """Test creating subscription without user_id"""
    print("\n=== Testing: Missing user_id ===")
    response = requests.post(
        f"{BASE_URL}/subscriptions/create/",
        json={"plan": "basic"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print("✓ Correctly rejected missing user_id")
    else:
        print("✗ Should have returned 400 error")

if __name__ == "__main__":
    print("=" * 60)
    print("RAZORPAY SUBSCRIPTION API TESTS")
    print("=" * 60)
    
    # Test 1: Get available plans
    test_get_plans()
    
    # Test 2: Get subscription status (before subscription)
    test_get_subscription_status()
    
    # Test 3: Create BASIC subscription
    test_create_subscription(user_id="test_user_123", plan="basic")
    
    # Test 4: Get subscription status (after subscription)
    test_get_subscription_status(user_id="test_user_123")
    
    # Test 5: Invalid plan
    test_invalid_plan()
    
    # Test 6: Missing user_id
    test_missing_user_id()
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETED")
    print("=" * 60)
    print("\nNote: These tests require:")
    print("1. Django server running on localhost:8003")
    print("2. Database initialized with default plans")
    print("3. Razorpay credentials in .env (test mode)")
    print("\nTo run: python test_subscription_api.py")

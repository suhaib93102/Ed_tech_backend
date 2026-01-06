#!/usr/bin/env python3
"""
Razorpay Integration Test Script
Tests the complete payment flow

Author: EdTech Platform
Date: December 20, 2024
"""
import requests
import json
import sys

# Configuration
API_BASE_URL = "http://127.0.0.1:8003/api"
TEST_USER_ID = "test_user_123"
TEST_AMOUNT = 299.99

def print_header(text):
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}\n")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def test_create_order():
    """Test order creation endpoint"""
    print_header("Test 1: Create Payment Order")
    
    try:
        url = f"{API_BASE_URL}/razorpay/create-order/"
        payload = {
            "user_id": TEST_USER_ID,
            "amount": TEST_AMOUNT,
            "currency": "INR",
            "notes": {
                "plan": "premium",
                "duration": "monthly",
                "test": True
            }
        }
        
        print_info(f"POST {url}")
        print_info(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload)
        data = response.json()
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response:\n{json.dumps(data, indent=2)}")
        
        if response.status_code == 201 and data.get('success'):
            print_success("Order created successfully!")
            print_success(f"Order ID: {data['order_id']}")
            print_success(f"Amount: {data['amount']} paise (₹{data['amount']/100})")
            print_success(f"Currency: {data['currency']}")
            print_success(f"Key ID: {data['key_id'][:15]}...")
            return data['order_id']
        else:
            print_error(f"Order creation failed: {data.get('error')}")
            return None
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return None

def test_get_payment_status(order_id):
    """Test payment status endpoint"""
    print_header("Test 2: Get Payment Status")
    
    try:
        url = f"{API_BASE_URL}/razorpay/status/{order_id}/"
        print_info(f"GET {url}")
        
        response = requests.get(url)
        data = response.json()
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response:\n{json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and data.get('success'):
            print_success("Payment status retrieved successfully!")
            print_success(f"Status: {data['status']}")
            print_success(f"Amount: {data['amount']} paise")
            return True
        else:
            print_error(f"Failed to get status: {data.get('error')}")
            return False
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False

def test_get_razorpay_key():
    """Test get Razorpay key endpoint"""
    print_header("Test 3: Get Razorpay Key")
    
    try:
        url = f"{API_BASE_URL}/razorpay/key/"
        print_info(f"GET {url}")
        
        response = requests.get(url)
        data = response.json()
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response:\n{json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and (data.get('key_id') or data.get('success')):
            print_success("Razorpay key retrieved successfully!")
            key_id = data.get('key_id') or data.get('key')
            print_success(f"Key ID: {key_id[:15]}..." if key_id else f"Response: {data}")
            return True
        else:
            print_error("Failed to get Razorpay key")
            return False
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False

def test_get_payment_history():
    """Test payment history endpoint"""
    print_header("Test 4: Get Payment History")
    
    try:
        url = f"{API_BASE_URL}/razorpay/history/?user_id={TEST_USER_ID}"
        print_info(f"GET {url}")
        
        response = requests.get(url)
        data = response.json()
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response:\n{json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and data.get('success'):
            print_success(f"Payment history retrieved successfully!")
            print_success(f"Total payments: {data.get('count', 0)}")
            return True
        else:
            print_error(f"Failed to get history: {data.get('error')}")
            return False
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False

def test_verify_payment_invalid_signature():
    """Test payment verification with invalid signature"""
    print_header("Test 5: Verify Payment (Invalid Signature)")
    
    try:
        url = f"{API_BASE_URL}/razorpay/verify-payment/"
        payload = {
            "razorpay_order_id": "order_test123",
            "razorpay_payment_id": "pay_test123",
            "razorpay_signature": "invalid_signature_12345"
        }
        
        print_info(f"POST {url}")
        print_info(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload)
        data = response.json()
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response:\n{json.dumps(data, indent=2)}")
        
        if response.status_code in [400, 404] and not data.get('success'):
            print_success("Correctly rejected invalid signature!")
            print_success(f"Error: {data.get('error')}")
            return True
        else:
            print_error("Failed to reject invalid signature")
            return False
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False

def main():
    """Run all tests"""
    print_header("🧪 Razorpay Integration Test Suite")
    print_info(f"API Base URL: {API_BASE_URL}")
    print_info(f"Test User ID: {TEST_USER_ID}")
    print_info(f"Test Amount: ₹{TEST_AMOUNT}")
    
    # Check if backend is running
    try:
        response = requests.get(f"{API_BASE_URL}/health/")
        if response.status_code != 200:
            print_error("Backend health check failed!")
            print_error("Make sure Django server is running:")
            print_error("  cd backend && python manage.py runserver 8003")
            sys.exit(1)
        print_success("Backend is running\n")
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend!")
        print_error("Make sure Django server is running:")
        print_error("  cd backend && python manage.py runserver 8003")
        sys.exit(1)
    
    # Run tests
    results = []
    
    # Test 1: Create Order
    order_id = test_create_order()
    results.append(("Create Order", order_id is not None))
    
    if order_id:
        # Test 2: Get Payment Status
        results.append(("Get Payment Status", test_get_payment_status(order_id)))
    else:
        results.append(("Get Payment Status", False))
        print_error("Skipped: No order ID available")
    
    # Test 3: Get Razorpay Key
    results.append(("Get Razorpay Key", test_get_razorpay_key()))
    
    # Test 4: Get Payment History
    results.append(("Get Payment History", test_get_payment_history()))
    
    # Test 5: Verify Invalid Signature
    results.append(("Verify Invalid Signature", test_verify_payment_invalid_signature()))
    
    # Print summary
    print_header("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name}")
    
    print(f"\n{'=' * 70}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'=' * 70}\n")
    
    if passed == total:
        print_success("All tests passed! 🎉")
        print_info("Next steps:")
        print_info("1. Install react-native-razorpay in mobile app")
        print_info("2. Test payment flow with Razorpay test cards")
        print_info("3. Verify signature verification works correctly")
        sys.exit(0)
    else:
        print_error(f"{total - passed} test(s) failed")
        print_info("Check the errors above and fix the issues")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)

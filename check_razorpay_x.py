"""
Check if Razorpay X is enabled and accessible
"""
import requests
from requests.auth import HTTPBasicAuth
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
django.setup()

from django.conf import settings

def check_razorpay_x():
    """Check Razorpay X activation status"""
    
    key_id = settings.RAZORPAY_KEY_ID
    key_secret = settings.RAZORPAY_KEY_SECRET
    auth = HTTPBasicAuth(key_id, key_secret)
    
    print("=" * 80)
    print("RAZORPAY X ACCESS CHECK")
    print("=" * 80)
    print()
    
    print(f"Using Key ID: {key_id}")
    print()
    
    # Test 1: Check payment API (should work)
    print("Test 1: Payment API Access")
    print("-" * 40)
    try:
        response = requests.get(
            "https://api.razorpay.com/v1/payments",
            auth=auth,
            params={"count": 1}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Payment API is accessible")
        else:
            print(f"❌ Payment API error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 2: Check Razorpay X contacts API
    print("Test 2: Razorpay X Contacts API")
    print("-" * 40)
    try:
        response = requests.get(
            "https://api.razorpay.com/v1/contacts",
            auth=auth,
            params={"count": 1}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Razorpay X Contacts API is accessible")
            data = response.json()
            print(f"   Found {data.get('count', 0)} contacts")
        else:
            print(f"❌ Razorpay X error: {response.text}")
            error_data = response.json()
            if 'error' in error_data:
                error = error_data['error']
                print(f"   Error Code: {error.get('code')}")
                print(f"   Description: {error.get('description')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 3: Check Razorpay X fund_accounts API
    print("Test 3: Razorpay X Fund Accounts API")
    print("-" * 40)
    try:
        response = requests.get(
            "https://api.razorpay.com/v1/fund_accounts",
            auth=auth,
            params={"count": 1}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Razorpay X Fund Accounts API is accessible")
            data = response.json()
            print(f"   Found {data.get('count', 0)} fund accounts")
        else:
            print(f"❌ Razorpay X error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 4: Check Razorpay X payouts API
    print("Test 4: Razorpay X Payouts API")
    print("-" * 40)
    try:
        response = requests.get(
            "https://api.razorpay.com/v1/payouts",
            auth=auth,
            params={"count": 1}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Razorpay X Payouts API is accessible")
            data = response.json()
            print(f"   Found {data.get('count', 0)} payouts")
        else:
            print(f"❌ Razorpay X error")
            error_data = response.json()
            if 'error' in error_data:
                error = error_data['error']
                print(f"   Error Code: {error.get('code')}")
                print(f"   Description: {error.get('description')}")
                print()
                print("   This likely means Razorpay X is NOT enabled on your account")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print()
    print("If Razorpay X is not enabled:")
    print("1. Login to Razorpay Dashboard: https://dashboard.razorpay.com/")
    print("2. Navigate to 'Razorpay X' in the left sidebar")
    print("3. Click 'Activate Razorpay X'")
    print("4. Complete the KYC process if required")
    print("5. Wait for approval (usually 1-2 business days)")
    print()
    print("Alternative for testing:")
    print("1. Use Razorpay X Test Mode credentials")
    print("2. Test credentials: rzp_test_* and key secret")
    print("3. Test mode doesn't require activation")
    print()

if __name__ == "__main__":
    check_razorpay_x()

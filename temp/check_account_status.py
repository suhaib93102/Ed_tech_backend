"""
Check Razorpay X account details and balance
"""
import requests
from requests.auth import HTTPBasicAuth
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
django.setup()

from django.conf import settings

def check_razorpay_x_account():
    """Check Razorpay X account and balance"""
    
    key_id = settings.RAZORPAY_KEY_ID
    key_secret = settings.RAZORPAY_KEY_SECRET
    account_number = getattr(settings, 'RAZORPAY_ACCOUNT_NUMBER', '')
    auth = HTTPBasicAuth(key_id, key_secret)
    
    print("=" * 80)
    print("RAZORPAY X ACCOUNT CHECK")
    print("=" * 80)
    print()
    
    print(f"Key ID: {key_id}")
    print(f"Key Type: {'Live' if 'live' in key_id else 'Test'}")
    print(f"Account Number: {account_number}")
    print()
    
    # Check if we can fetch balance
    print("Checking Account Balance...")
    print("-" * 40)
    
    if account_number:
        response = requests.get(
            f"https://api.razorpay.com/v1/balance/banking",
            auth=auth,
            params={"account_number": account_number}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            balance = data.get('balance', 0) / 100  # Convert paise to rupees
            print(f"✅ Account Balance: ₹{balance}")
        else:
            print("❌ Could not fetch balance")
            print("   This might indicate Razorpay X is not fully activated")
    else:
        print("❌ No account number configured")
    
    print()
    print("=" * 80)
    print("IMPORTANT: RAZORPAY X ACTIVATION")
    print("=" * 80)
    print()
    print("The error 'URL not found' for payouts endpoint typically means:")
    print()
    print("1. Razorpay X is NOT fully activated on your account")
    print("   Even though you can create Contacts and Fund Accounts,")
    print("   the Payouts feature requires additional activation.")
    print()
    print("2. You're using LIVE mode credentials but haven't completed:")
    print("   - KYC verification")
    print("   - Bank account linking")
    print("   - Current account setup")
    print()
    print("SOLUTIONS:")
    print()
    print("Option 1: Activate Razorpay X (for real money)")
    print("-" * 40)
    print("1. Go to: https://dashboard.razorpay.com/")
    print("2. Click on 'Razorpay X' in left sidebar")
    print("3. If you see 'Activate Now', click it")
    print("4. Complete KYC and bank account setup")
    print("5. Wait for approval (1-2 business days)")
    print("6. Once approved, add funds to your Razorpay X balance")
    print()
    print("Option 2: Use TEST mode (for testing without real money)")
    print("-" * 40)
    print("1. Get test credentials from Razorpay Dashboard")
    print("2. Update .env with:")
    print("   RAZORPAY_KEY_ID=rzp_test_XXXXXXXXXX")
    print("   RAZORPAY_KEY_SECRET=your_test_secret")
    print("3. Test mode doesn't require activation!")
    print("4. Payouts will be simulated (no real money transfer)")
    print()
    print("Recommended: Start with TEST mode first to verify the flow works")
    print()

if __name__ == "__main__":
    check_razorpay_x_account()

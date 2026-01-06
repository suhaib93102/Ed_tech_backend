"""
Direct Razorpay Payouts API Test using REST API
Tests real payout without relying on SDK's contact attribute

User: RahulJHA996886
UPI: rahuljha996886-1@oksbi
"""
import os
import requests
from requests.auth import HTTPBasicAuth
import json

# Razorpay credentials
KEY_ID = "rzp_live_RpW8iXPZdjGo6y"
KEY_SECRET = "bxPr9jrDfrQcCZHfpHmDIURD"
ACCOUNT_NUMBER = "2323230099506802"

# Test details
UPI_ID = "rahuljha996886-1@oksbi"
AMOUNT_PAISE = 1000  # ₹10

print("\n🧪 DIRECT RAZORPAY PAYOUTS API TEST\n")
print("="*60)

# Step 1: Create Contact
print("\n📋 Step 1: Creating Razorpay Contact")
contact_url = "https://api.razorpay.com/v1/contacts"
contact_data = {
    "name": "Rahul Jha",
    "email": "rahuljha996886@gmail.com",
    "contact": "9999999999",
    "type": "customer",
    "reference_id": "user_16_withdrawal"
}

try:
    contact_response = requests.post(
        contact_url,
        auth=HTTPBasicAuth(KEY_ID, KEY_SECRET),
        json=contact_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {contact_response.status_code}")
    print(f"Response: {json.dumps(contact_response.json(), indent=2)}")
    
    if contact_response.status_code in [200, 201]:
        contact_id = contact_response.json().get('id')
        print(f"✅ Contact created: {contact_id}")
        
        # Step 2: Create Fund Account (UPI)
        print("\n📋 Step 2: Creating Fund Account (UPI)")
        fund_account_url = "https://api.razorpay.com/v1/fund_accounts"
        fund_account_data = {
            "contact_id": contact_id,
            "account_type": "vpa",
            "vpa": {
                "address": UPI_ID
            }
        }
        
        fund_response = requests.post(
            fund_account_url,
            auth=HTTPBasicAuth(KEY_ID, KEY_SECRET),
            json=fund_account_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {fund_response.status_code}")
        print(f"Response: {json.dumps(fund_response.json(), indent=2)}")
        
        if fund_response.status_code in [200, 201]:
            fund_account_id = fund_response.json().get('id')
            print(f"✅ Fund Account created: {fund_account_id}")
            
            # Step 3: Create Payout
            print("\n📋 Step 3: Creating Payout (REAL MONEY!)")
            print(f"⚠️  Amount: ₹{AMOUNT_PAISE/100}")
            print(f"⚠️  UPI: {UPI_ID}")
            
            payout_url = "https://api.razorpay.com/v1/payouts"
            payout_data = {
                "account_number": ACCOUNT_NUMBER,
                "fund_account_id": fund_account_id,
                "amount": AMOUNT_PAISE,
                "currency": "INR",
                "mode": "UPI",
                "purpose": "payout",
                "queue_if_low_balance": True,
                "reference_id": f"withdrawal_test_{AMOUNT_PAISE}",
                "narration": "EdTech Coin Withdrawal Test"
            }
            
            payout_response = requests.post(
                payout_url,
                auth=HTTPBasicAuth(KEY_ID, KEY_SECRET),
                json=payout_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {payout_response.status_code}")
            print(f"Response: {json.dumps(payout_response.json(), indent=2)}")
            
            if payout_response.status_code in [200, 201]:
                payout = payout_response.json()
                print(f"\n✅ PAYOUT SUCCESSFUL!")
                print(f"   Payout ID: {payout.get('id')}")
                print(f"   Status: {payout.get('status')}")
                print(f"   Amount: ₹{payout.get('amount', 0)/100}")
                print(f"   UPI: {payout.get('fund_account_id')}")
                print(f"\n🎉 Money is being sent to {UPI_ID}!")
            else:
                print(f"\n❌ PAYOUT FAILED")
                print(f"   Error: {payout_response.json().get('error', {}).get('description')}")
        else:
            print(f"\n❌ Fund Account creation failed")
            print(f"   Error: {fund_response.json().get('error', {}).get('description')}")
    else:
        print(f"\n❌ Contact creation failed")
        error_data = contact_response.json()
        print(f"   Error: {error_data.get('error', {}).get('description')}")
        
        # Check if it's a Razorpay X not enabled error
        if 'not enabled' in str(error_data).lower() or 'razorpay x' in str(error_data).lower():
            print(f"\n⚠️  RAZORPAY X NOT ENABLED")
            print(f"   Your account only has Payment Gateway enabled")
            print(f"   You need to enable Razorpay X for Payouts/Contacts API")
            print(f"   Go to: https://dashboard.razorpay.com/ → Apply for Razorpay X")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*60}\n")

"""
Test creating a payout directly with proper parameters
"""
import requests
from requests.auth import HTTPBasicAuth
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
django.setup()

from django.conf import settings

def test_payout():
    """Test payout creation with actual account number"""
    
    key_id = settings.RAZORPAY_KEY_ID
    key_secret = settings.RAZORPAY_KEY_SECRET
    account_number = getattr(settings, 'RAZORPAY_ACCOUNT_NUMBER', '')
    auth = HTTPBasicAuth(key_id, key_secret)
    headers = {"Content-Type": "application/json"}
    
    print("=" * 80)
    print("PAYOUT CREATION TEST")
    print("=" * 80)
    print()
    
    print(f"Key ID: {key_id}")
    print(f"Account Number: {account_number}")
    print()
    
    # First, get existing contacts to use one
    print("Step 1: Getting existing contact...")
    print("-" * 40)
    response = requests.get(
        "https://api.razorpay.com/v1/contacts",
        auth=auth,
        params={"count": 1}
    )
    if response.status_code == 200:
        data = response.json()
        if data['count'] > 0:
            contact = data['items'][0]
            contact_id = contact['id']
            print(f"✅ Using contact: {contact_id}")
            print(f"   Name: {contact.get('name')}")
        else:
            print("❌ No contacts found. Creating one first...")
            # Create a contact
            contact_data = {
                "name": "Test User",
                "email": "test@edtech.local",
                "contact": "9999999999",
                "type": "customer"
            }
            response = requests.post(
                "https://api.razorpay.com/v1/contacts",
                auth=auth,
                json=contact_data,
                headers=headers
            )
            if response.status_code in [200, 201]:
                contact = response.json()
                contact_id = contact['id']
                print(f"✅ Created contact: {contact_id}")
            else:
                print(f"❌ Failed to create contact: {response.text}")
                return
    else:
        print(f"❌ Failed to fetch contacts: {response.text}")
        return
    print()
    
    # Get or create fund account
    print("Step 2: Getting/Creating fund account...")
    print("-" * 40)
    response = requests.get(
        "https://api.razorpay.com/v1/fund_accounts",
        auth=auth,
        params={"count": 1}
    )
    if response.status_code == 200:
        data = response.json()
        if data['count'] > 0:
            fund_account = data['items'][0]
            fund_account_id = fund_account['id']
            print(f"✅ Using fund account: {fund_account_id}")
            print(f"   VPA: {fund_account.get('vpa', {}).get('address', 'N/A')}")
        else:
            print("Creating fund account for UPI rahuljha996886-1@oksbi...")
            fund_account_data = {
                "contact_id": contact_id,
                "account_type": "vpa",
                "vpa": {
                    "address": "rahuljha996886-1@oksbi"
                }
            }
            response = requests.post(
                "https://api.razorpay.com/v1/fund_accounts",
                auth=auth,
                json=fund_account_data,
                headers=headers
            )
            if response.status_code in [200, 201]:
                fund_account = response.json()
                fund_account_id = fund_account['id']
                print(f"✅ Created fund account: {fund_account_id}")
            else:
                print(f"❌ Failed to create fund account: {response.text}")
                return
    print()
    
    # Create payout
    print("Step 3: Creating payout...")
    print("-" * 40)
    payout_data = {
        "account_number": account_number,
        "fund_account_id": fund_account_id,
        "amount": 1000,  # ₹10 in paise
        "currency": "INR",
        "mode": "UPI",
        "purpose": "payout",
        "queue_if_low_balance": True,
        "reference_id": f"test_payout_001",
        "narration": "Test EdTech Withdrawal"
    }
    
    print("Payout payload:")
    print(json.dumps(payout_data, indent=2))
    print()
    
    response = requests.post(
        "https://api.razorpay.com/v1/payouts",
        auth=auth,
        json=payout_data,
        headers=headers
    )
    
    print(f"Response Status: {response.status_code}")
    print(f"Response: {response.text}")
    print()
    
    if response.status_code in [200, 201]:
        payout = response.json()
        print("✅ PAYOUT CREATED SUCCESSFULLY!")
        print(f"   Payout ID: {payout.get('id')}")
        print(f"   Status: {payout.get('status')}")
        print(f"   Amount: ₹{payout.get('amount', 0)/100}")
        print(f"   UTR: {payout.get('utr', 'Pending')}")
        print()
        print("🎉 REAL MONEY IS BEING SENT!")
        print(f"   Check UPI ID: rahuljha996886-1@oksbi")
    else:
        error_data = response.json()
        print("❌ PAYOUT FAILED")
        if 'error' in error_data:
            error = error_data['error']
            print(f"   Error Code: {error.get('code')}")
            print(f"   Description: {error.get('description')}")
            print(f"   Field: {error.get('field')}")
            
            # Provide specific guidance
            if "account number" in error.get('description', '').lower():
                print()
                print("   ISSUE: Account number problem")
                print("   The account number in .env might be incorrect or")
                print("   Razorpay X might not be fully activated.")
                print()
                print("   To get correct account number:")
                print("   1. Login to https://dashboard.razorpay.com/")
                print("   2. Go to Razorpay X → Banking")
                print("   3. Copy the Account Number shown there")
                print("   4. Update RAZORPAY_ACCOUNT_NUMBER in .env")
            elif "balance" in error.get('description', '').lower():
                print()
                print("   ISSUE: Insufficient balance in Razorpay X")
                print("   You need to add funds to your Razorpay X account first")
                print()
                print("   To add funds:")
                print("   1. Login to https://dashboard.razorpay.com/")
                print("   2. Go to Razorpay X → Banking")
                print("   3. Click 'Add Funds' and transfer money from your bank")

if __name__ == "__main__":
    test_payout()

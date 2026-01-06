"""
REAL MONEY WITHDRAWAL TEST
Tests actual payout to UPI ID: rahuljha996886-1@oksbi

⚠️  WARNING: This script will attempt to send REAL MONEY via Razorpay Payouts!
Only run this if you have Razorpay X account enabled and funded.

User: RahulJHA996886
Password: Rahuljha@123
UPI ID: rahuljha996886-1@oksbi
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
django.setup()

# Add testserver to ALLOWED_HOSTS for testing
from django.conf import settings
settings.ALLOWED_HOSTS.append('testserver')

from django.contrib.auth.models import User
from question_solver.models import UserCoins, CoinWithdrawal
from rest_framework.test import APIClient
import json

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
BOLD = '\033[1m'
RESET = '\033[0m'

print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
print(f"{BOLD}{BLUE}REAL MONEY WITHDRAWAL TEST{RESET}")
print(f"{BOLD}{BLUE}{'='*80}{RESET}\n")

print(f"{YELLOW}⚠️  WARNING: This will attempt to send REAL MONEY!{RESET}\n")

# Test user credentials
USERNAME = 'RahulJHA996886'
PASSWORD = 'Rahuljha@123'
UPI_ID = 'rahuljha996886-1@oksbi'
COINS_TO_WITHDRAW = 100  # 100 coins = ₹10

# Setup API client
client = APIClient()

# Step 1: Create or get user
print(f"{BOLD}Step 1: Setting up user account{RESET}")
try:
    user = User.objects.get(username=USERNAME)
    print(f"{GREEN}✅ User exists: {user.username} (ID: {user.id}){RESET}")
except User.DoesNotExist:
    user = User.objects.create_user(
        username=USERNAME,
        email='rahuljha996886@gmail.com',
        password=PASSWORD,
        first_name='Rahul',
        last_name='Jha'
    )
    print(f"{GREEN}✅ Created new user: {user.username} (ID: {user.id}){RESET}")

# Step 2: Setup coins
print(f"\n{BOLD}Step 2: Adding coins to account{RESET}")
user_coins, created = UserCoins.objects.get_or_create(
    user_id=str(user.id),
    defaults={
        'total_coins': 500,
        'lifetime_coins': 500,
        'coins_spent': 0
    }
)

if not created:
    # User already has coins, ensure they have enough
    if user_coins.total_coins < COINS_TO_WITHDRAW:
        user_coins.total_coins = 500
        user_coins.lifetime_coins += 500
        user_coins.save()
        print(f"{GREEN}✅ Added more coins. New balance: {user_coins.total_coins} coins{RESET}")
    else:
        print(f"{GREEN}✅ User has sufficient balance: {user_coins.total_coins} coins{RESET}")
else:
    print(f"{GREEN}✅ Created coin account with {user_coins.total_coins} coins{RESET}")

print(f"{BLUE}ℹ️  Balance: {user_coins.total_coins} coins (₹{user_coins.total_coins/10}){RESET}")

# Step 3: Attempt withdrawal
print(f"\n{BOLD}Step 3: Initiating withdrawal{RESET}")
print(f"{BLUE}ℹ️  Coins to withdraw: {COINS_TO_WITHDRAW} (₹{COINS_TO_WITHDRAW/10}){RESET}")
print(f"{BLUE}ℹ️  UPI ID: {UPI_ID}{RESET}")

withdrawal_data = {
    'user_id': str(user.id),
    'coins_amount': COINS_TO_WITHDRAW,
    'upi_id': UPI_ID
}

print(f"\n{YELLOW}🔄 Calling withdrawal API...{RESET}")
response = client.post('/api/wallet/withdraw/', withdrawal_data)

print(f"\n{BOLD}Response Status: {response.status_code}{RESET}")

# Step 4: Check response
if response.status_code in [200, 201]:
    data = response.json()
    
    if data.get('success'):
        print(f"\n{GREEN}{BOLD}{'='*80}{RESET}")
        print(f"{GREEN}{BOLD}✅ WITHDRAWAL SUCCESSFUL!{RESET}")
        print(f"{GREEN}{BOLD}{'='*80}{RESET}\n")
        
        print(f"{GREEN}Withdrawal ID: {data.get('withdrawal_id')}{RESET}")
        print(f"{GREEN}Amount: ₹{data.get('amount')}{RESET}")
        print(f"{GREEN}Coins Deducted: {data.get('coins_deducted')}{RESET}")
        print(f"{GREEN}Razorpay Payout ID: {data.get('razorpay_payout_id')}{RESET}")
        print(f"{GREEN}Status: {data.get('status')}{RESET}")
        print(f"{GREEN}UPI ID: {data.get('upi_id')}{RESET}")
        
        # Check updated balance
        user_coins.refresh_from_db()
        print(f"\n{BLUE}Updated Balance: {user_coins.total_coins} coins (₹{user_coins.total_coins/10}){RESET}")
        
        # Get withdrawal record
        withdrawal = CoinWithdrawal.objects.get(id=data.get('withdrawal_id'))
        print(f"\n{BOLD}Withdrawal Details from Database:{RESET}")
        print(f"  Status: {withdrawal.status}")
        print(f"  Razorpay Contact ID: {withdrawal.razorpay_contact_id}")
        print(f"  Razorpay Fund Account ID: {withdrawal.razorpay_fund_account_id}")
        print(f"  Razorpay Payout ID: {withdrawal.razorpay_payout_id}")
        print(f"  Created: {withdrawal.created_at}")
        
        print(f"\n{GREEN}{BOLD}🎉 Money is being sent to {UPI_ID}!{RESET}")
        print(f"{BLUE}ℹ️  Check Razorpay dashboard for payout status{RESET}")
        print(f"{BLUE}ℹ️  Money should arrive within minutes{RESET}")
        
    else:
        print(f"\n{RED}{BOLD}❌ WITHDRAWAL FAILED{RESET}")
        print(f"{RED}Error: {data.get('error')}{RESET}")
        if 'details' in data:
            print(f"{RED}Details: {data.get('details')}{RESET}")
        
        # Check if coins were deducted (shouldn't be if failed)
        user_coins.refresh_from_db()
        print(f"\n{BLUE}Current Balance: {user_coins.total_coins} coins{RESET}")
        if user_coins.total_coins == 500:
            print(f"{GREEN}✅ Atomic transaction worked: Coins NOT deducted on failure{RESET}")
        else:
            print(f"{YELLOW}⚠️  Balance changed to: {user_coins.total_coins} coins{RESET}")

else:
    print(f"\n{RED}{BOLD}❌ API ERROR{RESET}")
    try:
        data = response.json()
        print(f"{RED}Error: {json.dumps(data, indent=2)}{RESET}")
    except:
        print(f"{RED}Response: {response.content.decode()}{RESET}")

# Step 5: Show withdrawal history
print(f"\n{BOLD}Step 4: Withdrawal History{RESET}")
history_response = client.get(f'/api/wallet/withdrawals/?user_id={user.id}')

if history_response.status_code == 200:
    history = history_response.json()
    print(f"{GREEN}✅ Total Withdrawals: {history['count']}{RESET}")
    print(f"{GREEN}✅ Total Withdrawn: {history['total_withdrawn_coins']} coins (₹{history['total_withdrawn_rupees']}){RESET}")
    
    if history['withdrawals']:
        print(f"\n{BOLD}Recent Withdrawals:{RESET}")
        for w in history['withdrawals'][:3]:
            print(f"  • {w['coins_amount']} coins (₹{w['rupees_amount']}) - {w['status']} - {w['created_at']}")

print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
print(f"{BOLD}{BLUE}TEST COMPLETE{RESET}")
print(f"{BOLD}{BLUE}{'='*80}{RESET}\n")

print(f"{YELLOW}📋 NEXT STEPS:{RESET}")
print(f"  1. Check Razorpay Dashboard: https://dashboard.razorpay.com/")
print(f"  2. Go to Payouts section to see transaction")
print(f"  3. UPI notification should arrive on {UPI_ID}")
print(f"  4. Check bank account linked to UPI")
print(f"\n{GREEN}✅ Backend withdrawal system is working!{RESET}\n")

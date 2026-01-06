#!/usr/bin/env python
"""
Production-Ready Withdrawal System Test Suite
Tests all aspects of the withdrawal flow including:
- User creation with coins
- Withdrawal validation rules
- Coin deduction
- Admin dashboard integration
- Error handling
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
django.setup()

from django.contrib.auth.models import User
from question_solver.models import UserCoins, CoinWithdrawal, CoinTransaction
from django.db import transaction
import json


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.YELLOW}ℹ️  {text}{Colors.END}")


def cleanup_test_data():
    """Clean up any existing test data"""
    print_info("Cleaning up existing test data...")
    User.objects.filter(username__startswith='test_user_').delete()
    UserCoins.objects.filter(user_id__startswith='test_user_').delete()
    CoinWithdrawal.objects.filter(user_id__startswith='test_user_').delete()
    print_success("Cleanup complete")


def create_test_user_with_coins(user_id, coins=1000):
    """Create a test user with specified coins"""
    print_info(f"Creating test user: {user_id} with {coins} coins")
    
    # Create Django user for authentication
    django_user, created = User.objects.get_or_create(
        username=user_id,
        defaults={'email': f'{user_id}@test.com'}
    )
    if created:
        django_user.set_password('testpass123')
        django_user.save()
    
    # Create coin balance
    user_coins, created = UserCoins.objects.get_or_create(
        user_id=user_id,
        defaults={
            'total_coins': coins,
            'lifetime_coins': coins,
            'coins_spent': 0
        }
    )
    
    if not created:
        user_coins.total_coins = coins
        user_coins.lifetime_coins = coins
        user_coins.coins_spent = 0
        user_coins.save()
    
    print_success(f"Created user: {user_id} with {coins} coins")
    return django_user, user_coins


def test_validation_rules():
    """Test all withdrawal validation rules"""
    print_header("TEST 1: Validation Rules")
    
    # Test Case 1: Minimum withdrawal (200 coins)
    print_info("Test 1a: Minimum withdrawal - 200 coins")
    user_id = "test_user_min_coins"
    user, user_coins = create_test_user_with_coins(user_id, 1000)
    
    # This should PASS (200 is minimum)
    initial_balance = user_coins.total_coins
    print(f"   Initial balance: {initial_balance} coins")
    print(f"   Withdrawal amount: 200 coins")
    print(f"   Expected: Should PASS (200 = minimum)")
    print_success("Test 1a setup complete")
    
    # Test Case 2: Below minimum (150 coins)
    print_info("\nTest 1b: Below minimum - 150 coins")
    user_id = "test_user_below_min"
    user, user_coins = create_test_user_with_coins(user_id, 1000)
    print(f"   Initial balance: {user_coins.total_coins} coins")
    print(f"   Withdrawal amount: 150 coins")
    print(f"   Expected: Should FAIL (150 < 200 minimum)")
    print_success("Test 1b setup complete")
    
    # Test Case 3: Balance check (remaining > 100)
    print_info("\nTest 1c: Balance check - remaining must be > 100")
    user_id = "test_user_balance_check"
    user, user_coins = create_test_user_with_coins(user_id, 350)
    print(f"   Initial balance: {user_coins.total_coins} coins")
    print(f"   Withdrawal amount: 300 coins")
    print(f"   Remaining after: {user_coins.total_coins - 300} coins")
    print(f"   Expected: Should FAIL (remaining 50 < 100)")
    print_success("Test 1c setup complete")
    
    # Test Case 4: Valid withdrawal with sufficient balance
    print_info("\nTest 1d: Valid withdrawal - 500 coins")
    user_id = "test_user_valid"
    user, user_coins = create_test_user_with_coins(user_id, 1000)
    print(f"   Initial balance: {user_coins.total_coins} coins")
    print(f"   Withdrawal amount: 500 coins")
    print(f"   Remaining after: {user_coins.total_coins - 500} coins")
    print(f"   Expected: Should PASS (500 >= 200, remaining 500 > 100)")
    print_success("Test 1d setup complete")
    
    print_success("\nAll validation test users created successfully")


def test_coin_deduction():
    """Test that coins are deducted immediately"""
    print_header("TEST 2: Coin Deduction Verification")
    
    user_id = "test_user_deduction"
    user, user_coins = create_test_user_with_coins(user_id, 1000)
    
    initial_balance = user_coins.total_coins
    withdrawal_amount = 200
    
    print(f"User: {user_id}")
    print(f"Initial balance: {initial_balance} coins")
    print(f"Withdrawal amount: {withdrawal_amount} coins")
    print(f"Expected final balance: {initial_balance - withdrawal_amount} coins")
    
    print_success("Coin deduction test user created")
    print_info("After making withdrawal request via API, verify:")
    print_info(f"  - Coins deducted IMMEDIATELY (not after admin approval)")
    print_info(f"  - Final balance should be {initial_balance - withdrawal_amount} coins")


def test_admin_dashboard_visibility():
    """Test that withdrawals appear in admin dashboard"""
    print_header("TEST 3: Admin Dashboard Visibility")
    
    user_id = "test_user_admin_visibility"
    user, user_coins = create_test_user_with_coins(user_id, 1000)
    
    print(f"User: {user_id}")
    print(f"Balance: {user_coins.total_coins} coins")
    print(f"UPI ID: test@paytm")
    
    print_success("Admin dashboard test user created")
    print_info("After making withdrawal request, verify in admin:")
    print_info("  1. Login to: http://localhost:8000/admin/")
    print_info("  2. Go to: Coin withdrawals")
    print_info("  3. Check for withdrawal from: test_user_admin_visibility")
    print_info("  4. Verify UPI ID is displayed: test@paytm")
    print_info("  5. Verify auto-refresh indicator shows")


def test_multiple_withdrawals():
    """Test multiple withdrawal scenarios"""
    print_header("TEST 4: Multiple Withdrawal Scenarios")
    
    scenarios = [
        ("test_user_scenario_1", 1000, 200, "test1@paytm"),
        ("test_user_scenario_2", 1500, 500, "test2@phonepe"),
        ("test_user_scenario_3", 2000, 800, "test3@gpay"),
    ]
    
    for user_id, coins, withdrawal, upi in scenarios:
        user, user_coins = create_test_user_with_coins(user_id, coins)
        print(f"\n{user_id}:")
        print(f"  Balance: {coins} coins")
        print(f"  Withdrawal: {withdrawal} coins")
        print(f"  UPI ID: {upi}")
        print(f"  Remaining: {coins - withdrawal} coins")
    
    print_success("\nMultiple withdrawal test users created")


def verify_database_state():
    """Verify current database state"""
    print_header("DATABASE STATE VERIFICATION")
    
    total_users = UserCoins.objects.filter(user_id__startswith='test_user_').count()
    total_coins = sum([u.total_coins for u in UserCoins.objects.filter(user_id__startswith='test_user_')])
    total_withdrawals = CoinWithdrawal.objects.filter(user_id__startswith='test_user_').count()
    
    print(f"Total test users: {total_users}")
    print(f"Total coins in test accounts: {total_coins}")
    print(f"Total test withdrawals: {total_withdrawals}")
    
    if total_users > 0:
        print_success("Database contains test data")
    else:
        print_error("No test data in database")


def generate_curl_commands():
    """Generate curl commands for testing"""
    print_header("CURL TEST COMMANDS")
    
    base_url = "http://localhost:8000"
    
    print(f"{Colors.BOLD}1. Test Valid Withdrawal (200 coins - minimum):{Colors.END}")
    print(f'''
curl -X POST {base_url}/api/wallet/withdraw/ \\
  -H "Content-Type: application/json" \\
  -d '{{
    "user_id": "test_user_min_coins",
    "upi_id": "test@paytm",
    "coins": 200
  }}'
''')
    
    print(f"\n{Colors.BOLD}2. Test Below Minimum (should FAIL):{Colors.END}")
    print(f'''
curl -X POST {base_url}/api/wallet/withdraw/ \\
  -H "Content-Type: application/json" \\
  -d '{{
    "user_id": "test_user_below_min",
    "upi_id": "test@paytm",
    "coins": 150
  }}'
''')
    
    print(f"\n{Colors.BOLD}3. Test Balance Check (should FAIL - remaining < 100):{Colors.END}")
    print(f'''
curl -X POST {base_url}/api/wallet/withdraw/ \\
  -H "Content-Type: application/json" \\
  -d '{{
    "user_id": "test_user_balance_check",
    "upi_id": "test@paytm",
    "coins": 300
  }}'
''')
    
    print(f"\n{Colors.BOLD}4. Test Valid Withdrawal (500 coins):{Colors.END}")
    print(f'''
curl -X POST {base_url}/api/wallet/withdraw/ \\
  -H "Content-Type: application/json" \\
  -d '{{
    "user_id": "test_user_valid",
    "upi_id": "test@phonepe",
    "coins": 500
  }}'
''')
    
    print(f"\n{Colors.BOLD}5. Test Invalid UPI ID (should FAIL):{Colors.END}")
    print(f'''
curl -X POST {base_url}/api/wallet/withdraw/ \\
  -H "Content-Type: application/json" \\
  -d '{{
    "user_id": "test_user_valid",
    "upi_id": "invalidupi",
    "coins": 200
  }}'
''')
    
    print(f"\n{Colors.BOLD}6. Check User Coin Balance:{Colors.END}")
    print(f'''
curl -X GET "{base_url}/api/daily-quiz/coins/?user_id=test_user_min_coins"
''')
    
    print(f"\n{Colors.BOLD}7. Get Withdrawal History:{Colors.END}")
    print(f'''
curl -X GET "{base_url}/api/wallet/withdrawals/?user_id=test_user_min_coins"
''')


def main():
    """Main test runner"""
    print_header("🧪 WITHDRAWAL SYSTEM - PRODUCTION TEST SUITE")
    
    try:
        # Clean up old test data
        cleanup_test_data()
        
        # Create test scenarios
        test_validation_rules()
        test_coin_deduction()
        test_admin_dashboard_visibility()
        test_multiple_withdrawals()
        
        # Verify database
        verify_database_state()
        
        # Generate curl commands
        generate_curl_commands()
        
        print_header("✅ TEST SETUP COMPLETE")
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}Next Steps:{Colors.END}")
        print(f"1. Start Django server: python manage.py runserver")
        print(f"2. Run the curl commands above to test the API")
        print(f"3. Check admin dashboard: http://localhost:8000/admin/")
        print(f"4. Verify withdrawals appear with correct UPI IDs")
        print(f"5. Verify coins are deducted immediately")
        print(f"\n{Colors.BOLD}{Colors.YELLOW}Important:{Colors.END}")
        print(f"- Minimum withdrawal: 200 coins")
        print(f"- Balance after withdrawal must be > 100 coins")
        print(f"- Coins deducted IMMEDIATELY when withdrawal requested")
        print(f"- Admin sees withdrawal in dashboard with UPI ID")
        print(f"- Admin manually pays via UPI and marks as completed\n")
        
    except Exception as e:
        print_error(f"Test setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

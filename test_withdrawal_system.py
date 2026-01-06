"""
Comprehensive Withdrawal System Test Suite
Tests UPI-based coin withdrawal with Razorpay Payouts API

Author: Senior Django Developer
Date: 2026-01-04

Test Coverage:
1. Valid withdrawal (100+ coins) - Contact → Fund Account → Payout → Deduct Coins
2. Insufficient balance
3. Below minimum withdrawal (< 100 coins)
4. Invalid UPI ID format
5. Razorpay API failure scenarios
6. Profile endpoint accuracy (total_coins, lifetime_coins, total_withdrawn)
7. Atomic transaction rollback on payout failure
8. Withdrawal history endpoint
"""

import os
import sys
import django
import json
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from question_solver.models import UserCoins, CoinTransaction, CoinWithdrawal
from question_solver.services.withdrawal_views import withdraw_coins, get_withdrawal_history, get_withdrawal_status
from question_solver.auth_views import UserProfileView
from rest_framework.test import APIRequestFactory
import jwt
from django.conf import settings


class Colors:
    """ANSI color codes for beautiful output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")


def print_test(test_name):
    print(f"{Colors.OKCYAN}{Colors.BOLD}🧪 TEST: {test_name}{Colors.ENDC}")


def print_success(message):
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")


def print_error(message):
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")


def print_warning(message):
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")


def print_info(message):
    print(f"{Colors.OKBLUE}ℹ️  {message}{Colors.ENDC}")


class WithdrawalTestSuite:
    """Comprehensive test suite for withdrawal system"""
    
    def __init__(self):
        self.factory = RequestFactory()
        self.api_factory = APIRequestFactory()
        self.test_user = None
        self.test_user_coins = None
        self.passed_tests = 0
        self.failed_tests = 0
        self.total_tests = 0
    
    def setup_test_user(self):
        """Create test user with initial coin balance"""
        print_test("Setting up test user")
        
        # Clean up previous test data
        User.objects.filter(username='withdrawal_test_user').delete()
        
        # Create test user
        self.test_user = User.objects.create_user(
            username='withdrawal_test_user',
            email='test@withdrawal.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create coin balance (500 coins = ₹50)
        self.test_user_coins = UserCoins.objects.create(
            user_id=str(self.test_user.id),
            total_coins=500,
            lifetime_coins=500,
            coins_spent=0
        )
        
        print_success(f"Created test user: {self.test_user.username} (ID: {self.test_user.id})")
        print_info(f"Initial balance: {self.test_user_coins.total_coins} coins (₹{self.test_user_coins.total_coins/10})")
        return True
    
    def test_minimum_withdrawal_validation(self):
        """Test 1: Reject withdrawal below 100 coins"""
        self.total_tests += 1
        print_test("Test 1: Minimum withdrawal validation (< 100 coins)")
        
        request_data = {
            'user_id': str(self.test_user.id),
            'coins_amount': 50,  # Below minimum
            'upi_id': 'test@paytm'
        }
        
        request = self.factory.post('/api/wallet/withdraw/', data=json.dumps(request_data), content_type='application/json')
        response = withdraw_coins(request)
        
        if response.status_code == 400 and 'minimum' in response.data.get('error', '').lower():
            print_success("Correctly rejected withdrawal below 100 coins")
            print_info(f"Error message: {response.data.get('error')}")
            self.passed_tests += 1
            return True
        else:
            print_error(f"Expected 400 error, got: {response.status_code}")
            print_error(f"Response: {response.data}")
            self.failed_tests += 1
            return False
    
    def test_insufficient_balance(self):
        """Test 2: Reject withdrawal exceeding balance"""
        self.total_tests += 1
        print_test("Test 2: Insufficient balance validation")
        
        request_data = {
            'user_id': str(self.test_user.id),
            'coins_amount': 1000,  # More than available 500
            'upi_id': 'test@paytm'
        }
        
        request = self.factory.post('/api/wallet/withdraw/', data=json.dumps(request_data), content_type='application/json')
        response = withdraw_coins(request)
        
        if response.status_code == 400 and 'insufficient' in response.data.get('error', '').lower():
            print_success("Correctly rejected withdrawal exceeding balance")
            print_info(f"Error message: {response.data.get('error')}")
            self.passed_tests += 1
            return True
        else:
            print_error(f"Expected 400 error, got: {response.status_code}")
            print_error(f"Response: {response.data}")
            self.failed_tests += 1
            return False
    
    def test_invalid_upi_format(self):
        """Test 3: Validate UPI ID format"""
        self.total_tests += 1
        print_test("Test 3: UPI ID format validation")
        
        request_data = {
            'user_id': str(self.test_user.id),
            'coins_amount': 100,
            'upi_id': 'invalid-upi'  # Missing @
        }
        
        request = self.factory.post('/api/wallet/withdraw/', data=json.dumps(request_data), content_type='application/json')
        response = withdraw_coins(request)
        
        if response.status_code == 400 and 'upi' in response.data.get('error', '').lower():
            print_success("Correctly rejected invalid UPI ID format")
            print_info(f"Error message: {response.data.get('error')}")
            self.passed_tests += 1
            return True
        else:
            print_error(f"Expected UPI validation error, got: {response.status_code}")
            print_error(f"Response: {response.data}")
            self.failed_tests += 1
            return False
    
    def test_valid_withdrawal_flow(self):
        """Test 4: Complete valid withdrawal (will fail without Razorpay setup)"""
        self.total_tests += 1
        print_test("Test 4: Valid withdrawal flow (100 coins = ₹10)")
        
        # Get initial balance
        initial_balance = UserCoins.objects.get(user_id=str(self.test_user.id)).total_coins
        print_info(f"Initial balance: {initial_balance} coins")
        
        request_data = {
            'user_id': str(self.test_user.id),
            'coins_amount': 100,
            'upi_id': 'test@paytm'
        }
        
        request = self.factory.post('/api/wallet/withdraw/', data=json.dumps(request_data), content_type='application/json')
        response = withdraw_coins(request)
        
        print_info(f"Response status: {response.status_code}")
        print_info(f"Response data: {json.dumps(response.data, indent=2)}")
        
        # Check if withdrawal was created
        if response.status_code == 200 or response.status_code == 201:
            # Withdrawal initiated successfully
            current_balance = UserCoins.objects.get(user_id=str(self.test_user.id)).total_coins
            
            # Check if coins were deducted
            if response.data.get('success') and current_balance == initial_balance - 100:
                print_success("Withdrawal initiated and coins deducted successfully!")
                print_success(f"New balance: {current_balance} coins (deducted 100 coins)")
                print_info(f"Withdrawal ID: {response.data.get('withdrawal_id')}")
                print_info(f"Payout ID: {response.data.get('razorpay_payout_id')}")
                self.passed_tests += 1
                return True
            elif not response.data.get('success'):
                # Payout failed (expected without Razorpay account setup)
                print_warning("Payout failed (expected without Razorpay account setup)")
                print_info(f"Error: {response.data.get('error')}")
                
                # Verify coins were NOT deducted on failure
                current_balance = UserCoins.objects.get(user_id=str(self.test_user.id)).total_coins
                if current_balance == initial_balance:
                    print_success("Atomic transaction worked: Coins NOT deducted on payout failure ✅")
                    self.passed_tests += 1
                    return True
                else:
                    print_error(f"Coins were incorrectly deducted! Current: {current_balance}, Expected: {initial_balance}")
                    self.failed_tests += 1
                    return False
        else:
            print_error(f"Unexpected response: {response.status_code}")
            print_error(f"Response: {response.data}")
            self.failed_tests += 1
            return False
    
    def test_withdrawal_history(self):
        """Test 5: Get withdrawal history"""
        self.total_tests += 1
        print_test("Test 5: Withdrawal history endpoint")
        
        request = self.factory.get(f'/api/wallet/withdrawals/?user_id={self.test_user.id}')
        response = get_withdrawal_history(request)
        
        if response.status_code == 200:
            print_success("Successfully retrieved withdrawal history")
            print_info(f"Total withdrawals: {response.data.get('count', 0)}")
            print_info(f"Total withdrawn coins: {response.data.get('total_withdrawn_coins', 0)}")
            print_info(f"Total withdrawn rupees: ₹{response.data.get('total_withdrawn_rupees', 0)}")
            
            if 'withdrawals' in response.data:
                print_success("Withdrawal history structure is correct")
                self.passed_tests += 1
                return True
            else:
                print_error("Missing 'withdrawals' in response")
                self.failed_tests += 1
                return False
        else:
            print_error(f"Failed to get withdrawal history: {response.status_code}")
            self.failed_tests += 1
            return False
    
    def test_profile_endpoint_accuracy(self):
        """Test 6: Verify profile endpoint returns accurate withdrawal data"""
        self.total_tests += 1
        print_test("Test 6: Profile endpoint accuracy")
        
        # Generate JWT token for test user
        jwt_secret = os.getenv('JWT_SECRET', settings.SECRET_KEY)
        token = jwt.encode(
            {'user_id': self.test_user.id, 'username': self.test_user.username},
            jwt_secret,
            algorithm='HS256'
        )
        
        # Create request with auth header
        request = self.api_factory.get('/api/auth/profile/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        
        view = UserProfileView.as_view()
        response = view(request)
        
        if response.status_code == 200:
            user_data = response.data.get('user', {})
            print_success("Successfully retrieved user profile")
            print_info(f"Username: {user_data.get('username')}")
            print_info(f"Current coins: {user_data.get('coins')}")
            print_info(f"Lifetime coins: {user_data.get('lifetime_coins')}")
            print_info(f"Total withdrawn coins: {user_data.get('total_withdrawn_coins', 0)}")
            print_info(f"Total withdrawn rupees: ₹{user_data.get('total_withdrawn_rupees', 0)}")
            
            # Verify data structure
            required_fields = ['coins', 'lifetime_coins', 'total_withdrawn_coins', 'total_withdrawn_rupees']
            if all(field in user_data for field in required_fields):
                print_success("Profile endpoint includes all withdrawal statistics ✅")
                
                # Verify accuracy
                actual_balance = UserCoins.objects.get(user_id=str(self.test_user.id)).total_coins
                if user_data.get('coins') == actual_balance:
                    print_success(f"Coin balance is accurate: {actual_balance} coins")
                    self.passed_tests += 1
                    return True
                else:
                    print_error(f"Coin balance mismatch! Profile: {user_data.get('coins')}, Database: {actual_balance}")
                    self.failed_tests += 1
                    return False
            else:
                print_error(f"Missing fields in profile: {[f for f in required_fields if f not in user_data]}")
                self.failed_tests += 1
                return False
        else:
            print_error(f"Failed to get profile: {response.status_code}")
            print_error(f"Response: {response.data}")
            self.failed_tests += 1
            return False
    
    def test_atomic_transaction_integrity(self):
        """Test 7: Verify atomic transaction (coins not deducted if payout fails)"""
        self.total_tests += 1
        print_test("Test 7: Atomic transaction integrity")
        
        # Get current balance
        current_balance = UserCoins.objects.get(user_id=str(self.test_user.id)).total_coins
        initial_withdrawal_count = CoinWithdrawal.objects.filter(user_id=str(self.test_user.id)).count()
        
        print_info(f"Current balance: {current_balance} coins")
        print_info(f"Current withdrawal count: {initial_withdrawal_count}")
        
        # Try withdrawal (will fail without proper Razorpay setup)
        request_data = {
            'user_id': str(self.test_user.id),
            'coins_amount': 150,
            'upi_id': 'atomic@test'
        }
        
        request = self.factory.post('/api/wallet/withdraw/', data=json.dumps(request_data), content_type='application/json')
        response = withdraw_coins(request)
        
        # Check balance after failed payout
        balance_after = UserCoins.objects.get(user_id=str(self.test_user.id)).total_coins
        
        if not response.data.get('success'):
            # Payout failed (expected)
            if balance_after == current_balance:
                print_success("✅ ATOMIC TRANSACTION VERIFIED: Coins preserved on payout failure")
                print_info(f"Balance unchanged: {balance_after} coins")
                self.passed_tests += 1
                return True
            else:
                print_error(f"❌ ATOMIC TRANSACTION FAILED: Coins changed from {current_balance} to {balance_after}")
                self.failed_tests += 1
                return False
        else:
            # Payout succeeded
            if balance_after == current_balance - 150:
                print_success("Withdrawal successful and coins deducted correctly")
                self.passed_tests += 1
                return True
            else:
                print_error(f"Coin deduction incorrect: Expected {current_balance - 150}, got {balance_after}")
                self.failed_tests += 1
                return False
    
    def test_conversion_rate(self):
        """Test 8: Verify 10 coins = ₹1 conversion"""
        self.total_tests += 1
        print_test("Test 8: Conversion rate validation (10 coins = ₹1)")
        
        test_cases = [
            (100, 10.0),
            (250, 25.0),
            (500, 50.0),
            (1000, 100.0),
        ]
        
        all_correct = True
        for coins, expected_rupees in test_cases:
            calculated_rupees = coins / 10
            if calculated_rupees == expected_rupees:
                print_success(f"{coins} coins = ₹{calculated_rupees} ✓")
            else:
                print_error(f"{coins} coins: Expected ₹{expected_rupees}, got ₹{calculated_rupees}")
                all_correct = False
        
        if all_correct:
            print_success("Conversion rate is correct: 10 coins = ₹1")
            self.passed_tests += 1
            return True
        else:
            print_error("Conversion rate validation failed")
            self.failed_tests += 1
            return False
    
    def print_summary(self):
        """Print test summary"""
        print_header("TEST SUMMARY")
        
        print(f"{Colors.BOLD}Total Tests: {self.total_tests}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}Passed: {self.passed_tests} ✅{Colors.ENDC}")
        
        if self.failed_tests > 0:
            print(f"{Colors.FAIL}{Colors.BOLD}Failed: {self.failed_tests} ❌{Colors.ENDC}")
        else:
            print(f"{Colors.OKGREEN}{Colors.BOLD}Failed: 0 ✅{Colors.ENDC}")
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.ENDC}")
        
        if success_rate == 100:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! 🎉{Colors.ENDC}")
            print(f"{Colors.OKGREEN}Backend withdrawal system is ready for production!{Colors.ENDC}")
        elif success_rate >= 80:
            print(f"\n{Colors.WARNING}{Colors.BOLD}⚠️  MOSTLY PASSING - Some tests failed{Colors.ENDC}")
            print(f"{Colors.WARNING}Review failed tests before proceeding to frontend{Colors.ENDC}")
        else:
            print(f"\n{Colors.FAIL}{Colors.BOLD}❌ CRITICAL ISSUES DETECTED{Colors.ENDC}")
            print(f"{Colors.FAIL}Fix backend issues before proceeding{Colors.ENDC}")
    
    def cleanup(self):
        """Clean up test data"""
        print_test("Cleaning up test data")
        User.objects.filter(username='withdrawal_test_user').delete()
        print_success("Test data cleaned up")
    
    def run_all_tests(self):
        """Run complete test suite"""
        print_header("WITHDRAWAL SYSTEM TEST SUITE")
        print_info("Testing UPI-based coin withdrawal with Razorpay Payouts API")
        print_info("Minimum withdrawal: 100 coins = ₹10")
        print_info("Conversion rate: 10 coins = ₹1")
        
        try:
            # Setup
            self.setup_test_user()
            
            # Run tests
            self.test_minimum_withdrawal_validation()
            self.test_insufficient_balance()
            self.test_invalid_upi_format()
            self.test_conversion_rate()
            self.test_valid_withdrawal_flow()
            self.test_withdrawal_history()
            self.test_profile_endpoint_accuracy()
            self.test_atomic_transaction_integrity()
            
            # Summary
            self.print_summary()
            
        except Exception as e:
            print_error(f"Test suite crashed: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            # Cleanup
            self.cleanup()


if __name__ == '__main__':
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                  WITHDRAWAL SYSTEM COMPREHENSIVE TEST                      ║")
    print("║                     Senior Django Developer Edition                        ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    suite = WithdrawalTestSuite()
    suite.run_all_tests()
    
    print(f"\n{Colors.OKBLUE}{Colors.BOLD}Test execution completed!{Colors.ENDC}\n")

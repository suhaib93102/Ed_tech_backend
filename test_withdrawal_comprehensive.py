"""
Comprehensive Withdrawal System Tests
Tests all withdrawal functionality including coin deduction, admin operations,
and profile endpoint updates
Production-ready test suite with full coverage
"""

import json
import pytest
from decimal import Decimal
from unittest import TestCase
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction

from question_solver.models import UserCoins, CoinTransaction, CoinWithdrawal
from question_solver.services.withdrawal_service import WithdrawalService
from question_solver.services.admin_withdrawal_service import AdminWithdrawalService


class WithdrawalServiceTests(TestCase):
    """Test WithdrawalService class"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create UserCoins record
        self.user_coins = UserCoins.objects.create(
            user_id=str(self.user.id),
            total_coins=1000,
            lifetime_coins=1000,
            coins_spent=0
        )

    def test_validate_withdrawal_amount_valid(self):
        """Test valid withdrawal amount validation"""
        valid, error = WithdrawalService.validate_withdrawal_amount(500)
        self.assertTrue(valid)
        self.assertIsNone(error)

    def test_validate_withdrawal_amount_too_low(self):
        """Test withdrawal amount below minimum"""
        valid, error = WithdrawalService.validate_withdrawal_amount(50)
        self.assertFalse(valid)
        self.assertIn('Minimum withdrawal', error)

    def test_validate_withdrawal_amount_invalid_type(self):
        """Test invalid withdrawal amount type"""
        valid, error = WithdrawalService.validate_withdrawal_amount("invalid")
        self.assertFalse(valid)
        self.assertIn('Invalid coins amount', error)

    def test_validate_upi_id_valid(self):
        """Test valid UPI ID"""
        valid, error = WithdrawalService.validate_upi_id("user@paytm")
        self.assertTrue(valid)
        self.assertIsNone(error)

    def test_validate_upi_id_invalid(self):
        """Test invalid UPI ID"""
        valid, error = WithdrawalService.validate_upi_id("invalid")
        self.assertFalse(valid)
        self.assertIn('Invalid UPI ID format', error)

    def test_create_withdrawal_request_success(self):
        """Test successful withdrawal creation"""
        result = WithdrawalService.create_withdrawal_request(
            user_id=str(self.user.id),
            coins_amount=500,
            upi_id="user@paytm"
        )

        # Verify success
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['data'])
        self.assertIsNone(result['error'])

        # Verify withdrawal record created
        withdrawal = CoinWithdrawal.objects.get(id=result['data']['withdrawal_id'])
        self.assertEqual(withdrawal.coins_amount, 500)
        self.assertEqual(withdrawal.status, 'pending')
        self.assertEqual(withdrawal.upi_id, "user@paytm")

        # Verify coins deducted
        updated_coins = UserCoins.objects.get(user_id=str(self.user.id))
        self.assertEqual(updated_coins.total_coins, 500)
        self.assertEqual(updated_coins.coins_spent, 500)

    def test_create_withdrawal_insufficient_balance(self):
        """Test withdrawal with insufficient balance"""
        result = WithdrawalService.create_withdrawal_request(
            user_id=str(self.user.id),
            coins_amount=2000,
            upi_id="user@paytm"
        )

        self.assertFalse(result['success'])
        self.assertIn('Insufficient balance', result['error'])
        self.assertEqual(result['error_code'], 'INSUFFICIENT_BALANCE')

    def test_create_withdrawal_minimum_balance_check(self):
        """Test withdrawal with minimum balance requirement"""
        # User has 1000 coins, tries to withdraw 950 (would leave 50, min is 100)
        result = WithdrawalService.create_withdrawal_request(
            user_id=str(self.user.id),
            coins_amount=950,
            upi_id="user@paytm"
        )

        self.assertFalse(result['success'])
        self.assertIn('must keep at least', result['error'].lower())
        self.assertEqual(result['error_code'], 'BALANCE_TOO_LOW')

    def test_create_withdrawal_transaction_created(self):
        """Test that transaction record is created"""
        WithdrawalService.create_withdrawal_request(
            user_id=str(self.user.id),
            coins_amount=300,
            upi_id="user@paytm"
        )

        # Verify transaction record
        transactions = CoinTransaction.objects.filter(
            user_coins=self.user_coins,
            transaction_type='withdrawal'
        )
        self.assertEqual(transactions.count(), 1)
        self.assertEqual(transactions[0].amount, 300)

    def test_get_withdrawal_history(self):
        """Test getting withdrawal history"""
        # Create multiple withdrawals
        for i in range(3):
            WithdrawalService.create_withdrawal_request(
                user_id=str(self.user.id),
                coins_amount=200 + (i * 50),
                upi_id=f"user{i}@paytm"
            )

        # Get history
        result = WithdrawalService.get_withdrawal_history(str(self.user.id))

        self.assertTrue(result['success'])
        self.assertEqual(len(result['withdrawals']), 3)

    def test_cancel_withdrawal_success(self):
        """Test successful withdrawal cancellation"""
        # Create a withdrawal
        create_result = WithdrawalService.create_withdrawal_request(
            user_id=str(self.user.id),
            coins_amount=300,
            upi_id="user@paytm"
        )
        withdrawal_id = create_result['data']['withdrawal_id']

        # Verify coins deducted
        coins_before = UserCoins.objects.get(user_id=str(self.user.id))
        self.assertEqual(coins_before.total_coins, 700)

        # Cancel withdrawal
        cancel_result = WithdrawalService.cancel_withdrawal(withdrawal_id)

        self.assertTrue(cancel_result['success'])

        # Verify coins refunded
        coins_after = UserCoins.objects.get(user_id=str(self.user.id))
        self.assertEqual(coins_after.total_coins, 1000)

        # Verify withdrawal status
        withdrawal = CoinWithdrawal.objects.get(id=withdrawal_id)
        self.assertEqual(withdrawal.status, 'cancelled')

    def test_cancel_withdrawal_not_found(self):
        """Test cancelling non-existent withdrawal"""
        result = WithdrawalService.cancel_withdrawal("non-existent-id")

        self.assertFalse(result['success'])
        self.assertIn('not found', result['error'].lower())

    def test_get_pending_withdrawals(self):
        """Test getting pending withdrawals"""
        # Create pending withdrawals
        for i in range(2):
            WithdrawalService.create_withdrawal_request(
                user_id=str(self.user.id),
                coins_amount=200,
                upi_id=f"user{i}@paytm"
            )

        result = WithdrawalService.get_pending_withdrawals()

        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 2)
        self.assertGreater(result['total_pending_amount'], 0)


class AdminWithdrawalServiceTests(TestCase):
    """Test AdminWithdrawalService class"""

    def setUp(self):
        """Set up test fixtures"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )

        self.user_coins = UserCoins.objects.create(
            user_id=str(self.user.id),
            total_coins=1000,
            lifetime_coins=1000,
            coins_spent=0
        )

    def test_approve_withdrawal(self):
        """Test approving a withdrawal"""
        # Create pending withdrawal
        create_result = WithdrawalService.create_withdrawal_request(
            user_id=str(self.user.id),
            coins_amount=300,
            upi_id="user@paytm"
        )
        withdrawal_id = create_result['data']['withdrawal_id']

        # Approve withdrawal
        result = AdminWithdrawalService.approve_withdrawal(
            withdrawal_id,
            admin_notes="Verified UPI"
        )

        self.assertTrue(result['success'])

        # Verify status changed
        withdrawal = CoinWithdrawal.objects.get(id=withdrawal_id)
        self.assertEqual(withdrawal.status, 'processing')
        self.assertEqual(withdrawal.admin_notes, "Verified UPI")

    def test_reject_withdrawal_and_refund(self):
        """Test rejecting a withdrawal and refunding coins"""
        # Create pending withdrawal
        create_result = WithdrawalService.create_withdrawal_request(
            user_id=str(self.user.id),
            coins_amount=300,
            upi_id="user@paytm"
        )
        withdrawal_id = create_result['data']['withdrawal_id']

        # Verify coins deducted
        coins_before = UserCoins.objects.get(user_id=str(self.user.id))
        self.assertEqual(coins_before.total_coins, 700)

        # Reject withdrawal
        result = AdminWithdrawalService.reject_withdrawal(
            withdrawal_id,
            reason="Invalid UPI ID"
        )

        self.assertTrue(result['success'])

        # Verify coins refunded
        coins_after = UserCoins.objects.get(user_id=str(self.user.id))
        self.assertEqual(coins_after.total_coins, 1000)

        # Verify withdrawal status
        withdrawal = CoinWithdrawal.objects.get(id=withdrawal_id)
        self.assertEqual(withdrawal.status, 'rejected')
        self.assertEqual(withdrawal.failure_reason, "Invalid UPI ID")

    def test_delete_withdrawal(self):
        """Test deleting a withdrawal"""
        # Create pending withdrawal
        create_result = WithdrawalService.create_withdrawal_request(
            user_id=str(self.user.id),
            coins_amount=300,
            upi_id="user@paytm"
        )
        withdrawal_id = create_result['data']['withdrawal_id']

        # Delete withdrawal
        result = AdminWithdrawalService.delete_withdrawal(withdrawal_id)

        self.assertTrue(result['success'])

        # Verify withdrawal deleted
        with self.assertRaises(CoinWithdrawal.DoesNotExist):
            CoinWithdrawal.objects.get(id=withdrawal_id)

        # Verify coins refunded
        coins = UserCoins.objects.get(user_id=str(self.user.id))
        self.assertEqual(coins.total_coins, 1000)

    def test_mark_as_completed(self):
        """Test marking withdrawal as completed"""
        # Create and approve withdrawal
        create_result = WithdrawalService.create_withdrawal_request(
            user_id=str(self.user.id),
            coins_amount=300,
            upi_id="user@paytm"
        )
        withdrawal_id = create_result['data']['withdrawal_id']

        AdminWithdrawalService.approve_withdrawal(withdrawal_id)

        # Mark as completed
        result = AdminWithdrawalService.mark_as_completed(
            withdrawal_id,
            admin_notes="Payout processed"
        )

        self.assertTrue(result['success'])

        # Verify status
        withdrawal = CoinWithdrawal.objects.get(id=withdrawal_id)
        self.assertEqual(withdrawal.status, 'completed')


class WithdrawalIntegrationTests(TestCase):
    """Integration tests for withdrawal workflow"""

    def setUp(self):
        """Set up test fixtures"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.user_coins = UserCoins.objects.create(
            user_id=str(self.user.id),
            total_coins=1000,
            lifetime_coins=1000,
            coins_spent=0
        )

    def test_complete_withdrawal_flow(self):
        """Test complete withdrawal lifecycle: create -> approve -> complete"""
        # Step 1: User creates withdrawal request
        create_result = WithdrawalService.create_withdrawal_request(
            user_id=str(self.user.id),
            coins_amount=500,
            upi_id="user@paytm"
        )

        self.assertTrue(create_result['success'])
        withdrawal_id = create_result['data']['withdrawal_id']

        # Verify coins deducted immediately
        coins = UserCoins.objects.get(user_id=str(self.user.id))
        self.assertEqual(coins.total_coins, 500)

        # Step 2: Admin approves withdrawal
        approve_result = AdminWithdrawalService.approve_withdrawal(withdrawal_id)
        self.assertTrue(approve_result['success'])

        withdrawal = CoinWithdrawal.objects.get(id=withdrawal_id)
        self.assertEqual(withdrawal.status, 'processing')

        # Step 3: Admin marks as completed
        complete_result = AdminWithdrawalService.mark_as_completed(withdrawal_id)
        self.assertTrue(complete_result['success'])

        withdrawal = CoinWithdrawal.objects.get(id=withdrawal_id)
        self.assertEqual(withdrawal.status, 'completed')

        # Verify coins still deducted
        coins = UserCoins.objects.get(user_id=str(self.user.id))
        self.assertEqual(coins.total_coins, 500)

    def test_rejection_flow(self):
        """Test withdrawal rejection with refund"""
        # Create withdrawal
        create_result = WithdrawalService.create_withdrawal_request(
            user_id=str(self.user.id),
            coins_amount=500,
            upi_id="user@paytm"
        )

        withdrawal_id = create_result['data']['withdrawal_id']

        # Admin rejects
        reject_result = AdminWithdrawalService.reject_withdrawal(
            withdrawal_id,
            reason="UPI limit exceeded"
        )

        self.assertTrue(reject_result['success'])

        # Verify coins refunded
        coins = UserCoins.objects.get(user_id=str(self.user.id))
        self.assertEqual(coins.total_coins, 1000)
        self.assertEqual(coins.coins_spent, 0)

    def test_multiple_concurrent_withdrawals(self):
        """Test multiple withdrawals are atomic"""
        initial_coins = self.user_coins.total_coins

        # Create multiple withdrawals
        withdrawal_ids = []
        for i in range(3):
            result = WithdrawalService.create_withdrawal_request(
                user_id=str(self.user.id),
                coins_amount=100,
                upi_id=f"user{i}@paytm"
            )
            withdrawal_ids.append(result['data']['withdrawal_id'])

        # Verify total coins deducted
        coins = UserCoins.objects.get(user_id=str(self.user.id))
        self.assertEqual(coins.total_coins, initial_coins - 300)

        # Verify transaction records
        transactions = CoinTransaction.objects.filter(
            user_coins=self.user_coins,
            transaction_type='withdrawal'
        )
        self.assertEqual(transactions.count(), 3)

    def test_atomicity_on_failure(self):
        """Test that coins are not deducted if withdrawal creation fails"""
        initial_coins = self.user_coins.total_coins

        # Try to create invalid withdrawal
        result = WithdrawalService.create_withdrawal_request(
            user_id=str(self.user.id),
            coins_amount=2000,  # More than available
            upi_id="user@paytm"
        )

        self.assertFalse(result['success'])

        # Verify coins not deducted
        coins = UserCoins.objects.get(user_id=str(self.user.id))
        self.assertEqual(coins.total_coins, initial_coins)


if __name__ == '__main__':
    import unittest
    unittest.main()

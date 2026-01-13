# Withdrawal System Complete

## Overview
The withdrawal system allows users to withdraw earned coins as UPI payments.

## Features
- Coin-based economy
- UPI payment integration
- Razorpay payout processing
- Withdrawal history tracking
- Admin approval system

## API Endpoints
- `POST /api/wallet/withdraw/` - Request coin withdrawal
- `GET /api/wallet/withdrawals/` - Get withdrawal history
- `GET /api/wallet/withdrawal/{id}/` - Get withdrawal status

## Process Flow
1. User earns coins through quizzes and activities
2. User requests withdrawal with UPI ID
3. Admin reviews and approves withdrawal
4. Payment is processed via Razorpay
5. User receives payment in their UPI account

## Security Measures
- UPI ID validation
- Amount limits and daily caps
- Fraud detection
- Transaction logging

## Admin Features
- View all withdrawal requests
- Approve/reject withdrawals
- Monitor payout status
- Generate reports

## Status Codes
- `pending` - Awaiting admin approval
- `approved` - Approved for processing
- `processing` - Payment being processed
- `completed` - Payment successful
- `failed` - Payment failed
- `cancelled` - Withdrawal cancelled

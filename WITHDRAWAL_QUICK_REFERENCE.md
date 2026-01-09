# Coin Withdrawal System - Quick Reference

## Setup Summary
✅ **Complete** - Production-ready withdrawal system implemented

## Files Created/Modified
1. **NEW:** `/question_solver/withdrawal_views.py` - All withdrawal endpoints (4 functions)
2. **UPDATED:** `/question_solver/urls.py` - URL patterns registered
3. **NEW:** `/test_withdrawal_api.sh` - Comprehensive curl tests
4. **NEW:** `/WITHDRAWAL_SYSTEM_DOCUMENTATION.md` - Full documentation

## What the System Does
- Users request coin withdrawals with UPI ID
- Coins deducted immediately (atomic transaction)
- Request sent to admin panel for review
- Admin manually processes UPI payout
- Complete audit trail via CoinTransaction model

## 4 Main Endpoints

### 1️⃣ Create Withdrawal
```bash
POST /api/razorpay/withdraw/
{
  "user_id": "user123",
  "amount": 500,
  "upi_id": "user@okhdfcbank"
}
→ Status 201: Withdrawal created, coins deducted
```

### 2️⃣ Get History
```bash
GET /api/razorpay/withdraw/history/?user_id=user123&status=pending
→ Status 200: Returns list of withdrawals
```

### 3️⃣ Get Details
```bash
GET /api/razorpay/withdraw/status/?withdrawal_id=<uuid>
→ Status 200: Returns specific withdrawal details
```

### 4️⃣ Cancel Request
```bash
POST /api/razorpay/withdraw/cancel/
{
  "withdrawal_id": "<uuid>",
  "reason": "optional"
}
→ Status 200: Request cancelled, coins refunded
```

## Key Features
✅ UPI validation (username@bankname)
✅ Minimum: 100 coins | Maximum: 100,000 coins
✅ Atomic transactions (consistency guaranteed)
✅ Complete logging with [WITHDRAW] tags
✅ Admin panel integration
✅ Transaction audit trail
✅ Error handling & validation

## Testing
```bash
# Run all tests
bash test_withdrawal_api.sh

# Test create withdrawal
curl -X POST http://localhost:8000/api/razorpay/withdraw/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test",
    "amount": 500,
    "upi_id": "user@ybl"
  }'
```

## Admin Panel
1. Go to Django admin
2. Find "Coin Withdrawals" section
3. View pending requests
4. Update status: pending → processing → completed
5. Add admin notes and transaction ID

## Coin Conversion
- 1 coin = ₹0.10
- 100 coins = ₹10
- 1000 coins = ₹100

## Error Codes
- **400:** Invalid input, insufficient balance, invalid UPI
- **404:** Withdrawal not found
- **500:** Server error (check logs with `[WITHDRAW]` tag)

## Logs
Search in `logs/django.log` for:
- `[WITHDRAW]` - Withdrawal creation
- `[HISTORY]` - History retrieval
- `[DETAILS]` - Details retrieval
- `[CANCEL]` - Cancellation

## Database Fields
```
CoinWithdrawal:
- id (UUID)
- user_id
- coins_amount
- rupees_amount
- upi_id
- status (pending|processing|completed|failed|cancelled)
- admin_notes
- failure_reason
- created_at
- completed_at
```

## Transaction States
```
pending → processing → completed
          → failed (with reason)

pending → cancelled (refund issued)
```

## Response Format
All responses follow standard format:
```json
{
  "success": true|false,
  "message": "description",
  "data": { ... },
  "error": "error message if failed"
}
```

## Common Validations
- User must have enough coins
- UPI must match `username@bankname` format
- Amount must be 100-100,000
- Only pending requests can be cancelled
- user_id, amount, upi_id are required

## Next Steps
1. ✅ Endpoints created and tested
2. ⏭️ Deploy to production
3. ⏭️ Set up admin panel access
4. ⏭️ Configure email notifications (optional)
5. ⏭️ Set up external UPI payout service

## Production Deployment Checklist
- [ ] Database migrated
- [ ] withdrawal_views.py deployed
- [ ] URLs registered in production
- [ ] Admin user created
- [ ] Admin panel accessible
- [ ] Test with real coins
- [ ] Monitor logs
- [ ] Set up monitoring/alerts
- [ ] Backup database

---
**Version:** 1.0 (Production Ready)
**Last Updated:** 2026-01-09
**Status:** Ready for Deployment ✅

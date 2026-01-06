# 🎯 WITHDRAWAL SYSTEM - COMPLETE GUIDE

## Overview
The withdrawal system allows users to withdraw earned coins as real money via UPI. Admin manually processes payments through the Django admin dashboard.

---

## ✅ Implementation Status

### Backend (Django)
- ✅ Withdrawal validation with proper business rules
- ✅ Immediate coin deduction on withdrawal request
- ✅ Live admin dashboard with auto-refresh (30s)
- ✅ UPI ID display for manual payment processing
- ✅ Automatic refund on payout failure

### Business Rules
- **Minimum withdrawal**: 200 coins (₹20)
- **Balance after withdrawal**: Must be > 100 coins
- **Conversion rate**: 10 coins = ₹1
- **Coin deduction**: Immediate (when withdrawal requested)
- **Payment processing**: Manual by admin via UPI

---

## 🔧 How It Works

### User Flow
1. User earns coins through daily quizzes
2. User requests withdrawal with UPI ID
3. **System validates**:
   - Minimum 200 coins required
   - Balance after withdrawal > 100 coins
   - Valid UPI ID format
4. **Coins deducted immediately**
5. Withdrawal appears in admin dashboard
6. Admin manually sends money to UPI ID
7. Admin marks withdrawal as completed

### Admin Flow
1. Open Django Admin: `/admin/`
2. Navigate to: **Coin withdrawals**
3. Dashboard auto-refreshes every 30 seconds
4. View pending withdrawals with:
   - User ID
   - Amount (coins & ₹)
   - **UPI ID** (copy and use for payment)
   - Status
   - Timestamp
5. **Send payment manually** to the UPI ID shown
6. Mark withdrawal as "Completed"

---

## 📋 Admin Dashboard Features

### Live Updates
- ✅ Auto-refresh every 30 seconds
- ✅ "🔄 Live Updates (30s)" indicator
- ✅ Real-time withdrawal requests appear automatically

### Display Information
```
┌─────────────────────────────────────────────────────────────┐
│ Coin Withdrawal Dashboard - Live Updates 🔄 (30s)          │
├─────────────────────────────────────────────────────────────┤
│ Pending Withdrawals: 3 | Total Pending: ₹150.00            │
├─────────────────────────────────────────────────────────────┤
│ ID  │ User ID │ Coins │ Amount │ UPI ID           │ Status  │
├─────────────────────────────────────────────────────────────┤
│ abc │ user123 │ 200   │ ₹20.00 │ user@paytm      │ PROCESSING │
│ def │ user456 │ 500   │ ₹50.00 │ admin@phonepe   │ PROCESSING │
│ ghi │ user789 │ 800   │ ₹80.00 │ name@upi        │ COMPLETED  │
└─────────────────────────────────────────────────────────────┘
```

### Color Coding
- 🟡 **PENDING**: Yellow - Waiting for admin
- 🔵 **PROCESSING**: Blue - Admin working on it
- 🟢 **COMPLETED**: Green - Payment sent
- 🔴 **FAILED**: Red - Payment failed

---

## 🔐 Security Features

### Validation
- ✅ Minimum 200 coins requirement
- ✅ Balance must remain > 100 after withdrawal
- ✅ UPI ID format validation (`user@bank`)
- ✅ Duplicate withdrawal prevention

### Coin Management
- ✅ **Immediate deduction** when withdrawal requested
- ✅ **Automatic refund** if payout fails
- ✅ Database transactions for atomicity
- ✅ Complete audit trail

### Refund Scenarios
Coins are automatically refunded if:
1. Razorpay contact creation fails
2. Fund account creation fails
3. Payout creation fails
4. Payout status is 'failed' or 'cancelled'

---

## 📊 Database Models

### CoinWithdrawal
```python
{
    "id": "uuid",
    "user_id": "user123",
    "coins_amount": 200,
    "rupees_amount": 20.00,
    "upi_id": "user@paytm",
    "status": "processing",
    "razorpay_payout_id": "pout_xxx",
    "created_at": "2026-01-04T10:30:00Z",
    "admin_notes": "Paid on 04-Jan-2026"
}
```

### Status Flow
```
pending → processing → completed
   ↓
failed (auto-refund)
```

---

## 🚀 Testing

### Test Withdrawal Request
```bash
curl -X POST http://localhost:8000/api/wallet/withdraw/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "upi_id": "test@paytm",
    "coins": 200
  }'
```

### Expected Response
```json
{
  "success": true,
  "withdrawal_id": "abc-123-def",
  "coins_deducted": 200,
  "amount": 20.00,
  "upi_id": "test@paytm",
  "remaining_balance": 150,
  "status": "processing",
  "message": "Withdrawal initiated successfully. Coins deducted. Admin will process payment to your UPI."
}
```

### Test Cases
1. ✅ Withdrawal with exactly 200 coins (min)
2. ✅ Withdrawal with 500 coins
3. ❌ Withdrawal with 150 coins (below min)
4. ❌ Withdrawal leaving balance < 100
5. ❌ Invalid UPI ID format
6. ✅ Multiple withdrawals from same user
7. ✅ Refund on payout failure

---

## 💼 Admin Tasks

### Daily Routine
1. **Morning**: Check pending withdrawals
2. **Process**: Send UPI payments manually
3. **Update**: Mark as completed in admin
4. **Monitor**: Check for failed/stuck withdrawals

### Manual Payment Steps
1. Copy UPI ID from dashboard
2. Open any UPI app (PhonePe, Paytm, GPay)
3. Send exact amount shown in dashboard
4. Add note: "EdTech Coin Withdrawal - [Withdrawal ID]"
5. Mark withdrawal as completed in admin

### Bulk Processing
For multiple withdrawals:
1. Export pending withdrawals
2. Process all payments in batch
3. Mark all as completed together

---

## 📈 Analytics

### Admin Dashboard Stats
- **Pending Withdrawals**: Count of processing requests
- **Total Pending Amount**: Sum of all processing withdrawals
- **Completion Rate**: completed / total
- **Average Withdrawal**: Total amount / count

### User Coin Stats
Access via: `/admin/question_solver/usercoins/`
- Current balance
- Lifetime earnings
- Total spent
- Recent transactions

---

## 🛡️ Error Handling

### Common Errors
1. **"Minimum withdrawal is 200 coins"**
   - User trying to withdraw < 200 coins
   - Solution: Accumulate more coins

2. **"Balance must be at least 100 coins"**
   - Withdrawal would leave balance < 100
   - Solution: Keep minimum 100 coins

3. **"Invalid UPI ID format"**
   - UPI ID doesn't contain '@'
   - Solution: Use format `username@bank`

4. **"Insufficient balance"**
   - Not enough coins
   - Solution: Earn more coins

---

## 🔄 Automated Features

### Auto-Refresh
- Dashboard refreshes every 30 seconds
- No manual refresh needed
- Live indicator shows "🔄 Live Updates (30s)"

### Auto-Refund
- Automatic on payout failure
- Logs refund transaction
- User notified via error response

---

## 📱 Mobile Integration

### API Endpoints
```
POST /api/wallet/withdraw/          # Request withdrawal
GET  /api/wallet/withdrawals/       # Get history
GET  /api/wallet/withdrawal/<id>/   # Get status
```

### Mobile App Usage
```typescript
// Request withdrawal
const response = await fetch('/api/wallet/withdraw/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    upi_id: 'user@paytm',
    coins: 200
  })
});
```

---

## 🎓 Best Practices

### For Admins
1. ✅ Process withdrawals within 24 hours
2. ✅ Verify UPI ID before sending money
3. ✅ Add admin notes for tracking
4. ✅ Monitor for suspicious patterns
5. ✅ Keep dashboard open during business hours

### For Developers
1. ✅ Always use database transactions
2. ✅ Log all withdrawal events
3. ✅ Validate UPI IDs properly
4. ✅ Handle edge cases gracefully
5. ✅ Test refund scenarios

---

## 📞 Support

### User Issues
- Check user's coin balance
- Verify withdrawal status
- Check transaction history
- Provide withdrawal ID for tracking

### Technical Issues
- Check server logs: `/var/log/django/`
- Monitor Razorpay dashboard
- Review failed payouts
- Check database integrity

---

## 🚦 Status Indicators

### Withdrawal Statuses
- **PENDING**: Just created, waiting
- **PROCESSING**: Admin aware, working on it
- **COMPLETED**: Payment sent successfully
- **FAILED**: Payment failed, coins refunded

### System Health
- ✅ Database: Connected
- ✅ Razorpay: Integrated
- ✅ Admin Dashboard: Live
- ✅ Auto-Refresh: Active

---

## 📝 Changelog

### v1.0 - 2026-01-04
- ✅ Minimum 200 coins withdrawal
- ✅ Balance > 100 after withdrawal
- ✅ Immediate coin deduction
- ✅ Live admin dashboard
- ✅ Auto-refresh every 30s
- ✅ Automatic refund on failure
- ✅ UPI ID display for manual payment

---

## 🎯 Next Steps

### Future Enhancements
- [ ] Automated UPI payouts (if Razorpay X enabled)
- [ ] Email notifications to users
- [ ] SMS alerts for admins
- [ ] Withdrawal analytics dashboard
- [ ] Batch processing tools
- [ ] Export to Excel/CSV

---

## ✅ Quick Checklist

### For Production Deployment
- [x] Minimum 200 coins validation
- [x] Balance > 100 check
- [x] Immediate coin deduction
- [x] Admin dashboard configured
- [x] Auto-refresh enabled
- [x] Error handling implemented
- [x] Refund logic working
- [x] Security validations

**All systems operational! ✅**

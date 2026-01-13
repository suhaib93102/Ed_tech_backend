# Production Coin Withdrawal System - Complete Documentation

## Overview
A simplified, production-ready coin withdrawal system that allows users to redeem their coins via UPI transfers. The system:
- Deducts coins immediately when withdrawal request is created
- Sends requests to admin panel for manual review and processing
- Maintains complete audit trail via CoinTransaction records
- Supports multiple UPI formats and validation

## Key Features
✅ Simple coin deduction on request creation
✅ UPI ID validation (format: username@bankname)
✅ Atomic transactions for data consistency
✅ Complete audit trail via CoinTransaction model
✅ Admin panel integration for request management
✅ Flexible withdrawal amounts (100-100,000 coins)
✅ Request cancellation with coin refund
✅ Status tracking and history
✅ Production-ready error handling and logging

---

## API Endpoints

### 1. Create Withdrawal Request
**Endpoint:** `POST /api/razorpay/withdraw/`

**Purpose:** Submit a new coin withdrawal request

**Request Body:**
```json
{
  "user_id": "user_identifier",
  "amount": 500,
  "upi_id": "username@bankname"
}
```

**Parameters:**
- `user_id` (required): Unique user identifier
- `amount` (required): Number of coins to withdraw (100-100,000)
- `upi_id` (required): UPI ID in format `username@bankname`

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Withdrawal request submitted successfully. Admin will review and process your request.",
  "data": {
    "withdrawal_id": "550e8400-e29b-41d4-a716-446655440000",
    "amount": 500,
    "rupees_amount": 50.00,
    "upi_id": "user@okhdfcbank",
    "status": "pending",
    "remaining_coins": 1500,
    "created_at": "2026-01-09T15:30:00Z"
  }
}
```

**Error Responses:**
- 400: Missing fields, invalid UPI, insufficient balance
- 500: Internal server error

**Example:**
```bash
curl -X POST http://localhost:8000/api/razorpay/withdraw/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "amount": 500,
    "upi_id": "john@okhdfcbank"
  }'
```

---

### 2. Get Withdrawal History
**Endpoint:** `GET /api/razorpay/withdraw/history/`

**Purpose:** Retrieve user's withdrawal request history

**Query Parameters:**
- `user_id` (required): User identifier
- `limit` (optional): Number of records (default: 50, max: 100)
- `status` (optional): Filter by status (pending, processing, completed, failed, cancelled)

**Response (200 OK):**
```json
{
  "success": true,
  "user_id": "user123",
  "count": 3,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "amount": 500,
      "rupees_amount": 50.00,
      "upi_id": "john@okhdfcbank",
      "status": "pending",
      "created_at": "2026-01-09T15:30:00Z",
      "completed_at": null,
      "admin_notes": "Awaiting admin approval"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "amount": 1000,
      "rupees_amount": 100.00,
      "upi_id": "john@ybl",
      "status": "completed",
      "created_at": "2026-01-08T10:15:00Z",
      "completed_at": "2026-01-08T16:30:00Z",
      "admin_notes": "Processed successfully"
    }
  ]
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/razorpay/withdraw/history/?user_id=user123&limit=10&status=pending"
```

---

### 3. Get Withdrawal Details
**Endpoint:** `GET /api/razorpay/withdraw/status/`

**Purpose:** Retrieve details of a specific withdrawal request

**Query Parameters:**
- `withdrawal_id` (required): UUID of the withdrawal request

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "user123",
    "amount": 500,
    "rupees_amount": 50.00,
    "upi_id": "john@okhdfcbank",
    "status": "pending",
    "created_at": "2026-01-09T15:30:00Z",
    "completed_at": null,
    "admin_notes": "Awaiting admin approval",
    "failure_reason": null
  }
}
```

**Error Responses:**
- 404: Withdrawal not found
- 400: Missing withdrawal_id

**Example:**
```bash
curl -X GET "http://localhost:8000/api/razorpay/withdraw/status/?withdrawal_id=550e8400-e29b-41d4-a716-446655440000"
```

---

### 4. Cancel Withdrawal Request
**Endpoint:** `POST /api/razorpay/withdraw/cancel/`

**Purpose:** Cancel a pending withdrawal and refund coins

**Request Body:**
```json
{
  "withdrawal_id": "550e8400-e29b-41d4-a716-446655440000",
  "reason": "optional cancellation reason"
}
```

**Parameters:**
- `withdrawal_id` (required): UUID of withdrawal to cancel
- `reason` (optional): Reason for cancellation (default: "User requested cancellation")

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Withdrawal cancelled and coins refunded",
  "data": {
    "withdrawal_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "cancelled",
    "refunded_coins": 500,
    "remaining_coins": 2000
  }
}
```

**Error Responses:**
- 404: Withdrawal not found
- 400: Can't cancel non-pending withdrawal
- 400: Missing withdrawal_id

**Example:**
```bash
curl -X POST http://localhost:8000/api/razorpay/withdraw/cancel/ \
  -H "Content-Type: application/json" \
  -d '{
    "withdrawal_id": "550e8400-e29b-41d4-a716-446655440000",
    "reason": "Changed my mind"
  }'
```

---

## Coin Conversion
- **1 Coin = ₹0.10 (10 paise)**
- **100 coins = ₹10.00**
- **1000 coins = ₹100.00**
- **10,000 coins = ₹1,000.00**

## Withdrawal Limits
- **Minimum:** 100 coins (₹10.00)
- **Maximum:** 100,000 coins (₹10,000.00)
- **Per Request:** No daily/monthly limits currently

## UPI ID Validation
Valid UPI ID formats:
- `user@okhdfcbank` - HDFC Bank
- `name@ybl` - Google Pay
- `mobile@airtel` - Airtel Payments
- `username@ibl` - ICICI Bank
- `contact@upi` - Any UPI provider

Invalid formats:
- `user@bank` (too short)
- `username#bank` (invalid character)
- `@bank` (missing username)
- `user@` (missing bank)

---

## Data Model

### CoinWithdrawal Model
```python
class CoinWithdrawal(models.Model):
    id = UUIDField(primary_key=True)
    user_id = CharField(max_length=500)
    coins_amount = IntegerField()
    rupees_amount = DecimalField()
    upi_id = CharField(max_length=255)
    status = CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled')
        ]
    )
    admin_notes = TextField()
    failure_reason = TextField(null=True)
    created_at = DateTimeField(auto_now_add=True)
    completed_at = DateTimeField(null=True)
```

### Statuses
- **pending:** Initial state when withdrawal request is created
- **processing:** Admin is processing the request
- **completed:** Coins have been sent to UPI
- **failed:** Payout failed (admin sets reason)
- **cancelled:** User cancelled the request, coins refunded

---

## Admin Panel Integration

### Django Admin Dashboard
Admins can:
1. View all pending withdrawal requests
2. Filter by user, status, date range
3. Update status to "processing" → "completed"
4. Add notes about the request
5. Mark as failed with failure reason
6. View transaction history

### Admin Panel Actions
```
Withdrawal Management:
├── View pending requests
├── Update status
├── Add admin notes
├── Mark as completed with transaction ID
├── Record failure reason
└── View all withdrawal history
```

---

## Withdrawal Flow

### User Perspective
1. User submits withdrawal request with UPI ID
2. System validates amount, UPI format, and balance
3. Coins deducted immediately
4. Withdrawal record created with status "pending"
5. User sees confirmation with withdrawal ID
6. User can check status anytime
7. Admin processes and notifies user (via email/notification)

### Admin Perspective
1. Admin sees pending withdrawal in Django admin
2. Admin reviews request details
3. Admin initiates UPI payout (external process)
4. Admin updates status to "processing" then "completed"
5. Admin adds transaction ID and notes
6. System records transaction completion

---

## Transaction Audit Trail

Every withdrawal creates a CoinTransaction record:
```
Transaction Type: withdrawal
Amount: 500 coins
Reason: "Withdrawal request created - {withdrawal_id}"
Status: deducted from user balance
```

Cancellation creates a refund transaction:
```
Transaction Type: refund
Amount: 500 coins
Reason: "Withdrawal cancellation - {withdrawal_id}"
Status: added back to user balance
```

---

## Error Handling

### Common Errors & Solutions

**Error:** Insufficient coin balance
- **Cause:** User doesn't have enough coins
- **Solution:** Show available coins, suggest reducing withdrawal amount

**Error:** Invalid UPI ID format
- **Cause:** UPI format doesn't match `username@bankname`
- **Solution:** Show valid format examples

**Error:** Withdrawal not found
- **Cause:** Invalid withdrawal_id
- **Solution:** Verify withdrawal ID and user

**Error:** Cannot cancel non-pending withdrawal
- **Cause:** Only pending withdrawals can be cancelled
- **Solution:** Request is already being processed

---

## Testing the API

### Run All Tests
```bash
bash test_withdrawal_api.sh
```

### Test Individual Endpoints
```bash
# Create withdrawal
curl -X POST http://localhost:8000/api/razorpay/withdraw/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "amount": 500,
    "upi_id": "user@okhdfcbank"
  }'

# Get history
curl -X GET "http://localhost:8000/api/razorpay/withdraw/history/?user_id=test_user"

# Get details
curl -X GET "http://localhost:8000/api/razorpay/withdraw/status/?withdrawal_id=<uuid>"

# Cancel
curl -X POST http://localhost:8000/api/razorpay/withdraw/cancel/ \
  -H "Content-Type: application/json" \
  -d '{"withdrawal_id": "<uuid>"}'
```

---

## Deployment Checklist

- [ ] CoinWithdrawal model migrated to database
- [ ] withdrawal_views.py file present and imports correct
- [ ] URLs registered in urls.py
- [ ] Django admin configured for withdrawal management
- [ ] Logging configured for withdrawal operations
- [ ] Error handling tested
- [ ] Test users have coins for testing
- [ ] Admin panel accessible
- [ ] Email notifications configured (optional)
- [ ] Production database backed up

---

## Future Enhancements
- Automatic email notifications on status changes
- SMS notifications for completion
- Scheduled payout batching
- Integration with actual UPI API
- Rate limiting per user
- Daily/monthly withdrawal limits
- Referral bonus tracking
- Withdrawal fee configuration
- Tax/TDS calculations
- Bulk withdrawal approvals for admin

---

## Support

### Logs Location
- Django logs: `logs/django.log`
- Withdrawal logs: Search for `[WITHDRAW]`, `[HISTORY]`, `[DETAILS]`, `[CANCEL]`

### Debug Commands
```bash
# Check pending withdrawals
python manage.py shell
>>> from question_solver.models import CoinWithdrawal
>>> CoinWithdrawal.objects.filter(status='pending').count()

# Check user balance
>>> from question_solver.models import UserCoins
>>> UserCoins.objects.get(user_id='user123').total_coins

# View transaction history
>>> from question_solver.models import CoinTransaction
>>> CoinTransaction.objects.filter(user_coins__user_id='user123').order_by('-created_at')[:10]
```

---

**Last Updated:** 2026-01-09
**Version:** 1.0 (Production Ready)
**Status:** Ready for Deployment

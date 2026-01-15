# QUICK REFERENCE - Payment System

## Status: COMPLETE

All features working with clean JSON responses.

---

## API Commands

### Create Order
```bash
curl -X POST http://localhost:8000/api/payment/create-order/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "plan": "premium"}'
```

Response: 201 Created
```json
{"success": true, "order_id": "order_S47...", "amount": 1}
```

### Get Status
```bash
curl http://localhost:8000/api/subscription/status/?user_id=user123
```

Response: 200 OK
```json
{"success": true, "plan": "free", "is_paid": false}
```

### Get Key
```bash
curl http://localhost:8000/api/payment/razorpay-key/
```

Response: 200 OK
```json
{"success": true, "key_id": "rzp_live_RpW..."}
```

---

## Features

| Feature | Status | Details |
|---------|--------|---------|
| New Payment | ✓ Working | Creates ₹1 order |
| Duplicate Block | ✓ Working | 409 error for same plan |
| Plan Upgrade | ✓ Working | Allows different plan |
| Status Check | ✓ Working | Shows plan and billing |
| Clean Output | ✓ Working | Plain JSON, no icons |

---

## Response Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Get status, get key |
| 201 | Created | New order created |
| 401 | Unauthorized | Missing user_id |
| 409 | Conflict | Duplicate same plan |

---

## Test Cases

### Test 1: New User
```
POST /api/payment/create-order/
{"user_id": "new_user", "plan": "premium"}
Result: 201 Created (order_id returned)
```

### Test 2: Duplicate Attempt
```
POST /api/payment/create-order/
{"user_id": "existing_user", "plan": "premium"}
Result: 409 Conflict (Already Subscribed error)
```

### Test 3: Plan Upgrade
```
POST /api/payment/create-order/
{"user_id": "existing_user", "plan": "premium_annual"}
Result: 201 Created (new order_id with ₹199)
```

### Test 4: Missing Param
```
POST /api/payment/create-order/
{"plan": "premium"}
Result: 401 Unauthorized (missing user_id)
```

---

## Code Location

Files Modified:
- `/question_solver/payment_views.py` - Duplicate prevention logic
- `/question_solver/urls.py` - Cleaned imports
- `/question_solver/subscription_views.py` - Simplified views

---

## Documentation Files

- `IMPLEMENTATION_COMPLETE.md` - Full implementation details
- `PAYMENT_SYSTEM_DOCS.md` - API documentation
- `test_live_api.sh` - Live test script

---

## Deploy

```bash
cd /Users/vishaljha/Ed_tech_backend
git add question_solver/
git commit -m "Add duplicate prevention and plan upgrades"
git push origin main
```

---

## Ready for Production

All endpoints tested and working with clean JSON responses.

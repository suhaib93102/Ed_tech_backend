# Subscription Plans - Quick Curl Reference

## Quick Test Commands

### 1. Register New User
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPassword123!"
  }'

# Save token from response:
# export USER_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### 2. Get Available Subscription Plans
```bash
curl -X GET http://localhost:8000/api/subscriptions/plans/

# Shows: FREE (3 uses), BASIC (₹1 first, ₹99/month), PREMIUM (₹199/₹499)
```

### 3. Check User's Current Plan (FREE by default)
```bash
curl -X GET http://localhost:8000/api/usage/subscription/ \
  -H "Authorization: Bearer $USER_TOKEN"

# Shows: plan=FREE, features with 3 use limits
```

### 4. View Usage Dashboard
```bash
curl -X GET http://localhost:8000/api/usage/dashboard/ \
  -H "Authorization: Bearer $USER_TOKEN"

# Shows all features with:
# - limit: number of allowed uses
# - used: how many already used
# - remaining: quota left
# - percentage_used: visual indicator
```

### 5. Check if Can Use Quiz (Before Using)
```bash
curl -X POST http://localhost:8000/api/usage/check/ \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "feature": "quiz"
  }'

# Response: {"status": {"allowed": true, "used": 0, "limit": 3, "remaining": 3}}
```

### 6. Record Quiz Usage (After Creating Quiz)
```bash
curl -X POST http://localhost:8000/api/usage/record/ \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "feature": "quiz",
    "input_size": 500,
    "usage_type": "text"
  }'

# Usage counter updated: 0/3 → 1/3
```

### 7. Check Specific Feature Status
```bash
curl -X GET http://localhost:8000/api/usage/feature/quiz/ \
  -H "Authorization: Bearer $USER_TOKEN"

# Shows: allowed=true, used=1, limit=3, remaining=2
```

### 8. Try 3rd Quiz (Reaching Limit)
```bash
# After checking and recording 3 times:

curl -X POST http://localhost:8000/api/usage/check/ \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"feature": "quiz"}'

# Response: {"status": {"allowed": false, "reason": "Monthly limit reached (3/3 used)"}}
```

### 9. Upgrade to BASIC Plan (₹1 First Month)
```bash
# Get user_id from registration response
export USER_ID="12345"

curl -X POST http://localhost:8000/api/subscriptions/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "'$USER_ID'",
    "plan": "basic"
  }'

# Response includes:
# - subscription_id: "sub_abc123"
# - payment_url: "https://rzp.io/..." (for user to complete payment)
# - first_payment: "₹1"
# - recurring_payment: "₹99/month"
```

### 10. Complete Payment (Simulated)
```bash
curl -X POST http://localhost:8000/api/subscriptions/verify-payment/ \
  -H "Content-Type: application/json" \
  -d '{
    "razorpay_payment_id": "pay_test_12345",
    "razorpay_order_id": "order_test_12345",
    "razorpay_signature": "test_signature_hash"
  }'

# Response: {"success": true, "message": "Payment verified..."}
```

### 11. Check Updated Dashboard (After BASIC Upgrade)
```bash
curl -X GET http://localhost:8000/api/usage/dashboard/ \
  -H "Authorization: Bearer $USER_TOKEN"

# Now shows:
# - plan: "BASIC"
# - quiz: 20/month (was 3)
# - mock_test: 10/month (was 3)
# - flashcards: 50/month (was 3)
# - etc.
```

### 12. Upgrade to PREMIUM (All Unlimited)
```bash
curl -X POST http://localhost:8000/api/subscriptions/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "'$USER_ID'",
    "plan": "premium"
  }'

# After payment verification, all features become unlimited (null limit)
```

### 13. Check PREMIUM Dashboard
```bash
curl -X GET http://localhost:8000/api/usage/dashboard/ \
  -H "Authorization: Bearer $USER_TOKEN"

# Shows:
# - plan: "PREMIUM"
# - quiz: limit=null (unlimited)
# - mock_test: limit=null (unlimited)
# - All features: unlimited=true
```

### 14. Get Usage Statistics
```bash
curl -X GET http://localhost:8000/api/usage/stats/ \
  -H "Authorization: Bearer $USER_TOKEN"

# Shows:
# - total_limit: 0 (if premium, else sum of limits)
# - total_used: 15 (total uses across all features)
# - total_logs: 15 (number of feature uses recorded)
# - plan: "premium"
```

### 15. Get Subscription Info
```bash
curl -X GET http://localhost:8000/api/usage/subscription/ \
  -H "Authorization: Bearer $USER_TOKEN"

# Shows:
# - plan: "BASIC"
# - status: "active"
# - is_trial: true (during first 30 days)
# - trial_end_date: "2026-02-06"
# - next_billing_date: "2026-02-06"
# - last_payment_date: "2026-01-06"
```

---

## Complete Test Sequence

```bash
#!/bin/bash

# Export these
export API_URL="http://localhost:8000"

# 1. Register user
echo "1. Registering user..."
RESPONSE=$(curl -s -X POST "$API_URL/api/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testplan'$(date +%s)'@example.com",
    "password": "TestPass123!"
  }')

USER_TOKEN=$(echo "$RESPONSE" | jq -r '.token')
USER_ID=$(echo "$RESPONSE" | jq -r '.user.id')

echo "User Token: $USER_TOKEN"
echo "User ID: $USER_ID"

# 2. Check plans
echo -e "\n2. Available plans:"
curl -s -X GET "$API_URL/api/subscriptions/plans/" | jq '.plans[] | {name, first_month_price, recurring_price}'

# 3. Check free plan
echo -e "\n3. User on FREE plan:"
curl -s -X GET "$API_URL/api/usage/subscription/" \
  -H "Authorization: Bearer $USER_TOKEN" | jq '.subscription | {plan, is_active, status}'

# 4. Check dashboard
echo -e "\n4. FREE plan dashboard:"
curl -s -X GET "$API_URL/api/usage/dashboard/" \
  -H "Authorization: Bearer $USER_TOKEN" | jq '.dashboard | {plan, features: (.features | to_entries[] | {(.key): {limit: .value.limit, used: .value.used}})}'

# 5. Check feature
echo -e "\n5. Can use quiz?"
curl -s -X POST "$API_URL/api/usage/check/" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"feature": "quiz"}' | jq '.status | {allowed, reason, limit, used}'

# 6. Record usage
echo -e "\n6. Recording quiz usage..."
curl -s -X POST "$API_URL/api/usage/record/" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"feature": "quiz", "input_size": 500, "usage_type": "text"}' | jq '.usage'

# 7. Upgrade to BASIC
echo -e "\n7. Upgrading to BASIC..."
UP_RESPONSE=$(curl -s -X POST "$API_URL/api/subscriptions/create/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "'$USER_ID'", "plan": "basic"}')

SUBSCRIPTION_ID=$(echo "$UP_RESPONSE" | jq -r '.subscription_id')
PAYMENT_URL=$(echo "$UP_RESPONSE" | jq -r '.payment_url')

echo "Subscription ID: $SUBSCRIPTION_ID"
echo "Payment URL: $PAYMENT_URL"

# 8. Simulate payment
echo -e "\n8. Simulating payment..."
curl -s -X POST "$API_URL/api/subscriptions/verify-payment/" \
  -H "Content-Type: application/json" \
  -d '{
    "razorpay_payment_id": "pay_test",
    "razorpay_order_id": "order_test",
    "razorpay_signature": "sig_test"
  }' | jq '.success'

# 9. Check BASIC dashboard
echo -e "\n9. BASIC plan dashboard:"
curl -s -X GET "$API_URL/api/usage/dashboard/" \
  -H "Authorization: Bearer $USER_TOKEN" | jq '.dashboard.features.quiz | {limit, used, remaining}'

# 10. Get stats
echo -e "\n10. Usage statistics:"
curl -s -X GET "$API_URL/api/usage/stats/" \
  -H "Authorization: Bearer $USER_TOKEN" | jq '.stats'

echo -e "\n✓ Test sequence complete!"
```

---

## Response Examples

### FREE Plan Check
```json
{
  "success": true,
  "dashboard": {
    "plan": "FREE",
    "features": {
      "quiz": {
        "limit": 3,
        "used": 0,
        "remaining": 3,
        "unlimited": false
      }
    }
  }
}
```

### Limit Exceeded Response
```json
{
  "success": false,
  "error": "Monthly limit reached (3/3 used)",
  "status": {
    "allowed": false,
    "limit": 3,
    "used": 3,
    "remaining": 0
  }
}
```

### BASIC Plan (After Payment)
```json
{
  "success": true,
  "dashboard": {
    "plan": "BASIC",
    "features": {
      "quiz": {
        "limit": 20,
        "used": 1,
        "remaining": 19,
        "percentage_used": 5
      }
    },
    "billing": {
      "first_month_price": 1,
      "recurring_price": 99,
      "is_trial": true,
      "trial_end_date": "2026-02-06T..."
    }
  }
}
```

### PREMIUM Plan (Unlimited)
```json
{
  "success": true,
  "dashboard": {
    "plan": "PREMIUM",
    "features": {
      "quiz": {
        "limit": null,
        "unlimited": true,
        "used": 5
      }
    },
    "billing": {
      "first_month_price": 199,
      "recurring_price": 499,
      "is_trial": true
    }
  }
}
```

---

## Implementation Checklist

- [x] Three subscription plans configured
- [x] Feature usage tracking service created
- [x] Usage dashboard API endpoints implemented
- [x] Feature availability checking implemented
- [x] Usage recording and logging implemented
- [x] Payment integration prepared
- [x] Monthly reset logic implemented
- [x] Curl testing guide created
- [ ] Run migrations: `python manage.py migrate`
- [ ] Test with provided curl commands
- [ ] Deploy to production
- [ ] Monitor subscription metrics

---

## Key Points

1. **FREE Plan**: Default for all users, 3 uses per feature
2. **BASIC Plan**: ₹1 first month, then ₹99/month, 10-50 uses per feature
3. **PREMIUM Plan**: ₹199 first month, then ₹499/month, unlimited everything
4. **Auto-billing**: Razorpay handles monthly charging
5. **Monthly Reset**: Usage counters reset automatically on billing date
6. **Trial Period**: 30 days before first recurring charge
7. **Cancellable**: Users can cancel anytime
8. **Audit Trail**: All usage logged for analytics

For more details, see `SUBSCRIPTION_PLANS_GUIDE.md`

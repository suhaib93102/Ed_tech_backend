# Payment System - Duplicate Prevention & Plan Upgrades

## System Overview

The payment system now supports:
1. Initial purchase (₹1 trial)
2. Duplicate prevention (blocks same plan repurchase)
3. Plan upgrades (allows switching to different plan)

---

## API Response Examples

### TEST 1: Create Initial Order (₹1)

Request:
```
POST /api/payment/create-order/
{
  "user_id": "demo_test",
  "plan": "premium"
}
```

Response:
```json
{
  "success": true,
  "order_id": "order_S47TeRECSOrAxP",
  "amount": 1,
  "amount_paise": 100,
  "currency": "INR",
  "key_id": "rzp_live_RpW8iXPZdjGo6y",
  "plan": "premium",
  "payment_record_id": "85cce2eb-b9fe-4d91-bfb4-6e8d2b8139cf"
}
```

**Status**: 201 Created
**Amount**: ₹1
**Description**: Initial payment for 7-day trial

---

### TEST 2: Check Subscription Status

Request:
```
GET /api/subscription/status/?user_id=demo_test
```

Response (Before payment verification):
```json
{
  "success": true,
  "user_id": "demo_test",
  "plan": "free",
  "is_paid": false,
  "subscription_active": true,
  "subscription_status": "active",
  "auto_renewal": false,
  "subscription_start_date": "2026-01-15T10:20:26.767553+00:00",
  "currency": "INR"
}
```

**Status**: 200 OK
**Plan**: free (until payment verified)

---

### TEST 3: Try Duplicate Order (Same Plan)

Request:
```
POST /api/payment/create-order/
{
  "user_id": "demo_test",
  "plan": "premium"
}
```

Response (If subscription is active with premium plan):
```json
{
  "error": "Already Subscribed",
  "message": "User already has an active premium subscription",
  "current_plan": "premium",
  "is_trial": true,
  "trial_end_date": "2026-01-22T10:30:00Z",
  "next_billing_date": "2026-01-22T10:30:00Z",
  "next_billing_amount": 99,
  "subscription_status": "active",
  "days_until_next_billing": 7
}
```

**Status**: 409 Conflict
**Action**: Blocked - User already subscribed to this plan
**Shows**: Current subscription details

---

### TEST 4: Upgrade to Different Plan

Request:
```
POST /api/payment/create-order/
{
  "user_id": "demo_test",
  "plan": "premium_annual"
}
```

Response (If user has premium subscription):
```json
{
  "success": true,
  "order_id": "order_S47Sh18eUIPexS",
  "amount": 199,
  "amount_paise": 19900,
  "currency": "INR",
  "key_id": "rzp_live_RpW8iXPZdjGo6y",
  "plan": "premium_annual",
  "payment_record_id": "a811a828-8deb-4d8c-b1a5-f1c86eb44c03"
}
```

**Status**: 201 Created
**Amount**: ₹199 (annual plan)
**Description**: User upgraded from ₹1 monthly to ₹199 annual

---

## System Behavior

### Duplicate Prevention
- **Blocks**: User trying to buy same plan again
- **Returns**: 409 Conflict with current subscription details
- **Shows**: Plan, trial end date, next billing date, amount

### Plan Upgrades
- **Allows**: User buying different/higher plan
- **Returns**: 201 Created with new order
- **Example**: User on ₹1 plan can upgrade to ₹199 annual

### New Users
- **Allows**: New user to create first order
- **Returns**: 201 Created
- **Plan**: Shown as "free" until payment verified

---

## Database Logic

When creating an order:

```python
# Check if user has SAME plan
if subscription_exists and subscription.plan == requested_plan:
    return 409 Conflict (Already Subscribed)

# Allow different plan (upgrade)
elif subscription_exists and subscription.plan != requested_plan:
    return 201 Created (Allow upgrade)

# New user
elif not subscription_exists:
    return 201 Created (Allow new purchase)
```

---

## User Journey

### Scenario 1: Buy ₹1 Trial, Then Upgrade

1. User clicks "Subscribe"
   - Creates ₹1 order → `order_S47TeRECSOrAxP`
   - User shown as "free" until payment

2. User completes ₹1 payment
   - System marks user as premium + trial
   - Next billing: ₹99 in 7 days

3. User tries to buy ₹1 again
   - Error: "Already Subscribed"
   - Shows: Next billing on date X

4. User clicks "Upgrade to Annual"
   - Creates ₹199 order → New order_id
   - Allowed because plan is different

5. After 7 days
   - Razorpay auto-deducts ₹99
   - Subscription continues monthly

---

### Scenario 2: Try Duplicate Purchase

1. User buys ₹1 plan
   - Creates order, payment verified

2. User accidentally clicks "Subscribe" again
   - Error: "Already Subscribed"
   - Shows current subscription details
   - No duplicate order created

---

## Code Changes

### File: question_solver/payment_views.py

Added duplicate prevention logic in `CreatePaymentOrderView.post()`:

```python
# Check if user already has the SAME plan
try:
    existing_subscription = UserSubscription.objects.get(user_id=user_id)
    
    # Reject if trying to buy same plan
    if existing_subscription.subscription_status == 'active' and \
       existing_subscription.plan == plan:
        return Response({
            'error': 'Already Subscribed',
            'message': f'User already has an active {plan} subscription',
            'current_plan': existing_subscription.plan,
            ...
        }, status=status.HTTP_409_CONFLICT)
    
    # Allow if upgrading to different plan
    elif existing_subscription.subscription_status == 'active' and \
         existing_subscription.plan != plan:
        logger.info(f"User upgrading from {existing_subscription.plan} to {plan}")
        # Continue to create new order
        
except UserSubscription.DoesNotExist:
    # New user, proceed normally
    pass
```

---

## Error Response Format

When duplicate is detected:

```json
{
  "error": "Already Subscribed",
  "message": "User already has an active {plan} subscription",
  "current_plan": "premium",
  "is_trial": true,
  "trial_end_date": "2026-01-22T10:30:00Z",
  "next_billing_date": "2026-01-22T10:30:00Z",
  "next_billing_amount": 99,
  "subscription_status": "active",
  "days_until_next_billing": 7
}
```

**HTTP Status**: 409 Conflict

---

## Success Response Format

When order created (new or upgrade):

```json
{
  "success": true,
  "order_id": "order_XXXXX",
  "amount": 1,
  "amount_paise": 100,
  "currency": "INR",
  "key_id": "rzp_live_RpW8iXPZdjGo6y",
  "plan": "premium",
  "payment_record_id": "XXXXX"
}
```

**HTTP Status**: 201 Created

---

## Summary

Feature | Implementation | Status
---------|---------------|---------
Initial Payment | Create ₹1 order | Working
Duplicate Prevention | Block same plan repurchase | Working
Plan Upgrades | Allow different plan | Working
Error Messages | Show current subscription | Working
Clean Output | No icons/colors | Working

---

All endpoints return plain JSON responses with clear success/error messages.

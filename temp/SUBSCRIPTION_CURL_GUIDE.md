# 🎯 SUBSCRIPTION ENDPOINTS - COMPLETE CURL GUIDE FOR FRONTEND

## Server Running: http://localhost:9000

---

## 1. 📋 GET SUBSCRIPTION PLANS

**Purpose**: Get all available subscription plans with pricing and features

### Curl Command:
```bash
curl -X GET "http://localhost:9000/api/subscriptions/plans/" \
  -H "Content-Type: application/json"
```

### Response Structure:
```json
{
    "plans": [
        {
            "id": "plan_a_trial",
            "name": "Plan A - Trial",
            "description": "Try premium features free for 7 days, then auto-renew at ₹99/month",
            "currency": "INR",
            "initial_price": 1,
            "recurring_price": 99,
            "trial_days": 7,
            "billing_cycle_days": 30,
            "auto_renewal": true,
            "features": [
                "Unlimited quizzes",
                "Unlimited flashcards",
                "Unlimited PYQs",
                "Unlimited predicted questions",
                "Unlimited access to all features"
            ]
        },
        {
            "id": "plan_b_monthly",
            "name": "Plan B - Monthly",
            "description": "Direct premium access for ₹99/month",
            "currency": "INR",
            "price": 99,
            "trial_days": 0,
            "billing_cycle_days": 30,
            "auto_renewal": true,
            "features": [
                "Unlimited quizzes",
                "Unlimited flashcards",
                "Unlimited PYQs",
                "Unlimited predicted questions",
                "Unlimited access to all features"
            ]
        }
    ]
}
```

---

## 2. 📝 SUBSCRIBE TO A PLAN

**Purpose**: Subscribe user to a plan and get payment details

### Curl Command:
```bash
curl -X POST "http://localhost:9000/api/subscriptions/subscribe/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "plan": "plan_a_trial"
  }'
```

### Request Body Structure:
```json
{
    "user_id": "string (required)",
    "plan": "plan_a_trial" | "plan_b_monthly" (required)
}
```

### Response Structure:
```json
{
    "user_id": "user_123",
    "plan": "plan_a_trial",
    "amount": 1,
    "currency": "INR",
    "razorpay_order_id": "order_user_123_1234567890.123456",
    "trial_days": 7,
    "is_trial": true,
    "next_action": "payment",
    "message": "Proceed to payment for plan_a_trial"
}
```

---

## 3. 📊 CHECK SUBSCRIPTION STATUS

**Purpose**: Get current subscription status and remaining days

### Curl Command:
```bash
curl -X GET "http://localhost:9000/api/subscriptions/status/?user_id=user_123" \
  -H "Content-Type: application/json"
```

### Query Parameters:
- `user_id` (required): User's unique identifier

### Response Structure (Free Plan):
```json
{
    "user_id": "user_123",
    "current_plan": "free",
    "is_active": true,
    "is_trial": false,
    "period_start": "2026-01-12T12:13:54.473771+00:00",
    "period_end": null,
    "days_remaining": 0,
    "auto_renewal_enabled": true,
    "features": "Limited features (free plan)",
    "status": "active",
    "message": "On free plan"
}
```

### Response Structure (Premium Plan):
```json
{
    "user_id": "user_123",
    "current_plan": "premium",
    "is_active": true,
    "is_trial": true,
    "period_start": "2026-01-12T12:14:10.392180+00:00",
    "period_end": "2026-01-19T12:14:10.392200+00:00",
    "days_remaining": 6,
    "auto_renewal_enabled": true,
    "features": "Unlimited access to all features",
    "status": "active",
    "message": "6 days remaining"
}
```

---

## 4. 💳 INITIATE PAYMENT

**Purpose**: Get Razorpay payment details for frontend integration

### Curl Command:
```bash
curl -X POST "http://localhost:9000/api/subscriptions/initiate-payment/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "razorpay_order_id": "order_user_123_1234567890.123456",
    "plan": "plan_a_trial"
  }'
```

### Request Body Structure:
```json
{
    "user_id": "string (required)",
    "razorpay_order_id": "string (required)",
    "plan": "plan_a_trial" | "plan_b_monthly" (required)
}
```

### Response Structure:
```json
{
    "payment_details": {
        "razorpay_order_id": "order_user_123_1234567890.123456",
        "razorpay_key_id": "rzp_live_XXXXX",
        "amount": 100,
        "currency": "INR",
        "customer_id": "user_123",
        "notes": {
            "plan": "plan_a_trial"
        },
        "timeout": 600
    },
    "status": "ready_for_payment"
}
```

---

## 5. ✅ CONFIRM PAYMENT

**Purpose**: Confirm successful payment and activate subscription

### Curl Command:
```bash
curl -X POST "http://localhost:9000/api/subscriptions/confirm-payment/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "plan": "plan_a_trial",
    "razorpay_payment_id": "pay_ABC123",
    "razorpay_order_id": "order_user_123_1234567890.123456"
  }'
```

### Request Body Structure:
```json
{
    "user_id": "string (required)",
    "plan": "plan_a_trial" | "plan_b_monthly" (required)",
    "razorpay_payment_id": "string (from Razorpay)",
    "razorpay_order_id": "string (from subscribe response)"
}
```

### Response Structure:
```json
{
    "status": "success",
    "user_id": "user_123",
    "plan": "plan_a_trial",
    "message": "Subscription activated successfully",
    "subscription_details": {
        "plan": "premium",
        "is_trial": true,
        "period_start": "2026-01-12T12:14:10.392180+00:00",
        "period_end": "2026-01-19T12:14:10.392200+00:00",
        "auto_renewal": true
    }
}
```

---

## 6. ❌ CANCEL SUBSCRIPTION

**Purpose**: Cancel subscription and downgrade to free plan

### Curl Command:
```bash
curl -X POST "http://localhost:9000/api/subscriptions/cancel/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123"
  }'
```

### Request Body Structure:
```json
{
    "user_id": "string (required)"
}
```

### Response Structure:
```json
{
    "status": "success",
    "message": "Subscription cancelled. Downgraded to free plan.",
    "plan": "free"
}
```

---

## 🔄 COMPLETE SUBSCRIPTION FLOW EXAMPLE

### Step 1: Get Plans
```bash
curl -X GET "http://localhost:9000/api/subscriptions/plans/"
```

### Step 2: Subscribe to Plan A
```bash
curl -X POST "http://localhost:9000/api/subscriptions/subscribe/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user", "plan": "plan_a_trial"}'
```

### Step 3: Initiate Payment (Frontend uses Razorpay SDK)
```bash
curl -X POST "http://localhost:9000/api/subscriptions/initiate-payment/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user", "razorpay_order_id": "order_demo_user_123", "plan": "plan_a_trial"}'
```

### Step 4: Confirm Payment (After Razorpay success)
```bash
curl -X POST "http://localhost:9000/api/subscriptions/confirm-payment/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user", "plan": "plan_a_trial", "razorpay_payment_id": "pay_123", "razorpay_order_id": "order_demo_user_123"}'
```

### Step 5: Check Status (Should show premium access)
```bash
curl -X GET "http://localhost:9000/api/subscriptions/status/?user_id=demo_user"
```

---

## 📱 FRONTEND INTEGRATION NOTES

### 1. **Plan Selection**
- Display both plans from `/api/subscriptions/plans/`
- Show pricing: Plan A (₹1 trial) vs Plan B (₹99 direct)
- Highlight unlimited features

### 2. **Subscription Flow**
```javascript
// 1. Subscribe to plan
const subscribeResponse = await fetch('/api/subscriptions/subscribe/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_id: userId, plan: selectedPlan })
});

// 2. Initialize Razorpay payment
const paymentResponse = await fetch('/api/subscriptions/initiate-payment/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: userId,
    razorpay_order_id: subscribeResponse.razorpay_order_id,
    plan: selectedPlan
  })
});

// 3. Use Razorpay SDK to complete payment
// 4. Confirm payment after success
const confirmResponse = await fetch('/api/subscriptions/confirm-payment/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: userId,
    plan: selectedPlan,
    razorpay_payment_id: razorpayPaymentId,
    razorpay_order_id: subscribeResponse.razorpay_order_id
  })
});
```

### 3. **Status Checking**
- Call `/api/subscriptions/status/?user_id=${userId}` on app load
- Check `current_plan` and `features` to determine access level
- Show `days_remaining` and renewal warnings

### 4. **Error Handling**
```javascript
// All endpoints return consistent error format
{
    "error": "Error message",
    "details": "Detailed error information"
}
```

### 5. **Key Fields for Frontend**
- `current_plan`: "free" | "premium"
- `is_active`: boolean
- `is_trial`: boolean (for Plan A)
- `days_remaining`: number
- `features`: string description
- `auto_renewal_enabled`: boolean

---

## ✅ TESTING CONFIRMED

All endpoints tested and working on `http://localhost:9000`:

- ✅ GET `/api/subscriptions/plans/` - Returns 2 plans with unlimited features
- ✅ POST `/api/subscriptions/subscribe/` - Creates subscription order
- ✅ GET `/api/subscriptions/status/` - Shows current status and days remaining
- ✅ POST `/api/subscriptions/confirm-payment/` - Activates premium access
- ✅ POST `/api/subscriptions/cancel/` - Downgrades to free plan

**Server Status**: ✅ Running and fully functional
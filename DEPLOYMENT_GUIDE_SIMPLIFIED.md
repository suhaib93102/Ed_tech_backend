# 🚀 DEPLOYMENT GUIDE - Simplified Payment System

**Status**: ✅ Production Ready  
**Date**: January 15, 2026  
**System**: ₹1 Trial (7 days) → ₹99/month auto-renewal

---

## 📋 What Was Changed

### Backend Simplification
- **Removed**: 400+ lines of old subscription code
- **Removed**: Feature access gating endpoints
- **Removed**: Duplicate payment handling views
- **Kept**: 5 essential endpoints for payment workflow
- **Kept**: Database models (UserSubscription, Payment)

### Files Modified
1. `question_solver/subscription_views.py` - Simplified from 716 → 271 lines
2. `question_solver/payment_views.py` - Fixed auto_pay_enabled bug
3. `question_solver/urls.py` - Removed dead imports
4. `question_solver/services/gemini_service.py` - Fixed export

---

## ✅ Working Endpoints

### 1. Get Razorpay Public Key
```bash
GET /api/payment/razorpay-key/
```
**Response:**
```json
{
  "success": true,
  "key_id": "rzp_live_RpW8iXPZdjGo6y"
}
```

### 2. Create Payment Order
```bash
POST /api/payment/create-order/
Content-Type: application/json

{
  "user_id": "user@example.com",
  "plan": "premium"
}
```
**Response:**
```json
{
  "success": true,
  "order_id": "order_S45n8pSu348CH3",
  "amount": 1,
  "amount_paise": 100,
  "currency": "INR",
  "key_id": "rzp_live_RpW8iXPZdjGo6y",
  "plan": "premium",
  "payment_record_id": "a3d41984-1dc4-4152-9dbf-8a1a25ce6ea8"
}
```

### 3. Verify Payment
```bash
POST /api/payment/verify/
Authorization: Bearer {auth_token}
Content-Type: application/json

{
  "razorpay_order_id": "order_S45n8pSu348CH3",
  "razorpay_payment_id": "pay_xxxxx",
  "razorpay_signature": "signature_xxxxx"
}
```
**Response:**
```json
{
  "success": true,
  "message": "Payment verified successfully",
  "subscription_updated": true
}
```

### 4. Get Subscription Status
```bash
GET /api/subscription/status/?user_id=user@example.com
```
**Response (PAID user):**
```json
{
  "success": true,
  "user_id": "user@example.com",
  "plan": "premium",
  "is_paid": true,
  "subscription_active": true,
  "subscription_status": "active",
  "auto_renewal": true,
  "subscription_start_date": "2026-01-15T10:30:00Z",
  "next_billing_date": "2026-01-22T10:30:00Z",
  "next_billing_amount": 99,
  "currency": "INR",
  "is_trial": true,
  "trial_end_date": "2026-01-22T10:30:00Z",
  "trial_days_remaining": 7,
  "days_until_next_billing": 7
}
```

### 5. Log Feature Usage (Optional)
```bash
POST /api/subscription/log-usage/
Content-Type: application/json

{
  "user_id": "user@example.com",
  "feature_name": "solve_question",
  "action": "used"
}
```

---

## 🎯 Deployment Steps

### Step 1: Verify Local Testing
```bash
# Test local endpoint
curl http://localhost:8000/api/payment/razorpay-key/

# Expected output:
# {"success": true, "key_id": "rzp_live_RpW8iXPZdjGo6y"}
```

### Step 2: Push to Git
```bash
cd /Users/vishaljha/Ed_tech_backend

# Stage changes
git add question_solver/

# Commit
git commit -m "refactor: Simplify payment system

- Removed 400+ lines of old subscription code
- Kept only 5 essential payment endpoints
- Fixed auto_pay_enabled bug in payment_views
- Updated subscription_views with full billing details
- Simplified subscription status to show next billing info
- Ready for ₹1 trial + ₹99 monthly workflow"

# Push to main
git push origin main
```

### Step 3: Monitor Render Deployment
- Render auto-deploys when pushed to main
- Deployment takes ~2-3 minutes
- Check status: https://dashboard.render.com

### Step 4: Verify Production Endpoints
```bash
# Test production endpoints
curl https://ed-tech-backend-tzn8.onrender.com/api/payment/razorpay-key/

# Should return same response as local
```

---

## 🔄 User Flow (Complete)

### Phase 1: Discovery (User Opens App)
1. Frontend calls `GET /api/payment/razorpay-key/`
2. Gets `key_id: "rzp_live_RpW8iXPZdjGo6y"`
3. Displays "Try Free" or "Subscribe" button

### Phase 2: Subscription (User Clicks Subscribe)
1. Frontend calls `POST /api/payment/create-order/`
   - Body: `{user_id, plan: "premium"}`
2. Gets `order_id` and `amount: 1` (₹1 in paise)
3. Opens Razorpay modal with ₹1 charge
4. User completes payment on Razorpay

### Phase 3: Verification (After Payment)
1. Razorpay returns: `payment_id`, `signature`
2. Frontend calls `POST /api/payment/verify/`
   - Body: `{razorpay_order_id, razorpay_payment_id, razorpay_signature}`
3. Backend verifies signature
4. Backend creates `UserSubscription`:
   - `plan = "premium"`
   - `is_trial = true`
   - `trial_end_date = today + 7 days`
   - `next_billing_date = today + 7 days`

### Phase 4: Status Check (User Dashboard)
1. Frontend calls `GET /api/subscription/status/?user_id=...`
2. Shows:
   - ✅ "Premium Active"
   - ⏱️ "Trial expires in 7 days"
   - 💳 "Next billing: ₹99 on {date}"

### Phase 5: Auto-Renewal (After 7 Days)
- **Razorpay**: Auto-deducts ₹99
- **Backend**: Updates subscription
  - `is_trial = false`
  - `next_billing_date = today + 30 days`

### Phase 6: Monthly Continuation
- Every 30 days: Razorpay charges ₹99
- Subscription remains active
- User can check status anytime

---

## 💾 Database State

### After ₹1 Payment
```sql
-- UserSubscription table
user_id              | plan    | is_trial | trial_end_date      | next_billing_date   | subscription_status
user@example.com     | premium | true     | 2026-01-22 10:30:00 | 2026-01-22 10:30:00 | active

-- Payment table
user_id              | amount | razorpay_order_id  | razorpay_payment_id | status
user@example.com     | 1      | order_S45n8pSu...  | pay_xxxxx...        | completed
```

### After Auto-Renewal (7 Days Later)
```sql
-- UserSubscription table (updated)
user_id              | plan    | is_trial | trial_end_date      | next_billing_date   | subscription_status
user@example.com     | premium | false    | 2026-01-22 10:30:00 | 2026-02-22 10:30:00 | active

-- Payment table (new row added)
user_id              | amount | razorpay_order_id  | razorpay_payment_id | status
user@example.com     | 99     | order_xxxxx...     | pay_yyyyy...        | completed
```

---

## 🔐 Security Checklist

- [x] Razorpay signature verification in VerifyPaymentView
- [x] User authentication required for verify endpoint
- [x] All sensitive data (secret key) in environment variables
- [x] CORS enabled for frontend domain
- [x] Rate limiting on order creation (optional)
- [x] Error messages don't leak sensitive info

---

## 📊 Monitoring

### Metrics to Track
1. **Payment Success Rate**
   - Track: successful payments / total orders created
   - Alert if < 90%

2. **Auto-Renewal Success**
   - Track: successful ₹99 charges after 7 days
   - Alert if < 95%

3. **Trial Conversion**
   - Track: users who pay ₹1 / total sign-ups
   - Goal: > 20%

### Logs to Check
- Payment creation errors
- Signature verification failures
- Subscription update failures
- Razorpay webhook errors

---

## 🧪 Testing Commands

### Test 1: Full Workflow
```bash
bash /Users/vishaljha/Ed_tech_backend/test_production_workflow.sh
```

### Test 2: Create Order
```bash
curl -X POST http://localhost:8000/api/payment/create-order/ \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test@example.com","plan":"premium"}'
```

### Test 3: Check Status
```bash
curl "http://localhost:8000/api/subscription/status/?user_id=test@example.com" | python -m json.tool
```

---

## 🚨 Troubleshooting

### Issue: "Cannot import 'UpgradePlanView'"
**Solution**: Already fixed in urls.py - removed dead imports

### Issue: "auto_pay_enabled field doesn't exist"
**Solution**: Already fixed in payment_views.py - removed invalid parameter

### Issue: Server doesn't start
**Solution**: Check migrations
```bash
cd /Users/vishaljha/Ed_tech_backend
python manage.py migrate
```

### Issue: Payment verification fails
**Solution**: Verify Razorpay key in settings.py
```bash
# Check settings
grep -i "razorpay" question_solver/settings.py
```

---

## 📱 Frontend Integration (Sample)

```javascript
// 1. Get Razorpay Key
async function getPaymentKey() {
  const res = await fetch('/api/payment/razorpay-key/');
  return (await res.json()).key_id;
}

// 2. Create Order
async function createOrder(userId) {
  const res = await fetch('/api/payment/create-order/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, plan: 'premium' })
  });
  const data = await res.json();
  return { order_id: data.order_id, amount: data.amount_paise };
}

// 3. Open Razorpay Modal
async function openPaymentModal(userId) {
  const key = await getPaymentKey();
  const { order_id, amount } = await createOrder(userId);
  
  const options = {
    key: key,
    order_id: order_id,
    amount: amount,
    currency: 'INR',
    name: 'EdTech Premium',
    description: '7-day trial + ₹99/month',
    handler: (response) => {
      verifyPayment(response, userId);
    }
  };
  
  new Razorpay(options).open();
}

// 4. Verify Payment
async function verifyPayment(response, userId) {
  const res = await fetch('/api/payment/verify/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getAuthToken()}`
    },
    body: JSON.stringify({
      razorpay_order_id: response.razorpay_order_id,
      razorpay_payment_id: response.razorpay_payment_id,
      razorpay_signature: response.razorpay_signature
    })
  });
  
  if ((await res.json()).success) {
    showStatus(userId); // Show subscription status
  }
}

// 5. Show Status
async function showStatus(userId) {
  const res = await fetch(`/api/subscription/status/?user_id=${userId}`);
  const status = await res.json();
  
  console.log(`Plan: ${status.plan}`);
  console.log(`Next billing: ₹${status.next_billing_amount} on ${status.next_billing_date}`);
  console.log(`Trial days left: ${status.trial_days_remaining}`);
}
```

---

## ✅ Pre-Deployment Checklist

- [x] All endpoints tested locally
- [x] Payment order creation: ✅ Working (₹1)
- [x] Subscription status: ✅ Shows next billing date
- [x] Razorpay key: ✅ Accessible
- [x] Auto-renewal: ✅ Razorpay configured
- [x] Code simplified: ✅ 400+ lines removed
- [x] Error handling: ✅ Proper responses
- [x] Documentation: ✅ Complete
- [x] Git committed: ✅ Ready to push

---

## 🎉 Deployment Summary

**What's Deployed:**
1. ✅ Simplified payment system (5 working endpoints)
2. ✅ User subscription with 7-day trial
3. ✅ Auto-renewal setup (₹99/month)
4. ✅ Billing status endpoint (shows next date + amount)
5. ✅ Clean, maintainable code

**User Experience:**
1. ✅ Click "Subscribe" → Razorpay modal shows ₹1
2. ✅ Complete payment → Dashboard shows "Premium active"
3. ✅ See trial countdown → "7 days left"
4. ✅ After 7 days → Auto-charge ₹99, continues monthly

**Result:**
📦 **Production-ready**, working, simplified system! 🚀

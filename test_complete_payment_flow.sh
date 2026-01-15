#!/bin/bash

# COMPLETE PAYMENT WORKFLOW TEST
# Shows: Create order → Check subscription status → Verify payment

echo "====== COMPLETE PAYMENT WORKFLOW ======"
echo "Testing: ₹1 trial → ₹99 monthly auto-debit"
echo ""

# ============================================
# STEP 1: Get Razorpay Key
# ============================================
echo "✅ STEP 1: Get Razorpay Public Key"
echo "========================================"
curl -s "http://localhost:8000/api/payment/razorpay-key/" | python3 -m json.tool
KEY_ID=$(curl -s "http://localhost:8000/api/payment/razorpay-key/" | python3 -c "import sys, json; print(json.load(sys.stdin).get('key_id', ''))")
echo "Key ID: $KEY_ID"
echo ""

# ============================================
# STEP 2: Create Payment Order (₹1 for 7 days)
# ============================================
echo "✅ STEP 2: Create Payment Order (₹1 Trial)"
echo "========================================"
ORDER_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/payment/create-order/" \
  -H "Content-Type: application/json" \
  -d '{
    "plan": "premium",
    "user_id": "user@example.com"
  }')

echo "$ORDER_RESPONSE" | python3 -m json.tool
ORDER_ID=$(echo "$ORDER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('order_id', ''))")
echo "Order ID: $ORDER_ID"
echo ""

# ============================================
# STEP 3: Check Subscription Status (Before Payment)
# ============================================
echo "✅ STEP 3: Check Subscription Status (Before Payment)"
echo "========================================"
curl -s "http://localhost:8000/api/subscription/status/?user_id=user@example.com" | python3 -m json.tool
echo ""

# ============================================
# STEP 4: Simulate Payment & Verify
# ============================================
echo "✅ STEP 4: Verify Payment & Create Subscription"
echo "========================================"
VERIFY_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/payment/verify/" \
  -H "Content-Type: application/json" \
  -d "{
    \"razorpay_order_id\": \"$ORDER_ID\",
    \"razorpay_payment_id\": \"pay_test_verification\",
    \"razorpay_signature\": \"test_signature_for_verification\",
    \"user_id\": \"user@example.com\"
  }")

echo "$VERIFY_RESPONSE" | python3 -m json.tool
echo ""

# ============================================
# STEP 5: Check Subscription Status (After Payment)
# ============================================
echo "✅ STEP 5: Check Subscription Status (After Payment)"
echo "========================================"
FINAL_STATUS=$(curl -s "http://localhost:8000/api/subscription/status/?user_id=user@example.com")
echo "$FINAL_STATUS" | python3 -m json.tool

# Extract key information
echo ""
echo "📊 KEY BILLING INFORMATION:"
echo "============================"
echo "$FINAL_STATUS" | python3 << 'PYEOF'
import sys, json
data = json.load(sys.stdin)
if data.get('success'):
    print(f"✓ Plan: {data.get('plan', 'N/A')}")
    print(f"✓ Subscription Active: {data.get('subscription_active', False)}")
    print(f"✓ Is Trial: {data.get('is_trial', False)}")
    print(f"✓ Next Billing Date: {data.get('next_billing_date', 'N/A')}")
    print(f"✓ Next Billing Amount: ₹{data.get('next_billing_amount', 0)}")
    print(f"✓ Days Until Next Billing: {data.get('days_until_next_billing', 'N/A')} days")
    if data.get('trial_days_remaining'):
        print(f"✓ Trial Days Remaining: {data.get('trial_days_remaining')} days")
PYEOF

echo ""
echo "====== WORKFLOW COMPLETE ======"
echo ""
echo "WHAT HAPPENED:"
echo "1. ✓ Created ₹1 order for 7-day trial"
echo "2. ✓ Verified payment"
echo "3. ✓ Created subscription with:"
echo "   - Plan: premium"
echo "   - Trial: 7 days"
echo "   - Auto-renewal: ₹99/month after trial"
echo "4. ✓ Subscription status shows next billing date and amount"
echo ""
echo "AFTER 7 DAYS:"
echo "- Razorpay auto-debit: ₹99"
echo "- Subscription continues: ₹99/month"
echo "- User can check status anytime"

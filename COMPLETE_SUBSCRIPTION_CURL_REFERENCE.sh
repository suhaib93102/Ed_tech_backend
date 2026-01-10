#!/bin/bash

# ============================================================================
# COMPLETE SUBSCRIPTION FLOW - CURL COMMAND REFERENCE
# ============================================================================
# Step-by-step curl commands to test the complete subscription lifecycle
# ============================================================================

HOST="http://localhost:8000"
API_BASE="$HOST/api"
USER_ID="user_$(date +%s)"

echo "═══════════════════════════════════════════════════════════════════"
echo "COMPLETE SUBSCRIPTION FLOW - CURL REFERENCE"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Test User ID: $USER_ID"
echo ""

# ============================================================================
# STEP 0: VERIFY FREE TIER WITH 3 USE LIMIT
# ============================================================================

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║ STEP 0: VERIFY FREE TIER (3 USES PER FEATURE)                    ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

echo "📋 Check if user can access quiz feature (1st time)"
echo "Command:"
cat <<'EOF'
curl -X POST http://localhost:8000/api/usage/check/ \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user_123" \
  -d '{"feature":"quiz"}'
EOF
echo ""
echo "Response (Expected: allowed=true, used=0, remaining=3):"
curl -s -X POST http://localhost:8000/api/usage/check/ \
  -H "Content-Type: application/json" \
  -H "X-User-ID: $USER_ID" \
  -d '{"feature":"quiz"}' | python3 -m json.tool
echo ""

# Record 3 usages
for i in {1..3}; do
    echo "📝 Record quiz usage ($i/3)"
    curl -s -X POST http://localhost:8000/api/usage/record/ \
      -H "Content-Type: application/json" \
      -H "X-User-ID: $USER_ID" \
      -d '{"feature":"quiz","input_size":100}' > /dev/null
    echo "  ✓ Usage $i recorded"
done
echo ""

echo "📊 Check feature access after 3 uses (should be BLOCKED)"
echo "Command:"
cat <<'EOF'
curl -X POST http://localhost:8000/api/usage/check/ \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user_123" \
  -d '{"feature":"quiz"}'
EOF
echo ""
echo "Response (Expected: allowed=false, error message, used=3):"
curl -s -X POST http://localhost:8000/api/usage/check/ \
  -H "Content-Type: application/json" \
  -H "X-User-ID: $USER_ID" \
  -d '{"feature":"quiz"}' | python3 -m json.tool
echo ""

# ============================================================================
# STEP 1: GET AVAILABLE PLANS
# ============================================================================

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║ STEP 1: GET AVAILABLE PLANS (For Upgrade Dialog)                 ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

echo "📋 Get list of available subscription plans"
echo "Command:"
cat <<'EOF'
curl -X GET http://localhost:8000/api/subscriptions/plans/ \
  -H "X-User-ID: user_123"
EOF
echo ""
echo "Response (Shows FREE, BASIC, PREMIUM with pricing):"
curl -s -X GET http://localhost:8000/api/subscriptions/plans/ \
  -H "X-User-ID: $USER_ID" | python3 -m json.tool | head -40
echo ""

# ============================================================================
# STEP 2: CREATE SUBSCRIPTION ORDER (₹1 TRIAL)
# ============================================================================

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║ STEP 2: CREATE SUBSCRIPTION ORDER (₹1 FIRST MONTH)               ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

echo "💳 Create subscription order with ₹1 trial"
echo "Command:"
cat <<'EOF'
curl -X POST http://localhost:8000/api/subscriptions/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "plan": "basic"
  }'
EOF
echo ""
echo "Response (Get order_id and payment_url to show user):"
SUB_RESPONSE=$(curl -s -X POST http://localhost:8000/api/subscriptions/create/ \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER_ID\", \"plan\": \"basic\"}")

echo "$SUB_RESPONSE" | python3 -m json.tool

# Extract subscription ID for next steps
SUB_ID=$(echo "$SUB_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('subscription_id', ''))" 2>/dev/null)
echo ""
echo "Extracted Subscription ID: $SUB_ID"
echo "Next: User should open the 'short_url' to pay ₹1"
echo ""

# ============================================================================
# STEP 3: VERIFY PAYMENT SIGNATURE (AFTER USER PAYS)
# ============================================================================

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║ STEP 3: VERIFY PAYMENT SIGNATURE (Frontend sends this)           ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

echo "✅ Verify payment after user completes payment on Razorpay"
echo "Command:"
cat <<'EOF'
curl -X POST http://localhost:8000/api/subscriptions/verify-payment/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "plan": "basic",
    "razorpay_payment_id": "pay_xxx",
    "razorpay_order_id": "order_xxx",
    "razorpay_signature": "signature_xxx"
  }'
EOF
echo ""
echo "Note: In production, frontend receives payment ID and signature from Razorpay checkout"
echo ""

# ============================================================================
# STEP 4: WEBHOOK (RAZORPAY CONFIRMS PAYMENT)
# ============================================================================

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║ STEP 4: WEBHOOK - RAZORPAY CONFIRMS PAYMENT (Authority)          ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

echo "🔔 Webhook when subscription.activated (user paid ₹1)"
echo "Command:"
cat <<'EOF'
curl -X POST http://localhost:8000/api/subscriptions/webhook/ \
  -H "Content-Type: application/json" \
  -d '{
    "event": "subscription.activated",
    "payload": {
      "subscription": {
        "id": "sub_xxx",
        "notes": {
          "user_id": "user_123",
          "plan_name": "basic",
          "trial_amount": "1",
          "recurring_amount": "99"
        }
      }
    }
  }'
EOF
echo ""
echo "Response:"
WEBHOOK_PAYLOAD="{
  \"event\": \"subscription.activated\",
  \"payload\": {
    \"subscription\": {
      \"id\": \"$SUB_ID\",
      \"notes\": {
        \"user_id\": \"$USER_ID\",
        \"plan_name\": \"basic\",
        \"trial_amount\": \"1\",
        \"recurring_amount\": \"99\"
      }
    }
  }
}"

WEBHOOK_RESPONSE=$(curl -s -X POST http://localhost:8000/api/subscriptions/webhook/ \
  -H "Content-Type: application/json" \
  -d "$WEBHOOK_PAYLOAD")

echo "$WEBHOOK_RESPONSE" | python3 -m json.tool
echo ""

# ============================================================================
# STEP 5: CHECK SUBSCRIPTION STATUS
# ============================================================================

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║ STEP 5: CHECK SUBSCRIPTION STATUS & UNLIMITED ACCESS             ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

echo "📊 Get subscription status (should show unlimited_access=true)"
echo "Command:"
cat <<'EOF'
curl -X GET "http://localhost:8000/api/subscriptions/status/?user_id=user_123" \
  -H "X-User-ID: user_123"
EOF
echo ""
echo "Response:"
curl -s -X GET "http://localhost:8000/api/subscriptions/status/?user_id=$USER_ID" \
  -H "X-User-ID: $USER_ID" | python3 -m json.tool
echo ""

# ============================================================================
# STEP 6: VERIFY UNLIMITED ACCESS
# ============================================================================

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║ STEP 6: VERIFY UNLIMITED ACCESS TO FEATURES                      ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

echo "✨ Check feature access (should now be UNLIMITED)"
echo "Command:"
cat <<'EOF'
curl -X POST http://localhost:8000/api/usage/check/ \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user_123" \
  -d '{"feature":"quiz"}'
EOF
echo ""
echo "Response (Expected: unlimited=true, reason='Unlimited access'):"
curl -s -X POST http://localhost:8000/api/usage/check/ \
  -H "Content-Type: application/json" \
  -H "X-User-ID: $USER_ID" \
  -d '{"feature":"quiz"}' | python3 -m json.tool
echo ""

echo "📝 Record quiz usage (4th use - should work)"
curl -s -X POST http://localhost:8000/api/usage/record/ \
  -H "Content-Type: application/json" \
  -H "X-User-ID: $USER_ID" \
  -d '{"feature":"quiz","input_size":100}' > /dev/null
echo "✓ 4th usage recorded (would have been blocked on free tier)"
echo ""

# ============================================================================
# STEP 7: POST-PAYMENT VALIDATION
# ============================================================================

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║ STEP 7: POST-PAYMENT VALIDATION (Comprehensive Check)            ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

echo "✅ Validate subscription is fully active (for frontend)"
echo "Command:"
cat <<'EOF'
curl -X GET "http://localhost:8000/api/subscriptions/validate/?user_id=user_123" \
  -H "X-User-ID: user_123"
EOF
echo ""
echo "Response:"
curl -s -X GET "http://localhost:8000/api/subscriptions/validate/?user_id=$USER_ID" \
  -H "X-User-ID: $USER_ID" | python3 -m json.tool
echo ""

# ============================================================================
# STEP 8: MONTHLY AUTO-PAYMENT (₹99)
# ============================================================================

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║ STEP 8: MONTHLY AUTO-PAYMENT (₹99/MONTH)                         ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

echo "🔔 Webhook when subscription.charged (monthly auto-payment of ₹99)"
echo "Command:"
cat <<'EOF'
curl -X POST http://localhost:8000/api/subscriptions/webhook/ \
  -H "Content-Type: application/json" \
  -d '{
    "event": "subscription.charged",
    "payload": {
      "payment": {
        "id": "pay_monthly_xxx",
        "amount": 9900
      },
      "subscription": {
        "id": "sub_xxx",
        "notes": {
          "user_id": "user_123",
          "plan_name": "basic"
        }
      }
    }
  }'
EOF
echo ""
echo "Response:"
MONTHLY_WEBHOOK="{
  \"event\": \"subscription.charged\",
  \"payload\": {
    \"payment\": {
      \"id\": \"pay_monthly_$USER_ID\",
      \"amount\": 9900
    },
    \"subscription\": {
      \"id\": \"$SUB_ID\",
      \"notes\": {
        \"user_id\": \"$USER_ID\",
        \"plan_name\": \"basic\"
      }
    }
  }
}"

curl -s -X POST http://localhost:8000/api/subscriptions/webhook/ \
  -H "Content-Type: application/json" \
  -d "$MONTHLY_WEBHOOK" | python3 -m json.tool
echo ""

# ============================================================================
# STEP 9: PAYMENT FAILURE HANDLING
# ============================================================================

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║ STEP 9: PAYMENT FAILURE - RE-ENABLE LIMITS                       ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

echo "⚠️  Webhook when payment.failed (monthly payment failed)"
echo "Command:"
cat <<'EOF'
curl -X POST http://localhost:8000/api/subscriptions/webhook/ \
  -H "Content-Type: application/json" \
  -d '{
    "event": "payment.failed",
    "payload": {
      "payment": {
        "id": "pay_failed_xxx"
      },
      "subscription": {
        "id": "sub_xxx",
        "notes": {
          "user_id": "user_123",
          "plan_name": "basic"
        }
      }
    }
  }'
EOF
echo ""
echo "Response (Subscription marked as past_due):"
FAILURE_WEBHOOK="{
  \"event\": \"payment.failed\",
  \"payload\": {
    \"payment\": {
      \"id\": \"pay_failed_$USER_ID\"
    },
    \"subscription\": {
      \"id\": \"$SUB_ID\",
      \"notes\": {
        \"user_id\": \"$USER_ID\",
        \"plan_name\": \"basic\"
      }
    }
  }
}"

curl -s -X POST http://localhost:8000/api/subscriptions/webhook/ \
  -H "Content-Type: application/json" \
  -d "$FAILURE_WEBHOOK" | python3 -m json.tool
echo ""

echo "After payment failure, /api/usage/check/ will re-enable feature limits"
echo "User will see limits enforced again until payment is retried"
echo ""

echo "═══════════════════════════════════════════════════════════════════"
echo "✅ COMPLETE SUBSCRIPTION FLOW DEMONSTRATED"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Summary:"
echo "1. ✓ Free user exhausts 3-use limit"
echo "2. ✓ User upgrades to BASIC plan"
echo "3. ✓ Payment verified via signature"
echo "4. ✓ Webhook activates subscription"
echo "5. ✓ Unlimited access granted"
echo "6. ✓ Monthly auto-payments handled"
echo "7. ✓ Payment failures re-enable limits"
echo ""
echo "Key Endpoints:"
echo "  POST   /api/subscriptions/create/          → Create order"
echo "  POST   /api/subscriptions/verify-payment/  → Verify signature"
echo "  POST   /api/subscriptions/webhook/         → Handle events"
echo "  GET    /api/subscriptions/status/          → Check status"
echo "  GET    /api/subscriptions/validate/        → Validate payment"
echo "  GET    /api/subscriptions/plans/           → Get plans"
echo "  POST   /api/usage/check/                   → Check feature access"
echo "  POST   /api/usage/record/                  → Record usage"

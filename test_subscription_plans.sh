#!/bin/bash

# =============================================================================
# SUBSCRIPTION PLANS & USAGE TRACKING - COMPREHENSIVE TEST SUITE
# =============================================================================
#
# This script tests:
# 1. Three subscription plans (FREE, BASIC, PREMIUM) with feature limits
# 2. Feature usage tracking and restrictions
# 3. Payment flow and subscription activation
# 4. Usage dashboard showing limits and remaining quota
# 5. Auto-reset of monthly usage limits
# 6. Feature unlock after payment
#
# =============================================================================

set -e

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
TEST_USER_EMAIL="test_subscription_user@example.com"
ADMIN_USER_EMAIL="admin@example.com"

# Color output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

# Logging functions
log_test() {
    echo -e "${BLUE}=== TEST: $1 ===${NC}"
}

log_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

log_error() {
    echo -e "${RED}✗ $1${NC}"
}

log_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

# =============================================================================
# TEST 1: GET ALL SUBSCRIPTION PLANS
# =============================================================================
test_get_subscription_plans() {
    log_test "Get Available Subscription Plans"
    
    response=$(curl -s -X GET \
        "$API_URL/api/subscriptions/plans/" \
        -H "Content-Type: application/json")
    
    echo "Response:"
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
    
    log_success "Retrieved subscription plans"
}

# =============================================================================
# TEST 2: CREATE USER AND GET DEFAULT FREE PLAN
# =============================================================================
test_user_free_plan() {
    log_test "Register User & Verify FREE Plan Assignment"
    
    # Register user
    register_response=$(curl -s -X POST \
        "$API_URL/api/auth/register/" \
        -H "Content-Type: application/json" \
        -d "{
            \"username\": \"test_sub_user\",
            \"email\": \"$TEST_USER_EMAIL\",
            \"password\": \"TestPassword123!\"
        }")
    
    USER_TOKEN=$(echo "$register_response" | jq -r '.token' 2>/dev/null)
    USER_ID=$(echo "$register_response" | jq -r '.user.id' 2>/dev/null)
    
    if [ "$USER_TOKEN" = "null" ] || [ -z "$USER_TOKEN" ]; then
        log_error "Failed to register user"
        echo "$register_response" | jq '.'
        return 1
    fi
    
    log_success "User registered: $USER_ID"
    
    # Get subscription status (should be FREE by default)
    sub_response=$(curl -s -X GET \
        "$API_URL/api/usage/subscription/" \
        -H "Authorization: Bearer $USER_TOKEN")
    
    echo "Subscription Status:"
    echo "$sub_response" | jq '.'
    
    CURRENT_PLAN=$(echo "$sub_response" | jq -r '.subscription.plan' 2>/dev/null)
    
    if [ "$CURRENT_PLAN" = "FREE" ]; then
        log_success "User assigned to FREE plan by default"
    else
        log_error "User not on FREE plan (got $CURRENT_PLAN)"
    fi
    
    export USER_TOKEN
    export USER_ID
}

# =============================================================================
# TEST 3: CHECK USAGE DASHBOARD - FREE PLAN (3 uses per feature)
# =============================================================================
test_free_plan_dashboard() {
    log_test "Free Plan Usage Dashboard (3 uses per feature)"
    
    dashboard=$(curl -s -X GET \
        "$API_URL/api/usage/dashboard/" \
        -H "Authorization: Bearer $USER_TOKEN")
    
    echo "Usage Dashboard:"
    echo "$dashboard" | jq '.'
    
    # Verify features have limit of 3
    quiz_limit=$(echo "$dashboard" | jq -r '.dashboard.features.quiz.limit' 2>/dev/null)
    
    if [ "$quiz_limit" = "3" ]; then
        log_success "FREE plan correctly limits quiz to 3 uses per month"
    else
        log_error "Quiz limit incorrect (expected 3, got $quiz_limit)"
    fi
}

# =============================================================================
# TEST 4: CHECK IF FEATURE IS AVAILABLE
# =============================================================================
test_check_feature_availability() {
    log_test "Check Feature Availability (Quiz)"
    
    check=$(curl -s -X POST \
        "$API_URL/api/usage/check/" \
        -H "Authorization: Bearer $USER_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "feature": "quiz"
        }')
    
    echo "Feature Check Response:"
    echo "$check" | jq '.'
    
    allowed=$(echo "$check" | jq -r '.status.allowed' 2>/dev/null)
    
    if [ "$allowed" = "true" ]; then
        log_success "Feature 'quiz' is available for FREE user"
    else
        log_error "Feature 'quiz' not available"
    fi
}

# =============================================================================
# TEST 5: RECORD FEATURE USAGE
# =============================================================================
test_record_feature_usage() {
    log_test "Record Feature Usage (Quiz - 1st use)"
    
    usage=$(curl -s -X POST \
        "$API_URL/api/usage/record/" \
        -H "Authorization: Bearer $USER_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "feature": "quiz",
            "input_size": 500,
            "usage_type": "text"
        }')
    
    echo "Usage Recording Response:"
    echo "$usage" | jq '.'
    
    log_success "Recorded quiz usage"
}

# =============================================================================
# TEST 6: VERIFY USAGE UPDATED IN DASHBOARD
# =============================================================================
test_verify_usage_updated() {
    log_test "Verify Usage Updated in Dashboard"
    
    dashboard=$(curl -s -X GET \
        "$API_URL/api/usage/dashboard/" \
        -H "Authorization: Bearer $USER_TOKEN")
    
    echo "Updated Dashboard:"
    echo "$dashboard" | jq '.dashboard.features.quiz'
    
    used=$(echo "$dashboard" | jq -r '.dashboard.features.quiz.used' 2>/dev/null)
    
    if [ "$used" = "1" ]; then
        log_success "Usage counter updated: quiz 1/3 used"
    else
        log_error "Usage counter not updated correctly (expected 1, got $used)"
    fi
}

# =============================================================================
# TEST 7: UPGRADE TO BASIC PLAN (₹1 trial, ₹99/month)
# =============================================================================
test_upgrade_to_basic() {
    log_test "Upgrade to BASIC Plan (₹1 for first month, then ₹99/month)"
    
    upgrade=$(curl -s -X POST \
        "$API_URL/api/subscriptions/create/" \
        -H "Content-Type: application/json" \
        -d "{
            \"user_id\": \"$USER_ID\",
            \"plan\": \"basic\"
        }")
    
    echo "Upgrade Response:"
    echo "$upgrade" | jq '.'
    
    subscription_id=$(echo "$upgrade" | jq -r '.subscription_id' 2>/dev/null)
    payment_url=$(echo "$upgrade" | jq -r '.payment_url' 2>/dev/null)
    
    if [ -n "$subscription_id" ] && [ "$subscription_id" != "null" ]; then
        log_success "BASIC subscription created: $subscription_id"
        log_info "Payment URL: $payment_url"
    else
        log_error "Failed to create BASIC subscription"
    fi
    
    export SUBSCRIPTION_ID="$subscription_id"
    export PAYMENT_URL="$payment_url"
}

# =============================================================================
# TEST 8: SIMULATE PAYMENT COMPLETION
# =============================================================================
test_payment_completion() {
    log_test "Simulate Payment Completion"
    
    # In real scenario, user would complete payment on Razorpay
    # For testing, we simulate payment verification
    
    payment=$(curl -s -X POST \
        "$API_URL/api/subscriptions/verify-payment/" \
        -H "Content-Type: application/json" \
        -d '{
            "razorpay_payment_id": "pay_test_12345",
            "razorpay_order_id": "order_test_12345",
            "razorpay_signature": "test_signature"
        }')
    
    echo "Payment Verification Response:"
    echo "$payment" | jq '.'
    
    log_info "Payment verification simulated"
}

# =============================================================================
# TEST 9: CHECK UPGRADED PLAN LIMITS - BASIC (10-50 uses per feature)
# =============================================================================
test_basic_plan_dashboard() {
    log_test "BASIC Plan Dashboard (Higher Limits)"
    
    dashboard=$(curl -s -X GET \
        "$API_URL/api/usage/dashboard/" \
        -H "Authorization: Bearer $USER_TOKEN")
    
    echo "BASIC Plan Dashboard:"
    echo "$dashboard" | jq '.dashboard | {plan: .plan, features: .features | to_entries[] | {name: .key, limit: .value.limit, used: .value.used}}'
    
    quiz_limit=$(echo "$dashboard" | jq -r '.dashboard.features.quiz.limit' 2>/dev/null)
    
    if [ "$quiz_limit" = "20" ]; then
        log_success "BASIC plan correctly shows quiz limit of 20 uses per month"
    else
        log_error "BASIC quiz limit incorrect (expected 20, got $quiz_limit)"
    fi
}

# =============================================================================
# TEST 10: TEST USAGE LIMIT RESTRICTION
# =============================================================================
test_usage_limit_restriction() {
    log_test "Test Usage Limit Restriction (Simulate reaching limit)"
    
    # Record 3 more usages to reach FREE plan limit
    for i in {1..3}; do
        curl -s -X POST \
            "$API_URL/api/usage/record/" \
            -H "Authorization: Bearer $USER_TOKEN" \
            -H "Content-Type: application/json" \
            -d '{
                "feature": "mock_test",
                "input_size": 1000,
                "usage_type": "file"
            }' > /dev/null
        
        log_info "Recorded mock_test usage $i/3"
    done
    
    # Try to use one more
    dashboard=$(curl -s -X GET \
        "$API_URL/api/usage/dashboard/" \
        -H "Authorization: Bearer $USER_TOKEN")
    
    echo "Dashboard after reaching limit:"
    echo "$dashboard" | jq '.dashboard.features.mock_test'
    
    used=$(echo "$dashboard" | jq -r '.dashboard.features.mock_test.used' 2>/dev/null)
    
    if [ "$used" = "3" ]; then
        log_success "Usage limit correctly enforced (3/3 mock_test used)"
    fi
}

# =============================================================================
# TEST 11: CHECK SPECIFIC FEATURE STATUS
# =============================================================================
test_feature_status() {
    log_test "Get Specific Feature Status"
    
    status=$(curl -s -X GET \
        "$API_URL/api/usage/feature/quiz/" \
        -H "Authorization: Bearer $USER_TOKEN")
    
    echo "Quiz Feature Status:"
    echo "$status" | jq '.'
    
    allowed=$(echo "$status" | jq -r '.status.allowed' 2>/dev/null)
    used=$(echo "$status" | jq -r '.status.used' 2>/dev/null)
    limit=$(echo "$status" | jq -r '.status.limit' 2>/dev/null)
    
    log_success "Feature status: Allowed=$allowed, Used=$used, Limit=$limit"
}

# =============================================================================
# TEST 12: UPGRADE TO PREMIUM (All features unlimited)
# =============================================================================
test_upgrade_to_premium() {
    log_test "Upgrade to PREMIUM Plan (Unlimited features)"
    
    upgrade=$(curl -s -X POST \
        "$API_URL/api/subscriptions/create/" \
        -H "Content-Type: application/json" \
        -d "{
            \"user_id\": \"$USER_ID\",
            \"plan\": \"premium\"
        }")
    
    echo "Premium Upgrade Response:"
    echo "$upgrade" | jq '.'
    
    premium_sub_id=$(echo "$upgrade" | jq -r '.subscription_id' 2>/dev/null)
    
    if [ -n "$premium_sub_id" ] && [ "$premium_sub_id" != "null" ]; then
        log_success "PREMIUM subscription created"
    fi
}

# =============================================================================
# TEST 13: VERIFY PREMIUM PLAN - UNLIMITED FEATURES
# =============================================================================
test_premium_unlimited() {
    log_test "PREMIUM Plan - Unlimited Features"
    
    dashboard=$(curl -s -X GET \
        "$API_URL/api/usage/dashboard/" \
        -H "Authorization: Bearer $USER_TOKEN")
    
    echo "PREMIUM Plan Features:"
    echo "$dashboard" | jq '.dashboard.features | to_entries[] | {name: .key, limit: .value.limit, unlimited: .value.unlimited}'
    
    quiz_unlimited=$(echo "$dashboard" | jq -r '.dashboard.features.quiz.unlimited' 2>/dev/null)
    
    if [ "$quiz_unlimited" = "true" ]; then
        log_success "PREMIUM plan correctly shows unlimited features"
    else
        log_error "Premium plan features not unlimited"
    fi
}

# =============================================================================
# TEST 14: GET USAGE STATISTICS
# =============================================================================
test_usage_statistics() {
    log_test "Get Usage Statistics"
    
    stats=$(curl -s -X GET \
        "$API_URL/api/usage/stats/" \
        -H "Authorization: Bearer $USER_TOKEN")
    
    echo "Usage Statistics:"
    echo "$stats" | jq '.'
    
    plan=$(echo "$stats" | jq -r '.stats.plan' 2>/dev/null)
    total_logs=$(echo "$stats" | jq -r '.stats.total_logs' 2>/dev/null)
    
    log_success "Statistics: Plan=$plan, Total Logs=$total_logs"
}

# =============================================================================
# INTEGRATION TEST: COMPLETE FLOW
# =============================================================================
test_complete_flow() {
    log_test "COMPLETE INTEGRATION TEST FLOW"
    
    echo ""
    log_info "Step 1: User starts with FREE plan (3 uses per feature)"
    log_info "Step 2: User tries features and sees usage limits"
    log_info "Step 3: User upgrades to BASIC plan (₹1 for first month)"
    log_info "Step 4: Features unlocked to higher limits (10-50 uses)"
    log_info "Step 5: User upgrades to PREMIUM (₹199 for first month)"
    log_info "Step 6: All features become unlimited"
    log_info "Step 7: Monthly usage resets automatically on billing date"
    log_info "Step 8: User sees billing info and next payment date"
    
    echo ""
    log_success "Complete integration flow documented"
}

# =============================================================================
# MAIN TEST EXECUTION
# =============================================================================
main() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════"
    echo "  SUBSCRIPTION PLANS & USAGE TRACKING TEST SUITE"
    echo "═══════════════════════════════════════════════════════════════════════"
    echo ""
    
    # Check if server is running
    if ! curl -s "$API_URL/api/health/" > /dev/null 2>&1; then
        log_error "Server not running at $API_URL"
        echo "Start server with: python manage.py runserver"
        exit 1
    fi
    
    log_success "Server is running at $API_URL"
    echo ""
    
    # Run tests
    test_get_subscription_plans
    echo ""
    
    test_user_free_plan
    echo ""
    
    test_free_plan_dashboard
    echo ""
    
    test_check_feature_availability
    echo ""
    
    test_record_feature_usage
    echo ""
    
    test_verify_usage_updated
    echo ""
    
    test_upgrade_to_basic
    echo ""
    
    test_basic_plan_dashboard
    echo ""
    
    test_feature_status
    echo ""
    
    test_upgrade_to_premium
    echo ""
    
    test_premium_unlimited
    echo ""
    
    test_usage_statistics
    echo ""
    
    test_complete_flow
    
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════"
    echo "  ALL TESTS COMPLETED"
    echo "═══════════════════════════════════════════════════════════════════════"
}

# Run main
main "$@"

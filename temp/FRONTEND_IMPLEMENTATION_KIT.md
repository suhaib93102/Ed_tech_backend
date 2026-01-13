╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║             FRONTEND SUBSCRIPTION IMPLEMENTATION - COMPLETE KIT              ║
║                                                                              ║
║                     All Prompts, Messages & UI Guidelines                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OVERVIEW - WHAT YOU'LL FIND IN THESE GUIDES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This package contains 4 comprehensive frontend implementation guides:

1. ✅ FRONTEND_SUBSCRIPTION_GUIDE.md
   └─ Complete UI/UX implementation guide with all prompts, messages, and
      technical integration details. Start here for reference.

2. ✅ FRONTEND_FLOW_DIAGRAMS.md
   └─ Visual representations of user journeys, state machines, API sequences,
      and component hierarchies. Use while implementing.

3. ✅ COMPLETE_SYSTEM_IMPLEMENTATION_GUIDE.md
   └─ Backend reference for developers integrating with the API.

4. ✅ SUBSCRIPTION_SYSTEM_QUICK_REFERENCE.md
   └─ Quick lookup for common tasks and troubleshooting.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
QUICK IMPLEMENTATION GUIDE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: Read Documentation (30 minutes)
  1. FRONTEND_SUBSCRIPTION_GUIDE.md - Understand all UI elements
  2. FRONTEND_FLOW_DIAGRAMS.md - Visualize user flows
  3. SUBSCRIPTION_SYSTEM_QUICK_REFERENCE.md - Bookmark for lookup

Step 2: Understand API Endpoints (15 minutes)
  From COMPLETE_SYSTEM_IMPLEMENTATION_GUIDE.md:
  ✓ GET /api/subscriptions/plans/
  ✓ GET /api/subscriptions/status/
  ✓ POST /api/subscriptions/create/
  ✓ POST /api/usage/check/
  ✓ POST /api/usage/record/
  ✓ POST /api/subscriptions/webhook/ (backend only, not frontend)

Step 3: Build Components (1-2 hours)
  ✓ SubscriptionBadge - Show user's current status
  ✓ FeatureUsageBar - Show remaining uses per feature
  ✓ UpgradeDialog - Prompt when limit reached
  ✓ PlansComparison - Show available plans
  ✓ ConfirmationDialog - Confirm before payment
  ✓ SuccessModal - Show after payment
  ✓ AccountManagement - User subscription settings

Step 4: Implement Integration (1-2 hours)
  ✓ Hook: useSubscription() - Manage subscription state
  ✓ Hook: useFeatureCheck() - Check feature availability
  ✓ Hook: usePayment() - Handle Razorpay integration
  ✓ Middleware: Add feature checks before execution

Step 5: Test & Deploy (30 minutes)
  ✓ Test free tier: Use 3 times, verify block on 4th
  ✓ Test upgrade: Create subscription, verify unlimited
  ✓ Test payment: Complete mock payment, verify webhook
  ✓ Test error handling: Network error, payment failure
  ✓ Test responsive: Mobile, tablet, desktop


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DOCUMENT REFERENCE - FIND WHAT YOU NEED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Looking for...                           See Document...
─────────────────────────────────────    ────────────────────────────────────
UI mockups & layouts                     FRONTEND_SUBSCRIPTION_GUIDE.md
                                         → PART 1: User Status Display
                                         → PART 2: Feature Usage Display

Upgrade flow & prompts                   FRONTEND_SUBSCRIPTION_GUIDE.md
                                         → PART 3: Upgrade Flow & Prompts
                                         → PART 4: Razorpay Payment

Error & status messages                  FRONTEND_SUBSCRIPTION_GUIDE.md
                                         → PART 5: Error & Status Messages

Dashboard layouts                        FRONTEND_SUBSCRIPTION_GUIDE.md
                                         → PART 6: Dashboard & Account

Implementation checklist                 FRONTEND_SUBSCRIPTION_GUIDE.md
                                         → PART 7: Technical Checklist

Code examples                            FRONTEND_SUBSCRIPTION_GUIDE.md
                                         → PART 10: Code Examples

User journey flow                        FRONTEND_FLOW_DIAGRAMS.md
                                         → Complete User Journey Map

Auto-billing flow                        FRONTEND_FLOW_DIAGRAMS.md
                                         → Monthly Auto-Billing Flow

Subscription state machine               FRONTEND_FLOW_DIAGRAMS.md
                                         → State Machine Diagram

API call sequences                       FRONTEND_FLOW_DIAGRAMS.md
                                         → API Call Sequence Diagrams

Component structure                      FRONTEND_FLOW_DIAGRAMS.md
                                         → Component Composition

Error handling flowchart                 FRONTEND_FLOW_DIAGRAMS.md
                                         → Error Handling Flowchart

Responsive design                        FRONTEND_FLOW_DIAGRAMS.md
                                         → Responsive Design Breakpoints

Backend API reference                    COMPLETE_SYSTEM_IMPLEMENTATION_GUIDE.md
                                         → API Endpoints Reference

Quick lookups & troubleshooting          SUBSCRIPTION_SYSTEM_QUICK_REFERENCE.md


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CORE CONCEPTS TO UNDERSTAND
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Three User States:

   FREE USER:
   • plan = "free"
   • unlimited_access = false
   • Limit: 3 uses per feature per month
   • Show: "2/3 remaining this month"
   
   PAID USER (ACTIVE):
   • plan = "basic" or "premium"
   • subscription_status = "active"
   • unlimited_access = true
   • Show: "∞ Unlimited Access"
   
   PAYMENT FAILED (PAST_DUE):
   • plan = "basic" or "premium"
   • subscription_status = "past_due"
   • unlimited_access = false (reverted)
   • Show: "⚠️ Payment failed. Limited again."

2. Key Decision Points:

   On App Load:
   • GET /api/subscriptions/status/
   • Check unlimited_access flag
   • Show appropriate badge

   Before Feature Execution:
   • POST /api/usage/check/
   • If allowed = false → Show upgrade dialog
   • If allowed = true → Execute feature

   After Feature Success:
   • POST /api/usage/record/
   • Update local usage counter
   • Show remaining uses

3. API Response Patterns:

   Allowed Response:
   {
     "success": true,
     "status": {
       "allowed": true,
       "unlimited": true/false,
       "remaining": N
     }
   }
   
   Blocked Response:
   {
     "success": false,
     "error": "Limit reached",
     "status": {
       "allowed": false,
       "upgrade_required": true
     }
   }

4. User Actions:

   When Limit Reached:
   User clicks [START QUIZ] → Check returns allowed=false
   → Show upgrade dialog → User chooses plan
   → Create subscription → Redirect to Razorpay
   → Pay ₹1 → Webhook activates → Show success
   → Back to app → Unlimited access enabled

   When Subscription Active:
   User clicks [START QUIZ] → Check returns allowed=true
   → Feature executes → Record usage → Show results

   When Payment Fails:
   Monthly ₹99 fails → Webhook sets status=past_due
   → unlimited_access becomes false → Limits re-enabled
   → Next check shows blocked again


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMMON UI PATTERNS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Pattern 1: Status Badge (Top of Page)

Show user's subscription status at all times:

┌──────────────────────────────────────────┐
│ ✅ BASIC | Active | Unlimited Access     │
└──────────────────────────────────────────┘

or

┌──────────────────────────────────────────┐
│ 💰 FREE | 2/3 quizzes remaining         │
└──────────────────────────────────────────┘

Code:
const { subscription } = useSubscription();
return (
  <StatusBadge
    plan={subscription.plan}
    unlimited={subscription.unlimited_access}
    remaining={subscription.quiz_used ? 3 - subscription.quiz_used : 3}
  />
);


Pattern 2: Feature Card (Dashboard)

Each feature shows usage + action button:

┌──────────────────────────────┐
│ 📝 QUIZ                      │
├──────────────────────────────┤
│ Usage: ▓▓░ (2/3)             │
│ 1 remaining this month       │
│                              │
│ [START QUIZ] [UPGRADE]       │
└──────────────────────────────┘

Code:
<FeatureCard feature="quiz">
  {status.allowed ? (
    <button>START QUIZ</button>
  ) : (
    <>
      <p>Monthly limit reached</p>
      <button onClick={showUpgrade}>UPGRADE</button>
    </>
  )}
</FeatureCard>


Pattern 3: Upgrade Prompt (When Limit Reached)

Show modal with plans comparison:

┌────────────────────────────────────┐
│ UPGRADE TO CONTINUE                │
├────────────────────────────────────┤
│ You've used all 3 quizzes          │
│                                    │
│ ┌──────┐  ┌──────┐  ┌──────┐     │
│ │FREE  │  │BASIC │  │PREM  │     │
│ │₹0    │  │₹1→99 │  │₹199  │     │
│ │[✓]   │  │[PICK]│  │[PICK]│     │
│ └──────┘  └──────┘  └──────┘     │
│                                    │
│ [PROCEED] [MAYBE LATER]            │
└────────────────────────────────────┘

Code:
{!status.allowed && (
  <Modal title="Upgrade to Continue">
    <PlansComparison onSelect={handleUpgrade} />
  </Modal>
)}


Pattern 4: Loading States

Show loading indicator during API calls:

┌────────────────────────────────────┐
│ ⏳ Checking subscription status...  │
└────────────────────────────────────┘

Then

┌────────────────────────────────────┐
│ ⏳ Creating subscription order...   │
└────────────────────────────────────┘

Then

┌────────────────────────────────────┐
│ ⏳ Processing payment...             │
│ Please wait, do not close window   │
└────────────────────────────────────┘

Code:
{isLoading && <Loader message={loadingMessage} />}


Pattern 5: Error Handling

Show clear error with retry option:

┌────────────────────────────────────┐
│ ❌ UNABLE TO CONNECT               │
├────────────────────────────────────┤
│ We couldn't reach the server.      │
│                                    │
│ [RETRY] [CONTACT SUPPORT]          │
└────────────────────────────────────┘

Code:
{error && (
  <ErrorBanner
    message={error}
    onRetry={retryLastAction}
    onSupport={contactSupport}
  />
)}


Pattern 6: Success Confirmation

Show success message:

┌────────────────────────────────────┐
│ ✅ PAYMENT SUCCESSFUL!             │
├────────────────────────────────────┤
│ BASIC subscription activated       │
│ ₹1 charged, renews Feb 9           │
│                                    │
│ Unlimited access now enabled!      │
│ [BACK TO APP] [VIEW ACCOUNT]      │
└────────────────────────────────────┘

Code:
{paymentSuccess && (
  <SuccessModal
    title="Payment Successful!"
    message="You now have unlimited access"
    onClose={goBackToDashboard}
  />
)}


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IMPLEMENTATION CHECKLIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase 1: Setup (30 min)
☐ Create folder structure for components
☐ Set up custom hooks directory
☐ Create API service layer
☐ Install Razorpay SDK: npm install razorpay

Phase 2: State Management (45 min)
☐ Create useSubscription() hook
  └─ Fetch status on load
  └─ Auto-refresh every 5 minutes
  └─ Store in Context/Redux

☐ Create useFeatureCheck() hook
  └─ POST /api/usage/check/ before execution
  └─ Cache result briefly
  └─ Return allowed status

☐ Create usePayment() hook
  └─ Handle Razorpay integration
  └─ Manage payment flow
  └─ Return payment status

Phase 3: Components (2 hours)
☐ SubscriptionBadge component
  └─ Display plan, status, unlimited flag
  └─ Show usage counter for free users

☐ FeatureCard component
  └─ Show usage bar
  └─ Show action buttons
  └─ Conditional display based on availability

☐ UpgradeDialog component
  └─ List available plans
  └─ Show pricing
  └─ Handle plan selection

☐ PlansComparison component
  └─ Side-by-side plan comparison
  └─ Feature list for each plan
  └─ Select button for each

☐ PaymentConfirmation component
  └─ Show plan details
  └─ Show pricing
  └─ Confirm terms checkbox
  └─ Proceed button

☐ SuccessModal component
  └─ Show success message
  └─ Show subscription details
  └─ Action button to continue

☐ AccountManagement component
  └─ Show current plan details
  └─ Show billing history
  └─ Payment method management
  └─ Cancel subscription option

☐ Error boundaries
  └─ Catch and display API errors
  └─ Provide retry mechanism

Phase 4: Integration (2 hours)
☐ Wrap features with FeatureChecker
  └─ Check before execute
  └─ Show upgrade if needed

☐ Add feature execution middleware
  └─ Call useFeatureCheck()
  └─ If allowed, execute feature
  └─ Record usage after success

☐ Add Razorpay configuration
  └─ Load Razorpay script
  └─ Initialize with public key
  └─ Handle payment callback

☐ Add error handling
  └─ Network error retry
  └─ Payment error handling
  └─ Server error fallback

Phase 5: Testing (1-2 hours)
☐ Test free tier flow
  └─ Use feature 3x
  └─ Verify block on 4x

☐ Test upgrade flow
  └─ Click upgrade
  └─ Confirm details
  └─ Mock payment success

☐ Test unlimited access
  └─ Use feature unlimited times
  └─ Verify no limit shown

☐ Test responsive design
  └─ Mobile (< 600px)
  └─ Tablet (600-1024px)
  └─ Desktop (> 1024px)

☐ Test error scenarios
  └─ Network error
  └─ Payment failure
  └─ Server error (500)

☐ Test accessibility
  └─ Keyboard navigation
  └─ Screen reader support
  └─ Color contrast


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MESSAGES & COPY - READY TO USE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

All messages are provided in FRONTEND_SUBSCRIPTION_GUIDE.md:
→ PART 5: Error & Status Messages (for reference)
→ PART 8: Helpful Tooltips & Microcopy (for UI text)
→ PART 9: Empty States & No-Data Scenarios (for edge cases)

Copy everything as-is or customize for your brand voice.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DEPLOYMENT READINESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Before deploying frontend, ensure:

Backend:
☐ All 7 API endpoints working
☐ Database tables migrated
☐ Razorpay credentials configured
☐ Webhook endpoint accessible
☐ Error logging configured

Frontend:
☐ All components implemented
☐ All hooks working correctly
☐ API integration tested
☐ Error handling tested
☐ Responsive design verified
☐ Accessibility verified
☐ Performance optimized

Testing:
☐ E2E test: Free user flow
☐ E2E test: Upgrade flow
☐ E2E test: Payment flow
☐ Manual testing completed
☐ Browser compatibility checked

Deployment:
☐ Environment variables set (RAZORPAY_KEY)
☐ Build optimized (minified, tree-shaken)
☐ Error monitoring configured (Sentry, etc.)
☐ Analytics configured (track upgrade flow)
☐ Monitoring dashboard set up


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MONITORING & METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Track these metrics to measure success:

User Journey Metrics:
• % of users seeing upgrade prompt
• % of users clicking upgrade
• % of upgrades completed
• % of payments successful
• Average time to payment completion
• Upgrade conversion rate

Technical Metrics:
• API latency (goal: < 200ms)
• Payment success rate (goal: > 99%)
• Error rate (goal: < 0.5%)
• Webhook delivery rate (goal: 100%)
• Page load time (goal: < 2s)

Business Metrics:
• Active paid subscriptions
• Monthly recurring revenue (MRR)
• Churn rate
• Average customer lifetime value (LTV)
• Free to paid conversion rate


═══════════════════════════════════════════════════════════════════════════════════

                    👨‍💻 YOU HAVE EVERYTHING YOU NEED 👩‍💻

All UI designs, messages, flows, and code examples are provided in the 4
frontend guides. Pick them up and start implementing!

TIME ESTIMATE: 4-6 hours for complete implementation
(depending on your experience level)

═══════════════════════════════════════════════════════════════════════════════════

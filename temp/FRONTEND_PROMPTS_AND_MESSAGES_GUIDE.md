╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║              FRONTEND PROMPTS & MESSAGES - COMPLETE GUIDE                   ║
║                                                                              ║
║         All User-Facing Text for Subscription & Feature System              ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

This guide defines every prompt, message, and dialog that should appear to users
in the frontend application for the subscription and feature usage system.

═══════════════════════════════════════════════════════════════════════════════════

TABLE OF CONTENTS

1. Feature Usage Messages
2. Subscription & Upgrade Dialogs
3. Payment Flow Messages
4. Success Confirmations
5. Error Messages
6. Dashboard & Settings Text
7. Email Templates
8. In-App Notifications
9. Help & FAQ Text
10. Admin Dashboard Text

═══════════════════════════════════════════════════════════════════════════════════

PART 1: FEATURE USAGE MESSAGES

┌──────────────────────────────────────────────────────────────────────────────┐
│ 1.1 FEATURE AVAILABLE (Within Limit)                                        │
└──────────────────────────────────────────────────────────────────────────────┘

When user can still use feature (Free tier, uses < 3):

TITLE: "Feature Available"
SUBTITLE: "You have {remaining} uses left this month"

EXAMPLES:
  "You have 3 uses left this month"
  "You have 2 uses left this month"
  "You have 1 use left this month"

USAGE INDICATOR:
  Progress Bar: [████░░░░] 1/3 used
  Text: "Quiz: 1 of 3 monthly uses"

BUTTON: 
  "Continue" or "Proceed"


┌──────────────────────────────────────────────────────────────────────────────┐
│ 1.2 LIMIT REACHED - UPGRADE REQUIRED (Free Tier)                             │
└──────────────────────────────────────────────────────────────────────────────┘

When user has exhausted free tier (3/3 uses):

🎯 MODAL DIALOG
  ┌─────────────────────────────────────────────────────┐
  │ 📊 Monthly Limit Reached                            │
  │                                                     │
  │ You've used all 3 free uses of Quiz this month.    │
  │                                                     │
  │ ┌─────────────────────────────────────────────────┐ │
  │ │ Quiz: [████████] 3/3 (EXHAUSTED)               │ │
  │ │ Next reset: Feb 9, 2026                         │ │
  │ └─────────────────────────────────────────────────┘ │
  │                                                     │
  │ Upgrade to continue:                              │
  │ • BASIC: ₹1 first month, then ₹99/month          │
  │ • PREMIUM: ₹199/month for all features            │
  │                                                     │
  │ [Upgrade Now]  [Reset in 30 days]                 │
  └─────────────────────────────────────────────────────┘

TITLE: "Monthly Limit Reached"

HEADING: 
  "You've used all 3 free uses of {feature} this month"

SUBHEADING:
  "Upgrade to continue using all features unlimited"

FEATURE INFO BOX:
  Title: "{Feature Name}: Free Tier"
  Progress: [████████████] 3/3 (in RED)
  Message: "Monthly limit exhausted"
  Reset Date: "Next reset: {next_month_date}"

UPGRADE OPTIONS:
  Option 1:
    Plan: BASIC
    Price: ₹1 for first month
    Then: ₹99/month
    Features: All features, 3 uses per feature
    Button: "Choose BASIC" (blue)
  
  Option 2:
    Plan: PREMIUM
    Price: ₹199/month
    Features: All features UNLIMITED
    Button: "Choose PREMIUM" (gold)

SECONDARY OPTIONS:
  Button: "I'll wait for reset" (gray)
  Link: "Learn more about plans"

COUNTDOWN TEXT:
  "Your free uses reset on {date}"
  "Remaining days: 21 days"


┌──────────────────────────────────────────────────────┐
│ 1.3 FEATURE NOT AVAILABLE (Other Reasons)           │
└──────────────────────────────────────────────────────┘

When feature not available for other reasons:

ERROR MESSAGE:
  "Feature temporarily unavailable"
  
OR:
  "This feature is not available in your region"

OR:
  "You've been rate-limited. Try again in 1 hour."


┌──────────────────────────────────────────────────────┐
│ 1.4 UNLIMITED USAGE - PAID SUBSCRIBER               │
└──────────────────────────────────────────────────────┘

When paid user with active subscription:

✅ INDICATOR:
  Badge: "🔓 UNLIMITED"
  Text: "Quiz: Unlimited uses (PREMIUM)"
  
OR:

  "✓ Your subscription is active"
  "Quiz: Unlimited uses available"
  "Active until: Feb 9, 2026"

NO LIMIT SHOWN:
  Do not show "3/3" or progress bar
  Do not show limit message


═══════════════════════════════════════════════════════════════════════════════════

PART 2: SUBSCRIPTION & UPGRADE DIALOGS

┌──────────────────────────────────────────────────────┐
│ 2.1 UPGRADE FLOW - STEP 1: CHOOSE PLAN              │
└──────────────────────────────────────────────────────┘

DIALOG TITLE: "Upgrade Your Account"

HEADING: 
  "Get Unlimited Access"

SUBHEADING:
  "Choose your plan and upgrade today"

PLAN CARDS:

Plan 1: BASIC (Recommended)
  ┌─────────────────────────────────────────┐
  │ BASIC Plan                              │
  │ ⭐⭐⭐ Most Popular                      │
  │                                         │
  │ First Month: ₹1                         │
  │ Then: ₹99/month (auto-renews)          │
  │                                         │
  │ ✓ All 8 features                       │
  │ ✓ Limited uses (3 per feature)         │
  │ ✓ Priority support                     │
  │ ✓ Cancel anytime                       │
  │                                         │
  │        [Choose BASIC]                   │
  │                                         │
  └─────────────────────────────────────────┘

Plan 2: PREMIUM
  ┌─────────────────────────────────────────┐
  │ PREMIUM Plan                            │
  │ ⭐⭐⭐⭐⭐ Best Value                    │
  │                                         │
  │ ₹199/month (auto-renews)               │
  │                                         │
  │ ✓ All 8 features                       │
  │ ✓ UNLIMITED uses                       │
  │ ✓ No feature limits                    │
  │ ✓ 24/7 priority support               │
  │ ✓ Advanced analytics                   │
  │ ✓ Cancel anytime                       │
  │                                         │
  │        [Choose PREMIUM]                 │
  │                                         │
  └─────────────────────────────────────────┘

FEATURES COMPARISON TABLE:

  | Feature          | FREE | BASIC | PREMIUM |
  |------------------|------|-------|---------|
  | Quiz             | 3/mo | 3/mo  | UNLIM   |
  | Flashcards       | 3/mo | 3/mo  | UNLIM   |
  | Mock Test        | 3/mo | 3/mo  | UNLIM   |
  | Ask Question     | 3/mo | 3/mo  | UNLIM   |
  | YouTube Summary  | 3/mo | 3/mo  | UNLIM   |
  | Predicted Q's    | 3/mo | 3/mo  | UNLIM   |
  | Daily Quiz       | ✗    | ✓     | ✓       |
  | Pair Quiz        | ✗    | ✓     | ✓       |
  | Support          | FAQ  | Email | 24/7    |

FOOTER TEXT:
  "All plans include a 7-day money-back guarantee"
  "Autorenews monthly. Cancel anytime from Settings"


┌──────────────────────────────────────────────────────┐
│ 2.2 UPGRADE FLOW - STEP 2: CONFIRM PLAN             │
└──────────────────────────────────────────────────────┘

DIALOG TITLE: "Confirm Your Purchase"

SELECTED PLAN:
  Plan Name: "BASIC Plan"
  Price: "₹1 for first month"

DETAILS BOX:
  ┌─────────────────────────────────────────┐
  │ Billing Details                         │
  │                                         │
  │ First Charge: ₹1                        │
  │ Next Charge: ₹99 (March 9, 2026)       │
  │ Billing Cycle: Monthly                  │
  │                                         │
  │ ✓ Automatically renews every month      │
  │ ✓ Cancel anytime from account settings  │
  │ ✓ No hidden charges                     │
  └─────────────────────────────────────────┘

TERMS ACCEPTANCE:
  Checkbox: "I agree to the Terms of Service and Refund Policy"
  Link: "View terms" "View refund policy"

BUTTONS:
  Primary: "Proceed to Payment" (blue)
  Secondary: "Edit Plan" (gray)
  Tertiary: "Cancel" (X)


┌──────────────────────────────────────────────────────┐
│ 2.3 UPGRADE FLOW - STEP 3: PAYMENT PAGE             │
└──────────────────────────────────────────────────────┘

HEADING: 
  "Complete Your Purchase"

AMOUNT:
  "Total: ₹1 (First Month)"
  "Then ₹99/month"

RAZORPAY EMBEDDED:
  (Razorpay handles card details - never shown in frontend)
  
INSTRUCTION TEXT:
  "Enter your card details below to complete payment"
  "Your payment is secured with 256-bit encryption"
  "Razorpay is certified Level 1 PCI DSS compliant"

AFTER PAYMENT:
  "Processing your payment..."
  (Show loading spinner)


┌──────────────────────────────────────────────────────┐
│ 2.4 PAYMENT PROCESSING                              │
└──────────────────────────────────────────────────────┘

DURING PAYMENT:
  Status: "Verifying payment..."
  Message: "Your payment is being processed. Please wait."

ERRORS:
  
  Error 1 - Card Declined:
    "Card was declined by bank"
    "Try another payment method or contact your bank"
    Button: "Try Again"
  
  Error 2 - Payment Timeout:
    "Payment took too long"
    "Try again or contact support"
    Button: "Retry"
  
  Error 3 - Network Error:
    "Network error. Please check your connection"
    "Try again"
    Button: "Retry"


═══════════════════════════════════════════════════════════════════════════════════

PART 3: PAYMENT FLOW MESSAGES

┌──────────────────────────────────────────────────────┐
│ 3.1 PAYMENT SUCCESS                                 │
└──────────────────────────────────────────────────────┘

✅ SUCCESS SCREEN
  ┌─────────────────────────────────────────┐
  │                                         │
  │ ✅ Payment Successful!                 │
  │                                         │
  │ Thank you for your purchase             │
  │                                         │
  │ Plan: BASIC                             │
  │ Amount: ₹1                              │
  │ Date: January 10, 2026                  │
  │ Transaction ID: razorpay_abc123...      │
  │                                         │
  │ Your subscription is now active!        │
  │ You have UNLIMITED access to all        │
  │ features starting today.                │
  │                                         │
  │ Enjoy your learning!                    │
  │                                         │
  │        [Go to Dashboard]                │
  │                                         │
  │ Next billing date: February 9, 2026     │
  │                                         │
  └─────────────────────────────────────────┘

POPUP NOTIFICATION (if in middle of feature):
  "🎉 Upgrade successful!"
  "You now have unlimited access. Continue with your {feature}."

EMAIL CONFIRMATION (see Email Templates section)


┌──────────────────────────────────────────────────────┐
│ 3.2 PAYMENT PENDING                                 │
└──────────────────────────────────────────────────────┘

If payment takes longer to confirm:

WAITING SCREEN:
  "Processing payment..."
  "This usually takes less than 30 seconds"
  
  [Don't close this page]

IF STILL WAITING AFTER 30 SECONDS:
  "This is taking longer than expected"
  "Don't close this page"
  "Refresh page if needed - your payment won't be duplicated"


┌──────────────────────────────────────────────────────┐
│ 3.3 PAYMENT FAILED                                  │
└──────────────────────────────────────────────────────┘

❌ ERROR SCREEN
  ┌─────────────────────────────────────────┐
  │                                         │
  │ ❌ Payment Failed                       │
  │                                         │
  │ Your payment could not be processed     │
  │                                         │
  │ Reason: Card Declined                   │
  │                                         │
  │ What to try:                            │
  │ • Use a different card                  │
  │ • Check expiry date and CVV             │
  │ • Contact your bank                     │
  │ • Try again in a few minutes            │
  │                                         │
  │        [Try Again]     [Contact Support]│
  │                                         │
  └─────────────────────────────────────────┘

COMMON ERROR MESSAGES:

1. Card Declined
   Message: "Your card was declined. Please try another payment method."
   Action: "Try Again" or "Use Different Card"

2. Insufficient Funds
   Message: "Your card has insufficient funds."
   Action: "Try Different Card" or "Add Money to Account"

3. Network Error
   Message: "Network error during payment. Your card was not charged."
   Action: "Try Again"

4. Timeout
   Message: "Payment timed out. Please try again."
   Action: "Try Again"

5. Invalid Card
   Message: "Invalid card details. Please check and try again."
   Action: "Try Again"

CRITICAL TEXT:
  "Your card has NOT been charged"
  "You can safely try again"


═══════════════════════════════════════════════════════════════════════════════════

PART 4: SUCCESS CONFIRMATIONS

┌──────────────────────────────────────────────────────┐
│ 4.1 SUBSCRIPTION ACTIVATED                          │
└──────────────────────────────────────────────────────┘

BANNER (Top of App):
  🎉 Welcome to BASIC Plan!
  Your subscription is active. Enjoy unlimited access to {feature}!
  
  [Dismiss]

TOAST NOTIFICATION:
  Duration: 5 seconds
  "Subscription activated! You now have unlimited access."

BADGE ON FEATURES:
  Before: "FREE - 3/month"
  After: "🔓 UNLIMITED"


┌──────────────────────────────────────────────────────┐
│ 4.2 RENEWAL CONFIRMATION                            │
└──────────────────────────────────────────────────────┘

WHEN MONTHLY CHARGE SUCCESSFUL:

NOTIFICATION:
  "✓ Monthly Charge: ₹99 confirmed"
  "Your subscription has been renewed"
  "Active until: March 9, 2026"

EMAIL RECEIPT (see Email Templates section)


┌──────────────────────────────────────────────────────┐
│ 4.3 CANCELLATION CONFIRMATION                       │
└──────────────────────────────────────────────────────┘

WHEN USER CANCELS SUBSCRIPTION:

CONFIRMATION DIALOG:
  ┌─────────────────────────────────────────┐
  │ Are you sure?                           │
  │                                         │
  │ Your BASIC subscription will be         │
  │ cancelled at the end of your billing    │
  │ period (February 9, 2026)              │
  │                                         │
  │ Until then, you'll keep unlimited       │
  │ access to all features.                 │
  │                                         │
  │ You can reactivate anytime.             │
  │                                         │
  │ [Yes, Cancel]  [Keep Subscription]      │
  └─────────────────────────────────────────┘

SUCCESS MESSAGE:
  "✓ Subscription cancelled"
  "Your access continues until February 9, 2026"
  "After that, you'll be on the free plan"
  "Reactivate anytime from Settings"


═══════════════════════════════════════════════════════════════════════════════════

PART 5: ERROR MESSAGES

┌──────────────────────────────────────────────────────┐
│ 5.1 SUBSCRIPTION ERRORS                             │
└──────────────────────────────────────────────────────┘

Error 1 - Already Subscribed:
  "You already have an active subscription"
  "Upgrade your plan from Settings > Account"

Error 2 - Subscription Expired:
  "Your subscription has expired"
  "Renew your subscription to continue"
  Button: "Renew Now"

Error 3 - Payment Failed:
  "Your monthly payment failed"
  "Update your payment method to continue"
  Button: "Update Payment Method"

Error 4 - Billing Error:
  "Billing error: Please contact support"
  "We'll help you resolve this"
  Button: "Contact Support"


┌──────────────────────────────────────────────────────┐
│ 5.2 FEATURE ACCESS ERRORS                           │
└──────────────────────────────────────────────────────┘

Error 1 - Limit Reached:
  "Monthly limit reached"
  "Upgrade to continue using this feature"
  Button: "Upgrade Now"

Error 2 - Feature Not Available:
  "This feature is not available for you"
  "Contact support for more information"

Error 3 - Feature Error:
  "Feature processing failed"
  "Please try again or contact support"
  Button: "Retry"

Error 4 - Image Quality Poor:
  "Image quality too poor to process"
  "Try a clearer image"
  Suggestion: "Tips for better images: Good lighting, clear text"


┌──────────────────────────────────────────────────────┐
│ 5.3 SYSTEM ERRORS (Generic)                         │
└──────────────────────────────────────────────────────┘

Error: "Something went wrong"
Message: "We're experiencing technical difficulties"
Action: "Retry" or "Contact Support"

Error: "Network connection failed"
Message: "Check your internet and try again"

Error: "Server is busy"
Message: "Too many requests. Please wait and try again"

CRITICAL: Never show technical error codes to user
  ❌ "502 Bad Gateway"
  ❌ "CORS Error"
  ✅ "Temporarily unavailable. Please try again."


═══════════════════════════════════════════════════════════════════════════════════

PART 6: DASHBOARD & SETTINGS TEXT

┌──────────────────────────────────────────────────────┐
│ 6.1 SUBSCRIPTION STATUS CARD                        │
└──────────────────────────────────────────────────────┘

FOR FREE USERS:
  ┌─────────────────────────────────────┐
  │ Your Plan: FREE                     │
  │                                     │
  │ You have 3 uses/month per feature  │
  │ Current usage:                      │
  │                                     │
  │ Quiz: [████░░░░] 1/3               │
  │ Flashcards: [░░░░░░░░] 0/3         │
  │ Mock Test: [░░░░░░░░] 0/3          │
  │ Ask Question: [░░░░░░░░] 0/3       │
  │                                     │
  │ Monthly Reset: Feb 9, 2026          │
  │                                     │
  │         [Upgrade Now]               │
  └─────────────────────────────────────┘

FOR PAID USERS (ACTIVE):
  ┌─────────────────────────────────────┐
  │ ✅ Your Plan: BASIC (Active)        │
  │                                     │
  │ 🔓 UNLIMITED access to all features │
  │                                     │
  │ Subscription Details:               │
  │ • Started: January 10, 2026         │
  │ • Renews: February 9, 2026          │
  │ • Amount: ₹99/month                 │
  │                                     │
  │ Usage this month:                   │
  │ • Quiz: UNLIMITED (47 used)         │
  │ • Flashcards: UNLIMITED (23 used)   │
  │ • All others: UNLIMITED             │
  │                                     │
  │ Payment Method: •••• 1234           │
  │                                     │
  │ [Update Payment]  [Cancel Plan]     │
  └─────────────────────────────────────┘

FOR CANCELLED USERS:
  ┌─────────────────────────────────────┐
  │ Your Plan: FREE (Cancelled)         │
  │                                     │
  │ Your subscription ended on:         │
  │ February 9, 2026                    │
  │                                     │
  │ You now have 3 uses/month per       │
  │ feature as a free user.             │
  │                                     │
  │ Current Usage:                      │
  │ Quiz: [██████░░] 2/3                │
  │                                     │
  │         [Reactivate Plan]           │
  └─────────────────────────────────────┘

FOR PAST-DUE USERS:
  ┌─────────────────────────────────────┐
  │ ⚠️ Payment Failed                   │
  │                                     │
  │ Your monthly payment failed on      │
  │ February 9, 2026                    │
  │                                     │
  │ Your subscription is suspended.     │
  │ Feature limits have been restored.  │
  │                                     │
  │ Update your payment method to       │
  │ continue with unlimited access.     │
  │                                     │
  │ [Update Payment Now]                │
  │ [View Retry History]                │
  └─────────────────────────────────────┘


┌──────────────────────────────────────────────────────┐
│ 6.2 USAGE BREAKDOWN TABLE                           │
└──────────────────────────────────────────────────────┘

FEATURE TABLE:
  ┌─────────────────┬────────┬──────┬──────────┐
  │ Feature         │ Limit  │ Used │ Remaining│
  ├─────────────────┼────────┼──────┼──────────┤
  │ Quiz            │ 3      │ 1    │ 2        │
  │ Flashcards      │ 3      │ 0    │ 3        │
  │ Mock Test       │ 3      │ 2    │ 1        │
  │ Ask Question    │ 3      │ 3    │ 0 ❌     │
  │ Pair Quiz       │ ❌     │ 0    │ —        │
  │ Daily Quiz      │ ❌     │ 0    │ —        │
  │ YouTube Summary │ 3      │ 0    │ 3        │
  │ Prev Questions  │ 3      │ 1    │ 2        │
  └─────────────────┴────────┴──────┴──────────┘

FOR PAID USERS:
  ┌─────────────────┬────────┬───────┐
  │ Feature         │ Status │ Usage │
  ├─────────────────┼────────┼───────┤
  │ Quiz            │ 🔓 All │ 47    │
  │ Flashcards      │ 🔓 All │ 23    │
  │ Mock Test       │ 🔓 All │ 12    │
  │ Ask Question    │ 🔓 All │ 5     │
  │ All others      │ 🔓 All │ ...   │
  └─────────────────┴────────┴───────┘


┌──────────────────────────────────────────────────────┐
│ 6.3 SETTINGS PAGE                                   │
└──────────────────────────────────────────────────────┘

ACCOUNT SECTION:

Subscription Settings:
  Label: "Subscription"
  Value: "BASIC Plan (Active)"
  Actions: "Change Plan" | "Cancel Subscription"

Billing Information:
  Label: "Next Billing Date"
  Value: "February 9, 2026"
  
  Label: "Payment Method"
  Value: "Visa ending in 1234"
  Actions: "Update" | "Add Card"

Billing History:
  Label: "Recent Charges"
  Value: "View billing history"
  Link: "See all transactions"


═══════════════════════════════════════════════════════════════════════════════════

PART 7: EMAIL TEMPLATES

┌──────────────────────────────────────────────────────┐
│ 7.1 WELCOME EMAIL (New Subscription)                │
└──────────────────────────────────────────────────────┘

SUBJECT: 
  "Welcome to EdTech Premium! Your subscription is active"

BODY:
  Dear {name},

  🎉 Welcome to EdTech BASIC Plan!

  Your subscription is now active, and you have unlimited access
  to all learning features.

  Subscription Details:
  • Plan: BASIC Plan
  • Start Date: January 10, 2026
  • Next Renewal: February 9, 2026
  • Monthly Cost: ₹99/month
  • Transaction ID: {transaction_id}
  
  First Payment: ₹1 (Trial period for first month)

  What You Can Now Do:
  ✓ Unlimited Quiz attempts
  ✓ Unlimited Flashcard generation
  ✓ Unlimited Mock Tests
  ✓ And 5 more premium features...

  Your next billing cycle:
  On February 9, 2026, we'll automatically charge ₹99 to your
  payment method ending in 1234.

  Need Help?
  • FAQ: {faq_link}
  • Contact Support: {support_email}
  • Update Payment: {payment_link}

  Happy Learning!
  EdTech Team


┌──────────────────────────────────────────────────────┐
│ 7.2 RENEWAL EMAIL (Automatic Charge)                │
└──────────────────────────────────────────────────────┘

SUBJECT:
  "Your EdTech subscription has been renewed ✓"

BODY:
  Dear {name},

  ✓ Your subscription has been successfully renewed!

  Payment Received:
  • Amount: ₹99
  • Date: February 9, 2026
  • Transaction ID: {transaction_id}
  • Payment Method: •••• 1234

  Next Renewal Date: March 9, 2026

  Your unlimited access is active!
  Keep learning with all premium features.

  [View Receipt]

  Need Help?
  {support_link}


┌──────────────────────────────────────────────────────┐
│ 7.3 PAYMENT FAILED EMAIL                            │
└──────────────────────────────────────────────────────┘

SUBJECT:
  "⚠️ Your EdTech payment failed - Action needed"

BODY:
  Dear {name},

  ⚠️ Your monthly subscription payment could not be processed.

  Failed Payment Details:
  • Amount: ₹99
  • Date Attempted: February 9, 2026
  • Reason: Card declined by bank
  • Next Retry: February 12, 2026

  What to Do Now:
  1. Update your payment method immediately
  2. We'll retry the payment in 3 days
  3. Your subscription remains active until the retry fails

  If payment fails after 3 retries, your subscription will be
  suspended and you'll lose premium access.

  [Update Payment Method]

  If the issue persists, contact your bank or try a different
  payment method.

  Contact Support:
  {support_link}

  EdTech Team


┌──────────────────────────────────────────────────────┐
│ 7.4 CANCELLATION CONFIRMATION EMAIL                 │
└──────────────────────────────────────────────────────┘

SUBJECT:
  "Your EdTech subscription has been cancelled"

BODY:
  Dear {name},

  Your BASIC Plan subscription has been cancelled.

  Cancellation Details:
  • Plan: BASIC
  • Last Payment: February 9, 2026
  • Cancellation Date: February 10, 2026
  • Final Charge: None (already paid through Feb 9)

  What Happens Now:
  • Your unlimited access ends on February 9, 2026
  • After that, you'll be on the FREE plan
  • FREE plan includes 3 uses/month per feature
  • You can reactivate anytime

  Want to Come Back?
  [Reactivate Subscription]

  Feedback:
  We'd love to know why you cancelled. Your feedback helps us
  improve!
  [Share Feedback]

  Thank you for using EdTech!
  EdTech Team


═══════════════════════════════════════════════════════════════════════════════════

PART 8: IN-APP NOTIFICATIONS

┌──────────────────────────────────────────────────────┐
│ 8.1 TOAST NOTIFICATIONS (Bottom Right)              │
└──────────────────────────────────────────────────────┘

Type: SUCCESS (Green)
Duration: 3 seconds
Examples:
  "✓ Payment successful!"
  "✓ Subscription activated"
  "✓ Plan upgraded to PREMIUM"
  "✓ Quiz completed"

Type: ERROR (Red)
Duration: 5 seconds
Examples:
  "✗ Payment failed. Try again."
  "✗ Monthly limit reached"
  "✗ Feature not available"
  "✗ Try again in a few minutes"

Type: INFO (Blue)
Duration: 4 seconds
Examples:
  "ℹ️ Processing your payment..."
  "ℹ️ Checking your eligibility..."
  "ℹ️ Refreshing your account..."

Type: WARNING (Orange)
Duration: 6 seconds
Examples:
  "⚠️ Your monthly payment is due soon"
  "⚠️ Payment method expires soon"
  "⚠️ You've used 2/3 free uses"


┌──────────────────────────────────────────────────────┐
│ 8.2 BANNER NOTIFICATIONS (Top of Page)              │
└──────────────────────────────────────────────────────┘

Type: ALERT (Red Background)
  "⚠️ Your payment failed. Update your payment method to continue."
  [Update Now] [Dismiss]

Type: INFO (Blue Background)
  "ℹ️ Special offer: Get PREMIUM for ₹99/month this month!"
  [Learn More] [Dismiss]

Type: SUCCESS (Green Background)
  "✅ Welcome! Your subscription is now active."
  [Dismiss]

Type: REMINDER (Orange Background)
  "📅 Your subscription renews on February 9, 2026"
  [Manage Subscription] [Dismiss]


┌──────────────────────────────────────────────────────┐
│ 8.3 BADGES & INDICATORS                             │
└──────────────────────────────────────────────────────┘

Feature Badges:
  FREE Tier: "FREE - 3/month"
  UNLIMITED: "🔓 UNLIMITED"
  UNAVAILABLE: "🔒 Upgrade required"

Status Badges:
  Active: "✅ ACTIVE"
  Trial: "⭐ TRIAL PERIOD"
  Past Due: "⚠️ PAYMENT FAILED"
  Cancelled: "❌ CANCELLED"

Plan Badge:
  "BASIC" or "PREMIUM" displayed in top-right corner


═══════════════════════════════════════════════════════════════════════════════════

PART 9: HELP & FAQ TEXT

┌──────────────────────────────────────────────────────┐
│ 9.1 FAQ ANSWERS                                     │
└──────────────────────────────────────────────────────┘

Q: What's the difference between FREE and BASIC plans?
A: 
  FREE Plan: 3 uses per feature per month
  BASIC Plan: All features with same 3 uses/month limit
  
  Most users choose BASIC for better support and priority access
  to new features.

Q: Will I be charged after the free trial?
A: 
  Yes, after your first month (₹1), we'll charge ₹99 on the same
  date every month. You can cancel anytime from Settings.

Q: What happens if my payment fails?
A: 
  We'll retry your payment 3 times over a few days. If all retries
  fail, your subscription will be suspended and you'll lose premium
  access. Update your payment method to restore access.

Q: Can I change my plan later?
A: 
  Yes! You can upgrade, downgrade, or cancel anytime from
  Settings > Subscription. Changes take effect immediately.

Q: Can I get a refund?
A: 
  We offer a 7-day money-back guarantee on your first purchase.
  After that, there are no refunds, but you can cancel anytime
  to stop future charges.

Q: Is my payment information secure?
A: 
  Yes. We use Razorpay, which is Level 1 PCI DSS certified.
  Your card details are never stored on our servers.

Q: Do you offer student discounts?
A: 
  Not currently, but check our website for any ongoing promotions!

Q: What if I need more than 3 uses per month?
A: 
  Upgrade to BASIC or PREMIUM for unlimited uses. Both plans
  include all features.


┌──────────────────────────────────────────────────────┐
│ 9.2 HELP CENTER ARTICLES                            │
└──────────────────────────────────────────────────────┘

Article 1: Getting Started with EdTech
  "Learn how to use EdTech and get the most out of your account"
  Topics: Create account, verify email, set preferences

Article 2: Understanding Feature Limits
  "Why you have limits and how to unlock unlimited access"
  Topics: Free tier, feature limits, upgrade benefits

Article 3: Subscription Management
  "Manage your subscription, upgrade, or cancel anytime"
  Topics: View plan, change plan, cancel, update payment

Article 4: Payment & Billing
  "How billing works and what to do if payment fails"
  Topics: Billing cycle, payment methods, failed payments

Article 5: Troubleshooting
  "Fix common issues and get help"
  Topics: Payment issues, access issues, technical problems


═══════════════════════════════════════════════════════════════════════════════════

PART 10: ADMIN DASHBOARD TEXT

┌──────────────────────────────────────────────────────┐
│ 10.1 ADMIN METRICS DISPLAY                          │
└──────────────────────────────────────────────────────┘

REVENUE METRICS:
  Total Revenue (This Month): ₹15,234
  Total Subscriptions: 47
  Active Subscriptions: 38
  Cancelled (Month): 2
  Failed Payments: 3

USER METRICS:
  Total Users: 312
  Free Users: 256
  Basic Subscribers: 38
  Premium Subscribers: 9
  Trial Users: 9

FEATURE METRICS:
  Most Used Feature: Quiz (247 uses)
  Least Used Feature: Daily Quiz (12 uses)
  Avg Uses/User: 3.2
  Usage Growth: +12% vs last month

PAYMENT METRICS:
  Successful Payments: 156
  Failed Payments: 3
  Success Rate: 98.1%
  Avg Transaction: ₹82
  Total Refunds: ₹0


┌──────────────────────────────────────────────────────┐
│ 10.2 ADMIN ACTIONS & MESSAGES                        │
└──────────────────────────────────────────────────────┘

Action: Refund User
  Confirmation: "Issue ₹99 refund to {email}?"
  Success: "✓ Refund of ₹99 issued to {email}"
  Email Sent: "Refund notification sent to user"

Action: Cancel User Subscription
  Confirmation: "Cancel subscription for {email}?"
  Success: "✓ Subscription cancelled"
  Access Removed: "User reverted to free plan"

Action: Manual Payment Approval
  Confirmation: "Approve manual payment of ₹99?"
  Success: "✓ Payment approved"
  Subscription Updated: "Subscription marked active"

Action: Send Custom Email
  Recipients: Select users or segments
  Template: Choose email template
  Preview: Show preview
  Send: "Send to {N} users"
  Success: "✓ Email sent to {N} users"


═══════════════════════════════════════════════════════════════════════════════════

STYLE GUIDE

┌──────────────────────────────────────────────────────┐
│ TONE & VOICE                                        │
└──────────────────────────────────────────────────────┘

✓ DO:
  - Be clear and friendly
  - Use action-oriented language
  - Explain WHY limits exist
  - Offer solutions
  - Be concise

❌ DON'T:
  - Be judgmental about users on free tier
  - Use technical jargon
  - Guilt-trip users
  - Be pushy about upgrades
  - Use ALL CAPS except for emphasized words


┌──────────────────────────────────────────────────────┐
│ FORMATTING GUIDELINES                               │
└──────────────────────────────────────────────────────┘

Prices:
  ✓ "₹1 first month"
  ✓ "₹99/month"
  ❌ "Rs. 1"
  ❌ "$1"

Dates:
  ✓ "January 10, 2026"
  ✓ "Feb 9, 2026"
  ❌ "01/10/26"

Features:
  ✓ "Quiz"
  ✓ "Flashcards"
  ✓ "Mock Test"
  ✓ "Pair Quiz"

Plans:
  ✓ "FREE" or "Free"
  ✓ "BASIC" or "Basic"
  ✓ "PREMIUM" or "Premium"

Numbers:
  ✓ "3 uses per month"
  ✓ "₹99/month"
  ❌ "0.5 uses per month"

Emojis (Minimal, intentional):
  ✓ "🎉" for celebration
  ✓ "✓" for success
  ✓ "⚠️" for warning
  ✓ "📅" for dates
  ❌ Overuse or inappropriate


┌──────────────────────────────────────────────────────┐
│ ACCESSIBILITY                                       │
└──────────────────────────────────────────────────────┘

For Color-Blind Users:
  ✓ Don't use color alone
  ✓ Use icons + text
  ✓ Example: "✓ Success (Green)" not just green
  
For Screen Readers:
  ✓ Use semantic HTML
  ✓ Include alt text on images
  ✓ Use labels on form inputs
  ✓ Include aria-labels on buttons

For Mobile Users:
  ✓ Large touch targets (48px minimum)
  ✓ Concise messages
  ✓ Clear calls-to-action
  ✓ No text smaller than 14px


═══════════════════════════════════════════════════════════════════════════════════

QUICK REFERENCE - COMMON SCENARIOS

┌──────────────────────────────────────────────────────┐
│ SCENARIO 1: User tries 4th Quiz (limit reached)    │
└──────────────────────────────────────────────────────┘

Flow:
  1. Show error modal: "Monthly Limit Reached"
  2. Show feature status: "Quiz: 3/3"
  3. Show upgrade options: BASIC and PREMIUM
  4. User clicks "Upgrade to BASIC"
  5. Process payment
  6. Show success and re-enable feature


┌──────────────────────────────────────────────────────┐
│ SCENARIO 2: Payment fails, then succeeds           │
└──────────────────────────────────────────────────────┘

Flow:
  1. Show error: "Payment failed - Try again"
  2. User updates card
  3. Retry payment
  4. Success: "Subscription renewed"
  5. Remove warning banners
  6. Restore unlimited access


┌──────────────────────────────────────────────────────┐
│ SCENARIO 3: User upgrades from FREE to PREMIUM     │
└──────────────────────────────────────────────────────┘

Flow:
  1. Show upgrade dialog
  2. Select PREMIUM plan
  3. Confirm billing details
  4. Process payment (₹199)
  5. Show success: "Upgraded to PREMIUM"
  6. Update all feature limits to unlimited
  7. Offer to start feature immediately


═══════════════════════════════════════════════════════════════════════════════════

IMPLEMENTATION CHECKLIST

Frontend Developer - Review These:

☐ All error messages in /Part 5
☐ All success messages in /Part 4
☐ All prompts in /Part 1-3
☐ All dashboard text in /Part 6
☐ All badge text in /Part 8
☐ All email templates in /Part 7
☐ Style guide in formatting section
☐ Accessibility guidelines
☐ Test all scenarios from Quick Reference

API Integration Checklist:

☐ Show message when feature allowed
☐ Show message when feature blocked
☐ Show message when payment processing
☐ Show message when payment succeeds
☐ Show message when payment fails
☐ Show dashboard with feature status
☐ Send emails for all transactions
☐ Show notifications for all state changes


═══════════════════════════════════════════════════════════════════════════════════

FINAL NOTES

1. CONSISTENCY: Use the exact text from this guide in your frontend
2. LOCALIZATION: If adding other languages, translate carefully
3. TESTING: Test all messages with real users before launch
4. UPDATES: Keep this guide updated as you add new features
5. A/B TESTING: Consider A/B testing different upgrade messages
6. TONE: Maintain friendly, helpful tone throughout app
7. CLARITY: Every message should be clear to non-technical users

═══════════════════════════════════════════════════════════════════════════════════

This guide is the single source of truth for all user-facing text in the
subscription and feature usage system. Reference it while building your frontend!

# Usage Tracking & Feature Restriction Endpoints

## Overview

Comprehensive API endpoints for real-time usage tracking, feature restrictions, and quota enforcement. All endpoints are protected with authentication and enforce subscription-based feature limits.

---

## Core Endpoints

### 1. Real-Time Usage Tracking
**GET** `/api/usage/real-time/`

Get real-time usage data for all features with current status.

**Requirements:** Authentication Required

**Response:**
```json
{
    "success": true,
    "timestamp": "2026-01-10T12:00:00Z",
    "plan": "free",
    "subscription_status": "active",
    "feature_usage": {
        "quiz": {
            "name": "Quiz",
            "used": 2,
            "limit": 3,
            "remaining": 1,
            "percentage": 66.67,
            "allowed": true
        },
        "flashcards": {
            "name": "Flashcards",
            "used": 3,
            "limit": 3,
            "remaining": 0,
            "percentage": 100,
            "allowed": false
        },
        ...
    },
    "summary": {
        "total_features": 10,
        "features_available": 8,
        "features_exhausted": 2
    }
}
```

**Query Parameters:** None

---

### 2. Usage History
**GET** `/api/usage/history/`

Get detailed usage history with filtering options.

**Requirements:** Authentication Required

**Query Parameters:**
- `feature` (optional): Filter by specific feature name
- `days` (optional): Number of days to retrieve (default: 7, max: 30)

**Example:**
```
GET /api/usage/history/?feature=quiz&days=7
```

**Response:**
```json
{
    "success": true,
    "query_period_days": 7,
    "start_date": "2026-01-03T12:00:00Z",
    "end_date": "2026-01-10T12:00:00Z",
    "total_entries": 25,
    "history": {
        "quiz": [
            {
                "input_size": 1000,
                "type": "text",
                "timestamp": "2026-01-10T11:30:00Z"
            },
            ...
        ],
        "flashcards": [...]
    }
}
```

---

### 3. Feature Restriction Details
**GET** `/api/usage/restriction/<feature_name>/`

Get detailed restriction information for a specific feature.

**Requirements:** Authentication Required

**Path Parameters:**
- `feature_name`: Name of the feature (e.g., 'quiz', 'flashcards')

**Example:**
```
GET /api/usage/restriction/quiz/
```

**Response:**
```json
{
    "success": true,
    "restriction_details": {
        "feature": "quiz",
        "feature_display_name": "Quiz",
        "allowed": true,
        "plan": "free",
        "subscription_status": "active",
        "usage": 2,
        "limit": 3,
        "remaining": 1,
        "percentage_used": 66.67,
        "can_use": true
    },
    "timestamp": "2026-01-10T12:00:00Z"
}
```

**For Restricted Features:**
```json
{
    "success": true,
    "restriction_details": {
        "feature": "flashcards",
        "feature_display_name": "Flashcards",
        "allowed": false,
        "plan": "free",
        "subscription_status": "active",
        "usage": 3,
        "limit": 3,
        "remaining": 0,
        "percentage_used": 100,
        "can_use": false,
        "restriction_reason": "Feature limit exhausted for free plan",
        "how_to_unlock": "Upgrade your subscription plan to unlimited access"
    }
}
```

---

## Enforcement & Testing Endpoints

### 4. Enforce Usage Check
**POST** `/api/usage/enforce-check/`

Strict enforcement endpoint - returns 403 if quota exhausted.

**Requirements:** Authentication Required

**Request Body:**
```json
{
    "feature": "quiz"
}
```

**Success Response (200):**
```json
{
    "success": true,
    "message": "Feature access granted",
    "feature": "quiz",
    "remaining": 1
}
```

**Restricted Response (403):**
```json
{
    "success": false,
    "error": "Feature access denied: Feature limit exhausted for free plan",
    "feature": "quiz",
    "status": {
        "allowed": false,
        "reason": "Feature limit exhausted for free plan",
        "limit": 3,
        "used": 3
    }
}
```

---

### 5. Test Feature Restriction
**POST** `/api/usage/test/restriction/`

Test endpoint to verify feature restrictions are working properly.

**Requirements:** Authentication Required

**Request Body:**
```json
{
    "feature": "quiz",
    "simulate_quota_exhausted": false
}
```

**Response:**
```json
{
    "success": true,
    "test_type": "feature_availability_check",
    "feature": "quiz",
    "allowed": true,
    "reason": "Feature available",
    "status": {
        "allowed": true,
        "reason": "Feature available",
        "limit": 3,
        "used": 2
    }
}
```

---

### 6. Test All Features
**POST** `/api/usage/test/all-features/`

Comprehensive test to check all features for availability and restrictions.

**Requirements:** Authentication Required

**Request Body:** Empty or {}

**Response:**
```json
{
    "success": true,
    "test_results": {
        "timestamp": "2026-01-10T12:00:00Z",
        "user_id": "user_123",
        "plan": "free",
        "subscription_status": "active",
        "features_tested": {
            "quiz": {
                "display_name": "Quiz",
                "allowed": true,
                "reason": "Feature available",
                "is_unlimited": false,
                "usage": 2,
                "limit": 3,
                "remaining": 1,
                "percentage_used": 66.67
            },
            "flashcards": {
                "display_name": "Flashcards",
                "allowed": false,
                "reason": "Feature limit exhausted for free plan",
                "is_unlimited": false,
                "usage": 3,
                "limit": 3,
                "remaining": 0,
                "percentage_used": 100
            },
            ...
        },
        "summary": {
            "total_features": 10,
            "features_available": 8,
            "features_restricted": 2,
            "features_unlimited": 0
        }
    }
}
```

---

## Feature Check & Usage Recording

### 7. Check Feature Usage (Pre-Request)
**POST** `/api/usage/check/`

Check if user can use a feature BEFORE making the actual request.

**Requirements:** Authentication Required

**Request Body:**
```json
{
    "feature": "quiz"
}
```

**Success Response (200):**
```json
{
    "success": true,
    "message": "Feature available",
    "status": {
        "allowed": true,
        "reason": "Feature available",
        "limit": 3,
        "used": 2
    }
}
```

**Restricted Response (403):**
```json
{
    "success": false,
    "error": "Feature limit exhausted for free plan",
    "status": {
        "allowed": false,
        "reason": "Feature limit exhausted for free plan",
        "limit": 3,
        "used": 3
    }
}
```

---

### 8. Record Feature Usage (Post-Request)
**POST** `/api/usage/record/`

Record feature usage AFTER successful feature use.

**Requirements:** Authentication Required

**Request Body:**
```json
{
    "feature": "quiz",
    "input_size": 1000,
    "usage_type": "text"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Usage recorded",
    "remaining_uses": 0
}
```

---

## Legacy Endpoints (Still Supported)

### 9. Usage Dashboard
**GET** `/api/usage/dashboard/`

Get user's complete usage dashboard.

**Requirements:** Authentication Required

---

### 10. Feature Status
**GET** `/api/usage/feature/<feature_name>/`

Check status of a specific feature.

**Requirements:** Authentication Required

---

### 11. Check Feature Usage
**POST** `/api/usage/check/`

Legacy endpoint to check feature availability.

**Requirements:** Authentication Required

---

### 12. Subscription Status
**GET** `/api/usage/subscription/`

Get user's subscription status and details.

**Requirements:** Authentication Required

---

### 13. Usage Stats
**GET** `/api/usage/stats/`

Get usage statistics and trends.

**Requirements:** Authentication Required

---

## Feature Limits by Plan

### Free Plan
- Quiz: 3 uses
- Flashcards: 3 uses
- Pair Quiz: 1 use
- Ask Question: 5 uses
- Predicted Questions: 3 uses
- YouTube Summarizer: 2 uses
- Other Features: Limited

### Basic Plan
- All features unlimited

### Premium Plan
- All features unlimited
- Priority support
- Advanced analytics

---

## Implementation Guide

### For Frontend Developers

**Step 1: Check Feature Before Using**
```javascript
// Before triggering a quiz
const response = await fetch('/api/usage/check/', {
    method: 'POST',
    body: JSON.stringify({ feature: 'quiz' })
});

if (!response.ok) {
    // Feature not available - show upgrade prompt
    showUpgradeModal();
} else {
    // Feature available - proceed
    startQuiz();
}
```

**Step 2: Record Usage After Completion**
```javascript
// After quiz completion
await fetch('/api/usage/record/', {
    method: 'POST',
    body: JSON.stringify({
        feature: 'quiz',
        input_size: content.length,
        usage_type: 'text'
    })
});
```

**Step 3: Show Real-Time Usage**
```javascript
// Display usage in dashboard
const response = await fetch('/api/usage/real-time/');
const data = await response.json();

// Display feature_usage data in UI
renderUsageChart(data.feature_usage);
```

---

## API Response Codes

| Code | Meaning |
|------|---------|
| 200 | Feature available, operation successful |
| 201 | Resource created |
| 400 | Invalid request (missing fields, bad format) |
| 403 | Feature access denied (quota exhausted) |
| 404 | Feature not found |
| 500 | Server error |

---

## Error Handling

### Common Errors

**Missing Feature Name:**
```json
{
    "success": false,
    "error": "feature name is required"
}
```

**Invalid JSON:**
```json
{
    "success": false,
    "error": "Invalid JSON"
}
```

**Feature Not Found:**
```json
{
    "success": false,
    "error": "Feature \"unknown_feature\" not found"
}
```

**Quota Exhausted:**
```json
{
    "success": false,
    "error": "Feature access denied: Feature limit exhausted for free plan",
    "status": {
        "allowed": false,
        "reason": "Feature limit exhausted for free plan"
    }
}
```

---

## Real-Time Updates

All endpoints return current usage data with timestamp. Usage is updated in real-time as features are used:

1. User requests feature (calls `/api/usage/check/`)
2. Feature is granted or denied based on limits
3. After successful use, `/api/usage/record/` is called
4. Real-time endpoints immediately reflect the new usage

---

## Restrictions & Enforcement

### Feature Restriction Rules

1. **Free Plan**: Limited uses per feature (usually 3)
2. **Paid Plan**: Unlimited uses (subscription_status = 'active')
3. **Expired Subscription**: Reverts to free tier limits
4. **Past Due Payment**: Feature access restricted immediately

### Enforcement Points

1. **Check Before Use** (`/api/usage/enforce-check/`)
   - Called before every feature use
   - Returns 403 if quota exhausted
   - Prevents over-usage

2. **Real-Time Tracking** (`/api/usage/real-time/`)
   - Updates instantly on usage
   - Shows accurate remaining quota
   - Displays all feature statuses

3. **History Retention** (`/api/usage/history/`)
   - Tracks all usage for 30 days
   - Detailed per-feature breakdown
   - Supports filtering and date ranges

---

## Testing

Run the comprehensive test suite:

```bash
python test_usage_endpoints.py
```

This tests:
- Real-time usage tracking
- Usage history retrieval
- Feature restriction details
- Enforcement checks
- All features test
- Restriction simulation
- Pre-usage checks
- Post-usage recording

---

## Security

All endpoints require authentication. API key/token is validated for each request. Usage data is isolated per user - users can only see their own usage.

---

## Changelog

### Version 1.0 (Current)
- Real-time usage tracking
- Comprehensive feature restrictions
- Enforcement endpoints
- Test endpoints for validation
- Detailed history tracking


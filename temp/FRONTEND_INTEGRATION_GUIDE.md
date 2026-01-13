# FEATURE USAGE SYSTEM - IMPLEMENTATION GUIDE FOR FRONTEND

## Quick Start Example

### Register Feature Usage in Your Components

#### 1. Quiz Component Example
```javascript
// src/components/Quiz.jsx

import { useFeatureUsage } from '../hooks/useFeatureUsage';

export function QuizComponent() {
  const { checkAccess, recordUsage } = useFeatureUsage();
  const [isLoading, setIsLoading] = useState(false);

  const handleStartQuiz = async () => {
    // Step 1: Check if user can access feature
    const canAccess = await checkAccess('quiz');
    
    if (!canAccess) {
      showUpgradeDialog('Quiz limit reached', 'Upgrade to Premium for unlimited quizzes');
      return;
    }

    setIsLoading(true);
    try {
      // Step 2: Execute quiz
      const result = await executeQuiz();
      
      // Step 3: Record usage after success
      const input_size = result.questions.length;
      await recordUsage({
        feature: 'quiz',
        input_size: input_size,
        usage_type: 'text'
      });

      // Step 4: Show success and remaining attempts
      showSuccess(`Quiz completed! ${result.remaining} attempts left`);
    } catch (error) {
      showError('Failed to complete quiz');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button onClick={handleStartQuiz} disabled={isLoading}>
      {isLoading ? 'Starting...' : 'Start Quiz'}
    </button>
  );
}
```

#### 2. React Hook Implementation
```javascript
// src/hooks/useFeatureUsage.js

import { useState } from 'react';

export function useFeatureUsage() {
  const [usage, setUsage] = useState(null);
  
  const getHeaders = () => ({
    'Content-Type': 'application/json',
    'X-User-ID': localStorage.getItem('user_id') || sessionStorage.getItem('user_id'),
    // OR for JWT:
    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
  });

  const checkAccess = async (featureName) => {
    try {
      const response = await fetch('https://api.yourdomain.com/api/usage/check/', {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ feature: featureName })
      });

      const data = await response.json();
      
      if (data.success) {
        setUsage(data.status);
        return true;
      } else {
        // Feature blocked
        console.warn(`Feature blocked: ${data.error}`);
        showUpgradePrompt(data.error);
        return false;
      }
    } catch (error) {
      console.error('Feature check failed:', error);
      return true; // Fail open - allow feature on network error
    }
  };

  const recordUsage = async (usageData) => {
    try {
      const response = await fetch('https://api.yourdomain.com/api/usage/record/', {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(usageData)
      });

      const data = await response.json();
      
      if (data.success) {
        setUsage(data.usage);
        return data;
      }
    } catch (error) {
      console.error('Usage recording failed:', error);
      // Don't throw - feature already executed
    }
  };

  const getDashboard = async () => {
    try {
      const response = await fetch('https://api.yourdomain.com/api/usage/dashboard/', {
        method: 'GET',
        headers: getHeaders()
      });

      return await response.json();
    } catch (error) {
      console.error('Dashboard fetch failed:', error);
      return null;
    }
  };

  return {
    checkAccess,
    recordUsage,
    getDashboard,
    currentUsage: usage
  };
}
```

#### 3. Usage Dashboard Component
```javascript
// src/components/UsageDashboard.jsx

import { useEffect, useState } from 'react';
import { useFeatureUsage } from '../hooks/useFeatureUsage';

export function UsageDashboard() {
  const { getDashboard } = useFeatureUsage();
  const [dashboard, setDashboard] = useState(null);

  useEffect(() => {
    const loadDashboard = async () => {
      const data = await getDashboard();
      if (data?.success) {
        setDashboard(data.dashboard);
      }
    };
    loadDashboard();
  }, []);

  if (!dashboard) return <div>Loading...</div>;

  return (
    <div className="usage-dashboard">
      <h2>Your Plan: {dashboard.plan}</h2>
      
      <div className="features-grid">
        {Object.entries(dashboard.features).map(([key, feature]) => (
          <div key={key} className="feature-card">
            <h3>{feature.display_name}</h3>
            
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${feature.percentage_used}%` }}
              />
            </div>
            
            <p>
              {feature.used}/{feature.limit || '∞'} used
              {feature.remaining !== null && ` (${feature.remaining} remaining)`}
            </p>
            
            {feature.remaining === 0 && (
              <button className="upgrade-btn">Upgrade Now</button>
            )}
          </div>
        ))}
      </div>
      
      <div className="billing-info">
        <h3>Billing</h3>
        <p>Status: {dashboard.billing.subscription_status}</p>
        <p>Plan: {dashboard.plan}</p>
        {dashboard.billing.next_billing_date && (
          <p>Next Billing: {new Date(dashboard.billing.next_billing_date).toLocaleDateString()}</p>
        )}
      </div>
    </div>
  );
}
```

#### 4. Upgrade Dialog Component
```javascript
// src/components/UpgradeDialog.jsx

export function UpgradeDialog({ feature, reason, onClose }) {
  const handleUpgrade = async () => {
    // Redirect to subscription/payment page
    window.location.href = '/subscribe';
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <h2>Upgrade Required</h2>
        
        <p className="reason">{reason}</p>
        
        <div className="features-comparison">
          <div className="plan free">
            <h3>Free</h3>
            <ul>
              <li>3 uses per feature</li>
              <li>Limited to quizzes</li>
              <li>No pair quizzes</li>
            </ul>
            <p className="price">Free Forever</p>
          </div>
          
          <div className="plan basic">
            <h3>Basic</h3>
            <ul>
              <li>20 quizzes/month</li>
              <li>50 flashcards/month</li>
              <li>15 questions/month</li>
            </ul>
            <p className="price">₹1 first month, then ₹99/month</p>
          </div>
          
          <div className="plan premium">
            <h3>Premium</h3>
            <ul>
              <li>Unlimited everything</li>
              <li>Priority support</li>
              <li>Advanced analytics</li>
            </ul>
            <p className="price">₹199 first month, then ₹499/month</p>
          </div>
        </div>
        
        <div className="actions">
          <button className="secondary" onClick={onClose}>Cancel</button>
          <button className="primary" onClick={handleUpgrade}>Choose Plan</button>
        </div>
      </div>
    </div>
  );
}
```

---

## Integration Points

### Where to Add Feature Checks

#### 1. Quiz Module
```javascript
// quiz_solver.jsx
const handleGenerateQuiz = async () => {
  if (!await checkAccess('quiz')) return;
  
  const quiz = await generateQuiz();
  await recordUsage({ feature: 'quiz', input_size: quiz.length, usage_type: 'text' });
};
```

#### 2. Flashcard Module
```javascript
// flashcard_generator.jsx
const handleGenerateFlashcards = async () => {
  if (!await checkAccess('flashcards')) return;
  
  const flashcards = await generateFlashcards();
  await recordUsage({ feature: 'flashcards', input_size: text.length, usage_type: 'text' });
};
```

#### 3. Ask Question Module
```javascript
// ask_question.jsx
const handleAskQuestion = async () => {
  if (!await checkAccess('ask_question')) return;
  
  const answer = await getAnswer(question);
  await recordUsage({ feature: 'ask_question', input_size: question.length, usage_type: 'text' });
};
```

#### 4. YouTube Summarizer
```javascript
// youtube_summarizer.jsx
const handleSummarize = async () => {
  if (!await checkAccess('youtube_summarizer')) return;
  
  const summary = await summarizeVideo(url);
  await recordUsage({ feature: 'youtube_summarizer', input_size: summary.length, usage_type: 'text' });
};
```

---

## Error Handling & UX

### Show Remaining Attempts
```javascript
const handleFeatureUse = async (feature) => {
  const status = await checkAccess(feature);
  
  if (status.allowed) {
    // Show how many uses left
    if (status.remaining <= 1) {
      showWarning(`Only ${status.remaining} use remaining!`);
    }
    
    // Execute feature
    await executeFeature();
    
    // Record and show updated count
    const result = await recordUsage({ feature });
    updateRemainingDisplay(result.usage.remaining);
  }
};
```

### Graceful Degradation
```javascript
// If usage check fails due to network error
const canAccess = await checkAccess('quiz').catch(() => true);
// Allow feature if check fails (fail open)
```

### Local Caching
```javascript
const [cachedUsage, setCachedUsage] = useState(() => {
  const cached = localStorage.getItem('usage_cache');
  return cached ? JSON.parse(cached) : null;
});

const fetchUsage = async () => {
  const usage = await getDashboard();
  localStorage.setItem('usage_cache', JSON.stringify(usage));
  setCachedUsage(usage);
};
```

---

## Testing Feature Restrictions Locally

```bash
# Test with curl
TEST_USER="testuser_$(date +%s)"

# 1. Check access (should allow)
curl -X POST http://localhost:3000/api/usage/check/ \
  -H "X-User-ID: $TEST_USER" \
  -H "Content-Type: application/json" \
  -d '{"feature":"quiz"}'

# 2. Record 3 uses
for i in 1 2 3; do
  curl -X POST http://localhost:3000/api/usage/record/ \
    -H "X-User-ID: $TEST_USER" \
    -H "Content-Type: application/json" \
    -d '{"feature":"quiz","input_size":100,"usage_type":"text"}'
done

# 3. Check access again (should block)
curl -X POST http://localhost:3000/api/usage/check/ \
  -H "X-User-ID: $TEST_USER" \
  -H "Content-Type: application/json" \
  -d '{"feature":"quiz"}'

# 4. Check dashboard
curl -X GET http://localhost:3000/api/usage/dashboard/ \
  -H "X-User-ID: $TEST_USER"
```

---

## Deployment Checklist

- [ ] Update all feature endpoints with usage checks
- [ ] Add upgrade prompt UI component
- [ ] Implement usage dashboard display
- [ ] Test with different user types (free, trial, paid)
- [ ] Verify subscription unlock works
- [ ] Monitor API logs for errors
- [ ] Document feature names in team wiki
- [ ] Train support team on usage limits
- [ ] Plan marketing around free tier benefits
- [ ] Set up analytics dashboard for admins

---

## Support & Troubleshooting

### User Can't Access Feature
1. Check `/api/usage/check/` returns `allowed: true`
2. Verify user has remaining attempts
3. Check `last_payment_date` for subscription status
4. Look at `FeatureUsageLog` table for recent uses

### Usage Count Seems Wrong
1. Check database: `SELECT * FROM question_solver_featureusagelog WHERE subscription_id='...'`
2. Verify `POST /usage/record/` was called
3. Check for duplicate logs
4. Look for failed API calls in logs

### Can't Upgrade Subscription
1. Verify Razorpay API keys are correct
2. Check subscription creation endpoint
3. Verify payment webhook is configured
4. Check `UserSubscription.subscription_status` field

---

## Performance Optimization

### Caching Strategy
```javascript
// Cache usage status for 5 minutes
const CACHE_DURATION = 5 * 60 * 1000;
let lastCheck = {};

const checkAccessOptimized = async (feature) => {
  const now = Date.now();
  
  if (lastCheck[feature] && now - lastCheck[feature].time < CACHE_DURATION) {
    return lastCheck[feature].result;
  }
  
  const result = await checkAccess(feature);
  lastCheck[feature] = { result, time: now };
  return result;
};
```

### Batching Requests
```javascript
// Check multiple features in one call
const checkMultipleFeatures = async (features) => {
  const results = await Promise.all(
    features.map(f => checkAccess(f))
  );
  return results;
};
```

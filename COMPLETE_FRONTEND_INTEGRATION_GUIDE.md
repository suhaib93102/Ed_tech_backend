# 🎯 COMPLETE FRONTEND INTEGRATION GUIDE

## Server: http://localhost:9000

---

## 📋 TABLE OF CONTENTS

1. [SUBSCRIPTION SYSTEM ENDPOINTS](#subscription-system-endpoints)
2. [IMAGE PROCESSING ENDPOINTS](#image-processing-endpoints)
3. [FRONTEND INTEGRATION PATTERNS](#frontend-integration-patterns)
4. [ERROR HANDLING](#error-handling)
5. [TESTING CHECKLIST](#testing-checklist)

---

## 💳 SUBSCRIPTION SYSTEM ENDPOINTS

### 1. Get Subscription Plans
```bash
curl -X GET "http://localhost:9000/api/subscriptions/plans/"
```

**Response:**
```json
{
    "success": true,
    "plans": [
        {
            "id": "free",
            "name": "Free Plan",
            "price": 0,
            "currency": "INR",
            "features": ["Basic access", "Limited quizzes"],
            "max_quizzes": 5,
            "max_flashcards": 10
        },
        {
            "id": "premium",
            "name": "Premium Plan",
            "price": 299,
            "currency": "INR",
            "features": ["Unlimited access", "All features", "Priority support"],
            "max_quizzes": -1,
            "max_flashcards": -1
        }
    ]
}
```

### 2. Get User Subscription Status
```bash
curl -X GET "http://localhost:9000/api/subscriptions/status/?user_id=user_123"
```

**Response:**
```json
{
    "success": true,
    "subscription": {
        "user_id": "user_123",
        "plan_id": "free",
        "status": "active",
        "start_date": "2024-01-01T00:00:00Z",
        "end_date": null,
        "is_active": true,
        "remaining_quizzes": 5,
        "remaining_flashcards": 10
    }
}
```

### 3. Subscribe to Plan
```bash
curl -X POST "http://localhost:9000/api/subscriptions/subscribe/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "plan_id": "premium"
  }'
```

### 4. Initiate Payment
```bash
curl -X POST "http://localhost:9000/api/subscriptions/initiate-payment/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "plan_id": "premium",
    "amount": 299
  }'
```

### 5. Confirm Payment
```bash
curl -X POST "http://localhost:9000/api/subscriptions/confirm-payment/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "payment_id": "pay_mock_payment_id",
    "order_id": "order_mock_order_id",
    "signature": "mock_signature"
  }'
```

### 6. Cancel Subscription
```bash
curl -X POST "http://localhost:9000/api/subscriptions/cancel/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123"
  }'
```

---

## 📸 IMAGE PROCESSING ENDPOINTS

### 1. Generate Predicted Questions from Image
```bash
curl -X POST "http://localhost:9000/api/predicted-questions/generate/" \
  -F "document=@image.png" \
  -F "user_id=user_123" \
  -F "exam_type=physics" \
  -F "num_questions=5" \
  -F "language=english"
```

### 2. Generate Flashcards from Image
```bash
curl -X POST "http://localhost:9000/api/flashcards/generate/" \
  -F "document=@image.png" \
  -F "user_id=user_123" \
  -F "num_cards=3" \
  -F "language=english"
```

### 3. Generate Quiz from Image
```bash
curl -X POST "http://localhost:9000/api/quiz/generate/" \
  -F "document=@image.png" \
  -F "user_id=user_123" \
  -F "num_questions=3" \
  -F "difficulty=easy" \
  -F "subject=physics"
```

---

## 🔧 FRONTEND INTEGRATION PATTERNS

### 1. **Subscription Management Class**
```javascript
class SubscriptionManager {
    constructor(baseUrl = 'http://localhost:9000') {
        this.baseUrl = baseUrl;
    }

    async getPlans() {
        const response = await fetch(`${this.baseUrl}/api/subscriptions/plans/`);
        return await response.json();
    }

    async getUserStatus(userId) {
        const response = await fetch(`${this.baseUrl}/api/subscriptions/status/?user_id=${userId}`);
        return await response.json();
    }

    async subscribe(userId, planId) {
        const response = await fetch(`${this.baseUrl}/api/subscriptions/subscribe/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, plan_id: planId })
        });
        return await response.json();
    }

    async initiatePayment(userId, planId, amount) {
        const response = await fetch(`${this.baseUrl}/api/subscriptions/initiate-payment/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, plan_id: planId, amount })
        });
        return await response.json();
    }

    async confirmPayment(userId, paymentId, orderId, signature) {
        const response = await fetch(`${this.baseUrl}/api/subscriptions/confirm-payment/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userId,
                payment_id: paymentId,
                order_id: orderId,
                signature
            })
        });
        return await response.json();
    }

    async cancelSubscription(userId) {
        const response = await fetch(`${this.baseUrl}/api/subscriptions/cancel/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId })
        });
        return await response.json();
    }
}
```

### 2. **Image Processing Class**
```javascript
class ImageProcessor {
    constructor(baseUrl = 'http://localhost:9000') {
        this.baseUrl = baseUrl;
    }

    async generatePredictedQuestions(file, userId, options = {}) {
        const formData = new FormData();
        formData.append('document', file);
        formData.append('user_id', userId);

        if (options.examType) formData.append('exam_type', options.examType);
        if (options.numQuestions) formData.append('num_questions', options.numQuestions);
        if (options.language) formData.append('language', options.language);

        const response = await fetch(`${this.baseUrl}/api/predicted-questions/generate/`, {
            method: 'POST',
            body: formData
        });
        return await response.json();
    }

    async generateFlashcards(file, userId, options = {}) {
        const formData = new FormData();
        formData.append('document', file);
        formData.append('user_id', userId);

        if (options.numCards) formData.append('num_cards', options.numCards);
        if (options.language) formData.append('language', options.language);

        const response = await fetch(`${this.baseUrl}/api/flashcards/generate/`, {
            method: 'POST',
            body: formData
        });
        return await response.json();
    }

    async generateQuiz(file, userId, options = {}) {
        const formData = new FormData();
        formData.append('document', file);
        formData.append('user_id', userId);

        if (options.numQuestions) formData.append('num_questions', options.numQuestions);
        if (options.difficulty) formData.append('difficulty', options.difficulty);
        if (options.subject) formData.append('subject', options.subject);

        const response = await fetch(`${this.baseUrl}/api/quiz/generate/`, {
            method: 'POST',
            body: formData
        });
        return await response.json();
    }
}
```

### 3. **Usage Example**
```javascript
// Initialize managers
const subscriptionManager = new SubscriptionManager();
const imageProcessor = new ImageProcessor();

// Check user subscription
const status = await subscriptionManager.getUserStatus('user_123');
if (status.success && status.subscription.is_active) {
    // User has active subscription, allow unlimited access

    // Process image for questions
    const fileInput = document.getElementById('imageInput');
    const file = fileInput.files[0];

    if (file) {
        const questions = await imageProcessor.generatePredictedQuestions(file, 'user_123', {
            examType: 'physics',
            numQuestions: 5,
            language: 'english'
        });

        if (questions.success) {
            displayQuestions(questions.questions);
        }
    }
} else {
    // Show subscription required message
    showSubscriptionPrompt();
}
```

---

## 🚨 ERROR HANDLING

### 1. **Network Errors**
```javascript
async function safeApiCall(apiFunction) {
    try {
        const response = await apiFunction();
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        // Show user-friendly error message
        showErrorToast('Failed to connect to server. Please try again.');
        return null;
    }
}
```

### 2. **API Response Errors**
```javascript
function handleApiResponse(response) {
    if (response.success) {
        return response;
    } else {
        // Handle specific error types
        switch (response.error) {
            case 'INVALID_USER':
                showErrorToast('Invalid user. Please log in again.');
                break;
            case 'PAYMENT_FAILED':
                showErrorToast('Payment failed. Please try again.');
                break;
            case 'SUBSCRIPTION_EXPIRED':
                showSubscriptionPrompt();
                break;
            default:
                showErrorToast(response.message || 'An error occurred.');
        }
        return null;
    }
}
```

### 3. **File Upload Validation**
```javascript
function validateImageFile(file) {
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/tiff', 'image/webp'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!allowedTypes.includes(file.type)) {
        throw new Error('Please select a valid image file (JPEG, PNG, GIF, BMP, TIFF, WebP)');
    }

    if (file.size > maxSize) {
        throw new Error('File size must be less than 10MB');
    }

    return true;
}
```

---

## ✅ TESTING CHECKLIST

### Subscription Endpoints:
- [ ] Get plans returns correct pricing and features
- [ ] User status shows correct subscription state
- [ ] Subscribe endpoint updates user plan
- [ ] Payment initiation creates Razorpay order
- [ ] Payment confirmation activates premium features
- [ ] Cancel subscription reverts to free plan

### Image Processing Endpoints:
- [ ] Predicted questions generates comprehensive questions
- [ ] Flashcards creates Q&A pairs from images
- [ ] Quiz generates multiple choice questions
- [ ] OCR processes different image formats
- [ ] Error handling for invalid files
- [ ] Performance within acceptable limits

### Frontend Integration:
- [ ] File upload validation works
- [ ] Loading states shown during processing
- [ ] Error messages displayed appropriately
- [ ] Subscription checks prevent unauthorized access
- [ ] API responses handled correctly
- [ ] Network errors handled gracefully

---

## 🚀 PRODUCTION DEPLOYMENT NOTES

1. **Environment Variables:**
   - Set `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET`
   - Configure database connection strings
   - Set CORS origins for frontend domain

2. **Security:**
   - Implement proper authentication
   - Add rate limiting for API endpoints
   - Validate file uploads server-side
   - Use HTTPS in production

3. **Performance:**
   - Consider caching subscription status
   - Implement file size limits
   - Add request timeouts
   - Monitor OCR processing times

4. **Monitoring:**
   - Log API usage and errors
   - Monitor subscription conversion rates
   - Track image processing success rates
   - Set up alerts for system issues

---

## 📞 SUPPORT

All endpoints tested and working on `http://localhost:9000`

**Last Updated:** January 6, 2025
**Server Status:** ✅ Running
**All Endpoints:** ✅ Tested and Functional
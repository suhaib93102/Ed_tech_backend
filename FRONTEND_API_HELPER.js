/**
 * API Helper - Frontend Integration Guide
 * 
 * This shows the correct way to call the EdTech backend API
 * from your frontend application (localhost:8081)
 * 
 * It handles CORS properly and includes all necessary headers
 */

// ═════════════════════════════════════════════════════════════════════════════
// CONFIGURATION
// ═════════════════════════════════════════════════════════════════════════════

// Use this URL for backend API calls
const API_BASE_URL = 'https://ed-tech-backend-tzn8.onrender.com/api';

// For local development (if running backend locally):
// const API_BASE_URL = 'http://localhost:8000/api';

// Get user ID from wherever you store it (localStorage, context, etc.)
function getUserId() {
  return localStorage.getItem('user_id') || 'user_' + Date.now();
}

// ═════════════════════════════════════════════════════════════════════════════
// BASIC FETCH HELPER (with CORS & Headers)
// ═════════════════════════════════════════════════════════════════════════════

/**
 * Make an API request with proper CORS headers
 * @param {string} endpoint - API endpoint (e.g., '/solve/')
 * @param {object} data - Request body data
 * @param {string} method - HTTP method (default: 'POST')
 * @returns {Promise} Response data
 */
async function apiCall(endpoint, data = {}, method = 'POST') {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const options = {
    method: method,
    headers: {
      'Content-Type': 'application/json',
      'X-User-ID': getUserId(),  // Important: Send user ID
    },
    mode: 'cors',  // Important: Enable CORS
    credentials: 'include',  // Important: Include cookies if needed
  };

  // Only add body for non-GET requests
  if (method !== 'GET' && Object.keys(data).length > 0) {
    options.body = JSON.stringify(data);
  }

  try {
    console.log(`📤 API Request: ${method} ${endpoint}`, data);
    
    const response = await fetch(url, options);
    
    // Check if response is OK
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    
    const responseData = await response.json();
    console.log(`✅ API Response: ${endpoint}`, responseData);
    
    return responseData;
  } catch (error) {
    console.error(`❌ API Error: ${endpoint}`, error);
    throw error;
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// EXAMPLE API CALLS
// ═════════════════════════════════════════════════════════════════════════════

/**
 * Solve a question by text
 * 
 * IMPORTANT: Test this with the actual parameter name!
 * The endpoint expects either 'image' or 'text'
 * Check what parameter name the backend actually uses
 */
async function solveQuestionByText(question) {
  try {
    const response = await apiCall('/solve/', {
      text: question,  // ← Try this first
      // OR try 'question_text' if 'text' doesn't work:
      // question_text: question,
    });
    return response;
  } catch (error) {
    console.error('Failed to solve question:', error);
    throw error;
  }
}

/**
 * Solve a question by image
 */
async function solveQuestionByImage(imageFile) {
  try {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    const url = `${API_BASE_URL}/solve/`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'X-User-ID': getUserId(),
      },
      mode: 'cors',
      credentials: 'include',
      body: formData,  // FormData, not JSON
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to solve question:', error);
    throw error;
  }
}

/**
 * Check if a feature is available for the user
 */
async function checkFeatureAccess(feature) {
  try {
    const response = await apiCall('/usage/check/', {
      feature: feature,
    });
    return response;
  } catch (error) {
    console.error('Failed to check feature access:', error);
    throw error;
  }
}

/**
 * Record feature usage
 */
async function recordFeatureUsage(feature) {
  try {
    const response = await apiCall('/usage/record/', {
      feature: feature,
    });
    return response;
  } catch (error) {
    console.error('Failed to record usage:', error);
    throw error;
  }
}

/**
 * Create subscription order
 */
async function createSubscriptionOrder(plan) {
  try {
    const response = await apiCall('/subscriptions/create/', {
      user_id: getUserId(),
      plan: plan,  // 'basic' or 'premium'
    });
    return response;
  } catch (error) {
    console.error('Failed to create subscription:', error);
    throw error;
  }
}

/**
 * Get subscription status
 */
async function getSubscriptionStatus() {
  try {
    const response = await apiCall('/subscriptions/status/', {}, 'GET');
    return response;
  } catch (error) {
    console.error('Failed to get subscription status:', error);
    throw error;
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// USING WITH AXIOS (Alternative to Fetch)
// ═════════════════════════════════════════════════════════════════════════════

// If you're using Axios, configure it like this:

// import axios from 'axios';

// const apiClient = axios.create({
//   baseURL: API_BASE_URL,
//   headers: {
//     'Content-Type': 'application/json',
//     'X-User-ID': getUserId(),
//   },
// });

// // Intercept responses to handle errors
// apiClient.interceptors.response.use(
//   response => {
//     console.log('✅ API Response:', response.data);
//     return response.data;
//   },
//   error => {
//     console.error('❌ API Error:', error.response?.data || error.message);
//     throw error;
//   }
// );

// // Usage with Axios:
// async function solveQuestionAxios(question) {
//   return apiClient.post('/solve/', { text: question });
// }

// ═════════════════════════════════════════════════════════════════════════════
// HANDLING CORS ERRORS IN YOUR COMPONENT
// ═════════════════════════════════════════════════════════════════════════════

/**
 * Example React component showing proper error handling
 */
class SolverComponent {
  async handleSolveQuestion(question) {
    try {
      // Check if user can use feature
      const accessCheck = await checkFeatureAccess('quiz');
      
      if (!accessCheck.status.allowed) {
        // Show upgrade dialog
        this.showUpgradeDialog(accessCheck.status);
        return;
      }
      
      // Show loading
      this.setState({ loading: true });
      
      // Call API
      const result = await solveQuestionByText(question);
      
      // Record usage
      await recordFeatureUsage('quiz');
      
      // Show result
      this.setState({ result });
    } catch (error) {
      // Handle different error types
      if (error.message.includes('CORS')) {
        console.error('CORS Error - Check backend CORS configuration');
        alert('Connection error. Please try again.');
      } else if (error.message.includes('502')) {
        console.error('Backend server error');
        alert('Server error. Please try again later.');
      } else {
        console.error('Unknown error:', error);
        alert('Error: ' + error.message);
      }
    } finally {
      this.setState({ loading: false });
    }
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// TESTING THE API (in browser console)
// ═════════════════════════════════════════════════════════════════════════════

// Paste this in your browser console to test:

// Test 1: Check API is responding
// fetch('https://ed-tech-backend-tzn8.onrender.com/api/health/')
//   .then(r => r.json())
//   .then(d => console.log('✓ API responding:', d))
//   .catch(e => console.error('✗ API not responding:', e));

// Test 2: Check CORS headers
// fetch('https://ed-tech-backend-tzn8.onrender.com/api/solve/', {
//   method: 'POST',
//   mode: 'cors',
//   headers: { 'Content-Type': 'application/json' },
//   body: JSON.stringify({ text: 'test' })
// })
//   .then(r => {
//     console.log('Response headers:');
//     console.log('Access-Control-Allow-Origin:', r.headers.get('Access-Control-Allow-Origin'));
//     return r.json();
//   })
//   .then(d => console.log('Response:', d))
//   .catch(e => console.error('Error:', e));

// Test 3: Try solving a question
// solveQuestionByText('What is 2+2?')
//   .then(result => console.log('✓ Question solved:', result))
//   .catch(error => console.error('✗ Failed to solve:', error));

// ═════════════════════════════════════════════════════════════════════════════
// COMMON ISSUES & SOLUTIONS
// ═════════════════════════════════════════════════════════════════════════════

/*
ISSUE 1: "CORS policy blocked the request"
SOLUTION:
  • Make sure to add 'mode': 'cors' to fetch options
  • Check that 'X-User-ID' header is being sent
  • Clear browser cache and hard refresh (Ctrl+F5)
  • Check Django settings.py has CORS configured

ISSUE 2: "Failed to load resource: net::ERR_FAILED"
SOLUTION:
  • Backend server might be down
  • Check: https://ed-tech-backend-tzn8.onrender.com/api/health/
  • If down, restart the server
  • Check internet connection

ISSUE 3: "No 'Access-Control-Allow-Origin' header"
SOLUTION:
  • Backend didn't send CORS headers
  • Check CORS_ALLOW_ALL_ORIGINS = True in settings.py
  • Restart Django server: Ctrl+C, then run manage.py runserver
  • Look at the CORS_ERROR_FIX_GUIDE.md for detailed help

ISSUE 4: "Node cannot be found in the current page"
SOLUTION:
  • This is a warning, usually harmless
  • Check browser console for actual error messages
  • This might be from a browser extension

ISSUE 5: "Expected "application/json" but got..."
SOLUTION:
  • Backend returned HTML error page instead of JSON
  • Check URL is correct
  • Check all required parameters are being sent
  • Look at the HTML response to see the error message
*/

// ═════════════════════════════════════════════════════════════════════════════
// EXPORT FOR USE IN OTHER MODULES
// ═════════════════════════════════════════════════════════════════════════════

export {
  apiCall,
  solveQuestionByText,
  solveQuestionByImage,
  checkFeatureAccess,
  recordFeatureUsage,
  createSubscriptionOrder,
  getSubscriptionStatus,
};

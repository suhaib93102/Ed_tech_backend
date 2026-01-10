╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║             QUICK DEBUG GUIDE - CORS & API ERRORS                           ║
║                                                                              ║
║            Step-by-step troubleshooting for your specific errors            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

YOUR ERRORS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣  "Access to XMLHttpRequest...blocked by CORS policy"
2️⃣  "solveQuestionByText error"
3️⃣  "Failed to load resource: net::ERR_FAILED"
4️⃣  "Node cannot be found in the current page"

═══════════════════════════════════════════════════════════════════════════════════

WHAT'S HAPPENING:

Your frontend (http://localhost:8081) is trying to call the backend API
(https://ed-tech-backend-tzn8.onrender.com/api/solve/) but the browser is
blocking the request for security reasons (CORS).

═══════════════════════════════════════════════════════════════════════════════════

IMMEDIATE FIXES (Do These First)

STEP 1: Clear Browser Cache
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Windows/Linux:
  1. Press Ctrl+Shift+Delete
  2. Select: "All time" in Time range dropdown
  3. Check: Cookies, Cache
  4. Click: "Clear data"

Mac:
  1. Press Cmd+Shift+Delete
  2. Follow same steps as above

Chrome:
  1. ⋮ (menu) → Settings → Privacy and security → Clear browsing data
  2. Time: All time
  3. Check: Cookies and cached images and files
  4. Clear data

STEP 2: Hard Refresh
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Windows/Linux:
  Ctrl+Shift+R or Ctrl+F5

Mac:
  Cmd+Shift+R or Cmd+Shift+Delete

This bypasses cache and forces reload.

STEP 3: Check Browser Console
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Press F12 to open DevTools
Go to Console tab
Look for the exact error message
Take a screenshot

═══════════════════════════════════════════════════════════════════════════════════

IF STILL NOT WORKING - BACKEND FIX

STEP 4: Update Django Settings
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

File: edtech_project/settings.py

Find line around 65: "CORS_ALLOW_ALL_ORIGINS = True"

Replace the entire CORS section with:

  ┌──────────────────────────────────────────────────────────────┐
  │ # ═════════════════════════════════════════════════════════ │
  │ # CORS Configuration                                        │
  │ # ═════════════════════════════════════════════════════════ │
  │ if DEBUG or 'RENDER' in os.environ:                         │
  │     CORS_ALLOW_ALL_ORIGINS = True                           │
  │ else:                                                        │
  │     CORS_ALLOW_ALL_ORIGINS = True                           │
  │                                                             │
  │ CORS_ALLOW_CREDENTIALS = True                               │
  │                                                             │
  │ CORS_ALLOW_HEADERS = [                                      │
  │     'accept',                                               │
  │     'accept-encoding',                                      │
  │     'authorization',                                        │
  │     'content-type',                                         │
  │     'origin',                                               │
  │     'user-agent',                                           │
  │     'x-csrftoken',                                          │
  │     'x-requested-with',                                     │
  │     'x-user-id',                                            │
  │ ]                                                           │
  │                                                             │
  │ CORS_ALLOW_METHODS = [                                      │
  │     'DELETE',                                               │
  │     'GET',                                                  │
  │     'HEAD',                                                 │
  │     'OPTIONS',                                              │
  │     'PATCH',                                                │
  │     'POST',                                                 │
  │     'PUT',                                                  │
  │ ]                                                           │
  │                                                             │
  │ CORS_PREFLIGHT_MAX_AGE = 86400                              │
  │                                                             │
  │ CORS_EXPOSE_HEADERS = [                                     │
  │     'Content-Type',                                         │
  │     'X-CSRFToken',                                          │
  │ ]                                                           │
  └──────────────────────────────────────────────────────────────┘

STEP 5: Restart Django
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

In terminal where Django is running:
  Ctrl+C

Wait 2 seconds, then restart:
  python manage.py runserver

You should see:
  ✓ Starting development server at http://127.0.0.1:8000/
  ✓ Quit the server with CONTROL-C

STEP 6: Test Backend is Running
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

In another terminal, run:

  curl -X GET http://localhost:8000/api/health/ -v

You should see:
  > GET /api/health/ HTTP/1.1
  > Host: localhost:8000
  <
  < HTTP/1.1 200 OK
  < Content-Type: application/json

If you see 404 or connection refused:
  → Backend isn't running or /api/health/ doesn't exist

═══════════════════════════════════════════════════════════════════════════════════

IF STILL NOT WORKING - FRONTEND FIX

STEP 7: Update Your Frontend Code
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Find the code that calls the API. It probably looks like:

  ❌ WRONG:
    const response = await fetch('https://ed-tech-backend-tzn8.onrender.com/api/solve/', {
      method: 'POST',
      body: JSON.stringify({ question: "..." })
    });

  ✅ CORRECT:
    const response = await fetch('https://ed-tech-backend-tzn8.onrender.com/api/solve/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-ID': 'your-user-id',
      },
      body: JSON.stringify({ text: "..." }),  // NOT 'question'!
      mode: 'cors',  // Add this
      credentials: 'include',  // Add this
    });

KEY CHANGES:
  1. Add 'mode': 'cors'  ← Critical
  2. Add headers with 'Content-Type'  ← Important
  3. Add 'X-User-ID' header  ← Required by backend
  4. Use 'text' parameter, NOT 'question'  ← Check backend docs
  5. Add 'credentials': 'include'  ← For cookies

STEP 8: Check API Parameter Name
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The error "Please provide either an image or text query" means:
  ✗ You're not sending 'text' parameter
  ✓ You need to send { text: "..." }

NOT:
  ✗ { question: "..." }
  ✗ { query: "..." }
  ✗ { question_text: "..." }

CORRECT:
  ✓ { text: "What is 2+2?" }

═══════════════════════════════════════════════════════════════════════════════════

TESTING WITH CURL (To Verify Backend Works)

STEP 9: Test Endpoint with Curl
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Test 1: Is backend running?

  curl -X GET http://localhost:8000/api/health/ \
    -H "X-User-ID: test_user"

Expected:
  HTTP/1.1 200 OK
  {"status":"ok"}

If you see "Connection refused":
  → Backend not running, restart it

Test 2: Can we call /solve/ endpoint?

  curl -X POST http://localhost:8000/api/solve/ \
    -H "Content-Type: application/json" \
    -H "X-User-ID: test_user" \
    -d '{"text":"What is 2+2?"}'

Expected:
  HTTP/1.1 200 OK
  {"success":true, "result": "..."}

OR

  HTTP/1.1 400 Bad Request
  {"error":"..."}

If you see HTTP 500:
  → Backend error, check Django logs

Test 3: Does backend send CORS headers?

  curl -X OPTIONS http://localhost:8000/api/solve/ \
    -H "Origin: http://localhost:8081" \
    -v | grep -i "access-control"

You should see:
  access-control-allow-origin: *
  access-control-allow-methods: POST, OPTIONS, GET, ...
  access-control-allow-headers: ...

If you see nothing:
  → CORS not configured properly

═══════════════════════════════════════════════════════════════════════════════════

DEBUGGING IN BROWSER

STEP 10: Check Network Tab in DevTools
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Open DevTools: F12
2. Go to Network tab
3. Make API call from your app
4. Look for request to /api/solve/
5. Click on it to see details

WHAT TO CHECK:

Request Headers tab:
  ✓ Host: ed-tech-backend-tzn8.onrender.com
  ✓ Origin: http://localhost:8081
  ✓ Content-Type: application/json
  ✓ X-User-ID: [something]

Response Headers tab:
  ✓ Access-Control-Allow-Origin: *
  ✓ Content-Type: application/json
  ✗ (empty) = CORS not set up

Response tab:
  ✓ {"success":true, ...} = Working
  ✗ <html>Error...</html> = Backend error
  ✗ (empty) = Connection failed

═══════════════════════════════════════════════════════════════════════════════════

CHECKLIST - HAVE YOU DONE THESE?

☐ Cleared browser cache (Ctrl+Shift+Delete)
☐ Hard refreshed page (Ctrl+F5)
☐ Restarted Django server
☐ Updated Django settings.py with CORS config
☐ Updated frontend code to use 'mode': 'cors'
☐ Using correct parameter name: 'text' not 'question'
☐ Including 'X-User-ID' header
☐ Backend is returning JSON, not HTML
☐ No typos in API URL (localhost:8000 vs onrender.com)
☐ Frontend is running on localhost:8081 (not 8080, 3000, etc.)

═══════════════════════════════════════════════════════════════════════════════════

EXAMPLE: Complete Working Request

Frontend Code (React):

  async function solveQuestion(question) {
    try {
      const response = await fetch(
        'https://ed-tech-backend-tzn8.onrender.com/api/solve/',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-User-ID': 'user_123',
          },
          body: JSON.stringify({
            text: question,  // ← Correct parameter
          }),
          mode: 'cors',  // ← Enable CORS
          credentials: 'include',  // ← Include cookies
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('✓ Success:', data);
      return data;
    } catch (error) {
      console.error('✗ Error:', error);
    }
  }

Django Backend (already configured):
  ✓ CORS_ALLOW_ALL_ORIGINS = True
  ✓ corsheaders in INSTALLED_APPS
  ✓ CorsMiddleware in MIDDLEWARE
  ✓ Endpoint accepts 'text' parameter

═══════════════════════════════════════════════════════════════════════════════════

STILL STUCK?

Copy this test code into your browser console:

  // Test 1: Is backend responding?
  fetch('https://ed-tech-backend-tzn8.onrender.com/api/health/')
    .then(r => {
      console.log('Status:', r.status);
      console.log('CORS Header:', r.headers.get('Access-Control-Allow-Origin'));
      return r.json();
    })
    .then(d => console.log('✓ Backend alive:', d))
    .catch(e => console.error('✗ Backend down:', e.message));

  // Test 2: Can we solve a question?
  fetch('https://ed-tech-backend-tzn8.onrender.com/api/solve/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-User-ID': 'test_user',
    },
    body: JSON.stringify({ text: 'What is 2+2?' }),
    mode: 'cors',
  })
    .then(r => {
      console.log('Status:', r.status);
      console.log('CORS Header:', r.headers.get('Access-Control-Allow-Origin'));
      return r.json();
    })
    .then(d => console.log('✓ Question solved:', d))
    .catch(e => console.error('✗ Error:', e.message));

Run these and look at the Console output.
If Test 1 succeeds but Test 2 fails:
  → Check the error message
  → Probably wrong parameter name or missing header

═══════════════════════════════════════════════════════════════════════════════════

FINAL SUMMARY

The error "CORS policy blocked the request" means:

  1. ✗ Frontend and backend are on different domains/ports
  2. ✗ Backend isn't sending CORS headers
  3. ✗ Frontend isn't sending correct headers

The fix:

  1. ✓ Add CORS to Django settings (ALREADY DONE)
  2. ✓ Restart Django server
  3. ✓ Update frontend to include 'mode': 'cors' and headers
  4. ✓ Clear browser cache and hard refresh
  5. ✓ Use correct API parameter name ('text')

═══════════════════════════════════════════════════════════════════════════════════

📖 Full Guide: CORS_ERROR_FIX_GUIDE.md
📝 API Helper: FRONTEND_API_HELPER.js
🔗 Backend Settings: edtech_project/settings.py

═══════════════════════════════════════════════════════════════════════════════════

╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                        CORS ERROR - COMPLETE GUIDE                          ║
║                                                                              ║
║            Understanding & Fixing: "CORS policy blocked the request"        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Your Error:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Access to XMLHttpRequest at 'https://ed-tech-backend-tzn8.onrender.com/api/solve/'
from origin 'http://localhost:8081' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.

═══════════════════════════════════════════════════════════════════════════════════

WHAT DOES THIS MEAN?

Your frontend (running on localhost:8081) is trying to make an API call to your
backend (running on ed-tech-backend-tzn8.onrender.com), but the browser is
blocking it because:

1. The origins are DIFFERENT:
   Frontend:  http://localhost:8081
   Backend:   https://ed-tech-backend-tzn8.onrender.com

2. The response is MISSING the header:
   Access-Control-Allow-Origin: http://localhost:8081

This is a SECURITY FEATURE (CORS = Cross-Origin Resource Sharing)

═══════════════════════════════════════════════════════════════════════════════════

WHY THIS SECURITY EXISTS

Imagine a malicious website did this:

1. You visit malicioussite.com in your browser
2. Their JavaScript makes a request to yourbank.com
3. You're logged into your bank, so the request has your session cookie
4. The malicious site gets back your bank balance!

CORS prevents this by:
  • Browsers block requests to different origins
  • The backend must explicitly allow requests from specific origins
  • This is controlled via HTTP headers

═══════════════════════════════════════════════════════════════════════════════════

YOUR CURRENT SETUP

Backend Configuration (settings.py):
  ✓ CORS is installed: 'corsheaders' in INSTALLED_APPS
  ✓ CORS middleware is enabled
  ✓ CORS_ALLOW_ALL_ORIGINS = True  ← Allows all origins

This SHOULD work, but there might be an issue.

═══════════════════════════════════════════════════════════════════════════════════

QUICK FIXES (TRY THESE FIRST)

SOLUTION 1: Clear Browser Cache & Hard Refresh
  1. Press Ctrl+Shift+Delete (or Cmd+Shift+Delete on Mac)
  2. Clear: Cookies, Cache, Site data
  3. Go back to localhost:8081
  4. Hard refresh: Ctrl+F5 (or Cmd+Shift+R)
  5. Try API call again

Result: ✅ Usually fixes the issue

SOLUTION 2: Check Network Headers in DevTools
  1. Open DevTools: F12
  2. Go to Network tab
  3. Make API call again
  4. Click on the request to /api/solve/
  5. Go to Response Headers
  6. Look for: Access-Control-Allow-Origin

What you SHOULD see:
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
  Access-Control-Allow-Headers: ...

What you might ACTUALLY see:
  (empty - meaning CORS headers are missing)

═══════════════════════════════════════════════════════════════════════════════════

IF THE QUICK FIXES DON'T WORK

The issue might be that your backend isn't sending CORS headers.

FIX: Update Django Settings

File: edtech_project/settings.py

FIND THIS SECTION:
  CORS_ALLOW_ALL_ORIGINS = True
  CORS_ALLOW_CREDENTIALS = True

REPLACE WITH THIS:

  # ═══════════════════════════════════════════════════════════════════════
  # CORS Configuration - Allow frontend requests
  # ═══════════════════════════════════════════════════════════════════════
  
  # For development: Allow all origins (localhost, etc.)
  if DEBUG:
      CORS_ALLOW_ALL_ORIGINS = True
  else:
      # For production: Only allow specific origins
      CORS_ALLOWED_ORIGINS = [
          'https://yourdomain.com',
          'https://www.yourdomain.com',
          'https://app.yourdomain.com',
      ]
  
  CORS_ALLOW_CREDENTIALS = True
  
  CORS_ALLOW_HEADERS = [
      'accept',
      'accept-encoding',
      'authorization',
      'content-type',
      'dnt',
      'origin',
      'user-agent',
      'x-csrftoken',
      'x-requested-with',
      'x-user-id',
      'X-User-ID',
  ]
  
  CORS_ALLOW_METHODS = [
      'DELETE',
      'GET',
      'OPTIONS',
      'PATCH',
      'POST',
      'PUT',
  ]
  
  # This makes sure preflight requests (OPTIONS) are handled
  CORS_PREFLIGHT_MAX_AGE = 86400  # Cache for 24 hours


AFTER THIS, restart your Django server:
  Ctrl+C to stop
  python manage.py runserver


═══════════════════════════════════════════════════════════════════════════════════

IF STILL NOT WORKING

Check if the API endpoint actually exists:

From your terminal:
  curl -X OPTIONS https://ed-tech-backend-tzn8.onrender.com/api/solve/ \
    -H "Origin: http://localhost:8081" \
    -v

You should see:
  HTTP/1.1 200 OK
  access-control-allow-origin: *
  access-control-allow-methods: GET, POST, OPTIONS, PUT, DELETE
  access-control-allow-headers: ...

If you see HTTP 405 or 404:
  → The endpoint doesn't exist or isn't configured properly


═══════════════════════════════════════════════════════════════════════════════════

FRONTEND FIX (Even if backend CORS works)

Your frontend might not be handling the request correctly. Update your API call:

TypeScript/JavaScript:

BEFORE (might not work with CORS):
  const response = await fetch('https://ed-tech-backend-tzn8.onrender.com/api/solve/', {
    method: 'POST',
    body: JSON.stringify({...})
  });

AFTER (explicitly handle CORS):
  const response = await fetch('https://ed-tech-backend-tzn8.onrender.com/api/solve/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-User-ID': 'your-user-id',  // if needed
    },
    body: JSON.stringify({...}),
    credentials: 'include',  // If you need to send cookies
    mode: 'cors',  // Explicitly enable CORS
  });

Using Axios:

BEFORE:
  axios.post('https://ed-tech-backend-tzn8.onrender.com/api/solve/', data)

AFTER:
  axios.post('https://ed-tech-backend-tzn8.onrender.com/api/solve/', data, {
    headers: {
      'Content-Type': 'application/json',
      'X-User-ID': 'your-user-id',
    },
    withCredentials: true,  // Send cookies if authenticated
  });


═══════════════════════════════════════════════════════════════════════════════════

TROUBLESHOOTING CHECKLIST

☐ Is CORS enabled in Django settings?
  Check: 'corsheaders' in INSTALLED_APPS
  Check: corsheaders.middleware.CorsMiddleware in MIDDLEWARE
  Check: CORS_ALLOW_ALL_ORIGINS = True (or CORS_ALLOWED_ORIGINS configured)

☐ Is the middleware in the RIGHT ORDER?
  Check: corsheaders.middleware.CorsMiddleware should be near the top
  Should be: BEFORE SessionMiddleware, CommonMiddleware, etc.

☐ Is the API endpoint accessible?
  Test: curl https://ed-tech-backend-tzn8.onrender.com/api/solve/
  Should NOT be 404 or 500

☐ Are you using HTTPS on backend?
  Frontend: http://localhost:8081 (or https://)
  Backend: https://ed-tech-backend-tzn8.onrender.com ✓
  Mixing HTTP/HTTPS can cause issues

☐ Did you restart the Django server?
  After changing settings.py, restart with: python manage.py runserver

☐ Are browser caches cleared?
  Sometimes browsers cache the failed request
  Clear cache: Ctrl+Shift+Delete

☐ Is the request actually JSON?
  Check: Content-Type header is 'application/json'
  Check: Request body is valid JSON


═══════════════════════════════════════════════════════════════════════════════════

DEVELOPMENT VS PRODUCTION

DEVELOPMENT (localhost:8081 → localhost:8000):
  CORS_ALLOW_ALL_ORIGINS = True
  ✓ Simple, works for testing
  ✓ No security needed (local development)

PRODUCTION (frontend.com → api.backend.com):
  CORS_ALLOWED_ORIGINS = ['https://frontend.com']
  ✓ Secure, only allows your frontend
  ✓ Blocks unauthorized origins

═══════════════════════════════════════════════════════════════════════════════════

OTHER ERRORS YOU MIGHT SEE

Error: "No 'Access-Control-Allow-Credentials' header"
  Fix: Add CORS_ALLOW_CREDENTIALS = True

Error: "No 'Access-Control-Allow-Headers' header"
  Fix: Add the header name to CORS_ALLOW_HEADERS

Error: "Method not allowed in CORS policy"
  Fix: Add the method to CORS_ALLOW_METHODS

Error: "Preflight request failed"
  Fix: Make sure OPTIONS method is allowed

═══════════════════════════════════════════════════════════════════════════════════

TESTING WITH CURL

Test if backend sends CORS headers:

  curl -X OPTIONS https://ed-tech-backend-tzn8.onrender.com/api/solve/ \
    -H "Origin: http://localhost:8081" \
    -H "Access-Control-Request-Method: POST" \
    -v

Look for in response:
  ✓ access-control-allow-origin: *
  ✓ access-control-allow-methods: POST, OPTIONS, ...
  ✓ HTTP 200 OK (not 405 or 500)

Test the actual POST:

  curl -X POST https://ed-tech-backend-tzn8.onrender.com/api/solve/ \
    -H "Content-Type: application/json" \
    -H "Origin: http://localhost:8081" \
    -d '{"text":"What is 2+2?"}' \
    -v

Look for:
  ✓ "access-control-allow-origin" header
  ✓ Response data (not CORS error)

═══════════════════════════════════════════════════════════════════════════════════

STEP-BY-STEP FIX GUIDE

STEP 1: Clear Browser Cache
  Ctrl+Shift+Delete → Clear cache → Hard refresh (Ctrl+F5)

STEP 2: Check if Backend Sends CORS Headers
  curl -X OPTIONS https://ed-tech-backend-tzn8.onrender.com/api/solve/ \
    -H "Origin: http://localhost:8081" \
    -v | grep -i "access-control"

STEP 3: If Step 2 shows nothing, update settings.py
  Replace CORS config with the one in "IF THE QUICK FIXES DON'T WORK" section

STEP 4: Restart Django
  Ctrl+C (stop server)
  python manage.py runserver

STEP 5: Test again
  curl -X OPTIONS https://ed-tech-backend-tzn8.onrender.com/api/solve/ \
    -H "Origin: http://localhost:8081" \
    -v | grep -i "access-control"

STEP 6: If STILL not working, check middleware order
  Open settings.py
  Look for MIDDLEWARE = [...]
  corsheaders.middleware.CorsMiddleware should be SECOND (after SecurityMiddleware)

STEP 7: Update frontend code (see FRONTEND FIX section)
  Add 'credentials': 'include' and 'mode': 'cors' to fetch options

═══════════════════════════════════════════════════════════════════════════════════

FINAL CHECKLIST

Backend:
  ☐ CORS installed: pip list | grep django-cors-headers
  ☐ CORS in INSTALLED_APPS: ✓ corsheaders
  ☐ CORS middleware in MIDDLEWARE: ✓ corsheaders.middleware.CorsMiddleware
  ☐ CORS settings configured: ✓ CORS_ALLOW_ALL_ORIGINS = True
  ☐ Server restarted after changes: ✓

Frontend:
  ☐ Using fetch with mode: 'cors'
  ☐ Content-Type header set to 'application/json'
  ☐ Using correct API endpoint URL
  ☐ Browser cache cleared
  ☐ No console errors besides CORS

═══════════════════════════════════════════════════════════════════════════════════

STILL STUCK? ENABLE DEBUG LOGGING

Add this to settings.py to see CORS debug info:

  import logging
  logger = logging.getLogger('corsheaders')
  logger.setLevel(logging.DEBUG)

Then watch the server logs when making the request:

  python manage.py runserver --verbosity 2

This will show exactly what CORS is doing.

═══════════════════════════════════════════════════════════════════════════════════

SUMMARY

The CORS error means:
  ✗ Browser blocked your request (security feature)
  ✓ Backend needs to send CORS headers allowing your frontend

To fix:
  1. Clear browser cache
  2. Ensure CORS is enabled in Django
  3. Restart Django server
  4. Update frontend to use 'mode': 'cors'
  5. Test with curl first, then browser

═══════════════════════════════════════════════════════════════════════════════════

# 🔐 AUTHENTICATION - QUICK REFERENCE CARD

## ✅ All Endpoints Tested & Working

### 1️⃣ SIGNUP
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"john123","email":"john@example.com","password":"SecurePass123!"}' \
  http://localhost:8000/api/auth/register/
```
Returns: `token`, `user_id`, `email`

---

### 2️⃣ LOGIN
```bash
# With username
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"john123","password":"SecurePass123!"}' \
  http://localhost:8000/api/auth/login/

# Or with email
curl -X POST -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"SecurePass123!"}' \
  http://localhost:8000/api/auth/login/
```
Returns: `token`, `user_id`, `coins`, `subscription_status`

---

### 3️⃣ PASSWORD RESET - 3 Steps

**Step 1: Request Reset**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"email":"john@example.com"}' \
  http://localhost:8000/api/auth/request-password-reset/
```

**Step 2: Validate Token (optional)**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"token":"RESET_TOKEN_FROM_EMAIL"}' \
  http://localhost:8000/api/auth/validate-reset-token/
```

**Step 3: Reset Password**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"token":"RESET_TOKEN_FROM_EMAIL","new_password":"NewPass456@"}' \
  http://localhost:8000/api/auth/reset-password/
```

---

### 4️⃣ VERIFY TOKEN
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"token":"JWT_TOKEN"}' \
  http://localhost:8000/api/auth/verify/
```

---

### 5️⃣ GET PROFILE (Requires Token)
```bash
curl -H "Authorization: Bearer JWT_TOKEN" \
  http://localhost:8000/api/auth/user/profile/
```

---

### 6️⃣ CHANGE PASSWORD (Requires Token)
```bash
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer JWT_TOKEN" \
  -d '{"old_password":"OldPass123!","new_password":"NewPass456@"}' \
  http://localhost:8000/api/auth/change-password/
```

---

### 7️⃣ LOGOUT (Requires Token)
```bash
curl -X POST -H "Authorization: Bearer JWT_TOKEN" \
  http://localhost:8000/api/auth/logout/
```

---

## �� Example Complete Flow

```bash
#!/bin/bash

# 1. SIGNUP
SIGNUP=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"Pass123!"}' \
  http://localhost:8000/api/auth/register/)

TOKEN=$(echo $SIGNUP | jq -r '.data.token')
echo "Signed up! Token: $TOKEN"

# 2. LOGIN
LOGIN=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Pass123!"}' \
  http://localhost:8000/api/auth/login/)

TOKEN=$(echo $LOGIN | jq -r '.data.token')
echo "Logged in! Token: $TOKEN"

# 3. GET PROFILE
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/auth/user/profile/ | jq .

# 4. CHANGE PASSWORD
curl -s -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"old_password":"Pass123!","new_password":"NewPass456@"}' \
  http://localhost:8000/api/auth/change-password/ | jq .

# 5. PASSWORD RESET REQUEST
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}' \
  http://localhost:8000/api/auth/request-password-reset/ | jq .

# 6. LOGOUT
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/auth/logout/ | jq .
```

---

## 🔑 Authentication Headers

All endpoints requiring authentication use:
```bash
-H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Or alternatively:
```bash
-H "X-User-ID: user123"
```

---

## ✨ Feature Limits After Login

- **Free Plan:** 3 uses per feature, monthly reset
- **Paid Plan:** Unlimited usage
- **Check Usage:** `GET /api/usage/real-time/` (requires auth)

---

## 📊 Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created (signup) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (auth failed) |
| 403 | Forbidden (quota exceeded) |
| 404 | Not Found |
| 500 | Server Error |

---

## ⚠️ Common Errors & Solutions

### Error: "Username already taken"
**Solution:** Choose a different username

### Error: "Email already registered"
**Solution:** Use a different email or login if you have an account

### Error: "Password must be at least 8 characters..."
**Solution:** Password needs: uppercase, lowercase, number, special char (!@#$%^&*)

### Error: "Invalid token"
**Solution:** Token may be expired (7 days) or invalid. Login again to get new token

### Error: "Authorization header is missing"
**Solution:** Add `-H "Authorization: Bearer $TOKEN"` to your curl command

---

## 🚀 Production Deployment

Before going live:
1. ✅ Set `FRONTEND_URL` for password reset links
2. ✅ Configure email backend (Gmail SMTP or AWS SES)
3. ✅ Set strong `SECRET_KEY` in Django settings
4. ✅ Enable HTTPS
5. ✅ Add rate limiting to prevent brute force
6. ✅ Configure CORS for your frontend domain

---

**Status: 🎯 PRODUCTION READY**

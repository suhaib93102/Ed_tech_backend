# 🔐 COMPLETE AUTHENTICATION FLOW GUIDE

## Issue Identified ❌
Your frontend is calling: `POST /api/api/auth/login/` (double `/api/`)
Should be: `POST /api/auth/login/` (single `/api/`)

---

## Auth API Base URL
```
http://localhost:8000/api/
```

**NOT** `http://localhost:8000/api/api/`

---

## 1️⃣ SIGNUP / REGISTRATION

### Endpoint
```
POST /api/auth/register/
```

### cURL Command
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123",
    "full_name": "John Doe"
  }'
```

### Success Response (200 OK)
```json
{
  "success": true,
  "message": "Registration successful",
  "data": {
    "user_id": 53,
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "created_at": "2026-01-10T21:22:28.786809+00:00"
  }
}
```

### Error Response - Email Already Exists
```json
{
  "success": false,
  "error": "Email already registered"
}
```

### Error Response - Weak Password
```json
{
  "success": false,
  "error": "Password must be at least 6 characters long"
}
```

---

## 2️⃣ LOGIN

### Endpoint
```
POST /api/auth/login/
```

### cURL Command (with email)
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john@example.com",
    "password": "SecurePass123"
  }'
```

### cURL Command (with username)
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123"
  }'
```

### Success Response (200 OK)
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user_id": 53,
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "coins": 100,
    "last_login": "2026-01-10T21:22:28+00:00"
  }
}
```

### Error Response - User Not Found (401)
```json
{
  "success": false,
  "error": "User not found. Please check your username/email or sign up for a new account.",
  "error_code": "USER_NOT_FOUND"
}
```

### Error Response - Wrong Password (401)
```json
{
  "success": false,
  "error": "Incorrect password. Please try again.",
  "error_code": "INVALID_PASSWORD"
}
```

---

## 3️⃣ VERIFY TOKEN (Get User Info)

### Endpoint
```
GET /api/auth/verify/
```

### cURL Command
```bash
curl -X GET http://localhost:8000/api/auth/verify/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "user_id": 53,
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "coins": 100,
    "is_active": true,
    "date_joined": "2026-01-10T21:22:28+00:00"
  }
}
```

### Error Response - Invalid Token (401)
```json
{
  "success": false,
  "error": "Invalid token"
}
```

---

## 4️⃣ CHANGE PASSWORD (When Logged In)

### Endpoint
```
POST /api/auth/change-password/
```

### cURL Command
```bash
curl -X POST http://localhost:8000/api/auth/change-password/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "old_password": "SecurePass123",
    "new_password": "NewSecurePass456"
  }'
```

### Success Response (200 OK)
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

### Error Response - Wrong Old Password (400)
```json
{
  "success": false,
  "error": "Incorrect old password"
}
```

### Error Response - Invalid New Password (400)
```json
{
  "success": false,
  "error": "Password must be at least 6 characters long"
}
```

---

## 5️⃣ REQUEST PASSWORD RESET (Forgot Password)

### Endpoint
```
POST /api/auth/request-password-reset/
```

### cURL Command
```bash
curl -X POST http://localhost:8000/api/auth/request-password-reset/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com"
  }'
```

### Success Response (200 OK)
```json
{
  "success": true,
  "message": "Password reset email sent to john@example.com. Check your inbox and spam folder.",
  "data": {
    "email": "john@example.com",
    "reset_token": "abc123def456..."
  }
}
```

### Error Response - User Not Found (404)
```json
{
  "success": false,
  "error": "User with this email not found"
}
```

---

## 6️⃣ VALIDATE RESET TOKEN

### Endpoint
```
POST /api/auth/validate-reset-token/
```

### cURL Command
```bash
curl -X POST http://localhost:8000/api/auth/validate-reset-token/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "abc123def456..."
  }'
```

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "email": "john@example.com",
    "user_id": 53,
    "username": "john_doe"
  }
}
```

### Error Response - Invalid or Expired Token (400)
```json
{
  "success": false,
  "error": "Token has expired or has already been used"
}
```

---

## 7️⃣ RESET PASSWORD (With Token)

### Endpoint
```
POST /api/auth/reset-password/
```

### cURL Command
```bash
curl -X POST http://localhost:8000/api/auth/reset-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "abc123def456...",
    "new_password": "NewSecurePass789"
  }'
```

### Success Response (200 OK)
```json
{
  "success": true,
  "message": "Password reset successfully. You can now login with your new password."
}
```

### Error Response - Invalid Token (400)
```json
{
  "success": false,
  "error": "Token has expired or has already been used"
}
```

---

## 📱 COMPLETE USER JOURNEY

```
┌─────────────────────────────────────────────────────────────────┐
│                    NEW USER REGISTRATION                        │
├─────────────────────────────────────────────────────────────────┤
│  1. POST /api/auth/register/                                   │
│     → username, email, password, full_name                     │
│     ← token (auto-logged in)                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      EXISTING USER LOGIN                        │
├─────────────────────────────────────────────────────────────────┤
│  1. POST /api/auth/login/                                      │
│     → username (or email), password                            │
│     ← token, user_id, coins, last_login                        │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                  VERIFY TOKEN & GET USER INFO                   │
├─────────────────────────────────────────────────────────────────┤
│  1. GET /api/auth/verify/                                      │
│     → Authorization: Bearer <token>                            │
│     ← user_id, username, email, coins, is_active              │
└─────────────────────────────────────────────────────────────────┘
                            ↓
                    ┌──────┴──────┐
                    ↓             ↓
      ┌───────────────────┐  ┌──────────────────┐
      │ CHANGE PASSWORD   │  │ FORGOT PASSWORD  │
      │ (Logged In User)  │  │ (Forgotten Pass) │
      └───────────────────┘  └──────────────────┘
             ↓                        ↓
      1. POST /api/auth/           1. POST /api/auth/
         change-password/             request-password-reset/
      → old_password,              → email
        new_password               ← reset_token
      ← success                           ↓
                                   2. POST /api/auth/
                                      validate-reset-token/
                                      → token
                                      ← user info
                                           ↓
                                   3. POST /api/auth/
                                      reset-password/
                                      → token, new_password
                                      ← success
                                           ↓
                                   4. POST /api/auth/login/
                                      (Login with new password)
```

---

## 🔑 Key Points

### Authentication Headers
```bash
# Use this header with every authenticated request:
Authorization: Bearer <token>
```

### Token Format
- JWT token (JSON Web Token)
- Valid for 7 days
- Stored securely on client side
- Sent in Authorization header for all protected endpoints

### Password Requirements
- Minimum 6 characters
- Case-sensitive
- Can include special characters

### Email Validation
- Must be valid email format
- Must be unique (no duplicates)
- Case-insensitive for lookup

### Base URL Configuration
Your frontend should have:
```javascript
// CORRECT ✅
const API_BASE = "https://ed-tech-backend-tzn8.onrender.com/api";

// WRONG ❌
const API_BASE = "https://ed-tech-backend-tzn8.onrender.com/api/api";
```

Then use:
```javascript
// For login
fetch(`${API_BASE}/auth/login/`, ...)

// For register
fetch(`${API_BASE}/auth/register/`, ...)

// For reset password
fetch(`${API_BASE}/auth/request-password-reset/`, ...)
```

---

## 🧪 Quick Test Script

```bash
#!/bin/bash

BASE_URL="http://localhost:8000/api"
TIMESTAMP=$(date +%s)

echo "=== 1. REGISTER NEW USER ==="
REGISTER_RESPONSE=$(curl -s -X POST $BASE_URL/auth/register/ \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"user_$TIMESTAMP\",
    \"email\": \"user_$TIMESTAMP@test.com\",
    \"password\": \"TestPass123\",
    \"full_name\": \"Test User\"
  }")

echo $REGISTER_RESPONSE | jq .
TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.data.token')
USER_ID=$(echo $REGISTER_RESPONSE | jq -r '.data.user_id')

echo ""
echo "=== 2. VERIFY TOKEN ==="
curl -s -X GET $BASE_URL/auth/verify/ \
  -H "Authorization: Bearer $TOKEN" | jq .

echo ""
echo "=== 3. CHANGE PASSWORD ==="
curl -s -X POST $BASE_URL/auth/change-password/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "old_password": "TestPass123",
    "new_password": "NewPass456"
  }' | jq .

echo ""
echo "=== 4. LOGIN WITH NEW PASSWORD ==="
curl -s -X POST $BASE_URL/auth/login/ \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"user_$TIMESTAMP\",
    \"password\": \"NewPass456\"
  }" | jq .

echo ""
echo "=== 5. REQUEST PASSWORD RESET ==="
curl -s -X POST $BASE_URL/auth/request-password-reset/ \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"user_$TIMESTAMP@test.com\"
  }" | jq .
```

---

## ✅ All Endpoints Summary

| Method | Endpoint | Auth Required | Purpose |
|--------|----------|---------------|---------|
| POST | `/auth/register/` | No | Create new account |
| POST | `/auth/login/` | No | Login with credentials |
| GET | `/auth/verify/` | Yes | Verify token & get user info |
| POST | `/auth/change-password/` | Yes | Change password (logged in) |
| POST | `/auth/request-password-reset/` | No | Request password reset email |
| POST | `/auth/validate-reset-token/` | No | Validate reset token |
| POST | `/auth/reset-password/` | No | Reset password with token |

---

## 🚀 Frontend Integration

### React/TypeScript Example
```typescript
// api.ts
const API_BASE = "https://ed-tech-backend-tzn8.onrender.com/api";

// REGISTER
export const registerUser = async (username: string, email: string, password: string) => {
  const response = await fetch(`${API_BASE}/auth/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password })
  });
  return response.json();
};

// LOGIN
export const loginUser = async (username: string, password: string) => {
  const response = await fetch(`${API_BASE}/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  return response.json();
};

// CHANGE PASSWORD
export const changePassword = async (token: string, oldPassword: string, newPassword: string) => {
  const response = await fetch(`${API_BASE}/auth/change-password/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ old_password: oldPassword, new_password: newPassword })
  });
  return response.json();
};

// REQUEST RESET
export const requestPasswordReset = async (email: string) => {
  const response = await fetch(`${API_BASE}/auth/request-password-reset/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  });
  return response.json();
};

// RESET PASSWORD
export const resetPassword = async (token: string, newPassword: string) => {
  const response = await fetch(`${API_BASE}/auth/reset-password/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token, new_password: newPassword })
  });
  return response.json();
};
```

---

## Status: ✅ FULLY WORKING

All authentication endpoints are functional and tested.


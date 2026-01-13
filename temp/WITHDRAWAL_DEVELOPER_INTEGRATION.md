# Withdrawal System - Developer Integration Guide

## Overview
This guide helps developers integrate the coin withdrawal system into frontend applications.

## File Structure
```
question_solver/
├── withdrawal_views.py          ← 4 main endpoints
├── models.py                    ← CoinWithdrawal, UserCoins, CoinTransaction
├── urls.py                      ← URL patterns registered
└── ...
```

## Installation & Deployment

### 1. Database Setup
```bash
# Apply migrations (CoinWithdrawal model should be migrated)
python manage.py migrate

# Verify in shell
python manage.py shell
>>> from question_solver.models import CoinWithdrawal
>>> CoinWithdrawal.objects.count()  # Should return 0 or existing count
```

### 2. Verify Files
```bash
# Check all required files exist
ls question_solver/withdrawal_views.py    # Must exist
grep "withdraw_coins" question_solver/urls.py  # Should find imports
```

### 3. Test Server
```bash
# Start development server
python manage.py runserver

# In another terminal, test endpoint
curl -X POST http://localhost:8000/api/razorpay/withdraw/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "amount": 500, "upi_id": "user@ybl"}'
```

---

## Frontend Integration

### JavaScript/React Example
```javascript
// Create withdrawal request
async function createWithdrawal(userId, amount, upiId) {
  const response = await fetch('/api/razorpay/withdraw/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id: userId,
      amount: parseInt(amount),
      upi_id: upiId
    })
  });
  
  const data = await response.json();
  if (data.success) {
    console.log('Withdrawal ID:', data.data.withdrawal_id);
    return data.data;
  } else {
    throw new Error(data.error);
  }
}

// Get withdrawal history
async function getWithdrawalHistory(userId, status = null) {
  let url = `/api/razorpay/withdraw/history/?user_id=${userId}`;
  if (status) url += `&status=${status}`;
  
  const response = await fetch(url);
  const data = await response.json();
  return data.data || [];
}

// Get withdrawal details
async function getWithdrawalDetails(withdrawalId) {
  const response = await fetch(
    `/api/razorpay/withdraw/status/?withdrawal_id=${withdrawalId}`
  );
  const data = await response.json();
  return data.data;
}

// Cancel withdrawal
async function cancelWithdrawal(withdrawalId, reason = '') {
  const response = await fetch('/api/razorpay/withdraw/cancel/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      withdrawal_id: withdrawalId,
      reason: reason
    })
  });
  
  const data = await response.json();
  if (data.success) {
    return data.data;
  } else {
    throw new Error(data.error);
  }
}
```

### React Component Example
```jsx
import React, { useState, useEffect } from 'react';

function WithdrawalComponent({ userId, currentCoins }) {
  const [amount, setAmount] = useState('');
  const [upiId, setUpiId] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    loadHistory();
  }, [userId]);

  const loadHistory = async () => {
    try {
      const response = await fetch(
        `/api/razorpay/withdraw/history/?user_id=${userId}`
      );
      const data = await response.json();
      if (data.success) {
        setHistory(data.data);
      }
    } catch (err) {
      console.error('Error loading history:', err);
    }
  };

  const handleWithdraw = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    try {
      const numAmount = parseInt(amount);
      
      // Validation
      if (!upiId.match(/^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+$/)) {
        throw new Error('Invalid UPI format. Example: user@okhdfcbank');
      }
      
      if (numAmount < 100) {
        throw new Error('Minimum withdrawal: 100 coins');
      }
      
      if (numAmount > 100000) {
        throw new Error('Maximum withdrawal: 100,000 coins');
      }
      
      if (numAmount > currentCoins) {
        throw new Error(`Insufficient balance. You have ${currentCoins} coins`);
      }

      const response = await fetch('/api/razorpay/withdraw/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          amount: numAmount,
          upi_id: upiId
        })
      });

      const data = await response.json();
      
      if (data.success) {
        setMessage(`Withdrawal request submitted! ID: ${data.data.withdrawal_id}`);
        setAmount('');
        setUpiId('');
        loadHistory();
      } else {
        throw new Error(data.error);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="withdrawal-container">
      <h2>Withdraw Coins</h2>
      
      <div className="info">
        <p>Available Coins: {currentCoins}</p>
        <p>Conversion: 1 coin = ₹0.10</p>
      </div>

      <form onSubmit={handleWithdraw}>
        <input
          type="number"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          placeholder="Amount (coins)"
          min="100"
          max="100000"
          required
        />
        
        <input
          type="text"
          value={upiId}
          onChange={(e) => setUpiId(e.target.value)}
          placeholder="UPI ID (e.g., user@okhdfcbank)"
          required
        />

        {amount && (
          <p>You'll receive: ₹{(parseInt(amount) * 0.10).toFixed(2)}</p>
        )}

        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Submit Request'}
        </button>
      </form>

      {message && <div className="success">{message}</div>}
      {error && <div className="error">{error}</div>}

      <div className="history">
        <h3>Withdrawal History</h3>
        {history.length === 0 ? (
          <p>No withdrawals yet</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Amount</th>
                <th>UPI</th>
                <th>Status</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {history.map((w) => (
                <tr key={w.id}>
                  <td>{w.amount} coins</td>
                  <td>{w.upi_id}</td>
                  <td className={`status-${w.status}`}>{w.status}</td>
                  <td>{new Date(w.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default WithdrawalComponent;
```

### Python Integration
```python
import requests
import json

class WithdrawalClient:
    def __init__(self, base_url="http://localhost:8000/api"):
        self.base_url = base_url
    
    def create_withdrawal(self, user_id, amount, upi_id):
        """Create a withdrawal request"""
        response = requests.post(
            f"{self.base_url}/razorpay/withdraw/",
            json={
                "user_id": user_id,
                "amount": amount,
                "upi_id": upi_id
            }
        )
        return response.json()
    
    def get_history(self, user_id, status=None, limit=50):
        """Get withdrawal history"""
        params = {"user_id": user_id, "limit": limit}
        if status:
            params["status"] = status
        
        response = requests.get(
            f"{self.base_url}/razorpay/withdraw/history/",
            params=params
        )
        return response.json()
    
    def get_details(self, withdrawal_id):
        """Get withdrawal details"""
        response = requests.get(
            f"{self.base_url}/razorpay/withdraw/status/",
            params={"withdrawal_id": withdrawal_id}
        )
        return response.json()
    
    def cancel(self, withdrawal_id, reason=""):
        """Cancel withdrawal"""
        response = requests.post(
            f"{self.base_url}/razorpay/withdraw/cancel/",
            json={
                "withdrawal_id": withdrawal_id,
                "reason": reason
            }
        )
        return response.json()

# Usage
client = WithdrawalClient()

# Create withdrawal
result = client.create_withdrawal("user123", 500, "user@okhdfcbank")
print(result)

# Get history
history = client.get_history("user123", status="pending")
print(f"Pending withdrawals: {len(history['data'])}")

# Get details
details = client.get_details("withdrawal-uuid")
print(f"Status: {details['data']['status']}")

# Cancel
cancel_result = client.cancel("withdrawal-uuid", "Changed my mind")
print(f"Refunded: {cancel_result['data']['refunded_coins']} coins")
```

---

## Error Handling

### Common Error Scenarios
```javascript
// Handle common errors
async function handleWithdrawalError(error) {
  const errorData = error.response?.data;
  
  if (error.response?.status === 400) {
    // Bad request - validation error
    if (errorData.error.includes('Insufficient')) {
      return 'You don\'t have enough coins';
    }
    if (errorData.error.includes('Invalid UPI')) {
      return 'UPI format: user@bankname (e.g., user@ybl)';
    }
    if (errorData.error.includes('Minimum withdrawal')) {
      return 'Minimum withdrawal is 100 coins';
    }
    return errorData.error;
  }
  
  if (error.response?.status === 404) {
    return 'Withdrawal not found';
  }
  
  if (error.response?.status === 500) {
    return 'Server error. Please try again later';
  }
  
  return 'Unknown error occurred';
}
```

---

## Validation Rules

### UPI ID
```javascript
function validateUPI(upi) {
  // Pattern: username@bankname
  return /^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+$/.test(upi);
}

// Valid examples
validateUPI('user@okhdfcbank')  // true
validateUPI('john@ybl')          // true
validateUPI('mobile@airtel')     // true
validateUPI('invalid-upi')       // false
```

### Amount
```javascript
function validateAmount(amount, availableCoins) {
  const num = parseInt(amount);
  
  // Check minimum
  if (num < 100) return 'Minimum: 100 coins';
  
  // Check maximum
  if (num > 100000) return 'Maximum: 100,000 coins';
  
  // Check balance
  if (num > availableCoins) return 'Insufficient balance';
  
  return null; // Valid
}
```

---

## API Response Format

### Successful Response (201)
```json
{
  "success": true,
  "message": "Withdrawal request submitted successfully...",
  "data": {
    "withdrawal_id": "550e8400-e29b-41d4-a716-446655440000",
    "amount": 500,
    "rupees_amount": 50.00,
    "upi_id": "user@okhdfcbank",
    "status": "pending",
    "remaining_coins": 1500,
    "created_at": "2026-01-09T15:30:00Z"
  }
}
```

### Error Response (400/404/500)
```json
{
  "success": false,
  "error": "Error description",
  "details": "Additional error details",
  "available_coins": 100  // If balance error
}
```

---

## Testing Checklist

- [ ] Create valid withdrawal request
- [ ] Validate insufficient balance error
- [ ] Validate invalid UPI error
- [ ] Validate amount limits
- [ ] Get withdrawal history
- [ ] Get specific withdrawal details
- [ ] Cancel pending withdrawal
- [ ] Verify coins refunded on cancel
- [ ] Test with various UPI formats
- [ ] Check Django admin panel updates

---

## Deployment Steps

1. **Copy files to production server**
   ```bash
   cp question_solver/withdrawal_views.py /production/path/
   ```

2. **Update production URLs**
   ```bash
   # Verify withdrawal_views imports in urls.py
   grep "from .withdrawal_views" question_solver/urls.py
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Restart application**
   ```bash
   systemctl restart gunicorn  # or your app server
   systemctl restart nginx
   ```

5. **Verify endpoints**
   ```bash
   curl -X GET "https://api.example.com/api/razorpay/withdraw/history/?user_id=test"
   ```

6. **Monitor logs**
   ```bash
   tail -f logs/django.log | grep WITHDRAW
   ```

---

## Support & Debugging

### Check endpoint status
```bash
curl -v -X POST http://localhost:8000/api/razorpay/withdraw/ \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","amount":500,"upi_id":"user@ybl"}'
```

### Django shell debugging
```bash
python manage.py shell

# Check if endpoint is working
from question_solver.withdrawal_views import withdraw_coins
print(withdraw_coins)  # Should show function

# Check models
from question_solver.models import CoinWithdrawal, UserCoins
CoinWithdrawal.objects.count()
UserCoins.objects.count()
```

### View logs
```bash
# Real-time logs
tail -f logs/django.log

# Search for withdrawal operations
grep "\[WITHDRAW\]" logs/django.log
```

---

**Version:** 1.0
**Last Updated:** 2026-01-09
**Status:** Production Ready ✅

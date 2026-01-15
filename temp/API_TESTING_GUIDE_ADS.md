# Unity Ads API Testing Guide

## API Endpoints Reference

### 1. Get Next Ad to Show

**Endpoint:** `POST /api/ads/get-next/`

Shows ads only to free users, checks frequency caps, and returns ad config.

**Request:**
```json
{
  "user_id": "user123",
  "device_id": "device_abc123",
  "platform": "android",
  "feature": "quiz",
  "app_version": "1.0.0"
}
```

**Response (Free User):**
```json
{
  "should_show_ad": true,
  "campaign": {
    "id": "campaign-uuid",
    "unity_game_id": "6018264",
    "unity_placement_id": "Placement_Interstitial",
    "ad_type": "interstitial",
    "delay_seconds": 500
  },
  "impression_id": "impression-uuid",
  "message": "Showing interstitial ad for quiz"
}
```

**Response (Premium User):**
```json
{
  "should_show_ad": false,
  "reason": "User is premium subscriber - no ads shown"
}
```

**cURL Test:**
```bash
curl -X POST "http://localhost:8000/api/ads/get-next/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_free",
    "device_id": "device_123",
    "platform": "android",
    "feature": "quiz",
    "app_version": "1.0.0"
  }'
```

---

### 2. Record Ad Status

**Endpoint:** `POST /api/ads/record-status/`

Records when user completes, skips, or fails an ad. Tracks rewards for rewarded ads.

**Request:**
```json
{
  "impression_id": "impression-uuid",
  "status": "completed",
  "duration_seconds": 30
}
```

Valid statuses:
- `shown` - Ad was displayed
- `clicked` - User clicked ad
- `completed` - User watched entire ad (for rewarded ads)
- `skipped` - User skipped ad
- `failed` - Ad failed to load

**Response:**
```json
{
  "success": true,
  "message": "Ad status updated to completed",
  "reward_earned": 10,
  "impression_id": "impression-uuid"
}
```

**cURL Test:**
```bash
curl -X POST "http://localhost:8000/api/ads/record-status/" \
  -H "Content-Type: application/json" \
  -d '{
    "impression_id": "impression-uuid-here",
    "status": "completed",
    "duration_seconds": 30
  }'
```

---

### 3. Get User Ad Preferences

**Endpoint:** `GET /api/ads/preferences/?user_id=<user_id>`

Retrieves user's ad preferences and statistics.

**Response:**
```json
{
  "success": true,
  "user_id": "user123",
  "ads_enabled": true,
  "ads_opted_in": true,
  "is_premium": false,
  "ads_shown_today": 2,
  "total_ads_shown": 45,
  "total_ads_completed": 38,
  "total_rewards_earned": 380,
  "blocked_campaigns": []
}
```

**cURL Test:**
```bash
curl -X GET "http://localhost:8000/api/ads/preferences/?user_id=user123"
```

---

### 4. Update User Ad Preferences

**Endpoint:** `POST /api/ads/preferences/`

Updates user's ad preferences (enable/disable ads, block campaigns).

**Request:**
```json
{
  "user_id": "user123",
  "ads_enabled": true,
  "ads_opted_in": true,
  "blocked_campaign_ids": ["campaign-uuid-1", "campaign-uuid-2"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Ad preferences updated",
  "user_id": "user123",
  "ads_enabled": true,
  "ads_opted_in": true
}
```

**cURL Test:**
```bash
curl -X POST "http://localhost:8000/api/ads/preferences/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "ads_enabled": true,
    "ads_opted_in": true,
    "blocked_campaign_ids": []
  }'
```

---

### 5. Get Ad Campaign Analytics

**Endpoint:** `GET /api/ads/analytics/?campaign_id=<campaign_id>`

Gets analytics for specific campaign.

**Response:**
```json
{
  "success": true,
  "campaign_id": "campaign-uuid",
  "campaign_name": "Main Interstitial Campaign",
  "total_impressions": 150,
  "total_clicks": 12,
  "total_completed": 95,
  "total_skipped": 40,
  "total_failed": 5,
  "click_through_rate": 8.00,
  "completion_rate": 63.33,
  "total_rewards_distributed": 950,
  "date": "2025-01-15"
}
```

**cURL Test:**
```bash
curl -X GET "http://localhost:8000/api/ads/analytics/?campaign_id=campaign-uuid-here"
```

---

### 6. Get All Analytics Summary

**Endpoint:** `GET /api/ads/analytics/summary/`

Gets analytics for all active campaigns.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "campaign_id": "campaign-uuid-1",
      "campaign_name": "Main Interstitial",
      "total_impressions": 150,
      "total_clicks": 12,
      "click_through_rate": 8.00,
      "completion_rate": 63.33,
      "date": "2025-01-15"
    },
    {
      "campaign_id": "campaign-uuid-2",
      "campaign_name": "Rewarded Video",
      "total_impressions": 80,
      "total_clicks": 8,
      "click_through_rate": 10.00,
      "completion_rate": 75.00,
      "date": "2025-01-15"
    }
  ],
  "count": 2
}
```

**cURL Test:**
```bash
curl -X GET "http://localhost:8000/api/ads/analytics/summary/"
```

---

### 7. Get Active Ad Campaigns Config

**Endpoint:** `GET /api/ads/config/`

Gets configuration of all active campaigns (for frontend initialization).

**Response:**
```json
{
  "success": true,
  "campaigns": [
    {
      "id": "campaign-uuid",
      "name": "Main Interstitial Campaign",
      "ad_type": "interstitial",
      "unity_game_id": "6018264",
      "unity_placement_id": "Placement_Interstitial",
      "max_ads_per_day": 5
    }
  ],
  "count": 1
}
```

**cURL Test:**
```bash
curl -X GET "http://localhost:8000/api/ads/config/"
```

---

## Complete Flow Test

### Scenario: Free User Completes Quiz, Sees Ad, Earns Reward

```bash
# Step 1: Check if free user (should be)
curl -X GET "http://localhost:8000/api/subscription/status/?user_id=test_user_free"

# Step 2: Request ad after quiz completion
RESPONSE=$(curl -X POST "http://localhost:8000/api/ads/get-next/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_free",
    "device_id": "device_123",
    "platform": "android",
    "feature": "quiz",
    "app_version": "1.0.0"
  }')

echo "Ad Response: $RESPONSE"

# Extract impression_id from response
IMPRESSION_ID=$(echo $RESPONSE | jq -r '.impression_id')
echo "Impression ID: $IMPRESSION_ID"

# Step 3: Simulate user completing ad
curl -X POST "http://localhost:8000/api/ads/record-status/" \
  -H "Content-Type: application/json" \
  -d "{
    \"impression_id\": \"$IMPRESSION_ID\",
    \"status\": \"completed\",
    \"duration_seconds\": 30
  }"

# Step 4: Check user rewards and preferences
curl -X GET "http://localhost:8000/api/ads/preferences/?user_id=test_user_free"

# Step 5: View analytics
curl -X GET "http://localhost:8000/api/ads/analytics/summary/"
```

---

## Scenario: Premium User (No Ads)

```bash
# Create premium subscription first via admin or API

# Request ad for premium user
curl -X POST "http://localhost:8000/api/ads/get-next/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_premium",
    "device_id": "device_456",
    "platform": "ios",
    "feature": "quiz",
    "app_version": "1.0.0"
  }'

# Response should indicate no ads
# {
#   "should_show_ad": false,
#   "reason": "User is premium subscriber - no ads shown"
# }
```

---

## Python Testing Script

```python
import requests
import json

API_BASE_URL = "http://localhost:8000"

class AdsAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def test_get_next_ad(self, user_id, feature="quiz"):
        """Test getting next ad"""
        url = f"{self.base_url}/api/ads/get-next/"
        payload = {
            "user_id": user_id,
            "device_id": "device_test",
            "platform": "android",
            "feature": feature,
            "app_version": "1.0.0"
        }
        
        response = requests.post(url, json=payload)
        print(f"✅ Get Next Ad: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    
    def test_record_ad_status(self, impression_id, status="completed"):
        """Test recording ad status"""
        url = f"{self.base_url}/api/ads/record-status/"
        payload = {
            "impression_id": impression_id,
            "status": status,
            "duration_seconds": 30 if status == "completed" else None
        }
        
        response = requests.post(url, json=payload)
        print(f"✅ Record Ad Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    
    def test_get_preferences(self, user_id):
        """Test getting user preferences"""
        url = f"{self.base_url}/api/ads/preferences/"
        params = {"user_id": user_id}
        
        response = requests.get(url, params=params)
        print(f"✅ Get Preferences: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    
    def test_full_flow(self, user_id):
        """Test complete ad flow"""
        print("\n🚀 Testing Complete Ad Flow")
        print("=" * 50)
        
        # Get next ad
        print("\n1️⃣ Requesting ad...")
        ad_response = self.test_get_next_ad(user_id)
        
        if not ad_response.get("should_show_ad"):
            print("❌ No ad to show")
            return
        
        impression_id = ad_response.get("impression_id")
        
        # Record completion
        print("\n2️⃣ Recording ad completion...")
        self.test_record_ad_status(impression_id, "completed")
        
        # Check preferences
        print("\n3️⃣ Checking user preferences...")
        self.test_get_preferences(user_id)
        
        print("\n✅ Flow test complete!")

# Run tests
if __name__ == "__main__":
    tester = AdsAPITester(API_BASE_URL)
    
    # Test free user
    print("=" * 50)
    print("Testing FREE user flow")
    print("=" * 50)
    tester.test_full_flow("test_user_free")
    
    # Test premium user
    print("\n\n" + "=" * 50)
    print("Testing PREMIUM user flow")
    print("=" * 50)
    tester.test_full_flow("test_user_premium")
```

**Run Python test:**
```bash
python ads_test.py
```

---

## Test Cases Checklist

- [ ] **Free user gets ad** - After feature completion
- [ ] **Premium user no ad** - Subscription status checked
- [ ] **Frequency cap enforced** - Max 5 ads per day
- [ ] **Time gap enforced** - Min 5 minutes between ads
- [ ] **Rewarded ad completes** - Coins are tracked
- [ ] **Ad analytics updated** - Impressions/completion rates
- [ ] **User preferences saved** - Blocked campaigns respected
- [ ] **Error handling** - Invalid IDs return 400/404
- [ ] **Rate limiting** - API responses under 200ms
- [ ] **Concurrent requests** - Handle multiple users

---

## Performance Testing

```bash
# Test with Apache Bench (100 requests, 10 concurrent)
ab -n 100 -c 10 \
  -p test_payload.json \
  -T application/json \
  "http://localhost:8000/api/ads/get-next/"

# Expected: <200ms response time
```

---

## Monitoring

```sql
-- SQL to check ad stats
SELECT 
    campaign_id,
    COUNT(*) as total_impressions,
    SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as completed,
    ROUND(100.0 * SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) / COUNT(*), 2) as completion_rate
FROM ads_adimpression
WHERE shown_at >= NOW() - INTERVAL '24 hours'
GROUP BY campaign_id
ORDER BY total_impressions DESC;
```

---

## Troubleshooting Common Issues

### Issue: "No ad to show"
- Check campaign is active: `AdCampaign.is_active = True`
- Check schedule exists for feature
- Check user is not premium
- Check daily frequency cap not reached

### Issue: Rewards not tracking
- Verify status is exactly "completed"
- Check impression exists in database
- Verify `record_ad_completed()` called

### Issue: API timeout
- Check database connection
- Check API server logs
- Monitor network latency
- Profile slow queries


# Unity Ads + Subscription Integration - React Native/Expo

## Complete Implementation Guide

### Overview
This guide covers:
- ✅ Backend (Django) - Ad models, tracking, and API endpoints
- ✅ Frontend (React Native/Expo) - Unity Ads SDK integration
- ✅ Subscription system with ₹1 trial + ₹99/month recurring
- ✅ Production-ready code with error handling

---

## PART 1: DJANGO BACKEND SETUP

### 1.1 Database Models

The backend includes four new models in `ads_models.py`:

```python
# Models created:
- AdCampaign          # Ad campaign configuration
- AdImpression        # Track each ad impression
- AdSchedule          # When to show ads (after which features)
- UserAdPreference    # User ad preferences & history
- AdAnalytics         # Campaign analytics
```

### 1.2 API Endpoints

Five new endpoints available:

```
POST   /api/ads/get-next/              # Get next ad to show
POST   /api/ads/record-status/         # Record ad status (shown/clicked/completed)
GET    /api/ads/preferences/           # Get user ad preferences
POST   /api/ads/preferences/           # Update user ad preferences
GET    /api/ads/analytics/             # Get campaign analytics
GET    /api/ads/config/                # Get active campaigns config
```

### 1.3 Admin Setup

Add to `question_solver/admin.py`:

```python
from .ads_models import AdCampaign, AdImpression, AdSchedule, UserAdPreference, AdAnalytics

@admin.register(AdCampaign)
class AdCampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'ad_type', 'is_active', 'created_at')
    list_filter = ('is_active', 'ad_type')
    search_fields = ('name',)

@admin.register(AdImpression)
class AdImpressionAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'campaign', 'status', 'shown_at')
    list_filter = ('status', 'platform', 'shown_at')
    search_fields = ('user_id',)
    readonly_fields = ('id', 'shown_at')

@admin.register(AdSchedule)
class AdScheduleAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'feature', 'is_active')
    list_filter = ('is_active', 'feature')

@admin.register(UserAdPreference)
class UserAdPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'ads_enabled', 'is_premium', 'total_ads_shown')
    list_filter = ('ads_enabled', 'is_premium')
    search_fields = ('user_id',)

@admin.register(AdAnalytics)
class AdAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'date', 'total_impressions', 'completion_rate')
    list_filter = ('date',)
    readonly_fields = ('date', 'total_impressions', 'total_clicks', 'total_completed')
```

### 1.4 Database Migrations

```bash
# Create migration files
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Verify in Django admin
# - Create an AdCampaign with your Unity Game IDs
# - Create AdSchedule entries for each feature
```

### 1.5 Creating Your First Ad Campaign

**Via Django Admin:**
1. Go to Django admin → Ad Campaigns
2. Create new campaign:
   - Name: "Main Interstitial"
   - iOS Game ID: `6018265`
   - Android Game ID: `6018264`
   - Placement ID: `Placement_<type>` (from Unity Dashboard)
   - Ad Type: `interstitial` or `rewarded`
   - Max Ads Per Day: `5`
   - Min Gap Between Ads: `300` (seconds)

3. Add Ad Schedule:
   - Campaign: Select the campaign above
   - Feature: `quiz` (show ads after quiz completion)
   - Probability: `1.0` (always show)
   - Delay: `500ms` (before showing ad)

---

## PART 2: REACT NATIVE/EXPO SETUP

### 2.1 Installation

```bash
# Initialize EAS for Expo
eas init

# Prebuild native code
npx expo prebuild --clean

# Install dependencies
npm install react-native-unity-ads axios zustand

# Or with yarn
yarn add react-native-unity-ads axios zustand
```

### 2.2 Configure app.json

```json
{
  "expo": {
    "plugins": [
      [
        "react-native-unity-ads",
        {
          "iosGameId": "6018265",
          "androidGameId": "6018264"
        }
      ]
    ]
  }
}
```

### 2.3 File Structure

```
src/
├── services/
│   ├── ads/
│   │   ├── AdsManager.ts              # Ad SDK initialization & display
│   │   ├── premiumService.ts          # Subscription status checks
│   │   └── SubscriptionPricingConfig.ts # Pricing & config
│   └── api.ts                         # API client setup
├── hooks/
│   └── useFeatureWithAd.ts            # Feature + ad wrapper hook
├── store/
│   └── premiumStore.ts                # Zustand subscription state
├── screens/
│   ├── QuizScreen.tsx                 # Feature screens
│   ├── SubscriptionScreen.tsx         # Subscription UI
│   └── ...
└── App.tsx
```

### 2.4 Copy Provided Files

Copy these files to your React Native project:

1. **AdsManager.ts** → `src/services/ads/AdsManager.ts`
   - Initializes Unity Ads SDK
   - Loads and shows ads
   - Tracks impressions

2. **premiumService.ts** → `src/services/ads/premiumService.ts`
   - Fetches subscription status from backend
   - Caches results (5 min default)
   - Checks if user is premium

3. **useFeatureWithAd.ts** → `src/hooks/useFeatureWithAd.ts`
   - React hook to wrap any feature with ad logic
   - Automatically shows ads after feature completion
   - Handles premium user bypass

4. **premiumStore.ts** → `src/store/premiumStore.ts`
   - Zustand store for global subscription state
   - Provides selectors for easy access
   - Reactive updates

5. **SubscriptionPricingConfig.ts** → `src/services/ads/SubscriptionPricingConfig.ts`
   - Centralized pricing configuration
   - Unity Ads config
   - Subscription plans

### 2.5 Initialize Services in App.tsx

```typescript
import { useEffect } from 'react';
import { useIsFocused } from '@react-navigation/native';
import AdsManager from './services/ads/AdsManager';
import premiumService from './services/ads/premiumService';
import { SUBSCRIPTION_CONFIG } from './services/ads/SubscriptionPricingConfig';
import useSubscriptionStore, { useIsPremium } from './store/premiumStore';

export default function App() {
  const isFocused = useIsFocused();
  const setUserId = useSubscriptionStore(state => state.setUserId);
  const isPremium = useIsPremium();

  useEffect(() => {
    // Initialize services
    const initialize = async () => {
      try {
        // Initialize ads
        await AdsManager.initialize(SUBSCRIPTION_CONFIG.UNITY_ADS);
        console.log('✅ AdsManager initialized');

        // Initialize premium service
        premiumService.initialize({
          apiBaseUrl: SUBSCRIPTION_CONFIG.API_BASE_URL,
          cacheDurationMs: SUBSCRIPTION_CONFIG.SYNC_CONFIG.CACHE_DURATION_MS,
        });
        console.log('✅ PremiumService initialized');

        // Set user ID (get from your auth system)
        const userId = await getUserIdFromAuth(); // Your auth logic
        setUserId(userId);
      } catch (error) {
        console.error('Initialization error:', error);
      }
    };

    if (isFocused) {
      initialize();
    }
  }, [isFocused, setUserId]);

  return (
    // Your app content
    <RootNavigator />
  );
}
```

---

## PART 3: USING ADS IN FEATURES

### 3.1 Wrapping Feature Functions with Ads

Example: Quiz Feature

```typescript
import { useFeatureWithAd } from '../hooks/useFeatureWithAd';
import useSubscriptionStore from '../store/premiumStore';

function QuizScreen() {
  const { executeFeature, loading, error, adShowing } = useFeatureWithAd('quiz');
  const userId = useSubscriptionStore(state => state.userId);

  const handleSolveQuiz = async () => {
    const result = await executeFeature(
      async () => {
        // Your quiz logic
        const response = await api.post('/solve/', {
          question_id: '123',
          answer: 'A',
        });
        return response.data;
      },
      userId // Pass user ID for ad tracking
    );

    if (result.success) {
      console.log('Quiz solved:', result.data);
      console.log('Ad shown:', result.adShown);
      console.log('Reward earned:', result.reward); // Usually 10 coins
    } else {
      console.error('Quiz error:', result.error);
    }
  };

  return (
    <View>
      <Button
        title={loading ? 'Loading...' : 'Solve Quiz'}
        onPress={handleSolveQuiz}
        disabled={loading || adShowing}
      />
      {error && <Text style={{color: 'red'}}>{error.message}</Text>}
      {adShowing && <Text>Showing ad...</Text>}
    </View>
  );
}
```

### 3.2 Manual Ad Showing

For more control:

```typescript
import AdsManager from '../services/ads/AdsManager';

async function manuallyShowAd() {
  const adResponse = await AdsManager.getNextAd(
    userId,
    deviceId,
    'android', // or 'ios'
    'quiz',
    apiBaseUrl
  );

  if (adResponse.should_show_ad && adResponse.campaign) {
    const shown = await AdsManager.showInterstitialAd(
      adResponse.campaign.unity_placement_id,
      adResponse.impression_id!,
      apiBaseUrl,
      userId
    );

    if (shown) {
      console.log('Ad displayed successfully');
    }
  }
}
```

### 3.3 Checking Premium Status

```typescript
import { useIsPremium, useSubscriptionPlan } from '../store/premiumStore';
import premiumService from '../services/ads/premiumService';

function MyFeature() {
  const isPremium = useIsPremium();
  const plan = useSubscriptionPlan();

  if (isPremium) {
    return <Text>Premium user - No ads shown</Text>;
  }

  return <Text>Free user - Ads will be shown</Text>;
}

// Manual check
async function checkStatus(userId: string) {
  const isPremium = await premiumService.isPremiumUser(userId);
  const inTrial = await premiumService.isInTrialPeriod(userId);
  
  console.log('Premium:', isPremium);
  console.log('In Trial:', inTrial);
}
```

---

## PART 4: SUBSCRIPTION FLOW

### 4.1 Subscription Plans

```typescript
import { getAllPlans, getPricingText } from '../services/ads/SubscriptionPricingConfig';

function PricingScreen() {
  const plans = getAllPlans();

  return (
    <ScrollView>
      {plans.map(plan => (
        <View key={plan.id} style={plan.highlighted ? styles.highlighted : {}}>
          <Text>{plan.displayName}</Text>
          <Text>{getPricingText(plan)}</Text>
          <Text>{plan.description}</Text>
          <Button title="Subscribe" onPress={() => handleSubscribe(plan)} />
        </View>
      ))}
    </ScrollView>
  );
}
```

### 4.2 Backend Subscription Configuration

**Razorpay Plan Setup:**

1. Go to Razorpay Dashboard
2. Create Subscription Plans:

   **Plan A (BASIC - ₹1 trial + ₹99/month):**
   ```
   - Plan ID: plan_basic_monthly
   - Interval: monthly
   - Period: 1 month
   - Amount: ₹9900 (₹99.00)
   - First payment: ₹100 (₹1.00 trial charge)
   ```

   **Plan B (PREMIUM - ₹99/month directly):**
   ```
   - Plan ID: plan_premium_monthly
   - Interval: monthly
   - Period: 1 month
   - Amount: ₹9900 (₹99.00)
   ```

3. Update Django settings with Plan IDs:
   ```python
   RAZORPAY_PLAN_IDS = {
       'basic': 'plan_basic_monthly',
       'premium': 'plan_premium_monthly',
   }
   ```

---

## PART 5: TESTING

### 5.1 Backend Testing

```bash
# Run migrations
python manage.py migrate

# Create test data
python manage.py shell
>>> from question_solver.ads_models import AdCampaign, AdSchedule
>>> 
>>> # Create campaign
>>> campaign = AdCampaign.objects.create(
...     name='Test Campaign',
...     ad_type='interstitial',
...     unity_game_id='6018264',
...     unity_placement_id='Placement_Interstitial',
... )
>>> 
>>> # Create schedule
>>> AdSchedule.objects.create(
...     campaign=campaign,
...     feature='quiz',
...     probability=1.0,
...     target_free_users_only=True,
... )
```

### 5.2 Frontend Testing

**Test Ad Display:**

```typescript
// In development, ads should show with test Razorpay IDs
// Mock ad responses for testing:

const mockAdResponse = {
  should_show_ad: true,
  campaign: {
    id: 'test-campaign',
    unity_game_id: '6018264',
    unity_placement_id: 'Placement_Interstitial',
    ad_type: 'interstitial',
    delay_seconds: 0,
  },
  impression_id: 'test-impression-id',
};

// Test subscription status
import premiumService from '../services/ads/premiumService';

async function testPremiumCheck() {
  const isPremium = await premiumService.isPremiumUser('test-user-123');
  console.log('Is Premium:', isPremium);
}
```

### 5.3 Test Checklist

- [ ] Backend migrations run successfully
- [ ] Django admin shows Ad Campaign CRUD
- [ ] Frontend initializes AdsManager without errors
- [ ] PremiumService fetches subscription status
- [ ] useFeatureWithAd hook works with feature functions
- [ ] Zustand store updates on premium status change
- [ ] Ad shows only for free users
- [ ] Premium users see no ads
- [ ] Ads don't show more than max_ads_per_day
- [ ] Minimum gap between ads is enforced
- [ ] Rewarded ads track completion
- [ ] Analytics update correctly

---

## PART 6: PRODUCTION DEPLOYMENT

### 6.1 Backend Checklist

```bash
# Before deployment:
1. ✅ Run all migrations
   python manage.py migrate

2. ✅ Create ad campaigns in production
   - Use production Razorpay credentials
   - Set correct Unity Game IDs
   - Configure proper frequency caps

3. ✅ Set Django environment variables
   SECRET_KEY=...
   DEBUG=False
   ALLOWED_HOSTS=...
   RAZORPAY_KEY_ID=...
   RAZORPAY_KEY_SECRET=...

4. ✅ Collect static files
   python manage.py collectstatic

5. ✅ Run tests
   python manage.py test question_solver.tests
```

### 6.2 Frontend Checklist

```bash
# Build and submit to stores:
1. ✅ Update API_BASE_URL to production
2. ✅ Set correct Unity Game IDs
3. ✅ Configure Razorpay Key ID for production
4. ✅ Test subscription flow end-to-end
5. ✅ Build for both iOS and Android
   eas build --platform ios
   eas build --platform android

6. ✅ Submit to App Store and Play Store
```

---

## PART 7: MONITORING

### 7.1 Backend Metrics

```python
# Monitor in Django admin:
- Ad impressions count
- Completion rates
- Revenue from ads (coins distributed)
- User ad preferences

# Query examples:
from question_solver.ads_models import AdImpression, AdAnalytics

# Today's ad impressions
today = timezone.now().date()
impressions = AdImpression.objects.filter(shown_at__date=today)
print(f"Ads shown today: {impressions.count()}")

# Completion rate
completed = impressions.filter(status='completed').count()
print(f"Completion rate: {completed/impressions.count()*100:.1f}%")

# Analytics
analytics = AdAnalytics.objects.filter(date=today)
for a in analytics:
    print(f"{a.campaign.name}: {a.total_impressions} impressions, {a.completion_rate:.1f}% completion")
```

### 7.2 Frontend Logging

```typescript
// Enable debug logging in development
if (__DEV__) {
  AdsManager.enableDebugLogging();
  premiumService.enableDebugLogging();
}

// Track ad events
useFeatureWithAd('quiz', {
  onAdComplete: () => console.log('✅ Ad completed'),
  onError: (error) => console.error('❌ Ad error:', error),
});
```

---

## TROUBLESHOOTING

### Problem: Ads not showing

**Solution:**
1. Check if campaign is active: `AdCampaign.is_active = True`
2. Verify schedule exists: `AdSchedule` entry for feature
3. Check user is not premium: `UserSubscription.plan == 'free'`
4. Verify frequency cap: `adsShownToday < max_ads_per_day`
5. Check ad time gap: Last ad > 5 minutes ago

### Problem: Premium users still see ads

**Solution:**
1. Check `UserAdPreference.is_premium` is True
2. Verify `UserSubscription.subscription_status == 'active'`
3. Clear cache: `premiumService.invalidateCache(userId)`
4. Refresh status: `await get().refreshStatus()`

### Problem: Rewards not being tracked

**Solution:**
1. Verify ad status is 'completed': `AdImpression.status == 'completed'`
2. Check `reward_amount` is set in impression
3. Verify `UserAdPreference.record_ad_completed()` was called

---

## SUPPORT

For issues or questions:
1. Check Django admin for ad campaigns and impressions
2. Check frontend console logs
3. Review Razorpay webhook logs
4. Check server logs for API errors

---

## Summary

✅ **Backend:**
- 5 ad models with comprehensive tracking
- 6 API endpoints for ad management
- Premium user detection
- Analytics and reporting

✅ **Frontend:**
- AdsManager for Unity Ads SDK
- Premium service with caching
- useFeatureWithAd hook for easy integration
- Zustand store for reactive state

✅ **Subscription:**
- ₹1 for 7 days trial plan
- ₹99/month recurring plan
- Automatic premium status detection
- No ads for premium users

✅ **Production Ready:**
- Error handling and logging
- Database migrations
- Admin interface
- Performance optimizations

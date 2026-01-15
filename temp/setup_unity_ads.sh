#!/bin/bash
#
# Migration and Setup Script for Unity Ads Integration
# Run this script after copying the ads files to your Django project
#

set -e

echo "================================"
echo "Unity Ads Integration Setup"
echo "================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check Django project
echo "Step 1: Verifying Django project..."
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ manage.py not found. Run this script from Django project root.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Django project found${NC}"
echo ""

# Step 2: Make migrations
echo "Step 2: Creating database migrations..."
python manage.py makemigrations question_solver
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Migrations created${NC}"
else
    echo -e "${RED}❌ Failed to create migrations${NC}"
    exit 1
fi
echo ""

# Step 3: Apply migrations
echo "Step 3: Applying migrations..."
python manage.py migrate
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Migrations applied${NC}"
else
    echo -e "${RED}❌ Failed to apply migrations${NC}"
    exit 1
fi
echo ""

# Step 4: Create sample ad campaign (optional)
echo "Step 4: Creating sample ad campaign..."
python manage.py shell << EOF
from question_solver.ads_models import AdCampaign, AdSchedule, SUBSCRIPTION_CONFIG

print("\n📝 Creating sample ad campaign...")

# Create main interstitial campaign
campaign, created = AdCampaign.objects.get_or_create(
    name='Main Interstitial Campaign',
    defaults={
        'description': 'Main interstitial ads shown after quiz completion',
        'is_active': True,
        'status': 'active',
        'unity_game_id': '6018264',
        'unity_placement_id': 'Placement_Interstitial',
        'ad_type': 'interstitial',
        'max_ads_per_day': 5,
        'min_gap_between_ads': 300,
    }
)

if created:
    print(f"✅ Campaign created: {campaign.name}")
else:
    print(f"ℹ️  Campaign already exists: {campaign.name}")

# Create schedules for all features
features = ['quiz', 'daily_quiz', 'mock_test', 'ask_question']

for feature in features:
    schedule, created = AdSchedule.objects.get_or_create(
        campaign=campaign,
        feature=feature,
        defaults={
            'show_after_feature_completion': True,
            'delay_seconds': 500,
            'probability': 1.0,
            'target_free_users_only': True,
            'is_active': True,
        }
    )
    
    if created:
        print(f"✅ Schedule created: Show ads after {feature}")
    else:
        print(f"ℹ️  Schedule already exists for {feature}")

print("\n✅ Sample campaign setup complete!")
EOF

echo -e "${GREEN}✅ Sample campaign created${NC}"
echo ""

# Step 5: Check file imports
echo "Step 5: Verifying imports..."
python -c "from question_solver.ads_models import AdCampaign, AdImpression, AdSchedule, UserAdPreference, AdAnalytics; print('✅ All models imported successfully')" 2>/dev/null || {
    echo -e "${RED}❌ Failed to import models${NC}"
    exit 1
}
echo ""

# Step 6: Display next steps
echo "================================"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "================================"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Update Django admin:"
echo "   - Add ads admin to question_solver/admin.py"
echo "   - Run: python manage.py runserver"
echo "   - Go to: http://localhost:8000/admin/question_solver/adcampaign/"
echo ""
echo "2. Configure Razorpay plans:"
echo "   - Create subscription plans in Razorpay Dashboard"
echo "   - Plan A: ₹1 for 7 days, then ₹99/month"
echo "   - Plan B: ₹99/month directly"
echo ""
echo "3. Update environment variables:"
echo "   - RAZORPAY_KEY_ID=your_key"
echo "   - RAZORPAY_KEY_SECRET=your_secret"
echo "   - API_BASE_URL=your_api_url"
echo ""
echo "4. Frontend setup:"
echo "   - Copy React Native files to your Expo project"
echo "   - Run: npm install react-native-unity-ads axios zustand"
echo "   - Configure app.json with Unity Game IDs"
echo ""
echo "5. Run tests:"
echo "   - python manage.py test question_solver"
echo ""
echo "📚 Documentation:"
echo "   - See UNITY_ADS_INTEGRATION_GUIDE.md for complete guide"
echo ""

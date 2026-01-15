#!/usr/bin/env python
"""Setup test user and configs"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
django.setup()

from django.contrib.auth.models import User
from question_solver.models import FeatureAdConfig
from rest_framework.authtoken.models import Token

# Create test user
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@example.com', 'is_staff': False}
)

# Create or get token
try:
    token = Token.objects.get(user=user)
except Token.DoesNotExist:
    token = Token.objects.create(user=user)

# Initialize feature configs
features = [
    {'feature_name': 'daily_quiz', 'feature_display_name': 'Daily Quiz', 'show_frequency': 1, 'max_ads_per_day': 10},
    {'feature_name': 'mock_test', 'feature_display_name': 'Mock Test', 'show_frequency': 2, 'max_ads_per_day': 5},
    {'feature_name': 'ask_question', 'feature_display_name': 'Ask Question', 'show_frequency': 3, 'max_ads_per_day': 5},
]

for feature in features:
    config, created = FeatureAdConfig.objects.get_or_create(
        feature_name=feature['feature_name'],
        defaults={
            'feature_display_name': feature['feature_display_name'],
            'show_frequency': feature['show_frequency'],
            'max_ads_per_day': feature['max_ads_per_day'],
            'show_ad_after_use': True,
            'ad_type': 'interstitial',
            'ios_placement_id': f"ios-{feature['feature_name']}",
            'android_placement_id': f"android-{feature['feature_name']}",
            'skip_for_premium': True,
        }
    )
    print(f"{'✅ Created' if created else '✅ Updated'}: {feature['feature_name']}")

print(f"\n✅ Test User: {user.username}")
print(f"✅ Token: {token.key}")
print(f"✅ Ready to test!")

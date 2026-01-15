#!/usr/bin/env python
"""Setup test user and configs - SIMPLIFIED"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
django.setup()

from django.contrib.auth.models import User
from question_solver.models import FeatureAdConfig
from django.db import models

# Create test user
try:
    user = User.objects.get(username='testuser')
    print(f"✅ Test user already exists: {user.username}")
except User.DoesNotExist:
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        is_staff=False
    )
    print(f"✅ Created test user: {user.username}")

# Initialize feature configs
features = [
    {'feature_name': 'daily_quiz', 'feature_display_name': 'Daily Quiz', 'show_frequency': 1, 'max_ads_per_day': 10},
    {'feature_name': 'mock_test', 'feature_display_name': 'Mock Test', 'show_frequency': 2, 'max_ads_per_day': 5},
    {'feature_name': 'ask_question', 'feature_display_name': 'Ask Question', 'show_frequency': 3, 'max_ads_per_day': 5},
    {'feature_name': 'pair_quiz', 'feature_display_name': 'Pair Quiz', 'show_frequency': 1, 'max_ads_per_day': 8},
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
    status = '✅ Created' if created else '✅ Updated'
    print(f"{status}: {feature['feature_display_name']}")

print(f"\n🎉 Setup Complete!")
print(f"📝 Test User: testuser / testpass123")

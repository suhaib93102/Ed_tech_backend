#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
django.setup()

from question_solver.models import UserSubscription
from django.utils import timezone
from datetime import timedelta

# Create test subscription
test_user = "test_duplicate_user_123"
subscription, created = UserSubscription.objects.get_or_create(
    user_id=test_user,
    defaults={
        'plan': 'premium',
        'is_trial': True,
        'subscription_status': 'active',
        'trial_end_date': timezone.now() + timedelta(days=7),
        'next_billing_date': timezone.now() + timedelta(days=7),
        'subscription_start_date': timezone.now()
    }
)
if not created:
    subscription.plan = 'premium'
    subscription.is_trial = True
    subscription.subscription_status = 'active'
    subscription.trial_end_date = timezone.now() + timedelta(days=7)
    subscription.next_billing_date = timezone.now() + timedelta(days=7)
    subscription.save()

print(f"Created/Updated subscription for {test_user}")
print(f"Plan: {subscription.plan}")
print(f"Status: {subscription.subscription_status}")
print(f"Is Trial: {subscription.is_trial}")

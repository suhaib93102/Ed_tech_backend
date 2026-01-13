# Subscription Usage Guide

## Overview
This guide covers the subscription and usage tracking features of the EdTech platform.

## Subscription Plans
The platform offers multiple subscription tiers with different features and limits.

## Usage Tracking
- Feature usage is tracked per user
- Limits are enforced based on subscription tier
- Usage statistics are available via API

## API Endpoints
- `GET /api/subscription/status/` - Get current subscription status
- `POST /api/subscription/upgrade/` - Upgrade subscription plan
- `GET /api/subscription/feature-access/` - Check feature access
- `POST /api/subscription/log-usage/` - Log feature usage

## Billing
- Automatic billing for recurring subscriptions
- Payment processing via Razorpay
- Billing history available via API
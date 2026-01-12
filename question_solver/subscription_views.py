from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from django.utils import timezone
from datetime import timedelta
import logging

from .models import UserSubscription, Payment, FeatureUsageLog

logger = logging.getLogger(__name__)


class SubscriptionStatusView(APIView):
    """
    Get user subscription status and feature limits
    GET /api/subscription/status/?user_id=<user_id>
    """
    parser_classes = [JSONParser]
    
    def get(self, request):
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response({
                'error': 'user_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            subscription, created = UserSubscription.objects.get_or_create(
                user_id=user_id,
                defaults={'plan': 'free'}
            )
            
            # Check if monthly reset is needed
            if subscription.usage_reset_date:
                days_since_reset = (timezone.now() - subscription.usage_reset_date).days
                if days_since_reset >= 30:
                    subscription.reset_monthly_usage()
            
            limits = subscription.get_feature_limits()
            
            # Format response to match specification
            usage_data = {
                'mock_tests': limits.get('mock_test', {}).get('used', 0),
                'quizzes': limits.get('quiz', {}).get('used', 0),
                'flash_cards': limits.get('flashcards', {}).get('used', 0),
                'pyqs': limits.get('pyqs', {}).get('used', 0),
                'ask_questions': limits.get('ask_question', {}).get('used', 0),
                'predicted_questions': limits.get('predicted_questions', {}).get('used', 0),
                'youtube_summarizer': limits.get('youtube_summarizer', {}).get('used', 0),
            }
            
            return Response({
                'success': True,
                'user_id': subscription.user_id,
                'plan': subscription.plan,
                'razorpay_customer_id': subscription.razorpay_customer_id or '',
                'razorpay_subscription_id': subscription.razorpay_subscription_id or '',
                'subscription_status': subscription.subscription_status,
                'current_period_end': subscription.subscription_end_date,
                'usage': usage_data,
                'feature_limits': limits,
                'auto_pay_enabled': subscription.subscription_status == 'active',
                'subscription_start_date': subscription.subscription_start_date,
                'next_billing_date': subscription.next_billing_date,
                'created': created
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting subscription status: {e}")
            return Response({
                'error': 'Failed to get subscription status',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpgradePlanView(APIView):
    """
    Upgrade user to premium plan
    POST /api/subscription/upgrade/
    """
    parser_classes = [JSONParser]
    
    def post(self, request):
        user_id = request.data.get('user_id')
        auto_pay = request.data.get('auto_pay_enabled', True)
        payment_method = request.data.get('payment_method', 'card')
        
        if not user_id:
            return Response({
                'error': 'user_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            subscription, _ = UserSubscription.objects.get_or_create(
                user_id=user_id,
                defaults={'plan': 'free'}
            )
            
            # Update subscription
            subscription.plan = 'premium'
            subscription.auto_pay_enabled = auto_pay
            subscription.payment_method = payment_method
            
            # Set billing dates
            now = timezone.now()
            subscription.subscription_start_date = now
            subscription.subscription_end_date = now + timedelta(days=30)
            subscription.next_billing_date = now + timedelta(days=30)
            
            subscription.save()
            
            logger.info(f"User {user_id} upgraded to premium with auto_pay={auto_pay}")
            
            return Response({
                'success': True,
                'message': 'Successfully upgraded to premium plan',
                'plan': subscription.plan,
                'auto_pay_enabled': subscription.auto_pay_enabled,
                'next_billing_date': subscription.next_billing_date,
                'billing_amount': '₹1.99',
                'billing_cycle': 'Monthly'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error upgrading plan: {e}")
            return Response({
                'error': 'Failed to upgrade plan',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AutoPayManagementView(APIView):
    """
    Enable/disable auto-pay for premium subscription
    POST /api/subscription/autopay/
    """
    parser_classes = [JSONParser]
    
    def post(self, request):
        user_id = request.data.get('user_id')
        enable = request.data.get('enable', True)
        
        if not user_id:
            return Response({
                'error': 'user_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            subscription = UserSubscription.objects.get(user_id=user_id)
            
            if subscription.plan != 'premium':
                return Response({
                    'error': 'Auto-pay is only available for premium plans'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            subscription.auto_pay_enabled = enable
            subscription.save()
            
            action = 'enabled' if enable else 'disabled'
            logger.info(f"Auto-pay {action} for user {user_id}")
            
            return Response({
                'success': True,
                'message': f'Auto-pay {action} successfully',
                'auto_pay_enabled': subscription.auto_pay_enabled,
                'next_billing_date': subscription.next_billing_date
            }, status=status.HTTP_200_OK)
            
        except UserSubscription.DoesNotExist:
            return Response({
                'error': 'Subscription not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error managing auto-pay: {e}")
            return Response({
                'error': 'Failed to manage auto-pay',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckFeatureAccessView(APIView):
    """
    Check if user can access a specific feature
    GET /api/subscription/feature-access/?user_id=<user_id>&feature=<feature_name>
    """
    parser_classes = [JSONParser]
    
    def get(self, request):
        user_id = request.query_params.get('user_id')
        feature = request.query_params.get('feature')
        
        if not user_id or not feature:
            return Response({
                'error': 'user_id and feature are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            subscription, created = UserSubscription.objects.get_or_create(
                user_id=user_id,
                defaults={'plan': 'free'}
            )
            
            can_access = subscription.can_use_feature(feature)
            limits = subscription.get_feature_limits()
            feature_limit = limits.get(feature, {})
            
            limit_value = feature_limit.get('limit')
            if can_access:
                message = 'Access granted'
            else:
                message = f'Limit reached ({limit_value} per month). Upgrade to premium for unlimited access.'
            
            return Response({
                'success': True,
                'can_access': can_access,
                'feature': feature,
                'plan': subscription.plan,
                'limit': feature_limit.get('limit'),
                'used': feature_limit.get('used'),
                'message': message
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error checking feature access: {e}")
            return Response({
                'error': 'Failed to check feature access',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogFeatureUsageView(APIView):
    """
    Log feature usage for tracking
    POST /api/subscription/log-usage/
    """
    parser_classes = [JSONParser]
    
    def post(self, request):
        user_id = request.data.get('user_id')
        feature_name = request.data.get('feature')
        usage_type = request.data.get('type')  # 'image', 'text', 'file'
        input_size = request.data.get('input_size', 0)
        
        if not user_id or not feature_name:
            return Response({
                'error': 'user_id and feature are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            subscription, _ = UserSubscription.objects.get_or_create(
                user_id=user_id,
                defaults={'plan': 'free'}
            )
            
            # Check access before logging
            if not subscription.can_use_feature(feature_name):
                return Response({
                    'success': False,
                    'message': 'Feature limit reached. Upgrade to premium for unlimited access.',
                    'plan': subscription.plan,
                    'upgrade_url': '/api/subscription/upgrade/'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Log usage
            subscription.increment_feature_usage(feature_name)
            
            # Create detailed log
            FeatureUsageLog.objects.create(
                subscription=subscription,
                feature_name=feature_name,
                usage_type=usage_type or 'text',
                input_size=input_size
            )
            
            logger.info(f"Logged feature usage: {feature_name} for user {user_id}")
            
            limits = subscription.get_feature_limits()
            feature_limit = limits.get(feature_name, {})
            
            return Response({
                'success': True,
                'message': 'Usage logged successfully',
                'feature': feature_name,
                'limit': feature_limit.get('limit'),
                'used': feature_limit.get('used'),
                'remaining': feature_limit.get('limit') - feature_limit.get('used') if feature_limit.get('limit') else None
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error logging feature usage: {e}")
            return Response({
                'error': 'Failed to log usage',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BillingHistoryView(APIView):
    """
    Get user's payment/billing history
    GET /api/subscription/billing-history/?user_id=<user_id>
    """
    parser_classes = [JSONParser]
    
    def get(self, request):
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response({
                'error': 'user_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            subscription = UserSubscription.objects.get(user_id=user_id)
            payments = Payment.objects.filter(subscription=subscription).order_by('-created_at')[:10]
            
            payments_data = [
                {
                    'transaction_id': p.transaction_id,
                    'amount': str(p.amount),
                    'currency': p.currency,
                    'status': p.status,
                    'payment_method': p.payment_method,
                    'billing_cycle_start': p.billing_cycle_start,
                    'billing_cycle_end': p.billing_cycle_end,
                    'created_at': p.created_at
                }
                for p in payments
            ]
            
            return Response({
                'success': True,
                'user_id': subscription.user_id,
                'plan': subscription.plan,
                'payments': payments_data,
                'total_payments': len(payments_data)
            }, status=status.HTTP_200_OK)
            
        except UserSubscription.DoesNotExist:
            return Response({
                'error': 'Subscription not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error getting billing history: {e}")
            return Response({
                'error': 'Failed to get billing history',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============= NEW SUBSCRIPTION PLAN SYSTEM (Plan A & Plan B) =============

class SubscriptionPlansView(APIView):
    """
    GET /api/subscriptions/plans/
    Returns all available subscription plans
    """
    def get(self, request):
        return Response({
            'plans': [
                {
                    'id': 'plan_a_trial',
                    'name': 'Plan A - Trial',
                    'description': 'Try premium features free for 7 days, then auto-renew at ₹99/month',
                    'currency': 'INR',
                    'initial_price': 1,
                    'recurring_price': 99,
                    'trial_days': 7,
                    'billing_cycle_days': 30,
                    'auto_renewal': True,
                    'features': [
                        'Unlimited quizzes',
                        'Unlimited flashcards',
                        'Unlimited PYQs',
                        'Unlimited predicted questions',
                        'Unlimited access to all features'
                    ]
                },
                {
                    'id': 'plan_b_monthly',
                    'name': 'Plan B - Monthly',
                    'description': 'Direct premium access for ₹99/month',
                    'currency': 'INR',
                    'price': 99,
                    'trial_days': 0,
                    'billing_cycle_days': 30,
                    'auto_renewal': True,
                    'features': [
                        'Unlimited quizzes',
                        'Unlimited flashcards',
                        'Unlimited PYQs',
                        'Unlimited predicted questions',
                        'Unlimited access to all features'
                    ]
                }
            ]
        })


class UserSubscriptionStatusView(APIView):
    """
    GET /api/subscriptions/status/?user_id=<user_id>
    Returns current subscription status and renewal info
    """
    def get(self, request):
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response({
                'error': 'user_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            subscription, created = UserSubscription.objects.get_or_create(
                user_id=user_id,
                defaults={'plan': 'free'}
            )
            
            current_plan = subscription.plan
            is_active = subscription.subscription_status == 'active'
            
            # Calculate days remaining
            days_remaining = 0
            next_renewal_date = None
            if subscription.next_billing_date:
                days_remaining = max(0, (subscription.next_billing_date - timezone.now()).days)
                next_renewal_date = subscription.next_billing_date.isoformat() if subscription.next_billing_date else None
            
            return Response({
                'user_id': user_id,
                'current_plan': current_plan,
                'is_active': is_active,
                'is_trial': subscription.is_trial,
                'period_start': subscription.subscription_start_date.isoformat(),
                'period_end': next_renewal_date,
                'days_remaining': days_remaining,
                'auto_renewal_enabled': True,  # Enabled for all plans in unlimited mode
                'features': 'Unlimited access to all features' if current_plan in ['premium', 'basic'] else 'Limited features (free plan)',
                'status': 'active' if is_active else 'inactive',
                'message': f'{days_remaining} days remaining' if is_active and days_remaining > 0 else 'Subscription expired' if current_plan != 'free' else 'On free plan'
            })
        except Exception as e:
            logger.error(f"Error getting subscription status: {e}")
            return Response({
                'error': 'Failed to get subscription status',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubscribeView(APIView):
    """
    POST /api/subscriptions/subscribe/
    Subscribe user to a plan
    """
    def post(self, request):
        user_id = request.data.get('user_id')
        plan = request.data.get('plan')  # 'plan_a_trial' or 'plan_b_monthly'
        
        if not user_id or not plan:
            return Response({
                'error': 'user_id and plan are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if plan not in ['plan_a_trial', 'plan_b_monthly']:
            return Response({
                'error': f'Invalid plan: {plan}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            subscription, created = UserSubscription.objects.get_or_create(
                user_id=user_id,
                defaults={'plan': 'free'}
            )
            
            # Determine pricing and duration
            if plan == 'plan_a_trial':
                price = 1
                trial_days = 7
                is_trial = True
            else:  # plan_b_monthly
                price = 99
                trial_days = 0
                is_trial = False
            
            # Generate Razorpay order (mocked)
            razorpay_order_id = f"order_{user_id}_{timezone.now().timestamp()}"
            
            return Response({
                'user_id': user_id,
                'plan': plan,
                'amount': price,
                'currency': 'INR',
                'razorpay_order_id': razorpay_order_id,
                'trial_days': trial_days,
                'is_trial': is_trial,
                'next_action': 'payment',
                'message': f'Proceed to payment for {plan}'
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error subscribing user: {e}")
            return Response({
                'error': 'Failed to create subscription',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InitiatePaymentView(APIView):
    """
    POST /api/subscriptions/initiate-payment/
    Initiate Razorpay payment
    """
    def post(self, request):
        user_id = request.data.get('user_id')
        razorpay_order_id = request.data.get('razorpay_order_id')
        plan = request.data.get('plan')
        
        if not user_id or not razorpay_order_id:
            return Response({
                'error': 'user_id and razorpay_order_id are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Mock Razorpay integration
            payment_details = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_key_id': 'rzp_live_XXXXX',  # Mock key
                'amount': 100 if plan == 'plan_a_trial' else 9900,  # in paise
                'currency': 'INR',
                'customer_id': user_id,
                'notes': {'plan': plan},
                'timeout': 600
            }
            
            return Response({
                'payment_details': payment_details,
                'status': 'ready_for_payment'
            })
        except Exception as e:
            logger.error(f"Error initiating payment: {e}")
            return Response({
                'error': 'Failed to initiate payment',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConfirmPaymentView(APIView):
    """
    POST /api/subscriptions/confirm-payment/
    Confirm payment and activate subscription (called by Razorpay webhook)
    """
    def post(self, request):
        user_id = request.data.get('user_id')
        plan = request.data.get('plan')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_order_id = request.data.get('razorpay_order_id')
        
        if not user_id or not plan:
            return Response({
                'error': 'user_id and plan are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            subscription, _ = UserSubscription.objects.get_or_create(
                user_id=user_id,
                defaults={'plan': 'free'}
            )
            
            # Update subscription with new plan
            subscription.plan = 'premium'
            subscription.subscription_status = 'active'
            subscription.subscription_start_date = timezone.now()
            
            # Set period end based on plan
            if plan == 'plan_a_trial':
                subscription.next_billing_date = timezone.now() + timedelta(days=7)
                subscription.trial_end_date = subscription.next_billing_date
                subscription.is_trial = True
                price = 1
            else:  # plan_b_monthly
                subscription.next_billing_date = timezone.now() + timedelta(days=30)
                subscription.is_trial = False
                price = 99
            
            subscription.last_payment_date = timezone.now()
            subscription.save()
            
            # Create payment record using correct field names
            Payment.objects.create(
                subscription=subscription,
                amount=price,
                currency='INR',
                status='completed',
                payment_method='razorpay',
                transaction_id=razorpay_payment_id or f'test_payment_{subscription.id}',
                razorpay_payment_id=razorpay_payment_id or 'test_payment',
                razorpay_order_id=razorpay_order_id or 'test_order',
                billing_cycle_start=timezone.now(),
                billing_cycle_end=subscription.next_billing_date
            )
            
            return Response({
                'status': 'success',
                'user_id': user_id,
                'plan': plan,
                'message': 'Subscription activated successfully',
                'subscription_details': {
                    'plan': subscription.plan,
                    'is_trial': subscription.is_trial,
                    'period_start': subscription.subscription_start_date.isoformat(),
                    'period_end': subscription.next_billing_date.isoformat(),
                    'auto_renewal': True
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error confirming payment: {e}")
            return Response({
                'error': 'Failed to confirm payment',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CancelSubscriptionView(APIView):
    """
    POST /api/subscriptions/cancel/
    Cancel subscription and downgrade to free plan
    """
    def post(self, request):
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({
                'error': 'user_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            subscription, _ = UserSubscription.objects.get_or_create(
                user_id=user_id,
                defaults={'plan': 'free'}
            )
            
            # Downgrade to free
            subscription.plan = 'free'
            subscription.subscription_status = 'cancelled'
            subscription.subscription_end_date = timezone.now()
            subscription.save()
            
            # Reset all usage quotas
            subscription.mock_test_used = 0
            subscription.quiz_used = 0
            subscription.flashcards_used = 0
            subscription.ask_question_used = 0
            subscription.predicted_questions_used = 0
            subscription.youtube_summarizer_used = 0
            subscription.pyqs_used = 0
            subscription.pair_quiz_used = 0
            subscription.previous_papers_used = 0
            subscription.daily_quiz_used = 0
            subscription.usage_reset_date = timezone.now()
            subscription.save()
            
            return Response({
                'status': 'success',
                'message': 'Subscription cancelled. Downgraded to free plan.',
                'plan': 'free'
            })
        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}")
            return Response({
                'error': 'Failed to cancel subscription',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# ============= USAGE QUOTA VIEW (COMMENTED OUT - NOT NEEDED FOR UNLIMITED PLANS) =============
# class UsageQuotaView(APIView):
#     """
#     GET /api/subscriptions/quotas/?user_id=<user_id>
#     Get user's monthly usage quotas
#     """
#     def get(self, request):
#         user_id = request.query_params.get('user_id')
#         
#         if not user_id:
#             return Response({
#                 'error': 'user_id is required'
#             }, status=status.HTTP_400_BAD_REQUEST)
#         
#         try:
#             subscription, _ = UserSubscription.objects.get_or_create(
#                 user_id=user_id,
#                 defaults={'plan': 'free'}
#             )
#             
#             limits = subscription.get_feature_limits()
#             
#             return Response({
#                 'user_id': user_id,
#                 'plan': subscription.plan,
#                 'quotas': {
#                     'quizzes': limits.get('quiz', {}),
#                     'flashcards': limits.get('flashcards', {}),
#                     'pyqs': limits.get('pyqs', {}),
#                     'predicted_questions': limits.get('predicted_questions', {}),
#                     'ask_questions': limits.get('ask_question', {})
#                 },
#                 'reset_date': subscription.usage_reset_date.isoformat() if subscription.usage_reset_date else None
#             })
#         except Exception as e:
#             logger.error(f"Error getting quotas: {e}")
#             return Response({
#                 'error': 'Failed to get quotas',
#                 'details': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

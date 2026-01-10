"""
Usage Dashboard API Views
Endpoints for user to track feature usage and plan limits
"""
import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .feature_usage_service import FeatureUsageService
from .decorators import require_auth

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
@require_auth
def usage_dashboard(request):
    """
    Get user's usage dashboard
    GET /api/usage/dashboard/
    Returns: Feature usage, limits, billing info
    """
    try:
        user_id = request.user_id
        
        dashboard = FeatureUsageService.get_usage_dashboard(user_id)
        
        return JsonResponse({
            'success': True,
            'dashboard': dashboard,
        })
    
    except Exception as e:
        logger.exception(f"[USAGE_DASHBOARD] ERROR: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@require_http_methods(["GET"])
@require_auth
def feature_status(request, feature_name):
    """
    Check status of a specific feature
    GET /api/usage/feature/<feature_name>/
    Returns: Can use, limit, usage, remaining
    """
    try:
        user_id = request.user_id
        
        status = FeatureUsageService.check_feature_available(user_id, feature_name)
        
        return JsonResponse({
            'success': True,
            'feature': feature_name,
            'status': status,
        })
    
    except Exception as e:
        logger.exception(f"[FEATURE_STATUS] ERROR: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
@require_auth
def check_feature_usage(request):
    """
    Check if user can use a feature before making the actual request
    POST /api/usage/check/
    Body: {"feature": "quiz", "extra_info": {...}}
    """
    try:
        user_id = request.user_id
        data = json.loads(request.body)
        feature_name = data.get('feature')
        
        if not feature_name:
            return JsonResponse({
                'success': False,
                'error': 'feature name is required',
            }, status=400)
        
        status = FeatureUsageService.check_feature_available(user_id, feature_name)
        
        if not status['allowed']:
            return JsonResponse({
                'success': False,
                'error': status['reason'],
                'status': status,
            }, status=403)
        
        return JsonResponse({
            'success': True,
            'message': 'Feature available',
            'status': status,
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON',
        }, status=400)
    except Exception as e:
        logger.exception(f"[CHECK_FEATURE_USAGE] ERROR: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
@require_auth
def record_feature_usage(request):
    """
    Record feature usage after successful usage
    POST /api/usage/record/
    Body: {"feature": "quiz", "input_size": 1000, "usage_type": "text"}
    """
    try:
        user_id = request.user_id
        data = json.loads(request.body)
        
        feature_name = data.get('feature')
        input_size = data.get('input_size', 0)
        usage_type = data.get('usage_type', 'default')
        
        if not feature_name:
            return JsonResponse({
                'success': False,
                'error': 'feature name is required',
            }, status=400)
        
        result = FeatureUsageService.use_feature(
            user_id=user_id,
            feature_name=feature_name,
            input_size=input_size,
            usage_type=usage_type,
        )
        
        return JsonResponse(result)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON',
        }, status=400)
    except Exception as e:
        logger.exception(f"[RECORD_FEATURE_USAGE] ERROR: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@require_http_methods(["GET"])
@require_auth
def subscription_status(request):
    """
    Get user's subscription status
    GET /api/usage/subscription/
    """
    try:
        user_id = request.user_id
        subscription = FeatureUsageService.get_or_create_subscription(user_id)
        is_active = FeatureUsageService.check_subscription_active(user_id)
        
        return JsonResponse({
            'success': True,
            'subscription': {
                'id': str(subscription.id),
                'plan': subscription.plan.upper(),
                'is_active': is_active,
                'status': subscription.subscription_status,
                'is_trial': subscription.is_trial,
                'trial_end_date': subscription.trial_end_date.isoformat() if subscription.trial_end_date else None,
                'subscription_start_date': subscription.subscription_start_date.isoformat(),
                'next_billing_date': subscription.next_billing_date.isoformat() if subscription.next_billing_date else None,
                'last_payment_date': subscription.last_payment_date.isoformat() if subscription.last_payment_date else None,
            }
        })
    
    except Exception as e:
        logger.exception(f"[SUBSCRIPTION_STATUS] ERROR: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@require_http_methods(["GET"])
@require_auth
def usage_stats(request):
    """
    Get usage statistics and trends
    GET /api/usage/stats/
    """
    try:
        user_id = request.user_id
        stats = FeatureUsageService.get_usage_stats(user_id)
        
        return JsonResponse({
            'success': True,
            'stats': stats,
        })
    
    except Exception as e:
        logger.exception(f"[USAGE_STATS] ERROR: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)

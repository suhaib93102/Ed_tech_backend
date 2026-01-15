"""
Django Admin Configuration for Ads System
Add this to question_solver/admin.py
"""

from django.contrib import admin
from django.utils.html import format_html
from .ads_models import (
    AdCampaign, AdImpression, AdSchedule, 
    UserAdPreference, AdAnalytics
)


@admin.register(AdCampaign)
class AdCampaignAdmin(admin.ModelAdmin):
    """Admin interface for managing ad campaigns"""
    
    list_display = (
        'name',
        'ad_type',
        'unity_game_id',
        'max_ads_per_day',
        'status_badge',
        'created_at'
    )
    list_filter = ('is_active', 'status', 'ad_type', 'created_at')
    search_fields = ('name', 'unity_game_id', 'unity_placement_id')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Campaign Info', {
            'fields': ('id', 'name', 'description', 'status', 'is_active')
        }),
        ('Unity Ads Configuration', {
            'fields': ('unity_game_id', 'unity_placement_id', 'ad_type')
        }),
        ('Frequency Settings', {
            'fields': ('max_ads_per_day', 'min_gap_between_ads')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'active': '#28a745',
            'paused': '#ffc107',
            'completed': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.status.upper()
        )
    status_badge.short_description = 'Status'


@admin.register(AdImpression)
class AdImpressionAdmin(admin.ModelAdmin):
    """Admin interface for viewing ad impressions"""
    
    list_display = (
        'user_id',
        'campaign_name',
        'feature_used',
        'status_indicator',
        'shown_at',
        'duration_seconds'
    )
    list_filter = (
        'status',
        'platform',
        'feature_used',
        'shown_at',
        'is_rewarded_completed'
    )
    search_fields = ('user_id', 'campaign__name', 'device_id')
    readonly_fields = (
        'id',
        'shown_at',
        'completed_at',
        'created_at',
        'updated_at'
    )
    
    fieldsets = (
        ('User & Campaign', {
            'fields': ('id', 'user_id', 'campaign', 'device_id')
        }),
        ('Device Info', {
            'fields': ('platform', 'app_version')
        }),
        ('Ad Details', {
            'fields': (
                'feature_used',
                'status',
                'duration_seconds',
                'is_rewarded_completed',
                'reward_amount',
                'reward_claimed'
            )
        }),
        ('Timing', {
            'fields': ('shown_at', 'completed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def campaign_name(self, obj):
        return obj.campaign.name
    campaign_name.short_description = 'Campaign'
    
    def status_indicator(self, obj):
        """Display status with color coding"""
        colors = {
            'shown': '#17a2b8',
            'clicked': '#007bff',
            'completed': '#28a745',
            'skipped': '#ffc107',
            'failed': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.status.upper()
        )
    status_indicator.short_description = 'Status'
    
    def has_add_permission(self, request):
        """Prevent manual creation of impressions"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of impressions (audit trail)"""
        return False


@admin.register(AdSchedule)
class AdScheduleAdmin(admin.ModelAdmin):
    """Admin interface for managing ad schedules"""
    
    list_display = (
        'campaign',
        'feature',
        'probability_percentage',
        'target_info',
        'is_active',
        'updated_at'
    )
    list_filter = ('is_active', 'feature', 'target_free_users_only', 'campaign')
    search_fields = ('campaign__name', 'feature')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Campaign & Feature', {
            'fields': ('id', 'campaign', 'feature')
        }),
        ('Trigger Configuration', {
            'fields': (
                'show_after_feature_completion',
                'delay_seconds',
                'probability'
            )
        }),
        ('Targeting', {
            'fields': ('target_free_users_only', 'is_active')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def probability_percentage(self, obj):
        """Display probability as percentage"""
        percentage = int(obj.probability * 100)
        return f"{percentage}%"
    probability_percentage.short_description = 'Probability'
    
    def target_info(self, obj):
        """Display targeting info"""
        return "Free Users Only" if obj.target_free_users_only else "All Users"
    target_info.short_description = 'Target'


@admin.register(UserAdPreference)
class UserAdPreferenceAdmin(admin.ModelAdmin):
    """Admin interface for user ad preferences"""
    
    list_display = (
        'user_id',
        'ads_enabled_indicator',
        'premium_indicator',
        'ads_shown_today',
        'total_ads_shown',
        'total_rewards_earned'
    )
    list_filter = (
        'ads_enabled',
        'ads_opted_in',
        'is_premium',
        'created_at'
    )
    search_fields = ('user_id',)
    readonly_fields = (
        'id',
        'total_ads_shown',
        'total_ads_completed',
        'total_rewards_earned',
        'created_at',
        'updated_at'
    )
    
    fieldsets = (
        ('User', {
            'fields': ('id', 'user_id', 'is_premium')
        }),
        ('Ad Preferences', {
            'fields': ('ads_enabled', 'ads_opted_in')
        }),
        ('Daily Stats', {
            'fields': ('ads_shown_today', 'last_ad_shown_at', 'ads_shown_last_reset')
        }),
        ('All-Time Stats', {
            'fields': (
                'total_ads_shown',
                'total_ads_completed',
                'total_rewards_earned'
            )
        }),
        ('Blocked Campaigns', {
            'fields': ('blocked_campaign_ids',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def ads_enabled_indicator(self, obj):
        """Display enabled status"""
        icon = '✅' if obj.ads_enabled else '❌'
        return f"{icon} {'Enabled' if obj.ads_enabled else 'Disabled'}"
    ads_enabled_indicator.short_description = 'Ads Enabled'
    
    def premium_indicator(self, obj):
        """Display premium status"""
        icon = '👑' if obj.is_premium else '🆓'
        return f"{icon} {'Premium' if obj.is_premium else 'Free'}"
    premium_indicator.short_description = 'Status'


@admin.register(AdAnalytics)
class AdAnalyticsAdmin(admin.ModelAdmin):
    """Admin interface for ad analytics"""
    
    list_display = (
        'campaign_name',
        'date',
        'total_impressions',
        'ctr_display',
        'completion_rate_display',
        'total_rewards_distributed'
    )
    list_filter = ('date', 'campaign')
    search_fields = ('campaign__name',)
    readonly_fields = (
        'id',
        'total_impressions',
        'total_clicks',
        'total_completed',
        'total_skipped',
        'total_failed',
        'click_through_rate',
        'completion_rate',
        'total_rewards_distributed',
        'updated_at'
    )
    
    fieldsets = (
        ('Campaign & Date', {
            'fields': ('id', 'campaign', 'date')
        }),
        ('Impressions', {
            'fields': (
                'total_impressions',
                'total_clicks',
                'total_completed',
                'total_skipped',
                'total_failed'
            )
        }),
        ('Rates', {
            'fields': ('click_through_rate', 'completion_rate')
        }),
        ('Rewards', {
            'fields': ('total_rewards_distributed',)
        }),
        ('Dates', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    
    def campaign_name(self, obj):
        return obj.campaign.name
    campaign_name.short_description = 'Campaign'
    
    def ctr_display(self, obj):
        """Display CTR as percentage"""
        return f"{obj.click_through_rate:.2f}%"
    ctr_display.short_description = 'CTR'
    
    def completion_rate_display(self, obj):
        """Display completion rate with color"""
        rate = obj.completion_rate
        if rate >= 50:
            color = '#28a745'  # Green
        elif rate >= 30:
            color = '#ffc107'  # Yellow
        else:
            color = '#dc3545'  # Red
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}%</span>',
            color,
            rate
        )
    completion_rate_display.short_description = 'Completion Rate'
    
    def has_add_permission(self, request):
        """Prevent manual creation of analytics"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of analytics"""
        return False


# Customize Django admin site
admin.site.site_header = "EdTech - Ad Management System"
admin.site.site_title = "Ad Management"
admin.site.index_title = "Welcome to Ad Management Dashboard"

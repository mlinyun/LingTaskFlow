from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile, LoginHistory


class UserProfileInline(admin.StackedInline):
    """用户档案内联管理"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = '用户档案'
    fields = (
        'avatar', 'timezone', 'theme_preference', 
        'email_notifications', 'task_count', 'completed_task_count'
    )
    readonly_fields = ('task_count', 'completed_task_count')


class UserAdmin(BaseUserAdmin):
    """扩展的用户管理"""
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """用户档案管理"""
    list_display = (
        'user', 'timezone', 'theme_preference', 
        'task_count', 'completed_task_count', 'completion_rate',
        'email_notifications', 'created_at'
    )
    list_filter = ('timezone', 'theme_preference', 'email_notifications', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('task_count', 'completed_task_count', 'completion_rate', 'created_at', 'updated_at')
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'avatar', 'timezone')
        }),
        ('偏好设置', {
            'fields': ('theme_preference', 'email_notifications')
        }),
        ('任务统计', {
            'fields': ('task_count', 'completed_task_count', 'completion_rate'),
            'classes': ('collapse',)
        }),
        ('时间记录', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def completion_rate(self, obj):
        """显示完成率"""
        return f"{obj.completion_rate}%"
    completion_rate.short_description = '完成率'


# 重新注册User模型以包含UserProfile内联
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    """登录历史管理"""
    list_display = (
        'username_attempted', 'user', 'status', 'ip_address', 
        'location', 'login_time', 'is_suspicious'
    )
    list_filter = (
        'status', 'login_time', 'location'
    )
    search_fields = (
        'username_attempted', 'user__username', 'user__email', 
        'ip_address', 'user_agent'
    )
    readonly_fields = (
        'username_attempted', 'user', 'status', 'ip_address', 
        'user_agent', 'device_fingerprint', 'location', 
        'login_time', 'failure_reason'
    )
    date_hierarchy = 'login_time'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'username_attempted', 'status', 'login_time')
        }),
        ('网络信息', {
            'fields': ('ip_address', 'location', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('设备信息', {
            'fields': ('device_fingerprint',),
            'classes': ('collapse',)
        }),
        ('其他信息', {
            'fields': ('failure_reason', 'session_duration'),
            'classes': ('collapse',)
        }),
    )

    def is_suspicious(self, obj):
        """显示是否为可疑登录"""
        return obj.is_suspicious
    is_suspicious.boolean = True
    is_suspicious.short_description = '可疑登录'

    def has_add_permission(self, request):
        """禁止手动添加登录历史"""
        return False

    def has_change_permission(self, request, obj=None):
        """禁止修改登录历史"""
        return False

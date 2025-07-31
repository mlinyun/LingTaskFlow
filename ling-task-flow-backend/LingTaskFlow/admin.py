from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile


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

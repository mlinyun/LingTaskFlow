from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html

from .models import UserProfile, LoginHistory, Task


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


class TaskInline(admin.TabularInline):
    """任务内联显示"""
    model = Task
    fk_name = 'owner'  # 指定使用owner外键
    fields = ('title', 'status', 'priority', 'due_date', 'progress')
    readonly_fields = ('created_at',)
    extra = 0
    max_num = 5

    def get_queryset(self, request):
        """只显示未删除的任务"""
        return super().get_queryset(request).filter(is_deleted=False)


class UserAdmin(BaseUserAdmin):
    """扩展的用户管理"""
    inlines = (UserProfileInline, TaskInline)
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


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """任务管理"""
    list_display = (
        'title', 'owner', 'assigned_to', 'status_colored', 'priority_colored',
        'progress_bar', 'due_date', 'is_overdue', 'created_at', 'is_deleted'
    )
    list_filter = (
        'status', 'priority', 'category', 'is_deleted',
        'created_at', 'due_date', 'owner'
    )
    search_fields = ('title', 'description', 'tags', 'notes', 'owner__username')
    readonly_fields = (
        'id', 'created_at', 'updated_at', 'completed_at',
        'is_overdue', 'time_remaining'
    )
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'description', 'owner', 'assigned_to')
        }),
        ('状态与优先级', {
            'fields': ('status', 'priority', 'progress')
        }),
        ('时间管理', {
            'fields': ('start_date', 'due_date', 'completed_at', 'estimated_hours', 'actual_hours'),
            'classes': ('collapse',)
        }),
        ('分类与标签', {
            'fields': ('category', 'tags'),
            'classes': ('collapse',)
        }),
        ('附件与备注', {
            'fields': ('attachment', 'notes'),
            'classes': ('collapse',)
        }),
        ('系统信息', {
            'fields': ('id', 'created_at', 'updated_at', 'order', 'is_deleted', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    # 过滤器
    list_per_page = 20
    actions = ['mark_as_completed', 'mark_as_pending', 'soft_delete_tasks', 'restore_tasks']

    def get_queryset(self, request):
        """包含软删除的记录"""
        return Task.all_objects.all()

    def status_colored(self, obj):
        """带颜色的状态显示"""
        color = obj.get_status_color()
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )

    status_colored.short_description = '状态'

    def priority_colored(self, obj):
        """带颜色的优先级显示"""
        color = obj.get_priority_color()
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display()
        )

    priority_colored.short_description = '优先级'

    def progress_bar(self, obj):
        """进度条显示"""
        progress = obj.progress
        color = '#28a745' if progress >= 100 else '#007bff' if progress >= 50 else '#ffc107'
        return format_html(
            '<div style="width: 100px; background-color: #e9ecef; border-radius: 4px;">'
            '<div style="width: {}%; background-color: {}; height: 20px; border-radius: 4px; '
            'text-align: center; line-height: 20px; color: white; font-size: 12px;">{}</div></div>',
            progress, color, f'{progress}%'
        )

    progress_bar.short_description = '进度'

    def is_overdue(self, obj):
        """是否过期"""
        return obj.is_overdue

    is_overdue.boolean = True
    is_overdue.short_description = '已过期'

    def time_remaining(self, obj):
        """剩余时间"""
        remaining = obj.time_remaining
        if remaining:
            days = remaining.days
            hours = remaining.seconds // 3600
            return f"{days}天{hours}小时"
        return "无"

    time_remaining.short_description = '剩余时间'

    # 批量操作
    def mark_as_completed(self, request, queryset):
        """标记为已完成"""
        updated = queryset.update(status='COMPLETED', progress=100)
        self.message_user(request, f"已将 {updated} 个任务标记为完成。")

    mark_as_completed.short_description = "标记选中任务为已完成"

    def mark_as_pending(self, request, queryset):
        """标记为待处理"""
        updated = queryset.update(status='PENDING')
        self.message_user(request, f"已将 {updated} 个任务标记为待处理。")

    mark_as_pending.short_description = "标记选中任务为待处理"

    def soft_delete_tasks(self, request, queryset):
        """软删除任务"""
        count = 0
        for task in queryset:
            if not task.is_deleted:
                task.soft_delete()
                count += 1
        self.message_user(request, f"已软删除 {count} 个任务。")

    soft_delete_tasks.short_description = "软删除选中任务"

    def restore_tasks(self, request, queryset):
        """恢复任务"""
        count = 0
        for task in queryset:
            if task.is_deleted:
                task.restore()
                count += 1
        self.message_user(request, f"已恢复 {count} 个任务。")

    restore_tasks.short_description = "恢复选中任务"

"""
LingTaskFlow 数据模型
定义用户扩展信息和任务管理相关的数据模型
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import uuid


class UserProfile(models.Model):
    """
    用户扩展模型
    为Django内置User模型提供额外的字段信息
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='关联用户'
    )
    
    # 用户个人信息
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        null=True,
        blank=True,
        verbose_name='头像',
        help_text='用户头像图片'
    )
    
    timezone = models.CharField(
        max_length=50,
        default='Asia/Shanghai',
        verbose_name='时区',
        help_text='用户所在时区'
    )
    
    # 统计信息
    task_count = models.PositiveIntegerField(
        default=0,
        verbose_name='任务总数',
        help_text='用户创建的任务总数量'
    )
    
    completed_task_count = models.PositiveIntegerField(
        default=0,
        verbose_name='已完成任务数',
        help_text='用户已完成的任务数量'
    )
    
    # 个人偏好设置
    theme_preference = models.CharField(
        max_length=20,
        choices=[
            ('light', '浅色主题'),
            ('dark', '深色主题'),
            ('auto', '跟随系统'),
        ],
        default='auto',
        verbose_name='主题偏好',
        help_text='用户界面主题偏好'
    )
    
    email_notifications = models.BooleanField(
        default=True,
        verbose_name='邮件通知',
        help_text='是否接收邮件通知'
    )
    
    # 时间戳
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        db_table = 'user_profiles'
        verbose_name = '用户扩展信息'
        verbose_name_plural = '用户扩展信息'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} 的扩展信息"

    def update_task_count(self):
        """更新任务统计数量"""
        # 这个方法将在Task模型创建后实现
        # self.task_count = self.user.tasks.filter(is_deleted=False).count()
        # self.completed_task_count = self.user.tasks.filter(
        #     is_deleted=False, 
        #     status='COMPLETED'
        # ).count()
        # self.save(update_fields=['task_count', 'completed_task_count'])
        pass

    @property
    def completion_rate(self):
        """计算任务完成率"""
        if self.task_count == 0:
            return 0
        return round((self.completed_task_count / self.task_count) * 100, 2)

    def get_avatar_url(self):
        """获取头像URL"""
        if self.avatar:
            return self.avatar.url
        return None


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    用户创建时自动创建UserProfile
    信号处理器，确保每个用户都有对应的扩展信息
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    用户保存时自动保存UserProfile
    确保UserProfile与User保持同步
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # 如果没有profile，创建一个
        UserProfile.objects.create(user=instance)


class LoginHistory(models.Model):
    """
    用户登录历史模型
    记录用户的登录活动，用于安全监控和分析
    """
    LOGIN_STATUS_CHOICES = [
        ('success', '成功'),
        ('failed', '失败'),
        ('locked', '账户锁定'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_history',
        verbose_name='用户',
        null=True,
        blank=True
    )
    
    username_attempted = models.CharField(
        max_length=150,
        verbose_name='尝试的用户名',
        help_text='记录登录尝试时使用的用户名或邮箱'
    )
    
    status = models.CharField(
        max_length=10,
        choices=LOGIN_STATUS_CHOICES,
        verbose_name='登录状态'
    )
    
    ip_address = models.GenericIPAddressField(
        verbose_name='IP地址',
        help_text='用户登录时的IP地址'
    )
    
    user_agent = models.TextField(
        verbose_name='用户代理',
        help_text='浏览器和设备信息'
    )
    
    device_fingerprint = models.CharField(
        max_length=64,
        verbose_name='设备指纹',
        help_text='基于多个因素生成的设备唯一标识',
        null=True,
        blank=True
    )
    
    location = models.CharField(
        max_length=255,
        verbose_name='地理位置',
        null=True,
        blank=True,
        help_text='基于IP地址的大致地理位置'
    )
    
    login_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='登录时间'
    )
    
    session_duration = models.DurationField(
        null=True,
        blank=True,
        verbose_name='会话持续时间',
        help_text='从登录到登出的时间长度'
    )
    
    failure_reason = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='失败原因',
        help_text='登录失败时的具体原因'
    )

    class Meta:
        verbose_name = '登录历史'
        verbose_name_plural = '登录历史记录'
        ordering = ['-login_time']
        indexes = [
            models.Index(fields=['user', '-login_time']),
            models.Index(fields=['ip_address', '-login_time']),
            models.Index(fields=['status', '-login_time']),
        ]

    def __str__(self):
        return f"{self.username_attempted} - {self.get_status_display()} - {self.login_time}"

    @property
    def is_suspicious(self):
        """
        判断是否为可疑登录
        基于多个因素判断登录活动是否异常
        """
        # 检查是否来自新设备
        if self.user and self.device_fingerprint:
            recent_logins = LoginHistory.objects.filter(
                user=self.user,
                status='success',
                login_time__gte=timezone.now() - timezone.timedelta(days=30)
            ).exclude(id=self.id)
            
            known_devices = recent_logins.values_list('device_fingerprint', flat=True)
            if self.device_fingerprint not in known_devices:
                return True
        
        return False

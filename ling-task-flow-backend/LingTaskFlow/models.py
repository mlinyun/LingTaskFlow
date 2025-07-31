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

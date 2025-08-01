"""
LingTaskFlow 数据模型
定义用户扩展信息和任务管理相关的数据模型
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
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
        indexes = [
            # 用户查询索引
            models.Index(fields=['user'], name='userprof_user_idx'),
            # 时间相关索引
            models.Index(fields=['-created_at'], name='userprof_created_idx'),
            models.Index(fields=['-updated_at'], name='userprof_updated_idx'),
            # 统计相关索引
            models.Index(fields=['task_count'], name='userprof_task_cnt_idx'),
            models.Index(fields=['completed_task_count'], name='userprof_comp_cnt_idx'),
            # 主题偏好索引
            models.Index(fields=['theme_preference'], name='userprof_theme_idx'),
            # 通知设置索引
            models.Index(fields=['email_notifications'], name='userprof_email_idx'),
        ]

    def __str__(self):
        return f"{self.user.username} 的扩展信息"

    def update_task_count(self):
        """更新任务统计数量"""
        self.task_count = self.user.owned_tasks.filter(is_deleted=False).count()
        self.completed_task_count = self.user.owned_tasks.filter(
            is_deleted=False, 
            status='COMPLETED'
        ).count()
        self.save(update_fields=['task_count', 'completed_task_count'])

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
            # 现有索引（优化命名）
            models.Index(fields=['user', '-login_time'], name='login_user_time_idx'),
            models.Index(fields=['ip_address', '-login_time'], name='login_ip_time_idx'),
            models.Index(fields=['status', '-login_time'], name='login_status_time_idx'),
            
            # 新增安全相关索引
            models.Index(fields=['username_attempted'], name='login_username_idx'),
            models.Index(fields=['device_fingerprint'], name='login_device_idx'),
            models.Index(fields=['location'], name='login_location_idx'),
            
            # 复合查询索引
            models.Index(fields=['user', 'status', '-login_time'], name='login_usr_stat_time_idx'),
            models.Index(fields=['ip_address', 'status'], name='login_ip_status_idx'),
            models.Index(fields=['status', 'failure_reason'], name='login_stat_reason_idx'),
            
            # 时间范围查询索引
            models.Index(fields=['-login_time', 'status'], name='login_time_stat_idx'),
            
            # 会话相关索引
            models.Index(fields=['session_duration'], name='login_session_idx'),
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


class SoftDeleteQuerySet(models.QuerySet):
    """
    软删除查询集
    提供更强大的软删除查询功能
    """
    def active(self):
        """返回未删除的记录"""
        return self.filter(is_deleted=False)
    
    def deleted(self):
        """返回已删除的记录"""
        return self.filter(is_deleted=True)
    
    def soft_delete(self):
        """批量软删除"""
        return self.update(is_deleted=True, deleted_at=timezone.now())
    
    def restore(self):
        """批量恢复"""
        return self.update(is_deleted=False, deleted_at=None)
    
    def hard_delete(self):
        """批量硬删除（永久删除）"""
        return self.delete()
    
    def deleted_before(self, date):
        """返回指定日期之前删除的记录"""
        return self.filter(is_deleted=True, deleted_at__lt=date)
    
    def deleted_after(self, date):
        """返回指定日期之后删除的记录"""
        return self.filter(is_deleted=True, deleted_at__gt=date)
    
    def deleted_between(self, start_date, end_date):
        """返回指定时间范围内删除的记录"""
        return self.filter(
            is_deleted=True,
            deleted_at__gte=start_date,
            deleted_at__lte=end_date
        )


class SoftDeleteManager(models.Manager):
    """
    软删除管理器
    用于处理软删除的查询集，默认排除已删除的记录
    """
    def get_queryset(self):
        """返回使用软删除查询集的未删除记录"""
        return SoftDeleteQuerySet(self.model, using=self._db).active()
    
    def all_with_deleted(self):
        """返回包含已删除记录的所有记录"""
        return SoftDeleteQuerySet(self.model, using=self._db)
    
    def deleted_only(self):
        """仅返回已删除的记录"""
        return SoftDeleteQuerySet(self.model, using=self._db).deleted()
    
    def soft_delete_queryset(self):
        """返回软删除查询集"""
        return SoftDeleteQuerySet(self.model, using=self._db)


class SoftDeleteModel(models.Model):
    """
    软删除基础模型
    提供全面软删除功能的抽象基类
    """
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='是否删除',
        help_text='软删除标记，True表示已删除'
    )
    
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='删除时间',
        help_text='记录删除时间'
    )
    
    deleted_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted_set',
        verbose_name='删除者',
        help_text='执行删除操作的用户'
    )
    
    # 默认管理器（排除已删除的记录）
    objects = SoftDeleteManager()
    # 包含所有记录的管理器
    all_objects = models.Manager()
    
    class Meta:
        abstract = True
    
    def soft_delete(self, user=None):
        """
        软删除
        
        Args:
            user: 执行删除操作的用户
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])
    
    def restore(self, user=None):
        """
        恢复删除
        
        Args:
            user: 执行恢复操作的用户（可用于记录日志）
        """
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])
    
    def hard_delete(self):
        """硬删除（永久删除）"""
        super().delete()
    
    def delete(self, using=None, keep_parents=False):
        """
        重写delete方法，默认执行软删除
        要执行硬删除，请使用hard_delete()方法
        """
        self.soft_delete()
    
    @property
    def is_permanently_deleted(self):
        """检查是否已永久删除（硬删除）"""
        try:
            # 尝试访问主键，如果对象已被硬删除，会抛出异常
            return not bool(self.pk)
        except:
            return True
    
    @property
    def deletion_age(self):
        """计算删除后的时间（天数）"""
        if not self.is_deleted or not self.deleted_at:
            return None
        return (timezone.now() - self.deleted_at).days
    
    @property
    def can_be_restored(self):
        """检查是否可以被恢复"""
        return self.is_deleted and self.deleted_at is not None
    
    def get_deletion_info(self):
        """获取删除信息"""
        if not self.is_deleted:
            return None
        
        return {
            'is_deleted': True,
            'deleted_at': self.deleted_at,
            'deleted_by': self.deleted_by,
            'deletion_age_days': self.deletion_age,
            'can_be_restored': self.can_be_restored
        }


class Task(SoftDeleteModel):
    """
    任务模型
    核心任务管理功能的数据模型，包含软删除功能
    """
    
    # 任务状态选择
    STATUS_CHOICES = [
        ('PENDING', '待处理'),
        ('IN_PROGRESS', '进行中'),
        ('COMPLETED', '已完成'),
        ('CANCELLED', '已取消'),
        ('ON_HOLD', '暂停'),
    ]
    
    # 优先级选择
    PRIORITY_CHOICES = [
        ('LOW', '低'),
        ('MEDIUM', '中'),
        ('HIGH', '高'),
        ('URGENT', '紧急'),
    ]
    
    # 基础字段
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='任务ID'
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name='任务标题',
        help_text='任务的简短描述'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='任务描述',
        help_text='任务的详细说明'
    )
    
    # 关联用户
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_tasks',
        verbose_name='任务所有者'
    )
    
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='assigned_tasks',
        null=True,
        blank=True,
        verbose_name='任务执行者',
        help_text='分配给谁执行这个任务'
    )
    
    # 任务状态和优先级
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name='任务状态'
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM',
        verbose_name='优先级'
    )
    
    # 时间相关字段
    due_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='截止时间',
        help_text='任务需要完成的时间'
    )
    
    start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='开始时间',
        help_text='任务计划开始的时间'
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='完成时间',
        help_text='任务实际完成的时间'
    )
    
    # 进度相关
    progress = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='完成进度',
        help_text='任务完成百分比 (0-100)'
    )
    
    estimated_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='预估工时',
        help_text='预计完成任务需要的小时数'
    )
    
    actual_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='实际工时',
        help_text='实际花费的小时数'
    )
    
    # 分类和标签
    category = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='任务分类',
        help_text='任务所属的分类'
    )
    
    tags = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='标签',
        help_text='用逗号分隔的标签列表'
    )
    
    # 附件和备注
    attachment = models.FileField(
        upload_to='task_attachments/%Y/%m/',
        null=True,
        blank=True,
        verbose_name='附件',
        help_text='任务相关的文件附件'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='备注',
        help_text='任务的额外备注信息'
    )
    
    # 系统字段
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    # 排序字段
    order = models.IntegerField(
        default=0,
        verbose_name='排序',
        help_text='用于任务排序的数值'
    )
    
    class Meta:
        db_table = 'tasks'
        verbose_name = '任务'
        verbose_name_plural = '任务'
        ordering = ['-created_at', 'order']
        indexes = [
            # 基础单字段索引
            models.Index(fields=['due_date'], name='task_due_date_idx'),
            models.Index(fields=['category'], name='task_category_idx'),
            models.Index(fields=['status'], name='task_status_idx'),
            models.Index(fields=['priority'], name='task_priority_idx'),
            models.Index(fields=['order'], name='task_order_idx'),
            
            # 用户相关复合索引 - 针对用户任务列表查询优化
            models.Index(fields=['owner', '-created_at'], name='task_owner_created_idx'),
            models.Index(fields=['assigned_to', '-created_at'], name='task_assign_created_idx'),
            models.Index(fields=['owner', 'status', '-created_at'], name='task_own_stat_crt_idx'),
            models.Index(fields=['assigned_to', 'status', '-created_at'], name='task_asn_stat_crt_idx'),
            
            # 软删除相关索引 - 针对软删除查询优化
            models.Index(fields=['is_deleted', '-created_at'], name='task_del_created_idx'),
            models.Index(fields=['is_deleted', 'owner', '-created_at'], name='task_del_own_crt_idx'),
            models.Index(fields=['is_deleted', 'assigned_to', '-created_at'], name='task_del_asn_crt_idx'),
            
            # 状态和优先级复合索引 - 针对任务筛选优化
            models.Index(fields=['status', 'priority'], name='task_status_priority_idx'),
            models.Index(fields=['priority', 'status', 'due_date'], name='task_pri_stat_due_idx'),
            
            # 时间相关复合索引 - 针对时间范围查询优化
            models.Index(fields=['due_date', 'status'], name='task_due_status_idx'),
            models.Index(fields=['start_date', 'due_date'], name='task_start_due_idx'),
            models.Index(fields=['completed_at'], name='task_completed_at_idx'),
            
            # 分类和状态复合索引 - 针对分类筛选优化
            models.Index(fields=['category', 'status'], name='task_cat_status_idx'),
            models.Index(fields=['category', 'priority'], name='task_cat_priority_idx'),
            
            # 统计查询优化索引
            models.Index(fields=['owner', 'status', 'is_deleted'], name='task_own_stat_del_idx'),
            models.Index(fields=['assigned_to', 'status', 'is_deleted'], name='task_asn_stat_del_idx'),
            
            # 过期任务查询优化
            models.Index(fields=['due_date', 'status', 'is_deleted'], name='task_due_stat_del_idx'),
            
            # 更新时间索引 - 针对最近更新查询
            models.Index(fields=['-updated_at'], name='task_updated_idx'),
            models.Index(fields=['owner', '-updated_at'], name='task_owner_updated_idx'),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        """
        重写save方法，处理状态变更时的自动更新
        """
        # 如果状态变为已完成，自动设置完成时间和进度
        if self.status == 'COMPLETED' and not self.completed_at:
            self.completed_at = timezone.now()
            self.progress = 100
        
        # 如果状态不是已完成，清除完成时间
        elif self.status != 'COMPLETED' and self.completed_at:
            self.completed_at = None
        
        super().save(*args, **kwargs)
        
        # 更新用户的任务统计
        if self.owner and hasattr(self.owner, 'profile'):
            self.owner.profile.update_task_count()

    @property
    def is_overdue(self):
        """检查任务是否已过期"""
        if not self.due_date:
            return False
        return self.due_date < timezone.now() and self.status not in ['COMPLETED', 'CANCELLED']

    @property
    def time_remaining(self):
        """计算剩余时间"""
        if not self.due_date:
            return None
        remaining = self.due_date - timezone.now()
        return remaining if remaining.total_seconds() > 0 else None

    @property
    def is_high_priority(self):
        """判断是否为高优先级任务"""
        return self.priority in ['HIGH', 'URGENT']

    @property
    def tags_list(self):
        """将标签字符串转换为列表"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def add_tag(self, tag):
        """添加标签"""
        tags = self.tags_list
        if tag not in tags:
            tags.append(tag)
            self.tags = ', '.join(tags)

    def remove_tag(self, tag):
        """移除标签"""
        tags = self.tags_list
        if tag in tags:
            tags.remove(tag)
            self.tags = ', '.join(tags)

    def get_priority_color(self):
        """获取优先级对应的颜色"""
        colors = {
            'LOW': '#28a745',      # 绿色
            'MEDIUM': '#ffc107',   # 黄色
            'HIGH': '#fd7e14',     # 橙色
            'URGENT': '#dc3545',   # 红色
        }
        return colors.get(self.priority, '#6c757d')

    def get_status_color(self):
        """获取状态对应的颜色"""
        colors = {
            'PENDING': '#6c757d',      # 灰色
            'IN_PROGRESS': '#007bff',  # 蓝色
            'COMPLETED': '#28a745',    # 绿色
            'CANCELLED': '#dc3545',    # 红色
            'ON_HOLD': '#ffc107',      # 黄色
        }
        return colors.get(self.status, '#6c757d')

    def can_edit(self, user):
        """检查用户是否可以编辑此任务"""
        return user == self.owner or user == self.assigned_to

    def can_delete(self, user):
        """检查用户是否可以删除此任务"""
        return user == self.owner

    @classmethod
    def get_tasks_by_status(cls, user, status):
        """根据状态获取用户任务"""
        return cls.objects.filter(
            models.Q(owner=user) | models.Q(assigned_to=user),
            status=status
        )

    @classmethod
    def get_overdue_tasks(cls, user):
        """获取用户的过期任务"""
        return cls.objects.filter(
            models.Q(owner=user) | models.Q(assigned_to=user),
            due_date__lt=timezone.now(),
            status__in=['PENDING', 'IN_PROGRESS', 'ON_HOLD']
        )

    @classmethod
    def get_tasks_due_soon(cls, user, days=7):
        """获取即将到期的任务"""
        soon = timezone.now() + timezone.timedelta(days=days)
        return cls.objects.filter(
            models.Q(owner=user) | models.Q(assigned_to=user),
            due_date__gte=timezone.now(),
            due_date__lte=soon,
            status__in=['PENDING', 'IN_PROGRESS', 'ON_HOLD']
        )

    # ==================== 软删除和恢复相关方法 ====================
    
    def soft_delete(self, user=None):
        """
        软删除任务
        
        Args:
            user: 执行删除操作的用户
        """
        # 调用父类的软删除方法
        super().soft_delete(user)
        
        # 更新用户的任务统计
        if self.owner and hasattr(self.owner, 'profile'):
            self.owner.profile.update_task_count()
    
    def restore(self, user=None):
        """
        恢复已删除的任务
        
        Args:
            user: 执行恢复操作的用户
        """
        # 调用父类的恢复方法
        super().restore(user)
        
        # 更新用户的任务统计
        if self.owner and hasattr(self.owner, 'profile'):
            self.owner.profile.update_task_count()
    
    def can_restore(self, user):
        """
        检查用户是否可以恢复此任务
        
        Args:
            user: 要检查权限的用户
            
        Returns:
            bool: 是否可以恢复
        """
        if not self.is_deleted:
            return False
        
        # 只有任务所有者可以恢复任务
        return user == self.owner
    
    def get_trash_info(self):
        """
        获取回收站信息
        
        Returns:
            dict: 包含回收站相关信息的字典
        """
        if not self.is_deleted:
            return None
        
        return {
            'task_id': str(self.id),
            'title': self.title,
            'deleted_at': self.deleted_at,
            'deleted_by': self.deleted_by.username if self.deleted_by else None,
            'deletion_age_days': self.deletion_age,
            'can_be_restored': self.can_be_restored,
            'owner': self.owner.username,
            'status_when_deleted': self.status,
            'priority': self.get_priority_display(),
            'due_date': self.due_date
        }
    
    @classmethod
    def get_user_trash(cls, user, include_assigned=False):
        """
        获取用户的回收站任务
        
        Args:
            user: 用户对象
            include_assigned: 是否包含分配给用户的任务
            
        Returns:
            QuerySet: 已删除的任务查询集
        """
        query = models.Q(owner=user)
        if include_assigned:
            query |= models.Q(assigned_to=user)
        
        return cls.all_objects.filter(query, is_deleted=True).order_by('-deleted_at')
    
    @classmethod
    def cleanup_old_deleted_tasks(cls, days=30):
        """
        清理指定天数前删除的任务（硬删除）
        
        Args:
            days: 删除多少天前的任务，默认30天
            
        Returns:
            int: 清理的任务数量
        """
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        old_deleted_tasks = cls.all_objects.filter(
            is_deleted=True,
            deleted_at__lt=cutoff_date
        )
        
        count = old_deleted_tasks.count()
        # 执行硬删除
        old_deleted_tasks.delete()
        
        return count
    
    @classmethod
    def restore_user_tasks(cls, user, task_ids):
        """
        批量恢复用户的任务
        
        Args:
            user: 用户对象
            task_ids: 要恢复的任务ID列表
            
        Returns:
            dict: 恢复结果统计
        """
        tasks = cls.all_objects.filter(
            id__in=task_ids,
            owner=user,
            is_deleted=True
        )
        
        restored_count = 0
        failed_count = 0
        
        for task in tasks:
            try:
                task.restore(user)
                restored_count += 1
            except Exception:
                failed_count += 1
        
        return {
            'restored': restored_count,
            'failed': failed_count,
            'total': len(task_ids)
        }
    
    @classmethod
    def permanent_delete_user_tasks(cls, user, task_ids):
        """
        批量永久删除用户的任务
        
        Args:
            user: 用户对象
            task_ids: 要永久删除的任务ID列表
            
        Returns:
            dict: 删除结果统计
        """
        tasks = cls.all_objects.filter(
            id__in=task_ids,
            owner=user,
            is_deleted=True
        )
        
        deleted_count = tasks.count()
        # 执行硬删除
        tasks.delete()
        
        return {
            'deleted': deleted_count,
            'total': len(task_ids)
        }
    
    @classmethod
    def get_deletion_statistics(cls, user):
        """
        获取用户的删除统计信息
        
        Args:
            user: 用户对象
            
        Returns:
            dict: 删除统计信息
        """
        deleted_tasks = cls.all_objects.filter(owner=user, is_deleted=True)
        
        # 按时间范围统计
        now = timezone.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timezone.timedelta(days=7)
        month_ago = today - timezone.timedelta(days=30)
        
        return {
            'total_deleted': deleted_tasks.count(),
            'deleted_today': deleted_tasks.filter(deleted_at__gte=today).count(),
            'deleted_this_week': deleted_tasks.filter(deleted_at__gte=week_ago).count(),
            'deleted_this_month': deleted_tasks.filter(deleted_at__gte=month_ago).count(),
            'oldest_deleted': deleted_tasks.order_by('deleted_at').first(),
            'newest_deleted': deleted_tasks.order_by('-deleted_at').first(),
            'can_be_cleaned': deleted_tasks.filter(
                deleted_at__lt=now - timezone.timedelta(days=30)
            ).count()
        }

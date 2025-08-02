"""
LingTaskFlow 序列化器
用于API数据的序列化和反序列化
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile, Task


class UserRegistrationSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=128,
        style={'input_type': 'password'},
        help_text='密码长度8-128字符，包含数字和字母'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text='确认密码，必须与密码一致'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm')
        extra_kwargs = {
            'username': {
                'min_length': 3,
                'max_length': 20,
                'help_text': '用户名长度3-20字符，唯一'
            },
            'email': {
                'required': True,
                'help_text': '邮箱地址，必须唯一'
            }
        }

    def validate_username(self, value):
        """验证用户名唯一性和格式"""
        import re
        
        # 检查用户名是否已存在
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户名已存在")
        
        # 检查用户名格式（只允许字母、数字、下划线）
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError("用户名只能包含字母、数字和下划线")
        
        # 检查是否以字母开头
        if not value[0].isalpha():
            raise serializers.ValidationError("用户名必须以字母开头")
        
        return value

    def validate_email(self, value):
        """验证邮箱唯一性和格式"""
        import re
        
        # 检查邮箱是否已被注册
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("邮箱已被注册")
        
        # 增强的邮箱格式验证
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise serializers.ValidationError("请输入有效的邮箱地址")
        
        return value.lower()  # 统一转换为小写

    def validate_password(self, value):
        """验证密码强度"""
        import re
        
        # 检查密码长度
        if len(value) < 8:
            raise serializers.ValidationError("密码长度不能少于8位")
        
        if len(value) > 128:
            raise serializers.ValidationError("密码长度不能超过128位")
        
        # 检查是否包含数字
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("密码必须包含至少一个数字")
        
        # 检查是否包含字母
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("密码必须包含至少一个字母")
        
        # 检查是否包含特殊字符（可选，增强安全性）
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(char in special_chars for char in value):
            raise serializers.ValidationError("密码建议包含特殊字符以提高安全性")
        
        # 检查常见弱密码
        weak_passwords = [
            'password', '12345678', 'qwerty123', 'abc123456', 
            'password123', '123456789', 'admin123'
        ]
        if value.lower() in weak_passwords:
            raise serializers.ValidationError("请使用更强的密码，避免常见密码")
        
        return value

    def validate(self, attrs):
        """验证密码一致性"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': '确认密码与密码不一致'
            })
        return attrs

    def create(self, validated_data):
        """创建用户并自动创建用户档案"""
        from django.db import transaction
        
        # 移除确认密码字段
        validated_data.pop('password_confirm')
        
        try:
            # 使用事务确保数据一致性
            with transaction.atomic():
                # 创建用户
                user = User.objects.create_user(
                    username=validated_data['username'],
                    email=validated_data['email'],
                    password=validated_data['password']
                )
                
                # 确保UserProfile已创建（由信号处理器自动创建）
                if not hasattr(user, 'profile'):
                    from .models import UserProfile
                    UserProfile.objects.create(user=user)
                
                return user
                
        except Exception as e:
            # 如果创建失败，抛出验证错误
            raise serializers.ValidationError(f"用户创建失败：{str(e)}")
    
    def to_representation(self, instance):
        """自定义序列化输出，移除敏感信息"""
        data = super().to_representation(instance)
        # 移除密码相关字段
        data.pop('password', None)
        data.pop('password_confirm', None)
        return data


class UserLoginSerializer(serializers.Serializer):
    """增强的用户登录序列化器"""
    username = serializers.CharField(
        max_length=150,
        help_text='用户名或邮箱地址'
    )
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text='用户密码'
    )
    remember_me = serializers.BooleanField(
        default=False,
        required=False,
        help_text='是否记住登录状态（延长Token有效期）'
    )

    def validate_username(self, value):
        """验证用户名格式"""
        if not value or not value.strip():
            raise serializers.ValidationError('用户名不能为空')
        return value.strip()

    def validate_password(self, value):
        """验证密码格式"""
        if not value:
            raise serializers.ValidationError('密码不能为空')
        if len(value) > 128:
            raise serializers.ValidationError('密码长度不能超过128字符')
        return value

    def validate(self, attrs):
        """验证用户凭据并检查账户状态"""
        from django.core.cache import cache
        from django.utils import timezone
        import hashlib
        
        username = attrs.get('username')
        password = attrs.get('password')
        
        if not username or not password:
            raise serializers.ValidationError('必须提供用户名和密码')

        # 生成登录尝试缓存键
        attempt_key = f"login_attempts_{hashlib.md5(username.encode()).hexdigest()}"
        lock_key = f"account_locked_{hashlib.md5(username.encode()).hexdigest()}"
        
        # 检查账户是否被锁定
        if cache.get(lock_key):
            lock_time = cache.get(f"{lock_key}_time", 0)
            remaining_time = max(0, 1800 - (timezone.now().timestamp() - lock_time))  # 30分钟锁定
            raise serializers.ValidationError(
                f'账户已被暂时锁定，请{int(remaining_time//60)}分钟后再试'
            )

        # 获取当前失败尝试次数
        failed_attempts = cache.get(attempt_key, 0)
        max_attempts = 5  # 最大尝试次数

        # 尝试用户名登录
        user = authenticate(username=username, password=password)
        
        # 如果用户名登录失败，尝试邮箱登录
        if not user:
            try:
                user_obj = User.objects.get(email__iexact=username)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        if not user:
            # 登录失败，增加失败计数
            failed_attempts += 1
            cache.set(attempt_key, failed_attempts, 1800)  # 30分钟过期
            
            if failed_attempts >= max_attempts:
                # 锁定账户
                cache.set(lock_key, True, 1800)  # 锁定30分钟
                cache.set(f"{lock_key}_time", timezone.now().timestamp(), 1800)
                raise serializers.ValidationError(
                    f'登录失败次数过多，账户已被锁定30分钟'
                )
            
            remaining_attempts = max_attempts - failed_attempts
            raise serializers.ValidationError(
                f'用户名/邮箱或密码错误，还有{remaining_attempts}次尝试机会'
            )
        
        # 检查用户账户状态
        if not user.is_active:
            raise serializers.ValidationError('用户账户已被禁用，请联系管理员')

        # 登录成功，清除失败记录
        cache.delete(attempt_key)
        cache.delete(lock_key)
        cache.delete(f"{lock_key}_time")

        attrs['user'] = user
        attrs['failed_attempts'] = failed_attempts  # 传递给视图用于日志记录
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'date_joined', 'last_login')
        read_only_fields = ('id', 'date_joined', 'last_login')


class TokenResponseSerializer(serializers.Serializer):
    """JWT Token响应序列化器"""
    access = serializers.CharField(help_text='访问令牌')
    refresh = serializers.CharField(help_text='刷新令牌')


def get_tokens_for_user(user):
    """为用户生成JWT Token"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserProfileSerializer(serializers.ModelSerializer):
    """用户档案序列化器"""
    user = UserSerializer(read_only=True)
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = (
            'user', 'avatar', 'avatar_url', 'timezone', 
            'task_count', 'completed_task_count', 'completion_rate',
            'theme_preference', 'email_notifications',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'user', 'task_count', 'completed_task_count', 
            'created_at', 'updated_at'
        )
    
    def get_avatar_url(self, obj):
        """获取头像URL"""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None
    
    def to_representation(self, instance):
        """自定义序列化输出"""
        data = super().to_representation(instance)
        # 添加完成率
        data['completion_rate'] = instance.completion_rate
        return data


class UserWithProfileSerializer(serializers.ModelSerializer):
    """用户信息及档案序列化器（完整信息）"""
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'date_joined', 'last_login', 'profile')
        read_only_fields = ('id', 'date_joined', 'last_login')


# ========================================================================
# 任务相关序列化器
# ========================================================================

class TaskListSerializer(serializers.ModelSerializer):
    """任务列表序列化器（简化版，用于列表展示）"""
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    is_high_priority = serializers.BooleanField(read_only=True)
    time_remaining_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = (
            'id', 'title', 'description', 'status', 'status_display', 'priority', 'priority_display',
            'progress', 'due_date', 'owner', 'owner_username', 'assigned_to', 
            'assigned_to_username', 'category', 'tags', 'is_overdue', 
            'is_high_priority', 'created_at', 'updated_at', 'time_remaining_display',
            'is_deleted', 'deleted_at'  # 添加软删除相关字段
        )
        read_only_fields = ('id', 'owner', 'created_at', 'updated_at', 'is_deleted', 'deleted_at')
    
    def get_time_remaining_display(self, obj):
        """获取剩余时间的友好显示"""
        remaining = obj.time_remaining
        if remaining:
            days = remaining.days
            hours = remaining.seconds // 3600
            if days > 0:
                return f"{days}天{hours}小时"
            elif hours > 0:
                return f"{hours}小时"
            else:
                minutes = (remaining.seconds % 3600) // 60
                return f"{minutes}分钟"
        return "无限制"


class TaskDetailSerializer(serializers.ModelSerializer):
    """任务详情序列化器（完整版，用于详情展示和编辑）"""
    owner_info = serializers.SerializerMethodField()
    assigned_to_info = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_color = serializers.CharField(source='get_status_color', read_only=True)
    priority_color = serializers.CharField(source='get_priority_color', read_only=True)
    
    # 计算属性
    is_overdue = serializers.BooleanField(read_only=True)
    is_high_priority = serializers.BooleanField(read_only=True)
    time_remaining = serializers.SerializerMethodField()
    
    # 权限检查
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    
    # 重新定义日期字段以确保正确的序列化
    start_date = serializers.DateTimeField(required=False, allow_null=True)
    due_date = serializers.DateTimeField(required=False, allow_null=True)
    
    class Meta:
        model = Task
        fields = (
            'id', 'title', 'description', 'status', 'status_display', 'status_color',
            'priority', 'priority_display', 'priority_color', 'progress',
            'due_date', 'start_date', 'completed_at', 'estimated_hours', 'actual_hours',
            'category', 'tags', 'notes', 'attachment', 'order',
            'owner', 'owner_info', 'assigned_to', 'assigned_to_info',
            'is_overdue', 'is_high_priority', 'time_remaining', 'can_edit', 'can_delete',
            'created_at', 'updated_at', 'is_deleted', 'deleted_at'
        )
        read_only_fields = (
            'id', 'owner', 'completed_at', 'created_at', 'updated_at', 
            'is_deleted', 'deleted_at'
        )
    
    def get_owner_info(self, obj):
        """获取任务所有者信息"""
        if obj.owner:
            return {
                'id': obj.owner.id,
                'username': obj.owner.username,
                'email': obj.owner.email,
                'full_name': f"{obj.owner.first_name} {obj.owner.last_name}".strip() or obj.owner.username
            }
        return None
    
    def get_assigned_to_info(self, obj):
        """获取任务执行者信息"""
        if obj.assigned_to:
            return {
                'id': obj.assigned_to.id,
                'username': obj.assigned_to.username,
                'email': obj.assigned_to.email,
                'full_name': f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip() or obj.assigned_to.username
            }
        return None
    
    def get_time_remaining(self, obj):
        """获取剩余时间（秒数）"""
        remaining = obj.time_remaining
        if remaining:
            return remaining.total_seconds()
        return None
    
    def get_can_edit(self, obj):
        """检查当前用户是否可以编辑任务"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.can_edit(request.user)
        return False
    
    def get_can_delete(self, obj):
        """检查当前用户是否可以删除任务"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.can_delete(request.user)
        return False


class TaskCreateSerializer(serializers.ModelSerializer):
    """任务创建序列化器"""
    tags = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text='标签，用逗号分隔'
    )
    
    class Meta:
        model = Task
        fields = (
            'title', 'description', 'status', 'priority', 'progress',
            'due_date', 'start_date', 'estimated_hours', 'category', 
            'tags', 'notes', 'attachment', 'assigned_to'
        )
        extra_kwargs = {
            'title': {'required': True},
            'status': {'default': 'PENDING'},
            'priority': {'default': 'MEDIUM'},
            'progress': {'default': 0, 'min_value': 0, 'max_value': 100}
        }
    
    def validate_title(self, value):
        """验证标题"""
        if not value.strip():
            raise serializers.ValidationError("任务标题不能为空")
        return value.strip()
    
    def validate_progress(self, value):
        """验证进度"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("进度必须在0-100之间")
        return value
    
    def validate_due_date(self, value):
        """验证截止时间"""
        # 注释掉严格的时间验证，允许设置过期任务（用于测试或历史数据）
        # if value and value < timezone.now():
        #     raise serializers.ValidationError("截止时间不能早于当前时间")
        return value
    
    def validate_start_date(self, value):
        """验证开始时间"""
        # 注释掉严格的时间验证，允许灵活设置开始时间
        # if value and value < timezone.now().date():
        #     raise serializers.ValidationError("开始时间不能早于今天")
        return value
    
    def validate(self, attrs):
        """交叉验证"""
        start_date = attrs.get('start_date')
        due_date = attrs.get('due_date')
        
        if start_date and due_date:
            # 如果due_date是datetime，取其date部分进行比较
            due_date_only = due_date.date() if hasattr(due_date, 'date') else due_date
            if start_date > due_date_only:
                raise serializers.ValidationError("开始时间不能晚于截止时间")
        
        return attrs
    
    def create(self, validated_data):
        """
        创建任务
        
        增强功能：
        - 自动设置任务所有者
        - 智能默认值设置
        - 自动计算优先级
        - 任务模板支持
        """
        from django.utils import timezone
        
        # 自动设置任务所有者为当前用户
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['owner'] = request.user
        
        # 智能默认值设置
        if not validated_data.get('created_at'):
            validated_data['created_at'] = timezone.now()
        
        # 如果没有设置开始时间，默认为今天的开始时间
        if not validated_data.get('start_date'):
            validated_data['start_date'] = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 智能优先级推荐
        if not validated_data.get('priority'):
            due_date = validated_data.get('due_date')
            if due_date:
                # 确保due_date是datetime或date对象
                if hasattr(due_date, 'date'):
                    due_date_only = due_date.date()
                else:
                    due_date_only = due_date
                
                # 计算剩余天数
                days_until_due = due_date_only - timezone.now().date()
                if days_until_due.days <= 1:
                    validated_data['priority'] = 'URGENT'
                elif days_until_due.days <= 3:
                    validated_data['priority'] = 'HIGH'
                elif days_until_due.days <= 7:
                    validated_data['priority'] = 'MEDIUM'
                else:
                    validated_data['priority'] = 'LOW'
            else:
                validated_data['priority'] = 'MEDIUM'
        
        # 智能分类设置
        if not validated_data.get('category'):
            title = validated_data.get('title', '').lower()
            if any(keyword in title for keyword in ['开发', '编程', '代码', '程序', 'bug', 'feature']):
                validated_data['category'] = '开发'
            elif any(keyword in title for keyword in ['测试', 'test', '验证', '检查']):
                validated_data['category'] = '测试'
            elif any(keyword in title for keyword in ['文档', '说明', '手册', '教程']):
                validated_data['category'] = '文档'
            elif any(keyword in title for keyword in ['设计', 'ui', 'ux', '界面', '原型']):
                validated_data['category'] = '设计'
            elif any(keyword in title for keyword in ['会议', '讨论', '沟通', '汇报']):
                validated_data['category'] = '会议'
            else:
                validated_data['category'] = '其他'
        
        # 智能工时预估
        if not validated_data.get('estimated_hours'):
            priority = validated_data.get('priority', 'MEDIUM')
            if priority == 'URGENT':
                validated_data['estimated_hours'] = 2.0
            elif priority == 'HIGH':
                validated_data['estimated_hours'] = 4.0
            elif priority == 'MEDIUM':
                validated_data['estimated_hours'] = 6.0
            else:
                validated_data['estimated_hours'] = 8.0
        
        # 自动标签生成
        if not validated_data.get('tags'):
            auto_tags = []
            
            # 根据优先级添加标签
            priority = validated_data.get('priority')
            if priority in ['HIGH', 'URGENT']:
                auto_tags.append('重要')
            
            # 根据截止时间添加标签
            due_date = validated_data.get('due_date')
            if due_date:
                # 确保due_date是datetime或date对象
                if hasattr(due_date, 'date'):
                    due_date_only = due_date.date()
                else:
                    due_date_only = due_date
                
                # 计算剩余天数
                days_until_due = due_date_only - timezone.now().date()
                if days_until_due.days <= 1:
                    auto_tags.append('紧急')
                elif days_until_due.days <= 3:
                    auto_tags.append('近期')
            
            # 根据分类添加标签
            category = validated_data.get('category')
            if category:
                auto_tags.append(category)
            
            if auto_tags:
                validated_data['tags'] = ', '.join(auto_tags)
        
        # 设置任务顺序（新任务排在最前面）
        if not validated_data.get('order'):
            owner = validated_data.get('owner')
            if owner:
                max_order = Task.objects.filter(owner=owner).aggregate(
                    max_order=models.Max('order')
                )['max_order'] or 0
                validated_data['order'] = max_order + 1
        
        return super().create(validated_data)


class TaskUpdateSerializer(serializers.ModelSerializer):
    """任务更新序列化器（增强版）"""
    tags = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text='标签，用逗号分隔'
    )
    
    class Meta:
        model = Task
        fields = (
            'title', 'description', 'status', 'priority', 'progress',
            'due_date', 'start_date', 'estimated_hours', 'actual_hours',
            'category', 'tags', 'notes', 'attachment', 'assigned_to', 'order'
        )
        extra_kwargs = {
            'progress': {'min_value': 0, 'max_value': 100}
        }
    
    def validate_title(self, value):
        """验证标题"""
        if value is not None and not value.strip():
            raise serializers.ValidationError("任务标题不能为空")
        return value.strip() if value else value
    
    def validate_progress(self, value):
        """验证进度"""
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("进度必须在0-100之间")
        return value
    
    def validate_status(self, value):
        """验证状态转换"""
        if value and self.instance:
            old_status = self.instance.status
            new_status = value
            
            # 定义允许的状态转换
            allowed_transitions = {
                'PENDING': ['IN_PROGRESS', 'ON_HOLD', 'CANCELLED'],
                'IN_PROGRESS': ['COMPLETED', 'ON_HOLD', 'CANCELLED', 'PENDING'],
                'ON_HOLD': ['PENDING', 'IN_PROGRESS', 'CANCELLED'],
                'COMPLETED': ['IN_PROGRESS'],  # 已完成的任务可以重新打开
                'CANCELLED': ['PENDING', 'IN_PROGRESS']  # 已取消的任务可以重新激活
            }
            
            if old_status != new_status and new_status not in allowed_transitions.get(old_status, []):
                raise serializers.ValidationError(
                    f"不能从状态 '{old_status}' 直接转换到 '{new_status}'"
                )
        
        return value
    
    def validate(self, attrs):
        """交叉验证和业务规则检查"""
        start_date = attrs.get('start_date')
        due_date = attrs.get('due_date')
        status = attrs.get('status')
        progress = attrs.get('progress')
        
        # 如果没有提供新值，使用实例的现有值
        if start_date is None and hasattr(self.instance, 'start_date'):
            start_date = self.instance.start_date
        if due_date is None and hasattr(self.instance, 'due_date'):
            due_date = self.instance.due_date
        if status is None and hasattr(self.instance, 'status'):
            status = self.instance.status
        if progress is None and hasattr(self.instance, 'progress'):
            progress = self.instance.progress
        
        # 时间验证
        if start_date and due_date:
            # 如果due_date是datetime，取其date部分进行比较
            due_date_only = due_date.date() if hasattr(due_date, 'date') else due_date
            start_date_only = start_date.date() if hasattr(start_date, 'date') else start_date
            if start_date_only > due_date_only:
                raise serializers.ValidationError("开始时间不能晚于截止时间")
        
        # 状态和进度一致性检查
        if status == 'COMPLETED':
            if progress is not None and progress < 100:
                # 如果状态设为完成但进度不是100，自动设置为100
                attrs['progress'] = 100
        elif status == 'PENDING':
            if progress is not None and progress > 0:
                # 如果状态设为待办但有进度，可能需要调整
                pass
        
        # 如果进度设为100但状态不是完成，询问是否自动完成
        if progress == 100 and status != 'COMPLETED':
            # 这里可以添加自动完成的逻辑或警告
            pass
        
        return attrs
    
    def update(self, instance, validated_data):
        """增强的更新方法"""
        from django.utils import timezone
        
        # 记录更新前的状态（用于历史记录）
        old_data = {
            'status': instance.status,
            'progress': instance.progress,
            'priority': instance.priority,
            'assigned_to': instance.assigned_to,
            'due_date': instance.due_date
        }
        
        # 处理状态变更的特殊逻辑
        new_status = validated_data.get('status')
        if new_status and new_status != instance.status:
            if new_status == 'COMPLETED':
                validated_data['completed_at'] = timezone.now()
                validated_data['progress'] = validated_data.get('progress', 100)
            elif instance.status == 'COMPLETED' and new_status != 'COMPLETED':
                # 如果从完成状态改为其他状态，清除完成时间
                validated_data['completed_at'] = None
        
        # 处理进度变更
        new_progress = validated_data.get('progress')
        if new_progress is not None and new_progress == 100 and instance.status != 'COMPLETED':
            # 如果进度设为100但状态不是完成，可以选择自动完成
            if validated_data.get('status') != 'COMPLETED':
                # 这里可以添加自动完成的逻辑
                pass
        
        # 更新实际工时（如果提供）
        actual_hours = validated_data.get('actual_hours')
        if actual_hours is not None:
            instance.actual_hours = actual_hours
        
        # 执行更新
        updated_instance = super().update(instance, validated_data)
        
        # 记录更新历史（可以扩展为独立的历史记录模型）
        self._log_update_history(updated_instance, old_data, validated_data)
        
        return updated_instance
    
    def _log_update_history(self, instance, old_data, new_data):
        """记录更新历史"""
        changes = []
        
        # 检查各个字段的变更
        for field in ['status', 'progress', 'priority', 'assigned_to', 'due_date']:
            old_value = old_data.get(field)
            new_value = new_data.get(field, getattr(instance, field))
            
            if old_value != new_value:
                changes.append({
                    'field': field,
                    'old_value': str(old_value) if old_value is not None else None,
                    'new_value': str(new_value) if new_value is not None else None,
                })
        
        if changes:
            # 这里可以保存到历史记录模型或日志系统
            import logging
            logger = logging.getLogger('task_updates')
            logger.info(f"任务 {instance.id} 更新记录: {changes}")
        
        return changes


class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    """任务状态更新序列化器（用于快速状态变更）"""
    
    class Meta:
        model = Task
        fields = ('status', 'progress')
        extra_kwargs = {
            'progress': {'min_value': 0, 'max_value': 100}
        }
    
    def validate(self, attrs):
        """验证状态变更"""
        status = attrs.get('status')
        progress = attrs.get('progress')
        
        # 如果状态为完成，进度应为100
        if status == 'COMPLETED' and progress is not None and progress < 100:
            attrs['progress'] = 100
        
        # 如果状态不是完成，但进度为100，可能需要提醒
        if status != 'COMPLETED' and progress == 100:
            # 这里可以添加警告或自动变更状态的逻辑
            pass
        
        return attrs


class TaskStatisticsSerializer(serializers.Serializer):
    """任务统计序列化器"""
    total_tasks = serializers.IntegerField(read_only=True)
    completed_tasks = serializers.IntegerField(read_only=True)
    pending_tasks = serializers.IntegerField(read_only=True)
    in_progress_tasks = serializers.IntegerField(read_only=True)
    cancelled_tasks = serializers.IntegerField(read_only=True)
    on_hold_tasks = serializers.IntegerField(read_only=True)
    overdue_tasks = serializers.IntegerField(read_only=True)
    high_priority_tasks = serializers.IntegerField(read_only=True)
    completion_rate = serializers.FloatField(read_only=True)
    
    # 按优先级分布
    priority_distribution = serializers.DictField(read_only=True)
    
    # 按状态分布
    status_distribution = serializers.DictField(read_only=True)
    
    # 按分类分布
    category_distribution = serializers.DictField(read_only=True)


class TaskBulkActionSerializer(serializers.Serializer):
    """任务批量操作序列化器"""
    action = serializers.ChoiceField(
        choices=[
            ('complete', '标记为完成'),
            ('delete', '软删除'),
            ('restore', '恢复'),
            ('assign', '分配给用户'),
            ('update_status', '更新状态'),
            ('update_priority', '更新优先级'),
        ],
        help_text='要执行的批量操作'
    )
    task_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        help_text='要操作的任务ID列表'
    )
    
    # 可选参数，根据操作类型使用
    assigned_to = serializers.IntegerField(required=False, help_text='分配给的用户ID')
    status = serializers.ChoiceField(
        choices=Task.STATUS_CHOICES,
        required=False,
        help_text='要更新的状态'
    )
    priority = serializers.ChoiceField(
        choices=Task.PRIORITY_CHOICES,
        required=False,
        help_text='要更新的优先级'
    )
    
    def validate(self, attrs):
        """验证批量操作参数"""
        action = attrs.get('action')
        
        if action == 'assign' and not attrs.get('assigned_to'):
            raise serializers.ValidationError("分配操作需要指定用户ID")
        
        if action == 'update_status' and not attrs.get('status'):
            raise serializers.ValidationError("状态更新操作需要指定新状态")
        
        if action == 'update_priority' and not attrs.get('priority'):
            raise serializers.ValidationError("优先级更新操作需要指定新优先级")
        
        return attrs

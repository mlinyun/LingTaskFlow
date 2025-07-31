"""
LingTaskFlow 序列化器
用于API数据的序列化和反序列化
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile


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

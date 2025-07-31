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
        """验证用户名唯一性"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户名已存在")
        return value

    def validate_email(self, value):
        """验证邮箱唯一性和格式"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("邮箱已被注册")
        return value

    def validate_password(self, value):
        """验证密码强度"""
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("密码必须包含至少一个数字")
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("密码必须包含至少一个字母")
        return value

    def validate(self, attrs):
        """验证密码一致性"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': '确认密码与密码不一致'
            })
        return attrs

    def create(self, validated_data):
        """创建用户"""
        # 移除确认密码字段
        validated_data.pop('password_confirm')
        
        # 创建用户
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    username = serializers.CharField(
        max_length=150,
        help_text='用户名或邮箱'
    )
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text='密码'
    )

    def validate(self, attrs):
        """验证用户凭据"""
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            # 尝试用户名登录
            user = authenticate(username=username, password=password)
            
            # 如果用户名登录失败，尝试邮箱登录
            if not user:
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass

            if not user:
                raise serializers.ValidationError('用户名/邮箱或密码错误')
            
            if not user.is_active:
                raise serializers.ValidationError('用户账户已被禁用')

            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('必须提供用户名和密码')


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

"""
LingTaskFlow 视图
处理用户认证和任务管理相关的API请求
"""
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

from .models import UserProfile
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserProfileSerializer,
    UserWithProfileSerializer,
    get_tokens_for_user
)
from .utils import rate_limit, registration_rate_limit_key, sanitize_user_input


@api_view(['POST'])
@permission_classes([AllowAny])
@rate_limit(max_attempts=5, time_window=300, key_func=registration_rate_limit_key)
def register_view(request):
    """
    用户注册API
    
    接受POST请求，创建新用户账户并返回JWT Token和完整用户信息
    
    安全特性:
    - 速率限制：5分钟内最多3次注册尝试
    - 输入数据清理和验证
    - 事务保护确保数据一致性
    
    请求体参数:
    - username: 用户名 (3-20字符，字母开头，只包含字母数字下划线)
    - email: 邮箱地址 (必须唯一，格式正确)
    - password: 密码 (8-128字符，包含数字、字母和特殊字符)
    - password_confirm: 确认密码 (必须与密码一致)
    
    响应数据:
    - success: 操作是否成功
    - message: 操作结果消息
    - data: 包含用户信息、档案信息和JWT Token
    """
    try:
        # 清理输入数据
        cleaned_data = sanitize_user_input(request.data)
        
        # 验证必需字段
        required_fields = ['username', 'email', 'password', 'password_confirm']
        missing_fields = [field for field in required_fields if not cleaned_data.get(field)]
        
        if missing_fields:
            return Response({
                'success': False,
                'message': '请填写所有必需字段',
                'errors': {field: '该字段为必填项' for field in missing_fields}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建序列化器
        serializer = UserRegistrationSerializer(data=cleaned_data)
        
        if serializer.is_valid():
            try:
                # 创建用户
                user = serializer.save()
                
                # 生成JWT Token
                tokens = get_tokens_for_user(user)
                
                # 获取完整的用户信息（包含档案）
                user_with_profile_serializer = UserWithProfileSerializer(
                    user, 
                    context={'request': request}
                )
                
                return Response({
                    'success': True,
                    'message': '注册成功，欢迎加入LingTaskFlow！',
                    'data': {
                        'user': user_with_profile_serializer.data,
                        'tokens': tokens
                    }
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                # 如果用户创建过程中出现错误，清理可能创建的用户
                if 'user' in locals() and hasattr(locals()['user'], 'id'):
                    try:
                        locals()['user'].delete()
                    except:
                        pass  # 忽略删除错误
                
                return Response({
                    'success': False,
                    'message': '注册过程中发生错误，请稍后重试',
                    'error': str(e) if settings.DEBUG else '内部服务器错误'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # 处理验证错误
        errors = {}
        for field, error_list in serializer.errors.items():
            if isinstance(error_list, list):
                errors[field] = error_list[0] if error_list else '字段验证失败'
            else:
                errors[field] = str(error_list)
        
        return Response({
            'success': False,
            'message': '注册信息验证失败，请检查输入',
            'errors': errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        # 捕获所有未预期的错误
        return Response({
            'success': False,
            'message': '服务暂时不可用，请稍后重试',
            'error': str(e) if settings.DEBUG else '内部服务器错误'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    用户登录API
    
    接受POST请求，验证用户凭据并返回JWT Token
    """
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # 更新最后登录时间
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # 生成JWT Token
        tokens = get_tokens_for_user(user)
        
        # 返回用户信息和Token
        user_serializer = UserSerializer(user)
        
        return Response({
            'success': True,
            'message': '登录成功',
            'data': {
                'user': user_serializer.data,
                'tokens': tokens
            }
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': '登录失败',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    """
    用户登出API
    
    将刷新Token加入黑名单（如果启用了黑名单功能）
    """
    try:
        from rest_framework_simplejwt.tokens import RefreshToken
        
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            
        return Response({
            'success': True,
            'message': '登出成功'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': '登出失败',
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user_profile_view(request):
    """
    获取当前用户信息API
    
    需要JWT认证，返回当前登录用户的详细信息和档案
    """
    if request.user.is_authenticated:
        serializer = UserWithProfileSerializer(
            request.user, 
            context={'request': request}
        )
        return Response({
            'success': True,
            'data': {
                'user': serializer.data
            }
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': '用户未认证'
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['PUT', 'PATCH'])
def update_profile_view(request):
    """
    更新用户档案API
    
    需要JWT认证，允许用户更新档案信息
    """
    if not request.user.is_authenticated:
        return Response({
            'success': False,
            'message': '用户未认证'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # 获取或创建用户档案
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # 使用partial=True来支持部分更新
    partial = request.method == 'PATCH'
    serializer = UserProfileSerializer(
        profile, 
        data=request.data, 
        partial=partial,
        context={'request': request}
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': '档案更新成功',
            'data': {
                'profile': serializer.data
            }
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': '档案更新失败',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

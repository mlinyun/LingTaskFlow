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

from .models import UserProfile
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserProfileSerializer,
    UserWithProfileSerializer,
    get_tokens_for_user
)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    用户注册API
    
    接受POST请求，创建新用户账户并返回JWT Token
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # 生成JWT Token
        tokens = get_tokens_for_user(user)
        
        # 返回用户信息和Token
        user_serializer = UserSerializer(user)
        
        return Response({
            'success': True,
            'message': '注册成功',
            'data': {
                'user': user_serializer.data,
                'tokens': tokens
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'message': '注册失败',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


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

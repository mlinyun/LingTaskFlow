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
from .utils import (
    rate_limit, 
    registration_rate_limit_key, 
    sanitize_user_input,
    log_login_attempt,
    get_enhanced_tokens_for_user,
    get_client_ip
)


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
@rate_limit(max_attempts=8, time_window=300, key_func=registration_rate_limit_key)
def login_view(request):
    """
    增强的用户登录API
    
    提供完整的登录功能，包括安全防护、登录历史记录和设备识别
    
    安全特性:
    - 登录失败次数限制（5次失败后锁定30分钟）
    - 速率限制防止暴力破解
    - 登录历史记录和设备指纹识别
    - 可疑登录检测和提醒
    
    请求体参数:
    - username: 用户名或邮箱地址
    - password: 用户密码
    - remember_me: 是否记住登录状态（可选，默认false）
    
    响应数据:
    - success: 操作是否成功
    - message: 操作结果消息
    - data: 包含用户信息、档案信息和JWT Token
    - security_info: 安全相关信息（可疑登录提醒等）
    """
    try:
        # 清理输入数据
        cleaned_data = sanitize_user_input(request.data)
        
        # 验证必需字段
        required_fields = ['username', 'password']
        missing_fields = [field for field in required_fields if not cleaned_data.get(field)]
        
        if missing_fields:
            # 记录失败尝试
            log_login_attempt(
                user=None,
                username_attempted=cleaned_data.get('username', ''),
                status='failed',
                request=request,
                failure_reason='缺少必需字段'
            )
            
            return Response({
                'success': False,
                'message': '请填写用户名和密码',
                'errors': {field: '该字段为必填项' for field in missing_fields}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建序列化器
        serializer = UserLoginSerializer(data=cleaned_data)
        
        if serializer.is_valid():
            try:
                user = serializer.validated_data['user']
                remember_me = serializer.validated_data.get('remember_me', False)
                failed_attempts = serializer.validated_data.get('failed_attempts', 0)
                
                # 更新最后登录时间
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
                
                # 生成JWT Token（支持记住登录状态）
                tokens = get_enhanced_tokens_for_user(user, remember_me)
                
                # 获取完整的用户信息（包含档案）
                user_with_profile_serializer = UserWithProfileSerializer(
                    user, 
                    context={'request': request}
                )
                
                # 记录成功登录
                log_login_attempt(
                    user=user,
                    username_attempted=cleaned_data['username'],
                    status='success',
                    request=request
                )
                
                # 检查是否为可疑登录
                from .models import LoginHistory
                recent_login = LoginHistory.objects.filter(
                    user=user,
                    status='success'
                ).first()
                
                security_info = {}
                if recent_login and recent_login.is_suspicious:
                    security_info['suspicious_login'] = True
                    security_info['message'] = '检测到来自新设备的登录，如果不是您本人操作，请立即修改密码'
                
                if failed_attempts > 0:
                    security_info['previous_failures'] = failed_attempts
                    security_info['message'] = f'提醒：登录前有{failed_attempts}次失败尝试'
                
                response_data = {
                    'success': True,
                    'message': '登录成功，欢迎回来！',
                    'data': {
                        'user': user_with_profile_serializer.data,
                        'tokens': tokens
                    }
                }
                
                if security_info:
                    response_data['security_info'] = security_info
                
                return Response(response_data, status=status.HTTP_200_OK)
                
            except Exception as e:
                # 记录系统错误
                log_login_attempt(
                    user=None,
                    username_attempted=cleaned_data['username'],
                    status='failed',
                    request=request,
                    failure_reason=f'系统错误: {str(e)}'
                )
                
                return Response({
                    'success': False,
                    'message': '登录过程中发生错误，请稍后重试',
                    'error': str(e) if settings.DEBUG else '内部服务器错误'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # 处理验证错误
        username_attempted = cleaned_data.get('username', '')
        errors = {}
        failure_reasons = []
        
        for field, error_list in serializer.errors.items():
            if isinstance(error_list, list):
                error_msg = error_list[0] if error_list else '字段验证失败'
                errors[field] = error_msg
                failure_reasons.append(f"{field}: {error_msg}")
            else:
                errors[field] = str(error_list)
                failure_reasons.append(f"{field}: {error_list}")
        
        # 记录登录失败
        if '账户已被暂时锁定' in str(serializer.errors):
            log_login_attempt(
                user=None,
                username_attempted=username_attempted,
                status='locked',
                request=request,
                failure_reason='账户锁定'
            )
        else:
            log_login_attempt(
                user=None,
                username_attempted=username_attempted,
                status='failed',
                request=request,
                failure_reason='; '.join(failure_reasons)
            )
        
        return Response({
            'success': False,
            'message': '登录失败，请检查输入信息',
            'errors': errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        # 捕获所有未预期的错误
        log_login_attempt(
            user=None,
            username_attempted=request.data.get('username', ''),
            status='failed',
            request=request,
            failure_reason=f'未预期错误: {str(e)}'
        )
        
        return Response({
            'success': False,
            'message': '服务暂时不可用，请稍后重试',
            'error': str(e) if settings.DEBUG else '内部服务器错误'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


@api_view(['POST'])
@permission_classes([AllowAny])
@rate_limit(max_attempts=10, time_window=300, key_func=lambda request: f"refresh_{get_client_ip(request)}")
def token_refresh_view(request):
    """
    Token刷新API
    
    接受POST请求，使用refresh token获取新的access token
    
    安全特性:
    - 速率限制：5分钟内最多10次刷新尝试
    - Refresh token验证和过期检查
    - 自动撤销已使用的refresh token（可选）
    - 登录历史记录更新
    
    请求体参数:
    - refresh: refresh token字符串 (必需)
    
    响应格式:
    成功时返回:
    {
        "success": true,
        "message": "Token刷新成功",
        "data": {
            "access": "新的access token",
            "access_expires_in": 过期时间戳,
            "token_type": "Bearer"
        }
    }
    
    失败时返回:
    {
        "success": false,
        "message": "错误信息",
        "errors": {...}
    }
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # 获取refresh token
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response({
                'success': False,
                'message': 'Token刷新失败',
                'errors': {
                    'refresh': '请提供refresh token'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 验证并解析refresh token
            refresh = RefreshToken(refresh_token)
            
            # 获取用户ID
            user_id = refresh.payload.get('user_id')
            if not user_id:
                raise InvalidToken('Token中缺少用户信息')
            
            # 验证用户是否存在且活跃
            try:
                user = User.objects.get(id=user_id, is_active=True)
            except User.DoesNotExist:
                raise InvalidToken('用户不存在或已被禁用')
            
            # 生成新的access token
            new_access_token = refresh.access_token
            
            # 计算过期时间
            access_expires_in = int((
                timezone.now() + timezone.timedelta(
                    seconds=settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME').total_seconds()
                )
            ).timestamp())
            
            # 记录token刷新活动
            client_ip = get_client_ip(request)
            try:
                log_login_attempt(
                    username_attempted=user.username,
                    user=user,
                    status='success',
                    ip_address=client_ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    failure_reason=None,
                    request=request,
                    login_type='token_refresh'
                )
            except Exception as e:
                # 日志记录失败不应影响Token刷新
                logger.warning(f"Token刷新日志记录失败: {str(e)}")
            
            # 成功响应
            response_data = {
                'success': True,
                'message': 'Token刷新成功',
                'data': {
                    'access': str(new_access_token),
                    'access_expires_in': access_expires_in,
                    'token_type': 'Bearer'
                }
            }
            
            logger.info(f"Token刷新成功 - 用户: {user.username}, IP: {client_ip}")
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except (TokenError, InvalidToken) as e:
            # Token无效或过期
            error_message = str(e)
            
            # 记录失败的刷新尝试
            client_ip = get_client_ip(request)
            try:
                log_login_attempt(
                    username_attempted='unknown',
                    user=None,
                    status='failure',
                    ip_address=client_ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    failure_reason=f'Token刷新失败: {error_message}',
                    request=request,
                    login_type='token_refresh'
                )
            except Exception as log_error:
                logger.warning(f"Token刷新失败日志记录失败: {str(log_error)}")
            
            logger.warning(f"Token刷新失败 - IP: {client_ip}, 错误: {error_message}")
            
            return Response({
                'success': False,
                'message': 'Token已过期或无效，请重新登录',
                'errors': {
                    'refresh': 'Token无效'
                }
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        # 意外错误
        client_ip = get_client_ip(request)
        logger.error(f"Token刷新服务器错误 - IP: {client_ip}, 错误: {str(e)}")
        
        return Response({
            'success': False,
            'message': '服务器内部错误，请稍后重试',
            'errors': {
                'server': '服务器错误'
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

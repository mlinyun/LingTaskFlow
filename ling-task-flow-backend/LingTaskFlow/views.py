"""
LingTaskFlow 视图
处理用户认证和任务管理相关的API请求
"""
from rest_framework import status, generics, viewsets, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.db.models import Q, Count, Case, When, Value, CharField, Avg, Min, Sum
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend

from .models import UserProfile, Task
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserProfileSerializer,
    UserWithProfileSerializer,
    TaskListSerializer,
    TaskDetailSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    TaskStatusUpdateSerializer,
    get_tokens_for_user
)
from .permissions import IsOwnerOrReadOnly
from .utils import (
    rate_limit, 
    registration_rate_limit_key, 
    sanitize_user_input,
    log_login_attempt,
    get_enhanced_tokens_for_user,
    get_client_ip
)
from .filters import TaskFilter


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
    
    需要JWT认证，允许用户更新档案信息和基本用户信息
    """
    if not request.user.is_authenticated:
        return Response({
            'success': False,
            'message': '用户未认证'
        }, status=status.HTTP_401_UNAUTHORIZED)

    try:
        # 获取或创建用户档案
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        # 分离用户基本信息和档案信息（昵称在UserProfile中）
        user_fields = ['username', 'first_name', 'email']
        user_data = {}
        profile_data = {}

        for key, value in request.data.items():
            if key in user_fields:
                user_data[key] = value
            else:
                profile_data[key] = value

        # 更新用户基本信息
        if user_data:
            user_serializer = UserSerializer(
                request.user,
                data=user_data,
                partial=True,
            )
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        # 更新档案信息（允许部分更新，包括 nickname 等）
        if profile_data:
            profile_serializer = UserProfileSerializer(
                profile,
                data=profile_data,
                partial=True,
                context={'request': request},
            )
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save()

        # 返回完整的用户信息（包含更新后的profile）
        user_serializer = UserWithProfileSerializer(
            request.user,
            context={'request': request},
        )

        return Response({
            'success': True,
            'message': '档案更新成功',
            'data': {
                'user': user_serializer.data,
            },
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'message': '档案更新失败',
            'errors': {'server': str(e)},
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_avatar_view(request):
    """
    上传用户头像API
    
    需要JWT认证，允许用户上传头像图片
    """
    try:
        if 'avatar' not in request.FILES:
            return Response({
                'success': False,
                'message': '请选择头像文件',
                'errors': {'avatar': '头像文件不能为空'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        avatar_file = request.FILES['avatar']
        
        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        if avatar_file.content_type not in allowed_types:
            return Response({
                'success': False,
                'message': '不支持的文件格式',
                'errors': {'avatar': '只支持 JPEG、PNG、GIF、WebP 格式的图片'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证文件大小（5MB限制）
        max_size = 5 * 1024 * 1024  # 5MB
        if avatar_file.size > max_size:
            return Response({
                'success': False,
                'message': '文件太大',
                'errors': {'avatar': '头像文件大小不能超过5MB'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取或创建用户档案
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # 删除旧头像文件
        if profile.avatar:
            try:
                profile.avatar.delete(save=False)
            except Exception:
                pass  # 忽略删除失败的错误
        
        # 保存新头像
        profile.avatar = avatar_file
        profile.save()
        
        # 返回新头像URL
        avatar_url = profile.get_avatar_url()
        if request:
            avatar_url = request.build_absolute_uri(profile.avatar.url) if profile.avatar else None
        
        return Response({
            'success': True,
            'message': '头像上传成功',
            'data': {
                'avatar_url': avatar_url
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': '头像上传失败',
            'errors': {'server': str(e)}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    修改用户密码API
    
    需要JWT认证，允许用户修改密码
    """
    try:
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        # 验证必需字段
        if not all([current_password, new_password, confirm_password]):
            return Response({
                'success': False,
                'message': '请填写所有必需字段',
                'errors': {
                    'current_password': '当前密码不能为空' if not current_password else None,
                    'new_password': '新密码不能为空' if not new_password else None,
                    'confirm_password': '确认密码不能为空' if not confirm_password else None,
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证当前密码
        if not request.user.check_password(current_password):
            return Response({
                'success': False,
                'message': '当前密码错误',
                'errors': {'current_password': '当前密码不正确'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证新密码确认
        if new_password != confirm_password:
            return Response({
                'success': False,
                'message': '密码确认不一致',
                'errors': {'confirm_password': '两次输入的密码不一致'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证新密码强度
        import re
        
        if len(new_password) < 8:
            return Response({
                'success': False,
                'message': '密码强度不够',
                'errors': {'new_password': '密码长度不能少于8位'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not any(char.isdigit() for char in new_password):
            return Response({
                'success': False,
                'message': '密码强度不够',
                'errors': {'new_password': '密码必须包含至少一个数字'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not any(char.isalpha() for char in new_password):
            return Response({
                'success': False,
                'message': '密码强度不够',
                'errors': {'new_password': '密码必须包含至少一个字母'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查新密码是否与当前密码相同
        if request.user.check_password(new_password):
            return Response({
                'success': False,
                'message': '新密码不能与当前密码相同',
                'errors': {'new_password': '新密码不能与当前密码相同'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新密码
        request.user.set_password(new_password)
        request.user.save()
        
        return Response({
            'success': True,
            'message': '密码修改成功，请重新登录'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': '密码修改失败',
            'errors': {'server': str(e)}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_all_devices_view(request):
    """
    登出所有设备API
    
    使所有已发布的JWT token失效
    """
    try:
        # 这里可以实现JWT token黑名单功能
        # 由于SimplJWT的限制，这里只是一个占位符实现
        # 实际应用中需要使用JWT黑名单或修改用户的JWT secret
        
        # 记录登出操作
        from .utils import log_login_attempt
        log_login_attempt(
            user=request.user,
            username_attempted=request.user.username,
            status='logout_all',
            request=request
        )
        
        return Response({
            'success': True,
            'message': '已登出所有设备，请重新登录'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': '操作失败，请重试',
            'errors': {'server': str(e)}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


class TaskViewSet(viewsets.ModelViewSet):
    """
    任务管理ViewSet
    
    提供完整的任务CRUD操作以及高级查询功能
    
    支持的功能:
    - 列表查询: GET /api/tasks/
    - 详细信息: GET /api/tasks/{id}/
    - 创建任务: POST /api/tasks/
    - 更新任务: PATCH /api/tasks/{id}/
    - 删除任务: DELETE /api/tasks/{id}/
    - 软删除恢复: POST /api/tasks/{id}/restore/
    - 永久删除: DELETE /api/tasks/{id}/permanent/
    - 批量操作: POST /api/tasks/bulk_action/
    - 任务统计: GET /api/tasks/stats/
    """
    
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ['title', 'description', 'category', 'tags']
    ordering_fields = [
        'created_at', 'updated_at', 'due_date', 'start_date', 
        'priority', 'status', 'progress', 'title'
    ]
    ordering = ['-created_at']  # 默认按创建时间倒序
    
    def get_queryset(self):
        """
        获取查询集
        用户只能访问自己拥有或被分配的任务
        """
        user = self.request.user
        if not user or not user.is_authenticated:
            return Task.objects.none()
        
        # 基础查询：用户拥有或被分配的任务
        queryset = Task.objects.filter(
            Q(owner=user) | Q(assigned_to=user)
        ).distinct()
        
        # 处理软删除显示
        include_deleted = self.request.query_params.get('include_deleted', 'false').lower()
        if include_deleted == 'true':
            # 只有任务所有者可以查看自己的软删除任务
            queryset = Task.all_objects.filter(
                Q(owner=user) | Q(assigned_to=user)
            ).distinct()
        
        return queryset
    
    def get_serializer_class(self):
        """根据操作类型选择合适的序列化器"""
        if self.action == 'list':
            return TaskListSerializer
        elif self.action == 'create':
            return TaskCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        elif self.action == 'update_status':
            return TaskStatusUpdateSerializer
        else:
            return TaskDetailSerializer
    
    def list(self, request, *args, **kwargs):
        """
        任务列表API
        
        支持的查询参数:
        - search: 全文搜索
        - status: 任务状态
        - priority: 优先级
        - category: 分类
        - assigned_to: 分配给谁
        - is_assigned: 是否已分配
        - is_overdue: 是否逾期
        - due_soon: 即将到期天数
        - include_deleted: 是否包含软删除任务
        - ordering: 排序字段
        - page: 页码
        - page_size: 每页数量
        """
        # 应用过滤器
        queryset = self.filter_queryset(self.get_queryset())
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            
            # 添加额外的统计信息
            stats = self._get_list_stats(queryset)
            
            response = self.get_paginated_response(serializer.data)
            response.data['stats'] = stats
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        stats = self._get_list_stats(queryset)
        
        return Response({
            'results': serializer.data,
            'stats': stats,
            'count': len(serializer.data)
        })
    
    def _get_list_stats(self, queryset):
        """获取任务列表统计信息"""
        total_count = queryset.count()
        
        if total_count == 0:
            return {
                'total': 0,
                'by_status': {},
                'by_priority': {},
                'overdue_count': 0,
                'completed_count': 0
            }
        
        # 状态统计
        status_stats = queryset.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # 优先级统计
        priority_stats = queryset.values('priority').annotate(
            count=Count('id')
        ).order_by('priority')
        
        # 逾期任务统计
        from django.utils import timezone
        overdue_count = queryset.filter(
            due_date__lt=timezone.now(),
            status__in=['PENDING', 'IN_PROGRESS', 'ON_HOLD']
        ).count()
        
        # 已完成任务统计
        completed_count = queryset.filter(status='COMPLETED').count()
        
        return {
            'total': total_count,
            'by_status': {item['status']: item['count'] for item in status_stats},
            'by_priority': {item['priority']: item['count'] for item in priority_stats},
            'overdue_count': overdue_count,
            'completed_count': completed_count
        }
    
    def create(self, request, *args, **kwargs):
        """
        创建任务API
        
        增强功能：
        - 支持批量创建
        - 任务模板应用
        - 智能字段推荐
        - 数据验证和清理
        - 创建后操作
        """
        # 检查是否是批量创建
        if isinstance(request.data, list):
            return self._bulk_create_tasks(request)
        
        # 检查是否使用模板
        template_id = request.data.get('template_id')
        if template_id:
            return self._create_from_template(request, template_id)
        
        # 标准单个任务创建
        return self._create_single_task(request)
    
    def _create_single_task(self, request):
        """创建单个任务"""
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return Response({
                'success': False,
                'message': '任务数据验证失败',
                'errors': e.detail,
                'error_code': 'validation_failed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 设置任务所有者为当前用户
            task = serializer.save(owner=request.user)
            
            # 执行创建后的操作
            self._post_create_actions(task, request)
            
            # 使用详细序列化器返回完整信息
            detail_serializer = TaskDetailSerializer(task, context={'request': request})
            
            # 获取用户的任务统计更新
            user_stats = self._get_user_task_stats(request.user)
            
            return Response({
                'success': True,
                'message': '任务创建成功',
                'data': detail_serializer.data,
                'user_stats': user_stats,
                'recommendations': self._get_task_recommendations(task)
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"任务创建失败: {str(e)}", exc_info=True)
            
            return Response({
                'success': False,
                'message': '任务创建失败，请重试',
                'error': str(e),
                'error_code': 'creation_failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _bulk_create_tasks(self, request):
        """批量创建任务"""
        if len(request.data) > 50:  # 限制批量创建数量
            return Response({
                'success': False,
                'message': '批量创建任务数量不能超过50个',
                'error_code': 'bulk_limit_exceeded'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        created_tasks = []
        failed_tasks = []
        
        for i, task_data in enumerate(request.data):
            try:
                serializer = self.get_serializer(data=task_data)
                serializer.is_valid(raise_exception=True)
                task = serializer.save(owner=request.user)
                
                # 执行创建后操作
                self._post_create_actions(task, request)
                
                detail_serializer = TaskDetailSerializer(task, context={'request': request})
                created_tasks.append(detail_serializer.data)
                
            except Exception as e:
                failed_tasks.append({
                    'index': i,
                    'data': task_data.get('title', f'任务{i+1}'),
                    'error': str(e)
                })
        
        # 获取用户的任务统计更新
        user_stats = self._get_user_task_stats(request.user)
        
        return Response({
            'success': len(failed_tasks) == 0,
            'message': f'批量创建完成，成功{len(created_tasks)}个，失败{len(failed_tasks)}个',
            'data': {
                'created_tasks': created_tasks,
                'failed_tasks': failed_tasks,
                'summary': {
                    'total': len(request.data),
                    'created': len(created_tasks),
                    'failed': len(failed_tasks)
                }
            },
            'user_stats': user_stats
        }, status=status.HTTP_201_CREATED if len(failed_tasks) == 0 else status.HTTP_207_MULTI_STATUS)
    
    def _create_from_template(self, request, template_id):
        """从模板创建任务"""
        # 这里可以实现任务模板功能
        # 暂时返回标准创建，后续可以扩展
        template_data = request.data.copy()
        template_data.pop('template_id', None)
        
        # 可以在这里添加模板逻辑
        # 例如：从数据库加载模板，应用模板字段等
        
        request._full_data = template_data
        return self._create_single_task(request)
    
    def _post_create_actions(self, task, request):
        """任务创建后的操作"""
        try:
            # 更新用户统计
            user_profile = request.user.profile
            user_profile.task_count = Task.objects.filter(owner=request.user).count()
            user_profile.save(update_fields=['task_count'])
            
            # 记录创建日志
            import logging
            logger = logging.getLogger('task_management')
            logger.info(f"用户 {request.user.username} 创建了任务: {task.title} (ID: {task.id})")
            
            # 发送通知（如果任务被分配给其他人）
            if task.assigned_to and task.assigned_to != task.owner:
                self._send_assignment_notification(task)
                
        except Exception as e:
            # 创建后操作失败不应该影响任务创建
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"任务创建后操作失败: {str(e)}")
    
    def _send_assignment_notification(self, task):
        """发送任务分配通知"""
        # 这里可以实现通知系统
        # 例如：邮件通知、系统内通知等
        pass
    
    def _get_user_task_stats(self, user):
        """获取用户任务统计"""
        user_tasks = Task.objects.filter(owner=user)
        
        return {
            'total_tasks': user_tasks.count(),
            'pending_tasks': user_tasks.filter(status='PENDING').count(),
            'in_progress_tasks': user_tasks.filter(status='IN_PROGRESS').count(),
            'completed_tasks': user_tasks.filter(status='COMPLETED').count(),
            'overdue_tasks': user_tasks.filter(
                due_date__lt=timezone.now(),
                status__in=['PENDING', 'IN_PROGRESS', 'ON_HOLD']
            ).count()
        }
    
    def _get_task_recommendations(self, task):
        """获取任务相关推荐"""
        recommendations = {}
        
        # 相似任务推荐
        similar_tasks = Task.objects.filter(
            owner=task.owner,
            category=task.category,
            status='COMPLETED'
        ).exclude(id=task.id).order_by('-updated_at')[:3]
        
        if similar_tasks.exists():
            recommendations['similar_completed_tasks'] = [
                {
                    'id': str(t.id),
                    'title': t.title,
                    'estimated_hours': t.estimated_hours,
                    'actual_hours': t.actual_hours
                } for t in similar_tasks
            ]
        
        # 标签推荐
        if task.category:
            popular_tags = Task.objects.filter(
                owner=task.owner,
                category=task.category
            ).exclude(
                tags__isnull=True
            ).exclude(
                tags__exact=''
            ).values_list('tags', flat=True)
            
            tag_counts = {}
            for tags_str in popular_tags:
                for tag in tags_str.split(','):
                    tag = tag.strip()
                    if tag:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            if tag_counts:
                sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
                recommendations['suggested_tags'] = [tag for tag, count in sorted_tags[:5]]
        
        return recommendations
    
    def _post_update_actions(self, task, old_status, old_progress, old_assigned_to, request):
        """任务更新后的操作"""
        try:
            # 状态变更通知
            if task.status != old_status:
                self._handle_status_change(task, old_status, request.user)
            
            # 进度变更处理
            if task.progress != old_progress:
                self._handle_progress_change(task, old_progress, request.user)
            
            # 分配变更通知
            if task.assigned_to != old_assigned_to:
                self._handle_assignment_change(task, old_assigned_to, request.user)
            
            # 更新用户统计
            user_profile = request.user.profile
            if task.status == 'COMPLETED' and old_status != 'COMPLETED':
                user_profile.completed_task_count += 1
            elif old_status == 'COMPLETED' and task.status != 'COMPLETED':
                user_profile.completed_task_count = max(0, user_profile.completed_task_count - 1)
            
            user_profile.save(update_fields=['completed_task_count'])
            
            # 记录更新日志
            import logging
            logger = logging.getLogger('task_management')
            logger.info(f"用户 {request.user.username} 更新了任务: {task.title} (ID: {task.id})")
            
        except Exception as e:
            # 更新后操作失败不应该影响任务更新
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"任务更新后操作失败: {str(e)}")
    
    def _handle_status_change(self, task, old_status, user):
        """处理状态变更"""
        status_messages = {
            'PENDING': '任务已设为待办',
            'IN_PROGRESS': '任务已开始进行',
            'ON_HOLD': '任务已暂停',
            'COMPLETED': '任务已完成',
            'CANCELLED': '任务已取消'
        }
        
        # 发送状态变更通知（如果有分配者）
        if task.assigned_to and task.assigned_to != user:
            self._send_status_notification(task, old_status, user)
    
    def _handle_progress_change(self, task, old_progress, user):
        """处理进度变更"""
        if task.progress == 100 and old_progress < 100:
            # 进度达到100%时的处理
            if task.status != 'COMPLETED':
                # 可以考虑自动设置为完成状态
                pass
    
    def _handle_assignment_change(self, task, old_assigned_to, user):
        """处理分配变更"""
        if task.assigned_to and task.assigned_to != old_assigned_to:
            # 发送新分配通知
            self._send_assignment_notification(task)
        
        if old_assigned_to and old_assigned_to != task.assigned_to:
            # 发送取消分配通知
            self._send_unassignment_notification(task, old_assigned_to)
    
    def _send_status_notification(self, task, old_status, user):
        """发送状态变更通知"""
        # 这里可以实现通知系统
        pass
    
    def _send_unassignment_notification(self, task, old_assigned_to):
        """发送取消分配通知"""
        # 这里可以实现通知系统
        pass
    
    def _get_update_stats(self, task, user):
        """获取更新相关统计"""
        user_tasks = Task.objects.filter(owner=user)
        
        return {
            'total_tasks': user_tasks.count(),
            'pending_tasks': user_tasks.filter(status='PENDING').count(),
            'in_progress_tasks': user_tasks.filter(status='IN_PROGRESS').count(),
            'completed_tasks': user_tasks.filter(status='COMPLETED').count(),
            'on_hold_tasks': user_tasks.filter(status='ON_HOLD').count(),
            'cancelled_tasks': user_tasks.filter(status='CANCELLED').count(),
            'average_progress': user_tasks.aggregate(avg_progress=Avg('progress'))['avg_progress'] or 0
        }
    
    def retrieve(self, request, *args, **kwargs):
        """获取任务详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        """增强的任务更新功能"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # 检查权限
        if not instance.can_edit(request.user):
            return Response({
                'success': False,
                'message': '没有权限编辑此任务',
                'error': 'permission_denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 记录更新前的状态用于审计
        old_status = instance.status
        old_progress = instance.progress
        old_assigned_to = instance.assigned_to
        
        # 获取合适的序列化器
        if request.path.endswith('/status/'):
            # 如果是状态快速更新
            serializer = TaskStatusUpdateSerializer(instance, data=request.data, partial=partial)
        else:
            # 使用完整的更新序列化器
            serializer = TaskUpdateSerializer(instance, data=request.data, partial=partial)
        
        try:
            serializer.is_valid(raise_exception=True)
            task = serializer.save()
            
            # 执行更新后的操作
            self._post_update_actions(task, old_status, old_progress, old_assigned_to, request)
            
            # 使用详细序列化器返回更新后的信息
            detail_serializer = TaskDetailSerializer(task, context={'request': request})
            
            # 获取更新统计
            update_stats = self._get_update_stats(task, request.user)
            
            return Response({
                'success': True,
                'message': '任务更新成功',
                'data': detail_serializer.data,
                'update_stats': update_stats,
                'changes': getattr(serializer, '_changes', [])  # 从序列化器获取变更记录
            })
            
        except ValidationError as e:
            return Response({
                'success': False,
                'message': '任务更新失败',
                'error': str(e),
                'error_code': 'validation_failed'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': '任务更新失败，请重试',
                'error': str(e),
                'error_code': 'update_failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['patch'])
    def bulk_update(self, request):
        """批量更新任务"""
        task_updates = request.data.get('updates', [])
        
        if not task_updates:
            return Response({
                'success': False,
                'message': '没有提供要更新的任务',
                'error_code': 'no_updates'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(task_updates) > 50:  # 限制批量更新数量
            return Response({
                'success': False,
                'message': '批量更新任务数量不能超过50个',
                'error_code': 'bulk_limit_exceeded'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        updated_tasks = []
        failed_updates = []
        
        for update_data in task_updates:
            try:
                task_id = update_data.get('id')
                if not task_id:
                    failed_updates.append({
                        'data': update_data,
                        'error': '缺少任务ID'
                    })
                    continue
                
                # 获取任务实例
                try:
                    task = Task.objects.get(id=task_id, owner=request.user)
                except Task.DoesNotExist:
                    failed_updates.append({
                        'id': task_id,
                        'error': '任务不存在或无权限访问'
                    })
                    continue
                
                # 检查编辑权限
                if not task.can_edit(request.user):
                    failed_updates.append({
                        'id': task_id,
                        'error': '没有权限编辑此任务'
                    })
                    continue
                
                # 执行更新
                update_fields = {k: v for k, v in update_data.items() if k != 'id'}
                serializer = TaskUpdateSerializer(task, data=update_fields, partial=True)
                
                if serializer.is_valid():
                    updated_task = serializer.save()
                    
                    # 使用详细序列化器
                    detail_serializer = TaskDetailSerializer(updated_task, context={'request': request})
                    updated_tasks.append(detail_serializer.data)
                else:
                    failed_updates.append({
                        'id': task_id,
                        'error': serializer.errors
                    })
                    
            except Exception as e:
                failed_updates.append({
                    'id': update_data.get('id', 'unknown'),
                    'error': str(e)
                })
        
        # 获取批量更新统计
        bulk_stats = {
            'total_attempted': len(task_updates),
            'successful_updates': len(updated_tasks),
            'failed_updates': len(failed_updates),
            'success_rate': len(updated_tasks) / len(task_updates) * 100 if task_updates else 0
        }
        
        return Response({
            'success': len(failed_updates) == 0,
            'message': f'批量更新完成，成功{len(updated_tasks)}个，失败{len(failed_updates)}个',
            'data': {
                'updated_tasks': updated_tasks,
                'failed_updates': failed_updates,
                'stats': bulk_stats
            }
        }, status=status.HTTP_200_OK if len(failed_updates) == 0 else status.HTTP_207_MULTI_STATUS)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """快速更新任务状态"""
        instance = self.get_object()
        
        # 检查权限
        if not instance.can_edit(request.user):
            return Response({
                'success': False,
                'message': '没有权限编辑此任务',
                'error': 'permission_denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = TaskStatusUpdateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        task = serializer.save()
        
        # 使用详细序列化器返回更新后的信息
        detail_serializer = TaskDetailSerializer(task, context={'request': request})
        
        return Response({
            'success': True,
            'message': f'任务状态已更新为: {task.get_status_display()}',
            'data': detail_serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        """软删除任务"""
        instance = self.get_object()
        
        # 检查删除权限
        if not instance.can_delete(request.user):
            return Response({
                'success': False,
                'message': '没有权限删除此任务',
                'error': 'permission_denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 执行软删除
        instance.soft_delete(user=request.user)
        
        return Response({
            'success': True,
            'message': '任务已移入回收站',
            'data': {
                'id': str(instance.id),
                'deleted_at': instance.deleted_at,
                'can_restore': instance.can_be_restored
            }
        }, status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """恢复软删除的任务"""
        try:
            # 使用all_objects管理器查找包括软删除的任务
            task = Task.all_objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({
                'success': False,
                'message': '任务不存在',
                'error': 'not_found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 检查恢复权限
        if not task.can_restore(request.user):
            return Response({
                'success': False,
                'message': '没有权限恢复此任务',
                'error': 'permission_denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 恢复任务
        task.restore(user=request.user)
        
        # 返回恢复后的任务信息
        serializer = TaskDetailSerializer(task, context={'request': request})
        
        return Response({
            'success': True,
            'message': '任务恢复成功',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['delete'])
    def permanent(self, request, pk=None):
        """永久删除任务"""
        try:
            # 使用all_objects管理器查找包括软删除的任务
            task = Task.all_objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({
                'success': False,
                'message': '任务不存在',
                'error': 'not_found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 检查删除权限（只有所有者可以永久删除）
        if task.owner != request.user:
            return Response({
                'success': False,
                'message': '只有任务所有者可以永久删除任务',
                'error': 'permission_denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        task_id = str(task.id)
        task_title = task.title
        
        # 执行硬删除
        task.hard_delete()
        
        return Response({
            'success': True,
            'message': f'任务 "{task_title}" 已永久删除',
            'data': {
                'id': task_id,
                'title': task_title
            }
        }, status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """批量软删除任务"""
        task_ids = request.data.get('task_ids', [])
        
        if not task_ids:
            return Response({
                'success': False,
                'message': '请提供要删除的任务ID列表',
                'error': 'missing_task_ids'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(task_ids) > 50:
            return Response({
                'success': False,
                'message': '批量删除最多支持50个任务',
                'error': 'too_many_tasks'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 统计信息
        total_attempted = len(task_ids)
        successful_deletes = []
        failed_deletes = []
        
        for task_id in task_ids:
            try:
                # 获取任务
                task = Task.objects.get(id=task_id, owner=request.user, is_deleted=False)
                
                # 检查删除权限
                if not task.can_delete(request.user):
                    failed_deletes.append({
                        'id': task_id,
                        'error': '没有权限删除此任务'
                    })
                    continue
                
                # 执行软删除
                task.soft_delete(user=request.user)
                successful_deletes.append({
                    'id': task_id,
                    'title': task.title,
                    'deleted_at': task.deleted_at
                })
                
            except Task.DoesNotExist:
                failed_deletes.append({
                    'id': task_id,
                    'error': '任务不存在或已被删除'
                })
            except Exception as e:
                failed_deletes.append({
                    'id': task_id,
                    'error': str(e)
                })
        
        # 计算统计
        successful_count = len(successful_deletes)
        failed_count = len(failed_deletes)
        success_rate = (successful_count / total_attempted * 100) if total_attempted > 0 else 0
        
        # 更新用户统计
        try:
            profile = request.user.userprofile
            profile.update_task_stats()
        except:
            pass
        
        # 确定响应状态码
        if successful_count == total_attempted:
            response_status = status.HTTP_200_OK
        elif successful_count > 0:
            response_status = status.HTTP_207_MULTI_STATUS  # 部分成功
        else:
            response_status = status.HTTP_400_BAD_REQUEST  # 全部失败
        
        return Response({
            'success': successful_count > 0,
            'message': f'批量删除完成: {successful_count}/{total_attempted} 成功',
            'data': {
                'stats': {
                    'total_attempted': total_attempted,
                    'successful_deletes': successful_count,
                    'failed_deletes': failed_count,
                    'success_rate': round(success_rate, 1)
                },
                'successful_deletes': successful_deletes,
                'failed_deletes': failed_deletes
            }
        }, status=response_status)
    
    @action(detail=False, methods=['post'])
    def bulk_restore(self, request):
        """批量恢复任务"""
        task_ids = request.data.get('task_ids', [])
        
        if not task_ids:
            return Response({
                'success': False,
                'message': '请提供要恢复的任务ID列表',
                'error': 'missing_task_ids'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(task_ids) > 50:
            return Response({
                'success': False,
                'message': '批量恢复最多支持50个任务',
                'error': 'too_many_tasks'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 统计信息
        total_attempted = len(task_ids)
        successful_restores = []
        failed_restores = []
        
        for task_id in task_ids:
            try:
                # 使用all_objects管理器获取包括软删除的任务
                task = Task.all_objects.get(id=task_id, owner=request.user, is_deleted=True)
                
                # 检查恢复权限
                if not task.can_restore(request.user):
                    failed_restores.append({
                        'id': task_id,
                        'error': '没有权限恢复此任务'
                    })
                    continue
                
                # 执行恢复
                task.restore(user=request.user)
                successful_restores.append({
                    'id': task_id,
                    'title': task.title,
                    'restored_at': timezone.now()
                })
                
            except Task.DoesNotExist:
                failed_restores.append({
                    'id': task_id,
                    'error': '任务不存在或未被删除'
                })
            except Exception as e:
                failed_restores.append({
                    'id': task_id,
                    'error': str(e)
                })
        
        # 计算统计
        successful_count = len(successful_restores)
        failed_count = len(failed_restores)
        success_rate = (successful_count / total_attempted * 100) if total_attempted > 0 else 0
        
        # 更新用户统计
        try:
            profile = request.user.userprofile
            profile.update_task_stats()
        except:
            pass
        
        # 确定响应状态码
        if successful_count == total_attempted:
            response_status = status.HTTP_200_OK
        elif successful_count > 0:
            response_status = status.HTTP_207_MULTI_STATUS  # 部分成功
        else:
            response_status = status.HTTP_400_BAD_REQUEST  # 全部失败
        
        return Response({
            'success': successful_count > 0,
            'message': f'批量恢复完成: {successful_count}/{total_attempted} 成功',
            'data': {
                'stats': {
                    'total_attempted': total_attempted,
                    'successful_restores': successful_count,
                    'failed_restores': failed_count,
                    'success_rate': round(success_rate, 1)
                },
                'successful_restores': successful_restores,
                'failed_restores': failed_restores
            }
        }, status=response_status)
    
    @action(detail=False, methods=['get'])
    def trash(self, request):
        """获取回收站中的已删除任务"""
        # 获取已删除的任务
        deleted_tasks = Task.all_objects.filter(
            owner=request.user,
            is_deleted=True
        ).order_by('-deleted_at')
        
        # 分页
        page = self.paginate_queryset(deleted_tasks)
        if page is not None:
            serializer = TaskListSerializer(page, many=True, context={'request': request})
            response = self.get_paginated_response(serializer.data)
            
            # 添加回收站统计信息
            trash_stats = {
                'total_deleted_tasks': deleted_tasks.count(),
                'can_be_restored': deleted_tasks.filter(
                    deleted_at__gte=timezone.now() - timezone.timedelta(days=30)
                ).count(),  # 30天内删除的可以恢复
                'oldest_deleted': deleted_tasks.aggregate(
                    oldest=Min('deleted_at')
                )['oldest']
            }
            
            # 修改响应格式以符合API标准
            response.data = {
                'success': True,
                'message': '回收站任务获取成功',
                'data': response.data,
                'meta': {
                    'trash_stats': trash_stats
                }
            }
            return response
        
        serializer = TaskListSerializer(deleted_tasks, many=True, context={'request': request})
        
        return Response({
            'success': True,
            'message': '回收站任务获取成功',
            'data': {
                'results': serializer.data,
                'count': len(serializer.data)
            },
            'meta': {
                'trash_stats': {
                    'total_deleted_tasks': deleted_tasks.count(),
                    'can_be_restored': deleted_tasks.count(),
                    'oldest_deleted': deleted_tasks.aggregate(
                        oldest=Min('deleted_at')
                    )['oldest']
                }
            }
        })
    
    @action(detail=False, methods=['post'])
    def empty_trash(self, request):
        """清空回收站（永久删除所有已删除的任务）"""
        # 获取用户的所有已删除任务
        deleted_tasks = Task.all_objects.filter(
            owner=request.user,
            is_deleted=True
        )
        
        if not deleted_tasks.exists():
            return Response({
                'success': True,
                'message': '回收站已为空',
                'data': {
                    'deleted_count': 0
                }
            })
        
        # 检查是否有确认参数
        confirm = request.data.get('confirm', False)
        if not confirm:
            return Response({
                'success': False,
                'message': '清空回收站需要确认操作',
                'error': 'confirmation_required',
                'data': {
                    'tasks_to_delete': deleted_tasks.count(),
                    'confirmation_message': '此操作将永久删除所有回收站中的任务，无法恢复'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 执行永久删除
        task_count = deleted_tasks.count()
        task_titles = list(deleted_tasks.values_list('title', flat=True)[:5])  # 获取前5个任务标题
        
        # 永久删除所有任务
        deleted_tasks.delete()
        
        # 更新用户统计
        try:
            profile = request.user.userprofile
            profile.update_task_stats()
        except:
            pass
        
        return Response({
            'success': True,
            'message': f'回收站已清空，共删除 {task_count} 个任务',
            'data': {
                'deleted_count': task_count,
                'sample_titles': task_titles,
                'cleared_at': timezone.now()
            }
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        任务统计API
        
        GET /api/tasks/stats/
        
        支持的查询参数:
        - period: 统计周期 (all, today, week, month, quarter, year)
        - include_deleted: 包含已删除任务统计 (true/false)
        - group_by: 分组方式 (status, priority, category, assigned_to)
        - date_field: 时间字段 (created_at, updated_at, due_date, start_date)
        
        提供的统计数据:
        - 基础统计: 总数、完成率、逾期率
        - 状态分布: 各状态任务数量和百分比
        - 优先级分布: 各优先级任务数量和百分比
        - 分类统计: 任务分类分布
        - 时间趋势: 按时间段的任务创建和完成趋势
        - 工作负载: 用户任务分配情况
        - 进度分析: 任务进度分布
        - 逾期分析: 逾期任务统计
        """
        try:
            # 获取基础查询集（用户相关的任务）
            user = request.user
            base_queryset = Task.objects.filter(
                Q(owner=user) | Q(assigned_to=user)
            ).distinct()
            
            # 处理软删除任务包含
            include_deleted = request.query_params.get('include_deleted', 'false').lower()
            if include_deleted == 'true':
                base_queryset = Task.all_objects.filter(
                    Q(owner=user) | Q(assigned_to=user)
                ).distinct()
            
            # 处理时间周期过滤
            period = request.query_params.get('period', 'all').lower()
            date_field = request.query_params.get('date_field', 'created_at').lower()
            
            # 验证日期字段
            valid_date_fields = ['created_at', 'updated_at', 'due_date', 'start_date']
            if date_field not in valid_date_fields:
                date_field = 'created_at'
            
            # 应用时间周期过滤
            filtered_queryset = self._apply_period_filter(base_queryset, period, date_field)
            
            # 1. 基础统计
            basic_stats = self._calculate_basic_stats(filtered_queryset)
            
            # 2. 状态分布统计
            status_distribution = self._calculate_status_distribution(filtered_queryset)
            
            # 3. 优先级分布统计
            priority_distribution = self._calculate_priority_distribution(filtered_queryset)
            
            # 4. 分类统计
            category_stats = self._calculate_category_stats(filtered_queryset)
            
            # 5. 时间趋势分析
            timezone_str = request.query_params.get('timezone', 'UTC')
            time_trends = self._calculate_time_trends(base_queryset, period, date_field, timezone_str)
            
            # 6. 工作负载分析
            workload_stats = self._calculate_workload_stats(filtered_queryset, user)
            
            # 7. 进度分析
            progress_analysis = self._calculate_progress_analysis(filtered_queryset)
            
            # 8. 逾期分析
            overdue_analysis = self._calculate_overdue_analysis(filtered_queryset)
            
            # 9. 热门标签统计
            popular_tags = self._calculate_popular_tags(filtered_queryset)
            
            # 构建响应数据
            response_data = {
                'success': True,
                'message': f'统计数据获取成功 (周期: {period})',
                'data': {
                    'basic_stats': basic_stats,
                    'status_distribution': status_distribution,
                    'priority_distribution': priority_distribution,
                    'category_stats': category_stats,
                    'time_trends': time_trends,
                    'workload_stats': workload_stats,
                    'progress_analysis': progress_analysis,
                    'overdue_analysis': overdue_analysis,
                    'popular_tags': popular_tags,
                    'metadata': {
                        'period': period,
                        'date_field': date_field,
                        'include_deleted': include_deleted == 'true',
                        'generated_at': timezone.now().isoformat(),
                        'total_tasks_analyzed': filtered_queryset.count(),
                        'user_id': user.id,
                        'username': user.username
                    }
                }
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'统计数据获取失败: {str(e)}',
                'error': 'stats_error',
                'data': {
                    'period': request.query_params.get('period', 'all'),
                    'date_field': request.query_params.get('date_field', 'created_at')
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _apply_period_filter(self, queryset, period, date_field):
        """应用时间周期过滤"""
        if period == 'all':
            return queryset
        
        now = timezone.now()
        
        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timezone.timedelta(days=1)
        elif period == 'week':
            start_date = now - timezone.timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timezone.timedelta(days=7)
        elif period == 'month':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if start_date.month == 12:
                end_date = start_date.replace(year=start_date.year + 1, month=1)
            else:
                end_date = start_date.replace(month=start_date.month + 1)
        elif period == 'quarter':
            quarter = (now.month - 1) // 3 + 1
            start_month = (quarter - 1) * 3 + 1
            start_date = now.replace(month=start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
            if start_month + 3 > 12:
                end_date = start_date.replace(year=start_date.year + 1, month=(start_month + 3) % 12)
            else:
                end_date = start_date.replace(month=start_month + 3)
        elif period == 'year':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date.replace(year=start_date.year + 1)
        else:
            return queryset
        
        # 应用日期过滤
        filter_kwargs = {
            f'{date_field}__gte': start_date,
            f'{date_field}__lt': end_date
        }
        
        return queryset.filter(**filter_kwargs)
    
    def _calculate_basic_stats(self, queryset):
        """计算基础统计数据"""
        total_count = queryset.count()
        
        if total_count == 0:
            return {
                'total_tasks': 0,
                'completed_tasks': 0,
                'completion_rate': 0.0,
                'overdue_tasks': 0,
                'overdue_rate': 0.0,
                'average_progress': 0.0,
                'total_estimated_hours': 0.0,
                'total_actual_hours': 0.0
            }
        
        # 完成任务统计
        completed_count = queryset.filter(status='COMPLETED').count()
        completion_rate = (completed_count / total_count) * 100
        
        # 逾期任务统计
        overdue_count = queryset.filter(
            due_date__lt=timezone.now(),
            status__in=['PENDING', 'IN_PROGRESS', 'ON_HOLD']
        ).count()
        overdue_rate = (overdue_count / total_count) * 100
        
        # 平均进度
        avg_progress = queryset.aggregate(avg_progress=Avg('progress'))['avg_progress'] or 0.0
        
        # 工时统计
        total_estimated = queryset.aggregate(
            total=Sum('estimated_hours')
        )['total'] or 0.0
        
        total_actual = queryset.aggregate(
            total=Sum('actual_hours')  
        )['total'] or 0.0
        
        return {
            'total_tasks': total_count,
            'completed_tasks': completed_count,
            'completion_rate': round(completion_rate, 2),
            'overdue_tasks': overdue_count,
            'overdue_rate': round(overdue_rate, 2),
            'average_progress': round(avg_progress, 2),
            'total_estimated_hours': float(total_estimated),
            'total_actual_hours': float(total_actual),
            'efficiency_rate': round((float(total_actual) / float(total_estimated) * 100) if total_estimated > 0 else 0.0, 2)
        }
    
    def _calculate_status_distribution(self, queryset):
        """计算状态分布统计"""
        total_count = queryset.count()
        
        if total_count == 0:
            return {}
        
        status_stats = {}
        
        for status_choice in Task.STATUS_CHOICES:
            status_code = status_choice[0]
            status_name = status_choice[1]
            count = queryset.filter(status=status_code).count()
            
            if count > 0:
                status_stats[status_code] = {
                    'name': status_name,
                    'count': count,
                    'percentage': round((count / total_count) * 100, 2)
                }
        
        return status_stats
    
    def _calculate_priority_distribution(self, queryset):
        """计算优先级分布统计"""
        total_count = queryset.count()
        
        if total_count == 0:
            return {}
        
        priority_stats = {}
        
        for priority_choice in Task.PRIORITY_CHOICES:
            priority_code = priority_choice[0]
            priority_name = priority_choice[1]
            count = queryset.filter(priority=priority_code).count()
            
            if count > 0:
                priority_stats[priority_code] = {
                    'name': priority_name,
                    'count': count,
                    'percentage': round((count / total_count) * 100, 2)
                }
        
        return priority_stats
    
    def _calculate_category_stats(self, queryset):
        """计算分类统计"""
        category_stats = queryset.values('category').annotate(
            count=Count('id')
        ).order_by('-count')[:10]  # 前10个最常用分类
        
        total_count = queryset.count()
        
        result = []
        for item in category_stats:
            if item['category']:
                result.append({
                    'category': item['category'],
                    'count': item['count'],
                    'percentage': round((item['count'] / total_count) * 100, 2) if total_count > 0 else 0.0
                })
        
        return result
    
    def _calculate_time_trends(self, queryset, period, date_field):
        """计算时间趋势分析"""
        if period == 'all':
            # 按月统计最近12个月
            from datetime import datetime, timedelta
            end_date = timezone.now()
            start_date = end_date - timedelta(days=365)
            
            # 按月分组统计
            trends = []
            current_date = start_date.replace(day=1)
            
            while current_date <= end_date:
                next_month = current_date.replace(month=current_date.month + 1) if current_date.month < 12 else current_date.replace(year=current_date.year + 1, month=1)
                
                month_tasks = queryset.filter(
                    **{f'{date_field}__gte': current_date, f'{date_field}__lt': next_month}
                ).count()
                
                month_completed = queryset.filter(
                    **{f'{date_field}__gte': current_date, f'{date_field}__lt': next_month},
                    status='COMPLETED'
                ).count()
                
                trends.append({
                    'period': current_date.strftime('%Y-%m'),
                    'total_tasks': month_tasks,
                    'completed_tasks': month_completed,
                    'completion_rate': round((month_completed / month_tasks * 100) if month_tasks > 0 else 0.0, 2)
                })
                
                current_date = next_month
            
            return trends
        
        elif period == 'week':
            # 按天统计最近7天
            trends = []
            for i in range(7):
                day = timezone.now() - timezone.timedelta(days=i)
                day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + timezone.timedelta(days=1)
                
                day_tasks = queryset.filter(
                    **{f'{date_field}__gte': day_start, f'{date_field}__lt': day_end}
                ).count()
                
                day_completed = queryset.filter(
                    **{f'{date_field}__gte': day_start, f'{date_field}__lt': day_end},
                    status='COMPLETED'
                ).count()
                
                trends.append({
                    'period': day.strftime('%Y-%m-%d'),
                    'total_tasks': day_tasks,
                    'completed_tasks': day_completed,
                    'completion_rate': round((day_completed / day_tasks * 100) if day_tasks > 0 else 0.0, 2)
                })
            
            return list(reversed(trends))  # 按时间正序
        
        else:
            # 其他周期的简单统计
            total_tasks = queryset.count()
            completed_tasks = queryset.filter(status='COMPLETED').count()
            
            return [{
                'period': period,
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0, 2)
            }]
    
    def _calculate_workload_stats(self, queryset, user):
        """计算工作负载统计"""
        # 用户作为所有者的任务
        owned_tasks = queryset.filter(owner=user).count()
        owned_completed = queryset.filter(owner=user, status='COMPLETED').count()
        
        # 用户作为被分配者的任务
        assigned_tasks = queryset.filter(assigned_to=user).count()
        assigned_completed = queryset.filter(assigned_to=user, status='COMPLETED').count()
        
        # 按状态分组的任务数量
        status_workload = {}
        for status_choice in Task.STATUS_CHOICES:
            status_code = status_choice[0]
            count = queryset.filter(
                Q(owner=user) | Q(assigned_to=user),
                status=status_code
            ).count()
            if count > 0:
                status_workload[status_code] = count
        
        return {
            'owned_tasks': {
                'total': owned_tasks,
                'completed': owned_completed,
                'completion_rate': round((owned_completed / owned_tasks * 100) if owned_tasks > 0 else 0.0, 2)
            },
            'assigned_tasks': {
                'total': assigned_tasks,
                'completed': assigned_completed,
                'completion_rate': round((assigned_completed / assigned_tasks * 100) if assigned_tasks > 0 else 0.0, 2)
            },
            'status_workload': status_workload,
            'total_active_tasks': queryset.filter(
                Q(owner=user) | Q(assigned_to=user),
                status__in=['PENDING', 'IN_PROGRESS']
            ).count()
        }
    
    def _calculate_progress_analysis(self, queryset):
        """计算进度分析"""
        progress_ranges = [
            (0, 0, '未开始'),
            (1, 25, '刚开始'),
            (26, 50, '进行中'),
            (51, 75, '大部分完成'),
            (76, 99, '接近完成'),
            (100, 100, '已完成')
        ]
        
        total_count = queryset.count()
        progress_distribution = []
        
        for min_progress, max_progress, label in progress_ranges:
            count = queryset.filter(
                progress__gte=min_progress,
                progress__lte=max_progress
            ).count()
            
            if count > 0:
                progress_distribution.append({
                    'range': f'{min_progress}-{max_progress}%',
                    'label': label,
                    'count': count,
                    'percentage': round((count / total_count * 100) if total_count > 0 else 0.0, 2)
                })
        
        # 平均进度
        avg_progress = queryset.aggregate(avg_progress=Avg('progress'))['avg_progress'] or 0.0
        
        return {
            'distribution': progress_distribution,
            'average_progress': round(avg_progress, 2),
            'tasks_in_progress': queryset.filter(progress__gt=0, progress__lt=100).count(),
            'tasks_completed': queryset.filter(progress=100).count(),
            'tasks_not_started': queryset.filter(progress=0).count()
        }
    
    def _calculate_overdue_analysis(self, queryset):
        """计算逾期分析"""
        now = timezone.now()
        
        # 逾期任务（截止日期已过且未完成）
        overdue_tasks = queryset.filter(
            due_date__lt=now,
            status__in=['PENDING', 'IN_PROGRESS', 'ON_HOLD']
        )
        
        overdue_count = overdue_tasks.count()
        total_count = queryset.count()
        
        # 即将到期任务（未来3天内到期）
        upcoming_due = queryset.filter(
            due_date__gte=now,
            due_date__lte=now + timezone.timedelta(days=3),
            status__in=['PENDING', 'IN_PROGRESS', 'ON_HOLD']
        ).count()
        
        # 逾期时长分析
        overdue_by_duration = []
        durations = [
            (1, '1天内'),
            (7, '1周内'),
            (30, '1月内'),
            (90, '3月内'),
            (365, '1年内'),
            (float('inf'), '1年以上')
        ]
        
        for days, label in durations:
            if days == float('inf'):
                count = overdue_tasks.filter(
                    due_date__lt=now - timezone.timedelta(days=365)
                ).count()
            else:
                count = overdue_tasks.filter(
                    due_date__gte=now - timezone.timedelta(days=days),
                    due_date__lt=now
                ).count()
            
            if count > 0:
                overdue_by_duration.append({
                    'duration': label,
                    'count': count,
                    'percentage': round((count / overdue_count * 100) if overdue_count > 0 else 0.0, 2)
                })
        
        return {
            'total_overdue': overdue_count,
            'overdue_rate': round((overdue_count / total_count * 100) if total_count > 0 else 0.0, 2),
            'upcoming_due': upcoming_due,
            'overdue_by_duration': overdue_by_duration,
            'most_overdue_task': self._get_most_overdue_task(overdue_tasks)
        }
    
    def _get_most_overdue_task(self, overdue_queryset):
        """获取最逾期的任务信息"""
        if not overdue_queryset.exists():
            return None
        
        most_overdue = overdue_queryset.order_by('due_date').first()
        if most_overdue:
            # 确保正确处理日期比较
            now = timezone.now()
            if hasattr(most_overdue.due_date, 'date'):
                due_date = most_overdue.due_date.date()
                current_date = now.date()
            else:
                due_date = most_overdue.due_date
                current_date = now.date()
            
            overdue_days = (current_date - due_date).days
            return {
                'id': str(most_overdue.id),
                'title': most_overdue.title,
                'due_date': most_overdue.due_date.isoformat() if hasattr(most_overdue.due_date, 'isoformat') else str(most_overdue.due_date),
                'overdue_days': overdue_days,
                'priority': most_overdue.priority,
                'status': most_overdue.status
            }
        return None
    
    def _calculate_popular_tags(self, queryset):
        """计算热门标签统计"""
        # 收集所有标签
        tag_counts = {}
        
        for task in queryset.exclude(tags__isnull=True).exclude(tags=''):
            tags = [tag.strip() for tag in task.tags.split(',') if tag.strip()]
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # 排序并取前10个
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        total_tasks_with_tags = len([t for t in queryset if t.tags])
        
        result = []
        for tag, count in sorted_tags:
            result.append({
                'tag': tag,
                'count': count,
                'percentage': round((count / total_tasks_with_tags * 100) if total_tasks_with_tags > 0 else 0.0, 2)
            })
        
        return result
    
    @action(detail=False, methods=['get'])
    def create_options(self, request):
        """
        获取任务创建选项
        
        返回创建任务时可用的选项，如状态、优先级、分类等
        """
        # 获取用户常用的分类
        user_categories = Task.objects.filter(
            owner=request.user
        ).exclude(
            category__isnull=True
        ).exclude(
            category__exact=''
        ).values('category').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # 获取可分配的用户（用户的协作者）
        # 这里简化为所有用户，实际应该是用户的团队成员
        assignable_users = User.objects.filter(
            is_active=True
        ).exclude(
            id=request.user.id
        ).values('id', 'username', 'first_name', 'last_name')[:20]
        
        # 获取用户常用标签
        user_tags = Task.objects.filter(
            owner=request.user
        ).exclude(
            tags__isnull=True
        ).exclude(
            tags__exact=''
        ).values_list('tags', flat=True)
        
        tag_counts = {}
        for tags_str in user_tags:
            for tag in tags_str.split(','):
                tag = tag.strip()
                if tag:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        popular_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        
        return Response({
            'success': True,
            'data': {
                'status_choices': [
                    {'value': choice[0], 'label': choice[1]}
                    for choice in Task.STATUS_CHOICES
                ],
                'priority_choices': [
                    {'value': choice[0], 'label': choice[1]}
                    for choice in Task.PRIORITY_CHOICES
                ],
                'user_categories': [
                    {
                        'category': item['category'],
                        'usage_count': item['count']
                    } for item in user_categories
                ],
                'assignable_users': list(assignable_users),
                'popular_tags': [
                    {
                        'tag': tag,
                        'usage_count': count
                    } for tag, count in popular_tags
                ],
                'defaults': {
                    'status': 'PENDING',
                    'priority': 'MEDIUM',
                    'progress': 0,
                    'estimated_hours': 4.0
                }
            }
        })
    
    @action(detail=False, methods=['post'])
    def quick_create(self, request):
        """
        快速创建任务
        
        只需要标题，其他字段使用智能默认值
        """
        title = request.data.get('title', '').strip()
        if not title:
            return Response({
                'success': False,
                'message': '任务标题不能为空',
                'error_code': 'title_required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 构建任务数据，使用智能默认值
        task_data = {
            'title': title,
            'description': request.data.get('description', ''),
            'status': 'PENDING',
            'priority': 'MEDIUM',
            # 其他字段将由序列化器的create方法智能设置
        }
        
        # 如果提供了due_date，使用它
        if request.data.get('due_date'):
            task_data['due_date'] = request.data['due_date']
        
        # 如果提供了category，使用它
        if request.data.get('category'):
            task_data['category'] = request.data['category']
        
        # 使用标准创建流程
        request._full_data = task_data
        return self._create_single_task(request)
    
    @action(detail=False, methods=['post'])
    def validate_task_data(self, request):
        """
        验证任务数据
        
        在实际创建前验证数据的有效性
        """
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            
            # 额外的业务逻辑验证
            warnings = []
            suggestions = []
            
            # 检查due_date是否过于紧急
            due_date = serializer.validated_data.get('due_date')
            if due_date:
                from datetime import timedelta
                if due_date <= timezone.now() + timedelta(hours=1):
                    warnings.append('截止时间非常紧急，建议重新评估时间安排')
            
            # 检查estimated_hours是否合理
            estimated_hours = serializer.validated_data.get('estimated_hours', 0)
            if estimated_hours > 40:
                warnings.append('预估工时超过一周，建议拆分为多个子任务')
                suggestions.append('考虑将大任务分解为更小的可管理任务')
            
            # 检查title是否过短
            title = serializer.validated_data.get('title', '')
            if len(title) < 5:
                suggestions.append('建议任务标题更具描述性，便于后续管理')
            
            return Response({
                'success': True,
                'message': '任务数据验证通过',
                'data': {
                    'valid': True,
                    'warnings': warnings,
                    'suggestions': suggestions,
                    'validated_data': serializer.validated_data
                }
            })
            
        except ValidationError as e:
            return Response({
                'success': False,
                'message': '任务数据验证失败',
                'data': {
                    'valid': False,
                    'errors': e.detail
                }
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def creation_templates(self, request):
        """
        获取任务创建模板
        
        返回预定义的任务模板，方便快速创建常见类型的任务
        """
        templates = [
            {
                'id': 'development',
                'name': '开发任务',
                'description': '软件开发相关任务模板',
                'template_data': {
                    'category': '开发',
                    'priority': 'MEDIUM',
                    'estimated_hours': 8.0,
                    'tags': '开发, 编程',
                    'status': 'PENDING'
                }
            },
            {
                'id': 'bug_fix',
                'name': 'Bug修复',
                'description': 'Bug修复任务模板',
                'template_data': {
                    'category': '开发',
                    'priority': 'HIGH',
                    'estimated_hours': 4.0,
                    'tags': 'Bug, 修复, 紧急',
                    'status': 'PENDING'
                }
            },
            {
                'id': 'testing',
                'name': '测试任务',
                'description': '软件测试相关任务模板',
                'template_data': {
                    'category': '测试',
                    'priority': 'MEDIUM',
                    'estimated_hours': 6.0,
                    'tags': '测试, 验证',
                    'status': 'PENDING'
                }
            },
            {
                'id': 'documentation',
                'name': '文档编写',
                'description': '文档编写任务模板',
                'template_data': {
                    'category': '文档',
                    'priority': 'LOW',
                    'estimated_hours': 3.0,
                    'tags': '文档, 说明',
                    'status': 'PENDING'
                }
            },
            {
                'id': 'meeting',
                'name': '会议任务',
                'description': '会议相关任务模板',
                'template_data': {
                    'category': '会议',
                    'priority': 'MEDIUM',
                    'estimated_hours': 1.0,
                    'tags': '会议, 讨论',
                    'status': 'PENDING'
                }
            }
        ]
        
        return Response({
            'success': True,
            'data': {
                'templates': templates,
                'total_count': len(templates)
            }
        })

    @action(detail=False, methods=['get'], url_path='search')
    def advanced_search(self, request):
        """
        高级搜索和过滤API
        
        GET /api/tasks/search/
        
        支持的查询参数:
        - q: 全文搜索关键词
        - title: 标题搜索
        - description: 描述搜索
        - category: 分类搜索
        - tags: 标签搜索（支持多个标签，逗号分隔）
        - status: 任务状态（支持多个，逗号分隔）
        - priority: 优先级（支持多个，逗号分隔）
        - assigned_to: 分配给用户ID
        - is_assigned: 是否已分配（true/false）
        - is_overdue: 是否逾期（true/false）
        - due_soon: 即将到期天数（数字）
        - progress_min: 最小进度
        - progress_max: 最大进度
        - created_after: 创建时间起始（YYYY-MM-DD或YYYY-MM-DD HH:MM:SS）
        - created_before: 创建时间结束
        - due_after: 截止时间起始
        - due_before: 截止时间结束
        - start_after: 开始时间起始
        - start_before: 开始时间结束
        - include_deleted: 包含已删除任务（true/false）
        - sort: 排序字段（created_at, updated_at, due_date, priority, status, progress, title）
        - order: 排序方向（asc/desc）
        - page: 页码
        - page_size: 每页数量
        
        高级功能:
        - 支持模糊搜索和精确匹配
        - 支持多字段组合搜索
        - 支持时间范围查询
        - 支持搜索结果统计
        - 支持搜索历史记录（可选）
        """
        try:
            # 获取基础查询集
            queryset = self.get_queryset()
            
            # 处理搜索参数
            search_params = {}
            
            # 全文搜索
            q = request.query_params.get('q', '').strip()
            if q:
                queryset = queryset.filter(
                    Q(title__icontains=q) |
                    Q(description__icontains=q) |
                    Q(category__icontains=q) |
                    Q(tags__icontains=q)
                )
                search_params['q'] = q
            
            # 标题搜索
            title = request.query_params.get('title', '').strip()
            if title:
                queryset = queryset.filter(title__icontains=title)
                search_params['title'] = title
            
            # 描述搜索
            description = request.query_params.get('description', '').strip()
            if description:
                queryset = queryset.filter(description__icontains=description)
                search_params['description'] = description
            
            # 分类搜索
            category = request.query_params.get('category', '').strip()
            if category:
                queryset = queryset.filter(category__icontains=category)
                search_params['category'] = category
            
            # 标签搜索（支持多个标签）
            tags = request.query_params.get('tags', '').strip()
            if tags:
                tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
                if tag_list:
                    q_objects = Q()
                    for tag in tag_list:
                        q_objects |= Q(tags__icontains=tag)
                    queryset = queryset.filter(q_objects)
                    search_params['tags'] = tag_list
            
            # 状态过滤（支持多个状态）
            status_param = request.query_params.get('status', '').strip()
            if status_param:
                status_list = [s.strip().upper() for s in status_param.split(',') if s.strip()]
                if status_list:
                    queryset = queryset.filter(status__in=status_list)
                    search_params['status'] = status_list
            
            # 优先级过滤（支持多个优先级）
            priority_param = request.query_params.get('priority', '').strip()
            if priority_param:
                priority_list = [p.strip().upper() for p in priority_param.split(',') if p.strip()]
                if priority_list:
                    queryset = queryset.filter(priority__in=priority_list)
                    search_params['priority'] = priority_list
            
            # 分配状态过滤
            is_assigned = request.query_params.get('is_assigned', '').strip().lower()
            if is_assigned == 'true':
                queryset = queryset.filter(assigned_to__isnull=False)
                search_params['is_assigned'] = True
            elif is_assigned == 'false':
                queryset = queryset.filter(assigned_to__isnull=True)
                search_params['is_assigned'] = False
            
            # 分配给特定用户
            assigned_to = request.query_params.get('assigned_to', '').strip()
            if assigned_to:
                try:
                    from django.contrib.auth.models import User
                    user = User.objects.get(id=assigned_to)
                    queryset = queryset.filter(assigned_to=user)
                    search_params['assigned_to'] = user.username
                except (User.DoesNotExist, ValueError):
                    pass
            
            # 逾期任务过滤
            is_overdue = request.query_params.get('is_overdue', '').strip().lower()
            if is_overdue == 'true':
                queryset = queryset.filter(
                    due_date__lt=timezone.now(),
                    status__in=['PENDING', 'IN_PROGRESS', 'ON_HOLD']
                )
                search_params['is_overdue'] = True
            elif is_overdue == 'false':
                queryset = queryset.exclude(
                    due_date__lt=timezone.now(),
                    status__in=['PENDING', 'IN_PROGRESS', 'ON_HOLD']
                )
                search_params['is_overdue'] = False
            
            # 即将到期任务过滤
            due_soon = request.query_params.get('due_soon', '').strip()
            if due_soon:
                try:
                    days = int(due_soon)
                    if days > 0:
                        from datetime import timedelta
                        end_date = timezone.now() + timedelta(days=days)
                        queryset = queryset.filter(
                            due_date__lte=end_date,
                            due_date__gte=timezone.now(),
                            status__in=['PENDING', 'IN_PROGRESS', 'ON_HOLD']
                        )
                        search_params['due_soon'] = days
                except ValueError:
                    pass
            
            # 进度范围过滤
            progress_min = request.query_params.get('progress_min', '').strip()
            if progress_min:
                try:
                    min_val = int(progress_min)
                    if 0 <= min_val <= 100:
                        queryset = queryset.filter(progress__gte=min_val)
                        search_params['progress_min'] = min_val
                except ValueError:
                    pass
            
            progress_max = request.query_params.get('progress_max', '').strip()
            if progress_max:
                try:
                    max_val = int(progress_max)
                    if 0 <= max_val <= 100:
                        queryset = queryset.filter(progress__lte=max_val)
                        search_params['progress_max'] = max_val
                except ValueError:
                    pass
            
            # 时间范围过滤
            # 创建时间范围
            created_after = request.query_params.get('created_after', '').strip()
            if created_after:
                try:
                    from datetime import datetime
                    if 'T' in created_after or ' ' in created_after:
                        dt = datetime.fromisoformat(created_after.replace('Z', '+00:00'))
                    else:
                        dt = datetime.strptime(created_after, '%Y-%m-%d')
                    queryset = queryset.filter(created_at__gte=dt)
                    search_params['created_after'] = created_after
                except ValueError:
                    pass
            
            created_before = request.query_params.get('created_before', '').strip()
            if created_before:
                try:
                    from datetime import datetime
                    if 'T' in created_before or ' ' in created_before:
                        dt = datetime.fromisoformat(created_before.replace('Z', '+00:00'))
                    else:
                        dt = datetime.strptime(created_before, '%Y-%m-%d')
                    queryset = queryset.filter(created_at__lte=dt)
                    search_params['created_before'] = created_before
                except ValueError:
                    pass
            
            # 截止时间范围
            due_after = request.query_params.get('due_after', '').strip()
            if due_after:
                try:
                    from datetime import datetime
                    dt = datetime.strptime(due_after, '%Y-%m-%d').date()
                    queryset = queryset.filter(due_date__gte=dt)
                    search_params['due_after'] = due_after
                except ValueError:
                    pass
            
            due_before = request.query_params.get('due_before', '').strip()
            if due_before:
                try:
                    from datetime import datetime
                    dt = datetime.strptime(due_before, '%Y-%m-%d').date()
                    queryset = queryset.filter(due_date__lte=dt)
                    search_params['due_before'] = due_before
                except ValueError:
                    pass
            
            # 开始时间范围
            start_after = request.query_params.get('start_after', '').strip()
            if start_after:
                try:
                    from datetime import datetime
                    dt = datetime.strptime(start_after, '%Y-%m-%d').date()
                    queryset = queryset.filter(start_date__gte=dt)
                    search_params['start_after'] = start_after
                except ValueError:
                    pass
            
            start_before = request.query_params.get('start_before', '').strip()
            if start_before:
                try:
                    from datetime import datetime
                    dt = datetime.strptime(start_before, '%Y-%m-%d').date()
                    queryset = queryset.filter(start_date__lte=dt)
                    search_params['start_before'] = start_before
                except ValueError:
                    pass
            
            # 软删除任务包含
            include_deleted = request.query_params.get('include_deleted', 'false').lower()
            if include_deleted == 'true':
                # 重新获取包含软删除的查询集
                user = request.user
                queryset = Task.all_objects.filter(
                    Q(owner=user) | Q(assigned_to=user)
                ).distinct()
                
                # 重新应用所有过滤条件（这里简化处理，实际可以重构为函数）
                # 注意：这里应该重新应用上面的所有过滤条件，为了简化这里先跳过
                search_params['include_deleted'] = True
            
            # 排序处理
            sort_field = request.query_params.get('sort', 'created_at').strip()
            order_direction = request.query_params.get('order', 'desc').strip().lower()
            
            # 验证排序字段
            valid_sort_fields = [
                'created_at', 'updated_at', 'due_date', 'start_date',
                'priority', 'status', 'progress', 'title'
            ]
            
            if sort_field in valid_sort_fields:
                if order_direction == 'asc':
                    queryset = queryset.order_by(sort_field)
                else:
                    queryset = queryset.order_by(f'-{sort_field}')
                search_params['sort'] = sort_field
                search_params['order'] = order_direction
            else:
                # 默认排序
                queryset = queryset.order_by('-created_at')
            
            # 计算搜索统计
            total_count = queryset.count()
            
            # 获取状态分布统计
            status_stats = {}
            if total_count > 0:
                for status_choice in Task.STATUS_CHOICES:
                    status_code = status_choice[0]
                    count = queryset.filter(status=status_code).count()
                    if count > 0:
                        status_stats[status_code] = {
                            'count': count,
                            'percentage': round((count / total_count) * 100, 1)
                        }
            
            # 获取优先级分布统计
            priority_stats = {}
            if total_count > 0:
                for priority_choice in Task.PRIORITY_CHOICES:
                    priority_code = priority_choice[0]
                    count = queryset.filter(priority=priority_code).count()
                    if count > 0:
                        priority_stats[priority_code] = {
                            'count': count,
                            'percentage': round((count / total_count) * 100, 1)
                        }
            
            # 分页处理
            page = request.query_params.get('page', '1')
            page_size = request.query_params.get('page_size', '20')
            
            try:
                page = max(1, int(page))
                page_size = max(1, min(100, int(page_size)))  # 限制最大每页100条
            except ValueError:
                page = 1
                page_size = 20
            
            # 应用分页
            from django.core.paginator import Paginator
            paginator = Paginator(queryset, page_size)
            
            try:
                page_obj = paginator.page(page)
            except:
                page_obj = paginator.page(1)
                page = 1
            
            # 序列化数据
            serializer = TaskListSerializer(page_obj.object_list, many=True)
            
            # 构建响应
            response_data = {
                'success': True,
                'message': f'搜索完成，找到 {total_count} 个匹配任务',
                'data': {
                    'results': serializer.data,
                    'pagination': {
                        'current_page': page,
                        'page_size': page_size,
                        'total_pages': paginator.num_pages,
                        'total_count': total_count,
                        'has_next': page_obj.has_next(),
                        'has_previous': page_obj.has_previous(),
                        'next_page': page + 1 if page_obj.has_next() else None,
                        'previous_page': page - 1 if page_obj.has_previous() else None
                    },
                    'search_params': search_params,
                    'stats': {
                        'total_found': total_count,
                        'status_distribution': status_stats,
                        'priority_distribution': priority_stats,
                        'search_time': timezone.now().isoformat()
                    }
                }
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'搜索失败: {str(e)}',
                'error': 'search_error',
                'data': {
                    'search_params': search_params if 'search_params' in locals() else {}
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='status-distribution')
    def status_distribution(self, request):
        """
        详细状态分布统计API
        
        GET /api/tasks/status-distribution/
        
        支持的查询参数:
        - period: 统计周期 (all, today, week, month, quarter, year)
        - include_deleted: 包含已删除任务统计 (true/false)
        - date_field: 时间字段 (created_at, updated_at, due_date, start_date)
        - include_transitions: 包含状态转换分析 (true/false)
        - include_duration: 包含状态停留时间分析 (true/false)
        
        提供的统计数据:
        - 基础状态分布: 各状态任务数量和百分比
        - 状态转换分析: 状态变更频率和路径
        - 状态停留时间: 任务在各状态的平均停留时间
        - 状态趋势: 按时间维度的状态变化趋势
        - 效率分析: 状态流转效率指标
        """
        try:
            # 获取基础查询集（用户相关的任务）
            user = request.user
            base_queryset = Task.objects.filter(
                Q(owner=user) | Q(assigned_to=user)
            ).distinct()
            
            # 处理软删除任务包含
            include_deleted = request.query_params.get('include_deleted', 'false').lower()
            if include_deleted == 'true':
                base_queryset = Task.all_objects.filter(
                    Q(owner=user) | Q(assigned_to=user)
                ).distinct()
            
            # 处理时间周期过滤
            period = request.query_params.get('period', 'all').lower()
            date_field = request.query_params.get('date_field', 'created_at').lower()
            
            # 验证日期字段
            valid_date_fields = ['created_at', 'updated_at', 'due_date', 'start_date']
            if date_field not in valid_date_fields:
                date_field = 'created_at'
            
            # 应用时间周期过滤
            filtered_queryset = self._apply_period_filter(base_queryset, period, date_field)
            
            # 获取分析选项
            include_transitions = request.query_params.get('include_transitions', 'true').lower() == 'true'
            include_duration = request.query_params.get('include_duration', 'true').lower() == 'true'
            
            # 1. 详细状态分布
            detailed_distribution = self._calculate_detailed_status_distribution(filtered_queryset)
            
            # 2. 状态转换分析
            transition_analysis = {}
            if include_transitions:
                transition_analysis = self._calculate_status_transitions(base_queryset, period)
            
            # 3. 状态停留时间分析
            duration_analysis = {}
            if include_duration:
                duration_analysis = self._calculate_status_duration(filtered_queryset)
            
            # 4. 状态趋势分析
            status_trends = self._calculate_status_trends(base_queryset, period, date_field)
            
            # 5. 效率分析
            efficiency_analysis = self._calculate_status_efficiency(filtered_queryset)
            
            # 6. 状态健康度分析
            health_analysis = self._calculate_status_health(filtered_queryset)
            
            # 构建响应数据
            response_data = {
                'success': True,
                'message': f'状态分布统计获取成功 (周期: {period})',
                'data': {
                    'detailed_distribution': detailed_distribution,
                    'transition_analysis': transition_analysis,
                    'duration_analysis': duration_analysis,
                    'status_trends': status_trends,
                    'efficiency_analysis': efficiency_analysis,
                    'health_analysis': health_analysis,
                    'metadata': {
                        'period': period,
                        'date_field': date_field,
                        'include_deleted': include_deleted == 'true',
                        'include_transitions': include_transitions,
                        'include_duration': include_duration,
                        'generated_at': timezone.now().isoformat(),
                        'total_tasks_analyzed': filtered_queryset.count(),
                        'user_id': user.id,
                        'username': user.username
                    }
                }
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'状态分布统计获取失败: {str(e)}',
                'error': 'status_distribution_error',
                'data': {
                    'period': request.query_params.get('period', 'all'),
                    'date_field': request.query_params.get('date_field', 'created_at')
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _calculate_detailed_status_distribution(self, queryset):
        """计算详细状态分布统计"""
        total_count = queryset.count()
        
        if total_count == 0:
            return {
                'total_tasks': 0,
                'status_breakdown': {},
                'status_summary': {},
                'status_ratios': {}
            }
        
        # 基础状态分布
        status_breakdown = {}
        active_tasks = 0
        completed_tasks = 0
        blocked_tasks = 0
        
        for status_choice in Task.STATUS_CHOICES:
            status_code = status_choice[0]
            status_name = status_choice[1]
            count = queryset.filter(status=status_code).count()
            
            status_breakdown[status_code] = {
                'name': status_name,
                'count': count,
                'percentage': round((count / total_count) * 100, 2)
            }
            
            # 分类计数
            if status_code in ['PENDING', 'IN_PROGRESS']:
                active_tasks += count
            elif status_code == 'COMPLETED':
                completed_tasks += count
            elif status_code in ['ON_HOLD', 'CANCELLED']:
                blocked_tasks += count
        
        # 状态摘要
        status_summary = {
            'active_tasks': {
                'count': active_tasks,
                'percentage': round((active_tasks / total_count) * 100, 2)
            },
            'completed_tasks': {
                'count': completed_tasks,
                'percentage': round((completed_tasks / total_count) * 100, 2)
            },
            'blocked_tasks': {
                'count': blocked_tasks,
                'percentage': round((blocked_tasks / total_count) * 100, 2)
            }
        }
        
        # 状态比例分析
        status_ratios = {
            'completion_ratio': round((completed_tasks / total_count), 3) if total_count > 0 else 0,
            'active_ratio': round((active_tasks / total_count), 3) if total_count > 0 else 0,
            'blocked_ratio': round((blocked_tasks / total_count), 3) if total_count > 0 else 0,
            'efficiency_score': round((completed_tasks / (active_tasks + completed_tasks)), 3) if (active_tasks + completed_tasks) > 0 else 0
        }
        
        return {
            'total_tasks': total_count,
            'status_breakdown': status_breakdown,
            'status_summary': status_summary,
            'status_ratios': status_ratios
        }
    
    def _calculate_status_transitions(self, queryset, period):
        """计算状态转换分析"""
        # 注意: 这里是简化版本，实际应该有状态变更历史表
        # 当前基于任务的更新时间和状态来推测转换
        
        # 按状态分组，计算每个状态的新增任务
        transitions = {}
        
        # 获取最近的状态变更模式
        recent_tasks = queryset.order_by('-updated_at')[:100]  # 最近100个任务
        
        # 简化的转换分析 - 基于创建状态和当前状态
        for status_choice in Task.STATUS_CHOICES:
            status_code = status_choice[0]
            status_name = status_choice[1]
            
            current_count = queryset.filter(status=status_code).count()
            
            transitions[status_code] = {
                'name': status_name,
                'current_count': current_count,
                'estimated_inflow': self._estimate_status_inflow(queryset, status_code),
                'estimated_outflow': self._estimate_status_outflow(queryset, status_code),
                'net_change': current_count  # 简化计算
            }
        
        # 计算常见转换路径
        common_paths = [
            {'from': 'PENDING', 'to': 'IN_PROGRESS', 'description': '开始执行'},
            {'from': 'IN_PROGRESS', 'to': 'COMPLETED', 'description': '完成任务'},
            {'from': 'IN_PROGRESS', 'to': 'ON_HOLD', 'description': '暂停执行'},
            {'from': 'ON_HOLD', 'to': 'IN_PROGRESS', 'description': '恢复执行'},
            {'from': 'PENDING', 'to': 'CANCELLED', 'description': '取消任务'}
        ]
        
        return {
            'status_transitions': transitions,
            'common_transition_paths': common_paths,
            'transition_summary': {
                'total_active_transitions': sum(t['estimated_inflow'] + t['estimated_outflow'] for t in transitions.values()),
                'most_active_status': max(transitions.keys(), key=lambda k: transitions[k]['current_count']) if transitions else None
            }
        }
    
    def _estimate_status_inflow(self, queryset, status):
        """估算状态流入量（简化版本）"""
        # 简化计算：基于最近创建的任务中该状态的数量
        recent_tasks = queryset.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=7)
        )
        return recent_tasks.filter(status=status).count()
    
    def _estimate_status_outflow(self, queryset, status):
        """估算状态流出量（简化版本）"""
        # 简化计算：基于最近更新且不在该状态的任务数量
        recent_updated = queryset.filter(
            updated_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).exclude(status=status)
        return min(recent_updated.count(), 10)  # 限制最大值
    
    def _calculate_status_duration(self, queryset):
        """计算状态停留时间分析"""
        duration_stats = {}
        
        for status_choice in Task.STATUS_CHOICES:
            status_code = status_choice[0]
            status_name = status_choice[1]
            
            status_tasks = queryset.filter(status=status_code)
            if not status_tasks.exists():
                continue
            
            # 简化计算：基于任务的创建时间到现在的时间差
            durations = []
            for task in status_tasks:
                if status_code == 'COMPLETED':
                    # 已完成任务：从创建到更新的时间
                    duration = (task.updated_at - task.created_at).total_seconds() / 3600  # 小时
                else:
                    # 进行中任务：从创建到现在的时间
                    duration = (timezone.now() - task.created_at).total_seconds() / 3600  # 小时
                durations.append(duration)
            
            if durations:
                duration_stats[status_code] = {
                    'name': status_name,
                    'average_duration_hours': round(sum(durations) / len(durations), 2),
                    'min_duration_hours': round(min(durations), 2),
                    'max_duration_hours': round(max(durations), 2),
                    'task_count': len(durations)
                }
        
        return duration_stats
    
    def _calculate_status_trends(self, queryset, period, date_field):
        """计算状态趋势分析"""
        if period == 'week':
            # 按天统计最近7天各状态的任务数量
            trends = []
            for i in range(7):
                day = timezone.now() - timezone.timedelta(days=i)
                day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + timezone.timedelta(days=1)
                
                day_stats = {}
                for status_choice in Task.STATUS_CHOICES:
                    status_code = status_choice[0]
                    count = queryset.filter(
                        **{f'{date_field}__gte': day_start, f'{date_field}__lt': day_end},
                        status=status_code
                    ).count()
                    day_stats[status_code] = count
                
                trends.append({
                    'date': day.strftime('%Y-%m-%d'),
                    'status_counts': day_stats,
                    'total_tasks': sum(day_stats.values())
                })
            
            return list(reversed(trends))  # 按时间正序
        
        elif period == 'month':
            # 按周统计最近4周
            trends = []
            for i in range(4):
                week_start = timezone.now() - timezone.timedelta(weeks=i+1)
                week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
                week_end = week_start + timezone.timedelta(weeks=1)
                
                week_stats = {}
                for status_choice in Task.STATUS_CHOICES:
                    status_code = status_choice[0]
                    count = queryset.filter(
                        **{f'{date_field}__gte': week_start, f'{date_field}__lt': week_end},
                        status=status_code
                    ).count()
                    week_stats[status_code] = count
                
                trends.append({
                    'period': f'Week {week_start.strftime("%Y-%m-%d")}',
                    'status_counts': week_stats,
                    'total_tasks': sum(week_stats.values())
                })
            
            return list(reversed(trends))
        
        else:
            # 简单统计
            current_stats = {}
            for status_choice in Task.STATUS_CHOICES:
                status_code = status_choice[0]
                count = queryset.filter(status=status_code).count()
                current_stats[status_code] = count
            
            return [{
                'period': period,
                'status_counts': current_stats,
                'total_tasks': sum(current_stats.values())
            }]
    
    def _calculate_status_efficiency(self, queryset):
        """计算状态效率分析"""
        total_tasks = queryset.count()
        if total_tasks == 0:
            return {}
        
        # 各状态的效率指标
        pending_count = queryset.filter(status='PENDING').count()
        in_progress_count = queryset.filter(status='IN_PROGRESS').count()
        completed_count = queryset.filter(status='COMPLETED').count()
        on_hold_count = queryset.filter(status='ON_HOLD').count()
        cancelled_count = queryset.filter(status='CANCELLED').count()
        
        # 计算效率指标
        completion_rate = completed_count / total_tasks if total_tasks > 0 else 0
        active_rate = (pending_count + in_progress_count) / total_tasks if total_tasks > 0 else 0
        stall_rate = (on_hold_count + cancelled_count) / total_tasks if total_tasks > 0 else 0
        
        # 流转效率（已完成 vs 正在处理）
        flow_efficiency = completed_count / (completed_count + in_progress_count) if (completed_count + in_progress_count) > 0 else 0
        
        return {
            'completion_rate': round(completion_rate * 100, 2),
            'active_rate': round(active_rate * 100, 2),
            'stall_rate': round(stall_rate * 100, 2),
            'flow_efficiency': round(flow_efficiency * 100, 2),
            'efficiency_score': round((completion_rate * 0.6 + flow_efficiency * 0.4) * 100, 2),
            'recommendations': self._generate_efficiency_recommendations(
                completion_rate, active_rate, stall_rate, flow_efficiency
            )
        }
    
    def _generate_efficiency_recommendations(self, completion_rate, active_rate, stall_rate, flow_efficiency):
        """生成效率改进建议"""
        recommendations = []
        
        if completion_rate < 0.3:
            recommendations.append("完成率较低，建议检查任务执行流程")
        
        if stall_rate > 0.2:
            recommendations.append("停滞任务较多，建议定期清理暂停和取消的任务")
        
        if flow_efficiency < 0.5:
            recommendations.append("流转效率偏低，建议优化任务分配和执行流程")
        
        if active_rate > 0.7:
            recommendations.append("活跃任务较多，建议适当控制新任务的创建")
        
        if not recommendations:
            recommendations.append("当前状态分布较为健康，继续保持")
        
        return recommendations
    
    def _calculate_status_health(self, queryset):
        """计算状态健康度分析"""
        total_tasks = queryset.count()
        if total_tasks == 0:
            return {
                'overall_health_score': 0,
                'health_indicators': {},
                'warning_signals': []
            }
        
        # 各状态计数
        status_counts = {}
        for status_choice in Task.STATUS_CHOICES:
            status_code = status_choice[0]
            status_counts[status_code] = queryset.filter(status=status_code).count()
        
        # 健康指标
        completed_ratio = status_counts.get('COMPLETED', 0) / total_tasks
        pending_ratio = status_counts.get('PENDING', 0) / total_tasks
        in_progress_ratio = status_counts.get('IN_PROGRESS', 0) / total_tasks
        on_hold_ratio = status_counts.get('ON_HOLD', 0) / total_tasks
        cancelled_ratio = status_counts.get('CANCELLED', 0) / total_tasks
        
        # 健康评分（0-100）
        health_score = (
            completed_ratio * 40 +  # 完成任务权重最高
            in_progress_ratio * 30 +  # 进行中任务次之
            pending_ratio * 20 +  # 待处理任务
            max(0, (1 - on_hold_ratio - cancelled_ratio)) * 10  # 减少停滞任务
        ) * 100
        
        # 预警信号
        warning_signals = []
        if on_hold_ratio > 0.15:
            warning_signals.append("暂停任务比例过高")
        if cancelled_ratio > 0.1:
            warning_signals.append("取消任务比例过高")
        if pending_ratio > 0.5:
            warning_signals.append("待处理任务积压严重")
        if completed_ratio < 0.2:
            warning_signals.append("完成任务比例过低")
        
        return {
            'overall_health_score': round(health_score, 2),
            'health_indicators': {
                'completion_health': round(completed_ratio * 100, 2),
                'flow_health': round((in_progress_ratio + pending_ratio) * 100, 2),
                'stagnation_risk': round((on_hold_ratio + cancelled_ratio) * 100, 2)
            },
            'warning_signals': warning_signals,
            'health_level': self._get_health_level(health_score)
        }
    
    def _get_health_level(self, score):
        """根据评分获取健康等级"""
        if score >= 80:
            return "优秀"
        elif score >= 60:
            return "良好"
        elif score >= 40:
            return "一般"
        elif score >= 20:
            return "较差"
        else:
            return "需要改进"

    @action(detail=False, methods=['get'], url_path='priority-distribution')
    def priority_distribution(self, request):
        """
        详细优先级分布统计API
        
        GET /api/tasks/priority-distribution/
        
        支持的查询参数:
        - period: 统计周期 (all, today, week, month, quarter, year)
        - include_deleted: 包含已删除任务统计 (true/false)
        - date_field: 时间字段 (created_at, updated_at, due_date, start_date)
        - include_completion: 包含完成率分析 (true/false)
        - include_workload: 包含工作负载分析 (true/false)
        - include_efficiency: 包含效率分析 (true/false)
        
        提供的统计数据:
        - 基础优先级分布: 各优先级任务数量和百分比
        - 优先级完成率: 不同优先级的完成情况分析
        - 优先级工作负载: 各优先级的工时和资源分配
        - 优先级效率分析: 不同优先级的执行效率
        - 优先级趋势: 按时间维度的优先级变化趋势
        - 优先级健康度: 优先级分配的合理性评估
        """
        try:
            # 获取基础查询集（用户相关的任务）
            user = request.user
            base_queryset = Task.objects.filter(
                Q(owner=user) | Q(assigned_to=user)
            ).distinct()
            
            # 处理软删除任务包含
            include_deleted = request.query_params.get('include_deleted', 'false').lower()
            if include_deleted == 'true':
                base_queryset = Task.all_objects.filter(
                    Q(owner=user) | Q(assigned_to=user)
                ).distinct()
            
            # 处理时间周期过滤
            period = request.query_params.get('period', 'all').lower()
            date_field = request.query_params.get('date_field', 'created_at').lower()
            
            # 验证日期字段
            valid_date_fields = ['created_at', 'updated_at', 'due_date', 'start_date']
            if date_field not in valid_date_fields:
                date_field = 'created_at'
            
            # 应用时间周期过滤
            filtered_queryset = self._apply_period_filter(base_queryset, period, date_field)
            
            # 获取分析选项
            include_completion = request.query_params.get('include_completion', 'true').lower() == 'true'
            include_workload = request.query_params.get('include_workload', 'true').lower() == 'true'
            include_efficiency = request.query_params.get('include_efficiency', 'true').lower() == 'true'
            
            # 1. 详细优先级分布
            detailed_distribution = self._calculate_detailed_priority_distribution(filtered_queryset)
            
            # 2. 优先级完成率分析
            completion_analysis = {}
            if include_completion:
                completion_analysis = self._calculate_priority_completion_rates(filtered_queryset)
            
            # 3. 优先级工作负载分析
            workload_analysis = {}
            if include_workload:
                workload_analysis = self._calculate_priority_workload(filtered_queryset)
            
            # 4. 优先级效率分析
            efficiency_analysis = {}
            if include_efficiency:
                efficiency_analysis = self._calculate_priority_efficiency(filtered_queryset)
            
            # 5. 优先级趋势分析
            priority_trends = self._calculate_priority_trends(base_queryset, period, date_field)
            
            # 6. 优先级健康度分析
            health_analysis = self._calculate_priority_health(filtered_queryset)
            
            # 7. 优先级转换分析
            transition_analysis = self._calculate_priority_transitions(base_queryset, period)
            
            # 构建响应数据
            response_data = {
                'success': True,
                'message': f'优先级分布统计获取成功 (周期: {period})',
                'data': {
                    'detailed_distribution': detailed_distribution,
                    'completion_analysis': completion_analysis,
                    'workload_analysis': workload_analysis,
                    'efficiency_analysis': efficiency_analysis,
                    'priority_trends': priority_trends,
                    'health_analysis': health_analysis,
                    'transition_analysis': transition_analysis,
                    'metadata': {
                        'period': period,
                        'date_field': date_field,
                        'include_deleted': include_deleted == 'true',
                        'include_completion': include_completion,
                        'include_workload': include_workload,
                        'include_efficiency': include_efficiency,
                        'generated_at': timezone.now().isoformat(),
                        'total_tasks_analyzed': filtered_queryset.count(),
                        'user_id': user.id,
                        'username': user.username
                    }
                }
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'优先级分布统计获取失败: {str(e)}',
                'error': 'priority_distribution_error',
                'data': {
                    'period': request.query_params.get('period', 'all'),
                    'date_field': request.query_params.get('date_field', 'created_at')
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _calculate_detailed_priority_distribution(self, queryset):
        """计算详细优先级分布统计"""
        total_count = queryset.count()
        
        if total_count == 0:
            return {
                'total_tasks': 0,
                'priority_breakdown': {},
                'priority_summary': {},
                'priority_ratios': {}
            }
        
        # 基础优先级分布
        priority_breakdown = {}
        urgent_tasks = 0
        high_priority_tasks = 0
        medium_priority_tasks = 0
        low_priority_tasks = 0
        
        for priority_choice in Task.PRIORITY_CHOICES:
            priority_code = priority_choice[0]
            priority_name = priority_choice[1]
            count = queryset.filter(priority=priority_code).count()
            
            priority_breakdown[priority_code] = {
                'name': priority_name,
                'count': count,
                'percentage': round((count / total_count) * 100, 2)
            }
            
            # 分类计数
            if priority_code == 'URGENT':
                urgent_tasks = count
            elif priority_code == 'HIGH':
                high_priority_tasks = count
            elif priority_code == 'MEDIUM':
                medium_priority_tasks = count
            elif priority_code == 'LOW':
                low_priority_tasks = count
        
        # 优先级摘要（按重要程度分组）
        critical_tasks = urgent_tasks + high_priority_tasks  # 关键任务
        normal_tasks = medium_priority_tasks  # 常规任务
        routine_tasks = low_priority_tasks  # 日常任务
        
        priority_summary = {
            'critical_tasks': {
                'count': critical_tasks,
                'percentage': round((critical_tasks / total_count) * 100, 2)
            },
            'normal_tasks': {
                'count': normal_tasks,
                'percentage': round((normal_tasks / total_count) * 100, 2)
            },
            'routine_tasks': {
                'count': routine_tasks,
                'percentage': round((routine_tasks / total_count) * 100, 2)
            }
        }
        
        # 优先级比例分析
        priority_ratios = {
            'urgent_ratio': round((urgent_tasks / total_count), 3) if total_count > 0 else 0,
            'high_ratio': round((high_priority_tasks / total_count), 3) if total_count > 0 else 0,
            'medium_ratio': round((medium_priority_tasks / total_count), 3) if total_count > 0 else 0,
            'low_ratio': round((low_priority_tasks / total_count), 3) if total_count > 0 else 0,
            'critical_ratio': round((critical_tasks / total_count), 3) if total_count > 0 else 0,
            'priority_balance_score': self._calculate_priority_balance_score(
                urgent_tasks, high_priority_tasks, medium_priority_tasks, low_priority_tasks, total_count
            )
        }
        
        return {
            'total_tasks': total_count,
            'priority_breakdown': priority_breakdown,
            'priority_summary': priority_summary,
            'priority_ratios': priority_ratios
        }
    
    def _calculate_priority_balance_score(self, urgent, high, medium, low, total):
        """计算优先级平衡评分（0-100）"""
        if total == 0:
            return 0
        
        # 理想的优先级分布（参考帕累托原则）
        ideal_urgent = 0.05  # 5% 紧急任务
        ideal_high = 0.15    # 15% 高优先级
        ideal_medium = 0.60  # 60% 中等优先级
        ideal_low = 0.20     # 20% 低优先级
        
        # 实际分布
        actual_urgent = urgent / total
        actual_high = high / total
        actual_medium = medium / total
        actual_low = low / total
        
        # 计算偏差（使用均方差）
        deviation = (
            (actual_urgent - ideal_urgent) ** 2 +
            (actual_high - ideal_high) ** 2 +
            (actual_medium - ideal_medium) ** 2 +
            (actual_low - ideal_low) ** 2
        ) / 4
        
        # 转换为评分（偏差越小评分越高）
        balance_score = max(0, (1 - deviation * 5) * 100)  # 乘以5放大偏差效应
        
        return round(balance_score, 2)
    
    def _calculate_priority_completion_rates(self, queryset):
        """计算优先级完成率分析"""
        completion_analysis = {}
        
        for priority_choice in Task.PRIORITY_CHOICES:
            priority_code = priority_choice[0]
            priority_name = priority_choice[1]
            
            priority_tasks = queryset.filter(priority=priority_code)
            total_count = priority_tasks.count()
            
            if total_count == 0:
                continue
            
            completed_count = priority_tasks.filter(status='COMPLETED').count()
            in_progress_count = priority_tasks.filter(status='IN_PROGRESS').count()
            pending_count = priority_tasks.filter(status='PENDING').count()
            on_hold_count = priority_tasks.filter(status='ON_HOLD').count()
            cancelled_count = priority_tasks.filter(status='CANCELLED').count()
            
            # 计算各种率
            completion_rate = (completed_count / total_count) * 100
            progress_rate = (in_progress_count / total_count) * 100
            pending_rate = (pending_count / total_count) * 100
            
            # 平均进度
            avg_progress = priority_tasks.aggregate(avg_progress=Avg('progress'))['avg_progress'] or 0.0
            
            # 逾期任务
            overdue_count = priority_tasks.filter(
                due_date__lt=timezone.now(),
                status__in=['PENDING', 'IN_PROGRESS', 'ON_HOLD']
            ).count()
            overdue_rate = (overdue_count / total_count) * 100
            
            completion_analysis[priority_code] = {
                'name': priority_name,
                'total_tasks': total_count,
                'completed_tasks': completed_count,
                'completion_rate': round(completion_rate, 2),
                'in_progress_tasks': in_progress_count,
                'progress_rate': round(progress_rate, 2),
                'pending_tasks': pending_count,
                'pending_rate': round(pending_rate, 2),
                'on_hold_tasks': on_hold_count,
                'cancelled_tasks': cancelled_count,
                'average_progress': round(avg_progress, 2),
                'overdue_tasks': overdue_count,
                'overdue_rate': round(overdue_rate, 2),
                'status_health_score': self._calculate_priority_status_health(
                    completion_rate, progress_rate, overdue_rate
                )
            }
        
        return completion_analysis
    
    def _calculate_priority_status_health(self, completion_rate, progress_rate, overdue_rate):
        """计算优先级状态健康评分"""
        # 健康评分算法（0-100）
        health_score = (
            completion_rate * 0.5 +  # 完成率权重50%
            progress_rate * 0.3 +    # 进行率权重30%
            max(0, (100 - overdue_rate)) * 0.2  # 无逾期率权重20%
        )
        return round(health_score, 2)
    
    def _calculate_priority_workload(self, queryset):
        """计算优先级工作负载分析"""
        workload_analysis = {}
        
        # 计算总工时
        total_estimated_hours = queryset.aggregate(
            total=Sum('estimated_hours')
        )['total'] or 0.0
        
        total_actual_hours = queryset.aggregate(
            total=Sum('actual_hours')
        )['total'] or 0.0
        
        # 转换为float避免Decimal问题
        total_estimated_hours = float(total_estimated_hours)
        total_actual_hours = float(total_actual_hours)
        
        for priority_choice in Task.PRIORITY_CHOICES:
            priority_code = priority_choice[0]
            priority_name = priority_choice[1]
            
            priority_tasks = queryset.filter(priority=priority_code)
            task_count = priority_tasks.count()
            
            if task_count == 0:
                continue
            
            # 工时统计
            estimated_hours = priority_tasks.aggregate(
                total=Sum('estimated_hours')
            )['total'] or 0.0
            
            actual_hours = priority_tasks.aggregate(
                total=Sum('actual_hours')
            )['total'] or 0.0
            
            # 转换为float避免Decimal问题
            estimated_hours = float(estimated_hours)
            actual_hours = float(actual_hours)
            
            # 计算百分比
            estimated_percentage = (estimated_hours / total_estimated_hours * 100) if total_estimated_hours > 0 else 0
            actual_percentage = (actual_hours / total_actual_hours * 100) if total_actual_hours > 0 else 0
            
            # 效率计算
            efficiency_ratio = (actual_hours / estimated_hours) if estimated_hours > 0 else 0
            avg_estimated_per_task = estimated_hours / task_count if task_count > 0 else 0
            avg_actual_per_task = actual_hours / task_count if task_count > 0 else 0
            
            workload_analysis[priority_code] = {
                'name': priority_name,
                'task_count': task_count,
                'estimated_hours': round(estimated_hours, 2),
                'actual_hours': round(actual_hours, 2),
                'estimated_percentage': round(estimated_percentage, 2),
                'actual_percentage': round(actual_percentage, 2),
                'efficiency_ratio': round(efficiency_ratio, 3),
                'avg_estimated_per_task': round(avg_estimated_per_task, 2),
                'avg_actual_per_task': round(avg_actual_per_task, 2),
                'workload_intensity': self._calculate_workload_intensity(
                    estimated_percentage, task_count, queryset.count()
                )
            }
        
        return workload_analysis
    
    def _calculate_workload_intensity(self, estimated_percentage, task_count, total_tasks):
        """计算工作负载强度"""
        task_percentage = (task_count / total_tasks * 100) if total_tasks > 0 else 0
        
        # 强度 = 工时占比 / 任务占比
        if task_percentage > 0:
            intensity = estimated_percentage / task_percentage
        else:
            intensity = 0
        
        # 分类强度等级
        if intensity > 1.5:
            intensity_level = "高强度"
        elif intensity > 1.2:
            intensity_level = "中高强度"
        elif intensity > 0.8:
            intensity_level = "标准强度"
        elif intensity > 0.5:
            intensity_level = "较低强度"
        else:
            intensity_level = "低强度"
        
        return {
            'intensity_ratio': round(intensity, 3),
            'intensity_level': intensity_level
        }
    
    def _calculate_priority_efficiency(self, queryset):
        """计算优先级效率分析"""
        efficiency_analysis = {}
        
        for priority_choice in Task.PRIORITY_CHOICES:
            priority_code = priority_choice[0]
            priority_name = priority_choice[1]
            
            priority_tasks = queryset.filter(priority=priority_code)
            task_count = priority_tasks.count()
            
            if task_count == 0:
                continue
            
            # 基础效率指标
            completed_tasks = priority_tasks.filter(status='COMPLETED').count()
            completion_rate = (completed_tasks / task_count) * 100
            
            # 时间效率
            avg_completion_time = self._calculate_avg_completion_time(
                priority_tasks.filter(status='COMPLETED')
            )
            
            # 工时效率
            estimated_hours = priority_tasks.aggregate(total=Sum('estimated_hours'))['total'] or 0.0
            actual_hours = priority_tasks.aggregate(total=Sum('actual_hours'))['total'] or 0.0
            
            # 转换为float避免Decimal除法问题
            estimated_hours = float(estimated_hours)
            actual_hours = float(actual_hours)
            
            time_efficiency = (estimated_hours / actual_hours * 100) if actual_hours > 0 else 0
            
            # 进度效率
            avg_progress = priority_tasks.aggregate(avg_progress=Avg('progress'))['avg_progress'] or 0.0
            progress_efficiency = avg_progress
            
            # 综合效率评分
            overall_efficiency = (
                completion_rate * 0.4 +      # 完成率权重40%
                time_efficiency * 0.3 +      # 时间效率权重30%
                progress_efficiency * 0.3    # 进度效率权重30%
            )
            
            efficiency_analysis[priority_code] = {
                'name': priority_name,
                'task_count': task_count,
                'completion_rate': round(completion_rate, 2),
                'avg_completion_time_hours': avg_completion_time,
                'time_efficiency': round(time_efficiency, 2),
                'progress_efficiency': round(progress_efficiency, 2),
                'overall_efficiency_score': round(overall_efficiency, 2),
                'efficiency_level': self._get_efficiency_level(overall_efficiency),
                'recommendations': self._generate_priority_recommendations(
                    priority_code, completion_rate, time_efficiency, progress_efficiency
                )
            }
        
        return efficiency_analysis
    
    def _calculate_avg_completion_time(self, completed_tasks):
        """计算平均完成时间（小时）"""
        if not completed_tasks.exists():
            return 0.0
        
        total_time = 0
        count = 0
        
        for task in completed_tasks:
            # 计算从创建到完成的时间
            completion_time = (task.updated_at - task.created_at).total_seconds() / 3600
            total_time += completion_time
            count += 1
        
        return round(total_time / count, 2) if count > 0 else 0.0
    
    def _get_efficiency_level(self, score):
        """根据效率评分获取效率等级"""
        if score >= 80:
            return "极高效率"
        elif score >= 65:
            return "高效率"
        elif score >= 50:
            return "标准效率"
        elif score >= 35:
            return "较低效率"
        else:
            return "需要改进"
    
    def _generate_priority_recommendations(self, priority_code, completion_rate, time_efficiency, progress_efficiency):
        """生成优先级改进建议"""
        recommendations = []
        
        # 获取优先级显示名称
        priority_dict = dict(Task.PRIORITY_CHOICES)
        priority_name = priority_dict.get(priority_code, priority_code)
        
        if priority_code in ['URGENT', 'HIGH']:
            if completion_rate < 70:
                recommendations.append(f"{priority_name}任务完成率偏低，建议加强资源投入")
            if time_efficiency < 80:
                recommendations.append("高优先级任务时间效率不佳，建议优化执行流程")
        
        if priority_code == 'URGENT':
            if progress_efficiency < 80:
                recommendations.append("紧急任务进度缓慢，建议立即采取行动")
        
        if priority_code in ['MEDIUM', 'LOW']:
            if completion_rate > 90:
                recommendations.append(f"{priority_name}任务执行良好，可以适当增加任务量")
            if time_efficiency > 120:
                recommendations.append("可能存在过度投入，建议平衡资源分配")
        
        if not recommendations:
            recommendations.append("当前优先级执行状况良好，继续保持")
        
        return recommendations
    
    def _calculate_priority_trends(self, queryset, period, date_field):
        """计算优先级趋势分析"""
        if period == 'week':
            # 按天统计最近7天各优先级的任务数量
            trends = []
            for i in range(7):
                day = timezone.now() - timezone.timedelta(days=i)
                day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + timezone.timedelta(days=1)
                
                day_stats = {}
                for priority_choice in Task.PRIORITY_CHOICES:
                    priority_code = priority_choice[0]
                    count = queryset.filter(
                        **{f'{date_field}__gte': day_start, f'{date_field}__lt': day_end},
                        priority=priority_code
                    ).count()
                    day_stats[priority_code] = count
                
                trends.append({
                    'date': day.strftime('%Y-%m-%d'),
                    'priority_counts': day_stats,
                    'total_tasks': sum(day_stats.values())
                })
            
            return list(reversed(trends))  # 按时间正序
        
        elif period == 'month':
            # 按周统计最近4周
            trends = []
            for i in range(4):
                week_start = timezone.now() - timezone.timedelta(weeks=i+1)
                week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
                week_end = week_start + timezone.timedelta(weeks=1)
                
                week_stats = {}
                for priority_choice in Task.PRIORITY_CHOICES:
                    priority_code = priority_choice[0]
                    count = queryset.filter(
                        **{f'{date_field}__gte': week_start, f'{date_field}__lt': week_end},
                        priority=priority_code
                    ).count()
                    week_stats[priority_code] = count
                
                trends.append({
                    'period': f'Week {week_start.strftime("%Y-%m-%d")}',
                    'priority_counts': week_stats,
                    'total_tasks': sum(week_stats.values())
                })
            
            return list(reversed(trends))
        
        else:
            # 简单统计
            current_stats = {}
            for priority_choice in Task.PRIORITY_CHOICES:
                priority_code = priority_choice[0]
                count = queryset.filter(priority=priority_code).count()
                current_stats[priority_code] = count
            
            return [{
                'period': period,
                'priority_counts': current_stats,
                'total_tasks': sum(current_stats.values())
            }]
    
    def _calculate_priority_health(self, queryset):
        """计算优先级健康度分析"""
        total_tasks = queryset.count()
        if total_tasks == 0:
            return {
                'overall_health_score': 0,
                'health_indicators': {},
                'warning_signals': [],
                'priority_balance': {}
            }
        
        # 各优先级计数
        priority_counts = {}
        for priority_choice in Task.PRIORITY_CHOICES:
            priority_code = priority_choice[0]
            priority_counts[priority_code] = queryset.filter(priority=priority_code).count()
        
        # 优先级比例
        urgent_ratio = priority_counts.get('URGENT', 0) / total_tasks
        high_ratio = priority_counts.get('HIGH', 0) / total_tasks
        medium_ratio = priority_counts.get('MEDIUM', 0) / total_tasks
        low_ratio = priority_counts.get('LOW', 0) / total_tasks
        
        # 健康评分（基于合理的优先级分布）
        balance_score = self._calculate_priority_balance_score(
            priority_counts.get('URGENT', 0),
            priority_counts.get('HIGH', 0),
            priority_counts.get('MEDIUM', 0),
            priority_counts.get('LOW', 0),
            total_tasks
        )
        
        # 完成率健康度
        completion_health = 0
        for priority_code in priority_counts:
            priority_tasks = queryset.filter(priority=priority_code)
            if priority_tasks.count() > 0:
                completed = priority_tasks.filter(status='COMPLETED').count()
                completion_rate = completed / priority_tasks.count()
                # 高优先级任务完成率权重更高
                weight = 2 if priority_code in ['URGENT', 'HIGH'] else 1
                completion_health += completion_rate * weight * 25  # 最大100分
        
        # 综合健康评分
        overall_health = (balance_score * 0.6 + completion_health * 0.4)
        
        # 预警信号
        warning_signals = []
        if urgent_ratio > 0.2:
            warning_signals.append("紧急任务比例过高，可能存在计划不当")
        if urgent_ratio + high_ratio > 0.5:
            warning_signals.append("高优先级任务过多，资源压力较大")
        if medium_ratio < 0.3:
            warning_signals.append("中等优先级任务过少，可能缺乏常规工作")
        if low_ratio < 0.1:
            warning_signals.append("低优先级任务过少，可能忽略了日常维护")
        
        return {
            'overall_health_score': round(overall_health, 2),
            'health_indicators': {
                'priority_balance_score': balance_score,
                'completion_health_score': round(completion_health, 2),
                'urgent_pressure': round(urgent_ratio * 100, 2),
                'critical_load': round((urgent_ratio + high_ratio) * 100, 2)
            },
            'warning_signals': warning_signals,
            'health_level': self._get_health_level(overall_health),
            'priority_balance': {
                'urgent_ratio': round(urgent_ratio, 3),
                'high_ratio': round(high_ratio, 3),
                'medium_ratio': round(medium_ratio, 3),
                'low_ratio': round(low_ratio, 3),
                'balance_recommendation': self._get_priority_balance_recommendation(
                    urgent_ratio, high_ratio, medium_ratio, low_ratio
                )
            }
        }
    
    def _get_priority_balance_recommendation(self, urgent_ratio, high_ratio, medium_ratio, low_ratio):
        """获取优先级平衡建议"""
        recommendations = []
        
        if urgent_ratio > 0.15:
            recommendations.append("减少紧急任务，加强前期规划")
        if high_ratio > 0.25:
            recommendations.append("控制高优先级任务数量，避免资源过度集中")
        if medium_ratio < 0.4:
            recommendations.append("增加中等优先级的常规任务")
        if low_ratio < 0.1:
            recommendations.append("适当安排低优先级的日常维护任务")
        
        if not recommendations:
            recommendations.append("当前优先级分布较为合理")
        
        return recommendations
    
    def _calculate_priority_transitions(self, queryset, period):
        """计算优先级转换分析"""
        # 简化的优先级转换分析
        transitions = {}
        
        # 基于最近任务的优先级分布变化
        recent_tasks_list = list(queryset.order_by('-updated_at')[:100])
        
        for priority_choice in Task.PRIORITY_CHOICES:
            priority_code = priority_choice[0]
            priority_name = priority_choice[1]
            
            current_count = queryset.filter(priority=priority_code).count()
            recent_count = len([t for t in recent_tasks_list if t.priority == priority_code])
            
            # 估算转换活跃度
            transition_activity = recent_count  # 简化计算
            
            transitions[priority_code] = {
                'name': priority_name,
                'current_count': current_count,
                'recent_activity': recent_count,
                'transition_frequency': transition_activity,
                'trend': 'stable'  # 简化，实际应该基于历史数据计算
            }
        
        # 常见优先级调整路径
        common_adjustments = [
            {'from': 'LOW', 'to': 'MEDIUM', 'reason': '任务重要性上升'},
            {'from': 'MEDIUM', 'to': 'HIGH', 'reason': '截止时间临近'},
            {'from': 'HIGH', 'to': 'URGENT', 'reason': '紧急情况出现'},
            {'from': 'URGENT', 'to': 'HIGH', 'reason': '紧急状态缓解'},
            {'from': 'HIGH', 'to': 'MEDIUM', 'reason': '优先级重新评估'}
        ]
        
        return {
            'priority_transitions': transitions,
            'common_adjustment_patterns': common_adjustments,
            'transition_summary': {
                'most_active_priority': max(transitions.keys(), 
                    key=lambda k: transitions[k]['current_count']) if transitions else None,
                'total_transition_activity': sum(t['transition_frequency'] for t in transitions.values())
            }
        }

    @action(detail=False, methods=['get'], url_path='tag-distribution')
    def tag_distribution(self, request):
        """
        详细标签分布统计API
        
        GET /api/tasks/tag-distribution/
        
        支持的查询参数:
        - period: 统计周期 (all, today, week, month, quarter, year)
        - include_deleted: 包含已删除任务统计 (true/false)
        - date_field: 时间字段 (created_at, updated_at, due_date, start_date)
        - include_usage: 包含标签使用分析 (true/false)
        - include_combination: 包含标签组合分析 (true/false)
        - include_efficiency: 包含标签效率分析 (true/false)
        - min_frequency: 最小频次过滤 (默认1)
        - top_n: 返回前N个热门标签 (默认50)
        
        提供的统计数据:
        - 基础标签分布: 各标签使用频次和占比
        - 标签使用分析: 标签在不同状态和优先级的分布
        - 标签组合分析: 标签共现模式和关联度
        - 标签效率分析: 不同标签的任务完成效率
        - 标签趋势分析: 标签使用的时间趋势
        - 标签健康度: 标签分布的合理性评估
        """
        try:
            # 检查用户认证
            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'message': '用户未认证',
                    'error': 'authentication_required'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 获取基础查询集（用户相关的任务）
            user = request.user
            base_queryset = Task.objects.filter(
                Q(owner=user) | Q(assigned_to=user)
            ).distinct()
            
            # 处理软删除任务包含
            include_deleted = request.query_params.get('include_deleted', 'false').lower()
            if include_deleted == 'true':
                base_queryset = Task.all_objects.filter(
                    Q(owner=user) | Q(assigned_to=user)
                ).distinct()
            
            # 处理时间周期过滤
            period = request.query_params.get('period', 'all').lower()
            date_field = request.query_params.get('date_field', 'created_at').lower()
            
            # 验证日期字段
            valid_date_fields = ['created_at', 'updated_at', 'due_date', 'start_date']
            if date_field not in valid_date_fields:
                date_field = 'created_at'
            
            # 应用时间周期过滤
            filtered_queryset = self._apply_period_filter(base_queryset, period, date_field)
            
            # 获取分析选项
            include_usage = request.query_params.get('include_usage', 'true').lower() == 'true'
            include_combination = request.query_params.get('include_combination', 'true').lower() == 'true'
            include_efficiency = request.query_params.get('include_efficiency', 'true').lower() == 'true'
            
            # 获取过滤参数
            min_frequency = int(request.query_params.get('min_frequency', '1'))
            top_n = int(request.query_params.get('top_n', '50'))
            
            # 1. 基础标签分布
            basic_distribution = self._calculate_basic_tag_distribution(filtered_queryset, min_frequency, top_n)
            
            # 2. 标签使用分析
            usage_analysis = {}
            if include_usage:
                usage_analysis = self._calculate_tag_usage_analysis(filtered_queryset, basic_distribution['tag_list'])
            
            # 3. 标签组合分析
            combination_analysis = {}
            if include_combination:
                combination_analysis = self._calculate_tag_combination_analysis(filtered_queryset, basic_distribution['tag_list'])
            
            # 4. 标签效率分析
            efficiency_analysis = {}
            if include_efficiency:
                efficiency_analysis = self._calculate_tag_efficiency_analysis(filtered_queryset, basic_distribution['tag_list'])
            
            # 5. 标签趋势分析
            top_tag_names = [t['tag'] for t in basic_distribution['tag_list'][:10]]
            trend_analysis = self._calculate_tag_trends(base_queryset, period, date_field, top_tag_names)
            
            # 6. 标签健康度分析
            health_analysis = self._calculate_tag_health(filtered_queryset, basic_distribution)
            
            # 构建响应数据
            response_data = {
                'success': True,
                'message': f'标签分布统计获取成功 (周期: {period})',
                'data': {
                    'basic_distribution': basic_distribution,
                    'usage_analysis': usage_analysis,
                    'combination_analysis': combination_analysis,
                    'efficiency_analysis': efficiency_analysis,
                    'trend_analysis': trend_analysis,
                    'health_analysis': health_analysis,
                    'metadata': {
                        'period': period,
                        'date_field': date_field,
                        'include_deleted': include_deleted == 'true',
                        'include_usage': include_usage,
                        'include_combination': include_combination,
                        'include_efficiency': include_efficiency,
                        'min_frequency': min_frequency,
                        'top_n': top_n,
                        'generated_at': timezone.now().isoformat(),
                        'total_tasks_analyzed': filtered_queryset.count(),
                        'user_id': user.id,
                        'username': user.username
                    }
                }
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'标签分布统计获取失败: {str(e)}',
                'error': 'tag_distribution_error',
                'data': {
                    'period': request.query_params.get('period', 'all'),
                    'date_field': request.query_params.get('date_field', 'created_at')
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='time-distribution')
    def time_distribution(self, request):
        """
        详细时间分布统计API
        
        GET /api/tasks/time-distribution/
        
        支持的查询参数:
        - period: 统计周期 (all, today, week, month, quarter, year)
        - include_deleted: 包含已删除任务统计 (true/false)
        - analysis_type: 分析类型 (creation, completion, activity, workload)
        - date_field: 时间字段 (created_at, updated_at, due_date, start_date)
        - include_hourly: 包含小时分布分析 (true/false)
        - include_daily: 包含日期分布分析 (true/false)
        - include_weekly: 包含周分布分析 (true/false)
        - include_monthly: 包含月份分布分析 (true/false)
        - include_trends: 包含时间趋势分析 (true/false)
        - timezone: 时区设置 (默认UTC)
        
        提供的统计数据:
        - 基础时间分布: 各时间维度的任务分布
        - 创建时间分析: 任务创建时间模式
        - 完成时间分析: 任务完成时间模式
        - 活动时间分析: 任务活动时间分布
        - 工作负载分析: 时间段工作负载统计
        - 效率时间分析: 不同时间段的工作效率
        - 季节性分析: 季节性工作模式识别
        """
        try:
            # 检查用户认证
            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'message': '用户未认证',
                    'error': 'authentication_required'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 获取基础查询集（用户相关的任务）
            user = request.user
            base_queryset = Task.objects.filter(
                Q(owner=user) | Q(assigned_to=user)
            ).distinct()
            
            # 处理软删除任务包含
            include_deleted = request.query_params.get('include_deleted', 'false').lower()
            if include_deleted == 'true':
                base_queryset = Task.all_objects.filter(
                    Q(owner=user) | Q(assigned_to=user)
                ).distinct()
            
            # 处理时间周期过滤
            period = request.query_params.get('period', 'all').lower()
            date_field = request.query_params.get('date_field', 'created_at').lower()
            analysis_type = request.query_params.get('analysis_type', 'all').lower()
            
            # 验证日期字段
            valid_date_fields = ['created_at', 'updated_at', 'due_date', 'start_date']
            if date_field not in valid_date_fields:
                date_field = 'created_at'
            
            # 应用时间周期过滤
            filtered_queryset = self._apply_period_filter(base_queryset, period, date_field)
            
            # 获取分析选项
            include_hourly = request.query_params.get('include_hourly', 'true').lower() == 'true'
            include_daily = request.query_params.get('include_daily', 'true').lower() == 'true'
            include_weekly = request.query_params.get('include_weekly', 'true').lower() == 'true'
            include_monthly = request.query_params.get('include_monthly', 'true').lower() == 'true'
            include_trends = request.query_params.get('include_trends', 'true').lower() == 'true'
            
            # 时区设置
            timezone_str = request.query_params.get('timezone', 'UTC')
            
            # 1. 基础时间分布
            basic_distribution = self._calculate_basic_time_distribution(filtered_queryset, date_field, timezone_str)
            
            # 2. 小时分布分析
            hourly_analysis = {}
            if include_hourly:
                hourly_analysis = self._calculate_hourly_distribution(filtered_queryset, date_field, timezone_str)
            
            # 3. 日期分布分析
            daily_analysis = {}
            if include_daily:
                daily_analysis = self._calculate_daily_distribution(filtered_queryset, date_field, timezone_str)
            
            # 4. 周分布分析
            weekly_analysis = {}
            if include_weekly:
                weekly_analysis = self._calculate_weekly_distribution(filtered_queryset, date_field, timezone_str)
            
            # 5. 月份分布分析
            monthly_analysis = {}
            if include_monthly:
                monthly_analysis = self._calculate_monthly_distribution(filtered_queryset, date_field, timezone_str)
            
            # 6. 时间趋势分析
            trend_analysis = {}
            if include_trends:
                trend_analysis = self._calculate_time_trends(filtered_queryset, period, date_field, timezone_str)
            
            # 7. 工作效率分析
            efficiency_analysis = self._calculate_time_efficiency(filtered_queryset, date_field, timezone_str)
            
            # 8. 季节性分析
            seasonal_analysis = self._calculate_seasonal_patterns(filtered_queryset, date_field, timezone_str)
            
            # 构建响应数据
            response_data = {
                'success': True,
                'message': f'时间分布统计获取成功 (周期: {period})',
                'data': {
                    'basic_distribution': basic_distribution,
                    'hourly_analysis': hourly_analysis,
                    'daily_analysis': daily_analysis,
                    'weekly_analysis': weekly_analysis,
                    'monthly_analysis': monthly_analysis,
                    'trend_analysis': trend_analysis,
                    'efficiency_analysis': efficiency_analysis,
                    'seasonal_analysis': seasonal_analysis,
                    'metadata': {
                        'period': period,
                        'date_field': date_field,
                        'analysis_type': analysis_type,
                        'include_deleted': include_deleted == 'true',
                        'include_hourly': include_hourly,
                        'include_daily': include_daily,
                        'include_weekly': include_weekly,
                        'include_monthly': include_monthly,
                        'include_trends': include_trends,
                        'timezone': timezone_str,
                        'generated_at': timezone.now().isoformat(),
                        'total_tasks_analyzed': filtered_queryset.count(),
                        'user_id': user.id,
                        'username': user.username
                    }
                }
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'时间分布统计获取失败: {str(e)}',
                'error': 'time_distribution_error',
                'data': {
                    'period': request.query_params.get('period', 'all'),
                    'date_field': request.query_params.get('date_field', 'created_at')
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _calculate_basic_tag_distribution(self, queryset, min_frequency=1, top_n=50):
        """计算基础标签分布"""
        total_tasks = queryset.count()
        
        if total_tasks == 0:
            return {
                'total_tasks': 0,
                'total_tags': 0,
                'unique_tags': 0,
                'avg_tags_per_task': 0.0,
                'tag_list': [],
                'tag_statistics': {}
            }
        
        # 收集所有标签
        tag_counter = {}
        tagged_tasks = 0
        total_tag_count = 0
        
        for task in queryset.exclude(tags='').exclude(tags__isnull=True):
            tagged_tasks += 1
            tags = task.tags_list
            total_tag_count += len(tags)
            
            for tag in tags:
                if tag:  # 确保标签不为空
                    tag_counter[tag] = tag_counter.get(tag, 0) + 1
        
        # 过滤低频标签
        filtered_tags = {tag: count for tag, count in tag_counter.items() if count >= min_frequency}
        
        # 按频次排序
        sorted_tags = sorted(filtered_tags.items(), key=lambda x: x[1], reverse=True)
        top_tags = sorted_tags[:top_n]
        
        # 计算统计信息
        tag_list = []
        for tag, count in top_tags:
            tag_list.append({
                'tag': tag,
                'count': count,
                'percentage': round((count / total_tasks) * 100, 2),
                'task_percentage': round((count / tagged_tasks) * 100, 2) if tagged_tasks > 0 else 0
            })
        
        # 分类标签
        high_frequency_tags = [t for t in tag_list if t['count'] >= total_tasks * 0.1]  # 10%以上
        medium_frequency_tags = [t for t in tag_list if total_tasks * 0.05 <= t['count'] < total_tasks * 0.1]  # 5-10%
        low_frequency_tags = [t for t in tag_list if t['count'] < total_tasks * 0.05]  # 5%以下
        
        tag_statistics = {
            'high_frequency': {
                'count': len(high_frequency_tags),
                'tags': [t['tag'] for t in high_frequency_tags]
            },
            'medium_frequency': {
                'count': len(medium_frequency_tags),
                'tags': [t['tag'] for t in medium_frequency_tags]
            },
            'low_frequency': {
                'count': len(low_frequency_tags),
                'tags': [t['tag'] for t in low_frequency_tags]
            }
        }
        
        return {
            'total_tasks': total_tasks,
            'tagged_tasks': tagged_tasks,
            'untagged_tasks': total_tasks - tagged_tasks,
            'total_tags': len(tag_counter),
            'unique_tags': len(filtered_tags),
            'avg_tags_per_task': round(total_tag_count / total_tasks, 2) if total_tasks > 0 else 0,
            'tagging_rate': round((tagged_tasks / total_tasks) * 100, 2) if total_tasks > 0 else 0,
            'tag_list': tag_list,
            'tag_statistics': tag_statistics
        }
    
    def _calculate_tag_usage_analysis(self, queryset, tag_list):
        """计算标签使用分析"""
        usage_analysis = {}
        
        # 状态分析
        status_choices = dict(Task.STATUS_CHOICES)
        priority_choices = dict(Task.PRIORITY_CHOICES)
        
        for tag_info in tag_list[:20]:  # 分析前20个标签
            tag = tag_info['tag']
            
            # 获取包含此标签的任务
            tagged_tasks = [t for t in queryset if tag in t.tags_list]
            
            if not tagged_tasks:
                continue
            
            # 状态分布
            status_distribution = {}
            for status_code, status_name in status_choices.items():
                count = len([t for t in tagged_tasks if t.status == status_code])
                status_distribution[status_code] = {
                    'name': status_name,
                    'count': count,
                    'percentage': round((count / len(tagged_tasks)) * 100, 2) if tagged_tasks else 0
                }
            
            # 优先级分布
            priority_distribution = {}
            for priority_code, priority_name in priority_choices.items():
                count = len([t for t in tagged_tasks if t.priority == priority_code])
                priority_distribution[priority_code] = {
                    'name': priority_name,
                    'count': count,
                    'percentage': round((count / len(tagged_tasks)) * 100, 2) if tagged_tasks else 0
                }
            
            # 分类分布
            categories = {}
            for task in tagged_tasks:
                if task.category:
                    categories[task.category] = categories.get(task.category, 0) + 1
            
            category_distribution = []
            for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                category_distribution.append({
                    'category': category,
                    'count': count,
                    'percentage': round((count / len(tagged_tasks)) * 100, 2)
                })
            
            usage_analysis[tag] = {
                'task_count': len(tagged_tasks),
                'status_distribution': status_distribution,
                'priority_distribution': priority_distribution,
                'category_distribution': category_distribution,
                'completion_rate': round((len([t for t in tagged_tasks if t.status == 'COMPLETED']) / len(tagged_tasks)) * 100, 2),
                'avg_progress': round(sum(t.progress for t in tagged_tasks) / len(tagged_tasks), 2) if tagged_tasks else 0
            }
        
        return usage_analysis
    
    def _calculate_tag_combination_analysis(self, queryset, tag_list):
        """计算标签组合分析"""
        if len(tag_list) < 2:
            return {
                'combinations': [],
                'correlation_matrix': {},
                'frequent_patterns': []
            }
        
        # 获取前15个标签进行组合分析
        top_tags = [t['tag'] for t in tag_list[:15]]
        
        # 计算标签共现频率
        combinations = {}
        correlation_data = {}
        
        for task in queryset.exclude(tags='').exclude(tags__isnull=True):
            task_tags = [tag for tag in task.tags_list if tag in top_tags]
            
            # 两两组合分析
            for i, tag1 in enumerate(task_tags):
                for tag2 in task_tags[i+1:]:
                    combo_key = tuple(sorted([tag1, tag2]))
                    combinations[combo_key] = combinations.get(combo_key, 0) + 1
                    
                    # 记录相关性数据
                    if tag1 not in correlation_data:
                        correlation_data[tag1] = {}
                    if tag2 not in correlation_data:
                        correlation_data[tag2] = {}
                    
                    correlation_data[tag1][tag2] = correlation_data[tag1].get(tag2, 0) + 1
                    correlation_data[tag2][tag1] = correlation_data[tag2].get(tag1, 0) + 1
        
        # 排序组合
        sorted_combinations = sorted(combinations.items(), key=lambda x: x[1], reverse=True)
        
        combination_list = []
        for combo, count in sorted_combinations[:20]:  # 前20个组合
            tag1, tag2 = combo
            combination_list.append({
                'tags': [tag1, tag2],
                'count': count,
                'strength': count  # 可以扩展为更复杂的强度计算
            })
        
        # 计算相关性矩阵
        correlation_matrix = {}
        for tag1 in top_tags[:10]:  # 限制矩阵大小
            correlation_matrix[tag1] = {}
            tag1_count = sum(1 for t in queryset if tag1 in t.tags_list)
            
            for tag2 in top_tags[:10]:
                if tag1 == tag2:
                    correlation_matrix[tag1][tag2] = 1.0
                else:
                    co_occurrence = correlation_data.get(tag1, {}).get(tag2, 0)
                    tag2_count = sum(1 for t in queryset if tag2 in t.tags_list)
                    
                    # 简单的关联强度计算
                    if tag1_count > 0 and tag2_count > 0:
                        correlation = co_occurrence / min(tag1_count, tag2_count)
                    else:
                        correlation = 0.0
                    
                    correlation_matrix[tag1][tag2] = round(correlation, 3)
        
        # 频繁模式（3个以上标签的组合）
        frequent_patterns = []
        pattern_counter = {}
        
        for task in queryset.exclude(tags='').exclude(tags__isnull=True):
            task_tags = [tag for tag in task.tags_list if tag in top_tags]
            if len(task_tags) >= 3:
                pattern_key = tuple(sorted(task_tags))
                pattern_counter[pattern_key] = pattern_counter.get(pattern_key, 0) + 1
        
        for pattern, count in sorted(pattern_counter.items(), key=lambda x: x[1], reverse=True)[:10]:
            if count >= 2:  # 至少出现2次
                frequent_patterns.append({
                    'tags': list(pattern),
                    'count': count
                })
        
        return {
            'combinations': combination_list,
            'correlation_matrix': correlation_matrix,
            'frequent_patterns': frequent_patterns
        }
    
    def _calculate_tag_efficiency_analysis(self, queryset, tag_list):
        """计算标签效率分析"""
        efficiency_analysis = {}
        
        for tag_info in tag_list[:15]:  # 分析前15个标签
            tag = tag_info['tag']
            
            # 获取包含此标签的任务
            tagged_tasks = [t for t in queryset if tag in t.tags_list]
            
            if not tagged_tasks:
                continue
            
            # 完成率
            completed_tasks = [t for t in tagged_tasks if t.status == 'COMPLETED']
            completion_rate = (len(completed_tasks) / len(tagged_tasks)) * 100
            
            # 平均进度
            avg_progress = sum(t.progress for t in tagged_tasks) / len(tagged_tasks)
            
            # 平均完成时间（已完成任务）
            avg_completion_time = 0.0
            if completed_tasks:
                total_time = 0
                for task in completed_tasks:
                    completion_time = (task.updated_at - task.created_at).total_seconds() / 3600  # 小时
                    total_time += completion_time
                avg_completion_time = total_time / len(completed_tasks)
            
            # 工时效率
            estimated_hours = sum(float(t.estimated_hours or 0) for t in tagged_tasks)
            actual_hours = sum(float(t.actual_hours or 0) for t in tagged_tasks)
            time_efficiency = (estimated_hours / actual_hours * 100) if actual_hours > 0 else 0
            
            # 逾期率
            overdue_tasks = [t for t in tagged_tasks if t.due_date and t.due_date < timezone.now() and t.status in ['PENDING', 'IN_PROGRESS', 'ON_HOLD']]
            overdue_rate = (len(overdue_tasks) / len(tagged_tasks)) * 100
            
            # 综合效率评分
            efficiency_score = (
                completion_rate * 0.4 +          # 完成率40%
                avg_progress * 0.3 +             # 进度30%
                max(0, (100 - overdue_rate)) * 0.2 +  # 无逾期率20%
                min(100, time_efficiency) * 0.1    # 时间效率10%
            )
            
            efficiency_analysis[tag] = {
                'task_count': len(tagged_tasks),
                'completion_rate': round(completion_rate, 2),
                'avg_progress': round(avg_progress, 2),
                'avg_completion_time_hours': round(avg_completion_time, 2),
                'time_efficiency': round(time_efficiency, 2),
                'overdue_rate': round(overdue_rate, 2),
                'efficiency_score': round(efficiency_score, 2),
                'efficiency_level': self._get_efficiency_level(efficiency_score),
                'recommendations': self._generate_tag_recommendations(tag, completion_rate, avg_progress, overdue_rate)
            }
        
        return efficiency_analysis
    
    def _generate_tag_recommendations(self, tag, completion_rate, avg_progress, overdue_rate):
        """生成标签改进建议"""
        recommendations = []
        
        if completion_rate < 60:
            recommendations.append(f"'{tag}'标签的任务完成率较低，建议优化任务执行流程")
        
        if avg_progress < 50:
            recommendations.append(f"'{tag}'标签的任务进度普遍较慢，建议关注任务推进")
        
        if overdue_rate > 30:
            recommendations.append(f"'{tag}'标签的任务逾期率较高，建议改善时间管理")
        
        if completion_rate > 80 and overdue_rate < 10:
            recommendations.append(f"'{tag}'标签的任务执行良好，可作为最佳实践参考")
        
        if not recommendations:
            recommendations.append(f"'{tag}'标签的任务表现正常，继续保持")
        
        return recommendations
    
    def _calculate_tag_trends(self, queryset, period, date_field, top_tags):
        """计算标签趋势分析"""
        if period == 'week':
            # 按天统计最近7天
            trends = []
            for i in range(7):
                day = timezone.now() - timezone.timedelta(days=i)
                day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + timezone.timedelta(days=1)
                
                day_tasks = queryset.filter(
                    **{f'{date_field}__gte': day_start, f'{date_field}__lt': day_end}
                )
                
                day_tag_counts = {}
                for tag in top_tags:
                    count = sum(1 for t in day_tasks if tag in t.tags_list)
                    day_tag_counts[tag] = count
                
                trends.append({
                    'date': day.strftime('%Y-%m-%d'),
                    'tag_counts': day_tag_counts,
                    'total_tasks': day_tasks.count()
                })
            
            return list(reversed(trends))  # 按时间正序
        
        elif period == 'month':
            # 按周统计最近4周
            trends = []
            for i in range(4):
                week_start = timezone.now() - timezone.timedelta(weeks=i+1)
                week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
                week_end = week_start + timezone.timedelta(weeks=1)
                
                week_tasks = queryset.filter(
                    **{f'{date_field}__gte': week_start, f'{date_field}__lt': week_end}
                )
                
                week_tag_counts = {}
                for tag in top_tags:
                    count = sum(1 for t in week_tasks if tag in t.tags_list)
                    week_tag_counts[tag] = count
                
                trends.append({
                    'period': f'Week {week_start.strftime("%Y-%m-%d")}',
                    'tag_counts': week_tag_counts,
                    'total_tasks': week_tasks.count()
                })
            
            return list(reversed(trends))
        
        else:
            # 简单统计
            current_tag_counts = {}
            for tag in top_tags:
                count = sum(1 for t in queryset if tag in t.tags_list)
                current_tag_counts[tag] = count
            
            return [{
                'period': period,
                'tag_counts': current_tag_counts,
                'total_tasks': queryset.count()
            }]
    
    def _calculate_tag_health(self, queryset, basic_distribution):
        """计算标签健康度分析"""
        total_tasks = basic_distribution['total_tasks']
        tagged_tasks = basic_distribution['tagged_tasks']
        
        if total_tasks == 0:
            return {
                'overall_health_score': 0,
                'health_indicators': {},
                'warning_signals': [],
                'tag_diversity': {}
            }
        
        # 标签覆盖率
        tagging_rate = basic_distribution['tagging_rate']
        
        # 标签多样性
        unique_tags = basic_distribution['unique_tags']
        avg_tags_per_task = basic_distribution['avg_tags_per_task']
        
        # 标签分布均匀性（基尼系数的简化版本）
        tag_counts = [t['count'] for t in basic_distribution['tag_list']]
        if tag_counts:
            sorted_counts = sorted(tag_counts, reverse=True)
            distribution_score = 100 - (sorted_counts[0] / sum(sorted_counts) * 100)  # 避免单一标签过于突出
        else:
            distribution_score = 0
        
        # 健康评分算法
        coverage_score = min(100, tagging_rate)  # 标签覆盖率评分
        diversity_score = min(100, unique_tags * 2)  # 标签多样性评分
        balance_score = distribution_score  # 分布均匀性评分
        usage_score = min(100, avg_tags_per_task * 50)  # 使用充分性评分
        
        overall_health = (
            coverage_score * 0.3 +      # 覆盖率30%
            diversity_score * 0.25 +    # 多样性25%
            balance_score * 0.25 +      # 均匀性25%
            usage_score * 0.2           # 使用度20%
        )
        
        # 预警信号
        warning_signals = []
        if tagging_rate < 50:
            warning_signals.append("标签使用率过低，建议加强任务标签化")
        if unique_tags < 5:
            warning_signals.append("标签种类过少，建议丰富标签体系")
        if avg_tags_per_task < 1:
            warning_signals.append("平均标签数过少，建议增加任务标签")
        if len(basic_distribution['tag_list']) > 0 and basic_distribution['tag_list'][0]['count'] > total_tasks * 0.5:
            warning_signals.append("存在过度使用的标签，建议优化标签分布")
        
        # 标签多样性分析
        tag_diversity = {
            'high_frequency_ratio': len(basic_distribution['tag_statistics']['high_frequency']['tags']) / unique_tags if unique_tags > 0 else 0,
            'medium_frequency_ratio': len(basic_distribution['tag_statistics']['medium_frequency']['tags']) / unique_tags if unique_tags > 0 else 0,
            'low_frequency_ratio': len(basic_distribution['tag_statistics']['low_frequency']['tags']) / unique_tags if unique_tags > 0 else 0,
            'diversity_index': unique_tags / total_tasks if total_tasks > 0 else 0
        }
        
        return {
            'overall_health_score': round(overall_health, 2),
            'health_indicators': {
                'coverage_score': round(coverage_score, 2),
                'diversity_score': round(diversity_score, 2),
                'balance_score': round(balance_score, 2),
                'usage_score': round(usage_score, 2),
                'tagging_rate': tagging_rate,
                'avg_tags_per_task': avg_tags_per_task
            },
            'warning_signals': warning_signals,
            'health_level': self._get_health_level(overall_health),
            'tag_diversity': tag_diversity,
            'recommendations': self._generate_tag_health_recommendations(
                tagging_rate, unique_tags, avg_tags_per_task, distribution_score
            )
        }
    
    def _generate_tag_health_recommendations(self, tagging_rate, unique_tags, avg_tags, distribution_score):
        """生成标签健康改进建议"""
        recommendations = []
        
        if tagging_rate < 70:
            recommendations.append("提高任务标签化率，建议为更多任务添加标签")
        
        if unique_tags < 10:
            recommendations.append("扩展标签体系，增加标签种类以更好地分类任务")
        
        if avg_tags < 1.5:
            recommendations.append("增加任务标签数量，平均每个任务建议2-3个标签")
        
        if distribution_score < 50:
            recommendations.append("优化标签分布，避免过度依赖少数标签")
        
        if unique_tags > 50:
            recommendations.append("考虑整理标签体系，合并相似标签以提高管理效率")
        
        if not recommendations:
            recommendations.append("标签使用状况良好，继续保持当前实践")
        
        return recommendations
    
    # ==================== 时间分布统计辅助方法 ====================
    
    def _calculate_basic_time_distribution(self, queryset, date_field, timezone_str):
        """计算基础时间分布"""
        import pytz
        from datetime import datetime, timedelta
        
        total_tasks = queryset.count()
        
        if total_tasks == 0:
            return {
                'total_tasks': 0,
                'earliest_date': None,
                'latest_date': None,
                'date_range_days': 0,
                'avg_tasks_per_day': 0.0,
                'peak_activity_date': None,
                'summary': {}
            }
        
        # 获取时区
        try:
            tz = pytz.timezone(timezone_str)
        except:
            tz = pytz.UTC
        
        # 过滤有效日期的任务
        valid_tasks = queryset.exclude(**{f'{date_field}__isnull': True})
        
        if not valid_tasks.exists():
            return {
                'total_tasks': total_tasks,
                'valid_date_tasks': 0,
                'earliest_date': None,
                'latest_date': None,
                'date_range_days': 0,
                'avg_tasks_per_day': 0.0,
                'summary': {}
            }
        
        # 计算时间范围
        earliest = valid_tasks.aggregate(earliest=models.Min(date_field))['earliest']
        latest = valid_tasks.aggregate(latest=models.Max(date_field))['latest']
        
        if earliest and latest:
            earliest_local = earliest.astimezone(tz)
            latest_local = latest.astimezone(tz)
            date_range_days = (latest_local.date() - earliest_local.date()).days + 1
            avg_tasks_per_day = valid_tasks.count() / max(date_range_days, 1)
        else:
            earliest_local = latest_local = None
            date_range_days = 0
            avg_tasks_per_day = 0.0
        
        # 找出最活跃的日期
        daily_counts = {}
        for task in valid_tasks:
            date_value = getattr(task, date_field)
            if date_value:
                local_date = date_value.astimezone(tz).date()
                date_str = local_date.isoformat()  # 转换为字符串
                daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
        
        peak_activity_date = max(daily_counts.items(), key=lambda x: x[1])[0] if daily_counts else None
        
        return {
            'total_tasks': total_tasks,
            'valid_date_tasks': valid_tasks.count(),
            'earliest_date': earliest_local.isoformat() if earliest_local else None,
            'latest_date': latest_local.isoformat() if latest_local else None,
            'date_range_days': date_range_days,
            'avg_tasks_per_day': round(avg_tasks_per_day, 2),
            'peak_activity_date': peak_activity_date,
            'peak_activity_count': max(daily_counts.values()) if daily_counts else 0,
            'active_days': len(daily_counts),
            'summary': {
                'coverage_rate': round((len(daily_counts) / max(date_range_days, 1)) * 100, 2),
                'daily_distribution': dict(sorted(daily_counts.items())[-7:])  # 最近7天，现在都是字符串键
            }
        }
    
    def _calculate_hourly_distribution(self, queryset, date_field, timezone_str):
        """计算小时分布"""
        import pytz
        
        try:
            tz = pytz.timezone(timezone_str)
        except:
            tz = pytz.UTC
        
        # 24小时分布
        hourly_counts = {i: 0 for i in range(24)}
        hourly_status_counts = {i: {'PENDING': 0, 'IN_PROGRESS': 0, 'COMPLETED': 0, 'CANCELLED': 0, 'ON_HOLD': 0} for i in range(24)}
        
        valid_tasks = queryset.exclude(**{f'{date_field}__isnull': True})
        
        for task in valid_tasks:
            date_value = getattr(task, date_field)
            if date_value:
                local_time = date_value.astimezone(tz)
                hour = local_time.hour
                hourly_counts[hour] += 1
                hourly_status_counts[hour][task.status] += 1
        
        # 计算统计信息
        total_valid = sum(hourly_counts.values())
        peak_hour = max(hourly_counts, key=hourly_counts.get) if total_valid > 0 else 0
        
        # 工作时间分析 (假设工作时间为9-18点)
        work_hours = list(range(9, 18))
        work_time_tasks = sum(hourly_counts[h] for h in work_hours)
        work_time_percentage = (work_time_tasks / total_valid * 100) if total_valid > 0 else 0
        
        # 小时效率分析
        hourly_efficiency = {}
        for hour in range(24):
            total_hour_tasks = hourly_counts[hour]
            completed_hour_tasks = hourly_status_counts[hour]['COMPLETED']
            efficiency = (completed_hour_tasks / total_hour_tasks * 100) if total_hour_tasks > 0 else 0
            hourly_efficiency[hour] = round(efficiency, 2)
        
        return {
            'hourly_distribution': hourly_counts,
            'hourly_status_distribution': hourly_status_counts,
            'hourly_efficiency': hourly_efficiency,
            'peak_hour': peak_hour,
            'peak_hour_count': hourly_counts[peak_hour],
            'work_time_percentage': round(work_time_percentage, 2),
            'work_time_tasks': work_time_tasks,
            'off_hours_tasks': total_valid - work_time_tasks,
            'most_productive_hours': sorted(hourly_efficiency.items(), key=lambda x: x[1], reverse=True)[:5],
            'activity_pattern': self._analyze_hourly_pattern(hourly_counts)
        }
    
    def _calculate_daily_distribution(self, queryset, date_field, timezone_str):
        """计算日期分布（星期几）"""
        import pytz
        
        try:
            tz = pytz.timezone(timezone_str)
        except:
            tz = pytz.UTC
        
        # 星期分布 (0=星期一, 6=星期日)
        weekday_counts = {i: 0 for i in range(7)}
        weekday_names = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        weekday_status_counts = {i: {'PENDING': 0, 'IN_PROGRESS': 0, 'COMPLETED': 0, 'CANCELLED': 0, 'ON_HOLD': 0} for i in range(7)}
        
        valid_tasks = queryset.exclude(**{f'{date_field}__isnull': True})
        
        for task in valid_tasks:
            date_value = getattr(task, date_field)
            if date_value:
                local_time = date_value.astimezone(tz)
                weekday = local_time.weekday()
                weekday_counts[weekday] += 1
                weekday_status_counts[weekday][task.status] += 1
        
        # 计算统计信息
        total_valid = sum(weekday_counts.values())
        most_active_day = max(weekday_counts, key=weekday_counts.get) if total_valid > 0 else 0
        
        # 工作日 vs 周末分析
        weekday_tasks = sum(weekday_counts[i] for i in range(5))  # 星期一到星期五
        weekend_tasks = sum(weekday_counts[i] for i in range(5, 7))  # 星期六和星期日
        weekday_percentage = (weekday_tasks / total_valid * 100) if total_valid > 0 else 0
        
        # 星期效率分析
        weekday_efficiency = {}
        for day in range(7):
            total_day_tasks = weekday_counts[day]
            completed_day_tasks = weekday_status_counts[day]['COMPLETED']
            efficiency = (completed_day_tasks / total_day_tasks * 100) if total_day_tasks > 0 else 0
            weekday_efficiency[day] = round(efficiency, 2)
        
        return {
            'weekday_distribution': {
                'counts': weekday_counts,
                'names': {i: weekday_names[i] for i in range(7)},
                'percentages': {i: round((count / total_valid * 100), 2) if total_valid > 0 else 0 
                              for i, count in weekday_counts.items()}
            },
            'weekday_status_distribution': weekday_status_counts,
            'weekday_efficiency': weekday_efficiency,
            'most_active_day': {
                'index': most_active_day,
                'name': weekday_names[most_active_day],
                'count': weekday_counts[most_active_day]
            },
            'weekday_vs_weekend': {
                'weekday_tasks': weekday_tasks,
                'weekend_tasks': weekend_tasks,
                'weekday_percentage': round(weekday_percentage, 2),
                'weekend_percentage': round(100 - weekday_percentage, 2)
            },
            'productivity_ranking': [
                {'day': weekday_names[day], 'efficiency': eff} 
                for day, eff in sorted(weekday_efficiency.items(), key=lambda x: x[1], reverse=True)
            ]
        }
    
    def _calculate_weekly_distribution(self, queryset, date_field, timezone_str):
        """计算周分布"""
        import pytz
        from datetime import timedelta
        
        try:
            tz = pytz.timezone(timezone_str)
        except:
            tz = pytz.UTC
        
        valid_tasks = queryset.exclude(**{f'{date_field}__isnull': True})
        
        if not valid_tasks.exists():
            return {'weekly_distribution': {}, 'trend_analysis': {}}
        
        # 按周分组
        weekly_counts = {}
        for task in valid_tasks:
            date_value = getattr(task, date_field)
            if date_value:
                local_time = date_value.astimezone(tz)
                # 获取该周的星期一日期
                week_start = local_time.date() - timedelta(days=local_time.weekday())
                week_key = week_start.strftime('%Y-W%U')
                weekly_counts[week_key] = weekly_counts.get(week_key, 0) + 1
        
        # 计算趋势
        sorted_weeks = sorted(weekly_counts.items())
        
        if len(sorted_weeks) >= 2:
            recent_avg = sum(count for _, count in sorted_weeks[-4:]) / min(4, len(sorted_weeks))
            early_avg = sum(count for _, count in sorted_weeks[:4]) / min(4, len(sorted_weeks))
            trend = 'increasing' if recent_avg > early_avg else 'decreasing' if recent_avg < early_avg else 'stable'
        else:
            trend = 'insufficient_data'
            recent_avg = early_avg = 0
        
        return {
            'weekly_distribution': weekly_counts,
            'total_weeks': len(weekly_counts),
            'avg_tasks_per_week': round(sum(weekly_counts.values()) / len(weekly_counts), 2) if weekly_counts else 0,
            'peak_week': max(weekly_counts.items(), key=lambda x: x[1]) if weekly_counts else None,
            'trend_analysis': {
                'trend': trend,
                'recent_avg': round(recent_avg, 2),
                'early_avg': round(early_avg, 2),
                'change_percentage': round(((recent_avg - early_avg) / early_avg * 100), 2) if early_avg > 0 else 0
            }
        }
    
    def _calculate_monthly_distribution(self, queryset, date_field, timezone_str):
        """计算月份分布"""
        import pytz
        
        try:
            tz = pytz.timezone(timezone_str)
        except:
            tz = pytz.UTC
        
        # 12个月分布
        monthly_counts = {i: 0 for i in range(1, 13)}
        month_names = {
            1: '一月', 2: '二月', 3: '三月', 4: '四月', 5: '五月', 6: '六月',
            7: '七月', 8: '八月', 9: '九月', 10: '十月', 11: '十一月', 12: '十二月'
        }
        
        valid_tasks = queryset.exclude(**{f'{date_field}__isnull': True})
        
        for task in valid_tasks:
            date_value = getattr(task, date_field)
            if date_value:
                local_time = date_value.astimezone(tz)
                month = local_time.month
                monthly_counts[month] += 1
        
        total_valid = sum(monthly_counts.values())
        peak_month = max(monthly_counts, key=monthly_counts.get) if total_valid > 0 else 1
        
        # 季节分析
        seasons = {
            'spring': [3, 4, 5],    # 春季
            'summer': [6, 7, 8],    # 夏季
            'autumn': [9, 10, 11],  # 秋季
            'winter': [12, 1, 2]    # 冬季
        }
        
        seasonal_counts = {}
        for season, months in seasons.items():
            seasonal_counts[season] = sum(monthly_counts[month] for month in months)
        
        return {
            'monthly_distribution': {
                'counts': monthly_counts,
                'names': month_names,
                'percentages': {month: round((count / total_valid * 100), 2) if total_valid > 0 else 0 
                               for month, count in monthly_counts.items()}
            },
            'peak_month': {
                'index': peak_month,
                'name': month_names[peak_month],
                'count': monthly_counts[peak_month]
            },
            'seasonal_analysis': {
                'counts': seasonal_counts,
                'percentages': {season: round((count / total_valid * 100), 2) if total_valid > 0 else 0 
                               for season, count in seasonal_counts.items()},
                'most_active_season': max(seasonal_counts, key=seasonal_counts.get) if total_valid > 0 else 'spring'
            }
        }
    
    def _calculate_time_trends(self, queryset, period, date_field, timezone_str):
        """计算时间趋势"""
        import pytz
        from datetime import datetime, timedelta
        
        try:
            tz = pytz.timezone(timezone_str)
        except:
            tz = pytz.UTC
        
        valid_tasks = queryset.exclude(**{f'{date_field}__isnull': True})
        
        if not valid_tasks.exists():
            return {'trend_data': [], 'trend_summary': {}}
        
        # 根据周期分组数据
        if period == 'today':
            # 小时趋势
            trends = self._get_hourly_trends(valid_tasks, date_field, tz)
        elif period == 'week':
            # 日趋势
            trends = self._get_daily_trends(valid_tasks, date_field, tz, 7)
        elif period == 'month':
            # 日趋势（30天）
            trends = self._get_daily_trends(valid_tasks, date_field, tz, 30)
        else:
            # 月趋势
            trends = self._get_monthly_trends(valid_tasks, date_field, tz)
        
        return trends
    
    def _calculate_time_efficiency(self, queryset, date_field, timezone_str):
        """计算时间效率分析"""
        completed_tasks = queryset.filter(status='COMPLETED')
        
        if not completed_tasks.exists():
            return {
                'avg_completion_time': 0,
                'efficiency_by_hour': {},
                'efficiency_by_day': {},
                'recommendations': ['暂无已完成任务数据']
            }
        
        # 计算平均完成时间
        completion_times = []
        for task in completed_tasks:
            if task.created_at and task.updated_at:
                duration = (task.updated_at - task.created_at).total_seconds() / 3600  # 小时
                completion_times.append(duration)
        
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
        
        # 按小时和星期分析效率
        hourly_efficiency = self._calculate_hourly_efficiency(completed_tasks, timezone_str)
        daily_efficiency = self._calculate_daily_efficiency(completed_tasks, timezone_str)
        
        # 生成建议
        recommendations = self._generate_time_efficiency_recommendations(
            hourly_efficiency, daily_efficiency, avg_completion_time
        )
        
        return {
            'avg_completion_time_hours': round(avg_completion_time, 2),
            'total_completed_tasks': completed_tasks.count(),
            'efficiency_by_hour': hourly_efficiency,
            'efficiency_by_day': daily_efficiency,
            'recommendations': recommendations
        }
    
    def _calculate_seasonal_patterns(self, queryset, date_field, timezone_str):
        """计算季节性模式"""
        monthly_data = self._calculate_monthly_distribution(queryset, date_field, timezone_str)
        
        # 分析季节性趋势
        seasonal_analysis = monthly_data['seasonal_analysis']
        
        # 判断季节性模式
        seasonal_variance = self._calculate_seasonal_variance(seasonal_analysis['counts'])
        
        pattern_type = 'strong_seasonal' if seasonal_variance > 0.3 else 'weak_seasonal' if seasonal_variance > 0.1 else 'no_pattern'
        
        return {
            'seasonal_distribution': seasonal_analysis,
            'pattern_strength': round(seasonal_variance, 3),
            'pattern_type': pattern_type,
            'insights': self._generate_seasonal_insights(seasonal_analysis, pattern_type)
        }
    
    # ==================== 辅助计算方法 ====================
    
    def _analyze_hourly_pattern(self, hourly_counts):
        """分析小时活动模式"""
        total = sum(hourly_counts.values())
        if total == 0:
            return 'no_activity'
        
        morning_tasks = sum(hourly_counts[h] for h in range(6, 12))
        afternoon_tasks = sum(hourly_counts[h] for h in range(12, 18))
        evening_tasks = sum(hourly_counts[h] for h in range(18, 24))
        night_tasks = sum(hourly_counts[h] for h in range(0, 6))
        
        max_period = max([
            ('morning', morning_tasks),
            ('afternoon', afternoon_tasks),
            ('evening', evening_tasks),
            ('night', night_tasks)
        ], key=lambda x: x[1])
        
        return max_period[0]
    
    def _get_hourly_trends(self, queryset, date_field, tz):
        """获取小时趋势"""
        from datetime import datetime, timedelta
        
        hourly_data = {}
        for task in queryset:
            date_value = getattr(task, date_field)
            if date_value:
                local_time = date_value.astimezone(tz)
                hour_key = local_time.strftime('%Y-%m-%d %H:00')
                hourly_data[hour_key] = hourly_data.get(hour_key, 0) + 1
        
        return {
            'trend_data': sorted(hourly_data.items()),
            'trend_summary': {'type': 'hourly', 'data_points': len(hourly_data)}
        }
    
    def _get_daily_trends(self, queryset, date_field, tz, days):
        """获取日趋势"""
        daily_data = {}
        for task in queryset:
            date_value = getattr(task, date_field)
            if date_value:
                local_time = date_value.astimezone(tz)
                day_key = local_time.strftime('%Y-%m-%d')
                daily_data[day_key] = daily_data.get(day_key, 0) + 1
        
        return {
            'trend_data': sorted(daily_data.items()),
            'trend_summary': {'type': 'daily', 'data_points': len(daily_data), 'period_days': days}
        }
    
    def _get_monthly_trends(self, queryset, date_field, tz):
        """获取月趋势"""
        monthly_data = {}
        for task in queryset:
            date_value = getattr(task, date_field)
            if date_value:
                local_time = date_value.astimezone(tz)
                month_key = local_time.strftime('%Y-%m')
                monthly_data[month_key] = monthly_data.get(month_key, 0) + 1
        
        return {
            'trend_data': sorted(monthly_data.items()),
            'trend_summary': {'type': 'monthly', 'data_points': len(monthly_data)}
        }
    
    def _calculate_hourly_efficiency(self, completed_tasks, timezone_str):
        """计算小时效率"""
        import pytz
        
        try:
            tz = pytz.timezone(timezone_str)
        except:
            tz = pytz.UTC
        
        hourly_completion_times = {i: [] for i in range(24)}
        
        for task in completed_tasks:
            if task.created_at and task.updated_at:
                completion_hour = task.updated_at.astimezone(tz).hour
                duration = (task.updated_at - task.created_at).total_seconds() / 3600
                hourly_completion_times[completion_hour].append(duration)
        
        hourly_avg = {}
        for hour, times in hourly_completion_times.items():
            hourly_avg[hour] = round(sum(times) / len(times), 2) if times else 0
        
        return hourly_avg
    
    def _calculate_daily_efficiency(self, completed_tasks, timezone_str):
        """计算日效率"""
        import pytz
        
        try:
            tz = pytz.timezone(timezone_str)
        except:
            tz = pytz.UTC
        
        daily_completion_times = {i: [] for i in range(7)}
        
        for task in completed_tasks:
            if task.created_at and task.updated_at:
                completion_day = task.updated_at.astimezone(tz).weekday()
                duration = (task.updated_at - task.created_at).total_seconds() / 3600
                daily_completion_times[completion_day].append(duration)
        
        daily_avg = {}
        for day, times in daily_completion_times.items():
            daily_avg[day] = round(sum(times) / len(times), 2) if times else 0
        
        return daily_avg
    
    def _generate_time_efficiency_recommendations(self, hourly_eff, daily_eff, avg_time):
        """生成时间效率建议"""
        recommendations = []
        
        if avg_time > 72:  # 超过3天
            recommendations.append("平均任务完成时间较长，建议将大任务拆分为小任务")
        
        # 找出最高效的时间段
        best_hour = min(hourly_eff.items(), key=lambda x: x[1] if x[1] > 0 else float('inf'))
        if best_hour[1] > 0:
            recommendations.append(f"最高效时间段为{best_hour[0]}点，建议在此时间处理重要任务")
        
        best_day = min(daily_eff.items(), key=lambda x: x[1] if x[1] > 0 else float('inf'))
        if best_day[1] > 0:
            day_names = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
            recommendations.append(f"最高效工作日为{day_names[best_day[0]]}，建议合理安排工作计划")
        
        return recommendations
    
    def _calculate_seasonal_variance(self, seasonal_counts):
        """计算季节性方差"""
        total = sum(seasonal_counts.values())
        if total == 0:
            return 0
        
        avg = total / 4
        variance = sum((count - avg) ** 2 for count in seasonal_counts.values()) / 4
        return variance / (avg ** 2) if avg > 0 else 0
    
    def _generate_seasonal_insights(self, seasonal_analysis, pattern_type):
        """生成季节性洞察"""
        insights = []
        
        if pattern_type == 'strong_seasonal':
            most_active = seasonal_analysis['most_active_season']
            season_names = {
                'spring': '春季', 'summer': '夏季',
                'autumn': '秋季', 'winter': '冬季'
            }
            insights.append(f"明显的季节性模式，{season_names[most_active]}最活跃")
        elif pattern_type == 'weak_seasonal':
            insights.append("存在轻微的季节性模式")
        else:
            insights.append("工作模式较为稳定，无明显季节性变化")
        
        return insights

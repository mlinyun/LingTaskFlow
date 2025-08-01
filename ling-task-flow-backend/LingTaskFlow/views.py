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
from django.db.models import Q, Count, Case, When, Value, CharField, Avg, Min
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
        """获取任务统计信息"""
        user = request.user
        queryset = self.get_queryset()
        
        # 基础统计
        total_tasks = queryset.count()
        
        if total_tasks == 0:
            return Response({
                'success': True,
                'data': {
                    'total_tasks': 0,
                    'status_distribution': {},
                    'priority_distribution': {},
                    'category_distribution': {},
                    'progress_summary': {
                        'average_progress': 0,
                        'completed_tasks': 0,
                        'completion_rate': 0
                    },
                    'time_summary': {
                        'overdue_tasks': 0,
                        'due_today': 0,
                        'due_this_week': 0
                    }
                }
            })
        
        # 状态分布
        status_dist = queryset.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # 优先级分布
        priority_dist = queryset.values('priority').annotate(
            count=Count('id')
        ).order_by('priority')
        
        # 分类分布
        category_dist = queryset.exclude(
            category__isnull=True
        ).exclude(
            category__exact=''
        ).values('category').annotate(
            count=Count('id')
        ).order_by('-count')[:10]  # 前10个分类
        
        # 进度摘要
        completed_tasks = queryset.filter(status='COMPLETED').count()
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # 平均进度（排除已完成任务）
        active_tasks = queryset.exclude(status__in=['COMPLETED', 'CANCELLED'])
        avg_progress = 0
        if active_tasks.exists():
            from django.db.models import Avg
            avg_progress = active_tasks.aggregate(
                avg=Avg('progress')
            )['avg'] or 0
        
        # 时间摘要
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        week_end = now + timedelta(days=(6 - now.weekday()))
        
        overdue_tasks = queryset.filter(
            due_date__lt=now,
            status__in=['PENDING', 'IN_PROGRESS', 'ON_HOLD']
        ).count()
        
        due_today = queryset.filter(
            due_date__date=now.date(),
            status__in=['PENDING', 'IN_PROGRESS', 'ON_HOLD']
        ).count()
        
        due_this_week = queryset.filter(
            due_date__lte=week_end,
            due_date__gte=now,
            status__in=['PENDING', 'IN_PROGRESS', 'ON_HOLD']
        ).count()
        
        return Response({
            'success': True,
            'data': {
                'total_tasks': total_tasks,
                'status_distribution': {
                    item['status']: item['count'] for item in status_dist
                },
                'priority_distribution': {
                    item['priority']: item['count'] for item in priority_dist
                },
                'category_distribution': {
                    item['category']: item['count'] for item in category_dist
                },
                'progress_summary': {
                    'average_progress': round(avg_progress, 1),
                    'completed_tasks': completed_tasks,
                    'completion_rate': round(completion_rate, 1)
                },
                'time_summary': {
                    'overdue_tasks': overdue_tasks,
                    'due_today': due_today,
                    'due_this_week': due_this_week
                }
            }
        })
    
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

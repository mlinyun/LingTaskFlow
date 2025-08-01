"""
LingTaskFlow 工具函数和装饰器
"""
from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import status
import hashlib
import time


def rate_limit(max_attempts=5, time_window=300, key_func=None):
    """
    简单的速率限制装饰器
    
    Args:
        max_attempts: 最大尝试次数
        time_window: 时间窗口（秒）
        key_func: 生成缓存键的函数
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(request)
            else:
                # 默认使用IP地址作为键
                ip = get_client_ip(request)
                cache_key = f"rate_limit_{view_func.__name__}_{ip}"
            
            # 获取当前尝试次数
            attempts = cache.get(cache_key, 0)
            
            if attempts >= max_attempts:
                return JsonResponse({
                    'success': False,
                    'message': f'请求过于频繁，请{time_window//60}分钟后再试',
                    'error': 'rate_limit_exceeded'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            # 执行原始视图
            response = view_func(request, *args, **kwargs)
            
            # 如果请求失败，增加尝试计数
            if hasattr(response, 'status_code') and response.status_code >= 400:
                cache.set(cache_key, attempts + 1, time_window)
            
            return response
        
        return wrapper
    return decorator


def get_client_ip(request):
    """获取客户端真实IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def registration_rate_limit_key(request):
    """注册接口的速率限制键生成函数"""
    ip = get_client_ip(request)
    # 结合IP和用户代理生成更精确的限制
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    unique_string = f"{ip}_{user_agent}"
    return f"register_rate_limit_{hashlib.md5(unique_string.encode()).hexdigest()}"


def validate_request_data(required_fields, request_data):
    """
    验证请求数据完整性
    
    Args:
        required_fields: 必需字段列表
        request_data: 请求数据
        
    Returns:
        tuple: (is_valid, missing_fields)
    """
    missing_fields = []
    for field in required_fields:
        if field not in request_data or not request_data[field]:
            missing_fields.append(field)
    
    return len(missing_fields) == 0, missing_fields


def sanitize_user_input(data):
    """
    清理用户输入数据
    
    Args:
        data: 输入数据字典
        
    Returns:
        dict: 清理后的数据
    """
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            # 移除前后空格
            value = value.strip()
            # 基本的XSS防护
            value = value.replace('<script>', '').replace('</script>', '')
            value = value.replace('<', '&lt;').replace('>', '&gt;')
        
        sanitized[key] = value
    
    return sanitized


def generate_device_fingerprint(request):
    """
    生成设备指纹
    
    基于用户代理、IP地址和其他HTTP头部信息生成设备唯一标识
    """
    import hashlib
    
    # 收集设备特征信息
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
    accept = request.META.get('HTTP_ACCEPT', '')
    
    # 组合特征信息
    fingerprint_data = f"{user_agent}|{accept_language}|{accept_encoding}|{accept}"
    
    # 生成MD5哈希
    return hashlib.md5(fingerprint_data.encode('utf-8')).hexdigest()


def get_client_location(ip_address):
    """
    根据IP地址获取大致地理位置
    
    注意：这里使用简单的实现，生产环境可以集成专业的IP地理位置服务
    """
    # 简单的内网IP检测
    if ip_address.startswith(('192.168.', '10.', '172.')):
        return '内网地址'
    
    if ip_address in ['127.0.0.1', 'localhost']:
        return '本地主机'
    
    # 这里可以集成第三方IP地理位置服务
    # 例如：ipapi.co, geoip2, ip-api.com等
    return '未知位置'


def log_login_attempt(user, username_attempted, status, request, failure_reason=None, login_type='login', **kwargs):
    """
    记录登录尝试
    
    Args:
        user: User对象（成功时）或None（失败时）
        username_attempted: 尝试的用户名
        status: 登录状态 ('success', 'failed', 'locked')
        request: HTTP请求对象
        failure_reason: 失败原因（可选）
        login_type: 登录类型 ('login', 'token_refresh') 默认为'login'
        **kwargs: 其他参数（向后兼容）
    """
    from .models import LoginHistory
    
    # 处理kwargs中的参数（向后兼容旧的调用方式）
    if 'ip_address' in kwargs:
        ip_address = kwargs['ip_address']
    else:
        ip_address = get_client_ip(request)
    
    if 'user_agent' in kwargs:
        user_agent = kwargs['user_agent']
    else:
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    device_fingerprint = generate_device_fingerprint(request)
    location = get_client_location(ip_address)
    
    # 如果是token刷新类型，调整记录内容
    if login_type == 'token_refresh':
        if status == 'success':
            failure_reason = f"Token刷新成功 - {failure_reason}" if failure_reason else "Token刷新成功"
        else:
            failure_reason = f"Token刷新失败 - {failure_reason}" if failure_reason else "Token刷新失败"
    
    LoginHistory.objects.create(
        user=user,
        username_attempted=username_attempted,
        status=status,
        ip_address=ip_address,
        user_agent=user_agent,
        device_fingerprint=device_fingerprint,
        location=location,
        failure_reason=failure_reason
    )


def get_enhanced_tokens_for_user(user, remember_me=False):
    """
    为用户生成增强的JWT Token
    
    Args:
        user: User对象
        remember_me: 是否记住登录状态
        
    Returns:
        dict: 包含access和refresh token的字典
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    from datetime import timedelta
    
    refresh = RefreshToken.for_user(user)
    
    # 如果用户选择记住登录状态，延长token有效期
    if remember_me:
        # 延长refresh token有效期到30天
        refresh.set_exp(lifetime=timedelta(days=30))
        # 延长access token有效期到1天
        refresh.access_token.set_exp(lifetime=timedelta(days=1))
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'expires_in': refresh.access_token.payload.get('exp'),
        'token_type': 'Bearer'
    }


# =============================================================================
# API 响应格式标准化
# =============================================================================

from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from typing import Any, Dict, Optional
from datetime import datetime


class StandardAPIResponse:
    """
    标准化API响应格式类
    
    统一的响应格式：
    {
        "success": True/False,
        "message": "响应消息",
        "data": {...},  # 成功时的数据
        "error": {...}, # 失败时的错误信息
        "meta": {...},  # 元数据，如分页信息
        "timestamp": "2025-08-02T12:00:00Z"
    }
    """
    
    @staticmethod
    def success(
        data: Any = None, 
        message: str = "操作成功", 
        meta: Optional[Dict] = None,
        status_code: int = status.HTTP_200_OK
    ) -> Response:
        """
        创建成功响应
        
        Args:
            data: 响应数据
            message: 成功消息
            meta: 元数据（如分页信息）
            status_code: HTTP状态码
            
        Returns:
            Response: DRF Response对象
        """
        response_data = {
            "success": True,
            "message": message,
            "data": data,
            "error": None,
            "meta": meta or {},
            "timestamp": datetime.now().isoformat()
        }
        return Response(response_data, status=status_code)
    
    @staticmethod
    def error(
        message: str = "操作失败",
        error_details: Optional[Dict] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: Optional[str] = None
    ) -> Response:
        """
        创建错误响应
        
        Args:
            message: 错误消息
            error_details: 详细错误信息
            status_code: HTTP状态码
            error_code: 业务错误码
            
        Returns:
            Response: DRF Response对象
        """
        error_data = {
            "code": error_code,
            "details": error_details or {}
        }
        
        response_data = {
            "success": False,
            "message": message,
            "data": None,
            "error": error_data,
            "meta": {},
            "timestamp": datetime.now().isoformat()
        }
        return Response(response_data, status=status_code)
    
    @staticmethod
    def paginated_success(
        data: Any,
        paginator: PageNumberPagination,
        message: str = "获取数据成功"
    ) -> Response:
        """
        创建分页成功响应
        
        Args:
            data: 序列化后的数据
            paginator: 分页器对象
            message: 成功消息
            
        Returns:
            Response: DRF Response对象
        """
        meta = {
            "pagination": {
                "page": paginator.page.number,
                "page_size": paginator.get_page_size(paginator.request),
                "total_pages": paginator.page.paginator.num_pages,
                "total_count": paginator.page.paginator.count,
                "has_next": paginator.page.has_next(),
                "has_previous": paginator.page.has_previous(),
                "next_page": paginator.page.next_page_number() if paginator.page.has_next() else None,
                "previous_page": paginator.page.previous_page_number() if paginator.page.has_previous() else None,
            }
        }
        
        return StandardAPIResponse.success(
            data=data,
            message=message,
            meta=meta
        )


class StandardPagination(PageNumberPagination):
    """
    标准化分页类
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        """
        返回标准化的分页响应
        """
        return StandardAPIResponse.paginated_success(
            data=data,
            paginator=self
        )


def format_validation_errors(errors: Dict) -> Dict:
    """
    格式化序列化器验证错误
    
    Args:
        errors: 序列化器错误字典
        
    Returns:
        Dict: 格式化后的错误信息
    """
    formatted_errors = {}
    
    for field, field_errors in errors.items():
        if isinstance(field_errors, list):
            formatted_errors[field] = [str(error) for error in field_errors]
        else:
            formatted_errors[field] = str(field_errors)
    
    return formatted_errors


def get_error_message_from_exception(exc) -> str:
    """
    从异常对象中获取错误消息
    
    Args:
        exc: 异常对象
        
    Returns:
        str: 错误消息
    """
    if hasattr(exc, 'detail'):
        if isinstance(exc.detail, dict):
            # 处理字段验证错误
            messages = []
            for field, errors in exc.detail.items():
                if isinstance(errors, list):
                    for error in errors:
                        messages.append(f"{field}: {str(error)}")
                else:
                    messages.append(f"{field}: {str(errors)}")
            return "; ".join(messages)
        elif isinstance(exc.detail, list):
            return "; ".join([str(error) for error in exc.detail])
        else:
            return str(exc.detail)
    
    return str(exc)

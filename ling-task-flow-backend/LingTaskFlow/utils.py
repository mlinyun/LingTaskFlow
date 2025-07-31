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

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

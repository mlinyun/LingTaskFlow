"""
LingTaskFlow 项目自定义异常处理器
提供标准化的错误响应格式
"""

import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from .utils import StandardAPIResponse, format_validation_errors, get_error_message_from_exception

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    自定义异常处理器，返回标准化的错误响应格式
    
    Args:
        exc: 异常对象
        context: 上下文信息
        
    Returns:
        Response: 标准化的错误响应
    """
    # 先调用DRF默认的异常处理器
    response = exception_handler(exc, context)

    # 记录异常信息（用于调试）
    request = context.get('request')
    view = context.get('view')

    logger.error(
        f"API Exception: {exc.__class__.__name__}: {str(exc)} "
        f"| View: {view.__class__.__name__ if view else 'Unknown'} "
        f"| Path: {request.path if request else 'Unknown'} "
        f"| Method: {request.method if request else 'Unknown'}"
    )

    if response is not None:
        # 处理不同类型的异常
        custom_response_data = _get_custom_response_data(exc, response)

        return StandardAPIResponse.error(
            message=custom_response_data['message'],
            error_details=custom_response_data['error_details'],
            status_code=response.status_code,
            error_code=custom_response_data.get('error_code')
        )

    # 处理未被DRF处理的异常
    return _handle_unhandled_exceptions(exc)


def _get_custom_response_data(exc, response):
    """
    根据异常类型获取自定义响应数据
    
    Args:
        exc: 异常对象
        response: DRF响应对象
        
    Returns:
        dict: 包含message、error_details、error_code的字典
    """
    error_details = {}
    error_code = None

    # 根据异常类型设置消息和错误码
    if response.status_code == status.HTTP_400_BAD_REQUEST:
        message = "请求参数错误"
        error_code = "VALIDATION_ERROR"

        if hasattr(exc, 'detail') and isinstance(exc.detail, dict):
            error_details = format_validation_errors(exc.detail)
        else:
            error_details = {"detail": get_error_message_from_exception(exc)}

    elif response.status_code == status.HTTP_401_UNAUTHORIZED:
        message = "认证失败，请检查登录状态"
        error_code = "AUTHENTICATION_FAILED"
        error_details = {"detail": get_error_message_from_exception(exc)}

    elif response.status_code == status.HTTP_403_FORBIDDEN:
        message = "权限不足，无法访问该资源"
        error_code = "PERMISSION_DENIED"
        error_details = {"detail": get_error_message_from_exception(exc)}

    elif response.status_code == status.HTTP_404_NOT_FOUND:
        message = "请求的资源不存在"
        error_code = "RESOURCE_NOT_FOUND"
        error_details = {"detail": get_error_message_from_exception(exc)}

    elif response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
        message = "请求方法不被允许"
        error_code = "METHOD_NOT_ALLOWED"
        error_details = {"detail": get_error_message_from_exception(exc)}

    elif response.status_code == status.HTTP_409_CONFLICT:
        message = "请求冲突，资源已存在或状态不匹配"
        error_code = "RESOURCE_CONFLICT"
        error_details = {"detail": get_error_message_from_exception(exc)}

    elif response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        message = "请求过于频繁，请稍后再试"
        error_code = "RATE_LIMIT_EXCEEDED"
        error_details = {"detail": get_error_message_from_exception(exc)}

    else:
        message = "服务器内部错误"
        error_code = "INTERNAL_ERROR"
        error_details = {"detail": get_error_message_from_exception(exc)}

    return {
        "message": message,
        "error_details": error_details,
        "error_code": error_code
    }


def _handle_unhandled_exceptions(exc):
    """
    处理未被DRF处理的异常
    
    Args:
        exc: 异常对象
        
    Returns:
        Response: 标准化的错误响应
    """
    if isinstance(exc, Http404):
        return StandardAPIResponse.error(
            message="请求的资源不存在",
            error_details={"detail": str(exc)},
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND"
        )

    elif isinstance(exc, PermissionDenied):
        return StandardAPIResponse.error(
            message="权限不足，无法访问该资源",
            error_details={"detail": str(exc)},
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="PERMISSION_DENIED"
        )

    # 其他未知异常
    logger.error(f"Unhandled exception: {exc.__class__.__name__}: {str(exc)}")

    return StandardAPIResponse.error(
        message="服务器内部错误",
        error_details={"detail": "An unexpected error occurred"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="INTERNAL_ERROR"
    )

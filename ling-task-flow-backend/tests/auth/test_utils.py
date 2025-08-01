"""
认证系统单元测试 - 工具函数测试
测试认证相关的工具函数和辅助模块
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.core.cache import cache
from unittest.mock import patch, MagicMock
import time
from LingTaskFlow.utils import (
    rate_limit,
    registration_rate_limit_key,
    sanitize_user_input,
    log_login_attempt,
    get_enhanced_tokens_for_user,
    get_client_ip
)


class RateLimitTest(TestCase):
    """速率限制测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.factory = RequestFactory()
        cache.clear()  # 清除缓存
    
    def tearDown(self):
        """清理测试环境"""
        cache.clear()
    
    def test_rate_limit_allows_within_limit(self):
        """测试在限制内的请求被允许"""
        request = self.factory.post('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        # 定义一个被装饰的函数
        @rate_limit(max_attempts=3, time_window=60)
        def test_view(request):
            return "success"
        
        # 在限制内的请求应该成功
        result1 = test_view(request)
        result2 = test_view(request)
        result3 = test_view(request)
        
        self.assertEqual(result1, "success")
        self.assertEqual(result2, "success")
        self.assertEqual(result3, "success")
    
    def test_rate_limit_blocks_excess_requests(self):
        """测试超出限制的请求被阻止"""
        request = self.factory.post('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        @rate_limit(max_attempts=2, time_window=60)
        def test_view(request):
            return "success"
        
        # 前两个请求应该成功
        result1 = test_view(request)
        result2 = test_view(request)
        
        self.assertEqual(result1, "success")
        self.assertEqual(result2, "success")
        
        # 第三个请求应该被阻止
        with self.assertRaises(Exception):  # 应该抛出速率限制异常
            test_view(request)
    
    def test_rate_limit_resets_after_time_window(self):
        """测试时间窗口后速率限制重置"""
        request = self.factory.post('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        @rate_limit(max_attempts=1, time_window=1)  # 1秒窗口
        def test_view(request):
            return "success"
        
        # 第一个请求成功
        result1 = test_view(request)
        self.assertEqual(result1, "success")
        
        # 立即的第二个请求应该被阻止
        with self.assertRaises(Exception):
            test_view(request)
        
        # 等待时间窗口过期
        time.sleep(1.1)
        
        # 现在应该可以再次请求
        result2 = test_view(request)
        self.assertEqual(result2, "success")
    
    def test_custom_key_function(self):
        """测试自定义键函数"""
        request = self.factory.post('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.user = User.objects.create_user('testuser', 'test@example.com', 'pass')
        
        def custom_key(request):
            return f"user:{request.user.id}"
        
        @rate_limit(max_attempts=1, time_window=60, key_func=custom_key)
        def test_view(request):
            return "success"
        
        # 第一个请求成功
        result1 = test_view(request)
        self.assertEqual(result1, "success")
        
        # 第二个请求应该被阻止
        with self.assertRaises(Exception):
            test_view(request)


class RegistrationRateLimitKeyTest(TestCase):
    """注册速率限制键函数测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.factory = RequestFactory()
    
    def test_registration_rate_limit_key_with_ip(self):
        """测试基于IP的注册速率限制键"""
        request = self.factory.post('/', {'email': 'test@example.com'})
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        
        key = registration_rate_limit_key(request)
        
        self.assertIn('192.168.1.100', key)
        self.assertIn('test@example.com', key)
    
    def test_registration_rate_limit_key_without_email(self):
        """测试没有邮箱时的注册速率限制键"""
        request = self.factory.post('/')
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        
        key = registration_rate_limit_key(request)
        
        self.assertIn('192.168.1.100', key)


class SanitizeUserInputTest(TestCase):
    """用户输入清理测试"""
    
    def test_sanitize_normal_input(self):
        """测试正常输入清理"""
        clean_input = "normal_username123"
        result = sanitize_user_input(clean_input)
        self.assertEqual(result, clean_input)
    
    def test_sanitize_xss_input(self):
        """测试XSS攻击输入清理"""
        malicious_input = "<script>alert('xss')</script>"
        result = sanitize_user_input(malicious_input)
        self.assertNotIn('<script>', result)
        self.assertNotIn('alert', result)
    
    def test_sanitize_sql_injection_input(self):
        """测试SQL注入输入清理"""
        malicious_input = "'; DROP TABLE users; --"
        result = sanitize_user_input(malicious_input)
        # 应该移除或转义危险字符
        self.assertNotIn('DROP TABLE', result)
    
    def test_sanitize_none_input(self):
        """测试None输入处理"""
        result = sanitize_user_input(None)
        self.assertEqual(result, '')
    
    def test_sanitize_empty_input(self):
        """测试空字符串输入"""
        result = sanitize_user_input('')
        self.assertEqual(result, '')


class LoginLoggingTest(TestCase):
    """登录日志测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @patch('LingTaskFlow.utils.logger')
    def test_log_successful_login_attempt(self, mock_logger):
        """测试成功登录日志记录"""
        request = self.factory.post('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.META['HTTP_USER_AGENT'] = 'TestBrowser/1.0'
        
        log_login_attempt(
            request=request,
            username='testuser',
            success=True,
            user=self.user
        )
        
        # 验证日志记录被调用
        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args[0][0]
        self.assertIn('testuser', call_args)
        self.assertIn('成功', call_args)
    
    @patch('LingTaskFlow.utils.logger')
    def test_log_failed_login_attempt(self, mock_logger):
        """测试失败登录日志记录"""
        request = self.factory.post('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        log_login_attempt(
            request=request,
            username='wronguser',
            success=False,
            failure_reason='用户不存在'
        )
        
        # 验证警告日志被调用
        mock_logger.warning.assert_called()
        call_args = mock_logger.warning.call_args[0][0]
        self.assertIn('wronguser', call_args)
        self.assertIn('失败', call_args)
        self.assertIn('用户不存在', call_args)


class EnhancedTokenTest(TestCase):
    """增强Token测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_get_enhanced_tokens_for_user(self):
        """测试获取增强Token"""
        request = self.factory.post('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.META['HTTP_USER_AGENT'] = 'TestBrowser/1.0'
        
        tokens = get_enhanced_tokens_for_user(self.user, request)
        
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
        self.assertIsInstance(tokens['access'], str)
        self.assertIsInstance(tokens['refresh'], str)
    
    def test_enhanced_tokens_include_device_info(self):
        """测试增强Token包含设备信息"""
        request = self.factory.post('/')
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        
        tokens = get_enhanced_tokens_for_user(self.user, request)
        
        # Token应该包含设备指纹信息
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
        
        # 可以进一步验证Token的payload是否包含设备信息
        # 这需要解析JWT Token的payload


class ClientIPTest(TestCase):
    """客户端IP获取测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.factory = RequestFactory()
    
    def test_get_client_ip_from_remote_addr(self):
        """测试从REMOTE_ADDR获取客户端IP"""
        request = self.factory.post('/')
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.100')
    
    def test_get_client_ip_from_x_forwarded_for(self):
        """测试从X-Forwarded-For获取客户端IP"""
        request = self.factory.post('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.195, 192.168.1.100'
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '203.0.113.195')  # 应该返回第一个IP
    
    def test_get_client_ip_from_x_real_ip(self):
        """测试从X-Real-IP获取客户端IP"""
        request = self.factory.post('/')
        request.META['HTTP_X_REAL_IP'] = '203.0.113.195'
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '203.0.113.195')
    
    def test_get_client_ip_fallback(self):
        """测试IP获取回退机制"""
        request = self.factory.post('/')
        # 不设置任何IP相关的头部
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '127.0.0.1')  # 应该返回默认值


class SecurityUtilsTest(TestCase):
    """安全工具函数测试"""
    
    def test_password_validation_in_utils(self):
        """测试工具函数中的密码验证"""
        # 如果有密码验证工具函数，在这里测试
        pass
    
    def test_device_fingerprinting(self):
        """测试设备指纹生成"""
        request = self.factory.post('/')
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        
        # 如果有设备指纹生成函数，在这里测试
        pass
    
    def test_suspicious_activity_detection(self):
        """测试可疑活动检测"""
        # 如果有可疑活动检测功能，在这里测试
        pass


class UtilsIntegrationTest(TestCase):
    """工具函数集成测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_complete_authentication_utils_flow(self):
        """测试完整的认证工具函数流程"""
        request = self.factory.post('/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        request.META['HTTP_USER_AGENT'] = 'TestBrowser/1.0'
        
        # 1. 清理输入
        clean_username = sanitize_user_input('testuser')
        self.assertEqual(clean_username, 'testuser')
        
        # 2. 获取客户端IP
        client_ip = get_client_ip(request)
        self.assertEqual(client_ip, '192.168.1.100')
        
        # 3. 生成增强Token
        tokens = get_enhanced_tokens_for_user(self.user, request)
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
        
        # 4. 记录登录尝试
        with patch('LingTaskFlow.utils.logger') as mock_logger:
            log_login_attempt(
                request=request,
                username='testuser',
                success=True,
                user=self.user
            )
            mock_logger.info.assert_called()
    
    @patch('django.core.cache.cache.get')
    @patch('django.core.cache.cache.set')
    def test_rate_limiting_with_caching(self, mock_cache_set, mock_cache_get):
        """测试带缓存的速率限制"""
        request = self.factory.post('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        # 模拟缓存未命中
        mock_cache_get.return_value = None
        
        @rate_limit(max_attempts=3, time_window=60)
        def test_view(request):
            return "success"
        
        result = test_view(request)
        self.assertEqual(result, "success")
        
        # 验证缓存被设置
        mock_cache_set.assert_called()

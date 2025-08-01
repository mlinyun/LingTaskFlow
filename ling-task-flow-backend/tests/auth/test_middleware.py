"""
认证系统单元测试 - 中间件测试
测试认证相关的中间件和安全功能
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.http import HttpResponse
from django.core.cache import cache
from unittest.mock import patch, Mock
import time
from LingTaskFlow.middleware import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    DeviceTrackingMiddleware,
    AuditLogMiddleware
)


class SecurityHeadersMiddlewareTest(TestCase):
    """安全头部中间件测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.factory = RequestFactory()
        self.middleware = SecurityHeadersMiddleware(get_response=lambda r: HttpResponse())
    
    def test_security_headers_added(self):
        """测试安全头部被正确添加"""
        request = self.factory.get('/')
        response = self.middleware(request)
        
        # 验证安全头部
        self.assertIn('X-Content-Type-Options', response)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        
        self.assertIn('X-Frame-Options', response)
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        
        self.assertIn('X-XSS-Protection', response)
        self.assertEqual(response['X-XSS-Protection'], '1; mode=block')
        
        self.assertIn('Referrer-Policy', response)
        self.assertEqual(response['Referrer-Policy'], 'strict-origin-when-cross-origin')
    
    def test_csp_header_added(self):
        """测试内容安全策略头部"""
        request = self.factory.get('/')
        response = self.middleware(request)
        
        self.assertIn('Content-Security-Policy', response)
        csp = response['Content-Security-Policy']
        self.assertIn("default-src 'self'", csp)
    
    def test_hsts_header_for_https(self):
        """测试HTTPS请求的HSTS头部"""
        request = self.factory.get('/', HTTP_X_FORWARDED_PROTO='https')
        response = self.middleware(request)
        
        self.assertIn('Strict-Transport-Security', response)
        hsts = response['Strict-Transport-Security']
        self.assertIn('max-age=', hsts)
        self.assertIn('includeSubDomains', hsts)


class RateLimitMiddlewareTest(TestCase):
    """速率限制中间件测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.factory = RequestFactory()
        self.middleware = RateLimitMiddleware(get_response=lambda r: HttpResponse())
        cache.clear()
    
    def tearDown(self):
        """清理测试环境"""
        cache.clear()
    
    def test_rate_limit_allows_normal_requests(self):
        """测试正常请求被允许"""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
    
    def test_rate_limit_blocks_excessive_requests(self):
        """测试过多请求被阻止"""
        # 配置较低的限制用于测试
        with patch.object(self.middleware, 'max_requests_per_minute', 2):
            request = self.factory.get('/')
            request.META['REMOTE_ADDR'] = '127.0.0.1'
            
            # 前两个请求应该成功
            response1 = self.middleware(request)
            response2 = self.middleware(request)
            
            self.assertEqual(response1.status_code, 200)
            self.assertEqual(response2.status_code, 200)
            
            # 第三个请求应该被限制
            response3 = self.middleware(request)
            self.assertEqual(response3.status_code, 429)  # Too Many Requests
    
    def test_rate_limit_different_ips_separate_limits(self):
        """测试不同IP有独立的速率限制"""
        with patch.object(self.middleware, 'max_requests_per_minute', 1):
            request1 = self.factory.get('/')
            request1.META['REMOTE_ADDR'] = '127.0.0.1'
            
            request2 = self.factory.get('/')
            request2.META['REMOTE_ADDR'] = '192.168.1.100'
            
            # 两个不同IP的请求都应该成功
            response1 = self.middleware(request1)
            response2 = self.middleware(request2)
            
            self.assertEqual(response1.status_code, 200)
            self.assertEqual(response2.status_code, 200)
    
    def test_rate_limit_headers_added(self):
        """测试速率限制头部被添加"""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        response = self.middleware(request)
        
        # 验证速率限制相关头部
        self.assertIn('X-RateLimit-Limit', response)
        self.assertIn('X-RateLimit-Remaining', response)
        self.assertIn('X-RateLimit-Reset', response)


class DeviceTrackingMiddlewareTest(TestCase):
    """设备追踪中间件测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.factory = RequestFactory()
        self.middleware = DeviceTrackingMiddleware(get_response=lambda r: HttpResponse())
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_device_fingerprint_created(self):
        """测试设备指纹创建"""
        request = self.factory.get('/')
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        request.user = self.user
        
        response = self.middleware(request)
        
        # 验证设备指纹被添加到请求中
        self.assertTrue(hasattr(request, 'device_fingerprint'))
        self.assertIsNotNone(request.device_fingerprint)
    
    def test_device_tracking_anonymous_user(self):
        """测试匿名用户的设备追踪"""
        request = self.factory.get('/')
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)'
        request.META['REMOTE_ADDR'] = '203.0.113.195'
        request.user = AnonymousUser()
        
        response = self.middleware(request)
        
        # 匿名用户也应该有设备指纹
        self.assertTrue(hasattr(request, 'device_fingerprint'))
    
    def test_suspicious_device_detection(self):
        """测试可疑设备检测"""
        request = self.factory.get('/')
        request.META['HTTP_USER_AGENT'] = 'SuspiciousBot/1.0'
        request.META['REMOTE_ADDR'] = '1.2.3.4'
        request.user = self.user
        
        response = self.middleware(request)
        
        # 可疑设备应该被标记
        self.assertTrue(hasattr(request, 'is_suspicious_device'))
    
    @patch('LingTaskFlow.middleware.logger')
    def test_new_device_logging(self, mock_logger):
        """测试新设备登录日志"""
        request = self.factory.get('/api/auth/login/')
        request.META['HTTP_USER_AGENT'] = 'NewBrowser/1.0'
        request.META['REMOTE_ADDR'] = '198.51.100.42'
        request.user = self.user
        
        response = self.middleware(request)
        
        # 应该记录新设备登录
        mock_logger.info.assert_called()


class AuditLogMiddlewareTest(TestCase):
    """审计日志中间件测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.factory = RequestFactory()
        self.middleware = AuditLogMiddleware(get_response=lambda r: HttpResponse())
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @patch('LingTaskFlow.middleware.logger')
    def test_api_request_logging(self, mock_logger):
        """测试API请求日志记录"""
        request = self.factory.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.META['HTTP_USER_AGENT'] = 'TestClient/1.0'
        request.user = self.user
        
        response = self.middleware(request)
        
        # 验证API请求被记录
        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args[0][0]
        self.assertIn('POST', call_args)
        self.assertIn('/api/auth/login/', call_args)
        self.assertIn('testuser', call_args)
    
    @patch('LingTaskFlow.middleware.logger')
    def test_sensitive_data_filtered(self, mock_logger):
        """测试敏感数据被过滤"""
        request = self.factory.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'secretpassword',
            'credit_card': '1234-5678-9012-3456'
        })
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.user = self.user
        
        response = self.middleware(request)
        
        # 验证敏感数据被过滤
        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args[0][0]
        self.assertNotIn('secretpassword', call_args)
        self.assertNotIn('1234-5678-9012-3456', call_args)
        self.assertIn('***', call_args)  # 应该被星号替换
    
    @patch('LingTaskFlow.middleware.logger')
    def test_failed_authentication_logging(self, mock_logger):
        """测试认证失败日志记录"""
        request = self.factory.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.user = AnonymousUser()
        
        # 模拟认证失败的响应
        def mock_get_response(req):
            response = HttpResponse()
            response.status_code = 401
            return response
        
        middleware = AuditLogMiddleware(get_response=mock_get_response)
        response = middleware(request)
        
        # 验证认证失败被记录为警告
        mock_logger.warning.assert_called()
    
    def test_exclude_static_files(self):
        """测试静态文件请求不被记录"""
        with patch('LingTaskFlow.middleware.logger') as mock_logger:
            request = self.factory.get('/static/css/style.css')
            request.META['REMOTE_ADDR'] = '127.0.0.1'
            request.user = AnonymousUser()
            
            response = self.middleware(request)
            
            # 静态文件请求不应该被记录
            mock_logger.info.assert_not_called()


class MiddlewareIntegrationTest(TestCase):
    """中间件集成测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        cache.clear()
    
    def tearDown(self):
        """清理测试环境"""
        cache.clear()
    
    def test_middleware_chain_execution(self):
        """测试中间件链执行"""
        # 创建中间件链
        def get_response(request):
            return HttpResponse("OK")
        
        # 应用所有中间件
        audit_middleware = AuditLogMiddleware(get_response)
        device_middleware = DeviceTrackingMiddleware(audit_middleware)
        rate_middleware = RateLimitMiddleware(device_middleware)
        security_middleware = SecurityHeadersMiddleware(rate_middleware)
        
        request = self.factory.get('/api/auth/profile/')
        request.META['HTTP_USER_AGENT'] = 'TestBrowser/1.0'
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.user = self.user
        
        response = security_middleware(request)
        
        # 验证所有中间件功能都生效
        self.assertEqual(response.status_code, 200)
        
        # 安全头部
        self.assertIn('X-Content-Type-Options', response)
        self.assertIn('X-RateLimit-Limit', response)
        
        # 设备指纹
        self.assertTrue(hasattr(request, 'device_fingerprint'))
    
    @patch('LingTaskFlow.middleware.logger')
    def test_security_incident_handling(self, mock_logger):
        """测试安全事件处理"""
        # 模拟可疑请求
        request = self.factory.post('/api/auth/login/', {
            'username': 'admin',
            'password': "' OR '1'='1"  # SQL注入尝试
        })
        request.META['HTTP_USER_AGENT'] = 'AttackBot/1.0'
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        request.user = AnonymousUser()
        
        # 应用中间件
        def get_response(req):
            return HttpResponse(status=401)
        
        security_middleware = SecurityHeadersMiddleware(get_response)
        device_middleware = DeviceTrackingMiddleware(security_middleware)
        audit_middleware = AuditLogMiddleware(device_middleware)
        
        response = audit_middleware(request)
        
        # 验证安全事件被记录
        mock_logger.warning.assert_called()
    
    def test_performance_under_load(self):
        """测试高负载下的性能"""
        def get_response(request):
            return HttpResponse("OK")
        
        middleware = SecurityHeadersMiddleware(get_response)
        
        # 模拟多个并发请求
        start_time = time.time()
        
        for i in range(100):
            request = self.factory.get(f'/api/test/{i}')
            request.META['REMOTE_ADDR'] = f'192.168.1.{i % 255}'
            request.user = self.user
            
            response = middleware(request)
            self.assertEqual(response.status_code, 200)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 验证响应时间合理（100个请求在5秒内完成）
        self.assertLess(duration, 5.0)


class MiddlewareConfigurationTest(TestCase):
    """中间件配置测试"""
    
    def test_middleware_ordering(self):
        """测试中间件顺序正确性"""
        # 这个测试验证中间件在settings.py中的顺序是否正确
        from django.conf import settings
        
        middleware_list = settings.MIDDLEWARE
        
        # 安全中间件应该在前面
        security_index = next(
            (i for i, mw in enumerate(middleware_list) 
             if 'SecurityHeadersMiddleware' in mw), 
            None
        )
        
        # 速率限制中间件应该在认证中间件之前
        rate_limit_index = next(
            (i for i, mw in enumerate(middleware_list) 
             if 'RateLimitMiddleware' in mw), 
            None
        )
        
        # 审计日志中间件应该在最后
        audit_index = next(
            (i for i, mw in enumerate(middleware_list) 
             if 'AuditLogMiddleware' in mw), 
            None
        )
        
        if all(x is not None for x in [security_index, rate_limit_index, audit_index]):
            self.assertLess(security_index, rate_limit_index)
            self.assertLess(rate_limit_index, audit_index)
    
    def test_middleware_settings_validation(self):
        """测试中间件设置验证"""
        # 验证中间件相关的设置是否正确配置
        from django.conf import settings
        
        # 验证速率限制设置
        self.assertTrue(hasattr(settings, 'RATE_LIMIT_ENABLED'))
        
        # 验证安全头部设置
        self.assertTrue(hasattr(settings, 'SECURITY_HEADERS_ENABLED'))
        
        # 验证审计日志设置
        self.assertTrue(hasattr(settings, 'AUDIT_LOG_ENABLED'))

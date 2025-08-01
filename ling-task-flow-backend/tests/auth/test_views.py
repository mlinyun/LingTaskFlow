"""
认证系统单元测试 - 视图测试
测试用户注册、登录、Token刷新等API视图的功能
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch, MagicMock
import json
from LingTaskFlow.models import UserProfile


class UserRegistrationViewTest(APITestCase):
    """用户注册视图测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        
    def test_successful_registration(self):
        """测试成功注册"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertIn('user', response.data['data'])
        self.assertIn('tokens', response.data['data'])
        self.assertIn('profile', response.data['data']['user'])
        
        # 验证用户已创建
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('SecurePass123!'))
        
        # 验证UserProfile已创建
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, UserProfile)
    
    def test_registration_with_invalid_data(self):
        """测试无效数据注册"""
        data = {
            'username': 'test',  # 太短
            'email': 'invalid-email',  # 无效邮箱
            'password': '123',  # 太弱
            'password_confirm': '456'  # 不匹配
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('errors', response.data)
    
    def test_registration_duplicate_username(self):
        """测试重复用户名注册"""
        # 先创建一个用户
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='pass123'
        )
        
        data = {
            'username': 'existinguser',
            'email': 'new@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_registration_duplicate_email(self):
        """测试重复邮箱注册"""
        # 先创建一个用户
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='pass123'
        )
        
        data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    @patch('LingTaskFlow.views.rate_limit')
    def test_registration_rate_limiting(self, mock_rate_limit):
        """测试注册速率限制"""
        # 模拟触发速率限制
        mock_rate_limit.side_effect = Exception("Rate limit exceeded")
        
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
    
    def test_registration_missing_fields(self):
        """测试缺少必填字段"""
        data = {
            'username': 'testuser',
            # 缺少email, password, password_confirm
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])


class UserLoginViewTest(APITestCase):
    """用户登录视图测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.client = APIClient()
        self.login_url = '/api/auth/login/'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_successful_login_with_username(self):
        """测试使用用户名成功登录"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertIn('tokens', response.data['data'])
        self.assertIn('user', response.data['data'])
        self.assertIn('access', response.data['data']['tokens'])
        self.assertIn('refresh', response.data['data']['tokens'])
    
    def test_successful_login_with_email(self):
        """测试使用邮箱成功登录"""
        data = {
            'username': 'test@example.com',  # 使用邮箱登录
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_login_with_wrong_password(self):
        """测试错误密码登录"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_login_with_nonexistent_user(self):
        """测试不存在的用户登录"""
        data = {
            'username': 'nonexistentuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_login_with_inactive_user(self):
        """测试未激活用户登录"""
        self.user.is_active = False
        self.user.save()
        
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    @patch('LingTaskFlow.views.log_login_attempt')
    def test_login_logging(self, mock_log_login):
        """测试登录尝试日志记录"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        # 验证日志记录被调用
        mock_log_login.assert_called()
    
    def test_login_missing_fields(self):
        """测试缺少登录字段"""
        data = {
            'username': 'testuser',
            # 缺少密码
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])


class TokenRefreshViewTest(APITestCase):
    """Token刷新视图测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.client = APIClient()
        self.refresh_url = '/api/auth/token/refresh/'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.refresh_token = RefreshToken.for_user(self.user)
    
    def test_successful_token_refresh(self):
        """测试成功刷新Token"""
        data = {
            'refresh': str(self.refresh_token)
        }
        
        response = self.client.post(self.refresh_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
    
    def test_token_refresh_with_invalid_token(self):
        """测试使用无效Token刷新"""
        data = {
            'refresh': 'invalid_token_string'
        }
        
        response = self.client.post(self.refresh_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])
    
    def test_token_refresh_with_expired_token(self):
        """测试使用过期Token刷新"""
        # 手动将Token设为过期
        self.refresh_token.set_exp(lifetime=-1)  # 设置为过期
        
        data = {
            'refresh': str(self.refresh_token)
        }
        
        response = self.client.post(self.refresh_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])
    
    def test_token_refresh_missing_token(self):
        """测试缺少刷新Token"""
        data = {}
        
        response = self.client.post(self.refresh_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    @patch('LingTaskFlow.views.rate_limit')
    def test_token_refresh_rate_limiting(self, mock_rate_limit):
        """测试Token刷新速率限制"""
        # 模拟触发速率限制
        mock_rate_limit.side_effect = Exception("Rate limit exceeded")
        
        data = {
            'refresh': str(self.refresh_token)
        }
        
        response = self.client.post(self.refresh_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class AuthenticationIntegrationTest(APITestCase):
    """认证系统集成测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.refresh_url = '/api/auth/token/refresh/'
    
    def test_full_authentication_flow(self):
        """测试完整的认证流程"""
        # 1. 注册用户
        register_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }
        
        register_response = self.client.post(
            self.register_url, 
            register_data, 
            format='json'
        )
        
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        register_tokens = register_response.data['data']['tokens']
        
        # 2. 使用注册返回的Token访问需要认证的接口
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {register_tokens["access"]}'
        )
        
        # 这里应该测试一个需要认证的接口，暂时跳过
        
        # 3. 登录获取新Token
        login_data = {
            'username': 'testuser',
            'password': 'SecurePass123!'
        }
        
        login_response = self.client.post(
            self.login_url, 
            login_data, 
            format='json'
        )
        
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        login_tokens = login_response.data['data']['tokens']
        
        # 4. 刷新Token
        refresh_data = {
            'refresh': login_tokens['refresh']
        }
        
        refresh_response = self.client.post(
            self.refresh_url, 
            refresh_data, 
            format='json'
        )
        
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data['data'])
        self.assertIn('refresh', refresh_response.data['data'])
    
    def test_token_authentication_required(self):
        """测试需要Token认证的接口"""
        # 不提供Token，访问需要认证的接口应该失败
        # 这里应该测试一个需要认证的接口
        pass
    
    def test_invalid_token_handling(self):
        """测试无效Token处理"""
        # 使用无效Token访问需要认证的接口
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        
        # 这里应该测试一个需要认证的接口，应该返回401
        pass


class AuthenticationSecurityTest(APITestCase):
    """认证系统安全性测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
    
    def test_sql_injection_protection(self):
        """测试SQL注入保护"""
        malicious_data = {
            'username': "'; DROP TABLE users; --",
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, malicious_data, format='json')
        
        # 应该正常处理，不会导致错误
        self.assertIn(response.status_code, [400, 401])
    
    def test_xss_protection(self):
        """测试XSS保护"""
        malicious_data = {
            'username': '<script>alert("xss")</script>',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }
        
        response = self.client.post(self.register_url, malicious_data, format='json')
        
        # 应该被拒绝或者被清理
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_password_not_exposed_in_response(self):
        """测试密码不在响应中暴露"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        # 响应中不应该包含密码
        response_str = json.dumps(response.data)
        self.assertNotIn('SecurePass123!', response_str)
        self.assertNotIn('password', response.data.get('data', {}).get('user', {}))
    
    def test_sensitive_error_message_handling(self):
        """测试敏感错误信息处理"""
        # 测试不存在的用户登录
        data = {
            'username': 'nonexistentuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        # 错误信息应该是通用的，不暴露用户是否存在
        self.assertIn('凭据', response.data.get('message', '').lower())

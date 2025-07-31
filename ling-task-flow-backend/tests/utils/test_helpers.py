"""
测试工具模块

提供测试中常用的辅助函数和工具类
"""
import os
import sys
import django
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 配置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ling_task_flow_backend.settings')
django.setup()

from LingTaskFlow.models import UserProfile


class MockUser:
    """模拟用户对象，用于权限测试"""
    def __init__(self, username, is_staff=False, is_superuser=False, is_authenticated=True):
        self.username = username
        self.is_authenticated = is_authenticated
        self.is_staff = is_staff
        self.is_superuser = is_superuser
    
    def __eq__(self, other):
        if hasattr(other, 'username'):
            return self.username == other.username
        return False
    
    def __str__(self):
        return f"MockUser({self.username})"


class MockRequest:
    """模拟HTTP请求对象"""
    def __init__(self, user=None, method='GET'):
        self.user = user or MockUser('anonymous', is_authenticated=False)
        self.method = method


class MockObject:
    """模拟数据库对象"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class BaseTestCase(TestCase):
    """基础测试类，提供常用的测试工具方法"""
    
    @classmethod
    def setUpTestData(cls):
        """设置测试数据"""
        super().setUpTestData()
        cls.test_users = {}
        cls.create_test_users()
    
    @classmethod
    def create_test_users(cls):
        """创建测试用户"""
        # 普通用户
        cls.test_users['regular'] = User.objects.create_user(
            username='testuser_regular',
            email='regular@test.com',
            password='TestPass123!'
        )
        
        # 管理员用户
        cls.test_users['admin'] = User.objects.create_user(
            username='testuser_admin',
            email='admin@test.com',
            password='AdminPass123!',
            is_staff=True
        )
        
        # 超级用户
        cls.test_users['superuser'] = User.objects.create_user(
            username='testuser_super',
            email='super@test.com',
            password='SuperPass123!',
            is_superuser=True
        )
    
    def create_user(self, username=None, email=None, password=None, **kwargs):
        """创建测试用户的便捷方法"""
        username = username or f'testuser_{len(User.objects.all())}'
        email = email or f'{username}@test.com'
        password = password or 'TestPass123!'
        
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **kwargs
        )
    
    def get_user_tokens(self, user):
        """获取用户的JWT Token"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class BaseAPITestCase(APITestCase):
    """API测试基类"""
    
    @classmethod
    def setUpTestData(cls):
        """设置测试数据"""
        super().setUpTestData()
        cls.test_users = {}
        cls.create_test_users()
    
    @classmethod
    def create_test_users(cls):
        """创建测试用户"""
        # 普通用户
        cls.test_users['regular'] = User.objects.create_user(
            username='testuser_regular',
            email='regular@test.com',
            password='TestPass123!'
        )
        
        # 管理员用户
        cls.test_users['admin'] = User.objects.create_user(
            username='testuser_admin',
            email='admin@test.com',
            password='AdminPass123!',
            is_staff=True
        )
        
        # 超级用户
        cls.test_users['superuser'] = User.objects.create_user(
            username='testuser_super',
            email='super@test.com',
            password='SuperPass123!',
            is_superuser=True
        )
    
    def setUp(self):
        """设置测试环境"""
        super().setUp()
        self.client = APIClient()
    
    def authenticate_user(self, user):
        """认证用户"""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return str(refresh.access_token)
    
    def logout_user(self):
        """用户登出"""
        self.client.credentials()
    
    def create_user(self, username=None, email=None, password=None, **kwargs):
        """创建测试用户的便捷方法"""
        username = username or f'testuser_{len(User.objects.all())}'
        email = email or f'{username}@test.com'
        password = password or 'TestPass123!'
        
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **kwargs
        )


class TestDataFactory:
    """测试数据工厂类"""
    
    @staticmethod
    def create_user_data(username=None, email=None, password=None):
        """创建用户数据"""
        username = username or 'testuser'
        email = email or f'{username}@test.com'
        password = password or 'TestPass123!'
        
        return {
            'username': username,
            'email': email,
            'password': password,
            'password_confirm': password
        }
    
    @staticmethod
    def create_login_data(username=None, password=None):
        """创建登录数据"""
        return {
            'username': username or 'testuser',
            'password': password or 'TestPass123!'
        }


def run_test_with_setup(test_func):
    """测试装饰器，自动设置Django环境"""
    def wrapper(*args, **kwargs):
        # 确保Django已配置
        if not django.apps.apps.ready:
            django.setup()
        return test_func(*args, **kwargs)
    return wrapper


def print_test_result(test_name, passed, message=None):
    """打印测试结果"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} {test_name}")
    if message:
        print(f"    {message}")


def assert_response_success(response, expected_status=200):
    """断言响应成功"""
    assert response.status_code == expected_status, f"期望状态码 {expected_status}，实际 {response.status_code}"
    if hasattr(response, 'json'):
        data = response.json()
        if 'success' in data:
            assert data['success'] == True, f"API调用应该成功: {data.get('message', '')}"


def assert_response_error(response, expected_status=400):
    """断言响应错误"""
    assert response.status_code == expected_status, f"期望状态码 {expected_status}，实际 {response.status_code}"
    if hasattr(response, 'json'):
        data = response.json()
        if 'success' in data:
            assert data['success'] == False, f"API调用应该失败: {data.get('message', '')}"

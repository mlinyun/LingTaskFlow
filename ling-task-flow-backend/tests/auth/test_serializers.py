"""
认证系统单元测试 - 序列化器测试
测试用户注册、登录等序列化器的功能
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from LingTaskFlow.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserProfileSerializer,
    UserWithProfileSerializer
)
from LingTaskFlow.models import UserProfile


class UserRegistrationSerializerTest(TestCase):
    """用户注册序列化器测试"""
    
    def test_valid_registration_data(self):
        """测试有效的注册数据"""
        valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }
        
        serializer = UserRegistrationSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        
        # 创建用户
        user = serializer.save()
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('SecurePass123!'))
    
    def test_password_mismatch(self):
        """测试密码不匹配"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'DifferentPass456!'
        }
        
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password_confirm', serializer.errors)
    
    def test_duplicate_username(self):
        """测试重复用户名"""
        # 创建一个用户
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
        
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
    
    def test_duplicate_email(self):
        """测试重复邮箱"""
        # 创建一个用户
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
        
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_invalid_username_format(self):
        """测试无效的用户名格式"""
        invalid_usernames = [
            '123user',    # 数字开头
            'user@name',  # 包含特殊字符
            'us',         # 太短
            'a' * 21,     # 太长
        ]
        
        for username in invalid_usernames:
            data = {
                'username': username,
                'email': 'test@example.com',
                'password': 'SecurePass123!',
                'password_confirm': 'SecurePass123!'
            }
            
            serializer = UserRegistrationSerializer(data=data)
            self.assertFalse(serializer.is_valid(), f"用户名 {username} 应该无效")
            self.assertIn('username', serializer.errors)
    
    def test_weak_password(self):
        """测试弱密码"""
        weak_passwords = [
            '123456',      # 太简单
            'password',    # 常用密码
            'abc123',      # 太短且简单
            '12345678',    # 纯数字
            'abcdefgh',    # 纯字母
        ]
        
        for password in weak_passwords:
            data = {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': password,
                'password_confirm': password
            }
            
            serializer = UserRegistrationSerializer(data=data)
            self.assertFalse(serializer.is_valid(), f"密码 {password} 应该无效")
            self.assertIn('password', serializer.errors)
    
    def test_invalid_email_format(self):
        """测试无效邮箱格式"""
        invalid_emails = [
            'notanemail',
            'invalid@',
            '@invalid.com',
            'invalid.email',
            'test@',
        ]
        
        for email in invalid_emails:
            data = {
                'username': 'testuser',
                'email': email,
                'password': 'SecurePass123!',
                'password_confirm': 'SecurePass123!'
            }
            
            serializer = UserRegistrationSerializer(data=data)
            self.assertFalse(serializer.is_valid(), f"邮箱 {email} 应该无效")
            self.assertIn('email', serializer.errors)


class UserLoginSerializerTest(TestCase):
    """用户登录序列化器测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_valid_login_with_username(self):
        """测试使用用户名有效登录"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        serializer = UserLoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['user'], self.user)
    
    def test_valid_login_with_email(self):
        """测试使用邮箱有效登录"""
        data = {
            'username': 'test@example.com',  # 可以用邮箱登录
            'password': 'testpass123'
        }
        
        serializer = UserLoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['user'], self.user)
    
    def test_invalid_credentials(self):
        """测试无效凭据"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        serializer = UserLoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_nonexistent_user(self):
        """测试不存在的用户"""
        data = {
            'username': 'nonexistentuser',
            'password': 'testpass123'
        }
        
        serializer = UserLoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_inactive_user(self):
        """测试未激活用户"""
        # 将用户设为未激活
        self.user.is_active = False
        self.user.save()
        
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        serializer = UserLoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)


class UserSerializerTest(TestCase):
    """用户序列化器测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_serialization(self):
        """测试用户序列化"""
        serializer = UserSerializer(self.user)
        data = serializer.data
        
        expected_fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        for field in expected_fields:
            self.assertIn(field, data)
        
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['first_name'], 'Test')
        self.assertEqual(data['last_name'], 'User')
    
    def test_password_not_included(self):
        """测试密码不包含在序列化数据中"""
        serializer = UserSerializer(self.user)
        data = serializer.data
        
        self.assertNotIn('password', data)


class UserProfileSerializerTest(TestCase):
    """用户资料序列化器测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = self.user.profile
    
    def test_userprofile_serialization(self):
        """测试用户资料序列化"""
        serializer = UserProfileSerializer(self.profile)
        data = serializer.data
        
        expected_fields = [
            'timezone', 'task_count', 'completed_task_count',
            'theme_preference', 'email_notifications', 'created_at', 'updated_at'
        ]
        for field in expected_fields:
            self.assertIn(field, data)
    
    def test_userprofile_update(self):
        """测试用户资料更新"""
        update_data = {
            'timezone': 'America/New_York',
            'theme_preference': 'dark',
            'email_notifications': False
        }
        
        serializer = UserProfileSerializer(self.profile, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_profile = serializer.save()
        self.assertEqual(updated_profile.timezone, 'America/New_York')
        self.assertEqual(updated_profile.theme_preference, 'dark')
        self.assertFalse(updated_profile.email_notifications)


class UserWithProfileSerializerTest(TestCase):
    """用户和资料组合序列化器测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_with_profile_serialization(self):
        """测试用户和资料组合序列化"""
        serializer = UserWithProfileSerializer(self.user)
        data = serializer.data
        
        # 应该包含用户基本信息
        user_fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        for field in user_fields:
            self.assertIn(field, data)
        
        # 应该包含资料信息
        self.assertIn('profile', data)
        profile_data = data['profile']
        
        profile_fields = ['timezone', 'task_count', 'completed_task_count', 'theme_preference']
        for field in profile_fields:
            self.assertIn(field, profile_data)

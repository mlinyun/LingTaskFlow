#!/usr/bin/env python3
"""
权限类测试脚本 - 修复版本
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import override_settings

# 设置 Django 项目路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# 配置 Django 设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ling_task_flow_backend.settings')
django.setup()

from django.contrib.auth.models import User
from django.http import HttpRequest
from LingTaskFlow.permissions import IsOwnerOrReadOnly


class SimpleTestObject:
    """简单的测试对象，模拟数据库模型"""
    def __init__(self, owner=None):
        self.owner = owner


class MockRequest:
    """模拟HTTP请求对象"""
    def __init__(self, user=None, method='GET'):
        self.user = user
        self.method = method


class MockUser:
    """模拟用户对象"""
    def __init__(self, username, is_staff=False, is_superuser=False):
        self.username = username
        self.is_authenticated = True
        self.is_staff = is_staff
        self.is_superuser = is_superuser
    
    def __eq__(self, other):
        """比较用户对象"""
        if hasattr(other, 'username'):
            return self.username == other.username
        return False
    
    def __str__(self):
        return f"MockUser({self.username})"


def create_test_user(username, is_staff=False, is_superuser=False):
    """创建测试用户"""
    return MockUser(username, is_staff, is_superuser)


def run_permission_tests():
    """运行权限测试"""
    print("=" * 60)
    print("LingTaskFlow 权限类测试")
    print("=" * 60)
    
    # 创建权限实例
    permission = IsOwnerOrReadOnly()
    
    # 创建测试用户
    regular_user = create_test_user("regular_user")
    admin_user = create_test_user("admin_user", is_staff=True)
    super_user = create_test_user("super_user", is_superuser=True)
    
    # 创建匿名用户
    class AnonymousUser:
        username = None
        is_authenticated = False
        is_staff = False
        is_superuser = False
        
        def __eq__(self, other):
            return False
    
    anonymous_user = AnonymousUser()
    
    # 创建测试对象
    test_obj = SimpleTestObject(owner=regular_user)
    
    # 测试用例
    test_cases = [
        # (user, method, expected_view_permission, expected_object_permission, description)
        (anonymous_user, 'GET', False, False, "匿名用户 - GET请求"),
        (anonymous_user, 'POST', False, False, "匿名用户 - POST请求"),
        (regular_user, 'GET', True, True, "普通用户 - GET请求"),
        (regular_user, 'POST', True, True, "对象所有者 - POST请求"),
        (admin_user, 'GET', True, True, "管理员用户 - GET请求"),
        (admin_user, 'POST', True, True, "管理员用户 - POST请求"),
        (super_user, 'GET', True, True, "超级用户 - GET请求"),
        (super_user, 'POST', True, True, "超级用户 - POST请求"),
    ]
    
    # 创建另一个用户来测试非所有者情况
    other_user = create_test_user("other_user")
    test_cases.append((other_user, 'GET', True, True, "非所有者 - GET请求（读权限）"))
    test_cases.append((other_user, 'POST', True, False, "非所有者 - POST请求（应拒绝）"))
    
    print("\n1. has_permission() 测试:")
    print("-" * 40)
    
    for user, method, expected_view, expected_obj, desc in test_cases:
        request = MockRequest(user, method)
        view_result = permission.has_permission(request, None)
        
        status = "✅ PASS" if view_result == expected_view else "❌ FAIL"
        print(f"{status} {desc}: {view_result} (期望: {expected_view})")
    
    print("\n2. has_object_permission() 测试:")
    print("-" * 40)
    
    for user, method, expected_view, expected_obj, desc in test_cases:
        # 只测试已认证用户的对象权限
        if hasattr(user, 'is_authenticated') and user.is_authenticated:
            request = MockRequest(user, method)
            obj_result = permission.has_object_permission(request, None, test_obj)
            
            status = "✅ PASS" if obj_result == expected_obj else "❌ FAIL"
            print(f"{status} {desc}: {obj_result} (期望: {expected_obj})")
        else:
            print(f"⏭️  SKIP {desc}: 用户未认证，跳过对象权限测试")
    
    print("\n3. 综合权限测试:")
    print("-" * 40)
    
    # 测试完整的权限流程
    for user, method, expected_view, expected_obj, desc in test_cases:
        request = MockRequest(user, method)
        
        # 检查视图权限
        view_perm = permission.has_permission(request, None)
        
        # 如果有视图权限，再检查对象权限
        if view_perm and hasattr(user, 'is_authenticated') and user.is_authenticated:
            obj_perm = permission.has_object_permission(request, None, test_obj)
            final_result = view_perm and obj_perm
        else:
            obj_perm = False
            final_result = False
        
        expected_final = expected_view and expected_obj
        status = "✅ PASS" if final_result == expected_final else "❌ FAIL"
        print(f"{status} {desc}: 视图权限={view_perm}, 对象权限={obj_perm}, 最终={final_result}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    run_permission_tests()

#!/usr/bin/env python
"""
简化的权限类测试
专注于测试核心的IsOwnerOrReadOnly权限类
"""

import os
import sys
import django
from unittest.mock import Mock

# 设置Django环境
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ling_task_flow_backend.settings')

django.setup()

from django.contrib.auth.models import User, AnonymousUser
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from LingTaskFlow.permissions import IsOwnerOrReadOnly

class MockObject:
    """模拟对象，用于测试权限"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

def create_test_users():
    """创建测试用户"""
    # 清理可能存在的测试用户
    User.objects.filter(username__in=['permission_user1', 'permission_user2', 'permission_admin']).delete()
    
    # 创建普通用户
    user1 = User.objects.create_user(
        username='permission_user1', 
        email='user1@test.com', 
        password='testpass'
    )
    user2 = User.objects.create_user(
        username='permission_user2', 
        email='user2@test.com', 
        password='testpass'
    )
    
    # 创建管理员用户
    admin_user = User.objects.create_user(
        username='permission_admin', 
        email='admin@test.com', 
        password='adminpass',
        is_staff=True,
        is_superuser=True
    )
    
    return user1, user2, admin_user

def create_mock_request(user, method='GET'):
    """创建模拟请求"""
    factory = APIRequestFactory()
    if method == 'GET':
        request = factory.get('/')
    elif method == 'POST':
        request = factory.post('/')
    elif method == 'PUT':
        request = factory.put('/')
    elif method == 'PATCH':
        request = factory.patch('/')
    elif method == 'DELETE':
        request = factory.delete('/')
    
    request.user = user
    return Request(request)

def test_is_owner_or_read_only_basic():
    """测试IsOwnerOrReadOnly基本功能"""
    print("🔐 测试IsOwnerOrReadOnly权限类基本功能")
    print("-" * 50)
    
    user1, user2, admin_user = create_test_users()
    permission = IsOwnerOrReadOnly()
    view = Mock()
    
    # 测试视图级权限
    print("  [1] 测试视图级权限...")
    
    # 匿名用户
    anon_request = create_mock_request(AnonymousUser(), 'GET')
    anon_result = permission.has_permission(anon_request, view)
    print(f"     匿名用户: {'✅' if not anon_result else '❌'} (期望拒绝)")
    
    # 认证用户
    auth_request = create_mock_request(user1, 'GET')
    auth_result = permission.has_permission(auth_request, view)
    print(f"     认证用户: {'✅' if auth_result else '❌'} (期望通过)")
    
    # 管理员用户
    admin_request = create_mock_request(admin_user, 'POST')
    admin_result = permission.has_permission(admin_request, view)
    print(f"     管理员用户: {'✅' if admin_result else '❌'} (期望通过)")
    
    view_tests_passed = (not anon_result) and auth_result and admin_result
    
    # 测试对象级权限
    print("\n  [2] 测试对象级权限...")
    
    # 创建测试对象
    obj = MockObject(owner=user1, title="测试对象")
    
    # 所有者读取权限
    owner_read_request = create_mock_request(user1, 'GET')
    owner_read_result = permission.has_object_permission(owner_read_request, view, obj)
    print(f"     所有者读取: {'✅' if owner_read_result else '❌'} (期望通过)")
    
    # 所有者写入权限
    owner_write_request = create_mock_request(user1, 'PUT')
    owner_write_result = permission.has_object_permission(owner_write_request, view, obj)
    print(f"     所有者写入: {'✅' if owner_write_result else '❌'} (期望通过)")
    
    # 非所有者读取权限
    other_read_request = create_mock_request(user2, 'GET')
    other_read_result = permission.has_object_permission(other_read_request, view, obj)
    print(f"     非所有者读取: {'✅' if other_read_result else '❌'} (期望通过)")
    
    # 非所有者写入权限
    other_write_request = create_mock_request(user2, 'PUT')
    other_write_result = permission.has_object_permission(other_write_request, view, obj)
    print(f"     非所有者写入: {'✅' if not other_write_result else '❌'} (期望拒绝)")
    
    # 管理员写入权限
    admin_write_request = create_mock_request(admin_user, 'DELETE')
    admin_write_result = permission.has_object_permission(admin_write_request, view, obj)
    print(f"     管理员写入: {'✅' if admin_write_result else '❌'} (期望通过)")
    
    object_tests_passed = (owner_read_result and owner_write_result and 
                          other_read_result and not other_write_result and 
                          admin_write_result)
    
    return view_tests_passed and object_tests_passed

def test_different_owner_attributes():
    """测试不同的所有者属性"""
    print("\n🏷️  测试不同的所有者属性")
    print("-" * 50)
    
    user1, user2, admin_user = create_test_users()
    permission = IsOwnerOrReadOnly()
    view = Mock()
    
    # 测试不同的所有者属性
    objects = [
        MockObject(owner=user1, name="owner属性对象"),
        MockObject(user=user1, name="user属性对象"),
        MockObject(created_by=user1, name="created_by属性对象"),
        MockObject(title="测试", name="无所有者属性对象")
    ]
    
    expected_results = [True, True, True, False]  # 对user1的写权限期望
    
    results = []
    
    for i, obj in enumerate(objects):
        request = create_mock_request(user1, 'PUT')
        result = permission.has_object_permission(request, view, obj)
        expected = expected_results[i]
        success = result == expected
        results.append(success)
        
        status = "✅" if success else "❌"
        print(f"     {status} {obj.name}: {'通过' if result else '拒绝'}")
        if not success:
            print(f"        期望: {'通过' if expected else '拒绝'}, 实际: {'通过' if result else '拒绝'}")
    
    return all(results)

def main():
    """主测试函数"""
    print("🔐 LingTaskFlow 权限类简化测试")
    print("=" * 60)
    
    try:
        # 运行测试
        test1_result = test_is_owner_or_read_only_basic()
        test2_result = test_different_owner_attributes()
        
        # 显示总结
        print("\n" + "=" * 60)
        print("📊 测试总结")
        print("=" * 60)
        
        total_tests = 2
        passed_tests = sum([test1_result, test2_result])
        
        print(f"总测试组: {total_tests}")
        print(f"通过测试组: {passed_tests}")
        print(f"失败测试组: {total_tests - passed_tests}")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
        
        if passed_tests == total_tests:
            print("\n🎉 权限类核心功能测试通过！")
            return True
        else:
            print(f"\n⚠️  有 {total_tests - passed_tests} 个测试组失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试执行异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

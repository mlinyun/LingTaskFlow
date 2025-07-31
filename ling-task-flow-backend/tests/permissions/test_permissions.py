#!/usr/bin/env python
"""
测试权限类功能
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
from LingTaskFlow.permissions import (
    IsOwnerOrReadOnly,
    IsOwner,
    IsAuthorOrReadOnly,
    IsAdminOrReadOnly,
    IsSelfOrReadOnly
)

class MockObject:
    """模拟对象，用于测试权限"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

def create_test_users():
    """创建测试用户"""
    # 清理可能存在的测试用户
    User.objects.filter(username__in=['testuser1', 'testuser2', 'admin_user']).delete()
    
    # 创建普通用户
    user1 = User.objects.create_user(username='testuser1', email='user1@test.com', password='testpass')
    user2 = User.objects.create_user(username='testuser2', email='user2@test.com', password='testpass')
    
    # 创建管理员用户
    admin_user = User.objects.create_user(
        username='admin_user', 
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

def test_is_owner_or_read_only():
    """测试IsOwnerOrReadOnly权限类"""
    print("🔐 测试IsOwnerOrReadOnly权限类")
    print("-" * 50)
    
    user1, user2, admin_user = create_test_users()
    permission = IsOwnerOrReadOnly()
    view = Mock()
    
    # 测试用例
    test_cases = [
        {
            'name': '匿名用户访问',
            'user': AnonymousUser(),
            'method': 'GET',
            'expected': False,
            'description': '匿名用户应该被拒绝'
        },
        {
            'name': '已认证用户读取权限',
            'user': user1,
            'method': 'GET',
            'expected': True,
            'description': '已认证用户应该有读取权限'
        },
        {
            'name': '管理员所有权限',
            'user': admin_user,
            'method': 'POST',
            'expected': True,
            'description': '管理员应该有所有权限'
        }
    ]
    
    results = []
    
    for case in test_cases:
        request = create_mock_request(case['user'], case['method'])
        result = permission.has_permission(request, view)
        success = result == case['expected']
        results.append(success)
        
        status = "✅" if success else "❌"
        print(f"  {status} {case['name']}: {case['description']}")
        if not success:
            print(f"     期望: {case['expected']}, 实际: {result}")
    
    # 测试对象权限
    print("\n  对象权限测试:")
    
    # 创建测试对象
    obj_with_owner = MockObject(owner=user1)
    obj_with_user = MockObject(user=user1)
    obj_without_owner = MockObject(title="test")
    
    object_test_cases = [
        {
            'name': '所有者写权限',
            'user': user1,
            'method': 'PUT',
            'obj': obj_with_owner,
            'expected': True
        },
        {
            'name': '非所有者写权限',
            'user': user2,
            'method': 'PUT',
            'obj': obj_with_owner,
            'expected': False
        },
        {
            'name': '所有者读权限',
            'user': user1,
            'method': 'GET',
            'obj': obj_with_owner,
            'expected': True
        },
        {
            'name': '非所有者读权限',
            'user': user2,
            'method': 'GET',
            'obj': obj_with_owner,
            'expected': True
        },
        {
            'name': 'user属性对象权限',
            'user': user1,
            'method': 'PUT',
            'obj': obj_with_user,
            'expected': True
        },
        {
            'name': '无所有者属性对象',
            'user': user1,
            'method': 'PUT',
            'obj': obj_without_owner,
            'expected': False
        }
    ]
    
    for case in object_test_cases:
        request = create_mock_request(case['user'], case['method'])
        result = permission.has_object_permission(request, view, case['obj'])
        success = result == case['expected']
        results.append(success)
        
        status = "✅" if success else "❌"
        print(f"  {status} {case['name']}")
        if not success:
            print(f"     期望: {case['expected']}, 实际: {result}")
    
    passed = sum(results)
    total = len(results)
    print(f"\n  IsOwnerOrReadOnly测试结果: {passed}/{total} 通过")
    return passed == total

def test_is_owner():
    """测试IsOwner权限类"""
    print("\n🔒 测试IsOwner权限类")
    print("-" * 50)
    
    user1, user2, admin_user = create_test_users()
    permission = IsOwner()
    view = Mock()
    
    obj = MockObject(owner=user1)
    
    test_cases = [
        {
            'name': '所有者读取',
            'user': user1,
            'method': 'GET',
            'expected': True
        },
        {
            'name': '所有者写入',
            'user': user1,
            'method': 'PUT',
            'expected': True
        },
        {
            'name': '非所有者读取',
            'user': user2,
            'method': 'GET',
            'expected': False
        },
        {
            'name': '非所有者写入',
            'user': user2,
            'method': 'PUT',
            'expected': False
        },
        {
            'name': '管理员访问',
            'user': admin_user,
            'method': 'DELETE',
            'expected': True
        }
    ]
    
    results = []
    
    for case in test_cases:
        request = create_mock_request(case['user'], case['method'])
        result = permission.has_object_permission(request, view, obj)
        success = result == case['expected']
        results.append(success)
        
        status = "✅" if success else "❌"
        print(f"  {status} {case['name']}")
        if not success:
            print(f"     期望: {case['expected']}, 实际: {result}")
    
    passed = sum(results)
    total = len(results)
    print(f"\n  IsOwner测试结果: {passed}/{total} 通过")
    return passed == total

def test_is_self_or_read_only():
    """测试IsSelfOrReadOnly权限类"""
    print("\n👤 测试IsSelfOrReadOnly权限类")
    print("-" * 50)
    
    user1, user2, admin_user = create_test_users()
    permission = IsSelfOrReadOnly()
    view = Mock()
    
    test_cases = [
        {
            'name': '用户修改自己',
            'user': user1,
            'method': 'PUT',
            'obj': user1,  # 用户对象本身
            'expected': True
        },
        {
            'name': '用户修改他人',
            'user': user1,
            'method': 'PUT',
            'obj': user2,
            'expected': False
        },
        {
            'name': '用户读取他人',
            'user': user1,
            'method': 'GET',
            'obj': user2,
            'expected': True
        },
        {
            'name': '管理员修改他人',
            'user': admin_user,
            'method': 'PUT',
            'obj': user1,
            'expected': True
        }
    ]
    
    results = []
    
    for case in test_cases:
        request = create_mock_request(case['user'], case['method'])
        result = permission.has_object_permission(request, view, case['obj'])
        success = result == case['expected']
        results.append(success)
        
        status = "✅" if success else "❌"
        print(f"  {status} {case['name']}")
        if not success:
            print(f"     期望: {case['expected']}, 实际: {result}")
    
    passed = sum(results)
    total = len(results)
    print(f"\n  IsSelfOrReadOnly测试结果: {passed}/{total} 通过")
    return passed == total

def test_is_admin_or_read_only():
    """测试IsAdminOrReadOnly权限类"""
    print("\n👑 测试IsAdminOrReadOnly权限类")
    print("-" * 50)
    
    user1, user2, admin_user = create_test_users()
    permission = IsAdminOrReadOnly()
    view = Mock()
    obj = MockObject(title="test object")
    
    test_cases = [
        {
            'name': '普通用户读取',
            'user': user1,
            'method': 'GET',
            'has_permission': True,
            'has_object_permission': True
        },
        {
            'name': '普通用户写入',
            'user': user1,
            'method': 'POST',
            'has_permission': False,
            'has_object_permission': False
        },
        {
            'name': '管理员读取',
            'user': admin_user,
            'method': 'GET',
            'has_permission': True,
            'has_object_permission': True
        },
        {
            'name': '管理员写入',
            'user': admin_user,
            'method': 'POST',
            'has_permission': True,
            'has_object_permission': True
        }
    ]
    
    results = []
    
    for case in test_cases:
        request = create_mock_request(case['user'], case['method'])
        
        # 测试视图权限
        perm_result = permission.has_permission(request, view)
        perm_success = perm_result == case['has_permission']
        
        # 测试对象权限
        obj_result = permission.has_object_permission(request, view, obj)
        obj_success = obj_result == case['has_object_permission']
        
        success = perm_success and obj_success
        results.append(success)
        
        status = "✅" if success else "❌"
        print(f"  {status} {case['name']}")
        if not success:
            print(f"     视图权限 - 期望: {case['has_permission']}, 实际: {perm_result}")
            print(f"     对象权限 - 期望: {case['has_object_permission']}, 实际: {obj_result}")
    
    passed = sum(results)
    total = len(results)
    print(f"\n  IsAdminOrReadOnly测试结果: {passed}/{total} 通过")
    return passed == total

def main():
    """主测试函数"""
    print("🔐 LingTaskFlow 权限类测试")
    print("=" * 60)
    
    tests = [
        ("IsOwnerOrReadOnly", test_is_owner_or_read_only),
        ("IsOwner", test_is_owner),
        ("IsSelfOrReadOnly", test_is_self_or_read_only),
        ("IsAdminOrReadOnly", test_is_admin_or_read_only),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {str(e)}")
            results.append((test_name, False))
    
    # 显示总结
    print("\n" + "=" * 60)
    print("📊 权限类测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"总权限类测试: {total}")
    print(f"通过测试: {passed}")
    print(f"失败测试: {total - passed}")
    print(f"成功率: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n🎉 所有权限类测试都通过了！")
        return True
    else:
        print(f"\n⚠️  有 {total - passed} 个权限类测试失败")
        print("\n失败的测试:")
        for test_name, success in results:
            if not success:
                print(f"  - {test_name}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 测试执行异常: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)

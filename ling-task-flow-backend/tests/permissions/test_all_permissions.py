#!/usr/bin/env python3
"""
完整权限类测试脚本 - 测试所有权限类
"""
import os
import sys
import django

# 设置 Django 项目路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# 配置 Django 设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ling_task_flow_backend.settings')
django.setup()

from LingTaskFlow.permissions import (
    IsOwnerOrReadOnly,
    IsOwner,
    IsAuthorOrReadOnly,
    IsAdminOrReadOnly,
    IsSelfOrReadOnly
)


class MockUser:
    """模拟用户对象"""
    def __init__(self, username, is_staff=False, is_superuser=False):
        self.username = username
        self.is_authenticated = True
        self.is_staff = is_staff
        self.is_superuser = is_superuser
    
    def __eq__(self, other):
        if hasattr(other, 'username'):
            return self.username == other.username
        return False
    
    def __str__(self):
        return f"MockUser({self.username})"


class AnonymousUser:
    """匿名用户"""
    username = None
    is_authenticated = False
    is_staff = False
    is_superuser = False
    
    def __eq__(self, other):
        return False


class MockRequest:
    """模拟HTTP请求对象"""
    def __init__(self, user=None, method='GET'):
        self.user = user
        self.method = method


class TestObject:
    """测试对象 - 带owner属性"""
    def __init__(self, owner=None):
        self.owner = owner


class TestUserProfile:
    """测试用户资料对象 - 带user属性"""
    def __init__(self, user=None):
        self.user = user


class TestPost:
    """测试文章对象 - 带author属性"""
    def __init__(self, author=None):
        self.author = author


def test_permission_class(permission_class, class_name, test_scenarios):
    """测试权限类"""
    print(f"\n{'='*60}")
    print(f"测试权限类: {class_name}")
    print(f"{'='*60}")
    
    permission = permission_class()
    
    for scenario in test_scenarios:
        user = scenario['user']
        method = scenario['method']
        obj = scenario['obj']
        expected_view = scenario['expected_view']
        expected_object = scenario['expected_object']
        description = scenario['description']
        
        # 测试视图权限
        request = MockRequest(user, method)
        view_result = permission.has_permission(request, None)
        
        # 测试对象权限
        if hasattr(user, 'is_authenticated') and user.is_authenticated:
            object_result = permission.has_object_permission(request, None, obj)
        else:
            object_result = False
        
        # 检查结果
        view_status = "✅" if view_result == expected_view else "❌"
        object_status = "✅" if object_result == expected_object else "❌"
        
        print(f"{view_status}{object_status} {description}")
        print(f"    视图权限: {view_result} (期望: {expected_view})")
        print(f"    对象权限: {object_result} (期望: {expected_object})")
        print()


def main():
    """主测试函数"""
    print("LingTaskFlow 权限系统完整测试")
    print("测试所有权限类的功能")
    
    # 创建测试用户
    anonymous = AnonymousUser()
    regular_user = MockUser("regular")
    admin_user = MockUser("admin", is_staff=True)
    super_user = MockUser("super", is_superuser=True)
    other_user = MockUser("other")
    
    # 创建测试对象
    task_owned_by_regular = TestObject(owner=regular_user)
    profile_owned_by_regular = TestUserProfile(user=regular_user)
    post_by_regular = TestPost(author=regular_user)
    
    # 1. 测试 IsOwnerOrReadOnly
    test_scenarios = [
        {
            'user': anonymous, 'method': 'GET', 'obj': task_owned_by_regular,
            'expected_view': False, 'expected_object': False,
            'description': '匿名用户访问任务'
        },
        {
            'user': regular_user, 'method': 'GET', 'obj': task_owned_by_regular,
            'expected_view': True, 'expected_object': True,
            'description': '任务所有者读取自己的任务'
        },
        {
            'user': regular_user, 'method': 'PUT', 'obj': task_owned_by_regular,
            'expected_view': True, 'expected_object': True,
            'description': '任务所有者修改自己的任务'
        },
        {
            'user': other_user, 'method': 'GET', 'obj': task_owned_by_regular,
            'expected_view': True, 'expected_object': True,
            'description': '其他用户读取任务（允许）'
        },
        {
            'user': other_user, 'method': 'PUT', 'obj': task_owned_by_regular,
            'expected_view': True, 'expected_object': False,
            'description': '其他用户修改任务（拒绝）'
        },
        {
            'user': admin_user, 'method': 'DELETE', 'obj': task_owned_by_regular,
            'expected_view': True, 'expected_object': True,
            'description': '管理员删除任务（允许）'
        },
    ]
    test_permission_class(IsOwnerOrReadOnly, "IsOwnerOrReadOnly", test_scenarios)
    
    # 2. 测试 IsOwner
    test_scenarios = [
        {
            'user': regular_user, 'method': 'GET', 'obj': task_owned_by_regular,
            'expected_view': True, 'expected_object': True,
            'description': '所有者访问自己的对象'
        },
        {
            'user': other_user, 'method': 'GET', 'obj': task_owned_by_regular,
            'expected_view': True, 'expected_object': False,
            'description': '非所有者访问对象（拒绝）'
        },
        {
            'user': admin_user, 'method': 'GET', 'obj': task_owned_by_regular,
            'expected_view': True, 'expected_object': True,
            'description': '管理员访问任何对象（允许）'
        },
    ]
    test_permission_class(IsOwner, "IsOwner", test_scenarios)
    
    # 3. 测试 IsAuthorOrReadOnly
    test_scenarios = [
        {
            'user': regular_user, 'method': 'GET', 'obj': post_by_regular,
            'expected_view': True, 'expected_object': True,
            'description': '作者读取自己的文章'
        },
        {
            'user': regular_user, 'method': 'PUT', 'obj': post_by_regular,
            'expected_view': True, 'expected_object': True,
            'description': '作者修改自己的文章'
        },
        {
            'user': other_user, 'method': 'GET', 'obj': post_by_regular,
            'expected_view': True, 'expected_object': True,
            'description': '其他用户读取文章（允许）'
        },
        {
            'user': other_user, 'method': 'PUT', 'obj': post_by_regular,
            'expected_view': True, 'expected_object': False,
            'description': '其他用户修改文章（拒绝）'
        },
    ]
    test_permission_class(IsAuthorOrReadOnly, "IsAuthorOrReadOnly", test_scenarios)
    
    # 4. 测试 IsAdminOrReadOnly
    test_scenarios = [
        {
            'user': regular_user, 'method': 'GET', 'obj': task_owned_by_regular,
            'expected_view': True, 'expected_object': True,
            'description': '普通用户读取（允许）'
        },
        {
            'user': regular_user, 'method': 'POST', 'obj': task_owned_by_regular,
            'expected_view': False, 'expected_object': False,
            'description': '普通用户写入（拒绝）'
        },
        {
            'user': admin_user, 'method': 'POST', 'obj': task_owned_by_regular,
            'expected_view': True, 'expected_object': True,
            'description': '管理员写入（允许）'
        },
        {
            'user': super_user, 'method': 'DELETE', 'obj': task_owned_by_regular,
            'expected_view': True, 'expected_object': True,
            'description': '超级用户删除（允许）'
        },
    ]
    test_permission_class(IsAdminOrReadOnly, "IsAdminOrReadOnly", test_scenarios)
    
    # 5. 测试 IsSelfOrReadOnly
    test_scenarios = [
        {
            'user': regular_user, 'method': 'GET', 'obj': profile_owned_by_regular,
            'expected_view': True, 'expected_object': True,
            'description': '用户读取自己的资料'
        },
        {
            'user': regular_user, 'method': 'PUT', 'obj': profile_owned_by_regular,
            'expected_view': True, 'expected_object': True,
            'description': '用户修改自己的资料'
        },
        {
            'user': other_user, 'method': 'GET', 'obj': profile_owned_by_regular,
            'expected_view': True, 'expected_object': True,
            'description': '其他用户读取资料（允许）'
        },
        {
            'user': other_user, 'method': 'PUT', 'obj': profile_owned_by_regular,
            'expected_view': True, 'expected_object': False,
            'description': '其他用户修改资料（拒绝）'
        },
        {
            'user': admin_user, 'method': 'PUT', 'obj': profile_owned_by_regular,
            'expected_view': True, 'expected_object': True,
            'description': '管理员修改资料（允许）'
        },
    ]
    test_permission_class(IsSelfOrReadOnly, "IsSelfOrReadOnly", test_scenarios)
    
    print(f"\n{'='*60}")
    print("所有权限类测试完成！")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

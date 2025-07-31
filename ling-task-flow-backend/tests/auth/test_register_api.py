#!/usr/bin/env python
"""
用户注册API功能测试脚本
测试任务1.2.2：实现用户注册API(/api/auth/register/)
"""
import os
import sys
import django
import requests
import json
import time
from django.conf import settings

# 设置Django环境
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ling_task_flow_backend.settings')
django.setup()

from django.contrib.auth.models import User
from LingTaskFlow.models import UserProfile

API_BASE_URL = "http://localhost:8000/api"

def test_successful_registration():
    """测试成功注册"""
    print("=== 测试成功注册 ===")
    
    test_data = {
        "username": "testuser_success",
        "email": "success@example.com",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!"
    }
    
    # 清理可能存在的测试用户
    User.objects.filter(username=test_data["username"]).delete()
    
    response = requests.post(
        f"{API_BASE_URL}/auth/register/",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 201, f"期望状态码201，实际{response.status_code}"
    
    data = response.json()
    assert data["success"] == True, "注册应该成功"
    assert "user" in data["data"], "响应应包含用户信息"
    assert "tokens" in data["data"], "响应应包含JWT Token"
    assert "profile" in data["data"]["user"], "响应应包含用户档案"
    
    # 验证数据库中用户已创建
    user = User.objects.get(username=test_data["username"])
    assert user.email == test_data["email"], "邮箱应正确保存"
    
    # 验证UserProfile已自动创建
    profile = UserProfile.objects.get(user=user)
    assert profile.timezone == "Asia/Shanghai", "默认时区应为Asia/Shanghai"
    
    print("✓ 成功注册测试通过")
    return data

def test_validation_errors():
    """测试各种验证错误"""
    print("\n=== 测试验证错误 ===")
    
    test_cases = [
        {
            "name": "用户名已存在",
            "data": {
                "username": "testuser_success",  # 已存在的用户名
                "email": "new@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!"
            },
            "expected_error_field": "username"
        },
        {
            "name": "邮箱已存在",
            "data": {
                "username": "newuser",
                "email": "success@example.com",  # 已存在的邮箱
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!"
            },
            "expected_error_field": "email"
        },
        {
            "name": "用户名格式错误",
            "data": {
                "username": "123invalid",  # 数字开头
                "email": "format@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!"
            },
            "expected_error_field": "username"
        },
        {
            "name": "邮箱格式错误",
            "data": {
                "username": "validuser",
                "email": "invalid-email",  # 无效邮箱格式
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!"
            },
            "expected_error_field": "email"
        },
        {
            "name": "密码太短",
            "data": {
                "username": "shortpass",
                "email": "short@example.com",
                "password": "weak",  # 太短
                "password_confirm": "weak"
            },
            "expected_error_field": "password"
        },
        {
            "name": "密码不匹配",
            "data": {
                "username": "mismatch",
                "email": "mismatch@example.com",
                "password": "SecurePass123!",
                "password_confirm": "DifferentPass123!"  # 不匹配
            },
            "expected_error_field": "password_confirm"
        },
        {
            "name": "弱密码",
            "data": {
                "username": "weakpass",
                "email": "weak@example.com",
                "password": "password123",  # 常见弱密码
                "password_confirm": "password123"
            },
            "expected_error_field": "password"
        }
    ]
    
    for test_case in test_cases:
        print(f"  测试: {test_case['name']}")
        
        response = requests.post(
            f"{API_BASE_URL}/auth/register/",
            json=test_case["data"],
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400, f"期望状态码400，实际{response.status_code}"
        
        data = response.json()
        assert data["success"] == False, "验证失败应返回success=False"
        assert "errors" in data, "应包含错误信息"
        
        if test_case["expected_error_field"] not in ["password_confirm"]:
            # password_confirm错误可能在不同字段中
            assert test_case["expected_error_field"] in data["errors"], \
                f"应包含{test_case['expected_error_field']}字段错误"
        
        print(f"    ✓ {test_case['name']} 验证正确")
    
    print("✓ 验证错误测试通过")

def test_missing_fields():
    """测试缺少必需字段"""
    print("\n=== 测试缺少必需字段 ===")
    
    incomplete_data = {
        "username": "incomplete",
        "email": "incomplete@example.com"
        # 缺少password和password_confirm
    }
    
    response = requests.post(
        f"{API_BASE_URL}/auth/register/",
        json=incomplete_data,
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 400, f"期望状态码400，实际{response.status_code}"
    
    data = response.json()
    assert data["success"] == False, "缺少字段应返回success=False"
    assert "errors" in data, "应包含错误信息"
    
    print("✓ 缺少必需字段测试通过")

def test_response_format():
    """测试响应格式"""
    print("\n=== 测试响应格式 ===")
    
    test_data = {
        "username": "formattest",
        "email": "format@example.com",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!"
    }
    
    # 清理可能存在的测试用户
    User.objects.filter(username=test_data["username"]).delete()
    
    response = requests.post(
        f"{API_BASE_URL}/auth/register/",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    data = response.json()
    
    # 验证响应结构
    required_fields = ["success", "message", "data"]
    for field in required_fields:
        assert field in data, f"响应应包含{field}字段"
    
    # 验证用户数据结构
    user_data = data["data"]["user"]
    user_required_fields = ["id", "username", "email", "profile"]
    for field in user_required_fields:
        assert field in user_data, f"用户数据应包含{field}字段"
    
    # 验证档案数据结构
    profile_data = user_data["profile"]
    profile_required_fields = ["timezone", "theme_preference", "email_notifications", "task_count"]
    for field in profile_required_fields:
        assert field in profile_data, f"档案数据应包含{field}字段"
    
    # 验证Token结构
    tokens = data["data"]["tokens"]
    token_required_fields = ["access", "refresh"]
    for field in token_required_fields:
        assert field in tokens, f"Token数据应包含{field}字段"
        assert isinstance(tokens[field], str), f"{field} token应为字符串"
        assert len(tokens[field]) > 100, f"{field} token长度应合理"
    
    print("✓ 响应格式测试通过")

def clean_test_data():
    """清理测试数据"""
    print("\n=== 清理测试数据 ===")
    
    test_usernames = [
        "testuser_success", "formattest", "newuser", "validuser",
        "shortpass", "mismatch", "weakpass", "incomplete"
    ]
    
    deleted_count = 0
    for username in test_usernames:
        deleted = User.objects.filter(username=username).delete()[0]
        deleted_count += deleted
    
    print(f"✓ 清理了 {deleted_count} 个测试用户")

def main():
    """主测试函数"""
    print("开始用户注册API功能测试\n")
    
    try:
        # 检查服务器连接
        response = requests.get(f"{API_BASE_URL}/health/")
        if response.status_code != 200:
            print("❌ 无法连接到API服务器，请确保服务器正在运行")
            return False
        
        test_successful_registration()
        test_validation_errors()
        test_missing_fields()
        test_response_format()
        
        print("\n🎉 所有测试通过！用户注册API功能正常")
        
        clean_test_data()
        return True
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"\n💥 请求错误: {e}")
        return False
    except Exception as e:
        print(f"\n💥 测试出错: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

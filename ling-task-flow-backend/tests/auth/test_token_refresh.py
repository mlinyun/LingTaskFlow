#!/usr/bin/env python
"""
测试Token刷新API功能
"""

import requests
import json
import time
from datetime import datetime

# API配置
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login/"
REFRESH_URL = f"{BASE_URL}/api/auth/token/refresh/"

def test_token_refresh():
    """测试Token刷新API功能"""
    print("🔄 测试Token刷新API功能")
    print("=" * 50)
    
    # 步骤1: 先登录获取tokens
    print("[1] 登录获取初始tokens...")
    login_data = {
        "username": "testadmin",
        "password": "TestPassword123!"
    }
    
    try:
        login_response = requests.post(LOGIN_URL, json=login_data, timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ 登录失败: {login_response.status_code}")
            print(f"   响应: {login_response.text}")
            return False
        
        login_data = login_response.json()
        
        if not login_data.get('success'):
            print(f"❌ 登录失败: {login_data.get('message')}")
            return False
        
        # 提取tokens
        tokens = login_data['data']['tokens']
        access_token = tokens['access']
        refresh_token = tokens['refresh']
        
        print("✅ 登录成功，获取到tokens")
        print(f"   Access Token (前50字符): {access_token[:50]}...")
        print(f"   Refresh Token (前50字符): {refresh_token[:50]}...")
        
    except Exception as e:
        print(f"❌ 登录异常: {str(e)}")
        return False
    
    # 步骤2: 使用refresh token获取新的access token
    print("\n[2] 使用refresh token获取新的access token...")
    
    refresh_data = {
        "refresh": refresh_token
    }
    
    try:
        refresh_response = requests.post(REFRESH_URL, json=refresh_data, timeout=10)
        
        if refresh_response.status_code == 200:
            refresh_result = refresh_response.json()
            
            if refresh_result.get('success'):
                new_access_token = refresh_result['data']['access']
                expires_in = refresh_result['data']['access_expires_in']
                
                print("✅ Token刷新成功")
                print(f"   新Access Token (前50字符): {new_access_token[:50]}...")
                print(f"   过期时间戳: {expires_in}")
                print(f"   Token类型: {refresh_result['data']['token_type']}")
                
                # 验证新token与旧token不同
                if new_access_token != access_token:
                    print("✅ 新token与旧token不同（正常）")
                else:
                    print("⚠️  新token与旧token相同（可能有问题）")
                
                return True
            else:
                print(f"❌ Token刷新失败: {refresh_result.get('message')}")
                return False
        else:
            print(f"❌ Token刷新HTTP错误: {refresh_response.status_code}")
            print(f"   响应: {refresh_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Token刷新异常: {str(e)}")
        return False

def test_invalid_refresh_token():
    """测试无效的refresh token"""
    print("\n[3] 测试无效的refresh token...")
    
    invalid_tokens = [
        {"name": "空token", "token": ""},
        {"name": "无效格式", "token": "invalid_token_123"},
        {"name": "过期token", "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY3MzAzMDQwMCwiaWF0IjoxNjczMDI2ODAwLCJqdGkiOiJhYmMxMjMiLCJ1c2VyX2lkIjoiMSJ9.invalid"},
    ]
    
    success_count = 0
    
    for test_case in invalid_tokens:
        print(f"\n   测试 {test_case['name']}...")
        
        try:
            refresh_data = {"refresh": test_case["token"]}
            response = requests.post(REFRESH_URL, json=refresh_data, timeout=10)
            
            if response.status_code in [400, 401]:
                result = response.json()
                if not result.get('success', True):
                    print(f"   ✅ 正确拒绝: {result.get('message', '未知错误')}")
                    success_count += 1
                else:
                    print(f"   ❌ 应该拒绝但返回success=true")
            else:
                print(f"   ❌ 意外的状态码: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 测试异常: {str(e)}")
    
    print(f"\n   无效token测试结果: {success_count}/{len(invalid_tokens)} 通过")
    return success_count == len(invalid_tokens)

def test_missing_refresh_token():
    """测试缺少refresh token的情况"""
    print("\n[4] 测试缺少refresh token...")
    
    try:
        # 发送空请求体
        response = requests.post(REFRESH_URL, json={}, timeout=10)
        
        if response.status_code == 400:
            result = response.json()
            if not result.get('success', True) and 'refresh' in str(result):
                print("✅ 正确处理缺少refresh token的情况")
                print(f"   消息: {result.get('message', '未知')}")
                return True
            else:
                print(f"❌ 错误消息不正确: {result}")
                return False
        else:
            print(f"❌ 状态码应为400，实际: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

def test_rate_limiting():
    """测试频率限制"""
    print("\n[5] 测试频率限制...")
    print("   进行快速连续请求...")
    
    # 快速发送多个请求测试频率限制
    invalid_token = "invalid_token_for_rate_limit_test"
    
    rate_limited = False
    
    for i in range(12):  # 超过限制的10次
        try:
            refresh_data = {"refresh": invalid_token}
            response = requests.post(REFRESH_URL, json=refresh_data, timeout=5)
            
            if response.status_code == 429:
                print(f"   ✅ 第{i+1}次请求触发频率限制")
                rate_limited = True
                break
            elif i < 10:
                print(f"   第{i+1}次请求: {response.status_code}")
            
            time.sleep(0.1)  # 短暂延迟
            
        except Exception as e:
            print(f"   第{i+1}次请求异常: {str(e)}")
            break
    
    if rate_limited:
        print("   ✅ 频率限制功能正常")
        return True
    else:
        print("   ⚠️  未触发频率限制（可能需要更多请求或检查配置）")
        return False

def main():
    """主测试函数"""
    print("🔄 Token刷新API完整测试")
    print("=" * 50)
    
    tests = [
        ("基本Token刷新功能", test_token_refresh),
        ("无效Token处理", test_invalid_refresh_token),
        ("缺少Token处理", test_missing_refresh_token),
        ("频率限制测试", test_rate_limiting),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)
        
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
                
        except Exception as e:
            print(f"❌ {test_name} 异常: {str(e)}")
            results.append((test_name, False))
        
        time.sleep(0.5)  # 测试间隔
    
    # 显示总结
    print("\n" + "=" * 50)
    print("📊 测试总结")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"总测试数: {total}")
    print(f"通过测试: {passed}")
    print(f"失败测试: {total - passed}")
    print(f"成功率: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n🎉 所有测试都通过了！Token刷新API功能正常！")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
        print("\n失败的测试:")
        for test_name, success in results:
            if not success:
                print(f"  - {test_name}")

if __name__ == "__main__":
    print("请确保Django开发服务器正在运行：python manage.py runserver")
    input("按Enter键开始测试...")
    main()

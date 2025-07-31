#!/usr/bin/env python
"""
简化的Token刷新API测试脚本
自动运行，无需手动交互
"""

import requests
import json
import time
from datetime import datetime

# API配置
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login/"
REFRESH_URL = f"{BASE_URL}/api/auth/token/refresh/"

def check_server_status():
    """检查服务器是否可访问"""
    try:
        response = requests.get(f"{BASE_URL}/api/health/", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_basic_token_refresh():
    """测试基本Token刷新功能"""
    print("🔄 测试基本Token刷新功能")
    print("-" * 40)
    
    # 步骤1: 登录获取tokens
    print("  [1] 登录获取初始tokens...")
    login_data = {
        "username": "testadmin",
        "password": "TestPassword123!"
    }
    
    try:
        login_response = requests.post(LOGIN_URL, json=login_data, timeout=10)
        
        if login_response.status_code != 200:
            print(f"  ❌ 登录失败: HTTP {login_response.status_code}")
            try:
                error_data = login_response.json()
                print(f"     错误: {error_data.get('message', '未知错误')}")
            except:
                print(f"     响应: {login_response.text[:200]}...")
            return False
        
        login_result = login_response.json()
        
        if not login_result.get('success'):
            print(f"  ❌ 登录失败: {login_result.get('message', '未知错误')}")
            return False
        
        # 提取tokens
        tokens = login_result['data']['tokens']
        access_token = tokens['access']
        refresh_token = tokens['refresh']
        
        print("  ✅ 登录成功，获取到tokens")
        print(f"     Access Token: {access_token[:30]}...")
        print(f"     Refresh Token: {refresh_token[:30]}...")
        
    except requests.exceptions.ConnectionError:
        print("  ❌ 无法连接到服务器，请检查Django服务器是否运行在端口8000")
        return False
    except Exception as e:
        print(f"  ❌ 登录异常: {str(e)}")
        return False
    
    # 步骤2: 使用refresh token获取新的access token
    print("\n  [2] 使用refresh token获取新的access token...")
    
    refresh_data = {"refresh": refresh_token}
    
    try:
        refresh_response = requests.post(REFRESH_URL, json=refresh_data, timeout=10)
        
        if refresh_response.status_code == 200:
            refresh_result = refresh_response.json()
            
            if refresh_result.get('success'):
                new_access_token = refresh_result['data']['access']
                expires_in = refresh_result['data']['access_expires_in']
                
                print("  ✅ Token刷新成功")
                print(f"     新Access Token: {new_access_token[:30]}...")
                print(f"     过期时间戳: {expires_in}")
                print(f"     Token类型: {refresh_result['data']['token_type']}")
                
                # 验证新token与旧token不同
                if new_access_token != access_token:
                    print("  ✅ 新token与旧token不同（正常）")
                else:
                    print("  ⚠️  新token与旧token相同（可能有问题）")
                
                return True
            else:
                print(f"  ❌ Token刷新失败: {refresh_result.get('message', '未知错误')}")
                return False
        else:
            print(f"  ❌ Token刷新HTTP错误: {refresh_response.status_code}")
            try:
                error_data = refresh_response.json()
                print(f"     错误: {error_data.get('message', '未知错误')}")
            except:
                print(f"     响应: {refresh_response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"  ❌ Token刷新异常: {str(e)}")
        return False

def test_invalid_refresh_tokens():
    """测试无效的refresh token处理"""
    print("\n🚫 测试无效refresh token处理")
    print("-" * 40)
    
    invalid_cases = [
        {"name": "空token", "token": "", "expected_status": 400},
        {"name": "无效格式", "token": "invalid_token_123", "expected_status": 401},
        {"name": "缺少refresh字段", "data": {}, "expected_status": 400},
    ]
    
    passed = 0
    total = len(invalid_cases)
    
    for i, case in enumerate(invalid_cases, 1):
        print(f"  [{i}] 测试 {case['name']}...")
        
        try:
            if 'data' in case:
                request_data = case['data']
            else:
                request_data = {"refresh": case["token"]}
            
            response = requests.post(REFRESH_URL, json=request_data, timeout=10)
            
            if response.status_code == case['expected_status']:
                result = response.json()
                if not result.get('success', True):
                    print(f"     ✅ 正确拒绝: {result.get('message', '无错误信息')}")
                    passed += 1
                else:
                    print(f"     ❌ 应该拒绝但返回success=true")
            else:
                print(f"     ❌ 期望状态码{case['expected_status']}，实际{response.status_code}")
                
        except Exception as e:
            print(f"     ❌ 测试异常: {str(e)}")
    
    print(f"\n  无效token测试结果: {passed}/{total} 通过")
    return passed == total

def test_server_health():
    """测试服务器健康状态"""
    print("🏥 检查服务器健康状态")
    print("-" * 40)
    
    try:
        # 测试健康检查端点
        response = requests.get(f"{BASE_URL}/api/health/", timeout=5)
        if response.status_code == 200:
            print("  ✅ 健康检查端点正常")
            return True
        else:
            print(f"  ❌ 健康检查失败: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("  ❌ 无法连接到服务器")
        print("     请确保Django服务器正在运行:")
        print("     python manage.py runserver 8000")
        return False
    except Exception as e:
        print(f"  ❌ 健康检查异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 LingTaskFlow Token刷新API测试")
    print("=" * 50)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 检查服务器状态
    if not test_server_health():
        print("\n❌ 服务器不可访问，测试终止")
        return
    
    print()
    
    # 运行测试
    tests = [
        ("基本Token刷新功能", test_basic_token_refresh),
        ("无效Token处理", test_invalid_refresh_tokens),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
            
            time.sleep(0.5)  # 测试间隔
            
        except Exception as e:
            print(f"❌ {test_name} 执行异常: {str(e)}")
            results.append((test_name, False))
    
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
        return True
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
        print("\n失败的测试:")
        for test_name, success in results:
            if not success:
                print(f"  - {test_name}")
        return False

if __name__ == "__main__":
    # 直接运行测试，无需手动输入
    success = main()
    
    # 根据测试结果设置退出码
    exit(0 if success else 1)

#!/usr/bin/env python
"""
简化的登录API测试脚本
只测试基本的登录功能
"""

import requests
import json
from datetime import datetime

# API配置
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login/"

def test_login_api():
    """测试登录API基本功能"""
    print("🚀 LingTaskFlow 登录API基本功能测试")
    print("=" * 50)
    
    # 测试数据
    test_cases = [
        {
            "name": "测试正确的登录凭据",
            "data": {"username": "testadmin", "password": "TestPassword123!"},
            "expect_success": True
        },
        {
            "name": "测试记住我功能",
            "data": {"username": "testadmin", "password": "TestPassword123!", "remember_me": True},
            "expect_success": True
        },
        {
            "name": "测试错误密码",
            "data": {"username": "testadmin", "password": "wrongpassword"},
            "expect_success": False
        },
        {
            "name": "测试不存在的用户",
            "data": {"username": "nonexistent", "password": "somepassword"},
            "expect_success": False
        },
        {
            "name": "测试空字段",
            "data": {"username": "", "password": ""},
            "expect_success": False
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}] {test_case['name']}")
        
        try:
            response = requests.post(LOGIN_URL, json=test_case['data'], timeout=10)
            
            # 基本状态检查
            if test_case['expect_success']:
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print(f"✅ 测试通过 - 状态码: {response.status_code}")
                        print(f"   消息: {data.get('message', '无消息')}")
                        
                        # 检查返回的数据结构
                        if 'data' in data and 'tokens' in data['data']:
                            print("   ✅ 包含tokens")
                        if 'data' in data and 'user' in data['data']:
                            print("   ✅ 包含用户信息")
                        if 'security_info' in data:
                            print("   ✅ 包含安全信息")
                            
                        results.append(True)
                    else:
                        print(f"❌ 测试失败 - 响应success为false")
                        print(f"   响应: {data}")
                        results.append(False)
                else:
                    print(f"❌ 测试失败 - 状态码: {response.status_code}")
                    print(f"   响应: {response.text}")
                    results.append(False)
            else:
                if response.status_code in [400, 401, 429]:
                    data = response.json()
                    if not data.get('success', True):
                        print(f"✅ 测试通过 - 正确拒绝 (状态码: {response.status_code})")
                        print(f"   错误消息: {data.get('message', '无消息')}")
                        results.append(True)
                    else:
                        print(f"❌ 测试失败 - 应该拒绝但返回success=true")
                        results.append(False)
                else:
                    print(f"❌ 测试失败 - 意外的状态码: {response.status_code}")
                    results.append(False)
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络错误: {str(e)}")
            results.append(False)
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            results.append(False)
    
    # 显示总结
    print("\n" + "=" * 50)
    print("📊 测试总结")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results)
    
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {total_tests - passed_tests}")
    print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 所有测试都通过了！登录API功能正常！")
    else:
        print(f"\n⚠️  有 {total_tests - passed_tests} 个测试失败")

if __name__ == "__main__":
    test_login_api()

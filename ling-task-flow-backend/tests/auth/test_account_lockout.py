#!/usr/bin/env python
"""
测试账户锁定功能
"""

import requests
import time
from datetime import datetime

# API配置
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login/"

def test_account_lockout():
    """测试账户锁定功能"""
    print("🔒 测试账户锁定功能")
    print("=" * 50)
    
    # 使用错误密码进行5次登录尝试
    wrong_credentials = {
        "username": "testadmin",
        "password": "wrongpassword123"
    }
    
    print("进行5次错误密码登录尝试...")
    
    for i in range(5):
        print(f"  尝试 {i+1}/5...")
        try:
            response = requests.post(LOGIN_URL, json=wrong_credentials, timeout=10)
            data = response.json()
            
            if response.status_code == 400:
                message = data.get('errors', {}).get('non_field_errors', '')
                if '次尝试机会' in str(message):
                    remaining = str(message).split('还有')[1].split('次')[0] if '还有' in str(message) else '未知'
                    print(f"    失败 - 剩余尝试次数: {remaining}")
                else:
                    print(f"    失败 - {data.get('message', '未知错误')}")
            else:
                print(f"    意外响应 - 状态码: {response.status_code}")
                
            time.sleep(0.5)  # 避免过快请求
            
        except Exception as e:
            print(f"    错误: {str(e)}")
            break
    
    print("\n测试账户是否被锁定...")
    time.sleep(1)
    
    # 现在尝试使用正确密码登录
    correct_credentials = {
        "username": "testadmin",
        "password": "TestPassword123!"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=correct_credentials, timeout=10)
        data = response.json()
        
        if response.status_code == 429:
            print("✅ 账户锁定功能正常工作!")
            print(f"   状态码: {response.status_code}")
            print(f"   消息: {data.get('message', '未知')}")
            return True
        elif response.status_code == 200:
            print("⚠️  账户没有被锁定，可能锁定功能有问题")
            print(f"   状态码: {response.status_code}")
            print(f"   消息: {data.get('message', '登录成功')}")
            return False
        else:
            print(f"❌ 意外的响应状态码: {response.status_code}")
            print(f"   响应: {data}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

def test_lockout_expiry():
    """测试锁定过期功能"""
    print("\n⏰ 测试锁定过期功能")
    print("=" * 50)
    print("等待30秒测试锁定过期...")
    print("(注意：实际生产环境锁定时间为30分钟)")
    
    # 在测试环境中，我们不会真的等30分钟
    # 这里只是演示锁定过期的概念
    for i in range(30, 0, -1):
        print(f"\r等待中... {i}秒", end="", flush=True)
        time.sleep(1)
    
    print("\n\n尝试登录测试锁定是否过期...")
    
    correct_credentials = {
        "username": "testadmin",
        "password": "TestPassword123!"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=correct_credentials, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            print("✅ 锁定已过期，可以正常登录")
            print(f"   消息: {data.get('message', '登录成功')}")
            return True
        elif response.status_code == 429:
            print("⚠️  账户仍被锁定")
            print(f"   消息: {data.get('message', '账户锁定')}")
            return False
        else:
            print(f"❌ 意外的响应状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

if __name__ == "__main__":
    print("📝 账户锁定功能测试")
    print("⚠️  注意：此测试会暂时锁定testadmin账户")
    input("按Enter键开始测试...")
    
    # 测试账户锁定
    lockout_success = test_account_lockout()
    
    if lockout_success:
        # 测试锁定过期
        expiry_success = test_lockout_expiry()
        
        if expiry_success:
            print("\n🎉 账户锁定功能完全正常！")
        else:
            print("\n⚠️  锁定过期功能可能需要调整")
    else:
        print("\n❌ 账户锁定功能可能有问题")
    
    print("\n测试完成。")

#!/usr/bin/env python3
"""
测试脚本：验证 API 修复是否生效
检查任务列表 API 是否在分页响应中包含 description 字段
"""

import requests
import json

# API 端点
BASE_URL = "http://127.0.0.1:8000"
TASKS_API = f"{BASE_URL}/api/tasks/"
LOGIN_API = f"{BASE_URL}/api/auth/login/"

def get_auth_token():
    """获取认证token"""
    print("🔐 正在获取认证token...")
    
    # 使用测试用户登录
    login_data = {
        "username": "admin",  # 假设有admin用户
        "password": "admin123"  # 假设密码
    }
    
    try:
        response = requests.post(LOGIN_API, json=login_data)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'access_token' in data['data']:
                token = data['data']['access_token']
                print("✅ 认证成功")
                return token
            else:
                print("❌ 登录响应格式不正确")
                return None
        else:
            print(f"❌ 登录失败 (状态码: {response.status_code})")
            return None
    except Exception as e:
        print(f"❌ 登录过程中发生错误: {e}")
        return None

def test_task_list_api():
    """测试任务列表 API 是否包含 description 字段"""
    print("🔍 测试任务列表 API...")
    
    # 首先获取认证token
    token = get_auth_token()
    if not token:
        print("❌ 无法获取认证token，跳过测试")
        return False
    
    # 设置认证头
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # 发送请求到任务列表 API
        response = requests.get(f"{TASKS_API}?page=1&page_size=20", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API 请求成功 (状态码: {response.status_code})")
            
            # 检查是否有任务数据
            if 'results' in data and len(data['results']) > 0:
                task = data['results'][0]
                
                # 检查任务对象中是否包含 description 字段
                if 'description' in task:
                    print(f"✅ description 字段存在: {task['description'][:50]}..." if len(task['description']) > 50 else f"✅ description 字段存在: {task['description']}")
                    
                    # 显示任务的所有字段
                    print(f"📋 任务字段: {list(task.keys())}")
                    
                    return True
                else:
                    print("❌ description 字段缺失")
                    print(f"📋 实际字段: {list(task.keys())}")
                    return False
            else:
                print("⚠️  没有找到任务数据")
                return None
        else:
            print(f"❌ API 请求失败 (状态码: {response.status_code})")
            print(f"响应: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保后端服务正在运行")
        return False
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return False

def test_task_creation_api():
    """测试任务创建 API 以便比较"""
    print("\n🔍 测试任务创建 API (仅查看响应格式)...")
    
    # 这里我们不实际创建任务，只是为了比较响应格式
    # 因为创建需要认证，我们只检查现有的任务
    pass

if __name__ == "__main__":
    print("🚀 开始测试 LingTaskFlow API 修复...")
    print("=" * 50)
    
    result = test_task_list_api()
    
    print("\n" + "=" * 50)
    if result is True:
        print("🎉 测试通过！API 修复成功，description 字段已包含在分页响应中")
    elif result is False:
        print("😞 测试失败！description 字段仍然缺失")
    else:
        print("⚠️  无法进行测试，可能没有任务数据")
        
    print("\n💡 提示：可以在 http://127.0.0.1:8000/api/docs/ 查看完整的 API 文档")

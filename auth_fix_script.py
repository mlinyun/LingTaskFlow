#!/usr/bin/env python
"""
快速认证解决脚本
创建测试用户并获取认证Token，解决认证阻塞问题
"""
import requests
import json

# API配置
API_BASE_URL = "http://localhost:8000/api"
REGISTER_URL = f"{API_BASE_URL}/auth/register/"
LOGIN_URL = f"{API_BASE_URL}/auth/login/"

# 测试用户数据
TEST_USER = {
    "username": "testuser",
    "email": "test@lingtaskflow.com",
    "password": "TestPassword123!",
    "password_confirm": "TestPassword123!"
}

def create_test_user():
    """创建测试用户"""
    print("🔐 正在创建测试用户...")
    
    try:
        # 尝试注册
        response = requests.post(REGISTER_URL, json=TEST_USER)
        
        if response.status_code == 201:
            data = response.json()
            print("✅ 测试用户创建成功！")
            print(f"   用户名: {TEST_USER['username']}")
            print(f"   邮箱: {TEST_USER['email']}")
            
            # 返回token
            if 'data' in data and 'tokens' in data['data']:
                access_token = data['data']['tokens']['access']
                refresh_token = data['data']['tokens']['refresh']
                print(f"✅ JWT Token已获取")
                return access_token, refresh_token
            
        elif response.status_code == 400:
            print("ℹ️  用户可能已存在，尝试登录...")
            return login_existing_user()
            
        else:
            print(f"❌ 注册失败: {response.text}")
            return None, None
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务器，请确保Django服务器在运行")
        print("   运行命令: cd ling-task-flow-backend && python manage.py runserver")
        return None, None
    except Exception as e:
        print(f"❌ 注册过程中出现错误: {e}")
        return None, None

def login_existing_user():
    """登录已存在的用户"""
    print("🔑 正在登录已存在的用户...")
    
    try:
        login_data = {
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
        
        response = requests.post(LOGIN_URL, json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 登录成功！")
            
            if 'data' in data and 'tokens' in data['data']:
                access_token = data['data']['tokens']['access']
                refresh_token = data['data']['tokens']['refresh']
                print(f"✅ JWT Token已获取")
                return access_token, refresh_token
        else:
            print(f"❌ 登录失败: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ 登录过程中出现错误: {e}")
        return None, None

def main():
    """主函数"""
    print("🚀 LingTaskFlow 认证问题解决脚本")
    print("=" * 50)
    
    # 创建/登录用户
    access_token, refresh_token = create_test_user()
    
    if access_token and refresh_token:
        print("\n✅ 认证Token获取成功！")
        print("=" * 50)
        print("📋 请按以下步骤在浏览器中设置Token：")
        print()
        print("1. 打开浏览器访问: http://localhost:9000")
        print("2. 按F12打开开发者工具")
        print("3. 切换到Console(控制台)标签")
        print("4. 复制粘贴以下代码并按回车：")
        print()
        print("// 设置认证Token")
        print(f'localStorage.setItem("access_token", "{access_token}");')
        print(f'localStorage.setItem("refresh_token", "{refresh_token}");')
        print('localStorage.setItem("user_info", JSON.stringify({')
        print(f'  "username": "{TEST_USER["username"]}",')
        print(f'  "email": "{TEST_USER["email"]}",')
        print('  "profile": {"timezone": "Asia/Shanghai", "theme_preference": "auto"}')
        print('}));')
        print('console.log("✅ Token设置完成！请刷新页面。");')
        print()
        print("5. 刷新页面 (F5)")
        print("6. 现在应该可以正常访问任务管理界面了")
        print()
        print("🎯 测试用户登录信息:")
        print(f"   用户名: {TEST_USER['username']}")
        print(f"   密码: {TEST_USER['password']}")
        
    else:
        print("\n❌ Token获取失败")
        print("请检查后端服务器是否正常运行")

if __name__ == "__main__":
    main()

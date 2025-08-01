#!/usr/bin/env python
"""
任务创建API增强功能测试脚本
测试2.1.2任务的API功能
"""
import requests
import json
import time
from datetime import datetime, timedelta

# API基础URL
BASE_URL = 'http://localhost:8000/api'
TASKS_URL = f'{BASE_URL}/tasks/'
AUTH_URL = f'{BASE_URL}/auth/'

def get_auth_token():
    """获取认证token"""
    login_data = {
        'username': 'testuser_api',
        'password': 'TestPass123!'
    }
    
    try:
        response = requests.post(f'{AUTH_URL}login/', json=login_data)
        if response.status_code == 200:
            return response.json()['data']['tokens']['access']
        else:
            print(f"登录失败: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("无法连接到服务器，请确保服务器正在运行")
        return None

def test_basic_task_creation(token):
    """测试基础任务创建"""
    print("\n📝 测试基础任务创建...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    task_data = {
        'title': '增强API测试任务',
        'description': '测试增强的创建任务API功能',
        'due_date': (datetime.now() + timedelta(days=5)).isoformat(),
        'priority': 'HIGH',
        'category': '开发'
    }
    
    try:
        response = requests.post(TASKS_URL, json=task_data, headers=headers)
        if response.status_code == 201:
            data = response.json()
            print("   ✅ 基础任务创建成功")
            print(f"      任务ID: {data['data']['id']}")
            print(f"      智能分类: {data['data']['category']}")
            print(f"      自动标签: {data['data']['tags']}")
            print(f"      预估工时: {data['data']['estimated_hours']}")
            
            # 显示用户统计
            if 'user_stats' in data:
                stats = data['user_stats']
                print(f"      用户统计: 总任务{stats['total_tasks']}, 待办{stats['pending_tasks']}")
            
            # 显示推荐信息
            if 'recommendations' in data:
                recs = data['recommendations']
                print(f"      推荐信息: {json.dumps(recs, ensure_ascii=False, indent=8)}")
            
            return data['data']['id']
        else:
            print(f"   ❌ 基础任务创建失败: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ 请求出错: {e}")
        return None

def test_smart_defaults(token):
    """测试智能默认值功能"""
    print("\n🧠 测试智能默认值...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # 测试紧急任务的智能优先级
    urgent_task = {
        'title': '紧急Bug修复',
        'due_date': (datetime.now() + timedelta(hours=12)).isoformat()
    }
    
    try:
        response = requests.post(TASKS_URL, json=urgent_task, headers=headers)
        if response.status_code == 201:
            data = response.json()['data']
            print(f"   ✅ 紧急任务智能优先级: {data['priority']}")
            print(f"      智能分类: {data['category']}")
            print(f"      自动标签: {data['tags']}")
        else:
            print(f"   ❌ 智能默认值测试失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 请求出错: {e}")

def test_quick_create(token):
    """测试快速创建功能"""
    print("\n⚡ 测试快速创建功能...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    quick_data = {
        'title': '快速创建的任务'
    }
    
    try:
        response = requests.post(f'{TASKS_URL}quick_create/', json=quick_data, headers=headers)
        if response.status_code == 201:
            data = response.json()['data']
            print("   ✅ 快速创建成功")
            print(f"      标题: {data['title']}")
            print(f"      状态: {data['status']}")
            print(f"      优先级: {data['priority']}")
            print(f"      智能分类: {data['category']}")
        else:
            print(f"   ❌ 快速创建失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 请求出错: {e}")

def test_batch_create(token):
    """测试批量创建功能"""
    print("\n📦 测试批量创建功能...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    batch_tasks = [
        {
            'title': '批量任务1 - 开发',
            'description': '第一个批量任务',
            'priority': 'HIGH'
        },
        {
            'title': '批量任务2 - 测试',
            'description': '第二个批量任务',
            'priority': 'MEDIUM'
        },
        {
            'title': '批量任务3 - 文档',
            'description': '第三个批量任务',
            'priority': 'LOW'
        }
    ]
    
    try:
        response = requests.post(TASKS_URL, json=batch_tasks, headers=headers)
        if response.status_code in [201, 207]:
            data = response.json()
            print("   ✅ 批量创建完成")
            print(f"      总计: {data['data']['summary']['total']}")
            print(f"      成功: {data['data']['summary']['created']}")
            print(f"      失败: {data['data']['summary']['failed']}")
            
            if data['data']['failed_tasks']:
                print("      失败详情:")
                for failed in data['data']['failed_tasks']:
                    print(f"        - {failed['data']}: {failed['error']}")
        else:
            print(f"   ❌ 批量创建失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 请求出错: {e}")

def test_create_options(token):
    """测试创建选项API"""
    print("\n⚙️ 测试创建选项API...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(f'{TASKS_URL}create_options/', headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            print("   ✅ 创建选项获取成功")
            print(f"      状态选项: {len(data['status_choices'])}个")
            print(f"      优先级选项: {len(data['priority_choices'])}个")
            print(f"      常用分类: {len(data['user_categories'])}个")
            print(f"      可分配用户: {len(data['assignable_users'])}个")
            print(f"      热门标签: {len(data['popular_tags'])}个")
            
            if data['user_categories']:
                print("      用户常用分类:")
                for cat in data['user_categories'][:3]:
                    print(f"        - {cat['category']} (使用{cat['usage_count']}次)")
        else:
            print(f"   ❌ 创建选项获取失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 请求出错: {e}")

def test_data_validation(token):
    """测试数据验证API"""
    print("\n✅ 测试数据验证API...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # 测试有效数据
    valid_data = {
        'title': '数据验证测试任务',
        'description': '这是一个用于测试数据验证的任务',
        'due_date': (datetime.now() + timedelta(days=7)).isoformat(),
        'estimated_hours': 4.0
    }
    
    try:
        response = requests.post(f'{TASKS_URL}validate_task_data/', json=valid_data, headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            print("   ✅ 有效数据验证通过")
            print(f"      验证结果: {'通过' if data['valid'] else '失败'}")
            if data.get('warnings'):
                print(f"      警告: {data['warnings']}")
            if data.get('suggestions'):
                print(f"      建议: {data['suggestions']}")
        else:
            print(f"   ❌ 数据验证失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 请求出错: {e}")
    
    # 测试无效数据
    invalid_data = {
        'title': '',  # 空标题
        'estimated_hours': 100  # 过长工时
    }
    
    try:
        response = requests.post(f'{TASKS_URL}validate_task_data/', json=invalid_data, headers=headers)
        print(f"   ✅ 无效数据验证: 状态码 {response.status_code}")
        if response.status_code == 400:
            data = response.json()['data']
            print(f"      验证结果: {'通过' if data['valid'] else '失败'}")
            if data.get('errors'):
                print(f"      错误: {data['errors']}")
    except Exception as e:
        print(f"   ❌ 请求出错: {e}")

def test_creation_templates(token):
    """测试创建模板API"""
    print("\n📋 测试创建模板API...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(f'{TASKS_URL}creation_templates/', headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            print("   ✅ 创建模板获取成功")
            print(f"      模板数量: {data['total_count']}")
            
            for template in data['templates']:
                print(f"      - {template['name']}: {template['description']}")
        else:
            print(f"   ❌ 创建模板获取失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 请求出错: {e}")

def main():
    """主测试函数"""
    print("🚀 LingTaskFlow 增强创建任务API测试")
    print("=" * 60)
    
    # 获取认证token
    token = get_auth_token()
    if not token:
        print("❌ 认证失败，无法继续测试")
        return
    
    # 运行各项测试
    task_id = test_basic_task_creation(token)
    time.sleep(0.5)
    
    test_smart_defaults(token)
    time.sleep(0.5)
    
    test_quick_create(token)
    time.sleep(0.5)
    
    test_batch_create(token)
    time.sleep(0.5)
    
    test_create_options(token)
    time.sleep(0.5)
    
    test_data_validation(token)
    time.sleep(0.5)
    
    test_creation_templates(token)
    
    print("\n" + "=" * 60)
    print("✅ 增强创建任务API测试完成！")
    print(f"📊 测试摘要:")
    print(f"   - 基础创建: ✅ 已测试")
    print(f"   - 智能默认值: ✅ 已测试")
    print(f"   - 快速创建: ✅ 已测试")
    print(f"   - 批量创建: ✅ 已测试")
    print(f"   - 创建选项: ✅ 已测试")
    print(f"   - 数据验证: ✅ 已测试")
    print(f"   - 创建模板: ✅ 已测试")

if __name__ == '__main__':
    main()

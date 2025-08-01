#!/usr/bin/env python
"""
任务列表API测试脚本
测试2.1.1任务的API功能
"""
import requests
import json
import time
from datetime import datetime, timedelta

# API基础URL
BASE_URL = 'http://localhost:8000/api'
TASKS_URL = f'{BASE_URL}/tasks/'
AUTH_URL = f'{BASE_URL}/auth/'

def test_user_registration_and_login():
    """测试用户注册和登录，获取认证token"""
    print("🔐 测试用户认证...")
    
    # 注册测试用户
    register_data = {
        'username': 'testuser_api',
        'email': 'testapi@example.com',
        'password': 'TestPass123!',
        'password_confirm': 'TestPass123!'
    }
    
    try:
        register_response = requests.post(f'{AUTH_URL}register/', json=register_data)
        if register_response.status_code == 201:
            print("   ✅ 用户注册成功")
            return register_response.json()['data']['tokens']['access']
        elif register_response.status_code == 400:
            # 用户可能已存在，尝试登录
            print("   ℹ️  用户已存在，尝试登录...")
    except requests.exceptions.ConnectionError:
        print("   ❌ 无法连接到服务器，请确保服务器正在运行")
        return None
    
    # 登录
    login_data = {
        'username': 'testuser_api',
        'password': 'TestPass123!'
    }
    
    try:
        login_response = requests.post(f'{AUTH_URL}login/', json=login_data)
        if login_response.status_code == 200:
            print("   ✅ 用户登录成功")
            return login_response.json()['data']['tokens']['access']
        else:
            print(f"   ❌ 登录失败: {login_response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("   ❌ 无法连接到服务器")
        return None

def test_task_creation(token):
    """测试任务创建"""
    print("\n📝 测试任务创建...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # 创建测试任务
    test_tasks = [
        {
            'title': 'API测试任务1',
            'description': '这是第一个API测试任务',
            'status': 'PENDING',
            'priority': 'HIGH',
            'category': '开发',
            'due_date': (datetime.now() + timedelta(days=7)).isoformat(),
            'estimated_hours': 5.0,
            'tags': 'API, 测试, 开发'
        },
        {
            'title': 'API测试任务2',
            'description': '这是第二个API测试任务',
            'status': 'IN_PROGRESS',
            'priority': 'MEDIUM',
            'category': '测试',
            'due_date': (datetime.now() + timedelta(days=3)).isoformat(),
            'progress': 30,
            'estimated_hours': 8.0,
            'tags': '测试, 进行中'
        },
        {
            'title': 'API测试任务3',
            'description': '这是第三个API测试任务，已逾期',
            'status': 'PENDING',
            'priority': 'URGENT',
            'category': '紧急',
            'due_date': (datetime.now() - timedelta(days=1)).isoformat(),
            'estimated_hours': 2.0,
            'tags': '紧急, 逾期'
        }
    ]
    
    created_tasks = []
    for i, task_data in enumerate(test_tasks, 1):
        try:
            response = requests.post(TASKS_URL, json=task_data, headers=headers)
            if response.status_code == 201:
                task = response.json()['data']
                created_tasks.append(task)
                print(f"   ✅ 任务{i}创建成功: {task['title']}")
            else:
                print(f"   ❌ 任务{i}创建失败: {response.text}")
        except Exception as e:
            print(f"   ❌ 任务{i}创建出错: {e}")
    
    return created_tasks

def test_task_list_api(token):
    """测试任务列表API"""
    print("\n📋 测试任务列表API...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # 测试基础列表查询
    print("   🔍 测试基础任务列表查询...")
    try:
        response = requests.get(TASKS_URL, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 获取任务列表成功，共 {data.get('count', 0)} 个任务")
            
            # 显示统计信息
            if 'stats' in data:
                stats = data['stats']
                print(f"      📊 统计信息:")
                print(f"         总数: {stats.get('total', 0)}")
                print(f"         状态分布: {stats.get('by_status', {})}")
                print(f"         优先级分布: {stats.get('by_priority', {})}")
                print(f"         逾期任务: {stats.get('overdue_count', 0)}")
                print(f"         已完成: {stats.get('completed_count', 0)}")
        else:
            print(f"   ❌ 获取任务列表失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 请求出错: {e}")

def test_task_filtering(token):
    """测试任务过滤功能"""
    print("\n🔍 测试任务过滤功能...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # 测试不同的过滤条件
    filter_tests = [
        {'params': {'status': 'PENDING'}, 'name': '状态过滤 (PENDING)'},
        {'params': {'priority': 'HIGH'}, 'name': '优先级过滤 (HIGH)'},
        {'params': {'search': 'API'}, 'name': '搜索过滤 (API)'},
        {'params': {'is_overdue': 'true'}, 'name': '逾期任务过滤'},
        {'params': {'category': '开发'}, 'name': '分类过滤 (开发)'},
        {'params': {'ordering': '-priority'}, 'name': '优先级排序'},
        {'params': {'ordering': 'due_date'}, 'name': '到期时间排序'},
    ]
    
    for test in filter_tests:
        try:
            response = requests.get(TASKS_URL, params=test['params'], headers=headers)
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                print(f"   ✅ {test['name']}: {count} 个结果")
            else:
                print(f"   ❌ {test['name']} 失败: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {test['name']} 出错: {e}")

def test_task_pagination(token):
    """测试分页功能"""
    print("\n📄 测试分页功能...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        # 测试第一页
        response = requests.get(TASKS_URL, params={'page_size': 2, 'page': 1}, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 分页测试成功")
            print(f"      当前页结果数: {len(data.get('results', []))}")
            print(f"      总数: {data.get('count', 0)}")
            print(f"      下一页: {'有' if data.get('next') else '无'}")
            print(f"      上一页: {'有' if data.get('previous') else '无'}")
        else:
            print(f"   ❌ 分页测试失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 分页测试出错: {e}")

def test_task_stats_api(token):
    """测试任务统计API"""
    print("\n📊 测试任务统计API...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(f'{TASKS_URL}stats/', headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            print("   ✅ 统计API调用成功")
            print(f"      总任务数: {data.get('total_tasks', 0)}")
            print(f"      状态分布: {data.get('status_distribution', {})}")
            print(f"      优先级分布: {data.get('priority_distribution', {})}")
            print(f"      进度摘要: {data.get('progress_summary', {})}")
            print(f"      时间摘要: {data.get('time_summary', {})}")
        else:
            print(f"   ❌ 统计API失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 统计API出错: {e}")

def test_task_detail_api(token, task_id):
    """测试任务详情API"""
    print(f"\n🔍 测试任务详情API (ID: {task_id})...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(f'{TASKS_URL}{task_id}/', headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            print("   ✅ 任务详情获取成功")
            print(f"      标题: {data.get('title', '')}")
            print(f"      状态: {data.get('status', '')}")
            print(f"      优先级: {data.get('priority', '')}")
            print(f"      创建时间: {data.get('created_at', '')}")
            print(f"      到期时间: {data.get('due_date', '')}")
        else:
            print(f"   ❌ 任务详情获取失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 任务详情获取出错: {e}")

def main():
    """主测试函数"""
    print("🚀 LingTaskFlow 任务列表API测试")
    print("=" * 60)
    
    # 1. 用户认证
    token = test_user_registration_and_login()
    if not token:
        print("❌ 认证失败，无法继续测试")
        return
    
    # 2. 创建测试任务
    created_tasks = test_task_creation(token)
    
    # 等待一秒确保任务创建完成
    time.sleep(1)
    
    # 3. 测试任务列表API
    test_task_list_api(token)
    
    # 4. 测试过滤功能
    test_task_filtering(token)
    
    # 5. 测试分页功能
    test_task_pagination(token)
    
    # 6. 测试统计API
    test_task_stats_api(token)
    
    # 7. 测试任务详情API
    if created_tasks:
        test_task_detail_api(token, created_tasks[0]['id'])
    
    print("\n" + "=" * 60)
    print("✅ API测试完成！")
    print(f"📊 测试摘要:")
    print(f"   - 认证系统: {'✅ 正常' if token else '❌ 失败'}")
    print(f"   - 任务创建: {'✅ 正常' if created_tasks else '❌ 失败'}")
    print(f"   - 任务列表: ✅ 已测试")
    print(f"   - 过滤功能: ✅ 已测试")
    print(f"   - 分页功能: ✅ 已测试")
    print(f"   - 统计功能: ✅ 已测试")
    print(f"   - 任务详情: ✅ 已测试")

if __name__ == '__main__':
    main()

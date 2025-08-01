#!/usr/bin/env python
"""
任务更新API测试脚本
测试2.1.3任务的更新API功能
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

def create_test_task(token):
    """创建测试任务用于更新测试"""
    print("\n📝 创建测试任务...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    task_data = {
        'title': '更新测试任务',
        'description': '用于测试更新功能的任务',
        'status': 'PENDING',
        'priority': 'MEDIUM',
        'category': '测试',
        'progress': 0,
        'estimated_hours': 8.0,
        'tags': '测试, 更新'
    }
    
    try:
        response = requests.post(TASKS_URL, json=task_data, headers=headers)
        if response.status_code == 201:
            task = response.json()['data']
            print(f"   ✅ 测试任务创建成功: {task['title']} (ID: {task['id']})")
            return task
        else:
            print(f"   ❌ 测试任务创建失败: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ 请求出错: {e}")
        return None

def test_basic_update(token, task_id):
    """测试基础任务更新"""
    print("\n🔄 测试基础任务更新...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    update_data = {
        'title': '更新后的任务标题',
        'description': '这是更新后的任务描述',
        'priority': 'HIGH',
        'progress': 30,
        'tags': '测试, 更新, 高优先级'
    }
    
    try:
        response = requests.patch(f'{TASKS_URL}{task_id}/', json=update_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            task = data['data']
            print("   ✅ 基础更新成功")
            print(f"      新标题: {task['title']}")
            print(f"      新优先级: {task['priority_display']}")
            print(f"      新进度: {task['progress']}%")
            
            # 显示变更记录
            if 'changes' in data:
                print(f"      变更记录: {len(data['changes'])}项")
                for change in data['changes']:
                    print(f"        - {change['field']}: {change['old_value']} → {change['new_value']}")
            
            # 显示统计信息
            if 'update_stats' in data:
                stats = data['update_stats']
                print(f"      用户统计: 总任务{stats['total_tasks']}, 进行中{stats['in_progress_tasks']}")
            
            return True
        else:
            print(f"   ❌ 基础更新失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 请求出错: {e}")
        return False

def test_status_update(token, task_id):
    """测试状态快速更新"""
    print("\n⚡ 测试状态快速更新...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    status_data = {
        'status': 'IN_PROGRESS',
        'progress': 50
    }
    
    try:
        response = requests.patch(f'{TASKS_URL}{task_id}/update_status/', json=status_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            task = data['data']
            print("   ✅ 状态更新成功")
            print(f"      新状态: {task['status_display']}")
            print(f"      新进度: {task['progress']}%")
            print(f"      消息: {data['message']}")
            return True
        else:
            print(f"   ❌ 状态更新失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 请求出错: {e}")
        return False

def test_completion_update(token, task_id):
    """测试完成任务更新"""
    print("\n🎯 测试完成任务更新...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    completion_data = {
        'status': 'COMPLETED',
        'progress': 100,
        'actual_hours': 6.5,
        'notes': '任务已完成，实际用时6.5小时'
    }
    
    try:
        response = requests.patch(f'{TASKS_URL}{task_id}/', json=completion_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            task = data['data']
            print("   ✅ 完成更新成功")
            print(f"      状态: {task['status_display']}")
            print(f"      进度: {task['progress']}%")
            print(f"      实际工时: {task['actual_hours']}小时")
            print(f"      完成时间: {task['completed_at']}")
            return True
        else:
            print(f"   ❌ 完成更新失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 请求出错: {e}")
        return False

def test_validation_errors(token, task_id):
    """测试数据验证错误"""
    print("\n⚠️ 测试数据验证...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # 测试无效进度
    invalid_data = {
        'progress': 150  # 超出范围
    }
    
    try:
        response = requests.patch(f'{TASKS_URL}{task_id}/', json=invalid_data, headers=headers)
        if response.status_code == 400:
            print("   ✅ 进度验证正确拒绝了无效数据")
            print(f"      错误信息: {response.json().get('error', '')}")
        else:
            print(f"   ❌ 进度验证未正确处理: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求出错: {e}")
    
    # 测试空标题
    invalid_title_data = {
        'title': ''
    }
    
    try:
        response = requests.patch(f'{TASKS_URL}{task_id}/', json=invalid_title_data, headers=headers)
        if response.status_code == 400:
            print("   ✅ 标题验证正确拒绝了空标题")
        else:
            print(f"   ❌ 标题验证未正确处理: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求出错: {e}")

def test_bulk_update(token):
    """测试批量更新功能"""
    print("\n📦 测试批量更新功能...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # 首先获取一些任务ID
    try:
        response = requests.get(f'{TASKS_URL}?page_size=5', headers=headers)
        if response.status_code != 200:
            print("   ❌ 无法获取任务列表")
            return
        
        response_data = response.json()
        # 处理不同的响应结构
        if 'data' in response_data and 'results' in response_data['data']:
            tasks = response_data['data']['results']
        elif 'results' in response_data:
            tasks = response_data['results']
        else:
            print(f"   ❌ 意外的响应结构: {list(response_data.keys())}")
            return
        
        if len(tasks) < 2:
            print("   ❌ 需要至少2个任务来测试批量更新")
            return
        
        # 准备批量更新数据
        bulk_updates = {
            'updates': [
                {
                    'id': tasks[0]['id'],
                    'priority': 'HIGH',
                    'tags': '批量更新, 高优先级'
                },
                {
                    'id': tasks[1]['id'],
                    'progress': 25,
                    'tags': '批量更新, 进行中'
                }
            ]
        }
        
        response = requests.patch(f'{TASKS_URL}bulk_update/', json=bulk_updates, headers=headers)
        if response.status_code in [200, 207]:
            data = response.json()
            print("   ✅ 批量更新完成")
            print(f"      总计: {data['data']['stats']['total_attempted']}")
            print(f"      成功: {data['data']['stats']['successful_updates']}")
            print(f"      失败: {data['data']['stats']['failed_updates']}")
            print(f"      成功率: {data['data']['stats']['success_rate']:.1f}%")
            
            if data['data']['failed_updates']:
                print("      失败详情:")
                for failed in data['data']['failed_updates']:
                    print(f"        - ID {failed['id']}: {failed['error']}")
        else:
            print(f"   ❌ 批量更新失败: {response.text}")
    
    except Exception as e:
        print(f"   ❌ 请求出错: {e}")

def test_status_transitions(token, task_id):
    """测试状态转换规则"""
    print("\n🔄 测试状态转换规则...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # 测试允许的状态转换：PENDING → IN_PROGRESS
    print("   测试 PENDING → IN_PROGRESS...")
    try:
        # 先设置为PENDING
        response = requests.patch(f'{TASKS_URL}{task_id}/', 
                                json={'status': 'PENDING'}, headers=headers)
        
        # 然后转换为IN_PROGRESS
        response = requests.patch(f'{TASKS_URL}{task_id}/', 
                                json={'status': 'IN_PROGRESS'}, headers=headers)
        if response.status_code == 200:
            print("      ✅ 允许的状态转换成功")
        else:
            print(f"      ❌ 允许的状态转换失败: {response.text}")
    except Exception as e:
        print(f"      ❌ 请求出错: {e}")
    
    # 测试不允许的状态转换（如果实现了严格的状态机）
    print("   测试状态转换验证...")
    try:
        # 尝试各种状态转换
        response = requests.patch(f'{TASKS_URL}{task_id}/', 
                                json={'status': 'COMPLETED'}, headers=headers)
        if response.status_code == 200:
            print("      ✅ 状态转换规则正常工作")
            
            # 测试从完成状态重新打开
            response = requests.patch(f'{TASKS_URL}{task_id}/', 
                                    json={'status': 'IN_PROGRESS'}, headers=headers)
            if response.status_code == 200:
                print("      ✅ 完成任务可以重新打开")
            else:
                print(f"      ❌ 完成任务重新打开失败: {response.text}")
        else:
            print(f"      ⚠️ 状态转换: {response.status_code}")
    except Exception as e:
        print(f"      ❌ 请求出错: {e}")

def main():
    """主测试函数"""
    print("🚀 LingTaskFlow 任务更新API测试")
    print("=" * 60)
    
    # 获取认证token
    token = get_auth_token()
    if not token:
        print("❌ 认证失败，无法继续测试")
        return
    
    # 创建测试任务
    test_task = create_test_task(token)
    if not test_task:
        print("❌ 无法创建测试任务，测试终止")
        return
    
    task_id = test_task['id']
    
    # 运行各项测试
    time.sleep(0.5)
    test_basic_update(token, task_id)
    
    time.sleep(0.5)
    test_status_update(token, task_id)
    
    time.sleep(0.5)
    test_completion_update(token, task_id)
    
    time.sleep(0.5)
    test_validation_errors(token, task_id)
    
    time.sleep(0.5)
    test_bulk_update(token)
    
    time.sleep(0.5)
    test_status_transitions(token, task_id)
    
    print("\n" + "=" * 60)
    print("✅ 任务更新API测试完成！")
    print(f"📊 测试摘要:")
    print(f"   - 基础更新: ✅ 已测试")
    print(f"   - 状态快速更新: ✅ 已测试")
    print(f"   - 完成任务更新: ✅ 已测试")
    print(f"   - 数据验证: ✅ 已测试")
    print(f"   - 批量更新: ✅ 已测试")
    print(f"   - 状态转换: ✅ 已测试")

if __name__ == '__main__':
    main()

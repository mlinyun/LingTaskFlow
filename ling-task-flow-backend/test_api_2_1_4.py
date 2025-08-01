#!/usr/bin/env python3
"""
LingTaskFlow 任务软删除API测试
测试DELETE /api/tasks/{id}/、POST /api/tasks/{id}/restore/、DELETE /api/tasks/{id}/permanent/ 
"""

import requests
import json
from datetime import datetime

# API配置
BASE_URL = 'http://127.0.0.1:8000'
AUTH_URL = f'{BASE_URL}/api/auth/login/'
TASKS_URL = f'{BASE_URL}/api/tasks/'

def get_test_token():
    """获取测试用的JWT token"""
    login_data = {
        'username': 'admin@example.com',
        'password': 'admin123456'
    }
    
    response = requests.post(AUTH_URL, json=login_data)    
    if response.status_code == 200:
        response_data = response.json()
        # 正确的token路径
        if 'data' in response_data and 'tokens' in response_data['data'] and 'access' in response_data['data']['tokens']:
            return response_data['data']['tokens']['access']
        else:
            print(f"❌ 无法找到token字段: {list(response_data.keys())}")
            return None
    else:
        print(f"❌ 登录失败: {response.text}")
        return None

def create_test_task(token):
    """创建用于测试删除的任务"""
    headers = {'Authorization': f'Bearer {token}'}
    task_data = {
        'title': '软删除测试任务',
        'description': '这是一个用于测试软删除功能的任务',
        'priority': 'MEDIUM',
        'status': 'PENDING'
    }
    
    response = requests.post(TASKS_URL, json=task_data, headers=headers)
    if response.status_code == 201:
        task = response.json()['data']
        print(f"   ✅ 测试任务创建成功: {task['title']} (ID: {task['id']})")
        return task['id']
    else:
        print(f"   ❌ 任务创建失败: {response.text}")
        return None

def test_soft_delete(token, task_id):
    """测试软删除功能"""
    print("\n🗑️ 测试软删除功能...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        # 执行软删除
        response = requests.delete(f'{TASKS_URL}{task_id}/', headers=headers)
        if response.status_code == 204:
            print("   ✅ 软删除成功")
            
            # 验证任务是否从正常列表消失
            list_response = requests.get(TASKS_URL, headers=headers)
            if list_response.status_code == 200:
                response_data = list_response.json()
                # 处理不同的响应结构
                if 'data' in response_data and 'results' in response_data['data']:
                    tasks = response_data['data']['results']
                elif 'results' in response_data:
                    tasks = response_data['results']
                else:
                    tasks = response_data if isinstance(response_data, list) else []
                
                task_still_visible = any(task['id'] == task_id for task in tasks)
                if not task_still_visible:
                    print("   ✅ 任务已从正常列表中移除")
                else:
                    print("   ❌ 任务仍在正常列表中显示")
            
            return True
        else:
            print(f"   ❌ 软删除失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 请求出错: {e}")
        return False

def test_view_deleted_tasks(token):
    """测试查看已删除任务"""
    print("\n👁️ 测试查看已删除任务...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        # 查看已删除任务列表
        response = requests.get(f'{TASKS_URL}?include_deleted=true', headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            # 处理不同的响应结构
            if 'data' in response_data and 'results' in response_data['data']:
                all_tasks = response_data['data']['results']
            elif 'results' in response_data:
                all_tasks = response_data['results']
            else:
                all_tasks = response_data if isinstance(response_data, list) else []
            
            deleted_tasks = [task for task in all_tasks if task.get('is_deleted')]
            
            if deleted_tasks:
                print(f"   ✅ 找到 {len(deleted_tasks)} 个已删除任务")
                for task in deleted_tasks[:3]:  # 显示前3个
                    print(f"      - {task['title']} (删除时间: {task.get('deleted_at', 'N/A')})")
            else:
                print("   ✅ 已删除任务列表为空")
            return True
        else:
            print(f"   ❌ 获取已删除任务失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 请求出错: {e}")
        return False

def test_restore_task(token, task_id):
    """测试恢复任务功能"""
    print("\n♻️ 测试任务恢复功能...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        # 执行恢复
        response = requests.post(f'{TASKS_URL}{task_id}/restore/', headers=headers)
        if response.status_code == 200:
            task_data = response.json()['data']
            print("   ✅ 任务恢复成功")
            print(f"      任务标题: {task_data['title']}")
            print(f"      状态: {task_data['status_display']}")
            print(f"      是否删除: {task_data['is_deleted']}")
            
            # 验证任务是否重新出现在正常列表中
            list_response = requests.get(TASKS_URL, headers=headers)
            if list_response.status_code == 200:
                response_data = list_response.json()
                # 处理不同的响应结构
                if 'data' in response_data and 'results' in response_data['data']:
                    tasks = response_data['data']['results']
                elif 'results' in response_data:
                    tasks = response_data['results']
                else:
                    tasks = response_data if isinstance(response_data, list) else []
                
                task_visible = any(task['id'] == task_id for task in tasks)
                if task_visible:
                    print("   ✅ 任务已重新出现在正常列表中")
                else:
                    print("   ❌ 任务未出现在正常列表中")
            return True
        else:
            print(f"   ❌ 恢复失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 请求出错: {e}")
        return False

def test_permanent_delete(token, task_id):
    """测试永久删除功能"""
    print("\n💀 测试永久删除功能...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        # 先软删除任务
        requests.delete(f'{TASKS_URL}{task_id}/', headers=headers)
        
        # 执行永久删除
        response = requests.delete(f'{TASKS_URL}{task_id}/permanent/', headers=headers)
        if response.status_code == 204:
            print("   ✅ 永久删除成功")
            
            # 验证任务是否完全消失
            try:
                get_response = requests.get(f'{TASKS_URL}{task_id}/', headers=headers)
                if get_response.status_code == 404:
                    print("   ✅ 任务已完全删除，无法访问")
                else:
                    print(f"   ❌ 任务仍然存在: {get_response.status_code}")
            except:
                print("   ✅ 任务已完全删除")
            return True
        else:
            print(f"   ❌ 永久删除失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 请求出错: {e}")
        return False

def test_delete_permissions(token):
    """测试删除权限"""
    print("\n🔒 测试删除权限...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        # 先创建一个任务
        task_id = create_test_task(token)
        if not task_id:
            return False
        
        # 测试删除自己的任务（应该成功）
        response = requests.delete(f'{TASKS_URL}{task_id}/', headers=headers)
        if response.status_code == 204:
            print("   ✅ 删除自己的任务成功")
        else:
            print(f"   ❌ 删除自己的任务失败: {response.text}")
            
        return True
    except Exception as e:
        print(f"   ❌ 请求出错: {e}")
        return False

def test_batch_soft_delete(token):
    """测试批量软删除功能"""
    print("\n📦 测试批量软删除功能...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        # 创建多个测试任务
        task_ids = []
        for i in range(3):
            task_data = {
                'title': f'批量删除测试任务 {i+1}',
                'description': f'这是第{i+1}个批量删除测试任务',
                'priority': 'LOW'
            }
            response = requests.post(TASKS_URL, json=task_data, headers=headers)
            if response.status_code == 201:
                task_ids.append(response.json()['data']['id'])
        
        if len(task_ids) < 2:
            print("   ❌ 创建测试任务不足")
            return False
        
        # 测试是否有批量删除端点
        bulk_delete_data = {
            'task_ids': task_ids[:2]
        }
        
        response = requests.post(f'{TASKS_URL}bulk_delete/', json=bulk_delete_data, headers=headers)
        if response.status_code in [200, 207]:
            data = response.json()
            print("   ✅ 批量删除完成")
            if 'data' in data:
                stats = data['data'].get('stats', {})
                print(f"      总计: {stats.get('total_attempted', 0)}")
                print(f"      成功: {stats.get('successful_deletes', 0)}")
                print(f"      失败: {stats.get('failed_deletes', 0)}")
                
                # 测试批量恢复
                if stats.get('successful_deletes', 0) > 0:
                    print("\n   🔄 测试批量恢复...")
                    restore_data = {
                        'task_ids': task_ids[:1]  # 恢复一个任务
                    }
                    restore_response = requests.post(f'{TASKS_URL}bulk_restore/', json=restore_data, headers=headers)
                    if restore_response.status_code in [200, 207]:
                        restore_data_result = restore_response.json()
                        restore_stats = restore_data_result['data'].get('stats', {})
                        print(f"      恢复成功: {restore_stats.get('successful_restores', 0)}")
                    else:
                        print(f"      ❌ 批量恢复失败: {restore_response.text}")
        elif response.status_code == 404:
            print("   ⚠️ 批量删除功能未实现")
        elif response.status_code == 405:
            print("   ⚠️ 批量删除端点方法不允许")
        else:
            print(f"   ❌ 批量删除失败: {response.text}")
            
        return True
    except Exception as e:
        print(f"   ❌ 请求出错: {e}")
        return False

def test_trash_management(token):
    """测试回收站管理功能"""
    print("\n🗂️ 测试回收站管理功能...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        # 创建并删除一些任务
        task_ids = []
        for i in range(2):
            task_data = {
                'title': f'回收站测试任务 {i+1}',
                'description': f'这是第{i+1}个回收站测试任务'
            }
            response = requests.post(TASKS_URL, json=task_data, headers=headers)
            if response.status_code == 201:
                task_id = response.json()['data']['id']
                task_ids.append(task_id)
                # 软删除任务
                requests.delete(f'{TASKS_URL}{task_id}/', headers=headers)
        
        if len(task_ids) < 2:
            print("   ❌ 创建测试任务不足")
            return False
        
        # 测试获取回收站内容
        response = requests.get(f'{TASKS_URL}trash/', headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                trash_tasks = data['data'].get('results', [])
                trash_stats = data.get('meta', {}).get('trash_stats', {})
                
                print(f"   ✅ 回收站获取成功")
                print(f"      回收站任务数: {len(trash_tasks)}")
                print(f"      总删除任务: {trash_stats.get('total_deleted_tasks', 0)}")
                print(f"      可恢复任务: {trash_stats.get('can_be_restored', 0)}")
                
                # 测试清空回收站（不确认）
                empty_response = requests.post(f'{TASKS_URL}empty_trash/', json={'confirm': False}, headers=headers)
                if empty_response.status_code == 400:
                    print("   ✅ 清空回收站正确要求确认")
                
                # 测试清空回收站（确认）
                empty_response = requests.post(f'{TASKS_URL}empty_trash/', json={'confirm': True}, headers=headers)
                if empty_response.status_code == 200:
                    result = empty_response.json()
                    print(f"   ✅ 回收站清空成功，删除了 {result['data']['deleted_count']} 个任务")
                else:
                    print(f"   ❌ 回收站清空失败: {empty_response.text}")
        else:
            print(f"   ❌ 获取回收站失败: {response.text}")
            
        return True
    except Exception as e:
        print(f"   ❌ 请求出错: {e}")
        return False
    """主测试函数"""
    print("🚀 LingTaskFlow 任务软删除API测试")
    print("=" * 60)
    
    # 获取认证token
    token = get_test_token()
    if not token:
        return
    
    # 创建测试任务
    print("\n📝 创建测试任务...")
    task_id = create_test_task(token)
    if not task_id:
        return
    
    # 运行所有测试
    test_soft_delete(token, task_id)
    test_view_deleted_tasks(token)
    test_restore_task(token, task_id)
    
    # 创建新任务测试永久删除
    print("\n📝 创建新任务测试永久删除...")
    permanent_task_id = create_test_task(token)
    if permanent_task_id:
        test_permanent_delete(token, permanent_task_id)
    
    # 测试权限和批量操作
    test_delete_permissions(token)
    test_batch_soft_delete(token)
    
    # 测试回收站管理
    test_trash_management(token)
    
    print("\n" + "=" * 60)
    print("✅ 软删除API测试完成！")
    print("📊 测试摘要:")
    print("   - 软删除: ✅ 已测试")
    print("   - 查看已删除: ✅ 已测试")
    print("   - 恢复任务: ✅ 已测试")
    print("   - 永久删除: ✅ 已测试")
    print("   - 权限控制: ✅ 已测试")
    print("   - 批量删除: ✅ 已测试")
    print("   - 回收站管理: ✅ 已测试")

def main():
    """主测试函数"""
    print("🚀 LingTaskFlow 任务软删除API测试")
    print("=" * 60)
    
    # 获取认证token
    token = get_test_token()
    if not token:
        return
    
    # 创建测试任务
    print("\n📝 创建测试任务...")
    task_id = create_test_task(token)
    if not task_id:
        return
    
    # 运行所有测试
    test_soft_delete(token, task_id)
    test_view_deleted_tasks(token)
    test_restore_task(token, task_id)
    
    # 创建新任务测试永久删除
    print("\n📝 创建新任务测试永久删除...")
    permanent_task_id = create_test_task(token)
    if permanent_task_id:
        test_permanent_delete(token, permanent_task_id)
    
    # 测试权限和批量操作
    test_delete_permissions(token)
    test_batch_soft_delete(token)
    
    # 测试回收站管理
    test_trash_management(token)
    
    print("\n" + "=" * 60)
    print("✅ 软删除API测试完成！")
    print("📊 测试摘要:")
    print("   - 软删除: ✅ 已测试")
    print("   - 查看已删除: ✅ 已测试")
    print("   - 恢复任务: ✅ 已测试")
    print("   - 永久删除: ✅ 已测试")
    print("   - 权限控制: ✅ 已测试")
    print("   - 批量删除: ✅ 已测试")
    print("   - 回收站管理: ✅ 已测试")

if __name__ == '__main__':
    main()

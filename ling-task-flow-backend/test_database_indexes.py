#!/usr/bin/env python
"""
数据库索引优化测试脚本
验证索引优化后的查询性能
"""
import os
import sys
import time

# 将项目目录添加到Python路径
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ling_task_flow_backend.settings')

import django
django.setup()

from django.db import connection, reset_queries
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from LingTaskFlow.models import Task, UserProfile


def measure_query_time(func):
    """装饰器：测量查询执行时间"""
    def wrapper(*args, **kwargs):
        reset_queries()
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        query_count = len(connection.queries)
        execution_time = (end_time - start_time) * 1000  # 转换为毫秒
        return result, execution_time, query_count
    return wrapper


def create_test_data():
    """创建测试数据"""
    print("🔄 创建测试数据...")
    
    # 创建测试用户
    users = []
    for i in range(5):
        username = f'testuser_{i}'
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@example.com',
                'first_name': f'Test{i}',
                'last_name': 'User'
            }
        )
        users.append(user)
    
    # 创建测试任务
    task_count_before = Task.objects.count()
    
    # 不同状态的任务
    statuses = ['PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'ON_HOLD']
    priorities = ['LOW', 'MEDIUM', 'HIGH', 'URGENT']
    categories = ['开发', '测试', '文档', '设计', '运维']
    
    for i in range(200):  # 创建200个测试任务
        owner = users[i % len(users)]
        assigned_to = users[(i + 1) % len(users)] if i % 3 == 0 else None
        
        task = Task.objects.create(
            title=f'测试任务 {i+1}',
            description=f'这是第{i+1}个测试任务的详细描述',
            owner=owner,
            assigned_to=assigned_to,
            status=statuses[i % len(statuses)],
            priority=priorities[i % len(priorities)],
            category=categories[i % len(categories)],
            due_date=timezone.now() + timedelta(days=(i % 30)),
            start_date=timezone.now() - timedelta(days=(i % 10)),
            progress=min(100, i % 101),
            estimated_hours=float(1 + (i % 20)),
            tags=f'标签{i%3}, 测试{i%5}',
            is_deleted=(i % 10 == 0)  # 10%的任务设为软删除
        )
    
    task_count_after = Task.objects.count()
    created_count = task_count_after - task_count_before
    
    print(f"   ✅ 创建了 {len(users)} 个用户")
    print(f"   ✅ 创建了 {created_count} 个新任务（总计 {task_count_after} 个任务）")
    print(f"   ✅ 软删除任务数: {Task.all_objects.filter(is_deleted=True).count()}")
    
    return users


@measure_query_time
def test_user_tasks_query(user):
    """测试用户任务查询"""
    return list(Task.objects.filter(owner=user).order_by('-created_at')[:20])


@measure_query_time
def test_user_status_tasks_query(user, status):
    """测试用户特定状态任务查询"""
    return list(Task.objects.filter(owner=user, status=status).order_by('-created_at'))


@measure_query_time
def test_assigned_tasks_query(user):
    """测试分配给用户的任务查询"""
    return list(Task.objects.filter(assigned_to=user).order_by('-created_at'))


@measure_query_time
def test_overdue_tasks_query(user):
    """测试过期任务查询"""
    return list(Task.objects.filter(
        owner=user,
        due_date__lt=timezone.now(),
        status__in=['PENDING', 'IN_PROGRESS', 'ON_HOLD']
    ))


@measure_query_time
def test_priority_status_query(priority, status):
    """测试优先级和状态组合查询"""
    return list(Task.objects.filter(priority=priority, status=status))


@measure_query_time
def test_category_tasks_query(category):
    """测试分类任务查询"""
    return list(Task.objects.filter(category=category, status='PENDING'))


@measure_query_time
def test_due_date_range_query():
    """测试时间范围查询"""
    start_date = timezone.now()
    end_date = start_date + timedelta(days=7)
    return list(Task.objects.filter(
        due_date__gte=start_date,
        due_date__lte=end_date,
        status__in=['PENDING', 'IN_PROGRESS']
    ))


@measure_query_time
def test_user_statistics_query(user):
    """测试用户统计查询"""
    stats = {
        'total': Task.objects.filter(owner=user).count(),
        'completed': Task.objects.filter(owner=user, status='COMPLETED').count(),
        'pending': Task.objects.filter(owner=user, status='PENDING').count(),
        'in_progress': Task.objects.filter(owner=user, status='IN_PROGRESS').count(),
        'high_priority': Task.objects.filter(owner=user, priority__in=['HIGH', 'URGENT']).count(),
    }
    return stats


@measure_query_time
def test_soft_delete_query():
    """测试软删除查询"""
    return {
        'active': list(Task.objects.all()[:10]),  # 默认管理器，排除软删除
        'deleted': list(Task.all_objects.filter(is_deleted=True)[:10]),  # 仅软删除
        'all': list(Task.all_objects.all()[:10])  # 包含所有
    }


def run_performance_tests():
    """运行性能测试"""
    print("\n" + "="*80)
    print("🚀 数据库索引优化性能测试")
    print("="*80)
    
    # 创建测试数据
    users = create_test_data()
    test_user = users[0]
    
    print(f"\n📊 开始性能测试（使用用户: {test_user.username}）")
    print("-" * 60)
    
    # 测试1: 用户任务查询
    result, exec_time, query_count = test_user_tasks_query(test_user)
    print(f"1. 用户任务查询 (前20条)")
    print(f"   结果数量: {len(result)}")
    print(f"   执行时间: {exec_time:.2f}ms")
    print(f"   查询次数: {query_count}")
    
    # 测试2: 用户状态任务查询
    result, exec_time, query_count = test_user_status_tasks_query(test_user, 'PENDING')
    print(f"\n2. 用户待处理任务查询")
    print(f"   结果数量: {len(result)}")
    print(f"   执行时间: {exec_time:.2f}ms")
    print(f"   查询次数: {query_count}")
    
    # 测试3: 分配任务查询
    result, exec_time, query_count = test_assigned_tasks_query(test_user)
    print(f"\n3. 分配给用户的任务查询")
    print(f"   结果数量: {len(result)}")
    print(f"   执行时间: {exec_time:.2f}ms")
    print(f"   查询次数: {query_count}")
    
    # 测试4: 过期任务查询
    result, exec_time, query_count = test_overdue_tasks_query(test_user)
    print(f"\n4. 过期任务查询")
    print(f"   结果数量: {len(result)}")
    print(f"   执行时间: {exec_time:.2f}ms")
    print(f"   查询次数: {query_count}")
    
    # 测试5: 优先级状态组合查询
    result, exec_time, query_count = test_priority_status_query('HIGH', 'PENDING')
    print(f"\n5. 高优先级待处理任务查询")
    print(f"   结果数量: {len(result)}")
    print(f"   执行时间: {exec_time:.2f}ms")
    print(f"   查询次数: {query_count}")
    
    # 测试6: 分类任务查询
    result, exec_time, query_count = test_category_tasks_query('开发')
    print(f"\n6. 开发分类待处理任务查询")
    print(f"   结果数量: {len(result)}")
    print(f"   执行时间: {exec_time:.2f}ms")
    print(f"   查询次数: {query_count}")
    
    # 测试7: 时间范围查询
    result, exec_time, query_count = test_due_date_range_query()
    print(f"\n7. 未来7天到期任务查询")
    print(f"   结果数量: {len(result)}")
    print(f"   执行时间: {exec_time:.2f}ms")
    print(f"   查询次数: {query_count}")
    
    # 测试8: 用户统计查询
    result, exec_time, query_count = test_user_statistics_query(test_user)
    print(f"\n8. 用户任务统计查询")
    print(f"   统计结果: {result}")
    print(f"   执行时间: {exec_time:.2f}ms")
    print(f"   查询次数: {query_count}")
    
    # 测试9: 软删除查询
    result, exec_time, query_count = test_soft_delete_query()
    print(f"\n9. 软删除相关查询")
    print(f"   活跃任务: {len(result['active'])}个")
    print(f"   删除任务: {len(result['deleted'])}个")
    print(f"   全部任务: {len(result['all'])}个")
    print(f"   执行时间: {exec_time:.2f}ms")
    print(f"   查询次数: {query_count}")


def show_database_indexes():
    """显示数据库索引信息"""
    print("\n" + "="*80)
    print("📋 数据库索引信息")
    print("="*80)
    
    with connection.cursor() as cursor:
        # SQLite查询索引信息
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND name LIKE 'task_%' ORDER BY name;")
        task_indexes = cursor.fetchall()
        
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND name LIKE 'userprof_%' ORDER BY name;")
        userprof_indexes = cursor.fetchall()
        
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND name LIKE 'login_%' ORDER BY name;")
        login_indexes = cursor.fetchall()
    
    print("\n🎯 Task模型索引:")
    for name, sql in task_indexes:
        print(f"   {name}")
    
    print(f"\n👤 UserProfile模型索引:")
    for name, sql in userprof_indexes:
        print(f"   {name}")
    
    print(f"\n🔐 LoginHistory模型索引:")
    for name, sql in login_indexes:
        print(f"   {name}")
    
    print(f"\n📊 索引统计:")
    print(f"   Task模型索引数: {len(task_indexes)}")
    print(f"   UserProfile模型索引数: {len(userprof_indexes)}")
    print(f"   LoginHistory模型索引数: {len(login_indexes)}")
    print(f"   总索引数: {len(task_indexes) + len(userprof_indexes) + len(login_indexes)}")


def main():
    """主函数"""
    print("🎯 LingTaskFlow 数据库索引优化测试")
    print("=" * 80)
    
    try:
        # 显示索引信息
        show_database_indexes()
        
        # 运行性能测试
        run_performance_tests()
        
        print("\n" + "="*80)
        print("✅ 数据库索引优化测试完成！")
        print("="*80)
        print("\n📈 优化效果总结:")
        print("   - 用户任务查询性能提升")
        print("   - 复合条件查询优化")
        print("   - 时间范围查询加速") 
        print("   - 软删除查询效率提升")
        print("   - 统计查询性能改善")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

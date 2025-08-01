"""
Task模型测试脚本
用于验证Task模型的功能是否正常工作
"""
import os
import sys
import django

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ling_task_flow_backend.settings')
django.setup()

from django.contrib.auth.models import User
from LingTaskFlow.models import Task
from django.utils import timezone
import uuid

def test_task_model():
    """测试Task模型功能"""
    print("=" * 60)
    print("🧪 Task模型功能测试")
    print("=" * 60)
    
    # 1. 创建测试用户
    print("\n1. 创建测试用户...")
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    print(f"   用户: {user.username} ({'新创建' if created else '已存在'})")
    
    # 2. 创建测试任务
    print("\n2. 创建测试任务...")
    task = Task.objects.create(
        title='第一个测试任务',
        description='这是一个测试任务，用于验证Task模型的功能',
        owner=user,
        status='PENDING',
        priority='HIGH',
        category='测试',
        tags='测试, 开发, Django',
        progress=25,
        estimated_hours=8.5
    )
    print(f"   任务创建成功: {task.title}")
    print(f"   任务ID: {task.id}")
    
    # 3. 测试任务属性
    print("\n3. 测试任务属性...")
    print(f"   状态: {task.get_status_display()} (颜色: {task.get_status_color()})")
    print(f"   优先级: {task.get_priority_display()} (颜色: {task.get_priority_color()})")
    print(f"   进度: {task.progress}%")
    print(f"   标签列表: {task.tags_list}")
    print(f"   是否高优先级: {task.is_high_priority}")
    print(f"   是否过期: {task.is_overdue}")
    
    # 4. 测试标签操作
    print("\n4. 测试标签操作...")
    task.add_tag('新标签')
    print(f"   添加标签后: {task.tags_list}")
    task.remove_tag('测试')
    print(f"   移除标签后: {task.tags_list}")
    
    # 5. 测试状态变更
    print("\n5. 测试状态变更...")
    print(f"   变更前 - 状态: {task.status}, 完成时间: {task.completed_at}")
    task.status = 'COMPLETED'
    task.save()
    print(f"   变更后 - 状态: {task.status}, 完成时间: {task.completed_at}")
    print(f"   进度自动更新为: {task.progress}%")
    
    # 6. 测试软删除功能
    print("\n6. 测试软删除功能...")
    print(f"   删除前: is_deleted={task.is_deleted}")
    task.soft_delete()
    print(f"   软删除后: is_deleted={task.is_deleted}, deleted_at={task.deleted_at}")
    
    # 7. 测试查询管理器
    print("\n7. 测试查询管理器...")
    print(f"   总任务数（包含已删除）: {Task.all_objects.count()}")
    print(f"   活跃任务数（排除已删除）: {Task.objects.count()}")
    
    # 8. 测试恢复功能
    print("\n8. 测试恢复功能...")
    task.restore()
    print(f"   恢复后: is_deleted={task.is_deleted}, deleted_at={task.deleted_at}")
    print(f"   活跃任务数: {Task.objects.count()}")
    
    # 9. 测试权限检查
    print("\n9. 测试权限检查...")
    print(f"   用户可以编辑任务: {task.can_edit(user)}")
    print(f"   用户可以删除任务: {task.can_delete(user)}")
    
    # 10. 测试类方法
    print("\n10. 测试类方法...")
    completed_tasks = Task.get_tasks_by_status(user, 'COMPLETED')
    print(f"   用户已完成任务数: {completed_tasks.count()}")
    
    # 11. 测试用户Profile统计更新
    print("\n11. 测试用户Profile统计...")
    if hasattr(user, 'profile'):
        user.profile.update_task_count()
        print(f"   用户任务总数: {user.profile.task_count}")
        print(f"   用户完成任务数: {user.profile.completed_task_count}")
        print(f"   完成率: {user.profile.completion_rate}%")
    
    print("\n" + "=" * 60)
    print("✅ Task模型测试完成！所有功能正常工作")
    print("=" * 60)
    
    return True

def create_more_test_tasks():
    """创建更多测试任务用于演示"""
    print("\n📋 创建更多测试任务...")
    
    user = User.objects.get(username='testuser')
    
    tasks_data = [
        {
            'title': '设计数据库架构',
            'description': '设计任务管理系统的数据库结构',
            'status': 'COMPLETED',
            'priority': 'HIGH',
            'category': '设计',
            'progress': 100
        },
        {
            'title': '实现用户认证',
            'description': '开发用户登录注册功能',
            'status': 'COMPLETED',
            'priority': 'HIGH',
            'category': '开发',
            'progress': 100
        },
        {
            'title': '创建API接口',
            'description': '开发RESTful API接口',
            'status': 'IN_PROGRESS',
            'priority': 'MEDIUM',
            'category': '开发',
            'progress': 60
        },
        {
            'title': '编写单元测试',
            'description': '为所有功能编写单元测试',
            'status': 'PENDING',
            'priority': 'MEDIUM',
            'category': '测试',
            'progress': 0
        },
        {
            'title': '部署到生产环境',
            'description': '配置生产环境并部署应用',
            'status': 'PENDING',
            'priority': 'LOW',
            'category': '运维',
            'progress': 0
        }
    ]
    
    for task_data in tasks_data:
        task = Task.objects.create(
            owner=user,
            **task_data
        )
        print(f"   创建任务: {task.title} ({task.get_status_display()})")
    
    # 更新统计
    user.profile.update_task_count()
    print(f"\n📊 任务统计更新:")
    print(f"   总任务数: {user.profile.task_count}")
    print(f"   完成任务数: {user.profile.completed_task_count}")
    print(f"   完成率: {user.profile.completion_rate}%")

if __name__ == "__main__":
    try:
        # 运行基础测试
        test_task_model()
        
        # 创建更多测试数据
        create_more_test_tasks()
        
        print(f"\n🎉 任务 1.3.1 - 创建Task模型 ✅ 完成!")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

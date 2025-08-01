"""
Task模型层单元测试
测试Task模型的所有功能，包括软删除和恢复方法
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import timedelta, datetime
import uuid

from LingTaskFlow.models import Task, UserProfile


class TaskModelTestCase(TestCase):
    """Task模型基础测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2', 
            email='test2@example.com',
            password='testpass123'
        )
        
        # 创建测试任务
        self.task = Task.objects.create(
            title='测试任务',
            description='这是一个测试任务',
            owner=self.user1,
            assigned_to=self.user2,
            status='PENDING',
            priority='MEDIUM',
            due_date=timezone.now() + timedelta(days=7)
        )
    
    def test_task_creation(self):
        """测试任务创建"""
        self.assertEqual(self.task.title, '测试任务')
        self.assertEqual(self.task.owner, self.user1)
        self.assertEqual(self.task.assigned_to, self.user2)
        self.assertEqual(self.task.status, 'PENDING')
        self.assertEqual(self.task.priority, 'MEDIUM')
        self.assertFalse(self.task.is_deleted)
        self.assertIsInstance(self.task.id, uuid.UUID)
    
    def test_task_string_representation(self):
        """测试任务字符串表示"""
        expected = f"{self.task.title} (待处理)"
        self.assertEqual(str(self.task), expected)
    
    def test_task_required_fields(self):
        """测试必填字段"""
        from django.core.exceptions import ValidationError
        
        # owner是必填字段（外键不能为None）
        with self.assertRaises(ValidationError):
            task_without_owner = Task(
                title='无所有者任务',
                status='PENDING'
            )
            task_without_owner.full_clean()
        
        # title是必填字段（不允许空字符串）
        with self.assertRaises(ValidationError):
            task_with_empty_title = Task(
                title='',  # 空标题应该失败
                owner=self.user1,
                status='PENDING'
            )
            task_with_empty_title.full_clean()
        
        # 正常情况应该通过验证
        valid_task = Task(
            title='有效任务',
            owner=self.user1,
            status='PENDING'
        )
        valid_task.full_clean()  # 应该不抛出异常
        valid_task.save()
        self.assertEqual(valid_task.title, '有效任务')
    
    def test_task_default_values(self):
        """测试默认值"""
        task = Task.objects.create(
            title='测试默认值',
            owner=self.user1
        )
        
        self.assertEqual(task.status, 'PENDING')
        self.assertEqual(task.priority, 'MEDIUM')
        self.assertEqual(task.progress, 0)
        self.assertFalse(task.is_deleted)
        self.assertIsNone(task.deleted_at)
        self.assertIsNone(task.deleted_by)
    
    def test_task_choices_validation(self):
        """测试选择字段验证"""
        # 有效的状态
        valid_statuses = ['PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'ON_HOLD']
        for status in valid_statuses:
            task = Task.objects.create(
                title=f'测试状态{status}',
                owner=self.user1,
                status=status
            )
            self.assertEqual(task.status, status)
        
        # 有效的优先级
        valid_priorities = ['LOW', 'MEDIUM', 'HIGH', 'URGENT']
        for priority in valid_priorities:
            task = Task.objects.create(
                title=f'测试优先级{priority}',
                owner=self.user1,
                priority=priority
            )
            self.assertEqual(task.priority, priority)


class TaskPropertyTestCase(TestCase):
    """Task模型属性测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_is_overdue_property(self):
        """测试is_overdue属性"""
        # 未过期任务
        future_task = Task.objects.create(
            title='未来任务',
            owner=self.user,
            due_date=timezone.now() + timedelta(days=1)
        )
        self.assertFalse(future_task.is_overdue)
        
        # 过期任务
        overdue_task = Task.objects.create(
            title='过期任务',
            owner=self.user,
            due_date=timezone.now() - timedelta(days=1),
            status='PENDING'
        )
        self.assertTrue(overdue_task.is_overdue)
        
        # 已完成任务不算过期
        completed_task = Task.objects.create(
            title='已完成任务',
            owner=self.user,
            due_date=timezone.now() - timedelta(days=1),
            status='COMPLETED'
        )
        self.assertFalse(completed_task.is_overdue)
        
        # 无截止时间不算过期
        no_due_date_task = Task.objects.create(
            title='无截止时间任务',
            owner=self.user
        )
        self.assertFalse(no_due_date_task.is_overdue)
    
    def test_time_remaining_property(self):
        """测试time_remaining属性"""
        # 有剩余时间
        future_task = Task.objects.create(
            title='未来任务',
            owner=self.user,
            due_date=timezone.now() + timedelta(days=1)
        )
        remaining = future_task.time_remaining
        self.assertIsNotNone(remaining)
        self.assertGreater(remaining.total_seconds(), 0)
        
        # 已过期
        overdue_task = Task.objects.create(
            title='过期任务',
            owner=self.user,
            due_date=timezone.now() - timedelta(days=1)
        )
        self.assertIsNone(overdue_task.time_remaining)
        
        # 无截止时间
        no_due_date_task = Task.objects.create(
            title='无截止时间任务',
            owner=self.user
        )
        self.assertIsNone(no_due_date_task.time_remaining)
    
    def test_is_high_priority_property(self):
        """测试is_high_priority属性"""
        # 高优先级
        high_task = Task.objects.create(
            title='高优先级任务',
            owner=self.user,
            priority='HIGH'
        )
        self.assertTrue(high_task.is_high_priority)
        
        urgent_task = Task.objects.create(
            title='紧急任务',
            owner=self.user,
            priority='URGENT'
        )
        self.assertTrue(urgent_task.is_high_priority)
        
        # 非高优先级
        medium_task = Task.objects.create(
            title='中等优先级任务',
            owner=self.user,
            priority='MEDIUM'
        )
        self.assertFalse(medium_task.is_high_priority)
        
        low_task = Task.objects.create(
            title='低优先级任务',
            owner=self.user,
            priority='LOW'
        )
        self.assertFalse(low_task.is_high_priority)
    
    def test_tags_list_property(self):
        """测试tags_list属性"""
        # 有标签
        task_with_tags = Task.objects.create(
            title='有标签任务',
            owner=self.user,
            tags='Python, Django, 测试'
        )
        expected_tags = ['Python', 'Django', '测试']
        self.assertEqual(task_with_tags.tags_list, expected_tags)
        
        # 无标签
        task_no_tags = Task.objects.create(
            title='无标签任务',
            owner=self.user,
            tags=''
        )
        self.assertEqual(task_no_tags.tags_list, [])
        
        # 空格处理
        task_spaces = Task.objects.create(
            title='空格处理任务',
            owner=self.user,
            tags='  tag1  ,  tag2  ,  '
        )
        expected_clean_tags = ['tag1', 'tag2']
        self.assertEqual(task_spaces.tags_list, expected_clean_tags)


class TaskMethodTestCase(TestCase):
    """Task模型方法测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.task = Task.objects.create(
            title='测试任务',
            owner=self.user,
            tags='tag1, tag2'
        )
    
    def test_add_tag_method(self):
        """测试add_tag方法"""
        self.task.add_tag('tag3')
        self.assertIn('tag3', self.task.tags_list)
        
        # 添加重复标签
        self.task.add_tag('tag1')
        tag_count = self.task.tags_list.count('tag1')
        self.assertEqual(tag_count, 1)
    
    def test_remove_tag_method(self):
        """测试remove_tag方法"""
        self.task.remove_tag('tag1')
        self.assertNotIn('tag1', self.task.tags_list)
        
        # 移除不存在的标签
        self.task.remove_tag('nonexistent')
        # 应该不会出错
    
    def test_get_priority_color_method(self):
        """测试get_priority_color方法"""
        colors = {
            'LOW': '#28a745',
            'MEDIUM': '#ffc107',
            'HIGH': '#fd7e14',
            'URGENT': '#dc3545'
        }
        
        for priority, expected_color in colors.items():
            self.task.priority = priority
            self.assertEqual(self.task.get_priority_color(), expected_color)
    
    def test_get_status_color_method(self):
        """测试get_status_color方法"""
        colors = {
            'PENDING': '#6c757d',
            'IN_PROGRESS': '#007bff',
            'COMPLETED': '#28a745',
            'CANCELLED': '#dc3545',
            'ON_HOLD': '#ffc107'
        }
        
        for status, expected_color in colors.items():
            self.task.status = status
            self.assertEqual(self.task.get_status_color(), expected_color)
    
    def test_can_edit_method(self):
        """测试can_edit方法"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        # 所有者可以编辑
        self.assertTrue(self.task.can_edit(self.user))
        
        # 执行者可以编辑
        self.task.assigned_to = other_user
        self.task.save()
        self.assertTrue(self.task.can_edit(other_user))
        
        # 其他用户不能编辑
        third_user = User.objects.create_user(
            username='thirduser',
            email='third@example.com',
            password='testpass123'
        )
        self.assertFalse(self.task.can_edit(third_user))
    
    def test_can_delete_method(self):
        """测试can_delete方法"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        # 所有者可以删除
        self.assertTrue(self.task.can_delete(self.user))
        
        # 执行者不能删除
        self.task.assigned_to = other_user
        self.task.save()
        self.assertFalse(self.task.can_delete(other_user))


class TaskSaveMethodTestCase(TestCase):
    """Task模型save方法测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_completed_status_auto_completion(self):
        """测试完成状态自动设置"""
        task = Task.objects.create(
            title='测试完成',
            owner=self.user,
            status='PENDING',
            progress=50
        )
        
        # 设置为已完成
        task.status = 'COMPLETED'
        task.save()
        
        # 检查自动设置
        self.assertIsNotNone(task.completed_at)
        self.assertEqual(task.progress, 100)
    
    def test_non_completed_status_clears_completion(self):
        """测试非完成状态清除完成信息"""
        task = Task.objects.create(
            title='测试取消完成',
            owner=self.user,
            status='COMPLETED',
            completed_at=timezone.now(),
            progress=100
        )
        
        # 修改为其他状态
        task.status = 'IN_PROGRESS'
        task.save()
        
        # 检查清除完成时间
        self.assertIsNone(task.completed_at)
    
    def test_user_profile_update_on_save(self):
        """测试保存时用户统计更新"""
        initial_count = self.user.profile.task_count
        
        # 创建新任务
        Task.objects.create(
            title='新任务',
            owner=self.user
        )
        
        # 刷新用户profile
        self.user.profile.refresh_from_db()
        
        # 检查统计更新
        self.assertEqual(self.user.profile.task_count, initial_count + 1)


class TaskClassMethodTestCase(TestCase):
    """Task模型类方法测试"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # 创建测试任务
        self.pending_task = Task.objects.create(
            title='待处理任务',
            owner=self.user1,
            status='PENDING'
        )
        self.completed_task = Task.objects.create(
            title='已完成任务',
            owner=self.user1,
            status='COMPLETED'
        )
        self.assigned_task = Task.objects.create(
            title='分配任务',
            owner=self.user2,
            assigned_to=self.user1,
            status='IN_PROGRESS'
        )
    
    def test_get_tasks_by_status(self):
        """测试get_tasks_by_status方法"""
        pending_tasks = Task.get_tasks_by_status(self.user1, 'PENDING')
        completed_tasks = Task.get_tasks_by_status(self.user1, 'COMPLETED')
        in_progress_tasks = Task.get_tasks_by_status(self.user1, 'IN_PROGRESS')
        
        # 检查结果
        self.assertIn(self.pending_task, pending_tasks)
        self.assertIn(self.completed_task, completed_tasks)
        self.assertIn(self.assigned_task, in_progress_tasks)  # 分配的任务也应该包含
    
    def test_get_overdue_tasks(self):
        """测试get_overdue_tasks方法"""
        # 创建过期任务
        overdue_task = Task.objects.create(
            title='过期任务',
            owner=self.user1,
            due_date=timezone.now() - timedelta(days=1),
            status='PENDING'
        )
        
        overdue_tasks = Task.get_overdue_tasks(self.user1)
        self.assertIn(overdue_task, overdue_tasks)
        
        # 已完成的过期任务不应该包含
        completed_overdue = Task.objects.create(
            title='已完成过期任务',
            owner=self.user1,
            due_date=timezone.now() - timedelta(days=1),
            status='COMPLETED'
        )
        self.assertNotIn(completed_overdue, overdue_tasks)
    
    def test_get_tasks_due_soon(self):
        """测试get_tasks_due_soon方法"""
        # 创建即将到期的任务
        soon_task = Task.objects.create(
            title='即将到期任务',
            owner=self.user1,
            due_date=timezone.now() + timedelta(days=3),
            status='PENDING'
        )
        
        # 创建很远的任务
        far_task = Task.objects.create(
            title='很远任务',
            owner=self.user1,
            due_date=timezone.now() + timedelta(days=30),
            status='PENDING'
        )
        
        due_soon_tasks = Task.get_tasks_due_soon(self.user1, days=7)
        
        self.assertIn(soon_task, due_soon_tasks)
        self.assertNotIn(far_task, due_soon_tasks)


if __name__ == '__main__':
    import os
    import django
    from django.test.utils import get_runner
    from django.conf import settings
    
    # 配置测试设置
    if not settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ling_task_flow_backend.settings')
        django.setup()
    
    # 运行测试
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['tests.models.test_task'])
    
    if failures:
        raise SystemExit(1)

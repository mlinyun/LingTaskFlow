"""
Task模型软删除功能单元测试
测试软删除、恢复、批量操作等功能
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid

from LingTaskFlow.models import Task


class SoftDeleteModelTestCase(TestCase):
    """软删除基础功能测试"""
    
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
        
        self.task = Task.objects.create(
            title='测试软删除任务',
            description='用于测试软删除功能',
            owner=self.user1,
            status='PENDING',
            priority='MEDIUM'
        )
    
    def test_soft_delete_basic(self):
        """测试基础软删除功能"""
        # 检查初始状态
        self.assertFalse(self.task.is_deleted)
        self.assertIsNone(self.task.deleted_at)
        self.assertIsNone(self.task.deleted_by)
        
        # 执行软删除
        self.task.soft_delete(user=self.user1)
        
        # 检查软删除状态
        self.assertTrue(self.task.is_deleted)
        self.assertIsNotNone(self.task.deleted_at)
        self.assertEqual(self.task.deleted_by, self.user1)
        self.assertTrue(self.task.can_be_restored)
        self.assertEqual(self.task.deletion_age, 0)
    
    def test_soft_delete_without_user(self):
        """测试无用户信息的软删除"""
        self.task.soft_delete()
        
        self.assertTrue(self.task.is_deleted)
        self.assertIsNotNone(self.task.deleted_at)
        self.assertIsNone(self.task.deleted_by)
    
    def test_restore_basic(self):
        """测试基础恢复功能"""
        # 先软删除
        self.task.soft_delete(user=self.user1)
        self.assertTrue(self.task.is_deleted)
        
        # 恢复
        self.task.restore(user=self.user2)
        
        # 检查恢复状态
        self.assertFalse(self.task.is_deleted)
        self.assertIsNone(self.task.deleted_at)
        self.assertIsNone(self.task.deleted_by)
        self.assertFalse(self.task.can_be_restored)
    
    def test_delete_method_override(self):
        """测试重写的delete方法"""
        # delete()方法应该执行软删除而不是硬删除
        task_id = self.task.id
        self.task.delete()
        
        # 任务应该还存在，但被标记为删除
        task_from_db = Task.all_objects.get(id=task_id)
        self.assertTrue(task_from_db.is_deleted)
        
        # 默认查询应该不包含已删除的任务
        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(id=task_id)
    
    def test_hard_delete(self):
        """测试硬删除"""
        task_id = self.task.id
        
        # 硬删除
        self.task.hard_delete()
        
        # 任务应该完全从数据库中删除
        with self.assertRaises(Task.DoesNotExist):
            Task.all_objects.get(id=task_id)
    
    def test_deletion_info(self):
        """测试删除信息获取"""
        # 未删除任务
        info = self.task.get_deletion_info()
        self.assertIsNone(info)
        
        # 已删除任务
        self.task.soft_delete(user=self.user1)
        info = self.task.get_deletion_info()
        
        self.assertIsNotNone(info)
        self.assertTrue(info['is_deleted'])
        self.assertIsNotNone(info['deleted_at'])
        self.assertEqual(info['deleted_by'], self.user1)
        self.assertEqual(info['deletion_age_days'], 0)
        self.assertTrue(info['can_be_restored'])


class SoftDeleteManagerTestCase(TestCase):
    """软删除管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建多个任务
        self.active_task1 = Task.objects.create(
            title='活跃任务1',
            owner=self.user,
            status='PENDING'
        )
        self.active_task2 = Task.objects.create(
            title='活跃任务2',
            owner=self.user,
            status='IN_PROGRESS'
        )
        self.deleted_task = Task.objects.create(
            title='删除任务',
            owner=self.user,
            status='COMPLETED'
        )
        
        # 软删除一个任务
        self.deleted_task.soft_delete(user=self.user)
    
    def test_default_manager_excludes_deleted(self):
        """测试默认管理器排除已删除记录"""
        tasks = Task.objects.all()
        
        self.assertIn(self.active_task1, tasks)
        self.assertIn(self.active_task2, tasks)
        self.assertNotIn(self.deleted_task, tasks)
        self.assertEqual(tasks.count(), 2)
    
    def test_all_objects_includes_deleted(self):
        """测试all_objects管理器包含已删除记录"""
        all_tasks = Task.all_objects.all()
        
        self.assertIn(self.active_task1, all_tasks)
        self.assertIn(self.active_task2, all_tasks)
        self.assertIn(self.deleted_task, all_tasks)
        self.assertEqual(all_tasks.count(), 3)
    
    def test_deleted_only_manager(self):
        """测试deleted_only管理器"""
        deleted_tasks = Task.objects.deleted_only()
        
        self.assertNotIn(self.active_task1, deleted_tasks)
        self.assertNotIn(self.active_task2, deleted_tasks)
        self.assertIn(self.deleted_task, deleted_tasks)
        self.assertEqual(deleted_tasks.count(), 1)
    
    def test_all_with_deleted_manager(self):
        """测试all_with_deleted管理器"""
        all_with_deleted = Task.objects.all_with_deleted()
        
        self.assertIn(self.active_task1, all_with_deleted)
        self.assertIn(self.active_task2, all_with_deleted)
        self.assertIn(self.deleted_task, all_with_deleted)
        self.assertEqual(all_with_deleted.count(), 3)


class TaskSoftDeleteMethodsTestCase(TestCase):
    """Task模型软删除专用方法测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        self.task = Task.objects.create(
            title='测试任务',
            owner=self.user,
            status='PENDING'
        )
    
    def test_can_restore_permission(self):
        """测试can_restore权限"""
        # 未删除任务不能恢复
        self.assertFalse(self.task.can_restore(self.user))
        
        # 软删除任务
        self.task.soft_delete(user=self.user)
        
        # 所有者可以恢复
        self.assertTrue(self.task.can_restore(self.user))
        
        # 其他用户不能恢复
        self.assertFalse(self.task.can_restore(self.other_user))
    
    def test_get_trash_info(self):
        """测试get_trash_info方法"""
        # 未删除任务
        self.assertIsNone(self.task.get_trash_info())
        
        # 删除任务
        self.task.soft_delete(user=self.user)
        trash_info = self.task.get_trash_info()
        
        self.assertIsNotNone(trash_info)
        self.assertEqual(trash_info['task_id'], str(self.task.id))
        self.assertEqual(trash_info['title'], self.task.title)
        self.assertEqual(trash_info['owner'], self.user.username)
        self.assertEqual(trash_info['deleted_by'], self.user.username)
        self.assertEqual(trash_info['status_when_deleted'], 'PENDING')
        self.assertTrue(trash_info['can_be_restored'])
    
    def test_get_user_trash(self):
        """测试get_user_trash类方法"""
        # 创建多个任务
        task1 = Task.objects.create(title='任务1', owner=self.user)
        task2 = Task.objects.create(title='任务2', owner=self.user)
        task3 = Task.objects.create(title='任务3', owner=self.other_user, assigned_to=self.user)
        
        # 删除部分任务
        task1.soft_delete(user=self.user)
        task3.soft_delete(user=self.other_user)
        
        # 测试用户回收站（不包含分配任务）
        user_trash = Task.get_user_trash(self.user, include_assigned=False)
        self.assertIn(task1, user_trash)
        self.assertNotIn(task2, user_trash)  # 未删除
        self.assertNotIn(task3, user_trash)  # 不是所有者
        
        # 测试用户回收站（包含分配任务）
        user_trash_with_assigned = Task.get_user_trash(self.user, include_assigned=True)
        self.assertIn(task1, user_trash_with_assigned)
        self.assertIn(task3, user_trash_with_assigned)  # 分配给用户的删除任务
    
    def test_restore_user_tasks(self):
        """测试restore_user_tasks批量恢复"""
        # 创建并删除多个任务
        task1 = Task.objects.create(title='任务1', owner=self.user)
        task2 = Task.objects.create(title='任务2', owner=self.user)
        task3 = Task.objects.create(title='任务3', owner=self.other_user)
        
        task1.soft_delete(user=self.user)
        task2.soft_delete(user=self.user)
        task3.soft_delete(user=self.other_user)
        
        # 批量恢复用户任务
        task_ids = [str(task1.id), str(task2.id), str(task3.id)]
        result = Task.restore_user_tasks(self.user, task_ids)
        
        # 检查结果
        self.assertEqual(result['restored'], 2)  # 只能恢复自己的任务
        self.assertEqual(result['failed'], 0)
        self.assertEqual(result['total'], 3)
        
        # 检查任务状态
        task1.refresh_from_db()
        task2.refresh_from_db()
        task3.refresh_from_db()
        
        self.assertFalse(task1.is_deleted)
        self.assertFalse(task2.is_deleted)
        self.assertTrue(task3.is_deleted)  # 不是用户的任务，未恢复
    
    def test_permanent_delete_user_tasks(self):
        """测试permanent_delete_user_tasks批量永久删除"""
        # 创建并删除多个任务
        task1 = Task.objects.create(title='任务1', owner=self.user)
        task2 = Task.objects.create(title='任务2', owner=self.user)
        task3 = Task.objects.create(title='任务3', owner=self.other_user)
        
        task1.soft_delete(user=self.user)
        task2.soft_delete(user=self.user)
        task3.soft_delete(user=self.other_user)
        
        # 批量永久删除
        task_ids = [str(task1.id), str(task2.id), str(task3.id)]
        result = Task.permanent_delete_user_tasks(self.user, task_ids)
        
        # 检查结果
        self.assertEqual(result['deleted'], 2)  # 只能删除自己的任务
        self.assertEqual(result['total'], 3)
        
        # 检查任务是否被永久删除
        with self.assertRaises(Task.DoesNotExist):
            Task.all_objects.get(id=task1.id)
        with self.assertRaises(Task.DoesNotExist):
            Task.all_objects.get(id=task2.id)
        
        # 其他用户的任务应该还存在
        task3_exists = Task.all_objects.filter(id=task3.id).exists()
        self.assertTrue(task3_exists)
    
    def test_cleanup_old_deleted_tasks(self):
        """测试cleanup_old_deleted_tasks清理功能"""
        # 创建"旧"删除任务
        old_task = Task.objects.create(title='旧任务', owner=self.user)
        recent_task = Task.objects.create(title='近期任务', owner=self.user)
        
        # 手动设置删除时间
        old_deleted_time = timezone.now() - timedelta(days=35)
        recent_deleted_time = timezone.now() - timedelta(days=5)
        
        old_task.soft_delete(user=self.user)
        recent_task.soft_delete(user=self.user)
        
        # 直接更新数据库中的删除时间
        Task.all_objects.filter(id=old_task.id).update(deleted_at=old_deleted_time)
        Task.all_objects.filter(id=recent_task.id).update(deleted_at=recent_deleted_time)
        
        # 执行清理（30天）
        cleaned_count = Task.cleanup_old_deleted_tasks(days=30)
        
        # 检查清理结果
        self.assertEqual(cleaned_count, 1)
        
        # 旧任务应该被永久删除
        old_task_exists = Task.all_objects.filter(id=old_task.id).exists()
        self.assertFalse(old_task_exists)
        
        # 近期任务应该还存在
        recent_task_exists = Task.all_objects.filter(id=recent_task.id).exists()
        self.assertTrue(recent_task_exists)
    
    def test_get_deletion_statistics(self):
        """测试get_deletion_statistics统计功能"""
        # 创建并删除多个任务
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 今天删除的任务
        today_task = Task.objects.create(title='今天删除', owner=self.user)
        today_task.soft_delete(user=self.user)
        
        # 一周前删除的任务
        week_old_task = Task.objects.create(title='一周前删除', owner=self.user)
        week_old_task.soft_delete(user=self.user)
        week_old_time = today - timedelta(days=7)
        Task.all_objects.filter(id=week_old_task.id).update(deleted_at=week_old_time)
        
        # 一月前删除的任务
        month_old_task = Task.objects.create(title='一月前删除', owner=self.user)
        month_old_task.soft_delete(user=self.user)
        month_old_time = today - timedelta(days=35)
        Task.all_objects.filter(id=month_old_task.id).update(deleted_at=month_old_time)
        
        # 获取统计
        stats = Task.get_deletion_statistics(self.user)
        
        # 检查统计结果
        self.assertEqual(stats['total_deleted'], 3)
        self.assertEqual(stats['deleted_today'], 1)
        self.assertEqual(stats['deleted_this_week'], 2)  # 今天和一周前删除的都算在本周内
        self.assertEqual(stats['deleted_this_month'], 2)  # 今天和一周前的算在本月内
        self.assertEqual(stats['can_be_cleaned'], 1)  # 一月前的可以清理
        
        # 检查最早和最新删除
        self.assertEqual(stats['oldest_deleted'].title, '一月前删除')
        self.assertEqual(stats['newest_deleted'].title, '今天删除')


class SoftDeleteIntegrationTestCase(TestCase):
    """软删除功能集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_profile_update_integration(self):
        """测试用户统计与软删除的集成"""
        initial_count = self.user.profile.task_count
        
        # 创建任务
        task = Task.objects.create(title='集成测试任务', owner=self.user)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.task_count, initial_count + 1)
        
        # 软删除任务
        task.soft_delete(user=self.user)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.task_count, initial_count)  # 应该减少
        
        # 恢复任务
        task.restore(user=self.user)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.task_count, initial_count + 1)  # 应该增加
    
    def test_query_performance_with_soft_delete(self):
        """测试软删除对查询性能的影响"""
        # 创建大量任务（模拟性能测试）
        tasks = []
        for i in range(100):
            task = Task.objects.create(
                title=f'性能测试任务{i}',
                owner=self.user,
                status='PENDING' if i % 2 == 0 else 'COMPLETED'
            )
            tasks.append(task)
        
        # 删除一半任务
        for i in range(0, 100, 2):
            tasks[i].soft_delete(user=self.user)
        
        # 测试查询性能
        import time
        
        # 默认查询（应该排除删除的）
        start_time = time.time()
        active_tasks = list(Task.objects.filter(owner=self.user))
        active_query_time = time.time() - start_time
        
        # 包含删除的查询
        start_time = time.time()
        all_tasks = list(Task.all_objects.filter(owner=self.user))
        all_query_time = time.time() - start_time
        
        # 检查结果正确性
        self.assertEqual(len(active_tasks), 50)  # 只有未删除的
        self.assertEqual(len(all_tasks), 100)   # 包含所有的
        
        # 性能检查（默认查询应该不会显著慢于全量查询）
        self.assertLess(active_query_time, all_query_time * 2)  # 允许2倍差异

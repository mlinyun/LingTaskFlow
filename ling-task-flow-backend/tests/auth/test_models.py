"""
认证系统单元测试 - 模型测试
测试UserProfile模型的功能
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from LingTaskFlow.models import UserProfile


class UserProfileModelTest(TestCase):
    """UserProfile模型测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_userprofile_creation_on_user_save(self):
        """测试用户创建时自动创建UserProfile"""
        # UserProfile应该已经通过信号自动创建
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
    
    def test_userprofile_default_values(self):
        """测试UserProfile默认值"""
        profile = self.user.profile
        
        self.assertEqual(profile.timezone, 'Asia/Shanghai')
        self.assertEqual(profile.task_count, 0)
        self.assertEqual(profile.completed_task_count, 0)
        self.assertEqual(profile.theme_preference, 'auto')
        self.assertTrue(profile.email_notifications)
        self.assertIsNone(profile.avatar.name if profile.avatar else None)
    
    def test_userprofile_str_representation(self):
        """测试字符串表示"""
        profile = self.user.profile
        expected = f"{self.user.username} 的扩展信息"
        self.assertEqual(str(profile), expected)
    
    def test_userprofile_update_fields(self):
        """测试更新UserProfile字段"""
        profile = self.user.profile
        
        # 更新字段
        profile.timezone = 'America/New_York'
        profile.theme_preference = 'dark'
        profile.email_notifications = False
        profile.task_count = 5
        profile.completed_task_count = 3
        profile.save()
        
        # 重新获取并验证
        profile.refresh_from_db()
        self.assertEqual(profile.timezone, 'America/New_York')
        self.assertEqual(profile.theme_preference, 'dark')
        self.assertFalse(profile.email_notifications)
        self.assertEqual(profile.task_count, 5)
        self.assertEqual(profile.completed_task_count, 3)
    
    def test_userprofile_avatar_upload(self):
        """测试头像上传"""
        profile = self.user.profile
        
        # 创建一个测试图片文件
        test_image = SimpleUploadedFile(
            name='test_avatar.jpg',
            content=b'fake_image_content',
            content_type='image/jpeg'
        )
        
        profile.avatar = test_image
        profile.save()
        
        # 验证头像路径
        self.assertIn('avatars/', profile.avatar.name)
        self.assertIn('test_avatar', profile.avatar.name)
    
    def test_userprofile_theme_choices(self):
        """测试主题选择的有效性"""
        profile = self.user.profile
        
        valid_themes = ['light', 'dark', 'auto']
        for theme in valid_themes:
            profile.theme_preference = theme
            profile.save()
            profile.refresh_from_db()
            self.assertEqual(profile.theme_preference, theme)
    
    def test_userprofile_cascade_delete(self):
        """测试用户删除时UserProfile级联删除"""
        profile_id = self.user.profile.id
        
        # 删除用户
        self.user.delete()
        
        # 验证UserProfile也被删除
        with self.assertRaises(UserProfile.DoesNotExist):
            UserProfile.objects.get(id=profile_id)
    
    def test_userprofile_unique_per_user(self):
        """测试每个用户只能有一个UserProfile"""
        # 尝试为同一用户创建另一个profile
        with self.assertRaises(IntegrityError):
            UserProfile.objects.create(user=self.user)
    
    def test_userprofile_ordering(self):
        """测试UserProfile排序"""
        # 创建多个用户和profile
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        user3 = User.objects.create_user(
            username='testuser3',
            email='test3@example.com',
            password='testpass123'
        )
        
        # 获取所有profile，应该按创建时间倒序
        profiles = UserProfile.objects.all()
        self.assertEqual(profiles[0].user, user3)
        self.assertEqual(profiles[1].user, user2)
        self.assertEqual(profiles[2].user, self.user)
    
    def test_userprofile_meta_options(self):
        """测试模型元数据选项"""
        meta = UserProfile._meta
        
        self.assertEqual(meta.db_table, 'user_profiles')
        self.assertEqual(meta.verbose_name, '用户扩展信息')
        self.assertEqual(meta.verbose_name_plural, '用户扩展信息')
        self.assertEqual(meta.ordering, ['-created_at'])
    
    def test_update_task_count_method_exists(self):
        """测试update_task_count方法存在"""
        profile = self.user.profile
        
        # 方法应该存在（即使现在是空实现）
        self.assertTrue(hasattr(profile, 'update_task_count'))
        self.assertTrue(callable(getattr(profile, 'update_task_count')))
        
        # 调用不应该抛出异常
        try:
            profile.update_task_count()
        except Exception as e:
            self.fail(f"update_task_count方法调用失败: {e}")


class UserModelExtensionTest(TestCase):
    """User模型扩展测试"""
    
    def test_user_profile_related_name(self):
        """测试User模型的profile关联"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 应该能通过user.profile访问UserProfile
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, UserProfile)
        
        # 反向关联也应该正常工作
        self.assertEqual(user.profile.user, user)

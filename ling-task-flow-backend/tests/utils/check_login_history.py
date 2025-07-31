#!/usr/bin/env python
"""
检查登录历史记录的脚本
"""

import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ling_task_flow_backend.settings')

django.setup()

from LingTaskFlow.models import LoginHistory
from django.contrib.auth.models import User

try:
    print("🔍 检查登录历史记录")
    print("=" * 50)
    
    # 获取所有登录历史记录
    login_histories = LoginHistory.objects.all().order_by('-login_time')
    
    print(f"总登录记录数: {login_histories.count()}")
    print()
    
    if login_histories.exists():
        print("最近的登录记录：")
        for i, history in enumerate(login_histories[:5], 1):  # 显示最近5条记录
            print(f"[{i}] 用户: {history.username_attempted}")
            print(f"    状态: {history.get_status_display()}")
            print(f"    IP地址: {history.ip_address}")
            print(f"    位置: {history.location or '未知'}")
            print(f"    登录时间: {history.login_time}")
            print(f"    是否可疑: {'是' if history.is_suspicious else '否'}")
            if history.failure_reason:
                print(f"    失败原因: {history.failure_reason}")
            print("-" * 30)
    else:
        print("没有找到登录记录")
    
    # 检查用户Profile创建情况
    print("\n👤 检查UserProfile创建情况")
    print("=" * 50)
    
    users_with_profiles = User.objects.filter(profile__isnull=False).count()
    total_users = User.objects.count()
    
    print(f"总用户数: {total_users}")
    print(f"有Profile的用户数: {users_with_profiles}")
    
    if total_users > 0:
        print(f"Profile创建率: {(users_with_profiles/total_users*100):.1f}%")
    
    # 检查测试用户的Profile
    try:
        test_user = User.objects.get(username='testadmin')
        if hasattr(test_user, 'profile'):
            profile = test_user.profile
            print(f"\n测试用户Profile信息:")
            print(f"  时区: {profile.timezone}")
            print(f"  任务数: {profile.task_count}")
            print(f"  完成率: {profile.completion_rate}%")
            print(f"  主题偏好: {profile.theme_preference}")
            print(f"  邮件通知: {'开启' if profile.email_notifications else '关闭'}")
        else:
            print(f"\n⚠️  测试用户没有Profile")
    except User.DoesNotExist:
        print("\n⚠️  测试用户不存在")
    
except Exception as e:
    print(f"错误: {str(e)}")
    import traceback
    traceback.print_exc()

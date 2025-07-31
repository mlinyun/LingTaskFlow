#!/usr/bin/env python
"""
设置测试用户密码的脚本
"""

import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ling_task_flow_backend.settings')

django.setup()

from django.contrib.auth.models import User

try:
    # 获取或创建测试用户
    user, created = User.objects.get_or_create(username='testadmin')
    if created:
        user.email = 'test@example.com'
        user.is_staff = True
        user.is_superuser = True
    
    # 设置密码
    user.set_password('TestPassword123!')
    user.save()
    
    print(f"用户 {user.username} 密码设置成功")
    print(f"用户名: testadmin")
    print(f"密码: TestPassword123!")
    
except Exception as e:
    print(f"错误: {str(e)}")

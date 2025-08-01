#!/usr/bin/env python3
"""
任务搜索和过滤API测试
测试任务2.1.7的实现
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ling_task_flow_backend.settings')

import django
django.setup()

from django.contrib.auth.models import User
from LingTaskFlow.models import Task
from django.utils import timezone

class TaskSearchAPITester:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000/api"
        self.token = None
        self.user = None
        
    def setup_test_data(self):
        """设置测试数据"""
        print("🔧 设置测试数据...")
        
        # 创建测试用户
        try:
            self.user = User.objects.get(username='test_search_user')
        except User.DoesNotExist:
            self.user = User.objects.create_user(
                username='test_search_user',
                email='test_search@example.com',
                password='testpass123'
            )
        
        # 清理之前的测试数据
        Task.all_objects.filter(owner=self.user).delete()
        
        # 创建多样化的测试任务
        test_tasks = [
            {
                'title': 'Python开发任务',
                'description': '开发Python后端API接口',
                'category': '开发',
                'priority': 'HIGH',
                'status': 'IN_PROGRESS',
                'progress': 60,
                'tags': 'Python, API, 后端',
                'due_date': (timezone.now() + timedelta(days=3)).date(),
                'start_date': (timezone.now() - timedelta(days=2)).date(),
            },
            {
                'title': '前端Vue组件开发',
                'description': '开发Vue3组件和页面',
                'category': '前端',
                'priority': 'MEDIUM',
                'status': 'PENDING',
                'progress': 0,
                'tags': 'Vue, 前端, 组件',
                'due_date': (timezone.now() + timedelta(days=7)).date(),
                'start_date': timezone.now().date(),
            },
            {
                'title': '数据库设计',
                'description': '设计数据库表结构和关系',
                'category': '数据库',
                'priority': 'HIGH',
                'status': 'COMPLETED',
                'progress': 100,
                'tags': '数据库, 设计, MySQL',
                'due_date': (timezone.now() - timedelta(days=1)).date(),
                'start_date': (timezone.now() - timedelta(days=5)).date(),
            },
            {
                'title': '项目文档编写',
                'description': '编写项目技术文档和用户手册',
                'category': '文档',
                'priority': 'LOW',
                'status': 'PENDING',
                'progress': 20,
                'tags': '文档, 说明书, 手册',
                'due_date': (timezone.now() + timedelta(days=14)).date(),
                'start_date': (timezone.now() + timedelta(days=1)).date(),
            },
            {
                'title': 'Bug修复：登录问题',
                'description': '修复用户登录时的会话问题',
                'category': '开发',
                'priority': 'URGENT',
                'status': 'IN_PROGRESS',
                'progress': 80,
                'tags': 'Bug, 修复, 登录',
                'due_date': timezone.now().date(),  # 今天到期（逾期测试）
                'start_date': (timezone.now() - timedelta(days=1)).date(),
            },
            {
                'title': '性能优化',
                'description': '优化应用性能和响应速度',
                'category': '优化',
                'priority': 'MEDIUM',
                'status': 'ON_HOLD',
                'progress': 30,
                'tags': '性能, 优化, 速度',
                'due_date': (timezone.now() + timedelta(days=10)).date(),
                'start_date': (timezone.now() + timedelta(days=2)).date(),
            }
        ]
        
        for task_data in test_tasks:
            Task.objects.create(owner=self.user, **task_data)
        
        print(f"✅ 创建了 {len(test_tasks)} 个测试任务")
    
    def login(self):
        """登录获取Token"""
        login_data = {
            'username': 'test_search_user',
            'password': 'testpass123'
        }
        
        response = requests.post(f"{self.base_url}/auth/login/", json=login_data)
        if response.status_code == 200:
            data = response.json()
            self.token = data['data']['tokens']['access']
            print("✅ 登录成功")
            return True
        else:
            print(f"❌ 登录失败: {response.text}")
            return False
    
    def get_headers(self):
        """获取请求头"""
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def test_basic_search(self):
        """测试基础搜索功能"""
        print("\n🔍 测试基础搜索功能...")
        
        # 测试全文搜索
        response = requests.get(
            f"{self.base_url}/tasks/search/",
            params={'q': 'Python'},
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data['data']['results']
            print(f"✅ 全文搜索 'Python': 找到 {len(results)} 个任务")
            for task in results:
                print(f"   - {task['title']}")
        else:
            print(f"❌ 全文搜索失败: {response.text}")
        
        # 测试标题搜索
        response = requests.get(
            f"{self.base_url}/tasks/search/",
            params={'title': '开发'},
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data['data']['results']
            print(f"✅ 标题搜索 '开发': 找到 {len(results)} 个任务")
        else:
            print(f"❌ 标题搜索失败: {response.text}")
    
    def test_status_priority_filter(self):
        """测试状态和优先级过滤"""
        print("\n📊 测试状态和优先级过滤...")
        
        # 测试状态过滤
        response = requests.get(
            f"{self.base_url}/tasks/search/",
            params={'status': 'IN_PROGRESS,PENDING'},
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data['data']['results']
            print(f"✅ 状态过滤 (IN_PROGRESS,PENDING): 找到 {len(results)} 个任务")
            
            # 显示状态分布统计
            stats = data['data']['stats']
            print("   状态分布:")
            for status, info in stats['status_distribution'].items():
                print(f"     {status}: {info['count']} 个 ({info['percentage']}%)")
        else:
            print(f"❌ 状态过滤失败: {response.text}")
        
        # 测试优先级过滤
        response = requests.get(
            f"{self.base_url}/tasks/search/",
            params={'priority': 'HIGH,URGENT'},
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data['data']['results']
            print(f"✅ 优先级过滤 (HIGH,URGENT): 找到 {len(results)} 个任务")
            
            # 显示优先级分布统计
            stats = data['data']['stats']
            print("   优先级分布:")
            for priority, info in stats['priority_distribution'].items():
                print(f"     {priority}: {info['count']} 个 ({info['percentage']}%)")
        else:
            print(f"❌ 优先级过滤失败: {response.text}")
    
    def test_time_range_filter(self):
        """测试时间范围过滤"""
        print("\n📅 测试时间范围过滤...")
        
        # 测试截止时间过滤
        today = timezone.now().date()
        future_date = today + timedelta(days=7)
        
        response = requests.get(
            f"{self.base_url}/tasks/search/",
            params={
                'due_after': today.isoformat(),
                'due_before': future_date.isoformat()
            },
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data['data']['results']
            print(f"✅ 截止时间过滤 (未来7天内): 找到 {len(results)} 个任务")
            for task in results:
                print(f"   - {task['title']} (截止: {task['due_date']})")
        else:
            print(f"❌ 截止时间过滤失败: {response.text}")
        
        # 测试逾期任务
        response = requests.get(
            f"{self.base_url}/tasks/search/",
            params={'is_overdue': 'true'},
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data['data']['results']
            print(f"✅ 逾期任务过滤: 找到 {len(results)} 个任务")
            for task in results:
                print(f"   - {task['title']} (截止: {task['due_date']})")
        else:
            print(f"❌ 逾期任务过滤失败: {response.text}")
        
        # 测试即将到期任务
        response = requests.get(
            f"{self.base_url}/tasks/search/",
            params={'due_soon': '5'},
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data['data']['results']
            print(f"✅ 即将到期任务 (5天内): 找到 {len(results)} 个任务")
        else:
            print(f"❌ 即将到期任务过滤失败: {response.text}")
    
    def test_progress_filter(self):
        """测试进度过滤"""
        print("\n📈 测试进度过滤...")
        
        # 测试进度范围过滤
        response = requests.get(
            f"{self.base_url}/tasks/search/",
            params={'progress_min': '50', 'progress_max': '90'},
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data['data']['results']
            print(f"✅ 进度过滤 (50%-90%): 找到 {len(results)} 个任务")
            for task in results:
                print(f"   - {task['title']} (进度: {task['progress']}%)")
        else:
            print(f"❌ 进度过滤失败: {response.text}")
    
    def test_tags_category_filter(self):
        """测试标签和分类过滤"""
        print("\n🏷️ 测试标签和分类过滤...")
        
        # 测试标签过滤
        response = requests.get(
            f"{self.base_url}/tasks/search/",
            params={'tags': 'API,前端'},
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data['data']['results']
            print(f"✅ 标签过滤 (API,前端): 找到 {len(results)} 个任务")
            for task in results:
                tags = task.get('tags_list', task.get('tags', []))
                if isinstance(tags, list):
                    tags_str = ', '.join(tags) if tags else '无标签'
                else:
                    tags_str = str(tags) if tags else '无标签'
                print(f"   - {task['title']} (标签: {tags_str})")
        else:
            print(f"❌ 标签过滤失败: {response.text}")
        
        # 测试分类过滤
        response = requests.get(
            f"{self.base_url}/tasks/search/",
            params={'category': '开发'},
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data['data']['results']
            print(f"✅ 分类过滤 '开发': 找到 {len(results)} 个任务")
            for task in results:
                print(f"   - {task['title']} (分类: {task.get('category', '无分类')})")
        else:
            print(f"❌ 分类过滤失败: {response.text}")
    
    def test_sorting_pagination(self):
        """测试排序和分页"""
        print("\n📄 测试排序和分页...")
        
        # 测试排序
        response = requests.get(
            f"{self.base_url}/tasks/search/",
            params={'sort': 'priority', 'order': 'desc'},
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data['data']['results']
            print(f"✅ 按优先级降序排序: 找到 {len(results)} 个任务")
            for task in results[:3]:  # 显示前3个
                print(f"   - {task['title']} (优先级: {task['priority']})")
        else:
            print(f"❌ 排序失败: {response.text}")
        
        # 测试分页
        response = requests.get(
            f"{self.base_url}/tasks/search/",
            params={'page': '1', 'page_size': '3'},
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            pagination = data['data']['pagination']
            print(f"✅ 分页测试: 第{pagination['current_page']}页, 共{pagination['total_pages']}页")
            print(f"   总计 {pagination['total_count']} 个任务, 每页 {pagination['page_size']} 个")
            print(f"   有下一页: {pagination['has_next']}, 有上一页: {pagination['has_previous']}")
        else:
            print(f"❌ 分页失败: {response.text}")
    
    def test_complex_search(self):
        """测试复合搜索"""
        print("\n🔍 测试复合搜索...")
        
        # 复合搜索：开发类别 + 高优先级 + 进行中状态
        response = requests.get(
            f"{self.base_url}/tasks/search/",
            params={
                'category': '开发',
                'priority': 'HIGH,URGENT',
                'status': 'IN_PROGRESS',
                'sort': 'due_date',
                'order': 'asc'
            },
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data['data']['results']
            search_params = data['data']['search_params']
            print(f"✅ 复合搜索: 找到 {len(results)} 个任务")
            print(f"   搜索条件: {search_params}")
            for task in results:
                print(f"   - {task['title']} ({task['priority']}, {task['status']})")
        else:
            print(f"❌ 复合搜索失败: {response.text}")
    
    def test_search_statistics(self):
        """测试搜索统计功能"""
        print("\n📊 测试搜索统计功能...")
        
        response = requests.get(
            f"{self.base_url}/tasks/search/",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            stats = data['data']['stats']
            
            print(f"✅ 搜索统计:")
            print(f"   总任务数: {stats['total_found']}")
            print(f"   搜索时间: {stats['search_time']}")
            
            print("\n   状态分布:")
            for status, info in stats['status_distribution'].items():
                print(f"     {status}: {info['count']} 个 ({info['percentage']}%)")
            
            print("\n   优先级分布:")
            for priority, info in stats['priority_distribution'].items():
                print(f"     {priority}: {info['count']} 个 ({info['percentage']}%)")
        else:
            print(f"❌ 搜索统计失败: {response.text}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始任务搜索和过滤API测试...")
        
        # 设置测试数据
        self.setup_test_data()
        
        # 登录
        if not self.login():
            print("❌ 无法登录，测试终止")
            return
        
        # 运行各项测试
        self.test_basic_search()
        self.test_status_priority_filter()
        self.test_time_range_filter()
        self.test_progress_filter()
        self.test_tags_category_filter()
        self.test_sorting_pagination()
        self.test_complex_search()
        self.test_search_statistics()
        
        print("\n✅ 任务搜索和过滤API测试完成！")
        print("\n📊 测试摘要:")
        print("- 基础搜索: ✅ 已测试")
        print("- 状态优先级过滤: ✅ 已测试")
        print("- 时间范围过滤: ✅ 已测试")
        print("- 进度过滤: ✅ 已测试")
        print("- 标签分类过滤: ✅ 已测试")
        print("- 排序分页: ✅ 已测试")
        print("- 复合搜索: ✅ 已测试")
        print("- 搜索统计: ✅ 已测试")

def main():
    tester = TaskSearchAPITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()

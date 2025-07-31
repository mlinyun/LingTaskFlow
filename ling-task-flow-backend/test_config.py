"""
测试配置文件

定义测试运行的配置选项和通用设置
"""
import os

# 测试数据库配置
TEST_DATABASE = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:',  # 使用内存数据库加速测试
}

# 测试API服务器配置
TEST_SERVER_HOST = 'localhost'
TEST_SERVER_PORT = 8000
TEST_API_BASE_URL = f"http://{TEST_SERVER_HOST}:{TEST_SERVER_PORT}/api"

# 测试用户配置
TEST_USERS = {
    'regular': {
        'username': 'testuser_regular',
        'email': 'regular@test.com',
        'password': 'TestPass123!'
    },
    'admin': {
        'username': 'testuser_admin',
        'email': 'admin@test.com',
        'password': 'AdminPass123!',
        'is_staff': True
    },
    'superuser': {
        'username': 'testuser_super',
        'email': 'super@test.com',
        'password': 'SuperPass123!',
        'is_superuser': True
    }
}

# 测试超时配置
REQUEST_TIMEOUT = 10  # 秒
TEST_RETRY_COUNT = 3

# 测试日志配置
ENABLE_TEST_LOGGING = True
LOG_LEVEL = 'INFO'

# 测试文件路径
TESTS_ROOT = os.path.dirname(os.path.abspath(__file__))
TESTS_DATA_DIR = os.path.join(TESTS_ROOT, 'tests', 'data')
TESTS_FIXTURES_DIR = os.path.join(TESTS_ROOT, 'tests', 'fixtures')

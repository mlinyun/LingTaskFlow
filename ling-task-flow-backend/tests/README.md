# LingTaskFlow 测试文档

## 📁 测试结构

```
tests/
├── __init__.py                 # 测试包初始化
├── auth/                       # 认证系统测试
│   ├── __init__.py
│   ├── test_register_api.py    # 用户注册API测试
│   ├── test_login_api.py       # 用户登录API测试
│   ├── test_token_refresh.py   # Token刷新测试
│   ├── test_account_lockout.py # 账户锁定测试
│   ├── test_middleware.py      # 中间件测试
│   ├── test_models.py          # 认证模型测试
│   ├── test_serializers.py     # 序列化器测试
│   ├── test_utils.py           # 认证工具测试
│   ├── test_views.py           # 视图测试
│   └── verify_tests.py         # 测试验证脚本
├── permissions/                # 权限系统测试
│   ├── __init__.py
│   ├── test_permissions.py     # 权限类测试
│   ├── test_permissions_fixed.py # 修复版权限测试
│   └── test_all_permissions.py # 完整权限测试
├── models/                     # 数据模型测试
│   ├── __init__.py
│   └── test_userprofile.py     # UserProfile模型测试
└── utils/                      # 测试工具和辅助
    ├── __init__.py
    └── test_helpers.py         # 测试辅助函数
```

## 🚀 运行测试

### 使用测试运行器（推荐）

```bash
# 运行所有测试
python run_tests.py --all

# 运行特定模块测试
python run_tests.py --auth          # 认证相关测试
python run_tests.py --permissions   # 权限相关测试
python run_tests.py --models        # 模型相关测试

# 运行特定类型测试
python run_tests.py --unit          # Django单元测试
python run_tests.py --integration   # 集成测试
```

### 使用Django测试命令

```bash
# 运行所有Django单元测试
python manage.py test tests

# 运行特定模块测试
python manage.py test tests.auth
python manage.py test tests.permissions
python manage.py test tests.models

# 运行特定测试类
python manage.py test tests.auth.test_register_api
```

### 运行单个测试文件

```bash
# 认证测试
python tests/auth/test_register_api.py
python tests/auth/test_login_api.py
python tests/auth/test_token_refresh.py

# 权限测试
python tests/permissions/test_all_permissions.py
python tests/permissions/test_permissions_fixed.py

# 模型测试
python tests/models/test_userprofile.py
```

## 📊 测试类型说明

### 1. Django单元测试

- **位置**: 使用Django TestCase编写的测试
- **特点**: 使用测试数据库，事务回滚，快速执行
- **运行**: `python manage.py test tests`

### 2. 集成测试

- **位置**: 直接执行的Python脚本
- **特点**: 测试完整的API流程，需要运行开发服务器
- **运行**: `python run_tests.py --integration`

### 3. API测试

- **位置**: `tests/auth/` 中的API测试文件
- **特点**: 测试HTTP接口，包括请求/响应验证
- **要求**: 需要启动Django开发服务器

### 4. 权限测试

- **位置**: `tests/permissions/` 中的权限测试文件
- **特点**: 测试访问控制和权限验证逻辑
- **独立**: 不需要HTTP服务器，直接测试权限类

## 🔧 测试工具

### BaseTestCase

提供常用的测试基类和工具方法：

```python
from tests.utils.test_helpers import BaseTestCase

class MyModelTest(BaseTestCase):
    def test_something(self):
        user = self.create_user('testuser')
        # ... 测试逻辑
```

### BaseAPITestCase

提供API测试基类：

```python
from tests.utils.test_helpers import BaseAPITestCase

class MyAPITest(BaseAPITestCase):
    def test_api_endpoint(self):
        self.authenticate_user(self.test_users['regular'])
        response = self.client.get('/api/endpoint/')
        # ... 断言逻辑
```

### MockUser 和 MockRequest

用于权限测试的模拟对象：

```python
from tests.utils.test_helpers import MockUser, MockRequest

def test_permission():
    user = MockUser('testuser', is_staff=True)
    request = MockRequest(user, 'POST')
    # ... 权限测试逻辑
```

## 📝 测试编写规范

### 1. 测试文件命名

- 测试文件以 `test_` 开头
- 测试类以 `Test` 开头
- 测试方法以 `test_` 开头

### 2. 测试组织

- 按功能模块组织测试文件
- 每个测试类专注测试一个功能点
- 使用描述性的测试方法名

### 3. 测试数据

- 使用 `setUpTestData()` 创建共享测试数据
- 使用 `setUp()` 创建每个测试独有的数据
- 测试数据要清晰、最小化

### 4. 断言

- 使用明确的断言消息
- 一个测试方法专注测试一个功能点
- 测试正常情况和异常情况

### 5. 测试清理

- Django测试自动回滚数据库事务
- 集成测试需要手动清理创建的数据
- 不要在测试间共享可变状态

## 🐛 调试测试

### 1. 查看详细输出

```bash
python manage.py test tests --verbosity=2
```

### 2. 运行单个测试

```bash
python manage.py test tests.auth.test_register_api.TestRegisterAPI.test_successful_registration
```

### 3. 保留测试数据库

```bash
python manage.py test tests --keepdb
```

### 4. 使用调试器

在测试代码中添加：

```python
import pdb; pdb.set_trace()
```

## 📈 测试覆盖率

目前测试覆盖的功能：

- ✅ 用户注册API (1.2.2)
- ✅ 用户登录API (1.2.3)
- ✅ Token刷新API (1.2.4)
- ✅ 权限类系统 (1.2.5)
- ✅ UserProfile模型 (1.2.1)

待编写的测试：

- [ ] 认证系统完整单元测试 (1.2.6)
- [ ] Task模型测试 (1.3.5)
- [ ] 任务API集成测试 (2.3.1)

## 🔄 持续集成

测试运行器支持CI/CD集成：

```bash
# 在CI环境中运行所有测试
python run_tests.py --all

# 检查退出代码
echo $?  # 0表示成功，非0表示失败
```

---

**维护者**: GitHub Copilot  
**最后更新**: 2025年1月31日

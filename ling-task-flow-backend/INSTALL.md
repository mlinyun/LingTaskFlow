# LingTaskFlow 后端环境安装指南

## 📋 环境要求

- **Python**: 3.11+ (推荐 3.11 或 3.12)
- **操作系统**: Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+)
- **内存**: 最低 4GB RAM (推荐 8GB+)
- **磁盘空间**: 至少 2GB 可用空间

## 🚀 快速安装

### 1. 创建虚拟环境

#### 使用 Conda (推荐)
```bash
# 创建环境
conda create -n ling-task-flow-backend python=3.12

# 激活环境
conda activate ling-task-flow-backend
```

#### 使用 venv
```bash
# 创建环境
python -m venv ling-task-flow-backend

# 激活环境 (Windows)
ling-task-flow-backend\Scripts\activate

# 激活环境 (macOS/Linux)
source ling-task-flow-backend/bin/activate
```

### 2. 安装依赖

#### 开发环境安装 (包含所有工具)
```bash
pip install -r requirements-dev.txt
```

#### 生产环境安装 (仅核心依赖)
```bash
pip install -r requirements-production.txt
```

#### 完整安装 (所有功能)
```bash
pip install -r requirements.txt
```

### 3. 数据库迁移
```bash
# 创建迁移文件
python manage.py makemigrations

# 应用迁移
python manage.py migrate

# 创建超级用户 (可选)
python manage.py createsuperuser
```

### 4. 启动开发服务器
```bash
python manage.py runserver
```

服务器将在 `http://localhost:8000` 启动

## 📦 依赖文件说明

### requirements.txt
- **用途**: 完整功能安装，包含所有可选组件
- **场景**: 功能测试、完整开发环境
- **包含**: 核心功能 + 开发工具 + 可选组件

### requirements-production.txt
- **用途**: 生产环境部署
- **场景**: 正式部署、Docker容器
- **包含**: 仅运行时必需的核心依赖

### requirements-dev.txt
- **用途**: 开发环境专用
- **场景**: 日常开发、代码调试
- **包含**: 生产依赖 + 开发工具 + 测试框架

## 🛠️ 可选组件安装

### Redis 缓存 (推荐生产环境)
```bash
# 安装Redis (Windows)
# 下载Redis for Windows或使用WSL

# 安装Redis (macOS)
brew install redis

# 安装Redis (Ubuntu)
sudo apt-get install redis-server

# Python Redis客户端已包含在requirements.txt中
```

### PostgreSQL 数据库 (生产环境)
```bash
# 安装PostgreSQL (Windows)
# 下载官方安装程序

# 安装PostgreSQL (macOS)
brew install postgresql

# 安装PostgreSQL (Ubuntu)
sudo apt-get install postgresql postgresql-contrib

# psycopg2已包含在requirements.txt中
```

## 🧪 验证安装

### 运行测试套件
```bash
# 运行所有测试
python manage.py test

# 运行集成测试
python run_api_tests.py

# 运行特定测试
python manage.py test tests.integration.test_task_api_integration
```

### 检查项目状态
```bash
# Django系统检查
python manage.py check

# 检查数据库连接
python manage.py dbshell

# 查看已安装的包
pip list
```

## 🔧 常见问题解决

### 1. 安装失败
```bash
# 升级pip
pip install --upgrade pip

# 清理缓存
pip cache purge

# 重新安装
pip install -r requirements.txt --force-reinstall
```

### 2. 数据库问题
```bash
# 重置数据库 (开发环境)
rm db.sqlite3
python manage.py migrate

# 重新创建迁移
rm -rf LingTaskFlow/migrations/00*.py
python manage.py makemigrations LingTaskFlow
python manage.py migrate
```

### 3. 端口占用
```bash
# 使用其他端口启动
python manage.py runserver 8001

# 查看端口使用情况 (Windows)
netstat -ano | findstr :8000

# 查看端口使用情况 (macOS/Linux)
lsof -i :8000
```

## 🌟 开发工具配置

### IDE 推荐设置
```json
// VS Code settings.json
{
    "python.defaultInterpreterPath": "./ling-task-flow-backend/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black"
}
```

### 代码质量检查
```bash
# 代码格式化
black .

# 导入排序
isort .

# 代码风格检查
flake8 .

# 运行所有质量检查
black . && isort . && flake8 .
```

## 📚 更多信息

- **项目文档**: `/docs/`
- **API文档**: `http://localhost:8000/swagger/` (安装drf-yasg后)
- **管理后台**: `http://localhost:8000/admin/`
- **健康检查**: `http://localhost:8000/api/health/`

## 🆘 获取帮助

如果遇到问题，请检查：
1. Python版本是否符合要求
2. 虚拟环境是否正确激活
3. 所有依赖是否成功安装
4. 数据库迁移是否完成

---

*更新日期: 2025年8月2日*  
*维护者: LingTaskFlow开发团队*

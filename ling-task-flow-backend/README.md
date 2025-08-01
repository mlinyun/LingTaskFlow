# 🚀 LingTaskFlow 后端 API

LingTaskFlow 任务管理系统的 Django REST API 后端实现。

## 📁 项目结构

```
ling-task-flow-backend/
├── 📁 LingTaskFlow/              # Django 主应用
├── 📁 ling_task_flow_backend/    # 项目配置
├── 📁 templates/                 # 模板文件
├── 📁 tests/                     # 测试框架
├──  manage.py                  # Django 管理工具
├── 📄 run_api_tests.py          # API 测试运行脚本
└── 📄 db.sqlite3               # SQLite 数据库
```

## 🎯 项目状态

**✅ 开发完成** | **🧪 测试通过** | **🚀 生产就绪**

- **API测试覆盖率**: 100% (18/18 测试通过)
- **性能基准**: 所有操作 < 20ms
- **安全验证**: 认证 + 权限 + 注入防护
- **代码质量**: 干净整洁，模块化设计

## 📊 查看报告

详细的项目报告和测试结果请查看项目根目录的 **[../report/](../report/)** 目录：

- 📄 [项目总结报告](../report/PROJECT_SUMMARY.md)
- ✅ [测试成功报告](../report/SUCCESS_REPORT.md)

## 🛠️ 快速开始

### 环境安装
详细安装说明请参考 **[INSTALL.md](INSTALL.md)**

```bash
# 1. 创建并激活虚拟环境
conda create -n ling-task-flow-backend python=3.11
conda activate ling-task-flow-backend

# 2. 安装依赖
pip install -r requirements-dev.txt  # 开发环境
# 或
pip install -r requirements-production.txt  # 生产环境

# 3. 数据库迁移
python manage.py migrate

# 4. 启动服务器
python manage.py runserver
```

### 运行 API 测试
```bash
python run_api_tests.py
```

### 运行完整测试套件
```bash
python manage.py test tests.integration.test_task_api_integration
```

## 📦 依赖管理

项目提供了三个不同的requirements文件：

- **requirements.txt** - 完整功能安装 (包含所有可选组件)
- **requirements-production.txt** - 生产环境部署 (仅核心依赖)
- **requirements-dev.txt** - 开发环境专用 (包含开发工具)

---

*开发框架: Django 5.2 + Django REST Framework*  
*数据库: SQLite (开发环境)*  
*测试状态: 100% 通过*

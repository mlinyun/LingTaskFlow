# 凌云智能任务管理平台 | LingTaskFlow

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/yourusername/LingTaskFlow)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/yourusername/LingTaskFlow/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.2-green.svg)](https://www.djangoproject.com/)
[![Vue.js](https://img.shields.io/badge/vue.js-3.0-green.svg)](https://vuejs.org/)

[English](README_EN.md) | [中文](README.md)

## 📋 项目简介

凌云智能任务管理平台（LingTaskFlow）是一个基于Django 5.2和Vue 3构建的现代化全栈任务管理系统。它提供直观的界面来管理任务、项目和团队协作，具备实时更新和全面的工作流管理功能。

该系统结合了Django后端架构的稳健性和Vue 3前端框架的响应性，为任务组织、优先级管理和团队生产力提升提供无缝的用户体验。

## ✨ 主要特性

- **🚀 现代技术栈**: 基于Django 5.2、Vue 3、Quasar框架和TypeScript构建
- **📱 响应式设计**: 移动优先的跨平台兼容设计
- **⚡ 实时更新**: 所有连接客户端的实时任务状态同步
- **🔐 安全认证**: 基于JWT的身份验证和基于角色的访问控制
- **📊 高级分析**: 全面的报告和任务完成统计
- **⌨️ 键盘快捷键**: 可自定义热键系统的高效工作流
- **🎯 智能筛选**: 任务管理的高级搜索和筛选功能

## 🛠️ 安装指南

### 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn
- PostgreSQL（推荐）或 SQLite

### 后端设置

```bash
# 克隆仓库
git clone https://github.com/yourusername/LingTaskFlow.git
cd LingTaskFlow

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装Python依赖
pip install -r requirements.txt

# 数据库设置
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动Django开发服务器
python manage.py runserver
```

### 前端设置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 💡 使用示例

### 基础任务管理

```python
# 通过API创建新任务
import requests

task_data = {
    "title": "完成项目文档",
    "description": "编写全面的README和API文档",
    "priority": "high",
    "due_date": "2025-08-15",
    "assigned_to": 1
}

response = requests.post(
    "http://localhost:8000/api/tasks/",
    json=task_data,
    headers={"Authorization": "Bearer YOUR_JWT_TOKEN"}
)
```

### 前端组件使用

```vue
<template>
  <TaskCard 
    :task="task" 
    @update="handleTaskUpdate"
    @delete="handleTaskDelete"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import TaskCard from '@/components/TaskCard.vue'

const task = ref({
  id: 1,
  title: '示例任务',
  status: 'in_progress',
  priority: 'medium'
})

const handleTaskUpdate = (updatedTask: Task) => {
  // 处理任务更新逻辑
}
</script>
```

### 键盘快捷键

- `Ctrl + N`: 创建新任务
- `Ctrl + S`: 保存当前任务
- `Ctrl + D`: 删除选中任务
- `Ctrl + F`: 打开搜索/筛选面板
- `Esc`: 关闭模态框/面板

## 🤝 贡献指南

我们欢迎对凌云智能任务管理平台的贡献！请遵循以下指南：

1. **Fork仓库**并创建功能分支
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **进行更改**并在适用时添加测试

3. **提交更改**并使用描述性消息
   ```bash
   git commit -m "为任务自动化添加惊人功能"
   ```

4. **推送到分支**并创建Pull Request
   ```bash
   git push origin feature/amazing-feature
   ```

### 开发指南

- Python代码遵循PEP 8规范
- 前端开发使用TypeScript
- 为新功能编写单元测试
- 更新API变更的文档
- 提交PR前确保所有测试通过

## 📄 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件。

## 🙏 致谢

- Django社区提供的强大后端框架
- Vue.js团队提供的响应式前端框架
- Quasar框架提供的美观UI组件
- 所有帮助改进此项目的贡献者

## 📞 联系方式

- **Issues**: [GitHub Issues](https://github.com/yourusername/LingTaskFlow/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/LingTaskFlow/discussions)
- **Email**: your.email@example.com

## 🗺️ 路线图

- [ ] 拖拽排序功能
- [ ] 移动端应用
- [ ] 第三方集成（Slack, Teams等）
- [ ] 高级报告和分析
- [ ] 多语言支持扩展

---

**⭐ 如果这个项目对你有帮助，请给我们一个星标！**
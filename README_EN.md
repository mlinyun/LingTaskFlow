# LingTaskFlow | Intelligent Task Management Platform

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/yourusername/LingTaskFlow)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/yourusername/LingTaskFlow/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.2-green.svg)](https://www.djangoproject.com/)
[![Vue.js](https://img.shields.io/badge/vue.js-3.0-green.svg)](https://vuejs.org/)

[English](README_EN.md) | [中文](README.md)

## 📋 Project Overview

LingTaskFlow (Intelligent Task Management Platform) is a modern, full-stack task management system built with Django 5.2
and Vue 3. It provides an intuitive interface for managing tasks, projects, and team collaboration with real-time
updates and comprehensive workflow management capabilities.

The system combines the robustness of Django's backend architecture with the reactivity of Vue 3's frontend framework,
delivering a seamless user experience for task organization, priority management, and team productivity enhancement.

## ✨ Key Features

- **🚀 Modern Tech Stack**: Built with Django 5.2, Vue 3, Quasar Framework, and TypeScript
- **📱 Responsive Design**: Mobile-first approach with cross-platform compatibility
- **⚡ Real-time Updates**: Live task status synchronization across all connected clients
- **🔐 Secure Authentication**: JWT-based authentication with role-based access control
- **📊 Advanced Analytics**: Comprehensive reporting and task completion statistics
- **⌨️ Keyboard Shortcuts**: Efficient workflow with customizable hotkey system
- **🎯 Smart Filtering**: Advanced search and filtering capabilities for task management

## 🛠️ Installation Guide

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- PostgreSQL (recommended) or SQLite

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/mlinyun/LingTaskFlow.git
cd LingTaskFlow

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Database setup
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start Django development server
python manage.py runserver
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 💡 Usage Examples

### Basic Task Management

```python
# Create a new task via API
import requests

task_data = {
    "title": "Complete project documentation",
    "description": "Write comprehensive README and API docs",
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

### Frontend Component Usage

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
  title: 'Sample Task',
  status: 'in_progress',
  priority: 'medium'
})

const handleTaskUpdate = (updatedTask: Task) => {
  // Handle task update logic
}
</script>
```

### Keyboard Shortcuts

- `Ctrl + N`: Create new task
- `Ctrl + S`: Save current task
- `Ctrl + D`: Delete selected task
- `Ctrl + F`: Open search/filter panel
- `Esc`: Close modals/panels

## 🤝 Contributing

We welcome contributions to LingTaskFlow (Intelligent Task Management Platform)! Please follow these guidelines:

1. **Fork the repository** and create your feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make your changes** and add tests if applicable

3. **Commit your changes** with descriptive messages
   ```bash
   git commit -m "Add amazing feature for task automation"
   ```

4. **Push to your branch** and create a Pull Request
   ```bash
   git push origin feature/amazing-feature
   ```

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for frontend development
- Write unit tests for new features
- Update documentation for API changes
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django community for the robust backend framework
- Vue.js team for the reactive frontend framework
- Quasar Framework for the beautiful UI components
- All contributors who help improve this project

## 📞 Contact

- **Issues**: [GitHub Issues](https://github.com/mlinyun/LingTaskFlow/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mlinyun/LingTaskFlow/discussions)
- **Email**: your.email@example.com

## 🗺️ Roadmap

- [ ] Drag and drop sorting functionality
- [ ] Mobile application
- [ ] Third-party integrations (Slack, Teams, etc.)
- [ ] Advanced reporting and analytics
- [ ] Extended multi-language support

---

**⭐ If this project helps you, please give us a star!**
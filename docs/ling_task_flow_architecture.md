````markdown
# LingTaskFlow 架构设计文档

## 📋 文档信息

| 项目名称 | LingTaskFlow - 凌云任务管理应用 |
|---------|------------------------------|
| 文档版本 | v2.0 Professional |
| 创建日期 | 2025年1月31日 |
| 更新日期 | 2025年1月31日 |
| 文档作者 | GitHub Copilot |
| 项目状态 | 开发中 |

## 🎯 项目概述

### 产品愿景
构建一个高效、直观、安全的个人任务管理系统，帮助用户实现任务的全生命周期管理，提升个人工作效率。

### 核心价值主张
- **简洁高效**：极简设计，专注核心功能
- **数据安全**：用户数据完全隔离，本地化存储
- **响应迅速**：毫秒级响应，流畅用户体验
- **扩展性强**：模块化设计，便于功能扩展

### 技术栈选择

#### 后端技术栈
```
- 框架：Django 5.2 + Django REST Framework 3.14+
- 认证：django-rest-framework-simplejwt
- 数据库：SQLite (开发) / PostgreSQL (生产)
- 环境：Python 3.11+ (Conda环境)
- 部署：Gunicorn + Nginx
- 监控：Django Debug Toolbar (开发)
```

#### 前端技术栈
```
- 框架：Vue 3.4+ (Composition API)
- UI库：Quasar Framework 2.14+
- 增强组件：shadcn-vue
- 状态管理：Pinia 2.1+
- 路由：Vue Router 4.2+
- 构建工具：Vite 5.0+
- 语言：TypeScript 5.3+
- HTTP客户端：Axios 1.6+
```

---

## 📊 系统架构设计

### 整体架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │    Database     │
│   (Vue 3 SPA)   │◄──►│   (Django API)  │◄──►│   (SQLite/PG)   │
│   Port: 9000    │    │   Port: 8000    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                        │                        │
        ▼                        ▼                        ▼
  Quasar Components      JWT Authentication         ORM Models
  Pinia State Store      DRF Serializers           Database Indexes
  Vue Router             Permission Classes         Migration Scripts
```

### 数据流向
```
User Action → Vue Component → Pinia Store → Axios → Django View → 
DRF Serializer → Model → Database → Response → JSON → Frontend
```

---

## 🔐 认证与授权系统

### JWT Token 配置
```python
# settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
}
```

### 权限类设计
```python
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    自定义权限：只有对象的所有者可以修改
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
```

---

## 📋 数据模型设计

### 用户扩展模型
```python
# models.py
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    timezone = models.CharField(max_length=50, default='Asia/Shanghai')
    task_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_profiles'
```

### 任务模型
```python
class Task(models.Model):
    class Status(models.TextChoices):
        TODO = 'TODO', '待办'
        IN_PROGRESS = 'IN_PROGRESS', '进行中'
        COMPLETED = 'COMPLETED', '已完成'
        CANCELLED = 'CANCELLED', '已取消'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100, db_index=True)
    description = models.TextField(max_length=1000, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO, db_index=True)
    priority = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # 软删除相关
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 关联用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    
    class Meta:
        db_table = 'tasks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status', 'is_deleted']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['is_deleted', 'deleted_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    def soft_delete(self):
        """软删除方法"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])
    
    def restore(self):
        """恢复删除的任务"""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])
```

---

## 🔌 API 接口规范

### 基础响应格式
```json
{
  "success": true,
  "message": "操作成功",
  "data": {},
  "timestamp": "2025-01-31T10:30:00Z",
  "request_id": "req_123456789"
}
```

### 错误响应格式
```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "VALIDATION_ERROR",
  "errors": {
    "field_name": ["具体错误信息"]
  },
  "timestamp": "2025-01-31T10:30:00Z",
  "request_id": "req_123456789"
}
```

### 1. 认证相关API

#### 1.1 用户注册
```
POST /api/auth/register/
Content-Type: application/json

Request Body:
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "SecurePass123",
  "password_confirm": "SecurePass123"
}

Response (201):
{
  "success": true,
  "message": "注册成功",
  "data": {
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "date_joined": "2025-01-31T10:30:00Z"
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
  }
}
```

#### 1.2 用户登录
```
POST /api/auth/login/
Content-Type: application/json

Request Body:
{
  "username": "testuser",  // 支持用户名或邮箱
  "password": "SecurePass123"
}

Response (200):
{
  "success": true,
  "message": "登录成功",
  "data": {
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "last_login": "2025-01-31T10:30:00Z"
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
  }
}
```

#### 1.3 刷新Token
```
POST /api/auth/token/refresh/
Content-Type: application/json

Request Body:
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

Response (200):
{
  "success": true,
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

### 2. 任务管理API

#### 2.1 获取任务列表
```
GET /api/tasks/?page=1&page_size=20&status=TODO&search=关键词&ordering=-created_at
Authorization: Bearer {access_token}

Query Parameters:
- page: 页码 (默认: 1)
- page_size: 每页数量 (默认: 20, 最大: 100)
- status: 状态筛选 (可选, 多值用逗号分隔)
- search: 搜索关键词 (可选)
- ordering: 排序字段 (可选: created_at, updated_at, title, 加-表示倒序)
- include_deleted: 是否包含已删除任务 (默认: false)

Response (200):
{
  "success": true,
  "data": {
    "count": 100,
    "next": "http://localhost:8000/api/tasks/?page=2",
    "previous": null,
    "results": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "完成项目文档",
        "description": "编写用户手册和API文档",
        "status": "TODO",
        "priority": 3,
        "is_deleted": false,
        "created_at": "2025-01-31T10:30:00Z",
        "updated_at": "2025-01-31T10:30:00Z"
      }
    ]
  }
}
```

#### 2.2 创建任务
```
POST /api/tasks/
Authorization: Bearer {access_token}
Content-Type: application/json

Request Body:
{
  "title": "新任务标题",
  "description": "任务详细描述",
  "priority": 3
}

Response (201):
{
  "success": true,
  "message": "任务创建成功",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "新任务标题",
    "description": "任务详细描述",
    "status": "TODO",
    "priority": 3,
    "is_deleted": false,
    "created_at": "2025-01-31T10:30:00Z",
    "updated_at": "2025-01-31T10:30:00Z"
  }
}
```

#### 2.3 更新任务
```
PATCH /api/tasks/{task_id}/
Authorization: Bearer {access_token}
Content-Type: application/json

Request Body:
{
  "title": "更新后的标题",
  "status": "IN_PROGRESS",
  "priority": 4
}

Response (200):
{
  "success": true,
  "message": "任务更新成功",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "更新后的标题",
    "description": "任务详细描述",
    "status": "IN_PROGRESS",
    "priority": 4,
    "is_deleted": false,
    "created_at": "2025-01-31T10:30:00Z",
    "updated_at": "2025-01-31T11:15:00Z"
  }
}
```

#### 2.4 软删除任务
```
DELETE /api/tasks/{task_id}/
Authorization: Bearer {access_token}

Response (200):
{
  "success": true,
  "message": "任务已移入回收站",
  "data": {
    "deleted_at": "2025-01-31T11:20:00Z",
    "recovery_deadline": "2025-03-02T11:20:00Z"
  }
}
```

#### 2.5 恢复任务
```
POST /api/tasks/{task_id}/restore/
Authorization: Bearer {access_token}

Response (200):
{
  "success": true,
  "message": "任务恢复成功",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "恢复的任务",
    "status": "TODO",
    "is_deleted": false,
    "deleted_at": null
  }
}
```

#### 2.6 永久删除任务
```
DELETE /api/tasks/{task_id}/permanent/
Authorization: Bearer {access_token}

Response (204):
{
  "success": true,
  "message": "任务已永久删除"
}
```

### 3. 统计信息API

#### 3.1 获取任务统计
```
GET /api/tasks/stats/
Authorization: Bearer {access_token}

Response (200):
{
  "success": true,
  "data": {
    "total_tasks": 150,
    "active_tasks": 120,
    "deleted_tasks": 30,
    "status_breakdown": {
      "TODO": 45,
      "IN_PROGRESS": 30,
      "COMPLETED": 40,
      "CANCELLED": 5
    },
    "priority_breakdown": {
      "1": 20,
      "2": 35,
      "3": 40,
      "4": 20,
      "5": 5
    },
    "recent_activity": {
      "created_today": 5,
      "completed_today": 3,
      "created_this_week": 25,
      "completed_this_week": 18
    }
  }
}
```

---

## 🎨 前端组件设计

### 状态管理 (Pinia Store)

#### Task Store
```typescript
// stores/task.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Task, TaskFilters, PaginatedResponse } from '@/types'

export const useTaskStore = defineStore('task', () => {
  // State
  const tasks = ref<Task[]>([])
  const loading = ref(false)
  const filters = ref<TaskFilters>({
    page: 1,
    page_size: 20,
    status: [],
    search: '',
    ordering: '-created_at',
    include_deleted: false
  })
  const pagination = ref({
    count: 0,
    next: null,
    previous: null
  })

  // Getters
  const activeTasks = computed(() => 
    tasks.value.filter(task => !task.is_deleted)
  )
  
  const tasksByStatus = computed(() => {
    const grouped: Record<string, Task[]> = {}
    activeTasks.value.forEach(task => {
      if (!grouped[task.status]) grouped[task.status] = []
      grouped[task.status].push(task)
    })
    return grouped
  })

  // Actions
  async function fetchTasks() {
    loading.value = true
    try {
      const response = await taskApi.getTasks(filters.value)
      tasks.value = response.data.results
      pagination.value = {
        count: response.data.count,
        next: response.data.next,
        previous: response.data.previous
      }
    } catch (error) {
      console.error('Failed to fetch tasks:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function createTask(taskData: Partial<Task>) {
    try {
      const response = await taskApi.createTask(taskData)
      tasks.value.unshift(response.data)
      return response.data
    } catch (error) {
      console.error('Failed to create task:', error)
      throw error
    }
  }

  async function updateTask(taskId: string, updates: Partial<Task>) {
    try {
      const response = await taskApi.updateTask(taskId, updates)
      const index = tasks.value.findIndex(t => t.id === taskId)
      if (index !== -1) {
        tasks.value[index] = response.data
      }
      return response.data
    } catch (error) {
      console.error('Failed to update task:', error)
      throw error
    }
  }

  async function deleteTask(taskId: string) {
    try {
      await taskApi.deleteTask(taskId)
      const task = tasks.value.find(t => t.id === taskId)
      if (task) {
        task.is_deleted = true
        task.deleted_at = new Date().toISOString()
      }
    } catch (error) {
      console.error('Failed to delete task:', error)
      throw error
    }
  }

  return {
    // State
    tasks,
    loading,
    filters,
    pagination,
    // Getters
    activeTasks,
    tasksByStatus,
    // Actions
    fetchTasks,
    createTask,
    updateTask,
    deleteTask
  }
})
```

### 主要组件结构

#### TaskList.vue
```vue
<template>
  <div class="task-list">
    <TaskFilters 
      v-model:filters="taskStore.filters"
      @filter-change="handleFilterChange"
    />
    
    <div v-if="taskStore.loading" class="loading">
      <q-spinner size="50px" />
    </div>
    
    <div v-else-if="taskStore.activeTasks.length === 0" class="empty-state">
      <EmptyState 
        icon="task_alt"
        title="暂无任务"
        description="点击右下角按钮创建您的第一个任务"
      />
    </div>
    
    <div v-else class="task-grid">
      <TaskCard
        v-for="task in taskStore.activeTasks"
        :key="task.id"
        :task="task"
        @edit="handleEditTask"
        @delete="handleDeleteTask"
        @status-change="handleStatusChange"
      />
    </div>
    
    <q-pagination
      v-if="taskStore.pagination.count > taskStore.filters.page_size"
      v-model="taskStore.filters.page"
      :max="Math.ceil(taskStore.pagination.count / taskStore.filters.page_size)"
      @update:model-value="handlePageChange"
    />
    
    <q-page-sticky position="bottom-right" :offset="[18, 18]">
      <q-btn
        fab
        icon="add"
        color="primary"
        @click="showCreateDialog = true"
      />
    </q-page-sticky>
    
    <TaskCreateDialog
      v-model="showCreateDialog"
      @created="handleTaskCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useTaskStore } from '@/stores/task'
import TaskFilters from '@/components/TaskFilters.vue'
import TaskCard from '@/components/TaskCard.vue'
import TaskCreateDialog from '@/components/TaskCreateDialog.vue'
import EmptyState from '@/components/EmptyState.vue'

const taskStore = useTaskStore()
const showCreateDialog = ref(false)

onMounted(() => {
  taskStore.fetchTasks()
})

const handleFilterChange = () => {
  taskStore.filters.page = 1
  taskStore.fetchTasks()
}

const handlePageChange = () => {
  taskStore.fetchTasks()
}

const handleEditTask = (task: Task) => {
  // 打开编辑对话框
}

const handleDeleteTask = async (taskId: string) => {
  try {
    await taskStore.deleteTask(taskId)
    $q.notify({
      type: 'positive',
      message: '任务已移入回收站',
      position: 'top'
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: '删除失败，请重试',
      position: 'top'
    })
  }
}

const handleStatusChange = async (taskId: string, newStatus: string) => {
  try {
    await taskStore.updateTask(taskId, { status: newStatus })
    $q.notify({
      type: 'positive',
      message: '状态更新成功',
      position: 'top'
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: '状态更新失败',
      position: 'top'
    })
  }
}

const handleTaskCreated = (task: Task) => {
  showCreateDialog.value = false
  $q.notify({
    type: 'positive',
    message: '任务创建成功',
    position: 'top'
  })
}
</script>
```

---

## 🔍 错误处理与状态码

### HTTP状态码定义

| 状态码 | 含义 | 使用场景 |
|--------|------|----------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 204 | No Content | 删除成功，无返回内容 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 认证失败 |
| 403 | Forbidden | 权限不足 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突 |
| 422 | Unprocessable Entity | 数据验证失败 |
| 429 | Too Many Requests | 请求过于频繁 |
| 500 | Internal Server Error | 服务器内部错误 |

### 业务错误码定义

```python
# constants.py
class ErrorCodes:
    # 认证相关 (1xxx)
    INVALID_CREDENTIALS = 1001
    USER_ALREADY_EXISTS = 1002
    WEAK_PASSWORD = 1003
    ACCOUNT_LOCKED = 1004
    
    # 任务相关 (2xxx)
    TASK_NOT_FOUND = 2001
    TASK_LIMIT_EXCEEDED = 2002
    INVALID_STATUS_TRANSITION = 2003
    TASK_ALREADY_DELETED = 2004
    TASK_RECOVERY_EXPIRED = 2005
    
    # 权限相关 (3xxx)
    PERMISSION_DENIED = 3001
    RESOURCE_NOT_OWNED = 3002
    
    # 系统相关 (9xxx)
    SYSTEM_MAINTENANCE = 9001
    RATE_LIMIT_EXCEEDED = 9002
```

### 异常处理器
```python
# exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
import uuid
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """自定义异常处理器"""
    response = exception_handler(exc, context)
    request_id = str(uuid.uuid4())
    
    if response is not None:
        custom_response_data = {
            'success': False,
            'message': get_error_message(exc),
            'error_code': get_error_code(exc),
            'errors': response.data if isinstance(response.data, dict) else {},
            'timestamp': timezone.now().isoformat(),
            'request_id': request_id
        }
        
        # 记录错误日志
        logger.error(
            f"API Error - Request ID: {request_id}, "
            f"Exception: {str(exc)}, "
            f"Context: {context}"
        )
        
        response.data = custom_response_data
    
    return response
```

---

## 📈 性能优化策略

### 数据库优化

#### 索引策略
```python
# 在模型中添加的索引
class Task(models.Model):
    # ...existing fields...
    
    class Meta:
        indexes = [
            # 复合索引：用户+状态+删除标记（最常用的查询组合）
            models.Index(fields=['user', 'status', 'is_deleted']),
            # 用户+创建时间（用于排序）
            models.Index(fields=['user', 'created_at']),
            # 软删除清理（定时任务使用）
            models.Index(fields=['is_deleted', 'deleted_at']),
            # 全文搜索（如果使用PostgreSQL）
            models.Index(fields=['title', 'description']) if 'postgresql' in settings.DATABASES['default']['ENGINE'] else None
        ]
```

#### 查询优化
```python
# views.py - 优化的查询集
class TaskViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user)
        
        # 根据include_deleted参数过滤
        include_deleted = self.request.query_params.get('include_deleted', 'false').lower() == 'true'
        if not include_deleted:
            queryset = queryset.filter(is_deleted=False)
        
        # 预加载相关对象（如果有外键关系）
        queryset = queryset.select_related('user')
        
        # 只查询需要的字段（如果是列表视图）
        if self.action == 'list':
            queryset = queryset.only(
                'id', 'title', 'status', 'priority', 
                'created_at', 'updated_at', 'is_deleted'
            )
        
        return queryset
```

### 前端优化

#### 虚拟滚动（大量数据）
```vue
<!-- TaskList.vue 大数据量优化版本 -->
<template>
  <q-virtual-scroll
    :items="taskStore.activeTasks"
    separator
    v-slot="{ item, index }"
    style="max-height: 70vh"
  >
    <TaskCard
      :key="item.id"
      :task="item"
      @edit="handleEditTask"
      @delete="handleDeleteTask"
    />
  </q-virtual-scroll>
</template>
```

#### 请求缓存策略
```typescript
// api/task.ts
import { AxiosResponse } from 'axios'

interface CacheConfig {
  ttl: number // 缓存时间（毫秒）
  key: string
}

class TaskAPI {
  private cache = new Map<string, { data: any; timestamp: number; ttl: number }>()
  
  async getTasks(filters: TaskFilters, cacheConfig?: CacheConfig): Promise<AxiosResponse> {
    const cacheKey = cacheConfig?.key || `tasks-${JSON.stringify(filters)}`
    
    // 检查缓存
    if (cacheConfig) {
      const cached = this.cache.get(cacheKey)
      if (cached && Date.now() - cached.timestamp < cached.ttl) {
        return { data: cached.data } as AxiosResponse
      }
    }
    
    const response = await api.get('/tasks/', { params: filters })
    
    // 更新缓存
    if (cacheConfig) {
      this.cache.set(cacheKey, {
        data: response.data,
        timestamp: Date.now(),
        ttl: cacheConfig.ttl
      })
    }
    
    return response
  }
  
  // 清除相关缓存
  invalidateCache(pattern: string) {
    for (const key of this.cache.keys()) {
      if (key.includes(pattern)) {
        this.cache.delete(key)
      }
    }
  }
}
```

---

## 🧪 测试策略

### 后端测试

#### 单元测试
```python
# tests/test_models.py
from django.test import TestCase
from django.contrib.auth.models import User
from LingTaskFlow.models import Task

class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_task_creation(self):
        """测试任务创建"""
        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            user=self.user
        )
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.status, 'TODO')
        self.assertEqual(task.user, self.user)
        self.assertFalse(task.is_deleted)
    
    def test_soft_delete(self):
        """测试软删除功能"""
        task = Task.objects.create(
            title='Test Task',
            user=self.user
        )
        task.soft_delete()
        
        self.assertTrue(task.is_deleted)
        self.assertIsNotNone(task.deleted_at)
        
        # 测试软删除的任务不在默认查询中
        active_tasks = Task.objects.filter(is_deleted=False)
        self.assertNotIn(task, active_tasks)
```

#### API测试
```python
# tests/test_api.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class TaskAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_create_task(self):
        """测试创建任务API"""
        data = {
            'title': 'New Task',
            'description': 'Task description',
            'priority': 3
        }
        response = self.client.post('/api/tasks/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['data']['title'], 'New Task')
    
    def test_list_tasks_pagination(self):
        """测试任务列表分页"""
        # 创建多个任务
        for i in range(25):
            Task.objects.create(
                title=f'Task {i}',
                user=self.user
            )
        
        response = self.client.get('/api/tasks/?page=1&page_size=20')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 20)
        self.assertIsNotNone(response.data['data']['next'])
```

### 前端测试

#### 组件测试
```typescript
// tests/TaskCard.test.ts
import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import TaskCard from '@/components/TaskCard.vue'
import { Quasar } from 'quasar'

describe('TaskCard', () => {
  const mockTask = {
    id: '1',
    title: 'Test Task',
    description: 'Test Description',
    status: 'TODO',
    priority: 3,
    created_at: '2025-01-31T10:30:00Z',
    updated_at: '2025-01-31T10:30:00Z',
    is_deleted: false
  }

  it('renders task information correctly', () => {
    const wrapper = mount(TaskCard, {
      props: { task: mockTask },
      global: {
        plugins: [Quasar]
      }
    })

    expect(wrapper.text()).toContain('Test Task')
    expect(wrapper.text()).toContain('Test Description')
  })

  it('emits edit event when edit button is clicked', async () => {
    const wrapper = mount(TaskCard, {
      props: { task: mockTask },
      global: {
        plugins: [Quasar]
      }
    })

    await wrapper.find('[data-test="edit-button"]').trigger('click')
    expect(wrapper.emitted().edit).toBeTruthy()
  })
})
```

---

## 🚀 部署指南

### 开发环境部署

#### 后端启动脚本
```bash
#!/bin/bash
# scripts/start-backend.sh

echo "🚀 启动 LingTaskFlow 后端服务..."

# 激活conda环境
source D:/Software/anaconda3/Scripts/activate
conda activate ling-task-flow-backend

# 进入项目目录
cd ling-task-flow-backend

# 检查数据库迁移
echo "📊 检查数据库迁移..."
python manage.py makemigrations
python manage.py migrate

# 收集静态文件
echo "📁 收集静态文件..."
python manage.py collectstatic --noinput

# 启动开发服务器
echo "🌐 启动开发服务器 (http://localhost:8000)..."
python manage.py runserver 0.0.0.0:8000
```

#### 前端启动脚本
```bash
#!/bin/bash
# scripts/start-frontend.sh

echo "🚀 启动 LingTaskFlow 前端服务..."

# 进入项目目录
cd ling-task-flow-frontend

# 安装依赖
echo "📦 安装依赖..."
npm install

# 启动开发服务器
echo "🌐 启动开发服务器 (http://localhost:9000)..."
npm run dev
```

### 生产环境部署

#### Docker 配置
```dockerfile
# Dockerfile.backend
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "ling_task_flow_backend.wsgi:application"]
```

```dockerfile
# Dockerfile.frontend
FROM node:22-alpine

WORKDIR /app

# 复制依赖文件
COPY package*.json ./
RUN npm ci --only=production

# 复制项目文件
COPY . .

# 构建项目
RUN npm run build

# 使用nginx提供静态文件
FROM nginx:alpine
COPY --from=0 /app/dist/spa /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  database:
    image: postgres:15
    environment:
      POSTGRES_DB: lingtaskflow
      POSTGRES_USER: lingtaskflow
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build:
      context: ./ling-task-flow-backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://lingtaskflow:${DB_PASSWORD}@database:5432/lingtaskflow
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=False
    depends_on:
      - database
    ports:
      - "8000:8000"

  frontend:
    build:
      context: ./ling-task-flow-frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

---

## 📊 监控与维护

### 性能监控

#### Django 性能监控
```python
# settings.py
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: True,
    }

# 生产环境监控
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
        },
        'performance': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/performance.log',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['performance'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

#### 定时任务清理
```python
# management/commands/cleanup_deleted_tasks.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from LingTaskFlow.models import Task

class Command(BaseCommand):
    help = '清理超过30天的软删除任务'

    def handle(self, *args, **options):
        cutoff_date = timezone.now() - timedelta(days=30)
        
        deleted_tasks = Task.objects.filter(
            is_deleted=True,
            deleted_at__lt=cutoff_date
        )
        
        count = deleted_tasks.count()
        deleted_tasks.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully cleaned up {count} expired tasks')
        )
```

### 备份策略

#### 数据库备份脚本
```bash
#!/bin/bash
# scripts/backup-database.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/lingtaskflow_backup_$DATE.sql"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行备份
pg_dump -h localhost -U lingtaskflow -d lingtaskflow > $BACKUP_FILE

# 压缩备份文件
gzip $BACKUP_FILE

# 删除7天前的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "数据库备份完成: ${BACKUP_FILE}.gz"
```

---

## 📋 开发检查清单

### 后端开发检查项

- [ ] 数据模型设计完成
- [ ] API接口实现完成
- [ ] 认证授权配置完成
- [ ] 输入验证和错误处理完成
- [ ] 单元测试编写完成
- [ ] API文档更新完成
- [ ] 性能优化实施完成
- [ ] 安全检查通过

### 前端开发检查项

- [ ] 组件设计完成
- [ ] 状态管理实现完成
- [ ] 路由配置完成
- [ ] UI/UX设计实现完成
- [ ] 响应式适配完成
- [ ] 错误处理实现完成
- [ ] 组件测试编写完成
- [ ] 性能优化实施完成

### 部署检查项

- [ ] 开发环境配置完成
- [ ] 生产环境配置完成
- [ ] 数据库迁移脚本准备完成
- [ ] 监控系统配置完成
- [ ] 备份策略实施完成
- [ ] 安全配置检查完成
- [ ] 负载测试完成
- [ ] 文档更新完成

---

## 📚 附录

### A. 技术选型说明

#### 为什么选择Django？
- 成熟的Web框架，内置ORM和管理后台
- 强大的认证授权系统
- 丰富的第三方库生态
- 良好的安全默认配置

#### 为什么选择Vue 3 + Quasar？
- Vue 3 Composition API提供更好的代码组织
- Quasar提供丰富的UI组件和工具
- TypeScript支持提高代码质量
- 单页应用提供更流畅的用户体验

### B. 数据库设计图

```
┌─────────────────┐    ┌─────────────────┐
│      User       │    │   UserProfile   │
├─────────────────┤    ├─────────────────┤
│ id (PK)         │◄──►│ id (PK)         │
│ username        │    │ user_id (FK)    │
│ email           │    │ avatar          │
│ password        │    │ timezone        │
│ date_joined     │    │ task_count      │
│ last_login      │    │ created_at      │
└─────────────────┘    └─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│      Task       │
├─────────────────┤
│ id (PK)         │
│ title           │
│ description     │
│ status          │
│ priority        │
│ is_deleted      │
│ deleted_at      │
│ created_at      │
│ updated_at      │
│ user_id (FK)    │
└─────────────────┘
```

### C. API响应示例

详细的API响应示例已在接口规范章节中提供。

---

*文档版本：v2.0 Professional*  
*最后更新：2025年1月31日*  
*维护者：GitHub Copilot*

---

# LingTaskFlow 灾难恢复与高可用架构设计文档

## 📋 文档信息

| 项目名称 | LingTaskFlow - 凌云任务管理应用 |
|---------|------------------------------|
| 文档版本 | v2.0 Professional |
| 创建日期 | 2025年1月31日 |
| 更新日期 | 2025年1月31日 |
| 文档作者 | GitHub Copilot |
| 项目状态 | 开发中 |

## 🎯 项目概述

### 灾难恢复愿景
构建一套完善的灾难恢复和高可用架构，确保LingTaskFlow在面对各种故障时能够快速恢复服务，最小化业务中断时间，保障用户数据安全。

### 核心价值主张
- **自动化恢复**：通过脚本和工具实现故障自动检测与恢复
- **数据安全**：定期备份用户数据，支持快速恢复
- **高可用架构**：多实例部署，负载均衡，故障自动切换
- **监控告警**：实时监控系统状态，异常自动告警

---

## 🔧 灾难恢复策略

### 备份策略

#### 数据库备份
- **备份频率**：每日凌晨1点自动备份
- **备份方式**：使用`pg_dump`工具进行逻辑备份
- **备份文件**：备份文件命名规则为`lingtaskflow_backup_YYYYMMDD.sql.gz`
- **备份存储**：备份文件存储在`/backups`目录，并同步到云存储

#### 文件系统备份
- **备份频率**：每日凌晨2点自动备份
- **备份方式**：使用`tar`命令打包应用文件和配置文件
- **备份文件**：备份文件命名规则为`lingtaskflow_files_backup_YYYYMMDD.tar.gz`
- **备份存储**：备份文件存储在`/backups`目录，并同步到云存储

#### 配置文件备份
- **备份频率**：每周一凌晨3点自动备份
- **备份方式**：使用`tar`命令打包Nginx和系统配置文件
- **备份文件**：备份文件命名规则为`lingtaskflow_config_backup_YYYYMMDD.tar.gz`
- **备份存储**：备份文件存储在`/backups`目录，并同步到云存储

### 恢复策略

#### 数据库恢复
```bash
#!/bin/bash
# scripts/restore-database.sh

set -e

BACKUP_DIR="/backups"
LATEST_DB_BACKUP=$(ls -t $BACKUP_DIR/lingtaskflow_backup_*.sql.gz | head -n 1)

if [ -z "$LATEST_DB_BACKUP" ]; then
    echo "没有找到可用的数据库备份文件"
    exit 1
fi

echo "开始恢复数据库：$LATEST_DB_BACKUP"

# 停止服务
echo "停止相关服务..."
systemctl stop lingtaskflow-backend
systemctl stop nginx

# 恢复数据库
gunzip -c $LATEST_DB_BACKUP | psql -U lingtaskflow -d lingtaskflow

echo "数据库恢复完成"

# 启动服务
echo "启动服务..."
systemctl start postgresql
systemctl start lingtaskflow-backend
systemctl start nginx

echo "服务已启动"
```

#### 文件系统恢复
```bash
#!/bin/bash
# scripts/restore-files.sh

set -e

BACKUP_DIR="/backups"
LATEST_FILES_BACKUP=$(ls -t $BACKUP_DIR/lingtaskflow_files_backup_*.tar.gz | head -n 1)

if [ -z "$LATEST_FILES_BACKUP" ]; then
    echo "没有找到可用的文件系统备份文件"
    exit 1
fi

echo "开始恢复文件系统：$LATEST_FILES_BACKUP"

# 停止服务
echo "停止相关服务..."
systemctl stop lingtaskflow-backend
systemctl stop nginx

# 恢复应用文件
tar -xzf $LATEST_FILES_BACKUP -C /app --strip-components=1

echo "文件系统恢复完成"

# 启动服务
echo "启动服务..."
systemctl start postgresql
systemctl start lingtaskflow-backend
systemctl start nginx

echo "服务已启动"
```

#### 配置文件恢复
```bash
#!/bin/bash
# scripts/restore-config.sh

set -e

BACKUP_DIR="/backups"
LATEST_CONFIG_BACKUP=$(ls -t $BACKUP_DIR/lingtaskflow_config_backup_*.tar.gz | head -n 1)

if [ -z "$LATEST_CONFIG_BACKUP" ]; then
    echo "没有找到可用的配置文件备份"
    exit 1
fi

echo "开始恢复配置文件：$LATEST_CONFIG_BACKUP"

# 停止服务
echo "停止相关服务..."
systemctl stop lingtaskflow-backend
systemctl stop nginx

# 恢复配置文件
tar -xzf $LATEST_CONFIG_BACKUP -C /

echo "配置文件恢复完成"

# 启动服务
echo "启动服务..."
systemctl start postgresql
systemctl start lingtaskflow-backend
systemctl start nginx

echo "服务已启动"
```

### 高可用配置

#### 负载均衡配置
```nginx
# configs/nginx.conf - 负载均衡配置
upstream backend_pool {
    least_conn;
    server backend1:8000 max_fails=3 fail_timeout=30s;
    server backend2:8000 max_fails=3 fail_timeout=30s;
    server backend3:8000 max_fails=3 fail_timeout=30s backup;
}

server {
    listen 80;
    listen [::]:80;
    server_name lingtaskflow.com;
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name lingtaskflow.com;
    
    # SSL配置
    ssl_certificate /etc/nginx/ssl/lingtaskflow.crt;
    ssl_certificate_key /etc/nginx/ssl/lingtaskflow.key;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # 安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # 静态文件缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # API代理
    location /api/ {
        proxy_pass http://backend_pool;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时配置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        # 健康检查
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;
    }
    
    # 前端应用
    location / {
        root /var/www/lingtaskflow;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # 防止缓存HTML文件
        location ~* \.html$ {
            expires -1;
            add_header Cache-Control "no-store, no-cache, must-revalidate";
        }
    }
    
    # 健康检查端点
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

#### 数据库主从复制
```yaml
# docker-compose.ha.yml - 高可用配置
version: '3.8'

services:
  postgres-master:
    image: postgres:15
    environment:
      POSTGRES_REPLICATION_USER: replicator
      POSTGRES_REPLICATION_PASSWORD: ${REPLICATION_PASSWORD}
    volumes:
      - postgres_master_data:/var/lib/postgresql/data
      - ./configs/postgres-master.conf:/etc/postgresql/postgresql.conf
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
    networks:
      - db_network

  postgres-slave:
    image: postgres:15
    environment:
      PGUSER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_MASTER_SERVICE: postgres-master
    volumes:
      - postgres_slave_data:/var/lib/postgresql/data
      - ./scripts/setup-slave.sh:/docker-entrypoint-initdb.d/setup-slave.sh
    depends_on:
      - postgres-master
    networks:
      - db_network

  redis-master:
    image: redis:7-alpine
    command: redis-server --appendonly yes --replica-announce-ip redis-master
    volumes:
      - redis_master_data:/data
    networks:
      - cache_network

  redis-slave:
    image: redis:7-alpine
    command: redis-server --replicaof redis-master 6379
    depends_on:
      - redis-master
    networks:
      - cache_network

  backend-1:
    build: ./ling-task-flow-backend
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres-master:5432/${DB_NAME}
      - REDIS_URL=redis://redis-master:6379/0
    depends_on:
      - postgres-master
      - redis-master
    networks:
      - app_network
      - db_network
      - cache_network

  backend-2:
    build: ./ling-task-flow-backend
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres-master:5432/${DB_NAME}
      - REDIS_URL=redis://redis-master:6379/0
    depends_on:
      - postgres-master
      - redis-master
    networks:
      - app_network
      - db_network
      - cache_network

  nginx:
    image: nginx:alpine
    volumes:
      - ./configs/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend-1
      - backend-2
    networks:
      - app_network

volumes:
  postgres_master_data:
  postgres_slave_data:
  redis_master_data:

networks:
  app_network:
  db_network:
  cache_network:
```

---

## 📈 故障恢复策略

### 自动故障切换脚本
```bash
#!/bin/bash
# scripts/failover.sh

HEALTH_CHECK_URL="http://localhost/api/health/"
MAX_RETRIES=3
RETRY_INTERVAL=10
LOG_FILE="/var/log/lingtaskflow-failover.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

check_health() {
    local url=$1
    local retries=0
    
    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -f --max-time 10 $url > /dev/null 2>&1; then
            return 0
        fi
        
        retries=$((retries + 1))
        log "健康检查失败 (尝试 $retries/$MAX_RETRIES)"
        
        if [ $retries -lt $MAX_RETRIES ]; then
            sleep $RETRY_INTERVAL
        fi
    done
    
    return 1
}

failover_to_backup() {
    log "开始故障切换到备用系统..."
    
    # 1. 更新DNS指向备用服务器
    log "更新DNS记录..."
    # 这里需要调用DNS提供商的API
    # update_dns_record "lingtaskflow.com" "A" "backup.server.ip"
    
    # 2. 启动备用数据库
    log "启动备用数据库..."
    ssh backup-server "systemctl start postgresql-backup"
    
    # 3. 同步最新数据
    log "同步数据到备用服务器..."
    rsync -avz --delete /data/backup/ backup-server:/data/restore/
    
    # 4. 启动备用应用服务
    log "启动备用应用服务..."
    ssh backup-server "docker-compose -f docker-compose.backup.yml up -d"
    
    # 5. 验证备用系统
    log "验证备用系统健康状态..."
    sleep 10
    
    if check_health "http://backup-server/api/health/"; then
        log "✓ 故障切换成功，备用系统运行正常"
        
        # 发送告警通知
        send_alert "故障切换完成" "主系统故障，已切换到备用系统。请尽快检查主系统状态。"
        
        return 0
    else
        log "✗ 故障切换失败，备用系统异常"
        send_alert "故障切换失败" "主系统和备用系统都无法正常提供服务，需要紧急处理！"
        return 1
    fi
}

send_alert() {
    local subject=$1
    local message=$2
    
    # 邮件通知
    echo "$message" | mail -s "$subject" $ADMIN_EMAIL
    
    # 短信通知（示例）
    # curl -X POST "https://sms.provider.com/api/send" \
    #      -d "phone=$ADMIN_PHONE&message=$subject: $message"
    
    # Slack通知（示例）
    # curl -X POST -H 'Content-type: application/json' \
    #      --data "{\"text\":\"$subject: $message\"}" \
    #      $SLACK_WEBHOOK_URL
}

# 主逻辑
log "开始健康检查..."

if ! check_health $HEALTH_CHECK_URL; then
    log "主系统健康检查失败，触发故障切换..."
    
    if failover_to_backup; then
        log "故障切换流程完成"
        exit 0
    else
        log "故障切换失败"
        exit 1
    fi
else
    log "系统运行正常"
    exit 0
fi
```

### 数据恢复验证脚本
```python
# scripts/verify_restore.py
#!/usr/bin/env python3

import psycopg2
import requests
import json
import sys
from datetime import datetime

def verify_database_restore():
    """验证数据库恢复完整性"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="lingtaskflow",
            user="lingtaskflow",
            password="password"
        )
        cur = conn.cursor()
        
        # 检查表是否存在
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cur.fetchall()]
        
        expected_tables = ['auth_user', 'tasks', 'user_profiles']
        missing_tables = set(expected_tables) - set(tables)
        
        if missing_tables:
            print(f"❌ 缺少表: {missing_tables}")
            return False
        
        # 检查数据完整性
        cur.execute("SELECT COUNT(*) FROM auth_user")
        user_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM tasks WHERE is_deleted = false")
        active_task_count = cur.fetchone()[0]
        
        print(f"✅ 数据库验证通过")
        print(f"   - 用户数量: {user_count}")
        print(f"   - 活跃任务数量: {active_task_count}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库验证失败: {str(e)}")
        return False

def verify_api_endpoints():
    """验证API端点可用性"""
    base_url = "http://localhost:8000"
    
    endpoints = [
        "/api/health/",
        "/api/auth/login/",
        "/api/tasks/",
    ]
    
    success_count = 0
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            
            if endpoint == "/api/tasks/":
                # 需要认证的端点，只检查是否返回401
                response = requests.get(url, timeout=10)
                if response.status_code == 401:
                    print(f"✅ {endpoint} - 认证检查正常")
                    success_count += 1
                else:
                    print(f"❌ {endpoint} - 状态码: {response.status_code}")
            else:
                # 公开端点
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"✅ {endpoint} - 响应正常")
                    success_count += 1
                else:
                    print(f"❌ {endpoint} - 状态码: {response.status_code}")
                    
        except requests.RequestException as e:
            print(f"❌ {endpoint} - 请求失败: {str(e)}")
    
    return success_count == len(endpoints)

def verify_frontend():
    """验证前端应用可用性"""
    try:
        response = requests.get("http://localhost", timeout=10)
        if response.status_code == 200 and "LingTaskFlow" in response.text:
            print("✅ 前端应用验证通过")
            return True
        else:
            print(f"❌ 前端应用验证失败 - 状态码: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ 前端应用验证失败: {str(e)}")
        return False

def main():
    """主验证流程"""
    print("🔍 开始系统恢复验证...")
    print(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    results = []
    
    # 数据库验证
    print("📊 验证数据库...")
    db_ok = verify_database_restore()
    results.append(("数据库", db_ok))
    
    # API验证
    print("\n🔌 验证API端点...")
    api_ok = verify_api_endpoints()
    results.append(("API服务", api_ok))
    
    # 前端验证
    print("\n🌐 验证前端应用...")
    frontend_ok = verify_frontend()
    results.append(("前端应用", frontend_ok))
    
    # 总结
    print("\n" + "=" * 50)
    print("📋 验证结果总结:")
    
    all_passed = True
    for component, status in results:
        status_text = "✅ 通过" if status else "❌ 失败"
        print(f"   {component}: {status_text}")
        if not status:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有组件验证通过，系统恢复成功！")
        sys.exit(0)
    else:
        print("\n⚠️  部分组件验证失败，需要进一步检查！")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 📈 系统扩展规划

### 未来功能扩展

#### 阶段一：核心功能增强（3个月内）
```markdown
1. 任务功能增强
   - 任务标签系统
   - 任务截止日期
   - 任务依赖关系
   - 任务模板功能

2. 用户体验优化
   - 拖拽排序
   - 快捷键支持
   - 离线同步功能
   - 主题切换

3. 数据统计
   - 个人效率报表
   - 任务完成趋势
   - 时间分析图表
```

#### 阶段二：协作功能（6个月内）
```markdown
1. 团队协作
   - 工作空间概念
   - 任务分配
   - 评论系统
   - 文件附件

2. 通知系统
   - 邮件通知
   - 浏览器推送
   - 移动端推送
   - 微信集成

3. 权限管理
   - 角色权限系统
   - 数据权限控制
   - 审计日志
```

#### 阶段三：企业级功能（12个月内）
```markdown
1. 多租户支持
   - 组织管理
   - 数据隔离
   - 计费系统
   - 资源配额

2. 高级分析
   - 机器学习预测
   - 智能推荐
   - 自动化工作流
   - API集成平台

3. 移动应用
   - React Native App
   - 离线功能
   - 推送通知
   - 生物识别认证
```

### 技术架构演进

#### 微服务化改造
```mermaid
graph TB
    Gateway[API Gateway] --> Auth[认证服务]
    Gateway --> Task[任务服务]
    Gateway --> User[用户服务]
    Gateway --> Notify[通知服务]
    
    Auth --> AuthDB[(认证数据库)]
    Task --> TaskDB[(任务数据库)]
    User --> UserDB[(用户数据库)]
    Notify --> Queue[消息队列]
    
    Task --> Cache[(Redis缓存)]
    Task --> Search[(搜索引擎)]
```

#### 数据库分片策略
```python
# 分片路由策略
class DatabaseRouter:
    """数据库分片路由器"""
    
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'tasks':
            # 根据用户ID进行分片
            user_id = hints.get('user_id')
            if user_id:
                shard_number = user_id % 4  # 4个分片
                return f'shard_{shard_number}'
        return 'default'
    
    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)
```

---

## 📚 文档维护指南

### 文档更新流程

#### 1. 架构变更记录
```markdown
# 架构变更日志

## [v1.1.0] - 2025-02-15
### 新增
- Redis缓存层集成
- API限流机制
- 性能监控组件

### 修改
- 数据库索引优化
- 前端组件重构
- 错误处理改进

### 删除
- 废弃的API端点
- 旧版本兼容代码
```

#### 2. API文档自动生成
```python
# settings.py - API文档配置
SPECTACULAR_SETTINGS = {
    'TITLE': 'LingTaskFlow API',
    'DESCRIPTION': '凌云任务管理应用API文档',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
    },
    'REDOC_UI_SETTINGS': {
        'hideDownloadButton': True,
        'hideHostname': True,
        'noAutoAuth': True,
    }
}
```

#### 3. 代码注释规范
```python
class TaskService:
    """
    任务服务类
    
    提供任务的业务逻辑处理，包括创建、更新、删除、查询等功能。
    支持软删除、批量操作、数据验证等特性。
    
    Attributes:
        model: 任务模型类
        cache_timeout: 缓存超时时间（秒）
        
    Example:
        >>> service = TaskService()
        >>> task = service.create_task(user, {'title': '新任务'})
        >>> print(task.id)
    """
    
    def create_task(self, user: User, task_data: dict) -> Task:
        """
        创建新任务
        
        Args:
            user: 任务所属用户
            task_data: 任务数据字典，包含title、description等字段
            
        Returns:
            Task: 创建的任务对象
            
        Raises:
            ValidationError: 当任务数据验证失败时
            PermissionError: 当用户没有创建权限时
            
        Note:
            任务创建后会自动设置状态为TODO，优先级为中等
        """
        pass
```

### 文档结构说明

```
docs/
├── architecture/
│   ├── ling_task_flow_architecture.md    # 本文档
│   ├── database_design.md                # 数据库设计详情
│   ├── api_specification.md              # API规范详情
│   └── security_guidelines.md            # 安全指南
├── development/
│   ├── setup_guide.md                    # 环境搭建指南
│   ├── coding_standards.md               # 编码规范
│   ├── testing_guide.md                  # 测试指南
│   └── deployment_guide.md               # 部署指南
├── user/
│   ├── user_manual.md                    # 用户手册
│   ├── admin_guide.md                    # 管理员指南
│   └── faq.md                            # 常见问题
└── changelog/
    ├── CHANGELOG.md                      # 版本更新日志
    ├── migration_guide.md                # 迁移指南
    └── breaking_changes.md               # 破坏性变更说明
```

---

## 🎯 总结

### 架构优势

1. **技术栈现代化**：采用最新的Django 5.2 + Vue 3技术栈，确保长期维护性
2. **安全性设计**：从认证到数据传输全链路安全保障
3. **性能优化**：多级缓存、数据库优化、前端虚拟滚动等性能优化策略
4. **可扩展性**：模块化设计，支持水平扩展和功能扩展
5. **开发效率**：完善的开发工具链和自动化流程

### 核心特性

- ✅ **用户认证**：JWT Token认证，支持登录、注册、token刷新
- ✅ **任务管理**：完整的CRUD操作，支持软删除和恢复
- ✅ **数据安全**：用户数据隔离，输入验证，XSS/CSRF防护
- ✅ **性能优化**：缓存策略，数据库索引，前端优化
- ✅ **监控运维**：健康检查，错误追踪，性能监控
- ✅ **容灾备份**：自动备份，故障切换，数据恢复

### 技术指标

| 指标 | 目标值 | 备注 |
|------|--------|------|
| API响应时间 | < 500ms | 95%的请求 |
| 系统可用性 | 99.9% | 年度目标 |
| 数据库查询 | < 100ms | 单次查询 |
| 前端首屏加载 | < 2s | 首次访问 |
| 并发用户数 | 1000+ | 同时在线 |
| 数据备份 | 每日 | 自动备份 |

### 开发里程碑

#### 第一阶段：MVP开发（4周）
- [ ] 用户认证系统
- [ ] 基础任务管理
- [ ] 核心API接口
- [ ] 基础前端界面

#### 第二阶段：功能完善（4周）
- [ ] 高级筛选排序
- [ ] 软删除和恢复
- [ ] 性能优化
- [ ] 错误处理完善

#### 第三阶段：生产就绪（2周）
- [ ] 监控系统集成
- [ ] 安全加固
- [ ] 部署自动化
- [ ] 文档完善

---

**项目状态：** 🏗️ 开发中  
**当前版本：** v1.0.0-alpha  
**文档版本：** v1.0  
**最后更新：** 2025年1月31日  

---

*本文档遵循语义化版本控制规范，定期更新以反映最新的架构设计和技术决策。*

*如有任何问题或建议，请联系项目维护团队。*
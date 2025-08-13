# LingTaskFlow 专业产品需求文档 (PRD)

## 📋 文档信息

| 项目名称 | LingTaskFlow - 凌云任务管理应用 |
|------|-------------------------|
| 文档版本 | v2.0 Professional       |
| 创建日期 | 2025 年 1 月 31 日         |
| 更新日期 | 2025 年 1 月 31 日         |
| 文档作者 | GitHub Copilot          |
| 项目状态 | 开发中                     |

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

### 1. 认证相关 API

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

#### 1.3 刷新 Token

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

### 2. 任务管理 API

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

### 3. 统计信息 API

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
import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { Task, TaskFilters, PaginatedResponse } from "@/types";

export const useTaskStore = defineStore("task", () => {
  // State
  const tasks = ref<Task[]>([]);
  const loading = ref(false);
  const filters = ref<TaskFilters>({
    page: 1,
    page_size: 20,
    status: [],
    search: "",
    ordering: "-created_at",
    include_deleted: false,
  });
  const pagination = ref({
    count: 0,
    next: null,
    previous: null,
  });

  // Getters
  const activeTasks = computed(() =>
    tasks.value.filter((task) => !task.is_deleted)
  );

  const tasksByStatus = computed(() => {
    const grouped: Record<string, Task[]> = {};
    activeTasks.value.forEach((task) => {
      if (!grouped[task.status]) grouped[task.status] = [];
      grouped[task.status].push(task);
    });
    return grouped;
  });

  // Actions
  async function fetchTasks() {
    loading.value = true;
    try {
      const response = await taskApi.getTasks(filters.value);
      tasks.value = response.data.results;
      pagination.value = {
        count: response.data.count,
        next: response.data.next,
        previous: response.data.previous,
      };
    } catch (error) {
      console.error("Failed to fetch tasks:", error);
      throw error;
    } finally {
      loading.value = false;
    }
  }

  async function createTask(taskData: Partial<Task>) {
    try {
      const response = await taskApi.createTask(taskData);
      tasks.value.unshift(response.data);
      return response.data;
    } catch (error) {
      console.error("Failed to create task:", error);
      throw error;
    }
  }

  async function updateTask(taskId: string, updates: Partial<Task>) {
    try {
      const response = await taskApi.updateTask(taskId, updates);
      const index = tasks.value.findIndex((t) => t.id === taskId);
      if (index !== -1) {
        tasks.value[index] = response.data;
      }
      return response.data;
    } catch (error) {
      console.error("Failed to update task:", error);
      throw error;
    }
  }

  async function deleteTask(taskId: string) {
    try {
      await taskApi.deleteTask(taskId);
      const task = tasks.value.find((t) => t.id === taskId);
      if (task) {
        task.is_deleted = true;
        task.deleted_at = new Date().toISOString();
      }
    } catch (error) {
      console.error("Failed to delete task:", error);
      throw error;
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
    deleteTask,
  };
});
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
      <q-btn fab icon="add" color="primary" @click="showCreateDialog = true" />
    </q-page-sticky>

    <TaskCreateDialog v-model="showCreateDialog" @created="handleTaskCreated" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useTaskStore } from "@/stores/task";
import TaskFilters from "@/components/TaskFilters.vue";
import TaskCard from "@/components/TaskCard.vue";
import TaskCreateDialog from "@/components/TaskCreateDialog.vue";
import EmptyState from "@/components/EmptyState.vue";

const taskStore = useTaskStore();
const showCreateDialog = ref(false);

onMounted(() => {
  taskStore.fetchTasks();
});

const handleFilterChange = () => {
  taskStore.filters.page = 1;
  taskStore.fetchTasks();
};

const handlePageChange = () => {
  taskStore.fetchTasks();
};

const handleEditTask = (task: Task) => {
  // 打开编辑对话框
};

const handleDeleteTask = async (taskId: string) => {
  try {
    await taskStore.deleteTask(taskId);
    $q.notify({
      type: "positive",
      message: "任务已移入回收站",
      position: "top",
    });
  } catch (error) {
    $q.notify({
      type: "negative",
      message: "删除失败，请重试",
      position: "top",
    });
  }
};

const handleStatusChange = async (taskId: string, newStatus: string) => {
  try {
    await taskStore.updateTask(taskId, { status: newStatus });
    $q.notify({
      type: "positive",
      message: "状态更新成功",
      position: "top",
    });
  } catch (error) {
    $q.notify({
      type: "negative",
      message: "状态更新失败",
      position: "top",
    });
  }
};

const handleTaskCreated = (task: Task) => {
  showCreateDialog.value = false;
  $q.notify({
    type: "positive",
    message: "任务创建成功",
    position: "top",
  });
};
</script>
```

---

## 🔍 错误处理与状态码

### HTTP 状态码定义

| 状态码 | 含义                    | 使用场景       |
|-----|-----------------------|------------|
| 200 | OK                    | 请求成功       |
| 201 | Created               | 资源创建成功     |
| 204 | No Content            | 删除成功，无返回内容 |
| 400 | Bad Request           | 请求参数错误     |
| 401 | Unauthorized          | 认证失败       |
| 403 | Forbidden             | 权限不足       |
| 404 | Not Found             | 资源不存在      |
| 409 | Conflict              | 资源冲突       |
| 422 | Unprocessable Entity  | 数据验证失败     |
| 429 | Too Many Requests     | 请求过于频繁     |
| 500 | Internal Server Error | 服务器内部错误    |

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
import { AxiosResponse } from "axios";

interface CacheConfig {
  ttl: number; // 缓存时间（毫秒）
  key: string;
}

class TaskAPI {
  private cache = new Map<
    string,
    { data: any; timestamp: number; ttl: number }
  >();

  async getTasks(
    filters: TaskFilters,
    cacheConfig?: CacheConfig
  ): Promise<AxiosResponse> {
    const cacheKey = cacheConfig?.key || `tasks-${JSON.stringify(filters)}`;

    // 检查缓存
    if (cacheConfig) {
      const cached = this.cache.get(cacheKey);
      if (cached && Date.now() - cached.timestamp < cached.ttl) {
        return { data: cached.data } as AxiosResponse;
      }
    }

    const response = await api.get("/tasks/", { params: filters });

    // 更新缓存
    if (cacheConfig) {
      this.cache.set(cacheKey, {
        data: response.data,
        timestamp: Date.now(),
        ttl: cacheConfig.ttl,
      });
    }

    return response;
  }

  // 清除相关缓存
  invalidateCache(pattern: string) {
    for (const key of this.cache.keys()) {
      if (key.includes(pattern)) {
        this.cache.delete(key);
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

#### API 测试

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
import { mount } from "@vue/test-utils";
import { describe, it, expect, vi } from "vitest";
import TaskCard from "@/components/TaskCard.vue";
import { Quasar } from "quasar";

describe("TaskCard", () => {
  const mockTask = {
    id: "1",
    title: "Test Task",
    description: "Test Description",
    status: "TODO",
    priority: 3,
    created_at: "2025-01-31T10:30:00Z",
    updated_at: "2025-01-31T10:30:00Z",
    is_deleted: false,
  };

  it("renders task information correctly", () => {
    const wrapper = mount(TaskCard, {
      props: { task: mockTask },
      global: {
        plugins: [Quasar],
      },
    });

    expect(wrapper.text()).toContain("Test Task");
    expect(wrapper.text()).toContain("Test Description");
  });

  it("emits edit event when edit button is clicked", async () => {
    const wrapper = mount(TaskCard, {
      props: { task: mockTask },
      global: {
        plugins: [Quasar],
      },
    });

    await wrapper.find('[data-test="edit-button"]').trigger("click");
    expect(wrapper.emitted().edit).toBeTruthy();
  });
});
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
version: "3.8"

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
- [ ] API 接口实现完成
- [ ] 认证授权配置完成
- [ ] 输入验证和错误处理完成
- [ ] 单元测试编写完成
- [ ] API 文档更新完成
- [ ] 性能优化实施完成
- [ ] 安全检查通过

### 前端开发检查项

- [ ] 组件设计完成
- [ ] 状态管理实现完成
- [ ] 路由配置完成
- [ ] UI/UX 设计实现完成
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

#### 为什么选择 Django？

- 成熟的 Web 框架，内置 ORM 和管理后台
- 强大的认证授权系统
- 丰富的第三方库生态
- 良好的安全默认配置

#### 为什么选择 Vue 3 + Quasar？

- Vue 3 Composition API 提供更好的代码组织
- Quasar 提供丰富的 UI 组件和工具
- TypeScript 支持提高代码质量
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

### C. API 响应示例

详细的 API 响应示例已在接口规范章节中提供。

---

_文档版本：v2.0 Professional_  
_最后更新：2025 年 1 月 31 日_  
_维护者：GitHub Copilot_

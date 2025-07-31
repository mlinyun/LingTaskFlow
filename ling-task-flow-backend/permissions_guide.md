# LingTaskFlow 权限系统使用指南

## 概述

LingTaskFlow 实现了一套完整的 Django REST Framework 权限系统，提供了五个核心权限类，用于控制 API 的访问权限。

## 权限类列表

### 1. IsOwnerOrReadOnly - 所有者或只读权限

**使用场景：** 任务管理、用户资料、评论系统

**权限规则：**
- 未认证用户：拒绝所有访问
- 已认证用户：可以读取所有内容，但只能修改自己拥有的对象
- 管理员用户：拥有所有权限

**代码示例：**
```python
from rest_framework.viewsets import ModelViewSet
from LingTaskFlow.permissions import IsOwnerOrReadOnly

class TaskViewSet(ModelViewSet):
    permission_classes = [IsOwnerOrReadOnly]
    # ... 其他配置
```

**对象属性支持：** `owner`, `user`, `created_by`

### 2. IsOwner - 严格所有者权限

**使用场景：** 用户个人资料、私人笔记、个人设置

**权限规则：**
- 只有对象的所有者才能进行任何操作（包括读取）
- 管理员拥有所有权限

**代码示例：**
```python
class UserProfileViewSet(ModelViewSet):
    permission_classes = [IsOwner]
    # 用户只能访问自己的资料
```

### 3. IsAuthorOrReadOnly - 作者或只读权限

**使用场景：** 博客文章、论坛帖子、公开评论

**权限规则：**
- 作者可以编辑自己的内容
- 其他已认证用户可以读取
- 管理员拥有所有权限

**代码示例：**
```python
class BlogPostViewSet(ModelViewSet):
    permission_classes = [IsAuthorOrReadOnly]
    # 作者可以编辑，其他人只能读取
```

**对象属性支持：** `author`, `created_by`

### 4. IsAdminOrReadOnly - 管理员或只读权限

**使用场景：** 系统公告、应用配置、全局设置

**权限规则：**
- 所有已认证用户可以读取
- 只有管理员可以进行写操作

**代码示例：**
```python
class SystemAnnouncementViewSet(ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    # 只有管理员可以发布公告
```

### 5. IsSelfOrReadOnly - 用户自身或只读权限

**使用场景：** 用户资料页面、个人设置、账户信息

**权限规则：**
- 用户只能修改自己的信息
- 其他用户可以读取（如查看用户资料）
- 管理员拥有所有权限

**代码示例：**
```python
class UserViewSet(ModelViewSet):
    permission_classes = [IsSelfOrReadOnly]
    # 用户只能修改自己的账户信息
```

**对象属性支持：** `username`（User对象）, `user`（关联对象）

## 使用方法

### 1. 在视图中使用

```python
from rest_framework.viewsets import ModelViewSet
from LingTaskFlow.permissions import IsOwnerOrReadOnly

class MyModelViewSet(ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer
    permission_classes = [IsOwnerOrReadOnly]
```

### 2. 组合使用权限

```python
from rest_framework.permissions import IsAuthenticated
from LingTaskFlow.permissions import IsOwnerOrReadOnly

class TaskViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    # 用户必须先登录，然后检查对象权限
```

### 3. 模型要求

确保你的模型有适当的所有者字段：

```python
class Task(models.Model):
    title = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)  # 所有者字段
    created_at = models.DateTimeField(auto_now_add=True)
```

或者：

```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # 用户字段
    bio = models.TextField(blank=True)
```

## 权限检查流程

1. **视图级权限检查**：`has_permission(request, view)`
   - 检查用户是否有权限访问这个视图

2. **对象级权限检查**：`has_object_permission(request, view, obj)`
   - 检查用户是否有权限操作特定对象

3. **管理员优先级**：
   - `is_staff` 或 `is_superuser` 的用户拥有所有权限

## HTTP 方法权限

- **安全方法**（只读）：`GET`, `HEAD`, `OPTIONS`
- **不安全方法**（写入）：`POST`, `PUT`, `PATCH`, `DELETE`

权限类会根据 HTTP 方法的类型应用不同的权限规则。

## 测试示例

权限系统包含完整的测试套件，你可以运行测试来验证权限功能：

```bash
# 运行基础权限测试
python test_permissions_fixed.py

# 运行完整权限测试
python test_all_permissions.py
```

## 自定义权限类

如果需要创建自定义权限类，可以继承 `permissions.BasePermission`：

```python
from rest_framework import permissions

class MyCustomPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # 视图级权限逻辑
        return True
    
    def has_object_permission(self, request, view, obj):
        # 对象级权限逻辑
        return True
```

## 最佳实践

1. **明确权限需求**：根据业务需求选择合适的权限类
2. **模型设计**：确保模型有正确的所有者字段
3. **权限组合**：可以组合多个权限类实现复杂权限控制
4. **测试权限**：为每个 API 端点编写权限测试
5. **文档说明**：在 API 文档中明确说明权限要求

## 常见问题

### Q: 如何处理没有所有者字段的模型？
A: 权限类会按顺序检查 `owner`、`user`、`created_by` 字段，如果都不存在则拒绝写操作。

### Q: 管理员权限如何生效？
A: 具有 `is_staff=True` 或 `is_superuser=True` 的用户自动获得所有权限。

### Q: 如何在权限类中添加自定义逻辑？
A: 可以继承现有权限类并重写相应方法，或者创建全新的权限类。

---

**注意：** 本权限系统已通过完整测试，涵盖了匿名用户、普通用户、管理员等各种场景的权限验证。

# LingTaskFlow 软删除和恢复功能详细说明

## 功能概述

LingTaskFlow 实现了完善的软删除功能，允许用户"删除"任务而不实际从数据库中移除，提供了安全的数据保护和恢复机制。

## 架构设计

### 1. 核心组件

#### SoftDeleteQuerySet
- 提供强大的软删除查询功能
- 支持批量操作和时间范围查询
- 方法：`active()`, `deleted()`, `soft_delete()`, `restore()`, `hard_delete()`

#### SoftDeleteManager  
- 软删除管理器，默认排除已删除记录
- 提供多种查询接口：`deleted_only()`, `all_with_deleted()`
- 支持软删除查询集操作

#### SoftDeleteModel
- 抽象基类，提供完整的软删除功能
- 包含删除状态、删除时间、删除者字段
- 实现软删除、恢复、硬删除方法

### 2. 数据模型

```python
class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)      # 删除标记
    deleted_at = models.DateTimeField(null=True)         # 删除时间
    deleted_by = models.ForeignKey(User, null=True)      # 删除者
    
    objects = SoftDeleteManager()        # 默认管理器（排除已删除）
    all_objects = models.Manager()       # 全部记录管理器
```

## 功能特性

### 1. 基础软删除功能

#### 软删除
```python
task.soft_delete(user=current_user)
```
- 设置 `is_deleted=True`
- 记录删除时间 `deleted_at`
- 记录删除者 `deleted_by`
- 自动更新用户统计

#### 恢复
```python
task.restore(user=current_user)
```
- 设置 `is_deleted=False`
- 清除删除时间和删除者
- 自动更新用户统计

#### 硬删除（永久删除）
```python
task.hard_delete()
```
- 真正从数据库删除记录
- 不可恢复

### 2. 权限控制

#### 删除权限
```python
task.can_delete(user)  # 只有任务所有者可以删除
```

#### 恢复权限
```python
task.can_restore(user)  # 只有任务所有者可以恢复
```

### 3. 查询功能

#### 基本查询
```python
Task.objects.all()                    # 活跃任务（默认）
Task.objects.deleted_only()           # 仅删除的任务
Task.objects.all_with_deleted()       # 所有任务（包含删除的）
```

#### 用户回收站
```python
Task.get_user_trash(user)             # 获取用户回收站
Task.get_user_trash(user, include_assigned=True)  # 包含分配的任务
```

### 4. 批量操作

#### 批量恢复
```python
result = Task.restore_user_tasks(user, task_ids)
# 返回: {'restored': 2, 'failed': 0, 'total': 2}
```

#### 批量永久删除
```python
result = Task.permanent_delete_user_tasks(user, task_ids)  
# 返回: {'deleted': 2, 'total': 2}
```

### 5. 统计功能

#### 删除统计
```python
stats = Task.get_deletion_statistics(user)
```
返回统计信息：
- 总删除数
- 今天/本周/本月删除数
- 最早/最新删除记录
- 可清理数量

#### 回收站信息
```python
trash_info = task.get_trash_info()
```
返回回收站详细信息：
- 任务基本信息
- 删除时间和删除者
- 删除时的状态
- 是否可恢复

### 6. 清理功能

#### 自动清理
```python
cleaned_count = Task.cleanup_old_deleted_tasks(days=30)
```
- 清理指定天数前删除的任务
- 执行硬删除，释放存储空间
- 返回清理的任务数量

#### 检查删除时长
```python
task.deletion_age      # 删除后的天数
task.can_be_restored   # 是否可以恢复
```

## 使用场景

### 1. 用户误删保护
- 用户误删任务时可以从回收站恢复
- 提供删除确认机制
- 支持批量恢复操作

### 2. 数据安全
- 重要任务不会被意外永久删除
- 保留删除者和删除时间信息
- 支持删除审计

### 3. 存储管理
- 定期清理过期删除记录
- 避免数据库膨胀
- 平衡安全性和存储效率

### 4. 用户体验
- 回收站界面友好
- 支持搜索和筛选
- 提供删除统计信息

## API 集成

### 序列化器支持
软删除功能已集成到任务序列化器中：
- TaskListSerializer 默认排除已删除任务
- TaskDetailSerializer 包含删除状态信息
- 支持回收站专用序列化器

### 视图集成
计划在 API 视图中实现：
- `DELETE /api/tasks/{id}/` - 软删除
- `POST /api/tasks/{id}/restore/` - 恢复任务  
- `DELETE /api/tasks/{id}/permanent/` - 永久删除
- `GET /api/tasks/trash/` - 回收站列表

## 性能考虑

### 1. 查询优化
- 为 `is_deleted` 字段创建索引
- 复合索引：`(is_deleted, owner, -created_at)`
- 时间范围查询索引：`(deleted_at, is_deleted)`

### 2. 存储优化
- 定期清理过期删除记录
- 考虑分区存储（活跃/删除）
- 监控删除记录占比

### 3. 缓存策略
- 缓存用户删除统计
- 回收站计数缓存
- 避免重复查询删除状态

## 安全考虑

### 1. 权限验证
- 严格的删除权限检查
- 防止跨用户操作
- 管理员权限支持

### 2. 数据保护
- 防止意外硬删除
- 删除操作日志记录
- 支持删除审计

### 3. 隐私保护
- 已删除任务不出现在搜索中
- API 响应中排除敏感信息
- 支持真正的数据清理

## 扩展功能

### 1. 批量操作增强
- 支持条件批量删除
- 定时任务清理
- 导出删除记录

### 2. 通知功能
- 删除操作通知
- 清理提醒
- 恢复确认

### 3. 审计日志
- 详细的删除日志
- 操作时间线
- 用户行为分析

## 最佳实践

### 1. 开发建议
- 始终使用软删除代替硬删除
- 定期执行清理任务
- 监控删除记录增长

### 2. 用户教育
- 解释软删除机制
- 提供恢复指导
- 强调数据安全

### 3. 运维管理
- 设置合理的清理周期
- 监控存储使用情况
- 备份重要删除记录

这套软删除系统为 LingTaskFlow 提供了企业级的数据安全保障，在保护用户数据的同时维持了良好的系统性能。

# 类型定义组织结构

本项目采用模块化的类型定义组织方式，将所有类型定义集中在 `src/types/` 目录下，按功能领域分类。

## 目录结构

```
src/types/
├── index.ts          # 统一导出入口
├── api.ts           # API相关类型
├── auth.ts          # 认证相关类型
├── ui.ts            # UI组件相关类型
└── business.ts      # 业务逻辑相关类型
```

## 使用方式

### 1. 推荐用法 - 从统一入口导入

```typescript
// 导入常用类型
import type { User, APIResponse, TaskType, NotificationType } from 'src/types';

// 导入枚举
import { TaskStatus, TaskPriority, UserStatus } from 'src/types';
```

### 2. 从特定模块导入

```typescript
// 只导入认证相关类型
import type { User, AuthData, LoginCredentials } from 'src/types/auth';

// 只导入UI相关类型
import type { NotificationOptions, DialogOptions } from 'src/types/ui';
```

## 类型模块说明

### api.ts - API相关类型

- `StandardAPIResponse<T>` - 标准化API响应格式
- `APIError` - API错误类型
- `PaginatedData<T>` - 分页数据类型
- `ValidationError` - 表单验证错误
- `HTTPStatus`, `ErrorCode` - 状态码和错误码枚举

### auth.ts - 认证相关类型

- `User` - 用户信息接口
- `UserProfile` - 用户详情配置
- `AuthData` - 认证数据（登录成功后的数据）
- `LoginCredentials` - 登录凭据
- `TokenInfo` - JWT Token信息
- `UserStatus`, `ThemePreference` - 用户状态和主题偏好枚举

### ui.ts - UI组件相关类型

- `NotificationOptions` - 通知配置
- `DialogOptions` - 对话框配置
- `FormField` - 表单字段配置
- `TableColumn<T>` - 表格列配置（支持泛型）
- `PaginationConfig` - 分页配置
- `NotificationType` - 通知类型枚举

### business.ts - 业务逻辑相关类型

- `Task` - 任务接口
- `Project` - 项目接口
- `Tag` - 标签接口
- `TaskFormData` - 任务表单数据
- `TimeEntry` - 时间跟踪记录
- `TaskStatus`, `TaskPriority`, `ProjectStatus` - 业务状态枚举

## 类型别名

为了便于使用，提供了一些常用的类型别名：

- `APIResponse<T>` = `StandardAPIResponse<T>`
- `UserType` = `User`
- `TaskType` = `Task`
- `ProjectType` = `Project`

## 最佳实践

1. **优先使用统一入口导入** - 从 `src/types` 导入可以获得最好的IDE支持
2. **合理使用泛型** - 如 `TableColumn<TaskType>`、`APIResponse<User[]>` 等
3. **保持类型定义同步** - 修改后端API时，及时更新对应的TypeScript类型
4. **使用枚举替代字符串字面量** - 提高类型安全性和代码可维护性

## 迁移指南

如果你之前在其他文件中定义了类型，建议：

1. 将通用类型移动到对应的类型模块中
2. 更新导入语句使用新的类型模块
3. 删除重复的类型定义
4. 组件特定的类型可以保留在组件文件中

这种组织方式提供了更好的类型复用性、可维护性和开发体验。

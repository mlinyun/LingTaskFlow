/**
 * 类型定义统一导出入口
 * 提供所有类型的集中导入
 */

// API 相关类型
export type {
    StandardAPIResponse,
    APIError,
    CustomError,
    PaginatedData,
    PaginationMeta,
    PaginationLinks,
    ValidationError,
    ValidationErrors,
    APIRequestConfig,
    HTTPMethod,
} from './api';

export { ErrorCode, HTTPStatus } from './api';

// 认证相关类型
export type {
    User,
    UserProfile,
    TokenInfo,
    AuthData,
    LoginCredentials,
    RegisterData,
    RegisterResponse,
    AuthResponse,
    SecurityInfo,
    LoginResponse,
} from './auth';

export { UserStatus, ThemePreference } from './auth';

// UI 相关类型
export type {
    NotificationOptions,
    DialogOptions,
    ConfirmDialogOptions,
    ValidationRule,
    FormField,
    TableColumn,
    PaginationConfig,
    NavLink,
    BreadcrumbItem,
    LoadingState,
    ErrorState,
    PageState,
    ThemeConfig,
    LayoutConfig,
    SearchFilter,
} from './ui';

export { NotificationType } from './ui';

// 任务相关类型
export type {
    Task,
    TaskCreateData,
    TaskUpdateData,
    TaskSearchParams,
    TaskStats,
    TaskActivity,
    TrashStats,
    TrashResponse,
    SavedSearch,
    SearchHistory,
    StatusDistribution,
    TagDistribution,
    TimeDistribution,
} from './task';

export type { TaskStatus, TaskPriority } from './task';

// 业务相关类型（排除Task，使用task.ts中的定义）
export type {
    Tag,
    Project,
    ProjectFormData,
    TagFormData,
    ProjectStats,
    TimeEntry,
    TimeEntryFormData,
    Comment,
    CommentFormData,
    TaskFilter,
    ProjectFilter,
} from './business';

// 重命名业务类型中的冲突枚举，避免与 task.ts 中的类型冲突
export {
    TaskPriority as BusinessTaskPriority,
    TaskStatus as BusinessTaskStatus,
    ProjectStatus,
    TagColor,
} from './business';

// 常用类型别名（便于使用）
import type { StandardAPIResponse } from './api';
import type { User } from './auth';
import type { Project, Task } from './business';

export type APIResponse<T = unknown> = StandardAPIResponse<T>;
export type UserType = User;
export type TaskType = Task;
export type ProjectType = Project;

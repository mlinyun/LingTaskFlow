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

// 业务相关类型
export type {
    Tag,
    Project,
    Task,
    TaskFormData,
    ProjectFormData,
    TagFormData,
    TaskStats,
    ProjectStats,
    TimeEntry,
    TimeEntryFormData,
    Comment,
    CommentFormData,
    TaskFilter,
    ProjectFilter,
} from './business';

export { TaskPriority, TaskStatus, ProjectStatus, TagColor } from './business';

// 常用类型别名（便于使用）
import type { StandardAPIResponse } from './api';
import type { User } from './auth';
import type { Task, Project } from './business';

export type APIResponse<T = unknown> = StandardAPIResponse<T>;
export type UserType = User;
export type TaskType = Task;
export type ProjectType = Project;

/**
 * UI 相关类型定义
 * 包含通知、对话框、表单、导航等UI组件类型
 */

// 通知类型枚举
export enum NotificationType {
    SUCCESS = 'positive',
    ERROR = 'negative',
    WARNING = 'warning',
    INFO = 'info',
}

// 通知配置接口
export interface NotificationOptions {
    message: string;
    type: NotificationType;
    timeout?: number;
    position?: 'top' | 'bottom' | 'left' | 'right' | 'center';
    actions?: Array<{
        label: string;
        color?: string;
        handler: () => void;
    }>;
}

// 对话框配置
export interface DialogOptions {
    title: string;
    message: string;
    cancel?: boolean;
    persistent?: boolean;
    ok?: string | boolean;
    cancel_text?: string;
    html?: boolean;
}

// 确认对话框选项
export interface ConfirmDialogOptions extends DialogOptions {
    onOk?: () => void;
    onCancel?: () => void;
}

// 表单验证规则
export type ValidationRule = (val: unknown) => boolean | string;

// 表单字段配置
export interface FormField {
    name: string;
    label: string;
    type: 'text' | 'email' | 'password' | 'number' | 'textarea' | 'select' | 'checkbox' | 'radio';
    required?: boolean;
    rules?: ValidationRule[];
    placeholder?: string;
    options?: Array<{ label: string; value: string | number | boolean }>;
    disabled?: boolean;
    readonly?: boolean;
}

// 表格列配置
export interface TableColumn<T = Record<string, unknown>> {
    name: string;
    label: string;
    field: string | ((row: T) => unknown);
    align?: 'left' | 'center' | 'right';
    sortable?: boolean;
    sort?: (a: unknown, b: unknown, rowA: T, rowB: T) => number;
    format?: (val: unknown, row: T) => string;
    style?: string;
    classes?: string;
    headerStyle?: string;
    headerClasses?: string;
}

// 分页配置
export interface PaginationConfig {
    page: number;
    rowsPerPage: number;
    sortBy?: string;
    descending?: boolean;
    rowsNumber?: number;
}

// 导航链接
export interface NavLink {
    title: string;
    caption?: string;
    icon?: string;
    link?: string;
    to?: string;
    href?: string;
    external?: boolean;
    children?: NavLink[];
    disabled?: boolean;
    separator?: boolean;
}

// 面包屑项
export interface BreadcrumbItem {
    label: string;
    icon?: string;
    to?: string;
    href?: string;
    disable?: boolean;
}

// 加载状态
export interface LoadingState {
    loading: boolean;
    message?: string;
}

// 错误状态
export interface ErrorState {
    hasError: boolean;
    message?: string;
    details?: string;
    code?: string | number;
}

// 页面状态组合
export interface PageState extends LoadingState, ErrorState {
    initialized: boolean;
}

// 主题配置
export interface ThemeConfig {
    dark: boolean;
    primary: string;
    secondary: string;
    accent: string;
    positive: string;
    negative: string;
    warning: string;
    info: string;
}

// 布局配置
export interface LayoutConfig {
    drawerOpen: boolean;
    miniState: boolean;
    showHeader: boolean;
    showFooter: boolean;
    headerHeight: number;
    footerHeight: number;
}

// 搜索过滤器
export interface SearchFilter {
    keyword?: string;
    category?: string;
    status?: string;
    dateFrom?: string;
    dateTo?: string;
    [key: string]: string | number | boolean | undefined;
}

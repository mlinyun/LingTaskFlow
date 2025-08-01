/**
 * API 相关类型定义
 * 包含API响应格式、错误类型、请求类型等
 */

// 标准化API响应格式
export interface StandardAPIResponse<T = unknown> {
    success: boolean;
    message: string;
    data: T;
    error: {
        code?: string;
        details?: Record<string, unknown>;
    } | null;
    meta: Record<string, unknown>;
    timestamp: string;
}

// API调用错误类型
export interface APIError {
    message: string;
    status?: number;
    errorData?: Record<string, unknown>;
    code?: string;
}

// 自定义错误类型
export interface CustomError extends Error {
    errorData?: Record<string, unknown>;
    timestamp?: string;
    status?: number;
}

// 分页数据类型
export interface PaginatedData<T> {
    results: T[];
    pagination: {
        page: number;
        page_size: number;
        total_pages: number;
        total_count: number;
        has_next: boolean;
        has_previous: boolean;
        next_page: number | null;
        previous_page: number | null;
    };
}

// HTTP 请求方法
export type HTTPMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

// API 请求配置
export interface APIRequestConfig {
    url: string;
    method: HTTPMethod;
    data?: unknown;
    params?: Record<string, unknown>;
    headers?: Record<string, string>;
    showError?: boolean;
    showSuccess?: boolean;
}

// 分页元数据类型
export interface PaginationMeta {
    page: number;
    page_size: number;
    total_pages: number;
    total_count: number;
    has_next: boolean;
    has_previous: boolean;
    next_page: number | null;
    previous_page: number | null;
}

// 分页链接类型
export interface PaginationLinks {
    next: string | null;
    previous: string | null;
    first: string;
    last: string;
}

// 表单验证错误
export interface ValidationError {
    field: string;
    message: string;
    code?: string;
}

// 验证错误集合
export interface ValidationErrors {
    [field: string]: string[] | string;
}

// 错误代码枚举
export enum ErrorCode {
    VALIDATION_ERROR = 'VALIDATION_ERROR',
    AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR',
    AUTHORIZATION_ERROR = 'AUTHORIZATION_ERROR',
    NOT_FOUND = 'NOT_FOUND',
    SERVER_ERROR = 'SERVER_ERROR',
    NETWORK_ERROR = 'NETWORK_ERROR',
    TIMEOUT_ERROR = 'TIMEOUT_ERROR',
}

// HTTP状态码枚举
export enum HTTPStatus {
    OK = 200,
    CREATED = 201,
    NO_CONTENT = 204,
    BAD_REQUEST = 400,
    UNAUTHORIZED = 401,
    FORBIDDEN = 403,
    NOT_FOUND = 404,
    METHOD_NOT_ALLOWED = 405,
    CONFLICT = 409,
    UNPROCESSABLE_ENTITY = 422,
    INTERNAL_SERVER_ERROR = 500,
    BAD_GATEWAY = 502,
    SERVICE_UNAVAILABLE = 503,
    GATEWAY_TIMEOUT = 504,
}

/**
 * 认证相关类型定义
 * 包含用户信息、认证数据、登录凭据等
 */

// 用户基础信息接口
export interface User {
    id: number;
    username: string;
    email: string;
    date_joined?: string;
    last_login?: string;
    profile?: UserProfile;
}

// 用户详情配置接口
export interface UserProfile {
    user?: User;
    avatar?: string;
    avatar_url?: string;
    timezone: string;
    task_count: number;
    completed_task_count: number;
    completion_rate: number;
    theme_preference: string;
    email_notifications: boolean;
    created_at?: string;
    updated_at?: string;
}

// JWT Token 信息
export interface TokenInfo {
    access: string;
    refresh: string;
    expires_in: number;
    token_type: string;
}

// 认证数据接口（登录/注册成功后的数据）
export interface AuthData {
    user: User;
    tokens: TokenInfo;
}

// 登录凭据
export interface LoginCredentials {
    username: string;
    password: string;
    remember_me?: boolean;
}

// 注册数据
export interface RegisterData {
    username: string;
    email: string;
    password: string;
    password_confirm: string;
    first_name?: string;
    last_name?: string;
}

// 注册响应
export interface RegisterResponse {
    message: string;
    user: {
        id: number;
        username: string;
        email: string;
    };
}

// 认证操作响应
export interface AuthResponse {
    success: boolean;
    message: string;
}

// 安全信息（可选，用于显示登录提醒等）
export interface SecurityInfo {
    suspicious_login?: boolean;
    message?: string;
    previous_failures?: number;
}

// 完整的登录响应（包含安全信息）
export interface LoginResponse extends AuthData {
    security_info?: SecurityInfo;
}

// 用户状态枚举
export enum UserStatus {
    ACTIVE = 'active',
    INACTIVE = 'inactive',
    SUSPENDED = 'suspended',
}

// 主题偏好枚举
export enum ThemePreference {
    LIGHT = 'light',
    DARK = 'dark',
    AUTO = 'auto',
}

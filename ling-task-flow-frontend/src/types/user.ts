/**
 * 用户相关类型定义
 */

export interface User {
    id: number;
    username: string;
    email: string;
    first_name?: string;
    last_name?: string;
    profile?: UserProfile;
}

export interface UserProfile {
    task_count: number;
    completed_task_count: number;
    bio?: string;
    avatar?: string;
    avatar_url?: string;
    nickname?: string;
    phone?: string;
    timezone?: string;
    theme_preference?: string;
    language?: string;
    email_notifications?: boolean;
    created_at?: string;
    updated_at?: string;
}

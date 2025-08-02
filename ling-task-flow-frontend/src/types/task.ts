/**
 * 任务相关类型定义
 */

export interface Task {
    id: number;
    title: string;
    description?: string;
    status: TaskStatus;
    priority: TaskPriority;
    tags: string[];
    due_date?: string;
    completed_at?: string;
    is_deleted: boolean;
    deleted_at?: string;
    created_at: string;
    updated_at: string;
    user: number;
}

export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled';
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface TaskCreateData {
    title: string;
    description?: string;
    status?: TaskStatus;
    priority?: TaskPriority;
    tags?: string[];
    due_date?: string;
}

export interface TaskUpdateData {
    title?: string;
    description?: string;
    status?: TaskStatus;
    priority?: TaskPriority;
    tags?: string[];
    due_date?: string;
}

export interface TaskSearchParams {
    search?: string;
    status?: TaskStatus;
    priority?: TaskPriority;
    tags?: string[];
    due_date_from?: string;
    due_date_to?: string;
    ordering?: string;
    include_deleted?: boolean;
}

export interface TaskStats {
    total_tasks: number;
    active_tasks: number;
    completed_tasks: number;
    deleted_tasks: number;
    status_distribution: Record<TaskStatus, number>;
    priority_distribution: Record<TaskPriority, number>;
    completion_rate: number;
    tags_distribution: Record<string, number>;
    recent_activity: TaskActivity[];
}

export interface TaskActivity {
    id: number;
    task_id: number;
    task_title: string;
    action: 'created' | 'updated' | 'completed' | 'deleted' | 'restored';
    timestamp: string;
}

/**
 * 任务相关类型定义
 */

export interface Task {
    id: string; // 后端使用UUID，应该是字符串
    title: string;
    description?: string;
    status: TaskStatus;
    priority: TaskPriority;
    tags: string; // 逗号分隔的标签列表
    tags_list?: string[]; // 后端提供的标签数组（只读）
    due_date?: string;
    completed_at?: string;
    is_deleted: boolean;
    deleted_at?: string;
    created_at: string;
    updated_at: string;
    owner: number; // 修正字段名从user改为owner
}

export type TaskStatus = 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED' | 'ON_HOLD';
export type TaskPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';

export interface TaskCreateData {
    title: string;
    description?: string;
    status?: TaskStatus;
    priority?: TaskPriority;
    tags?: string; // 改为字符串，逗号分隔的标签列表
    due_date?: string;
}

export interface TaskUpdateData {
    title?: string;
    description?: string;
    status?: TaskStatus;
    priority?: TaskPriority;
    tags?: string; // 改为字符串，逗号分隔的标签列表
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

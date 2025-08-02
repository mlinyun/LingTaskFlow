/**
 * 业务核心类型定义
 * 包含任务、项目、标签等业务实体类型
 */

// 任务优先级枚举
export enum TaskPriority {
    LOW = 'LOW',
    MEDIUM = 'MEDIUM',
    HIGH = 'HIGH',
    URGENT = 'URGENT',
}

// 任务状态枚举
export enum TaskStatus {
    PENDING = 'PENDING',
    IN_PROGRESS = 'IN_PROGRESS',
    COMPLETED = 'COMPLETED',
    CANCELLED = 'CANCELLED',
    ON_HOLD = 'ON_HOLD',
}

// 项目状态枚举
export enum ProjectStatus {
    PLANNING = 'planning',
    ACTIVE = 'active',
    ON_HOLD = 'on_hold',
    COMPLETED = 'COMPLETED',
    ARCHIVED = 'archived',
}

// 标签颜色枚举
export enum TagColor {
    RED = 'red',
    PINK = 'pink',
    PURPLE = 'purple',
    BLUE = 'blue',
    CYAN = 'cyan',
    TEAL = 'teal',
    GREEN = 'green',
    LIME = 'lime',
    YELLOW = 'yellow',
    ORANGE = 'orange',
    GREY = 'grey',
}

// 标签接口
export interface Tag {
    id: number;
    name: string;
    color: TagColor;
    description?: string;
    created_at: string;
    updated_at: string;
}

// 项目接口
export interface Project {
    id: number;
    name: string;
    description?: string;
    status: ProjectStatus;
    priority: TaskPriority;
    start_date?: string;
    end_date?: string;
    deadline?: string;
    owner_id: number;
    owner?: User;
    tags?: Tag[];
    task_count?: number;
    completed_task_count?: number;
    completion_rate?: number;
    created_at: string;
    updated_at: string;
}

// 任务接口
export interface Task {
    id: number;
    title: string;
    description?: string;
    status: TaskStatus;
    priority: TaskPriority;
    due_date?: string;
    estimated_hours?: number;
    actual_hours?: number;
    project_id?: number;
    project?: Project;
    assignee_id?: number;
    assignee?: User;
    tags?: Tag[];
    subtasks?: Task[];
    parent_task_id?: number;
    parent_task?: Task;
    completion_rate?: number;
    created_at: string;
    updated_at: string;
    completed_at?: string;
}

// 任务创建/更新数据
export interface TaskFormData {
    title: string;
    description?: string;
    status?: TaskStatus;
    priority: TaskPriority;
    due_date?: string;
    estimated_hours?: number;
    project_id?: number;
    assignee_id?: number;
    tag_ids?: number[];
    parent_task_id?: number;
}

// 项目创建/更新数据
export interface ProjectFormData {
    name: string;
    description?: string;
    status?: ProjectStatus;
    priority: TaskPriority;
    start_date?: string;
    end_date?: string;
    deadline?: string;
    tag_ids?: number[];
}

// 标签创建/更新数据
export interface TagFormData {
    name: string;
    color: TagColor;
    description?: string;
}

// 任务统计数据
export interface TaskStats {
    total_tasks: number;
    completed_tasks: number;
    in_progress_tasks: number;
    overdue_tasks: number;
    completion_rate: number;
    average_completion_time: number;
}

// 项目统计数据
export interface ProjectStats {
    total_projects: number;
    active_projects: number;
    completed_projects: number;
    on_hold_projects: number;
    completion_rate: number;
}

// 时间跟踪记录
export interface TimeEntry {
    id: number;
    task_id: number;
    task?: Task;
    user_id: number;
    user?: User;
    description?: string;
    hours: number;
    date: string;
    created_at: string;
    updated_at: string;
}

// 时间跟踪表单数据
export interface TimeEntryFormData {
    task_id: number;
    description?: string;
    hours: number;
    date: string;
}

// 评论接口
export interface Comment {
    id: number;
    content: string;
    task_id?: number;
    project_id?: number;
    author_id: number;
    author?: User;
    created_at: string;
    updated_at: string;
}

// 评论表单数据
export interface CommentFormData {
    content: string;
    task_id?: number;
    project_id?: number;
}

// 过滤器选项
export interface TaskFilter {
    status?: TaskStatus[];
    priority?: TaskPriority[];
    project_id?: number;
    assignee_id?: number;
    tag_ids?: number[];
    due_date_from?: string;
    due_date_to?: string;
    overdue_only?: boolean;
}

export interface ProjectFilter {
    status?: ProjectStatus[];
    priority?: TaskPriority[];
    owner_id?: number;
    tag_ids?: number[];
    start_date_from?: string;
    start_date_to?: string;
    end_date_from?: string;
    end_date_to?: string;
}

// 导入声明（引用auth.ts中的User类型）
import type { User } from './auth';

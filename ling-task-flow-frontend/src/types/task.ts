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
    due_date?: string;
    completed_at?: string;
    is_deleted: boolean;
    deleted_at?: string;
    created_at: string;
    updated_at: string;
    owner: number; // 修正字段名从user改为owner
    owner_username?: string; // 负责人用户名，用于显示
    order?: number; // 排序字段，用于拖拽排序
    is_overdue: boolean; // 是否逾期，来自后端序列化器
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
    created_date_from?: string;
    created_date_to?: string;
    updated_date_from?: string;
    updated_date_to?: string;
    owner?: number;
    assigned_to?: number;
    has_due_date?: boolean;
    is_overdue?: boolean;
    progress_min?: number;
    progress_max?: number;
    category?: string;
    ordering?: string;
    include_deleted?: boolean;
}

export interface SavedSearch {
    id: string;
    name: string;
    description?: string;
    params: TaskSearchParams;
    created_at: string;
    updated_at: string;
}

export interface SearchHistory {
    id: string;
    query: string;
    params: TaskSearchParams;
    results_count: number;
    searched_at: string;
}

export interface TaskStats {
    basic_stats: {
        total_tasks: number;
        completed_tasks: number;
        completion_rate: number;
        overdue_tasks: number;
        overdue_rate: number;
        average_progress: number;
        total_estimated_hours: number;
        total_actual_hours: number;
        efficiency_rate: number;
    };
    status_distribution: Record<
        string,
        {
            name: string;
            count: number;
            percentage: number;
        }
    >;
    priority_distribution: Record<
        string,
        {
            name: string;
            count: number;
            percentage: number;
        }
    >;
    category_stats: Array<{
        category: string;
        count: number;
        percentage: number;
    }>;
    time_trends: {
        trend_data: Array<[string, number]>;
        trend_summary: {
            type: string;
            data_points: number;
        };
    };
    workload_stats: {
        owned_tasks: {
            total: number;
            completed: number;
            completion_rate: number;
        };
        assigned_tasks: {
            total: number;
            completed: number;
            completion_rate: number;
        };
        status_workload: Record<string, number>;
        total_active_tasks: number;
    };
    progress_analysis: {
        distribution: Array<{
            range: string;
            label: string;
            count: number;
            percentage: number;
        }>;
        average_progress: number;
        tasks_in_progress: number;
        tasks_completed: number;
        tasks_not_started: number;
    };
    overdue_analysis: {
        total_overdue: number;
        overdue_rate: number;
        upcoming_due: number;
        overdue_by_duration: Array<{
            duration: string;
            count: number;
        }>;
        most_overdue_task: Task | null;
    };
    popular_tags: Array<{
        tag: string;
        count: number;
        percentage: number;
    }>;
    metadata: {
        period: string;
        date_field: string;
        include_deleted: boolean;
        generated_at: string;
        total_tasks_analyzed: number;
        user_id: number;
        username: string;
    };
}

export interface TaskActivity {
    id: number;
    task_id: number;
    task_title: string;
    action: 'created' | 'updated' | 'completed' | 'deleted' | 'restored';
    timestamp: string;
}

export interface TrashStats {
    total_deleted_tasks: number;
    can_be_restored: number;
    oldest_deleted?: string; // ISO date string
}

export interface TrashResponse {
    tasks: Task[];
    total: number;
    trashStats: TrashStats;
}

// 详细状态分布统计接口
export interface StatusDistribution {
    basic_distribution: Array<{
        status: string;
        status_display: string;
        count: number;
        percentage: number;
        efficiency_score?: number;
    }>;
    transition_analysis?: {
        common_transitions: Array<{
            from_status: string;
            to_status: string;
            transition_count: number;
            frequency: number;
        }>;
        transition_efficiency: {
            average_transition_time: number;
            fastest_transitions: Array<{
                from_status: string;
                to_status: string;
                average_time: number;
            }>;
        };
    };
    duration_analysis?: {
        status_duration: Array<{
            status: string;
            average_duration_hours: number;
            median_duration_hours: number;
            tasks_count: number;
        }>;
        efficiency_metrics: {
            total_active_time: number;
            average_completion_time: number;
            efficiency_rating: string;
        };
    };
    trend_analysis: {
        status_trends: Array<{
            status: string;
            trend_data: Array<[string, number]>;
            trend_direction: 'up' | 'down' | 'stable';
        }>;
        period_comparison: {
            current_period: Record<string, number>;
            previous_period: Record<string, number>;
            percentage_change: Record<string, number>;
        };
    };
    metadata: {
        period: string;
        date_field: string;
        include_deleted: boolean;
        generated_at: string;
        total_tasks_analyzed: number;
    };
}

// 详细标签分布统计接口
export interface TagDistribution {
    basic_distribution: Array<{
        tag: string;
        count: number;
        percentage: number;
        usage_score: number;
    }>;
    usage_analysis?: {
        tags_by_status: Array<{
            tag: string;
            status_distribution: Record<string, number>;
            completion_rate: number;
        }>;
        tags_by_priority: Array<{
            tag: string;
            priority_distribution: Record<string, number>;
            average_priority_score: number;
        }>;
    };
    combination_analysis?: {
        popular_combinations: Array<{
            tags: string[];
            count: number;
            combination_score: number;
        }>;
        tag_correlation: Array<{
            tag1: string;
            tag2: string;
            correlation_strength: number;
            co_occurrence_count: number;
        }>;
    };
    efficiency_analysis?: {
        tag_efficiency: Array<{
            tag: string;
            completion_rate: number;
            average_completion_time: number;
            efficiency_rating: 'high' | 'medium' | 'low';
        }>;
        performance_insights: {
            most_efficient_tags: string[];
            least_efficient_tags: string[];
            recommendations: string[];
        };
    };
    trend_analysis: {
        tag_trends: Array<{
            tag: string;
            trend_data: Array<[string, number]>;
            trend_direction: 'rising' | 'falling' | 'stable';
        }>;
        popularity_changes: Array<{
            tag: string;
            current_usage: number;
            previous_usage: number;
            change_percentage: number;
        }>;
    };
    health_metrics: {
        total_unique_tags: number;
        average_tags_per_task: number;
        tag_diversity_score: number;
        recommended_cleanup: string[];
    };
    metadata: {
        period: string;
        date_field: string;
        include_deleted: boolean;
        min_frequency: number;
        top_n: number;
        generated_at: string;
        total_tasks_analyzed: number;
    };
}

// 详细时间分布统计接口
export interface TimeDistribution {
    basic_distribution: {
        creation_pattern: Array<{
            time_label: string;
            count: number;
            percentage: number;
        }>;
        completion_pattern: Array<{
            time_label: string;
            count: number;
            percentage: number;
        }>;
        activity_pattern: Array<{
            time_label: string;
            activity_count: number;
            task_count: number;
        }>;
    };
    hourly_analysis?: {
        creation_by_hour: Array<{
            hour: number;
            count: number;
            percentage: number;
        }>;
        completion_by_hour: Array<{
            hour: number;
            count: number;
            efficiency_score: number;
        }>;
        peak_hours: {
            most_productive: number[];
            least_productive: number[];
            optimal_work_window: [number, number];
        };
    };
    daily_analysis?: {
        weekday_distribution: Array<{
            weekday: number;
            weekday_name: string;
            creation_count: number;
            completion_count: number;
            efficiency_score: number;
        }>;
        monthly_distribution: Array<{
            month: number;
            month_name: string;
            creation_count: number;
            completion_count: number;
            workload_score: number;
        }>;
    };
    workload_analysis?: {
        time_based_workload: Array<{
            time_period: string;
            active_tasks: number;
            completed_tasks: number;
            workload_intensity: 'light' | 'moderate' | 'heavy';
        }>;
        efficiency_by_time: Array<{
            time_period: string;
            completion_rate: number;
            average_completion_time: number;
            efficiency_rating: number;
        }>;
    };
    trend_analysis?: {
        creation_trends: Array<{
            period: string;
            count: number;
            trend_direction: 'up' | 'down' | 'stable';
        }>;
        completion_trends: Array<{
            period: string;
            count: number;
            efficiency_change: number;
        }>;
        seasonal_patterns: {
            detected_patterns: string[];
            seasonal_recommendations: string[];
        };
    };
    insights: {
        best_work_times: string[];
        productivity_patterns: string[];
        time_management_tips: string[];
        workload_warnings: string[];
    };
    metadata: {
        period: string;
        analysis_type: string;
        date_field: string;
        timezone: string;
        include_deleted: boolean;
        generated_at: string;
        total_tasks_analyzed: number;
    };
}

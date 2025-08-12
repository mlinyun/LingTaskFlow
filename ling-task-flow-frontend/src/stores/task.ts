import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from 'boot/axios';
import { handleApiError } from 'src/utils/errorHandler';
import type {
    Task,
    TaskCreateData,
    TaskUpdateData,
    TaskSearchParams,
    TaskStats,
    TrashStats,
    StatusDistribution,
    TagDistribution,
    TimeDistribution,
    TaskStatus,
} from '../types';

export const useTaskStore = defineStore('task', () => {
    // 状态定义
    const tasks = ref<Task[]>([]);
    const totalTasks = ref(0);
    const currentPage = ref(1);
    const pageSize = ref(20);
    const loading = ref(false);
    const searchParams = ref<TaskSearchParams>({});
    const selectedTasks = ref<string[]>([]);
    const taskStats = ref<TaskStats | null>(null);

    // 加载状态定义
    const loadingStates = ref<{
        fetchingTasks: boolean;
        fetchingStats: boolean;
    }>({
        fetchingTasks: false,
        fetchingStats: false,
    });

    // 拖拽排序相关状态
    const isDragging = ref(false);
    const draggedTask = ref<Task | null>(null);

    // 计算属性
    const totalPages = computed(() =>
        Math.ceil(totalTasks.value / pageSize.value),
    );
    const hasNextPage = computed(() => currentPage.value < totalPages.value);
    const hasPrevPage = computed(() => currentPage.value > 1);

    const selectedTasksCount = computed(() => selectedTasks.value.length);

    // 任务列表筛选
    const activeTasks = computed(() =>
        tasks.value.filter(task => !task.deleted_at),
    );
    const deletedTasks = computed(() =>
        tasks.value.filter(task => task.deleted_at),
    );

    const tasksByStatus = computed(() => {
        const grouped: Record<string, Task[]> = {};
        tasks.value.forEach(task => {
            const key = task.status as unknown as string;
            (grouped[key] ??= []).push(task);
        });
        return grouped;
    });

    const tasksByPriority = computed(() => {
        const grouped: Record<string, Task[]> = {};
        tasks.value.forEach(task => {
            const key = task.priority as unknown as string;
            (grouped[key] ??= []).push(task);
        });
        return grouped;
    });

    // API 调用方法

    /**
     * 获取任务列表
     */
    const fetchTasks = async (params: TaskSearchParams = {}) => {
        loading.value = true;
        loadingStates.value.fetchingTasks = true;
        try {
            const queryParams = {
                page: currentPage.value,
                page_size: pageSize.value,
                ...searchParams.value,
                ...params,
            };

            const response = await api.get('/tasks/', {
                params: queryParams,
            });

            // axios拦截器已经处理了标准化响应，直接使用data和meta
            const taskData = response.data || [];
            const meta = (response as unknown as { meta?: Record<string, unknown> }).meta || {};
            const pagination = meta.pagination as
                | {
                      page?: number;
                      page_size?: number;
                      total_pages?: number;
                      total_count?: number;
                      has_next?: boolean;
                      has_previous?: boolean;
                      next_page?: number | null;
                      previous_page?: number | null;
                  }
                | undefined;

            tasks.value = taskData;
            if (pagination) {
                totalTasks.value = pagination.total_count || 0;
            } else {
                totalTasks.value = 0;
            }

            // 返回标准化的分页数据格式，保持向后兼容
            return {
                results: taskData,
                pagination: pagination || {
                    page: currentPage.value,
                    page_size: pageSize.value,
                    total_pages: 1,
                    total_count: 0,
                    has_next: false,
                    has_previous: false,
                    next_page: null,
                    previous_page: null,
                },
            };
        } catch (error) {
            console.error('获取任务列表失败:', error);

            // 使用统一的错误处理
            handleApiError(
                error as Error & { response?: { status: number; data?: Record<string, unknown> } },
                {
                    showNotification: true,
                    autoRetry: true,
                    maxRetries: 2,
                },
            );

            throw error;
        } finally {
            loading.value = false;
            loadingStates.value.fetchingTasks = false;
        }
    };

    /**
     * 获取单个任务详情
     */
    const fetchTaskById = async (id: string): Promise<Task> => {
        try {
            const response = await api.get(`/tasks/${id}/`);

            // axios拦截器已经处理了标准化响应格式
            const task = response.data;

            // 更新本地缓存中的任务
            const index = tasks.value.findIndex(t => t.id === id);
            if (index !== -1) {
                tasks.value[index] = task;
            }

            return task;
        } catch (error) {
            console.error('获取任务详情失败:', error);
            throw error;
        }
    };

    /**
     * 创建新任务
     */
    const createTask = async (taskData: TaskCreateData): Promise<Task> => {
        try {
            const response = await api.post('/tasks/', taskData);

            // axios拦截器已经处理了标准化响应格式
            const newTask = response.data;

            // 乐观更新：将新任务添加到列表开头
            tasks.value.unshift(newTask);
            totalTasks.value += 1;

            return newTask;
        } catch (error) {
            console.error('创建任务失败:', error);
            throw error;
        }
    };

    /**
     * 更新任务
     */
    const updateTask = async (id: string, taskData: TaskUpdateData): Promise<Task> => {
        try {
            const response = await api.patch(`/tasks/${id}/`, taskData);

            // axios拦截器已经处理了标准化响应格式
            const updatedTask = response.data;

            // 乐观更新：更新本地任务数据
            const index = tasks.value.findIndex(task => task.id === id);
            if (index !== -1) {
                tasks.value[index] = updatedTask;
            }

            return updatedTask;
        } catch (error) {
            console.error('更新任务失败:', error);
            throw error;
        }
    };

    /**
     * 软删除任务
     */
    const deleteTask = async (id: string): Promise<void> => {
        try {
            await api.delete(`/tasks/${id}/`);

            // 乐观更新：标记任务为已删除
            const index = tasks.value.findIndex(task => task.id === id);
            if (index !== -1 && tasks.value[index]) {
                tasks.value[index].is_deleted = true;
                tasks.value[index].deleted_at = new Date().toISOString();
            }
        } catch (error) {
            console.error('删除任务失败:', error);
            throw error;
        }
    };

    /**
     * 恢复已删除的任务
     */
    const restoreTask = async (id: string): Promise<Task> => {
        try {
            const response = await api.post(`/tasks/${id}/restore/`);

            // axios拦截器已经处理了标准化响应格式
            const restoredTask = response.data;

            // 乐观更新：恢复任务状态
            const index = tasks.value.findIndex(task => task.id === id);
            if (index !== -1) {
                tasks.value[index] = restoredTask;
            }

            return restoredTask;
        } catch (error) {
            console.error('恢复任务失败:', error);
            throw error;
        }
    };

    /**
     * 永久删除任务
     */
    const permanentDeleteTask = async (id: string): Promise<void> => {
        try {
            await api.delete(`/tasks/${id}/permanent/`);

            // 从本地列表中移除任务
            const index = tasks.value.findIndex(task => task.id === id);
            if (index !== -1) {
                tasks.value.splice(index, 1);
                totalTasks.value -= 1;
            }
        } catch (error) {
            console.error('永久删除任务失败:', error);
            throw error;
        }
    };

    /**
     * 批量操作任务
     */
    const batchUpdateTasks = async (
        taskIds: string[],
        updateData: Partial<TaskUpdateData>,
    ): Promise<void> => {
        try {
            const promises = taskIds.map(id => updateTask(id, updateData));
            await Promise.all(promises);
        } catch (error) {
            console.error('批量更新任务失败:', error);
            throw error;
        }
    };

    const batchDeleteTasks = async (taskIds: string[]): Promise<void> => {
        try {
            const promises = taskIds.map(id => deleteTask(id));
            await Promise.all(promises);
        } catch (error) {
            console.error('批量删除任务失败:', error);
            throw error;
        }
    };

    /**
     * 批量恢复任务
     */
    const batchRestoreTasks = async (taskIds: string[]): Promise<void> => {
        try {
            const response = await api.post('/tasks/bulk_restore/', {
                task_ids: taskIds,
            });

            // 根据响应更新本地状态
            const restoreData = response.data;
            if (restoreData.stats?.successful_restores > 0) {
                // 重新获取任务列表以更新状态
                await fetchTasks();
            }
        } catch (error) {
            console.error('批量恢复任务失败:', error);
            throw error;
        }
    };

    /**
     * 批量更新任务状态（使用统一批量接口 bulk_action）
     */
    const batchUpdateStatus = async (
        taskIds: string[],
        newStatus: TaskStatus,
    ): Promise<{
        successful: number;
        failed: number;
        stats?: Record<string, unknown>;
        failedItems?: Array<{ id: string; error: unknown }>;
    }> => {
        try {
            const response = await api.post('/tasks/bulk_action/', {
                action: 'update_status',
                task_ids: taskIds,
                status: newStatus,
            });

            const resp = response.data;

            // 尝试根据成功项更新本地任务列表
            const successfulItems = (resp?.data?.successful_items || []) as Array<{ data?: Task }>;
            successfulItems.forEach((item) => {
                const updated = item?.data as Task | undefined;
                if (updated && updated.id) {
                    const idx = tasks.value.findIndex(t => t.id === updated.id);
                    if (idx !== -1) {
                        tasks.value[idx] = updated;
                    }
                }
            });

            return {
                successful: resp?.data?.stats?.successful ?? successfulItems.length,
                failed: resp?.data?.stats?.failed ?? (resp?.data?.failed_items?.length || 0),
                stats: resp?.data?.stats,
                failedItems: resp?.data?.failed_items,
            };
        } catch (error) {
            console.error('批量更新任务状态失败:', error);
            throw error;
        }
    };

    /**
     * 批量永久删除任务
     */
    const batchPermanentDeleteTasks = async (taskIds: string[]): Promise<void> => {
        try {
            const promises = taskIds.map(id => permanentDeleteTask(id));
            await Promise.all(promises);
        } catch (error) {
            console.error('批量永久删除任务失败:', error);
            throw error;
        }
    };

    /**
     * 搜索任务
     */
    const searchTasks = async (searchQuery: string): Promise<Task[]> => {
        try {
            const response = await api.get('/tasks/search/', {
                params: { q: searchQuery },
            });

            // axios拦截器已经处理了标准化响应格式
            return response.data || [];
        } catch (error) {
            console.error('搜索任务失败:', error);
            throw error;
        }
    };

    /**
     * 获取回收站任务
     */
    const fetchTrashTasks = async (
        page = 1,
    ): Promise<{
        tasks: Task[];
        total: number;
        trashStats: TrashStats;
    }> => {
        try {
            loading.value = true;
            const response = await api.get('/tasks/trash/', {
                params: {
                    page,
                    page_size: pageSize.value,
                },
            });

            const responseData = response.data;

            // 处理后端的特殊响应结构
            // 后端返回: { data: { data: [...], meta: { pagination: {...} } }, meta: { trash_stats: {...} } }
            let tasks: Task[] = [];
            let total = 0;
            let trashStats: TrashStats = {
                total_deleted_tasks: 0,
                can_be_restored: 0,
            };

            // 解析任务数据
            if (responseData.data) {
                const innerData = responseData.data;

                if (Array.isArray(innerData.data)) {
                    // 分页响应：data.data 是任务数组
                    tasks = innerData.data;
                    total = innerData.meta?.pagination?.total_count || tasks.length;
                } else if (Array.isArray(innerData.results)) {
                    // DRF分页格式：data.results 是任务数组
                    tasks = innerData.results;
                    total = innerData.count || tasks.length;
                } else if (Array.isArray(innerData)) {
                    // 直接是数组
                    tasks = innerData;
                    total = tasks.length;
                }
            }

            // 解析统计数据 - 尝试多个可能的路径
            if (responseData.meta?.trash_stats) {
                trashStats = responseData.meta.trash_stats;
            } else if (responseData.data?.meta?.trash_stats) {
                trashStats = responseData.data.meta.trash_stats;
            } else if (responseData.trash_stats) {
                trashStats = responseData.trash_stats;
            } else {
                // 如果没有统计数据，使用任务数量计算
                trashStats = {
                    total_deleted_tasks: tasks.length,
                    can_be_restored: tasks.length,
                };

                // 如果有任务，找出最早删除的时间
                if (tasks.length > 0) {
                    const oldestTask = tasks.reduce((oldest, task) => {
                        if (!task.deleted_at) return oldest;
                        if (!oldest.deleted_at) return task;
                        return new Date(task.deleted_at) < new Date(oldest.deleted_at)
                            ? task
                            : oldest;
                    });
                    if (oldestTask.deleted_at) {
                        trashStats.oldest_deleted = oldestTask.deleted_at;
                    }
                }
            }

            return {
                tasks,
                total,
                trashStats,
            };
        } catch (error) {
            console.error('获取回收站任务失败:', error);
            throw error;
        } finally {
            loading.value = false;
        }
    };

    /**
     * 清空回收站
     */
    const emptyTrash = async (confirm = false): Promise<void> => {
        try {
            await api.post('/tasks/empty_trash/', {
                confirm,
            });
        } catch (error) {
            console.error('清空回收站失败:', error);
            throw error;
        }
    };

    /**
     * 获取任务统计数据
     */
    const fetchTaskStats = async (): Promise<TaskStats> => {
        loadingStates.value.fetchingStats = true;
        try {
            const response = await api.get('/tasks/stats/');

            // axios拦截器已经处理了标准化响应格式
            const stats = response.data;
            taskStats.value = stats;
            return stats;
        } catch (error) {
            console.error('获取任务统计失败:', error);
            throw error;
        } finally {
            loadingStates.value.fetchingStats = false;
        }
    };

    /**
     * 获取状态分布统计
     */
    const fetchStatusDistribution = async (params?: {
        period?: string;
        include_deleted?: boolean;
        date_field?: string;
        include_transitions?: boolean;
        include_duration?: boolean;
    }): Promise<StatusDistribution> => {
        try {
            const response = await api.get('/tasks/status-distribution/', { params });
            return response.data;
        } catch (error) {
            console.error('获取状态分布失败:', error);
            throw error;
        }
    };

    /**
     * 获取标签分布统计
     */
    const fetchTagDistribution = async (params?: {
        period?: string;
        include_deleted?: boolean;
        date_field?: string;
        include_usage?: boolean;
        include_combination?: boolean;
        include_efficiency?: boolean;
        min_frequency?: number;
        top_n?: number;
    }): Promise<TagDistribution> => {
        try {
            const response = await api.get('/tasks/tag-distribution/', { params });
            return response.data;
        } catch (error) {
            console.error('获取标签分布失败:', error);
            throw error;
        }
    };

    /**
     * 获取时间分布统计
     */
    const fetchTimeDistribution = async (params?: {
        period?: string;
        include_deleted?: boolean;
        analysis_type?: string;
        date_field?: string;
        include_hourly?: boolean;
        include_daily?: boolean;
        include_weekly?: boolean;
        include_monthly?: boolean;
        include_trends?: boolean;
        timezone?: string;
    }): Promise<TimeDistribution> => {
        try {
            const response = await api.get('/tasks/time-distribution/', { params });
            return response.data;
        } catch (error) {
            console.error('获取时间分布失败:', error);
            throw error;
        }
    };

    /**
     * 批量更新任务排序
     */
    const updateTasksOrder = async (
        tasksWithOrder: Array<{ id: string; sort_order: number }>,
    ): Promise<void> => {
        try {
            const response = await api.patch('/tasks/batch-sort-order/', {
                tasks: tasksWithOrder,
            });

            // 更新本地任务的排序
            tasksWithOrder.forEach(({ id, sort_order }) => {
                const task = tasks.value.find(t => t.id === id);
                if (task) {
                    task.order = sort_order;
                }
            });

            // 重新排序本地任务列表
            tasks.value.sort((a, b) => (a.order || 0) - (b.order || 0));

            console.log('任务排序更新成功:', response.data);
        } catch (error) {
            console.error('批量更新任务排序失败:', error);
            throw error;
        }
    };

    // 状态管理方法

    /**
     * 设置搜索参数
     */
    const setSearchParams = (params: TaskSearchParams) => {
        searchParams.value = { ...params }; // 直接替换而非合并
        currentPage.value = 1; // 重置到第一页
    };

    /**
     * 清空搜索参数
     */
    const clearSearchParams = () => {
        searchParams.value = {};
        currentPage.value = 1;
    };

    /**
     * 设置页码
     */
    const setPage = (page: number) => {
        currentPage.value = page;
    };

    /**
     * 设置页面大小
     */
    const setPageSize = (size: number) => {
        pageSize.value = size;
        currentPage.value = 1; // 重置到第一页
    };

    /**
     * 选择/取消选择任务
     */
    const toggleTaskSelection = (taskId: string) => {
        const index = selectedTasks.value.indexOf(taskId);
        if (index === -1) {
            selectedTasks.value.push(taskId);
        } else {
            selectedTasks.value.splice(index, 1);
        }
    };

    /**
     * 全选/取消全选
     */
    const toggleAllTasksSelection = () => {
        if (selectedTasks.value.length === activeTasks.value.length) {
            selectedTasks.value = [];
        } else {
            selectedTasks.value = activeTasks.value.map(task => task.id);
        }
    };

    /**
     * 清空选择
     */
    const clearSelection = () => {
        selectedTasks.value = [];
    };

    /**
     * 重置所有状态
     */
    const resetState = () => {
        tasks.value = [];
        totalTasks.value = 0;
        currentPage.value = 1;
        searchParams.value = {};
        selectedTasks.value = [];
        taskStats.value = null;
        loading.value = false;
    };

    return {
        // 状态
        tasks,
        totalTasks,
        currentPage,
        pageSize,
        loading,
        loadingStates,
        searchParams,
        selectedTasks,
        taskStats,
        isDragging,
        draggedTask,

        // 计算属性
        totalPages,
        hasNextPage,
        hasPrevPage,
        selectedTasksCount,
        activeTasks,
        deletedTasks,
        tasksByStatus,
        tasksByPriority,

        // 方法
        fetchTasks,
        fetchTaskById,
        createTask,
        updateTask,
        deleteTask,
        restoreTask,
        permanentDeleteTask,
        batchUpdateTasks,
        batchDeleteTasks,
        batchRestoreTasks,
        batchUpdateStatus,
        batchPermanentDeleteTasks,
        searchTasks,
        fetchTrashTasks,
        emptyTrash,
        fetchTaskStats,
        fetchStatusDistribution,
        fetchTagDistribution,
        fetchTimeDistribution,
        updateTasksOrder,
        setSearchParams,
        clearSearchParams,
        setPage,
        setPageSize,
        toggleTaskSelection,
        toggleAllTasksSelection,
        clearSelection,
        resetState,
    };
});

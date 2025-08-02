import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from 'boot/axios';
import type { Task, TaskCreateData, TaskUpdateData, TaskSearchParams, TaskStats } from '../types';

export const useTaskStore = defineStore('task', () => {
    // 状态定义
    const tasks = ref<Task[]>([]);
    const totalTasks = ref(0);
    const currentPage = ref(1);
    const pageSize = ref(20);
    const loading = ref(false);
    const searchParams = ref<TaskSearchParams>({});
    const selectedTasks = ref<number[]>([]);
    const taskStats = ref<TaskStats | null>(null);

    // 计算属性
    const totalPages = computed(() => Math.ceil(totalTasks.value / pageSize.value));
    const hasNextPage = computed(() => currentPage.value < totalPages.value);
    const hasPrevPage = computed(() => currentPage.value > 1);
    const selectedTasksCount = computed(() => selectedTasks.value.length);
    const activeTasks = computed(() => tasks.value.filter(task => !task.is_deleted));
    const deletedTasks = computed(() => tasks.value.filter(task => task.is_deleted));

    // 任务状态统计
    const tasksByStatus = computed(() => {
        const statusMap = new Map<string, number>();
        activeTasks.value.forEach(task => {
            const count = statusMap.get(task.status) || 0;
            statusMap.set(task.status, count + 1);
        });
        return statusMap;
    });

    const tasksByPriority = computed(() => {
        const priorityMap = new Map<string, number>();
        activeTasks.value.forEach(task => {
            const count = priorityMap.get(task.priority) || 0;
            priorityMap.set(task.priority, count + 1);
        });
        return priorityMap;
    });

    // API 调用方法

    /**
     * 获取任务列表
     */
    const fetchTasks = async (params: TaskSearchParams = {}) => {
        loading.value = true;
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
            throw error;
        } finally {
            loading.value = false;
        }
    };

    /**
     * 获取单个任务详情
     */
    const fetchTaskById = async (id: number): Promise<Task> => {
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
    const updateTask = async (id: number, taskData: TaskUpdateData): Promise<Task> => {
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
    const deleteTask = async (id: number): Promise<void> => {
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
    const restoreTask = async (id: number): Promise<Task> => {
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
    const permanentDeleteTask = async (id: number): Promise<void> => {
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
        taskIds: number[],
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

    const batchDeleteTasks = async (taskIds: number[]): Promise<void> => {
        try {
            const promises = taskIds.map(id => deleteTask(id));
            await Promise.all(promises);
        } catch (error) {
            console.error('批量删除任务失败:', error);
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
     * 获取任务统计数据
     */
    const fetchTaskStats = async (): Promise<TaskStats> => {
        try {
            const response = await api.get('/tasks/stats/');

            // axios拦截器已经处理了标准化响应格式
            const stats = response.data;
            taskStats.value = stats;
            return stats;
        } catch (error) {
            console.error('获取任务统计失败:', error);
            throw error;
        }
    };

    // 状态管理方法

    /**
     * 设置搜索参数
     */
    const setSearchParams = (params: TaskSearchParams) => {
        searchParams.value = { ...searchParams.value, ...params };
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
    const toggleTaskSelection = (taskId: number) => {
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
        searchParams,
        selectedTasks,
        taskStats,

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
        searchTasks,
        fetchTaskStats,
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

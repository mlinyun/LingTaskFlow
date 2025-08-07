<template>
    <q-page class="task-list-page">
        <!-- 页面头部组件 -->
        <PageHeader
            title-primary="任务管理"
            title-accent="系统"
            subtitle="智能化任务管理，提升工作效率与团队协作"
            :primary-action="{
                icon: 'add',
                label: '新建任务',
                tooltip: '创建新的任务项目 (Ctrl+N)',
            }"
            :secondary-actions="[
                {
                    name: 'refresh',
                    icon: 'refresh',
                    tooltip: '刷新任务列表 (Ctrl+R)',
                    class: 'refresh-btn',
                },
                {
                    name: 'filter',
                    icon: 'filter_list',
                    tooltip: '快速筛选 (Ctrl+F)',
                    class: 'filter-toggle-btn',
                },
            ]"
            @primary-action="openCreateDialog"
            @secondary-action="handleSecondaryAction"
        />

        <!-- 任务筛选面板组件 -->
        <TaskFilterPanel
            v-model:search-query="searchQuery"
            v-model:status-filter="statusFilter"
            v-model:priority-filter="priorityFilter"
            v-model:sort-by="sortBy"
            @filter-change="handleFilterChange"
            @clear-filters="clearFilters"
        />

        <!-- 任务统计组件 -->
        <TaskStatistics
            :total-tasks="taskStore.totalTasks"
            :active-tasks="taskStore.activeTasks.length"
            :completed-tasks="completedTasks"
            :selected-tasks="taskStore.selectedTasksCount"
        />

        <!-- 任务操作按钮组件 -->
        <TaskActionButtons
            :selected-count="taskStore.selectedTasksCount"
            @mark-complete="batchMarkComplete"
            @batch-delete="batchDelete"
            @clear-selection="taskStore.clearSelection"
        />

        <!-- 科技感任务控制台组件 -->
        <TaskConsole
            :total-tasks="taskStore.totalTasks"
            :active-tasks="taskStore.activeTasks.length"
            :selected-tasks="taskStore.selectedTasksCount"
            :select-all="selectAll"
            :indeterminate="indeterminate"
            :view-mode="viewMode"
            :loading="taskStore.loadingStates.fetchingTasks"
            @select-all="handleSelectAll"
            @toggle-view-mode="toggleViewMode"
            @create-task="openCreateDialog"
        >
            <template #task-cards>
                <!-- 任务卡片 -->
                <CyberTaskCard
                    v-for="(task, index) in taskStore.activeTasks"
                    :key="task.id"
                    :task="task"
                    :is-selected="taskStore.selectedTasks.includes(task.id)"
                    :view-mode="viewMode"
                    :data-index="index"
                    @view="handleViewTask"
                    @edit="handleEditTask"
                    @delete="handleDeleteTask"
                    @selection-change="(taskId, selected) => taskStore.toggleTaskSelection(taskId)"
                />
            </template>
        </TaskConsole>

        <!-- 分页 -->
        <div v-if="taskStore.totalPages > 1" class="pagination-section">
            <q-pagination
                v-model="taskStore.currentPage"
                :max="taskStore.totalPages"
                direction-links
                boundary-links
                icon-first="skip_previous"
                icon-last="skip_next"
                icon-prev="fast_rewind"
                icon-next="fast_forward"
                @update:model-value="handlePageChange"
            />
        </div>

        <!-- 任务创建/编辑对话框 -->
        <TaskDialogForm v-model="showTaskDialog" :task="selectedTask" @saved="onTaskSaved" />

        <!-- 任务查看对话框 -->
        <TaskViewDialog
            v-model="showViewDialog"
            :task="viewingTask"
            @edit="handleEditFromView"
            @delete="handleDeleteFromView"
            @status-change="handleStatusChange"
        />
    </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';
import { useTaskStore } from 'stores/task';
import TaskDialogForm from 'components/task-list/TaskDialogForm.vue';
import TaskViewDialog from 'components/task-list/TaskViewDialog.vue';
import type { Task, TaskStatus, TaskPriority, TaskSearchParams } from '../types';
import { useGlobalConfirm } from '../composables/useGlobalConfirm';
import { useComponentShortcuts } from '../composables/useComponentShortcuts';
import CyberTaskCard from 'components/task-list/CyberTaskCard.vue';
import TaskConsole from 'components/task-list/TaskConsole.vue';
import TaskFilterPanel from 'components/task-list/TaskFilterPanel.vue';
import TaskStatistics from 'components/task-list/TaskStatistics.vue';
import TaskActionButtons from 'components/task-list/TaskActionButtons.vue';
import PageHeader from 'components/task-list/PageHeader.vue';

const $q = useQuasar();
const router = useRouter();
const taskStore = useTaskStore();
const confirmDialog = useGlobalConfirm();

// 快捷键管理
useComponentShortcuts({
    context: 'task-list',
    shortcuts: {
        'create-task': {
            key: 'n',
            ctrl: true,
            description: '创建新任务',
            action: () => openCreateDialog(),
        },
        refresh: {
            key: 'r',
            ctrl: true,
            description: '刷新任务列表',
            action: () => {
                loadTasks().catch(console.error);
            },
        },
        search: {
            key: 'f',
            ctrl: true,
            description: '搜索任务',
            action: () => {
                // 聚焦到搜索框
                const searchInput = document.querySelector(
                    'input[placeholder*="搜索"]',
                ) as HTMLInputElement;
                if (searchInput) {
                    searchInput.focus();
                    searchInput.select();
                }
            },
        },
    },
});

// 响应式数据
const searchQuery = ref('');
const statusFilter = ref<TaskStatus | null>(null);
const priorityFilter = ref<TaskPriority | null>(null);
const sortBy = ref('created_at');
const viewMode = ref<'list' | 'grid'>('list');
const showTaskDialog = ref(false);
const selectedTask = ref<Task | null>(null);
const showViewDialog = ref(false);
const viewingTask = ref<Task | null>(null);
const currentSearchParams = ref<Partial<TaskSearchParams>>({});

// 计算属性
const selectAll = computed({
    get: () => {
        const activeTasks = taskStore.activeTasks;
        return activeTasks.length > 0 && taskStore.selectedTasks.length === activeTasks.length;
    },
    set: (value: boolean) => {
        if (value) {
            taskStore.toggleAllTasksSelection();
        } else {
            taskStore.clearSelection();
        }
    },
});

const indeterminate = computed(() => {
    const selectedCount = taskStore.selectedTasksCount;
    const totalCount = taskStore.activeTasks.length;
    return selectedCount > 0 && selectedCount < totalCount;
});

// 已完成任务数量
const completedTasks = computed(() => {
    return taskStore.activeTasks.filter(task => task.status === 'COMPLETED').length;
});

// 方法
const loadTasks = async () => {
    try {
        await taskStore.fetchTasks();
    } catch {
        $q.notify({
            type: 'negative',
            message: '加载任务失败',
            position: 'top',
        });
    }
};

const handleFilterChange = () => {
    updateSearchParams();
};

// 统一的搜索参数更新函数
const updateSearchParams = () => {
    const params: TaskSearchParams = {};

    // 基础筛选参数 - 只添加有效值
    if (searchQuery.value && searchQuery.value.trim()) {
        params.search = searchQuery.value.trim();
    }
    if (statusFilter.value !== null && statusFilter.value !== undefined) {
        params.status = statusFilter.value;
    }
    if (priorityFilter.value !== null && priorityFilter.value !== undefined) {
        params.priority = priorityFilter.value;
    }
    if (sortBy.value) {
        params.ordering = sortBy.value;
    }

    // 完全替换搜索参数，而不是合并
    taskStore.setSearchParams(params);
    currentSearchParams.value = params;
    void loadTasks();
};

const clearFilters = () => {
    // 清空所有筛选器
    searchQuery.value = '';
    statusFilter.value = null;
    priorityFilter.value = null;
    sortBy.value = 'created_at';

    // 清空Store中的搜索参数
    taskStore.clearSearchParams();
    currentSearchParams.value = {};
    void loadTasks();
};

const handleSelectAll = () => {
    taskStore.toggleAllTasksSelection();
};

const toggleViewMode = () => {
    viewMode.value = viewMode.value === 'list' ? 'grid' : 'list';
};

const handlePageChange = (page: number) => {
    taskStore.setPage(page);
    void loadTasks();
};

const handleEditTask = (task: Task) => {
    openEditDialog(task);
};

const handleViewTask = (task: Task) => {
    viewingTask.value = task;
    showViewDialog.value = true;
};

const handleEditFromView = (task: Task) => {
    // 关闭查看对话框，打开编辑对话框
    showViewDialog.value = false;
    openEditDialog(task);
};

const handleDeleteFromView = (task: Task) => {
    // 关闭查看对话框，执行删除操作
    showViewDialog.value = false;
    void handleDeleteTask(task);
};

const handleStatusChange = async (taskId: string, status: TaskStatus) => {
    try {
        await taskStore.updateTask(taskId, { status });
        $q.notify({
            type: 'positive',
            message: '任务状态已更新',
            position: 'top',
        });
    } catch {
        $q.notify({
            type: 'negative',
            message: '更新任务状态失败',
            position: 'top',
        });
    }
};

const handleDeleteTask = async (task: Task) => {
    try {
        const confirmed = await confirmDialog.confirmWarning(
            '删除任务',
            `确定要删除任务"${task.title}"吗？`,
            {
                details: '任务删除后将移至回收站，可在30天内恢复。',
                warningText: '删除后可以在回收站中找到',
                confirmText: '删除',
                confirmIcon: 'delete',
            },
        );

        if (confirmed) {
            confirmDialog.setLoading(true, '正在删除任务...');
            try {
                await taskStore.deleteTask(task.id);

                // 显示成功通知，包含撤销选项
                const notif = $q.notify({
                    type: 'positive',
                    message: `任务"${task.title}"已删除`,
                    position: 'top',
                    timeout: 5000,
                    actions: [
                        {
                            label: '撤销',
                            color: 'white',
                            handler: () => {
                                void (async () => {
                                    try {
                                        await taskStore.restoreTask(task.id);
                                        $q.notify({
                                            type: 'info',
                                            message: '任务已恢复',
                                            position: 'top',
                                            timeout: 3000,
                                        });
                                    } catch {
                                        $q.notify({
                                            type: 'negative',
                                            message: '恢复任务失败',
                                            position: 'top',
                                        });
                                    }
                                })();
                            },
                        },
                    ],
                });

                // 5秒后自动清除通知（如果用户没有撤销）
                setTimeout(() => {
                    if (notif) {
                        notif();
                    }
                }, 5000);
            } catch {
                $q.notify({
                    type: 'negative',
                    message: '删除任务失败',
                    position: 'top',
                });
            } finally {
                confirmDialog.setLoading(false);
            }
        }
    } catch (error) {
        console.error('删除任务失败:', error);
    }
};

const batchMarkComplete = async () => {
    try {
        await taskStore.batchUpdateTasks(taskStore.selectedTasks, { status: 'COMPLETED' });
        taskStore.clearSelection();
        $q.notify({
            type: 'positive',
            message: '任务已标记为完成',
            position: 'top',
        });
    } catch {
        $q.notify({
            type: 'negative',
            message: '批量操作失败',
            position: 'top',
        });
    }
};

const batchDelete = async () => {
    const selectedCount = taskStore.selectedTasksCount;
    const selectedTaskIds = [...taskStore.selectedTasks]; // 创建副本

    try {
        const confirmed = await confirmDialog.confirmWarning(
            '批量删除任务',
            `确定要删除选中的 ${selectedCount} 个任务吗？`,
            {
                details: '任务删除后将移至回收站，可在30天内恢复。',
                warningText: '删除后可以在回收站中找到',
                confirmText: '批量删除',
                confirmIcon: 'delete',
            },
        );

        if (confirmed) {
            confirmDialog.setLoading(true, '正在删除任务...');
            try {
                await taskStore.batchDeleteTasks(selectedTaskIds);
                taskStore.clearSelection();

                // 显示成功通知
                $q.notify({
                    type: 'positive',
                    message: `已删除 ${selectedCount} 个任务`,
                    position: 'top',
                    timeout: 4000,
                    actions: [
                        {
                            label: '查看回收站',
                            color: 'white',
                            handler: () => {
                                void router.push('/trash');
                            },
                        },
                    ],
                });
            } catch {
                $q.notify({
                    type: 'negative',
                    message: '批量删除失败',
                    position: 'top',
                });
            } finally {
                confirmDialog.setLoading(false);
            }
        }
    } catch (error) {
        console.error('批量删除失败:', error);
    }
};

// 对话框操作
const openCreateDialog = () => {
    selectedTask.value = null;
    showTaskDialog.value = true;
};

// 处理次要操作
const handleSecondaryAction = (actionName: string) => {
    switch (actionName) {
        case 'refresh':
            loadTasks();
            break;
        case 'filter':
            // 这里可以添加快速筛选逻辑
            console.log('Quick filter action');
            break;
        default:
            console.log('Unknown action:', actionName);
    }
};

const openEditDialog = (task: Task) => {
    selectedTask.value = task;
    showTaskDialog.value = true;
};

const onTaskSaved = (task: Task) => {
    // 任务已保存，对话框会自动关闭
    // TaskStore 已经处理了数据更新
    console.log('任务已保存:', task.title);
};

// 组件挂载时加载数据
onMounted(() => {
    void loadTasks();
});
</script>

<style scoped lang="scss">
// 页面整体样式 - 统一科技感设计
.task-list-page {
    background: #f8fafc;
    min-height: calc(100vh - 50px);
    position: relative;
    padding: 1.5rem;

    // 添加科技感网格纹理 - 与仪表板一致
    &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image:
            linear-gradient(rgba(59, 130, 246, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(59, 130, 246, 0.02) 1px, transparent 1px);
        background-size: 40px 40px;
        pointer-events: none;
    }
}

.page-header {
    margin-bottom: 2rem;
    position: relative;
    background: linear-gradient(
        135deg,
        rgba(59, 130, 246, 0.08) 0%,
        rgba(14, 165, 233, 0.05) 50%,
        rgba(6, 182, 212, 0.08) 100%
    );
    border-radius: 24px;
    padding: 2rem;
    overflow: hidden;
    border: 1px solid rgba(59, 130, 246, 0.15);
    box-shadow:
        0 20px 60px rgba(14, 165, 233, 0.08),
        0 8px 24px rgba(59, 130, 246, 0.06),
        inset 0 1px 0 rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(20px);

    // 科技感背景
    .header-background {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        pointer-events: none;

        .tech-grid {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image:
                linear-gradient(rgba(59, 130, 246, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(59, 130, 246, 0.03) 1px, transparent 1px);
            background-size: 30px 30px;
            animation: gridMove 20s linear infinite;
        }

        .floating-particles {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;

            .particle {
                position: absolute;
                width: 4px;
                height: 4px;
                background: radial-gradient(circle, rgba(59, 130, 246, 0.8) 0%, transparent 70%);
                border-radius: 50%;
                animation: float 6s ease-in-out infinite;

                &:nth-child(1) {
                    top: 20%;
                    left: 10%;
                    animation-delay: 0s;
                }

                &:nth-child(2) {
                    top: 60%;
                    left: 80%;
                    animation-delay: 2s;
                }

                &:nth-child(3) {
                    top: 30%;
                    right: 20%;
                    animation-delay: 4s;
                }

                &:nth-child(4) {
                    bottom: 40%;
                    left: 60%;
                    animation-delay: 1s;
                }
            }
        }
    }

    .header-content {
        position: relative;
        z-index: 2;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 2rem;

        .title-section {
            flex: 1;

            .title-container {
                display: flex;
                align-items: center;
                gap: 1.5rem;

                .icon-wrapper {
                    position: relative;
                    width: 56px;
                    height: 56px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: linear-gradient(
                        135deg,
                        rgba(59, 130, 246, 0.15),
                        rgba(14, 165, 233, 0.1)
                    );
                    border-radius: 16px;
                    border: 2px solid rgba(59, 130, 246, 0.2);
                    box-shadow:
                        0 8px 24px rgba(59, 130, 246, 0.15),
                        inset 0 1px 0 rgba(255, 255, 255, 0.3);

                    .title-icon {
                        color: #3b82f6;
                        z-index: 2;
                    }

                    .icon-glow {
                        position: absolute;
                        top: 50%;
                        left: 50%;
                        transform: translate(-50%, -50%);
                        width: 40px;
                        height: 40px;
                        background: radial-gradient(
                            circle,
                            rgba(59, 130, 246, 0.2) 0%,
                            transparent 70%
                        );
                        border-radius: 50%;
                        animation: pulse 2s ease-in-out infinite;
                    }
                }

                .title-text {
                    flex: 1;

                    .page-title {
                        font-size: 2rem;
                        font-weight: 800;
                        margin: 0 0 0.5rem 0;
                        line-height: 1.2;
                        display: flex;
                        align-items: baseline;
                        gap: 0.5rem;

                        .title-primary {
                            background: linear-gradient(135deg, #1e40af, #3b82f6);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                            background-clip: text;
                        }

                        .title-accent {
                            color: #0ea5e9;
                            font-weight: 600;
                            font-size: 1.5rem;
                        }
                    }

                    .page-subtitle {
                        color: #64748b;
                        margin: 0;
                        font-size: 0.95rem;
                        font-weight: 500;
                        display: flex;
                        align-items: center;
                        letter-spacing: 0.02em;
                    }
                }
            }
        }

        .action-section {
            flex-shrink: 0;

            .action-buttons {
                display: flex;
                align-items: center;
                gap: 0.75rem;

                .create-btn {
                    background: linear-gradient(135deg, #3b82f6, #2563eb);
                    color: white;
                    border: 1px solid rgba(226, 232, 240, 0.5);
                    box-shadow:
                        0 8px 24px rgba(59, 130, 246, 0.25),
                        inset 0 1px 0 rgba(255, 255, 255, 0.2);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    font-weight: 600;
                    height: 44px;
                    padding: 0 1.5rem;

                    &:hover {
                        transform: translateY(-2px);
                        box-shadow:
                            0 12px 32px rgba(59, 130, 246, 0.35),
                            inset 0 1px 0 rgba(255, 255, 255, 0.3);
                        background: linear-gradient(135deg, #2563eb, #1d4ed8);
                    }

                    &:active {
                        transform: translateY(0);
                    }
                }

                .refresh-btn,
                .filter-toggle-btn {
                    width: 44px;
                    height: 44px;
                    background: rgba(59, 130, 246, 0.08);
                    border: 1px solid rgba(59, 130, 246, 0.15);
                    color: #3b82f6;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

                    &:hover {
                        background: rgba(59, 130, 246, 0.15);
                        border-color: rgba(59, 130, 246, 0.25);
                        transform: translateY(-1px);
                        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
                    }

                    &:active {
                        transform: translateY(0);
                    }
                }
            }
        }
    }

    // 底部装饰线 - 重新设计为更科技感的效果
    .header-decoration {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 6px;
        overflow: hidden;

        // 发光边框效果
        .deco-border-glow {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(
                90deg,
                transparent 0%,
                rgba(59, 130, 246, 0.3) 20%,
                rgba(14, 165, 233, 0.8) 50%,
                rgba(59, 130, 246, 0.3) 80%,
                transparent 100%
            );
            box-shadow:
                0 0 8px rgba(14, 165, 233, 0.4),
                0 0 16px rgba(59, 130, 246, 0.2);
            animation: borderPulse 3s ease-in-out infinite;
        }

        // 流动粒子效果
        .deco-particles {
            position: absolute;
            bottom: 1px;
            left: 0;
            right: 0;
            height: 4px;

            .deco-particle {
                position: absolute;
                width: 3px;
                height: 3px;
                background: radial-gradient(
                    circle,
                    #3b82f6 0%,
                    rgba(59, 130, 246, 0.6) 50%,
                    transparent 100%
                );
                border-radius: 50%;
                opacity: 0;
                animation: particleFlow 4s linear infinite;

                &:nth-child(1) {
                    left: 10%;
                    animation-delay: 0s;
                }

                &:nth-child(2) {
                    left: 30%;
                    animation-delay: 0.8s;
                }

                &:nth-child(3) {
                    left: 50%;
                    animation-delay: 1.6s;
                }

                &:nth-child(4) {
                    left: 70%;
                    animation-delay: 2.4s;
                }

                &:nth-child(5) {
                    left: 90%;
                    animation-delay: 3.2s;
                }
            }
        }

        // 脉冲扫描线
        .deco-pulse-line {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100px;
            height: 1px;
            background: linear-gradient(
                90deg,
                transparent 0%,
                rgba(6, 182, 212, 0.8) 50%,
                transparent 100%
            );
            box-shadow: 0 0 6px rgba(6, 182, 212, 0.6);
            animation: scanLine 6s linear infinite;
        }
    }
}

// 动画定义
@keyframes gridMove {
    0% {
        transform: translate(0, 0);
    }
    100% {
        transform: translate(30px, 30px);
    }
}

@keyframes float {
    0%,
    100% {
        transform: translateY(0px) rotate(0deg);
        opacity: 0.7;
    }
    50% {
        transform: translateY(-10px) rotate(180deg);
        opacity: 1;
    }
}

@keyframes pulse {
    0%,
    100% {
        transform: translate(-50%, -50%) scale(1);
        opacity: 0.7;
    }
    50% {
        transform: translate(-50%, -50%) scale(1.2);
        opacity: 0.9;
    }
}

@keyframes ripple {
    0% {
        transform: translate(-50%, -50%) scale(0);
        opacity: 1;
    }
    100% {
        transform: translate(-50%, -50%) scale(2);
        opacity: 0;
    }
}

// 新增装饰线动画
@keyframes borderPulse {
    0%,
    100% {
        opacity: 0.6;
        box-shadow:
            0 0 8px rgba(14, 165, 233, 0.4),
            0 0 16px rgba(59, 130, 246, 0.2);
    }
    50% {
        opacity: 1;
        box-shadow:
            0 0 12px rgba(14, 165, 233, 0.6),
            0 0 24px rgba(59, 130, 246, 0.4);
    }
}

@keyframes particleFlow {
    0% {
        opacity: 0;
        transform: translateX(-10px) scale(0.5);
    }
    10% {
        opacity: 1;
        transform: translateX(0px) scale(1);
    }
    90% {
        opacity: 1;
        transform: translateX(30px) scale(1);
    }
    100% {
        opacity: 0;
        transform: translateX(40px) scale(0.5);
    }
}

@keyframes scanLine {
    0% {
        left: -100px;
        opacity: 0;
    }
    10% {
        opacity: 1;
    }
    90% {
        opacity: 1;
    }
    100% {
        left: calc(100% + 100px);
        opacity: 0;
    }
}

.tasks-section {
    margin-bottom: 1.5rem;

    .tasks-container {
        border-radius: 8px;
        overflow: hidden;

        .tasks-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 1rem;
            background: #f8fafc;

            .header-left {
                display: flex;
                align-items: center;
                gap: 0.75rem;

                .tasks-count {
                    color: #6b7280;
                    font-size: 0.8rem;
                }
            }
        }

        .tasks-content {
            &.no-padding {
                padding: 0;
            }

            .loading-state {
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 150px;

                .loading-container {
                    text-align: center;

                    p {
                        margin-top: 0.75rem;
                        color: #6b7280;
                        font-size: 0.875rem;
                    }
                }
            }

            .empty-state {
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 200px;

                .empty-container {
                    text-align: center;

                    h3 {
                        color: #374151;
                        margin: 0.75rem 0 0.375rem 0;
                        font-size: 1.125rem;
                    }

                    p {
                        color: #6b7280;
                        margin-bottom: 1.5rem;
                        font-size: 0.875rem;
                    }
                }
            }

            .tasks-list {
                &.view-list {
                    display: flex;
                    flex-direction: column;
                    gap: 0.75rem;
                }

                &.view-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
                    gap: 0.75rem;
                    padding: 0.75rem;
                }
            }
        }
    }
}

.pagination-section {
    display: flex;
    justify-content: center;
    margin-top: 1.5rem;
}

// 响应式设计
@media (max-width: 768px) {
    .page-header {
        padding: 1.5rem;
        margin-bottom: 1.5rem;

        .header-content {
            flex-direction: column;
            gap: 1.5rem;

            .title-section {
                .title-container {
                    gap: 1rem;

                    .icon-wrapper {
                        width: 48px;
                        height: 48px;
                    }

                    .title-text {
                        .page-title {
                            font-size: 1.75rem;

                            .title-accent {
                                font-size: 1.25rem;
                            }
                        }

                        .page-subtitle {
                            font-size: 0.9rem;
                        }
                    }
                }
            }

            .action-section {
                width: 100%;

                .action-buttons {
                    justify-content: space-between;
                    width: 100%;

                    .create-btn {
                        flex: 1;
                        max-width: 200px;
                    }
                }
            }
        }
    }

    .tasks-section {
        .tasks-container {
            .tasks-content {
                .tasks-list {
                    &.view-grid {
                        grid-template-columns: 1fr;
                    }
                }
            }
        }
    }
}

@media (max-width: 480px) {
    .page-header {
        padding: 1rem;
        border-radius: 16px;

        .header-content {
            .title-section {
                .title-container {
                    flex-direction: column;
                    text-align: center;
                    gap: 1rem;

                    .title-text {
                        .page-title {
                            font-size: 1.5rem;
                            justify-content: center;

                            .title-accent {
                                font-size: 1.125rem;
                            }
                        }
                    }
                }
            }

            .action-section {
                .action-buttons {
                    flex-direction: column;
                    gap: 0.75rem;

                    .create-btn {
                        max-width: none;
                        width: 100%;
                    }

                    .refresh-btn,
                    .filter-toggle-btn {
                        width: 100%;
                        height: 40px;
                    }
                }
            }
        }
    }

    .stats-grid {
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 0.75rem !important;

        .stat-card {
            .stat-content {
                .stat-value {
                    font-size: 1.5rem !important;
                }
            }
        }
    }
}

// 科技感任务列表样式
.tasks-section {
    .tasks-container.modern-tech-style {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(59, 130, 246, 0.15);
        border-radius: 16px;
        box-shadow:
            0 20px 60px rgba(14, 165, 233, 0.08),
            0 8px 24px rgba(59, 130, 246, 0.06),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(20px);
        overflow: hidden;
        position: relative;

        // 科技感头部
        .tasks-header.tech-header {
            background: linear-gradient(
                135deg,
                rgba(59, 130, 246, 0.05) 0%,
                rgba(14, 165, 233, 0.03) 50%,
                rgba(6, 182, 212, 0.05) 100%
            );
            border-bottom: 1px solid rgba(59, 130, 246, 0.1);
            padding: 1.5rem 2rem;
            position: relative;
            overflow: hidden;

            // 背景装饰
            .header-bg-pattern {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                pointer-events: none;

                .circuit-lines {
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background-image:
                        linear-gradient(rgba(59, 130, 246, 0.08) 1px, transparent 1px),
                        linear-gradient(90deg, rgba(59, 130, 246, 0.08) 1px, transparent 1px);
                    background-size: 20px 20px;
                    animation: circuitFlow 15s linear infinite;
                }

                .data-flow {
                    position: absolute;
                    top: 50%;
                    left: 0;
                    right: 0;
                    height: 2px;
                    background: linear-gradient(
                        90deg,
                        transparent 0%,
                        rgba(59, 130, 246, 0.3) 20%,
                        rgba(14, 165, 233, 0.6) 50%,
                        rgba(59, 130, 246, 0.3) 80%,
                        transparent 100%
                    );
                    animation: dataFlow 3s ease-in-out infinite;
                }
            }

            .header-content {
                position: relative;
                z-index: 2;
                display: flex;
                justify-content: space-between;
                align-items: center;

                .header-left {
                    display: flex;
                    align-items: center;
                    gap: 2rem;

                    .select-all-wrapper {
                        position: relative;
                        display: flex;
                        align-items: center;

                        .tech-checkbox {
                            border: 2px solid rgba(59, 130, 246, 0.3);
                            border-radius: 4px;
                            background: rgba(59, 130, 246, 0.05);
                        }

                        .checkbox-glow {
                            position: absolute;
                            top: 50%;
                            left: 50%;
                            transform: translate(-50%, -50%);
                            width: 24px;
                            height: 24px;
                            background: radial-gradient(
                                circle,
                                rgba(59, 130, 246, 0.2) 0%,
                                transparent 70%
                            );
                            border-radius: 50%;
                            animation: checkboxGlow 2s ease-in-out infinite;
                        }
                    }

                    .tasks-counter {
                        .counter-display {
                            display: flex;
                            flex-direction: column;
                            gap: 0.25rem;

                            .counter-label {
                                font-size: 0.75rem;
                                color: #64748b;
                                font-weight: 500;
                                text-transform: uppercase;
                                letter-spacing: 0.05em;
                            }

                            .counter-value {
                                display: flex;
                                align-items: baseline;
                                gap: 0.25rem;
                                font-family: 'Roboto Mono', monospace;

                                .count-number {
                                    font-size: 1.25rem;
                                    font-weight: 700;
                                    color: #3b82f6;
                                }

                                .count-separator {
                                    font-size: 1rem;
                                    color: #94a3b8;
                                }

                                .count-total {
                                    font-size: 1rem;
                                    color: #64748b;
                                    font-weight: 500;
                                }
                            }
                        }

                        .counter-indicator {
                            margin-top: 0.5rem;
                            width: 80px;
                            height: 3px;
                            background: rgba(59, 130, 246, 0.1);
                            border-radius: 2px;
                            overflow: hidden;

                            .indicator-bar {
                                height: 100%;
                                background: linear-gradient(90deg, #3b82f6, #06b6d4);
                                border-radius: 2px;
                                transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
                                position: relative;

                                &::after {
                                    content: '';
                                    position: absolute;
                                    top: 0;
                                    left: 0;
                                    right: 0;
                                    bottom: 0;
                                    background: linear-gradient(
                                        90deg,
                                        transparent 0%,
                                        rgba(255, 255, 255, 0.3) 50%,
                                        transparent 100%
                                    );
                                    animation: indicatorShine 2s ease-in-out infinite;
                                }
                            }
                        }
                    }
                }

                .header-right {
                    display: flex;
                    align-items: center;
                    gap: 1.5rem;

                    .view-controls {
                        display: flex;
                        align-items: center;
                        gap: 1rem;

                        .tech-view-btn {
                            position: relative;
                            width: 40px;
                            height: 40px;
                            background: rgba(59, 130, 246, 0.08);
                            border: 1px solid rgba(59, 130, 246, 0.2);
                            border-radius: 8px;
                            color: #3b82f6;
                            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

                            &:hover {
                                background: rgba(59, 130, 246, 0.15);
                                border-color: rgba(59, 130, 246, 0.3);
                                transform: translateY(-1px);
                            }

                            .btn-glow {
                                position: absolute;
                                top: -2px;
                                left: -2px;
                                right: -2px;
                                bottom: -2px;
                                background: linear-gradient(
                                    45deg,
                                    transparent,
                                    rgba(59, 130, 246, 0.1),
                                    transparent
                                );
                                border-radius: 10px;
                                opacity: 0;
                                transition: opacity 0.3s ease;
                            }

                            &:hover .btn-glow {
                                opacity: 1;
                            }
                        }

                        .drag-indicator {
                            display: flex;
                            align-items: center;
                            gap: 0.5rem;
                            padding: 0.5rem 1rem;
                            background: rgba(6, 182, 212, 0.08);
                            border: 1px solid rgba(6, 182, 212, 0.2);
                            border-radius: 20px;
                            color: #0891b2;
                            font-size: 0.8rem;
                            font-weight: 500;

                            .drag-hint {
                                white-space: nowrap;
                            }
                        }
                    }
                }
            }
        }

        // 科技感内容区域
        .tasks-content.tech-content {
            padding: 2rem;
            position: relative;
            min-height: 400px;

            // 科技感拖拽网格
            .tasks-grid.tech-grid {
                position: relative;
                z-index: 2;

                .drag-container {
                    position: relative;
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
                    gap: 1.5rem;

                    // 拖拽项目包装器
                    .task-item-wrapper {
                        position: relative;
                        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                        cursor: grab;

                        &:hover {
                            transform: translateY(-2px);
                        }

                        &.dragging {
                            opacity: 0.7;
                            transform: rotate(5deg) scale(1.05);
                            cursor: grabbing;
                            z-index: 1000;
                        }

                        &.selected {
                            .task-tech-border {
                                border-color: rgba(59, 130, 246, 0.4);

                                .border-scan {
                                    opacity: 1;
                                }
                            }
                        }

                        // 拖拽手柄
                        .drag-handle {
                            position: absolute;
                            top: 50%;
                            left: -12px;
                            transform: translateY(-50%);
                            width: 8px;
                            height: 32px;
                            background: rgba(59, 130, 246, 0.1);
                            border-radius: 4px;
                            cursor: grab;
                            opacity: 0;
                            transition: all 0.3s ease;
                            z-index: 5;

                            .handle-dots {
                                position: absolute;
                                top: 50%;
                                left: 50%;
                                transform: translate(-50%, -50%);
                                display: grid;
                                grid-template-columns: 1fr 1fr;
                                gap: 2px;

                                .dot {
                                    width: 2px;
                                    height: 2px;
                                    background: #3b82f6;
                                    border-radius: 50%;
                                }
                            }

                            .handle-glow {
                                position: absolute;
                                top: 0;
                                left: 0;
                                right: 0;
                                bottom: 0;
                                background: linear-gradient(
                                    180deg,
                                    rgba(59, 130, 246, 0.2),
                                    rgba(14, 165, 233, 0.2)
                                );
                                border-radius: inherit;
                                opacity: 0;
                                animation: handleGlow 2s ease-in-out infinite;
                            }

                            &:hover {
                                background: rgba(59, 130, 246, 0.2);
                                cursor: grabbing;

                                .handle-glow {
                                    opacity: 1;
                                }
                            }
                        }

                        &:hover .drag-handle {
                            opacity: 1;
                            left: -16px;
                        }

                        // 科技感边框
                        .task-tech-border {
                            position: absolute;
                            top: -1px;
                            left: -1px;
                            right: -1px;
                            bottom: -1px;
                            border: 1px solid rgba(59, 130, 246, 0.15);
                            border-radius: 12px;
                            pointer-events: none;
                            z-index: 1;

                            // 边框角落装饰
                            .border-corner {
                                position: absolute;
                                width: 12px;
                                height: 12px;
                                border: 2px solid rgba(59, 130, 246, 0.3);

                                &.tl {
                                    top: -1px;
                                    left: -1px;
                                    border-right: none;
                                    border-bottom: none;
                                    border-radius: 12px 0 0 0;
                                }

                                &.tr {
                                    top: -1px;
                                    right: -1px;
                                    border-left: none;
                                    border-bottom: none;
                                    border-radius: 0 12px 0 0;
                                }

                                &.bl {
                                    bottom: -1px;
                                    left: -1px;
                                    border-right: none;
                                    border-top: none;
                                    border-radius: 0 0 0 12px;
                                }

                                &.br {
                                    bottom: -1px;
                                    right: -1px;
                                    border-left: none;
                                    border-top: none;
                                    border-radius: 0 0 12px 0;
                                }
                            }

                            // 扫描效果
                            .border-scan {
                                position: absolute;
                                top: 0;
                                left: 0;
                                right: 0;
                                bottom: 0;
                                border: 1px solid transparent;
                                border-radius: 12px;
                                background: linear-gradient(
                                    45deg,
                                    transparent,
                                    rgba(59, 130, 246, 0.1),
                                    transparent
                                );
                                opacity: 0;
                                animation: borderScan 3s ease-in-out infinite;
                            }
                        }

                        // 任务卡片样式
                        .tech-task-card {
                            position: relative;
                            z-index: 2;
                            border: none;
                            box-shadow: none;
                            background: rgba(255, 255, 255, 0.9);
                            backdrop-filter: blur(10px);
                        }

                        // 选中状态指示器
                        .selection-indicator {
                            position: absolute;
                            top: -2px;
                            left: -2px;
                            right: -2px;
                            bottom: -2px;
                            border-radius: 14px;
                            pointer-events: none;
                            z-index: 0;

                            .selection-glow {
                                position: absolute;
                                top: 0;
                                left: 0;
                                right: 0;
                                bottom: 0;
                                background: linear-gradient(
                                    45deg,
                                    rgba(59, 130, 246, 0.1),
                                    rgba(14, 165, 233, 0.1)
                                );
                                border-radius: inherit;
                                animation: selectionGlow 2s ease-in-out infinite;
                            }

                            .selection-pulse {
                                position: absolute;
                                top: 50%;
                                left: 50%;
                                transform: translate(-50%, -50%);
                                width: 20px;
                                height: 20px;
                                background: radial-gradient(
                                    circle,
                                    rgba(59, 130, 246, 0.3) 0%,
                                    transparent 70%
                                );
                                border-radius: 50%;
                                animation: selectionPulse 1.5s ease-in-out infinite;
                            }
                        }

                        // 拖拽占位符
                        .drag-placeholder {
                            position: absolute;
                            top: 0;
                            left: 0;
                            right: 0;
                            bottom: 0;
                            background: rgba(6, 182, 212, 0.05);
                            border: 2px dashed rgba(6, 182, 212, 0.3);
                            border-radius: 12px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            opacity: 0;
                            transform: scale(0.95);
                            transition: all 0.3s ease;
                            z-index: 0;

                            &.active {
                                opacity: 1;
                                transform: scale(1);
                            }

                            .placeholder-content {
                                display: flex;
                                flex-direction: column;
                                align-items: center;
                                gap: 0.5rem;
                                color: #0891b2;
                                font-weight: 500;
                                font-size: 0.9rem;
                            }
                        }
                    }
                }

                // 网格视图特殊样式
                &.view-grid {
                    .drag-container {
                        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                        gap: 1rem;
                    }

                    .task-item-wrapper {
                        .tech-task-card {
                            min-height: 200px;
                        }
                    }
                }
            }
        }
    }
}
</style>

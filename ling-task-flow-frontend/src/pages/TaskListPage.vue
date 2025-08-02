<template>
    <q-page padding>
        <!-- 页面头部 -->
        <div class="page-header">
            <div class="header-content">
                <div class="title-section">
                    <h1 class="page-title">任务管理</h1>
                    <p class="page-subtitle">管理您的所有任务，提升工作效率</p>
                </div>
                <div class="action-section">
                    <q-btn
                        color="primary"
                        icon="add"
                        label="新建任务"
                        unelevated
                        rounded
                        @click="openCreateDialog"
                    />
                </div>
            </div>
        </div>

        <!-- 任务统计卡片 -->
        <div class="stats-section">
            <div class="stats-grid">
                <q-card flat bordered class="stat-card stat-total">
                    <q-card-section>
                        <div class="stat-content">
                            <div class="stat-icon">
                                <q-icon name="assignment" size="24px" color="blue-6" />
                            </div>
                            <div class="stat-info">
                                <div class="stat-value">{{ taskStore.totalTasks }}</div>
                                <div class="stat-label">总任务数</div>
                            </div>
                        </div>
                    </q-card-section>
                </q-card>

                <q-card flat bordered class="stat-card stat-pending">
                    <q-card-section>
                        <div class="stat-content">
                            <div class="stat-icon">
                                <q-icon name="schedule" size="24px" color="orange-6" />
                            </div>
                            <div class="stat-info">
                                <div class="stat-value">{{ getPendingTasksCount() }}</div>
                                <div class="stat-label">待处理</div>
                            </div>
                        </div>
                    </q-card-section>
                </q-card>

                <q-card flat bordered class="stat-card stat-progress">
                    <q-card-section>
                        <div class="stat-content">
                            <div class="stat-icon">
                                <q-icon name="play_arrow" size="24px" color="blue-6" />
                            </div>
                            <div class="stat-info">
                                <div class="stat-value">{{ getInProgressTasksCount() }}</div>
                                <div class="stat-label">进行中</div>
                            </div>
                        </div>
                    </q-card-section>
                </q-card>

                <q-card flat bordered class="stat-card stat-completed">
                    <q-card-section>
                        <div class="stat-content">
                            <div class="stat-icon">
                                <q-icon name="check_circle" size="24px" color="green-6" />
                            </div>
                            <div class="stat-info">
                                <div class="stat-value">{{ getCompletedTasksCount() }}</div>
                                <div class="stat-label">已完成</div>
                            </div>
                        </div>
                    </q-card-section>
                </q-card>
            </div>
        </div>

        <!-- 美化的筛选和搜索区域 -->
        <q-card flat bordered class="filters-card">
            <q-card-section class="filters-header">
                <div class="filters-title">
                    <q-icon name="filter_list" size="20px" color="primary" class="q-mr-sm" />
                    <span class="text-subtitle1 text-weight-medium">筛选和搜索</span>
                </div>
            </q-card-section>

            <q-separator />

            <q-card-section class="filters-content">
                <div class="filters-row">
                    <!-- 搜索框 - 更大更突出 -->
                    <div class="search-container">
                        <q-input
                            v-model="searchQuery"
                            placeholder="搜索任务标题、描述或标签..."
                            outlined
                            rounded
                            clearable
                            class="search-input"
                            @update:model-value="handleSearch"
                            debounce="500"
                        >
                            <template #prepend>
                                <q-icon name="search" color="primary" />
                            </template>
                        </q-input>
                    </div>
                </div>

                <div class="filters-row">
                    <!-- 状态筛选 - 美化样式 -->
                    <div class="filter-group">
                        <div class="filter-label">
                            <q-icon name="flag" size="16px" color="blue-6" />
                            <span>状态筛选</span>
                        </div>
                        <q-select
                            v-model="statusFilter"
                            :options="statusOptions"
                            outlined
                            rounded
                            clearable
                            emit-value
                            map-options
                            placeholder="选择状态"
                            class="filter-select"
                            @update:model-value="handleFilterChange"
                        >
                            <template v-slot:option="{ itemProps, opt }">
                                <q-item v-bind="itemProps">
                                    <q-item-section avatar>
                                        <q-icon
                                            :name="getStatusIcon(opt.value)"
                                            :color="getStatusColor(opt.value)"
                                            size="sm"
                                        />
                                    </q-item-section>
                                    <q-item-section>
                                        <q-item-label>{{ opt.label }}</q-item-label>
                                    </q-item-section>
                                </q-item>
                            </template>
                            <template v-slot:selected-item v-if="statusFilter">
                                <q-chip
                                    :color="getStatusColor(statusFilter)"
                                    text-color="white"
                                    size="sm"
                                    :icon="getStatusIcon(statusFilter)"
                                >
                                    {{ getStatusLabel(statusFilter) }}
                                </q-chip>
                            </template>
                        </q-select>
                    </div>

                    <!-- 优先级筛选 - 美化样式 -->
                    <div class="filter-group">
                        <div class="filter-label">
                            <q-icon name="priority_high" size="16px" color="red-6" />
                            <span>优先级筛选</span>
                        </div>
                        <q-select
                            v-model="priorityFilter"
                            :options="priorityOptions"
                            outlined
                            rounded
                            clearable
                            emit-value
                            map-options
                            placeholder="选择优先级"
                            class="filter-select"
                            @update:model-value="handleFilterChange"
                        >
                            <template v-slot:option="{ itemProps, opt }">
                                <q-item v-bind="itemProps">
                                    <q-item-section avatar>
                                        <q-icon
                                            :name="getPriorityIcon(opt.value)"
                                            :color="getPriorityColor(opt.value)"
                                            size="sm"
                                        />
                                    </q-item-section>
                                    <q-item-section>
                                        <q-item-label
                                            :class="`text-${getPriorityColor(opt.value)}`"
                                        >
                                            {{ opt.label }}
                                        </q-item-label>
                                    </q-item-section>
                                </q-item>
                            </template>
                            <template v-slot:selected-item v-if="priorityFilter">
                                <q-chip
                                    :color="getPriorityColor(priorityFilter)"
                                    text-color="white"
                                    size="sm"
                                    :icon="getPriorityIcon(priorityFilter)"
                                >
                                    {{ getPriorityLabel(priorityFilter) }}
                                </q-chip>
                            </template>
                        </q-select>
                    </div>

                    <!-- 排序选择 - 美化样式 -->
                    <div class="filter-group">
                        <div class="filter-label">
                            <q-icon name="sort" size="16px" color="green-6" />
                            <span>排序方式</span>
                        </div>
                        <q-select
                            v-model="sortBy"
                            :options="sortOptions"
                            outlined
                            rounded
                            emit-value
                            map-options
                            placeholder="选择排序"
                            class="filter-select"
                            @update:model-value="handleSortChange"
                        >
                            <template v-slot:option="{ itemProps, opt }">
                                <q-item v-bind="itemProps">
                                    <q-item-section avatar>
                                        <q-icon
                                            :name="getSortIcon(opt.value)"
                                            color="green-6"
                                            size="sm"
                                        />
                                    </q-item-section>
                                    <q-item-section>
                                        <q-item-label>{{ opt.label }}</q-item-label>
                                    </q-item-section>
                                </q-item>
                            </template>
                        </q-select>
                    </div>

                    <!-- 操作按钮组 -->
                    <div class="action-buttons">
                        <q-btn
                            unelevated
                            rounded
                            color="negative"
                            icon="clear_all"
                            label="清空筛选"
                            class="clear-filter-btn"
                            @click="clearFilters"
                            :disable="!hasActiveFilters"
                        />
                    </div>
                </div>

                <!-- 活动筛选器展示 -->
                <div v-if="hasActiveFilters" class="active-filters-section">
                    <q-separator class="q-my-md" />
                    <div class="active-filters-header">
                        <span class="text-subtitle2 text-weight-medium">当前筛选条件</span>
                        <q-btn
                            flat
                            dense
                            round
                            icon="close"
                            size="sm"
                            color="grey-6"
                            @click="clearFilters"
                        />
                    </div>
                    <div class="active-filters-chips">
                        <q-chip
                            v-if="searchQuery"
                            removable
                            color="blue"
                            text-color="white"
                            icon="search"
                            @remove="
                                () => {
                                    searchQuery = '';
                                    nextTick(() => handleSearch());
                                }
                            "
                        >
                            搜索: {{ searchQuery }}
                        </q-chip>
                        <q-chip
                            v-if="statusFilter"
                            removable
                            :color="getStatusColor(statusFilter)"
                            text-color="white"
                            :icon="getStatusIcon(statusFilter)"
                            @remove="
                                () => {
                                    statusFilter = null;
                                    nextTick(() => handleFilterChange());
                                }
                            "
                        >
                            状态: {{ getStatusLabel(statusFilter) }}
                        </q-chip>
                        <q-chip
                            v-if="priorityFilter"
                            removable
                            :color="getPriorityColor(priorityFilter)"
                            text-color="white"
                            :icon="getPriorityIcon(priorityFilter)"
                            @remove="
                                () => {
                                    priorityFilter = null;
                                    nextTick(() => handleFilterChange());
                                }
                            "
                        >
                            优先级: {{ getPriorityLabel(priorityFilter) }}
                        </q-chip>
                    </div>
                </div>
            </q-card-section>
        </q-card>

        <!-- 批量操作栏 -->
        <div v-if="taskStore.selectedTasksCount > 0" class="batch-actions">
            <div class="selected-info">
                <q-icon name="check_circle" color="primary" />
                <span>已选择 {{ taskStore.selectedTasksCount }} 个任务</span>
            </div>
            <div class="batch-buttons">
                <q-btn
                    flat
                    icon="done_all"
                    label="标记完成"
                    color="positive"
                    @click="batchMarkComplete"
                />
                <q-btn flat icon="delete" label="批量删除" color="negative" @click="batchDelete" />
                <q-btn
                    flat
                    icon="close"
                    label="取消选择"
                    color="grey-7"
                    @click="taskStore.clearSelection"
                />
            </div>
        </div>

        <!-- 任务列表 -->
        <div class="tasks-section">
            <q-card flat bordered class="tasks-container">
                <!-- 列表头部 -->
                <q-card-section class="tasks-header">
                    <div class="header-left">
                        <q-checkbox
                            v-model="selectAll"
                            :indeterminate="indeterminate"
                            @update:model-value="handleSelectAll"
                        />
                        <span class="tasks-count"> 共 {{ taskStore.totalTasks }} 个任务 </span>
                    </div>
                    <div class="header-right">
                        <q-btn
                            flat
                            dense
                            :icon="viewMode === 'list' ? 'view_module' : 'view_list'"
                            @click="toggleViewMode"
                        >
                            <q-tooltip>
                                {{ viewMode === 'list' ? '网格视图' : '列表视图' }}
                            </q-tooltip>
                        </q-btn>
                    </div>
                </q-card-section>

                <q-separator />

                <!-- 任务列表内容 -->
                <q-card-section
                    class="tasks-content"
                    :class="{ 'no-padding': viewMode === 'grid' }"
                >
                    <div v-if="taskStore.loading" class="loading-state">
                        <div class="loading-container">
                            <q-spinner-dots size="40px" color="primary" />
                            <p>加载任务中...</p>
                        </div>
                    </div>

                    <div v-else-if="taskStore.activeTasks.length === 0" class="empty-state">
                        <div class="empty-container">
                            <q-icon name="assignment" size="80px" color="grey-4" />
                            <h3>暂无任务</h3>
                            <p>创建您的第一个任务开始管理工作吧！</p>
                            <q-btn
                                color="primary"
                                icon="add"
                                label="创建任务"
                                unelevated
                                rounded
                                @click="openCreateDialog"
                            />
                        </div>
                    </div>

                    <div v-else class="tasks-list" :class="`view-${viewMode}`">
                        <TaskCard
                            v-for="task in taskStore.activeTasks"
                            :key="task.id"
                            :task="task"
                            :selected="taskStore.selectedTasks.includes(task.id)"
                            @toggle-selection="taskStore.toggleTaskSelection"
                            @edit="handleEditTask"
                            @delete="handleDeleteTask"
                            @duplicate="handleDuplicateTask"
                            @view="handleViewTask"
                            @status-change="handleStatusChange"
                        />
                    </div>
                </q-card-section>
            </q-card>
        </div>

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
        <TaskDialog v-model="showTaskDialog" :task="selectedTask" @saved="onTaskSaved" />

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
import { ref, computed, onMounted, nextTick } from 'vue';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';
import { useTaskStore } from 'stores/task';
import TaskCard from 'components/TaskCard.vue';
import TaskDialog from 'components/TaskDialog.vue';
import TaskViewDialog from 'components/TaskViewDialog.vue';
import type { Task, TaskStatus, TaskPriority, TaskSearchParams } from '../types';

const $q = useQuasar();
const router = useRouter();
const taskStore = useTaskStore();

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

// 筛选选项
const statusOptions = [
    { label: '待处理', value: 'PENDING' },
    { label: '进行中', value: 'IN_PROGRESS' },
    { label: '已完成', value: 'COMPLETED' },
    { label: '已取消', value: 'CANCELLED' },
    { label: '暂停', value: 'ON_HOLD' },
];

const priorityOptions = [
    { label: '低', value: 'LOW' },
    { label: '中', value: 'MEDIUM' },
    { label: '高', value: 'HIGH' },
    { label: '紧急', value: 'URGENT' },
];

const sortOptions = [
    { label: '创建时间（最新）', value: '-created_at' },
    { label: '创建时间（最早）', value: 'created_at' },
    { label: '更新时间（最新）', value: '-updated_at' },
    { label: '优先级（高到低）', value: '-priority' },
    { label: '优先级（低到高）', value: 'priority' },
    { label: '到期时间', value: 'due_date' },
];

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

// 统计方法
const getPendingTasksCount = () => {
    return taskStore.tasks.filter((task: Task) => task.status === 'PENDING').length;
};

const getInProgressTasksCount = () => {
    return taskStore.tasks.filter((task: Task) => task.status === 'IN_PROGRESS').length;
};

const getCompletedTasksCount = () => {
    return taskStore.tasks.filter((task: Task) => task.status === 'COMPLETED').length;
};

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

const handleSearch = () => {
    updateSearchParams();
};

const handleFilterChange = () => {
    updateSearchParams();
};

const handleSortChange = () => {
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

// 活动筛选器状态
const hasActiveFilters = computed(() => {
    return !!(searchQuery.value || statusFilter.value || priorityFilter.value);
});

// 状态相关函数
const getStatusIcon = (status: TaskStatus): string => {
    const icons: Record<TaskStatus, string> = {
        PENDING: 'schedule',
        IN_PROGRESS: 'play_arrow',
        COMPLETED: 'check_circle',
        CANCELLED: 'cancel',
        ON_HOLD: 'pause_circle',
    };
    return icons[status] || 'help';
};

const getStatusColor = (status: TaskStatus): string => {
    const colors: Record<TaskStatus, string> = {
        PENDING: 'orange',
        IN_PROGRESS: 'blue',
        COMPLETED: 'green',
        CANCELLED: 'red',
        ON_HOLD: 'grey',
    };
    return colors[status] || 'grey';
};

const getStatusLabel = (status: TaskStatus): string => {
    const labels: Record<TaskStatus, string> = {
        PENDING: '待处理',
        IN_PROGRESS: '进行中',
        COMPLETED: '已完成',
        CANCELLED: '已取消',
        ON_HOLD: '暂停',
    };
    return labels[status] || '未知';
};

// 排序相关函数
const getSortIcon = (sortValue: string): string => {
    const icons: Record<string, string> = {
        '-created_at': 'schedule',
        created_at: 'schedule',
        '-updated_at': 'update',
        '-priority': 'keyboard_arrow_up',
        priority: 'keyboard_arrow_down',
        due_date: 'event',
    };
    return icons[sortValue] || 'sort';
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

const handleDuplicateTask = (task: Task) => {
    $q.notify({
        type: 'info',
        message: `复制任务"${task.title}"功能正在开发中...`,
        position: 'top',
    });
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
    handleDeleteTask(task);
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

const handleDeleteTask = (task: Task) => {
    $q.dialog({
        title: '确认删除',
        message: `确定要删除任务"${task.title}"吗？删除后可以在回收站中恢复。`,
        cancel: {
            label: '取消',
            flat: true,
            color: 'grey',
        },
        ok: {
            label: '删除',
            color: 'negative',
            icon: 'delete',
        },
        persistent: true,
    }).onOk(() => {
        void (async () => {
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
            }
        })();
    });
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

const batchDelete = () => {
    const selectedCount = taskStore.selectedTasksCount;
    const selectedTaskIds = [...taskStore.selectedTasks]; // 创建副本

    $q.dialog({
        title: '确认批量删除',
        message: `确定要删除选中的 ${selectedCount} 个任务吗？删除后可以在回收站中恢复。`,
        cancel: {
            label: '取消',
            flat: true,
            color: 'grey',
        },
        ok: {
            label: '删除',
            color: 'negative',
            icon: 'delete',
        },
        persistent: true,
    }).onOk(() => {
        void (async () => {
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
            }
        })();
    });
};

// 对话框操作
const openCreateDialog = () => {
    selectedTask.value = null;
    showTaskDialog.value = true;
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

// 优先级工具函数
const getPriorityColor = (priority: TaskPriority): string => {
    const colors: Record<TaskPriority, string> = {
        LOW: 'green',
        MEDIUM: 'blue',
        HIGH: 'orange',
        URGENT: 'red',
    };
    return colors[priority] || 'blue';
};

const getPriorityLabel = (priority: TaskPriority): string => {
    const labels: Record<TaskPriority, string> = {
        LOW: '低',
        MEDIUM: '中',
        HIGH: '高',
        URGENT: '紧急',
    };
    return labels[priority] || '中';
};

const getPriorityIcon = (priority: TaskPriority): string => {
    const icons: Record<TaskPriority, string> = {
        LOW: 'keyboard_arrow_down',
        MEDIUM: 'remove',
        HIGH: 'keyboard_arrow_up',
        URGENT: 'priority_high',
    };
    return icons[priority] || 'remove';
};

// 组件挂载时加载数据
onMounted(() => {
    void loadTasks();
});
</script>

<style scoped lang="scss">
.page-header {
    margin-bottom: 1.5rem;

    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 1.5rem;

        .title-section {
            flex: 1;

            .page-title {
                font-size: 1.5rem;
                font-weight: 700;
                color: #1f2937;
                margin: 0 0 0.25rem 0;
            }

            .page-subtitle {
                color: #6b7280;
                margin: 0;
                font-size: 0.875rem;
            }
        }

        .action-section {
            flex-shrink: 0;
        }
    }
}

.stats-section {
    margin-bottom: 1.5rem;

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 0.75rem;

        .stat-card {
            border-radius: 8px;
            transition: all 0.2s ease;

            &:hover {
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                transform: translateY(-1px);
            }

            .stat-content {
                display: flex;
                align-items: center;
                gap: 0.75rem;

                .stat-icon {
                    flex-shrink: 0;
                    width: 36px;
                    height: 36px;
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: rgba(59, 130, 246, 0.1);
                }

                .stat-info {
                    flex: 1;

                    .stat-value {
                        font-size: 1.25rem;
                        font-weight: 700;
                        color: #1f2937;
                        line-height: 1.2;
                    }

                    .stat-label {
                        font-size: 0.75rem;
                        color: #6b7280;
                        margin-top: 0.125rem;
                    }
                }
            }

            &.stat-pending .stat-icon {
                background: rgba(245, 158, 11, 0.1);
            }

            &.stat-progress .stat-icon {
                background: rgba(59, 130, 246, 0.1);
            }

            &.stat-completed .stat-icon {
                background: rgba(34, 197, 94, 0.1);
            }
        }
    }
}

// 紧凑的筛选卡片样式
.filters-card {
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
    border-radius: 8px;
    overflow: hidden;

    .filters-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.75rem 1rem;

        .filters-title {
            display: flex;
            align-items: center;
            font-weight: 600;
            font-size: 0.875rem;
        }
    }

    .filters-content {
        padding: 1rem;

        .filters-row {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            align-items: flex-end;

            &:first-child {
                margin-bottom: 1rem;
            }

            .search-container {
                flex: 1;
                min-width: 250px;

                .search-input {
                    font-size: 0.875rem;

                    :deep(.q-field__control) {
                        height: 36px;
                        min-height: 36px;
                        padding: 0 12px;
                        display: flex;
                        align-items: center;
                    }

                    :deep(.q-field__native) {
                        padding: 0;
                        line-height: 36px;
                        min-height: 36px;
                        display: flex;
                        align-items: center;
                    }

                    // 确保输入框内容对齐
                    :deep(.q-field__input) {
                        padding: 0;
                        margin: 0;
                        line-height: 36px;
                        min-height: 36px;
                        display: flex;
                        align-items: center;
                    }

                    // 确保前缀图标对齐
                    :deep(.q-field__marginal) {
                        height: 36px;
                        display: flex;
                        align-items: center;
                    }

                    // 确保控制容器对齐
                    :deep(.q-field__control-container) {
                        display: flex;
                        align-items: center;
                        min-height: 36px;
                    }
                }
            }

            .filter-group {
                flex: 1;
                min-width: 160px;

                .filter-label {
                    display: flex;
                    align-items: center;
                    gap: 0.375rem;
                    margin-bottom: 0.375rem;
                    color: #6b7280;
                    font-size: 0.75rem;
                    font-weight: 500;
                }

                .filter-select {
                    width: 100%;

                    :deep(.q-field__control) {
                        height: 36px;
                        min-height: 36px;
                        font-size: 0.875rem;
                        padding: 0 12px;
                        display: flex;
                        align-items: center;
                    }

                    :deep(.q-field__native) {
                        padding: 0;
                        line-height: 36px;
                        display: flex;
                        align-items: center;
                    }

                    // 确保选中状态下芯片不会改变高度并居中
                    :deep(.q-chip) {
                        height: 22px;
                        max-height: 22px;
                        font-size: 0.7rem;
                        margin: 0;
                        align-self: center;
                    }

                    // 确保选中项容器高度一致并居中
                    :deep(.q-field__control-container) {
                        padding: 0;
                        min-height: 36px;
                        display: flex;
                        align-items: center;
                    }

                    // 确保占位符文本对齐
                    :deep(.q-field__marginal) {
                        height: 36px;
                        display: flex;
                        align-items: center;
                    }

                    // 选中项对齐 - 关键修复
                    :deep(.q-field__input) {
                        padding: 0;
                        margin: 0;
                        line-height: 36px;
                        min-height: 36px;
                        display: flex;
                        align-items: center;
                    }

                    // 确保选中项内容垂直居中
                    :deep(.q-field__input .q-chip) {
                        margin: 0;
                        align-self: center;
                    }

                    // 修复选择器下拉箭头对齐
                    :deep(.q-field__append) {
                        height: 36px;
                        display: flex;
                        align-items: center;
                    }
                }
            }

            .action-buttons {
                display: flex;
                gap: 0.75rem;
                flex-shrink: 0;

                .clear-filter-btn {
                    height: 36px;
                    min-height: 36px;
                    padding: 0 16px;
                    font-size: 0.875rem;
                    font-weight: 500;

                    :deep(.q-btn__content) {
                        display: flex;
                        align-items: center;
                        gap: 0.5rem;
                    }
                }
            }
        }

        .active-filters-section {
            .active-filters-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 0.75rem;
                color: #374151;
                font-size: 0.8rem;
            }

            .active-filters-chips {
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
            }
        }
    }
}

.batch-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #f8fafc;
    padding: 0.75rem;
    border-radius: 6px;
    margin-bottom: 0.75rem;
    border: 1px solid #e2e8f0;

    .selected-info {
        display: flex;
        align-items: center;
        gap: 0.375rem;
        font-weight: 500;
        color: #374151;
        font-size: 0.875rem;
    }

    .batch-buttons {
        display: flex;
        gap: 0.375rem;
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
        .header-content {
            flex-direction: column;
            gap: 1rem;

            .action-section {
                width: 100%;

                .q-btn {
                    width: 100%;
                }
            }
        }
    }

    .filters-card {
        .filters-content {
            padding: 1rem;

            .filters-row {
                flex-direction: column;
                align-items: stretch;
                gap: 1rem;

                .search-container {
                    min-width: auto;
                    width: 100%;
                }

                .filter-group {
                    min-width: auto;
                    width: 100%;
                }

                .action-buttons {
                    flex-direction: column;
                    width: 100%;

                    .q-btn {
                        width: 100%;
                    }
                }
            }

            .active-filters-chips {
                flex-direction: column;
                gap: 0.5rem;

                .q-chip {
                    justify-content: center;
                }
            }
        }
    }

    .batch-actions {
        flex-direction: column;
        gap: 1rem;
        align-items: stretch;

        .batch-buttons {
            justify-content: center;
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

    .filters-card {
        .filters-header {
            padding: 0.75rem 1rem;

            .filters-title {
                font-size: 0.9rem;
            }
        }
    }
}
</style>

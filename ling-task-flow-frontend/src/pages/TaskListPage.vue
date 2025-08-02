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
                        @click="showCreateDialog = true"
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

        <!-- 过滤和搜索栏 -->
        <div class="filters-section">
            <div class="filters-container">
                <!-- 搜索框 -->
                <div class="search-box">
                    <q-input
                        v-model="searchQuery"
                        placeholder="搜索任务..."
                        outlined
                        dense
                        clearable
                        @update:model-value="handleSearch"
                        debounce="500"
                    >
                        <template #prepend>
                            <q-icon name="search" />
                        </template>
                    </q-input>
                </div>

                <!-- 状态筛选 -->
                <q-select
                    v-model="statusFilter"
                    :options="statusOptions"
                    label="状态"
                    outlined
                    dense
                    clearable
                    emit-value
                    map-options
                    style="min-width: 120px"
                    @update:model-value="handleFilterChange"
                />

                <!-- 优先级筛选 -->
                <q-select
                    v-model="priorityFilter"
                    :options="priorityOptions"
                    label="优先级"
                    outlined
                    dense
                    clearable
                    emit-value
                    map-options
                    style="min-width: 120px"
                    @update:model-value="handleFilterChange"
                />

                <!-- 排序选择 -->
                <q-select
                    v-model="sortBy"
                    :options="sortOptions"
                    label="排序"
                    outlined
                    dense
                    emit-value
                    map-options
                    style="min-width: 140px"
                    @update:model-value="handleSortChange"
                />

                <!-- 清空筛选 -->
                <q-btn
                    flat
                    icon="clear_all"
                    label="清空筛选"
                    color="grey-7"
                    @click="clearFilters"
                />
            </div>
        </div>

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
                                @click="showCreateDialog = true"
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

        <!-- 临时创建任务对话框 -->
        <q-dialog v-model="showCreateDialog">
            <q-card style="min-width: 400px">
                <q-card-section>
                    <div class="text-h6">创建新任务</div>
                </q-card-section>
                <q-card-section>
                    <q-input v-model="newTaskTitle" label="任务标题" outlined />
                    <q-input
                        v-model="newTaskDescription"
                        label="任务描述"
                        type="textarea"
                        outlined
                        class="q-mt-md"
                    />
                </q-card-section>
                <q-card-actions align="right">
                    <q-btn flat label="取消" v-close-popup />
                    <q-btn color="primary" label="创建" @click="createTask" />
                </q-card-actions>
            </q-card>
        </q-dialog>
    </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { useTaskStore } from 'stores/task';
import TaskCard from 'components/TaskCard.vue';
import type { Task, TaskStatus, TaskPriority, TaskSearchParams } from '../types';

const $q = useQuasar();
const taskStore = useTaskStore();

// 响应式数据
const searchQuery = ref('');
const statusFilter = ref<TaskStatus | null>(null);
const priorityFilter = ref<TaskPriority | null>(null);
const sortBy = ref('created_at');
const viewMode = ref<'list' | 'grid'>('list');
const showCreateDialog = ref(false);
const newTaskTitle = ref('');
const newTaskDescription = ref('');

// 筛选选项
const statusOptions = [
    { label: '待处理', value: 'pending' },
    { label: '进行中', value: 'in_progress' },
    { label: '已完成', value: 'completed' },
    { label: '已取消', value: 'cancelled' },
];

const priorityOptions = [
    { label: '低', value: 'low' },
    { label: '中', value: 'medium' },
    { label: '高', value: 'high' },
    { label: '紧急', value: 'urgent' },
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
    return taskStore.tasks.filter((task: Task) => task.status === 'pending').length;
};

const getInProgressTasksCount = () => {
    return taskStore.tasks.filter((task: Task) => task.status === 'in_progress').length;
};

const getCompletedTasksCount = () => {
    return taskStore.tasks.filter((task: Task) => task.status === 'completed').length;
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
    const params: Partial<TaskSearchParams> = {};
    if (searchQuery.value) {
        params.search = searchQuery.value;
    }
    taskStore.setSearchParams(params);
    void loadTasks();
};

const handleFilterChange = () => {
    const params: Partial<TaskSearchParams> = {};
    if (statusFilter.value) {
        params.status = statusFilter.value;
    }
    if (priorityFilter.value) {
        params.priority = priorityFilter.value;
    }
    taskStore.setSearchParams(params);
    void loadTasks();
};

const handleSortChange = () => {
    taskStore.setSearchParams({
        ordering: sortBy.value,
    });
    void loadTasks();
};

const clearFilters = () => {
    searchQuery.value = '';
    statusFilter.value = null;
    priorityFilter.value = null;
    sortBy.value = 'created_at';
    taskStore.clearSearchParams();
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

const handleEditTask = () => {
    $q.notify({
        type: 'info',
        message: '编辑功能正在开发中...',
        position: 'top',
    });
};

const handleDuplicateTask = (task: Task) => {
    $q.notify({
        type: 'info',
        message: `复制任务"${task.title}"功能正在开发中...`,
        position: 'top',
    });
};

const handleViewTask = (task: Task) => {
    $q.notify({
        type: 'info',
        message: `查看任务"${task.title}"功能正在开发中...`,
        position: 'top',
    });
};

const handleStatusChange = async (taskId: number, status: TaskStatus) => {
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
        message: `确定要删除任务"${task.title}"吗？`,
        cancel: true,
        persistent: true,
    }).onOk(() => {
        void (async () => {
            try {
                await taskStore.deleteTask(task.id);
                $q.notify({
                    type: 'positive',
                    message: '任务已删除',
                    position: 'top',
                });
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
        await taskStore.batchUpdateTasks(taskStore.selectedTasks, { status: 'completed' });
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
    $q.dialog({
        title: '确认批量删除',
        message: `确定要删除选中的 ${taskStore.selectedTasksCount} 个任务吗？`,
        cancel: true,
        persistent: true,
    }).onOk(() => {
        void (async () => {
            try {
                await taskStore.batchDeleteTasks(taskStore.selectedTasks);
                taskStore.clearSelection();
                $q.notify({
                    type: 'positive',
                    message: '任务已批量删除',
                    position: 'top',
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

const createTask = async () => {
    if (!newTaskTitle.value.trim()) {
        $q.notify({
            type: 'negative',
            message: '请输入任务标题',
            position: 'top',
        });
        return;
    }

    try {
        const taskData = {
            title: newTaskTitle.value,
            ...(newTaskDescription.value && { description: newTaskDescription.value }),
        };

        await taskStore.createTask(taskData);

        newTaskTitle.value = '';
        newTaskDescription.value = '';
        showCreateDialog.value = false;

        $q.notify({
            type: 'positive',
            message: '任务创建成功',
            position: 'top',
        });
    } catch {
        $q.notify({
            type: 'negative',
            message: '创建任务失败',
            position: 'top',
        });
    }
};

// 组件挂载时加载数据
onMounted(() => {
    void loadTasks();
});
</script>

<style scoped lang="scss">
.page-header {
    margin-bottom: 2rem;

    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 2rem;

        .title-section {
            flex: 1;

            .page-title {
                font-size: 1.75rem;
                font-weight: 700;
                color: #1f2937;
                margin: 0 0 0.5rem 0;
            }

            .page-subtitle {
                color: #6b7280;
                margin: 0;
                font-size: 1rem;
            }
        }

        .action-section {
            flex-shrink: 0;
        }
    }
}

.stats-section {
    margin-bottom: 2rem;

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;

        .stat-card {
            border-radius: 12px;
            transition: all 0.2s ease;

            &:hover {
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                transform: translateY(-2px);
            }

            .stat-content {
                display: flex;
                align-items: center;
                gap: 1rem;

                .stat-icon {
                    flex-shrink: 0;
                    width: 48px;
                    height: 48px;
                    border-radius: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: rgba(59, 130, 246, 0.1);
                }

                .stat-info {
                    flex: 1;

                    .stat-value {
                        font-size: 1.5rem;
                        font-weight: 700;
                        color: #1f2937;
                        line-height: 1.2;
                    }

                    .stat-label {
                        font-size: 0.875rem;
                        color: #6b7280;
                        margin-top: 0.25rem;
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

.filters-section {
    margin-bottom: 1.5rem;

    .filters-container {
        display: flex;
        gap: 1rem;
        align-items: center;
        flex-wrap: wrap;

        .search-box {
            flex: 1;
            min-width: 200px;
            max-width: 300px;
        }
    }
}

.batch-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #f8fafc;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    border: 1px solid #e2e8f0;

    .selected-info {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 500;
        color: #374151;
    }

    .batch-buttons {
        display: flex;
        gap: 0.5rem;
    }
}

.tasks-section {
    margin-bottom: 2rem;

    .tasks-container {
        border-radius: 12px;
        overflow: hidden;

        .tasks-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 1.5rem;
            background: #f8fafc;

            .header-left {
                display: flex;
                align-items: center;
                gap: 1rem;

                .tasks-count {
                    color: #6b7280;
                    font-size: 0.875rem;
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
                min-height: 200px;

                .loading-container {
                    text-align: center;

                    p {
                        margin-top: 1rem;
                        color: #6b7280;
                    }
                }
            }

            .empty-state {
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 300px;

                .empty-container {
                    text-align: center;

                    h3 {
                        color: #374151;
                        margin: 1rem 0 0.5rem 0;
                    }

                    p {
                        color: #6b7280;
                        margin-bottom: 2rem;
                    }
                }
            }

            .tasks-list {
                &.view-list {
                    display: flex;
                    flex-direction: column;
                    gap: 1rem;
                }

                &.view-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                    gap: 1rem;
                    padding: 1rem;
                }
            }
        }
    }
}

.pagination-section {
    display: flex;
    justify-content: center;
    margin-top: 2rem;
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

    .filters-section {
        .filters-container {
            flex-direction: column;
            align-items: stretch;

            .search-box {
                max-width: none;
            }

            .q-select {
                min-width: none !important;
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
</style>

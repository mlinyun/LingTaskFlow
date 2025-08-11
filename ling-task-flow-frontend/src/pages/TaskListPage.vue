<template>
    <q-page class="task-list-page">
        <!-- 页面头部 - 使用统一的PageHeader组件 -->
        <PageHeader
            icon="assignment"
            title-primary="任务列表"
            title-accent="管理中心"
            subtitle="高效管理您的所有任务，轻松规划工作流程"
            :primary-action="{
                icon: 'add',
                label: '新建任务',
                loading: loading,
            }"
            :secondary-actions="[
                { name: 'refresh', icon: 'refresh', tooltip: '刷新数据', class: 'fullscreen-btn' },
                {
                    name: 'filter',
                    icon: showFilters ? 'filter_list_off' : 'filter_list',
                    tooltip: showFilters ? '隐藏过滤器' : '显示过滤器',
                    class: 'download-btn',
                },
            ]"
            @primary-action="showCreateDialog = true"
            @secondary-action="handleSecondaryAction"
        />

        <!-- 主要内容区域 -->
        <div class="content-container">
            <!-- 过滤面板 -->
            <TaskFilterPanel
                v-if="showFilters"
                :search-query="searchQuery"
                :status-filter="filterStatus"
                :priority-filter="filterPriority"
                @update:search-query="val => (searchQuery = val)"
                @update:status-filter="status => (filterStatus = status)"
                @update:priority-filter="priority => (filterPriority = priority)"
                @clear-filters="resetFilters"
            />

            <!-- 任务列表内容 -->
            <div class="tasks-section">
                <!-- 空状态 -->
                <div v-if="!loading && filteredTasks.length === 0" class="empty-state">
                    <div class="empty-content">
                        <div class="empty-icon">
                            <q-icon name="assignment" />
                            <div class="empty-icon-glow"></div>
                        </div>
                        <h3 class="empty-title">
                            {{
                                searchQuery || filterStatus || filterPriority
                                    ? '没有找到匹配的任务'
                                    : '还没有任务'
                            }}
                        </h3>
                        <p class="empty-description">
                            {{
                                searchQuery || filterStatus || filterPriority
                                    ? '尝试调整筛选条件或清空搜索'
                                    : '创建您的第一个任务来开始高效工作'
                            }}
                        </p>
                        <q-btn
                            v-if="!searchQuery && !filterStatus && !filterPriority"
                            class="create-btn"
                            icon="add"
                            label="创建任务"
                            @click="showCreateDialog = true"
                            no-caps
                            unelevated
                        />
                        <q-btn
                            v-else
                            class="clear-btn"
                            icon="clear"
                            label="清空筛选"
                            @click="resetFilters"
                            no-caps
                            outline
                        />
                    </div>
                </div>

                <!-- 任务列表 -->
                <div v-else-if="filteredTasks.length > 0" class="tasks-container">
                    <div class="tasks-header">
                        <div class="header-left">
                            <h3 class="tasks-title">任务列表</h3>
                            <div class="tasks-count">
                                共 {{ filteredTasks.length }} 个任务
                                <span v-if="hasActiveFilters" class="filter-indicator"
                                    >（已筛选）</span
                                >
                            </div>
                        </div>
                        <div class="header-right">
                            <q-btn-dropdown icon="sort" label="排序" no-caps flat class="sort-btn">
                                <q-list>
                                    <q-item
                                        v-for="option in sortOptions"
                                        :key="option.value"
                                        clickable
                                        @click="sortBy = option.value"
                                        :active="sortBy === option.value"
                                    >
                                        <q-item-section>
                                            <q-item-label>{{ option.label }}</q-item-label>
                                        </q-item-section>
                                        <q-item-section avatar v-if="sortBy === option.value">
                                            <q-icon name="check" color="primary" />
                                        </q-item-section>
                                    </q-item>
                                </q-list>
                            </q-btn-dropdown>
                        </div>
                    </div>

                    <div class="tasks-grid">
                        <TaskCard
                            v-for="task in filteredTasks"
                            :key="task.id"
                            :task="task"
                            @view="viewTask"
                            @toggle-status="toggleTaskStatus"
                            @edit="editTask"
                            @delete="deleteTask"
                        />
                    </div>
                </div>
            </div>
        </div>

        <!-- 创建/编辑任务对话框 -->
        <TaskDialogForm
            v-model="showCreateDialog"
            :task="editingTask"
            @save="handleSaveTask"
            @cancel="handleCancelEdit"
        />

        <!-- 任务详情查看对话框 -->
        <TaskViewDialog v-model="showViewDialog" :task="viewingTask" />

        <!-- 加载状态 -->
        <q-inner-loading :showing="loading" color="primary" />
    </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import PageHeader from 'components/common/PageHeader.vue';
import { useTaskStore } from 'src/stores/task';
import type { Task, TaskStatus, TaskPriority } from 'src/types/task';
import TaskDialogForm from 'src/components/task-list/TaskDialogForm.vue';
import TaskViewDialog from 'src/components/task-list/TaskViewDialog.vue';
import TaskFilterPanel from 'src/components/task-list/TaskFilterPanel.vue';

// 任务卡片组件替代原生 DOM 结构
import TaskCard from 'src/components/task-list/TaskCard.vue';
const $q = useQuasar();
const taskStore = useTaskStore();

// 加载与弹窗
const loading = ref(false);
const showCreateDialog = ref(false);
const showViewDialog = ref(false);
const editingTask = ref<Task | null>(null);
const viewingTask = ref<Task | null>(null);

// 过滤/排序控制
const showFilters = ref(false);
const filterStatus = ref<TaskStatus | null>(null);
const filterPriority = ref<TaskPriority | null>(null);
const searchQuery = ref('');
type SortKey = 'created_at' | 'updated_at' | 'priority' | 'title';
const sortBy = ref<SortKey>('created_at');

// 移除内置的状态/优先级选项，改由 TaskFilterPanel 提供
// const statusOptions = [ ... ];
// const priorityOptions = [ ... ];
const sortOptions: Array<{ label: string; value: SortKey }> = [
    { label: '创建时间', value: 'created_at' },
    { label: '更新时间', value: 'updated_at' },
    { label: '优先级', value: 'priority' },
    { label: '标题', value: 'title' },
];

// 选项

// 任务列表与统计
const allTasks = computed(() => taskStore.tasks);

const filteredTasks = computed(() => {
    let tasks = [...allTasks.value];

    // 状态过滤
    if (filterStatus.value) tasks = tasks.filter(t => t.status === filterStatus.value);

    // 优先级过滤
    if (filterPriority.value) tasks = tasks.filter(t => t.priority === filterPriority.value);

    // 搜索过滤
    if (searchQuery.value) {
        const q = searchQuery.value.toLowerCase();
        tasks = tasks.filter(
            t =>
                t.title.toLowerCase().includes(q) ||
                (t.description ? t.description.toLowerCase().includes(q) : false) ||
                (t.tags || '').toLowerCase().includes(q),
        );
    }

    // 排序
    tasks.sort((a, b) => {
        const priorityOrder: Record<string, number> = { URGENT: 4, HIGH: 3, MEDIUM: 2, LOW: 1 };
        switch (sortBy.value) {
            case 'priority': {
                return (priorityOrder[b.priority] || 0) - (priorityOrder[a.priority] || 0);
            }
            case 'title':
                return a.title.localeCompare(b.title);
            case 'updated_at':
                return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
            case 'created_at':
            default:
                return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        }
    });

    return tasks;
});

// 删除：统计相关计算属性（总数、进行中、完成、待办、完成率）
// const totalTasks = computed(() => allTasks.value.length);
// const completedTasks = computed(() => allTasks.value.filter(t => t.status === 'COMPLETED').length);
// const activeTasks = computed(() => allTasks.value.filter(t => t.status !== 'COMPLETED').length);
// const todoTasks = computed(() => allTasks.value.filter(t => t.status === 'PENDING').length);
// const completionRate = computed(() => totalTasks.value ? ((completedTasks.value / totalTasks.value) * 100).toFixed(1) : '0.0');

const hasActiveFilters = computed(
    () => !!(filterStatus.value || filterPriority.value || searchQuery.value),
);

// 颜色与标签

// 事件与操作
const handleSecondaryAction = (name: string) => {
    switch (name) {
        case 'refresh':
            void fetchTasks();
            break;
        case 'filter':
            showFilters.value = !showFilters.value;
            break;
    }
};

// 删除：仅用于统计卡片点击的筛选函数
//

const resetFilters = () => {
    filterStatus.value = null;
    filterPriority.value = null;
    searchQuery.value = '';
};
// filters reset end

const viewTask = (task: Task) => {
    viewingTask.value = task;
    showViewDialog.value = true;
};

const editTask = (task: Task) => {
    editingTask.value = task;
    showCreateDialog.value = true;
};

const deleteTask = async (task: Task) => {
    try {
        loading.value = true;
        await taskStore.deleteTask(task.id);
        $q.notify({ type: 'positive', message: '任务已删除', position: 'top' });
    } catch (e) {
        console.error(e);
        $q.notify({ type: 'negative', message: '删除失败', position: 'top' });
    } finally {
        loading.value = false;
    }
};

const toggleTaskStatus = async (task: Task) => {
    const newStatus: TaskStatus = task.status === 'COMPLETED' ? 'PENDING' : 'COMPLETED';
    try {
        await taskStore.updateTask(task.id, { status: newStatus });
        $q.notify({ type: 'positive', message: '任务状态已更新', position: 'top' });
    } catch (e) {
        console.error(e);
        $q.notify({ type: 'negative', message: '更新状态失败', position: 'top' });
    }
};

const handleSaveTask = async (taskData: Partial<Task>) => {
    try {
        loading.value = true;
        if (editingTask.value) {
            await taskStore.updateTask(editingTask.value.id, taskData);
        } else {
            await taskStore.createTask(taskData as Omit<Task, 'id' | 'created_at' | 'updated_at'>);
        }
        handleCancelEdit();
    } catch (error) {
        console.error('保存任务失败:', error);
        $q.notify({ type: 'negative', message: '保存任务失败', position: 'top' });
    } finally {
        loading.value = false;
    }
};

const handleCancelEdit = () => {
    editingTask.value = null;
    showCreateDialog.value = false;
};

const fetchTasks = async () => {
    try {
        loading.value = true;
        await taskStore.fetchTasks();
    } catch (e) {
        console.error('获取任务列表失败', e);
        $q.notify({ type: 'negative', message: '获取任务列表失败', position: 'top' });
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    void fetchTasks();
});
</script>

<style scoped lang="scss">
// 页面整体样式 - 科技感设计
.task-list-page {
    background: #f8fafc;
    min-height: calc(100vh - 50px);
    padding: 1.5rem;
    position: relative;

    // 科技感网格纹理背景
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
        z-index: 0;
    }

    @media (max-width: 768px) {
        padding: 1rem;
    }
}

// 内容容器
.content-container {
    position: relative;
    z-index: 1;
    max-width: 1200px;
    margin: 0 auto;
}

// 统计面板样式（已删除）

// 过滤面板样式
.filters-section {
    margin-bottom: 2rem;
}

.filters-card {
    background: rgba(255, 255, 255, 0.98);
    border-radius: 20px;
    border: 1px solid rgba(59, 130, 246, 0.1);
    box-shadow:
        0 10px 32px rgba(14, 165, 233, 0.08),
        0 4px 16px rgba(59, 130, 246, 0.06),
        inset 0 1px 0 rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(20px);
    overflow: hidden;
}

.filters-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 2rem 1rem;
    border-bottom: 1px solid rgba(59, 130, 246, 0.1);
}

.filters-title {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 1.125rem;
    font-weight: 600;
    color: #1f2937;

    .q-icon {
        color: #3b82f6;
    }
}

.clear-filters-btn {
    color: #6b7280;

    &:hover {
        color: #3b82f6;
        background: rgba(59, 130, 246, 0.1);
    }
}

.filters-content {
    padding: 1rem 2rem 2rem;
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr;
    gap: 1.5rem;
    align-items: end;

    @media (max-width: 1024px) {
        grid-template-columns: 1fr 1fr;
    }

    @media (max-width: 640px) {
        grid-template-columns: 1fr;
    }
}

.filter-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.filter-label {
    font-size: 0.875rem;
    font-weight: 500;
    color: #374151;
    margin: 0;
}

.search-input {
    .q-field__control {
        border-radius: 12px;
    }
}

.filter-select {
    .q-field__control {
        border-radius: 12px;
    }
}

// 任务列表样式
.tasks-section {
    position: relative;
}

// 空状态样式
.empty-state {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 400px;
    padding: 3rem 1.5rem;
}

.empty-content {
    text-align: center;
    max-width: 400px;
}

.empty-icon {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 96px;
    height: 96px;
    margin-bottom: 2rem;

    .q-icon {
        font-size: 48px;
        color: #9ca3af;
        z-index: 2;
    }
}

.empty-icon-glow {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 80px;
    height: 80px;
    background: radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%);
    border-radius: 50%;
    animation: pulse 3s ease-in-out infinite;
}

.empty-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #374151;
    margin: 0 0 1rem 0;
}

.empty-description {
    font-size: 1rem;
    color: #6b7280;
    margin: 0 0 2rem 0;
    line-height: 1.6;
}

.create-btn {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    color: white;
    border-radius: 12px;
    padding: 0.75rem 2rem;
    font-weight: 600;
    box-shadow: 0 8px 24px rgba(59, 130, 246, 0.25);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

    &:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 32px rgba(59, 130, 246, 0.35);
    }
}

.clear-btn {
    border: 2px solid #d1d5db;
    color: #6b7280;
    border-radius: 12px;
    padding: 0.75rem 2rem;
    font-weight: 600;
    transition: all 0.3s ease;

    &:hover {
        border-color: #3b82f6;
        color: #3b82f6;
        background: rgba(59, 130, 246, 0.05);
    }
}

// 任务列表容器
.tasks-container {
    background: rgba(255, 255, 255, 0.98);
    border-radius: 20px;
    border: 1px solid rgba(59, 130, 246, 0.1);
    box-shadow:
        0 10px 32px rgba(14, 165, 233, 0.08),
        0 4px 16px rgba(59, 130, 246, 0.06),
        inset 0 1px 0 rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(20px);
    overflow: hidden;
}

.tasks-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 2rem;
    border-bottom: 1px solid rgba(59, 130, 246, 0.1);
}

.header-left {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.tasks-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1f2937;
    margin: 0;
}

.tasks-count {
    font-size: 0.875rem;
    color: #6b7280;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.filter-indicator {
    background: #3b82f6;
    color: white;
    padding: 0.125rem 0.5rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
}

.header-right {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.sort-btn {
    background: rgba(59, 130, 246, 0.08);
    border: 1px solid rgba(59, 130, 246, 0.15);
    color: #3b82f6;
    border-radius: 12px;
    padding: 0.5rem 1rem;
    font-weight: 500;
    transition: all 0.3s ease;

    &:hover {
        background: rgba(59, 130, 246, 0.15);
        border-color: rgba(59, 130, 246, 0.25);
    }
}

// 任务网格
.tasks-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
    gap: 1.5rem;
    padding: 2rem;

    @media (max-width: 768px) {
        grid-template-columns: 1fr;
        padding: 1.5rem;
    }
}

// 任务卡片
.task-card {
    position: relative;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 16px;
    border: 1px solid rgba(226, 232, 240, 0.8);
    padding: 1.5rem;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(10px);
    overflow: hidden;

    &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: 16px;
        padding: 1px;
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(14, 165, 233, 0.1));
        mask:
            linear-gradient(#fff 0 0) content-box,
            linear-gradient(#fff 0 0);
        mask-composite: exclude;
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    &:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(14, 165, 233, 0.15);
        border-color: rgba(59, 130, 246, 0.2);

        &::before {
            opacity: 1;
        }

        .task-actions {
            opacity: 1;
            visibility: visible;
        }
    }
}

// 任务状态指示器
.task-status-indicator {
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    border-radius: 0 4px 4px 0;

    &.status-pending {
        background: linear-gradient(180deg, #ef4444, #dc2626);
    }

    &.status-in_progress {
        background: linear-gradient(180deg, #f59e0b, #d97706);
    }

    &.status-completed {
        background: linear-gradient(180deg, #22c55e, #16a34a);
    }
}

// 任务内容
.task-content {
    position: relative;
    z-index: 1;
    padding-left: 1rem;
}

.task-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
    gap: 1rem;
}

.task-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: #1f2937;
    margin: 0;
    line-height: 1.4;
    flex: 1;
}

.task-meta {
    display: flex;
    gap: 0.5rem;
    flex-shrink: 0;
}

.priority-badge {
    font-size: 0.75rem;
    font-weight: 500;
    padding: 0.25rem 0.5rem;
    border-radius: 8px;
}

.status-badge {
    font-size: 0.75rem;
    font-weight: 500;
    padding: 0.25rem 0.5rem;
    border-radius: 8px;
}

.task-description {
    color: #6b7280;
    font-size: 0.9rem;
    line-height: 1.5;
    margin: 0 0 1rem 0;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.task-tags {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.tags-icon {
    color: #9ca3af;
    font-size: 14px;
}

.tags-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem;
}

.tag {
    background: rgba(59, 130, 246, 0.1);
    color: #3b82f6;
    font-size: 0.75rem;
    font-weight: 500;
    padding: 0.125rem 0.5rem;
    border-radius: 6px;
}

.tag-more {
    background: rgba(107, 114, 128, 0.1);
    color: #6b7280;
    font-size: 0.75rem;
    font-weight: 500;
    padding: 0.125rem 0.5rem;
    border-radius: 6px;
}

.task-timestamps {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    font-size: 0.75rem;
    color: #9ca3af;
}

.timestamp {
    display: flex;
    align-items: center;
    gap: 0.25rem;

    .q-icon {
        font-size: 14px;
    }
}

// 任务操作按钮
.task-actions {
    position: absolute;
    top: 1rem;
    right: 1rem;
    display: flex;
    gap: 0.5rem;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
    z-index: 2;
}

.action-btn {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    transition: all 0.2s ease;

    &:hover {
        transform: scale(1.1);
    }
}

// 动画
@keyframes pulse {
    0%,
    100% {
        opacity: 0.6;
        transform: translate(-50%, -50%) scale(1);
    }
    50% {
        opacity: 1;
        transform: translate(-50%, -50%) scale(1.1);
    }
}

// 响应式设计
@media (max-width: 640px) {
    .task-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }

    .task-meta {
        align-self: flex-end;
    }

    .task-timestamps {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.25rem;
    }
}

/* 新增卡片底部工具栏样式 */
.task-toolbar {
    margin-top: 0.5rem;
    display: flex;
    justify-content: flex-end;
}

/* 重置旧的浮动按钮样式，防止影响 */
.task-actions {
    position: static;
    top: auto;
    right: auto;
    opacity: 1;
    visibility: visible;
}
</style>

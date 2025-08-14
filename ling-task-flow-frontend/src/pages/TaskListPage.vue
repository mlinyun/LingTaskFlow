<template>
    <q-page class="task-list-page">
        <!-- 页面头部 - 使用统一的PageHeader组件 -->
        <PageHeader
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
                {
                    name: 'bulk-operations',
                    icon: showBulkOperations ? 'check_box' : 'check_box_outline_blank',
                    tooltip: showBulkOperations ? '退出批量模式' : '进入批量模式',
                    class: 'download-btn',
                },
            ]"
            icon="assignment"
            subtitle="高效管理您的所有任务，轻松规划工作流程"
            title-accent="管理中心"
            title-primary="任务列表"
            @primary-action="showCreateDialog = true"
            @secondary-action="handleSecondaryAction"
        />

        <!-- 主要内容区域 -->
        <div class="content-container">
            <!-- 过滤面板 -->
            <TaskFilterPanel
                v-if="showFilters"
                :priority-filter="filterPriority"
                :search-query="searchQuery"
                :status-filter="filterStatus"
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
                            no-caps
                            unelevated
                            @click="showCreateDialog = true"
                        />
                        <q-btn
                            v-else
                            class="clear-btn"
                            icon="clear"
                            label="清空筛选"
                            no-caps
                            outline
                            @click="resetFilters"
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
                            <!-- 虚拟滚动开关 -->
                            <q-toggle
                                v-model="enableVirtualScroll"
                                :disable="filteredTasks.length < 50"
                                :icon="enableVirtualScroll ? 'speed' : 'view_list'"
                                checked-icon="speed"
                                class="virtual-scroll-toggle"
                                color="primary"
                                label="虚拟滚动"
                                unchecked-icon="view_list"
                            >
                                <q-tooltip>
                                    {{
                                        enableVirtualScroll
                                            ? '已启用虚拟滚动（大数据优化）'
                                            : filteredTasks.length < 50
                                              ? '任务数少于50个，无需虚拟滚动'
                                              : '启用虚拟滚动（推荐50+任务）'
                                    }}
                                </q-tooltip>
                            </q-toggle>

                            <q-btn-dropdown class="sort-btn" flat icon="sort" label="排序" no-caps>
                                <q-list>
                                    <q-item
                                        v-for="option in sortOptions"
                                        :key="option.value"
                                        :active="sortBy === option.value"
                                        clickable
                                        @click="sortBy = option.value"
                                    >
                                        <q-item-section>
                                            <q-item-label>{{ option.label }}</q-item-label>
                                        </q-item-section>
                                        <q-item-section v-if="sortBy === option.value" avatar>
                                            <q-icon color="primary" name="check" />
                                        </q-item-section>
                                    </q-item>
                                </q-list>
                            </q-btn-dropdown>
                        </div>
                    </div>

                    <!-- 批量操作工具栏 -->
                    <div v-if="showBulkOperations" class="bulk-operations-toolbar">
                        <div class="toolbar-content">
                            <div class="selection-info">
                                <q-checkbox
                                    v-model="allSelected"
                                    :indeterminate="someSelected"
                                    class="all-select-checkbox"
                                    @update:model-value="toggleAllSelection"
                                />
                                <span class="selection-text">
                                    已选择 {{ taskStore.selectedTasks.length }} /
                                    {{ filteredTasks.length }} 个任务
                                </span>
                            </div>
                            <div class="batch-actions">
                                <q-btn
                                    :disable="taskStore.selectedTasks.length === 0"
                                    class="batch-btn"
                                    icon="play_arrow"
                                    label="批量进行中"
                                    no-caps
                                    unelevated
                                    @click="batchUpdateSelectedStatus('IN_PROGRESS')"
                                />
                                <q-btn
                                    :disable="taskStore.selectedTasks.length === 0"
                                    class="batch-btn"
                                    color="positive"
                                    icon="check"
                                    label="批量完成"
                                    no-caps
                                    unelevated
                                    @click="batchUpdateSelectedStatus('COMPLETED')"
                                />
                                <q-btn
                                    :disable="taskStore.selectedTasks.length === 0"
                                    class="batch-btn"
                                    color="warning"
                                    icon="undo"
                                    label="批量待处理"
                                    no-caps
                                    unelevated
                                    @click="batchUpdateSelectedStatus('PENDING')"
                                />
                                <q-btn
                                    class="clear-btn"
                                    flat
                                    icon="clear"
                                    label="清空选择"
                                    no-caps
                                    @click="clearSelection"
                                />
                            </div>
                        </div>
                    </div>

                    <!-- 拖拽提示 -->
                    <div v-if="sortBy === 'order' && hasActiveFilters" class="drag-info-banner">
                        <q-icon name="info" />
                        <span>清除筛选条件后可拖拽排序</span>
                    </div>

                    <!-- 任务列表 -->
                    <template v-if="enableVirtualScroll">
                        <!-- 虚拟滚动渲染（禁用拖拽，仅渲染可视内容） -->
                        <q-virtual-scroll
                            :items="virtualItems"
                            :virtual-scroll-item-size="VIRTUAL_ITEM_SIZE"
                            class="q-virtual-scroll tasks-grid"
                        >
                            <template #default="{ item: task }">
                                <TaskCard
                                    :key="task.id"
                                    :selectable="showBulkOperations"
                                    :selected="taskStore.selectedTasks.includes(task.id)"
                                    :task="task"
                                    @delete="deleteTask"
                                    @edit="editTask"
                                    @view="viewTask"
                                    @toggle-select="toggleTaskSelection"
                                    @toggle-status="confirmToggleStatus"
                                    @start-task="startTask"
                                    @pause-task="pauseTask"
                                    @resume-task="resumeTask"
                                />
                            </template>
                        </q-virtual-scroll>
                    </template>
                    <template v-else>
                        <!-- 传统拖拽渲染 -->
                        <VueDraggableNext
                            v-model="draggableTasks"
                            :animation="200"
                            :class="{ dragging: isDragging, 'drag-disabled': !canDrag }"
                            :disabled="!canDrag"
                            :force-fallback="false"
                            :handle="'.drag-handle'"
                            chosen-class="task-chosen"
                            class="tasks-grid"
                            drag-class="task-drag"
                            ghost-class="task-ghost"
                            item-key="id"
                            @end="handleDragEnd"
                            @start="handleDragStart"
                        >
                            <template #item="{ element: task }">
                                <TaskCard
                                    :key="task.id"
                                    :selectable="showBulkOperations"
                                    :selected="taskStore.selectedTasks.includes(task.id)"
                                    :task="task"
                                    @delete="deleteTask"
                                    @edit="editTask"
                                    @view="viewTask"
                                    @toggle-select="toggleTaskSelection"
                                    @toggle-status="confirmToggleStatus"
                                    @start-task="startTask"
                                    @pause-task="pauseTask"
                                    @resume-task="resumeTask"
                                >
                                    <!-- 拖拽手柄 -->
                                    <template #drag-handle>
                                        <template v-if="canDrag">
                                            <div class="drag-handle">
                                                <q-icon name="drag_indicator" />
                                            </div>
                                        </template>
                                    </template>
                                </TaskCard>
                            </template>
                        </VueDraggableNext>
                    </template>
                </div>
            </div>
        </div>

        <!-- 创建/编辑任务对话框 -->
        <TaskDialogForm
            v-model="showCreateDialog"
            :task="editingTask"
            @cancel="handleCancelEdit"
            @save="handleSaveTask"
        />

        <!-- 任务详情查看对话框 -->
        <TaskViewDialog v-model="showViewDialog" :task="viewingTask" />

        <!-- 加载状态 -->
        <q-inner-loading :showing="loading" color="primary" />
    </q-page>
</template>

<script lang="ts" setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { useQuasar } from 'quasar';
import VueDraggableNext from 'vue3-draggable-next';
import PageHeader from 'components/common/PageHeader.vue';
import TaskCard from 'components/task-list/TaskCard.vue';
import TaskFilterPanel from 'components/task-list/TaskFilterPanel.vue';
import TaskDialogForm from 'components/task-list/TaskDialogForm.vue';
import TaskViewDialog from 'components/task-list/TaskViewDialog.vue';
import { useTaskStore } from 'src/stores/task';
import type { Task, TaskPriority, TaskStatus } from 'src/types/task';
import { useGlobalConfirm } from 'src/composables/useGlobalConfirm';
import { ConfirmPresets } from 'src/composables/useConfirmDialog';
import { format } from 'date-fns';
import { cachedApi } from 'src/utils/cachedApi';
import { CacheConfigs } from 'src/utils/cache';
import { debounce, performanceMonitor } from 'src/utils/performance';

const $q = useQuasar();
const taskStore = useTaskStore();
const $confirm = useGlobalConfirm();

// 基础状态
const loading = ref(false);
const showCreateDialog = ref(false);
const showViewDialog = ref(false);
const editingTask = ref<Task | null>(null);
const viewingTask = ref<Task | null>(null);

// 过滤和搜索
const showFilters = ref(false);
const searchQuery = ref('');
const filterStatus = ref<TaskStatus | null>(null);
const filterPriority = ref<TaskPriority | null>(null);

// 防抖搜索
const debouncedSearch = debounce(() => {
    performanceMonitor.mark('search-start');
    // 搜索逻辑在 filteredTasks 计算属性中处理
    const duration = performanceMonitor.measure('search-execution', 'search-start');
    if (duration > 100) {
        console.warn(`搜索耗时: ${duration.toFixed(2)}ms`);
    }
}, 300);

// 监听搜索查询变化
watch(searchQuery, () => {
    debouncedSearch();
});

// 排序
type SortKey = 'created_at' | 'updated_at' | 'priority' | 'title' | 'order';
const sortBy = ref<SortKey>('created_at');
const sortOptions: Array<{ label: string; value: SortKey }> = [
    { label: '创建时间', value: 'created_at' },
    { label: '更新时间', value: 'updated_at' },
    { label: '优先级', value: 'priority' },
    { label: '标题', value: 'title' },
    { label: '自定义排序', value: 'order' },
];

// 批量操作
const showBulkOperations = ref(false);

// 拖拽状态
const isDragging = ref(false);
const dragSnapshot = ref<Task[]>([]);

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
            case 'order':
                return (a.order || 0) - (b.order || 0);
            case 'created_at':
            default:
                return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        }
    });

    return tasks;
});

// 新增：与 Draggable 绑定的可变数组，定义在 filteredTasks 之后
const draggableTasks = ref<Task[]>([]);

// 当筛选/排序变化时，同步 Draggable 数据源
watch(
    () => filteredTasks.value,
    newVal => {
        if (!isDragging.value) {
            draggableTasks.value = [...newVal];
        }
    },
    { immediate: true },
);

const hasActiveFilters = computed(
    () => !!(filterStatus.value || filterPriority.value || searchQuery.value),
);

// 判断是否可以拖拽（仅在自定义排序且无筛选时允许）
const canDrag = computed(() => {
    return sortBy.value === 'order' && !hasActiveFilters.value;
});

// 拖拽处理
const handleDragStart = () => {
    isDragging.value = true;
    // 保存拖拽前的快照，用于失败回滚
    dragSnapshot.value = [...taskStore.tasks];
};

const handleDragEnd = async (evt: { oldIndex: number; newIndex: number }) => {
    // 拖拽结束
    isDragging.value = false;

    // 如果位置没有变化，直接返回
    if (evt.oldIndex === evt.newIndex) {
        return;
    }

    try {
        // 基于可变的 draggableTasks 计算新的排序值
        const tasksWithOrder = draggableTasks.value.map((task, index) => ({
            id: task.id,
            sort_order: index + 1,
        }));

        // 调用后端API更新排序（内部会更新本地 tasks.order 并重新排序）
        await taskStore.updateTasksOrder(tasksWithOrder);

        $q.notify({
            type: 'positive',
            message: '排序已保存',
            position: 'top',
            timeout: 2000,
            icon: 'check_circle',
        });
    } catch (error) {
        console.error('更新任务排序失败:', error);

        // 回滚到拖拽前的全量任务状态
        if (dragSnapshot.value.length > 0) {
            taskStore.tasks.splice(0, taskStore.tasks.length, ...dragSnapshot.value);
        }

        $q.notify({
            type: 'negative',
            message: '排序保存失败，已回滚',
            position: 'top',
            timeout: 3000,
            icon: 'error',
        });
    }
};

// 过期判断与天数计算（假设已有实现）
const isOverdue = (task: Task) => {
    if (!task.due_date) return false;
    const now = new Date();
    const due = new Date(task.due_date);
    return task.status !== 'COMPLETED' && due < now;
};

// 批量选择相关
const allSelected = computed({
    get() {
        return (
            filteredTasks.value.length > 0 &&
            taskStore.selectedTasks.length === filteredTasks.value.length
        );
    },
    set(val: boolean) {
        toggleAllSelection(val);
    },
});

const someSelected = computed(() => {
    return (
        taskStore.selectedTasks.length > 0 &&
        taskStore.selectedTasks.length < filteredTasks.value.length
    );
});

function toggleAllSelection(val?: boolean) {
    const shouldSelectAll =
        typeof val === 'boolean'
            ? val
            : !(taskStore.selectedTasks.length === filteredTasks.value.length);
    if (shouldSelectAll) {
        taskStore.selectedTasks = filteredTasks.value.map(t => t.id);
    } else {
        taskStore.selectedTasks = [];
    }
}

function toggleTaskSelection(id: string) {
    const idx = taskStore.selectedTasks.indexOf(id);
    if (idx === -1) taskStore.selectedTasks.push(id);
    else taskStore.selectedTasks.splice(idx, 1);
}

function clearSelection() {
    taskStore.selectedTasks = [];
}

// 批量状态更新
async function batchUpdateSelectedStatus(targetStatus: TaskStatus) {
    const selectedIds = taskStore.selectedTasks.slice();
    if (selectedIds.length === 0) return;

    // 如包含逾期任务，提示确认
    const hasOverdue = filteredTasks.value.some(t => selectedIds.includes(t.id) && isOverdue(t));
    if (hasOverdue) {
        const ok = await $confirm.confirmWarning(
            '确认批量更新',
            '所选任务中包含已逾期任务，确定继续批量更新状态吗？',
            { confirmText: '继续', cancelText: '取消' },
        );
        if (!ok) return;
    }

    try {
        await taskStore.batchUpdateStatus(selectedIds, targetStatus);
        $q.notify({ type: 'positive', message: '批量更新成功' });
        clearSelection();
    } catch (e: unknown) {
        const msg = (e as { message?: string })?.message || '批量更新失败';
        $q.notify({ type: 'negative', message: msg });
    }
}

// 页面操作方法
const handleSecondaryAction = (name: string) => {
    switch (name) {
        case 'refresh':
            // 强制刷新，不使用缓存
            void fetchTasks(false);
            $q.notify({ type: 'info', message: '正在刷新数据...', timeout: 1000 });
            break;
        case 'filter':
            showFilters.value = !showFilters.value;
            break;
        case 'bulk-operations':
            showBulkOperations.value = !showBulkOperations.value;
            if (!showBulkOperations.value) clearSelection();
            break;
    }
};

const resetFilters = () => {
    filterStatus.value = null;
    filterPriority.value = null;
    searchQuery.value = '';
};

// 任务操作方法
const viewTask = (task: Task) => {
    viewingTask.value = task;
    showViewDialog.value = true;
};

const editTask = (task: Task) => {
    editingTask.value = task;
    showCreateDialog.value = true;
};

const deleteTask = async (task: Task) => {
    // 统一确认弹窗：删除任务
    const ok = await $confirm.confirm(ConfirmPresets.deleteTask(task.title));
    if (!ok) return;

    try {
        loading.value = true;
        await taskStore.deleteTask(task.id);
        $q.notify({ type: 'positive', message: '任务已删除' });
    } catch (e) {
        console.error(e);
        $q.notify({ type: 'negative', message: '删除失败' });
    } finally {
        loading.value = false;
    }
};

// 检查是否为逾期任务并提示用户
const checkOverdueAndConfirm = async (task: Task): Promise<boolean> => {
    if (isOverdue(task)) {
        const formatted = task.due_date
            ? format(new Date(task.due_date), 'yyyy-MM-dd HH:ss')
            : '未设置';
        return await $confirm.confirmWarning(
            '逾期任务操作确认',
            `该任务已逾期（截止时间：${formatted}），继续操作将会记录逾期次数。是否继续？`,
            { confirmText: '继续操作', cancelText: '取消', persistent: true },
        );
    }
    return true; // 非逾期任务直接通过
};

const confirmToggleStatus = async (task: Task) => {
    const newStatus = task.status === 'COMPLETED' ? 'PENDING' : 'COMPLETED';

    // 对于逾期任务，检查是否确认操作；若确认，则引导用户重设截止时间而不是直接改状态
    if (isOverdue(task) && (newStatus === 'COMPLETED' || newStatus === 'PENDING')) {
        const confirmed = await checkOverdueAndConfirm(task);
        if (!confirmed) return;
        // 打开编辑对话框以让用户重新设置截止时间
        editingTask.value = task;
        showCreateDialog.value = true;
        $q.notify({ type: 'info', message: '请重新设置该任务的截止时间后再更新状态' });
        return;
    }

    try {
        await taskStore.updateTask(task.id, { status: newStatus });
        $q.notify({ type: 'positive', message: '任务状态已更新' });
    } catch (e) {
        console.error(e);
        // 检查是否是逾期限制错误
        const error = e as { response?: { data?: { detail?: string } } };
        if (error.response?.data?.detail?.includes('逾期')) {
            $q.notify({
                type: 'warning',
                message: error.response.data.detail,
                timeout: 5000,
            });
        } else {
            $q.notify({ type: 'negative', message: '更新状态失败' });
        }
    }
};

// 开始任务：PENDING -> IN_PROGRESS
const startTask = async (task: Task) => {
    if (task.status !== 'PENDING') {
        // 非法状态保护：仅允许待处理任务开始
        await taskStore.updateTask(task.id, { status: 'IN_PROGRESS' });
        $q.notify({ type: 'positive', message: '已开始任务' });
        return;
    }

    // 对于逾期任务，检查是否确认操作；若确认，则引导用户重设截止时间而不是直接改状态
    if (isOverdue(task)) {
        const confirmed = await checkOverdueAndConfirm(task);
        if (!confirmed) return;
        // 打开编辑对话框以让用户重新设置截止时间
        editingTask.value = task;
        showCreateDialog.value = true;
        $q.notify({ type: 'info', message: '请重新设置该任务的截止时间后再开始任务' });
        return;
    }

    try {
        await taskStore.updateTask(task.id, { status: 'IN_PROGRESS' });
        $q.notify({ type: 'positive', message: '已开始任务' });
    } catch (e) {
        console.error(e);
        // 检查是否是逾期限制错误
        const error = e as { response?: { data?: { detail?: string } } };
        if (error.response?.data?.detail?.includes('逾期')) {
            $q.notify({
                type: 'warning',
                message: error.response.data.detail,
                timeout: 5000,
            });
        } else {
            $q.notify({ type: 'negative', message: '开始任务失败' });
        }
    }
};

// 暂停任务：IN_PROGRESS -> ON_HOLD
const pauseTask = async (task: Task) => {
    try {
        await taskStore.updateTask(task.id, { status: 'ON_HOLD' });
        $q.notify({ type: 'warning', message: '任务已暂停' });
    } catch (e) {
        console.error(e);
        $q.notify({ type: 'negative', message: '暂停任务失败' });
    }
};

// 恢复任务：ON_HOLD -> IN_PROGRESS
const resumeTask = async (task: Task) => {
    // 对于逾期任务，检查是否确认操作；若确认，则引导用户重设截止时间而不是直接改状态
    if (isOverdue(task)) {
        const confirmed = await checkOverdueAndConfirm(task);
        if (!confirmed) return;
        editingTask.value = task;
        showCreateDialog.value = true;
        $q.notify({ type: 'info', message: '请重新设置该任务的截止时间后再恢复任务' });
        return;
    }

    try {
        await taskStore.updateTask(task.id, { status: 'IN_PROGRESS' });
        $q.notify({ type: 'positive', message: '任务已恢复进行' });
    } catch (e) {
        console.error(e);
        // 检查是否是逾期限制错误
        const error = e as { response?: { data?: { detail?: string } } };
        if (error.response?.data?.detail?.includes('逾期')) {
            $q.notify({
                type: 'warning',
                message: error.response.data.detail,
                timeout: 5000,
            });
        } else {
            $q.notify({ type: 'negative', message: '恢复任务失败' });
        }
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
        $q.notify({ type: 'negative', message: '保存任务失败' });
    } finally {
        loading.value = false;
    }
};

const handleCancelEdit = () => {
    editingTask.value = null;
    showCreateDialog.value = false;
};

// 获取任务列表（使用缓存API）
const fetchTasks = async (useCache = true) => {
    try {
        loading.value = true;
        performanceMonitor.mark('fetchTasks-start');

        if (useCache) {
            // 使用缓存API获取任务列表
            try {
                const response = await cachedApi.get('/tasks/', {
                    params: {
                        page: taskStore.currentPage,
                        page_size: taskStore.pageSize,
                        status: taskStore.searchParams.status,
                        priority: taskStore.searchParams.priority,
                        search: taskStore.searchParams.search,
                        ordering: taskStore.searchParams.ordering,
                    },
                    cache: {
                        key: 'tasks',
                        config: CacheConfigs.TASKS,
                        forceRefresh: false,
                    },
                });

                // 设置任务数据和分页信息（axios拦截器已将标准响应解包）
                let taskData = response.data || [];
                let meta = (response as unknown as { meta?: Record<string, unknown> }).meta || {};
                let pagination =
                    (meta as { pagination?: Record<string, unknown> }).pagination || {};

                // 如果是从缓存返回且数据为空，执行一次强制刷新，避免长期缓存空数据
                if (
                    (response as unknown as { fromCache?: boolean }).fromCache &&
                    (!Array.isArray(taskData) || taskData.length === 0)
                ) {
                    // 先清理缓存，再强制刷新
                    cachedApi.invalidateCache('tasks', CacheConfigs.TASKS);
                    const fresh = await cachedApi.get('/tasks/', {
                        params: {
                            page: taskStore.currentPage,
                            page_size: taskStore.pageSize,
                            status: taskStore.searchParams.status,
                            priority: taskStore.searchParams.priority,
                            search: taskStore.searchParams.search,
                            ordering: taskStore.searchParams.ordering,
                        },
                        cache: {
                            key: 'tasks',
                            config: CacheConfigs.TASKS,
                            forceRefresh: true,
                        },
                    });
                    taskData = fresh.data || [];
                    meta = (fresh as unknown as { meta?: Record<string, unknown> }).meta || {};
                    pagination =
                        (meta as { pagination?: Record<string, unknown> }).pagination || {};
                }

                // Debug: Log the data structure to console
                console.log('[fetchTasks] taskData:', taskData);
                console.log('[fetchTasks] meta:', meta);
                console.log('[fetchTasks] pagination:', pagination);

                taskStore.setTasks(taskData);
                const totalCountRaw = (pagination as Record<string, unknown>)['total_count'];
                const totalCount =
                    typeof totalCountRaw === 'number'
                        ? totalCountRaw
                        : Array.isArray(taskData)
                          ? taskData.length
                          : 0;
                taskStore.setTotalTasks(totalCount);

                // Debug: Log the store state after setting
                console.log('[fetchTasks] Store tasks count:', taskStore.tasks.length);
                console.log('[fetchTasks] Store totalTasks:', taskStore.totalTasks);
            } catch (error: unknown) {
                console.error('获取任务列表失败', error);
                $q.notify({ type: 'negative', message: '获取任务列表失败' });
            }
        } else {
            // 强制刷新，不使用缓存
            await taskStore.fetchTasks();
            // 清除相关缓存
            cachedApi.invalidateCache('tasks', CacheConfigs.TASKS);
        }

        const duration = performanceMonitor.measure('fetchTasks-execution', 'fetchTasks-start');
        if (duration > 1000) {
            console.warn(`任务列表加载耗时: ${duration.toFixed(2)}ms`);
        }
    } catch (e) {
        console.error('获取任务列表失败', e);
        $q.notify({ type: 'negative', message: '获取任务列表失败' });
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    performanceMonitor.mark('component-mount-start');
    void fetchTasks();
    const mountDuration = performanceMonitor.measure('component-mount', 'component-mount-start');
    console.log(`TaskListPage 组件挂载耗时: ${mountDuration.toFixed(2)}ms`);
});

onUnmounted(() => {
    // 清理性能监控数据
    performanceMonitor.clear();
    // 清理选中状态
    clearSelection();
});

// 大数据渲染优化：虚拟滚动开关（默认：当任务数>=200时自动开启）
const enableVirtualScroll = ref(false);
watch(
    () => filteredTasks.value.length,
    len => {
        if (len >= 200 && !enableVirtualScroll.value) enableVirtualScroll.value = true;
        if (len < 100 && enableVirtualScroll.value) enableVirtualScroll.value = false;
    },
    { immediate: true },
);

// 估算卡片高度（用于 QVirtualScroll 初始渲染）
const VIRTUAL_ITEM_SIZE = computed(() => (window.innerWidth <= 768 ? 280 : 320));

// 将 draggableTasks 作为虚拟滚动 items 数据源
const virtualItems = computed(() => draggableTasks.value);
</script>

<style scoped>
.bulk-operations-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(255, 255, 255, 0.98);
    border: 1px solid rgba(59, 130, 246, 0.15);
    border-radius: 16px;
    padding: 0.5rem 1rem;
    margin: 2rem 2rem 0;
}

.toolbar-content {
    display: flex;
    align-items: center;
    width: 100%;
    justify-content: space-between;
}
.selection-info {
    display: flex;
    align-items: center;
    gap: 8px;
}
.batch-actions {
    display: flex;
    align-items: center;
    gap: 8px;
}
.batch-btn {
    min-width: 120px;
}
.clear-btn {
    margin-left: 8px;
}
</style>

<style lang="scss" scoped>
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

.toolbar-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
}

.selection-info {
    display: flex;
    align-items: center;
    gap: 8px;
}

.batch-actions {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.task-selected {
    outline: 2px solid rgba(59, 130, 246, 0.35);
}
.drag-info-banner {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(59, 130, 246, 0.08);
    border: 1px dashed rgba(59, 130, 246, 0.4);
    color: #2563eb;
    padding: 8px 12px;
    border-radius: 10px;
    margin: 12px 24px 0;
}

.tasks-grid.drag-disabled {
    opacity: 0.8;
}

.task-ghost {
    opacity: 0.5 !important;
}

.task-chosen {
    transform: scale(1.02);
}

.task-drag {
    cursor: grabbing !important;
}

.drag-handle {
    position: absolute;
    top: 10px;
    right: 10px;
    z-index: 3;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 8px;
    background: rgba(59, 130, 246, 0.08);
    border: 1px solid rgba(59, 130, 246, 0.15);
    color: #3b82f6;
    cursor: grab;
}

.drag-handle:hover {
    background: rgba(59, 130, 246, 0.15);
    border-color: rgba(59, 130, 246, 0.25);
}

/* 任务网格 */
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

/* 虚拟滚动样式 - 保持网格布局 */
.q-virtual-scroll .q-virtual-scroll__content {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
    gap: 1.5rem;
    padding: 2rem;

    @media (max-width: 768px) {
        grid-template-columns: 1fr;
        padding: 1.5rem;
    }
}

/* 虚拟滚动容器高度 */
.q-virtual-scroll.tasks-grid {
    height: calc(100vh - 200px);
    min-height: 400px;
}
</style>

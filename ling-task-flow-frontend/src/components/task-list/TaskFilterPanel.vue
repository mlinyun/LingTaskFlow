<template>
    <div class="modern-filter-panel">
        <!-- 顶部工具栏 -->
        <div class="filter-toolbar">
            <div class="toolbar-left">
                <q-icon class="toolbar-icon" name="tune" size="18px" />
                <span class="toolbar-title">智能筛选</span>
                <q-badge
                    v-if="hasActiveFilters"
                    :label="activeFiltersCount"
                    color="primary"
                    rounded
                />
            </div>
            <div class="toolbar-right">
                <q-btn
                    v-if="hasActiveFilters"
                    class="reset-btn"
                    color="grey-7"
                    dense
                    flat
                    icon="refresh"
                    size="sm"
                    @click="handleClearFilters"
                >
                    <q-tooltip>清空所有筛选</q-tooltip>
                </q-btn>
            </div>
        </div>

        <!-- 主要筛选区域 -->
        <div class="filter-main">
            <!-- 搜索栏 - 独立突出显示 -->
            <div class="search-section">
                <q-input
                    :model-value="searchQuery"
                    class="search-input-modern"
                    debounce="250"
                    dense
                    filled
                    placeholder="🔍 搜索任务标题、描述..."
                    @update:model-value="handleSearchChange"
                >
                    <template v-slot:append>
                        <q-icon v-if="!searchQuery" color="grey-5" name="search" />
                        <q-btn
                            v-else
                            color="grey-6"
                            dense
                            flat
                            icon="close"
                            round
                            size="xs"
                            @click="handleRemoveSearchFilter"
                        />
                    </template>
                </q-input>
            </div>

            <!-- 快速筛选器 -->
            <div class="quick-filters">
                <!-- 状态筛选 -->
                <div class="filter-pill-group">
                    <div class="filter-label-compact">状态</div>
                    <div class="pill-container">
                        <q-btn
                            v-for="status in statusOptions"
                            :key="status.value"
                            :color="
                                statusFilter === status.value
                                    ? getStatusColor(status.value)
                                    : 'grey-4'
                            "
                            :outline="statusFilter !== status.value"
                            :text-color="statusFilter === status.value ? 'white' : 'grey-7'"
                            :unelevated="statusFilter === status.value"
                            class="filter-pill"
                            dense
                            no-caps
                            size="sm"
                            @click="handleStatusToggle(status.value)"
                        >
                            <q-icon
                                :name="getStatusIcon(status.value)"
                                class="q-mr-xs"
                                size="14px"
                            />
                            {{ status.label }}
                        </q-btn>
                        <q-btn
                            v-if="statusFilter"
                            class="clear-pill-btn"
                            color="grey-5"
                            dense
                            flat
                            icon="close"
                            round
                            size="xs"
                            @click="handleRemoveStatusFilter"
                        />
                    </div>
                </div>

                <!-- 优先级筛选 -->
                <div class="filter-pill-group">
                    <div class="filter-label-compact">优先级</div>
                    <div class="pill-container">
                        <q-btn
                            v-for="priority in priorityOptions"
                            :key="priority.value"
                            :color="
                                priorityFilter === priority.value
                                    ? getPriorityColor(priority.value)
                                    : 'grey-4'
                            "
                            :outline="priorityFilter !== priority.value"
                            :text-color="priorityFilter === priority.value ? 'white' : 'grey-7'"
                            :unelevated="priorityFilter === priority.value"
                            class="filter-pill"
                            dense
                            no-caps
                            size="sm"
                            @click="handlePriorityToggle(priority.value)"
                        >
                            <q-icon
                                :name="getPriorityIcon(priority.value)"
                                class="q-mr-xs"
                                size="14px"
                            />
                            {{ priority.label }}
                        </q-btn>
                        <q-btn
                            v-if="priorityFilter"
                            class="clear-pill-btn"
                            color="grey-5"
                            dense
                            flat
                            icon="close"
                            round
                            size="xs"
                            @click="handleRemovePriorityFilter"
                        />
                    </div>
                </div>

                <!-- 排序插槽 -->
                <div v-if="$slots.sort" class="filter-pill-group">
                    <div class="filter-label-compact">排序</div>
                    <div class="pill-container">
                        <slot name="sort"></slot>
                    </div>
                </div>
            </div>
        </div>

        <!-- 活动筛选标签（底部显示） -->
        <transition name="slide-up">
            <div v-if="hasActiveFilters" class="active-tags-footer">
                <div class="active-tags-label">已启用筛选：</div>
                <div class="active-tags">
                    <q-chip
                        v-if="searchQuery"
                        color="primary"
                        icon="search"
                        removable
                        size="sm"
                        text-color="white"
                        @remove="handleRemoveSearchFilter"
                    >
                        "{{ searchQuery }}"
                    </q-chip>
                    <q-chip
                        v-if="statusFilter"
                        :color="getStatusColor(statusFilter)"
                        :icon="getStatusIcon(statusFilter)"
                        removable
                        size="sm"
                        text-color="white"
                        @remove="handleRemoveStatusFilter"
                    >
                        {{ getStatusLabel(statusFilter) }}
                    </q-chip>
                    <q-chip
                        v-if="priorityFilter"
                        :color="getPriorityColor(priorityFilter)"
                        :icon="getPriorityIcon(priorityFilter)"
                        removable
                        size="sm"
                        text-color="white"
                        @remove="handleRemovePriorityFilter"
                    >
                        {{ getPriorityLabel(priorityFilter) }}
                    </q-chip>
                </div>
            </div>
        </transition>
    </div>
</template>

<script lang="ts" setup>
import { computed, nextTick } from 'vue';
import type { TaskPriority, TaskStatus } from 'src/types/task';

interface Props {
    searchQuery: string;
    statusFilter: TaskStatus | null;
    priorityFilter: TaskPriority | null;
    sortBy?: string; // 兼容保留
}

interface Emits {
    (e: 'update:search-query', value: string): void;
    (e: 'update:status-filter', value: TaskStatus | null): void;
    (e: 'update:priority-filter', value: TaskPriority | null): void;
    (e: 'filter-change'): void;
    (e: 'clear-filters'): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const statusOptions = [
    { label: '待处理', value: 'PENDING' as TaskStatus },
    { label: '进行中', value: 'IN_PROGRESS' as TaskStatus },
    { label: '已完成', value: 'COMPLETED' as TaskStatus },
    { label: '已取消', value: 'CANCELLED' as TaskStatus },
    { label: '暂停', value: 'ON_HOLD' as TaskStatus },
];

const priorityOptions = [
    { label: '低', value: 'LOW' as TaskPriority },
    { label: '中', value: 'MEDIUM' as TaskPriority },
    { label: '高', value: 'HIGH' as TaskPriority },
    { label: '紧急', value: 'URGENT' as TaskPriority },
];

const hasActiveFilters = computed(
    () => !!(props.searchQuery || props.statusFilter || props.priorityFilter),
);

const activeFiltersCount = computed(() => {
    let count = 0;
    if (props.searchQuery) count += 1;
    if (props.statusFilter) count += 1;
    if (props.priorityFilter) count += 1;
    return count;
});

const getStatusIcon = (status: TaskStatus): string =>
    ({
        PENDING: 'schedule',
        IN_PROGRESS: 'play_arrow',
        COMPLETED: 'check_circle',
        CANCELLED: 'cancel',
        ON_HOLD: 'pause_circle',
    })[status] || 'help';

const getStatusColor = (status: TaskStatus): string =>
    ({
        PENDING: 'orange',
        IN_PROGRESS: 'blue',
        COMPLETED: 'green',
        CANCELLED: 'red',
        ON_HOLD: 'grey',
    })[status] || 'grey';

const getStatusLabel = (status: TaskStatus): string =>
    ({
        PENDING: '待处理',
        IN_PROGRESS: '进行中',
        COMPLETED: '已完成',
        CANCELLED: '已取消',
        ON_HOLD: '暂停',
    })[status] || '未知';

const getPriorityColor = (priority: TaskPriority): string =>
    ({
        LOW: 'green',
        MEDIUM: 'blue',
        HIGH: 'orange',
        URGENT: 'red',
    })[priority] || 'blue';

const getPriorityLabel = (priority: TaskPriority): string =>
    ({
        LOW: '低',
        MEDIUM: '中',
        HIGH: '高',
        URGENT: '紧急',
    })[priority] || '中';

const getPriorityIcon = (priority: TaskPriority): string =>
    ({
        LOW: 'keyboard_arrow_down',
        MEDIUM: 'remove',
        HIGH: 'keyboard_arrow_up',
        URGENT: 'priority_high',
    })[priority] || 'remove';

const handleSearchChange = (value: string | number | null) => {
    const searchValue = value ? String(value) : '';
    emit('update:search-query', searchValue);
    emit('filter-change');
};

const handleStatusChange = (value: TaskStatus | null) => {
    emit('update:status-filter', value);
    emit('filter-change');
};

const handlePriorityChange = (value: TaskPriority | null) => {
    emit('update:priority-filter', value);
    emit('filter-change');
};

// 切换型按钮：再次点击则取消
const handleStatusToggle = (value: TaskStatus) => {
    const next = props.statusFilter === value ? null : value;
    handleStatusChange(next);
};

const handlePriorityToggle = (value: TaskPriority) => {
    const next = props.priorityFilter === value ? null : value;
    handlePriorityChange(next);
};

const handleClearFilters = () => emit('clear-filters');

const handleRemoveSearchFilter = () => {
    emit('update:search-query', '');
    void nextTick(() => emit('filter-change'));
};

const handleRemoveStatusFilter = () => {
    emit('update:status-filter', null);
    void nextTick(() => emit('filter-change'));
};

const handleRemovePriorityFilter = () => {
    emit('update:priority-filter', null);
    void nextTick(() => emit('filter-change'));
};
</script>

<style lang="scss" scoped>
/* 容器 */
.modern-filter-panel {
    background: rgba(255, 255, 255, 0.98);
    border-radius: 16px;
    border: 1px solid rgba(59, 130, 246, 0.12);
    box-shadow:
        0 10px 32px rgba(14, 165, 233, 0.08),
        0 4px 16px rgba(59, 130, 246, 0.06),
        inset 0 1px 0 rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(14px);
    margin-bottom: 1rem;
}

/* 工具栏 */
.filter-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid rgba(59, 130, 246, 0.1);
}

.toolbar-left {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.toolbar-icon {
    color: #3b82f6;
}

.toolbar-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #1f2937;
}

.reset-btn {
    margin-left: 0.25rem;
}

/* 主体 */
.filter-main {
    padding: 0.75rem 1rem 1rem;
}

/* 搜索区域 */
.search-section {
    margin-bottom: 0.5rem;
}

.search-input-modern {
    :deep(.q-field__control) {
        border-radius: 12px;
    }
}

/* 快速筛选（Pills） */
.quick-filters {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem 1rem;

    @media (max-width: 720px) {
        grid-template-columns: 1fr;
    }
}

.filter-pill-group {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.filter-label-compact {
    font-size: 12px;
    color: #6b7280;
    font-weight: 600;
    letter-spacing: 0.02em;
}

.pill-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    align-items: center;
}

.filter-pill {
    border-radius: 999px;
    padding: 4px 10px;
}

.clear-pill-btn {
    margin-left: -0.25rem;
}

/* 活动标签 */
.active-tags-footer {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    border-top: 1px dashed rgba(107, 114, 128, 0.3);
    padding: 0.5rem 1rem;
    background: rgba(248, 250, 252, 0.9);
}

.active-tags-label {
    font-size: 12px;
    color: #6b7280;
    white-space: nowrap;
}

.active-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
}

/* 进入动效 */
.slide-up-enter-active,
.slide-up-leave-active {
    transition: all 0.18s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
    opacity: 0;
    transform: translateY(6px);
}
</style>

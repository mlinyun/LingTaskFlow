<template>
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
                        :model-value="searchQuery"
                        placeholder="搜索任务标题、描述或标签..."
                        outlined
                        rounded
                        clearable
                        class="search-input"
                        @update:model-value="handleSearchChange"
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
                        :model-value="statusFilter"
                        :options="statusOptions"
                        outlined
                        rounded
                        clearable
                        emit-value
                        map-options
                        placeholder="选择状态"
                        class="filter-select"
                        @update:model-value="handleStatusChange"
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
                        :model-value="priorityFilter"
                        :options="priorityOptions"
                        outlined
                        rounded
                        clearable
                        emit-value
                        map-options
                        placeholder="选择优先级"
                        class="filter-select"
                        @update:model-value="handlePriorityChange"
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
                                    <q-item-label :class="`text-${getPriorityColor(opt.value)}`">
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
                        :model-value="sortBy"
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
                        @click="handleClearFilters"
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
                        @click="handleClearFilters"
                    />
                </div>
                <div class="active-filters-chips">
                    <q-chip
                        v-if="searchQuery"
                        removable
                        color="blue"
                        text-color="white"
                        icon="search"
                        @remove="handleRemoveSearchFilter"
                    >
                        搜索: {{ searchQuery }}
                    </q-chip>
                    <q-chip
                        v-if="statusFilter"
                        removable
                        :color="getStatusColor(statusFilter)"
                        text-color="white"
                        :icon="getStatusIcon(statusFilter)"
                        @remove="handleRemoveStatusFilter"
                    >
                        状态: {{ getStatusLabel(statusFilter) }}
                    </q-chip>
                    <q-chip
                        v-if="priorityFilter"
                        removable
                        :color="getPriorityColor(priorityFilter)"
                        text-color="white"
                        :icon="getPriorityIcon(priorityFilter)"
                        @remove="handleRemovePriorityFilter"
                    >
                        优先级: {{ getPriorityLabel(priorityFilter) }}
                    </q-chip>
                </div>
            </div>
        </q-card-section>
    </q-card>
</template>

<script setup lang="ts">
import { computed, nextTick } from 'vue';
import type { TaskStatus, TaskPriority } from '../../types';

// Props
interface Props {
    searchQuery: string;
    statusFilter: TaskStatus | null;
    priorityFilter: TaskPriority | null;
    sortBy: string;
}

const props = defineProps<Props>();

// Emits
interface Emits {
    (e: 'update:search-query', value: string): void;
    (e: 'update:status-filter', value: TaskStatus | null): void;
    (e: 'update:priority-filter', value: TaskPriority | null): void;
    (e: 'update:sort-by', value: string): void;
    (e: 'filter-change'): void;
    (e: 'clear-filters'): void;
}

const emit = defineEmits<Emits>();

// 筛选选项
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

const sortOptions = [
    { label: '创建时间（最新）', value: '-created_at' },
    { label: '创建时间（最早）', value: 'created_at' },
    { label: '更新时间（最新）', value: '-updated_at' },
    { label: '优先级（高到低）', value: '-priority' },
    { label: '优先级（低到高）', value: 'priority' },
    { label: '到期时间', value: 'due_date' },
];

// 计算属性
const hasActiveFilters = computed(() => {
    return !!(props.searchQuery || props.statusFilter || props.priorityFilter);
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

// 优先级相关函数
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

// 事件处理函数
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

const handleSortChange = (value: string) => {
    emit('update:sort-by', value);
    emit('filter-change');
};

const handleClearFilters = () => {
    emit('clear-filters');
};

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

<style scoped lang="scss">
// 紧凑的筛选卡片样式
.filters-card {
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
    border-radius: 8px;
    overflow: hidden;
    background: white;
    border: 1px solid rgba(59, 130, 246, 0.15);

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

// 响应式设计
@media (max-width: 768px) {
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
                    width: 100%;
                    justify-content: center;
                }
            }

            .active-filters-chips {
                flex-direction: column;
                gap: 0.5rem;

                .q-chip {
                    align-self: flex-start;
                }
            }
        }
    }
}

@media (max-width: 480px) {
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

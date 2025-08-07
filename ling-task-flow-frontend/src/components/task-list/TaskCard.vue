<template>
    <q-card
        class="task-card"
        :class="{
            'task-card--selected': props.selected || false,
            'task-card--completed': task.status === 'COMPLETED',
            [`priority-${task.priority.toLowerCase()}`]: true,
        }"
        flat
        bordered
    >
        <!-- 任务头部 -->
        <div class="task-header">
            <div class="task-header-content">
                <q-checkbox
                    :model-value="props.selected || false"
                    @update:model-value="$emit('toggle-selection', task.id)"
                    class="task-checkbox"
                />

                <!-- 只读优先级显示 -->
                <q-chip
                    :color="getPriorityColor(task.priority)"
                    :icon="getPriorityIcon(task.priority)"
                    text-color="white"
                    size="sm"
                    class="priority-readonly"
                    dense
                >
                    {{ getPriorityLabel(task.priority) }}
                </q-chip>

                <!-- 任务操作菜单 -->
                <div class="task-actions">
                    <q-btn-dropdown
                        flat
                        dense
                        round
                        icon="more_vert"
                        size="sm"
                        no-caps
                        class="text-grey-6"
                    >
                        <q-list dense>
                            <q-item clickable v-close-popup @click="emit('edit', task)">
                                <q-item-section avatar>
                                    <q-icon name="edit" size="xs" />
                                </q-item-section>
                                <q-item-section>编辑</q-item-section>
                            </q-item>
                            <q-item clickable v-close-popup @click="emit('view', task)">
                                <q-item-section avatar>
                                    <q-icon name="visibility" size="xs" />
                                </q-item-section>
                                <q-item-section>查看</q-item-section>
                            </q-item>
                            <q-item clickable v-close-popup @click="emit('duplicate', task)">
                                <q-item-section avatar>
                                    <q-icon name="content_copy" size="xs" />
                                </q-item-section>
                                <q-item-section>复制</q-item-section>
                            </q-item>
                            <q-separator />
                            <q-item clickable v-close-popup @click="handleDeleteTask">
                                <q-item-section avatar>
                                    <q-icon name="delete" size="xs" color="negative" />
                                </q-item-section>
                                <q-item-section class="text-negative">删除</q-item-section>
                            </q-item>
                        </q-list>
                    </q-btn-dropdown>
                </div>
            </div>
        </div>

        <!-- 任务内容 -->
        <div class="task-content">
            <div class="task-title" @click="emit('view', task)">
                {{ task.title }}
            </div>

            <div v-if="task.description" class="task-description">
                {{ task.description }}
            </div>

            <!-- 为没有描述的任务提供占位空间 -->
            <div v-else class="task-description task-description--empty">
                <!-- 空描述占位 -->
            </div>

            <!-- 任务标签 -->
            <div v-if="getTaskTags(task.tags).length > 0" class="task-tags">
                <q-chip
                    v-for="tag in getTaskTags(task.tags)"
                    :key="tag"
                    size="sm"
                    color="grey-3"
                    text-color="grey-8"
                    class="task-tag"
                    dense
                >
                    {{ tag }}
                </q-chip>
            </div>
        </div>

        <!-- 任务元信息 -->
        <div class="task-footer">
            <div class="task-meta">
                <!-- 截止日期 -->
                <div
                    v-if="task.due_date"
                    class="task-due-date"
                    :class="getDueDateClass(task.due_date)"
                >
                    <q-icon :name="getDueDateIcon(task.due_date)" size="xs" />
                    <span>{{ formatDueDate(task.due_date) }}</span>
                </div>

                <!-- 任务状态 -->
                <q-chip
                    :color="getStatusColor(task.status)"
                    :icon="getStatusIcon(task.status)"
                    text-color="white"
                    size="sm"
                    dense
                >
                    {{ getStatusLabel(task.status) }}
                </q-chip>

                <!-- 负责人 -->
                <div class="task-assignee">
                    <q-avatar size="24px" color="primary" text-color="white">
                        {{ task.owner ? task.owner.toString().charAt(0).toUpperCase() : 'U' }}
                    </q-avatar>
                </div>
            </div>

            <!-- 时间戳 -->
            <div class="task-timestamps">
                <span class="timestamp" :title="formatDateTime(task.created_at)">
                    创建于 {{ formatRelativeTime(task.created_at) }}
                </span>
                <span
                    v-if="task.updated_at !== task.created_at"
                    class="timestamp"
                    :title="formatDateTime(task.updated_at)"
                >
                    • 更新于 {{ formatRelativeTime(task.updated_at) }}
                </span>
            </div>
        </div>

        <!-- 任务快速操作 -->
        <div
            v-if="getPrimaryAction(task.status) || getSecondaryActions(task.status).length > 0"
            class="task-quick-actions"
            :class="{ loading: statusLoading }"
        >
            <div class="status-flow-buttons">
                <!-- 主要操作按钮 -->
                <q-btn
                    v-if="getPrimaryAction(task.status)"
                    :color="getPrimaryAction(task.status)?.color"
                    :icon="getPrimaryAction(task.status)?.icon"
                    :label="getPrimaryAction(task.status)?.label"
                    :loading="statusLoading"
                    class="primary-action-btn"
                    unelevated
                    no-caps
                    @click="handlePrimaryAction"
                >
                    <q-tooltip>{{ getPrimaryAction(task.status)?.tooltip }}</q-tooltip>
                </q-btn>

                <!-- 次要操作按钮 -->
                <div class="secondary-actions">
                    <q-btn
                        v-for="action in getSecondaryActions(task.status)"
                        :key="action.status"
                        :icon="action.icon"
                        :color="action.color"
                        flat
                        round
                        size="sm"
                        class="secondary-action-btn"
                        @click="handleStatusChange(action.status)"
                    >
                        <q-tooltip>{{ action.tooltip }}</q-tooltip>
                    </q-btn>
                </div>
            </div>

            <!-- 状态进度指示器 -->
            <div class="status-flow-indicator">
                <div
                    class="status-progress"
                    :class="`bg-${getStatusColor(task.status)}`"
                    :style="{ width: `${getStatusProgress(task.status) * 100}%` }"
                ></div>
            </div>
        </div>
    </q-card>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { Task, TaskStatus, TaskPriority } from '../../types';
import { useGlobalConfirm } from '../../composables/useGlobalConfirm';

interface Props {
    task: Task;
    selected?: boolean;
}

interface Emits {
    (e: 'toggle-selection', taskId: string): void;
    (e: 'edit', task: Task): void;
    (e: 'delete', task: Task): void;
    (e: 'duplicate', task: Task): void;
    (e: 'view', task: Task): void;
    (e: 'status-change', taskId: string, status: TaskStatus): void;
}

const props = defineProps<Props>();

const emit = defineEmits<Emits>();

// 使用全局确认对话框
const confirmDialog = useGlobalConfirm();

// 状态管理
const statusLoading = ref(false);

// 状态流转配置
interface StatusAction {
    status: TaskStatus;
    label: string;
    icon: string;
    color: string;
    tooltip: string;
}

// 获取主要操作按钮
const getPrimaryAction = (status: TaskStatus): StatusAction | null => {
    const actions: Record<TaskStatus, StatusAction | null> = {
        PENDING: {
            status: 'IN_PROGRESS',
            label: '开始',
            icon: 'play_arrow',
            color: 'blue',
            tooltip: '开始处理这个任务',
        },
        IN_PROGRESS: {
            status: 'COMPLETED',
            label: '完成',
            icon: 'check',
            color: 'positive',
            tooltip: '标记任务为已完成',
        },
        COMPLETED: null,
        CANCELLED: {
            status: 'PENDING',
            label: '重新开始',
            icon: 'refresh',
            color: 'blue',
            tooltip: '重新激活这个任务',
        },
        ON_HOLD: {
            status: 'IN_PROGRESS',
            label: '继续',
            icon: 'play_arrow',
            color: 'blue',
            tooltip: '继续处理这个任务',
        },
    };
    return actions[status];
};

// 获取次要操作按钮
const getSecondaryActions = (status: TaskStatus): StatusAction[] => {
    const allActions: StatusAction[] = [
        {
            status: 'PENDING',
            label: '待处理',
            icon: 'schedule',
            color: 'grey',
            tooltip: '标记为待处理',
        },
        {
            status: 'IN_PROGRESS',
            label: '进行中',
            icon: 'play_circle',
            color: 'blue',
            tooltip: '标记为进行中',
        },
        {
            status: 'ON_HOLD',
            label: '暂停',
            icon: 'pause',
            color: 'orange',
            tooltip: '暂停这个任务',
        },
        {
            status: 'CANCELLED',
            label: '取消',
            icon: 'cancel',
            color: 'negative',
            tooltip: '取消这个任务',
        },
    ];

    // 根据当前状态过滤可用操作
    return allActions
        .filter(action => {
            if (action.status === status) return false;

            // 业务规则：已完成的任务只能取消或重新开始
            if (status === 'COMPLETED') {
                return action.status === 'CANCELLED';
            }

            // 已取消的任务不显示次要操作
            if (status === 'CANCELLED') {
                return false;
            }

            return true;
        })
        .slice(0, 2); // 最多显示2个次要操作
};

// 获取状态进度值
const getStatusProgress = (status: TaskStatus): number => {
    const progressMap: Record<TaskStatus, number> = {
        PENDING: 0,
        IN_PROGRESS: 0.5,
        ON_HOLD: 0.3,
        COMPLETED: 1,
        CANCELLED: 0,
    };
    return progressMap[status];
};

// 处理主要操作
const handlePrimaryAction = async () => {
    const action = getPrimaryAction(props.task.status);
    if (action) {
        await handleStatusChange(action.status);
    }
};

// 处理状态变更
const handleStatusChange = async (newStatus: TaskStatus) => {
    statusLoading.value = true;
    try {
        emit('status-change', props.task.id, newStatus);
        // 模拟API调用延迟
        await new Promise(resolve => setTimeout(resolve, 300));
    } finally {
        statusLoading.value = false;
    }
};

// 处理删除任务
const handleDeleteTask = async () => {
    try {
        const confirmed = await confirmDialog.confirmDanger(
            '删除任务',
            `确定要删除任务"${props.task.title}"吗？`,
            {
                details: '任务删除后将移至回收站，可在30天内恢复。',
                warningText: '删除后的任务可以在回收站中找到',
                confirmText: '删除',
                confirmIcon: 'delete',
            },
        );

        if (confirmed) {
            emit('delete', props.task);
        }
    } catch (error) {
        console.error('删除任务失败:', error);
    }
};

// 辅助方法
const getTaskTags = (tagsString: string): string[] => {
    if (!tagsString || typeof tagsString !== 'string') return [];
    return tagsString
        .split(',')
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0);
};

const getStatusColor = (status: TaskStatus): string => {
    const colors = {
        PENDING: 'orange',
        IN_PROGRESS: 'blue',
        COMPLETED: 'green',
        CANCELLED: 'grey',
        ON_HOLD: 'purple',
    };
    return colors[status];
};

const getStatusLabel = (status: TaskStatus): string => {
    const labels = {
        PENDING: '待处理',
        IN_PROGRESS: '进行中',
        COMPLETED: '已完成',
        CANCELLED: '已取消',
        ON_HOLD: '暂停',
    };
    return labels[status];
};

const getStatusIcon = (status: TaskStatus): string => {
    const icons = {
        PENDING: 'schedule',
        IN_PROGRESS: 'play_arrow',
        COMPLETED: 'check_circle',
        CANCELLED: 'cancel',
        ON_HOLD: 'pause',
    };
    return icons[status];
};

const getPriorityColor = (priority: TaskPriority): string => {
    const colors = {
        LOW: 'green',
        MEDIUM: 'orange',
        HIGH: 'red',
        URGENT: 'purple',
    };
    return colors[priority];
};

const getPriorityLabel = (priority: TaskPriority): string => {
    const labels = {
        LOW: '低',
        MEDIUM: '中',
        HIGH: '高',
        URGENT: '紧急',
    };
    return labels[priority];
};

const getPriorityIcon = (priority: TaskPriority): string => {
    const icons = {
        LOW: 'arrow_downward',
        MEDIUM: 'remove',
        HIGH: 'arrow_upward',
        URGENT: 'priority_high',
    };
    return icons[priority];
};

const getDueDateClass = (dueDate: string): string => {
    const now = new Date();
    const due = new Date(dueDate);
    const diffDays = Math.ceil((due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays < 0) return 'overdue';
    if (diffDays <= 1) return 'due-soon';
    if (diffDays <= 3) return 'due-warning';
    return 'due-normal';
};

const getDueDateIcon = (dueDate: string): string => {
    const now = new Date();
    const due = new Date(dueDate);
    const diffDays = Math.ceil((due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays < 0) return 'schedule';
    if (diffDays <= 1) return 'schedule';
    return 'schedule';
};

const formatDueDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffDays = Math.ceil((date.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return '今天';
    if (diffDays === 1) return '明天';
    if (diffDays === -1) return '昨天';
    if (diffDays < 0) return `逾期 ${Math.abs(diffDays)} 天`;
    if (diffDays <= 7) return `${diffDays} 天后`;

    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
};

const formatDateTime = (dateStr: string): string => {
    return new Date(dateStr).toLocaleString('zh-CN');
};

const formatRelativeTime = (dateStr: string): string => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMinutes < 1) return '刚刚';
    if (diffMinutes < 60) return `${diffMinutes} 分钟前`;
    if (diffHours < 24) return `${diffHours} 小时前`;
    if (diffDays < 30) return `${diffDays} 天前`;

    return date.toLocaleDateString('zh-CN');
};
</script>

<style scoped lang="scss">
.task-card {
    transition: all 0.2s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;

    // 优先级顶部边框指示器
    &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        z-index: 1;
        transition: all 0.3s ease;
    }

    &.priority-low::before {
        background: linear-gradient(90deg, #4caf50, #66bb6a);
    }

    &.priority-medium::before {
        background: linear-gradient(90deg, #2196f3, #42a5f5);
    }

    &.priority-high::before {
        background: linear-gradient(90deg, #ff9800, #ffb74d);
    }

    &.priority-urgent::before {
        background: linear-gradient(90deg, #f44336, #ef5350);
        height: 6px;
        box-shadow: 0 0 8px rgba(244, 67, 54, 0.4);
        animation: urgentPulse 2s infinite;
    }

    &:hover {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transform: translateY(-1px);

        &.priority-urgent {
            box-shadow: 0 4px 16px rgba(244, 67, 54, 0.2);
            border-color: rgba(244, 67, 54, 0.2);
        }

        &.priority-high {
            border-color: rgba(255, 152, 0, 0.2);
        }
    }

    &--selected {
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }

    &--completed {
        opacity: 0.8;

        .task-title {
            text-decoration: line-through;
            color: #6b7280;
        }
    }

    .task-header {
        padding: 0.75rem 1rem 0.5rem;

        .task-header-content {
            display: flex;
            align-items: center;
            gap: 0.5rem;

            .task-checkbox {
                flex-shrink: 0;
            }

            .task-priority {
                flex: 1;
            }

            .task-actions {
                flex-shrink: 0;
                margin-left: auto;
            }
        }
    }

    .task-content {
        padding: 0 1rem 0.75rem;

        .task-title {
            font-size: 1rem;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 0.5rem;
            line-height: 1.4;
            cursor: pointer;

            &:hover {
                color: #3b82f6;
            }
        }

        .task-description {
            color: #6b7280;
            font-size: 0.875rem;
            line-height: 1.5;
            margin-bottom: 0.75rem;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
            min-height: 4rem; /* 固定最小高度，确保统一显示 */
            height: 4rem; /* 固定高度，约等于3行文字的高度 */

            &--empty {
                background: transparent;
                /* 保持相同的高度但不显示任何内容 */
            }
        }

        .task-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.25rem;
            margin-bottom: 0.5rem;

            .task-tag {
                font-size: 0.75rem;
            }
        }
    }

    .task-footer {
        padding: 0.5rem 1rem 0.75rem;
        border-top: 1px solid #f3f4f6;

        .task-meta {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.5rem;

            .task-due-date {
                display: flex;
                align-items: center;
                gap: 0.25rem;
                font-size: 0.75rem;
                padding: 0.125rem 0.375rem;
                border-radius: 0.25rem;

                &.due-normal {
                    color: #6b7280;
                    background: #f3f4f6;
                }

                &.due-warning {
                    color: #d97706;
                    background: #fef3c7;
                }

                &.due-soon {
                    color: #dc2626;
                    background: #fee2e2;
                }

                &.overdue {
                    color: #ffffff;
                    background: #dc2626;
                }
            }

            .task-assignee {
                margin-left: auto;
            }
        }

        .task-timestamps {
            font-size: 0.75rem;
            color: #9ca3af;

            .timestamp {
                cursor: help;
            }
        }
    }

    .task-quick-actions {
        padding: 0.75rem 1rem;
        border-top: 1px solid rgba(0, 0, 0, 0.08);
        background: linear-gradient(to right, rgba(255, 255, 255, 0.95), rgba(248, 250, 252, 0.95));
        position: relative;

        .status-flow-buttons {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            width: 100%;

            .primary-action-btn {
                font-weight: 600;
                border-radius: 8px;
                padding: 0.5rem 1rem;
                transition: all 0.2s ease;
                text-transform: none;
                letter-spacing: 0.5px;

                &:hover {
                    transform: translateY(-1px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                }

                &.bg-primary {
                    background: linear-gradient(135deg, #1976d2, #42a5f5);

                    &:hover {
                        background: linear-gradient(135deg, #1565c0, #1e88e5);
                    }
                }

                &.bg-positive {
                    background: linear-gradient(135deg, #2e7d32, #66bb6a);

                    &:hover {
                        background: linear-gradient(135deg, #1b5e20, #4caf50);
                    }
                }

                &.bg-warning {
                    background: linear-gradient(135deg, #f57c00, #ffb74d);

                    &:hover {
                        background: linear-gradient(135deg, #ef6c00, #ff9800);
                    }
                }
            }

            .secondary-actions {
                display: flex;
                gap: 0.25rem;
                margin-left: auto;

                .secondary-action-btn {
                    border-radius: 50%;
                    width: 36px;
                    height: 36px;
                    min-width: 36px;
                    transition: all 0.2s ease;
                    border: 1px solid rgba(0, 0, 0, 0.08);

                    &:hover {
                        transform: scale(1.1);
                        background: rgba(0, 0, 0, 0.05);
                        border-color: rgba(0, 0, 0, 0.12);
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                    }

                    .q-icon {
                        font-size: 18px;
                    }
                }
            }
        }

        .status-flow-indicator {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: rgba(0, 0, 0, 0.05);

            .status-progress {
                height: 100%;
                transition: all 0.3s ease;
                border-radius: 0 0 12px 12px;

                &.bg-grey-4 {
                    background: linear-gradient(90deg, #e0e0e0, #f5f5f5);
                }

                &.bg-orange {
                    background: linear-gradient(90deg, #ff9800, #ffb74d);
                }

                &.bg-green {
                    background: linear-gradient(90deg, #4caf50, #66bb6a);
                }
            }
        }

        // 加载状态样式
        &.loading {
            .primary-action-btn {
                opacity: 0.7;
                cursor: not-allowed;

                &:hover {
                    transform: none;
                    box-shadow: none;
                }
            }

            .secondary-action-btn {
                opacity: 0.6;
                cursor: not-allowed;

                &:hover {
                    transform: none;
                    background: transparent;
                    box-shadow: none;
                }
            }
        }
    }

    .task-priority {
        .priority-readonly {
            cursor: default;

            &:hover {
                transform: none;
                box-shadow: none;
            }
        }
    }
}

// 响应式设计
@media (max-width: 640px) {
    .task-card {
        .task-header {
            .task-header-content {
                .task-priority {
                    display: none;
                }
            }
        }

        .task-footer {
            .task-meta {
                flex-wrap: wrap;
                gap: 0.5rem;

                .task-assignee {
                    margin-left: 0;
                }
            }
        }

        .task-quick-actions {
            .status-flow-buttons {
                flex-direction: column;
                gap: 0.5rem;

                .secondary-actions {
                    margin-left: 0;
                    justify-content: center;
                }
            }
        }
    }
}

// 紧急任务脉动动画
@keyframes urgentPulse {
    0%,
    100% {
        opacity: 1;
        box-shadow: 0 0 8px rgba(244, 67, 54, 0.4);
    }
    50% {
        opacity: 0.8;
        box-shadow: 0 0 16px rgba(244, 67, 54, 0.6);
    }
}
</style>

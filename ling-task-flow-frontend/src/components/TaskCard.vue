<template>
    <q-card
        class="task-card"
        :class="{
            'task-card--selected': selected,
            'task-card--completed': task.status === 'completed',
        }"
        flat
        bordered
    >
        <!-- 任务头部 -->
        <q-card-section class="task-header">
            <div class="task-header-content">
                <q-checkbox
                    :model-value="selected"
                    @update:model-value="$emit('toggle-selection', task.id)"
                    class="task-checkbox"
                />

                <div class="task-priority">
                    <q-chip
                        :color="getPriorityColor(task.priority)"
                        text-color="white"
                        size="sm"
                        :icon="getPriorityIcon(task.priority)"
                    >
                        {{ getPriorityLabel(task.priority) }}
                    </q-chip>
                </div>

                <div class="task-actions">
                    <q-btn flat dense round icon="more_vert" color="grey-6" size="sm">
                        <q-menu anchor="bottom right" self="top right">
                            <q-list dense>
                                <q-item clickable v-close-popup @click="$emit('edit', task)">
                                    <q-item-section avatar>
                                        <q-icon name="edit" size="xs" />
                                    </q-item-section>
                                    <q-item-section>编辑</q-item-section>
                                </q-item>

                                <q-item clickable v-close-popup @click="$emit('duplicate', task)">
                                    <q-item-section avatar>
                                        <q-icon name="content_copy" size="xs" />
                                    </q-item-section>
                                    <q-item-section>复制</q-item-section>
                                </q-item>

                                <q-separator />

                                <q-item clickable v-close-popup @click="$emit('delete', task)">
                                    <q-item-section avatar>
                                        <q-icon name="delete" size="xs" color="negative" />
                                    </q-item-section>
                                    <q-item-section class="text-negative">删除</q-item-section>
                                </q-item>
                            </q-list>
                        </q-menu>
                    </q-btn>
                </div>
            </div>
        </q-card-section>

        <!-- 任务内容 -->
        <q-card-section class="task-content">
            <div class="task-title" @click="$emit('view', task)">
                {{ task.title }}
            </div>

            <div v-if="task.description" class="task-description">
                {{ task.description }}
            </div>

            <!-- 任务标签 -->
            <div v-if="task.tags && task.tags.length > 0" class="task-tags">
                <q-chip
                    v-for="tag in task.tags"
                    :key="tag"
                    size="sm"
                    outline
                    color="blue-grey-6"
                    class="task-tag"
                >
                    {{ tag }}
                </q-chip>
            </div>
        </q-card-section>

        <!-- 任务底部信息 -->
        <q-card-section class="task-footer">
            <div class="task-meta">
                <!-- 状态 -->
                <q-chip
                    :color="getStatusColor(task.status)"
                    text-color="white"
                    size="sm"
                    :icon="getStatusIcon(task.status)"
                >
                    {{ getStatusLabel(task.status) }}
                </q-chip>

                <!-- 到期时间 -->
                <div
                    v-if="task.due_date"
                    class="task-due-date"
                    :class="getDueDateClass(task.due_date)"
                >
                    <q-icon :name="getDueDateIcon(task.due_date)" size="xs" />
                    <span>{{ formatDueDate(task.due_date) }}</span>
                </div>
            </div>

            <div class="task-timestamps">
                <span class="timestamp" :title="`创建时间: ${formatDateTime(task.created_at)}`">
                    {{ formatRelativeTime(task.created_at) }}
                </span>
                <span
                    v-if="task.updated_at !== task.created_at"
                    class="timestamp"
                    :title="`更新时间: ${formatDateTime(task.updated_at)}`"
                >
                    · {{ formatRelativeTime(task.updated_at) }}
                </span>
            </div>
        </q-card-section>

        <!-- 快速状态切换按钮 -->
        <q-card-actions v-if="task.status !== 'completed'" class="task-quick-actions">
            <q-btn
                flat
                dense
                :color="task.status === 'in_progress' ? 'orange' : 'blue'"
                :icon="task.status === 'in_progress' ? 'pause' : 'play_arrow'"
                :label="task.status === 'in_progress' ? '暂停' : '开始'"
                size="sm"
                @click="toggleStatus"
            />

            <q-btn
                flat
                dense
                color="positive"
                icon="check"
                label="完成"
                size="sm"
                @click="markCompleted"
            />
        </q-card-actions>
    </q-card>
</template>

<script setup lang="ts">
import type { Task, TaskStatus, TaskPriority } from '../types';

interface Props {
    task: Task;
    selected?: boolean;
}

interface Emits {
    (e: 'toggle-selection', taskId: number): void;
    (e: 'edit', task: Task): void;
    (e: 'delete', task: Task): void;
    (e: 'duplicate', task: Task): void;
    (e: 'view', task: Task): void;
    (e: 'status-change', taskId: number, status: TaskStatus): void;
}

const props = withDefaults(defineProps<Props>(), {
    selected: false,
});

const emit = defineEmits<Emits>();

// 辅助方法
const getStatusColor = (status: TaskStatus): string => {
    const colors = {
        pending: 'orange',
        in_progress: 'blue',
        completed: 'green',
        cancelled: 'grey',
    };
    return colors[status];
};

const getStatusLabel = (status: TaskStatus): string => {
    const labels = {
        pending: '待处理',
        in_progress: '进行中',
        completed: '已完成',
        cancelled: '已取消',
    };
    return labels[status];
};

const getStatusIcon = (status: TaskStatus): string => {
    const icons = {
        pending: 'schedule',
        in_progress: 'play_arrow',
        completed: 'check_circle',
        cancelled: 'cancel',
    };
    return icons[status];
};

const getPriorityColor = (priority: TaskPriority): string => {
    const colors = {
        low: 'green',
        medium: 'orange',
        high: 'red',
        urgent: 'purple',
    };
    return colors[priority];
};

const getPriorityLabel = (priority: TaskPriority): string => {
    const labels = {
        low: '低',
        medium: '中',
        high: '高',
        urgent: '紧急',
    };
    return labels[priority];
};

const getPriorityIcon = (priority: TaskPriority): string => {
    const icons = {
        low: 'arrow_downward',
        medium: 'remove',
        high: 'arrow_upward',
        urgent: 'priority_high',
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

// 方法
const toggleStatus = () => {
    const newStatus: TaskStatus = props.task.status === 'in_progress' ? 'pending' : 'in_progress';
    emit('status-change', props.task.id, newStatus);
};

const markCompleted = () => {
    emit('status-change', props.task.id, 'completed');
};
</script>

<style scoped lang="scss">
.task-card {
    transition: all 0.2s ease;
    cursor: pointer;

    &:hover {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transform: translateY(-1px);
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
        padding: 0.5rem 1rem;
        border-top: 1px solid #f3f4f6;
        background: #fafafa;
        display: flex;
        gap: 0.5rem;
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
            flex-direction: column;
            gap: 0.25rem;
        }
    }
}
</style>

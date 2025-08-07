<template>
    <div
        class="cyber-task-card draggable-item"
        :class="{
            selected: isSelected,
            dragging: isDragging,
        }"
        :data-task-id="task.id"
    >
        <!-- 卡片边框和装饰 -->
        <div class="card-frame">
            <div class="frame-corner top-left"></div>
            <div class="frame-corner top-right"></div>
            <div class="frame-corner bottom-left"></div>
            <div class="frame-corner bottom-right"></div>
            <div class="frame-scan"></div>
        </div>

        <!-- 拖拽手柄 -->
        <div class="drag-handle">
            <div class="handle-lines">
                <div class="line"></div>
                <div class="line"></div>
                <div class="line"></div>
                <div class="line"></div>
            </div>
        </div>

        <!-- 卡片头部 -->
        <div class="card-header">
            <div class="header-left">
                <q-checkbox
                    :model-value="isSelected"
                    @update:model-value="handleSelectionChange"
                    class="task-checkbox"
                />
                <div class="task-id">ID_{{ task.id.slice(-6).toUpperCase() }}</div>
            </div>
            <div class="header-right">
                <div class="priority-indicator" :class="`priority-${task.priority.toLowerCase()}`">
                    <div class="priority-dots">
                        <div
                            class="dot"
                            v-for="i in getPriorityLevel(task.priority)"
                            :key="i"
                        ></div>
                    </div>
                    <span class="priority-text">{{ task.priority }}</span>
                </div>
                <div
                    class="status-indicator"
                    :class="`status-${task.status.toLowerCase().replace('_', '-')}`"
                >
                    <q-icon :name="getStatusIcon(task.status)" size="16px" />
                    <span class="status-text">{{ getStatusLabel(task.status) }}</span>
                </div>
            </div>
        </div>

        <!-- 卡片内容 -->
        <div class="card-content">
            <div class="task-title">{{ task.title }}</div>
            <div class="task-description" v-if="task.description">
                {{ task.description.slice(0, 100) }}{{ task.description.length > 100 ? '...' : '' }}
            </div>
            <div class="task-tags" v-if="task.tags && task.tags.length > 0">
                <div class="tag" v-for="tag in task.tags.slice(0, 3)" :key="tag">#{{ tag }}</div>
                <div class="tag-more" v-if="task.tags.length > 3">+{{ task.tags.length - 3 }}</div>
            </div>
        </div>

        <!-- 卡片底部 -->
        <div class="card-footer">
            <div class="footer-left">
                <div class="created-date">
                    <q-icon name="schedule" size="14px" />
                    <span>{{ formatDate(task.created_at) }}</span>
                </div>
                <div class="due-date" v-if="task.due_date">
                    <q-icon name="event" size="14px" />
                    <span :class="{ overdue: isOverdue(task.due_date) }">
                        {{ formatDate(task.due_date) }}
                    </span>
                </div>
            </div>
            <div class="footer-right">
                <div class="action-buttons">
                    <q-btn
                        flat
                        dense
                        round
                        icon="visibility"
                        size="sm"
                        class="action-btn"
                        @click="$emit('view', task)"
                    >
                        <q-tooltip>查看详情</q-tooltip>
                    </q-btn>
                    <q-btn
                        flat
                        dense
                        round
                        icon="edit"
                        size="sm"
                        class="action-btn"
                        @click="$emit('edit', task)"
                    >
                        <q-tooltip>编辑任务</q-tooltip>
                    </q-btn>
                    <q-btn
                        flat
                        dense
                        round
                        icon="delete"
                        size="sm"
                        class="action-btn danger"
                        @click="$emit('delete', task)"
                    >
                        <q-tooltip>删除任务</q-tooltip>
                    </q-btn>
                </div>
            </div>
        </div>

        <!-- 选中状态覆盖层 -->
        <div v-if="isSelected" class="selection-overlay">
            <div class="selection-pulse"></div>
            <div class="selection-checkmark">
                <q-icon name="check_circle" size="24px" />
            </div>
        </div>

        <!-- 拖拽占位符 -->
        <div class="drag-placeholder" :class="{ active: showDragPlaceholder }">
            <div class="placeholder-content">
                <q-icon name="swap_vert" size="20px" />
                <span>DROP_HERE</span>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { Task, TaskStatus, TaskPriority } from '../../types';

interface Props {
    task: Task;
    isSelected?: boolean;
    isDragging?: boolean;
    showDragPlaceholder?: boolean;
    viewMode?: 'list' | 'grid';
}

interface Emits {
    (e: 'view', task: Task): void;
    (e: 'edit', task: Task): void;
    (e: 'delete', task: Task): void;
    (e: 'selection-change', taskId: string, selected: boolean): void;
}

const props = withDefaults(defineProps<Props>(), {
    isSelected: false,
    isDragging: false,
    showDragPlaceholder: false,
    viewMode: 'list',
});

const emit = defineEmits<Emits>();

// 工具函数
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

const getPriorityLevel = (priority: TaskPriority): number => {
    const levels: Record<TaskPriority, number> = {
        LOW: 1,
        MEDIUM: 2,
        HIGH: 3,
        URGENT: 4,
    };
    return levels[priority] || 2;
};

const formatDate = (dateString: string): string => {
    if (!dateString) return '';
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
        });
    } catch {
        return dateString;
    }
};

const isOverdue = (dueDateString: string): boolean => {
    if (!dueDateString) return false;
    try {
        const dueDate = new Date(dueDateString);
        const now = new Date();
        return dueDate < now;
    } catch {
        return false;
    }
};

const handleSelectionChange = (selected: boolean) => {
    emit('selection-change', props.task.id, selected);
};
</script>

<style scoped lang="scss">
.cyber-task-card {
    background: white;
    border: 1px solid rgba(59, 130, 246, 0.15);
    border-radius: 8px;
    margin-bottom: 1rem;
    position: relative;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    overflow: hidden;
    box-shadow:
        0 4px 12px rgba(59, 130, 246, 0.05),
        0 1px 3px rgba(0, 0, 0, 0.05);

    &:hover {
        transform: translateY(-2px);
        border-color: rgba(59, 130, 246, 0.3);
        box-shadow:
            0 8px 25px rgba(59, 130, 246, 0.1),
            0 4px 12px rgba(0, 0, 0, 0.08);
    }

    &.selected {
        border-color: #3b82f6;
        box-shadow:
            0 8px 25px rgba(59, 130, 246, 0.15),
            0 4px 12px rgba(0, 0, 0, 0.1);
    }

    &.dragging {
        opacity: 0.8;
        transform: rotate(2deg) scale(1.02);
        z-index: 1000;
        box-shadow: 0 12px 30px rgba(59, 130, 246, 0.3);
    }

    .card-frame {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        pointer-events: none;

        .frame-corner {
            position: absolute;
            width: 12px;
            height: 12px;

            &.top-left {
                top: 0;
                left: 0;
                border-top: 2px solid rgba(59, 130, 246, 0.3);
                border-left: 2px solid rgba(59, 130, 246, 0.3);
            }

            &.top-right {
                top: 0;
                right: 0;
                border-top: 2px solid rgba(59, 130, 246, 0.3);
                border-right: 2px solid rgba(59, 130, 246, 0.3);
            }

            &.bottom-left {
                bottom: 0;
                left: 0;
                border-bottom: 2px solid rgba(59, 130, 246, 0.3);
                border-left: 2px solid rgba(59, 130, 246, 0.3);
            }

            &.bottom-right {
                bottom: 0;
                right: 0;
                border-bottom: 2px solid rgba(59, 130, 246, 0.3);
                border-right: 2px solid rgba(59, 130, 246, 0.3);
            }
        }

        .frame-scan {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(
                90deg,
                transparent 0%,
                rgba(59, 130, 246, 0.6) 50%,
                transparent 100%
            );
            animation: scanFrame 3s ease-in-out infinite;
            opacity: 0;
        }
    }

    &:hover .card-frame .frame-scan {
        opacity: 1;
    }

    .drag-handle {
        position: absolute;
        left: 0.5rem;
        top: 50%;
        transform: translateY(-50%);
        width: 8px;
        height: 24px;
        cursor: grab;
        z-index: 10;

        &:active {
            cursor: grabbing;
        }

        .handle-lines {
            display: flex;
            flex-direction: column;
            gap: 2px;
            height: 100%;
            justify-content: center;

            .line {
                width: 6px;
                height: 1px;
                background: rgba(59, 130, 246, 0.4);
                border-radius: 1px;
                transition: all 0.3s ease;
            }
        }

        &:hover .handle-lines .line {
            background: #3b82f6;
            box-shadow: 0 0 4px rgba(59, 130, 246, 0.6);
        }
    }

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 1rem 0.5rem 2rem;
        border-bottom: 1px solid rgba(59, 130, 246, 0.1);

        .header-left {
            display: flex;
            align-items: center;
            gap: 0.75rem;

            .task-id {
                font-family: 'Courier New', monospace;
                font-size: 0.75rem;
                color: #64748b;
                letter-spacing: 1px;
                background: rgba(59, 130, 246, 0.1);
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                border: 1px solid rgba(59, 130, 246, 0.2);
            }
        }

        .header-right {
            display: flex;
            align-items: center;
            gap: 0.75rem;

            .priority-indicator {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-size: 0.75rem;
                font-weight: 600;

                .priority-dots {
                    display: flex;
                    gap: 2px;

                    .dot {
                        width: 4px;
                        height: 4px;
                        border-radius: 50%;
                        background: currentColor;
                    }
                }

                &.priority-low {
                    color: #10b981;
                    background: rgba(16, 185, 129, 0.1);
                    border: 1px solid rgba(16, 185, 129, 0.2);
                }

                &.priority-medium {
                    color: #3b82f6;
                    background: rgba(59, 130, 246, 0.1);
                    border: 1px solid rgba(59, 130, 246, 0.2);
                }

                &.priority-high {
                    color: #f59e0b;
                    background: rgba(245, 158, 11, 0.1);
                    border: 1px solid rgba(245, 158, 11, 0.2);
                }

                &.priority-urgent {
                    color: #ef4444;
                    background: rgba(239, 68, 68, 0.1);
                    border: 1px solid rgba(239, 68, 68, 0.2);
                }
            }

            .status-indicator {
                display: flex;
                align-items: center;
                gap: 0.25rem;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-size: 0.75rem;
                font-weight: 600;

                &.status-pending {
                    color: #f59e0b;
                    background: rgba(245, 158, 11, 0.1);
                    border: 1px solid rgba(245, 158, 11, 0.2);
                }

                &.status-in-progress {
                    color: #3b82f6;
                    background: rgba(59, 130, 246, 0.1);
                    border: 1px solid rgba(59, 130, 246, 0.2);
                }

                &.status-completed {
                    color: #10b981;
                    background: rgba(16, 185, 129, 0.1);
                    border: 1px solid rgba(16, 185, 129, 0.2);
                }

                &.status-cancelled {
                    color: #ef4444;
                    background: rgba(239, 68, 68, 0.1);
                    border: 1px solid rgba(239, 68, 68, 0.2);
                }

                &.status-on-hold {
                    color: #6b7280;
                    background: rgba(107, 114, 128, 0.1);
                    border: 1px solid rgba(107, 114, 128, 0.2);
                }
            }
        }
    }

    .card-content {
        padding: 1rem 1rem 0.5rem 2rem;

        .task-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #64748b;
            margin-bottom: 0.5rem;
            line-height: 1.4;
        }

        .task-description {
            color: #94a3b8;
            font-size: 0.875rem;
            line-height: 1.5;
            margin-bottom: 0.75rem;
        }

        .task-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;

            .tag {
                background: rgba(59, 130, 246, 0.1);
                color: #3b82f6;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-size: 0.75rem;
                border: 1px solid rgba(59, 130, 246, 0.2);
                font-family: 'Courier New', monospace;
            }

            .tag-more {
                background: rgba(107, 114, 128, 0.1);
                color: #6b7280;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-size: 0.75rem;
                border: 1px solid rgba(107, 114, 128, 0.2);
            }
        }
    }

    .card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 1rem 1rem 2rem;

        .footer-left {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;

            .created-date,
            .due-date {
                display: flex;
                align-items: center;
                gap: 0.25rem;
                font-size: 0.75rem;
                color: #6b7280;

                .overdue {
                    color: #ef4444;
                }
            }
        }

        .footer-right {
            .action-buttons {
                display: flex;
                gap: 0.25rem;

                .action-btn {
                    background: rgba(59, 130, 246, 0.1);
                    color: #3b82f6;
                    border: 1px solid rgba(59, 130, 246, 0.2);
                    transition: all 0.3s ease;

                    &:hover {
                        background: rgba(59, 130, 246, 0.2);
                        box-shadow: 0 0 8px rgba(59, 130, 246, 0.3);
                    }

                    &.danger {
                        background: rgba(239, 68, 68, 0.1);
                        color: #ef4444;
                        border-color: rgba(239, 68, 68, 0.2);

                        &:hover {
                            background: rgba(239, 68, 68, 0.2);
                            box-shadow: 0 0 8px rgba(239, 68, 68, 0.3);
                        }
                    }
                }
            }
        }
    }

    .selection-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(59, 130, 246, 0.05);
        border-radius: 8px;
        pointer-events: none;

        .selection-pulse {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border: 2px solid rgba(59, 130, 246, 0.3);
            border-radius: 8px;
            animation: selectionPulse 2s ease-in-out infinite;
        }

        .selection-checkmark {
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            background: #3b82f6;
            border-radius: 50%;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            box-shadow: 0 0 12px rgba(59, 130, 246, 0.6);
        }
    }

    .drag-placeholder {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(59, 130, 246, 0.1);
        border: 2px dashed #3b82f6;
        border-radius: 8px;
        display: none;
        align-items: center;
        justify-content: center;

        &.active {
            display: flex;
        }

        .placeholder-content {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.5rem;
            color: #3b82f6;
            font-family: 'Courier New', monospace;
            font-weight: 600;
            letter-spacing: 1px;
        }
    }
}

// 动画
@keyframes scanFrame {
    0% {
        left: 0;
        opacity: 0;
    }
    50% {
        opacity: 1;
    }
    100% {
        left: 100%;
        opacity: 0;
    }
}

@keyframes selectionPulse {
    0%,
    100% {
        opacity: 0.5;
        transform: scale(1);
    }
    50% {
        opacity: 1;
        transform: scale(1.02);
    }
}

// 响应式设计
@media (max-width: 768px) {
    .cyber-task-card {
        margin-bottom: 0.75rem;

        .card-header {
            padding: 0.75rem 0.75rem 0.5rem 1.5rem;

            .header-left,
            .header-right {
                gap: 0.5rem;
            }

            .task-id {
                font-size: 0.7rem;
                padding: 0.2rem 0.4rem;
            }

            .priority-indicator,
            .status-indicator {
                font-size: 0.7rem;
                padding: 0.2rem 0.4rem;
            }
        }

        .card-content {
            padding: 0.75rem 0.75rem 0.5rem 1.5rem;

            .task-title {
                font-size: 1rem;
            }

            .task-description {
                font-size: 0.8rem;
            }
        }

        .card-footer {
            padding: 0.5rem 0.75rem 0.75rem 1.5rem;

            .footer-left {
                .created-date,
                .due-date {
                    font-size: 0.7rem;
                }
            }

            .footer-right {
                .action-buttons {
                    gap: 0.2rem;

                    .action-btn {
                        min-width: 28px;
                        min-height: 28px;
                    }
                }
            }
        }
    }
}
</style>

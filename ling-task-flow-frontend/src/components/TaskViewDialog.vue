<template>
    <q-dialog v-model="isOpen" :maximized="false" position="standard">
        <q-card class="task-view-dialog" style="width: 900px; max-width: 90vw; max-height: 80vh">
            <!-- 对话框头部 -->
            <q-card-section class="dialog-header">
                <div class="header-content">
                    <div class="task-info">
                        <div class="task-title-container">
                            <q-icon name="visibility" size="32px" class="title-icon" />
                            <div class="title-info">
                                <h4 class="task-title">{{ task?.title || '任务详情' }}</h4>
                            </div>
                        </div>

                        <!-- 状态和优先级标识 -->
                        <div class="status-badges">
                            <q-chip
                                v-if="task"
                                :color="getStatusColor(task.status)"
                                :icon="getStatusIcon(task.status)"
                                text-color="white"
                                size="md"
                                class="status-chip"
                            >
                                {{ getStatusLabel(task.status) }}
                            </q-chip>

                            <q-chip
                                v-if="task"
                                :color="getPriorityColor(task.priority)"
                                :icon="getPriorityIcon(task.priority)"
                                text-color="white"
                                size="md"
                                class="priority-chip"
                            >
                                {{ getPriorityLabel(task.priority) }}
                            </q-chip>
                        </div>
                    </div>

                    <!-- 操作按钮 -->
                    <div class="header-actions">
                        <q-btn
                            flat
                            round
                            icon="edit"
                            size="md"
                            color="primary"
                            @click="openEditDialog"
                            class="action-btn"
                        >
                            <q-tooltip>编辑任务</q-tooltip>
                        </q-btn>

                        <q-btn
                            flat
                            round
                            icon="content_copy"
                            size="md"
                            color="grey-7"
                            @click="duplicateTask"
                            class="action-btn"
                        >
                            <q-tooltip>复制任务</q-tooltip>
                        </q-btn>

                        <q-btn
                            flat
                            round
                            icon="delete"
                            size="md"
                            color="negative"
                            @click="deleteTask"
                            class="action-btn"
                        >
                            <q-tooltip>删除任务</q-tooltip>
                        </q-btn>

                        <q-separator vertical />

                        <q-btn
                            flat
                            round
                            icon="close"
                            size="md"
                            @click="closeDialog"
                            class="close-btn"
                        >
                            <q-tooltip>关闭</q-tooltip>
                        </q-btn>
                    </div>
                </div>
            </q-card-section>

            <q-separator />

            <!-- 对话框内容 -->
            <q-card-section class="dialog-content">
                <div class="content-layout" v-if="task">
                    <!-- 左侧主要内容 -->
                    <div class="main-content">
                        <!-- 任务描述 -->
                        <section class="content-section">
                            <h5 class="section-title">
                                <q-icon name="description" size="20px" />
                                任务描述
                            </h5>
                            <div class="section-content">
                                <div
                                    v-if="task.description && task.description.trim()"
                                    class="task-description"
                                >
                                    {{ task.description }}
                                </div>
                                <div v-else class="empty-description">
                                    <q-icon name="info" size="16px" />
                                    暂无任务描述
                                </div>
                            </div>
                        </section>

                        <!-- 任务标签 -->
                        <section class="content-section">
                            <h5 class="section-title">
                                <q-icon name="local_offer" size="20px" />
                                标签
                            </h5>
                            <div class="section-content">
                                <div
                                    v-if="getTaskTags(task.tags).length > 0"
                                    class="tags-container"
                                >
                                    <q-chip
                                        v-for="tag in getTaskTags(task.tags)"
                                        :key="tag"
                                        color="grey-3"
                                        text-color="grey-8"
                                        size="sm"
                                        class="task-tag"
                                    >
                                        {{ tag }}
                                    </q-chip>
                                </div>
                                <div v-else class="empty-tags">
                                    <q-icon name="info" size="16px" />
                                    暂无标签
                                </div>
                            </div>
                        </section>

                        <!-- 时间信息 -->
                        <section class="content-section">
                            <h5 class="section-title">
                                <q-icon name="schedule" size="20px" />
                                时间信息
                            </h5>
                            <div class="section-content">
                                <div class="time-info">
                                    <div class="time-item">
                                        <q-icon name="add" size="16px" color="green" />
                                        <span class="time-label">创建时间：</span>
                                        <span class="time-value">{{
                                            formatDateTime(task.created_at)
                                        }}</span>
                                    </div>

                                    <div class="time-item">
                                        <q-icon name="update" size="16px" color="blue" />
                                        <span class="time-label">更新时间：</span>
                                        <span class="time-value">{{
                                            formatDateTime(task.updated_at)
                                        }}</span>
                                    </div>

                                    <div v-if="task.due_date" class="time-item">
                                        <q-icon
                                            name="event"
                                            size="16px"
                                            :color="getDueDateColor(task.due_date)"
                                        />
                                        <span class="time-label">截止时间：</span>
                                        <span
                                            class="time-value"
                                            :class="getDueDateClass(task.due_date)"
                                        >
                                            {{ formatDateTime(task.due_date) }}
                                            <span class="due-status">{{
                                                getDueDateStatus(task.due_date)
                                            }}</span>
                                        </span>
                                    </div>

                                    <div v-else class="time-item">
                                        <q-icon name="event_busy" size="16px" color="grey" />
                                        <span class="time-label">截止时间：</span>
                                        <span class="time-value text-grey">未设置</span>
                                    </div>
                                </div>
                            </div>
                        </section>
                    </div>

                    <!-- 右侧信息面板 -->
                    <div class="side-panel">
                        <!-- 基本信息 -->
                        <section class="panel-section">
                            <h6 class="panel-title">基本信息</h6>
                            <div class="info-grid">
                                <div class="info-item">
                                    <span class="info-label">状态：</span>
                                    <q-chip
                                        :color="getStatusColor(task.status)"
                                        :icon="getStatusIcon(task.status)"
                                        text-color="white"
                                        size="sm"
                                        dense
                                    >
                                        {{ getStatusLabel(task.status) }}
                                    </q-chip>
                                </div>

                                <div class="info-item">
                                    <span class="info-label">优先级：</span>
                                    <q-chip
                                        :color="getPriorityColor(task.priority)"
                                        :icon="getPriorityIcon(task.priority)"
                                        text-color="white"
                                        size="sm"
                                        dense
                                    >
                                        {{ getPriorityLabel(task.priority) }}
                                    </q-chip>
                                </div>

                                <div class="info-item">
                                    <span class="info-label">负责人：</span>
                                    <div class="assignee-info">
                                        <q-avatar size="24px" color="primary" text-color="white">
                                            {{
                                                task.owner_username
                                                    ? task.owner_username.charAt(0).toUpperCase()
                                                    : 'U'
                                            }}
                                        </q-avatar>
                                        <span class="assignee-name">{{
                                            task.owner_username || '未分配'
                                        }}</span>
                                    </div>
                                </div>
                            </div>
                        </section>

                        <!-- 快速操作 -->
                        <!-- 快速操作功能已移除，提供更简洁的查看体验 -->

                        <!-- 统计信息 -->
                        <section class="panel-section">
                            <h6 class="panel-title">统计信息</h6>
                            <div class="stats-grid">
                                <div class="stat-item">
                                    <q-icon name="visibility" size="16px" color="grey-6" />
                                    <span class="stat-value">{{
                                        formatRelativeTime(task.created_at)
                                    }}</span>
                                    <span class="stat-label">创建于</span>
                                </div>

                                <div class="stat-item">
                                    <q-icon name="update" size="16px" color="grey-6" />
                                    <span class="stat-value">{{
                                        formatRelativeTime(task.updated_at)
                                    }}</span>
                                    <span class="stat-label">最后更新</span>
                                </div>

                                <div v-if="task.due_date" class="stat-item">
                                    <q-icon
                                        name="timer"
                                        size="16px"
                                        :color="getDueDateColor(task.due_date)"
                                    />
                                    <span
                                        class="stat-value"
                                        :class="getDueDateClass(task.due_date)"
                                    >
                                        {{ getTimeRemaining(task.due_date) }}
                                    </span>
                                    <span class="stat-label">剩余时间</span>
                                </div>
                            </div>
                        </section>
                    </div>
                </div>

                <!-- 加载状态 -->
                <div v-else class="loading-container">
                    <q-spinner size="40px" color="primary" />
                    <p>加载任务详情...</p>
                </div>
            </q-card-section>
        </q-card>
    </q-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useQuasar } from 'quasar';
import type { Task, TaskStatus, TaskPriority } from '../types';

interface Props {
    modelValue: boolean;
    task?: Task | null;
}

interface Emits {
    (e: 'update:modelValue', value: boolean): void;
    (e: 'edit', task: Task): void;
    (e: 'duplicate', task: Task): void;
    (e: 'delete', task: Task): void;
}

const props = withDefaults(defineProps<Props>(), {
    task: null,
});

const emit = defineEmits<Emits>();
const $q = useQuasar();

// 计算属性
const isOpen = computed({
    get: () => props.modelValue,
    set: (value: boolean) => emit('update:modelValue', value),
});

// 对话框操作
const closeDialog = () => {
    isOpen.value = false;
};

const openEditDialog = () => {
    if (props.task) {
        emit('edit', props.task);
        closeDialog();
    }
};

const duplicateTask = () => {
    if (props.task) {
        emit('duplicate', props.task);
        closeDialog();
    }
};

const deleteTask = () => {
    if (props.task) {
        $q.dialog({
            title: '确认删除',
            message: `确定要删除任务"${props.task.title}"吗？删除后可以在回收站中恢复。`,
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
            if (props.task) {
                emit('delete', props.task);
                closeDialog();
            }
        });
    }
};

// 工具函数
const getTaskTags = (tagsString: string): string[] => {
    if (!tagsString || typeof tagsString !== 'string') return [];
    return tagsString
        .split(',')
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0);
};

const getStatusColor = (status: TaskStatus): string => {
    const colors: Record<TaskStatus, string> = {
        PENDING: 'orange',
        IN_PROGRESS: 'blue',
        COMPLETED: 'positive',
        CANCELLED: 'negative',
        ON_HOLD: 'purple',
    };
    return colors[status];
};

const getStatusLabel = (status: TaskStatus): string => {
    const labels: Record<TaskStatus, string> = {
        PENDING: '待处理',
        IN_PROGRESS: '进行中',
        COMPLETED: '已完成',
        CANCELLED: '已取消',
        ON_HOLD: '暂停',
    };
    return labels[status];
};

const getStatusIcon = (status: TaskStatus): string => {
    const icons: Record<TaskStatus, string> = {
        PENDING: 'schedule',
        IN_PROGRESS: 'play_arrow',
        COMPLETED: 'check_circle',
        CANCELLED: 'cancel',
        ON_HOLD: 'pause',
    };
    return icons[status];
};

const getPriorityColor = (priority: TaskPriority): string => {
    const colors: Record<TaskPriority, string> = {
        LOW: 'green',
        MEDIUM: 'blue',
        HIGH: 'orange',
        URGENT: 'red',
    };
    return colors[priority];
};

const getPriorityLabel = (priority: TaskPriority): string => {
    const labels: Record<TaskPriority, string> = {
        LOW: '低优先级',
        MEDIUM: '中优先级',
        HIGH: '高优先级',
        URGENT: '紧急',
    };
    return labels[priority];
};

const getPriorityIcon = (priority: TaskPriority): string => {
    const icons: Record<TaskPriority, string> = {
        LOW: 'arrow_downward',
        MEDIUM: 'remove',
        HIGH: 'arrow_upward',
        URGENT: 'priority_high',
    };
    return icons[priority];
};

const formatDateTime = (dateStr: string): string => {
    return new Date(dateStr).toLocaleString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
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

const getDueDateColor = (dueDate: string): string => {
    const now = new Date();
    const due = new Date(dueDate);
    const diffDays = Math.ceil((due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays < 0) return 'negative';
    if (diffDays <= 1) return 'warning';
    if (diffDays <= 3) return 'orange';
    return 'grey-6';
};

const getDueDateClass = (dueDate: string): string => {
    const now = new Date();
    const due = new Date(dueDate);
    const diffDays = Math.ceil((due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays < 0) return 'text-negative';
    if (diffDays <= 1) return 'text-warning';
    if (diffDays <= 3) return 'text-orange';
    return '';
};

const getDueDateStatus = (dueDate: string): string => {
    const now = new Date();
    const due = new Date(dueDate);
    const diffDays = Math.ceil((due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays < 0) return '(已逾期)';
    if (diffDays === 0) return '(今天到期)';
    if (diffDays === 1) return '(明天到期)';
    if (diffDays <= 7) return `(${diffDays}天后到期)`;
    return '';
};

const getTimeRemaining = (dueDate: string): string => {
    const now = new Date();
    const due = new Date(dueDate);
    const diffMs = due.getTime() - now.getTime();
    const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

    if (diffMs < 0) return '已逾期';
    if (diffDays === 0) return '今天到期';
    if (diffDays === 1) return '明天到期';
    if (diffDays <= 7) return `${diffDays}天`;
    if (diffDays <= 30) return `${diffDays}天`;

    const diffMonths = Math.floor(diffDays / 30);
    return diffMonths > 0 ? `${diffMonths}个月` : `${diffDays}天`;
};
</script>

<style scoped lang="scss">
.task-view-dialog {
    display: flex;
    flex-direction: column;
    overflow: hidden;

    .dialog-header {
        background: linear-gradient(
            135deg,
            #ffffff 0%,
            #f8fafc 15%,
            #e2e8f0 30%,
            #cbd5e1 45%,
            #94a3b8 60%,
            #64748b 75%,
            #475569 90%,
            #334155 100%
        );
        position: relative;
        overflow: hidden;
        color: #1e293b;
        padding: 1.5rem 2rem;
        border-bottom: 2px solid rgba(59, 130, 246, 0.2);

        // 蓝色科技光效
        &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(
                45deg,
                transparent 0%,
                rgba(59, 130, 246, 0.08) 20%,
                rgba(37, 99, 235, 0.12) 40%,
                rgba(29, 78, 216, 0.15) 60%,
                rgba(59, 130, 246, 0.1) 80%,
                transparent 100%
            );
            z-index: 1;
        }

        // 动态蓝色光束
        &::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                90deg,
                transparent 0%,
                rgba(59, 130, 246, 0.15) 30%,
                rgba(37, 99, 235, 0.2) 50%,
                rgba(59, 130, 246, 0.15) 70%,
                transparent 100%
            );
            animation: sweep 4s ease-in-out infinite;
            z-index: 2;
        }

        .header-content {
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: relative;
            z-index: 3;

            .task-info {
                display: flex;
                align-items: center;
                gap: 2rem;
                flex: 1;

                .task-title-container {
                    display: flex;
                    align-items: center;
                    gap: 1rem;

                    .title-icon {
                        background: linear-gradient(135deg, #3b82f6, #2563eb);
                        color: white !important;
                        padding: 0.5rem;
                        border-radius: 8px;
                        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.4);
                        border: 2px solid rgba(255, 255, 255, 0.8);
                    }

                    .title-info {
                        .task-title {
                            margin: 0;
                            font-size: 1.5rem;
                            font-weight: 600;
                            line-height: 1.3;
                            color: #1e293b;
                            text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
                        }

                        .task-subtitle {
                            margin: 0;
                            font-size: 0.875rem;
                            opacity: 0.7;
                            color: #475569;
                        }
                    }
                }

                .status-badges {
                    display: flex;
                    gap: 0.5rem;

                    .status-chip,
                    .priority-chip {
                        font-weight: 600;
                    }
                }
            }

            .header-actions {
                display: flex;
                align-items: center;
                gap: 0.5rem;

                .action-btn,
                .close-btn {
                    background: linear-gradient(
                        135deg,
                        rgba(255, 255, 255, 0.9),
                        rgba(248, 250, 252, 0.8)
                    );
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(59, 130, 246, 0.3);
                    transition: all 0.3s ease;
                    color: #475569;

                    &:hover {
                        background: linear-gradient(
                            135deg,
                            rgba(59, 130, 246, 0.1),
                            rgba(37, 99, 235, 0.08)
                        );
                        border-color: rgba(59, 130, 246, 0.5);
                        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.2);
                        transform: translateY(-1px);
                        color: #1e293b;
                    }

                    .q-icon {
                        color: inherit;
                    }
                }
            }
        }
    }

    .dialog-content {
        flex: 1;
        padding: 2rem;
        overflow-y: auto;

        // 对话框内容滚动条样式 - 柔和蓝白科技风格
        &::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }

        &::-webkit-scrollbar-track {
            background: linear-gradient(to bottom, #f8fafc, #f1f5f9);
            border-radius: 3px;
            border: 1px solid rgba(148, 163, 184, 0.1);
        }

        &::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #cbd5e1, #94a3b8);
            border-radius: 3px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 1px 2px rgba(148, 163, 184, 0.1);
            transition: all 0.2s ease;

            &:hover {
                background: linear-gradient(135deg, #94a3b8, #64748b);
                border-color: rgba(255, 255, 255, 0.4);
                box-shadow: 0 1px 3px rgba(148, 163, 184, 0.15);
            }

            &:active {
                background: linear-gradient(135deg, #64748b, #475569);
            }
        }

        &::-webkit-scrollbar-corner {
            background: linear-gradient(135deg, #f8fafc, #f1f5f9);
            border-radius: 3px;
        }

        .content-layout {
            display: grid;
            grid-template-columns: 1fr 350px;
            gap: 2rem;
            height: 100%;

            .main-content {
                .content-section {
                    margin-bottom: 2rem;

                    .section-title {
                        display: flex;
                        align-items: center;
                        gap: 0.5rem;
                        margin: 0 0 1rem 0;
                        font-size: 1.125rem;
                        font-weight: 600;
                        color: #374151;
                        padding-bottom: 0.5rem;
                        border-bottom: 2px solid #e5e7eb;
                    }

                    .section-content {
                        .task-description {
                            font-size: 1rem;
                            line-height: 1.6;
                            color: #374151;
                            white-space: pre-wrap;
                            background: #f9fafb;
                            padding: 1rem;
                            border-radius: 8px;
                            border-left: 4px solid #3b82f6;
                        }

                        .empty-description,
                        .empty-tags {
                            display: flex;
                            align-items: center;
                            gap: 0.5rem;
                            padding: 1rem;
                            background: #f3f4f6;
                            border-radius: 8px;
                            color: #6b7280;
                            font-style: italic;
                        }

                        .tags-container {
                            display: flex;
                            flex-wrap: wrap;
                            gap: 0.5rem;

                            .task-tag {
                                border: 1px solid #d1d5db;
                            }
                        }

                        .time-info {
                            .time-item {
                                display: flex;
                                align-items: center;
                                gap: 0.5rem;
                                padding: 0.75rem;
                                margin-bottom: 0.5rem;
                                background: #f9fafb;
                                border-radius: 6px;

                                .time-label {
                                    font-weight: 500;
                                    color: #6b7280;
                                    min-width: 80px;
                                }

                                .time-value {
                                    font-weight: 600;
                                    color: #374151;

                                    .due-status {
                                        font-weight: 400;
                                        font-size: 0.875rem;
                                        margin-left: 0.5rem;
                                    }

                                    &.text-negative {
                                        color: #ef4444;
                                    }

                                    &.text-warning {
                                        color: #f59e0b;
                                    }

                                    &.text-orange {
                                        color: #ea580c;
                                    }
                                }
                            }
                        }
                    }
                }
            }

            .side-panel {
                background: #f8fafc;
                border-radius: 12px;
                padding: 1.5rem;
                height: fit-content;

                .panel-section {
                    margin-bottom: 0.5rem;

                    &:last-child {
                        margin-bottom: 0;
                    }

                    .panel-title {
                        margin: 0 0 1rem 0;
                        font-size: 1rem;
                        font-weight: 600;
                        color: #374151;
                        text-transform: uppercase;
                        font-size: 0.875rem;
                        letter-spacing: 0.05em;
                    }

                    .info-grid {
                        .info-item {
                            display: flex;
                            align-items: center;
                            justify-content: space-between;
                            padding: 0.75rem 0;
                            border-bottom: 1px solid #e5e7eb;

                            &:last-child {
                                border-bottom: none;
                            }

                            .info-label {
                                font-weight: 500;
                                color: #6b7280;
                            }

                            .assignee-info {
                                display: flex;
                                align-items: center;
                                gap: 0.5rem;

                                .assignee-name {
                                    font-weight: 500;
                                    color: #374151;
                                }
                            }
                        }
                    }

                    .stats-grid {
                        .stat-item {
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                            padding: 0.75rem;
                            background: white;
                            border-radius: 8px;
                            margin-bottom: 0.5rem;

                            &:last-child {
                                margin-bottom: 0;
                            }

                            .stat-value {
                                font-weight: 600;
                                color: #374151;
                                margin: 0.25rem 0;

                                &.text-negative {
                                    color: #ef4444;
                                }

                                &.text-warning {
                                    color: #f59e0b;
                                }

                                &.text-orange {
                                    color: #ea580c;
                                }
                            }

                            .stat-label {
                                font-size: 0.75rem;
                                color: #6b7280;
                                text-transform: uppercase;
                                letter-spacing: 0.05em;
                            }
                        }
                    }
                }
            }
        }

        .loading-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 50vh;
            color: #6b7280;

            p {
                margin-top: 1rem;
                font-size: 1rem;
            }
        }
    }
}

// 响应式设计
@media (max-width: 1024px) {
    .task-view-dialog {
        .dialog-content {
            .content-layout {
                grid-template-columns: 1fr;

                .side-panel {
                    order: -1;
                    margin-bottom: 1rem;
                }
            }
        }
    }
}

@media (max-width: 768px) {
    .task-view-dialog {
        .dialog-header {
            padding: 1rem;

            .header-content {
                flex-direction: column;
                gap: 1rem;

                .task-info {
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 1rem;

                    .task-title-container {
                        .title-info {
                            .task-title {
                                font-size: 1.25rem;
                            }
                        }
                    }

                    .status-badges {
                        align-self: stretch;
                        justify-content: center;
                    }
                }
            }
        }

        .dialog-content {
            padding: 1rem;
        }
    }
}

// 动画关键帧
@keyframes sweep {
    0% {
        left: -100%;
        opacity: 0;
    }
    25% {
        opacity: 1;
    }
    75% {
        opacity: 1;
    }
    100% {
        left: 100%;
        opacity: 0;
    }
}
</style>

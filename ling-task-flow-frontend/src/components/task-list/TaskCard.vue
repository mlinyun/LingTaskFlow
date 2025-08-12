<template>
    <div
        :class="{ 'task-selected': selectable && selected }"
        class="task-card"
        @click="() => emit('view', task)"
    >
        <!-- 拖拽手柄 -->
        <slot name="drag-handle" />

        <!-- 选择复选框 -->
        <div v-if="selectable" class="task-checkbox" @click.stop>
            <q-checkbox
                :model-value="selected"
                class="card-checkbox"
                @update:model-value="toggleSelect"
            />
        </div>

        <div :class="`status-${task.status.toLowerCase()}`" class="task-status-indicator" />

        <div class="task-content">
            <div class="task-header">
                <h4 class="task-title">{{ task.title }}</h4>
                <div class="task-meta">
                    <q-badge
                        :color="getPriorityColor(task.priority)"
                        :label="getPriorityLabel(task.priority)"
                        class="priority-badge"
                    />
                    <q-badge
                        :color="getStatusColor(task.status)"
                        :label="getStatusLabel(task.status)"
                        class="status-badge"
                        outline
                    />
                    <!-- 逾期标识移到状态旁边 -->
                    <q-badge
                        v-if="isOverdue"
                        class="overdue-badge"
                        color="red"
                        label="已逾期"
                        text-color="white"
                    />
                </div>
            </div>

            <!-- 截止时间展示 -->
            <div v-if="task.due_date" :class="{ overdue: isOverdue }" class="due-date-info">
                <q-icon name="event" />
                <span>截止：{{ formatDueDate(task.due_date) }}</span>
            </div>

            <p v-if="task.description" class="task-description">{{ task.description }}</p>

            <div v-if="tags.length > 0" class="task-tags">
                <q-icon class="tags-icon" name="label" />
                <div class="tags-list">
                    <span v-for="tag in tags.slice(0, 3)" :key="tag" class="tag">#{{ tag }}</span>
                    <span v-if="tags.length > 3" class="tag-more">+{{ tags.length - 3 }}</span>
                </div>
            </div>

            <div class="task-timestamps">
                <div class="timestamp">
                    <q-icon name="schedule" />
                    <span>{{ formatTimestamp(task.created_at) }}</span>
                </div>
                <div v-if="task.updated_at !== task.created_at" class="timestamp">
                    <q-icon name="edit" />
                    <span>{{ formatTimestamp(task.updated_at) }}</span>
                </div>
            </div>

            <div class="task-toolbar" @click.stop>
                <!-- 状态转换按钮 -->
                <q-btn
                    v-if="task.status === 'PENDING'"
                    color="blue"
                    flat
                    icon="play_arrow"
                    round
                    size="sm"
                    @click="() => emit('start-task', task)"
                >
                    <q-tooltip>开始任务</q-tooltip>
                </q-btn>

                <q-btn
                    v-if="task.status === 'IN_PROGRESS'"
                    color="orange"
                    flat
                    icon="pause"
                    round
                    size="sm"
                    @click="() => emit('pause-task', task)"
                >
                    <q-tooltip>暂停任务</q-tooltip>
                </q-btn>

                <q-btn
                    v-if="task.status === 'ON_HOLD'"
                    color="blue"
                    flat
                    icon="play_arrow"
                    round
                    size="sm"
                    @click="() => emit('resume-task', task)"
                >
                    <q-tooltip>恢复任务</q-tooltip>
                </q-btn>

                <!-- 完成/取消完成按钮 -->
                <q-btn
                    :color="task.status === 'COMPLETED' ? 'orange' : 'green'"
                    :icon="task.status === 'COMPLETED' ? 'undo' : 'check'"
                    flat
                    round
                    size="sm"
                    @click="() => emit('toggle-status', task)"
                >
                    <q-tooltip>{{
                        task.status === 'COMPLETED' ? '标记为未完成' : '标记为完成'
                    }}</q-tooltip>
                </q-btn>

                <!-- 编辑按钮 -->
                <q-btn
                    color="primary"
                    flat
                    icon="edit"
                    round
                    size="sm"
                    @click="() => emit('edit', task)"
                >
                    <q-tooltip>编辑任务</q-tooltip>
                </q-btn>

                <!-- 删除按钮 -->
                <q-btn
                    color="red"
                    flat
                    icon="delete"
                    round
                    size="sm"
                    @click="() => emit('delete', task)"
                >
                    <q-tooltip>删除任务</q-tooltip>
                </q-btn>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue';
import type { Task, TaskPriority, TaskStatus } from 'src/types/task';
import { getTaskTags } from 'src/utils/tagUtils';
import { format } from 'date-fns';

const emit = defineEmits<{
    (e: 'view', task: Task): void;
    (e: 'toggle-status', task: Task): void;
    (e: 'start-task', task: Task): void;
    (e: 'pause-task', task: Task): void;
    (e: 'resume-task', task: Task): void;
    (e: 'edit', task: Task): void;
    (e: 'delete', task: Task): void;
    (e: 'toggle-select', id: string): void;
}>();

const props = defineProps<{
    task: Task;
    selectable?: boolean;
    selected?: boolean;
}>();

const toggleSelect = () => {
    emit('toggle-select', props.task.id);
};

const tags = computed(() => getTaskTags(props.task.tags));

// 判断任务是否逾期
const isOverdue = computed(() => {
    if (!props.task.due_date) return false;

    // 已完成或已取消的任务不显示为逾期
    if (props.task.status === 'COMPLETED' || props.task.status === 'CANCELLED') {
        return false;
    }

    const dueDate = new Date(props.task.due_date);
    const now = new Date();
    return dueDate < now;
});

const formatTimestamp = (ts?: string) => {
    if (!ts) return '';
    try {
        return format(new Date(ts), 'yyyy-MM-dd HH:mm');
    } catch {
        return ts;
    }
};

const formatDueDate = (dateStr: string) => {
    try {
        // 统一使用与后端一致的格式化方式
        return format(new Date(dateStr), 'yyyy-MM-dd HH:mm');
    } catch {
        return dateStr;
    }
};

const getPriorityColor = (priority: TaskPriority) => {
    switch (priority) {
        case 'URGENT':
            return 'red';
        case 'HIGH':
            return 'orange';
        case 'MEDIUM':
            return 'blue';
        case 'LOW':
        default:
            return 'grey-7';
    }
};

const getStatusColor = (status: TaskStatus) => {
    switch (status) {
        case 'COMPLETED':
            return 'green';
        case 'IN_PROGRESS':
            return 'orange';
        case 'PENDING':
            return 'grey-7';
        case 'CANCELLED':
            return 'red';
        case 'ON_HOLD':
            return 'purple';
        default:
            return 'grey-7';
    }
};

const getPriorityLabel = (priority: TaskPriority) =>
    ({
        URGENT: '紧急',
        HIGH: '高',
        MEDIUM: '中',
        LOW: '低',
    })[priority] || '未知';

const getStatusLabel = (status: TaskStatus) =>
    ({
        PENDING: '待处理',
        IN_PROGRESS: '进行中',
        COMPLETED: '已完成',
        CANCELLED: '已取消',
        ON_HOLD: '暂停',
    })[status] || '未知';
</script>

<style lang="scss" scoped>
/***** 复用 TaskListPage 现有样式命名，保证视觉一致 *****/
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
}
.task-card::before {
    content: '';
    position: absolute;
    inset: 0;
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
.task-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(14, 165, 233, 0.15);
    border-color: rgba(59, 130, 246, 0.2);
}
.task-card:hover::before {
    opacity: 1;
}

.task-status-indicator {
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    border-radius: 0 4px 4px 0;
}
.task-status-indicator.status-pending {
    background: linear-gradient(180deg, #ef4444, #dc2626);
}
.task-status-indicator.status-in_progress {
    background: linear-gradient(180deg, #f59e0b, #d97706);
}
.task-status-indicator.status-completed {
    background: linear-gradient(180deg, #22c55e, #16a34a);
}

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
    align-items: center;
    flex-wrap: wrap;
}
.priority-badge,
.status-badge,
.overdue-badge {
    font-size: 0.75rem;
    font-weight: 500;
    padding: 0.25rem 0.5rem;
    border-radius: 8px;
}

.overdue-badge {
    background: #ef4444 !important;
    color: white !important;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%,
    100% {
        opacity: 1;
    }
    50% {
        opacity: 0.7;
    }
}

.task-description {
    margin: 0.25rem 0 0.75rem;
    color: #4b5563;
    font-size: 0.95rem;
    line-height: 1.6;
}
.task-tags {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0.5rem 0;
}
.tags-icon {
    color: #9ca3af;
    font-size: 1rem;
}
.tags-list {
    display: flex;
    gap: 0.375rem;
    flex-wrap: wrap;
}
.tag {
    background: #f3f4f6;
    color: #4b5563;
    padding: 0.125rem 0.5rem;
    border-radius: 9999px;
    font-size: 0.75rem;
}
.tag-more {
    color: #6b7280;
    font-size: 0.75rem;
}

.task-timestamps {
    display: flex;
    gap: 1rem;
    margin-top: 0.75rem;
    color: #6b7280;
    font-size: 0.85rem;
}
.timestamp {
    display: flex;
    align-items: center;
    gap: 0.375rem;
}

/* 截止时间行 */
.due-date-info {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin: 4px 0 6px;
    color: #6b7280;
    font-size: 0.85rem;
}
.due-date-info.overdue {
    color: #dc2626;
    font-weight: 600;
}

.task-toolbar {
    position: absolute;
    right: 1rem;
    bottom: 1rem;
    display: flex;
    gap: 0.25rem;
    opacity: 1;
    visibility: visible;
    transition: opacity 0.2s ease;
}
.task-card.task-selected {
    border-color: #3b82f6;
    box-shadow:
        0 0 0 2px rgba(59, 130, 246, 0.25),
        0 12px 32px rgba(14, 165, 233, 0.15);
}
.task-checkbox {
    position: absolute;
    top: 10px;
    left: 10px;
    z-index: 2;
}
.card-checkbox {
    background: white;
    border-radius: 8px;
}
</style>

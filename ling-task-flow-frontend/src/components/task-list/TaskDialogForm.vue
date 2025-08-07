<template>
    <q-dialog v-model="isOpen" persistent no-backdrop-dismiss>
        <q-card class="task-dialog" style="min-width: 700px; max-width: 900px; width: 80vw">
            <!-- 科技感背景 -->
            <div class="dialog-background">
                <div class="tech-grid"></div>
                <div class="floating-particles">
                    <div class="particle"></div>
                    <div class="particle"></div>
                    <div class="particle"></div>
                </div>
                <div class="gradient-overlay"></div>
            </div>

            <q-card-section class="dialog-header">
                <div class="dialog-title">
                    <div class="title-icon-container">
                        <q-icon
                            :name="isEditing ? 'edit' : 'add_task'"
                            size="24px"
                            class="title-icon"
                        />
                        <div class="icon-glow"></div>
                    </div>
                    <div class="title-content">
                        <span class="title-text">{{ isEditing ? '编辑任务' : '创建新任务' }}</span>
                        <div class="title-subtitle">
                            {{ isEditing ? '修改任务信息' : '填写任务详细信息' }}
                        </div>
                    </div>
                </div>
                <q-btn
                    flat
                    round
                    dense
                    icon="close"
                    @click="onCancel"
                    :disable="loading"
                    class="close-btn"
                />
            </q-card-section>

            <q-separator class="tech-separator" />

            <q-card-section class="dialog-content">
                <q-form @submit="onSubmit" class="task-form">
                    <!-- 任务标题 -->
                    <div class="form-group">
                        <div class="field-hint">
                            <q-icon name="info" size="14px" />
                            <span>请为您的任务起一个清晰明确的标题</span>
                        </div>
                        <div class="input-container">
                            <q-input
                                v-model="formData.title"
                                label="任务标题"
                                outlined
                                dense
                                color="primary"
                                :rules="[
                                    val => !!val || '请输入任务标题',
                                    val => val.length <= 200 || '任务标题不能超过200个字符',
                                ]"
                                :loading="loading"
                                class="tech-input"
                                label-color="primary"
                            >
                                <template v-slot:prepend>
                                    <div class="input-icon-container">
                                        <q-icon name="title" class="input-icon" />
                                        <div class="icon-pulse"></div>
                                    </div>
                                </template>
                                <template v-slot:append>
                                    <div class="input-indicator">
                                        <span class="char-counter"
                                            >{{ formData.title?.length || 0 }}/200</span
                                        >
                                    </div>
                                </template>
                            </q-input>
                            <div class="input-glow"></div>
                        </div>
                    </div>

                    <!-- 任务描述 -->
                    <div class="form-group">
                        <div class="field-hint">
                            <q-icon name="lightbulb" size="14px" />
                            <span>详细描述任务内容，帮助您更好地完成任务</span>
                        </div>
                        <div class="input-container">
                            <q-input
                                v-model="formData.description"
                                label="任务描述"
                                type="textarea"
                                outlined
                                dense
                                color="primary"
                                rows="4"
                                :rules="[
                                    val =>
                                        !val || val.length <= 1000 || '任务描述不能超过1000个字符',
                                ]"
                                :loading="loading"
                                class="tech-input description-input"
                                label-color="primary"
                            >
                                <template v-slot:prepend>
                                    <div class="input-icon-container">
                                        <q-icon name="description" class="input-icon" />
                                        <div class="icon-pulse"></div>
                                    </div>
                                </template>
                                <template v-slot:append>
                                    <div class="input-indicator">
                                        <span class="char-counter"
                                            >{{ formData.description?.length || 0 }}/1000</span
                                        >
                                    </div>
                                </template>
                            </q-input>
                            <div class="input-glow"></div>
                        </div>
                    </div>

                    <!-- 任务优先级和截止日期（水平排列） -->
                    <div class="form-row">
                        <div class="form-group form-group-half">
                            <div class="field-hint">
                                <q-icon name="flag" size="14px" />
                                <span>设置任务的优先级</span>
                            </div>
                            <div class="input-container">
                                <q-select
                                    v-model="formData.priority"
                                    label="优先级"
                                    :options="priorityOptions"
                                    outlined
                                    dense
                                    color="primary"
                                    emit-value
                                    map-options
                                    :loading="loading"
                                    class="tech-input"
                                    label-color="primary"
                                >
                                    <template v-slot:prepend>
                                        <div class="input-icon-container">
                                            <q-icon name="priority_high" class="input-icon" />
                                            <div class="icon-pulse"></div>
                                        </div>
                                    </template>
                                    <template v-slot:selected>
                                        <div class="selected-priority">
                                            <q-icon
                                                :name="getPriorityIcon(formData.priority)"
                                                :color="getPriorityColor(formData.priority)"
                                                size="18px"
                                            />
                                            <span>{{
                                                priorityOptions.find(
                                                    opt => opt.value === formData.priority,
                                                )?.label
                                            }}</span>
                                        </div>
                                    </template>
                                    <template v-slot:option="{ itemProps, opt }">
                                        <q-item v-bind="itemProps" class="priority-option">
                                            <q-item-section avatar>
                                                <q-icon
                                                    :name="getPriorityIcon(opt.value)"
                                                    :color="getPriorityColor(opt.value)"
                                                    size="20px"
                                                />
                                            </q-item-section>
                                            <q-item-section>
                                                <q-item-label>{{ opt.label }}</q-item-label>
                                            </q-item-section>
                                        </q-item>
                                    </template>
                                </q-select>
                                <div class="input-glow"></div>
                            </div>
                        </div>

                        <div class="form-group form-group-half">
                            <div class="field-hint">
                                <q-icon name="schedule" size="14px" />
                                <span>{{
                                    formData.due_date
                                        ? '已设置截止时间'
                                        : '可选，设置任务的完成期限'
                                }}</span>
                            </div>
                            <div class="input-container">
                                <q-input
                                    v-model="formData.due_date"
                                    label="截止日期"
                                    type="datetime-local"
                                    outlined
                                    dense
                                    color="primary"
                                    :loading="loading"
                                    class="tech-input"
                                    label-color="primary"
                                >
                                    <template v-slot:prepend>
                                        <div class="input-icon-container">
                                            <q-icon name="event" class="input-icon" />
                                            <div class="icon-pulse"></div>
                                        </div>
                                    </template>
                                    <template v-slot:append>
                                        <q-btn
                                            flat
                                            round
                                            dense
                                            icon="clear"
                                            @click="formData.due_date = ''"
                                            v-if="formData.due_date"
                                            class="clear-btn"
                                        />
                                    </template>
                                </q-input>
                                <div class="input-glow"></div>
                            </div>
                        </div>
                    </div>

                    <!-- 标签 -->
                    <div class="form-group">
                        <div class="field-hint">
                            <q-icon name="style" size="14px" />
                            <span>{{
                                formData.tags?.length
                                    ? `已添加 ${formData.tags.length} 个标签`
                                    : '添加标签帮助分类和查找任务'
                            }}</span>
                        </div>
                        <div class="input-container">
                            <q-input
                                v-model="tagInput"
                                label="标签 (按回车添加)"
                                outlined
                                dense
                                color="primary"
                                @keydown.enter.prevent="addTag"
                                :loading="loading"
                                class="tech-input"
                                label-color="primary"
                            >
                                <template v-slot:prepend>
                                    <div class="input-icon-container">
                                        <q-icon name="local_offer" class="input-icon" />
                                        <div class="icon-pulse"></div>
                                    </div>
                                </template>
                                <template v-slot:append>
                                    <q-btn
                                        flat
                                        round
                                        dense
                                        icon="add"
                                        @click="addTag"
                                        :disable="!tagInput.trim()"
                                        class="add-tag-btn"
                                    />
                                </template>
                            </q-input>
                            <div class="input-glow"></div>
                        </div>

                        <!-- 标签显示 -->
                        <div
                            class="tags-container"
                            v-if="formData.tags && formData.tags.length > 0"
                        >
                            <transition-group name="tag" tag="div" class="tags-grid">
                                <q-chip
                                    v-for="(tag, index) in formData.tags"
                                    :key="`tag-${index}-${tag}`"
                                    removable
                                    @remove="removeTag(index)"
                                    class="tech-chip"
                                    size="sm"
                                >
                                    <template v-slot:default>
                                        <q-icon name="label" size="14px" class="q-mr-xs" />
                                        {{ tag }}
                                    </template>
                                </q-chip>
                            </transition-group>
                        </div>
                    </div>

                    <!-- 任务状态 (仅编辑时显示) -->
                    <div class="form-group" v-if="isEditing">
                        <div class="field-hint">
                            <q-icon name="track_changes" size="14px" />
                            <span>更新任务的当前状态</span>
                        </div>
                        <div class="input-container">
                            <q-select
                                v-model="formData.status"
                                label="任务状态"
                                :options="statusOptions"
                                outlined
                                dense
                                color="primary"
                                emit-value
                                map-options
                                :loading="loading"
                                class="tech-input"
                                label-color="primary"
                            >
                                <template v-slot:prepend>
                                    <div class="input-icon-container">
                                        <q-icon name="assignment" class="input-icon" />
                                        <div class="icon-pulse"></div>
                                    </div>
                                </template>
                                <template v-slot:selected>
                                    <div class="selected-status">
                                        <q-icon
                                            :name="getStatusIcon(formData.status)"
                                            :color="getStatusColor(formData.status)"
                                            size="18px"
                                        />
                                        <span>{{
                                            statusOptions.find(opt => opt.value === formData.status)
                                                ?.label
                                        }}</span>
                                    </div>
                                </template>
                                <template v-slot:option="{ itemProps, opt }">
                                    <q-item v-bind="itemProps" class="status-option">
                                        <q-item-section avatar>
                                            <q-icon
                                                :name="getStatusIcon(opt.value)"
                                                :color="getStatusColor(opt.value)"
                                                size="20px"
                                            />
                                        </q-item-section>
                                        <q-item-section>
                                            <q-item-label>{{ opt.label }}</q-item-label>
                                        </q-item-section>
                                    </q-item>
                                </template>
                            </q-select>
                            <div class="input-glow"></div>
                        </div>
                    </div>
                </q-form>
            </q-card-section>

            <q-separator class="tech-separator" />

            <q-card-actions align="right" class="dialog-actions">
                <div class="actions-container">
                    <q-btn
                        flat
                        label="取消"
                        @click="onCancel"
                        :disable="loading"
                        class="cancel-btn"
                    >
                        <q-icon name="close" size="18px" class="q-mr-sm" />
                        <q-tooltip>取消 (Esc)</q-tooltip>
                    </q-btn>
                    <q-btn
                        unelevated
                        :label="isEditing ? '保存' : '创建'"
                        type="submit"
                        @click="onSubmit"
                        :loading="loading"
                        class="submit-btn"
                    >
                        <template v-slot:loading>
                            <q-spinner-hourglass class="on-left" />
                            {{ isEditing ? '保存中...' : '创建中...' }}
                        </template>
                        <q-icon
                            :name="isEditing ? 'save' : 'add_task'"
                            size="18px"
                            class="q-mr-sm"
                            v-if="!loading"
                        />
                        <q-tooltip>{{ isEditing ? '保存' : '创建' }} (Ctrl+S)</q-tooltip>
                    </q-btn>
                </div>
            </q-card-actions>
        </q-card>
    </q-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useQuasar } from 'quasar';
import { useTaskStore } from 'stores/task';
import type { Task, TaskCreateData, TaskUpdateData, TaskStatus, TaskPriority } from 'src/types';
import { useComponentShortcuts } from 'src/composables/useComponentShortcuts';

interface Props {
    modelValue: boolean;
    task?: Task | null;
}

interface Emits {
    (e: 'update:modelValue', value: boolean): void;
    (e: 'saved', task: Task): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const taskStore = useTaskStore();
const $q = useQuasar();

// 快捷键管理
useComponentShortcuts({
    context: 'dialog',
    shortcuts: {
        save: {
            key: 's',
            ctrl: true,
            description: '保存任务',
            action: () => {
                if (!loading.value) {
                    onSubmit().catch(console.error);
                }
            },
        },
        cancel: {
            key: 'Escape',
            description: '取消编辑',
            action: () => {
                if (!loading.value) {
                    onCancel();
                }
            },
        },
    },
});

// 状态管理
const loading = ref(false);
const tagInput = ref('');

// 计算属性
const isOpen = computed({
    get: () => props.modelValue,
    set: (value: boolean) => emit('update:modelValue', value),
});

const isEditing = computed(() => !!props.task);

// 表单数据
const formData = ref({
    title: '',
    description: '',
    priority: 'MEDIUM' as TaskPriority,
    status: 'PENDING' as TaskStatus,
    due_date: '',
    tags: [] as string[],
});

// 选项数据
const priorityOptions = [
    { label: '低优先级', value: 'LOW' as TaskPriority },
    { label: '中优先级', value: 'MEDIUM' as TaskPriority },
    { label: '高优先级', value: 'HIGH' as TaskPriority },
    { label: '紧急', value: 'URGENT' as TaskPriority },
];

const statusOptions = [
    { label: '待处理', value: 'PENDING' as TaskStatus },
    { label: '进行中', value: 'IN_PROGRESS' as TaskStatus },
    { label: '已完成', value: 'COMPLETED' as TaskStatus },
    { label: '已暂停', value: 'ON_HOLD' as TaskStatus },
];

// 工具函数
const getPriorityIcon = (priority: TaskPriority): string => {
    const icons: Record<TaskPriority, string> = {
        LOW: 'keyboard_arrow_down',
        MEDIUM: 'remove',
        HIGH: 'keyboard_arrow_up',
        URGENT: 'priority_high',
    };
    return icons[priority] || 'remove';
};

const getPriorityColor = (priority: TaskPriority): string => {
    const colors: Record<TaskPriority, string> = {
        LOW: 'grey',
        MEDIUM: 'blue',
        HIGH: 'orange',
        URGENT: 'red',
    };
    return colors[priority] || 'blue';
};

const getStatusIcon = (status: TaskStatus): string => {
    const icons: Record<TaskStatus, string> = {
        PENDING: 'radio_button_unchecked',
        IN_PROGRESS: 'play_circle',
        COMPLETED: 'check_circle',
        CANCELLED: 'cancel',
        ON_HOLD: 'pause_circle',
    };
    return icons[status] || 'radio_button_unchecked';
};

const getStatusColor = (status: TaskStatus): string => {
    const colors: Record<TaskStatus, string> = {
        PENDING: 'grey',
        IN_PROGRESS: 'blue',
        COMPLETED: 'green',
        CANCELLED: 'red',
        ON_HOLD: 'orange',
    };
    return colors[status] || 'grey';
};

// 标签管理
const addTag = () => {
    const tag = tagInput.value.trim();
    if (tag && !formData.value.tags.includes(tag)) {
        formData.value.tags.push(tag);
        tagInput.value = '';
    }
};

const removeTag = (index: number) => {
    formData.value.tags.splice(index, 1);
};

// 表单操作
const resetForm = () => {
    formData.value = {
        title: '',
        description: '',
        priority: 'MEDIUM' as TaskPriority,
        status: 'PENDING' as TaskStatus,
        due_date: '',
        tags: [],
    };
    tagInput.value = '';
};

const loadTaskData = (task: Task) => {
    console.log('loadTaskData called with task:', task);

    formData.value = {
        title: task.title,
        description: task.description || '',
        priority: task.priority,
        status: task.status,
        due_date: task.due_date ? new Date(task.due_date).toISOString().slice(0, 16) : '',
        // 解析tags字符串为数组
        tags: task.tags ? task.tags.split(',').filter(tag => tag.trim()) : [],
    };

    console.log('formData after loading:', formData.value);
};

const onSubmit = async () => {
    if (loading.value) return;

    try {
        loading.value = true;

        // 准备提交数据 - 将标签数组转换为逗号分隔的字符串
        const baseData = {
            title: formData.value.title,
            description: formData.value.description,
            priority: formData.value.priority,
            status: formData.value.status,
            tags: formData.value.tags.join(','), // 将数组转换为逗号分隔的字符串
            ...(formData.value.due_date && {
                due_date: new Date(formData.value.due_date).toISOString(),
            }),
        };

        let savedTask: Task;

        if (isEditing.value && props.task) {
            // 编辑任务
            savedTask = await taskStore.updateTask(props.task.id, baseData as TaskUpdateData);
            $q.notify({
                type: 'positive',
                message: '任务更新成功！',
                position: 'top',
            });
        } else {
            // 创建任务
            savedTask = await taskStore.createTask(baseData as TaskCreateData);
            $q.notify({
                type: 'positive',
                message: '任务创建成功！',
                position: 'top',
            });
        }

        emit('saved', savedTask);
        isOpen.value = false;
        resetForm();
    } catch (error) {
        console.error('保存任务失败:', error);
        $q.notify({
            type: 'negative',
            message: isEditing.value ? '任务更新失败' : '任务创建失败',
            position: 'top',
        });
    } finally {
        loading.value = false;
    }
};

const onCancel = () => {
    if (loading.value) return;

    isOpen.value = false;
    resetForm();
};

// 监听对话框打开和任务变化
watch(
    () => props.modelValue,
    newVal => {
        if (newVal) {
            if (props.task) {
                loadTaskData(props.task);
            } else {
                resetForm();
            }
        }
    },
);

watch(
    () => props.task,
    newTask => {
        if (newTask && props.modelValue) {
            loadTaskData(newTask);
        }
    },
);
</script>

<style scoped lang="scss">
.task-dialog {
    position: relative;
    background: rgba(248, 250, 252, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    overflow: hidden;
    border: 1px solid rgba(59, 130, 246, 0.2);
    box-shadow:
        0 25px 50px rgba(0, 0, 0, 0.15),
        0 0 0 1px rgba(255, 255, 255, 0.8),
        inset 0 1px 0 rgba(255, 255, 255, 0.9);

    // 科技感背景
    .dialog-background {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        pointer-events: none;
        z-index: 1;

        .tech-grid {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image:
                linear-gradient(rgba(59, 130, 246, 0.04) 1px, transparent 1px),
                linear-gradient(90deg, rgba(59, 130, 246, 0.04) 1px, transparent 1px);
            background-size: 30px 30px;
            animation: gridMove 30s linear infinite;
        }

        .floating-particles {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;

            .particle {
                position: absolute;
                width: 4px;
                height: 4px;
                background: radial-gradient(circle, rgba(59, 130, 246, 0.8) 0%, transparent 70%);
                border-radius: 50%;
                animation: float 12s ease-in-out infinite;

                &:nth-child(1) {
                    top: 20%;
                    left: 15%;
                    animation-delay: 0s;
                }

                &:nth-child(2) {
                    top: 60%;
                    right: 20%;
                    animation-delay: 4s;
                }

                &:nth-child(3) {
                    bottom: 30%;
                    left: 70%;
                    animation-delay: 8s;
                }
            }
        }

        .gradient-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(
                135deg,
                rgba(59, 130, 246, 0.03) 0%,
                transparent 50%,
                rgba(14, 165, 233, 0.03) 100%
            );
        }
    }

    // 对话框头部
    .dialog-header {
        position: relative;
        z-index: 2;
        padding: 2rem;
        background: linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.9) 0%,
            rgba(248, 250, 252, 0.8) 100%
        );
        border-bottom: 1px solid rgba(59, 130, 246, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;

        .dialog-title {
            display: flex;
            align-items: center;
            gap: 1rem;
            flex: 1;

            .title-icon-container {
                position: relative;
                width: 48px;
                height: 48px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(
                    135deg,
                    rgba(59, 130, 246, 0.1),
                    rgba(14, 165, 233, 0.1)
                );
                border-radius: 16px;
                border: 2px solid rgba(59, 130, 246, 0.2);

                .title-icon {
                    color: #3b82f6;
                    z-index: 2;
                }

                .icon-glow {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    width: 100%;
                    height: 100%;
                    background: radial-gradient(
                        circle,
                        rgba(59, 130, 246, 0.3) 0%,
                        transparent 70%
                    );
                    border-radius: 50%;
                    animation: pulse 2s ease-in-out infinite;
                }
            }

            .title-content {
                .title-text {
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: #1e293b;
                    display: block;
                    line-height: 1.2;
                }

                .title-subtitle {
                    font-size: 0.875rem;
                    color: #64748b;
                    margin-top: 0.25rem;
                    font-weight: 500;
                }
            }
        }

        .close-btn {
            position: absolute;
            top: 2.5rem;
            right: 2rem;
            width: 40px;
            height: 40px;
            background: rgba(255, 255, 255, 0.8);
            border: 1px solid rgba(59, 130, 246, 0.15);
            border-radius: 12px;
            color: #64748b;
            transition: all 0.3s ease;
            z-index: 10;

            &:hover {
                background: rgba(239, 68, 68, 0.1);
                border-color: rgba(239, 68, 68, 0.3);
                color: #ef4444;
                transform: scale(1.05);
            }
        }
    }

    // 科技感分隔线
    .tech-separator {
        height: 1px;
        background: linear-gradient(
            90deg,
            transparent 0%,
            rgba(59, 130, 246, 0.3) 20%,
            rgba(59, 130, 246, 0.6) 50%,
            rgba(59, 130, 246, 0.3) 80%,
            transparent 100%
        );
        border: none;
        margin: 0;
        position: relative;

        &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 60px;
            height: 1px;
            background: linear-gradient(90deg, transparent, #3b82f6, transparent);
            animation: scanLine 3s ease-in-out infinite;
        }
    }

    // 对话框内容
    .dialog-content {
        position: relative;
        z-index: 2;
        padding: 2rem;
        max-height: 70vh;
        overflow-y: auto;

        // 自定义滚动条
        &::-webkit-scrollbar {
            width: 6px;
        }

        &::-webkit-scrollbar-track {
            background: rgba(59, 130, 246, 0.05);
            border-radius: 3px;
        }

        &::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #3b82f6, #2563eb);
            border-radius: 3px;

            &:hover {
                background: linear-gradient(135deg, #2563eb, #1d4ed8);
            }
        }

        .task-form {
            // 水平布局行
            .form-row {
                display: flex;
                gap: 1.25rem;
                margin-bottom: 1.5rem;

                @media (max-width: 768px) {
                    flex-direction: column;
                    gap: 0;
                }
            }

            .form-group {
                margin-bottom: 1.5rem;

                &:last-child {
                    margin-bottom: 0;
                }

                // 水平布局中的半宽表单组
                &.form-group-half {
                    flex: 1;
                    margin-bottom: 0;

                    @media (max-width: 768px) {
                        margin-bottom: 1.25rem;
                    }
                }

                .input-container {
                    position: relative;

                    .tech-input {
                        :deep(.q-field__control) {
                            height: 48px;
                            min-height: 48px;
                            border-radius: 12px;
                            background: rgba(255, 255, 255, 0.8);
                            border: 2px solid rgba(59, 130, 246, 0.15);
                            backdrop-filter: blur(10px);
                            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                            position: relative;
                            overflow: hidden;
                            display: flex;
                            align-items: center;

                            &::before {
                                content: '';
                                position: absolute;
                                top: 0;
                                left: 0;
                                right: 0;
                                bottom: 0;
                                background: linear-gradient(
                                    135deg,
                                    rgba(59, 130, 246, 0.05) 0%,
                                    transparent 50%,
                                    rgba(14, 165, 233, 0.05) 100%
                                );
                                pointer-events: none;
                            }

                            &:hover {
                                border-color: rgba(59, 130, 246, 0.3);
                                transform: translateY(-1px);
                                box-shadow: 0 6px 20px rgba(59, 130, 246, 0.1);
                            }
                        }

                        :deep(.q-field--focused .q-field__control) {
                            border-color: #3b82f6;
                            box-shadow:
                                0 0 0 3px rgba(59, 130, 246, 0.1),
                                0 6px 20px rgba(59, 130, 246, 0.15);
                            transform: translateY(-2px);
                        }

                        :deep(.q-field__label) {
                            color: #64748b;
                            font-weight: 600;
                            font-size: 0.875rem;
                            line-height: 1;
                        }

                        :deep(.q-field--focused .q-field__label) {
                            color: #3b82f6;
                        }

                        :deep(.q-field__native),
                        :deep(.q-field__input) {
                            color: #1e293b;
                            font-weight: 500;
                            padding: 0 0.75rem;
                            line-height: 1.4;
                        }

                        :deep(.q-field__prepend) {
                            padding-right: 8px;
                        }

                        :deep(.q-field__append) {
                            padding-left: 8px;
                        }

                        // 多行文本输入框
                        &.description-input {
                            :deep(.q-field__control) {
                                height: auto;
                                min-height: 96px;
                                align-items: flex-start;
                                padding-top: 12px;
                                padding-bottom: 12px;
                            }

                            :deep(.q-field__native) {
                                resize: vertical;
                                min-height: 60px;
                                line-height: 1.5;
                            }

                            :deep(.q-field__prepend) {
                                align-self: flex-start;
                                padding-top: 2px;
                            }

                            :deep(.q-field__append) {
                                align-self: flex-start;
                                padding-top: 2px;
                            }
                        }

                        // 图标容器
                        .input-icon-container {
                            position: relative;
                            width: 32px;
                            height: 32px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            background: rgba(59, 130, 246, 0.1);
                            border-radius: 8px;
                            flex-shrink: 0;

                            .input-icon {
                                color: #3b82f6;
                                font-size: 16px;
                                z-index: 2;
                            }

                            .icon-pulse {
                                position: absolute;
                                top: 50%;
                                left: 50%;
                                transform: translate(-50%, -50%);
                                width: 100%;
                                height: 100%;
                                background: rgba(59, 130, 246, 0.2);
                                border-radius: 8px;
                                animation: pulse 2s ease-in-out infinite;
                            }
                        }

                        // 输入指示器
                        .input-indicator {
                            display: flex;
                            align-items: center;
                            gap: 0.5rem;
                            flex-shrink: 0;

                            .char-counter {
                                font-size: 0.75rem;
                                color: #64748b;
                                font-weight: 600;
                                background: rgba(59, 130, 246, 0.1);
                                padding: 0.2rem 0.4rem;
                                border-radius: 4px;
                                min-width: 50px;
                                text-align: center;
                            }
                        }

                        // 清除按钮和添加按钮
                        .clear-btn,
                        .add-tag-btn {
                            width: 28px;
                            height: 28px;
                            background: rgba(59, 130, 246, 0.1);
                            border-radius: 6px;
                            color: #3b82f6;
                            transition: all 0.3s ease;
                            flex-shrink: 0;

                            &:hover {
                                background: rgba(59, 130, 246, 0.2);
                                transform: scale(1.1);
                            }
                        }

                        // 选中状态显示
                        .selected-priority,
                        .selected-status {
                            display: flex;
                            align-items: center;
                            gap: 0.5rem;
                            font-weight: 600;
                            line-height: 1;
                        }
                    }

                    .input-glow {
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        height: 48px; // 标准输入框高度
                        border-radius: 12px;
                        background: linear-gradient(
                            135deg,
                            rgba(59, 130, 246, 0.1) 0%,
                            transparent 50%,
                            rgba(14, 165, 233, 0.1) 100%
                        );
                        opacity: 0;
                        transition: opacity 0.3s ease;
                        pointer-events: none;
                        z-index: -1;
                    }

                    // 描述输入框的特殊光效
                    .tech-input.description-input + .input-glow {
                        height: 96px; // 描述输入框高度
                    }

                    &:hover .input-glow {
                        opacity: 1;
                    }
                }

                // 字段提示
                .field-hint {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    color: #64748b;
                    font-size: 0.75rem;
                    font-weight: 500;
                    padding-left: 0.75rem;
                    margin-bottom: 0.5rem; // 改为下边距，位于输入框上方

                    .q-icon {
                        color: #3b82f6;
                        opacity: 0.7;
                        font-size: 12px;
                    }
                }

                // 标签容器
                .tags-container {
                    margin-top: 0.75rem;

                    .tags-grid {
                        display: flex;
                        flex-wrap: wrap;
                        gap: 0.5rem;

                        .tech-chip {
                            background: linear-gradient(135deg, #3b82f6, #2563eb);
                            color: white;
                            border-radius: 8px;
                            font-weight: 600;
                            font-size: 0.75rem;
                            padding: 0.4rem 0.75rem;
                            border: 1px solid rgba(255, 255, 255, 0.2);
                            backdrop-filter: blur(10px);
                            transition: all 0.3s ease;

                            &:hover {
                                transform: translateY(-1px);
                                box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
                            }

                            :deep(.q-chip__icon--remove) {
                                color: rgba(255, 255, 255, 0.8);
                                transition: all 0.3s ease;

                                &:hover {
                                    color: #ef4444;
                                    background: rgba(255, 255, 255, 0.2);
                                    border-radius: 50%;
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // 对话框操作
    .dialog-actions {
        position: relative;
        z-index: 2;
        padding: 1.5rem 2rem;
        background: linear-gradient(
            135deg,
            rgba(248, 250, 252, 0.9) 0%,
            rgba(241, 245, 249, 0.8) 100%
        );
        border-top: 1px solid rgba(59, 130, 246, 0.1);
        border-radius: 0 0 24px 24px;

        .actions-container {
            display: flex;
            gap: 1rem;
            width: 100%;
            justify-content: flex-end;
            max-width: 100%;

            .cancel-btn {
                padding: 0.75rem 1.5rem;
                border-radius: 12px;
                color: #64748b;
                font-weight: 600;
                background: rgba(255, 255, 255, 0.8);
                border: 1px solid rgba(59, 130, 246, 0.15);
                transition: all 0.3s ease;
                min-width: 100px;

                &:hover {
                    background: rgba(239, 68, 68, 0.1);
                    border-color: rgba(239, 68, 68, 0.3);
                    color: #ef4444;
                    transform: translateY(-1px);
                }
            }

            .submit-btn {
                padding: 0.75rem 2rem;
                border-radius: 12px;
                background: linear-gradient(135deg, #3b82f6, #2563eb);
                color: white;
                font-weight: 700;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
                min-width: 120px;

                &::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: -100%;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(
                        90deg,
                        transparent,
                        rgba(255, 255, 255, 0.3),
                        transparent
                    );
                    transition: left 0.6s ease;
                }

                &:hover {
                    background: linear-gradient(135deg, #2563eb, #1d4ed8);
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);

                    &::before {
                        left: 100%;
                    }
                }

                &:active {
                    transform: translateY(0);
                }
            }
        }
    }
}

// 选项样式
.priority-option,
.status-option {
    border-radius: 12px;
    margin: 0.25rem;
    background: rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(59, 130, 246, 0.1);
    transition: all 0.3s ease;

    &:hover {
        background: rgba(59, 130, 246, 0.1);
        border-color: rgba(59, 130, 246, 0.3);
        transform: translateX(4px);
    }
}

// 标签动画
.tag-enter-active,
.tag-leave-active {
    transition: all 0.3s ease;
}

.tag-enter-from {
    opacity: 0;
    transform: scale(0.8) translateY(-10px);
}

.tag-leave-to {
    opacity: 0;
    transform: scale(0.8) translateY(10px);
}

// 动画定义
@keyframes gridMove {
    0% {
        transform: translate(0, 0);
    }
    100% {
        transform: translate(30px, 30px);
    }
}

@keyframes float {
    0%,
    100% {
        transform: translateY(0px) translateX(0px) scale(1);
        opacity: 0.4;
    }
    33% {
        transform: translateY(-15px) translateX(8px) scale(1.2);
        opacity: 0.8;
    }
    66% {
        transform: translateY(8px) translateX(-5px) scale(0.9);
        opacity: 0.6;
    }
}

@keyframes pulse {
    0%,
    100% {
        opacity: 0.3;
        transform: translate(-50%, -50%) scale(1);
    }
    50% {
        opacity: 0.6;
        transform: translate(-50%, -50%) scale(1.1);
    }
}

@keyframes scanLine {
    0%,
    100% {
        opacity: 0;
        transform: translateX(-150%);
    }
    50% {
        opacity: 1;
        transform: translateX(50%);
    }
}

// 响应式设计
@media (max-width: 768px) {
    .task-dialog {
        margin: 1rem;
        min-width: auto !important;
        max-width: none !important;
        width: calc(100vw - 2rem) !important;
        border-radius: 20px;
        max-height: 90vh;

        .dialog-header {
            padding: 1.5rem;

            .dialog-title {
                .title-content {
                    .title-text {
                        font-size: 1.25rem;
                    }
                }
            }

            .close-btn {
                top: 0.75rem;
                right: 0.75rem;
            }
        }

        .dialog-content {
            padding: 1.5rem;
            max-height: 60vh;

            .task-form {
                .form-row {
                    flex-direction: column;
                    gap: 0;
                }

                .form-group {
                    margin-bottom: 1.25rem;

                    &.form-group-half {
                        margin-bottom: 1.25rem;
                    }

                    .input-container .tech-input {
                        :deep(.q-field__control) {
                            height: 44px;
                            min-height: 44px;
                        }

                        &.description-input {
                            :deep(.q-field__control) {
                                min-height: 88px;
                            }
                        }
                    }
                }
            }
        }

        .dialog-actions {
            padding: 1rem 1.5rem;

            .actions-container {
                flex-direction: column-reverse;
                gap: 0.75rem;

                .cancel-btn,
                .submit-btn {
                    width: 100%;
                    justify-content: center;
                    min-width: auto;
                }
            }
        }
    }
}

@media (max-width: 480px) {
    .task-dialog {
        width: 100vw !important;
        height: 100vh !important;
        margin: 0 !important;
        border-radius: 0 !important;
        max-height: 100vh !important;

        .dialog-content {
            max-height: calc(100vh - 200px);
        }
    }
}
</style>

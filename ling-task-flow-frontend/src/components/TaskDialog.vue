<template>
    <q-dialog v-model="isOpen" persistent no-backdrop-dismiss>
        <q-card class="task-dialog" style="min-width: 500px; max-width: 600px">
            <q-card-section class="dialog-header">
                <div class="dialog-title">
                    <q-icon
                        :name="isEditing ? 'edit' : 'add_task'"
                        size="24px"
                        :color="isEditing ? 'orange' : 'primary'"
                    />
                    <span class="text-h6">{{ isEditing ? '编辑任务' : '创建新任务' }}</span>
                </div>
                <q-btn flat round dense icon="close" @click="onCancel" :disable="loading" />
            </q-card-section>

            <q-separator />

            <q-card-section class="dialog-content">
                <q-form @submit="onSubmit" class="task-form">
                    <!-- 任务标题 -->
                    <div class="form-group">
                        <q-input
                            v-model="formData.title"
                            label="任务标题 *"
                            outlined
                            dense
                            color="primary"
                            :rules="[
                                val => !!val || '请输入任务标题',
                                val => val.length <= 200 || '任务标题不能超过200个字符',
                            ]"
                            :loading="loading"
                            class="form-input"
                        >
                            <template v-slot:prepend>
                                <q-icon name="title" color="grey-6" />
                            </template>
                        </q-input>
                    </div>

                    <!-- 任务描述 -->
                    <div class="form-group">
                        <q-input
                            v-model="formData.description"
                            label="任务描述"
                            type="textarea"
                            outlined
                            dense
                            color="primary"
                            rows="3"
                            :rules="[
                                val => !val || val.length <= 1000 || '任务描述不能超过1000个字符',
                            ]"
                            :loading="loading"
                            class="form-input"
                        >
                            <template v-slot:prepend>
                                <q-icon name="description" color="grey-6" />
                            </template>
                        </q-input>
                    </div>

                    <!-- 任务优先级 -->
                    <div class="form-group">
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
                            class="form-input"
                        >
                            <template v-slot:prepend>
                                <q-icon name="priority_high" color="grey-6" />
                            </template>
                            <template v-slot:option="{ itemProps, opt, selected, toggleOption }">
                                <q-item v-bind="itemProps">
                                    <q-item-section avatar>
                                        <q-icon
                                            :name="getPriorityIcon(opt.value)"
                                            :color="getPriorityColor(opt.value)"
                                        />
                                    </q-item-section>
                                    <q-item-section>
                                        <q-item-label>{{ opt.label }}</q-item-label>
                                    </q-item-section>
                                    <q-item-section side>
                                        <q-checkbox
                                            :model-value="selected"
                                            @update:model-value="toggleOption(opt)"
                                        />
                                    </q-item-section>
                                </q-item>
                            </template>
                        </q-select>
                    </div>

                    <!-- 截止日期 -->
                    <div class="form-group">
                        <q-input
                            v-model="formData.due_date"
                            label="截止日期"
                            type="datetime-local"
                            outlined
                            dense
                            color="primary"
                            :loading="loading"
                            class="form-input"
                        >
                            <template v-slot:prepend>
                                <q-icon name="event" color="grey-6" />
                            </template>
                            <template v-slot:append>
                                <q-btn
                                    flat
                                    round
                                    dense
                                    icon="clear"
                                    @click="formData.due_date = ''"
                                    v-if="formData.due_date"
                                />
                            </template>
                        </q-input>
                    </div>

                    <!-- 标签 -->
                    <div class="form-group">
                        <q-input
                            v-model="tagInput"
                            label="标签 (按回车添加)"
                            outlined
                            dense
                            color="primary"
                            @keydown.enter.prevent="addTag"
                            :loading="loading"
                            class="form-input"
                        >
                            <template v-slot:prepend>
                                <q-icon name="local_offer" color="grey-6" />
                            </template>
                        </q-input>

                        <!-- 标签显示 -->
                        <div
                            class="tags-container"
                            v-if="formData.tags && formData.tags.length > 0"
                        >
                            <q-chip
                                v-for="(tag, index) in formData.tags"
                                :key="index"
                                removable
                                @remove="removeTag(index)"
                                color="primary"
                                text-color="white"
                                size="sm"
                            >
                                {{ tag }}
                            </q-chip>
                        </div>
                    </div>

                    <!-- 任务状态 (仅编辑时显示) -->
                    <div class="form-group" v-if="isEditing">
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
                            class="form-input"
                        >
                            <template v-slot:prepend>
                                <q-icon name="assignment" color="grey-6" />
                            </template>
                            <template v-slot:option="{ itemProps, opt, selected, toggleOption }">
                                <q-item v-bind="itemProps">
                                    <q-item-section avatar>
                                        <q-icon
                                            :name="getStatusIcon(opt.value)"
                                            :color="getStatusColor(opt.value)"
                                        />
                                    </q-item-section>
                                    <q-item-section>
                                        <q-item-label>{{ opt.label }}</q-item-label>
                                    </q-item-section>
                                    <q-item-section side>
                                        <q-checkbox
                                            :model-value="selected"
                                            @update:model-value="toggleOption(opt)"
                                        />
                                    </q-item-section>
                                </q-item>
                            </template>
                        </q-select>
                    </div>
                </q-form>
            </q-card-section>

            <q-separator />

            <q-card-actions align="right" class="dialog-actions">
                <q-btn flat label="取消" @click="onCancel" :disable="loading" color="grey-7" />
                <q-btn
                    unelevated
                    :label="isEditing ? '保存' : '创建'"
                    type="submit"
                    color="primary"
                    @click="onSubmit"
                    :loading="loading"
                />
            </q-card-actions>
        </q-card>
    </q-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { useTaskStore } from 'src/stores/task';
import { useQuasar } from 'quasar';
import type { Task, TaskCreateData, TaskUpdateData, TaskPriority, TaskStatus } from 'src/types';

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
        // 优先使用tags_list（如果存在），否则解析tags字符串
        tags: task.tags_list || (task.tags ? task.tags.split(',').filter(tag => tag.trim()) : []),
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
    .dialog-header {
        padding: 1.5rem;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);

        .dialog-title {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            flex: 1;

            .q-icon {
                background: rgba(59, 130, 246, 0.1);
                padding: 0.5rem;
                border-radius: 8px;
            }

            span {
                font-weight: 600;
                color: #1e293b;
            }
        }
    }

    .dialog-content {
        padding: 1.5rem;
        max-height: 70vh;
        overflow-y: auto;

        .task-form {
            .form-group {
                margin-bottom: 1.25rem;

                &:last-child {
                    margin-bottom: 0;
                }

                .form-input {
                    :deep(.q-field__control) {
                        border-radius: 8px;
                        border: 2px solid #e2e8f0;

                        &:hover {
                            border-color: #cbd5e1;
                        }
                    }

                    :deep(.q-field--focused .q-field__control) {
                        border-color: #3b82f6;
                        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
                    }
                }

                .tags-container {
                    margin-top: 0.75rem;
                    display: flex;
                    flex-wrap: wrap;
                    gap: 0.5rem;
                }
            }
        }
    }

    .dialog-actions {
        padding: 1rem 1.5rem;
        background: #f8fafc;

        .q-btn {
            padding: 0.5rem 1.5rem;
            border-radius: 8px;
            font-weight: 500;

            &[color='primary'] {
                background: linear-gradient(135deg, #3b82f6, #2563eb);

                &:hover {
                    background: linear-gradient(135deg, #2563eb, #1d4ed8);
                }
            }
        }
    }
}

// 响应式设计
@media (max-width: 768px) {
    .task-dialog {
        margin: 1rem;
        min-width: auto !important;
        max-width: none !important;
        width: calc(100vw - 2rem);

        .dialog-header {
            padding: 1rem;
        }

        .dialog-content {
            padding: 1rem;
        }

        .dialog-actions {
            padding: 1rem;
        }
    }
}
</style>

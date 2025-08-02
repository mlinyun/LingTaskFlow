<template>
    <q-page class="q-pa-md">
        <div class="row q-gutter-md">
            <!-- 页面标题和统计 -->
            <div class="col-12">
                <div class="q-pb-md border-bottom">
                    <div class="flex items-center justify-between">
                        <div>
                            <h1 class="text-h4 q-ma-none text-weight-medium">
                                <q-icon name="delete" size="md" class="q-mr-sm" color="warning" />
                                回收站
                            </h1>
                            <p class="text-body2 text-grey-6 q-ma-none q-mt-xs">
                                已删除的任务将在30天后永久删除
                            </p>
                        </div>
                        <div class="flex q-gutter-sm">
                            <!-- 刷新按钮 -->
                            <q-btn
                                outline
                                color="primary"
                                icon="refresh"
                                label="刷新"
                                :loading="loading"
                                @click="refreshTrash"
                            />
                            <!-- 清空回收站按钮 -->
                            <q-btn
                                v-if="trashTasks.length > 0"
                                color="negative"
                                icon="delete_forever"
                                label="清空回收站"
                                @click="confirmEmptyTrash"
                            />
                        </div>
                    </div>
                </div>
            </div>

            <!-- 回收站统计卡片 -->
            <div class="col-12" v-if="trashStats">
                <div class="row q-gutter-md">
                    <div class="col-12 col-md-4">
                        <q-card flat bordered>
                            <q-card-section class="text-center">
                                <div class="text-h5 text-negative">{{ trashStats.total_deleted_tasks }}</div>
                                <div class="text-caption text-grey-7">回收站任务总数</div>
                            </q-card-section>
                        </q-card>
                    </div>
                    <div class="col-12 col-md-4">
                        <q-card flat bordered>
                            <q-card-section class="text-center">
                                <div class="text-h5 text-positive">{{ trashStats.can_be_restored }}</div>
                                <div class="text-caption text-grey-7">可恢复任务</div>
                            </q-card-section>
                        </q-card>
                    </div>
                    <div class="col-12 col-md-4">
                        <q-card flat bordered>
                            <q-card-section class="text-center">
                                <div class="text-h5 text-info">{{ daysFromOldest }}</div>
                                <div class="text-caption text-grey-7">最早删除天数</div>
                            </q-card-section>
                        </q-card>
                    </div>
                </div>
            </div>

            <!-- 空状态 -->
            <div class="col-12" v-if="!loading && trashTasks.length === 0">
                <q-card flat class="text-center q-pa-xl">
                    <q-icon name="delete_outline" size="120px" color="grey-4" />
                    <div class="text-h6 text-grey-6 q-mt-md">回收站是空的</div>
                    <div class="text-body2 text-grey-5 q-mt-xs">删除的任务会出现在这里</div>
                    <q-btn
                        color="primary"
                        label="返回任务列表"
                        class="q-mt-md"
                        to="/tasks"
                        outline
                    />
                </q-card>
            </div>

            <!-- 已删除任务列表 -->
            <div class="col-12" v-if="trashTasks.length > 0">
                <q-card flat bordered>
                    <!-- 批量操作工具栏 -->
                    <q-card-section v-if="selectedTasks.length > 0" class="bg-grey-1 border-bottom">
                        <div class="flex items-center justify-between">
                            <div class="text-body2">
                                已选择 {{ selectedTasks.length }} 个任务
                            </div>
                            <div class="flex q-gutter-sm">
                                <q-btn
                                    outline
                                    color="positive"
                                    icon="restore"
                                    label="批量恢复"
                                    :loading="batchRestoring"
                                    @click="batchRestore"
                                />
                                <q-btn
                                    outline
                                    color="negative"
                                    icon="delete_forever"
                                    label="批量永久删除"
                                    :loading="batchDeleting"
                                    @click="batchPermanentDelete"
                                />
                                <q-btn
                                    flat
                                    color="grey-7"
                                    icon="clear"
                                    label="取消选择"
                                    @click="clearSelection"
                                />
                            </div>
                        </div>
                    </q-card-section>

                    <!-- 任务列表头部 -->
                    <q-card-section class="q-pa-none">
                        <q-list separator>
                            <!-- 全选头部 -->
                            <q-item class="bg-grey-1">
                                <q-item-section avatar>
                                    <q-checkbox
                                        v-model="allSelected"
                                        :indeterminate="someSelected"
                                        @update:model-value="toggleAllSelection"
                                    />
                                </q-item-section>
                                <q-item-section class="text-weight-medium">
                                    任务信息
                                </q-item-section>
                                <q-item-section side class="text-weight-medium">
                                    删除信息
                                </q-item-section>
                                <q-item-section side class="text-weight-medium">
                                    操作
                                </q-item-section>
                            </q-item>

                            <!-- 任务项 -->
                            <q-item
                                v-for="task in trashTasks"
                                :key="task.id"
                                class="task-item"
                                :class="{ 'bg-selected': selectedTasks.includes(task.id) }"
                            >
                                <q-item-section avatar>
                                    <q-checkbox
                                        :model-value="selectedTasks.includes(task.id)"
                                        @update:model-value="toggleTaskSelection(task.id)"
                                    />
                                </q-item-section>

                                <q-item-section>
                                    <q-item-label class="text-h6">{{ task.title }}</q-item-label>
                                    <q-item-label
                                        caption
                                        lines="2"
                                        class="text-grey-7"
                                        v-if="task.description"
                                    >
                                        {{ task.description }}
                                    </q-item-label>
                                    <div class="flex q-gutter-xs q-mt-xs">
                                        <q-badge
                                            :color="getPriorityColor(task.priority)"
                                            :label="getPriorityLabel(task.priority)"
                                        />
                                        <q-badge
                                            :color="getStatusColor(task.status)"
                                            :label="getStatusLabel(task.status)"
                                            outline
                                        />
                                        <q-badge
                                            v-if="task.tags"
                                            color="grey-5"
                                            outline
                                        >
                                            <q-icon name="label" size="xs" class="q-mr-xs" />
                                            {{ task.tags }}
                                        </q-badge>
                                    </div>
                                </q-item-section>

                                <q-item-section side class="text-grey-6">
                                    <div class="text-caption">
                                        <div>删除于 {{ formatDeleteTime(task.deleted_at) }}</div>
                                        <div class="text-warning" v-if="task.deleted_at">
                                            {{ getRemainingDays(task.deleted_at) }}天后永久删除
                                        </div>
                                        <div class="text-info" v-else>
                                            刚刚删除
                                        </div>
                                    </div>
                                </q-item-section>

                                <q-item-section side>
                                    <div class="flex q-gutter-xs">
                                        <q-btn
                                            round
                                            flat
                                            color="positive"
                                            icon="restore"
                                            size="sm"
                                            @click="restoreTask(task)"
                                        >
                                            <q-tooltip>恢复任务</q-tooltip>
                                        </q-btn>
                                        <q-btn
                                            round
                                            flat
                                            color="negative"
                                            icon="delete_forever"
                                            size="sm"
                                            @click="permanentDeleteTask(task)"
                                        >
                                            <q-tooltip>永久删除</q-tooltip>
                                        </q-btn>
                                    </div>
                                </q-item-section>
                            </q-item>
                        </q-list>
                    </q-card-section>

                    <!-- 分页 -->
                    <q-card-section v-if="totalTasks > pageSize" class="flex justify-center">
                        <q-pagination
                            v-model="currentPage"
                            :max="totalPages"
                            :max-pages="7"
                            direction-links
                            boundary-numbers
                            @update:model-value="onPageChange"
                        />
                    </q-card-section>
                </q-card>
            </div>
        </div>

        <!-- 加载状态 -->
        <q-inner-loading :showing="loading">
            <q-spinner-gears size="50px" color="primary" />
        </q-inner-loading>
    </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { useTaskStore } from 'stores/task';
import type { Task, TrashStats } from '../types';
import { formatDistanceToNow, differenceInDays } from 'date-fns';
import { zhCN } from 'date-fns/locale';

// 依赖注入
const $q = useQuasar();
const taskStore = useTaskStore();

// 响应式数据
const loading = ref(false);
const trashTasks = ref<Task[]>([]);
const trashStats = ref<TrashStats | null>(null);
const totalTasks = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const selectedTasks = ref<string[]>([]);
const batchRestoring = ref(false);
const batchDeleting = ref(false);

// 计算属性
const totalPages = computed(() => Math.ceil(totalTasks.value / pageSize.value));

const allSelected = computed({
    get: () => selectedTasks.value.length === trashTasks.value.length && trashTasks.value.length > 0,
    set: (value: boolean) => {
        if (value) {
            selectedTasks.value = trashTasks.value.map(task => task.id);
        } else {
            selectedTasks.value = [];
        }
    }
});

const someSelected = computed(() =>
    selectedTasks.value.length > 0 && selectedTasks.value.length < trashTasks.value.length
);

const daysFromOldest = computed(() => {
    if (!trashStats.value?.oldest_deleted) return 0;
    return differenceInDays(new Date(), new Date(trashStats.value.oldest_deleted));
});

// 方法
const fetchTrashTasks = async (page = 1) => {
    try {
        loading.value = true;
        const response = await taskStore.fetchTrashTasks(page);

        trashTasks.value = response.tasks;
        totalTasks.value = response.total;
        trashStats.value = response.trashStats;
        currentPage.value = page;
        selectedTasks.value = []; // 清空选择
    } catch (error) {
        console.error('获取回收站任务失败:', error);
        $q.notify({
            type: 'negative',
            message: '获取回收站任务失败',
            position: 'top'
        });
    } finally {
        loading.value = false;
    }
};

const refreshTrash = () => {
    void fetchTrashTasks(currentPage.value);
};

const onPageChange = (page: number) => {
    void fetchTrashTasks(page);
};

const toggleTaskSelection = (taskId: string) => {
    const index = selectedTasks.value.indexOf(taskId);
    if (index > -1) {
        selectedTasks.value.splice(index, 1);
    } else {
        selectedTasks.value.push(taskId);
    }
};

const toggleAllSelection = () => {
    allSelected.value = !allSelected.value;
};

const clearSelection = () => {
    selectedTasks.value = [];
};

const restoreTask = async (task: Task) => {
    try {
        await taskStore.restoreTask(task.id);
        $q.notify({
            type: 'positive',
            message: `任务"${task.title}"已恢复`,
            position: 'top'
        });
        await fetchTrashTasks(currentPage.value);
    } catch (error) {
        console.error('恢复任务失败:', error);
        $q.notify({
            type: 'negative',
            message: '恢复任务失败',
            position: 'top'
        });
    }
};

const permanentDeleteTask = (task: Task) => {
    $q.dialog({
        title: '永久删除确认',
        message: `确定要永久删除任务"${task.title}"吗？此操作无法撤销。`,
        cancel: {
            label: '取消',
            flat: true,
            color: 'grey-7'
        },
        ok: {
            label: '永久删除',
            color: 'negative',
            icon: 'delete_forever'
        },
        persistent: true
    }).onOk(() => {
        void (async () => {
            try {
                await taskStore.permanentDeleteTask(task.id);
                $q.notify({
                    type: 'positive',
                    message: `任务"${task.title}"已永久删除`,
                    position: 'top'
                });
                await fetchTrashTasks(currentPage.value);
            } catch (error) {
                console.error('永久删除任务失败:', error);
                $q.notify({
                    type: 'negative',
                    message: '永久删除任务失败',
                    position: 'top'
                });
            }
        })();
    });
};

const batchRestore = async () => {
    if (selectedTasks.value.length === 0) return;

    const taskCount = selectedTasks.value.length;
    try {
        batchRestoring.value = true;
        await taskStore.batchRestoreTasks(selectedTasks.value);
        $q.notify({
            type: 'positive',
            message: `已恢复 ${taskCount} 个任务`,
            position: 'top'
        });
        await fetchTrashTasks(currentPage.value);
    } catch (error) {
        console.error('批量恢复失败:', error);
        $q.notify({
            type: 'negative',
            message: '批量恢复失败',
            position: 'top'
        });
    } finally {
        batchRestoring.value = false;
    }
};

const batchPermanentDelete = () => {
    if (selectedTasks.value.length === 0) return;

    const taskCount = selectedTasks.value.length;
    $q.dialog({
        title: '批量永久删除确认',
        message: `确定要永久删除选中的 ${taskCount} 个任务吗？此操作无法撤销。`,
        cancel: {
            label: '取消',
            flat: true,
            color: 'grey-7'
        },
        ok: {
            label: '永久删除',
            color: 'negative',
            icon: 'delete_forever'
        },
        persistent: true
    }).onOk(() => {
        void (async () => {
            try {
                batchDeleting.value = true;
                await taskStore.batchPermanentDeleteTasks(selectedTasks.value);
                $q.notify({
                    type: 'positive',
                    message: `已永久删除 ${taskCount} 个任务`,
                    position: 'top'
                });
                await fetchTrashTasks(currentPage.value);
            } catch (error) {
                console.error('批量永久删除失败:', error);
                $q.notify({
                    type: 'negative',
                    message: '批量永久删除失败',
                    position: 'top'
                });
            } finally {
                batchDeleting.value = false;
            }
        })();
    });
};

const confirmEmptyTrash = () => {
    if (trashTasks.value.length === 0) return;

    const taskCount = trashStats.value?.total_deleted_tasks || 0;
    $q.dialog({
        title: '清空回收站确认',
        message: `确定要清空回收站吗？这将永久删除 ${taskCount} 个任务，此操作无法撤销。`,
        cancel: {
            label: '取消',
            flat: true,
            color: 'grey-7'
        },
        ok: {
            label: '清空回收站',
            color: 'negative',
            icon: 'delete_forever'
        },
        persistent: true
    }).onOk(() => {
        void (async () => {
            try {
                await taskStore.emptyTrash(true);
                $q.notify({
                    type: 'positive',
                    message: `回收站已清空，共删除 ${taskCount} 个任务`,
                    position: 'top'
                });
                await fetchTrashTasks(1); // 重新获取第一页
            } catch (error) {
                console.error('清空回收站失败:', error);
                $q.notify({
                    type: 'negative',
                    message: '清空回收站失败',
                    position: 'top'
                });
            }
        })();
    });
};

// 格式化辅助函数
const formatDeleteTime = (deletedAt: string | undefined): string => {
    if (!deletedAt) return '未知时间';
    try {
        return formatDistanceToNow(new Date(deletedAt), {
            addSuffix: true,
            locale: zhCN
        });
    } catch (error) {
        console.error('时间格式化失败:', error);
        return '时间格式错误';
    }
};

const getRemainingDays = (deletedAt: string | undefined): number => {
    if (!deletedAt) return 30; // 如果没有删除时间，假设刚删除
    try {
        const deleteDate = new Date(deletedAt);
        const expiryDate = new Date(deleteDate.getTime() + 30 * 24 * 60 * 60 * 1000); // 30天后
        const remaining = differenceInDays(expiryDate, new Date());
        return Math.max(0, remaining);
    } catch (error) {
        console.error('剩余天数计算失败:', error);
        return 30;
    }
};

const getPriorityColor = (priority: string): string => {
    const colors = {
        'LOW': 'green',
        'MEDIUM': 'blue',
        'HIGH': 'orange',
        'URGENT': 'red'
    };
    return colors[priority as keyof typeof colors] || 'grey';
};

const getPriorityLabel = (priority: string): string => {
    const labels = {
        'LOW': '低优先级',
        'MEDIUM': '中优先级',
        'HIGH': '高优先级',
        'URGENT': '紧急'
    };
    return labels[priority as keyof typeof labels] || priority;
};

const getStatusColor = (status: string): string => {
    const colors = {
        'PENDING': 'grey',
        'IN_PROGRESS': 'blue',
        'COMPLETED': 'green',
        'CANCELLED': 'red',
        'ON_HOLD': 'orange'
    };
    return colors[status as keyof typeof colors] || 'grey';
};

const getStatusLabel = (status: string): string => {
    const labels = {
        'PENDING': '待处理',
        'IN_PROGRESS': '进行中',
        'COMPLETED': '已完成',
        'CANCELLED': '已取消',
        'ON_HOLD': '暂停'
    };
    return labels[status as keyof typeof labels] || status;
};

// 生命周期
onMounted(() => {
    void fetchTrashTasks();
});
</script>

<style scoped>
.border-bottom {
    border-bottom: 1px solid var(--q-separator-color);
}

.task-item {
    transition: background-color 0.2s ease;
}

.task-item:hover {
    background-color: var(--q-color-grey-1);
}

.bg-selected {
    background-color: var(--q-color-blue-1);
}
</style>

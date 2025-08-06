<template>
    <q-page class="trash-page">
        <!-- 页面头部 - 科技风格设计 -->
        <div class="page-header">
            <div class="header-background">
                <div class="tech-grid"></div>
                <div class="floating-particles">
                    <div class="particle"></div>
                    <div class="particle"></div>
                    <div class="particle"></div>
                    <div class="particle"></div>
                </div>
            </div>

            <div class="header-content">
                <div class="title-section">
                    <div class="title-container">
                        <div class="icon-wrapper">
                            <q-icon name="delete" size="24px" class="title-icon" />
                            <div class="icon-glow"></div>
                        </div>
                        <div class="title-text">
                            <h1 class="page-title">
                                <span class="title-primary">回收站</span>
                                <span class="title-accent">管理中心</span>
                            </h1>
                            <p class="page-subtitle">
                                <q-icon name="restore" size="14px" class="q-mr-xs" />
                                {{ formatDate(new Date()) }} 安全管理已删除的任务，支持智能恢复
                            </p>
                        </div>
                    </div>
                </div>

                <div class="action-section">
                    <div class="action-buttons">
                        <q-btn
                            icon="refresh"
                            label="刷新数据"
                            class="refresh-btn"
                            rounded
                            :loading="loading"
                            @click="refreshTrash"
                        />
                        <q-btn
                            :icon="showBulkOperations ? 'close' : 'checklist'"
                            class="fullscreen-btn"
                            flat
                            round
                            @click="showBulkOperations = !showBulkOperations"
                        />
                        <q-btn
                            icon="settings"
                            class="download-btn"
                            flat
                            round
                            @click="showSettings = true"
                        />
                    </div>
                </div>
            </div>

            <!-- 底部装饰线 - 重新设计为更科技感的效果 -->
            <div class="header-decoration">
                <div class="deco-border-glow"></div>
                <div class="deco-particles">
                    <div class="deco-particle"></div>
                    <div class="deco-particle"></div>
                    <div class="deco-particle"></div>
                    <div class="deco-particle"></div>
                    <div class="deco-particle"></div>
                </div>
                <div class="deco-pulse-line"></div>
            </div>
        </div>

        <!-- 统计信息面板 - 与数据概览统一的现代化设计 -->
        <div class="stats-section">
            <div class="stats-grid">
                <div class="stats-card stats-card--red">
                    <div class="stats-card__background">
                        <div class="stats-card__gradient"></div>
                        <div class="stats-card__glow"></div>
                        <div class="stats-card__border"></div>
                    </div>

                    <div class="stats-card__content">
                        <div class="stats-card__icon-container">
                            <div class="stats-card__icon-bg"></div>
                            <q-icon name="delete_outline" class="stats-card__icon" />
                            <div class="stats-card__icon-pulse"></div>
                        </div>

                        <div class="stats-card__data">
                            <div class="stats-card__label">回收站</div>
                            <div class="stats-card__value">
                                {{ trashStats?.total_deleted_tasks || 0 }}
                            </div>
                            <div class="stats-card__metric">总任务数</div>
                        </div>

                        <div class="stats-card__decoration">
                            <div class="stats-card__decoration-bg"></div>
                            <div class="stats-card__decoration-pulse"></div>
                        </div>
                    </div>

                    <div class="stats-card__data-flow">
                        <div class="stats-card__data-flow-line"></div>
                        <div class="stats-card__data-flow-dot"></div>
                    </div>
                </div>

                <div class="stats-card stats-card--green">
                    <div class="stats-card__background">
                        <div class="stats-card__gradient"></div>
                        <div class="stats-card__glow"></div>
                        <div class="stats-card__border"></div>
                    </div>

                    <div class="stats-card__content">
                        <div class="stats-card__icon-container">
                            <div class="stats-card__icon-bg"></div>
                            <q-icon name="restore" class="stats-card__icon" />
                            <div class="stats-card__icon-pulse"></div>
                        </div>

                        <div class="stats-card__data">
                            <div class="stats-card__label">可恢复</div>
                            <div class="stats-card__value">
                                {{ trashStats?.can_be_restored || 0 }}
                            </div>
                            <div class="stats-card__metric">待恢复任务</div>
                        </div>

                        <div class="stats-card__decoration">
                            <div class="stats-card__decoration-bg"></div>
                            <div class="stats-card__decoration-pulse"></div>
                        </div>
                    </div>

                    <div class="stats-card__data-flow">
                        <div class="stats-card__data-flow-line"></div>
                        <div class="stats-card__data-flow-dot"></div>
                    </div>
                </div>

                <div class="stats-card stats-card--orange">
                    <div class="stats-card__background">
                        <div class="stats-card__gradient"></div>
                        <div class="stats-card__glow"></div>
                        <div class="stats-card__border"></div>
                    </div>

                    <div class="stats-card__content">
                        <div class="stats-card__icon-container">
                            <div class="stats-card__icon-bg"></div>
                            <q-icon name="schedule" class="stats-card__icon" />
                            <div class="stats-card__icon-pulse"></div>
                        </div>

                        <div class="stats-card__data">
                            <div class="stats-card__label">最早删除</div>
                            <div class="stats-card__value">{{ daysFromOldest }}</div>
                            <div class="stats-card__metric">天数统计</div>
                        </div>

                        <div class="stats-card__decoration">
                            <div class="stats-card__decoration-bg"></div>
                            <div class="stats-card__decoration-pulse"></div>
                        </div>
                    </div>

                    <div class="stats-card__data-flow">
                        <div class="stats-card__data-flow-line"></div>
                        <div class="stats-card__data-flow-dot"></div>
                    </div>
                </div>

                <div class="stats-card stats-card--purple">
                    <div class="stats-card__background">
                        <div class="stats-card__gradient"></div>
                        <div class="stats-card__glow"></div>
                        <div class="stats-card__border"></div>
                    </div>

                    <div class="stats-card__content">
                        <div class="stats-card__icon-container">
                            <div class="stats-card__icon-bg"></div>
                            <q-icon name="auto_delete" class="stats-card__icon" />
                            <div class="stats-card__icon-pulse"></div>
                        </div>

                        <div class="stats-card__data">
                            <div class="stats-card__label">剩余保留</div>
                            <div class="stats-card__value">
                                {{ Math.max(0, 30 - daysFromOldest) }}
                            </div>
                            <div class="stats-card__metric">天数倒计时</div>
                        </div>

                        <div class="stats-card__decoration">
                            <div class="stats-card__decoration-bg"></div>
                            <div class="stats-card__decoration-pulse"></div>
                        </div>
                    </div>

                    <div class="stats-card__data-flow">
                        <div class="stats-card__data-flow-line"></div>
                        <div class="stats-card__data-flow-dot"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 任务内容区域 -->
        <div class="content-section">
            <!-- 批量操作工具栏 -->
            <div v-if="showBulkOperations" class="bulk-operations-toolbar">
                <div class="toolbar-content">
                    <div class="selection-info">
                        <q-checkbox
                            v-model="allSelected"
                            :indeterminate="someSelected"
                            @update:model-value="toggleAllSelection"
                            class="all-select-checkbox"
                        />
                        <span class="selection-text">
                            已选择 {{ selectedTasks.length }} / {{ trashTasks.length }} 个任务
                        </span>
                    </div>
                    <div class="batch-actions">
                        <q-btn
                            class="batch-btn batch-restore-btn"
                            @click="batchRestore"
                            :loading="batchRestoring"
                            :disable="selectedTasks.length === 0"
                            icon="restore"
                            label="批量恢复"
                            no-caps
                            unelevated
                        />
                        <q-btn
                            class="batch-btn batch-delete-btn"
                            @click="batchPermanentDelete"
                            :loading="batchDeleting"
                            :disable="selectedTasks.length === 0"
                            icon="delete_forever"
                            label="批量删除"
                            no-caps
                            unelevated
                        />
                        <q-btn
                            class="clear-btn"
                            @click="clearSelection"
                            icon="clear"
                            label="清空选择"
                            flat
                            no-caps
                        />
                    </div>
                </div>
            </div>

            <!-- 空状态 -->
            <div v-if="!loading && trashTasks.length === 0" class="empty-state">
                <div class="empty-content">
                    <div class="empty-icon">
                        <q-icon name="delete_outline" />
                        <div class="empty-icon-glow"></div>
                    </div>
                    <h3 class="empty-title">回收站是空的</h3>
                    <p class="empty-description">
                        删除的任务会出现在这里，您可以选择恢复或永久删除它们
                    </p>
                    <q-btn
                        class="back-btn"
                        to="/tasks"
                        icon="arrow_back"
                        label="返回任务列表"
                        no-caps
                        unelevated
                    />
                </div>
            </div>

            <!-- 任务列表 -->
            <div v-else-if="trashTasks.length > 0" class="tasks-container">
                <div class="tasks-header">
                    <div class="header-left">
                        <h3 class="tasks-title">已删除的任务</h3>
                        <div class="tasks-count">共 {{ totalTasks }} 个任务</div>
                    </div>
                    <div class="header-right">
                        <q-btn
                            class="clear-all-btn"
                            @click="handleEmptyTrash"
                            icon="delete_forever"
                            label="清空回收站"
                            no-caps
                            outline
                        />
                    </div>
                </div>

                <div class="tasks-grid">
                    <div
                        v-for="task in trashTasks"
                        :key="task.id"
                        class="task-card"
                        :class="{ 'task-selected': selectedTasks.includes(task.id) }"
                    >
                        <!-- 选择复选框 -->
                        <div class="task-checkbox" v-if="showBulkOperations">
                            <q-checkbox
                                :model-value="selectedTasks.includes(task.id)"
                                @update:model-value="toggleTaskSelection(task.id)"
                                class="card-checkbox"
                            />
                        </div>

                        <!-- 任务内容 -->
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
                                        outline
                                        class="status-badge"
                                    />
                                </div>
                            </div>

                            <p v-if="task.description" class="task-description">
                                {{ task.description }}
                            </p>

                            <div class="task-tags" v-if="task.tags">
                                <q-icon name="label" class="tags-icon" />
                                <span class="tags-text">{{ task.tags }}</span>
                            </div>

                            <div class="task-delete-info">
                                <div class="delete-time">
                                    <q-icon name="schedule" class="time-icon" />
                                    <span>删除于 {{ formatDeleteTime(task.deleted_at) }}</span>
                                </div>
                                <div
                                    class="remaining-days"
                                    :class="getRemainingDaysClass(task.deleted_at)"
                                >
                                    <q-icon name="timer" class="timer-icon" />
                                    <span>{{ getRemainingDays(task.deleted_at) }}天后永久删除</span>
                                </div>
                            </div>
                        </div>

                        <!-- 操作按钮 -->
                        <div class="task-actions">
                            <q-btn
                                class="action-btn restore-btn"
                                @click="restoreTask(task)"
                                icon="restore"
                                round
                                unelevated
                            >
                                <q-tooltip>恢复任务</q-tooltip>
                            </q-btn>
                            <q-btn
                                class="action-btn delete-btn"
                                @click="permanentDeleteTask(task)"
                                icon="delete_forever"
                                round
                                unelevated
                            >
                                <q-tooltip>永久删除</q-tooltip>
                            </q-btn>
                        </div>
                    </div>
                </div>

                <!-- 分页 -->
                <div v-if="totalTasks > pageSize" class="pagination-container">
                    <q-pagination
                        v-model="currentPage"
                        :max="totalPages"
                        :max-pages="7"
                        direction-links
                        boundary-numbers
                        @update:model-value="onPageChange"
                        class="custom-pagination"
                    />
                </div>
            </div>
        </div>

        <!-- 加载状态 -->
        <q-inner-loading :showing="loading" class="custom-loading">
            <div class="loading-content">
                <div class="loading-spinner">
                    <q-spinner-dots size="40px" color="primary" />
                </div>
                <div class="loading-text">正在加载回收站数据...</div>
            </div>
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
import { useGlobalConfirm } from '../composables/useGlobalConfirm';

// 依赖注入
const $q = useQuasar();
const taskStore = useTaskStore();
const confirmDialog = useGlobalConfirm();

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
const showBulkOperations = ref(false);
const showSettings = ref(false);

// 计算属性
const totalPages = computed(() => Math.ceil(totalTasks.value / pageSize.value));

const allSelected = computed({
    get: () =>
        selectedTasks.value.length === trashTasks.value.length && trashTasks.value.length > 0,
    set: (value: boolean) => {
        if (value) {
            selectedTasks.value = trashTasks.value.map(task => task.id);
        } else {
            selectedTasks.value = [];
        }
    },
});

const someSelected = computed(
    () => selectedTasks.value.length > 0 && selectedTasks.value.length < trashTasks.value.length,
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
            position: 'top',
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
            position: 'top',
        });
        await fetchTrashTasks(currentPage.value);
    } catch (error) {
        console.error('恢复任务失败:', error);
        $q.notify({
            type: 'negative',
            message: '恢复任务失败',
            position: 'top',
        });
    }
};

const permanentDeleteTask = async (task: Task) => {
    try {
        const confirmed = await confirmDialog.confirmDanger(
            '永久删除任务',
            `确定要永久删除任务"${task.title}"吗？`,
            {
                details: '永久删除后将无法恢复，请谨慎操作。',
                warningText: '此操作不可撤销，数据将永久丢失',
                confirmText: '永久删除',
                confirmIcon: 'delete_forever',
                persistent: true,
            },
        );

        if (confirmed) {
            confirmDialog.setLoading(true, '正在删除任务...');
            try {
                await taskStore.permanentDeleteTask(task.id);
                $q.notify({
                    type: 'positive',
                    message: `任务"${task.title}"已永久删除`,
                    position: 'top',
                });
                await fetchTrashTasks(currentPage.value);
            } catch (error) {
                console.error('永久删除任务失败:', error);
                $q.notify({
                    type: 'negative',
                    message: '永久删除任务失败',
                    position: 'top',
                });
            } finally {
                confirmDialog.setLoading(false);
            }
        }
    } catch (error) {
        console.error('删除任务失败:', error);
    }
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
            position: 'top',
        });
        await fetchTrashTasks(currentPage.value);
    } catch (error) {
        console.error('批量恢复失败:', error);
        $q.notify({
            type: 'negative',
            message: '批量恢复失败',
            position: 'top',
        });
    } finally {
        batchRestoring.value = false;
    }
};

const batchPermanentDelete = async () => {
    if (selectedTasks.value.length === 0) return;

    const taskCount = selectedTasks.value.length;
    try {
        const confirmed = await confirmDialog.confirmDanger(
            '批量永久删除任务',
            `确定要永久删除选中的 ${taskCount} 个任务吗？`,
            {
                details: '所有选中的任务都将被永久删除。',
                warningText: '此操作不可撤销，所有数据将永久丢失',
                confirmText: '批量永久删除',
                confirmIcon: 'delete_forever',
                persistent: true,
            },
        );

        if (confirmed) {
            confirmDialog.setLoading(true, '正在删除任务...');
            batchDeleting.value = true;
            try {
                await taskStore.batchPermanentDeleteTasks(selectedTasks.value);
                $q.notify({
                    type: 'positive',
                    message: `已永久删除 ${taskCount} 个任务`,
                    position: 'top',
                });
                await fetchTrashTasks(currentPage.value);
                selectedTasks.value = [];
            } catch (error) {
                console.error('批量永久删除失败:', error);
                $q.notify({
                    type: 'negative',
                    message: '批量永久删除失败',
                    position: 'top',
                });
            } finally {
                batchDeleting.value = false;
                confirmDialog.setLoading(false);
            }
        }
    } catch (error) {
        console.error('批量删除任务失败:', error);
    }
};

const handleEmptyTrash = async () => {
    if (trashTasks.value.length === 0) return;

    const taskCount = trashStats.value?.total_deleted_tasks || 0;
    try {
        const confirmed = await confirmDialog.confirmDanger(
            '清空回收站',
            `确定要清空回收站吗？这将永久删除 ${taskCount} 个任务`,
            {
                details: '回收站中的所有任务都将被永久删除。',
                warningText: '此操作不可撤销，所有数据将永久丢失',
                confirmText: '清空回收站',
                confirmIcon: 'delete_forever',
                persistent: true,
            },
        );

        if (confirmed) {
            confirmDialog.setLoading(true, '正在清空回收站...');
            try {
                await taskStore.emptyTrash(true);
                $q.notify({
                    type: 'positive',
                    message: `回收站已清空，共删除 ${taskCount} 个任务`,
                    position: 'top',
                });
                await fetchTrashTasks(1); // 重新获取第一页
            } catch (error) {
                console.error('清空回收站失败:', error);
                $q.notify({
                    type: 'negative',
                    message: '清空回收站失败',
                    position: 'top',
                });
            } finally {
                confirmDialog.setLoading(false);
            }
        }
    } catch (error) {
        console.error('清空回收站失败:', error);
    }
};

// 格式化辅助函数
const formatDate = (date: Date) => {
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long',
    });
};

const formatDeleteTime = (deletedAt: string | undefined): string => {
    if (!deletedAt) return '未知时间';
    try {
        return formatDistanceToNow(new Date(deletedAt), {
            addSuffix: true,
            locale: zhCN,
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

const getRemainingDaysClass = (deletedAt: string | undefined): string => {
    const days = getRemainingDays(deletedAt);
    if (days <= 3) return 'days-critical';
    if (days <= 7) return 'days-warning';
    return 'days-normal';
};

const getPriorityColor = (priority: string): string => {
    const colors = {
        LOW: 'green',
        MEDIUM: 'blue',
        HIGH: 'orange',
        URGENT: 'red',
    };
    return colors[priority as keyof typeof colors] || 'grey';
};

const getPriorityLabel = (priority: string): string => {
    const labels = {
        LOW: '低优先级',
        MEDIUM: '中优先级',
        HIGH: '高优先级',
        URGENT: '紧急',
    };
    return labels[priority as keyof typeof labels] || priority;
};

const getStatusColor = (status: string): string => {
    const colors = {
        PENDING: 'grey',
        IN_PROGRESS: 'blue',
        COMPLETED: 'green',
        CANCELLED: 'red',
        ON_HOLD: 'orange',
    };
    return colors[status as keyof typeof colors] || 'grey';
};

const getStatusLabel = (status: string): string => {
    const labels = {
        PENDING: '待处理',
        IN_PROGRESS: '进行中',
        COMPLETED: '已完成',
        CANCELLED: '已取消',
        ON_HOLD: '暂停',
    };
    return labels[status as keyof typeof labels] || status;
};

// 生命周期
onMounted(() => {
    void fetchTrashTasks();
});
</script>

<style scoped lang="scss">
// 页面整体样式 - 科技感设计
.trash-page {
    min-height: calc(100vh - 50px);
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    position: relative;
    padding: 1.5rem;

    // 背景纹理
    &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image:
            linear-gradient(rgba(59, 130, 246, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(59, 130, 246, 0.03) 1px, transparent 1px);
        background-size: 40px 40px;
        pointer-events: none;
        z-index: 0;
    }
}

// 页面头部设计 - 与Dashboard保持一致
.page-header {
    margin-bottom: 2rem;
    position: relative;
    background: linear-gradient(
        135deg,
        rgba(59, 130, 246, 0.08) 0%,
        rgba(14, 165, 233, 0.05) 50%,
        rgba(6, 182, 212, 0.08) 100%
    );
    border-radius: 24px;
    padding: 2rem;
    overflow: hidden;
    border: 1px solid rgba(59, 130, 246, 0.15);
    box-shadow:
        0 20px 60px rgba(14, 165, 233, 0.08),
        0 8px 24px rgba(59, 130, 246, 0.06),
        inset 0 1px 0 rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(20px);

    // 科技感背景
    .header-background {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        pointer-events: none;

        .tech-grid {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image:
                linear-gradient(rgba(59, 130, 246, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(59, 130, 246, 0.03) 1px, transparent 1px);
            background-size: 30px 30px;
            animation: gridMove 20s linear infinite;
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
                animation: float 6s ease-in-out infinite;

                &:nth-child(1) {
                    top: 20%;
                    left: 10%;
                    animation-delay: 0s;
                }

                &:nth-child(2) {
                    top: 60%;
                    left: 80%;
                    animation-delay: 2s;
                }

                &:nth-child(3) {
                    top: 30%;
                    right: 20%;
                    animation-delay: 4s;
                }

                &:nth-child(4) {
                    bottom: 40%;
                    left: 60%;
                    animation-delay: 1s;
                }
            }
        }
    }

    .header-content {
        position: relative;
        z-index: 2;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 2rem;

        .title-section {
            flex: 1;

            .title-container {
                display: flex;
                align-items: center;
                gap: 1.5rem;

                .icon-wrapper {
                    position: relative;
                    width: 56px;
                    height: 56px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: linear-gradient(
                        135deg,
                        rgba(59, 130, 246, 0.15),
                        rgba(14, 165, 233, 0.1)
                    );
                    border-radius: 16px;
                    border: 2px solid rgba(59, 130, 246, 0.2);
                    box-shadow:
                        0 8px 24px rgba(59, 130, 246, 0.15),
                        inset 0 1px 0 rgba(255, 255, 255, 0.3);

                    .title-icon {
                        color: #3b82f6;
                        z-index: 2;
                    }

                    .icon-glow {
                        position: absolute;
                        top: 50%;
                        left: 50%;
                        transform: translate(-50%, -50%);
                        width: 40px;
                        height: 40px;
                        background: radial-gradient(
                            circle,
                            rgba(59, 130, 246, 0.2) 0%,
                            transparent 70%
                        );
                        border-radius: 50%;
                        animation: pulse 2s ease-in-out infinite;
                    }
                }

                .title-text {
                    flex: 1;

                    .page-title {
                        font-size: 2rem;
                        font-weight: 800;
                        margin: 0 0 0.5rem 0;
                        line-height: 1.2;
                        display: flex;
                        align-items: baseline;
                        gap: 0.5rem;

                        .title-primary {
                            background: linear-gradient(135deg, #1e40af, #3b82f6);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                            background-clip: text;
                        }

                        .title-accent {
                            color: #0ea5e9;
                            font-weight: 600;
                            font-size: 1.5rem;
                        }
                    }

                    .page-subtitle {
                        color: #64748b;
                        margin: 0;
                        font-size: 0.95rem;
                        font-weight: 500;
                        display: flex;
                        align-items: center;
                        letter-spacing: 0.02em;
                    }
                }
            }
        }

        .action-section {
            flex-shrink: 0;

            .action-buttons {
                display: flex;
                align-items: center;
                gap: 0.75rem;

                .refresh-btn {
                    background: linear-gradient(135deg, #3b82f6, #2563eb);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    box-shadow:
                        0 8px 24px rgba(59, 130, 246, 0.25),
                        inset 0 1px 0 rgba(255, 255, 255, 0.2);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    font-weight: 600;
                    height: 44px;
                    padding: 0 1.5rem;

                    &:hover {
                        transform: translateY(-2px);
                        box-shadow:
                            0 12px 32px rgba(59, 130, 246, 0.35),
                            inset 0 1px 0 rgba(255, 255, 255, 0.3);
                        background: linear-gradient(135deg, #2563eb, #1d4ed8);
                    }

                    &:active {
                        transform: translateY(0);
                    }
                }

                .fullscreen-btn,
                .download-btn {
                    width: 44px;
                    height: 44px;
                    background: rgba(59, 130, 246, 0.08);
                    border: 1px solid rgba(59, 130, 246, 0.15);
                    color: #3b82f6;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

                    &:hover {
                        background: rgba(59, 130, 246, 0.15);
                        border-color: rgba(59, 130, 246, 0.25);
                        transform: translateY(-1px);
                        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
                    }

                    &:active {
                        transform: translateY(0);
                    }
                }
            }
        }
    }

    // 底部装饰线 - 重新设计为更科技感的效果
    .header-decoration {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 6px;
        overflow: hidden;

        // 发光边框效果
        .deco-border-glow {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(
                90deg,
                transparent 0%,
                rgba(59, 130, 246, 0.3) 20%,
                rgba(14, 165, 233, 0.8) 50%,
                rgba(59, 130, 246, 0.3) 80%,
                transparent 100%
            );
            box-shadow:
                0 0 8px rgba(14, 165, 233, 0.4),
                0 0 16px rgba(59, 130, 246, 0.2);
            animation: borderPulse 3s ease-in-out infinite;
        }

        // 流动粒子效果
        .deco-particles {
            position: absolute;
            bottom: 1px;
            left: 0;
            right: 0;
            height: 4px;

            .deco-particle {
                position: absolute;
                width: 3px;
                height: 3px;
                background: radial-gradient(
                    circle,
                    #3b82f6 0%,
                    rgba(59, 130, 246, 0.6) 50%,
                    transparent 100%
                );
                border-radius: 50%;
                opacity: 0;
                animation: particleFlow 4s linear infinite;

                &:nth-child(1) {
                    left: 10%;
                    animation-delay: 0s;
                }

                &:nth-child(2) {
                    left: 30%;
                    animation-delay: 0.8s;
                }

                &:nth-child(3) {
                    left: 50%;
                    animation-delay: 1.6s;
                }

                &:nth-child(4) {
                    left: 70%;
                    animation-delay: 2.4s;
                }

                &:nth-child(5) {
                    left: 90%;
                    animation-delay: 3.2s;
                }
            }
        }

        // 脉冲扫描线
        .deco-pulse-line {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100px;
            height: 1px;
            background: linear-gradient(
                90deg,
                transparent 0%,
                rgba(6, 182, 212, 0.8) 50%,
                transparent 100%
            );
            box-shadow: 0 0 6px rgba(6, 182, 212, 0.6);
            animation: scanLine 6s linear infinite;
        }
    }
}

// 统计信息面板 - 与数据概览统一的现代化设计
.stats-section {
    padding: 0 2rem 2rem;
    position: relative;
    z-index: 1;

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1rem;
    }
}

// StatsCard 组件样式 - 紧凑版本，一行显示4个
.stats-card {
    position: relative;
    height: 100px;
    border-radius: 16px;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

    &:hover {
        transform: translateY(-4px) scale(1.02);

        .stats-card__glow {
            opacity: 0.3;
        }

        .stats-card__icon-pulse {
            animation: iconPulse 2s ease-in-out infinite;
        }

        .stats-card__decoration-pulse {
            animation: decorationPulse 3s ease-in-out infinite;
        }

        .stats-card__data-flow-line {
            animation: dataFlow 2s ease-in-out infinite;
        }
    }

    // 背景系统
    &__background {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        overflow: hidden;
    }

    &__gradient {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.95) 0%,
            rgba(255, 255, 255, 0.85) 100%
        );
        backdrop-filter: blur(20px);
    }

    &__glow {
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(
            circle,
            var(--decoration-color-alpha, rgba(59, 130, 246, 0.15)) 0%,
            transparent 70%
        );
        opacity: 0.1;
        transition: opacity 0.4s ease;
    }

    &__border {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        background: linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.1) 0%,
            rgba(255, 255, 255, 0.05) 50%,
            transparent 100%
        );
    }

    // 主要内容布局 - 紧凑版
    &__content {
        position: relative;
        z-index: 2;
        height: 100%;
        display: grid;
        grid-template-columns: auto 1fr auto;
        gap: 0.75rem;
        padding: 1rem;
        align-items: center;
    }

    // 图标容器 (左侧) - 缩小版
    &__icon-container {
        position: relative;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    &__icon-bg {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 40px;
        height: 40px;
        background: var(--icon-bg, rgba(59, 130, 246, 0.15));
        border-radius: 12px;
        border: 1px solid var(--icon-color-alpha, rgba(59, 130, 246, 0.3));
    }

    &__icon {
        position: relative;
        z-index: 2;
        font-size: 20px;
        color: var(--icon-color, #3b82f6);
        filter: drop-shadow(0 2px 4px var(--icon-shadow, rgba(59, 130, 246, 0.4)));
    }

    &__icon-pulse {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 40px;
        height: 40px;
        background: var(--icon-color-alpha, rgba(59, 130, 246, 0.3));
        border-radius: 12px;
        opacity: 0;
    }

    // 数据显示区域 (中间) - 紧凑版
    &__data {
        display: flex;
        flex-direction: column;
        gap: 0.125rem;
        min-width: 0;
    }

    &__label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        opacity: 0.8;
    }

    &__value {
        font-size: 1.75rem;
        font-weight: 800;
        line-height: 1;
        background: linear-gradient(135deg, var(--value-gradient, #3b82f6, #1e40af));
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 2px 4px rgba(59, 130, 246, 0.2));
    }

    &__metric {
        font-size: 0.625rem;
        font-weight: 500;
        color: #94a3b8;
        opacity: 0.9;
    }

    // 装饰元素 (右侧) - 缩小版
    &__decoration {
        position: relative;
        width: 28px;
        height: 28px;
    }

    &__decoration-bg {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 28px;
        height: 28px;
        background: radial-gradient(
            circle,
            var(--decoration-color-alpha, rgba(59, 130, 246, 0.2)) 0%,
            transparent 70%
        );
        border-radius: 50%;
    }

    &__decoration-pulse {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 28px;
        height: 28px;
        background: var(--decoration-color-alpha, rgba(59, 130, 246, 0.2));
        border-radius: 50%;
        opacity: 0;
    }

    // 数据流动效果
    &__data-flow {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 2px;
        overflow: hidden;
    }

    &__data-flow-line {
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent 0%,
            var(--flow-color, rgba(59, 130, 246, 0.6)) 50%,
            transparent 100%
        );
    }

    &__data-flow-dot {
        position: absolute;
        top: 50%;
        right: 1rem;
        transform: translateY(-50%);
        width: 4px;
        height: 4px;
        background: var(--decoration-color, #3b82f6);
        border-radius: 50%;
        opacity: 0.6;
    }
}

// 动画定义
@keyframes dataFlow {
    0% {
        left: -100%;
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

@keyframes iconPulse {
    0%,
    100% {
        opacity: 0;
        transform: translate(-50%, -50%) scale(1);
    }

    50% {
        opacity: 0.6;
        transform: translate(-50%, -50%) scale(1.2);
    }
}

@keyframes decorationPulse {
    0%,
    100% {
        opacity: 0;
        transform: translate(-50%, -50%) scale(1);
    }

    33% {
        opacity: 0.2;
        transform: translate(-50%, -50%) scale(1.1);
    }

    66% {
        opacity: 0.3;
        transform: translate(-50%, -50%) scale(0.9);
    }
}

// 蓝白科技感颜色主题 - 统一使用蓝色系
.stats-card--blue {
    --card-gradient: #3b82f6, #1d4ed8;
    --icon-bg: rgba(59, 130, 246, 0.15);
    --icon-color: #3b82f6;
    --icon-color-alpha: rgba(59, 130, 246, 0.3);
    --icon-shadow: rgba(59, 130, 246, 0.4);
    --decoration-color: #3b82f6;
    --decoration-color-alpha: rgba(59, 130, 246, 0.2);
    --value-gradient: #3b82f6, #1e40af;
    --flow-color: rgba(59, 130, 246, 0.6);
}

.stats-card--orange {
    // 改为浅蓝色调
    --card-gradient: #0ea5e9, #0284c7;
    --icon-bg: rgba(14, 165, 233, 0.15);
    --icon-color: #0ea5e9;
    --icon-color-alpha: rgba(14, 165, 233, 0.3);
    --icon-shadow: rgba(14, 165, 233, 0.4);
    --decoration-color: #0ea5e9;
    --decoration-color-alpha: rgba(14, 165, 233, 0.2);
    --value-gradient: #0ea5e9, #0284c7;
    --flow-color: rgba(14, 165, 233, 0.6);
}

.stats-card--green {
    // 改为青蓝色调
    --card-gradient: #06b6d4, #0891b2;
    --icon-bg: rgba(6, 182, 212, 0.15);
    --icon-color: #06b6d4;
    --icon-color-alpha: rgba(6, 182, 212, 0.3);
    --icon-shadow: rgba(6, 182, 212, 0.4);
    --decoration-color: #06b6d4;
    --decoration-color-alpha: rgba(6, 182, 212, 0.2);
    --value-gradient: #06b6d4, #0891b2;
    --flow-color: rgba(6, 182, 212, 0.6);
}

.stats-card--purple {
    // 改为深蓝色调
    --card-gradient: #1e40af, #1e3a8a;
    --icon-bg: rgba(30, 64, 175, 0.15);
    --icon-color: #1e40af;
    --icon-color-alpha: rgba(30, 64, 175, 0.3);
    --icon-shadow: rgba(30, 64, 175, 0.4);
    --decoration-color: #1e40af;
    --decoration-color-alpha: rgba(30, 64, 175, 0.2);
    --value-gradient: #1e40af, #1e3a8a;
    --flow-color: rgba(30, 64, 175, 0.6);
}

.stats-card--red {
    // 改为中蓝色调
    --card-gradient: #2563eb, #1d4ed8;
    --icon-bg: rgba(37, 99, 235, 0.15);
    --icon-color: #2563eb;
    --icon-color-alpha: rgba(37, 99, 235, 0.3);
    --icon-shadow: rgba(37, 99, 235, 0.4);
    --decoration-color: #2563eb;
    --decoration-color-alpha: rgba(37, 99, 235, 0.2);
    --value-gradient: #2563eb, #1d4ed8;
    --flow-color: rgba(37, 99, 235, 0.6);
}

// 内容区域
.content-section {
    padding: 0 2rem 2rem;
    position: relative;
    z-index: 1;
}

// 批量操作工具栏
.bulk-operations-toolbar {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 16px;
    padding: 1rem 1.5rem;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(59, 130, 246, 0.15);
    backdrop-filter: blur(20px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.08);

    .toolbar-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;

        .selection-info {
            display: flex;
            align-items: center;
            gap: 0.75rem;

            .selection-text {
                font-weight: 500;
                color: #1e293b;
            }
        }

        .batch-actions {
            display: flex;
            gap: 0.75rem;

            .batch-btn {
                height: 40px;
                padding: 0 1.25rem;
                font-weight: 600;
                transition: all 0.3s ease;

                &.batch-restore-btn {
                    background: linear-gradient(135deg, #10b981, #059669);
                    color: white;

                    &:hover {
                        transform: translateY(-1px);
                        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
                    }
                }

                &.batch-delete-btn {
                    background: linear-gradient(135deg, #ef4444, #dc2626);
                    color: white;

                    &:hover {
                        transform: translateY(-1px);
                        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
                    }
                }
            }

            .clear-btn {
                color: #6b7280;

                &:hover {
                    background: rgba(107, 114, 128, 0.1);
                }
            }
        }
    }
}

// 空状态
.empty-state {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 400px;

    .empty-content {
        text-align: center;
        max-width: 400px;

        .empty-icon {
            position: relative;
            width: 120px;
            height: 120px;
            margin: 0 auto 2rem;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #94a3b8;
            font-size: 60px;

            .empty-icon-glow {
                position: absolute;
                top: 50%;
                left: 50%;
                width: 140px;
                height: 140px;
                background: radial-gradient(circle, rgba(148, 163, 184, 0.1) 0%, transparent 70%);
                border-radius: 50%;
                transform: translate(-50%, -50%);
                animation: emptyGlow 3s ease-in-out infinite;
            }
        }

        .empty-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 0.75rem;
        }

        .empty-description {
            font-size: 1rem;
            color: #64748b;
            line-height: 1.6;
            margin-bottom: 2rem;
        }

        .back-btn {
            background: linear-gradient(135deg, #3b82f6, #2563eb);
            color: white;
            height: 48px;
            padding: 0 2rem;
            font-weight: 600;
            transition: all 0.3s ease;

            &:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3);
            }
        }
    }
}

// 任务容器
.tasks-container {
    .tasks-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        padding: 1.5rem;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        border: 1px solid rgba(59, 130, 246, 0.1);
        backdrop-filter: blur(20px);

        .header-left {
            .tasks-title {
                font-size: 1.25rem;
                font-weight: 600;
                color: #1e293b;
                margin: 0 0 0.25rem 0;
            }

            .tasks-count {
                font-size: 0.875rem;
                color: #64748b;
            }
        }

        .clear-all-btn {
            color: #ef4444;
            border-color: #ef4444;
            height: 40px;
            padding: 0 1.25rem;
            font-weight: 500;

            &:hover {
                background: rgba(239, 68, 68, 0.1);
            }
        }
    }

    .tasks-grid {
        display: grid;
        gap: 1rem;

        .task-card {
            position: relative;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid rgba(226, 232, 240, 0.8);
            backdrop-filter: blur(20px);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            gap: 1rem;

            &:hover {
                transform: translateY(-2px);
                box-shadow:
                    0 8px 25px rgba(59, 130, 246, 0.08),
                    0 3px 10px rgba(14, 165, 233, 0.05);
                border-color: rgba(59, 130, 246, 0.2);
            }

            &.task-selected {
                border-color: #3b82f6;
                background: linear-gradient(
                    135deg,
                    rgba(59, 130, 246, 0.05) 0%,
                    rgba(255, 255, 255, 0.95) 100%
                );
                box-shadow: 0 4px 16px rgba(59, 130, 246, 0.12);
            }

            .task-checkbox {
                flex-shrink: 0;
                display: flex;
                align-items: flex-start;
                padding-top: 0.25rem;
            }

            .task-content {
                flex: 1;

                .task-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    margin-bottom: 0.75rem;

                    .task-title {
                        font-size: 1.125rem;
                        font-weight: 600;
                        color: #1e293b;
                        margin: 0;
                        line-height: 1.4;
                    }

                    .task-meta {
                        display: flex;
                        gap: 0.5rem;
                        flex-shrink: 0;
                        margin-left: 1rem;

                        .priority-badge,
                        .status-badge {
                            font-size: 0.75rem;
                            padding: 0.25rem 0.5rem;
                        }
                    }
                }

                .task-description {
                    color: #64748b;
                    line-height: 1.5;
                    margin-bottom: 0.75rem;
                    display: -webkit-box;
                    -webkit-line-clamp: 2;
                    line-clamp: 2;
                    -webkit-box-orient: vertical;
                    overflow: hidden;
                }

                .task-tags {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    margin-bottom: 1rem;
                    color: #6b7280;
                    font-size: 0.875rem;

                    .tags-icon {
                        font-size: 14px;
                    }
                }

                .task-delete-info {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 1rem;
                    padding-top: 0.75rem;
                    border-top: 1px solid rgba(226, 232, 240, 0.6);

                    .delete-time,
                    .remaining-days {
                        display: flex;
                        align-items: center;
                        gap: 0.5rem;
                        font-size: 0.75rem;

                        .time-icon,
                        .timer-icon {
                            font-size: 14px;
                        }
                    }

                    .delete-time {
                        color: #6b7280;
                    }

                    .remaining-days {
                        &.days-normal {
                            color: #10b981;
                        }
                        &.days-warning {
                            color: #f59e0b;
                        }
                        &.days-critical {
                            color: #ef4444;
                        }
                    }
                }
            }

            .task-actions {
                flex-shrink: 0;
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
                align-items: center;

                .action-btn {
                    width: 40px;
                    height: 40px;
                    transition: all 0.3s ease;

                    &.restore-btn {
                        background: linear-gradient(135deg, #10b981, #059669);
                        color: white;

                        &:hover {
                            transform: scale(1.1);
                            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
                        }
                    }

                    &.delete-btn {
                        background: linear-gradient(135deg, #ef4444, #dc2626);
                        color: white;

                        &:hover {
                            transform: scale(1.1);
                            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
                        }
                    }
                }
            }
        }
    }
}

// 分页器
.pagination-container {
    display: flex;
    justify-content: center;
    margin-top: 2rem;

    .custom-pagination {
        :deep(.q-pagination__content) {
            .q-btn {
                background: rgba(255, 255, 255, 0.95);
                border: 1px solid rgba(226, 232, 240, 0.8);
                color: #64748b;
                transition: all 0.3s ease;

                &:hover {
                    background: rgba(59, 130, 246, 0.1);
                    border-color: #3b82f6;
                    color: #3b82f6;
                }

                &.q-btn--flat.q-btn--rectangle.q-btn--actionable.q-focusable.q-hoverable.q-btn--active {
                    background: linear-gradient(135deg, #3b82f6, #2563eb);
                    color: white;
                    border-color: #3b82f6;
                }
            }
        }
    }
}

// 自定义加载状态
.custom-loading {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);

    .loading-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;

        .loading-spinner {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #3b82f6, #2563eb);
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .loading-text {
            font-size: 1rem;
            color: #64748b;
            font-weight: 500;
        }
    }
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
        transform: translateY(0px) rotate(0deg);
        opacity: 0.7;
    }
    50% {
        transform: translateY(-10px) rotate(180deg);
        opacity: 1;
    }
}

@keyframes pulse {
    0%,
    100% {
        transform: translate(-50%, -50%) scale(1);
        opacity: 0.7;
    }
    50% {
        transform: translate(-50%, -50%) scale(1.2);
        opacity: 0.9;
    }
}

@keyframes borderPulse {
    0%,
    100% {
        opacity: 0.6;
    }
    50% {
        opacity: 1;
    }
}

@keyframes particleFlow {
    0% {
        opacity: 0;
        transform: translateX(-10px) scale(0.5);
    }
    10% {
        opacity: 1;
        transform: translateX(0px) scale(1);
    }
    90% {
        opacity: 1;
        transform: translateX(30px) scale(1);
    }
    100% {
        opacity: 0;
        transform: translateX(40px) scale(0.5);
    }
}

@keyframes scanLine {
    0% {
        left: -100px;
        opacity: 0;
    }
    10% {
        opacity: 1;
    }
    90% {
        opacity: 1;
    }
    100% {
        left: calc(100% + 100px);
        opacity: 0;
    }
}

@keyframes statGlow {
    0%,
    100% {
        opacity: 0.05;
        transform: rotate(0deg);
    }
    50% {
        opacity: 0.1;
        transform: rotate(180deg);
    }
}

@keyframes emptyGlow {
    0%,
    100% {
        opacity: 0.1;
        transform: translate(-50%, -50%) scale(1);
    }
    50% {
        opacity: 0.2;
        transform: translate(-50%, -50%) scale(1.1);
    }
}

// 响应式设计
@media (max-width: 768px) {
    .page-header {
        padding: 1.5rem;
        margin-bottom: 1.5rem;

        .header-content {
            flex-direction: column;
            gap: 1.5rem;

            .title-section .title-container {
                gap: 1rem;

                .icon-wrapper {
                    width: 48px;
                    height: 48px;
                }

                .title-text .page-title {
                    font-size: 1.75rem;

                    .title-accent {
                        font-size: 1.25rem;
                    }
                }
            }

            .action-section {
                width: 100%;

                .action-buttons {
                    justify-content: space-between;
                    width: 100%;

                    .refresh-btn {
                        flex: 1;
                        max-width: 200px;
                    }
                }
            }
        }
    }

    .stats-section {
        padding: 0 1rem 1.5rem;

        .stats-grid {
            grid-template-columns: repeat(2, 1fr); // 平板端显示2列
            gap: 0.75rem;
        }
    }

    // 针对 stats-card 的移动端优化 - 基于新的紧凑尺寸
    .stats-card {
        height: 90px; // 移动端进一步降低高度

        &__content {
            padding: 0.75rem;
            gap: 0.5rem;
        }

        &__icon-container {
            width: 36px;
            height: 36px;
        }

        &__icon-bg {
            width: 36px;
            height: 36px;
            border-radius: 10px;
        }

        &__icon {
            font-size: 18px;
        }

        &__icon-pulse {
            width: 36px;
            height: 36px;
            border-radius: 10px;
        }

        &__label {
            font-size: 0.675rem;
        }

        &__value {
            font-size: 1.5rem;
        }

        &__metric {
            font-size: 0.575rem;
        }

        &__decoration {
            width: 24px;
            height: 24px;
        }

        &__decoration-bg,
        &__decoration-pulse {
            width: 24px;
            height: 24px;
        }
    }

    .content-section {
        padding: 0 1rem 1.5rem;
    }

    .bulk-operations-toolbar .toolbar-content {
        flex-direction: column;
        gap: 1rem;

        .batch-actions {
            width: 100%;
            justify-content: space-between;
        }
    }

    .tasks-container .tasks-header {
        flex-direction: column;
        gap: 1rem;
        align-items: stretch;
    }

    .task-card {
        flex-direction: column;
        gap: 1rem;

        .task-actions {
            flex-direction: row;
            justify-content: center;
        }

        .task-delete-info {
            grid-template-columns: 1fr;
            gap: 0.5rem;
        }
    }
}

@media (max-width: 480px) {
    .page-header {
        padding: 1rem;

        .title-text .page-title {
            font-size: 1.5rem;
            flex-direction: column;
            align-items: flex-start;

            .title-accent {
                font-size: 1.125rem;
            }
        }
    }

    .stats-section,
    .content-section {
        padding: 0 0.75rem 1rem;
    }

    .stats-grid {
        grid-template-columns: 1fr; // 超小屏幕单列显示
        gap: 0.5rem;
    }

    // 超小屏幕的 stats-card 优化 - 基于新的紧凑尺寸
    .stats-card {
        height: 80px;

        &__content {
            padding: 0.625rem;
            gap: 0.375rem;
        }

        &__icon-container {
            width: 32px;
            height: 32px;
        }

        &__icon-bg {
            width: 32px;
            height: 32px;
            border-radius: 8px;
        }

        &__icon {
            font-size: 16px;
        }

        &__icon-pulse {
            width: 32px;
            height: 32px;
            border-radius: 8px;
        }

        &__label {
            font-size: 0.625rem;
        }

        &__value {
            font-size: 1.25rem;
        }

        &__metric {
            font-size: 0.5rem;
        }

        &__decoration {
            width: 20px;
            height: 20px;
        }

        &__decoration-bg,
        &__decoration-pulse {
            width: 20px;
            height: 20px;
        }
    }

    .task-card {
        padding: 1rem;
    }
}
</style>

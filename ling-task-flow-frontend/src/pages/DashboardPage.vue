<template>
    <q-page class="dashboard-page">
        <!-- 页面标题 -->
        <div class="page-header q-pa-lg">
            <div class="row items-center justify-between">
                <div>
                    <h4 class="text-h4 q-ma-none text-white">统计仪表板</h4>
                    <p class="text-subtitle1 q-ma-none text-white-7">
                        {{ formatDate(new Date()) }} • 数据概览
                    </p>
                </div>
                <q-btn
                    icon="refresh"
                    label="刷新数据"
                    flat
                    color="white"
                    @click="refreshData"
                    :loading="loading"
                />
            </div>
        </div>

        <!-- 统计卡片网格 -->
        <div class="stats-grid q-pa-lg">
            <div class="row q-gutter-lg">
                <!-- 总任务数 -->
                <div class="col-12 col-sm-6 col-md-3">
                    <StatsCard
                        icon="assignment"
                        title="总任务数"
                        :value="taskStats?.total_tasks || 0"
                        color="blue"
                        :trend="getTrend('total')"
                        @click="goToTasks()"
                    />
                </div>

                <!-- 活跃任务 -->
                <div class="col-12 col-sm-6 col-md-3">
                    <StatsCard
                        icon="schedule"
                        title="活跃任务"
                        :value="taskStats?.active_tasks || 0"
                        color="orange"
                        :trend="getTrend('active')"
                        @click="() => goToTasks({ status: 'IN_PROGRESS' })"
                    />
                </div>

                <!-- 已完成任务 -->
                <div class="col-12 col-sm-6 col-md-3">
                    <StatsCard
                        icon="done_all"
                        title="已完成"
                        :value="taskStats?.completed_tasks || 0"
                        color="green"
                        :trend="getTrend('completed')"
                        @click="goToTasks({ status: 'COMPLETED' })"
                    />
                </div>

                <!-- 完成率 -->
                <div class="col-12 col-sm-6 col-md-3">
                    <StatsCard
                        icon="trending_up"
                        title="完成率"
                        :value="`${taskStats?.completion_rate || 0}%`"
                        color="purple"
                        :trend="getTrend('completion_rate')"
                        @click="goToTasks()"
                    />
                </div>
            </div>
        </div>

        <!-- 图表和详细信息 -->
        <div class="charts-section q-pa-lg">
            <div class="row q-gutter-lg">
                <!-- 状态分布图表 -->
                <div class="col-12 col-md-6">
                    <q-card class="stats-chart-card">
                        <q-card-section>
                            <div class="text-h6 q-mb-md">任务状态分布</div>
                            <StatusDistributionChart
                                :data="statusChartData"
                                @status-click="handleStatusClick"
                            />
                        </q-card-section>
                    </q-card>
                </div>

                <!-- 优先级分布图表 -->
                <div class="col-12 col-md-6">
                    <q-card class="stats-chart-card">
                        <q-card-section>
                            <div class="text-h6 q-mb-md">优先级分布</div>
                            <PriorityDistributionChart
                                :data="priorityChartData"
                                @priority-click="handlePriorityClick"
                            />
                        </q-card-section>
                    </q-card>
                </div>
            </div>
        </div>

        <!-- 最近活动和快速操作 -->
        <div class="activity-section q-pa-lg">
            <div class="row q-gutter-lg">
                <!-- 最近活动 -->
                <div class="col-12 col-md-8">
                    <q-card class="activity-card">
                        <q-card-section>
                            <div class="text-h6 q-mb-md">最近活动</div>
                            <RecentActivityList :activities="recentActivities" />
                        </q-card-section>
                    </q-card>
                </div>

                <!-- 快速操作 -->
                <div class="col-12 col-md-4">
                    <q-card class="quick-actions-card">
                        <q-card-section>
                            <div class="text-h6 q-mb-md">快速操作</div>
                            <div class="quick-actions">
                                <q-btn
                                    unelevated
                                    color="primary"
                                    icon="add"
                                    label="新建任务"
                                    class="full-width q-mb-sm"
                                    @click="createNewTask"
                                />
                                <q-btn
                                    unelevated
                                    color="secondary"
                                    icon="search"
                                    label="搜索任务"
                                    class="full-width q-mb-sm"
                                    @click="() => goToTasks()"
                                />
                                <q-btn
                                    unelevated
                                    color="orange"
                                    icon="schedule"
                                    label="查看逾期"
                                    class="full-width q-mb-sm"
                                    @click="goToTasks({ is_overdue: true })"
                                />
                                <q-btn
                                    unelevated
                                    color="negative"
                                    icon="delete"
                                    label="回收站"
                                    class="full-width"
                                    @click="goToTrash"
                                />
                            </div>
                        </q-card-section>
                    </q-card>
                </div>
            </div>
        </div>

        <!-- 加载状态 -->
        <q-inner-loading :showing="loading" color="primary" />
    </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useTaskStore } from 'src/stores/task';
import type { TaskStats, TaskSearchParams, TaskStatus, TaskPriority } from 'src/types';
import StatsCard from '../components/dashboard/StatsCard.vue';
import StatusDistributionChart from '../components/dashboard/StatusDistributionChart.vue';
import PriorityDistributionChart from '../components/dashboard/PriorityDistributionChart.vue';
import RecentActivityList from '../components/dashboard/RecentActivityList.vue';
import { Notify } from 'quasar';

const router = useRouter();
const taskStore = useTaskStore();

// 响应式状态
const loading = ref(false);
const taskStats = ref<TaskStats | null>(null);

// 计算属性
const statusChartData = computed(() => {
    if (!taskStats.value?.status_distribution) return [];

    return Object.entries(taskStats.value.status_distribution).map(([status, count]) => ({
        status,
        count,
        label: getStatusLabel(status),
        color: getStatusColor(status),
    }));
});

const priorityChartData = computed(() => {
    if (!taskStats.value?.priority_distribution) return [];

    return Object.entries(taskStats.value.priority_distribution).map(([priority, count]) => ({
        priority,
        count,
        label: getPriorityLabel(priority),
        color: getPriorityColor(priority),
    }));
});

const recentActivities = computed(() => {
    return taskStats.value?.recent_activity || [];
});

// 初始化
onMounted(async () => {
    await loadData();
});

// 方法
const loadData = async () => {
    loading.value = true;
    try {
        const stats = await taskStore.fetchTaskStats();
        taskStats.value = stats;
    } catch (error) {
        console.error('加载统计数据失败:', error);
        Notify.create({
            type: 'negative',
            message: '加载统计数据失败，请稍后重试',
            position: 'top',
        });
    } finally {
        loading.value = false;
    }
};

const refreshData = async () => {
    await loadData();
    Notify.create({
        type: 'positive',
        message: '数据已刷新',
        position: 'top',
    });
};

const formatDate = (date: Date) => {
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long',
    });
};

// 趋势计算（简化实现，实际应该从后端获取）
const getTrend = (type: string) => {
    // 这里应该从后端获取趋势数据，暂时返回模拟数据
    const trends = {
        total: { value: 12, direction: 'up' as const },
        active: { value: 8, direction: 'up' as const },
        completed: { value: 15, direction: 'up' as const },
        completion_rate: { value: 5, direction: 'up' as const },
    };
    return trends[type as keyof typeof trends] || { value: 0, direction: 'neutral' as const };
};

// 状态相关辅助方法
const getStatusLabel = (status: string) => {
    const labels = {
        PENDING: '待处理',
        IN_PROGRESS: '进行中',
        COMPLETED: '已完成',
        CANCELLED: '已取消',
        ON_HOLD: '暂停',
    };
    return labels[status as keyof typeof labels] || status;
};

const getStatusColor = (status: string) => {
    const colors = {
        PENDING: '#ff9800',
        IN_PROGRESS: '#2196f3',
        COMPLETED: '#4caf50',
        CANCELLED: '#f44336',
        ON_HOLD: '#9c27b0',
    };
    return colors[status as keyof typeof colors] || '#757575';
};

// 优先级相关辅助方法
const getPriorityLabel = (priority: string) => {
    const labels = {
        LOW: '低',
        MEDIUM: '中',
        HIGH: '高',
        URGENT: '紧急',
    };
    return labels[priority as keyof typeof labels] || priority;
};

const getPriorityColor = (priority: string) => {
    const colors = {
        LOW: '#4caf50',
        MEDIUM: '#ff9800',
        HIGH: '#f44336',
        URGENT: '#e91e63',
    };
    return colors[priority as keyof typeof colors] || '#757575';
};

// 导航方法
const goToTasks = async (params?: TaskSearchParams) => {
    if (params) {
        taskStore.setSearchParams(params);
    }
    await router.push('/tasks');
};

const handleStatusClick = async (status: string) => {
    await goToTasks({ status: status as TaskStatus });
};

const handlePriorityClick = async (priority: string) => {
    await goToTasks({ priority: priority as TaskPriority });
};

const goToTrash = async () => {
    await router.push('/trash');
};

const createNewTask = async () => {
    // 触发新建任务操作，通过事件总线或直接调用任务列表页面的方法
    await router.push('/tasks');
    // TODO: 在任务页面实现新建任务对话框的打开
};
</script>

<style lang="scss" scoped>
.dashboard-page {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

.page-header {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.stats-grid {
    .col-12,
    .col-sm-6,
    .col-md-3 {
        min-height: 140px;
    }
}

.stats-chart-card,
.activity-card,
.quick-actions-card {
    height: 400px;
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.2);
    transition: all 0.3s ease;

    &:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
}

.quick-actions {
    .q-btn {
        border-radius: 12px;
        font-weight: 500;
        transition: all 0.3s ease;

        &:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        }
    }
}

// 响应式设计
@media (max-width: 768px) {
    .page-header {
        padding: 1rem !important;
    }

    .stats-grid,
    .charts-section,
    .activity-section {
        padding: 1rem !important;
    }

    .stats-chart-card,
    .activity-card,
    .quick-actions-card {
        height: auto;
        min-height: 300px;
    }
}
</style>

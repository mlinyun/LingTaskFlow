<template>
    <q-page class="dashboard-page">
        <!-- 页面标题 -->
        <div class="page-header q-pa-lg">
            <div class="row items-center justify-between">
                <div>
                    <h4 class="text-h4 q-ma-none text-blue-9">统计仪表板</h4>
                    <p class="text-subtitle1 q-ma-none text-blue-7">
                        {{ formatDate(new Date()) }} • 数据概览
                    </p>
                </div>
                <q-btn
                    icon="refresh"
                    label="刷新数据"
                    flat
                    color="blue"
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
                            <div class="chart-title-section">
                                <q-icon name="pie_chart" size="24px" class="chart-title-icon" />
                                <div class="text-h6 chart-title">任务状态分布</div>
                                <div class="chart-subtitle">实时状态统计分析</div>
                            </div>
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
                            <div class="chart-title-section">
                                <q-icon name="bar_chart" size="24px" class="chart-title-icon" />
                                <div class="text-h6 chart-title">优先级分布</div>
                                <div class="chart-subtitle">任务优先级分析</div>
                            </div>
                            <PriorityDistributionChart
                                :data="priorityChartData"
                                @priority-click="handlePriorityClick"
                            />
                        </q-card-section>
                    </q-card>
                </div>
            </div>
        </div>

        <!-- 最近活动 -->
        <div class="activity-section q-pa-lg">
            <div class="row q-gutter-lg">
                <!-- 最近活动 -->
                <div class="col-12">
                    <q-card class="activity-card">
                        <q-card-section>
                            <div class="chart-title-section">
                                <q-icon name="timeline" size="24px" class="chart-title-icon" />
                                <div class="text-h6 chart-title">最近活动</div>
                                <div class="chart-subtitle">实时动态追踪</div>
                            </div>
                            <RecentActivityList :activities="recentActivities" />
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
    // 蓝白科技感配色 - 统一使用蓝色系
    const colors = {
        PENDING: '#0ea5e9', // 天空蓝 - 待处理
        IN_PROGRESS: '#3b82f6', // 皇家蓝 - 进行中
        COMPLETED: '#06b6d4', // 青蓝色 - 已完成
        CANCELLED: '#64748b', // 石板蓝 - 已取消
        ON_HOLD: '#1e40af', // 深海蓝 - 暂停
    };
    return colors[status as keyof typeof colors] || '#94a3b8';
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
    // 蓝白科技感配色 - 按优先级使用不同深度的蓝色
    const colors = {
        LOW: '#06b6d4', // 青蓝色 - 低优先级
        MEDIUM: '#0ea5e9', // 天空蓝 - 中优先级
        HIGH: '#3b82f6', // 皇家蓝 - 高优先级
        URGENT: '#1e40af', // 深海蓝 - 紧急
    };
    return colors[priority as keyof typeof colors] || '#94a3b8';
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
</script>

<style lang="scss" scoped>
.dashboard-page {
    // 修改为白色背景，与其他页面保持一致
    background: #ffffff;
    min-height: calc(100vh - 50px);
    position: relative;

    // 添加科技感网格纹理 - 调整为蓝色系
    &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image:
            linear-gradient(rgba(59, 130, 246, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(59, 130, 246, 0.02) 1px, transparent 1px);
        background-size: 40px 40px;
        pointer-events: none;
    }
}

.page-header {
    background: rgba(59, 130, 246, 0.05);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(59, 130, 246, 0.1);
    box-shadow: 0 2px 20px rgba(59, 130, 246, 0.05);

    // 科技感发光效果
    &::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(
            90deg,
            transparent 0%,
            rgba(59, 130, 246, 0.6) 50%,
            transparent 100%
        );
    }
}

.stats-grid {
    .col-12,
    .col-sm-6,
    .col-md-3 {
        min-height: 140px;
    }
}

.stats-chart-card,
.activity-card {
    height: 400px;
    border-radius: 20px;
    // 蓝白科技感卡片样式
    background: rgba(255, 255, 255, 0.98);
    border: 1px solid rgba(59, 130, 246, 0.1);
    box-shadow:
        0 8px 32px rgba(14, 165, 233, 0.08),
        0 2px 8px rgba(59, 130, 246, 0.05),
        inset 0 1px 0 rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(20px);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;

    // 科技感边框发光
    &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: 20px;
        padding: 1px;
        background: linear-gradient(
            135deg,
            rgba(59, 130, 246, 0.2) 0%,
            rgba(14, 165, 233, 0.1) 50%,
            rgba(2, 132, 199, 0.2) 100%
        );
        mask:
            linear-gradient(#fff 0 0) content-box,
            linear-gradient(#fff 0 0);
        mask-composite: exclude;
        pointer-events: none;
    }

    &:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow:
            0 20px 60px rgba(14, 165, 233, 0.15),
            0 8px 24px rgba(59, 130, 246, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);
        border-color: rgba(59, 130, 246, 0.2);

        &::before {
            background: linear-gradient(
                135deg,
                rgba(59, 130, 246, 0.4) 0%,
                rgba(14, 165, 233, 0.3) 50%,
                rgba(2, 132, 199, 0.4) 100%
            );
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
    .activity-card {
        height: auto;
        min-height: 300px;
        border-radius: 16px;

        &:hover {
            transform: translateY(-3px) scale(1.01);
        }
    }
}

// 科技感动画效果
@keyframes techGlow {
    0%,
    100% {
        box-shadow:
            0 8px 32px rgba(14, 165, 233, 0.08),
            0 2px 8px rgba(59, 130, 246, 0.05);
    }
    50% {
        box-shadow:
            0 8px 32px rgba(14, 165, 233, 0.12),
            0 2px 8px rgba(59, 130, 246, 0.08);
    }
}

// 为重要卡片添加轻微的脉冲效果
.stats-chart-card:nth-child(odd) {
    animation: techGlow 6s ease-in-out infinite;
}

// 图表标题样式
.chart-title-section {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(59, 130, 246, 0.1);
    position: relative;

    // 科技感底部装饰线
    &::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        width: 60px;
        height: 2px;
        background: linear-gradient(90deg, #3b82f6, transparent);
        border-radius: 1px;
    }
}

.chart-title-icon {
    color: #3b82f6;
    background: rgba(59, 130, 246, 0.1);
    padding: 8px;
    border-radius: 8px;
}

.chart-title {
    color: #1e40af;
    font-weight: 600;
    margin: 0;
    flex: 1;
}

.chart-subtitle {
    font-size: 12px;
    color: #64748b;
    margin-left: auto;
    padding: 4px 12px;
    background: rgba(14, 165, 233, 0.05);
    border-radius: 20px;
    border: 1px solid rgba(14, 165, 233, 0.1);
}
</style>

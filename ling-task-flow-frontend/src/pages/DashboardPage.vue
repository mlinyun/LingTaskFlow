<template>
    <q-page class="dashboard-page">
        <!-- 页面头部 - 使用公共组件 -->
        <PageHeader
            :primary-action="{
                icon: 'refresh',
                label: '刷新数据',
                loading: loading,
            }"
            :secondary-actions="[
                { name: 'settings', icon: 'settings', tooltip: '设置', class: 'fullscreen-btn' },
                { name: 'fullscreen', icon: 'fullscreen', tooltip: '全屏', class: 'download-btn' },
            ]"
            icon="analytics"
            subtitle="实时数据监控与智能分析"
            title-accent="仪表盘"
            title-primary="数据概览"
            @primary-action="refreshData"
            @secondary-action="handleSecondaryAction"
        />

        <!-- 主要内容区域 -->
        <div class="content-container">
            <!-- 加载状态 - 使用仪表板骨架屏 -->
            <DashboardSkeleton v-if="taskStore.loadingStates.fetchingStats || loading" />

            <!-- 一般加载状态 -->
            <LoadingState
                v-else-if="taskStore.loading"
                color="primary"
                message="加载仪表板数据..."
                spinner="gears"
                variant="centered"
            />

            <!-- 仪表板内容 -->
            <div v-else class="content-grid">
                <!-- 左侧：关键指标卡片 -->
                <div class="metrics-panel">
                    <div class="panel-header">
                        <h3>关键指标</h3>
                        <q-chip color="positive" icon="trending_up" size="sm" text-color="white">
                            实时更新
                        </q-chip>
                    </div>

                    <div class="metrics-grid">
                        <!-- 主要指标卡片 -->
                        <div class="metric-card primary">
                            <StatsCard
                                :trend="getTrend('total')"
                                :value="taskStats?.basic_stats?.total_tasks || 0"
                                color="blue"
                                icon="assignment"
                                title="总任务数"
                                @click="goToTasks()"
                            />
                        </div>

                        <div class="metric-card primary">
                            <StatsCard
                                :trend="getTrend('completed')"
                                :value="taskStats?.basic_stats?.completed_tasks || 0"
                                color="green"
                                icon="done_all"
                                title="已完成"
                                @click="goToTasks({ status: 'COMPLETED' })"
                            />
                        </div>

                        <div class="metric-card primary">
                            <StatsCard
                                :trend="getTrend('active')"
                                :value="taskStats?.workload_stats?.total_active_tasks || 0"
                                color="orange"
                                icon="schedule"
                                title="进行中"
                                @click="goToTasks({ status: 'IN_PROGRESS' })"
                            />
                        </div>

                        <div class="metric-card primary">
                            <StatsCard
                                :trend="getTrend('completion_rate')"
                                :value="`${taskStats?.basic_stats?.completion_rate?.toFixed(1) || 0}%`"
                                color="purple"
                                icon="trending_up"
                                title="完成率"
                                @click="goToTasks()"
                            />
                        </div>

                        <!-- 次要指标卡片 -->
                        <div class="metric-card secondary">
                            <StatsCard
                                :trend="getTrend('overdue')"
                                :value="taskStats?.overdue_analysis?.total_overdue || 0"
                                color="red"
                                icon="schedule_send"
                                title="逾期任务"
                                @click="goToTasks()"
                            />
                        </div>

                        <div class="metric-card secondary">
                            <StatsCard
                                :trend="getTrend('progress')"
                                :value="`${taskStats?.basic_stats?.average_progress?.toFixed(1) || 0}%`"
                                color="blue"
                                icon="timeline"
                                title="平均进度"
                                @click="goToTasks()"
                            />
                        </div>
                    </div>
                </div>

                <!-- 右侧：图表和分析 -->
                <div class="analytics-panel">
                    <!-- 状态分布图表 -->
                    <div class="chart-card">
                        <div class="chart-header">
                            <div class="chart-title">
                                <q-icon name="pie_chart" size="20px" />
                                <span>任务状态分布</span>
                            </div>
                            <q-btn flat icon="more_vert" round size="sm" />
                        </div>
                        <div class="chart-content">
                            <StatusDistributionChart
                                :data="statusChartData"
                                @status-click="handleStatusClick"
                            />
                        </div>
                    </div>

                    <!-- 优先级分布图表 -->
                    <div class="chart-card">
                        <div class="chart-header">
                            <div class="chart-title">
                                <q-icon name="bar_chart" size="20px" />
                                <span>优先级分布</span>
                            </div>
                            <q-btn flat icon="more_vert" round size="sm" />
                        </div>
                        <div class="chart-content">
                            <PriorityDistributionChart
                                :data="priorityChartData"
                                @priority-click="handlePriorityClick"
                            />
                        </div>
                    </div>
                </div>

                <!-- 底部：详细信息面板 -->
                <div class="details-section">
                    <div class="details-grid">
                        <!-- 标签统计 -->
                        <StatisticCard
                            :items="categoryStatItems"
                            icon="category"
                            no-data-text="暂无标签数据"
                            title="标签统计"
                            type="category"
                            @item-click="handleCategoryClick"
                        />

                        <!-- 进度分析 -->
                        <StatisticCard
                            :items="progressStatItems"
                            icon="analytics"
                            no-data-text="暂无进度数据"
                            title="进度分析"
                            type="progress"
                            @item-click="handleProgressClick"
                        />
                    </div>
                </div>
            </div>
            <!-- 关闭 content-grid -->
        </div>
        <!-- 关闭 content-container -->

        <!-- 加载状态 -->
        <q-inner-loading :showing="loading" color="primary" />
    </q-page>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useTaskStore } from 'src/stores/task';
import type { TaskPriority, TaskSearchParams, TaskStats, TaskStatus } from 'src/types';
import PageHeader from '../components/common/PageHeader.vue';
import StatsCard from '../components/dashboard/StatsCard.vue';
import StatusDistributionChart from '../components/dashboard/StatusDistributionChart.vue';
import PriorityDistributionChart from '../components/dashboard/PriorityDistributionChart.vue';
import StatisticCard from '../components/dashboard/StatisticCard.vue';
import DashboardSkeleton from '../components/skeletons/DashboardSkeleton.vue';
import LoadingState from '../components/skeletons/LoadingState.vue';
import { Notify } from 'quasar';

const router = useRouter();
const taskStore = useTaskStore();

// 响应式状态
const loading = ref(false);
const taskStats = ref<TaskStats | null>(null);

// 计算属性
const statusChartData = computed(() => {
    if (!taskStats.value?.status_distribution) return [];

    return Object.entries(taskStats.value.status_distribution).map(([status, data]) => ({
        status,
        count: data.count,
        label: data.name,
        color: getStatusColor(status),
    }));
});

const priorityChartData = computed(() => {
    if (!taskStats.value?.priority_distribution) return [];

    return Object.entries(taskStats.value.priority_distribution).map(([priority, data]) => ({
        priority,
        count: data.count,
        label: data.name,
        color: getPriorityColor(priority),
    }));
});

// 标签统计数据转换
const categoryStatItems = computed(() => {
    if (!taskStats.value?.category_stats) return [];

    return taskStats.value.category_stats.map(item => ({
        key: item.category,
        label: item.category,
        count: item.count,
        percentage: item.percentage,
        category: item.category,
    }));
});

// 进度分析数据转换
const progressStatItems = computed(() => {
    if (!taskStats.value?.progress_analysis?.distribution) return [];

    return taskStats.value.progress_analysis.distribution.map(item => ({
        key: item.range,
        label: item.label,
        count: item.count,
        percentage: item.percentage,
        range: item.range,
    }));
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

// 趋势计算（简化实现，实际应该从后端获取）
const getTrend = (type: string) => {
    // 这里应该从后端获取趋势数据，暂时返回模拟数据
    const trends = {
        total: { value: 12, direction: 'up' as const },
        active: { value: 8, direction: 'up' as const },
        completed: { value: 15, direction: 'up' as const },
        completion_rate: { value: 5, direction: 'up' as const },
        overdue: { value: -2, direction: 'down' as const },
        progress: { value: 10, direction: 'up' as const },
        estimated_hours: { value: 5, direction: 'up' as const },
        efficiency: { value: 8, direction: 'up' as const },
    };
    return trends[type as keyof typeof trends] || { value: 0, direction: 'neutral' as const };
};

// 状态相关辅助方法
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

// 进度颜色辅助方法
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

// 统计项接口定义（与 StatisticCard 组件一致）
interface StatisticItem {
    key: string;
    label: string;
    count: number;
    percentage: number;
    range?: string;
    category?: string;
}

// 标签点击事件处理
const handleCategoryClick = (item: StatisticItem) => {
    // 可以根据标签导航到任务列表，这里暂时显示通知
    Notify.create({
        type: 'info',
        message: `点击了标签：${item.label} (${item.count}个任务)`,
        position: 'top',
    });
    // 未来可以添加：await goToTasks({ category: item.category });
};

// 进度点击事件处理
const handleProgressClick = (item: StatisticItem) => {
    // 可以根据进度范围导航到任务列表，这里暂时显示通知
    Notify.create({
        type: 'info',
        message: `点击了进度范围：${item.label} (${item.count}个任务)`,
        position: 'top',
    });
    // 未来可以添加：await goToTasks({ progressRange: item.range });
};

// 处理头部次要操作
const handleSecondaryAction = (actionName: string) => {
    switch (actionName) {
        case 'settings':
            Notify.create({
                type: 'info',
                message: '设置功能开发中...',
                position: 'top',
            });
            break;
        case 'fullscreen':
            Notify.create({
                type: 'info',
                message: '全屏功能开发中...',
                position: 'top',
            });
            break;
        default:
            console.log(`未知操作: ${actionName}`);
    }
};
</script>

<style lang="scss" scoped>
.dashboard-page {
    background: #f8fafc;
    min-height: calc(100vh - 50px);
    padding: 1.5rem;

    @media (max-width: 768px) {
        padding: 1rem;
    }
}

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

// 新增装饰线动画
@keyframes borderPulse {
    0%,
    100% {
        opacity: 0.6;
        box-shadow:
            0 0 8px rgba(14, 165, 233, 0.4),
            0 0 16px rgba(59, 130, 246, 0.2);
    }
    50% {
        opacity: 1;
        box-shadow:
            0 0 12px rgba(14, 165, 233, 0.6),
            0 0 24px rgba(59, 130, 246, 0.4);
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

// 主要内容网格
.content-grid {
    display: grid;
    grid-template-columns: 400px 1fr;
    gap: 2rem;
    margin-bottom: 2rem;

    @media (max-width: 1200px) {
        grid-template-columns: 350px 1fr;
        gap: 1.5rem;
    }

    @media (max-width: 1024px) {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }
}

// 指标面板
.metrics-panel {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow:
        0 4px 20px rgba(0, 0, 0, 0.04),
        0 1px 3px rgba(0, 0, 0, 0.02);
    border: 1px solid rgba(226, 232, 240, 0.8);
    height: fit-content;
    transition: all 0.3s ease;

    &:hover {
        transform: translateY(-2px);
        box-shadow:
            0 8px 25px rgba(0, 0, 0, 0.08),
            0 3px 10px rgba(0, 0, 0, 0.04);
    }

    .panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e2e8f0;

        h3 {
            margin: 0;
            font-size: 1.125rem;
            font-weight: 600;
            color: #1e293b;
        }
    }

    .metrics-grid {
        display: grid;
        gap: 1rem;
    }
}

// 分析面板
.analytics-panel {
    display: grid;
    grid-template-rows: 1fr 1fr;
    gap: 1.5rem;

    .chart-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow:
            0 4px 20px rgba(0, 0, 0, 0.04),
            0 1px 3px rgba(0, 0, 0, 0.02);
        border: 1px solid rgba(226, 232, 240, 0.8);
        transition: all 0.3s ease;
        min-height: 380px;
        display: flex;
        flex-direction: column;

        &:hover {
            transform: translateY(-2px);
            box-shadow:
                0 8px 25px rgba(0, 0, 0, 0.08),
                0 3px 10px rgba(0, 0, 0, 0.04);
        }

        .chart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid #e2e8f0;

            .chart-title {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                font-size: 1rem;
                font-weight: 600;
                color: #1e293b;

                .q-icon {
                    color: #3b82f6;
                }
            }
        }

        .chart-content {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 10px;
            min-height: 300px;
        }
    }
}

// 详细信息区域
.details-section {
    .details-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
    }
}

// 动画定义
@keyframes pulse {
    0%,
    100% {
        opacity: 0.4;
        transform: translate(-50%, -50%) scale(1);
    }
    50% {
        opacity: 0.8;
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

            .title-section {
                .title-container {
                    gap: 1rem;

                    .icon-wrapper {
                        width: 48px;
                        height: 48px;
                    }

                    .title-text {
                        .page-title {
                            font-size: 1.75rem;

                            .title-accent {
                                font-size: 1.25rem;
                            }
                        }

                        .page-subtitle {
                            font-size: 0.9rem;
                        }
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

    .content-grid {
        gap: 1rem;
    }

    .metrics-panel,
    .analytics-panel .chart-card,
    .details-section .detail-card {
        padding: 1rem;
    }

    .analytics-panel .chart-card {
        min-height: 320px;

        .chart-content {
            min-height: 240px;
        }
    }

    .details-section .details-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
}

@media (max-width: 480px) {
    .dashboard-page {
        padding: 0.75rem;
    }

    .page-header {
        padding: 1rem;

        .header-content {
            .title-section {
                .title-container {
                    flex-direction: column;
                    text-align: center;
                    gap: 1rem;

                    .title-text {
                        .page-title {
                            font-size: 1.5rem;
                            justify-content: center;

                            .title-accent {
                                font-size: 1.125rem;
                            }
                        }
                    }
                }
            }

            .action-section {
                .action-buttons {
                    flex-direction: column;
                    gap: 0.75rem;

                    .refresh-btn {
                        max-width: none;
                        width: 100%;
                    }

                    .fullscreen-btn,
                    .download-btn {
                        width: 100%;
                        height: 40px;
                    }
                }
            }
        }
    }

    .content-grid {
        gap: 0.75rem;
        margin-bottom: 1rem;
    }
}
</style>

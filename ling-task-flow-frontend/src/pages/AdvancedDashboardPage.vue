<template>
    <q-page class="advanced-dashboard-page q-pa-lg">
        <!-- 页面标题和控制面板 -->
        <div class="page-header q-mb-lg">
            <div class="row items-center justify-between">
                <div class="col-auto">
                    <h4 class="page-title q-ma-none">
                        <q-icon name="analytics" size="32px" class="q-mr-sm" />
                        高级数据分析中心
                    </h4>
                    <p class="page-subtitle q-ma-none q-mt-sm">
                        {{ formatDate(new Date()) }} • 多维度数据洞察
                    </p>
                </div>
                <div class="col-auto">
                    <q-btn
                        @click="refreshAllData"
                        icon="refresh"
                        label="刷新全部数据"
                        color="primary"
                        unelevated
                        :loading="loading"
                        class="refresh-btn"
                    />
                </div>
            </div>
        </div>

        <!-- 分析参数控制面板 -->
        <div class="analysis-controls q-mb-lg">
            <q-expansion-item
                icon="settings"
                label="分析参数设置"
                default-opened
                class="controls-expansion"
            >
                <q-card flat>
                    <q-card-section class="q-pt-none">
                        <div class="row q-gutter-md items-center">
                            <div class="col-12 col-sm-6 col-md-3">
                                <q-select
                                    v-model="analysisParams.period"
                                    :options="periodOptions"
                                    label="统计周期"
                                    outlined
                                    dense
                                    emit-value
                                    map-options
                                    @update:model-value="onParamsChange"
                                />
                            </div>
                            <div class="col-12 col-sm-6 col-md-3">
                                <q-select
                                    v-model="analysisParams.date_field"
                                    :options="dateFieldOptions"
                                    label="时间基准"
                                    outlined
                                    dense
                                    emit-value
                                    map-options
                                    @update:model-value="onParamsChange"
                                />
                            </div>
                            <div class="col-12 col-sm-6 col-md-3">
                                <q-select
                                    v-model="analysisParams.timezone"
                                    :options="timezoneOptions"
                                    label="时区设置"
                                    outlined
                                    dense
                                    emit-value
                                    map-options
                                    @update:model-value="onParamsChange"
                                />
                            </div>
                            <div class="col-12 col-sm-6 col-md-3">
                                <q-toggle
                                    v-model="analysisParams.include_deleted"
                                    label="包含已删除数据"
                                    @update:model-value="onParamsChange"
                                />
                            </div>
                        </div>
                    </q-card-section>
                </q-card>
            </q-expansion-item>
        </div>

        <!-- 基础统计概览 -->
        <div class="basic-stats-section q-mb-lg">
            <div class="section-title q-mb-md">
                <q-icon name="bar_chart" size="20px" class="q-mr-sm" />
                基础统计概览
            </div>
            <div class="row q-gutter-md">
                <div
                    class="col-12 col-sm-6 col-md-3"
                    v-for="(stat, index) in basicStatsCards"
                    :key="index"
                >
                    <q-card class="stats-card">
                        <q-card-section>
                            <div class="stats-content">
                                <div class="stats-icon">
                                    <q-icon :name="stat.icon" size="24px" :color="stat.color" />
                                </div>
                                <div class="stats-info">
                                    <div class="stats-value">{{ stat.value }}</div>
                                    <div class="stats-label">{{ stat.label }}</div>
                                    <div class="stats-trend" v-if="stat.trend">
                                        <q-icon
                                            :name="
                                                stat.trend.direction === 'up'
                                                    ? 'trending_up'
                                                    : stat.trend.direction === 'down'
                                                      ? 'trending_down'
                                                      : 'trending_flat'
                                            "
                                            :color="
                                                stat.trend.direction === 'up'
                                                    ? 'positive'
                                                    : stat.trend.direction === 'down'
                                                      ? 'negative'
                                                      : 'grey'
                                            "
                                            size="14px"
                                        />
                                        <span
                                            :class="`text-${stat.trend.direction === 'up' ? 'positive' : stat.trend.direction === 'down' ? 'negative' : 'grey'}`"
                                        >
                                            {{ stat.trend.value }}%
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </q-card-section>
                    </q-card>
                </div>
            </div>
        </div>

        <!-- 专业分析图表区域 -->
        <div class="charts-section">
            <!-- 状态分布专业分析 -->
            <div class="chart-row q-mb-lg">
                <div class="section-title q-mb-md">
                    <q-icon name="donut_small" size="20px" class="q-mr-sm" />
                    状态分布深度分析
                </div>
                <div class="row q-gutter-lg">
                    <div class="col-12 col-md-6">
                        <q-card class="chart-card">
                            <q-card-section>
                                <div class="chart-title">状态分布与转换效率</div>
                                <div class="status-distribution-chart">
                                    <div v-if="statusDistribution?.basic_distribution?.length">
                                        <div
                                            v-for="status in statusDistribution.basic_distribution"
                                            :key="status.status"
                                            class="status-item q-mb-sm"
                                        >
                                            <div class="status-header">
                                                <span class="status-label">{{
                                                    status.status_display
                                                }}</span>
                                                <span class="status-percentage"
                                                    >{{ status.percentage.toFixed(1) }}%</span
                                                >
                                            </div>
                                            <q-linear-progress
                                                :value="status.percentage / 100"
                                                :color="getStatusColor(status.status)"
                                                size="8px"
                                                rounded
                                            />
                                            <div class="status-details">
                                                <span class="status-count"
                                                    >{{ status.count }} 个任务</span
                                                >
                                                <span
                                                    class="efficiency-score"
                                                    v-if="status.efficiency_score"
                                                >
                                                    效率: {{ status.efficiency_score?.toFixed(1) }}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                    <div v-else class="no-data">暂无状态分布数据</div>
                                </div>
                            </q-card-section>
                        </q-card>
                    </div>
                    <div class="col-12 col-md-6">
                        <q-card class="chart-card">
                            <q-card-section>
                                <div class="chart-title">状态转换路径分析</div>
                                <div class="transition-analysis">
                                    <div
                                        v-if="
                                            statusDistribution?.transition_analysis
                                                ?.common_transitions?.length
                                        "
                                    >
                                        <div
                                            v-for="transition in statusDistribution.transition_analysis.common_transitions.slice(
                                                0,
                                                5,
                                            )"
                                            :key="`${transition.from_status}-${transition.to_status}`"
                                            class="transition-item q-mb-sm"
                                        >
                                            <div class="transition-path">
                                                <span class="from-status">{{
                                                    transition.from_status
                                                }}</span>
                                                <q-icon
                                                    name="arrow_right_alt"
                                                    class="transition-arrow"
                                                />
                                                <span class="to-status">{{
                                                    transition.to_status
                                                }}</span>
                                            </div>
                                            <div class="transition-metrics">
                                                <span class="transition-count"
                                                    >{{ transition.transition_count }} 次</span
                                                >
                                                <span class="transition-frequency"
                                                    >频率:
                                                    {{ transition.frequency.toFixed(1) }}%</span
                                                >
                                            </div>
                                        </div>
                                    </div>
                                    <div v-else class="no-data">暂无转换分析数据</div>
                                </div>
                            </q-card-section>
                        </q-card>
                    </div>
                </div>
            </div>

            <!-- 标签分布专业分析 -->
            <div class="chart-row q-mb-lg">
                <div class="section-title q-mb-md">
                    <q-icon name="local_offer" size="20px" class="q-mr-sm" />
                    标签使用与效率分析
                </div>
                <div class="row q-gutter-lg">
                    <div class="col-12 col-md-6">
                        <q-card class="chart-card">
                            <q-card-section>
                                <div class="chart-title">热门标签分布</div>
                                <div class="tag-distribution-chart">
                                    <div v-if="tagDistribution?.basic_distribution?.length">
                                        <div
                                            v-for="tag in tagDistribution.basic_distribution.slice(
                                                0,
                                                10,
                                            )"
                                            :key="tag.tag"
                                            class="tag-item q-mb-sm"
                                        >
                                            <div class="tag-header">
                                                <q-chip
                                                    :label="tag.tag"
                                                    size="sm"
                                                    :color="getTagColor(tag.tag)"
                                                    text-color="white"
                                                />
                                                <span class="tag-usage"
                                                    >{{ tag.percentage.toFixed(1) }}%</span
                                                >
                                            </div>
                                            <q-linear-progress
                                                :value="tag.percentage / 100"
                                                :color="getTagColor(tag.tag)"
                                                size="6px"
                                                rounded
                                            />
                                            <div class="tag-details">
                                                <span class="tag-count"
                                                    >{{ tag.count }} 次使用</span
                                                >
                                                <span class="usage-score"
                                                    >评分: {{ tag.usage_score?.toFixed(1) }}</span
                                                >
                                            </div>
                                        </div>
                                    </div>
                                    <div v-else class="no-data">暂无标签数据</div>
                                </div>
                            </q-card-section>
                        </q-card>
                    </div>
                    <div class="col-12 col-md-6">
                        <q-card class="chart-card">
                            <q-card-section>
                                <div class="chart-title">标签效率分析</div>
                                <div class="tag-efficiency-chart">
                                    <div
                                        v-if="
                                            tagDistribution?.efficiency_analysis?.tag_efficiency
                                                ?.length
                                        "
                                    >
                                        <div
                                            v-for="eff in tagDistribution.efficiency_analysis.tag_efficiency.slice(
                                                0,
                                                8,
                                            )"
                                            :key="eff.tag"
                                            class="efficiency-item q-mb-sm"
                                        >
                                            <div class="efficiency-header">
                                                <span class="efficiency-tag">{{ eff.tag }}</span>
                                                <q-badge
                                                    :color="
                                                        getEfficiencyColor(eff.efficiency_rating)
                                                    "
                                                    :label="eff.efficiency_rating"
                                                />
                                            </div>
                                            <div class="efficiency-metrics">
                                                <div class="metric">
                                                    <span class="metric-label">完成率:</span>
                                                    <span class="metric-value"
                                                        >{{
                                                            eff.completion_rate?.toFixed(1)
                                                        }}%</span
                                                    >
                                                </div>
                                                <div class="metric">
                                                    <span class="metric-label">平均用时:</span>
                                                    <span class="metric-value"
                                                        >{{
                                                            eff.average_completion_time?.toFixed(1)
                                                        }}h</span
                                                    >
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div v-else class="no-data">暂无效率分析数据</div>
                                </div>
                            </q-card-section>
                        </q-card>
                    </div>
                </div>
            </div>

            <!-- 时间分布专业分析 -->
            <div class="chart-row q-mb-lg">
                <div class="section-title q-mb-md">
                    <q-icon name="schedule" size="20px" class="q-mr-sm" />
                    时间模式与效率分析
                </div>
                <div class="row q-gutter-lg">
                    <div class="col-12 col-md-6">
                        <q-card class="chart-card">
                            <q-card-section>
                                <div class="chart-title">工作时间分布</div>
                                <div class="hourly-distribution-chart">
                                    <div
                                        v-if="
                                            timeDistribution?.hourly_analysis?.creation_by_hour
                                                ?.length
                                        "
                                    >
                                        <div class="hourly-chart">
                                            <div
                                                v-for="hour in timeDistribution.hourly_analysis
                                                    .creation_by_hour"
                                                :key="hour.hour"
                                                class="hour-bar"
                                                :style="{
                                                    height: `${(hour.percentage / Math.max(...timeDistribution.hourly_analysis.creation_by_hour.map(h => h.percentage))) * 100}%`,
                                                }"
                                            >
                                                <div class="hour-label">{{ hour.hour }}</div>
                                                <div class="hour-value">{{ hour.count }}</div>
                                            </div>
                                        </div>
                                        <div class="peak-hours-info q-mt-md">
                                            <div
                                                class="info-item"
                                                v-if="timeDistribution.hourly_analysis.peak_hours"
                                            >
                                                <strong>最高效时段:</strong>
                                                {{
                                                    timeDistribution.hourly_analysis.peak_hours.most_productive?.join(
                                                        ', ',
                                                    ) || '暂无数据'
                                                }}点
                                            </div>
                                        </div>
                                    </div>
                                    <div v-else class="no-data">暂无小时分布数据</div>
                                </div>
                            </q-card-section>
                        </q-card>
                    </div>
                    <div class="col-12 col-md-6">
                        <q-card class="chart-card">
                            <q-card-section>
                                <div class="chart-title">工作日效率分析</div>
                                <div class="daily-efficiency-chart">
                                    <div
                                        v-if="
                                            timeDistribution?.daily_analysis?.weekday_distribution
                                                ?.length
                                        "
                                    >
                                        <div
                                            v-for="day in timeDistribution.daily_analysis
                                                .weekday_distribution"
                                            :key="day.weekday"
                                            class="weekday-item q-mb-sm"
                                        >
                                            <div class="weekday-header">
                                                <span class="weekday-name">{{
                                                    day.weekday_name
                                                }}</span>
                                                <span class="efficiency-score"
                                                    >效率:
                                                    {{ day.efficiency_score?.toFixed(1) }}</span
                                                >
                                            </div>
                                            <div class="weekday-metrics">
                                                <div class="metric-bar">
                                                    <span class="metric-label">创建</span>
                                                    <q-linear-progress
                                                        :value="
                                                            day.creation_count /
                                                            Math.max(
                                                                ...timeDistribution.daily_analysis.weekday_distribution.map(
                                                                    d => d.creation_count,
                                                                ),
                                                            )
                                                        "
                                                        color="primary"
                                                        size="4px"
                                                    />
                                                    <span class="metric-count">{{
                                                        day.creation_count
                                                    }}</span>
                                                </div>
                                                <div class="metric-bar">
                                                    <span class="metric-label">完成</span>
                                                    <q-linear-progress
                                                        :value="
                                                            day.completion_count /
                                                            Math.max(
                                                                ...timeDistribution.daily_analysis.weekday_distribution.map(
                                                                    d => d.completion_count,
                                                                ),
                                                            )
                                                        "
                                                        color="positive"
                                                        size="4px"
                                                    />
                                                    <span class="metric-count">{{
                                                        day.completion_count
                                                    }}</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div v-else class="no-data">暂无工作日分析数据</div>
                                </div>
                            </q-card-section>
                        </q-card>
                    </div>
                </div>
            </div>

            <!-- 智能洞察与建议 -->
            <div class="insights-section">
                <div class="section-title q-mb-md">
                    <q-icon name="psychology" size="20px" class="q-mr-sm" />
                    智能洞察与建议
                </div>
                <div class="row q-gutter-lg">
                    <div class="col-12 col-md-4">
                        <q-card class="insight-card">
                            <q-card-section>
                                <div class="insight-title">
                                    <q-icon name="trending_up" color="positive" />
                                    效率洞察
                                </div>
                                <div class="insight-content">
                                    <div v-if="timeDistribution?.insights?.best_work_times?.length">
                                        <p><strong>最佳工作时段:</strong></p>
                                        <ul>
                                            <li
                                                v-for="time in timeDistribution.insights
                                                    .best_work_times"
                                                :key="time"
                                            >
                                                {{ time }}
                                            </li>
                                        </ul>
                                    </div>
                                    <div
                                        v-if="
                                            timeDistribution?.insights?.productivity_patterns
                                                ?.length
                                        "
                                    >
                                        <p><strong>生产力模式:</strong></p>
                                        <ul>
                                            <li
                                                v-for="pattern in timeDistribution.insights
                                                    .productivity_patterns"
                                                :key="pattern"
                                            >
                                                {{ pattern }}
                                            </li>
                                        </ul>
                                    </div>
                                </div>
                            </q-card-section>
                        </q-card>
                    </div>
                    <div class="col-12 col-md-4">
                        <q-card class="insight-card">
                            <q-card-section>
                                <div class="insight-title">
                                    <q-icon name="lightbulb" color="warning" />
                                    优化建议
                                </div>
                                <div class="insight-content">
                                    <div
                                        v-if="
                                            tagDistribution?.efficiency_analysis
                                                ?.performance_insights?.recommendations?.length
                                        "
                                    >
                                        <p><strong>标签优化建议:</strong></p>
                                        <ul>
                                            <li
                                                v-for="rec in tagDistribution.efficiency_analysis
                                                    .performance_insights.recommendations"
                                                :key="rec"
                                            >
                                                {{ rec }}
                                            </li>
                                        </ul>
                                    </div>
                                    <div
                                        v-if="
                                            timeDistribution?.insights?.time_management_tips?.length
                                        "
                                    >
                                        <p><strong>时间管理技巧:</strong></p>
                                        <ul>
                                            <li
                                                v-for="tip in timeDistribution.insights
                                                    .time_management_tips"
                                                :key="tip"
                                            >
                                                {{ tip }}
                                            </li>
                                        </ul>
                                    </div>
                                </div>
                            </q-card-section>
                        </q-card>
                    </div>
                    <div class="col-12 col-md-4">
                        <q-card class="insight-card">
                            <q-card-section>
                                <div class="insight-title">
                                    <q-icon name="warning" color="negative" />
                                    风险提醒
                                </div>
                                <div class="insight-content">
                                    <div
                                        v-if="timeDistribution?.insights?.workload_warnings?.length"
                                    >
                                        <p><strong>工作负载警告:</strong></p>
                                        <ul>
                                            <li
                                                v-for="warning in timeDistribution.insights
                                                    .workload_warnings"
                                                :key="warning"
                                            >
                                                {{ warning }}
                                            </li>
                                        </ul>
                                    </div>
                                    <div
                                        v-if="
                                            tagDistribution?.health_metrics?.recommended_cleanup
                                                ?.length
                                        "
                                    >
                                        <p><strong>数据清理建议:</strong></p>
                                        <ul>
                                            <li
                                                v-for="cleanup in tagDistribution.health_metrics
                                                    .recommended_cleanup"
                                                :key="cleanup"
                                            >
                                                {{ cleanup }}
                                            </li>
                                        </ul>
                                    </div>
                                </div>
                            </q-card-section>
                        </q-card>
                    </div>
                </div>
            </div>
        </div>

        <!-- 加载状态 -->
        <q-inner-loading :showing="loading" color="primary" />
    </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useTaskStore } from 'src/stores/task';
import type { StatusDistribution, TagDistribution, TimeDistribution, TaskStats } from 'src/types';
import { Notify } from 'quasar';

const taskStore = useTaskStore();

// 响应式状态
const loading = ref(false);
const taskStats = ref<TaskStats | null>(null);
const statusDistribution = ref<StatusDistribution | null>(null);
const tagDistribution = ref<TagDistribution | null>(null);
const timeDistribution = ref<TimeDistribution | null>(null);

// 分析参数
const analysisParams = ref({
    period: 'month',
    date_field: 'created_at',
    include_deleted: false,
    timezone: 'Asia/Shanghai',
});

// 选项配置
const periodOptions = [
    { label: '全部时间', value: 'all' },
    { label: '今天', value: 'today' },
    { label: '本周', value: 'week' },
    { label: '本月', value: 'month' },
    { label: '本季度', value: 'quarter' },
    { label: '今年', value: 'year' },
];

const dateFieldOptions = [
    { label: '创建时间', value: 'created_at' },
    { label: '更新时间', value: 'updated_at' },
    { label: '截止时间', value: 'due_date' },
    { label: '开始时间', value: 'start_date' },
];

const timezoneOptions = [
    { label: '中国时间 (UTC+8)', value: 'Asia/Shanghai' },
    { label: '世界标准时间 (UTC)', value: 'UTC' },
    { label: '美国东部时间', value: 'America/New_York' },
    { label: '欧洲中部时间', value: 'Europe/Berlin' },
];

// 计算属性 - 基础统计卡片
const basicStatsCards = computed(() => {
    if (!taskStats.value?.basic_stats) return [];

    const stats = taskStats.value.basic_stats;
    return [
        {
            icon: 'assignment',
            label: '总任务数',
            value: stats.total_tasks || 0,
            color: 'primary',
            trend: getTrend('total'),
        },
        {
            icon: 'play_circle',
            label: '活跃任务',
            value: (stats.total_tasks || 0) - (stats.completed_tasks || 0),
            color: 'info',
            trend: getTrend('active'),
        },
        {
            icon: 'check_circle',
            label: '已完成',
            value: stats.completed_tasks || 0,
            color: 'positive',
            trend: getTrend('completed'),
        },
        {
            icon: 'percent',
            label: '完成率',
            value: `${(stats.completion_rate || 0).toFixed(1)}%`,
            color: 'accent',
            trend: getTrend('completion_rate'),
        },
        {
            icon: 'warning',
            label: '逾期任务',
            value: stats.overdue_tasks || 0,
            color: 'negative',
            trend: getTrend('overdue'),
        },
        {
            icon: 'timeline',
            label: '平均进度',
            value: `${(stats.average_progress || 0).toFixed(1)}%`,
            color: 'orange',
            trend: getTrend('progress'),
        },
        {
            icon: 'schedule',
            label: '预计时长',
            value: `${(stats.total_estimated_hours || 0).toFixed(1)}h`,
            color: 'purple',
            trend: getTrend('estimated_hours'),
        },
        {
            icon: 'speed',
            label: '效率指数',
            value: `${(stats.efficiency_rate || 0).toFixed(1)}%`,
            color: 'teal',
            trend: getTrend('efficiency'),
        },
    ];
});

// 初始化
onMounted(async () => {
    await loadAllData();
});

// 监听参数变化
watch(
    analysisParams,
    () => {
        void loadAllData();
    },
    { deep: true },
);

// 方法
const loadAllData = async () => {
    loading.value = true;
    try {
        const params = { ...analysisParams.value };

        // 并行加载所有数据
        const [stats, statusDist, tagDist, timeDist] = await Promise.all([
            taskStore.fetchTaskStats(),
            taskStore.fetchStatusDistribution(params),
            taskStore.fetchTagDistribution(params),
            taskStore.fetchTimeDistribution(params),
        ]);

        taskStats.value = stats;
        statusDistribution.value = statusDist;
        tagDistribution.value = tagDist;
        timeDistribution.value = timeDist;
    } catch (error) {
        console.error('加载数据失败:', error);
        Notify.create({
            type: 'negative',
            message: '加载数据失败，请稍后重试',
            position: 'top',
        });
    } finally {
        loading.value = false;
    }
};

const refreshAllData = async () => {
    await loadAllData();
    Notify.create({
        type: 'positive',
        message: '数据已刷新',
        position: 'top',
    });
};

const onParamsChange = () => {
    // 防抖处理，避免频繁请求
    setTimeout(() => {
        void loadAllData();
    }, 300);
};

const formatDate = (date: Date) => {
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long',
    });
};

// 趋势计算（模拟数据，实际应该从后端获取）
const getTrend = (type: string) => {
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

// 状态颜色映射
const getStatusColor = (status: string) => {
    const colors = {
        PENDING: 'orange',
        IN_PROGRESS: 'blue',
        COMPLETED: 'green',
        CANCELLED: 'grey',
        ON_HOLD: 'purple',
    };
    return colors[status as keyof typeof colors] || 'grey';
};

// 标签颜色映射
const getTagColor = (tag: string) => {
    const colors = ['blue', 'green', 'orange', 'purple', 'cyan', 'pink', 'indigo', 'amber'];
    const hash = tag.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return colors[hash % colors.length];
};

// 效率评级颜色
const getEfficiencyColor = (rating: string) => {
    const colors = {
        high: 'positive',
        medium: 'warning',
        low: 'negative',
    };
    return colors[rating as keyof typeof colors] || 'grey';
};
</script>

<style lang="scss" scoped>
.advanced-dashboard-page {
    background: #f8fafc;
    min-height: calc(100vh - 50px);
}

.page-header {
    .page-title {
        color: #1e293b;
        font-weight: 600;
        font-size: 1.5rem;
    }

    .page-subtitle {
        color: #64748b;
        font-size: 0.875rem;
    }

    .refresh-btn {
        border-radius: 8px;
    }
}

.analysis-controls {
    .controls-expansion {
        background: white;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
}

.section-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: #1e293b;
    display: flex;
    align-items: center;
}

.stats-card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease;

    &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .stats-content {
        display: flex;
        align-items: center;
        gap: 12px;

        .stats-icon {
            padding: 8px;
            border-radius: 8px;
            background: rgba(25, 118, 210, 0.1);
        }

        .stats-info {
            flex: 1;

            .stats-value {
                font-size: 1.5rem;
                font-weight: 700;
                color: #1e293b;
                line-height: 1.2;
            }

            .stats-label {
                font-size: 0.875rem;
                color: #64748b;
                margin-bottom: 4px;
            }

            .stats-trend {
                display: flex;
                align-items: center;
                gap: 4px;
                font-size: 0.75rem;
                font-weight: 500;
            }
        }
    }
}

.chart-card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    height: 100%;

    .chart-title {
        font-size: 1rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 1px solid #e2e8f0;
    }
}

.status-item {
    .status-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4px;
    }

    .status-label {
        font-weight: 500;
        color: #374151;
    }

    .status-percentage {
        font-weight: 600;
        color: #1976d2;
    }

    .status-details {
        display: flex;
        justify-content: space-between;
        font-size: 0.75rem;
        color: #6b7280;
        margin-top: 4px;
    }
}

.transition-item {
    padding: 8px;
    background: #f8fafc;
    border-radius: 6px;

    .transition-path {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 4px;

        .from-status,
        .to-status {
            font-weight: 500;
            font-size: 0.875rem;
        }

        .transition-arrow {
            color: #64748b;
        }
    }

    .transition-metrics {
        display: flex;
        gap: 16px;
        font-size: 0.75rem;
        color: #6b7280;
    }
}

.tag-item {
    .tag-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4px;
    }

    .tag-usage {
        font-weight: 600;
        color: #1976d2;
        font-size: 0.875rem;
    }

    .tag-details {
        display: flex;
        justify-content: space-between;
        font-size: 0.75rem;
        color: #6b7280;
        margin-top: 4px;
    }
}

.efficiency-item {
    padding: 8px;
    background: #f8fafc;
    border-radius: 6px;

    .efficiency-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;

        .efficiency-tag {
            font-weight: 500;
        }
    }

    .efficiency-metrics {
        display: flex;
        gap: 16px;

        .metric {
            font-size: 0.75rem;

            .metric-label {
                color: #6b7280;
            }

            .metric-value {
                color: #374151;
                font-weight: 500;
            }
        }
    }
}

.hourly-chart {
    display: flex;
    align-items: end;
    gap: 2px;
    height: 120px;
    margin-bottom: 16px;

    .hour-bar {
        flex: 1;
        background: linear-gradient(to top, #3b82f6, #60a5fa);
        border-radius: 2px 2px 0 0;
        position: relative;
        min-height: 8px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        padding: 4px 2px;

        .hour-label {
            font-size: 0.625rem;
            color: white;
            font-weight: 500;
        }

        .hour-value {
            font-size: 0.625rem;
            color: white;
            font-weight: 600;
        }
    }
}

.weekday-item {
    .weekday-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;

        .weekday-name {
            font-weight: 500;
        }

        .efficiency-score {
            font-size: 0.875rem;
            color: #1976d2;
            font-weight: 600;
        }
    }

    .weekday-metrics {
        display: flex;
        flex-direction: column;
        gap: 4px;

        .metric-bar {
            display: flex;
            align-items: center;
            gap: 8px;

            .metric-label {
                font-size: 0.75rem;
                color: #6b7280;
                width: 32px;
            }

            .metric-count {
                font-size: 0.75rem;
                color: #374151;
                width: 24px;
                text-align: right;
            }
        }
    }
}

.insight-card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    height: 100%;

    .insight-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 1rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 12px;
    }

    .insight-content {
        font-size: 0.875rem;
        color: #374151;
        line-height: 1.5;

        ul {
            margin: 8px 0;
            padding-left: 16px;

            li {
                margin-bottom: 4px;
            }
        }

        p {
            margin: 8px 0 4px 0;
            font-weight: 500;
        }
    }
}

.no-data {
    text-align: center;
    color: #9ca3af;
    font-style: italic;
    padding: 24px;
}
</style>

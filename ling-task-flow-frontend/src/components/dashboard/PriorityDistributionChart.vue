<template>
    <div class="priority-distribution-chart">
        <div v-if="!hasData" class="no-data">
            <q-icon name="bar_chart" size="48px" color="grey-5" />
            <p class="text-grey-6">暂无数据</p>
        </div>

        <div v-else class="chart-container">
            <!-- 柱状图容器 -->
            <div class="bar-chart-container">
                <canvas ref="chartCanvas" width="350" height="200"></canvas>
            </div>

            <!-- 统计信息 -->
            <div class="chart-stats">
                <div
                    v-for="item in sortedData"
                    :key="item.priority"
                    class="stat-item cursor-pointer"
                    @click="handlePriorityClick(item.priority)"
                >
                    <div class="stat-header">
                        <div class="stat-color" :style="{ backgroundColor: item.color }"></div>
                        <span class="stat-label">{{ item.label }}</span>
                    </div>
                    <div class="stat-value">{{ item.count }}</div>
                    <div class="stat-percentage">{{ getPercentage(item.count) }}%</div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue';

interface ChartDataItem {
    priority: string;
    count: number;
    label: string;
    color: string;
}

interface Props {
    data: ChartDataItem[];
}

const props = defineProps<Props>();

const emit = defineEmits<{
    'priority-click': [priority: string];
}>();

const chartCanvas = ref<HTMLCanvasElement | null>(null);

const hasData = computed(() => {
    return props.data.length > 0 && props.data.some(item => item.count > 0);
});

const totalTasks = computed(() => {
    return props.data.reduce((sum, item) => sum + item.count, 0);
});

const sortedData = computed(() => {
    // 按优先级排序：URGENT > HIGH > MEDIUM > LOW
    const priorityOrder = { URGENT: 4, HIGH: 3, MEDIUM: 2, LOW: 1 };
    return [...props.data]
        .filter(item => item.count > 0)
        .sort(
            (a, b) =>
                (priorityOrder[b.priority as keyof typeof priorityOrder] || 0) -
                (priorityOrder[a.priority as keyof typeof priorityOrder] || 0),
        );
});

const getPercentage = (count: number) => {
    if (totalTasks.value === 0) return '0.00';
    return ((count / totalTasks.value) * 100).toFixed(2);
};

const drawChart = () => {
    if (!chartCanvas.value || !hasData.value) return;

    const canvas = chartCanvas.value;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // 清空画布
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const padding = 40;
    const chartWidth = canvas.width - padding * 2;
    const chartHeight = canvas.height - padding * 2;
    const barWidth = Math.min(40, chartWidth / sortedData.value.length - 20);
    const maxValue = Math.max(...sortedData.value.map(item => item.count));

    if (maxValue === 0) return;

    // 绘制背景网格线
    ctx.strokeStyle = '#f0f0f0';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 5; i++) {
        const y = padding + (chartHeight / 5) * i;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(canvas.width - padding, y);
        ctx.stroke();
    }

    // 绘制柱状图
    sortedData.value.forEach((item, index) => {
        const barHeight = (item.count / maxValue) * chartHeight;
        const x =
            padding +
            (chartWidth / sortedData.value.length) * index +
            (chartWidth / sortedData.value.length - barWidth) / 2;
        const y = canvas.height - padding - barHeight;

        // 绘制柱子
        ctx.fillStyle = item.color;
        ctx.fillRect(x, y, barWidth, barHeight);

        // 绘制数值标签
        ctx.fillStyle = '#333';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(item.count.toString(), x + barWidth / 2, y - 8);

        // 绘制标签
        ctx.fillStyle = '#666';
        ctx.font = '10px Arial';
        const labelY = canvas.height - padding + 20;
        ctx.fillText(item.label, x + barWidth / 2, labelY);
    });

    // 绘制Y轴标签
    ctx.fillStyle = '#666';
    ctx.font = '10px Arial';
    ctx.textAlign = 'right';
    for (let i = 0; i <= 5; i++) {
        const value = Math.round((maxValue / 5) * (5 - i));
        const y = padding + (chartHeight / 5) * i + 4;
        ctx.fillText(value.toString(), padding - 10, y);
    }
};

const handlePriorityClick = (priority: string) => {
    emit('priority-click', priority);
};

// 监听数据变化，重新绘制图表
watch(
    () => props.data,
    async () => {
        await nextTick();
        drawChart();
    },
    { deep: true },
);

onMounted(async () => {
    await nextTick();
    drawChart();
});
</script>

<style lang="scss" scoped>
.priority-distribution-chart {
    height: 300px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.no-data {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 12px;

    p {
        margin: 0;
        font-size: 14px;
    }
}

.chart-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
    width: 100%;
    height: 100%;
}

.bar-chart-container {
    flex-shrink: 0;
}

.chart-stats {
    display: flex;
    justify-content: center;
    gap: 16px;
    flex-wrap: wrap;
}

.stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 8px 12px;
    border-radius: 8px;
    min-width: 70px;
    transition: all 0.2s ease;

    &:hover {
        background-color: rgba(0, 0, 0, 0.05);
        transform: translateY(-2px);
    }
}

.stat-header {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 4px;
}

.stat-color {
    width: 12px;
    height: 12px;
    border-radius: 3px;
}

.stat-label {
    font-size: 12px;
    color: #666;
    font-weight: 500;
}

.stat-value {
    font-size: 18px;
    font-weight: bold;
    color: #333;
    margin-bottom: 2px;
}

.stat-percentage {
    font-size: 11px;
    color: #999;
}

// 响应式设计
@media (max-width: 768px) {
    .bar-chart-container canvas {
        width: 300px !important;
        height: 160px !important;
    }

    .chart-stats {
        gap: 12px;
    }

    .stat-item {
        min-width: 60px;
        padding: 6px 8px;
    }

    .stat-value {
        font-size: 16px;
    }
}
</style>

<template>
    <div class="status-distribution-chart">
        <div v-if="!hasData" class="no-data">
            <q-icon color="grey-5" name="pie_chart" size="48px" />
            <p class="text-grey-6">暂无数据</p>
        </div>

        <div v-else class="chart-container">
            <!-- 饼图容器 -->
            <div class="pie-chart-container">
                <canvas ref="chartCanvas" height="240" width="240"></canvas>
                <div class="chart-center">
                    <div class="total-count">{{ totalTasks }}</div>
                    <div class="total-label">总任务</div>
                </div>
            </div>

            <!-- 图例 -->
            <div class="chart-legend">
                <div
                    v-for="item in chartData"
                    :key="item.status"
                    class="legend-item cursor-pointer"
                    @click="handleStatusClick(item.status)"
                >
                    <div :style="{ backgroundColor: item.color }" class="legend-color"></div>
                    <div class="legend-info">
                        <div class="legend-label">{{ item.label }}</div>
                        <div class="legend-value">
                            {{ item.count }} ({{ getPercentage(item.count) }}%)
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue';

interface ChartDataItem {
    status: string;
    count: number;
    label: string;
    color: string;
}

interface Props {
    data: ChartDataItem[];
}

const props = defineProps<Props>();

const emit = defineEmits<{
    'status-click': [status: string];
}>();

const chartCanvas = ref<HTMLCanvasElement | null>(null);

const hasData = computed(() => {
    return props.data.length > 0 && props.data.some(item => item.count > 0);
});

const totalTasks = computed(() => {
    return props.data.reduce((sum, item) => sum + item.count, 0);
});

const chartData = computed(() => {
    return props.data.filter(item => item.count > 0);
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

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const outerRadius = 85;
    const innerRadius = 50; // 甜甜圈内半径

    let startAngle = -Math.PI / 2; // 从顶部开始

    chartData.value.forEach(item => {
        const sliceAngle = (item.count / totalTasks.value) * 2 * Math.PI;

        // 绘制扇形
        ctx.beginPath();
        ctx.arc(centerX, centerY, outerRadius, startAngle, startAngle + sliceAngle);
        ctx.arc(centerX, centerY, innerRadius, startAngle + sliceAngle, startAngle, true);
        ctx.closePath();

        // 设置颜色
        ctx.fillStyle = item.color;
        ctx.fill();

        // 添加边框
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.stroke();

        startAngle += sliceAngle;
    });
};

const handleStatusClick = (status: string) => {
    emit('status-click', status);
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
.status-distribution-chart {
    height: 100%;
    max-height: 300px;
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
    flex-direction: row;
    align-items: center;
    gap: 32px;
    width: 100%;
    height: 100%;
    min-height: 280px;
}

.pie-chart-container {
    position: relative;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
}

.chart-center {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    pointer-events: none;
}

.total-count {
    font-size: 24px;
    font-weight: bold;
    color: #333;
    line-height: 1;
}

.total-label {
    font-size: 12px;
    color: #666;
    margin-top: 4px;
}

.chart-legend {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 12px;
    max-height: 280px;
    overflow-y: auto;
    overflow-x: hidden; // 防止水平溢出
    padding-left: 16px;
    padding-right: 8px; // 添加右侧内边距，防止悬停时元素溢出
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 12px;
    border-radius: 8px;
    transition: all 0.2s ease;
    margin-right: 4px; // 为悬停位移预留空间

    &:hover {
        background-color: rgba(0, 0, 0, 0.05);
        transform: translateX(2px); // 减少位移距离，避免溢出
        margin-right: 2px; // 调整右边距补偿位移
    }
}

.legend-color {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    flex-shrink: 0;
}

.legend-info {
    flex: 1;
}

.legend-label {
    font-size: 14px;
    font-weight: 500;
    color: #333;
    margin-bottom: 2px;
}

.legend-value {
    font-size: 12px;
    color: #666;
}

// 响应式设计
@media (max-width: 1024px) and (min-width: 769px) {
    .chart-container {
        gap: 24px;
    }

    .chart-legend {
        padding-left: 12px;
        padding-right: 6px; // 中等屏幕也添加右侧内边距
    }
}

@media (max-width: 768px) {
    .status-distribution-chart {
        height: auto;
        min-height: 400px;
    }

    .chart-container {
        flex-direction: column;
        gap: 20px;
        min-height: auto;
    }

    .pie-chart-container {
        canvas {
            width: 200px !important;
            height: 200px !important;
        }
    }

    .chart-legend {
        width: 100%;
        max-height: none;
        flex-direction: row;
        flex-wrap: wrap;
        justify-content: center;
        padding-left: 0;
        padding-right: 0;
        overflow-x: hidden; // 防止水平溢出
    }

    .legend-item {
        flex: 0 1 auto;
        min-width: 140px;
        margin-right: 2px; // 在移动端也保持右边距

        &:hover {
            transform: translateX(1px); // 移动端减少位移
        }
    }
}
</style>

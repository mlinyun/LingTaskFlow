<template>
    <q-card
        class="stats-card cursor-pointer"
        :class="[`stats-card--${color}`]"
        @click="$emit('click')"
    >
        <q-card-section class="stats-card-content">
            <!-- 卡片头部：图标和标题 -->
            <div class="stats-header">
                <div class="stats-icon">
                    <q-icon :name="icon" size="20px" />
                </div>
                <div class="stats-title">{{ title }}</div>
            </div>

            <!-- 主要数据区域 -->
            <div class="stats-main">
                <div class="stats-value">{{ displayValue }}</div>
                <div class="stats-trend" v-if="trend">
                    <q-icon :name="trendIcon" :color="trendColor" size="14px" />
                    <span :class="`text-${trendColor}`">
                        {{ trend.value }}{{ trendUnit }}
                    </span>
                </div>
            </div>

            <!-- 背景装饰图标 -->
            <div class="stats-decoration">
                <q-icon :name="icon" size="36px" class="decoration-icon" />
            </div>

            <!-- 科技感数据流动效果 -->
            <div class="data-flow">
                <div class="flow-dot"></div>
                <div class="flow-dot"></div>
                <div class="flow-dot"></div>
            </div>
        </q-card-section>
    </q-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
    icon: string;
    title: string;
    value: string | number;
    color: 'blue' | 'orange' | 'green' | 'purple' | 'red';
    trend?: {
        value: number;
        direction: 'up' | 'down' | 'neutral';
    };
}

const props = defineProps<Props>();

defineEmits<{
    click: [];
}>();

const displayValue = computed(() => {
    if (typeof props.value === 'number') {
        return props.value.toLocaleString();
    }
    return props.value;
});

const trendIcon = computed(() => {
    if (!props.trend) return '';

    switch (props.trend.direction) {
        case 'up':
            return 'trending_up';
        case 'down':
            return 'trending_down';
        default:
            return 'trending_flat';
    }
});

const trendColor = computed(() => {
    if (!props.trend) return 'grey';

    switch (props.trend.direction) {
        case 'up':
            return 'positive';
        case 'down':
            return 'negative';
        default:
            return 'grey';
    }
});

const trendUnit = computed(() => {
    return props.trend?.direction === 'neutral' ? '' : '%';
});
</script>

<style lang="scss" scoped>
.stats-card {
    border-radius: 20px;
    border: 1px solid rgba(59, 130, 246, 0.1);
    background: rgba(255, 255, 255, 0.98);
    box-shadow:
        0 8px 32px rgba(14, 165, 233, 0.08),
        0 2px 8px rgba(59, 130, 246, 0.05),
        inset 0 1px 0 rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(20px);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
    position: relative;
    height: 110px;
    width: 100%;
    max-width: none;

    // 移动端优化
    @media (max-width: 600px) {
        height: 90px;
        border-radius: 16px;
    }

    // 中等屏幕优化 - 平板横屏时确保4个卡片能在一行
    @media (min-width: 601px) and (max-width: 1024px) {
        height: 100px;
    }

    // 大屏幕优化
    @media (min-width: 1025px) {
        height: 110px;
    }

    // 科技感边框发光效果
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
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    &:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow:
            0 20px 60px rgba(14, 165, 233, 0.15),
            0 8px 24px rgba(59, 130, 246, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);
        border-color: rgba(59, 130, 246, 0.2);

        &::before {
            opacity: 1;
        }

        .data-flow .flow-dot {
            animation-play-state: running;
        }

        .decoration-icon {
            opacity: 0.15;
            transform: scale(1.1);
        }
    }

    // 顶部科技感装饰条
    &::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--card-gradient));
        opacity: 0.8;
    }
}

.stats-card-content {
    padding: 14px !important;
    height: 100%;
    display: flex;
    flex-direction: column;
    position: relative;
    z-index: 2;

    // 移动端优化
    @media (max-width: 600px) {
        padding: 10px !important;
    }

    // 中等屏幕优化
    @media (min-width: 601px) and (max-width: 1024px) {
        padding: 12px !important;
    }
}

// 卡片头部：图标和标题
.stats-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
}

.stats-icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--icon-bg);
    color: var(--icon-color);
    box-shadow: 0 4px 12px var(--icon-shadow);
    transition: all 0.3s ease;

    .stats-card:hover & {
        transform: scale(1.1);
        box-shadow: 0 6px 16px var(--icon-shadow);
    }
}

.stats-title {
    font-size: 12px;
    color: #64748b;
    font-weight: 600;
    letter-spacing: 0.02em;
    line-height: 1.2;

    // 移动端优化
    @media (max-width: 600px) {
        font-size: 11px;
    }

    // 中等屏幕优化
    @media (min-width: 601px) and (max-width: 1024px) {
        font-size: 11.5px;
    }
}

// 主要数据区域
.stats-main {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 8px;
}

.stats-value {
    font-size: 24px;
    font-weight: 800;
    color: #1e293b;
    line-height: 1;
    background: linear-gradient(135deg, var(--value-gradient));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    transition: all 0.3s ease;

    .stats-card:hover & {
        transform: scale(1.05);
    }

    // 移动端优化
    @media (max-width: 600px) {
        font-size: 20px;
    }

    // 中等屏幕优化
    @media (min-width: 601px) and (max-width: 1024px) {
        font-size: 22px;
    }
}

.stats-trend {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    font-weight: 600;

    .q-icon {
        transition: transform 0.3s ease;
    }

    .stats-card:hover & .q-icon {
        transform: scale(1.2);
    }
}

// 背景装饰图标 - 修复超出边界问题
.stats-decoration {
    position: absolute;
    right: 15px;
    bottom: 15px;
    opacity: 0.08;
    z-index: 1;
    pointer-events: none;
}

.decoration-icon {
    color: var(--decoration-color);
    transition: all 0.4s ease;
}

// 科技感数据流动效果
.data-flow {
    position: absolute;
    bottom: 8px;
    left: 20px;
    right: 20px;
    height: 2px;
    overflow: hidden;

    .flow-dot {
        position: absolute;
        width: 4px;
        height: 2px;
        background: var(--flow-color);
        border-radius: 1px;
        opacity: 0;
        animation: dataFlow 3s linear infinite;
        animation-play-state: paused;

        &:nth-child(1) {
            animation-delay: 0s;
        }

        &:nth-child(2) {
            animation-delay: 1s;
        }

        &:nth-child(3) {
            animation-delay: 2s;
        }
    }
}

@keyframes dataFlow {
    0% {
        left: -4px;
        opacity: 0;
    }
    10% {
        opacity: 1;
    }
    90% {
        opacity: 1;
    }
    100% {
        left: 100%;
        opacity: 0;
    }
}

// 蓝白科技感颜色主题 - 统一使用蓝色系
.stats-card--blue {
    --card-gradient: #3b82f6, #1d4ed8;
    --icon-bg: rgba(59, 130, 246, 0.15);
    --icon-color: #3b82f6;
    --icon-shadow: rgba(59, 130, 246, 0.4);
    --decoration-color: #3b82f6;
    --value-gradient: #3b82f6, #1e40af;
    --flow-color: rgba(59, 130, 246, 0.6);
}

.stats-card--orange {
    // 改为浅蓝色调
    --card-gradient: #0ea5e9, #0284c7;
    --icon-bg: rgba(14, 165, 233, 0.15);
    --icon-color: #0ea5e9;
    --icon-shadow: rgba(14, 165, 233, 0.4);
    --decoration-color: #0ea5e9;
    --value-gradient: #0ea5e9, #0284c7;
    --flow-color: rgba(14, 165, 233, 0.6);
}

.stats-card--green {
    // 改为青蓝色调
    --card-gradient: #06b6d4, #0891b2;
    --icon-bg: rgba(6, 182, 212, 0.15);
    --icon-color: #06b6d4;
    --icon-shadow: rgba(6, 182, 212, 0.4);
    --decoration-color: #06b6d4;
    --value-gradient: #06b6d4, #0891b2;
    --flow-color: rgba(6, 182, 212, 0.6);
}

.stats-card--purple {
    // 改为深蓝色调
    --card-gradient: #1e40af, #1e3a8a;
    --icon-bg: rgba(30, 64, 175, 0.15);
    --icon-color: #1e40af;
    --icon-shadow: rgba(30, 64, 175, 0.4);
    --decoration-color: #1e40af;
    --value-gradient: #1e40af, #1e3a8a;
    --flow-color: rgba(30, 64, 175, 0.6);
}

.stats-card--red {
    // 改为中蓝色调
    --card-gradient: #2563eb, #1d4ed8;
    --icon-bg: rgba(37, 99, 235, 0.15);
    --icon-color: #2563eb;
    --icon-shadow: rgba(37, 99, 235, 0.4);
    --decoration-color: #2563eb;
    --value-gradient: #2563eb, #1d4ed8;
    --flow-color: rgba(37, 99, 235, 0.6);
}

// 响应式设计
@media (max-width: 768px) {
    .stats-card {
        height: auto;
        min-height: 120px;
    }

    .stats-card-content {
        padding: 16px !important;
    }

    .stats-header {
        gap: 10px;
        margin-bottom: 12px;
    }

    .stats-icon {
        width: 36px;
        height: 36px;
    }

    .stats-value {
        font-size: 24px;
    }

    .stats-decoration {
        right: 10px;
        bottom: 10px;
    }

    .decoration-icon {
        font-size: 32px !important;
    }
}

@media (max-width: 480px) {
    .stats-card {
        min-height: 100px;
    }

    .stats-value {
        font-size: 20px;
    }

    .decoration-icon {
        display: none;
    }

    .data-flow {
        display: none;
    }
}
</style>

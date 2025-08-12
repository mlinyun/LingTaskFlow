<template>
    <q-card
        :class="[`stats-card--${color}`]"
        class="stats-card cursor-pointer"
        @click="$emit('click')"
    >
        <q-card-section class="stats-card-content">
            <!-- 左中右三栏布局 -->
            <div class="stats-layout">
                <!-- 左侧：图标区域 -->
                <div class="stats-left">
                    <div class="stats-icon">
                        <q-icon :name="icon" size="24px" />
                        <div class="icon-glow"></div>
                    </div>
                </div>

                <!-- 中间：主要数据区域 -->
                <div class="stats-center">
                    <!-- 左侧：标题和数值 -->
                    <div class="stats-main-data">
                        <div class="stats-title">{{ title }}</div>
                        <div class="stats-value">{{ displayValue }}</div>
                    </div>

                    <!-- 右侧：趋势信息 -->
                    <div v-if="trend" class="stats-trend-container">
                        <div class="stats-trend">
                            <q-icon :color="trendColor" :name="trendIcon" size="12px" />
                            <span :class="`text-${trendColor}`">
                                {{ trend.value }}{{ trendUnit }}
                            </span>
                        </div>
                    </div>
                </div>

                <!-- 右侧：背景装饰图标 -->
                <div class="stats-right">
                    <div class="stats-decoration">
                        <q-icon :name="icon" class="decoration-icon" size="48px" />
                        <div class="decoration-glow"></div>
                    </div>
                </div>
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

<script lang="ts" setup>
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
    border: none;
    background: rgba(255, 255, 255, 0.98);
    box-shadow:
        0 8px 32px rgba(14, 165, 233, 0.08),
        0 2px 8px rgba(59, 130, 246, 0.05),
        0 0 0 1px rgba(255, 255, 255, 0.3),
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
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        border-radius: 22px;
        background: linear-gradient(
            135deg,
            rgba(59, 130, 246, 0.4) 0%,
            rgba(14, 165, 233, 0.2) 25%,
            rgba(6, 182, 212, 0.3) 50%,
            rgba(14, 165, 233, 0.2) 75%,
            rgba(59, 130, 246, 0.4) 100%
        );
        z-index: -1;
        opacity: 0;
        transition: opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        filter: blur(2px);
    }

    &:hover {
        transform: translateY(-4px) scale(1.01);
        box-shadow:
            0 16px 48px rgba(14, 165, 233, 0.12),
            0 6px 18px rgba(59, 130, 246, 0.08),
            0 0 0 1px rgba(59, 130, 246, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);

        &::before {
            opacity: 0.8;
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
    padding: 16px !important;
    height: 100%;
    display: flex;
    flex-direction: column;
    position: relative;
    z-index: 2;

    // 移动端优化
    @media (max-width: 600px) {
        padding: 12px !important;
    }

    // 中等屏幕优化
    @media (min-width: 601px) and (max-width: 1024px) {
        padding: 14px !important;
    }
}

// 左中右三栏布局
.stats-layout {
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: center;
    gap: 12px;
    height: 100%;
    min-height: 78px;

    @media (max-width: 600px) {
        gap: 8px;
        min-height: 66px;
    }

    @media (min-width: 601px) and (max-width: 1024px) {
        gap: 10px;
        min-height: 72px;
    }
}

// 左侧：图标区域
.stats-left {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.stats-icon {
    position: relative;
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--icon-bg);
    color: var(--icon-color);
    box-shadow: 0 4px 16px var(--icon-shadow);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

    .stats-card:hover & {
        transform: scale(1.1) rotate(5deg);
        box-shadow: 0 8px 24px var(--icon-shadow);
    }

    .icon-glow {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 36px;
        height: 36px;
        background: radial-gradient(circle, var(--icon-color-alpha) 0%, transparent 70%);
        border-radius: 50%;
        opacity: 0;
        animation: iconPulse 2s ease-in-out infinite;

        .stats-card:hover & {
            opacity: 1;
        }
    }

    // 移动端优化
    @media (max-width: 600px) {
        width: 36px;
        height: 36px;
        border-radius: 10px;

        .q-icon {
            font-size: 20px !important;
        }

        .icon-glow {
            width: 28px;
            height: 28px;
        }
    }

    // 中等屏幕优化
    @media (min-width: 601px) and (max-width: 1024px) {
        width: 40px;
        height: 40px;

        .q-icon {
            font-size: 22px !important;
        }

        .icon-glow {
            width: 32px;
            height: 32px;
        }
    }
}

// 中间：主要数据区域
.stats-center {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    flex: 1;
    min-width: 0; // 防止flex溢出
    padding: 0 1.5rem;

    @media (max-width: 600px) {
        gap: 6px;
        padding: 0 4px;
    }
}

// 左侧：标题和数值区域
.stats-main-data {
    display: flex;
    flex-direction: column;
    gap: 4px;
    flex: 1;
    min-width: 0;

    @media (max-width: 600px) {
        gap: 2px;
    }
}

// 右侧：趋势容器
.stats-trend-container {
    display: flex;
    align-items: center;
    flex-shrink: 0;
}

.stats-title {
    font-size: 13px;
    color: #64748b;
    font-weight: 600;
    letter-spacing: 0.02em;
    line-height: 1.2;
    margin-bottom: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;

    // 移动端优化
    @media (max-width: 600px) {
        font-size: 11px;
        margin-bottom: 1px;
    }

    // 中等屏幕优化
    @media (min-width: 601px) and (max-width: 1024px) {
        font-size: 12px;
    }
}

.stats-value {
    font-size: 28px;
    font-weight: 800;
    color: #1e293b;
    line-height: 1;
    background: linear-gradient(135deg, var(--value-gradient));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;

    .stats-card:hover & {
        transform: scale(1.05);
        filter: brightness(1.1);
    }

    // 移动端优化
    @media (max-width: 600px) {
        font-size: 20px;
    }

    // 中等屏幕优化
    @media (min-width: 601px) and (max-width: 1024px) {
        font-size: 24px;
    }
}

.stats-trend {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    font-size: 11px;
    font-weight: 600;
    padding: 6px 8px;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.6);
    border: 1px solid rgba(0, 0, 0, 0.05);
    min-width: 48px;
    text-align: center;
    backdrop-filter: blur(10px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

    .q-icon {
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 1px;
    }

    .stats-card:hover & {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

        .q-icon {
            transform: scale(1.2) rotate(10deg);
        }
    }

    // 移动端优化
    @media (max-width: 600px) {
        font-size: 9px;
        padding: 4px 6px;
        min-width: 40px;
        gap: 1px;

        .q-icon {
            font-size: 10px !important;
        }
    }

    // 中等屏幕优化
    @media (min-width: 601px) and (max-width: 1024px) {
        font-size: 10px;
        padding: 5px 7px;
        min-width: 44px;

        .q-icon {
            font-size: 11px !important;
        }
    }
}

// 右侧：背景装饰图标
.stats-right {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    position: relative;
}

.stats-decoration {
    position: relative;
    opacity: 0.06;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

    .stats-card:hover & {
        opacity: 0.12;
        transform: scale(1.1) rotate(-5deg);
    }

    .decoration-glow {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 60px;
        height: 60px;
        background: radial-gradient(circle, var(--decoration-color-alpha) 0%, transparent 70%);
        border-radius: 50%;
        opacity: 0;
        animation: decorationPulse 3s ease-in-out infinite;

        .stats-card:hover & {
            opacity: 0.3;
        }
    }

    // 移动端优化 - 简化装饰图标
    @media (max-width: 600px) {
        opacity: 0.04;

        .decoration-icon {
            font-size: 32px !important;
        }

        .decoration-glow {
            width: 40px;
            height: 40px;
        }

        .stats-card:hover & {
            opacity: 0.08;
            transform: scale(1.05);
        }
    }

    // 中等屏幕优化
    @media (min-width: 601px) and (max-width: 1024px) {
        .decoration-icon {
            font-size: 40px !important;
        }

        .decoration-glow {
            width: 50px;
            height: 50px;
        }
    }
}

.decoration-icon {
    color: var(--decoration-color);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

// 科技感数据流动效果 - 适配左中右布局
.data-flow {
    position: absolute;
    top: 50%;
    left: 56px; // 图标区域后
    right: 20px;
    height: 2px;
    overflow: hidden;
    transform: translateY(-50%);
    opacity: 0;
    transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1);

    .stats-card:hover & {
        opacity: 1;
    }

    .stats-card:not(:hover) & {
        opacity: 0;
    }

    @media (max-width: 600px) {
        left: 44px; // 移动端图标宽度 + 8px
    }

    @media (min-width: 601px) and (max-width: 1024px) {
        left: 50px; // 中等屏幕图标宽度 + 10px
    }

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

// 响应式优化 - 现已内联到各个组件中
</style>

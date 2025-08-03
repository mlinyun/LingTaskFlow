<template>
    <q-card
        class="stats-card cursor-pointer"
        :class="[`stats-card--${color}`]"
        @click="$emit('click')"
    >
        <q-card-section class="flex items-center justify-between">
            <div class="stats-content">
                <div class="stats-icon">
                    <q-icon :name="icon" size="32px" />
                </div>
                <div class="stats-info">
                    <div class="stats-title">{{ title }}</div>
                    <div class="stats-value">{{ displayValue }}</div>
                    <div class="stats-trend" v-if="trend">
                        <q-icon :name="trendIcon" :color="trendColor" size="sm" />
                        <span :class="`text-${trendColor}`">
                            {{ trend.value }}{{ trendUnit }}
                        </span>
                    </div>
                </div>
            </div>
            <div class="stats-decoration">
                <q-icon :name="icon" size="64px" class="decoration-icon" />
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
    // 蓝白科技感卡片设计
    background: rgba(255, 255, 255, 0.98);
    box-shadow:
        0 8px 32px rgba(14, 165, 233, 0.08),
        0 2px 8px rgba(59, 130, 246, 0.05),
        inset 0 1px 0 rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(20px);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
    position: relative;
    height: 140px;

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

    .q-card__section {
        padding: 20px;
        height: 100%;
    }
}

.stats-content {
    display: flex;
    align-items: center;
    gap: 16px;
    z-index: 2;
    position: relative;
}

.stats-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--icon-bg);
    color: var(--icon-color);
    box-shadow: 0 4px 12px var(--icon-shadow);
}

.stats-info {
    flex: 1;
}

.stats-title {
    font-size: 14px;
    color: #666;
    margin-bottom: 4px;
    font-weight: 500;
}

.stats-value {
    font-size: 24px;
    font-weight: bold;
    color: #333;
    margin-bottom: 4px;
}

.stats-trend {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    font-weight: 500;
}

.stats-decoration {
    position: absolute;
    right: -10px;
    top: 50%;
    transform: translateY(-50%);
    opacity: 0.1;
    z-index: 1;
}

.decoration-icon {
    color: var(--decoration-color);
}

// 蓝白科技感颜色主题 - 统一使用蓝色系
.stats-card--blue {
    --card-gradient: #3b82f6, #1d4ed8;
    --icon-bg: rgba(59, 130, 246, 0.15);
    --icon-color: #3b82f6;
    --icon-shadow: rgba(59, 130, 246, 0.4);
    --decoration-color: #3b82f6;
}

.stats-card--orange {
    // 改为浅蓝色调
    --card-gradient: #0ea5e9, #0284c7;
    --icon-bg: rgba(14, 165, 233, 0.15);
    --icon-color: #0ea5e9;
    --icon-shadow: rgba(14, 165, 233, 0.4);
    --decoration-color: #0ea5e9;
}

.stats-card--green {
    // 改为青蓝色调
    --card-gradient: #06b6d4, #0891b2;
    --icon-bg: rgba(6, 182, 212, 0.15);
    --icon-color: #06b6d4;
    --icon-shadow: rgba(6, 182, 212, 0.4);
    --decoration-color: #06b6d4;
}

.stats-card--purple {
    // 改为深蓝色调
    --card-gradient: #1e40af, #1e3a8a;
    --icon-bg: rgba(30, 64, 175, 0.15);
    --icon-color: #1e40af;
    --icon-shadow: rgba(30, 64, 175, 0.4);
    --decoration-color: #1e40af;
}

.stats-card--red {
    // 改为中蓝色调
    --card-gradient: #2563eb, #1d4ed8;
    --icon-bg: rgba(37, 99, 235, 0.15);
    --icon-color: #2563eb;
    --icon-shadow: rgba(37, 99, 235, 0.4);
    --decoration-color: #2563eb;
}

// 响应式设计
@media (max-width: 768px) {
    .stats-card {
        height: auto;
        min-height: 120px;
    }

    .stats-content {
        gap: 12px;
    }

    .stats-icon {
        width: 40px;
        height: 40px;
    }

    .stats-value {
        font-size: 20px;
    }

    .decoration-icon {
        display: none;
    }
}
</style>

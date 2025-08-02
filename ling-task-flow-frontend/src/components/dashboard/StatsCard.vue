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
    border-radius: 16px;
    border: none;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    overflow: hidden;
    position: relative;
    height: 140px;

    &:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
    }

    &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--card-gradient));
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

// 颜色主题
.stats-card--blue {
    --card-gradient: #2196f3, #21cbf3;
    --icon-bg: rgba(33, 150, 243, 0.1);
    --icon-color: #2196f3;
    --icon-shadow: rgba(33, 150, 243, 0.3);
    --decoration-color: #2196f3;
}

.stats-card--orange {
    --card-gradient: #ff9800, #ffc107;
    --icon-bg: rgba(255, 152, 0, 0.1);
    --icon-color: #ff9800;
    --icon-shadow: rgba(255, 152, 0, 0.3);
    --decoration-color: #ff9800;
}

.stats-card--green {
    --card-gradient: #4caf50, #8bc34a;
    --icon-bg: rgba(76, 175, 80, 0.1);
    --icon-color: #4caf50;
    --icon-shadow: rgba(76, 175, 80, 0.3);
    --decoration-color: #4caf50;
}

.stats-card--purple {
    --card-gradient: #9c27b0, #e91e63;
    --icon-bg: rgba(156, 39, 176, 0.1);
    --icon-color: #9c27b0;
    --icon-shadow: rgba(156, 39, 176, 0.3);
    --decoration-color: #9c27b0;
}

.stats-card--red {
    --card-gradient: #f44336, #ff5722;
    --icon-bg: rgba(244, 67, 54, 0.1);
    --icon-color: #f44336;
    --icon-shadow: rgba(244, 67, 54, 0.3);
    --decoration-color: #f44336;
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

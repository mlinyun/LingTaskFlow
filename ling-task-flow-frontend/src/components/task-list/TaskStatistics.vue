<template>
    <div class="task-statistics">
        <div class="stats-container">
            <div class="stats-header">
                <div class="header-indicator">
                    <div class="indicator-dot active"></div>
                    <div class="indicator-dot"></div>
                    <div class="indicator-dot"></div>
                </div>
                <h3 class="stats-title">TASK_STATISTICS</h3>
                <div class="stats-underline"></div>
            </div>

            <div class="stats-grid">
                <div class="stat-card total">
                    <div class="stat-icon">
                        <q-icon name="assignment" size="24px" />
                    </div>
                    <div class="stat-content">
                        <span class="stat-label">TOTAL</span>
                        <span class="stat-value">{{ formatNumber(props.totalTasks) }}</span>
                        <div class="stat-indicator">
                            <div class="indicator-bar" :style="{ width: '100%' }"></div>
                        </div>
                    </div>
                    <div class="stat-glow"></div>
                </div>

                <div class="stat-card active">
                    <div class="stat-icon">
                        <q-icon name="play_arrow" size="24px" />
                    </div>
                    <div class="stat-content">
                        <span class="stat-label">ACTIVE</span>
                        <span class="stat-value">{{ formatNumber(props.activeTasks) }}</span>
                        <div class="stat-indicator">
                            <div
                                class="indicator-bar"
                                :style="{
                                    width: getPercentage(props.activeTasks, props.totalTasks) + '%',
                                }"
                            ></div>
                        </div>
                    </div>
                    <div class="stat-glow"></div>
                </div>

                <div class="stat-card completed">
                    <div class="stat-icon">
                        <q-icon name="check_circle" size="24px" />
                    </div>
                    <div class="stat-content">
                        <span class="stat-label">已完成</span>
                        <span class="stat-value">{{ formatNumber(props.completedTasks) }}</span>
                        <div class="stat-indicator">
                            <div
                                class="indicator-bar"
                                :style="{
                                    width:
                                        getPercentage(props.completedTasks, props.totalTasks) + '%',
                                }"
                            ></div>
                        </div>
                    </div>
                    <div class="stat-glow"></div>
                </div>

                <div class="stat-card selected" v-if="props.selectedTasks > 0">
                    <div class="stat-icon">
                        <q-icon name="check_box" size="24px" />
                    </div>
                    <div class="stat-content">
                        <span class="stat-label">SELECTED</span>
                        <span class="stat-value">{{ formatNumber(props.selectedTasks) }}</span>
                        <div class="stat-indicator">
                            <div
                                class="indicator-bar"
                                :style="{
                                    width:
                                        getPercentage(props.selectedTasks, props.activeTasks) + '%',
                                }"
                            ></div>
                        </div>
                    </div>
                    <div class="stat-glow"></div>
                </div>
            </div>

            <!-- 数据流动效果 -->
            <div class="data-stream">
                <div class="stream-line" v-for="i in 3" :key="i"></div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
// Props
interface Props {
    totalTasks: number;
    activeTasks: number;
    completedTasks: number;
    selectedTasks?: number;
}

const props = withDefaults(defineProps<Props>(), {
    selectedTasks: 0,
});

// 格式化数字显示
const formatNumber = (num: number): string => {
    return String(num).padStart(3, '0');
};

// 计算百分比
const getPercentage = (value: number, total: number): number => {
    if (total === 0) return 0;
    return Math.round((value / total) * 100);
};
</script>

<style scoped lang="scss">
.task-statistics {
    margin-bottom: 1.5rem;

    .stats-container {
        position: relative;
        background: linear-gradient(
            135deg,
            rgba(59, 130, 246, 0.05) 0%,
            rgba(14, 165, 233, 0.03) 50%,
            rgba(6, 182, 212, 0.05) 100%
        );
        border: 1px solid rgba(59, 130, 246, 0.15);
        border-radius: 16px;
        padding: 1.5rem;
        overflow: hidden;
        backdrop-filter: blur(10px);
        box-shadow:
            0 8px 24px rgba(59, 130, 246, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);

        // 背景网格
        &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image:
                linear-gradient(rgba(59, 130, 246, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(59, 130, 246, 0.03) 1px, transparent 1px);
            background-size: 20px 20px;
            pointer-events: none;
            animation: gridFlow 20s linear infinite;
        }

        .stats-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1.5rem;
            position: relative;
            z-index: 2;

            .header-indicator {
                display: flex;
                gap: 0.25rem;

                .indicator-dot {
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: rgba(59, 130, 246, 0.3);
                    transition: all 0.3s ease;

                    &.active {
                        background: #3b82f6;
                        box-shadow: 0 0 8px rgba(59, 130, 246, 0.6);
                        animation: dotPulse 2s ease-in-out infinite;
                    }
                }
            }

            .stats-title {
                font-family: 'Courier New', monospace;
                font-size: 1rem;
                font-weight: 700;
                color: #3b82f6;
                letter-spacing: 1px;
                margin: 0;
                text-shadow: 0 0 8px rgba(59, 130, 246, 0.3);
            }

            .stats-underline {
                flex: 1;
                height: 1px;
                background: linear-gradient(
                    90deg,
                    rgba(59, 130, 246, 0.3) 0%,
                    rgba(59, 130, 246, 0.1) 50%,
                    transparent 100%
                );
                position: relative;

                &::after {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 30px;
                    height: 1px;
                    background: #3b82f6;
                    animation: underlineScan 3s ease-in-out infinite;
                }
            }
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            position: relative;
            z-index: 2;

            .stat-card {
                position: relative;
                background: rgba(255, 255, 255, 0.7);
                border: 1px solid rgba(59, 130, 246, 0.1);
                border-radius: 12px;
                padding: 1rem;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                overflow: hidden;
                backdrop-filter: blur(5px);

                &:hover {
                    transform: translateY(-2px);
                    border-color: rgba(59, 130, 246, 0.2);
                    box-shadow: 0 8px 24px rgba(59, 130, 246, 0.15);

                    .stat-glow {
                        opacity: 1;
                    }
                }

                .stat-icon {
                    position: absolute;
                    top: 0.75rem;
                    right: 0.75rem;
                    opacity: 0.1;
                    transition: all 0.3s ease;
                }

                .stat-content {
                    position: relative;
                    z-index: 2;

                    .stat-label {
                        display: block;
                        font-family: 'Courier New', monospace;
                        font-size: 0.7rem;
                        color: #64748b;
                        letter-spacing: 1px;
                        margin-bottom: 0.5rem;
                        font-weight: 500;
                        text-transform: uppercase;
                    }

                    .stat-value {
                        display: block;
                        font-family: 'Courier New', monospace;
                        font-size: 1.5rem;
                        font-weight: 700;
                        margin-bottom: 0.75rem;
                        transition: all 0.3s ease;
                    }

                    .stat-indicator {
                        position: relative;
                        width: 100%;
                        height: 3px;
                        background: rgba(59, 130, 246, 0.1);
                        border-radius: 2px;
                        overflow: hidden;

                        .indicator-bar {
                            height: 100%;
                            border-radius: 2px;
                            transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1);
                            position: relative;

                            &::after {
                                content: '';
                                position: absolute;
                                top: 0;
                                left: 0;
                                right: 0;
                                bottom: 0;
                                background: linear-gradient(
                                    90deg,
                                    transparent 0%,
                                    rgba(255, 255, 255, 0.3) 50%,
                                    transparent 100%
                                );
                                animation: indicatorShine 2s ease-in-out infinite;
                            }
                        }
                    }
                }

                .stat-glow {
                    position: absolute;
                    top: -2px;
                    left: -2px;
                    right: -2px;
                    bottom: -2px;
                    background: linear-gradient(
                        45deg,
                        transparent,
                        rgba(59, 130, 246, 0.1),
                        transparent
                    );
                    border-radius: 14px;
                    opacity: 0;
                    transition: opacity 0.3s ease;
                    pointer-events: none;
                }

                // 不同类型的统计卡片样式
                &.total {
                    .stat-value {
                        color: #3b82f6;
                        text-shadow: 0 0 8px rgba(59, 130, 246, 0.3);
                    }
                    .stat-indicator .indicator-bar {
                        background: linear-gradient(90deg, #3b82f6, #2563eb);
                    }
                    .stat-icon {
                        color: #3b82f6;
                    }
                }

                &.active {
                    .stat-value {
                        color: #0ea5e9;
                        text-shadow: 0 0 8px rgba(14, 165, 233, 0.3);
                    }
                    .stat-indicator .indicator-bar {
                        background: linear-gradient(90deg, #0ea5e9, #0284c7);
                    }
                    .stat-icon {
                        color: #0ea5e9;
                    }
                }

                &.completed {
                    .stat-value {
                        color: #10b981;
                        text-shadow: 0 0 8px rgba(16, 185, 129, 0.3);
                    }
                    .stat-indicator .indicator-bar {
                        background: linear-gradient(90deg, #10b981, #059669);
                    }
                    .stat-icon {
                        color: #10b981;
                    }
                }

                &.selected {
                    .stat-value {
                        color: #f59e0b;
                        text-shadow: 0 0 8px rgba(245, 158, 11, 0.3);
                    }
                    .stat-indicator .indicator-bar {
                        background: linear-gradient(90deg, #f59e0b, #d97706);
                    }
                    .stat-icon {
                        color: #f59e0b;
                    }
                    animation: selectedPulse 2s ease-in-out infinite;
                }
            }
        }

        .data-stream {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            pointer-events: none;
            z-index: 1;

            .stream-line {
                position: absolute;
                width: 2px;
                height: 100%;
                background: linear-gradient(
                    180deg,
                    transparent 0%,
                    rgba(59, 130, 246, 0.3) 50%,
                    transparent 100%
                );
                opacity: 0;
                animation: streamFlow 4s ease-in-out infinite;

                &:nth-child(1) {
                    left: 20%;
                    animation-delay: 0s;
                }

                &:nth-child(2) {
                    left: 50%;
                    animation-delay: 1.3s;
                }

                &:nth-child(3) {
                    left: 80%;
                    animation-delay: 2.6s;
                }
            }
        }
    }
}

// 动画定义
@keyframes gridFlow {
    0% {
        transform: translate(0, 0);
    }
    100% {
        transform: translate(20px, 20px);
    }
}

@keyframes dotPulse {
    0%,
    100% {
        transform: scale(1);
        opacity: 1;
    }
    50% {
        transform: scale(1.2);
        opacity: 0.8;
    }
}

@keyframes underlineScan {
    0% {
        left: 0;
        opacity: 1;
    }
    50% {
        left: calc(50% - 15px);
        opacity: 0.5;
    }
    100% {
        left: calc(100% - 30px);
        opacity: 0;
    }
}

@keyframes indicatorShine {
    0% {
        transform: translateX(-100%);
    }
    50% {
        transform: translateX(0%);
    }
    100% {
        transform: translateX(100%);
    }
}

@keyframes streamFlow {
    0% {
        opacity: 0;
        transform: translateY(-20px);
    }
    20% {
        opacity: 1;
        transform: translateY(0);
    }
    80% {
        opacity: 1;
        transform: translateY(calc(100% - 20px));
    }
    100% {
        opacity: 0;
        transform: translateY(100%);
    }
}

@keyframes selectedPulse {
    0%,
    100% {
        box-shadow: 0 0 0 rgba(245, 158, 11, 0);
    }
    50% {
        box-shadow: 0 0 20px rgba(245, 158, 11, 0.3);
    }
}

// 响应式设计
@media (max-width: 768px) {
    .task-statistics {
        .stats-container {
            padding: 1rem;

            .stats-header {
                margin-bottom: 1rem;

                .stats-title {
                    font-size: 0.9rem;
                }
            }

            .stats-grid {
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 0.75rem;

                .stat-card {
                    padding: 0.75rem;

                    .stat-content {
                        .stat-value {
                            font-size: 1.25rem;
                        }
                    }
                }
            }
        }
    }
}

@media (max-width: 480px) {
    .task-statistics {
        .stats-container {
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);

                .stat-card {
                    .stat-content {
                        .stat-label {
                            font-size: 0.6rem;
                        }

                        .stat-value {
                            font-size: 1.1rem;
                        }
                    }
                }
            }
        }
    }
}
</style>

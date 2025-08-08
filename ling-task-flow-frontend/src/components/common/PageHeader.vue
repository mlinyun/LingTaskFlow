<template>
    <div class="page-header">
        <div class="header-background">
            <div class="tech-grid"></div>
            <div class="floating-particles">
                <div class="particle"></div>
                <div class="particle"></div>
                <div class="particle"></div>
                <div class="particle"></div>
            </div>
        </div>

        <div class="header-content">
            <div class="title-section">
                <div class="title-container">
                    <div class="icon-wrapper">
                        <q-icon :name="icon" size="24px" class="title-icon" />
                        <div class="icon-glow"></div>
                    </div>
                    <div class="title-text">
                        <h1 class="page-title">
                            <span class="title-primary">{{ titlePrimary }}</span>
                            <span class="title-accent">{{ titleAccent }}</span>
                        </h1>
                        <p class="page-subtitle">
                            <q-icon name="insights" size="14px" class="q-mr-xs" />
                            {{ formatDate(new Date()) }} {{ subtitle }}
                        </p>
                    </div>
                </div>
            </div>

            <div class="action-section">
                <div class="action-buttons">
                    <!-- 主要操作按钮（如果提供） -->
                    <q-btn
                        v-if="primaryAction"
                        :icon="primaryAction.icon"
                        :label="primaryAction.label"
                        class="refresh-btn"
                        rounded
                        :loading="primaryAction.loading"
                        @click="$emit('primary-action')"
                    />

                    <!-- 次要操作按钮 -->
                    <q-btn
                        v-for="action in secondaryActions"
                        :key="action.name"
                        :icon="action.icon"
                        :class="action.class || 'fullscreen-btn'"
                        flat
                        round
                        @click="$emit('secondary-action', action.name)"
                    >
                        <q-tooltip v-if="action.tooltip">{{ action.tooltip }}</q-tooltip>
                    </q-btn>
                </div>
            </div>
        </div>

        <!-- 底部装饰线 - 重新设计为更科技感的效果 -->
        <div class="header-decoration">
            <div class="deco-border-glow"></div>
            <div class="deco-particles">
                <div class="deco-particle"></div>
                <div class="deco-particle"></div>
                <div class="deco-particle"></div>
                <div class="deco-particle"></div>
                <div class="deco-particle"></div>
            </div>
            <div class="deco-pulse-line"></div>
        </div>
    </div>
</template>

<script setup lang="ts">
interface SecondaryAction {
    name: string;
    icon: string;
    tooltip?: string;
    class?: string;
}

interface PrimaryAction {
    icon: string;
    label: string;
    loading?: boolean;
}

interface Props {
    icon: string;
    titlePrimary: string;
    titleAccent?: string;
    subtitle: string;
    primaryAction?: PrimaryAction;
    secondaryActions?: SecondaryAction[];
}

interface Emits {
    (e: 'primary-action'): void;
    (e: 'secondary-action', actionName: string): void;
}

withDefaults(defineProps<Props>(), {
    titleAccent: '',
    secondaryActions: () => [],
});

defineEmits<Emits>();

// 日期格式化函数
const formatDate = (date: Date): string => {
    const options: Intl.DateTimeFormatOptions = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long',
    };
    return new Intl.DateTimeFormat('zh-CN', options).format(date);
};
</script>

<style scoped lang="scss">
// 页面头部设计 - 与Dashboard保持一致
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
                linear-gradient(rgba(59, 130, 246, 0.06) 1px, transparent 1px),
                linear-gradient(90deg, rgba(59, 130, 246, 0.06) 1px, transparent 1px);
            background-size: 30px 30px;
            animation: gridMove 30s linear infinite;
        }

        .floating-particles {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;

            .particle {
                position: absolute;
                width: 6px;
                height: 6px;
                background: radial-gradient(
                    circle,
                    rgba(59, 130, 246, 0.8) 0%,
                    rgba(59, 130, 246, 0.4) 50%,
                    transparent 100%
                );
                border-radius: 50%;
                animation: float 12s ease-in-out infinite;

                &:nth-child(1) {
                    top: 15%;
                    left: 10%;
                    animation-delay: 0s;
                    animation-duration: 12s;
                }

                &:nth-child(2) {
                    top: 70%;
                    left: 75%;
                    animation-delay: 3s;
                    animation-duration: 15s;
                }

                &:nth-child(3) {
                    top: 30%;
                    left: 80%;
                    animation-delay: 6s;
                    animation-duration: 18s;
                }

                &:nth-child(4) {
                    top: 60%;
                    left: 20%;
                    animation-delay: 9s;
                    animation-duration: 14s;
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
                gap: 1rem;

                .icon-wrapper {
                    position: relative;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 48px;
                    height: 48px;
                    background: linear-gradient(
                        135deg,
                        rgba(59, 130, 246, 0.15),
                        rgba(14, 165, 233, 0.1)
                    );
                    border-radius: 12px;
                    border: 1px solid rgba(59, 130, 246, 0.2);

                    .title-icon {
                        color: #3b82f6;
                        z-index: 2;
                    }

                    .icon-glow {
                        position: absolute;
                        top: 50%;
                        left: 50%;
                        transform: translate(-50%, -50%);
                        width: 32px;
                        height: 32px;
                        background: radial-gradient(
                            circle,
                            rgba(59, 130, 246, 0.4) 0%,
                            rgba(59, 130, 246, 0.2) 50%,
                            transparent 100%
                        );
                        border-radius: 50%;
                        animation: pulse 3s ease-in-out infinite;
                    }
                }

                .title-text {
                    .page-title {
                        margin: 0;
                        font-size: 1.75rem;
                        font-weight: 700;
                        line-height: 1.2;
                        display: flex;
                        flex-direction: row; /* 横向排列 */
                        align-items: baseline; /* 不同字号基线对齐 */
                        gap: 0.5rem; /* 主副标题间距 */
                        flex-wrap: wrap; /* 窄屏时允许换行 */

                        .title-primary {
                            background: linear-gradient(135deg, #1e293b, #475569);
                            background-clip: text;
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                        }

                        .title-accent {
                            font-size: 0.85rem;
                            font-weight: 600;
                            color: #2563eb;
                            text-transform: uppercase;
                            letter-spacing: 0.12em;
                            padding: 0.15rem 0.5rem;
                            border: 1px solid rgba(59, 130, 246, 0.3);
                            background: rgba(59, 130, 246, 0.08);
                            border-radius: 999px; /* 胶囊形状 */
                            line-height: 1.1;
                        }
                    }

                    .page-subtitle {
                        margin: 0.5rem 0 0;
                        color: #64748b;
                        font-size: 0.875rem;
                        font-weight: 500;
                        display: flex;
                        align-items: center;
                        gap: 0.25rem;
                    }
                }
            }
        }

        .action-section {
            .action-buttons {
                display: flex;
                align-items: center;
                gap: 0.75rem;

                .refresh-btn {
                    background: linear-gradient(135deg, #3b82f6, #2563eb);
                    color: white;
                    border: none;
                    padding: 0.75rem 1.5rem;
                    font-weight: 600;
                    box-shadow: 0 4px 16px rgba(59, 130, 246, 0.3);
                    transition: all 0.3s ease;

                    &:hover {
                        transform: translateY(-1px);
                        box-shadow: 0 6px 24px rgba(59, 130, 246, 0.4);
                    }
                }

                .fullscreen-btn,
                .download-btn {
                    width: 40px;
                    height: 40px;
                    background: rgba(255, 255, 255, 0.8);
                    color: #64748b;
                    border: 1px solid rgba(59, 130, 246, 0.1);
                    backdrop-filter: blur(10px);
                    transition: all 0.3s ease;

                    &:hover {
                        background: rgba(59, 130, 246, 0.1);
                        color: #3b82f6;
                        border-color: rgba(59, 130, 246, 0.3);
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
        height: 3px;
        overflow: hidden;

        // 发光边框效果
        .deco-border-glow {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, #3b82f6, transparent);
            opacity: 0.6;
            animation: borderPulse 3s ease-in-out infinite;
        }

        // 流动粒子效果
        .deco-particles {
            position: absolute;
            bottom: 2px;
            left: 0;
            right: 0;
            height: 4px;

            .deco-particle {
                position: absolute;
                width: 3px;
                height: 3px;
                background: #3b82f6;
                border-radius: 50%;
                opacity: 0;
                animation: particleFlow 4s linear infinite;

                &:nth-child(1) {
                    left: 0%;
                    animation-delay: 0s;
                }

                &:nth-child(2) {
                    left: 20%;
                    animation-delay: 0.8s;
                }

                &:nth-child(3) {
                    left: 40%;
                    animation-delay: 1.6s;
                }

                &:nth-child(4) {
                    left: 60%;
                    animation-delay: 2.4s;
                }

                &:nth-child(5) {
                    left: 80%;
                    animation-delay: 3.2s;
                }
            }
        }

        // 脉冲扫描线
        .deco-pulse-line {
            position: absolute;
            bottom: 0;
            left: -100px;
            width: 100px;
            height: 6px;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(59, 130, 246, 0.8),
                rgba(59, 130, 246, 1),
                rgba(59, 130, 246, 0.8),
                transparent
            );
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

@keyframes borderPulse {
    0%,
    100% {
        opacity: 0.6;
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.3);
    }
    50% {
        opacity: 1;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.6);
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

// 响应式设计
@media (max-width: 768px) {
    .page-header {
        padding: 1.5rem;
        margin-bottom: 1.5rem;

        .header-content {
            flex-direction: column;
            gap: 1.5rem;
            align-items: stretch;

            .title-section .title-container {
                .title-text .page-title {
                    font-size: 1.5rem;
                    gap: 0.4rem;
                }
            }

            .action-section .action-buttons {
                justify-content: center;
            }
        }
    }
}

@media (max-width: 480px) {
    .page-header {
        padding: 1rem;
        border-radius: 16px;

        .header-content {
            .title-section .title-container {
                .icon-wrapper {
                    width: 40px;
                    height: 40px;
                }

                .title-text .page-title {
                    font-size: 1.25rem;
                }
            }

            .action-section .action-buttons {
                .refresh-btn {
                    padding: 0.5rem 1rem;
                    font-size: 0.875rem;
                }
            }
        }
    }
}
</style>

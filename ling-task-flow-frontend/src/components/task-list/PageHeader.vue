<template>
    <div class="page-header">
        <!-- 科技感背景 -->
        <div class="header-background">
            <div class="tech-grid"></div>
            <div class="floating-particles">
                <div class="particle" v-for="i in 4" :key="i"></div>
            </div>
        </div>

        <!-- 头部内容 -->
        <div class="header-content">
            <!-- 标题区域 -->
            <div class="title-section">
                <div class="title-container">
                    <div class="icon-wrapper">
                        <q-icon :name="icon" size="32px" class="title-icon" />
                        <div class="icon-glow"></div>
                    </div>
                    <div class="title-text">
                        <h1 class="page-title">
                            <span class="title-primary">{{ titlePrimary }}</span>
                            <span class="title-accent">{{ titleAccent }}</span>
                        </h1>
                        <p class="page-subtitle">
                            <q-icon name="trending_up" size="14px" class="q-mr-xs" />
                            {{ subtitle }}
                        </p>
                    </div>
                </div>
            </div>

            <!-- 操作区域 -->
            <div class="action-section">
                <div class="action-buttons">
                    <!-- 主要操作按钮 -->
                    <q-btn
                        color="primary"
                        :icon="primaryAction.icon"
                        :label="primaryAction.label"
                        unelevated
                        rounded
                        size="md"
                        class="create-btn"
                        @click="$emit('primaryAction')"
                    >
                        <q-tooltip anchor="bottom middle" self="top middle" :offset="[0, 8]">
                            {{ primaryAction.tooltip }}
                        </q-tooltip>
                    </q-btn>

                    <!-- 次要操作按钮 -->
                    <q-btn
                        v-for="action in secondaryActions"
                        :key="action.name"
                        flat
                        round
                        :icon="action.icon"
                        color="primary"
                        size="md"
                        :class="action.class"
                        @click="$emit('secondaryAction', action.name)"
                    >
                        <q-tooltip anchor="bottom middle" self="top middle" :offset="[0, 8]">
                            {{ action.tooltip }}
                        </q-tooltip>
                    </q-btn>
                </div>
            </div>
        </div>

        <!-- 底部装饰线 -->
        <div class="header-decoration">
            <div class="deco-border-glow"></div>
            <div class="deco-particles">
                <div class="deco-particle" v-for="i in 3" :key="i"></div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
interface SecondaryAction {
    name: string;
    icon: string;
    tooltip: string;
    class?: string;
}

interface PrimaryAction {
    icon: string;
    label: string;
    tooltip: string;
}

interface Props {
    icon?: string;
    titlePrimary: string;
    titleAccent?: string;
    subtitle: string;
    primaryAction: PrimaryAction;
    secondaryActions?: SecondaryAction[];
}

interface Emits {
    (e: 'primaryAction'): void;
    (e: 'secondaryAction', actionName: string): void;
}

withDefaults(defineProps<Props>(), {
    icon: 'assignment',
    titleAccent: '',
    secondaryActions: () => [],
});

defineEmits<Emits>();
</script>

<style scoped>
.page-header {
    position: relative;
    background: linear-gradient(135deg, #1e293b 0%, #334155 50%, #1e293b 100%);
    overflow: hidden;
    border-radius: 12px;
    margin-bottom: 24px;
    box-shadow:
        0 8px 32px rgba(0, 0, 0, 0.3),
        0 2px 8px rgba(0, 0, 0, 0.2),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

/* 科技感背景 */
.header-background {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    opacity: 0.6;
    overflow: hidden;
}

.tech-grid {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image:
        linear-gradient(rgba(59, 130, 246, 0.1) 1px, transparent 1px),
        linear-gradient(90deg, rgba(59, 130, 246, 0.1) 1px, transparent 1px);
    background-size: 20px 20px;
    animation: grid-shift 20s linear infinite;
}

.floating-particles {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
}

.particle {
    position: absolute;
    width: 4px;
    height: 4px;
    background: radial-gradient(circle, #3b82f6, transparent);
    border-radius: 50%;
    animation: float-particle 8s ease-in-out infinite;
}

.particle:nth-child(1) {
    top: 20%;
    left: 10%;
    animation-delay: 0s;
    animation-duration: 8s;
}

.particle:nth-child(2) {
    top: 60%;
    left: 80%;
    animation-delay: 2s;
    animation-duration: 10s;
}

.particle:nth-child(3) {
    top: 30%;
    left: 70%;
    animation-delay: 4s;
    animation-duration: 12s;
}

.particle:nth-child(4) {
    top: 80%;
    left: 20%;
    animation-delay: 6s;
    animation-duration: 9s;
}

/* 头部内容 */
.header-content {
    position: relative;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 32px 24px;
    z-index: 2;
}

.title-section {
    flex: 1;
}

.title-container {
    display: flex;
    align-items: center;
    gap: 16px;
}

.icon-wrapper {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 56px;
    height: 56px;
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(99, 102, 241, 0.2));
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 12px;
    backdrop-filter: blur(10px);
}

.title-icon {
    color: #3b82f6;
    z-index: 1;
}

.icon-glow {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 40px;
    height: 40px;
    background: radial-gradient(circle, rgba(59, 130, 246, 0.4), transparent);
    border-radius: 50%;
    animation: icon-pulse 3s ease-in-out infinite;
}

.title-text {
    flex: 1;
}

.page-title {
    margin: 0 0 8px 0;
    font-size: 28px;
    font-weight: 700;
    line-height: 1.2;
    font-family: 'Rajdhani', 'PingFang SC', sans-serif;
}

.title-primary {
    color: #ffffff;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.title-accent {
    color: #3b82f6;
    text-shadow: 0 0 20px rgba(59, 130, 246, 0.5);
    margin-left: 8px;
}

.page-subtitle {
    margin: 0;
    font-size: 14px;
    color: rgba(255, 255, 255, 0.8);
    display: flex;
    align-items: center;
    gap: 4px;
}

/* 操作区域 */
.action-section {
    display: flex;
    align-items: center;
}

.action-buttons {
    display: flex;
    gap: 12px;
    align-items: center;
}

.create-btn {
    font-weight: 600;
    letter-spacing: 0.5px;
    padding: 12px 24px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow:
        0 4px 14px rgba(59, 130, 246, 0.3),
        0 2px 4px rgba(0, 0, 0, 0.2);
}

.create-btn:hover {
    transform: translateY(-2px);
    box-shadow:
        0 6px 20px rgba(59, 130, 246, 0.4),
        0 4px 8px rgba(0, 0, 0, 0.3);
}

.refresh-btn,
.filter-toggle-btn {
    width: 48px;
    height: 48px;
    border: 1px solid rgba(59, 130, 246, 0.2);
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(99, 102, 241, 0.1));
    backdrop-filter: blur(10px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.refresh-btn:hover,
.filter-toggle-btn:hover {
    border-color: rgba(59, 130, 246, 0.4);
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(99, 102, 241, 0.2));
    transform: translateY(-2px);
    box-shadow:
        0 4px 16px rgba(59, 130, 246, 0.3),
        0 2px 8px rgba(0, 0, 0, 0.2);
}

/* 底部装饰 */
.header-decoration {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 3px;
    overflow: hidden;
}

.deco-border-glow {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(
        90deg,
        transparent 0%,
        rgba(59, 130, 246, 0.5) 20%,
        rgba(59, 130, 246, 0.8) 50%,
        rgba(59, 130, 246, 0.5) 80%,
        transparent 100%
    );
    animation: border-glow 3s ease-in-out infinite;
}

.deco-particles {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
}

.deco-particle {
    position: absolute;
    bottom: 0;
    width: 2px;
    height: 2px;
    background: #3b82f6;
    border-radius: 50%;
    animation: deco-float 4s ease-in-out infinite;
}

.deco-particle:nth-child(1) {
    left: 20%;
    animation-delay: 0s;
}

.deco-particle:nth-child(2) {
    left: 50%;
    animation-delay: 1.5s;
}

.deco-particle:nth-child(3) {
    left: 80%;
    animation-delay: 3s;
}

/* 动画定义 */
@keyframes grid-shift {
    0% {
        transform: translate(0, 0);
    }
    100% {
        transform: translate(20px, 20px);
    }
}

@keyframes float-particle {
    0%,
    100% {
        transform: translateY(0px) scale(1);
        opacity: 0.6;
    }
    50% {
        transform: translateY(-20px) scale(1.2);
        opacity: 1;
    }
}

@keyframes icon-pulse {
    0%,
    100% {
        transform: translate(-50%, -50%) scale(1);
        opacity: 0.6;
    }
    50% {
        transform: translate(-50%, -50%) scale(1.2);
        opacity: 0.8;
    }
}

@keyframes border-glow {
    0%,
    100% {
        opacity: 0.6;
        transform: scaleX(1);
    }
    50% {
        opacity: 1;
        transform: scaleX(1.05);
    }
}

@keyframes deco-float {
    0%,
    100% {
        transform: translateY(0px);
        opacity: 0.8;
    }
    50% {
        transform: translateY(-8px);
        opacity: 1;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.6);
    }
}

/* 响应式设计 */
@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
        gap: 20px;
        padding: 24px 16px;
        text-align: center;
    }

    .title-container {
        justify-content: center;
    }

    .page-title {
        font-size: 24px;
    }

    .title-accent {
        display: block;
        margin-left: 0;
        margin-top: 4px;
    }

    .action-buttons {
        justify-content: center;
        flex-wrap: wrap;
    }

    .create-btn {
        order: -1;
        width: 100%;
        max-width: 200px;
    }
}

@media (max-width: 480px) {
    .page-title {
        font-size: 20px;
    }

    .page-subtitle {
        font-size: 13px;
        justify-content: center;
    }

    .action-buttons {
        gap: 8px;
    }

    .refresh-btn,
    .filter-toggle-btn {
        width: 44px;
        height: 44px;
    }
}
</style>

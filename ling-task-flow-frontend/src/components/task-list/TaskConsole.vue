<template>
    <div class="task-console">
        <!-- 控制台头部 -->
        <div class="console-header">
            <div class="header-grid-background"></div>
            <div class="header-content">
                <div class="console-title">
                    <div class="title-indicator">
                        <div class="indicator-dot active"></div>
                        <div class="indicator-dot"></div>
                        <div class="indicator-dot"></div>
                    </div>
                    <h2 class="title-text">任务智能控制台</h2>
                    <div class="title-underline"></div>
                </div>
                <div class="console-stats">
                    <div class="stat-item">
                        <span class="stat-label">总计</span>
                        <span class="stat-value">{{ String(totalTasks).padStart(3, '0') }}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">活跃</span>
                        <span class="stat-value">{{ String(activeTasks).padStart(3, '0') }}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">已选</span>
                        <span class="stat-value">{{ String(selectedTasks).padStart(3, '0') }}</span>
                    </div>
                </div>
                <div class="console-controls">
                    <div class="control-group">
                        <q-checkbox
                            :model-value="selectAll"
                            :indeterminate="indeterminate"
                            @update:model-value="$emit('select-all')"
                            class="cyber-checkbox"
                        />
                        <span class="control-label">全选</span>
                    </div>
                    <div class="view-switch">
                        <q-btn
                            flat
                            dense
                            :icon="viewMode === 'list' ? 'view_module' : 'view_list'"
                            @click="$emit('toggle-view-mode')"
                            class="cyber-btn"
                        >
                            <q-tooltip>{{
                                viewMode === 'list' ? '网格视图' : '列表视图'
                            }}</q-tooltip>
                        </q-btn>
                    </div>
                </div>
            </div>
            <div class="header-scan-line"></div>
        </div>

        <!-- 任务矩阵容器 -->
        <div class="task-matrix">
            <!-- 矩阵背景 -->
            <div class="matrix-background">
                <div class="matrix-grid"></div>
                <div class="matrix-nodes">
                    <div class="node" v-for="i in 12" :key="i"></div>
                </div>
                <div class="data-streams">
                    <div class="stream" v-for="i in 3" :key="i"></div>
                </div>
            </div>

            <!-- 加载状态 -->
            <div v-if="loading" class="matrix-loading">
                <div class="loading-container">
                    <div class="loading-spinner">
                        <div class="spinner-ring" v-for="i in 3" :key="i"></div>
                    </div>
                    <div class="loading-text">正在加载任务矩阵...</div>
                    <div class="loading-progress">
                        <div class="progress-bar"></div>
                    </div>
                </div>
            </div>

            <!-- 空状态 -->
            <div v-else-if="activeTasks === 0" class="matrix-empty">
                <div class="empty-terminal">
                    <div class="terminal-header">
                        <div class="terminal-dots">
                            <div class="dot red"></div>
                            <div class="dot yellow"></div>
                            <div class="dot green"></div>
                        </div>
                        <div class="terminal-title">任务终端</div>
                    </div>
                    <div class="terminal-content">
                        <div class="terminal-lines">
                            <div class="line">
                                <span class="prompt">root@system:~$</span>
                                <span class="command">ls -la /tasks/</span>
                            </div>
                            <div class="line">
                                <span class="output">total 0</span>
                            </div>
                            <div class="line">
                                <span class="prompt">root@system:~$</span>
                                <span class="command">echo "未找到任务"</span>
                            </div>
                            <div class="line">
                                <span class="output error">未找到任务</span>
                            </div>
                            <div class="line">
                                <span class="prompt">root@system:~$</span>
                                <span class="cursor">_</span>
                            </div>
                        </div>
                        <q-btn
                            color="primary"
                            icon="add_circle_outline"
                            label="初始化任务矩阵"
                            unelevated
                            class="cyber-create-btn"
                            @click="$emit('create-task')"
                        />
                    </div>
                </div>
            </div>

            <!-- 任务网格 -->
            <div v-else class="task-grid-container" :class="`mode-${viewMode}`">
                <!-- 拖拽区域 -->
                <div class="drag-zone" id="task-drag-zone">
                    <!-- 拖拽指示线 -->
                    <div class="drag-indicator-line" id="drag-line"></div>

                    <!-- 任务卡片插槽 -->
                    <slot name="task-cards"></slot>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
interface Props {
    totalTasks: number;
    activeTasks: number;
    selectedTasks: number;
    selectAll: boolean;
    indeterminate: boolean;
    viewMode: 'list' | 'grid';
    loading: boolean;
}

interface Emits {
    (e: 'select-all'): void;
    (e: 'toggle-view-mode'): void;
    (e: 'create-task'): void;
}

defineProps<Props>();
defineEmits<Emits>();
</script>

<style scoped lang="scss">
// 科技感任务控制台样式
.task-console {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow:
        0 20px 60px rgba(14, 165, 233, 0.08),
        0 8px 24px rgba(59, 130, 246, 0.06),
        inset 0 1px 0 rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(59, 130, 246, 0.15);
    position: relative;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(20px);

    .console-header {
        background: linear-gradient(
            135deg,
            rgba(59, 130, 246, 0.08) 0%,
            rgba(14, 165, 233, 0.05) 50%,
            rgba(6, 182, 212, 0.08) 100%
        );
        padding: 1.5rem;
        position: relative;
        border-bottom: 1px solid rgba(59, 130, 246, 0.15);

        .header-content {
            position: relative;
            z-index: 2;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 2rem;

            .console-title {
                flex: 1;

                .title-indicator {
                    display: flex;
                    gap: 0.5rem;
                    margin-bottom: 0.5rem;

                    .indicator-dot {
                        width: 8px;
                        height: 8px;
                        border-radius: 50%;
                        background: rgba(100, 116, 139, 0.5);
                        animation: dotPulse 2s ease-in-out infinite;

                        &.active {
                            background: #3b82f6;
                            box-shadow: 0 0 8px rgba(59, 130, 246, 0.6);
                        }
                    }
                }

                .title-text {
                    font-family: 'Courier New', monospace;
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: #1e40af;
                    text-shadow: 0 0 10px rgba(30, 64, 175, 0.3);
                    letter-spacing: 2px;
                    margin: 0 0 0.5rem 0;
                }

                .title-underline {
                    height: 2px;
                    background: linear-gradient(90deg, #1e40af 0%, #3b82f6 50%, transparent 100%);
                    border-radius: 1px;
                    box-shadow: 0 0 4px rgba(30, 64, 175, 0.4);
                }
            }

            .console-stats {
                display: flex;
                gap: 2rem;

                .stat-item {
                    text-align: center;

                    .stat-label {
                        display: block;
                        font-family: 'Courier New', monospace;
                        font-size: 0.75rem;
                        color: #64748b;
                        letter-spacing: 1px;
                        margin-bottom: 0.25rem;
                    }

                    .stat-value {
                        font-family: 'Courier New', monospace;
                        font-size: 1.25rem;
                        font-weight: 700;
                        color: #3b82f6;
                        text-shadow: 0 0 8px rgba(59, 130, 246, 0.4);
                    }
                }
            }

            .console-controls {
                display: flex;
                align-items: center;
                gap: 1.5rem;

                .control-group {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;

                    .control-label {
                        font-family: 'Courier New', monospace;
                        font-size: 0.75rem;
                        color: #94a3b8;
                        letter-spacing: 1px;
                    }
                }

                .view-switch .cyber-btn {
                    background: rgba(59, 130, 246, 0.1);
                    border: 1px solid rgba(59, 130, 246, 0.3);
                    color: #3b82f6;
                    border-radius: 6px;
                    transition: all 0.3s ease;

                    &:hover {
                        background: rgba(59, 130, 246, 0.2);
                        box-shadow: 0 0 12px rgba(59, 130, 246, 0.3);
                        transform: translateY(-1px);
                    }
                }
            }
        }

        .header-scan-line {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(
                90deg,
                transparent 0%,
                rgba(59, 130, 246, 0.6) 50%,
                transparent 100%
            );
            animation: scanLine 3s linear infinite;
        }
    }

    .task-matrix {
        position: relative;
        min-height: 400px;

        .matrix-background {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            pointer-events: none;
            z-index: 1;

            .matrix-grid {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-image:
                    linear-gradient(rgba(59, 130, 246, 0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(59, 130, 246, 0.03) 1px, transparent 1px);
                background-size: 40px 40px;
                animation: matrixMove 20s linear infinite;
            }

            .matrix-nodes {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;

                .node {
                    position: absolute;
                    width: 4px;
                    height: 4px;
                    background: rgba(59, 130, 246, 0.4);
                    border-radius: 50%;
                    animation: nodeGlow 3s ease-in-out infinite;

                    &:nth-child(1) {
                        top: 10%;
                        left: 10%;
                        animation-delay: 0s;
                    }
                    &:nth-child(2) {
                        top: 20%;
                        left: 90%;
                        animation-delay: 0.5s;
                    }
                    &:nth-child(3) {
                        top: 40%;
                        left: 70%;
                        animation-delay: 1s;
                    }
                    &:nth-child(4) {
                        top: 60%;
                        left: 20%;
                        animation-delay: 1.5s;
                    }
                    &:nth-child(5) {
                        top: 80%;
                        left: 80%;
                        animation-delay: 2s;
                    }
                    &:nth-child(6) {
                        top: 30%;
                        left: 50%;
                        animation-delay: 2.5s;
                    }
                    &:nth-child(7) {
                        top: 70%;
                        left: 40%;
                        animation-delay: 3s;
                    }
                    &:nth-child(8) {
                        top: 15%;
                        left: 60%;
                        animation-delay: 3.5s;
                    }
                    &:nth-child(9) {
                        top: 85%;
                        left: 30%;
                        animation-delay: 4s;
                    }
                    &:nth-child(10) {
                        top: 50%;
                        left: 10%;
                        animation-delay: 4.5s;
                    }
                    &:nth-child(11) {
                        top: 25%;
                        left: 75%;
                        animation-delay: 5s;
                    }
                    &:nth-child(12) {
                        top: 75%;
                        left: 60%;
                        animation-delay: 5.5s;
                    }
                }
            }

            .data-streams {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;

                .stream {
                    position: absolute;
                    width: 2px;
                    height: 100%;
                    background: linear-gradient(
                        to bottom,
                        transparent 0%,
                        rgba(59, 130, 246, 0.3) 50%,
                        transparent 100%
                    );
                    animation: streamFlow 8s linear infinite;

                    &:nth-child(1) {
                        left: 25%;
                        animation-delay: 0s;
                    }
                    &:nth-child(2) {
                        left: 50%;
                        animation-delay: 2s;
                    }
                    &:nth-child(3) {
                        left: 75%;
                        animation-delay: 4s;
                    }
                }
            }
        }

        .matrix-loading {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 400px;
            padding: 3rem;
            position: relative;
            z-index: 2;

            .loading-container {
                text-align: center;

                .loading-spinner {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin-bottom: 2rem;

                    .spinner-ring {
                        width: 40px;
                        height: 40px;
                        border: 3px solid rgba(59, 130, 246, 0.1);
                        border-top: 3px solid #3b82f6;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                        margin: 0 5px;

                        &:nth-child(2) {
                            animation-delay: 0.3s;
                            width: 30px;
                            height: 30px;
                        }

                        &:nth-child(3) {
                            animation-delay: 0.6s;
                            width: 20px;
                            height: 20px;
                        }
                    }
                }

                .loading-text {
                    font-family: 'Courier New', monospace;
                    font-size: 1.1rem;
                    color: #3b82f6;
                    letter-spacing: 2px;
                    margin-bottom: 1rem;
                }

                .loading-progress {
                    width: 300px;
                    height: 4px;
                    background: rgba(59, 130, 246, 0.1);
                    border-radius: 2px;
                    overflow: hidden;
                    margin: 0 auto;

                    .progress-bar {
                        height: 100%;
                        background: linear-gradient(90deg, #3b82f6, #1d4ed8);
                        border-radius: 2px;
                        animation: progressMove 2s ease-in-out infinite;
                    }
                }
            }
        }

        .matrix-empty {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 400px;
            padding: 3rem;
            position: relative;
            z-index: 2;

            .empty-terminal {
                background: #f8fafc;
                border-radius: 8px;
                border: 1px solid rgba(59, 130, 246, 0.2);
                width: 100%;
                max-width: 600px;
                box-shadow: 0 10px 30px rgba(59, 130, 246, 0.1);

                .terminal-header {
                    display: flex;
                    align-items: center;
                    padding: 0.75rem 1rem;
                    background: white;
                    border-bottom: 1px solid rgba(59, 130, 246, 0.15);

                    .terminal-dots {
                        display: flex;
                        gap: 0.5rem;

                        .dot {
                            width: 12px;
                            height: 12px;
                            border-radius: 50%;

                            &.red {
                                background: #ef4444;
                            }
                            &.yellow {
                                background: #f59e0b;
                            }
                            &.green {
                                background: #10b981;
                            }
                        }
                    }

                    .terminal-title {
                        font-family: 'Courier New', monospace;
                        font-size: 0.875rem;
                        color: #9ca3af;
                        margin-left: 1rem;
                        letter-spacing: 1px;
                    }
                }

                .terminal-content {
                    padding: 1.5rem;

                    .terminal-lines {
                        margin-bottom: 2rem;

                        .line {
                            font-family: 'Courier New', monospace;
                            font-size: 0.875rem;
                            margin-bottom: 0.5rem;
                            color: #64748b;

                            .prompt {
                                color: #1e40af;
                            }

                            .command {
                                color: #3b82f6;
                                margin-left: 0.5rem;
                            }

                            .output {
                                color: #374151;
                                margin-left: 1rem;

                                &.error {
                                    color: #ef4444;
                                }
                            }

                            .cursor {
                                color: #1e40af;
                                animation: cursorBlink 1s infinite;
                            }
                        }
                    }

                    .cyber-create-btn {
                        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
                        color: white;
                        border: 1px solid rgba(59, 130, 246, 0.5);
                        border-radius: 6px;
                        font-family: 'Courier New', monospace;
                        letter-spacing: 1px;
                        transition: all 0.3s ease;

                        &:hover {
                            transform: translateY(-2px);
                            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
                        }
                    }
                }
            }
        }

        .task-grid-container {
            padding: 1.5rem;
            position: relative;
            z-index: 2;

            .drag-zone {
                position: relative;

                .drag-indicator-line {
                    position: absolute;
                    width: 100%;
                    height: 2px;
                    background: rgba(59, 130, 246, 0.6);
                    border-radius: 1px;
                    opacity: 0;
                    transition: all 0.3s ease;
                    z-index: 10;
                    pointer-events: none;

                    &.active {
                        opacity: 1;
                        box-shadow: 0 0 8px rgba(59, 130, 246, 0.6);
                    }
                }
            }

            &.mode-grid {
                .drag-zone {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                    gap: 1.5rem;
                }
            }

            &.mode-list {
                .drag-zone {
                    display: flex;
                    flex-direction: column;
                    gap: 1rem;
                }
            }
        }
    }
}

// 动画定义
@keyframes dotPulse {
    0%,
    100% {
        opacity: 0.4;
    }
    50% {
        opacity: 1;
    }
}

@keyframes scanLine {
    0% {
        transform: translateX(-100%);
    }
    100% {
        transform: translateX(100%);
    }
}

@keyframes matrixMove {
    0% {
        transform: translate(0, 0);
    }
    100% {
        transform: translate(40px, 40px);
    }
}

@keyframes nodeGlow {
    0%,
    100% {
        opacity: 0.4;
        transform: scale(1);
    }
    50% {
        opacity: 1;
        transform: scale(1.5);
    }
}

@keyframes streamFlow {
    0% {
        transform: translateY(-100%);
        opacity: 0;
    }
    10% {
        opacity: 1;
    }
    90% {
        opacity: 1;
    }
    100% {
        transform: translateY(100%);
        opacity: 0;
    }
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}

@keyframes progressMove {
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

@keyframes cursorBlink {
    0%,
    50% {
        opacity: 1;
    }
    51%,
    100% {
        opacity: 0;
    }
}

// 响应式设计
@media (max-width: 768px) {
    .task-console {
        .console-header {
            .header-content {
                flex-direction: column;
                gap: 1rem;

                .console-stats {
                    gap: 1rem;
                }

                .console-controls {
                    gap: 1rem;
                }
            }
        }

        .task-matrix {
            .task-grid-container {
                &.mode-grid {
                    .drag-zone {
                        grid-template-columns: 1fr;
                    }
                }
            }
        }
    }
}
</style>

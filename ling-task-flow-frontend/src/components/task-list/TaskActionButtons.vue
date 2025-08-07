<template>
    <Transition name="batch-actions" mode="out-in">
        <div v-if="selectedCount > 0" class="task-action-buttons">
            <!-- 选择信息显示 -->
            <div class="selection-info">
                <div class="selection-indicator">
                    <q-icon name="check_circle" />
                    <div class="selection-glow"></div>
                </div>
                <div class="selection-text">
                    <span class="selection-count">{{ selectedCount }}</span>
                    <span class="selection-label">个任务已选择</span>
                </div>
            </div>

            <!-- 操作按钮组 -->
            <div class="action-buttons">
                <!-- 标记完成按钮 -->
                <q-btn flat no-caps class="action-btn complete-btn" @click="$emit('markComplete')">
                    <div class="btn-content">
                        <q-icon name="done_all" />
                        <span>标记完成</span>
                        <div class="btn-glow"></div>
                    </div>
                </q-btn>

                <!-- 批量删除按钮 -->
                <q-btn flat no-caps class="action-btn delete-btn" @click="$emit('batchDelete')">
                    <div class="btn-content">
                        <q-icon name="delete" />
                        <span>批量删除</span>
                        <div class="btn-glow"></div>
                    </div>
                </q-btn>

                <!-- 取消选择按钮 -->
                <q-btn flat no-caps class="action-btn cancel-btn" @click="$emit('clearSelection')">
                    <div class="btn-content">
                        <q-icon name="close" />
                        <span>取消选择</span>
                        <div class="btn-glow"></div>
                    </div>
                </q-btn>
            </div>

            <!-- 科技感背景装饰 -->
            <div class="tech-background">
                <div class="tech-grid"></div>
                <div class="tech-lines">
                    <div class="tech-line" v-for="i in 3" :key="i"></div>
                </div>
                <div class="energy-pulse"></div>
            </div>
        </div>
    </Transition>
</template>

<script setup lang="ts">
interface Props {
    selectedCount: number;
}

interface Emits {
    (e: 'markComplete'): void;
    (e: 'batchDelete'): void;
    (e: 'clearSelection'): void;
}

defineProps<Props>();
defineEmits<Emits>();
</script>

<style scoped>
.task-action-buttons {
    position: relative;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(135deg, #0f1629 0%, #1a2139 50%, #0f1629 100%);
    border: 1px solid rgba(0, 255, 255, 0.3);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 16px;
    overflow: hidden;
    box-shadow:
        0 4px 20px rgba(0, 255, 255, 0.1),
        0 2px 10px rgba(0, 0, 0, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
}

.selection-info {
    display: flex;
    align-items: center;
    gap: 12px;
    z-index: 2;
}

.selection-indicator {
    position: relative;
    color: #00ffff;
    font-size: 24px;
    animation: pulse-glow 2s ease-in-out infinite;
}

.selection-glow {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 32px;
    height: 32px;
    background: radial-gradient(circle, rgba(0, 255, 255, 0.3) 0%, transparent 70%);
    border-radius: 50%;
    animation: selection-pulse 2s ease-in-out infinite;
}

.selection-text {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.selection-count {
    font-size: 18px;
    font-weight: 700;
    color: #00ffff;
    text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
    font-family: 'JetBrains Mono', monospace;
}

.selection-label {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.7);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.action-buttons {
    display: flex;
    gap: 8px;
    z-index: 2;
}

.action-btn {
    position: relative;
    min-height: 40px;
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-content {
    position: relative;
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 500;
    z-index: 1;
}

.btn-glow {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
}

/* 完成按钮样式 */
.complete-btn {
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(34, 197, 94, 0.2) 100%);
    border: 1px solid rgba(34, 197, 94, 0.3);
    color: #22c55e;
}

.complete-btn .btn-glow {
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(34, 197, 94, 0.3) 100%);
    box-shadow:
        0 0 20px rgba(34, 197, 94, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.complete-btn:hover {
    border-color: rgba(34, 197, 94, 0.5);
    color: #ffffff;
    text-shadow: 0 0 10px rgba(34, 197, 94, 0.8);
    transform: translateY(-2px);
    box-shadow:
        0 6px 25px rgba(34, 197, 94, 0.25),
        0 2px 10px rgba(0, 0, 0, 0.3);
}

.complete-btn:hover .btn-glow {
    opacity: 1;
}

/* 删除按钮样式 */
.delete-btn {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.2) 100%);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: #ef4444;
}

.delete-btn .btn-glow {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(239, 68, 68, 0.3) 100%);
    box-shadow:
        0 0 20px rgba(239, 68, 68, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.delete-btn:hover {
    border-color: rgba(239, 68, 68, 0.5);
    color: #ffffff;
    text-shadow: 0 0 10px rgba(239, 68, 68, 0.8);
    transform: translateY(-2px);
    box-shadow:
        0 6px 25px rgba(239, 68, 68, 0.25),
        0 2px 10px rgba(0, 0, 0, 0.3);
}

.delete-btn:hover .btn-glow {
    opacity: 1;
}

/* 取消按钮样式 */
.cancel-btn {
    background: linear-gradient(135deg, rgba(107, 114, 128, 0.1) 0%, rgba(107, 114, 128, 0.2) 100%);
    border: 1px solid rgba(107, 114, 128, 0.3);
    color: #6b7280;
}

.cancel-btn .btn-glow {
    background: linear-gradient(135deg, rgba(107, 114, 128, 0.2) 0%, rgba(107, 114, 128, 0.3) 100%);
    box-shadow:
        0 0 20px rgba(107, 114, 128, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.cancel-btn:hover {
    border-color: rgba(107, 114, 128, 0.5);
    color: #ffffff;
    text-shadow: 0 0 10px rgba(107, 114, 128, 0.8);
    transform: translateY(-2px);
    box-shadow:
        0 6px 25px rgba(107, 114, 128, 0.25),
        0 2px 10px rgba(0, 0, 0, 0.3);
}

.cancel-btn:hover .btn-glow {
    opacity: 1;
}

/* 科技感背景装饰 */
.tech-background {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    opacity: 0.6;
    pointer-events: none;
}

.tech-grid {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: radial-gradient(
        circle at 1px 1px,
        rgba(0, 255, 255, 0.15) 1px,
        transparent 0
    );
    background-size: 20px 20px;
    animation: grid-pulse 4s ease-in-out infinite;
}

.tech-lines {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
}

.tech-line {
    position: absolute;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0, 255, 255, 0.5), transparent);
    animation: tech-scan 3s ease-in-out infinite;
}

.tech-line:nth-child(1) {
    top: 20%;
    animation-delay: 0s;
}

.tech-line:nth-child(2) {
    top: 50%;
    animation-delay: 1s;
}

.tech-line:nth-child(3) {
    top: 80%;
    animation-delay: 2s;
}

.energy-pulse {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 200px;
    height: 200px;
    background: radial-gradient(circle, rgba(0, 255, 255, 0.1) 0%, transparent 70%);
    border-radius: 50%;
    animation: energy-wave 4s ease-in-out infinite;
}

/* 动画定义 */
@keyframes pulse-glow {
    0%,
    100% {
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
        transform: scale(1);
    }
    50% {
        text-shadow: 0 0 20px rgba(0, 255, 255, 0.8);
        transform: scale(1.05);
    }
}

@keyframes selection-pulse {
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

@keyframes grid-pulse {
    0%,
    100% {
        opacity: 0.3;
    }
    50% {
        opacity: 0.6;
    }
}

@keyframes tech-scan {
    0% {
        left: -100%;
        width: 0;
    }
    50% {
        left: 0;
        width: 100%;
    }
    100% {
        left: 100%;
        width: 0;
    }
}

@keyframes energy-wave {
    0%,
    100% {
        transform: translate(-50%, -50%) scale(0.8);
        opacity: 0.3;
    }
    50% {
        transform: translate(-50%, -50%) scale(1.2);
        opacity: 0.1;
    }
}

/* 过渡动画 */
.batch-actions-enter-active,
.batch-actions-leave-active {
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.batch-actions-enter-from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
}

.batch-actions-leave-to {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
}

/* 响应式设计 */
@media (max-width: 768px) {
    .task-action-buttons {
        flex-direction: column;
        gap: 16px;
        padding: 16px;
    }

    .action-buttons {
        width: 100%;
        justify-content: space-between;
    }

    .action-btn {
        flex: 1;
        min-width: 0;
    }

    .btn-content {
        padding: 10px 12px;
        font-size: 13px;
    }

    .selection-count {
        font-size: 16px;
    }

    .selection-label {
        font-size: 11px;
    }
}

@media (max-width: 480px) {
    .action-buttons {
        flex-direction: column;
        gap: 8px;
    }

    .btn-content span {
        display: none;
    }

    .btn-content {
        justify-content: center;
        padding: 12px;
    }
}
</style>

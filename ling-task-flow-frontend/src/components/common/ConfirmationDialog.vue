<template>
    <q-dialog
        v-model="isVisible"
        :maximized="false"
        :persistent="persistent"
        class="confirm-dialog-wrapper"
        position="standard"
        transition-hide="scale"
        transition-show="scale"
    >
        <q-card
            :class="[`confirm-dialog--${type}`, { 'confirm-dialog--danger': isDanger }]"
            class="confirm-dialog"
        >
            <!-- 科技感背景装饰 -->
            <div class="confirm-dialog__background">
                <div class="tech-grid"></div>
                <div class="floating-particles">
                    <div class="particle"></div>
                    <div class="particle"></div>
                    <div class="particle"></div>
                </div>
                <div class="glow-effect"></div>
            </div>

            <!-- 对话框内容 -->
            <q-card-section class="confirm-dialog__header">
                <div class="confirm-dialog__icon-wrapper">
                    <div :class="`icon-container--${type}`" class="icon-container">
                        <q-icon :class="`text-${iconColor}`" :name="iconName" :size="iconSize" />
                        <div class="icon-pulse"></div>
                    </div>
                </div>

                <div class="confirm-dialog__title-section">
                    <h3 class="confirm-dialog__title">{{ title }}</h3>
                    <div class="title-underline"></div>
                </div>
            </q-card-section>

            <q-card-section class="confirm-dialog__content">
                <div class="confirm-dialog__message">
                    <p class="message-text">{{ message }}</p>

                    <!-- 详细信息 (可选) -->
                    <div v-if="details" class="confirm-dialog__details">
                        <q-expansion-item
                            class="details-expansion"
                            dense
                            icon="info"
                            label="详细信息"
                        >
                            <template v-slot:header>
                                <q-item-section avatar>
                                    <q-icon color="blue" name="info_outline" size="sm" />
                                </q-item-section>
                                <q-item-section class="text-caption text-grey-6">
                                    查看详细信息
                                </q-item-section>
                            </template>

                            <div class="details-content">
                                <p class="details-text">{{ details }}</p>
                            </div>
                        </q-expansion-item>
                    </div>

                    <!-- 警告信息 (危险操作) -->
                    <div v-if="isDanger && warningText" class="confirm-dialog__warning">
                        <div class="warning-banner">
                            <q-icon class="warning-icon" name="warning" />
                            <span class="warning-text">{{ warningText }}</span>
                        </div>
                    </div>
                </div>
            </q-card-section>

            <!-- 操作按钮 -->
            <q-card-actions align="right" class="confirm-dialog__actions">
                <div class="action-buttons">
                    <!-- 取消按钮 -->
                    <q-btn
                        :color="cancelColor"
                        :disable="loading"
                        :label="cancelText"
                        :loading="loading"
                        class="cancel-btn"
                        flat
                        @click="handleCancel"
                    >
                        <q-icon class="q-mr-xs" name="close" size="xs" />
                    </q-btn>

                    <!-- 确认按钮 -->
                    <q-btn
                        :class="`confirm-btn--${type}`"
                        :color="confirmColor"
                        :disable="loading"
                        :label="confirmText"
                        :loading="loading"
                        class="confirm-btn"
                        unelevated
                        @click="handleConfirm"
                    >
                        <q-icon :name="confirmIcon" class="q-mr-xs" size="xs" />
                        <div class="btn-glow"></div>
                    </q-btn>
                </div>
            </q-card-actions>

            <!-- 加载遮罩 -->
            <q-inner-loading :showing="loading" class="confirm-dialog__loading">
                <div class="loading-content">
                    <q-spinner-orbit color="primary" size="2em" />
                    <p class="loading-text">{{ loadingText }}</p>
                </div>
            </q-inner-loading>
        </q-card>
    </q-dialog>
</template>

<script lang="ts" setup>
import { computed } from 'vue';

// 定义确认对话框类型
export type ConfirmDialogType = 'info' | 'warning' | 'danger' | 'success';

export interface ConfirmDialogProps {
    modelValue: boolean;
    type?: ConfirmDialogType;
    title: string;
    message: string;
    details?: string | undefined;
    warningText?: string | undefined;
    confirmText?: string;
    cancelText?: string;
    confirmIcon?: string;
    persistent?: boolean;
    loading?: boolean;
    loadingText?: string;
}

const props = withDefaults(defineProps<ConfirmDialogProps>(), {
    type: 'info',
    confirmText: '确认',
    cancelText: '取消',
    confirmIcon: 'check',
    persistent: false,
    loading: false,
    loadingText: '处理中...',
});

const emit = defineEmits<{
    'update:modelValue': [value: boolean];
    confirm: [];
    cancel: [];
}>();

// 对话框显示状态
const isVisible = computed({
    get: () => props.modelValue,
    set: (value: boolean) => emit('update:modelValue', value),
});

// 样式计算属性
const isDanger = computed(() => props.type === 'danger');

const iconName = computed(() => {
    const iconMap: Record<ConfirmDialogType, string> = {
        info: 'info',
        warning: 'warning',
        danger: 'dangerous',
        success: 'check_circle',
    };
    return iconMap[props.type];
});

const iconSize = computed(() => '32px');

const iconColor = computed(() => {
    const colorMap: Record<ConfirmDialogType, string> = {
        info: 'blue',
        warning: 'orange',
        danger: 'red',
        success: 'green',
    };
    return colorMap[props.type];
});

const confirmColor = computed(() => {
    const colorMap: Record<ConfirmDialogType, string> = {
        info: 'primary',
        warning: 'warning',
        danger: 'negative',
        success: 'positive',
    };
    return colorMap[props.type];
});

const cancelColor = computed(() => 'grey-6');

// 事件处理
const handleConfirm = () => {
    emit('confirm');
};

const handleCancel = () => {
    emit('cancel');
    if (!props.persistent) {
        isVisible.value = false;
    }
};
</script>

<style lang="scss" scoped>
.confirm-dialog-wrapper {
    :deep(.q-dialog__inner) {
        padding: 16px;
    }
}

.confirm-dialog {
    position: relative;
    min-width: 420px;
    max-width: 500px;
    overflow: hidden;
    border-radius: 16px;
    box-shadow:
        0 20px 40px rgba(0, 0, 0, 0.15),
        0 8px 16px rgba(0, 0, 0, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);

    // 响应式设计
    @media (max-width: 600px) {
        min-width: 320px;
        max-width: 90vw;
        margin: 16px;
    }

    // 类型样式
    &--info {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }

    &--warning {
        background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%);
    }

    &--danger {
        background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%);

        .confirm-dialog__background .glow-effect {
            background: radial-gradient(circle, rgba(239, 68, 68, 0.2) 0%, transparent 70%);
        }
    }

    &--success {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    }
}

// 科技感背景装饰
.confirm-dialog__background {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;
    z-index: 0;

    .tech-grid {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image:
            linear-gradient(rgba(59, 130, 246, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(59, 130, 246, 0.03) 1px, transparent 1px);
        background-size: 20px 20px;
        animation: grid-drift 20s linear infinite;
    }

    .floating-particles {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;

        .particle {
            position: absolute;
            width: 4px;
            height: 4px;
            background: radial-gradient(circle, rgba(59, 130, 246, 0.4) 0%, transparent 70%);
            border-radius: 50%;
            animation: particle-float 8s ease-in-out infinite;

            &:nth-child(1) {
                top: 20%;
                left: 15%;
                animation-delay: 0s;
                animation-duration: 6s;
            }

            &:nth-child(2) {
                top: 60%;
                right: 20%;
                animation-delay: 2s;
                animation-duration: 8s;
            }

            &:nth-child(3) {
                bottom: 25%;
                left: 70%;
                animation-delay: 4s;
                animation-duration: 7s;
            }
        }
    }

    .glow-effect {
        position: absolute;
        top: -50%;
        left: -50%;
        right: -50%;
        bottom: -50%;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%);
        animation: glow-pulse 4s ease-in-out infinite;
    }
}

// 头部样式
.confirm-dialog__header {
    position: relative;
    z-index: 1;
    padding: 24px 24px 16px;
    display: flex;
    align-items: center;
    gap: 16px;
}

.confirm-dialog__icon-wrapper {
    flex-shrink: 0;

    .icon-container {
        position: relative;
        width: 56px;
        height: 56px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;

        &--info {
            background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
        }

        &--warning {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.2);
        }

        &--danger {
            background: linear-gradient(135deg, #fecaca 0%, #fca5a5 100%);
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
        }

        &--success {
            background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
            box-shadow: 0 4px 12px rgba(34, 197, 94, 0.2);
        }

        .icon-pulse {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 50%;
            border: 2px solid currentColor;
            opacity: 0;
            animation: icon-pulse 2s ease-out infinite;
        }
    }
}

.confirm-dialog__title-section {
    flex: 1;

    .confirm-dialog__title {
        margin: 0;
        font-size: 1.25rem;
        font-weight: 600;
        color: #1f2937;
        line-height: 1.4;
    }

    .title-underline {
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, #3b82f6 0%, transparent 100%);
        margin-top: 8px;
        border-radius: 1px;
    }
}

// 内容样式
.confirm-dialog__content {
    position: relative;
    z-index: 1;
    padding: 0 24px 16px;

    .message-text {
        font-size: 0.95rem;
        line-height: 1.6;
        color: #4b5563;
        margin: 0 0 16px 0;
    }
}

.confirm-dialog__details {
    margin-top: 16px;

    .details-expansion {
        border: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: 8px;
        overflow: hidden;

        :deep(.q-expansion-item__container) {
            .q-item {
                background: rgba(255, 255, 255, 0.5);
                min-height: 36px;
            }
        }
    }

    .details-content {
        padding: 12px 16px;
        background: rgba(255, 255, 255, 0.7);
        border-top: 1px solid rgba(0, 0, 0, 0.1);

        .details-text {
            font-size: 0.85rem;
            line-height: 1.5;
            color: #6b7280;
            margin: 0;
        }
    }
}

.confirm-dialog__warning {
    margin-top: 16px;

    .warning-banner {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid #f59e0b;
        border-radius: 8px;

        .warning-icon {
            color: #d97706;
            font-size: 18px;
        }

        .warning-text {
            font-size: 0.875rem;
            color: #92400e;
            font-weight: 500;
        }
    }
}

// 操作按钮样式
.confirm-dialog__actions {
    position: relative;
    z-index: 1;
    padding: 16px 24px 24px;
    background: linear-gradient(180deg, transparent 0%, rgba(255, 255, 255, 0.3) 100%);

    .action-buttons {
        display: flex;
        gap: 12px;
        width: 100%;
        justify-content: flex-end;
    }

    .cancel-btn {
        min-width: 80px;
        border-radius: 8px;
        transition: all 0.2s ease;

        &:hover {
            background: rgba(0, 0, 0, 0.05);
        }
    }

    .confirm-btn {
        position: relative;
        min-width: 100px;
        border-radius: 8px;
        overflow: hidden;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

        &:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        .btn-glow {
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
            transition: left 0.5s ease;
        }

        &:hover .btn-glow {
            left: 100%;
        }

        &--danger:hover {
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
        }
    }
}

// 加载状态
.confirm-dialog__loading {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(4px);

    .loading-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;

        .loading-text {
            font-size: 0.875rem;
            color: #6b7280;
            margin: 0;
        }
    }
}

// 动画定义
@keyframes grid-drift {
    0% {
        transform: translate(0, 0);
    }
    100% {
        transform: translate(20px, 20px);
    }
}

@keyframes particle-float {
    0%,
    100% {
        transform: translateY(0) rotate(0deg);
        opacity: 0.3;
    }
    50% {
        transform: translateY(-10px) rotate(180deg);
        opacity: 0.6;
    }
}

@keyframes glow-pulse {
    0%,
    100% {
        opacity: 0.5;
        transform: scale(1);
    }
    50% {
        opacity: 0.8;
        transform: scale(1.05);
    }
}

@keyframes icon-pulse {
    0% {
        opacity: 0;
        transform: scale(1);
    }
    50% {
        opacity: 0.3;
        transform: scale(1.1);
    }
    100% {
        opacity: 0;
        transform: scale(1.2);
    }
}
</style>

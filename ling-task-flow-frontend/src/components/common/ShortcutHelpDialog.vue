<template>
    <q-dialog
        v-model="isVisible"
        position="standard"
        transition-show="scale"
        transition-hide="scale"
        :maximized="false"
        class="shortcut-help-wrapper"
    >
        <q-card class="shortcut-help-dialog">
            <!-- 科技感背景装饰 -->
            <div class="dialog-background">
                <div class="tech-grid"></div>
                <div class="floating-particles">
                    <div class="particle"></div>
                    <div class="particle"></div>
                    <div class="particle"></div>
                </div>
                <div class="glow-effect"></div>
            </div>

            <!-- 标题栏 -->
            <q-card-section class="dialog-header">
                <div class="header-content">
                    <div class="title-section">
                        <q-icon name="keyboard" size="md" class="title-icon" />
                        <h3 class="dialog-title">快捷键帮助</h3>
                    </div>
                    <q-btn
                        flat
                        round
                        icon="close"
                        color="grey-6"
                        size="sm"
                        @click="$emit('update:modelValue', false)"
                        class="close-btn"
                    >
                        <q-tooltip>关闭 (Esc)</q-tooltip>
                    </q-btn>
                </div>
            </q-card-section>

            <!-- 快捷键列表 -->
            <q-card-section class="dialog-content">
                <div class="shortcuts-container">
                    <!-- 按上下文分组 -->
                    <div
                        v-for="group in shortcutGroups"
                        :key="group.context"
                        class="shortcut-group"
                    >
                        <div class="group-header">
                            <q-icon :name="group.icon" size="sm" class="group-icon" />
                            <h4 class="group-title">{{ group.title }}</h4>
                        </div>

                        <div class="shortcuts-list">
                            <div
                                v-for="shortcut in group.shortcuts"
                                :key="shortcut.id"
                                class="shortcut-item"
                                :class="{ 'shortcut-disabled': shortcut.disabled }"
                            >
                                <div class="shortcut-keys">
                                    <kbd class="key-combination">
                                        {{ formatShortcut(shortcut) }}
                                    </kbd>
                                </div>
                                <div class="shortcut-description">
                                    {{ shortcut.description }}
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 提示信息 -->
                    <div class="help-tips">
                        <div class="tip-item">
                            <q-icon name="info" size="sm" color="blue" />
                            <span>在输入框中时，部分快捷键会被禁用以避免冲突</span>
                        </div>
                        <div class="tip-item">
                            <q-icon name="settings" size="sm" color="green" />
                            <span>可以在设置中自定义快捷键组合</span>
                        </div>
                    </div>
                </div>
            </q-card-section>

            <!-- 底部操作 -->
            <q-card-actions class="dialog-actions">
                <div class="action-buttons">
                    <q-btn
                        flat
                        label="关闭"
                        color="grey-6"
                        @click="$emit('update:modelValue', false)"
                        class="close-action-btn"
                    >
                        <q-icon name="close" size="xs" class="q-mr-xs" />
                    </q-btn>
                </div>
            </q-card-actions>
        </q-card>
    </q-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useGlobalShortcuts } from '../../composables/useKeyboardShortcuts';

// 类型定义
interface ShortcutConfig {
    id: string;
    key: string;
    ctrl?: boolean;
    alt?: boolean;
    shift?: boolean;
    meta?: boolean;
    description: string;
    action: () => void;
    context?: string;
    disabled?: boolean;
}

interface ShortcutGroup {
    context: string;
    title: string;
    icon: string;
    order: number;
    shortcuts: ShortcutWithId[];
}

// Props
interface Props {
    modelValue: boolean;
}

const props = defineProps<Props>();

// Emits
const emit = defineEmits<{
    'update:modelValue': [value: boolean];
}>();

// 快捷键管理（使用全局实例）
const shortcuts = useGlobalShortcuts();

// 响应式状态
const isVisible = computed({
    get: () => props.modelValue,
    set: (value: boolean) => {
        emit('update:modelValue', value);
    },
});

// 快捷键分组配置
const contextConfig: Record<
    string,
    {
        title: string;
        icon: string;
        order: number;
    }
> = {
    global: {
        title: '全局快捷键',
        icon: 'public',
        order: 1,
    },
    'task-list': {
        title: '任务列表',
        icon: 'list',
        order: 2,
    },
    dialog: {
        title: '对话框',
        icon: 'chat',
        order: 3,
    },
};

// 按上下文分组快捷键
// 为带有 id 的快捷键定义类型
type ShortcutWithId = ShortcutConfig & { id: string };

const shortcutGroups = computed(() => {
    const groups: Record<string, ShortcutGroup> = {};

    // 使用响应式数组，动态注册/移除能触发更新
    const allShortcuts: ShortcutWithId[] = shortcuts.shortcutItems.value as ShortcutWithId[];

    // 按上下文分组
    allShortcuts.forEach((shortcut: ShortcutWithId) => {
        const context = shortcut.context || 'global';
        if (!groups[context]) {
            const config = contextConfig[context] || {
                title: context,
                icon: 'keyboard',
                order: 999,
            };
            groups[context] = {
                context,
                title: config.title,
                icon: config.icon,
                order: config.order,
                shortcuts: [],
            };
        }
        groups[context].shortcuts.push(shortcut);
    });

    // 按order排序，然后按快捷键描述排序
    return Object.values(groups)
        .sort((a, b) => a.order - b.order)
        .map(group => ({
            ...group,
            shortcuts: group.shortcuts.sort((a: ShortcutWithId, b: ShortcutWithId) => {
                return a.description.localeCompare(b.description);
            }),
        }));
});

// 格式化快捷键显示
const formatShortcut = (shortcut: ShortcutConfig) => {
    return shortcuts.formatShortcut(shortcut);
};
</script>

<style lang="scss" scoped>
.shortcut-help-wrapper {
    .shortcut-help-dialog {
        width: 90vw;
        max-width: 800px;
        max-height: 90vh;
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
}

.dialog-background {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;
    overflow: hidden;

    .tech-grid {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image:
            linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 20px 20px;
        animation: grid-move 20s linear infinite;
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
            background: radial-gradient(circle, #00d4ff, transparent);
            border-radius: 50%;
            animation: float 6s ease-in-out infinite;

            &:nth-child(1) {
                top: 20%;
                left: 20%;
                animation-delay: 0s;
            }

            &:nth-child(2) {
                top: 60%;
                right: 30%;
                animation-delay: 2s;
            }

            &:nth-child(3) {
                bottom: 30%;
                left: 70%;
                animation-delay: 4s;
            }
        }
    }

    .glow-effect {
        position: absolute;
        top: -50%;
        left: -50%;
        right: -50%;
        bottom: -50%;
        background: radial-gradient(circle, rgba(0, 212, 255, 0.1) 0%, transparent 70%);
        animation: glow-pulse 4s ease-in-out infinite;
    }
}

.dialog-header {
    position: relative;
    z-index: 1;
    padding: 24px 32px 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);

    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .title-section {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .title-icon {
        color: #00d4ff;
    }

    .dialog-title {
        margin: 0;
        font-size: 24px;
        font-weight: 700;
        color: #ffffff;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }

    .close-btn {
        transition: all 0.3s ease;

        &:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: scale(1.1);
        }
    }
}

.dialog-content {
    position: relative;
    z-index: 1;
    padding: 24px 32px;
    max-height: 60vh;
    overflow-y: auto;

    &::-webkit-scrollbar {
        width: 8px;
    }

    &::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }

    &::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #00d4ff, #0099cc);
        border-radius: 4px;
    }
}

.shortcuts-container {
    .shortcut-group {
        margin-bottom: 32px;

        &:last-child {
            margin-bottom: 0;
        }
    }

    .group-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(0, 212, 255, 0.3);

        .group-icon {
            color: #00d4ff;
        }

        .group-title {
            margin: 0;
            font-size: 18px;
            font-weight: 600;
            color: #ffffff;
        }
    }

    .shortcuts-list {
        display: grid;
        gap: 12px;
    }

    .shortcut-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 16px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        transition: all 0.3s ease;

        &:hover {
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(0, 212, 255, 0.3);
            transform: translateY(-1px);
        }

        &.shortcut-disabled {
            opacity: 0.6;
            background: rgba(255, 255, 255, 0.02);

            .key-combination {
                background: rgba(255, 255, 255, 0.1);
                color: #999;
            }
        }
    }

    .shortcut-keys {
        min-width: 120px;
    }

    .key-combination {
        display: inline-block;
        padding: 6px 12px;
        background: linear-gradient(135deg, #00d4ff, #0099cc);
        color: #ffffff;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 13px;
        font-weight: 600;
        border: none;
        border-radius: 6px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    }

    .shortcut-description {
        flex: 1;
        margin-left: 16px;
        color: #e0e0e0;
        font-size: 14px;
        line-height: 1.4;
    }
}

.help-tips {
    margin-top: 32px;
    padding-top: 24px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);

    .tip-item {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
        padding: 12px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        color: #b0b0b0;
        font-size: 13px;

        &:last-child {
            margin-bottom: 0;
        }
    }
}

.dialog-actions {
    position: relative;
    z-index: 1;
    padding: 16px 32px 24px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);

    .action-buttons {
        display: flex;
        justify-content: flex-end;
        gap: 12px;
    }

    .close-action-btn {
        padding: 8px 24px;
        transition: all 0.3s ease;

        &:hover {
            background: rgba(255, 255, 255, 0.1);
        }
    }
}

// 动画
@keyframes grid-move {
    0% {
        transform: translate(0, 0);
    }
    100% {
        transform: translate(20px, 20px);
    }
}

@keyframes float {
    0%,
    100% {
        transform: translateY(0px) rotate(0deg);
    }
    33% {
        transform: translateY(-10px) rotate(120deg);
    }
    66% {
        transform: translateY(5px) rotate(240deg);
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
        transform: scale(1.1);
    }
}

// 响应式设计
@media (max-width: 768px) {
    .shortcut-help-wrapper {
        .shortcut-help-dialog {
            width: 95vw;
            max-height: 95vh;
        }
    }

    .dialog-header {
        padding: 16px 20px 12px;

        .dialog-title {
            font-size: 20px;
        }
    }

    .dialog-content {
        padding: 16px 20px;
    }

    .shortcut-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;

        .shortcut-description {
            margin-left: 0;
        }
    }

    .dialog-actions {
        padding: 12px 20px 16px;
    }
}
</style>

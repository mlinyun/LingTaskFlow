<template>
    <q-drawer v-model="drawerOpen" show-if-above bordered class="app-drawer" :width="320">
        <!-- 科技感背景 -->
        <div class="drawer-background">
            <div class="tech-grid"></div>
            <div class="floating-particles">
                <div class="particle"></div>
                <div class="particle"></div>
                <div class="particle"></div>
            </div>
            <div class="gradient-overlay"></div>
        </div>

        <q-list padding class="drawer-content">
            <!-- 任务统计概览 -->
            <q-item-label header class="section-header">
                <q-icon name="insights" class="q-mr-sm" />
                任务概览
            </q-item-label>

            <!-- 加载状态 -->
            <div v-if="statsLoading" class="stats-loading">
                <q-spinner-dots size="2rem" color="primary" />
                <div class="loading-text">正在加载统计数据...</div>
            </div>

            <!-- 统计数据 -->
            <q-item v-else-if="taskStats" class="stats-overview">
                <q-item-section>
                    <!-- 基础统计卡片 -->
                    <div class="stats-cards-grid">
                        <div class="stat-card primary">
                            <q-icon name="task_alt" class="stat-icon" />
                            <div class="stat-content">
                                <div class="stat-value">
                                    {{ taskStats.basic_stats.total_tasks }}
                                </div>
                                <div class="stat-label">总任务</div>
                            </div>
                        </div>

                        <div class="stat-card success">
                            <q-icon name="check_circle" class="stat-icon" />
                            <div class="stat-content">
                                <div class="stat-value">
                                    {{ taskStats.basic_stats.completed_tasks }}
                                </div>
                                <div class="stat-label">已完成</div>
                            </div>
                        </div>
                    </div>

                    <!-- 完成率进度条 -->
                    <div class="progress-section">
                        <div class="progress-header">
                            <span class="progress-title">完成进度</span>
                            <span class="progress-percentage">{{ completionRate }}%</span>
                        </div>
                        <q-linear-progress
                            :value="completionRate / 100"
                            color="primary"
                            class="progress-bar"
                            size="10px"
                            rounded
                        />
                        <div class="progress-details">
                            <span class="detail"
                                >{{ taskStats.basic_stats.completed_tasks }} /
                                {{ taskStats.basic_stats.total_tasks }}</span
                            >
                        </div>
                    </div>
                </q-item-section>
            </q-item>

            <!-- 错误状态 -->
            <div v-else-if="statsError" class="stats-error">
                <q-icon name="error_outline" size="2rem" color="negative" />
                <div class="error-text">加载统计数据失败</div>
                <q-btn flat size="sm" color="primary" @click="loadTaskStats" class="retry-btn">
                    重试
                </q-btn>
            </div>

            <!-- 导航菜单 -->
            <q-item-label header class="section-header">
                <q-icon name="menu" class="q-mr-sm" />
                导航菜单
            </q-item-label>

            <navigation-link v-for="link in navigationLinks" :key="link.title" v-bind="link" />
        </q-list>
    </q-drawer>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue';
import { useTaskStore } from 'stores/task';
import type { TaskStats } from 'src/types/task';
import NavigationLink from './NavigationLink.vue';

// Props
interface Props {
    modelValue: boolean;
    navigationLinks: Array<{
        title: string;
        caption: string;
        icon: string;
        link: string;
        color: string;
    }>;
}

const props = defineProps<Props>();

// Emits
const emit = defineEmits<{
    'update:modelValue': [value: boolean];
}>();

// Store
const taskStore = useTaskStore();

// 响应式数据
const taskStats = ref<TaskStats | null>(null);
const statsLoading = ref(false);
const statsError = ref(false);

// Computed
const drawerOpen = computed({
    get: () => props.modelValue,
    set: (value: boolean) => emit('update:modelValue', value),
});

// 计算完成率
const completionRate = computed(() => {
    if (!taskStats.value?.basic_stats) return 0;
    const { total_tasks, completed_tasks } = taskStats.value.basic_stats;
    if (total_tasks === 0) return 0;
    return Number(((completed_tasks / total_tasks) * 100).toFixed(2));
});

// 方法
const loadTaskStats = async () => {
    try {
        statsLoading.value = true;
        statsError.value = false;

        const stats = await taskStore.fetchTaskStats();
        taskStats.value = stats;
    } catch (error) {
        console.error('加载任务统计失败:', error);
        statsError.value = true;
    } finally {
        statsLoading.value = false;
    }
};

// 生命周期
onMounted(() => {
    void loadTaskStats();
});
</script>

<style lang="scss" scoped>
// 主要抽屉容器 - 科技感背景
.app-drawer {
    position: relative;
    background: linear-gradient(
        135deg,
        rgba(248, 250, 252, 0.95) 0%,
        rgba(241, 245, 249, 0.9) 50%,
        rgba(248, 250, 252, 0.95) 100%
    );
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(59, 130, 246, 0.15);
    box-shadow:
        4px 0 24px rgba(14, 165, 233, 0.08),
        2px 0 12px rgba(59, 130, 246, 0.06),
        inset -1px 0 0 rgba(255, 255, 255, 0.8);

    // 侧边栏滚动条样式 - 与主页一致的柔和蓝白科技风格
    &::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    &::-webkit-scrollbar-track {
        background: linear-gradient(to bottom, #f8fafc, #f1f5f9);
        border-radius: 4px;
        border: 1px solid rgba(148, 163, 184, 0.15);
        box-shadow: inset 0 0 2px rgba(148, 163, 184, 0.1);
    }

    &::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #94a3b8, #64748b);
        border-radius: 4px;
        border: 1px solid rgba(255, 255, 255, 0.4);
        box-shadow:
            0 1px 3px rgba(100, 116, 139, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

        &:hover {
            background: linear-gradient(135deg, #64748b, #475569);
            border-color: rgba(255, 255, 255, 0.6);
            box-shadow:
                0 2px 4px rgba(100, 116, 139, 0.2),
                inset 0 1px 0 rgba(255, 255, 255, 0.3);
            transform: scale(1.1);
        }

        &:active {
            background: linear-gradient(135deg, #475569, #374151);
            transform: scale(0.95);
        }
    }

    &::-webkit-scrollbar-corner {
        background: linear-gradient(135deg, #f8fafc, #f1f5f9);
        border-radius: 4px;
    }

    // 科技感背景层
    .drawer-background {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        pointer-events: none;
        z-index: 1;

        .tech-grid {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image:
                linear-gradient(rgba(59, 130, 246, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(59, 130, 246, 0.03) 1px, transparent 1px);
            background-size: 25px 25px;
            animation: gridMove 25s linear infinite;
        }

        .floating-particles {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;

            .particle {
                position: absolute;
                width: 3px;
                height: 3px;
                background: radial-gradient(circle, rgba(59, 130, 246, 0.6) 0%, transparent 70%);
                border-radius: 50%;
                animation: float 8s ease-in-out infinite;

                &:nth-child(1) {
                    top: 15%;
                    left: 20%;
                    animation-delay: 0s;
                }

                &:nth-child(2) {
                    top: 60%;
                    left: 70%;
                    animation-delay: 3s;
                }

                &:nth-child(3) {
                    top: 35%;
                    right: 15%;
                    animation-delay: 6s;
                }
            }
        }

        .gradient-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(
                180deg,
                rgba(59, 130, 246, 0.02) 0%,
                transparent 30%,
                transparent 70%,
                rgba(14, 165, 233, 0.02) 100%
            );
        }
    }

    // 内容层
    .drawer-content {
        position: relative;
        z-index: 2;
        height: 100%;
        overflow-y: auto;

        // 内容区域滚动条样式 - 与主页一致的柔和蓝白科技风格
        &::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        &::-webkit-scrollbar-track {
            background: linear-gradient(to bottom, #f8fafc, #f1f5f9);
            border-radius: 4px;
            border: 1px solid rgba(148, 163, 184, 0.15);
            box-shadow: inset 0 0 2px rgba(148, 163, 184, 0.1);
        }

        &::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #94a3b8, #64748b);
            border-radius: 4px;
            border: 1px solid rgba(255, 255, 255, 0.4);
            box-shadow:
                0 1px 3px rgba(100, 116, 139, 0.15),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

            &:hover {
                background: linear-gradient(135deg, #64748b, #475569);
                border-color: rgba(255, 255, 255, 0.6);
                box-shadow:
                    0 2px 4px rgba(100, 116, 139, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.3);
                transform: scale(1.1);
            }

            &:active {
                background: linear-gradient(135deg, #475569, #374151);
                transform: scale(0.95);
            }
        }

        &::-webkit-scrollbar-corner {
            background: linear-gradient(135deg, #f8fafc, #f1f5f9);
            border-radius: 4px;
        }
    }
}

// 节标题样式
.section-header {
    color: #3b82f6;
    font-weight: 700;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    opacity: 0.9;

    .q-icon {
        font-size: 1rem;
        opacity: 0.8;
    }
}

// 统计概览样式
.stats-overview {
    margin-bottom: 1rem;

    .stats-cards-grid {
        display: flex;
        gap: 0.75rem;
        margin-bottom: 1.25rem;

        .stat-card {
            background: rgba(255, 255, 255, 0.8);
            border-radius: 16px;
            padding: 1rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            border: 1px solid rgba(59, 130, 246, 0.08);
            backdrop-filter: blur(10px);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            flex: 1;

            &::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: var(--stat-color);
                transition: all 0.3s ease;
            }

            &:hover {
                transform: translateY(-2px);
                box-shadow:
                    0 12px 32px rgba(0, 0, 0, 0.06),
                    0 2px 6px rgba(0, 0, 0, 0.04);
                border-color: rgba(59, 130, 246, 0.15);

                &::before {
                    height: 4px;
                }

                .stat-icon {
                    transform: scale(1.1);
                }
            }

            &.primary {
                --stat-color: #3b82f6;

                .stat-icon {
                    color: #3b82f6;
                    background: rgba(59, 130, 246, 0.1);
                }
            }

            &.success {
                --stat-color: #10b981;

                .stat-icon {
                    color: #10b981;
                    background: rgba(16, 185, 129, 0.1);
                }
            }

            &.warning {
                --stat-color: #f59e0b;

                .stat-icon {
                    color: #f59e0b;
                    background: rgba(245, 158, 11, 0.1);
                }
            }

            &.danger {
                --stat-color: #ef4444;

                .stat-icon {
                    color: #ef4444;
                    background: rgba(239, 68, 68, 0.1);
                }
            }

            .stat-icon {
                font-size: 1.5rem;
                width: 2.5rem;
                height: 2.5rem;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
                flex-shrink: 0;
            }

            .stat-content {
                flex: 1;
                min-width: 0;

                .stat-value {
                    font-size: 1.125rem;
                    font-weight: 800;
                    line-height: 1.2;
                    margin-bottom: 0.125rem;
                    color: #1e293b;
                }

                .stat-label {
                    font-size: 0.75rem;
                    color: #64748b;
                    font-weight: 600;
                    opacity: 0.9;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }
            }
        }
    }

    .progress-section {
        background: rgba(255, 255, 255, 0.6);
        border-radius: 16px;
        padding: 1rem;
        border: 1px solid rgba(59, 130, 246, 0.08);
        backdrop-filter: blur(10px);

        .progress-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;

            .progress-title {
                font-size: 0.875rem;
                font-weight: 700;
                color: #374151;
            }

            .progress-percentage {
                font-size: 1rem;
                font-weight: 800;
                color: #3b82f6;
            }
        }

        .progress-bar {
            background: rgba(59, 130, 246, 0.1);
            border-radius: 8px;
            margin-bottom: 0.5rem;

            :deep(.q-linear-progress__track) {
                background: rgba(59, 130, 246, 0.08);
            }

            :deep(.q-linear-progress__model) {
                background: linear-gradient(90deg, #3b82f6, #1d4ed8);
                border-radius: 8px;
            }
        }

        .progress-details {
            text-align: center;

            .detail {
                font-size: 0.75rem;
                color: #64748b;
                font-weight: 600;
            }
        }
    }
}

// 加载和错误状态样式
.stats-loading,
.stats-error {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem 1rem;
    text-align: center;
    background: rgba(255, 255, 255, 0.6);
    border-radius: 16px;
    border: 1px solid rgba(59, 130, 246, 0.08);
    backdrop-filter: blur(10px);
    margin-bottom: 1.5rem;

    .loading-text,
    .error-text {
        margin-top: 0.75rem;
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 600;
    }

    .retry-btn {
        margin-top: 0.75rem;
        border-radius: 8px;
        font-weight: 600;
    }
}

// 动画定义
@keyframes gridMove {
    0% {
        transform: translate(0, 0);
    }
    100% {
        transform: translate(25px, 25px);
    }
}

@keyframes float {
    0%,
    100% {
        transform: translateY(0px) translateX(0px);
        opacity: 0.3;
    }
    33% {
        transform: translateY(-10px) translateX(5px);
        opacity: 0.8;
    }
    66% {
        transform: translateY(5px) translateX(-3px);
        opacity: 0.5;
    }
}
</style>

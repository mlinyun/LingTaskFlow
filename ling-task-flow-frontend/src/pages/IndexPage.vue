<template>
    <q-page class="home-page" padding>
        <!-- 主要欢迎区域 -->
        <div class="hero-section">
            <div class="hero-content">
                <div class="brand-wrapper">
                    <q-icon name="psychology" size="3rem" color="primary" class="brand-icon" />
                    <div class="brand-text">
                        <h1 class="hero-title">凌云智能任务管理平台</h1>
                        <p class="hero-subtitle">AI 驱动的智能任务管理，提升团队协作效率</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- 平台特色功能 -->
        <div class="features-section">
            <div class="features-grid">
                <div v-for="feature in features" :key="feature.id" class="feature-item">
                    <div class="feature-icon-wrapper">
                        <q-icon :name="feature.icon" size="1.25rem" :color="feature.color" />
                    </div>
                    <div class="feature-content">
                        <h4 class="feature-title">{{ feature.title }}</h4>
                        <p class="feature-desc">{{ feature.description }}</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- 最近活动 -->
        <div class="activity-section">
            <h3 class="section-title">最近活动</h3>
            <q-card flat bordered class="activity-card">
                <q-card-section>
                    <div class="activity-list">
                        <div
                            v-for="activity in recentActivities"
                            :key="activity.id"
                            class="activity-item"
                        >
                            <q-icon
                                :name="activity.icon"
                                :color="activity.color"
                                size="1.25rem"
                                class="activity-icon"
                            />
                            <div class="activity-content">
                                <span class="activity-text">{{ activity.text }}</span>
                                <span class="activity-time">{{ activity.time }}</span>
                            </div>
                        </div>
                    </div>
                </q-card-section>
            </q-card>
        </div>
    </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue';

// 平台特色功能
const features = ref([
    {
        id: 1,
        title: 'AI 智能推荐',
        description: '基于 AI 的任务优先级智能排序',
        icon: 'psychology',
        color: 'primary',
    },
    {
        id: 2,
        title: '实时协作',
        description: '多人同时编辑，实时同步更新',
        icon: 'group_work',
        color: 'secondary',
    },
    {
        id: 3,
        title: '智能分析',
        description: '深度数据分析，提供决策支持',
        icon: 'insights',
        color: 'info',
    },
    {
        id: 4,
        title: '云端同步',
        description: '跨设备数据同步，随时随地办公',
        icon: 'cloud_sync',
        color: 'positive',
    },
]);

// 最近活动
const recentActivities = ref([
    {
        id: 1,
        text: '完成了任务 "首页界面优化调整"',
        time: '2分钟前',
        icon: 'check_circle',
        color: 'positive',
    },
    {
        id: 2,
        text: '创建了新项目 "移动端开发"',
        time: '1小时前',
        icon: 'add_circle',
        color: 'primary',
    },
    {
        id: 3,
        text: '张三加入了团队',
        time: '2小时前',
        icon: 'person_add',
        color: 'secondary',
    },
    {
        id: 4,
        text: '系统自动备份完成',
        time: '3小时前',
        icon: 'backup',
        color: 'info',
    },
]);
</script>

<style scoped lang="scss">
.home-page {
    background: #ffffff;
    min-height: calc(100vh - 50px);
    position: relative;

    // 添加科技感网格纹理 - 与仪表板一致
    &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image:
            linear-gradient(rgba(59, 130, 246, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(59, 130, 246, 0.02) 1px, transparent 1px);
        background-size: 40px 40px;
        pointer-events: none;
    }
}

// 主要欢迎区域 - 简洁设计
.hero-section {
    color: #1f2937;
    padding: 1rem 0 2rem;
    position: relative;

    .hero-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 2rem;
        position: relative;
        z-index: 2;

        .brand-wrapper {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1.5rem;

            .brand-icon {
                opacity: 0.9;
            }

            .brand-text {
                text-align: left;

                .hero-title {
                    font-size: 2.5rem;
                    font-weight: 700;
                    margin: 0 0 0.75rem 0;
                    background: linear-gradient(45deg, #1f2937, #3b82f6);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    line-height: 1.2;
                }

                .hero-subtitle {
                    font-size: 1.125rem;
                    opacity: 0.8;
                    margin: 0;
                    font-weight: 400;
                    color: #6b7280;
                }
            }
        }
    }
}

// 特色功能区域
.features-section {
    margin-bottom: 3rem;

    .features-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.25rem;
        max-width: 1200px;
        margin: 0 auto;
        .feature-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 1rem 0.75rem;
            // 科技感卡片设计 - 与仪表板一致
            background: rgba(255, 255, 255, 0.98);
            border-radius: 16px;
            border: 1px solid rgba(59, 130, 246, 0.1);
            box-shadow:
                0 6px 24px rgba(14, 165, 233, 0.06),
                0 2px 6px rgba(59, 130, 246, 0.04),
                inset 0 1px 0 rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(20px);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;

            // 科技感边框发光
            &::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                border-radius: 16px;
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
                transform: translateY(-4px) scale(1.01);
                box-shadow:
                    0 12px 36px rgba(14, 165, 233, 0.12),
                    0 6px 16px rgba(59, 130, 246, 0.08),
                    inset 0 1px 0 rgba(255, 255, 255, 0.9);
                border-color: rgba(59, 130, 246, 0.2);

                &::before {
                    opacity: 1;
                }
            }

            .feature-icon-wrapper {
                background: rgba(59, 130, 246, 0.1);
                border: 2px solid rgba(59, 130, 246, 0.2);
                border-radius: 50%;
                width: 44px;
                height: 44px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 0.75rem;
                flex-shrink: 0;
                box-shadow: 0 3px 8px rgba(59, 130, 246, 0.08);
            }

            .feature-content {
                flex: 1;

                .feature-title {
                    font-size: 0.9rem;
                    font-weight: 600;
                    color: #1e40af;
                    margin: 0 0 0.375rem 0;
                }

                .feature-desc {
                    color: #64748b;
                    font-size: 0.8rem;
                    line-height: 1.4;
                    margin: 0;
                }
            }
        }
    }
}

// 最近活动区域
.activity-section {
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e40af;
        margin: 0 0 1.5rem 0;
        text-align: center;
    }

    .activity-card {
        max-width: 800px;
        margin: 0 auto;
        // 科技感卡片设计 - 与仪表板一致
        background: rgba(255, 255, 255, 0.98);
        border-radius: 20px;
        border: 1px solid rgba(59, 130, 246, 0.1);
        box-shadow:
            0 8px 32px rgba(14, 165, 233, 0.08),
            0 2px 8px rgba(59, 130, 246, 0.05),
            inset 0 1px 0 rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(20px);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

        // 修改 Quasar 卡片默认样式
        :deep(.q-card__section--vert) {
            padding: 0 16px;
        }

        .activity-list {
            .activity-item {
                display: flex;
                align-items: center;
                padding: 1rem 0;
                border-bottom: 1px solid rgba(59, 130, 246, 0.1);
                transition: all 0.3s ease;

                &:last-child {
                    border-bottom: none;
                }

                &:hover {
                    background: rgba(59, 130, 246, 0.02);
                    border-radius: 8px;
                    margin: 0 -1rem;
                    padding: 1rem;
                }

                .activity-icon {
                    margin-right: 1rem;
                    flex-shrink: 0;
                    background: rgba(59, 130, 246, 0.1);
                    border-radius: 50%;
                    width: 32px;
                    height: 32px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border: 1px solid rgba(59, 130, 246, 0.2);
                }

                .activity-content {
                    flex: 1;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;

                    .activity-text {
                        color: #1e40af;
                        font-size: 0.875rem;
                        font-weight: 500;
                    }

                    .activity-time {
                        color: #64748b;
                        font-size: 0.75rem;
                        background: rgba(14, 165, 233, 0.05);
                        padding: 2px 8px;
                        border-radius: 12px;
                        border: 1px solid rgba(14, 165, 233, 0.1);
                    }
                }
            }
        }
    }
}

// 响应式设计
@media (max-width: 1024px) {
    .features-section .features-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 1.5rem;
    }
}

@media (max-width: 768px) {
    .hero-section {
        padding: 2rem 0;

        .hero-content {
            padding: 0 1rem;

            .brand-wrapper {
                flex-direction: column;
                text-align: center;
                gap: 1rem;

                .brand-text {
                    text-align: center;

                    .hero-title {
                        font-size: 1.875rem;
                    }

                    .hero-subtitle {
                        font-size: 1rem;
                    }
                }
            }
        }
    }

    .features-section .features-grid {
        grid-template-columns: 1fr;
        gap: 1rem;

        .feature-item {
            padding: 1rem;
        }
    }

    .section-title {
        font-size: 1.25rem !important;
    }
}
</style>

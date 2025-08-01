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
                        <q-icon :name="feature.icon" size="1.5rem" :color="feature.color" />
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
        title: 'AI智能推荐',
        description: '基于机器学习的任务优先级智能排序',
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
        text: '完成了任务 "用户界面优化"',
        time: '5分钟前',
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
    min-height: calc(100vh - 50px); // 减去 header 高度
}

// 主要欢迎区域
.hero-section {
    color: #1f2937;
    padding: 1.5rem 0;
    margin: -1rem -1rem 2rem -1rem;
    position: relative;
    overflow: hidden;

    &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        pointer-events: none;
    }

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
        gap: 1.5rem;
        max-width: 1200px;
        margin: 0 auto;

        .feature-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 1rem 0.75rem;
            background: white;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            transition: all 0.3s ease;

            &:hover {
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
                border-color: #cbd5e1;
                transform: translateY(-2px);
            }

            .feature-icon-wrapper {
                background: #f8fafc;
                border-radius: 50%;
                width: 48px;
                height: 48px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 0.75rem;
                flex-shrink: 0;
            }

            .feature-content {
                flex: 1;

                .feature-title {
                    font-size: 0.875rem;
                    font-weight: 600;
                    color: #1f2937;
                    margin: 0 0 0.5rem 0;
                }

                .feature-desc {
                    color: #6b7280;
                    font-size: 0.75rem;
                    line-height: 1.4;
                    margin: 0;
                }
            }
        }
    }
}

// 最近活动区域
.activity-section {
    margin-bottom: 2rem;

    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1f2937;
        text-align: center;
        margin-bottom: 2rem;
    }

    .activity-card {
        max-width: 800px;
        margin: 0 auto;
        border-radius: 12px;
        border: 1px solid #e2e8f0;

        .activity-list {
            .activity-item {
                display: flex;
                align-items: center;
                padding: 1rem 0;
                border-bottom: 1px solid #f3f4f6;

                &:last-child {
                    border-bottom: none;
                }

                .activity-icon {
                    margin-right: 1rem;
                    flex-shrink: 0;
                }

                .activity-content {
                    flex: 1;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;

                    .activity-text {
                        color: #374151;
                        font-size: 0.875rem;
                        font-weight: 500;
                    }

                    .activity-time {
                        color: #9ca3af;
                        font-size: 0.75rem;
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

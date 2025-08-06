<template>
    <q-header class="ling-header">
        <div class="header-background">
            <div class="gradient-overlay"></div>
            <div class="tech-pattern"></div>
        </div>

        <q-toolbar class="header-toolbar">
            <!-- 左侧区域：菜单按钮 + 品牌 -->
            <div class="left-section">
                <!-- 菜单按钮 -->
                <div class="menu-section">
                    <q-btn
                        flat
                        dense
                        round
                        icon="menu"
                        aria-label="Menu"
                        @click="handleMenuToggle"
                        class="menu-btn"
                    >
                        <q-tooltip anchor="bottom middle" self="top middle" :delay="800">
                            导航菜单
                        </q-tooltip>
                    </q-btn>

                    <!-- 分隔线 -->
                    <div class="divider"></div>
                </div>

                <!-- 品牌区域 -->
                <div class="brand-section">
                    <div class="brand-icon-wrapper">
                        <q-icon name="psychology" class="brand-icon" />
                        <div class="icon-glow"></div>
                    </div>
                    <div class="brand-text">
                        <span class="brand-title">LingTaskFlow</span>
                        <span class="brand-subtitle">凌云智能任务管理平台</span>
                    </div>
                </div>
            </div>

            <!-- 右侧用户区域 -->
            <div class="user-section">
                <!-- 用户信息卡片 -->
                <div v-if="authStore?.user" class="user-info-card">
                    <div class="user-avatar">
                        <q-icon name="person" />
                        <div class="avatar-status"></div>
                    </div>
                    <div class="user-details">
                        <div class="user-name">{{ authStore?.userDisplayName }}</div>
                        <div class="user-status">在线</div>
                    </div>
                </div>

                <!-- 操作按钮组 -->
                <div class="action-buttons">
                    <!-- 通知按钮 -->
                    <q-btn
                        flat
                        dense
                        round
                        icon="notifications"
                        class="action-btn"
                        @click="$q.notify('通知功能开发中...')"
                    >
                        <q-badge color="red" floating>3</q-badge>
                        <q-tooltip anchor="bottom middle" self="top middle" :delay="800">
                            通知消息
                        </q-tooltip>
                    </q-btn>

                    <!-- 设置按钮 -->
                    <q-btn
                        flat
                        dense
                        round
                        icon="settings"
                        class="action-btn"
                        @click="handleSettings"
                    >
                        <q-tooltip anchor="bottom middle" self="top middle" :delay="800">
                            系统设置
                        </q-tooltip>
                    </q-btn>

                    <!-- 用户菜单 -->
                    <q-btn
                        flat
                        dense
                        round
                        icon="person"
                        class="user-menu-btn"
                        @mouseenter="showUserMenu"
                        @mouseleave="hideUserMenu"
                    >
                        <q-menu
                            v-model="userMenuVisible"
                            fit
                            anchor="bottom end"
                            self="top end"
                            :offset="[0, 8]"
                            @mouseenter="showUserMenu"
                            @mouseleave="hideUserMenu"
                        >
                            <q-list class="user-dropdown">
                                <!-- 用户信息头部 -->
                                <div class="dropdown-header">
                                    <div class="header-background">
                                        <div class="tech-grid"></div>
                                        <div class="gradient-overlay"></div>
                                    </div>
                                    <div class="dropdown-user-info">
                                        <div class="user-avatar-large">
                                            <q-icon name="person" />
                                            <div class="avatar-ring"></div>
                                        </div>
                                        <div class="user-text-info">
                                            <div class="dropdown-user-name">
                                                {{ authStore?.userDisplayName }}
                                            </div>
                                            <div class="dropdown-user-email">
                                                {{ authStore?.user?.email }}
                                            </div>
                                            <div class="user-status-badge">
                                                <div class="status-dot"></div>
                                                <span>在线</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div class="menu-separator"></div>

                                <!-- 菜单项目 -->
                                <div class="menu-items">
                                    <q-item
                                        clickable
                                        @click="
                                            handleProfile;
                                            userMenuVisible = false;
                                        "
                                        class="dropdown-item"
                                    >
                                        <q-item-section avatar class="item-icon">
                                            <div class="icon-container">
                                                <q-icon name="person" />
                                                <div class="icon-ripple"></div>
                                            </div>
                                        </q-item-section>
                                        <q-item-section>
                                            <q-item-label class="item-title">个人资料</q-item-label>
                                            <q-item-label caption class="item-subtitle"
                                                >查看和编辑个人信息</q-item-label
                                            >
                                        </q-item-section>
                                        <q-item-section side class="item-arrow">
                                            <q-icon name="chevron_right" class="chevron-icon" />
                                        </q-item-section>
                                    </q-item>

                                    <q-item
                                        clickable
                                        @click="
                                            handleSettings;
                                            userMenuVisible = false;
                                        "
                                        class="dropdown-item"
                                    >
                                        <q-item-section avatar class="item-icon">
                                            <div class="icon-container">
                                                <q-icon name="settings" />
                                                <div class="icon-ripple"></div>
                                            </div>
                                        </q-item-section>
                                        <q-item-section>
                                            <q-item-label class="item-title">系统设置</q-item-label>
                                            <q-item-label caption class="item-subtitle"
                                                >偏好设置和配置</q-item-label
                                            >
                                        </q-item-section>
                                        <q-item-section side class="item-arrow">
                                            <q-icon name="chevron_right" class="chevron-icon" />
                                        </q-item-section>
                                    </q-item>

                                    <q-item
                                        clickable
                                        @click="userMenuVisible = false"
                                        class="dropdown-item"
                                    >
                                        <q-item-section avatar class="item-icon">
                                            <div class="icon-container">
                                                <q-icon name="help_outline" />
                                                <div class="icon-ripple"></div>
                                            </div>
                                        </q-item-section>
                                        <q-item-section>
                                            <q-item-label class="item-title">帮助支持</q-item-label>
                                            <q-item-label caption class="item-subtitle"
                                                >使用指南和技术支持</q-item-label
                                            >
                                        </q-item-section>
                                        <q-item-section side class="item-arrow">
                                            <q-icon name="chevron_right" class="chevron-icon" />
                                        </q-item-section>
                                    </q-item>

                                    <div class="logout-separator"></div>

                                    <!-- 退出登录项 -->
                                    <q-item
                                        clickable
                                        @click="
                                            handleLogout;
                                            userMenuVisible = false;
                                        "
                                        class="dropdown-item logout-item"
                                    >
                                        <q-item-section avatar class="item-icon">
                                            <div class="icon-container logout-icon">
                                                <q-icon name="logout" />
                                                <div class="icon-ripple logout-ripple"></div>
                                            </div>
                                        </q-item-section>
                                        <q-item-section @click="handleLogout">
                                            <q-item-label class="item-title">退出登录</q-item-label>
                                            <q-item-label caption class="item-subtitle"
                                                >安全退出系统</q-item-label
                                            >
                                        </q-item-section>
                                        <q-item-section side class="item-arrow">
                                            <q-icon
                                                name="power_settings_new"
                                                class="chevron-icon"
                                            />
                                        </q-item-section>
                                    </q-item>
                                </div>
                            </q-list>
                        </q-menu>
                    </q-btn>
                </div>
            </div>
        </q-toolbar>
    </q-header>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { useAuthStore } from 'stores/auth';
import { useGlobalConfirm } from '../../composables/useGlobalConfirm';

// 定义组件事件
const emit = defineEmits<{
    toggleDrawer: [];
}>();

// 响应式数据
const userMenuVisible = ref(false);
let menuTimer: NodeJS.Timeout | null = null;

// 依赖注入
const router = useRouter();
const $q = useQuasar();
const authStore = useAuthStore();
const confirmDialog = useGlobalConfirm();

// 方法
const handleMenuToggle = () => {
    emit('toggleDrawer');
};

const handleProfile = () => {
    $q.notify('个人资料功能开发中...');
};

const handleSettings = () => {
    $q.notify('设置功能开发中...');
};

// 用户菜单显示/隐藏方法
const showUserMenu = () => {
    if (menuTimer) {
        clearTimeout(menuTimer);
        menuTimer = null;
    }
    userMenuVisible.value = true;
};

const hideUserMenu = () => {
    // 添加延迟，防止鼠标移动到菜单内容时菜单消失
    menuTimer = setTimeout(() => {
        userMenuVisible.value = false;
    }, 100);
};

const handleLogout = async () => {
    try {
        // 尝试使用确认对话框，如果失败则直接执行登出
        let confirmed = false;

        try {
            confirmed = await confirmDialog.confirmInfo('退出登录', '您确定要退出登录吗？', {
                details: '退出后需要重新登录才能使用系统。',
                confirmText: '退出登录',
                confirmIcon: 'logout',
            });
        } catch (dialogError) {
            // 如果确认对话框不可用，直接确认
            console.warn('确认对话框不可用，直接执行登出:', dialogError);
            confirmed = confirm('您确定要退出登录吗？');
        }

        if (confirmed) {
            try {
                confirmDialog.setLoading(true, '正在退出登录...');
            } catch {
                // 忽略设置加载状态的错误
            }

            try {
                await authStore.logout();
                $q.notify({
                    type: 'positive',
                    message: '已成功退出登录',
                    position: 'top',
                });
                void router.push('/login');
            } catch (error) {
                console.error('退出登录失败:', error);
                $q.notify({
                    type: 'negative',
                    message: '退出登录失败',
                    position: 'top',
                });
            } finally {
                try {
                    confirmDialog.setLoading(false);
                } catch {
                    // 忽略设置加载状态的错误
                }
            }
        }
    } catch (error) {
        console.error('退出登录失败:', error);
    }
};
</script>

<style lang="scss" scoped>
.ling-header {
    height: 64px; // 保持原有高度
    position: fixed; // 固定在页面顶部
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000; // 确保在最上层
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);

    .header-background {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 1;

        .gradient-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 50%, #0369a1 100%);
        }

        .tech-pattern {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background:
                repeating-linear-gradient(
                    90deg,
                    transparent,
                    transparent 98px,
                    rgba(255, 255, 255, 0.03) 100px
                ),
                repeating-linear-gradient(
                    0deg,
                    transparent,
                    transparent 98px,
                    rgba(255, 255, 255, 0.03) 100px
                );

            &::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(
                    90deg,
                    transparent 0%,
                    rgba(255, 255, 255, 0.05) 25%,
                    rgba(255, 255, 255, 0.1) 50%,
                    rgba(255, 255, 255, 0.05) 75%,
                    transparent 100%
                );
                animation: techScan 8s linear infinite;
            }
        }
    }

    .header-toolbar {
        position: relative;
        z-index: 2;
        padding: 0 24px;
        height: 64px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
}

// 左侧区域布局
.left-section {
    display: flex;
    align-items: center;
    gap: 16px;
}

// 左侧菜单区域
.menu-section {
    display: flex;
    align-items: center;
    gap: 16px;

    .menu-btn {
        color: white;
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        width: 48px;
        height: 48px;
        backdrop-filter: blur(10px);
        background: rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;

        &:hover {
            background: rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.4);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }

        &:active {
            transform: translateY(0);
        }
    }

    .divider {
        width: 2px;
        height: 32px;
        background: linear-gradient(to bottom, transparent, rgba(255, 255, 255, 0.3), transparent);
        border-radius: 1px;
    }
}

// 品牌区域
.brand-section {
    display: flex;
    align-items: center;
    gap: 16px;

    .brand-icon-wrapper {
        position: relative;

        .brand-icon {
            font-size: 2.5rem;
            color: white;
            filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.3));
        }

        .icon-glow {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.2) 0%, transparent 70%);
            animation: iconPulse 3s ease-in-out infinite;
        }
    }

    .brand-text {
        display: flex;
        flex-direction: column;
        align-items: flex-start;

        .brand-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: white;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
            letter-spacing: 1px;
        }

        .brand-subtitle {
            font-size: 0.75rem;
            color: rgba(255, 255, 255, 0.8);
            font-weight: 400;
            letter-spacing: 0.5px;
            margin-top: -2px;
        }
    }
}

// 右侧用户区域
.user-section {
    display: flex;
    align-items: center;
    gap: 16px;

    .user-info-card {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 4px 8px;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.2);

        .user-avatar {
            position: relative;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.2rem;

            .avatar-status {
                position: absolute;
                bottom: 2px;
                right: 2px;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: #10b981;
                border: 2px solid white;
            }
        }

        .user-details {
            display: flex;
            flex-direction: column;

            .user-name {
                color: white;
                font-weight: 600;
                font-size: 0.9rem;
                line-height: 1.2;
            }

            .user-status {
                color: rgba(255, 255, 255, 0.7);
                font-size: 0.75rem;
                line-height: 1.2;
            }
        }
    }

    .action-buttons {
        display: flex;
        align-items: center;
        gap: 8px;

        .action-btn,
        .user-menu-btn {
            color: white;
            border-radius: 12px;
            width: 44px;
            height: 44px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;

            .q-icon {
                font-size: 1.3rem;
                line-height: 1;
            }

            &:hover {
                background: rgba(255, 255, 255, 0.2);
                border-color: rgba(255, 255, 255, 0.4);
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            }

            &:active {
                transform: translateY(0);
            }
        }
    }
}

// 用户下拉菜单样式
.user-dropdown {
    min-width: 340px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(59, 130, 246, 0.15);
    box-shadow:
        0 25px 50px rgba(0, 0, 0, 0.08),
        0 0 0 1px rgba(255, 255, 255, 0.05),
        inset 0 1px 0 rgba(255, 255, 255, 0.25);
    overflow: hidden;
    position: relative;

    &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background:
            radial-gradient(circle at 20% 80%, rgba(59, 130, 246, 0.03) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(14, 165, 233, 0.03) 0%, transparent 50%);
        pointer-events: none;
    }

    .dropdown-header {
        padding: 24px 24px 20px;
        position: relative;
        background: linear-gradient(
            135deg,
            rgba(14, 165, 233, 0.08) 0%,
            rgba(59, 130, 246, 0.05) 100%
        );

        .header-background {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;

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
                animation: gridFloat 20s linear infinite;
            }

            .gradient-overlay {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(
                    135deg,
                    rgba(59, 130, 246, 0.02) 0%,
                    transparent 50%,
                    rgba(14, 165, 233, 0.02) 100%
                );
            }
        }

        .dropdown-user-info {
            display: flex;
            align-items: center;
            gap: 16px;
            position: relative;
            z-index: 1;

            .user-avatar-large {
                position: relative;
                width: 52px;
                height: 52px;
                border-radius: 50%;
                background: linear-gradient(
                    135deg,
                    rgba(59, 130, 246, 0.1) 0%,
                    rgba(14, 165, 233, 0.15) 100%
                );
                display: flex;
                align-items: center;
                justify-content: center;
                color: #1e40af;
                font-size: 1.6rem;
                border: 2px solid rgba(59, 130, 246, 0.2);
                box-shadow: 0 8px 20px rgba(59, 130, 246, 0.1);

                .avatar-ring {
                    position: absolute;
                    top: -4px;
                    left: -4px;
                    right: -4px;
                    bottom: -4px;
                    border-radius: 50%;
                    border: 2px solid transparent;
                    background: linear-gradient(
                            45deg,
                            rgba(59, 130, 246, 0.3),
                            transparent,
                            rgba(14, 165, 233, 0.3)
                        )
                        border-box;
                    mask:
                        linear-gradient(#fff 0 0) padding-box,
                        linear-gradient(#fff 0 0);
                    -webkit-mask:
                        linear-gradient(#fff 0 0) padding-box,
                        linear-gradient(#fff 0 0);
                    mask-composite: exclude;
                    -webkit-mask-composite: exclude;
                    animation: ringRotate 4s linear infinite;
                }
            }

            .user-text-info {
                flex: 1;

                .dropdown-user-name {
                    font-weight: 700;
                    font-size: 1.25rem;
                    margin-bottom: 4px;
                    color: #1e293b;
                    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
                }

                .dropdown-user-email {
                    font-size: 0.9rem;
                    color: #64748b;
                    margin-bottom: 8px;
                    font-weight: 500;
                }

                .user-status-badge {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    font-size: 0.85rem;
                    color: #059669;
                    font-weight: 600;

                    .status-dot {
                        width: 8px;
                        height: 8px;
                        border-radius: 50%;
                        background: #10b981;
                        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
                        animation: statusBeat 2s ease-in-out infinite;
                    }
                }
            }
        }
    }

    .menu-separator {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.15), transparent);
        margin: 0 20px;
        position: relative;

        &::after {
            content: '';
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 40px;
            height: 1px;
            background: linear-gradient(90deg, rgba(14, 165, 233, 0.3), rgba(59, 130, 246, 0.3));
            box-shadow: 0 0 8px rgba(59, 130, 246, 0.2);
        }
    }

    .menu-items {
        padding: 8px 0;
    }

    .dropdown-item {
        padding: 14px 24px;
        margin: 2px 12px;
        border-radius: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        color: #334155;
        position: relative;
        overflow: hidden;

        &::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.05), transparent);
            transition: left 0.6s ease;
        }

        &:hover {
            background: linear-gradient(
                135deg,
                rgba(59, 130, 246, 0.08) 0%,
                rgba(14, 165, 233, 0.05) 100%
            );
            color: #1e40af;
            transform: translateY(-1px);
            box-shadow: 0 4px 20px rgba(59, 130, 246, 0.08);

            &::before {
                left: 100%;
            }

            .icon-container {
                background: linear-gradient(
                    135deg,
                    rgba(59, 130, 246, 0.15) 0%,
                    rgba(14, 165, 233, 0.2) 100%
                );
                border-color: rgba(59, 130, 246, 0.3);
                transform: scale(1.05);

                .icon-ripple {
                    opacity: 1;
                    transform: scale(1.2);
                }
            }

            .chevron-icon {
                transform: translateX(6px);
                color: #3b82f6;
            }
        }

        .item-icon {
            min-width: 60px;

            .icon-container {
                position: relative;
                width: 44px;
                height: 44px;
                border-radius: 12px;
                background: linear-gradient(
                    135deg,
                    rgba(59, 130, 246, 0.08) 0%,
                    rgba(14, 165, 233, 0.12) 100%
                );
                display: flex;
                align-items: center;
                justify-content: center;
                border: 1px solid rgba(59, 130, 246, 0.15);
                transition: all 0.3s ease;

                .q-icon {
                    font-size: 1.3rem;
                    color: #3b82f6;
                    z-index: 1;
                    position: relative;
                }

                .icon-ripple {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%) scale(0.8);
                    width: 100%;
                    height: 100%;
                    border-radius: 12px;
                    background: linear-gradient(
                        135deg,
                        rgba(59, 130, 246, 0.1),
                        rgba(14, 165, 233, 0.15)
                    );
                    opacity: 0;
                    transition: all 0.3s ease;
                }
            }
        }

        .item-title {
            font-weight: 600;
            font-size: 1rem;
            margin-bottom: 2px;
            color: inherit;
        }

        .item-subtitle {
            color: #64748b;
            font-size: 0.85rem;
            line-height: 1.4;
            font-weight: 500;
        }

        .item-arrow {
            .chevron-icon {
                font-size: 1.2rem;
                transition: all 0.3s ease;
                color: #94a3b8;
            }
        }

        &.logout-item {
            margin-top: 8px;
            border-top: 1px solid rgba(239, 68, 68, 0.1);

            .icon-container {
                background: linear-gradient(
                    135deg,
                    rgba(239, 68, 68, 0.08) 0%,
                    rgba(248, 113, 113, 0.12) 100%
                );
                border-color: rgba(239, 68, 68, 0.15);

                .q-icon {
                    color: #ef4444;
                }

                .logout-ripple {
                    background: linear-gradient(
                        135deg,
                        rgba(239, 68, 68, 0.1),
                        rgba(248, 113, 113, 0.15)
                    );
                }
            }

            .item-title {
                color: #dc2626;
            }

            &:hover {
                background: linear-gradient(
                    135deg,
                    rgba(239, 68, 68, 0.08) 0%,
                    rgba(248, 113, 113, 0.05) 100%
                );
                color: #dc2626;

                .icon-container {
                    background: linear-gradient(
                        135deg,
                        rgba(239, 68, 68, 0.15) 0%,
                        rgba(248, 113, 113, 0.2) 100%
                    );
                    border-color: rgba(239, 68, 68, 0.3);
                }

                .chevron-icon {
                    color: #ef4444;
                }
            }
        }
    }

    .logout-separator {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(239, 68, 68, 0.15), transparent);
        margin: 8px 20px;
    }
}

// 动画效果
@keyframes techScan {
    0% {
        transform: translateX(-100%);
    }
    100% {
        transform: translateX(100%);
    }
}

@keyframes iconPulse {
    0%,
    100% {
        opacity: 0.3;
        transform: translate(-50%, -50%) scale(1);
    }
    50% {
        opacity: 0.6;
        transform: translate(-50%, -50%) scale(1.1);
    }
}

@keyframes ringRotate {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}

@keyframes statusBeat {
    0%,
    100% {
        opacity: 1;
        transform: scale(1);
    }
    50% {
        opacity: 0.8;
        transform: scale(0.95);
    }
}

@keyframes gridFloat {
    0% {
        transform: translate(0, 0);
    }
    100% {
        transform: translate(20px, 20px);
    }
}

// 响应式设计
@media (max-width: 768px) {
    .ling-header {
        // 移动端保持固定位置
        position: fixed;
        top: 0;
        z-index: 1000;
    }

    .brand-text .brand-subtitle {
        display: none;
    }

    .user-info-card {
        display: none;
    }

    .header-toolbar {
        padding: 0 16px;
    }
}
</style>

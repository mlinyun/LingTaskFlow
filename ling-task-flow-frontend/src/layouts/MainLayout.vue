<template>
    <ConfirmationDialogProvider>
        <ShortcutProvider>
            <q-layout view="hHh Lpr lFf">
                <!-- 使用独立的 AppHeader 组件 -->
                <app-header @toggleDrawer="toggleLeftDrawer" />

                <!-- 使用独立的 AppDrawer 组件 -->
                <app-drawer v-model="leftDrawerOpen" :navigation-links="navigationLinks" />

                <q-page-container class="main-page-container">
                    <router-view />
                </q-page-container>

                <!-- 全局错误通知 -->
                <ErrorNotification ref="errorNotificationRef" />
            </q-layout>
        </ShortcutProvider>
    </ConfirmationDialogProvider>
</template>

<script setup lang="ts">
import { ref, onMounted, provide } from 'vue';
import AppHeader from 'components/layout/AppHeader.vue';
import AppDrawer from 'components/layout/AppDrawer.vue';
import ErrorNotification from 'components/common/ErrorNotification.vue';
import ConfirmationDialogProvider from 'components/common/ConfirmationDialogProvider.vue';
import ShortcutProvider from 'components/common/ShortcutProvider.vue';
import { apiErrorHandler } from 'src/utils/errorHandler';

// 响应式数据
const leftDrawerOpen = ref(false);
const errorNotificationRef = ref<InstanceType<typeof ErrorNotification> | null>(null);

// 初始化错误处理器
onMounted(() => {
    apiErrorHandler.init();
});

// 为子组件提供错误处理方法
provide('errorHandler', {
    showNetworkError: (message: string, retryAction?: () => void) => {
        errorNotificationRef.value?.showNetworkError(message, retryAction);
    },
    showApiError: (message: string, retryAction?: () => void) => {
        errorNotificationRef.value?.showApiError(message, retryAction);
    },
    showValidationError: (message: string) => {
        errorNotificationRef.value?.showValidationError(message);
    },
    showPermissionError: (message: string) => {
        errorNotificationRef.value?.showPermissionError(message);
    },
    showSystemError: (message: string) => {
        errorNotificationRef.value?.showSystemError(message);
    },
});

// 导航链接配置
const navigationLinks = [
    {
        title: '平台首页',
        caption: '欢迎页面和功能概览',
        icon: 'home',
        link: '/',
        color: 'primary',
    },
    {
        title: '任务列表',
        caption: '查看和管理您的任务',
        icon: 'list',
        link: '/tasks',
        color: 'secondary',
    },
    {
        title: '数据概览',
        caption: '任务统计和分析',
        icon: 'dashboard',
        link: '/dashboard',
        color: 'info',
    },
    {
        title: '回收站',
        caption: '已删除的任务',
        icon: 'delete',
        link: '/trash',
        color: 'warning',
    },
];

// 方法
const toggleLeftDrawer = () => {
    leftDrawerOpen.value = !leftDrawerOpen.value;
};
</script>

<style lang="scss" scoped>
.main-page-container {
    // 确保容器占满剩余空间
    height: 100vh;
    min-height: 100vh;

    // 为固定的顶部导航栏留出空间
    padding-top: 64px;

    // 处理内容溢出
    overflow: auto;

    // 确保内容不会超出视窗
    max-width: 100vw;

    // 确保子元素正确布局
    display: flex;
    flex-direction: column;

    // 处理滚动条样式 - 柔和蓝白科技风格
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

// 确保 router-view 内容正确填充
:deep(.q-page) {
    // 确保页面内容正确占据空间
    min-height: calc(100vh - var(--header-height-desktop)); // 减去头部高度
    width: 100%;

    // 处理页面内容溢出
    overflow-x: auto;
    overflow-y: auto;

    // 为页面内容添加基本内边距
    padding: 1.5rem;
    box-sizing: border-box;

    // 确保内容不会超出容器
    max-width: 100%;
    word-wrap: break-word;
    word-break: break-word;

    // 页面内容滚动条样式 - 柔和蓝白科技风格
    &::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }

    &::-webkit-scrollbar-track {
        background: linear-gradient(to bottom, #f8fafc, #f1f5f9);
        border-radius: 3px;
        border: 1px solid rgba(148, 163, 184, 0.1);
    }

    &::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #cbd5e1, #94a3b8);
        border-radius: 3px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 1px 2px rgba(148, 163, 184, 0.1);
        transition: all 0.2s ease;

        &:hover {
            background: linear-gradient(135deg, #94a3b8, #64748b);
            border-color: rgba(255, 255, 255, 0.4);
            box-shadow: 0 1px 3px rgba(148, 163, 184, 0.15);
        }

        &:active {
            background: linear-gradient(135deg, #64748b, #475569);
        }
    }
}

// 处理移动端适配
@media (max-width: 768px) {
    .main-page-container {
        // 移动端保持相同的顶部边距
        padding-top: 64px;

        // 移动端减少内边距
        :deep(.q-page) {
            padding: 0.5rem;
            min-height: calc(100vh - 64px); // 减去固定导航栏高度
        }
    }
}

// 处理超宽屏幕
@media (min-width: 1920px) {
    .main-page-container {
        :deep(.q-page) {
            // 超宽屏幕限制最大内容宽度
            max-width: 1600px;
            margin: 0 auto;
        }
    }
}
</style>

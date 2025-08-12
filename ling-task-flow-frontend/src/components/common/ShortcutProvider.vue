<template>
    <!-- 快捷键帮助对话框 -->
    <ShortcutHelpDialog v-model="showShortcutHelp" />

    <!-- 插槽内容 -->
    <slot />
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useGlobalShortcuts } from '../../composables/useKeyboardShortcuts';
import ShortcutHelpDialog from './ShortcutHelpDialog.vue';

// 路由
const router = useRouter();

// 快捷键管理
const shortcuts = useGlobalShortcuts();

// 快捷键帮助对话框状态
const showShortcutHelp = ref(false);

// 注册全局快捷键
onMounted(() => {
    // 创建新任务
    shortcuts.registerShortcut('CREATE_TASK', {
        key: 'n',
        ctrl: true,
        description: '创建新任务',
        context: 'global',
        action: () => {
            // 触发创建任务事件
            window.dispatchEvent(new CustomEvent('shortcut:create-task'));
        },
    });

    // 搜索任务
    shortcuts.registerShortcut('SEARCH', {
        key: 'f',
        ctrl: true,
        description: '搜索任务',
        context: 'global',
        action: () => {
            // 触发搜索事件
            window.dispatchEvent(new CustomEvent('shortcut:search'));
        },
    });

    // 刷新页面
    shortcuts.registerShortcut('REFRESH', {
        key: 'r',
        ctrl: true,
        description: '刷新页面',
        context: 'global',
        action: () => {
            // 触发刷新事件
            window.dispatchEvent(new CustomEvent('shortcut:refresh'));
        },
    });

    // 关闭对话框
    shortcuts.registerShortcut('CLOSE_DIALOG', {
        key: 'Escape',
        description: '关闭对话框',
        context: 'dialog',
        action: () => {
            // 触发关闭对话框事件
            window.dispatchEvent(new CustomEvent('shortcut:close-dialog'));
        },
    });

    // 保存
    shortcuts.registerShortcut('SAVE', {
        key: 's',
        ctrl: true,
        description: '保存',
        context: 'dialog',
        action: () => {
            // 触发保存事件
            window.dispatchEvent(new CustomEvent('shortcut:save'));
        },
    });

    // 删除选中项
    shortcuts.registerShortcut('DELETE', {
        key: 'Delete',
        description: '删除选中项',
        context: 'task-list',
        action: () => {
            // 触发删除事件
            window.dispatchEvent(new CustomEvent('shortcut:delete'));
        },
    });

    // 全选
    shortcuts.registerShortcut('SELECT_ALL', {
        key: 'a',
        ctrl: true,
        description: '全选',
        context: 'task-list',
        action: () => {
            // 触发全选事件
            window.dispatchEvent(new CustomEvent('shortcut:select-all'));
        },
    });

    // 显示帮助
    shortcuts.registerShortcut('HELP', {
        key: 'F1',
        description: '显示快捷键帮助',
        context: 'global',
        action: () => {
            showShortcutHelp.value = true;
        },
    });

    // 快速操作面板
    shortcuts.registerShortcut('QUICK_ACTIONS', {
        key: 'k',
        ctrl: true,
        description: '快速操作面板',
        context: 'global',
        action: () => {
            // 触发快速操作面板事件
            window.dispatchEvent(new CustomEvent('shortcut:quick-actions'));
        },
    });

    // 跳转到仪表板
    shortcuts.registerShortcut('GO_TO_DASHBOARD', {
        key: '1',
        ctrl: true,
        description: '跳转到仪表板',
        context: 'global',
        action: () => {
            void router.push('/dashboard');
        },
    });

    // 跳转到任务列表
    shortcuts.registerShortcut('GO_TO_TASKS', {
        key: '2',
        ctrl: true,
        description: '跳转到任务列表',
        context: 'global',
        action: () => {
            void router.push('/tasks');
        },
    });

    // 跳转到回收站
    shortcuts.registerShortcut('GO_TO_TRASH', {
        key: '3',
        ctrl: true,
        description: '跳转到回收站',
        context: 'global',
        action: () => {
            void router.push('/trash');
        },
    });

    // 复制任务
    shortcuts.registerShortcut('COPY_TASK', {
        key: 'c',
        ctrl: true,
        shift: true,
        description: '复制选中任务',
        context: 'task-list',
        action: () => {
            window.dispatchEvent(new CustomEvent('shortcut:copy-task'));
        },
    });

    // 新建标签页打开任务
    shortcuts.registerShortcut('OPEN_TASK_NEW_TAB', {
        key: 'Enter',
        ctrl: true,
        description: '在新标签页打开任务',
        context: 'task-list',
        action: () => {
            window.dispatchEvent(new CustomEvent('shortcut:open-task-new-tab'));
        },
    });

    // 切换侧边栏
    shortcuts.registerShortcut('TOGGLE_SIDEBAR', {
        key: 'b',
        ctrl: true,
        description: '切换侧边栏',
        context: 'global',
        action: () => {
            window.dispatchEvent(new CustomEvent('shortcut:toggle-sidebar'));
        },
    });

    // 切换主题
    shortcuts.registerShortcut('TOGGLE_THEME', {
        key: 't',
        ctrl: true,
        shift: true,
        description: '切换主题',
        context: 'global',
        action: () => {
            window.dispatchEvent(new CustomEvent('shortcut:toggle-theme'));
        },
    });
});

// 全局快捷键类型声明
declare global {
    interface Window {
        $shortcuts: ReturnType<typeof useGlobalShortcuts>;
    }
}

// 在挂载后将快捷键方法挂载到全局
onMounted(() => {
    if (typeof window !== 'undefined') {
        window.$shortcuts = shortcuts;
    }
});
</script>

<style scoped>
/* 这个组件不需要特殊样式 */
</style>

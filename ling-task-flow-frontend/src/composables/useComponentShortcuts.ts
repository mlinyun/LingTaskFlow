/**
 * 组件快捷键增强组合式 API
 * 为组件提供便捷的快捷键集成功能
 */

import { onMounted, onUnmounted } from 'vue';
import { useGlobalShortcuts } from './useKeyboardShortcuts';

export interface ComponentShortcutOptions {
    context?: string;
    autoSetContext?: boolean;
    shortcuts?: Record<
        string,
        {
            key: string;
            ctrl?: boolean;
            alt?: boolean;
            shift?: boolean;
            meta?: boolean;
            description: string;
            action: () => void;
            disabled?: boolean;
        }
    >;
}

export function useComponentShortcuts(options: ComponentShortcutOptions = {}) {
    const shortcuts = useGlobalShortcuts();
    const registeredShortcuts = new Set<string>();

    const {
        context = 'component',
        autoSetContext = true,
        shortcuts: shortcutConfigs = {},
    } = options;

    // 添加快捷键提示到tooltip
    const addShortcutTooltip = (originalTooltip: string, shortcutKey: string): string => {
        const shortcutConfig = shortcuts.getShortcut(shortcutKey);
        if (!shortcutConfig) return originalTooltip;

        const shortcutText = shortcuts.formatShortcut(shortcutConfig);
        return `${originalTooltip} (${shortcutText})`;
    };

    // 注册组件快捷键
    const registerComponentShortcuts = () => {
        Object.entries(shortcutConfigs).forEach(([id, config]) => {
            const fullId = `${context}:${id}`;
            shortcuts.registerShortcut(fullId, {
                ...config,
                context,
            });
            registeredShortcuts.add(fullId);
        });
    };

    // 注册单个快捷键
    const registerShortcut = (
        id: string,
        config: {
            key: string;
            ctrl?: boolean;
            alt?: boolean;
            shift?: boolean;
            meta?: boolean;
            description: string;
            action: () => void;
            disabled?: boolean;
        },
    ) => {
        const fullId = `${context}:${id}`;
        shortcuts.registerShortcut(fullId, {
            ...config,
            context,
        });
        registeredShortcuts.add(fullId);
    };

    // 取消注册快捷键
    const unregisterShortcut = (id: string) => {
        const fullId = `${context}:${id}`;
        shortcuts.unregisterShortcut(fullId);
        registeredShortcuts.delete(fullId);
    };

    // 启用/禁用快捷键
    const setShortcutEnabled = (id: string, enabled: boolean) => {
        const fullId = `${context}:${id}`;
        shortcuts.setShortcutEnabled(fullId, enabled);
    };

    // 监听自定义事件
    const addEventListener = (eventName: string, handler: () => void) => {
        window.addEventListener(eventName, handler);
        return () => window.removeEventListener(eventName, handler);
    };

    // 触发自定义事件
    const dispatchEvent = (eventName: string, data?: unknown) => {
        window.dispatchEvent(new CustomEvent(eventName, { detail: data }));
    };

    // 生命周期管理
    onMounted(() => {
        if (autoSetContext) {
            shortcuts.setContext(context);
        }
        registerComponentShortcuts();
    });

    onUnmounted(() => {
        // 清理注册的快捷键
        registeredShortcuts.forEach(id => {
            shortcuts.unregisterShortcut(id);
        });
        registeredShortcuts.clear();
    });

    return {
        // 快捷键管理
        registerShortcut,
        unregisterShortcut,
        setShortcutEnabled,
        addShortcutTooltip,

        // 事件管理
        addEventListener,
        dispatchEvent,

        // 上下文管理
        setContext: shortcuts.setContext,

        // 工具方法
        formatShortcut: shortcuts.formatShortcut,

        // 全局快捷键实例
        shortcuts,
    };
}

// 预定义的常用快捷键配置
export const COMMON_SHORTCUTS = {
    // 对话框相关
    dialog: {
        save: {
            key: 's',
            ctrl: true,
            description: '保存并关闭',
        },
        cancel: {
            key: 'Escape',
            description: '取消并关闭',
        },
        confirm: {
            key: 'Enter',
            ctrl: true,
            description: '确认操作',
        },
    },

    // 列表相关
    list: {
        create: {
            key: 'n',
            ctrl: true,
            description: '创建新项',
        },
        refresh: {
            key: 'r',
            ctrl: true,
            description: '刷新列表',
        },
        search: {
            key: 'f',
            ctrl: true,
            description: '搜索',
        },
        selectAll: {
            key: 'a',
            ctrl: true,
            description: '全选',
        },
        delete: {
            key: 'Delete',
            description: '删除选中项',
        },
    },

    // 任务相关
    task: {
        complete: {
            key: 'Enter',
            description: '完成任务',
        },
        edit: {
            key: 'e',
            description: '编辑任务',
        },
        copy: {
            key: 'c',
            ctrl: true,
            shift: true,
            description: '复制任务',
        },
        priority: {
            key: 'p',
            description: '切换优先级',
        },
    },
};

// 快捷键工具函数
export const shortcutUtils = {
    // 创建带快捷键的tooltip
    createTooltip: (text: string, shortcut?: string) => {
        if (!shortcut) return text;
        const shortcuts = useGlobalShortcuts();
        const config = shortcuts.getShortcut(shortcut);
        if (!config) return text;

        const shortcutText = shortcuts.formatShortcut(config);
        return `${text} (${shortcutText})`;
    },

    // 检查快捷键是否可用
    isShortcutAvailable: (shortcut: string) => {
        const shortcuts = useGlobalShortcuts();
        return shortcuts.getShortcut(shortcut) !== undefined;
    },

    // 格式化快捷键显示
    formatShortcut: (config: {
        key: string;
        ctrl?: boolean;
        alt?: boolean;
        shift?: boolean;
        meta?: boolean;
    }) => {
        const shortcuts = useGlobalShortcuts();
        return shortcuts.formatShortcut({
            ...config,
            description: '',
            action: () => {},
        });
    },
};

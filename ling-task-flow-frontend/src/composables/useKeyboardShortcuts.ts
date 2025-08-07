/**
 * 键盘快捷键组合式 API
 * 提供全局快捷键管理功能
 */

import { onMounted, onUnmounted, ref, computed } from 'vue';

// 快捷键配置类型
export interface ShortcutConfig {
    key: string;
    ctrl?: boolean;
    alt?: boolean;
    shift?: boolean;
    meta?: boolean;
    description: string;
    action: () => void;
    context?: string; // 上下文，如 'global', 'task-list', 'dialog' 等
    disabled?: boolean;
}

// 快捷键组合类型
export interface KeyCombination {
    key: string;
    ctrl: boolean;
    alt: boolean;
    shift: boolean;
    meta: boolean;
}

// 预定义的快捷键配置
export const DEFAULT_SHORTCUTS: Record<string, Omit<ShortcutConfig, 'action'>> = {
    CREATE_TASK: {
        key: 'n',
        ctrl: true,
        description: '创建新任务',
        context: 'global',
    },
    SEARCH: {
        key: 'f',
        ctrl: true,
        description: '搜索任务',
        context: 'global',
    },
    REFRESH: {
        key: 'r',
        ctrl: true,
        description: '刷新页面',
        context: 'global',
    },
    SAVE: {
        key: 's',
        ctrl: true,
        description: '保存',
        context: 'dialog',
    },
    CLOSE_DIALOG: {
        key: 'Escape',
        description: '关闭对话框',
        context: 'dialog',
    },
    DELETE: {
        key: 'Delete',
        description: '删除选中项',
        context: 'task-list',
    },
    SELECT_ALL: {
        key: 'a',
        ctrl: true,
        description: '全选',
        context: 'task-list',
    },
    HELP: {
        key: 'F1',
        description: '显示帮助',
        context: 'global',
    },
    QUICK_ACTIONS: {
        key: 'k',
        ctrl: true,
        description: '快速操作面板',
        context: 'global',
    },
    GO_TO_DASHBOARD: {
        key: '1',
        ctrl: true,
        description: '跳转到仪表板',
        context: 'global',
    },
    GO_TO_TASKS: {
        key: '2',
        ctrl: true,
        description: '跳转到任务列表',
        context: 'global',
    },
    GO_TO_TRASH: {
        key: '3',
        ctrl: true,
        description: '跳转到回收站',
        context: 'global',
    },
};

export function useKeyboardShortcuts() {
    const shortcuts = ref<Map<string, ShortcutConfig>>(new Map());
    const isEnabled = ref(true);
    const currentContext = ref<string>('global');

    // 将按键组合转换为字符串键
    const getShortcutKey = (combination: KeyCombination): string => {
        const parts: string[] = [];
        if (combination.ctrl) parts.push('ctrl');
        if (combination.alt) parts.push('alt');
        if (combination.shift) parts.push('shift');
        if (combination.meta) parts.push('meta');
        parts.push(combination.key.toLowerCase());
        return parts.join('+');
    };

    // 从事件创建按键组合
    const getKeyComboFromEvent = (event: KeyboardEvent): KeyCombination => {
        return {
            key: event.key,
            ctrl: event.ctrlKey,
            alt: event.altKey,
            shift: event.shiftKey,
            meta: event.metaKey,
        };
    };

    // 注册快捷键
    const registerShortcut = (id: string, config: ShortcutConfig) => {
        shortcuts.value.set(id, config);
    };

    // 取消注册快捷键
    const unregisterShortcut = (id: string) => {
        shortcuts.value.delete(id);
    };

    // 禁用/启用快捷键
    const setShortcutEnabled = (id: string, enabled: boolean) => {
        const shortcut = shortcuts.value.get(id);
        if (shortcut) {
            shortcut.disabled = !enabled;
        }
    };

    // 设置当前上下文
    const setContext = (context: string) => {
        currentContext.value = context;
    };

    // 获取当前上下文的快捷键
    const getContextShortcuts = computed(() => {
        return Array.from(shortcuts.value.entries())
            .filter(([, config]) => 
                !config.disabled && 
                (config.context === 'global' || config.context === currentContext.value)
            )
            .map(([id, config]) => ({ id, ...config }));
    });

    // 格式化快捷键显示文本
    const formatShortcut = (config: ShortcutConfig): string => {
        const parts: string[] = [];
        
        // 根据操作系统显示不同的修饰键符号
        const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
        
        if (config.ctrl) parts.push(isMac ? '⌘' : 'Ctrl');
        if (config.alt) parts.push(isMac ? '⌥' : 'Alt');
        if (config.shift) parts.push(isMac ? '⇧' : 'Shift');
        if (config.meta) parts.push(isMac ? '⌘' : 'Win');
        
        // 特殊按键映射
        const keyMap: Record<string, string> = {
            'Escape': 'Esc',
            'Delete': 'Del',
            'ArrowUp': '↑',
            'ArrowDown': '↓',
            'ArrowLeft': '←',
            'ArrowRight': '→',
            ' ': 'Space',
        };
        
        const displayKey = keyMap[config.key] || config.key.toUpperCase();
        parts.push(displayKey);
        
        return parts.join(isMac ? '' : '+');
    };

    // 键盘事件处理器
    const handleKeyDown = (event: KeyboardEvent) => {
        if (!isEnabled.value) return;

        // 如果焦点在输入框中，跳过某些快捷键
        const activeElement = document.activeElement;
        const isInputFocused = activeElement && (
            activeElement.tagName === 'INPUT' ||
            activeElement.tagName === 'TEXTAREA' ||
            (activeElement as HTMLElement).contentEditable === 'true'
        );

        const combo = getKeyComboFromEvent(event);
        const shortcutKey = getShortcutKey(combo);

        // 查找匹配的快捷键
        for (const [id, config] of shortcuts.value.entries()) {
            if (config.disabled) continue;
            
            const configCombo = {
                key: config.key,
                ctrl: config.ctrl || false,
                alt: config.alt || false,
                shift: config.shift || false,
                meta: config.meta || false,
            };
            
            const configKey = getShortcutKey(configCombo);
            
            if (configKey === shortcutKey) {
                // 检查上下文
                if (config.context && config.context !== 'global' && config.context !== currentContext.value) {
                    continue;
                }
                
                // 对于某些快捷键，在输入框中不响应
                if (isInputFocused && ['ctrl+a', 'ctrl+c', 'ctrl+v', 'ctrl+x', 'ctrl+z'].includes(shortcutKey)) {
                    continue;
                }
                
                event.preventDefault();
                event.stopPropagation();
                
                try {
                    config.action();
                } catch (error) {
                    console.error(`Error executing shortcut ${id}:`, error);
                }
                
                break;
            }
        }
    };

    // 全局启用/禁用快捷键
    const setEnabled = (enabled: boolean) => {
        isEnabled.value = enabled;
    };

    // 获取快捷键配置
    const getShortcut = (id: string) => {
        return shortcuts.value.get(id);
    };

    // 清除所有快捷键
    const clearShortcuts = () => {
        shortcuts.value.clear();
    };

    // 批量注册快捷键
    const registerShortcuts = (configs: Record<string, ShortcutConfig>) => {
        Object.entries(configs).forEach(([id, config]) => {
            registerShortcut(id, config);
        });
    };

    // 生命周期管理
    onMounted(() => {
        document.addEventListener('keydown', handleKeyDown, true);
    });

    onUnmounted(() => {
        document.removeEventListener('keydown', handleKeyDown, true);
        clearShortcuts();
    });

    return {
        // 状态
        shortcuts: shortcuts.value,
        isEnabled,
        currentContext,
        
        // 计算属性
        contextShortcuts: getContextShortcuts,
        
        // 方法
        registerShortcut,
        unregisterShortcut,
        setShortcutEnabled,
        setContext,
        setEnabled,
        getShortcut,
        clearShortcuts,
        registerShortcuts,
        formatShortcut,
        
        // 实用工具
        DEFAULT_SHORTCUTS,
    };
}

// 全局快捷键实例
let globalShortcuts: ReturnType<typeof useKeyboardShortcuts> | null = null;

export function useGlobalShortcuts() {
    if (!globalShortcuts) {
        globalShortcuts = useKeyboardShortcuts();
    }
    return globalShortcuts;
}

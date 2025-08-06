/**
 * 确认对话框组合式 API
 * 提供便捷的确认对话框管理功能
 */

import { reactive } from 'vue';

// 定义确认对话框类型
export type ConfirmDialogType = 'info' | 'warning' | 'danger' | 'success';

export interface ConfirmOptions {
    type?: ConfirmDialogType;
    title: string;
    message: string;
    details?: string | undefined;
    warningText?: string | undefined;
    confirmText?: string;
    cancelText?: string;
    confirmIcon?: string;
    persistent?: boolean;
    loadingText?: string;
}

export interface ConfirmDialogState {
    visible: boolean;
    loading: boolean;
    type: ConfirmDialogType;
    title: string;
    message: string;
    details?: string | undefined;
    warningText?: string | undefined;
    confirmText: string;
    cancelText: string;
    confirmIcon: string;
    persistent: boolean;
    loadingText: string;
}

export interface UseConfirmDialogReturn {
    state: ConfirmDialogState;
    confirm: (options: ConfirmOptions) => Promise<boolean>;
    hide: () => void;
    setLoading: (loading: boolean, text?: string) => void;
    confirmInfo: (
        title: string,
        message: string,
        options?: Partial<ConfirmOptions>,
    ) => Promise<boolean>;
    confirmWarning: (
        title: string,
        message: string,
        options?: Partial<ConfirmOptions>,
    ) => Promise<boolean>;
    confirmDanger: (
        title: string,
        message: string,
        options?: Partial<ConfirmOptions>,
    ) => Promise<boolean>;
    confirmSuccess: (
        title: string,
        message: string,
        options?: Partial<ConfirmOptions>,
    ) => Promise<boolean>;
    handleConfirm: () => void;
    handleCancel: () => void;
}

export function useConfirmDialog(): UseConfirmDialogReturn {
    // 对话框状态
    const state = reactive<ConfirmDialogState>({
        visible: false,
        loading: false,
        type: 'info',
        title: '',
        message: '',
        details: undefined,
        warningText: undefined,
        confirmText: '确认',
        cancelText: '取消',
        confirmIcon: 'check',
        persistent: false,
        loadingText: '处理中...',
    });

    // Promise 相关
    let resolvePromise: ((value: boolean) => void) | null = null;

    /**
     * 显示确认对话框
     */
    const confirm = (options: ConfirmOptions): Promise<boolean> => {
        return new Promise(resolve => {
            // 保存 Promise 的 resolve
            resolvePromise = resolve;

            // 更新状态
            Object.assign(state, {
                visible: true,
                loading: false,
                type: options.type || 'info',
                title: options.title,
                message: options.message,
                details: options.details,
                warningText: options.warningText,
                confirmText: options.confirmText || '确认',
                cancelText: options.cancelText || '取消',
                confirmIcon: options.confirmIcon || getDefaultIcon(options.type || 'info'),
                persistent: options.persistent || false,
                loadingText: options.loadingText || '处理中...',
            });
        });
    };

    /**
     * 快捷方法：信息确认
     */
    const confirmInfo = (title: string, message: string, options?: Partial<ConfirmOptions>) => {
        return confirm({
            type: 'info',
            title,
            message,
            confirmIcon: 'check',
            ...options,
        });
    };

    /**
     * 快捷方法：警告确认
     */
    const confirmWarning = (title: string, message: string, options?: Partial<ConfirmOptions>) => {
        return confirm({
            type: 'warning',
            title,
            message,
            confirmIcon: 'warning',
            ...options,
        });
    };

    /**
     * 快捷方法：危险操作确认
     */
    const confirmDanger = (title: string, message: string, options?: Partial<ConfirmOptions>) => {
        return confirm({
            type: 'danger',
            title,
            message,
            confirmText: '删除',
            confirmIcon: 'delete',
            warningText: '此操作不可撤销，请谨慎操作',
            ...options,
        });
    };

    /**
     * 快捷方法：成功确认
     */
    const confirmSuccess = (title: string, message: string, options?: Partial<ConfirmOptions>) => {
        return confirm({
            type: 'success',
            title,
            message,
            confirmIcon: 'check_circle',
            ...options,
        });
    };

    /**
     * 处理确认操作
     */
    const handleConfirm = () => {
        if (resolvePromise) {
            resolvePromise(true);
            resolvePromise = null;
        }
        hide();
    };

    /**
     * 处理取消操作
     */
    const handleCancel = () => {
        if (resolvePromise) {
            resolvePromise(false);
            resolvePromise = null;
        }
        hide();
    };

    /**
     * 设置加载状态
     */
    const setLoading = (loading: boolean, loadingText?: string) => {
        state.loading = loading;
        if (loadingText) {
            state.loadingText = loadingText;
        }
    };

    /**
     * 隐藏对话框
     */
    const hide = () => {
        state.visible = false;
        state.loading = false;
    };

    /**
     * 获取默认图标
     */
    const getDefaultIcon = (type: ConfirmDialogType): string => {
        const iconMap: Record<ConfirmDialogType, string> = {
            info: 'check',
            warning: 'warning',
            danger: 'delete',
            success: 'check_circle',
        };
        return iconMap[type];
    };

    return {
        // 状态
        state,

        // 基础方法
        confirm,
        hide,
        setLoading,

        // 快捷方法
        confirmInfo,
        confirmWarning,
        confirmDanger,
        confirmSuccess,

        // 事件处理
        handleConfirm,
        handleCancel,
    };
}

/**
 * 预定义的常用确认对话框配置
 */
export const ConfirmPresets = {
    // 删除任务
    deleteTask: (taskTitle: string) => ({
        type: 'danger' as ConfirmDialogType,
        title: '删除任务',
        message: `确定要删除任务"${taskTitle}"吗？`,
        details: '任务删除后将移至回收站，可在30天内恢复。',
        warningText: '删除后的任务可以在回收站中找到',
        confirmText: '删除',
        confirmIcon: 'delete',
    }),

    // 永久删除任务
    permanentDeleteTask: (taskTitle: string) => ({
        type: 'danger' as ConfirmDialogType,
        title: '永久删除任务',
        message: `确定要永久删除任务"${taskTitle}"吗？`,
        details: '永久删除后将无法恢复，请谨慎操作。',
        warningText: '此操作不可撤销，数据将永久丢失',
        confirmText: '永久删除',
        confirmIcon: 'delete_forever',
        persistent: true,
    }),

    // 批量删除任务
    batchDeleteTasks: (count: number) => ({
        type: 'danger' as ConfirmDialogType,
        title: '批量删除任务',
        message: `确定要删除选中的 ${count} 个任务吗？`,
        details: '所有选中的任务都将被移至回收站。',
        warningText: '批量操作将同时影响多个任务',
        confirmText: '批量删除',
        confirmIcon: 'delete',
    }),

    // 恢复任务
    restoreTask: (taskTitle: string) => ({
        type: 'info' as ConfirmDialogType,
        title: '恢复任务',
        message: `确定要恢复任务"${taskTitle}"吗？`,
        details: '任务将从回收站移回到任务列表中。',
        confirmText: '恢复',
        confirmIcon: 'restore',
    }),

    // 批量恢复任务
    batchRestoreTasks: (count: number) => ({
        type: 'info' as ConfirmDialogType,
        title: '批量恢复任务',
        message: `确定要恢复选中的 ${count} 个任务吗？`,
        details: '所有选中的任务都将从回收站恢复到任务列表。',
        confirmText: '批量恢复',
        confirmIcon: 'restore',
    }),

    // 清空回收站
    clearTrash: () => ({
        type: 'danger' as ConfirmDialogType,
        title: '清空回收站',
        message: '确定要清空回收站吗？',
        details: '回收站中的所有任务都将被永久删除。',
        warningText: '此操作不可撤销，所有数据将永久丢失',
        confirmText: '清空回收站',
        confirmIcon: 'delete_sweep',
        persistent: true,
    }),

    // 完成任务
    completeTask: (taskTitle: string) => ({
        type: 'success' as ConfirmDialogType,
        title: '完成任务',
        message: `确定要标记任务"${taskTitle}"为已完成吗？`,
        details: '任务完成后可以在已完成列表中查看。',
        confirmText: '标记完成',
        confirmIcon: 'task_alt',
    }),

    // 重新打开任务
    reopenTask: (taskTitle: string) => ({
        type: 'warning' as ConfirmDialogType,
        title: '重新打开任务',
        message: `确定要重新打开任务"${taskTitle}"吗？`,
        details: '任务将从已完成状态变为进行中状态。',
        confirmText: '重新打开',
        confirmIcon: 'replay',
    }),

    // 退出登录
    logout: () => ({
        type: 'warning' as ConfirmDialogType,
        title: '退出登录',
        message: '确定要退出登录吗？',
        details: '退出后需要重新登录才能使用应用。',
        confirmText: '退出登录',
        confirmIcon: 'logout',
    }),

    // 取消编辑
    cancelEdit: () => ({
        type: 'warning' as ConfirmDialogType,
        title: '取消编辑',
        message: '确定要取消编辑吗？',
        details: '未保存的更改将会丢失。',
        warningText: '当前的修改内容将不会被保存',
        confirmText: '取消编辑',
        confirmIcon: 'cancel',
    }),
};

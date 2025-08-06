/**
 * 使用全局确认对话框的组合式函数
 */

import { inject } from 'vue';
import type { UseConfirmDialogReturn } from './useConfirmDialog';

export function useGlobalConfirm(): UseConfirmDialogReturn {
    // 尝试获取注入的确认对话框
    const confirmDialog = inject<UseConfirmDialogReturn | null>('confirmDialog', null);

    if (!confirmDialog) {
        // 如果在开发环境，显示警告
        if (process.env.NODE_ENV === 'development') {
            console.warn(
                'ConfirmDialog not provided. Make sure ConfirmDialogProvider is mounted before using useGlobalConfirm.',
            );
        }

        // 返回一个空的实现以避免错误
        return {
            state: {
                visible: false,
                loading: false,
                type: 'info' as const,
                title: '',
                message: '',
                details: undefined,
                warningText: undefined,
                confirmText: '确认',
                cancelText: '取消',
                confirmIcon: 'check',
                persistent: false,
                loadingText: '处理中...',
            },
            confirm: async () => {
                console.warn('Confirm dialog not available');
                return Promise.resolve(false);
            },
            hide: () => {
                console.warn('Confirm dialog not available');
            },
            setLoading: () => {
                console.warn('Confirm dialog not available');
            },
            confirmInfo: async () => {
                console.warn('Confirm dialog not available');
                return Promise.resolve(false);
            },
            confirmWarning: async () => {
                console.warn('Confirm dialog not available');
                return Promise.resolve(false);
            },
            confirmDanger: async () => {
                console.warn('Confirm dialog not available');
                return Promise.resolve(false);
            },
            confirmSuccess: async () => {
                console.warn('Confirm dialog not available');
                return Promise.resolve(false);
            },
            handleConfirm: () => {
                console.warn('Confirm dialog not available');
            },
            handleCancel: () => {
                console.warn('Confirm dialog not available');
            },
        };
    }

    return confirmDialog;
}

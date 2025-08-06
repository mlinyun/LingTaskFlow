<template>
    <!-- 全局确认对话框提供器 -->
    <Teleport to="body">
        <ConfirmDialog
            v-model="confirmDialog.state.visible"
            :type="confirmDialog.state.type"
            :title="confirmDialog.state.title"
            :message="confirmDialog.state.message"
            :details="confirmDialog.state.details"
            :warning-text="confirmDialog.state.warningText"
            :confirm-text="confirmDialog.state.confirmText"
            :cancel-text="confirmDialog.state.cancelText"
            :confirm-icon="confirmDialog.state.confirmIcon"
            :persistent="confirmDialog.state.persistent"
            :loading="confirmDialog.state.loading"
            :loading-text="confirmDialog.state.loadingText"
            @confirm="confirmDialog.handleConfirm"
            @cancel="confirmDialog.handleCancel"
        />
    </Teleport>

    <!-- 插槽内容 -->
    <slot />
</template>

<script setup lang="ts">
import { provide, onMounted } from 'vue';
import ConfirmDialog from './ConfirmDialog.vue';
import { useConfirmDialog, type UseConfirmDialogReturn } from '../../composables/useConfirmDialog';

// 创建确认对话框实例
const confirmDialog: UseConfirmDialogReturn = useConfirmDialog();

// 立即提供给子组件使用
provide('confirmDialog', confirmDialog);

// 全局确认对话框类型声明
declare global {
    interface Window {
        $confirm: UseConfirmDialogReturn;
    }
}

// 在挂载后将确认对话框方法挂载到全局
onMounted(() => {
    if (typeof window !== 'undefined') {
        window.$confirm = confirmDialog;
    }
});
</script>

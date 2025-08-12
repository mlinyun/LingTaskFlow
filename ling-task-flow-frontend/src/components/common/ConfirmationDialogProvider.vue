<template>
    <!-- 全局确认对话框提供器 -->
    <Teleport to="body">
        <ConfirmationDialog
            v-model="confirmDialog.state.visible"
            :cancel-text="confirmDialog.state.cancelText"
            :confirm-icon="confirmDialog.state.confirmIcon"
            :confirm-text="confirmDialog.state.confirmText"
            :details="confirmDialog.state.details"
            :loading="confirmDialog.state.loading"
            :loading-text="confirmDialog.state.loadingText"
            :message="confirmDialog.state.message"
            :persistent="confirmDialog.state.persistent"
            :title="confirmDialog.state.title"
            :type="confirmDialog.state.type"
            :warning-text="confirmDialog.state.warningText"
            @cancel="confirmDialog.handleCancel"
            @confirm="confirmDialog.handleConfirm"
        />
    </Teleport>

    <!-- 插槽内容 -->
    <slot />
</template>

<script lang="ts" setup>
import { onMounted, provide } from 'vue';
import ConfirmationDialog from './ConfirmationDialog.vue';
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

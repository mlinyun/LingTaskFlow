<!--
  TaskCardSkeleton.vue
  任务卡片骨架屏组件
  用于任务列表加载时的占位显示
-->

<template>
    <q-card class="task-card-skeleton q-mb-md" flat bordered>
        <q-card-section class="q-pa-md">
            <!-- 任务标题骨架 -->
            <div class="row items-center q-mb-sm">
                <q-skeleton type="rect" width="60%" height="20px" class="q-mr-md" />
                <q-skeleton type="QChip" width="60px" height="24px" />
            </div>

            <!-- 任务描述骨架 -->
            <q-skeleton type="text" width="80%" height="16px" class="q-mb-sm" />
            <q-skeleton type="text" width="60%" height="16px" class="q-mb-md" />

            <!-- 标签骨架 -->
            <div class="row items-center q-mb-md q-gutter-xs">
                <q-skeleton type="QChip" width="50px" height="22px" />
                <q-skeleton type="QChip" width="60px" height="22px" />
                <q-skeleton type="QChip" width="45px" height="22px" />
            </div>

            <!-- 底部信息骨架 -->
            <div class="row items-center justify-between">
                <div class="row items-center q-gutter-md">
                    <!-- 优先级骨架 -->
                    <q-skeleton type="QChip" width="70px" height="24px" />
                    <!-- 进度骨架 -->
                    <div class="column">
                        <q-skeleton type="text" width="40px" height="12px" class="q-mb-xs" />
                        <q-skeleton type="rect" width="80px" height="4px" />
                    </div>
                </div>

                <!-- 时间信息骨架 -->
                <div class="column items-end">
                    <q-skeleton type="text" width="80px" height="12px" class="q-mb-xs" />
                    <q-skeleton type="text" width="60px" height="12px" />
                </div>
            </div>
        </q-card-section>

        <!-- 操作按钮骨架 -->
        <q-card-actions align="right" class="q-pa-md q-pt-none">
            <q-skeleton type="QBtn" width="60px" height="32px" class="q-mr-sm" />
            <q-skeleton type="QBtn" width="60px" height="32px" class="q-mr-sm" />
            <q-skeleton type="QBtn" width="60px" height="32px" />
        </q-card-actions>
    </q-card>
</template>

<script setup lang="ts">
// 无需逻辑，纯展示组件
</script>

<style lang="scss" scoped>
.task-card-skeleton {
    // 添加轻微的动画效果，让骨架屏更生动
    .q-skeleton {
        opacity: 0.7;
    }

    // 保持与实际任务卡片相同的最小高度
    min-height: 200px;

    // 轻微的阴影效果
    box-shadow:
        0 1px 3px rgba(0, 0, 0, 0.12),
        0 1px 2px rgba(0, 0, 0, 0.24);

    // 边框样式
    border: 1px solid rgba(0, 0, 0, 0.08);
}

// 暗色主题适配
.body--dark {
    .task-card-skeleton {
        border-color: rgba(255, 255, 255, 0.1);
        box-shadow:
            0 1px 3px rgba(255, 255, 255, 0.05),
            0 1px 2px rgba(255, 255, 255, 0.1);
    }
}
</style>

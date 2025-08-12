<!--
  TaskCardSkeleton.vue
  任务卡片骨架屏组件
  用于任务列表加载时的占位显示
-->

<template>
    <q-card bordered class="task-card-skeleton q-mb-md" flat>
        <q-card-section class="q-pa-md">
            <!-- 任务标题骨架 -->
            <div class="row items-center q-mb-sm">
                <q-skeleton class="q-mr-md" height="20px" type="rect" width="60%" />
                <q-skeleton height="24px" type="QChip" width="60px" />
            </div>

            <!-- 任务描述骨架 -->
            <q-skeleton class="q-mb-sm" height="16px" type="text" width="80%" />
            <q-skeleton class="q-mb-md" height="16px" type="text" width="60%" />

            <!-- 标签骨架 -->
            <div class="row items-center q-mb-md q-gutter-xs">
                <q-skeleton height="22px" type="QChip" width="50px" />
                <q-skeleton height="22px" type="QChip" width="60px" />
                <q-skeleton height="22px" type="QChip" width="45px" />
            </div>

            <!-- 底部信息骨架 -->
            <div class="row items-center justify-between">
                <div class="row items-center q-gutter-md">
                    <!-- 优先级骨架 -->
                    <q-skeleton height="24px" type="QChip" width="70px" />
                    <!-- 进度骨架 -->
                    <div class="column">
                        <q-skeleton class="q-mb-xs" height="12px" type="text" width="40px" />
                        <q-skeleton height="4px" type="rect" width="80px" />
                    </div>
                </div>

                <!-- 时间信息骨架 -->
                <div class="column items-end">
                    <q-skeleton class="q-mb-xs" height="12px" type="text" width="80px" />
                    <q-skeleton height="12px" type="text" width="60px" />
                </div>
            </div>
        </q-card-section>

        <!-- 操作按钮骨架 -->
        <q-card-actions align="right" class="q-pa-md q-pt-none">
            <q-skeleton class="q-mr-sm" height="32px" type="QBtn" width="60px" />
            <q-skeleton class="q-mr-sm" height="32px" type="QBtn" width="60px" />
            <q-skeleton height="32px" type="QBtn" width="60px" />
        </q-card-actions>
    </q-card>
</template>

<script lang="ts" setup>
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

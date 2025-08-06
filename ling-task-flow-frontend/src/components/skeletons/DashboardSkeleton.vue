<!--
  DashboardSkeleton.vue
  仪表板骨架屏组件
  用于仪表板页面加载时的占位显示
-->

<template>
    <div class="dashboard-skeleton q-pa-md">
        <!-- 页面标题骨架 -->
        <div class="q-mb-xl">
            <q-skeleton type="text" width="200px" height="32px" class="q-mb-sm" />
            <q-skeleton type="text" width="400px" height="16px" />
        </div>

        <!-- 统计卡片骨架 -->
        <div class="row q-gutter-md q-mb-xl">
            <div v-for="i in 4" :key="i" class="col-12 col-sm-6 col-md-3">
                <q-card class="stats-card-skeleton" flat bordered>
                    <q-card-section class="q-pa-lg">
                        <!-- 图标骨架 -->
                        <div class="row items-center justify-between q-mb-md">
                            <q-skeleton type="QAvatar" size="48px" />
                            <q-skeleton type="text" width="40px" height="16px" />
                        </div>

                        <!-- 数值骨架 -->
                        <q-skeleton type="text" width="80px" height="36px" class="q-mb-sm" />

                        <!-- 标题骨架 -->
                        <q-skeleton type="text" width="120px" height="16px" />
                    </q-card-section>
                </q-card>
            </div>
        </div>

        <!-- 图表区域骨架 -->
        <div class="row q-gutter-md q-mb-xl">
            <!-- 状态分布图表骨架 -->
            <div class="col-12 col-lg-6">
                <q-card flat bordered class="chart-skeleton">
                    <q-card-section class="q-pa-lg">
                        <q-skeleton type="text" width="150px" height="24px" class="q-mb-lg" />

                        <!-- 饼图骨架 -->
                        <div class="row justify-center q-mb-md">
                            <q-skeleton type="circle" size="200px" />
                        </div>

                        <!-- 图例骨架 -->
                        <div class="column q-gutter-sm">
                            <div v-for="i in 4" :key="i" class="row items-center q-gutter-sm">
                                <q-skeleton type="circle" size="12px" />
                                <q-skeleton type="text" width="80px" height="14px" />
                                <q-skeleton type="text" width="40px" height="14px" />
                            </div>
                        </div>
                    </q-card-section>
                </q-card>
            </div>

            <!-- 优先级分布图表骨架 -->
            <div class="col-12 col-lg-6">
                <q-card flat bordered class="chart-skeleton">
                    <q-card-section class="q-pa-lg">
                        <q-skeleton type="text" width="150px" height="24px" class="q-mb-lg" />

                        <!-- 柱状图骨架 -->
                        <div
                            class="row items-end justify-center q-gutter-sm q-mb-md"
                            style="height: 200px"
                        >
                            <q-skeleton
                                v-for="i in 4"
                                :key="i"
                                type="rect"
                                width="40px"
                                :height="`${120 + i * 20}px`"
                            />
                        </div>

                        <!-- 标签骨架 -->
                        <div class="row justify-center q-gutter-md">
                            <q-skeleton
                                v-for="i in 4"
                                :key="i"
                                type="text"
                                width="60px"
                                height="14px"
                            />
                        </div>
                    </q-card-section>
                </q-card>
            </div>
        </div>

        <!-- 最近活动骨架 -->
        <div class="row">
            <div class="col-12">
                <q-card flat bordered class="activity-skeleton">
                    <q-card-section class="q-pa-lg">
                        <q-skeleton type="text" width="150px" height="24px" class="q-mb-lg" />

                        <!-- 活动列表骨架 -->
                        <div class="column q-gutter-md">
                            <div v-for="i in 6" :key="i" class="row items-center q-gutter-md">
                                <!-- 活动图标骨架 -->
                                <q-skeleton type="QAvatar" size="32px" />

                                <!-- 活动内容骨架 -->
                                <div class="col">
                                    <q-skeleton
                                        type="text"
                                        width="80%"
                                        height="16px"
                                        class="q-mb-xs"
                                    />
                                    <q-skeleton type="text" width="120px" height="14px" />
                                </div>
                            </div>
                        </div>
                    </q-card-section>
                </q-card>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
// 无需逻辑，纯展示组件
</script>

<style lang="scss" scoped>
.dashboard-skeleton {
    .stats-card-skeleton,
    .chart-skeleton,
    .activity-skeleton {
        min-height: 250px;
        border: 1px solid rgba(0, 0, 0, 0.08);
        box-shadow:
            0 1px 3px rgba(0, 0, 0, 0.12),
            0 1px 2px rgba(0, 0, 0, 0.24);
    }

    .q-skeleton {
        opacity: 0.7;
    }
}

// 暗色主题适配
.body--dark {
    .dashboard-skeleton {
        .stats-card-skeleton,
        .chart-skeleton,
        .activity-skeleton {
            border-color: rgba(255, 255, 255, 0.1);
            box-shadow:
                0 1px 3px rgba(255, 255, 255, 0.05),
                0 1px 2px rgba(255, 255, 255, 0.1);
        }
    }
}
</style>

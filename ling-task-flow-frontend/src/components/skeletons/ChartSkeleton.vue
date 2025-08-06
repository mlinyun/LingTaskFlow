<!--
  ChartSkeleton.vue
  图表骨架屏组件
  用于图表加载时的占位显示，支持不同类型的图表
-->

<template>
    <div class="chart-skeleton">
        <!-- 图表标题骨架 -->
        <q-skeleton
            v-if="showTitle"
            type="text"
            :width="titleWidth"
            height="24px"
            class="q-mb-lg"
        />

        <!-- 图表内容区域 -->
        <div class="chart-content">
            <!-- 饼图骨架 -->
            <div v-if="type === 'pie'" class="pie-chart-skeleton">
                <div class="row justify-center q-mb-md">
                    <q-skeleton type="circle" :size="chartSize" />
                </div>

                <!-- 图例骨架 -->
                <div class="legend-skeleton column q-gutter-sm">
                    <div v-for="i in legendItems" :key="i" class="row items-center q-gutter-sm">
                        <q-skeleton type="circle" size="12px" />
                        <q-skeleton type="text" width="80px" height="14px" />
                        <q-skeleton type="text" width="40px" height="14px" />
                    </div>
                </div>
            </div>

            <!-- 柱状图骨架 -->
            <div v-else-if="type === 'bar'" class="bar-chart-skeleton">
                <!-- Y轴标签骨架 -->
                <div class="y-axis-skeleton">
                    <div v-for="i in 5" :key="i" class="y-label">
                        <q-skeleton type="text" width="30px" height="12px" />
                    </div>
                </div>

                <!-- 柱状图主体骨架 -->
                <div class="bars-container">
                    <div
                        class="row items-end justify-center q-gutter-sm q-mb-md"
                        :style="`height: ${parseInt(chartSize || '200')}px`"
                    >
                        <q-skeleton
                            v-for="i in barCount"
                            :key="i"
                            type="rect"
                            width="40px"
                            :height="`${Math.random() * 100 + 50}px`"
                        />
                    </div>

                    <!-- X轴标签骨架 -->
                    <div class="row justify-center q-gutter-md">
                        <q-skeleton
                            v-for="i in barCount"
                            :key="i"
                            type="text"
                            width="60px"
                            height="14px"
                        />
                    </div>
                </div>
            </div>

            <!-- 线图骨架 -->
            <div v-else-if="type === 'line'" class="line-chart-skeleton">
                <div class="chart-area" :style="`height: ${chartSize}`">
                    <!-- 网格线骨架 -->
                    <div class="grid-lines">
                        <q-skeleton
                            v-for="i in 5"
                            :key="`h-${i}`"
                            type="rect"
                            width="100%"
                            height="1px"
                            class="grid-line horizontal"
                        />
                        <q-skeleton
                            v-for="i in 7"
                            :key="`v-${i}`"
                            type="rect"
                            width="1px"
                            height="100%"
                            class="grid-line vertical"
                        />
                    </div>

                    <!-- 折线骨架 -->
                    <svg :width="chartSize || '200px'" :height="chartSize || '200px'" class="line-path">
                        <q-skeleton type="rect" width="80%" height="2px" class="line-skeleton" />
                    </svg>
                </div>
            </div>

            <!-- 通用图表骨架（默认） -->
            <div v-else class="generic-chart-skeleton">
                <q-skeleton type="rect" width="100%" :height="chartSize" />
            </div>
        </div>

        <!-- 图表描述骨架 -->
        <q-skeleton v-if="showDescription" type="text" width="60%" height="14px" class="q-mt-md" />
    </div>
</template>

<script setup lang="ts">
interface Props {
    // 图表类型：pie(饼图), bar(柱状图), line(折线图), generic(通用)
    type?: 'pie' | 'bar' | 'line' | 'generic';
    // 图表尺寸
    chartSize?: string;
    // 是否显示标题
    showTitle?: boolean;
    // 标题宽度
    titleWidth?: string;
    // 是否显示描述
    showDescription?: boolean;
    // 图例项目数量（饼图用）
    legendItems?: number;
    // 柱状图柱子数量
    barCount?: number;
}

withDefaults(defineProps<Props>(), {
    type: 'generic',
    chartSize: '200px',
    showTitle: true,
    titleWidth: '150px',
    showDescription: false,
    legendItems: 4,
    barCount: 4,
});
</script>

<style lang="scss" scoped>
.chart-skeleton {
    .chart-content {
        position: relative;
    }

    // 饼图骨架样式
    .pie-chart-skeleton {
        .legend-skeleton {
            max-width: 200px;
            margin: 0 auto;
        }
    }

    // 柱状图骨架样式
    .bar-chart-skeleton {
        position: relative;

        .y-axis-skeleton {
            position: absolute;
            left: 0;
            top: 0;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 10px 0;

            .y-label {
                height: 12px;
            }
        }

        .bars-container {
            margin-left: 40px;
        }
    }

    // 线图骨架样式
    .line-chart-skeleton {
        .chart-area {
            position: relative;
            border: 1px solid rgba(0, 0, 0, 0.1);
        }

        .grid-lines {
            position: absolute;
            width: 100%;
            height: 100%;

            .grid-line {
                position: absolute;
                opacity: 0.3;

                &.horizontal {
                    left: 0;

                    @for $i from 1 through 5 {
                        &:nth-child(#{$i}) {
                            top: #{($i - 1) * 25%};
                        }
                    }
                }

                &.vertical {
                    top: 0;

                    @for $i from 1 through 7 {
                        &:nth-child(#{$i + 5}) {
                            left: #{($i - 1) * 16.67%};
                        }
                    }
                }
            }
        }

        .line-path {
            position: absolute;
            top: 50%;
            left: 10%;
            transform: translateY(-50%);
        }
    }

    .q-skeleton {
        opacity: 0.7;
    }
}

// 暗色主题适配
.body--dark {
    .chart-skeleton {
        .line-chart-skeleton .chart-area {
            border-color: rgba(255, 255, 255, 0.2);
        }
    }
}
</style>

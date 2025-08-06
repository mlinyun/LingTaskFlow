<!--
  LoadingState.vue
  通用加载状态组件
  支持不同类型的加载指示器和文本
-->

<template>
    <div
        class="loading-state"
        :class="[`loading-state--${variant}`, { 'loading-state--overlay': overlay }]"
    >
        <!-- 覆盖层（当overlay为true时） -->
        <div v-if="overlay" class="loading-overlay" />

        <!-- 加载内容 -->
        <div class="loading-content">
            <!-- 自定义插槽内容 -->
            <slot name="spinner">
                <!-- 默认加载指示器 -->
                <q-spinner-dots v-if="spinner === 'dots'" :color="color" :size="size" />
                <q-spinner-ball v-else-if="spinner === 'ball'" :color="color" :size="size" />
                <q-spinner-bars v-else-if="spinner === 'bars'" :color="color" :size="size" />
                <q-spinner-cube v-else-if="spinner === 'cube'" :color="color" :size="size" />
                <q-spinner-gears v-else-if="spinner === 'gears'" :color="color" :size="size" />
                <q-spinner-hourglass
                    v-else-if="spinner === 'hourglass'"
                    :color="color"
                    :size="size"
                />
                <q-spinner-infinity
                    v-else-if="spinner === 'infinity'"
                    :color="color"
                    :size="size"
                />
                <q-spinner-oval v-else-if="spinner === 'oval'" :color="color" :size="size" />
                <q-spinner-pie v-else-if="spinner === 'pie'" :color="color" :size="size" />
                <q-spinner-puff v-else-if="spinner === 'puff'" :color="color" :size="size" />
                <q-spinner-radio v-else-if="spinner === 'radio'" :color="color" :size="size" />
                <q-spinner-rings v-else-if="spinner === 'rings'" :color="color" :size="size" />
                <q-spinner-tail v-else-if="spinner === 'tail'" :color="color" :size="size" />
                <q-spinner v-else :color="color" :size="size" />
            </slot>

            <!-- 加载文本 -->
            <div v-if="message" class="loading-message" :class="`text-${textColor}`">
                {{ message }}
            </div>

            <!-- 自定义内容插槽 -->
            <slot />
        </div>
    </div>
</template>

<script setup lang="ts">
interface Props {
    // 加载指示器类型
    spinner?:
        | 'dots'
        | 'ball'
        | 'bars'
        | 'cube'
        | 'gears'
        | 'hourglass'
        | 'infinity'
        | 'oval'
        | 'pie'
        | 'puff'
        | 'radio'
        | 'rings'
        | 'tail'
        | 'default';
    // 指示器颜色
    color?: string;
    // 指示器大小
    size?: string;
    // 加载文本
    message?: string;
    // 文本颜色
    textColor?: string;
    // 变体样式
    variant?: 'inline' | 'centered' | 'fullscreen';
    // 是否显示覆盖层
    overlay?: boolean;
}

withDefaults(defineProps<Props>(), {
    spinner: 'dots',
    color: 'primary',
    size: '2em',
    message: '',
    textColor: 'grey-6',
    variant: 'centered',
    overlay: false,
});
</script>

<style lang="scss" scoped>
.loading-state {
    position: relative;

    // 内联样式（不影响布局）
    &--inline {
        display: inline-flex;
        align-items: center;
        gap: 8px;

        .loading-content {
            display: flex;
            align-items: center;
            gap: 8px;
        }
    }

    // 居中样式（在容器内居中）
    &--centered {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100px;

        .loading-content {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 16px;
        }
    }

    // 全屏样式（覆盖整个视口）
    &--fullscreen {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(2px);

        .loading-content {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 16px;
            background: white;
            padding: 32px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
    }

    // 覆盖层样式
    &--overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 1000;

        .loading-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(1px);
        }

        .loading-content {
            position: relative;
            z-index: 1001;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            gap: 16px;
        }
    }
}

.loading-message {
    font-size: 14px;
    text-align: center;
    margin-top: 8px;
}

// 暗色主题适配
.body--dark {
    .loading-state {
        &--fullscreen {
            background: rgba(0, 0, 0, 0.8);

            .loading-content {
                background: $dark;
                color: white;
            }
        }

        &--overlay {
            .loading-overlay {
                background: rgba(0, 0, 0, 0.7);
            }
        }
    }
}

// 响应式适配
@media (max-width: 600px) {
    .loading-state--fullscreen .loading-content {
        padding: 24px;
        margin: 16px;
    }
}
</style>

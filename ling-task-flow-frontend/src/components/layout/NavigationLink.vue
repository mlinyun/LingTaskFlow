<template>
    <q-item
        v-ripple
        :class="{ 'q-item--active': isActive }"
        :to="link"
        class="navigation-link"
        clickable
        exact
    >
        <q-item-section avatar>
            <q-icon :color="color || 'grey-7'" :name="icon" size="sm" />
        </q-item-section>

        <q-item-section>
            <q-item-label class="text-weight-medium">{{ title }}</q-item-label>
            <q-item-label caption class="text-grey-6">{{ caption }}</q-item-label>
        </q-item-section>
    </q-item>
</template>

<script lang="ts" setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';

// 接口定义
export interface NavigationLinkProps {
    title: string;
    caption?: string;
    icon: string;
    link: string;
    color?: string;
}

// Props
const props = defineProps<NavigationLinkProps>();

// 路由
const route = useRoute();

// 计算当前路由是否激活
const isActive = computed(() => {
    return route.path === props.link || route.path.startsWith(props.link + '/');
});
</script>

<style lang="scss" scoped>
.navigation-link {
    border-radius: 12px;
    margin: 4px 8px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    background: rgba(255, 255, 255, 0.4);
    border: 1px solid rgba(59, 130, 246, 0.08);
    backdrop-filter: blur(10px);
    position: relative;
    overflow: hidden;

    &::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent 0%,
            rgba(59, 130, 246, 0.1) 50%,
            transparent 100%
        );
        transition: left 0.5s ease;
    }

    &:hover {
        background: rgba(255, 255, 255, 0.7);
        border-color: rgba(59, 130, 246, 0.15);
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);

        &::before {
            left: 100%;
        }

        .q-item__section--avatar .q-icon {
            transform: scale(1.1);
            filter: drop-shadow(0 2px 4px rgba(59, 130, 246, 0.3));
        }
    }
}

.q-item--active {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(14, 165, 233, 0.1) 100%);
    border-color: rgba(59, 130, 246, 0.25);
    color: #3b82f6;
    box-shadow:
        0 4px 12px rgba(59, 130, 246, 0.15),
        inset 0 1px 0 rgba(255, 255, 255, 0.3);

    &::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 3px;
        height: 100%;
        background: linear-gradient(180deg, #3b82f6 0%, #1d4ed8 100%);
        border-radius: 0 2px 2px 0;
    }

    .q-item__section--avatar .q-icon {
        color: #3b82f6 !important;
        transform: scale(1.1);
        filter: drop-shadow(0 2px 4px rgba(59, 130, 246, 0.4));
    }

    .q-item__label {
        font-weight: 700;
    }

    .q-item__label--caption {
        color: #64748b;
        opacity: 0.9;
    }
}

// 图标动画
.q-item__section--avatar .q-icon {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

// 文字样式优化
.q-item__label {
    font-weight: 600;
    font-size: 0.875rem;
    transition: all 0.3s ease;
}

.q-item__label--caption {
    font-size: 0.75rem;
    color: #64748b;
    opacity: 0.8;
    font-weight: 500;
    transition: all 0.3s ease;
}
</style>

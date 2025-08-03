<template>
    <q-item
        clickable
        v-ripple
        :to="link"
        exact
        class="navigation-link"
        :class="{ 'q-item--active': isActive }"
    >
        <q-item-section avatar>
            <q-icon :name="icon" :color="color || 'grey-7'" size="sm" />
        </q-item-section>

        <q-item-section>
            <q-item-label class="text-weight-medium">{{ title }}</q-item-label>
            <q-item-label caption class="text-grey-6">{{ caption }}</q-item-label>
        </q-item-section>
    </q-item>
</template>

<script setup lang="ts">
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

<style scoped>
.navigation-link {
    border-radius: 8px;
    margin: 4px 8px;
    transition: all 0.2s ease;
}

.navigation-link:hover {
    background-color: rgba(25, 118, 210, 0.08);
}

.q-item--active {
    background-color: rgba(25, 118, 210, 0.12);
    color: var(--q-primary);
}

.q-item--active .q-item__section--avatar .q-icon {
    color: var(--q-primary) !important;
}
</style>

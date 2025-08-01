<template>
    <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useAuthStore } from 'stores/auth';

const authStore = useAuthStore();

// 应用启动时初始化认证状态
onMounted(() => {
    authStore.initAuth();
});
</script>

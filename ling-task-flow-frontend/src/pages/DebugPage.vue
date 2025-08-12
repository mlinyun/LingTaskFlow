/* eslint-disable @typescript-eslint/await-thenable */
<template>
    <q-page padding>
        <h1>调试页面</h1>
        <div>
            <h2>认证状态:</h2>
            <p>IsAuthenticated: {{ authStore.isAuthenticated }}</p>
            <p>User: {{ authStore.user }}</p>
            <p>Token exists: {{ !!tokenExists }}</p>

            <h2>本地存储:</h2>
            <p>Access Token: {{ accessToken }}</p>
            <p>User Info: {{ userInfo }}</p>

            <h2>操作:</h2>
            <q-btn color="warning" @click="clearStorage">清除本地存储</q-btn>
            <q-btn class="q-ml-sm" color="primary" @click="refreshPage">刷新页面</q-btn>
        </div>
    </q-page>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue';
import { useAuthStore } from 'stores/auth';
import { LocalStorage } from 'quasar';

const authStore = useAuthStore();
const tokenExists = ref(false);
const accessToken = ref('');
const userInfo = ref('');

onMounted(() => {
    accessToken.value = LocalStorage.getItem('access_token') || 'null';
    userInfo.value = JSON.stringify(LocalStorage.getItem('user_info')) || 'null';
    tokenExists.value = !!LocalStorage.getItem('access_token');
});

const clearStorage = () => {
    LocalStorage.clear();
    location.reload();
};

const refreshPage = () => {
    location.reload();
};
</script>

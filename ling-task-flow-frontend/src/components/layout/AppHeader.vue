<template>
    <q-header elevated class="bg-primary text-white">
        <q-toolbar>
            <q-btn flat dense round icon="menu" aria-label="Menu" @click="handleMenuToggle" />

            <q-toolbar-title class="text-weight-bold">
                <q-icon name="task" size="sm" class="q-mr-sm" />
                LingTaskFlow
            </q-toolbar-title>

            <!-- 用户信息和操作按钮 -->
            <div class="q-gutter-sm row items-center">
                <q-chip
                    v-if="authStore.user"
                    :label="authStore.userDisplayName"
                    icon="person"
                    color="white"
                    text-color="primary"
                    class="q-pa-sm"
                />

                <q-btn-dropdown flat round dense icon="account_circle" class="q-ml-sm">
                    <q-list>
                        <q-item clickable v-close-popup @click="handleProfile">
                            <q-item-section avatar>
                                <q-icon name="person" />
                            </q-item-section>
                            <q-item-section>个人资料</q-item-section>
                        </q-item>

                        <q-item clickable v-close-popup @click="handleSettings">
                            <q-item-section avatar>
                                <q-icon name="settings" />
                            </q-item-section>
                            <q-item-section>设置</q-item-section>
                        </q-item>

                        <q-separator />

                        <q-item clickable v-close-popup @click="handleLogout">
                            <q-item-section avatar>
                                <q-icon name="logout" />
                            </q-item-section>
                            <q-item-section>退出登录</q-item-section>
                        </q-item>
                    </q-list>
                </q-btn-dropdown>
            </div>
        </q-toolbar>
    </q-header>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { useAuthStore } from 'stores/auth';

// 定义组件事件
const emit = defineEmits<{
    toggleDrawer: []
}>();

// 依赖注入
const router = useRouter();
const $q = useQuasar();
const authStore = useAuthStore();

// 方法
const handleMenuToggle = () => {
    emit('toggleDrawer');
};

const handleProfile = () => {
    $q.notify('个人资料功能开发中...');
};

const handleSettings = () => {
    $q.notify('设置功能开发中...');
};

const handleLogout = () => {
    $q.dialog({
        title: '确认退出',
        message: '您确定要退出登录吗？',
        cancel: true,
        persistent: true,
    }).onOk(() => {
        void authStore.logout().then(() => {
            $q.notify({
                type: 'positive',
                message: '已成功退出登录',
                position: 'top',
            });
            void router.push('/login');
        });
    });
};
</script>

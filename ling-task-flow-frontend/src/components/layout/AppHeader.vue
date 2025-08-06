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
                    v-if="authStore?.user"
                    :label="authStore?.userDisplayName"
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
import { useGlobalConfirm } from '../../composables/useGlobalConfirm';

// 定义组件事件
const emit = defineEmits<{
    toggleDrawer: [];
}>();

// 依赖注入
const router = useRouter();
const $q = useQuasar();
const authStore = useAuthStore();
const confirmDialog = useGlobalConfirm();

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

const handleLogout = async () => {
    try {
        // 尝试使用确认对话框，如果失败则直接执行登出
        let confirmed = false;

        try {
            confirmed = await confirmDialog.confirmInfo(
                '退出登录',
                '您确定要退出登录吗？',
                {
                    details: '退出后需要重新登录才能使用系统。',
                    confirmText: '退出登录',
                    confirmIcon: 'logout'
                }
            );
        } catch (dialogError) {
            // 如果确认对话框不可用，直接确认
            console.warn('确认对话框不可用，直接执行登出:', dialogError);
            confirmed = confirm('您确定要退出登录吗？');
        }

        if (confirmed) {
            try {
                confirmDialog.setLoading(true, '正在退出登录...');
            } catch {
                // 忽略设置加载状态的错误
            }

            try {
                await authStore.logout();
                $q.notify({
                    type: 'positive',
                    message: '已成功退出登录',
                    position: 'top',
                });
                void router.push('/login');
            } catch (error) {
                console.error('退出登录失败:', error);
                $q.notify({
                    type: 'negative',
                    message: '退出登录失败',
                    position: 'top',
                });
            } finally {
                try {
                    confirmDialog.setLoading(false);
                } catch {
                    // 忽略设置加载状态的错误
                }
            }
        }
    } catch (error) {
        console.error('退出登录失败:', error);
    }
};
</script>

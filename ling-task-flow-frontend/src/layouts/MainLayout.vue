<template>
    <q-layout view="lHh Lpr lFf">
        <q-header elevated class="bg-primary text-white">
            <q-toolbar>
                <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />

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

        <q-drawer v-model="leftDrawerOpen" show-if-above bordered class="bg-grey-1" :width="280">
            <q-list padding>
                <!-- 任务统计概览 -->
                <q-item-label header class="text-weight-bold text-primary"> 任务概览 </q-item-label>

                <q-item v-if="authStore.user?.profile" class="q-mb-md">
                    <q-item-section>
                        <div class="row q-gutter-sm">
                            <q-card flat bordered class="col">
                                <q-card-section class="text-center q-pa-sm">
                                    <div class="text-h6 text-primary">
                                        {{ authStore.user.profile.task_count }}
                                    </div>
                                    <div class="text-caption">总任务</div>
                                </q-card-section>
                            </q-card>
                            <q-card flat bordered class="col">
                                <q-card-section class="text-center q-pa-sm">
                                    <div class="text-h6 text-positive">
                                        {{ authStore.user.profile.completed_task_count }}
                                    </div>
                                    <div class="text-caption">已完成</div>
                                </q-card-section>
                            </q-card>
                        </div>
                        <q-linear-progress
                            :value="authStore.completionRate / 100"
                            color="positive"
                            class="q-mt-sm"
                            size="8px"
                            rounded
                        />
                        <div class="text-center text-caption q-mt-xs">
                            完成率 {{ authStore.completionRate }}%
                        </div>
                    </q-item-section>
                </q-item>

                <q-separator class="q-mb-md" />

                <!-- 导航菜单 -->
                <q-item-label header class="text-weight-bold text-primary"> 导航菜单 </q-item-label>

                <navigation-link v-for="link in navigationLinks" :key="link.title" v-bind="link" />
            </q-list>
        </q-drawer>

        <q-page-container>
            <router-view />
        </q-page-container>
    </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { useAuthStore } from 'stores/auth';
import NavigationLink from 'components/NavigationLink.vue';

// 响应式数据
const leftDrawerOpen = ref(false);

// 依赖注入
const router = useRouter();
const $q = useQuasar();
const authStore = useAuthStore();

// 导航链接配置
const navigationLinks = [
    {
        title: '平台首页',
        caption: '欢迎页面和功能概览',
        icon: 'home',
        link: '/',
        color: 'primary',
    },
    {
        title: '任务列表',
        caption: '查看和管理您的任务',
        icon: 'list',
        link: '/tasks',
        color: 'secondary',
    },
    {
        title: '数据概览',
        caption: '任务统计和分析',
        icon: 'dashboard',
        link: '/dashboard',
        color: 'info',
    },
    {
        title: '回收站',
        caption: '已删除的任务',
        icon: 'delete',
        link: '/trash',
        color: 'warning',
    },
];

// 方法
const toggleLeftDrawer = () => {
    leftDrawerOpen.value = !leftDrawerOpen.value;
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

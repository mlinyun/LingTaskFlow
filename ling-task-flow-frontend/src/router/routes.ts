import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
    // 认证页面（无需布局）
    {
        path: '/login',
        name: 'Login',
        component: () => import('pages/LoginPage.vue'),
        meta: { requiresAuth: false },
    },
    {
        path: '/register',
        name: 'Register',
        component: () => import('pages/RegisterPage.vue'),
        meta: { requiresAuth: false },
    },

    // 主应用布局（需要认证）
    {
        path: '/',
        component: () => import('layouts/MainLayout.vue'),
        meta: { requiresAuth: true },
        children: [
            // 首页 - 平台首页
            {
                path: '',
                name: 'Home',
                component: () => import('pages/IndexPage.vue'),
            },
            // 任务管理
            {
                path: 'tasks',
                name: 'TaskList',
                component: () => import('pages/TaskListPage.vue'),
            },
            // 数据概览/仪表板
            {
                path: 'dashboard',
                name: 'Dashboard',
                component: () => import('pages/DashboardPage.vue'),
            },
            // 高级数据分析
            {
                path: 'advanced-analytics',
                name: 'AdvancedAnalytics',
                component: () => import('pages/AdvancedDashboardPage.vue'),
            },
            // 回收站
            {
                path: 'trash',
                name: 'TrashPage',
                component: () => import('pages/TrashPage.vue'),
            },
        ],
    },

    // 404页面
    {
        path: '/:catchAll(.*)*',
        component: () => import('pages/ErrorNotFound.vue'),
    },
];

export default routes;

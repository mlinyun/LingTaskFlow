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
        component: () => import('pages/LoginPage.vue'),
        meta: { requiresAuth: false },
    },

    // 主应用页面（需要认证和布局）
    {
        path: '/',
        component: () => import('layouts/MainLayout.vue'),
        meta: { requiresAuth: true },
        children: [
            {
                path: '',
                redirect: '/tasks',
            },
            {
                path: 'tasks',
                name: 'TaskList',
                component: () => import('pages/TaskListPage.vue'),
            },
            {
                path: 'dashboard',
                name: 'Dashboard',
                component: () => import('pages/DashboardPage.vue'),
            },
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

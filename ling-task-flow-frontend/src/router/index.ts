import { defineRouter } from '#q-app/wrappers';
import {
    createMemoryHistory,
    createRouter,
    createWebHashHistory,
    createWebHistory,
} from 'vue-router';
import { LocalStorage } from 'quasar';
import routes from './routes';

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default defineRouter(function (/* { store, ssrContext } */) {
    const createHistory = process.env.SERVER
        ? createMemoryHistory
        : process.env.VUE_ROUTER_MODE === 'history'
          ? createWebHistory
          : createWebHashHistory;

    const Router = createRouter({
        scrollBehavior: () => ({ left: 0, top: 0 }),
        routes,

        // Leave this as is and make changes in quasar.conf.js instead!
        // quasar.conf.js -> build -> vueRouterMode
        // quasar.conf.js -> build -> publicPath
        history: createHistory(process.env.VUE_ROUTER_BASE),
    });

    // 路由守卫 - 认证检查
    Router.beforeEach((to, from, next) => {
        const token = LocalStorage.getItem('access_token');
        const isAuthenticated = !!token;

        // 页面需要认证但用户未登录
        if (to.meta.requiresAuth && !isAuthenticated) {
            next('/login');
            return;
        }

        // 用户已登录但访问登录/注册页面，重定向到任务列表
        if ((to.path === '/login' || to.path === '/register') && isAuthenticated) {
            next('/tasks');
            return;
        }

        next();
    });

    return Router;
});

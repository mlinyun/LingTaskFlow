import { defineBoot } from '#q-app/wrappers';
import { useAuthStore } from 'src/stores/auth';
import { lazyLoad } from 'src/directives/lazyLoad';
import { cachedApi } from '../utils/cachedApi';

export default defineBoot(({ app }) => {
    // 在应用启动时初始化认证状态
    const authStore = useAuthStore();
    authStore.initAuth();

    // 注册全局指令
    app.directive('lazy-load', lazyLoad);

    // 设置全局缓存API客户端
    app.config.globalProperties.$cachedApi = cachedApi;
});

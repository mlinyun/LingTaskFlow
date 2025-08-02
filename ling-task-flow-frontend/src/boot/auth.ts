import { defineBoot } from '#q-app/wrappers';
import { useAuthStore } from 'src/stores/auth';

export default defineBoot(() => {
    // 在应用启动时初始化认证状态
    const authStore = useAuthStore();
    authStore.initAuth();
});

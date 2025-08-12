import { defineStore } from 'pinia';
import { LocalStorage } from 'quasar';
import { computed, ref } from 'vue';
import { apiPost } from 'src/utils/api';
import type { AuthData, User } from 'src/types';

export const useAuthStore = defineStore('auth', () => {
    // 状态
    const user = ref<User | null>(null);
    const isAuthenticated = ref(false);
    const loading = ref(false);

    // 计算属性
    const userDisplayName = computed(() => {
        return user.value?.username || user.value?.email || '用户';
    });

    const completionRate = computed(() => {
        if (!user.value?.profile) return 0;
        const { task_count, completed_task_count } = user.value.profile;
        return task_count > 0 ? Math.round((completed_task_count / task_count) * 100) : 0;
    });

    // 初始化认证状态
    const initAuth = () => {
        const token = LocalStorage.getItem('access_token');
        const userInfo = LocalStorage.getItem('user_info');

        if (token && userInfo) {
            user.value = userInfo as User;
            isAuthenticated.value = true;
        }
    };

    // 保存认证信息
    const saveAuthData = (authData: AuthData) => {
        user.value = authData.user;
        isAuthenticated.value = true;

        LocalStorage.set('access_token', authData.tokens.access);
        LocalStorage.set('refresh_token', authData.tokens.refresh);
        LocalStorage.set('user_info', authData.user);
    };

    // 用户登录
    const login = async (credentials: { username: string; password: string }) => {
        loading.value = true;
        try {
            // 使用我们的API工具函数，但不自动显示成功提示
            const authData = await apiPost<AuthData>('/auth/login/', credentials, true, false);

            saveAuthData(authData);
            return { success: true, message: '登录成功，欢迎回来！' };
        } catch (error: unknown) {
            console.error('Login error:', error);
            let errorMessage = '登录失败，请检查输入信息';

            if (error instanceof Error) {
                errorMessage = error.message;
            }

            return {
                success: false,
                message: errorMessage,
            };
        } finally {
            loading.value = false;
        }
    };

    // 用户注册
    const register = async (userData: {
        username: string;
        email: string;
        password: string;
        password_confirm: string;
    }) => {
        loading.value = true;
        try {
            // 注册用户，但不自动登录
            await apiPost('/auth/register/', userData, true, false);

            // 注册成功，返回成功信息，但不保存认证数据
            return { success: true, message: '注册成功' };
        } catch (error: unknown) {
            console.error('Register error:', error);
            let errorMessage = '注册失败，请检查输入信息';

            if (error instanceof Error) {
                errorMessage = error.message;
            }

            return {
                success: false,
                message: errorMessage,
            };
        } finally {
            loading.value = false;
        }
    };

    // 用户登出
    const logout = async () => {
        try {
            // 调用后端登出API（如果有）
            await apiPost('/auth/logout/', undefined, false).catch(() => {
                // 忽略登出API错误，继续清理本地状态
            });
        } finally {
            // 清理本地状态
            user.value = null;
            isAuthenticated.value = false;

            LocalStorage.remove('access_token');
            LocalStorage.remove('refresh_token');
            LocalStorage.remove('user_info');
        }
    };

    // 更新用户信息
    const updateUser = (newUserData: Partial<User>) => {
        if (user.value) {
            user.value = { ...user.value, ...newUserData };
            LocalStorage.set('user_info', user.value);
        }
    };

    // Token刷新
    const refreshToken = async () => {
        const refreshTokenValue = LocalStorage.getItem('refresh_token');
        if (!refreshTokenValue) {
            throw new Error('No refresh token available');
        }

        try {
            const response = await apiPost<{ access: string }>(
                '/auth/token/refresh/',
                {
                    refresh: refreshTokenValue,
                },
                false,
            );

            if (response.access) {
                LocalStorage.set('access_token', response.access);
                return response.access;
            }
            throw new Error('Invalid refresh response');
        } catch (error) {
            // Token刷新失败，清理认证状态
            await logout();
            throw error;
        }
    };

    return {
        // 状态
        user,
        isAuthenticated,
        loading,

        // 计算属性
        userDisplayName,
        completionRate,

        // 方法
        initAuth,
        login,
        register,
        logout,
        updateUser,
        refreshToken,
    };
});

import { defineBoot } from '#q-app/wrappers';
import axios, { type AxiosInstance, type AxiosResponse } from 'axios';
import { LocalStorage } from 'quasar';
import type { StandardAPIResponse, CustomError } from 'src/types';

// 扩展AxiosResponse类型
interface ExtendedAxiosResponse<T = unknown> extends AxiosResponse<T> {
    meta?: Record<string, unknown>;
    message?: string;
}

declare module 'vue' {
    interface ComponentCustomProperties {
        $axios: AxiosInstance;
        $api: AxiosInstance;
    }
}

// LingTaskFlow API 基础配置
const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/api',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// 请求拦截器 - 添加认证Token
api.interceptors.request.use(
    config => {
        const token = LocalStorage.getItem('access_token');
        if (token && typeof token === 'string') {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    error => {
        return Promise.reject(error instanceof Error ? error : new Error(String(error)));
    },
);

// 响应拦截器 - 处理标准化API响应格式
api.interceptors.response.use(
    response => {
        // 检查后端返回的标准化响应格式
        const { data } = response;

        // 如果是标准化格式，检查success字段
        if (data && typeof data === 'object' && 'success' in data) {
            const standardData = data as StandardAPIResponse;
            if (standardData.success === false) {
                // 后端业务逻辑错误，但HTTP状态码可能是200
                const error = new Error(standardData.message || '操作失败') as CustomError;
                error.name = 'BusinessError';
                // 将完整的错误信息附加到error对象上
                error.errorData = standardData.error?.details || {};
                error.timestamp = standardData.timestamp;
                return Promise.reject(error);
            }
            // 成功响应，返回data字段中的实际数据
            response.data = standardData.data;
            // 保留元数据信息
            const extendedResponse = response as ExtendedAxiosResponse;
            extendedResponse.meta = standardData.meta;
            extendedResponse.message = standardData.message;
        }

        return response;
    },
    async error => {
        // HTTP错误处理
        if (error.response?.status === 401) {
            // Token过期，尝试刷新Token
            const refreshToken = LocalStorage.getItem('refresh_token');

            if (refreshToken && typeof refreshToken === 'string') {
                try {
                    // 尝试刷新Token
                    const refreshResponse = await axios.post(
                        'http://127.0.0.1:8000/api/auth/token/refresh/',
                        {
                            refresh: refreshToken,
                        },
                    );

                    // 检查刷新响应的格式
                    const refreshData = refreshResponse.data;
                    let newAccessToken = null;

                    if (
                        refreshData &&
                        typeof refreshData === 'object' &&
                        'success' in refreshData
                    ) {
                        // 标准化响应格式
                        const standardRefreshData = refreshData as StandardAPIResponse<{
                            access: string;
                        }>;
                        if (standardRefreshData.success && standardRefreshData.data) {
                            newAccessToken = standardRefreshData.data.access;
                        }
                    } else {
                        // 旧格式响应（兼容性处理）
                        newAccessToken = (refreshData as { access: string }).access;
                    }

                    if (newAccessToken) {
                        // 保存新Token
                        LocalStorage.set('access_token', newAccessToken);

                        // 重试原始请求
                        if (error.config) {
                            error.config.headers.Authorization = `Bearer ${newAccessToken}`;
                            return api.request(error.config);
                        }
                    }
                } catch (refreshError) {
                    console.error('Token刷新失败:', refreshError);
                }
            }

            // Token刷新失败或没有refresh token，清除本地存储并跳转登录
            LocalStorage.remove('access_token');
            LocalStorage.remove('refresh_token');
            LocalStorage.remove('user_info');

            // 如果不在登录页面，则跳转到登录页面
            if (window.location.pathname !== '/login') {
                window.location.href = '/login';
            }
        }

        // 处理其他HTTP错误
        let errorMessage = '网络错误，请稍后重试';
        let errorData = null;

        if (error.response?.data) {
            const responseData = error.response.data;

            // 检查是否为标准化错误响应
            if (responseData && typeof responseData === 'object' && 'success' in responseData) {
                const standardErrorData = responseData as StandardAPIResponse;
                errorMessage = standardErrorData.message || errorMessage;
                errorData = standardErrorData.error?.details || {};
            } else if (typeof responseData === 'string') {
                errorMessage = responseData;
            }
        }

        const customError = new Error(errorMessage) as CustomError;
        customError.name = 'APIError';
        customError.status = error.response?.status;
        customError.errorData = errorData || {};

        return Promise.reject(customError);
    },
);

export default defineBoot(({ app }) => {
    // for use inside Vue files (Options API) through this.$axios and this.$api
    app.config.globalProperties.$axios = axios;
    app.config.globalProperties.$api = api;
});

export { api };

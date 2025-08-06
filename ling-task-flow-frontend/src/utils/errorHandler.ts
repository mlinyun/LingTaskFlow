/**
 * API错误处理工具
 * 统一处理API请求错误，提供友好的错误提示
 */

import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';

export interface ApiError {
    status: number;
    code?: string;
    message: string;
    details?: Record<string, unknown> | string | null;
    timestamp: string;
}

export interface ApiErrorConfig {
    showNotification?: boolean;
    showDialog?: boolean;
    autoRetry?: boolean;
    maxRetries?: number;
    retryDelay?: number;
}

export class ApiErrorHandler {
    private $q: ReturnType<typeof useQuasar> | null = null;
    private router: ReturnType<typeof useRouter> | null = null;
    private retryCount = new Map<string, number>();

    constructor() {
        // 注意：在组合式API中使用时需要在setup()内部初始化
    }

    init() {
        this.$q = useQuasar();
        this.router = useRouter();
    }

    /**
     * 处理API错误响应
     */
    handleApiError(
        error: Error & { response?: { status: number; data?: Record<string, unknown> } },
        config: ApiErrorConfig = {},
    ): ApiError {
        const {
            showNotification = true,
            showDialog = false,
            autoRetry = false,
            maxRetries = 3,
            retryDelay = 1000,
        } = config;

        // 构建标准化错误对象
        const apiError: ApiError = this.normalizeError(error);

        // 记录错误
        this.logError(apiError, error);

        // 根据错误类型处理
        this.handleErrorByType(apiError, {
            showNotification,
            showDialog,
            autoRetry,
            maxRetries,
            retryDelay,
        });

        return apiError;
    }

    /**
     * 标准化错误对象
     */
    private normalizeError(
        error: Error & { response?: { status: number; data?: Record<string, unknown> } },
    ): ApiError {
        const timestamp = new Date().toISOString();

        // 网络错误
        if (!error.response) {
            return {
                status: 0,
                code: 'NETWORK_ERROR',
                message: '网络连接失败，请检查网络设置',
                details: error.message,
                timestamp,
            };
        }

        // HTTP错误响应
        const { status, data } = error.response;

        return {
            status,
            code: (data?.code as string) || this.getDefaultErrorCode(status),
            message: (data?.message as string) || this.getDefaultErrorMessage(status),
            details: (data?.details as Record<string, unknown>) || data || null,
            timestamp,
        };
    }

    /**
     * 根据错误类型处理
     */
    private handleErrorByType(apiError: ApiError, config: ApiErrorConfig) {
        switch (apiError.status) {
            case 0: // 网络错误
                this.handleNetworkError(apiError, config);
                break;
            case 400: // 请求错误
                this.handleBadRequestError(apiError, config);
                break;
            case 401: // 未授权
                this.handleUnauthorizedError(apiError, config);
                break;
            case 403: // 禁止访问
                this.handleForbiddenError(apiError, config);
                break;
            case 404: // 资源不存在
                this.handleNotFoundError(apiError, config);
                break;
            case 422: // 验证错误
                this.handleValidationError(apiError, config);
                break;
            case 429: // 请求过多
                this.handleRateLimitError(apiError, config);
                break;
            case 500: // 服务器错误
                this.handleServerError(apiError, config);
                break;
            case 502:
            case 503:
            case 504: // 服务不可用
                this.handleServiceUnavailableError(apiError, config);
                break;
            default:
                this.handleGenericError(apiError, config);
        }
    }

    /**
     * 网络错误处理
     */
    private handleNetworkError(apiError: ApiError, config: ApiErrorConfig) {
        if (config.showNotification && this.$q) {
            this.$q.notify({
                type: 'negative',
                message: apiError.message,
                icon: 'wifi_off',
                position: 'top',
                timeout: 0,
                actions: [
                    {
                        label: '重试',
                        color: 'white',
                        handler: () => window.location.reload(),
                    },
                    {
                        label: '关闭',
                        color: 'white',
                        handler: () => {},
                    },
                ],
            });
        }
    }

    /**
     * 未授权错误处理
     */
    private handleUnauthorizedError(apiError: ApiError, config: ApiErrorConfig) {
        if (config.showNotification && this.$q) {
            this.$q.notify({
                type: 'negative',
                message: '登录已过期，请重新登录',
                icon: 'login',
                position: 'center',
                timeout: 3000,
            });
        }

        // 清除本地存储的认证信息
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');

        // 跳转到登录页
        if (this.router) {
            void this.router.push('/login');
        }
    }

    /**
     * 权限不足错误处理
     */
    private handleForbiddenError(apiError: ApiError, config: ApiErrorConfig) {
        if (config.showDialog && this.$q) {
            this.$q.dialog({
                title: '权限不足',
                message: apiError.message || '您没有执行此操作的权限',
                ok: '了解',
                persistent: true,
            });
        } else if (config.showNotification && this.$q) {
            this.$q.notify({
                type: 'negative',
                message: apiError.message || '权限不足',
                icon: 'lock',
                position: 'top',
                timeout: 4000,
            });
        }
    }

    /**
     * 验证错误处理
     */
    private handleValidationError(apiError: ApiError, config: ApiErrorConfig) {
        if (config.showNotification && this.$q) {
            // 如果有详细的验证错误信息
            if (apiError.details && typeof apiError.details === 'object') {
                const errors = Object.values(apiError.details).flat();
                errors.forEach((error: unknown) => {
                    if (this.$q && typeof error === 'string') {
                        this.$q.notify({
                            type: 'warning',
                            message: error,
                            icon: 'warning',
                            position: 'top',
                            timeout: 4000,
                        });
                    }
                });
            } else if (this.$q) {
                this.$q.notify({
                    type: 'warning',
                    message: apiError.message,
                    icon: 'warning',
                    position: 'top',
                    timeout: 4000,
                });
            }
        }
    }

    /**
     * 服务器错误处理
     */
    private handleServerError(apiError: ApiError, config: ApiErrorConfig) {
        if (config.showNotification && this.$q) {
            this.$q.notify({
                type: 'negative',
                message: '服务器出现错误，请稍后重试',
                icon: 'cloud_off',
                position: 'top',
                timeout: 5000,
                actions: [
                    {
                        label: '重试',
                        color: 'white',
                        handler: () => window.location.reload(),
                    },
                ],
            });
        }
    }

    /**
     * 服务不可用错误处理
     */
    private handleServiceUnavailableError(apiError: ApiError, config: ApiErrorConfig) {
        if (config.showNotification && this.$q) {
            this.$q.notify({
                type: 'negative',
                message: '服务暂时不可用，请稍后重试',
                icon: 'cloud_off',
                position: 'top',
                timeout: 8000,
                actions: [
                    {
                        label: '重试',
                        color: 'white',
                        handler: () => window.location.reload(),
                    },
                ],
            });
        }
    }

    /**
     * 通用错误处理
     */
    private handleGenericError(apiError: ApiError, config: ApiErrorConfig) {
        if (config.showNotification && this.$q) {
            this.$q.notify({
                type: 'negative',
                message: apiError.message || '操作失败，请重试',
                icon: 'error',
                position: 'top',
                timeout: 4000,
            });
        }
    }

    /**
     * 其他错误类型的处理方法
     */
    private handleBadRequestError(apiError: ApiError, config: ApiErrorConfig) {
        if (config.showNotification && this.$q) {
            this.$q.notify({
                type: 'warning',
                message: apiError.message || '请求参数错误',
                icon: 'warning',
                position: 'top',
                timeout: 4000,
            });
        }
    }

    private handleNotFoundError(apiError: ApiError, config: ApiErrorConfig) {
        if (config.showNotification && this.$q) {
            this.$q.notify({
                type: 'warning',
                message: '请求的资源不存在',
                icon: 'search_off',
                position: 'top',
                timeout: 4000,
            });
        }
    }

    private handleRateLimitError(apiError: ApiError, config: ApiErrorConfig) {
        if (config.showNotification && this.$q) {
            this.$q.notify({
                type: 'warning',
                message: '请求过于频繁，请稍后重试',
                icon: 'hourglass_empty',
                position: 'top',
                timeout: 5000,
            });
        }
    }

    /**
     * 获取默认错误代码
     */
    private getDefaultErrorCode(status: number): string {
        const codes: Record<number, string> = {
            400: 'BAD_REQUEST',
            401: 'UNAUTHORIZED',
            403: 'FORBIDDEN',
            404: 'NOT_FOUND',
            422: 'VALIDATION_ERROR',
            429: 'RATE_LIMIT',
            500: 'SERVER_ERROR',
            502: 'BAD_GATEWAY',
            503: 'SERVICE_UNAVAILABLE',
            504: 'GATEWAY_TIMEOUT',
        };
        return codes[status] || 'UNKNOWN_ERROR';
    }

    /**
     * 获取默认错误消息
     */
    private getDefaultErrorMessage(status: number): string {
        const messages: Record<number, string> = {
            400: '请求参数错误',
            401: '未登录或登录已过期',
            403: '权限不足',
            404: '请求的资源不存在',
            422: '数据验证失败',
            429: '请求过于频繁',
            500: '服务器内部错误',
            502: '网关错误',
            503: '服务暂时不可用',
            504: '网关超时',
        };
        return messages[status] || '未知错误';
    }

    /**
     * 记录错误
     */
    private logError(apiError: ApiError, originalError: Error) {
        console.error('API Error:', {
            apiError,
            originalError,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            userAgent: navigator.userAgent,
        });

        // 在生产环境中，这里可以发送错误到监控服务
        if (process.env.NODE_ENV === 'production') {
            // 发送到错误监控服务
            this.sendToErrorService(apiError, originalError);
        }
    }

    /**
     * 发送错误到监控服务
     */
    private sendToErrorService(apiError: ApiError, originalError: Error) {
        // 示例：发送到Sentry或其他错误监控服务
        console.log('Sending error to monitoring service:', { apiError, originalError });
    }
}

// 创建全局实例
export const apiErrorHandler = new ApiErrorHandler();

// 便捷方法
export function handleApiError(
    error: Error & { response?: { status: number; data?: Record<string, unknown> } },
    config?: ApiErrorConfig,
): ApiError {
    return apiErrorHandler.handleApiError(error, config);
}

/**
 * API请求拦截器
 * 为axios添加错误处理、重试机制等功能
 */

import axios, { type AxiosError, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios'
import { apiErrorHandler } from './errorHandler'

// 请求重试配置
interface RetryConfig {
    retries: number
    delay: number
    retryCondition?: (error: AxiosError) => boolean
}

// 定义通用配置类型
type RequestConfig = Record<string, unknown>

// 扩展的axios配置类型，带有重试和错误处理标记
interface ExtendedAxiosRequestConfig extends InternalAxiosRequestConfig {
    retry?: RetryConfig
    skipErrorHandling?: boolean
    __retryCount?: number
}

// 扩展axios配置类型
declare module 'axios' {
    interface AxiosRequestConfig {
        retry?: RetryConfig
        skipErrorHandling?: boolean
    }
}

/**
 * 创建axios实例
 */
const apiClient = axios.create({
    baseURL: process.env.NODE_ENV === 'development'
        ? 'http://localhost:8000/api'
        : '/api',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    }
})

/**
 * 请求拦截器
 */
apiClient.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        // 添加认证token
        const token = localStorage.getItem('access_token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }

        // 添加请求ID用于追踪
        config.headers['X-Request-ID'] = generateRequestId()

        // 记录请求日志
        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`, {
            params: config.params,
            data: config.data
        })

        return config
    },
    (error: AxiosError) => {
        console.error('❌ Request Error:', error)
        return Promise.reject(error)
    }
)

/**
 * 响应拦截器
 */
apiClient.interceptors.response.use(
    (response: AxiosResponse) => {
        // 记录成功响应
        console.log(`✅ API Response: ${response.status} ${response.config.url}`, {
            data: response.data
        })

        return response
    },
    async (error: AxiosError) => {
        const config = error.config as InternalAxiosRequestConfig & { retry?: RetryConfig }

        // 记录错误响应
        console.error(`❌ API Error: ${error.response?.status || 'Network'} ${config?.url}`, {
            error: error.response?.data,
            message: error.message
        })

        // 处理token过期
        if (error.response?.status === 401) {
            await handleTokenExpired()
        }

        // 重试逻辑
        if (shouldRetry(error, config)) {
            return retryRequest(config)
        }

        // 如果不跳过错误处理，则使用全局错误处理器
        if (!config?.skipErrorHandling) {
            // 转换AxiosError为错误处理器期望的类型
            const adaptedError = {
                ...error,
                response: error.response ? {
                    status: error.response.status,
                    data: error.response.data as Record<string, unknown> | undefined
                } : undefined
            } as Error & { response?: { status: number; data?: Record<string, unknown> } }

            apiErrorHandler.handleApiError(adaptedError, {
                showNotification: true,
                autoRetry: false
            })
        }

        return Promise.reject(error)
    }
)

/**
 * 生成请求ID
 */
function generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

/**
 * 处理token过期
 */
async function handleTokenExpired(): Promise<void> {
    const refreshToken = localStorage.getItem('refresh_token')

    if (!refreshToken) {
        // 清除认证信息并跳转到登录页
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return
    }

    try {
        // 尝试刷新token
        const response = await axios.post('/api/auth/refresh/', {
            refresh: refreshToken
        })

        const { access } = response.data
        localStorage.setItem('access_token', access)

        console.log('🔄 Token refreshed successfully')
    } catch (refreshError) {
        console.error('❌ Token refresh failed:', refreshError)

        // 刷新失败，清除认证信息
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
    }
}

/**
 * 判断是否应该重试
 */
function shouldRetry(
    error: AxiosError,
    config?: ExtendedAxiosRequestConfig
): boolean {
    if (!config?.retry) return false

    // 已经达到最大重试次数
    const currentRetries = config.__retryCount || 0
    if (currentRetries >= config.retry.retries) return false

    // 检查重试条件
    if (config.retry.retryCondition) {
        return config.retry.retryCondition(error)
    }

    // 默认重试条件：网络错误或5xx错误
    return !error.response || (error.response.status >= 500 && error.response.status <= 599)
}

/**
 * 重试请求
 */
async function retryRequest(
    config: ExtendedAxiosRequestConfig
): Promise<AxiosResponse> {
    const currentRetries = (config.__retryCount || 0) + 1
    config.__retryCount = currentRetries

    console.log(`🔄 Retrying request (${currentRetries}/${config.retry?.retries}): ${config.url}`)

    // 等待延迟
    if (config.retry?.delay) {
        await new Promise(resolve => setTimeout(resolve, config.retry!.delay * currentRetries))
    }

    return apiClient(config)
}

/**
 * 请求工厂函数
 */
export const api = {
    // GET请求
    get: <T = unknown>(url: string, config?: RequestConfig) =>
        apiClient.get<T>(url, config).then(response => response.data),

    // POST请求
    post: <T = unknown>(url: string, data?: unknown, config?: RequestConfig) =>
        apiClient.post<T>(url, data, config).then(response => response.data),

    // PUT请求
    put: <T = unknown>(url: string, data?: unknown, config?: RequestConfig) =>
        apiClient.put<T>(url, data, config).then(response => response.data),

    // PATCH请求
    patch: <T = unknown>(url: string, data?: unknown, config?: RequestConfig) =>
        apiClient.patch<T>(url, data, config).then(response => response.data),

    // DELETE请求
    delete: <T = unknown>(url: string, config?: RequestConfig) =>
        apiClient.delete<T>(url, config).then(response => response.data),

    // 带重试的请求
    withRetry: <T = unknown>(
        method: 'get' | 'post' | 'put' | 'patch' | 'delete',
        url: string,
        dataOrConfig?: unknown,
        config?: RequestConfig,
        retryConfig: RetryConfig = { retries: 3, delay: 1000 }
    ) => {
        const requestConfig = method === 'get' || method === 'delete'
            ? { ...dataOrConfig as RequestConfig, retry: retryConfig }
            : { ...config, retry: retryConfig }

        switch (method) {
            case 'get':
                return api.get<T>(url, requestConfig)
            case 'post':
                return api.post<T>(url, dataOrConfig, requestConfig)
            case 'put':
                return api.put<T>(url, dataOrConfig, requestConfig)
            case 'patch':
                return api.patch<T>(url, dataOrConfig, requestConfig)
            case 'delete':
                return api.delete<T>(url, requestConfig)
            default: {
                // 添加never检查以确保完整性
                const _exhaustiveCheck: never = method
                throw new Error('Unsupported method: ' + String(_exhaustiveCheck))
            }
        }
    },

    // 原始axios实例（用于特殊需求）
    instance: apiClient
}

export default api

/**
 * LingTaskFlow API 工具函数
 * 提供标准化的API调用方法和错误处理
 */

import { api } from 'src/boot/axios';
import { Notify } from 'quasar';
import type { AxiosResponse } from 'axios';
import type { CustomError, PaginatedData } from 'src/types';

// 扩展的响应类型（axios拦截器已处理后的响应）
interface ExtendedResponse<T = unknown> extends AxiosResponse<T> {
    message?: string;
    meta?: Record<string, unknown>;
}

/**
 * 标准化的API GET请求
 * @param url - 请求URL
 * @param showError - 是否显示错误提示
 * @returns Promise<T> - 返回data字段的数据
 */
export async function apiGet<T = unknown>(url: string, showError = true): Promise<T> {
    try {
        const response = await api.get(url);
        return response.data as T;
    } catch (error) {
        if (showError) {
            handleAPIError(error);
        }
        throw error;
    }
}

/**
 * 标准化的API POST请求
 * @param url - 请求URL
 * @param data - 请求数据
 * @param showError - 是否显示错误提示
 * @param showSuccess - 是否显示成功提示
 * @returns Promise<T> - 返回data字段的数据
 */
export async function apiPost<T = unknown>(
    url: string,
    data?: unknown,
    showError = true,
    showSuccess = false,
): Promise<T> {
    try {
        const response = await api.post(url, data);
        const extendedResponse = response as ExtendedResponse<T>;

        if (showSuccess && extendedResponse.message) {
            Notify.create({
                type: 'positive',
                message: extendedResponse.message,
                position: 'top',
            });
        }

        return extendedResponse.data;
    } catch (error) {
        if (showError) {
            handleAPIError(error);
        }
        throw error;
    }
}

/**
 * 标准化的API PUT请求
 * @param url - 请求URL
 * @param data - 请求数据
 * @param showError - 是否显示错误提示
 * @param showSuccess - 是否显示成功提示
 * @returns Promise<T> - 返回data字段的数据
 */
export async function apiPut<T = unknown>(
    url: string,
    data?: unknown,
    showError = true,
    showSuccess = false,
): Promise<T> {
    try {
        const response = await api.put(url, data);
        const extendedResponse = response as ExtendedResponse<T>;

        if (showSuccess && extendedResponse.message) {
            Notify.create({
                type: 'positive',
                message: extendedResponse.message,
                position: 'top',
            });
        }

        return extendedResponse.data;
    } catch (error) {
        if (showError) {
            handleAPIError(error);
        }
        throw error;
    }
}

/**
 * 标准化的API PATCH请求
 * @param url - 请求URL
 * @param data - 请求数据
 * @param showError - 是否显示错误提示
 * @param showSuccess - 是否显示成功提示
 * @returns Promise<T> - 返回data字段的数据
 */
export async function apiPatch<T = unknown>(
    url: string,
    data?: unknown,
    showError = true,
    showSuccess = false,
): Promise<T> {
    try {
        const response = await api.patch(url, data);
        const extendedResponse = response as ExtendedResponse<T>;

        if (showSuccess && extendedResponse.message) {
            Notify.create({
                type: 'positive',
                message: extendedResponse.message,
                position: 'top',
            });
        }

        return extendedResponse.data;
    } catch (error) {
        if (showError) {
            handleAPIError(error);
        }
        throw error;
    }
}

/**
 * 标准化的API DELETE请求
 * @param url - 请求URL
 * @param showError - 是否显示错误提示
 * @param showSuccess - 是否显示成功提示
 * @returns Promise<T> - 返回data字段的数据
 */
export async function apiDelete<T = unknown>(
    url: string,
    showError = true,
    showSuccess = false,
): Promise<T> {
    try {
        const response = await api.delete(url);
        const extendedResponse = response as ExtendedResponse<T>;

        if (showSuccess && extendedResponse.message) {
            Notify.create({
                type: 'positive',
                message: extendedResponse.message,
                position: 'top',
            });
        }

        return extendedResponse.data;
    } catch (error) {
        if (showError) {
            handleAPIError(error);
        }
        throw error;
    }
}

/**
 * 处理API错误
 * @param error - 错误对象
 */
export function handleAPIError(error: unknown): void {
    let message = '网络错误，请稍后重试';

    if (error instanceof Error) {
        message = error.message;

        // 检查是否有详细的错误信息
        const customError = error as CustomError;
        if (customError.errorData && typeof customError.errorData === 'object') {
            const details = customError.errorData.details || customError.errorData;

            // 如果是验证错误，显示具体字段错误
            if (typeof details === 'object') {
                const fieldErrors: string[] = [];
                for (const [field, fieldError] of Object.entries(details)) {
                    if (Array.isArray(fieldError)) {
                        fieldErrors.push(`${field}: ${fieldError.join(', ')}`);
                    } else {
                        fieldErrors.push(`${field}: ${String(fieldError)}`);
                    }
                }
                if (fieldErrors.length > 0) {
                    message = fieldErrors.join('; ');
                }
            }
        }
    }

    Notify.create({
        type: 'negative',
        message,
        position: 'top',
        timeout: 5000,
        actions: [{ icon: 'close', color: 'white', round: true }],
    });
}

/**
 * 获取分页数据
 * @param url - 请求URL
 * @param params - 查询参数
 * @param showError - 是否显示错误提示
 * @returns Promise<PaginatedData<T>> - 分页数据
 */
export async function apiGetPaginated<T = unknown>(
    url: string,
    params?: Record<string, unknown>,
    showError = true,
): Promise<PaginatedData<T>> {
    try {
        const response = await api.get(url, { params });
        const extendedResponse = response as ExtendedResponse;

        // 从meta中获取分页信息
        const meta = extendedResponse.meta || {};
        const pagination = (meta.pagination || {}) as Record<string, unknown>;

        return {
            results: extendedResponse.data as T[],
            pagination: {
                page: (pagination.page as number) || 1,
                page_size: (pagination.page_size as number) || 20,
                total_pages: (pagination.total_pages as number) || 1,
                total_count: (pagination.total_count as number) || 0,
                has_next: (pagination.has_next as boolean) || false,
                has_previous: (pagination.has_previous as boolean) || false,
                next_page: (pagination.next_page as number) || null,
                previous_page: (pagination.previous_page as number) || null,
            },
        };
    } catch (error) {
        if (showError) {
            handleAPIError(error);
        }
        throw error;
    }
}

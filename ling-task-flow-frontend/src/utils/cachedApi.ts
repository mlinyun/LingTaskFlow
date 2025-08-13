/**
 * 带缓存功能的API客户端包装器
 * 自动处理请求缓存、失效和刷新机制
 */

import { CacheConfigs, cacheManager } from './cache';
import { api } from '../boot/axios';
import type { AxiosRequestConfig, AxiosResponse } from 'axios';

interface CachedRequestOptions extends AxiosRequestConfig {
    cache?: {
        key: string;
        config: (typeof CacheConfigs)[keyof typeof CacheConfigs];
        forceRefresh?: boolean;
    };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
interface CachedResponse<T = any> extends AxiosResponse<T> {
    fromCache?: boolean;
}

class CachedApiClient {
    /**
     * 带缓存的GET请求
     */
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    async get<T = any>(
        url: string,
        options: CachedRequestOptions = {},
    ): Promise<CachedResponse<T>> {
        const { cache, ...axiosConfig } = options;

        // 如果没有缓存配置，直接发送请求
        if (!cache) {
            return api.get<T>(url, axiosConfig);
        }

        const { key, config, forceRefresh = false } = cache;
        const cacheKey = `${url}_${JSON.stringify(axiosConfig.params || {})}`;
        const fullCacheKey = `${key}_${cacheKey}`;

        // 如果不强制刷新，先尝试从缓存获取
        if (!forceRefresh) {
            const cachedData = cacheManager.get<T>(fullCacheKey, config);
            if (cachedData) {
                // 返回缓存数据，模拟axios响应格式
                return {
                    data: cachedData,
                    status: 200,
                    statusText: 'OK',
                    headers: {},
                    config: axiosConfig,
                    fromCache: true,
                } as CachedResponse<T>;
            }
        }

        // 发送实际请求
        try {
            const response = await api.get<T>(url, axiosConfig);

            // 缓存响应数据
            cacheManager.set(fullCacheKey, response.data, config);

            return {
                ...response,
                fromCache: false,
            };
        } catch (error: unknown) {
            // 如果请求失败且有缓存数据，返回缓存数据
            const cachedData = cacheManager.get<T>(fullCacheKey, config);
            if (cachedData) {
                console.warn('API请求失败，返回缓存数据:', error);
                return {
                    data: cachedData,
                    status: 200,
                    statusText: 'OK (from cache)',
                    headers: {},
                    config: axiosConfig,
                    fromCache: true,
                } as CachedResponse<T>;
            }
            throw error;
        }
    }

    /**
     * POST请求（清除相关缓存）
     */
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    async post<T = any>(
        url: string,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        data?: any,
        options: CachedRequestOptions = {},
    ): Promise<AxiosResponse<T>> {
        const { cache, ...axiosConfig } = options;

        const response = await api.post<T>(url, data, axiosConfig);

        // POST请求成功后，清除相关缓存
        if (cache) {
            this.invalidateCache(cache.key, cache.config);
        }

        return response;
    }

    /**
     * PUT请求（清除相关缓存）
     */
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    async put<T = any>(
        url: string,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        data?: any,
        options: CachedRequestOptions = {},
    ): Promise<AxiosResponse<T>> {
        const { cache, ...axiosConfig } = options;

        const response = await api.put<T>(url, data, axiosConfig);

        // PUT请求成功后，清除相关缓存
        if (cache) {
            this.invalidateCache(cache.key, cache.config);
        }

        return response;
    }

    /**
     * PATCH请求（清除相关缓存）
     */
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    async patch<T = any>(
        url: string,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        data?: any,
        options: CachedRequestOptions = {},
    ): Promise<AxiosResponse<T>> {
        const { cache, ...axiosConfig } = options;

        const response = await api.patch<T>(url, data, axiosConfig);

        // PATCH请求成功后，清除相关缓存
        if (cache) {
            this.invalidateCache(cache.key, cache.config);
        }

        return response;
    }

    /**
     * DELETE请求（清除相关缓存）
     */
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    async delete<T = any>(
        url: string,
        options: CachedRequestOptions = {},
    ): Promise<AxiosResponse<T>> {
        const { cache, ...axiosConfig } = options;

        const response = await api.delete<T>(url, axiosConfig);

        // DELETE请求成功后，清除相关缓存
        if (cache) {
            this.invalidateCache(cache.key, cache.config);
        }

        return response;
    }

    /**
     * 清除指定缓存
     */
    invalidateCache(key: string, config: (typeof CacheConfigs)[keyof typeof CacheConfigs]): void {
        // 清除以指定key开头的所有缓存项
        const prefix = config.prefix + key;
        cacheManager.clear({ ...config, prefix });
    }

    /**
     * 清除所有缓存
     */
    clearAllCache(): void {
        Object.values(CacheConfigs).forEach(config => {
            cacheManager.clear(config);
        });
    }

    /**
     * 获取缓存统计信息
     */
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    getCacheStats(): Record<string, any> {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const stats: Record<string, any> = {};

        Object.entries(CacheConfigs).forEach(([name, config]) => {
            stats[name] = cacheManager.getStats(config);
        });

        return stats;
    }

    /**
     * 预热缓存 - 预加载常用数据
     */
    async warmupCache(): Promise<void> {
        try {
            // 预加载用户信息
            await this.get('/auth/profile/', {
                cache: {
                    key: 'profile',
                    config: CacheConfigs.USER,
                },
            });

            // 预加载任务统计
            await this.get('/tasks/stats/', {
                cache: {
                    key: 'stats',
                    config: CacheConfigs.STATS,
                },
            });

            console.log('缓存预热完成');
        } catch (error) {
            console.warn('缓存预热失败:', error);
        }
    }
}

// 创建全局缓存API客户端实例
export const cachedApi = new CachedApiClient();

// 导出常用的缓存配置
export { CacheConfigs };

// 导出缓存管理器（用于手动操作）
export { cacheManager };

export default cachedApi;

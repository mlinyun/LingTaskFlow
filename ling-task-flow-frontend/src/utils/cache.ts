/**
 * 请求缓存策略实现
 * 支持内存缓存、本地存储缓存和缓存失效机制
 */

// eslint-disable-next-line @typescript-eslint/no-explicit-any
interface CacheItem<T = any> {
    data: T;
    timestamp: number;
    expiry: number; // 过期时间（毫秒）
    key: string;
}

interface CacheOptions {
    expiry?: number; // 缓存过期时间（毫秒），默认5分钟
    storage?: 'memory' | 'localStorage' | 'sessionStorage'; // 存储类型
    prefix?: string; // 缓存键前缀
}

class CacheManager {
    private memoryCache = new Map<string, CacheItem>();
    private readonly defaultExpiry = 5 * 60 * 1000; // 5分钟
    private readonly defaultPrefix = 'ltf_cache_';

    /**
     * 设置缓存
     */
    set<T>(key: string, data: T, options: CacheOptions = {}): void {
        const {
            expiry = this.defaultExpiry,
            storage = 'memory',
            prefix = this.defaultPrefix,
        } = options;

        const cacheKey = prefix + key;
        const cacheItem: CacheItem<T> = {
            data,
            timestamp: Date.now(),
            expiry,
            key: cacheKey,
        };

        switch (storage) {
            case 'memory':
                this.memoryCache.set(cacheKey, cacheItem);
                break;
            case 'localStorage':
                try {
                    localStorage.setItem(cacheKey, JSON.stringify(cacheItem));
                } catch {
                    console.warn('localStorage缓存失败');
                    // 降级到内存缓存
                    this.memoryCache.set(cacheKey, cacheItem);
                }
                break;
            case 'sessionStorage':
                try {
                    sessionStorage.setItem(cacheKey, JSON.stringify(cacheItem));
                } catch {
                    console.warn('sessionStorage缓存失败');
                    // 降级到内存缓存
                    this.memoryCache.set(cacheKey, cacheItem);
                }
                break;
        }
    }

    /**
     * 获取缓存
     */
    get<T>(key: string, options: CacheOptions = {}): T | null {
        const { storage = 'memory', prefix = this.defaultPrefix } = options;

        const cacheKey = prefix + key;
        let cacheItem: CacheItem<T> | null = null;

        switch (storage) {
            case 'memory':
                cacheItem = this.memoryCache.get(cacheKey) || null;
                break;
            case 'localStorage':
                try {
                    const stored = localStorage.getItem(cacheKey);
                    if (stored) {
                        cacheItem = JSON.parse(stored);
                    }
                } catch {
                    console.warn('localStorage读取失败');
                }
                break;
            case 'sessionStorage':
                try {
                    const stored = sessionStorage.getItem(cacheKey);
                    if (stored) {
                        cacheItem = JSON.parse(stored);
                    }
                } catch {
                    console.warn('sessionStorage读取失败');
                }
                break;
        }

        if (!cacheItem) {
            return null;
        }

        // 检查是否过期
        const now = Date.now();
        if (now - cacheItem.timestamp > cacheItem.expiry) {
            this.delete(key, options);
            return null;
        }

        return cacheItem.data;
    }

    /**
     * 删除缓存
     */
    delete(key: string, options: CacheOptions = {}): void {
        const { storage = 'memory', prefix = this.defaultPrefix } = options;

        const cacheKey = prefix + key;

        switch (storage) {
            case 'memory':
                this.memoryCache.delete(cacheKey);
                break;
            case 'localStorage':
                localStorage.removeItem(cacheKey);
                break;
            case 'sessionStorage':
                sessionStorage.removeItem(cacheKey);
                break;
        }
    }

    /**
     * 清空所有缓存
     */
    clear(options: CacheOptions = {}): void {
        const { storage = 'memory', prefix = this.defaultPrefix } = options;

        switch (storage) {
            case 'memory':
                // 清空内存缓存中指定前缀的项
                for (const key of this.memoryCache.keys()) {
                    if (key.startsWith(prefix)) {
                        this.memoryCache.delete(key);
                    }
                }
                break;
            case 'localStorage':
                // 清空localStorage中指定前缀的项
                for (let i = localStorage.length - 1; i >= 0; i--) {
                    const key = localStorage.key(i);
                    if (key && key.startsWith(prefix)) {
                        localStorage.removeItem(key);
                    }
                }
                break;
            case 'sessionStorage':
                // 清空sessionStorage中指定前缀的项
                for (let i = sessionStorage.length - 1; i >= 0; i--) {
                    const key = sessionStorage.key(i);
                    if (key && key.startsWith(prefix)) {
                        sessionStorage.removeItem(key);
                    }
                }
                break;
        }
    }

    /**
     * 清理过期缓存
     */
    cleanExpired(options: CacheOptions = {}): void {
        const { storage = 'memory', prefix = this.defaultPrefix } = options;

        const now = Date.now();

        switch (storage) {
            case 'memory':
                for (const [key, item] of this.memoryCache.entries()) {
                    if (key.startsWith(prefix) && now - item.timestamp > item.expiry) {
                        this.memoryCache.delete(key);
                    }
                }
                break;
            case 'localStorage':
                for (let i = localStorage.length - 1; i >= 0; i--) {
                    const key = localStorage.key(i);
                    if (key && key.startsWith(prefix)) {
                        try {
                            const stored = localStorage.getItem(key);
                            if (stored) {
                                const item: CacheItem = JSON.parse(stored);
                                if (now - item.timestamp > item.expiry) {
                                    localStorage.removeItem(key);
                                }
                            }
                        } catch {
                            // 解析失败，删除该项
                            localStorage.removeItem(key);
                        }
                    }
                }
                break;
            case 'sessionStorage':
                for (let i = sessionStorage.length - 1; i >= 0; i--) {
                    const key = sessionStorage.key(i);
                    if (key && key.startsWith(prefix)) {
                        try {
                            const stored = sessionStorage.getItem(key);
                            if (stored) {
                                const item: CacheItem = JSON.parse(stored);
                                if (now - item.timestamp > item.expiry) {
                                    sessionStorage.removeItem(key);
                                }
                            }
                        } catch {
                            // 解析失败，删除该项
                            sessionStorage.removeItem(key);
                        }
                    }
                }
                break;
        }
    }

    /**
     * 获取缓存统计信息
     */
    getStats(options: CacheOptions = {}): {
        total: number;
        expired: number;
        valid: number;
        size: string;
    } {
        const { storage = 'memory', prefix = this.defaultPrefix } = options;

        let total = 0;
        let expired = 0;
        let valid = 0;
        let totalSize = 0;

        const now = Date.now();

        switch (storage) {
            case 'memory':
                for (const [key, item] of this.memoryCache.entries()) {
                    if (key.startsWith(prefix)) {
                        total++;
                        totalSize += JSON.stringify(item).length;
                        if (now - item.timestamp > item.expiry) {
                            expired++;
                        } else {
                            valid++;
                        }
                    }
                }
                break;
            case 'localStorage':
            case 'sessionStorage': {
                const storage_obj = storage === 'localStorage' ? localStorage : sessionStorage;
                for (let i = 0; i < storage_obj.length; i++) {
                    const key = storage_obj.key(i);
                    if (key && key.startsWith(prefix)) {
                        try {
                            const stored = storage_obj.getItem(key);
                            if (stored) {
                                total++;
                                totalSize += stored.length;
                                const item: CacheItem = JSON.parse(stored);
                                if (now - item.timestamp > item.expiry) {
                                    expired++;
                                } else {
                                    valid++;
                                }
                            }
                        } catch {
                            total++; // 计入总数，但不计入有效或过期
                        }
                    }
                }
                break;
            }
        }

        return {
            total,
            expired,
            valid,
            size: this.formatBytes(totalSize),
        };
    }

    /**
     * 格式化字节大小
     */
    private formatBytes(bytes: number): string {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// 创建全局缓存管理器实例
export const cacheManager = new CacheManager();

// 预定义的缓存配置
export const CacheConfigs = {
    // 任务列表缓存 - 5分钟
    TASKS: {
        expiry: 5 * 60 * 1000,
        storage: 'memory' as const,
        prefix: 'ltf_tasks_',
    },
    // 统计数据缓存 - 10分钟
    STATS: {
        expiry: 10 * 60 * 1000,
        storage: 'memory' as const,
        prefix: 'ltf_stats_',
    },
    // 用户信息缓存 - 30分钟
    USER: {
        expiry: 30 * 60 * 1000,
        storage: 'localStorage' as const,
        prefix: 'ltf_user_',
    },
    // 搜索历史缓存 - 1天
    SEARCH_HISTORY: {
        expiry: 24 * 60 * 60 * 1000,
        storage: 'localStorage' as const,
        prefix: 'ltf_search_',
    },
    // 临时数据缓存 - 1分钟
    TEMP: {
        expiry: 1 * 60 * 1000,
        storage: 'sessionStorage' as const,
        prefix: 'ltf_temp_',
    },
};

// 定期清理过期缓存（每10分钟执行一次）
setInterval(
    () => {
        Object.values(CacheConfigs).forEach(config => {
            cacheManager.cleanExpired(config);
        });
    },
    10 * 60 * 1000,
);

// 页面卸载时清理临时缓存
window.addEventListener('beforeunload', () => {
    cacheManager.clear(CacheConfigs.TEMP);
});

export default cacheManager;

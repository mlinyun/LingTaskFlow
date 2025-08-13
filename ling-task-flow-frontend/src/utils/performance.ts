/**
 * 组件渲染性能优化工具
 * 包括防抖、节流、虚拟滚动优化、组件懒加载等
 */

import { computed, nextTick, onMounted, onUnmounted, ref, type Ref } from 'vue';

/**
 * 防抖函数
 * @param fn 要防抖的函数
 * @param delay 延迟时间（毫秒）
 * @param immediate 是否立即执行
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function debounce<T extends (...args: any[]) => any>(
    fn: T,
    delay: number = 300,
    immediate: boolean = false,
): (...args: Parameters<T>) => void {
    let timeoutId: number | null = null;
    let isInvoked = false;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return function (this: any, ...args: Parameters<T>) {
        const callNow = immediate && !isInvoked;

        if (timeoutId !== null) {
            clearTimeout(timeoutId);
        }

        timeoutId = window.setTimeout(() => {
            isInvoked = false;
            if (!immediate) {
                fn.apply(this, args);
            }
        }, delay);

        if (callNow) {
            isInvoked = true;
            fn.apply(this, args);
        }
    };
}

/**
 * 节流函数
 * @param fn 要节流的函数
 * @param delay 延迟时间（毫秒）
 * @param options 选项
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function throttle<T extends (...args: any[]) => any>(
    fn: T,
    delay: number = 300,
    options: { leading?: boolean; trailing?: boolean } = {},
): (...args: Parameters<T>) => void {
    const { leading = true, trailing = true } = options;
    let timeoutId: number | null = null;
    let lastExecTime = 0;
    let lastArgs: Parameters<T> | null = null;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return function (this: any, ...args: Parameters<T>) {
        const currentTime = Date.now();
        const timeSinceLastExec = currentTime - lastExecTime;

        lastArgs = args;

        const executeFunction = () => {
            lastExecTime = Date.now();
            fn.apply(this, lastArgs!);
        };

        if (timeSinceLastExec >= delay) {
            if (leading) {
                executeFunction();
            }
        } else {
            if (timeoutId !== null) {
                clearTimeout(timeoutId);
            }

            if (trailing) {
                timeoutId = window.setTimeout(() => {
                    executeFunction();
                    timeoutId = null;
                }, delay - timeSinceLastExec);
            }
        }
    };
}

/**
 * RAF 节流函数
 * @param fn 要执行的函数
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function rafThrottle<T extends (...args: any[]) => any>(
    fn: T,
): (...args: Parameters<T>) => void {
    let rafId: number | null = null;
    let lastArgs: Parameters<T> | null = null;

    return function (this: unknown, ...args: Parameters<T>) {
        lastArgs = args;

        if (rafId === null) {
            rafId = requestAnimationFrame(() => {
                fn.apply(this, lastArgs!);
                rafId = null;
            });
        }
    };
}

/**
 * 组件懒加载 Hook
 * @param threshold 触发阈值
 * @param rootMargin 根边距
 */
export function useLazyLoad(threshold: number = 0.1, rootMargin: string = '50px') {
    const target = ref<HTMLElement>();
    const isVisible = ref(false);
    const isLoaded = ref(false);

    let observer: IntersectionObserver | null = null;

    onMounted(() => {
        if (!target.value) return;

        observer = new IntersectionObserver(
            entries => {
                const entry = entries[0];
                if (entry && entry.isIntersecting && !isLoaded.value) {
                    isVisible.value = true;
                    isLoaded.value = true;
                    observer?.unobserve(target.value!);
                }
            },
            { threshold, rootMargin },
        );

        observer.observe(target.value);
    });

    onUnmounted(() => {
        if (observer && target.value) {
            observer.unobserve(target.value);
        }
    });

    return {
        target,
        isVisible,
        isLoaded,
    };
}

/**
 * 虚拟滚动优化 Hook
 * @param items 数据列表
 * @param itemHeight 每项高度
 * @param containerHeight 容器高度
 * @param overscan 预渲染项数
 */
export function useVirtualScroll<T>(
    items: Ref<T[]>,
    itemHeight: number,
    containerHeight: number,
    overscan: number = 5,
) {
    const scrollTop = ref(0);
    const containerRef = ref<HTMLElement>();

    // 计算可见范围
    const visibleRange = computed(() => {
        const start = Math.floor(scrollTop.value / itemHeight);
        const visibleCount = Math.ceil(containerHeight / itemHeight);
        const end = start + visibleCount;

        return {
            start: Math.max(0, start - overscan),
            end: Math.min(items.value.length, end + overscan),
        };
    });

    // 可见项目
    const visibleItems = computed(() => {
        const { start, end } = visibleRange.value;
        return items.value.slice(start, end).map((item, index) => ({
            item,
            index: start + index,
            top: (start + index) * itemHeight,
        }));
    });

    // 总高度
    const totalHeight = computed(() => items.value.length * itemHeight);

    // 滚动处理
    const handleScroll = rafThrottle((event: Event) => {
        const target = event.target as HTMLElement;
        scrollTop.value = target.scrollTop;
    });

    return {
        containerRef,
        visibleItems,
        totalHeight,
        handleScroll,
        scrollTop,
    };
}

/**
 * 图片预加载
 * @param urls 图片URL列表
 * @param options 选项
 */
export function preloadImages(
    urls: string[],
    options: {
        onProgress?: (loaded: number, total: number) => void;
        onComplete?: (results: { url: string; success: boolean }[]) => void;
        timeout?: number;
    } = {},
): Promise<{ url: string; success: boolean }[]> {
    const { onProgress, onComplete, timeout = 10000 } = options;
    const results: { url: string; success: boolean }[] = [];
    let loadedCount = 0;

    return new Promise(resolve => {
        if (urls.length === 0) {
            resolve([]);
            return;
        }

        urls.forEach((url, index) => {
            const img = new Image();
            let isResolved = false;

            const handleLoad = (success: boolean) => {
                if (isResolved) return;
                isResolved = true;

                results[index] = { url, success };
                loadedCount++;

                onProgress?.(loadedCount, urls.length);

                if (loadedCount === urls.length) {
                    onComplete?.(results);
                    resolve(results);
                }
            };

            img.onload = () => handleLoad(true);
            img.onerror = () => handleLoad(false);

            // 超时处理
            setTimeout(() => handleLoad(false), timeout);

            img.src = url;
        });
    });
}

/**
 * 组件更新优化 Hook
 * 使用浅比较避免不必要的重新渲染
 */
export function useShallowCompare<T extends Record<string, unknown>>(props: T): Ref<T> {
    const memoizedProps = ref<T>({ ...props });
    const prevProps = ref<T>({ ...props });

    // 浅比较函数
    const shallowEqual = (obj1: T, obj2: T): boolean => {
        const keys1 = Object.keys(obj1);
        const keys2 = Object.keys(obj2);

        if (keys1.length !== keys2.length) {
            return false;
        }

        for (const key of keys1) {
            if (obj1[key] !== obj2[key]) {
                return false;
            }
        }

        return true;
    };

    // 更新检查
    const updateProps = (newProps: T) => {
        if (!shallowEqual(newProps, prevProps.value)) {
            memoizedProps.value = { ...newProps };
            prevProps.value = { ...newProps };
        }
    };

    return computed(() => {
        updateProps(props);
        return memoizedProps.value;
    });
}

/**
 * 批量DOM更新
 * @param updates 更新函数列表
 */
export async function batchDOMUpdates(updates: (() => void)[]): Promise<void> {
    // 批量执行更新
    updates.forEach(update => update());

    // 等待DOM更新完成
    await nextTick();
}

/**
 * 性能监控
 */
export class PerformanceMonitor {
    private marks: Map<string, number> = new Map();
    private measures: Map<string, number> = new Map();

    /**
     * 开始计时
     */
    mark(name: string): void {
        this.marks.set(name, performance.now());
    }

    /**
     * 结束计时并返回耗时
     */
    measure(name: string, startMark?: string): number {
        const endTime = performance.now();
        const startTime = startMark ? this.marks.get(startMark) : this.marks.get(name);

        if (startTime === undefined) {
            console.warn(`Performance mark '${startMark || name}' not found`);
            return 0;
        }

        const duration = endTime - startTime;
        this.measures.set(name, duration);

        return duration;
    }

    /**
     * 获取测量结果
     */
    getMeasure(name: string): number | undefined {
        return this.measures.get(name);
    }

    /**
     * 获取所有测量结果
     */
    getAllMeasures(): Record<string, number> {
        return Object.fromEntries(this.measures);
    }

    /**
     * 清除所有标记和测量
     */
    clear(): void {
        this.marks.clear();
        this.measures.clear();
    }

    /**
     * 记录组件渲染时间
     */
    measureComponent(componentName: string, renderFn: () => void): number {
        this.mark(`${componentName}-start`);
        renderFn();
        return this.measure(`${componentName}-render`, `${componentName}-start`);
    }
}

// 全局性能监控实例
export const performanceMonitor = new PerformanceMonitor();

/**
 * 内存使用监控
 */
export function getMemoryUsage(): {
    used: number;
    total: number;
    percentage: number;
} | null {
    if ('memory' in performance) {
        const memory = (
            performance as unknown as {
                memory: { usedJSHeapSize: number; totalJSHeapSize: number; limit: number };
            }
        ).memory;
        return {
            used: memory.usedJSHeapSize,
            total: memory.totalJSHeapSize,
            percentage: (memory.usedJSHeapSize / memory.totalJSHeapSize) * 100,
        };
    }
    return null;
}

/**
 * 组件渲染性能装饰器
 */
export function withPerformanceTracking<T extends (...args: unknown[]) => unknown>(
    fn: T,
    name: string,
): T {
    return ((...args: unknown[]) => {
        performanceMonitor.mark(`${name}-start`);
        const result = fn(...args);
        const duration = performanceMonitor.measure(`${name}-execution`, `${name}-start`);

        if (duration > 16) {
            // 超过一帧的时间
            console.warn(`Performance warning: ${name} took ${duration.toFixed(2)}ms`);
        }

        return result;
    }) as T;
}

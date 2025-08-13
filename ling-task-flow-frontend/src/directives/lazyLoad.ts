/**
 * 图片懒加载指令
 * 支持占位符、加载动画、错误处理和性能优化
 */

import type { DirectiveBinding } from 'vue';

interface LazyLoadOptions {
    placeholder?: string; // 占位符图片URL
    error?: string; // 错误时显示的图片URL
    loading?: string; // 加载中显示的图片URL
    threshold?: number; // 触发加载的阈值（0-1）
    rootMargin?: string; // 根边距
    attempts?: number; // 重试次数
    delay?: number; // 延迟加载时间（毫秒）
    fade?: boolean; // 是否启用淡入效果
}

interface LazyImageElement extends HTMLImageElement {
    _lazyLoadObserver?: IntersectionObserver;
    _lazyLoadOptions?: LazyLoadOptions;
    _lazyLoadAttempts?: number;
    _lazyLoadOriginalSrc?: string;
}

// 默认配置
const defaultOptions: LazyLoadOptions = {
    placeholder:
        'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OTk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkxvYWRpbmcuLi48L3RleHQ+PC9zdmc+',
    error: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjVmNWY1Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZmlsbD0iI2NjY2NjYyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkVycm9yPC90ZXh0Pjwvc3ZnPg==',
    loading:
        'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+PGNpcmNsZSBjeD0iMTAwIiBjeT0iMTAwIiByPSIyMCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjMDA3N2ZmIiBzdHJva2Utd2lkdGg9IjIiPjxhbmltYXRlIGF0dHJpYnV0ZU5hbWU9InIiIGZyb209IjAiIHRvPSIyMCIgZHVyPSIxcyIgcmVwZWF0Q291bnQ9ImluZGVmaW5pdGUiLz48L2NpcmNsZT48L3N2Zz4=',
    threshold: 0.1,
    rootMargin: '50px',
    attempts: 3,
    delay: 0,
    fade: true,
};

// 全局观察器实例
let globalObserver: IntersectionObserver | null = null;

/**
 * 创建或获取全局观察器
 */
function getObserver(options: LazyLoadOptions): IntersectionObserver {
    if (!globalObserver) {
        globalObserver = new IntersectionObserver(
            entries => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target as LazyImageElement;
                        loadImage(img);
                        globalObserver?.unobserve(img);
                    }
                });
            },
            {
                threshold: options.threshold || 0.1,
                rootMargin: options.rootMargin || '0px',
            },
        );
    }
    return globalObserver;
}

/**
 * 加载图片
 */
function loadImage(img: LazyImageElement): void {
    const options = img._lazyLoadOptions || defaultOptions;
    const originalSrc = img._lazyLoadOriginalSrc;

    if (!originalSrc) return;

    // 显示加载状态
    if (options.loading) {
        img.src = options.loading;
    }

    // 创建新的图片对象来预加载
    const imageLoader = new Image();

    imageLoader.onload = () => {
        // 延迟加载（如果设置了延迟）
        setTimeout(() => {
            img.src = originalSrc;
            img.classList.add('lazy-loaded');

            // 添加淡入效果
            if (options.fade) {
                img.style.opacity = '0';
                img.style.transition = 'opacity 0.3s ease-in-out';

                // 强制重绘
                void img.offsetHeight;

                img.style.opacity = '1';
            }

            // 触发自定义事件
            img.dispatchEvent(
                new CustomEvent('lazy-loaded', {
                    detail: { src: originalSrc },
                }),
            );
        }, options.delay || 0);
    };

    imageLoader.onerror = () => {
        img._lazyLoadAttempts = (img._lazyLoadAttempts || 0) + 1;

        // 如果还有重试次数，延迟重试
        if (img._lazyLoadAttempts < (options.attempts || 3)) {
            setTimeout(() => {
                loadImage(img);
            }, 1000 * img._lazyLoadAttempts); // 递增延迟
        } else {
            // 显示错误图片
            if (options.error) {
                img.src = options.error;
            }
            img.classList.add('lazy-error');

            // 触发错误事件
            img.dispatchEvent(
                new CustomEvent('lazy-error', {
                    detail: { src: originalSrc, attempts: img._lazyLoadAttempts },
                }),
            );
        }
    };

    // 开始加载
    imageLoader.src = originalSrc;
}

/**
 * 解析指令参数
 */
function parseOptions(binding: DirectiveBinding): LazyLoadOptions {
    const options = { ...defaultOptions };

    if (typeof binding.value === 'object' && binding.value !== null) {
        Object.assign(options, binding.value);
    }

    // 从修饰符中解析选项
    if (binding.modifiers.immediate) {
        options.threshold = 1;
        options.rootMargin = '0px';
    }

    if (binding.modifiers.slow) {
        options.delay = 500;
    }

    if (binding.modifiers.fast) {
        options.delay = 0;
    }

    return options;
}

/**
 * 懒加载指令
 */
export const lazyLoad = {
    mounted(el: LazyImageElement, binding: DirectiveBinding) {
        // 只处理img元素
        if (el.tagName !== 'IMG') {
            console.warn('v-lazy-load指令只能用于img元素');
            return;
        }

        const options = parseOptions(binding);
        const src = binding.arg || el.getAttribute('data-src') || el.src;

        if (!src) {
            console.warn('v-lazy-load指令需要指定图片源');
            return;
        }

        // 保存配置和原始src
        el._lazyLoadOptions = options;
        el._lazyLoadOriginalSrc = src;
        el._lazyLoadAttempts = 0;

        // 设置占位符
        if (options.placeholder) {
            el.src = options.placeholder;
        }

        // 添加CSS类
        el.classList.add('lazy-loading');

        // 如果浏览器支持IntersectionObserver，使用观察器
        if ('IntersectionObserver' in window) {
            const observer = getObserver(options);
            el._lazyLoadObserver = observer;
            observer.observe(el);
        } else {
            // 降级方案：立即加载
            loadImage(el);
        }
    },

    updated(el: LazyImageElement, binding: DirectiveBinding) {
        // 如果src发生变化，重新加载
        const newSrc = binding.arg || el.getAttribute('data-src');
        const oldSrc = el._lazyLoadOriginalSrc;

        if (newSrc && newSrc !== oldSrc) {
            // 停止观察旧元素
            if (el._lazyLoadObserver) {
                el._lazyLoadObserver.unobserve(el);
            }

            // 重新初始化
            const options = parseOptions(binding);
            el._lazyLoadOptions = options;
            el._lazyLoadOriginalSrc = newSrc;
            el._lazyLoadAttempts = 0;

            // 重置状态
            el.classList.remove('lazy-loaded', 'lazy-error');
            el.classList.add('lazy-loading');

            // 设置占位符
            if (options.placeholder) {
                el.src = options.placeholder;
            }

            // 重新观察
            if (el._lazyLoadObserver) {
                el._lazyLoadObserver.observe(el);
            }
        }
    },

    unmounted(el: LazyImageElement) {
        // 清理观察器
        if (el._lazyLoadObserver) {
            el._lazyLoadObserver.unobserve(el);
        }

        // 清理属性
        delete el._lazyLoadObserver;
        delete el._lazyLoadOptions;
        delete el._lazyLoadAttempts;
        delete el._lazyLoadOriginalSrc;
    },
};

// 添加CSS样式
if (typeof document !== 'undefined') {
    const style = document.createElement('style');
    style.textContent = `
        .lazy-loading {
            background-color: #f5f5f5;
            background-image: linear-gradient(45deg, transparent 25%, rgba(255,255,255,.5) 25%, rgba(255,255,255,.5) 75%, transparent 75%, transparent),
                              linear-gradient(45deg, transparent 25%, rgba(255,255,255,.5) 25%, rgba(255,255,255,.5) 75%, transparent 75%, transparent);
            background-size: 20px 20px;
            background-position: 0 0, 10px 10px;
            animation: lazy-loading-animation 1s linear infinite;
        }
        
        .lazy-loaded {
            background: none;
            animation: none;
        }
        
        .lazy-error {
            background: #f5f5f5;
            animation: none;
        }
        
        @keyframes lazy-loading-animation {
            0% {
                background-position: 0 0, 10px 10px;
            }
            100% {
                background-position: 20px 20px, 30px 30px;
            }
        }
    `;
    document.head.appendChild(style);
}

export default lazyLoad;

/**
 * 标签处理工具函数
 * 统一处理任务标签的解析和格式化
 */

/**
 * 将标签字符串解析为标签数组
 * @param tagsString 逗号分隔的标签字符串
 * @returns 标签数组
 */
export function parseTagsString(tagsString: string | undefined | null): string[] {
    if (!tagsString || typeof tagsString !== 'string') {
        return [];
    }

    return tagsString
        .split(',')
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0);
}

/**
 * 将标签数组格式化为字符串
 * @param tags 标签数组
 * @returns 逗号分隔的标签字符串
 */
export function formatTagsArray(tags: string[]): string {
    if (!Array.isArray(tags)) {
        return '';
    }

    return tags
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0)
        .join(', ');
}

/**
 * 获取任务的标签数组（兼容函数，保持向后兼容）
 * @param tagsString 逗号分隔的标签字符串
 * @returns 标签数组
 */
export function getTaskTags(tagsString: string | undefined | null): string[] {
    return parseTagsString(tagsString);
}

/**
 * 验证标签是否有效
 * @param tag 标签字符串
 * @returns 是否有效
 */
export function isValidTag(tag: string): boolean {
    if (typeof tag !== 'string') {
        return false;
    }

    const trimmed = tag.trim();

    // 检查长度
    if (trimmed.length === 0 || trimmed.length > 50) {
        return false;
    }

    // 检查是否包含非法字符（逗号、换行符等）
    if (trimmed.includes(',') || trimmed.includes('\n') || trimmed.includes('\r')) {
        return false;
    }

    return true;
}

/**
 * 清理和规范化标签数组
 * @param tags 原始标签数组
 * @returns 清理后的标签数组
 */
export function cleanTags(tags: string[]): string[] {
    if (!Array.isArray(tags)) {
        return [];
    }

    return (
        tags
            .map(tag => tag.trim())
            .filter(tag => isValidTag(tag))
            // 去重，保持原有顺序
            .filter((tag, index, arr) => arr.indexOf(tag) === index)
            // 限制标签数量
            .slice(0, 10)
    );
}

/**
 * 标签显示的辅助函数
 * @param tags 标签数组
 * @param maxDisplay 最大显示数量，默认3个
 * @returns 包含显示标签和剩余数量的对象
 */
export function getDisplayTags(
    tags: string[],
    maxDisplay: number = 3,
): {
    displayTags: string[];
    remainingCount: number;
    hasMore: boolean;
} {
    const cleanedTags = cleanTags(tags);
    const displayTags = cleanedTags.slice(0, maxDisplay);
    const remainingCount = Math.max(0, cleanedTags.length - maxDisplay);

    return {
        displayTags,
        remainingCount,
        hasMore: remainingCount > 0,
    };
}

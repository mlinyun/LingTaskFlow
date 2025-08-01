/**
 * 组件特定的类型定义
 * 用于示例组件或特定UI组件的类型
 */

// 示例Todo类型（示例组件使用）
export interface Todo {
    id: number;
    content: string;
}

// 示例Meta类型（示例组件使用）
export interface Meta {
    totalCount: number;
}

// 可以在这里添加其他组件特定的类型定义
// 对于应用级别的类型，请使用 src/types/ 中的模块化类型

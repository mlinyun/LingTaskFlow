<template>
    <div class="statistic-card">
        <div class="card-header">
            <q-icon :name="icon" size="20px" />
            <span>{{ title }}</span>
        </div>
        <div class="card-content">
            <div v-if="items && items.length > 0">
                <div
                    v-for="item in items"
                    :key="item.key"
                    class="stat-row"
                    @click="handleRowClick(item)"
                >
                    <span class="stat-label">{{ item.label }}</span>
                    <div class="stat-bar">
                        <q-linear-progress
                            :color="getItemColor(item)"
                            :value="item.percentage / 100"
                            rounded
                            size="6px"
                        />
                        <span class="stat-value">{{ formatValue(item) }}</span>
                    </div>
                </div>
            </div>
            <div v-else class="no-data">{{ noDataText }}</div>
        </div>
    </div>
</template>

<script lang="ts" setup>
// 定义统计项的接口
interface StatisticItem {
    key: string;
    label: string;
    count: number;
    percentage: number;
    range?: string; // 进度分析特有
    category?: string; // 标签统计特有
}

// 组件属性
interface Props {
    title: string;
    icon: string;
    items: StatisticItem[];
    noDataText?: string;
    type?: 'category' | 'progress';
    showPercentage?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
    noDataText: '暂无数据',
    type: 'category',
    showPercentage: false,
});

// 事件定义
interface Emits {
    (e: 'item-click', item: StatisticItem): void;
}

const emit = defineEmits<Emits>();

// 处理行点击事件
const handleRowClick = (item: StatisticItem) => {
    emit('item-click', item);
};

// 获取项目颜色
const getItemColor = (item: StatisticItem): string => {
    if (props.type === 'progress' && item.range) {
        return getProgressColor(item.range);
    }

    if (props.type === 'category') {
        return getCategoryColor(item.category || item.key);
    }

    return 'primary';
};

// 进度颜色映射
const getProgressColor = (range: string): string => {
    if (range.includes('0-0')) return 'red';
    if (range.includes('1-25')) return 'orange';
    if (range.includes('26-50')) return 'amber';
    if (range.includes('51-75')) return 'light-green';
    if (range.includes('76-99') || range.includes('100-100')) return 'green';
    return 'blue';
};

// 标签颜色映射 - 根据数量排序动态分配颜色
const getCategoryColor = (category: string): string => {
    // 定义颜色序列，按排名顺序分配
    const colorSequence = [
        'blue', // 第1名 - 皇家蓝
        'green', // 第2名 - 绿色
        'orange', // 第3名 - 橙色
        'purple', // 第4名 - 紫色
        'teal', // 第5名 - 青色
        'indigo', // 第6名 - 靛蓝
        'pink', // 第7名 - 粉色
        'amber', // 第8名 - 琥珀色
        'deep-orange', // 第9名 - 深橙色
        'cyan', // 第10名 - 青蓝色
        'lime', // 第11名 - 柠檬绿
        'grey', // 第12名及以后 - 灰色
    ];

    // 如果是标签类型，根据排序获取颜色
    if (props.type === 'category' && props.items.length > 0) {
        // 创建按数量排序的标签列表
        const sortedCategories = [...props.items]
            .sort((a, b) => b.count - a.count)
            .map(item => item.category || item.key);

        // 找到当前标签在排序中的位置
        const rankIndex = sortedCategories.indexOf(category);

        // 根据排名返回对应颜色，超出范围使用灰色
        if (rankIndex >= 0 && rankIndex < colorSequence.length) {
            return colorSequence[rankIndex] as string;
        }

        // 如果超出定义的颜色范围，使用灰色
        return 'grey';
    }

    // 默认返回主色调
    return 'primary';
};

// 格式化值显示
const formatValue = (item: StatisticItem): string => {
    if (props.showPercentage) {
        return `${item.percentage.toFixed(1)}%`;
    }

    // 同时显示数量和百分比，让数据更加明确
    return `${item.count} (${item.percentage.toFixed(2)}%)`;
};
</script>

<style lang="scss" scoped>
.statistic-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow:
        0 4px 20px rgba(0, 0, 0, 0.04),
        0 1px 3px rgba(0, 0, 0, 0.02);
    border: 1px solid rgba(226, 232, 240, 0.8);
    transition: all 0.3s ease;

    &:hover {
        transform: translateY(-2px);
        box-shadow:
            0 8px 25px rgba(0, 0, 0, 0.08),
            0 3px 10px rgba(0, 0, 0, 0.04);
    }

    .card-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #e2e8f0;
        font-size: 1rem;
        font-weight: 600;
        color: #1e293b;

        .q-icon {
            color: #3b82f6;
        }
    }

    .card-content {
        .no-data {
            text-align: center;
            color: #64748b;
            font-style: italic;
            padding: 2rem 0;
        }

        .stat-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 0;
            border-bottom: 1px solid #f1f5f9;
            cursor: pointer;
            border-radius: 8px;
            margin: 0 -0.5rem;
            padding-left: 0.5rem;
            padding-right: 0.5rem;
            transition: all 0.2s ease;

            &:last-child {
                border-bottom: none;
            }

            &:hover {
                background: rgba(59, 130, 246, 0.04);
                border-color: rgba(59, 130, 246, 0.1);
            }

            .stat-label {
                font-weight: 500;
                color: #374151;
                flex: 0 0 25%;
                transition: color 0.2s ease;
            }

            .stat-bar {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                flex: 1;

                .q-linear-progress {
                    flex: 1;
                }

                .stat-value {
                    font-weight: 600;
                    color: #3b82f6;
                    font-size: 0.875rem;
                    min-width: 5rem;
                    text-align: right;
                    transition: color 0.2s ease;
                    white-space: nowrap;
                }
            }

            &:hover {
                .stat-label {
                    color: #1e293b;
                }

                .stat-value {
                    color: #1d4ed8;
                }
            }
        }
    }
}

// 响应式设计
@media (max-width: 768px) {
    .statistic-card {
        padding: 1rem;

        .card-content {
            .stat-row {
                .stat-label {
                    flex: 0 0 30%;
                    font-size: 0.9rem;
                }

                .stat-bar {
                    gap: 0.5rem;

                    .stat-value {
                        font-size: 0.75rem;
                        min-width: 4rem;
                    }
                }
            }
        }
    }
}
</style>

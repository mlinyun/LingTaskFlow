<template>
    <div class="recent-activity-list">
        <div v-if="!hasActivities" class="no-activity">
            <q-icon name="history" size="48px" color="grey-5" />
            <p class="text-grey-6">暂无最近活动</p>
        </div>

        <div v-else class="activity-timeline">
            <div v-for="activity in displayActivities" :key="activity.id" class="activity-item">
                <div class="activity-icon">
                    <q-icon
                        :name="getActionIcon(activity.action)"
                        :color="getActionColor(activity.action)"
                        size="sm"
                    />
                </div>

                <div class="activity-content">
                    <div class="activity-header">
                        <span class="activity-action">{{ getActionText(activity.action) }}</span>
                        <span class="activity-task">{{ activity.task_title }}</span>
                    </div>
                    <div class="activity-time">
                        <q-icon name="schedule" size="xs" />
                        {{ formatTime(activity.timestamp) }}
                    </div>
                </div>

                <div class="activity-link">
                    <q-btn
                        flat
                        round
                        size="sm"
                        icon="open_in_new"
                        color="grey-6"
                        @click="goToTask(activity.task_id)"
                    >
                        <q-tooltip>查看任务</q-tooltip>
                    </q-btn>
                </div>
            </div>
        </div>

        <div v-if="hasMoreActivities" class="load-more">
            <q-btn flat color="primary" label="查看更多" @click="loadMore" />
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';

interface Activity {
    id: number;
    task_id: number;
    task_title: string;
    action: 'created' | 'updated' | 'completed' | 'deleted' | 'restored';
    timestamp: string;
}

interface Props {
    activities: Activity[];
    maxDisplay?: number;
}

const props = withDefaults(defineProps<Props>(), {
    maxDisplay: 10,
});

const router = useRouter();

const hasActivities = computed(() => {
    return props.activities.length > 0;
});

const displayActivities = computed(() => {
    return props.activities.slice(0, props.maxDisplay);
});

const hasMoreActivities = computed(() => {
    return props.activities.length > props.maxDisplay;
});

const getActionIcon = (action: string) => {
    const icons = {
        created: 'add_circle',
        updated: 'edit',
        completed: 'check_circle',
        deleted: 'delete',
        restored: 'restore',
    };
    return icons[action as keyof typeof icons] || 'info';
};

const getActionColor = (action: string) => {
    // 蓝白科技感配色 - 使用不同深度的蓝色表示不同动作
    const colors = {
        created: '#3b82f6', // 皇家蓝 - 创建
        updated: '#0ea5e9', // 天空蓝 - 更新
        completed: '#06b6d4', // 青蓝色 - 完成
        deleted: '#64748b', // 石板蓝 - 删除
        restored: '#1e40af', // 深海蓝 - 恢复
    };
    return colors[action as keyof typeof colors] || '#94a3b8';
};

const getActionText = (action: string) => {
    const texts = {
        created: '创建了',
        updated: '更新了',
        completed: '完成了',
        deleted: '删除了',
        restored: '恢复了',
    };
    return texts[action as keyof typeof texts] || '操作了';
};

const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (minutes < 1) {
        return '刚刚';
    } else if (minutes < 60) {
        return `${minutes}分钟前`;
    } else if (hours < 24) {
        return `${hours}小时前`;
    } else if (days < 30) {
        return `${days}天前`;
    } else {
        return date.toLocaleDateString('zh-CN');
    }
};

const goToTask = async (taskId: number) => {
    // 跳转到任务详情或任务列表
    await router.push(`/tasks?highlight=${taskId}`);
};

const loadMore = () => {
    // 这里可以触发加载更多活动的事件
    console.log('加载更多活动...');
};
</script>

<style lang="scss" scoped>
.recent-activity-list {
    height: 100%;
    display: flex;
    flex-direction: column;
}

.no-activity {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 200px;
    gap: 12px;

    p {
        margin: 0;
        font-size: 14px;
    }
}

.activity-timeline {
    flex: 1;
    overflow-y: auto;
    padding-right: 8px;

    // 自定义滚动条样式
    &::-webkit-scrollbar {
        width: 4px;
    }

    &::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 2px;
    }

    &::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 2px;

        &:hover {
            background: #a1a1a1;
        }
    }
}

.activity-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid rgba(59, 130, 246, 0.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;

    // 科技感左侧连接线
    &::before {
        content: '';
        position: absolute;
        left: 15px;
        top: 44px;
        bottom: -12px;
        width: 2px;
        background: linear-gradient(
            180deg,
            rgba(59, 130, 246, 0.3) 0%,
            rgba(59, 130, 246, 0.1) 100%
        );
    }

    &:last-child {
        border-bottom: none;

        &::before {
            display: none;
        }
    }

    &:hover {
        background: linear-gradient(
            135deg,
            rgba(59, 130, 246, 0.02) 0%,
            rgba(14, 165, 233, 0.02) 100%
        );
        border-radius: 12px;
        padding-left: 12px;
        padding-right: 12px;
        transform: translateX(4px);
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.05);
    }
}

.activity-icon {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.9);
    border: 2px solid rgba(59, 130, 246, 0.2);
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
    flex-shrink: 0;
    margin-top: 2px;
    position: relative;
    z-index: 2;

    // 科技感发光效果
    &::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        border-radius: 50%;
        background: linear-gradient(
            135deg,
            rgba(59, 130, 246, 0.2) 0%,
            rgba(14, 165, 233, 0.1) 100%
        );
        z-index: -1;
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .activity-item:hover &::before {
        opacity: 1;
    }
}

.activity-content {
    flex: 1;
    min-width: 0;
}

.activity-header {
    display: flex;
    align-items: center;
    gap: 4px;
    margin-bottom: 4px;
    font-size: 14px;
    line-height: 1.4;
}

.activity-action {
    color: #64748b;
    font-weight: 500;
}

.activity-task {
    color: #1e40af;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 200px;
    padding: 2px 8px;
    background: rgba(59, 130, 246, 0.05);
    border-radius: 6px;
    border: 1px solid rgba(59, 130, 246, 0.1);
}

.activity-time {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: #64748b;

    .q-icon {
        color: #0ea5e9;
    }
}

.activity-link {
    flex-shrink: 0;
    opacity: 0;
    transition: opacity 0.2s ease;

    .activity-item:hover & {
        opacity: 1;
    }
}

.load-more {
    padding: 16px 0;
    text-align: center;
    border-top: 1px solid #f0f0f0;
    margin-top: 8px;
}

// 响应式设计
@media (max-width: 768px) {
    .activity-item {
        gap: 8px;
        padding: 10px 0;
    }

    .activity-icon {
        width: 28px;
        height: 28px;
    }

    .activity-task {
        max-width: 150px;
    }

    .activity-link {
        opacity: 1; // 在移动设备上始终显示
    }
}
</style>

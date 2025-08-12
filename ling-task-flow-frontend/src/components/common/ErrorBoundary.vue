<!--
  ErrorBoundary.vue
  全局错误边界组件
  用于捕获和处理组件渲染错误
-->

<template>
    <div v-if="hasError" class="error-boundary">
        <q-card class="error-card">
            <q-card-section class="text-center q-pa-xl">
                <q-icon class="q-mb-md" color="negative" name="error_outline" size="80px" />
                <h5 class="text-h5 q-mt-none q-mb-md">{{ errorTitle }}</h5>
                <p class="text-body1 text-grey-7 q-mb-lg">{{ errorMessage }}</p>

                <!-- 错误详情（开发模式下显示） -->
                <q-expansion-item
                    v-if="showDetails && errorDetails"
                    class="q-mb-lg"
                    icon="bug_report"
                    label="错误详情"
                >
                    <q-card bordered flat>
                        <q-card-section>
                            <pre class="error-details">{{ errorDetails }}</pre>
                        </q-card-section>
                    </q-card>
                </q-expansion-item>

                <!-- 操作按钮 -->
                <div class="row justify-center q-gutter-md">
                    <q-btn color="primary" icon="refresh" label="重新加载" @click="handleReload" />
                    <q-btn color="grey-7" flat icon="home" label="返回首页" @click="handleGoHome" />
                    <q-btn
                        v-if="showReport"
                        color="orange"
                        flat
                        icon="bug_report"
                        label="报告问题"
                        @click="handleReportError"
                    />
                </div>
            </q-card-section>
        </q-card>
    </div>
    <slot v-else />
</template>

<script lang="ts" setup>
import { computed, onErrorCaptured, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';

interface Props {
    // 是否显示错误详情
    showDetails?: boolean;
    // 是否显示报告按钮
    showReport?: boolean;
    // 自定义错误标题
    title?: string;
    // 自定义错误消息
    message?: string;
}

const props = withDefaults(defineProps<Props>(), {
    showDetails: process.env.NODE_ENV === 'development',
    showReport: true,
    title: '',
    message: '',
});

const router = useRouter();
const $q = useQuasar();

const hasError = ref(false);
const error = ref<Error | null>(null);

// 计算属性
const errorTitle = computed(() => {
    if (props.title) return props.title;
    if (error.value?.name === 'ChunkLoadError') return '资源加载失败';
    if (error.value?.name === 'TypeError') return '类型错误';
    if (error.value?.name === 'ReferenceError') return '引用错误';
    return '页面出现错误';
});

const errorMessage = computed(() => {
    if (props.message) return props.message;
    if (error.value?.name === 'ChunkLoadError') {
        return '应用资源加载失败，这可能是由于网络问题或新版本发布导致的。请尝试刷新页面。';
    }
    return '很抱歉，页面遇到了一个意外错误。我们已经记录了这个问题，请尝试刷新页面或返回首页。';
});

const errorDetails = computed(() => {
    if (!error.value) return '';
    return `${error.value.name}: ${error.value.message}\n\n堆栈跟踪:\n${error.value.stack}`;
});

// 错误捕获
onErrorCaptured((err: Error) => {
    console.error('ErrorBoundary caught error:', err);
    error.value = err;
    hasError.value = true;

    // 记录错误到监控系统（如果有的话）
    logError(err);

    return false; // 阻止错误继续向上传播
});

// 错误记录函数
function logError(err: Error) {
    // 这里可以集成错误监控服务，如 Sentry
    console.error('Error logged:', {
        name: err.name,
        message: err.message,
        stack: err.stack,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
    });
}

// 事件处理
function handleReload() {
    hasError.value = false;
    error.value = null;
    window.location.reload();
}

function handleGoHome() {
    hasError.value = false;
    error.value = null;
    void router.push('/');
}

function handleReportError() {
    const errorInfo = {
        name: error.value?.name || 'Unknown',
        message: error.value?.message || 'No message',
        stack: error.value?.stack || 'No stack trace',
        timestamp: new Date().toISOString(),
        url: window.location.href,
        userAgent: navigator.userAgent,
    };

    // 可以在这里打开反馈表单或发送错误报告
    $q.dialog({
        title: '错误报告',
        message: '感谢您报告这个问题！错误信息已被记录，我们会尽快修复。',
        ok: '确定',
    });

    // 示例：发送到错误收集服务
    console.log('Error report:', errorInfo);
}

// 暴露方法给父组件
defineExpose({
    reset: () => {
        hasError.value = false;
        error.value = null;
    },
    triggerError: (err: Error) => {
        error.value = err;
        hasError.value = true;
    },
});
</script>

<style lang="scss" scoped>
.error-boundary {
    min-height: 400px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
}

.error-card {
    max-width: 600px;
    width: 100%;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.error-details {
    font-family: 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.4;
    color: #666;
    background: #f5f5f5;
    padding: 1rem;
    border-radius: 4px;
    overflow-x: auto;
    max-height: 200px;
    overflow-y: auto;
}

// 暗色主题适配
.body--dark {
    .error-details {
        background: #2d2d2d;
        color: #ccc;
    }
}

// 响应式设计
@media (max-width: 600px) {
    .error-boundary {
        padding: 1rem;
    }

    .error-card {
        .q-card-section {
            padding: 1.5rem 1rem;
        }
    }
}
</style>

<!--
  ErrorNotification.vue
  全局错误通知组件
  用于显示各种类型的错误提示
-->

<template>
    <!-- 网络状态提示 -->
    <q-banner
        v-if="!isOnline"
        class="bg-warning text-white network-banner"
        dense
    >
        <template #avatar>
            <q-icon name="wifi_off" />
        </template>
        网络连接已断开，请检查您的网络设置
        <template #action>
            <q-btn
                flat
                label="重试"
                @click="checkConnection"
            />
        </template>
    </q-banner>

    <!-- 错误提示横幅 -->
    <q-banner
        v-if="globalError"
        :class="errorBannerClass"
        dense
    >
        <template #avatar>
            <q-icon :name="errorIcon" />
        </template>
        {{ globalError.message }}
        <template #action>
            <q-btn
                flat
                icon="close"
                @click="clearError"
            />
            <q-btn
                v-if="globalError.retryable"
                flat
                label="重试"
                @click="retryAction"
            />
        </template>
    </q-banner>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useQuasar } from 'quasar'

interface ErrorInfo {
    type: 'network' | 'api' | 'validation' | 'permission' | 'system'
    message: string
    retryable?: boolean
    retryAction?: (() => void) | undefined
    details?: string
}

const $q = useQuasar()

// 状态管理
const isOnline = ref(navigator.onLine)
const globalError = ref<ErrorInfo | null>(null)

// 计算属性
const errorBannerClass = computed(() => {
    if (!globalError.value) return ''

    const baseClass = 'text-white error-banner'
    switch (globalError.value.type) {
        case 'network':
            return `${baseClass} bg-orange`
        case 'api':
            return `${baseClass} bg-negative`
        case 'validation':
            return `${baseClass} bg-warning text-dark`
        case 'permission':
            return `${baseClass} bg-red-8`
        case 'system':
            return `${baseClass} bg-purple`
        default:
            return `${baseClass} bg-negative`
    }
})

const errorIcon = computed(() => {
    if (!globalError.value) return 'error'

    switch (globalError.value.type) {
        case 'network':
            return 'wifi_off'
        case 'api':
            return 'cloud_off'
        case 'validation':
            return 'warning'
        case 'permission':
            return 'lock'
        case 'system':
            return 'bug_report'
        default:
            return 'error'
    }
})

// 网络状态监听
function handleOnline() {
    isOnline.value = true
    if (globalError.value?.type === 'network') {
        clearError()
    }
}

function handleOffline() {
    isOnline.value = false
}

function checkConnection() {
    // 尝试发送一个简单的请求来检查网络连接
    fetch('/api/health', { method: 'HEAD' })
        .then(() => {
            isOnline.value = true
        })
        .catch(() => {
            isOnline.value = false
        })
}

// 错误处理方法
function showError(error: ErrorInfo) {
    globalError.value = error

    // 根据错误类型显示不同的通知
    switch (error.type) {
        case 'network':
            $q.notify({
                type: 'negative',
                message: error.message,
                icon: 'wifi_off',
                position: 'top',
                timeout: 0,
                actions: [
                    { label: '重试', color: 'white', handler: checkConnection },
                    { label: '关闭', color: 'white', handler: () => {} }
                ]
            })
            break
        case 'api':
            $q.notify({
                type: 'negative',
                message: error.message,
                icon: 'cloud_off',
                position: 'top',
                timeout: 5000,
                ...(error.retryable && error.retryAction ? {
                    actions: [
                        { label: '重试', color: 'white', handler: error.retryAction }
                    ]
                } : {})
            })
            break
        case 'validation':
            $q.notify({
                type: 'warning',
                message: error.message,
                icon: 'warning',
                position: 'top',
                timeout: 4000
            })
            break
        case 'permission':
            $q.notify({
                type: 'negative',
                message: error.message,
                icon: 'lock',
                position: 'center',
                timeout: 0,
                actions: [
                    { label: '了解', color: 'white', handler: () => {} }
                ]
            })
            break
        case 'system':
            $q.notify({
                type: 'negative',
                message: error.message,
                icon: 'bug_report',
                position: 'top',
                timeout: 0,
                actions: [
                    { label: '刷新页面', color: 'white', handler: () => window.location.reload() },
                    { label: '关闭', color: 'white', handler: () => {} }
                ]
            })
            break
    }
}

function clearError() {
    globalError.value = null
}

function retryAction() {
    if (globalError.value?.retryAction) {
        globalError.value.retryAction()
        clearError()
    }
}

// 生命周期
onMounted(() => {
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
})

onUnmounted(() => {
    window.removeEventListener('online', handleOnline)
    window.removeEventListener('offline', handleOffline)
})

// 暴露方法
defineExpose({
    showError,
    clearError,
    showNetworkError: (message: string, retryAction?: () => void) => {
        showError({
            type: 'network',
            message,
            retryable: !!retryAction,
            ...(retryAction ? { retryAction } : {})
        })
    },
    showApiError: (message: string, retryAction?: () => void) => {
        showError({
            type: 'api',
            message,
            retryable: !!retryAction,
            ...(retryAction ? { retryAction } : {})
        })
    },
    showValidationError: (message: string) => {
        showError({
            type: 'validation',
            message
        })
    },
    showPermissionError: (message: string) => {
        showError({
            type: 'permission',
            message
        })
    },
    showSystemError: (message: string) => {
        showError({
            type: 'system',
            message
        })
    }
})
</script>

<style lang="scss" scoped>
.network-banner,
.error-banner {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 9999;
    border-radius: 0;
}

.network-banner {
    top: 0;
}

.error-banner {
    top: auto;
    bottom: 0;
}

// 响应式设计
@media (max-width: 600px) {
    .network-banner,
    .error-banner {
        .q-banner__content {
            font-size: 14px;
        }
    }
}
</style>

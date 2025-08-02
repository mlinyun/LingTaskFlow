<template>
    <div class="login-page">
        <!-- 背景动效 -->
        <div class="background-animation">
            <div class="floating-shapes">
                <div class="shape shape-1"></div>
                <div class="shape shape-2"></div>
                <div class="shape shape-3"></div>
                <div class="shape shape-4"></div>
                <div class="shape shape-5"></div>
            </div>
        </div>

        <!-- 主容器 -->
        <div class="login-container">
            <!-- 左侧信息区域 -->
            <div class="info-section">
                <div class="brand-section">
                    <div class="brand-logo">
                        <q-icon name="psychology" size="4rem" color="white" />
                    </div>
                    <h1 class="brand-title">凌云智能任务管理平台</h1>
                    <p class="brand-subtitle">LingCloud Intelligence Task Management Platform</p>
                </div>

                <div class="features-list">
                    <div class="feature-item">
                        <q-icon name="auto_awesome" size="24px" color="white" />
                        <span>AI 智能任务规划</span>
                    </div>
                    <div class="feature-item">
                        <q-icon name="dashboard" size="24px" color="white" />
                        <span>实时数据仪表板</span>
                    </div>
                    <div class="feature-item">
                        <q-icon name="cloud_sync" size="24px" color="white" />
                        <span>云端同步协作</span>
                    </div>
                    <div class="feature-item">
                        <q-icon name="security" size="24px" color="white" />
                        <span>企业级安全保障</span>
                    </div>
                </div>
            </div>

            <!-- 右侧登录表单 -->
            <div class="form-section">
                <div class="form-container">
                    <div class="form-header">
                        <h2>欢迎回来</h2>
                        <p>登录您的账户以继续使用</p>
                    </div>

                    <q-form @submit="handleLogin" class="login-form">
                        <div class="input-group">
                            <q-input
                                v-model="loginForm.username"
                                label="用户名 / 邮箱"
                                outlined
                                dense
                                color="primary"
                                :rules="[val => !!val || '请输入用户名或邮箱']"
                                :loading="authStore.loading"
                                class="modern-input"
                            >
                                <template v-slot:prepend>
                                    <q-icon name="person" color="grey-6" />
                                </template>
                            </q-input>
                        </div>

                        <div class="input-group">
                            <q-input
                                v-model="loginForm.password"
                                :type="showPassword ? 'text' : 'password'"
                                label="密码"
                                outlined
                                dense
                                color="primary"
                                :rules="[val => !!val || '请输入密码']"
                                :loading="authStore.loading"
                                class="modern-input"
                            >
                                <template v-slot:prepend>
                                    <q-icon name="lock" color="grey-6" />
                                </template>
                                <template v-slot:append>
                                    <q-btn
                                        flat
                                        dense
                                        round
                                        :icon="showPassword ? 'visibility_off' : 'visibility'"
                                        color="grey-6"
                                        @click="showPassword = !showPassword"
                                    />
                                </template>
                            </q-input>
                        </div>

                        <div class="form-options">
                            <q-checkbox
                                v-model="rememberMe"
                                label="记住我"
                                color="primary"
                                size="sm"
                            />
                            <q-btn
                                flat
                                dense
                                color="primary"
                                label="忘记密码？"
                                class="forgot-password"
                                @click="$q.notify({ type: 'info', message: '功能开发中...' })"
                            />
                        </div>

                        <q-btn
                            type="submit"
                            color="primary"
                            class="login-btn"
                            size="lg"
                            :loading="authStore.loading"
                            label="登录"
                            no-caps
                            unelevated
                        />

                        <div class="signup-link">
                            <span>还没有账户？</span>
                            <q-btn
                                flat
                                dense
                                color="primary"
                                label="立即注册"
                                @click="goToRegister"
                                no-caps
                            />
                        </div>
                    </q-form>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from 'src/stores/auth';
import { useQuasar } from 'quasar';
import type { LoginCredentials } from 'src/types';

const router = useRouter();
const authStore = useAuthStore();
const $q = useQuasar();

// 表单数据
const loginForm = ref<LoginCredentials>({
    username: '',
    password: '',
});

const showPassword = ref(false);
const rememberMe = ref(false);

// 登录处理
const handleLogin = async () => {
    try {
        const credentials = {
            ...loginForm.value,
            remember_me: rememberMe.value,
        };

        const result = await authStore.login(credentials);

        if (result.success) {
            $q.notify({
                type: 'positive',
                message: result.message || '登录成功！',
                position: 'top',
            });

            await router.push('/tasks');
        } else {
            $q.notify({
                type: 'negative',
                message: result.message || '登录失败',
                position: 'top',
            });
        }
    } catch (error) {
        console.error('登录失败:', error);
        $q.notify({
            type: 'negative',
            message: '登录失败，请检查网络连接',
            position: 'top',
        });
    }
};

// 跳转到注册页面
const goToRegister = async () => {
    await router.push('/register');
};
</script>

<style scoped lang="scss">
.login-page {
    min-height: 100vh;
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
}

.background-animation {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;

    .floating-shapes {
        position: relative;
        width: 100%;
        height: 100%;

        .shape {
            position: absolute;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            animation: float 6s ease-in-out infinite;

            &.shape-1 {
                width: 80px;
                height: 80px;
                top: 20%;
                left: 10%;
                animation-delay: 0s;
            }

            &.shape-2 {
                width: 120px;
                height: 120px;
                top: 60%;
                left: 80%;
                animation-delay: 2s;
            }

            &.shape-3 {
                width: 60px;
                height: 60px;
                top: 80%;
                left: 20%;
                animation-delay: 4s;
            }

            &.shape-4 {
                width: 100px;
                height: 100px;
                top: 10%;
                left: 70%;
                animation-delay: 1s;
            }

            &.shape-5 {
                width: 40px;
                height: 40px;
                top: 40%;
                left: 5%;
                animation-delay: 3s;
            }
        }
    }
}

@keyframes float {
    0%,
    100% {
        transform: translateY(0px) translateX(0px);
    }
    50% {
        transform: translateY(-20px) translateX(10px);
    }
}

.login-container {
    display: flex;
    min-height: 100vh;
    position: relative;
    z-index: 1;
}

.info-section {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 2rem;
    color: white;

    .brand-section {
        text-align: center;
        margin-bottom: 3rem;

        .brand-logo {
            margin-bottom: 1rem;
            opacity: 0.9;
        }

        .brand-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            background: linear-gradient(45deg, #fff, #e0e7ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .brand-subtitle {
            font-size: 1rem;
            opacity: 0.8;
            font-weight: 300;
            letter-spacing: 1px;
        }
    }

    .features-list {
        max-width: 300px;

        .feature-item {
            display: flex;
            align-items: center;
            margin-bottom: 1.5rem;
            padding: 0.75rem;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);

            .q-icon {
                margin-right: 1rem;
            }

            span {
                font-weight: 500;
            }
        }
    }
}

.form-section {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(20px);
    border-left: 1px solid rgba(255, 255, 255, 0.2);
}

.form-container {
    width: 100%;
    max-width: 400px;
    padding: 2.5rem;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
}

.form-header {
    text-align: center;
    margin-bottom: 2rem;

    h2 {
        font-size: 1.875rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }

    p {
        color: #6b7280;
        font-size: 0.875rem;
    }
}

.login-form {
    .input-group {
        margin-bottom: 0.25rem;

        :deep(.modern-input) {
            .q-field__control {
                border-radius: 12px;
                border: 2px solid #e5e7eb;
                background: white;

                &:hover {
                    border-color: #d1d5db;
                }
            }

            &.q-field--focused .q-field__control {
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }

            .q-field__label {
                font-weight: 500;
                color: #6b7280;
            }
        }
    }

    .form-options {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;

        .forgot-password {
            font-size: 0.875rem;
            padding: 0;
        }
    }

    .login-btn {
        width: 100%;
        height: 48px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 1.5rem;
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);

        &:hover {
            background: linear-gradient(135deg, #2563eb, #1e40af);
        }
    }

    .signup-link {
        text-align: center;
        color: #6b7280;
        font-size: 0.875rem;

        span {
            margin-right: 0.5rem;
        }
    }
}

// 响应式设计
@media (max-width: 768px) {
    .login-container {
        flex-direction: column;
    }

    .info-section {
        display: none;
    }

    .form-section {
        background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
        border: none;
    }

    .form-container {
        margin: 1rem;
        padding: 2rem;
    }
}
</style>

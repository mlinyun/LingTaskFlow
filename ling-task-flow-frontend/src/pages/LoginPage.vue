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
                        <q-icon color="white" name="psychology" size="4rem" />
                    </div>
                    <h1 class="brand-title">凌云智能任务管理平台</h1>
                    <p class="brand-subtitle">LingCloud Intelligence Task Management Platform</p>
                </div>

                <div class="features-list">
                    <div class="feature-item">
                        <q-icon color="white" name="auto_awesome" size="24px" />
                        <span>AI 智能任务规划</span>
                    </div>
                    <div class="feature-item">
                        <q-icon color="white" name="dashboard" size="24px" />
                        <span>实时数据仪表板</span>
                    </div>
                    <div class="feature-item">
                        <q-icon color="white" name="cloud_sync" size="24px" />
                        <span>云端同步协作</span>
                    </div>
                    <div class="feature-item">
                        <q-icon color="white" name="security" size="24px" />
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

                    <q-form class="futuristic-form" @submit="handleLogin">
                        <!-- 表单标题装饰 -->
                        <div class="form-title-section">
                            <div class="title-line"></div>
                            <span class="title-text">用户认证</span>
                            <div class="title-line"></div>
                        </div>

                        <!-- 输入字段容器 -->
                        <div class="input-fields-container">
                            <div class="input-field-wrapper">
                                <div class="field-glow"></div>
                                <q-input
                                    v-model="loginForm.username"
                                    :loading="authStore.loading"
                                    :rules="[val => !!val || '请输入用户名或邮箱']"
                                    class="cyber-input"
                                    color="primary"
                                    dense
                                    hide-bottom-space
                                    label="用户名 / 邮箱"
                                    outlined
                                >
                                    <template v-slot:prepend>
                                        <div class="input-icon-wrapper">
                                            <q-icon name="person" />
                                            <div class="icon-pulse"></div>
                                        </div>
                                    </template>
                                </q-input>
                                <div class="field-border-animation"></div>
                            </div>

                            <div class="input-field-wrapper">
                                <div class="field-glow"></div>
                                <q-input
                                    v-model="loginForm.password"
                                    :loading="authStore.loading"
                                    :rules="[val => !!val || '请输入密码']"
                                    :type="showPassword ? 'text' : 'password'"
                                    class="cyber-input"
                                    color="primary"
                                    dense
                                    hide-bottom-space
                                    label="密码"
                                    outlined
                                >
                                    <template v-slot:prepend>
                                        <div class="input-icon-wrapper">
                                            <q-icon name="lock" />
                                            <div class="icon-pulse"></div>
                                        </div>
                                    </template>
                                    <template v-slot:append>
                                        <q-btn
                                            :icon="showPassword ? 'visibility_off' : 'visibility'"
                                            class="visibility-toggle"
                                            dense
                                            flat
                                            round
                                            @click="showPassword = !showPassword"
                                        />
                                    </template>
                                </q-input>
                                <div class="field-border-animation"></div>
                            </div>
                        </div>

                        <!-- 表单选项 -->
                        <div class="form-options-futuristic">
                            <q-checkbox
                                v-model="rememberMe"
                                class="cyber-checkbox"
                                color="primary"
                                label="记住我"
                                size="sm"
                            />
                            <q-btn
                                class="forgot-password-link"
                                color="primary"
                                dense
                                flat
                                label="忘记密码？"
                                @click="$q.notify({ type: 'info', message: '功能开发中...' })"
                            />
                        </div>

                        <!-- 登录按钮 -->
                        <div class="submit-button-container">
                            <q-btn
                                :loading="authStore.loading"
                                class="cyber-submit-btn"
                                no-caps
                                size="lg"
                                type="submit"
                                unelevated
                            >
                                <div class="btn-glow"></div>
                                <div class="btn-text">
                                    <span>启动系统</span>
                                    <q-icon class="btn-icon" name="login" size="20px" />
                                </div>
                                <div class="btn-circuit-pattern">
                                    <div class="circuit-line circuit-1"></div>
                                    <div class="circuit-line circuit-2"></div>
                                    <div class="circuit-line circuit-3"></div>
                                </div>
                            </q-btn>
                        </div>

                        <!-- 分割线 -->
                        <div class="form-divider">
                            <div class="divider-line"></div>
                            <div class="divider-text">
                                <span>或</span>
                                <div class="text-glow"></div>
                            </div>
                            <div class="divider-line"></div>
                        </div>

                        <!-- 注册链接 -->
                        <div class="register-link-container">
                            <div class="link-backdrop"></div>
                            <span class="link-text">还没有账户？</span>
                            <q-btn
                                class="register-link-btn"
                                color="primary"
                                dense
                                flat
                                label="立即注册"
                                no-caps
                                @click="goToRegister"
                            >
                                <div class="link-glow"></div>
                            </q-btn>
                        </div>
                    </q-form>
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
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
            // 显示友好的登录成功提示
            $q.notify({
                type: 'positive',
                message: result.message || '登录成功，欢迎回来！',
                position: 'top',
                timeout: 2000,
                actions: [
                    {
                        icon: 'close',
                        color: 'white',
                        size: 'sm',
                        round: true,
                    },
                ],
            });

            await router.push('/');
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

<style lang="scss" scoped>
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
    max-width: 360px;
    padding: 1.8rem;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 16px;
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
}

.form-header {
    text-align: center;
    margin-bottom: 1.5rem;

    h2 {
        font-size: 1.625rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.25rem;
    }

    p {
        color: #6b7280;
        font-size: 0.8rem;
    }
}

.futuristic-form {
    position: relative;
    padding: 0;

    // 表单标题装饰
    .form-title-section {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
        position: relative;

        .title-line {
            flex: 1;
            height: 1px;
            background: linear-gradient(90deg, transparent 0%, #3b82f6 50%, transparent 100%);
            position: relative;

            &::after {
                content: '';
                position: absolute;
                top: -1px;
                left: 0;
                right: 0;
                height: 3px;
                background: linear-gradient(
                    90deg,
                    transparent 0%,
                    rgba(59, 130, 246, 0.3) 50%,
                    transparent 100%
                );
                filter: blur(1px);
            }
        }

        .title-text {
            margin: 0 1.5rem;
            font-size: 0.875rem;
            font-weight: 600;
            color: #3b82f6;
            text-transform: uppercase;
            letter-spacing: 2px;
            white-space: nowrap;
            position: relative;

            &::before {
                content: '';
                position: absolute;
                top: -8px;
                left: -8px;
                right: -8px;
                bottom: -8px;
                background: radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%);
                border-radius: 8px;
                z-index: -1;
            }
        }
    }

    // 输入字段容器
    .input-fields-container {
        margin-bottom: 1.25rem;

        .input-field-wrapper {
            position: relative;
            margin-bottom: 1rem;

            .field-glow {
                position: absolute;
                top: -2px;
                left: -2px;
                right: -2px;
                bottom: -2px;
                background: linear-gradient(45deg, #3b82f6, #8b5cf6, #06b6d4, #3b82f6);
                background-size: 400% 400%;
                border-radius: 14px;
                opacity: 0;
                transition: opacity 0.3s ease;
                animation: gradientShift 3s ease infinite;
                z-index: -1;
            }

            &:focus-within .field-glow {
                opacity: 0.6;
            }

            .field-border-animation {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                border-radius: 12px;
                pointer-events: none;
                z-index: 10;

                &::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    border-radius: inherit;
                    padding: 1px;
                    background: linear-gradient(45deg, transparent, #3b82f6, transparent);
                    mask:
                        linear-gradient(#fff 0 0) content-box,
                        linear-gradient(#fff 0 0);
                    mask-composite: exclude;
                    opacity: 0;
                    transition: opacity 0.3s ease;
                }
            }

            &:focus-within .field-border-animation::before {
                opacity: 1;
            }
        }
    }

    // 科技感输入框样式
    :deep(.cyber-input) {
        .q-field__control {
            height: 48px;
            min-height: 48px;
            border-radius: 10px;
            border: 2px solid rgba(59, 130, 246, 0.2);
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            position: relative;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

            &::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                border-radius: inherit;
                background: linear-gradient(
                    135deg,
                    rgba(59, 130, 246, 0.05),
                    rgba(139, 92, 246, 0.05)
                );
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            &:hover {
                border-color: rgba(59, 130, 246, 0.4);
                box-shadow: 0 0 20px rgba(59, 130, 246, 0.1);

                &::before {
                    opacity: 1;
                }
            }
        }

        &.q-field--focused .q-field__control {
            border-color: #3b82f6;
            box-shadow:
                0 0 0 3px rgba(59, 130, 246, 0.1),
                0 0 30px rgba(59, 130, 246, 0.2),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);

            &::before {
                opacity: 1;
            }
        }

        // 输入框图标容器
        .input-icon-wrapper {
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 24px;
            height: 24px;

            .q-icon {
                color: #6b7280;
                transition: all 0.3s ease;
                z-index: 2;
            }

            .icon-pulse {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                border-radius: 50%;
                background: radial-gradient(circle, rgba(59, 130, 246, 0.2) 0%, transparent 70%);
                opacity: 0;
                transform: scale(0.8);
                transition: all 0.3s ease;
                z-index: 1;
            }
        }

        &.q-field--focused .input-icon-wrapper {
            .q-icon {
                color: #3b82f6;
                transform: scale(1.1);
            }

            .icon-pulse {
                opacity: 1;
                transform: scale(1.2);
                animation: iconPulse 2s ease-in-out infinite;
            }
        }

        // 标签样式
        .q-field__label {
            font-weight: 500;
            color: #6b7280;
            font-size: 14px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        &.q-field--focused .q-field__label,
        &.q-field--float .q-field__label {
            color: #3b82f6;
            font-weight: 600;
            font-size: 12px;
            text-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
        }

        // 输入框内容
        .q-field__native,
        .q-field__input {
            font-size: 15px;
            font-weight: 500;
            color: #1f2937;
            transition: all 0.3s ease;
        }

        // 可见性切换按钮
        .visibility-toggle {
            color: #6b7280;
            transition: all 0.3s ease;

            &:hover {
                color: #3b82f6;
                background: rgba(59, 130, 246, 0.1);
                transform: scale(1.1);
            }
        }
    }

    // 表单选项区域
    .form-options-futuristic {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding: 0 0.5rem;

        :deep(.cyber-checkbox) {
            // 完全重置所有Quasar默认样式
            all: unset !important;
            display: inline-flex !important;
            align-items: center !important;
            gap: 6px !important;
            cursor: pointer !important;

            // 重置所有子元素的定位
            * {
                position: static !important;
                margin: 0 !important;
                padding: 0 !important;
            }

            .q-checkbox__inner {
                display: inline-flex !important;
                align-items: center !important;
                position: static !important;
                font-size: 0.875rem !important;
            }

            .q-checkbox__bg {
                display: inline-block !important;
                width: 16px !important;
                height: 16px !important;
                border: 2px solid rgba(0, 198, 251, 0.3) !important;
                border-radius: 4px !important;
                position: static !important;
                transition: all 0.3s ease !important;
                flex-shrink: 0 !important;
            }

            .q-checkbox__svg {
                width: 16px !important;
                height: 16px !important;
                position: static !important;
                display: block !important;
            }

            .q-checkbox__label {
                display: inline-block !important;
                font-size: 0.8rem !important;
                font-weight: 500 !important;
                color: #6b7280 !important;
                line-height: 1.2 !important;
                position: static !important;
                vertical-align: middle !important;
            }

            // 悬停状态
            &:hover {
                .q-checkbox__bg {
                    border-color: #00c6fb !important;
                    box-shadow: 0 0 8px rgba(0, 198, 251, 0.2) !important;
                }
            }

            &:before,
            &:after,
            *:before,
            *:after {
                display: none !important;
            }
        }

        .forgot-password-link {
            font-size: 0.875rem;
            font-weight: 500;
            color: #6b7280;
            transition: all 0.3s ease;
            position: relative;

            &::after {
                content: '';
                position: absolute;
                bottom: -2px;
                left: 0;
                right: 0;
                height: 1px;
                background: linear-gradient(90deg, transparent, #3b82f6, transparent);
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            &:hover {
                color: #3b82f6;

                &::after {
                    opacity: 1;
                }
            }
        }
    }

    // 提交按钮容器
    .submit-button-container {
        margin-bottom: 1.25rem;
        position: relative;

        .cyber-submit-btn {
            width: 100%;
            height: 48px;
            border-radius: 10px;
            position: relative;
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 50%, #1d4ed8 100%);
            color: white;
            font-weight: 600;
            font-size: 15px;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

            &::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(
                    90deg,
                    transparent,
                    rgba(255, 255, 255, 0.4),
                    transparent
                );
                transition: left 0.5s ease;
            }

            .btn-glow {
                position: absolute;
                top: -2px;
                left: -2px;
                right: -2px;
                bottom: -2px;
                background: linear-gradient(45deg, #3b82f6, #8b5cf6, #06b6d4, #3b82f6);
                background-size: 400% 400%;
                border-radius: 14px;
                opacity: 0;
                transition: opacity 0.3s ease;
                animation: gradientShift 3s ease infinite;
                z-index: -1;
            }

            .btn-text {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                position: relative;
                z-index: 2;

                .btn-icon {
                    transition: transform 0.3s ease;
                }
            }

            .btn-circuit-pattern {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                opacity: 0;
                transition: opacity 0.3s ease;

                .circuit-line {
                    position: absolute;
                    background: rgba(255, 255, 255, 0.3);

                    &.circuit-1 {
                        top: 20%;
                        left: 10%;
                        width: 30%;
                        height: 1px;
                        animation: circuitFlow1 2s ease-in-out infinite;
                    }

                    &.circuit-2 {
                        top: 50%;
                        right: 15%;
                        width: 25%;
                        height: 1px;
                        animation: circuitFlow2 2s ease-in-out infinite 0.5s;
                    }

                    &.circuit-3 {
                        bottom: 20%;
                        left: 20%;
                        width: 40%;
                        height: 1px;
                        animation: circuitFlow3 2s ease-in-out infinite 1s;
                    }
                }
            }

            &:hover {
                transform: translateY(-2px);
                box-shadow:
                    0 10px 25px rgba(59, 130, 246, 0.3),
                    0 0 50px rgba(59, 130, 246, 0.2);

                &::before {
                    left: 100%;
                }

                .btn-glow {
                    opacity: 1;
                }

                .btn-text .btn-icon {
                    transform: scale(1.2) rotate(5deg);
                }

                .btn-circuit-pattern {
                    opacity: 1;
                }
            }

            &:active {
                transform: translateY(0);
            }
        }
    }

    // 分割线
    .form-divider {
        display: flex;
        align-items: center;

        .divider-line {
            flex: 1;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(107, 114, 128, 0.3), transparent);
        }

        .divider-text {
            position: relative;
            margin: 0 1.5rem;

            span {
                font-size: 0.875rem;
                color: #6b7280;
                font-weight: 500;
                position: relative;
                z-index: 2;
            }

            .text-glow {
                position: absolute;
                top: -8px;
                left: -8px;
                right: -8px;
                bottom: -8px;
                background: radial-gradient(circle, rgba(107, 114, 128, 0.1) 0%, transparent 70%);
                border-radius: 50%;
                z-index: 1;
            }
        }
    }

    // 注册链接容器
    .register-link-container {
        text-align: center;
        position: relative;
        padding: 0.75rem;
        border-radius: 6px;

        .link-backdrop {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(139, 92, 246, 0.05));
            border-radius: inherit;
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        &:hover .link-backdrop {
            opacity: 1;
        }

        .link-text {
            color: #6b7280;
            font-size: 0.875rem;
            margin-right: 0.5rem;
            font-weight: 500;
        }

        .register-link-btn {
            position: relative;
            font-weight: 600;
            color: #3b82f6;

            .link-glow {
                position: absolute;
                top: -4px;
                left: -4px;
                right: -4px;
                bottom: -4px;
                background: radial-gradient(circle, rgba(59, 130, 246, 0.2) 0%, transparent 70%);
                border-radius: 6px;
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            &:hover .link-glow {
                opacity: 1;
            }
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

    // 移动端表单优化
    .futuristic-form {
        .input-fields-container .input-field-wrapper {
            margin-bottom: 1.2rem;
        }

        .submit-button-container .cyber-submit-btn {
            height: 52px;
        }
    }
}

// 科技感动画效果
@keyframes gradientShift {
    0% {
        background-position: 0% 50%;
    }
    50% {
        background-position: 100% 50%;
    }
    100% {
        background-position: 0% 50%;
    }
}

@keyframes iconPulse {
    0%,
    100% {
        opacity: 0.3;
        transform: scale(1.2);
    }
    50% {
        opacity: 0.8;
        transform: scale(1.5);
    }
}

@keyframes circuitFlow1 {
    0% {
        opacity: 0;
        transform: translateX(-100%);
    }
    50% {
        opacity: 1;
        transform: translateX(0);
    }
    100% {
        opacity: 0;
        transform: translateX(100%);
    }
}

@keyframes circuitFlow2 {
    0% {
        opacity: 0;
        transform: translateX(100%);
    }
    50% {
        opacity: 1;
        transform: translateX(0);
    }
    100% {
        opacity: 0;
        transform: translateX(-100%);
    }
}

@keyframes circuitFlow3 {
    0% {
        opacity: 0;
        transform: translateX(-50%);
    }
    50% {
        opacity: 1;
        transform: translateX(0);
    }
    100% {
        opacity: 0;
        transform: translateX(50%);
    }
}
</style>

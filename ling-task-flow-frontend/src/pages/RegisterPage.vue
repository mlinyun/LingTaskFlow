<template>
    <div class="register-page">
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
        <div class="register-container">
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
                        <q-icon name="speed" size="24px" color="white" />
                        <span>快速上手，零学习成本</span>
                    </div>
                    <div class="feature-item">
                        <q-icon name="group" size="24px" color="white" />
                        <span>团队协作，提升效率</span>
                    </div>
                    <div class="feature-item">
                        <q-icon name="insights" size="24px" color="white" />
                        <span>智能分析，决策支持</span>
                    </div>
                    <div class="feature-item">
                        <q-icon name="verified" size="24px" color="white" />
                        <span>数据安全，值得信赖</span>
                    </div>
                </div>
            </div>

            <!-- 右侧注册表单 -->
            <div class="form-section">
                <div class="form-container">
                    <div class="form-header">
                        <h2>创建账户</h2>
                        <p>加入凌云平台，开启高效工作之旅</p>
                    </div>

                    <q-form @submit="handleRegister" class="register-form">
                        <div class="input-group">
                            <q-input
                                v-model="registerForm.username"
                                label="用户名"
                                outlined
                                dense
                                color="primary"
                                :rules="[
                                    val => !!val || '请输入用户名',
                                    val => val.length >= 3 || '用户名至少3个字符',
                                    val => val.length <= 20 || '用户名不能超过20个字符',
                                ]"
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
                                v-model="registerForm.email"
                                label="邮箱地址"
                                type="email"
                                outlined
                                dense
                                color="primary"
                                :rules="[
                                    val => !!val || '请输入邮箱',
                                    val => isValidEmail(val) || '请输入有效的邮箱地址',
                                ]"
                                :loading="authStore.loading"
                                class="modern-input"
                            >
                                <template v-slot:prepend>
                                    <q-icon name="email" color="grey-6" />
                                </template>
                            </q-input>
                        </div>

                        <div class="input-group">
                            <q-input
                                v-model="registerForm.password"
                                :type="showPassword ? 'text' : 'password'"
                                label="密码"
                                outlined
                                dense
                                color="primary"
                                :rules="[
                                    val => !!val || '请输入密码',
                                    val => val.length >= 8 || '密码至少8个字符',
                                    val =>
                                        /(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(val) ||
                                        '密码需包含大小写字母和数字',
                                ]"
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

                        <div class="input-group">
                            <q-input
                                v-model="registerForm.password_confirm"
                                :type="showPassword ? 'text' : 'password'"
                                label="确认密码"
                                outlined
                                dense
                                color="primary"
                                :rules="[
                                    val => !!val || '请确认密码',
                                    val => val === registerForm.password || '两次输入的密码不一致',
                                ]"
                                :loading="authStore.loading"
                                class="modern-input"
                            >
                                <template v-slot:prepend>
                                    <q-icon name="lock_reset" color="grey-6" />
                                </template>
                            </q-input>
                        </div>

                        <div class="form-options">
                            <q-checkbox v-model="agreeTerms" color="primary" size="sm">
                                <span class="terms-text">
                                    我已阅读并同意
                                    <q-btn
                                        flat
                                        dense
                                        color="primary"
                                        label="《用户协议》"
                                        class="terms-link"
                                        @click="
                                            $q.notify({ type: 'info', message: '功能开发中...' })
                                        "
                                    />
                                    和
                                    <q-btn
                                        flat
                                        dense
                                        color="primary"
                                        label="《隐私政策》"
                                        class="terms-link"
                                        @click="
                                            $q.notify({ type: 'info', message: '功能开发中...' })
                                        "
                                    />
                                </span>
                            </q-checkbox>
                        </div>

                        <q-btn
                            type="submit"
                            color="primary"
                            class="register-btn"
                            size="lg"
                            :loading="authStore.loading"
                            :disable="!agreeTerms"
                            label="创建账户"
                            no-caps
                            unelevated
                        />

                        <div class="login-link">
                            <span>已有账户？</span>
                            <q-btn
                                flat
                                dense
                                color="primary"
                                label="立即登录"
                                @click="goToLogin"
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
import type { RegisterData } from 'src/types';

const router = useRouter();
const authStore = useAuthStore();
const $q = useQuasar();

// 表单数据
const registerForm = ref<RegisterData>({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
});

const showPassword = ref(false);
const agreeTerms = ref(false);

// 邮箱验证函数
const isValidEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
};

// 注册处理
const handleRegister = async () => {
    try {
        await authStore.register(registerForm.value);

        $q.notify({
            type: 'positive',
            message: '注册成功！请使用您的账户登录',
            position: 'top',
            timeout: 3000,
        });

        // 注册成功后跳转到登录页面
        await router.push('/login');
    } catch (error) {
        console.error('注册失败:', error);
        $q.notify({
            type: 'negative',
            message: '注册失败，请检查输入信息',
            position: 'top',
        });
    }
};

// 跳转到登录页面
const goToLogin = async () => {
    await router.push('/login');
};
</script>

<style scoped lang="scss">
.register-page {
    min-height: 100vh;
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, #00c6fb 0%, #005bea 100%);
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
                width: 90px;
                height: 90px;
                top: 15%;
                left: 15%;
                animation-delay: 0s;
            }

            &.shape-2 {
                width: 110px;
                height: 110px;
                top: 65%;
                left: 85%;
                animation-delay: 1.5s;
            }

            &.shape-3 {
                width: 70px;
                height: 70px;
                top: 85%;
                left: 15%;
                animation-delay: 3s;
            }

            &.shape-4 {
                width: 95px;
                height: 95px;
                top: 5%;
                left: 75%;
                animation-delay: 4.5s;
            }

            &.shape-5 {
                width: 50px;
                height: 50px;
                top: 45%;
                left: 8%;
                animation-delay: 2s;
            }
        }
    }
}

@keyframes float {
    0%,
    100% {
        transform: translateY(0px) translateX(0px) rotate(0deg);
    }
    50% {
        transform: translateY(-25px) translateX(15px) rotate(180deg);
    }
}

.register-container {
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
            background: linear-gradient(45deg, #fff, #e0f2fe);
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
        max-width: 320px;

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
    max-width: 420px;
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

.register-form {
    .input-group {
        margin-bottom: 1.5rem;

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
                border-color: #0ea5e9;
                box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
            }

            .q-field__label {
                font-weight: 500;
                color: #6b7280;
            }
        }
    }

    .form-options {
        margin-bottom: 2rem;

        .terms-text {
            font-size: 0.875rem;
            color: #6b7280;
            line-height: 1.5;

            .terms-link {
                font-size: 0.875rem;
                padding: 0;
                min-height: auto;
                text-decoration: underline;
            }
        }
    }

    .register-btn {
        width: 100%;
        height: 48px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 1.5rem;
        background: linear-gradient(135deg, #0ea5e9, #0284c7);

        &:hover:not(.q-btn--disable) {
            background: linear-gradient(135deg, #0284c7, #0369a1);
        }

        &.q-btn--disable {
            opacity: 0.5;
        }
    }

    .login-link {
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
    .register-container {
        flex-direction: column;
    }

    .info-section {
        display: none;
    }

    .form-section {
        background: linear-gradient(135deg, #00c6fb 0%, #005bea 100%);
        border: none;
    }

    .form-container {
        margin: 1rem;
        padding: 2rem;
    }
}
</style>

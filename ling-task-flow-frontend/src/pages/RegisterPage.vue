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
                        <q-icon color="white" name="psychology" size="4rem" />
                    </div>
                    <h1 class="brand-title">凌云智能任务管理平台</h1>
                    <p class="brand-subtitle">LingCloud Intelligence Task Management Platform</p>
                </div>

                <div class="features-list">
                    <div class="feature-item">
                        <q-icon color="white" name="speed" size="24px" />
                        <span>快速上手，零学习成本</span>
                    </div>
                    <div class="feature-item">
                        <q-icon color="white" name="group" size="24px" />
                        <span>团队协作，提升效率</span>
                    </div>
                    <div class="feature-item">
                        <q-icon color="white" name="insights" size="24px" />
                        <span>智能分析，决策支持</span>
                    </div>
                    <div class="feature-item">
                        <q-icon color="white" name="verified" size="24px" />
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

                    <q-form class="futuristic-form" @submit="handleRegister">
                        <!-- 表单标题装饰 -->
                        <div class="form-title-section">
                            <div class="title-line"></div>
                            <span class="title-text">账户创建</span>
                            <div class="title-line"></div>
                        </div>

                        <!-- 输入字段容器 -->
                        <div class="input-fields-container">
                            <div class="input-field-wrapper">
                                <div class="field-glow"></div>
                                <q-input
                                    v-model="registerForm.username"
                                    :loading="authStore.loading"
                                    :rules="[
                                        val => !!val || '请输入用户名',
                                        val => val.length >= 3 || '用户名至少3个字符',
                                        val => val.length <= 20 || '用户名不能超过20个字符',
                                    ]"
                                    class="cyber-input"
                                    color="primary"
                                    dense
                                    hide-bottom-space
                                    label="用户名"
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
                                    v-model="registerForm.email"
                                    :loading="authStore.loading"
                                    :rules="[
                                        val => !!val || '请输入邮箱',
                                        val => isValidEmail(val) || '请输入有效的邮箱地址',
                                    ]"
                                    class="cyber-input"
                                    color="primary"
                                    dense
                                    hide-bottom-space
                                    label="邮箱地址"
                                    outlined
                                    type="email"
                                >
                                    <template v-slot:prepend>
                                        <div class="input-icon-wrapper">
                                            <q-icon name="email" />
                                            <div class="icon-pulse"></div>
                                        </div>
                                    </template>
                                </q-input>
                                <div class="field-border-animation"></div>
                            </div>

                            <div class="input-field-wrapper">
                                <div class="field-glow"></div>
                                <q-input
                                    v-model="registerForm.password"
                                    :loading="authStore.loading"
                                    :rules="[
                                        val => !!val || '请输入密码',
                                        val => val.length >= 8 || '密码至少8个字符',
                                        val =>
                                            /(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(val) ||
                                            '密码需包含大小写字母和数字',
                                    ]"
                                    :type="showPassword ? 'text' : 'password'"
                                    class="cyber-input"
                                    color="primary"
                                    dense
                                    hide-bottom-space
                                    label="密码"
                                    outlined
                                    @blur="isPasswordFocused = false"
                                    @focus="isPasswordFocused = true"
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

                            <div class="input-field-wrapper">
                                <div class="field-glow"></div>
                                <q-input
                                    v-model="registerForm.password_confirm"
                                    :loading="authStore.loading"
                                    :rules="[
                                        val => !!val || '请确认密码',
                                        val =>
                                            val === registerForm.password || '两次输入的密码不一致',
                                    ]"
                                    :type="showPassword ? 'text' : 'password'"
                                    class="cyber-input"
                                    color="primary"
                                    dense
                                    hide-bottom-space
                                    label="确认密码"
                                    outlined
                                >
                                    <template v-slot:prepend>
                                        <div class="input-icon-wrapper">
                                            <q-icon name="lock_reset" />
                                            <div class="icon-pulse"></div>
                                        </div>
                                    </template>
                                </q-input>
                                <div class="field-border-animation"></div>
                            </div>
                        </div>

                        <!-- 密码强度指示器 -->
                        <div
                            v-if="registerForm.password && isPasswordFocused"
                            class="password-strength-indicator"
                        >
                            <div class="strength-line-container">
                                <div class="strength-line">
                                    <div
                                        :class="getPasswordStrengthClass()"
                                        :style="{ width: `${(passwordStrength / 5) * 100}%` }"
                                        class="strength-progress"
                                    ></div>
                                </div>
                                <span class="strength-text">{{ getPasswordStrengthText() }}</span>
                            </div>
                        </div>

                        <!-- 服务条款 -->
                        <div class="terms-container">
                            <q-checkbox
                                v-model="agreeTerms"
                                class="cyber-checkbox"
                                color="primary"
                                size="sm"
                            />
                            <div class="terms-text">
                                我已阅读并同意
                                <q-btn
                                    class="terms-link"
                                    color="primary"
                                    dense
                                    flat
                                    label="服务条款"
                                    @click="$q.notify({ type: 'info', message: '服务条款详情...' })"
                                />
                                和
                                <q-btn
                                    class="terms-link"
                                    color="primary"
                                    dense
                                    flat
                                    label="隐私政策"
                                    @click="$q.notify({ type: 'info', message: '隐私政策详情...' })"
                                />
                            </div>
                        </div>

                        <!-- 注册按钮 -->
                        <div class="submit-button-container">
                            <q-btn
                                :disable="!agreeTerms"
                                :loading="authStore.loading"
                                class="cyber-submit-btn"
                                no-caps
                                size="lg"
                                type="submit"
                                unelevated
                            >
                                <div class="btn-glow"></div>
                                <div class="btn-text">
                                    <span>创建账户</span>
                                    <q-icon class="btn-icon" name="account_circle" size="18px" />
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

                        <!-- 登录链接 -->
                        <div class="login-link-container">
                            <div class="link-backdrop"></div>
                            <span class="link-text">已有账户？</span>
                            <q-btn
                                class="login-link-btn"
                                color="primary"
                                dense
                                flat
                                label="立即登录"
                                no-caps
                                @click="goToLogin"
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
import { computed, ref } from 'vue';
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
const isPasswordFocused = ref(false);

// 增强的密码强度计算
const passwordStrength = computed(() => {
    const password = registerForm.value.password;
    if (!password) return 0;

    let score = 0;

    // 长度评分 (0-25分)
    if (password.length >= 8) score += 5;
    if (password.length >= 12) score += 5;
    if (password.length >= 16) score += 5;
    if (password.length >= 20) score += 5;
    if (password.length >= 24) score += 5;

    // 字符类型评分 (0-40分)
    if (/[a-z]/.test(password)) score += 8; // 小写字母
    if (/[A-Z]/.test(password)) score += 8; // 大写字母
    if (/[0-9]/.test(password)) score += 8; // 数字
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score += 8; // 特殊字符
    if (/[^\w\s]/.test(password)) score += 8; // 其他符号

    // 复杂度评分 (0-25分)
    const uniqueChars = new Set(password).size;
    if (uniqueChars >= 8) score += 5; // 字符多样性
    if (uniqueChars >= 12) score += 5;
    if (uniqueChars >= 16) score += 5;

    // 模式检测 (0-10分)
    if (!/(.)\1{2,}/.test(password)) score += 5; // 无连续重复字符
    if (
        !/012|123|234|345|456|567|678|789|890/.test(password) &&
        !/abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz/i.test(
            password,
        )
    ) {
        score += 5; // 无连续序列
    }

    // 将总分(0-100)映射到强度等级(0-5)
    if (score >= 80) return 5; // 非常强
    if (score >= 65) return 4; // 强
    if (score >= 45) return 3; // 中等
    if (score >= 25) return 2; // 弱
    if (score > 0) return 1; // 很弱
    return 0;
});

// 密码强度文本
const getPasswordStrengthText = () => {
    switch (passwordStrength.value) {
        case 0:
            return '';
        case 1:
            return '很弱';
        case 2:
            return '弱';
        case 3:
            return '中等';
        case 4:
            return '强';
        case 5:
            return '很强';
        default:
            return '';
    }
};

// 密码强度样式类
const getPasswordStrengthClass = () => {
    switch (passwordStrength.value) {
        case 0:
        case 1:
            return 'very-weak';
        case 2:
            return 'weak';
        case 3:
            return 'medium';
        case 4:
            return 'strong';
        case 5:
            return 'very-strong';
        default:
            return '';
    }
};

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

<style lang="scss" scoped>
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
    max-width: 380px;
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
            background: linear-gradient(90deg, transparent 0%, #00c6fb 50%, transparent 100%);
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
                    rgba(0, 198, 251, 0.3) 50%,
                    transparent 100%
                );
                filter: blur(1px);
            }
        }

        .title-text {
            margin: 0 1.5rem;
            font-size: 0.875rem;
            font-weight: 600;
            color: #00c6fb;
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
                background: radial-gradient(circle, rgba(0, 198, 251, 0.1) 0%, transparent 70%);
                border-radius: 8px;
                z-index: -1;
            }
        }
    }

    // 输入字段容器
    .input-fields-container {
        margin-bottom: 1rem;

        .input-field-wrapper {
            position: relative;
            margin-bottom: 0.875rem;

            .field-glow {
                position: absolute;
                top: -2px;
                left: -2px;
                right: -2px;
                bottom: -2px;
                background: linear-gradient(45deg, #00c6fb, #005bea, #8b5cf6, #00c6fb);
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
                    background: linear-gradient(45deg, transparent, #00c6fb, transparent);
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

    // 密码强度指示器
    .password-strength-indicator {
        margin-bottom: 0.75rem;

        .strength-line-container {
            display: flex;
            align-items: center;
            gap: 0.75rem;

            .strength-line {
                flex: 1;
                height: 2px;
                background: rgba(107, 114, 128, 0.15);
                border-radius: 1px;
                position: relative;
                overflow: hidden;

                .strength-progress {
                    position: absolute;
                    top: 0;
                    left: 0;
                    height: 100%;
                    border-radius: inherit;
                    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
                    transform-origin: left;

                    &.very-weak {
                        background: linear-gradient(90deg, #dc2626, #ef4444);
                        box-shadow: 0 0 3px rgba(220, 38, 38, 0.4);
                    }

                    &.weak {
                        background: linear-gradient(90deg, #ea580c, #f97316);
                        box-shadow: 0 0 3px rgba(234, 88, 12, 0.4);
                    }

                    &.medium {
                        background: linear-gradient(90deg, #f59e0b, #fbbf24);
                        box-shadow: 0 0 4px rgba(245, 158, 11, 0.3);
                    }

                    &.strong {
                        background: linear-gradient(90deg, #10b981, #34d399);
                        box-shadow: 0 0 4px rgba(16, 185, 129, 0.3);
                    }

                    &.very-strong {
                        background: linear-gradient(90deg, #00c6fb, #005bea);
                        box-shadow: 0 0 6px rgba(0, 198, 251, 0.4);
                    }
                }
            }

            .strength-text {
                font-size: 0.75rem;
                font-weight: 500;
                color: #6b7280;
                white-space: nowrap;
                min-width: 2rem;
                text-align: right;
            }
        }
    }

    // 服务条款容器
    .terms-container {
        margin-bottom: 1rem;
        padding: 0.75rem;
        background: rgba(0, 198, 251, 0.02);
        border-radius: 6px;
        border: 1px solid rgba(0, 198, 251, 0.06);
        display: flex;
        align-items: center;
        position: relative;
        transition: all 0.3s ease;

        &:hover {
            background: rgba(0, 198, 251, 0.04);
            border-color: rgba(0, 198, 251, 0.12);
        }

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
                font-size: 1.25rem !important;
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

        .terms-text {
            font-size: 0.8rem;
            color: #6b7280;
            line-height: 1.2;
            flex: 1;

            .terms-link {
                padding: 0 2px;
                min-height: auto;
                font-size: 0.8rem;
                font-weight: 500;
                color: #00c6fb;
                text-decoration: underline;
                transition: all 0.3s ease;
                border-radius: 2px;

                &:hover {
                    color: #005bea;
                    text-shadow: 0 0 6px rgba(0, 198, 251, 0.25);
                    background: rgba(0, 198, 251, 0.05);
                }
            }
        }
    }

    // 科技感输入框样式
    :deep(.cyber-input) {
        .q-field__control {
            height: 48px;
            min-height: 48px;
            border-radius: 10px;
            border: 2px solid rgba(0, 198, 251, 0.2);
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
                    rgba(0, 198, 251, 0.05),
                    rgba(0, 91, 234, 0.05)
                );
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            &:hover {
                border-color: rgba(0, 198, 251, 0.4);
                box-shadow: 0 0 20px rgba(0, 198, 251, 0.1);

                &::before {
                    opacity: 1;
                }
            }
        }

        &.q-field--focused .q-field__control {
            border-color: #00c6fb;
            box-shadow:
                0 0 0 3px rgba(0, 198, 251, 0.1),
                0 0 30px rgba(0, 198, 251, 0.2),
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
                background: radial-gradient(circle, rgba(0, 198, 251, 0.2) 0%, transparent 70%);
                opacity: 0;
                transform: scale(0.8);
                transition: all 0.3s ease;
                z-index: 1;
            }
        }

        &.q-field--focused .input-icon-wrapper {
            .q-icon {
                color: #00c6fb;
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
            color: #00c6fb;
            font-weight: 600;
            font-size: 12px;
            text-shadow: 0 0 10px rgba(0, 198, 251, 0.3);
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
                color: #00c6fb;
                background: rgba(0, 198, 251, 0.1);
                transform: scale(1.1);
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
            background: linear-gradient(135deg, #00c6fb 0%, #005bea 50%, #0d47a1 100%);
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
                background: linear-gradient(45deg, #00c6fb, #005bea, #8b5cf6, #00c6fb);
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

            &:hover:not([disabled]) {
                transform: translateY(-2px);
                box-shadow:
                    0 10px 25px rgba(0, 198, 251, 0.3),
                    0 0 50px rgba(0, 198, 251, 0.2);

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

            &[disabled] {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }

            &:active:not([disabled]) {
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

    // 登录链接容器
    .login-link-container {
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
            background: linear-gradient(135deg, rgba(0, 198, 251, 0.05), rgba(0, 91, 234, 0.05));
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

        .login-link-btn {
            position: relative;
            font-weight: 600;
            color: #00c6fb;

            .link-glow {
                position: absolute;
                top: -4px;
                left: -4px;
                right: -4px;
                bottom: -4px;
                background: radial-gradient(circle, rgba(0, 198, 251, 0.2) 0%, transparent 70%);
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
.input-group {
    margin-bottom: 1.5rem;

    :deep(.modern-input) {
        .q-field__control {
            height: 48px;
            min-height: 48px;
            border-radius: 12px;
            border: 2px solid #e5e7eb;
            background: white;
            padding: 0 16px;
            display: flex;
            align-items: center;

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

        // 确保输入框内容对齐
        .q-field__native,
        .q-field__input {
            padding: 0;
            line-height: 48px;
            min-height: 48px;
            display: flex;
            align-items: center;
        }

        // 确保前缀和后缀图标对齐
        .q-field__marginal {
            height: 48px;
            display: flex;
            align-items: center;
        }

        // 确保标签浮动时的对齐
        .q-field__control-container {
            padding: 0;
            min-height: 48px;
            display: flex;
            align-items: center;
        }

        // 确保前缀后缀按钮对齐
        .q-field__prepend,
        .q-field__append {
            height: 48px;
            display: flex;
            align-items: center;
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

// 动画关键帧
@keyframes gradientShift {
    0%,
    100% {
        background-position: 0% 50%;
    }
    50% {
        background-position: 100% 50%;
    }
}

@keyframes iconPulse {
    0%,
    100% {
        transform: scale(1.2);
        opacity: 1;
    }
    50% {
        transform: scale(1.4);
        opacity: 0.8;
    }
}

@keyframes circuitFlow1 {
    0% {
        opacity: 0;
        transform: translateX(-20px);
    }
    50% {
        opacity: 1;
        transform: translateX(0);
    }
    100% {
        opacity: 0;
        transform: translateX(20px);
    }
}

@keyframes circuitFlow2 {
    0% {
        opacity: 0;
        transform: translateX(20px);
    }
    50% {
        opacity: 1;
        transform: translateX(0);
    }
    100% {
        opacity: 0;
        transform: translateX(-20px);
    }
}

@keyframes circuitFlow3 {
    0% {
        opacity: 0;
        transform: translateX(-15px);
    }
    50% {
        opacity: 1;
        transform: translateX(0);
    }
    100% {
        opacity: 0;
        transform: translateX(15px);
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

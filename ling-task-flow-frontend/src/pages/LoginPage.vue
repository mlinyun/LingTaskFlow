<template>
    <div class="flex flex-center bg-gradient full-height">
        <div class="login-container">
            <q-card class="login-card">
                <q-card-section class="text-center q-pb-none">
                    <div class="logo-section">
                        <q-icon name="task" size="3rem" color="primary" class="q-mb-md" />
                        <h4 class="text-h4 q-ma-none text-weight-bold">LingTaskFlow</h4>
                        <p class="text-grey-6 q-mt-sm q-mb-none">智能任务管理平台</p>
                    </div>
                </q-card-section>

                <q-card-section>
                    <!-- 登录/注册切换标签 -->
                    <q-tabs
                        v-model="currentTab"
                        dense
                        class="text-grey"
                        active-color="primary"
                        indicator-color="primary"
                        align="justify"
                        narrow-indicator
                    >
                        <q-tab name="login" label="登录" />
                        <q-tab name="register" label="注册" />
                    </q-tabs>

                    <q-separator class="q-mt-md" />

                    <!-- 登录表单 -->
                    <q-tab-panels v-model="currentTab" animated>
                        <q-tab-panel name="login" class="q-px-none">
                            <q-form @submit="handleLogin" class="q-gutter-md q-mt-md">
                                <q-input
                                    v-model="loginForm.username"
                                    label="用户名或邮箱"
                                    outlined
                                    :rules="[val => !!val || '请输入用户名或邮箱']"
                                    prefix-icon="person"
                                    clearable
                                    :loading="authStore.loading"
                                >
                                    <template v-slot:prepend>
                                        <q-icon name="person" />
                                    </template>
                                </q-input>

                                <q-input
                                    v-model="loginForm.password"
                                    label="密码"
                                    :type="showPassword ? 'text' : 'password'"
                                    outlined
                                    :rules="[val => !!val || '请输入密码']"
                                    :loading="authStore.loading"
                                >
                                    <template v-slot:prepend>
                                        <q-icon name="lock" />
                                    </template>
                                    <template v-slot:append>
                                        <q-icon
                                            :name="showPassword ? 'visibility_off' : 'visibility'"
                                            class="cursor-pointer"
                                            @click="showPassword = !showPassword"
                                        />
                                    </template>
                                </q-input>

                                <div class="row justify-between items-center">
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
                                        class="text-caption"
                                        @click="$q.notify('功能开发中...')"
                                    />
                                </div>

                                <q-btn
                                    type="submit"
                                    color="primary"
                                    class="full-width"
                                    size="lg"
                                    :loading="authStore.loading"
                                    label="登录"
                                    no-caps
                                />
                            </q-form>
                        </q-tab-panel>

                        <!-- 注册表单 -->
                        <q-tab-panel name="register" class="q-px-none">
                            <q-form @submit="handleRegister" class="q-gutter-md q-mt-md">
                                <q-input
                                    v-model="registerForm.username"
                                    label="用户名"
                                    outlined
                                    :rules="[
                                        val => !!val || '请输入用户名',
                                        val => val.length >= 3 || '用户名至少3个字符',
                                    ]"
                                    :loading="authStore.loading"
                                >
                                    <template v-slot:prepend>
                                        <q-icon name="person" />
                                    </template>
                                </q-input>

                                <q-input
                                    v-model="registerForm.email"
                                    label="邮箱"
                                    type="email"
                                    outlined
                                    :rules="[
                                        val => !!val || '请输入邮箱',
                                        val => isValidEmail(val) || '请输入有效的邮箱地址',
                                    ]"
                                    :loading="authStore.loading"
                                >
                                    <template v-slot:prepend>
                                        <q-icon name="email" />
                                    </template>
                                </q-input>

                                <q-input
                                    v-model="registerForm.password"
                                    label="密码"
                                    :type="showPassword ? 'text' : 'password'"
                                    outlined
                                    :rules="[
                                        val => !!val || '请输入密码',
                                        val => val.length >= 6 || '密码至少6个字符',
                                    ]"
                                    :loading="authStore.loading"
                                >
                                    <template v-slot:prepend>
                                        <q-icon name="lock" />
                                    </template>
                                    <template v-slot:append>
                                        <q-icon
                                            :name="showPassword ? 'visibility_off' : 'visibility'"
                                            class="cursor-pointer"
                                            @click="showPassword = !showPassword"
                                        />
                                    </template>
                                </q-input>

                                <q-input
                                    v-model="registerForm.password_confirm"
                                    label="确认密码"
                                    :type="showPassword ? 'text' : 'password'"
                                    outlined
                                    :rules="[
                                        val => !!val || '请确认密码',
                                        val =>
                                            val === registerForm.password || '两次输入的密码不一致',
                                    ]"
                                    :loading="authStore.loading"
                                >
                                    <template v-slot:prepend>
                                        <q-icon name="lock" />
                                    </template>
                                </q-input>

                                <q-checkbox v-model="agreeTerms" color="primary" size="sm">
                                    <span class="text-caption">
                                        我已阅读并同意
                                        <q-btn
                                            flat
                                            dense
                                            color="primary"
                                            label="用户协议"
                                            class="text-caption q-pa-none"
                                            @click="$q.notify('功能开发中...')"
                                        />
                                        和
                                        <q-btn
                                            flat
                                            dense
                                            color="primary"
                                            label="隐私政策"
                                            class="text-caption q-pa-none"
                                            @click="$q.notify('功能开发中...')"
                                        />
                                    </span>
                                </q-checkbox>

                                <q-btn
                                    type="submit"
                                    color="primary"
                                    class="full-width"
                                    size="lg"
                                    :loading="authStore.loading"
                                    :disable="!agreeTerms"
                                    label="注册"
                                    no-caps
                                />
                            </q-form>
                        </q-tab-panel>
                    </q-tab-panels>
                </q-card-section>
            </q-card>

            <!-- 底部信息 -->
            <div class="footer-info text-center q-mt-lg">
                <p class="text-grey-5 text-caption">
                    © 2024 LingTaskFlow. 智能任务管理，让工作更高效。
                </p>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { useAuthStore } from 'stores/auth';

// 响应式数据
const currentTab = ref('login');
const showPassword = ref(false);
const rememberMe = ref(false);
const agreeTerms = ref(false);

// 表单数据
const loginForm = reactive({
    username: '',
    password: '',
});

const registerForm = reactive({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
});

// 依赖注入
const router = useRouter();
const $q = useQuasar();
const authStore = useAuthStore();

// 邮箱验证函数
const isValidEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
};

// 登录处理
const handleLogin = async () => {
    const result = await authStore.login(loginForm);

    if (result.success) {
        $q.notify({
            type: 'positive',
            message: result.message || '登录成功',
            position: 'top',
        });

        // 跳转到主页面
        void router.push('/');
    } else {
        $q.notify({
            type: 'negative',
            message: result.message,
            position: 'top',
        });
    }
};

// 注册处理
const handleRegister = async () => {
    const result = await authStore.register(registerForm);

    if (result.success) {
        $q.notify({
            type: 'positive',
            message: result.message || '注册成功',
            position: 'top',
        });

        // 跳转到主页面
        void router.push('/');
    } else {
        $q.notify({
            type: 'negative',
            message: result.message,
            position: 'top',
        });
    }
};
</script>

<style scoped>
.full-height {
    min-height: 100vh;
    height: 100vh;
}

.bg-gradient {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-container {
    width: 100%;
    max-width: 420px;
    padding: 20px;
}

.login-card {
    border-radius: 16px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-section {
    padding: 20px 0;
}

.footer-info {
    margin-top: 2rem;
}

/* 响应式设计 */
@media (max-width: 480px) {
    .login-container {
        padding: 10px;
    }

    .login-card {
        border-radius: 12px;
    }
}
</style>

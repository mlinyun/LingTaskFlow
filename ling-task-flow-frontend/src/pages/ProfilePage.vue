<template>
    <q-page class="profile-page">
        <!-- 页面头部组件 -->
        <PageHeader
            icon="account_circle"
            title-primary="个人资料"
            title-accent="管理中心"
            subtitle="管理您的个人信息和账户设置"
            :primary-action="{
                icon: isEditing ? 'save' : 'edit',
                label: isEditing ? '保存更改' : '编辑资料',
                loading: loading,
            }"
            :secondary-actions="[
                {
                    name: 'refresh',
                    icon: 'refresh',
                    tooltip: '刷新数据',
                    class: 'fullscreen-btn',
                },
                {
                    name: 'avatar',
                    icon: 'photo_camera',
                    tooltip: '更换头像',
                    class: 'download-btn',
                },
            ]"
            @primary-action="handlePrimaryAction"
            @secondary-action="handleSecondaryAction"
        />

        <!-- 主要内容区域 -->
        <div class="content-container">
            <!-- 加载状态 -->
            <LoadingState
                v-if="loading && !userInfo"
                variant="centered"
                message="加载个人信息..."
                spinner="gears"
                color="primary"
            />

            <!-- 个人资料内容 -->
            <div v-else class="profile-content">
                <!-- 左侧：头像和基本信息 -->
                <div class="profile-sidebar">
                    <!-- 新头像信息卡片 -->
                    <div class="identity-card">
                        <div class="identity-body">
                            <div class="avatar-wrap">
                                <q-avatar size="120px" class="avatar">
                                    <img
                                        v-if="userInfo?.profile?.avatar_url"
                                        :src="userInfo.profile.avatar_url"
                                        :alt="userInfo.username"
                                    />
                                    <q-icon
                                        v-else
                                        name="account_circle"
                                        size="120px"
                                        color="primary"
                                    />
                                </q-avatar>
                                <q-btn
                                    class="avatar-edit-btn"
                                    icon="photo_camera"
                                    round
                                    color="primary"
                                    size="sm"
                                    @click="openAvatarUpload"
                                >
                                    <q-tooltip>更换头像</q-tooltip>
                                </q-btn>
                            </div>

                            <div class="identity-info">
                                <h3 class="name">
                                    {{ userInfo?.profile?.nickname || userInfo?.username }}
                                </h3>

                                <div class="info-row">
                                    <q-icon name="email" size="16px" />
                                    <span class="info-text">{{ userInfo?.email }}</span>
                                </div>

                                <div class="info-row">
                                    <q-icon name="calendar_today" size="16px" />
                                    <span class="info-text"
                                        >加入于 {{ formatDate(userInfo?.date_joined) }}</span
                                    >
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 统计卡片 -->
                    <div class="stats-card">
                        <div class="card-header">
                            <h4>活动统计</h4>
                            <q-icon name="analytics" color="primary" />
                        </div>
                        <div class="stats-grid">
                            <div class="stat-item">
                                <div class="stat-value">
                                    {{ userInfo?.profile?.task_count || 0 }}
                                </div>
                                <div class="stat-label">总任务数</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">
                                    {{ userInfo?.profile?.completed_task_count || 0 }}
                                </div>
                                <div class="stat-label">已完成</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">{{ completionRate }}%</div>
                                <div class="stat-label">完成率</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">{{ activeDays }}</div>
                                <div class="stat-label">活跃天数</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 右侧：详细信息表单 -->
                <div class="profile-main">
                    <!-- 基本信息表单 -->
                    <div class="info-card">
                        <div class="card-header">
                            <h4>基本信息</h4>
                            <q-icon name="person" color="primary" />
                        </div>

                        <q-form class="info-form">
                            <div class="form-row">
                                <q-input
                                    v-model="formData.username"
                                    label="用户名"
                                    :readonly="!isEditing"
                                    :outlined="isEditing"
                                    :borderless="!isEditing"
                                    dense
                                    hide-bottom-space
                                    class="form-field"
                                    :rules="[val => !!val || '用户名不能为空']"
                                >
                                    <template v-slot:prepend>
                                        <q-icon name="account_circle" />
                                    </template>
                                </q-input>

                                <q-input
                                    v-model="formData.email"
                                    label="邮箱地址"
                                    type="email"
                                    :readonly="!isEditing"
                                    :outlined="isEditing"
                                    :borderless="!isEditing"
                                    dense
                                    hide-bottom-space
                                    class="form-field"
                                    :rules="[
                                        val => !!val || '邮箱不能为空',
                                        val => /.+@.+\..+/.test(val) || '请输入有效的邮箱地址',
                                    ]"
                                >
                                    <template v-slot:prepend>
                                        <q-icon name="email" />
                                    </template>
                                </q-input>
                            </div>

                            <div class="form-row">
                                <q-input
                                    v-model="formData.nickname"
                                    label="昵称"
                                    :readonly="!isEditing"
                                    :outlined="isEditing"
                                    :borderless="!isEditing"
                                    dense
                                    hide-bottom-space
                                    class="form-field"
                                >
                                    <template v-slot:prepend>
                                        <q-icon name="badge" />
                                    </template>
                                </q-input>

                                <q-input
                                    v-model="formData.phone"
                                    label="联系电话"
                                    :readonly="!isEditing"
                                    :outlined="isEditing"
                                    :borderless="!isEditing"
                                    dense
                                    hide-bottom-space
                                    class="form-field"
                                >
                                    <template v-slot:prepend>
                                        <q-icon name="phone" />
                                    </template>
                                </q-input>
                            </div>

                            <div class="form-row form-row--single">
                                <q-input
                                    v-model="formData.bio"
                                    label="个人简介"
                                    type="textarea"
                                    :readonly="!isEditing"
                                    :outlined="isEditing"
                                    :borderless="!isEditing"
                                    rows="3"
                                    dense
                                    hide-bottom-space
                                    class="form-field bio-field"
                                    maxlength="500"
                                    counter
                                >
                                    <template v-slot:prepend>
                                        <q-icon name="description" class="self-start q-mt-sm" />
                                    </template>
                                </q-input>
                            </div>
                        </q-form>
                    </div>

                    <!-- 安全设置 -->
                    <div class="security-card">
                        <div class="card-header">
                            <h4>安全设置</h4>
                            <q-icon name="security" color="primary" />
                        </div>

                        <div class="security-actions">
                            <q-btn
                                icon="lock"
                                label="修改密码"
                                outline
                                color="primary"
                                class="security-btn"
                                @click="openPasswordDialog"
                            />

                            <q-btn
                                icon="logout"
                                label="登出所有设备"
                                outline
                                color="negative"
                                class="security-btn"
                                @click="logoutAllDevices"
                            />
                        </div>

                        <div class="last-login" v-if="userInfo?.last_login">
                            <q-icon name="schedule" />
                            <span>上次登录：{{ formatDateTime(userInfo.last_login) }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 头像上传对话框 -->
        <q-dialog v-model="showAvatarDialog">
            <q-card class="avatar-upload-dialog">
                <q-card-section class="dialog-header">
                    <div class="text-h6">更换头像</div>
                    <q-btn icon="close" flat round dense v-close-popup />
                </q-card-section>

                <q-card-section>
                    <q-file
                        v-model="avatarFile"
                        accept="image/*"
                        max-file-size="5242880"
                        @rejected="onAvatarRejected"
                    >
                        <template v-slot:prepend>
                            <q-icon name="attach_file" />
                        </template>
                    </q-file>

                    <div v-if="avatarFile" class="avatar-preview">
                        <img :src="avatarPreview" alt="头像预览" />
                    </div>
                </q-card-section>

                <q-card-actions align="right">
                    <q-btn flat label="取消" v-close-popup />
                    <q-btn
                        color="primary"
                        label="上传"
                        :loading="uploadingAvatar"
                        :disable="!avatarFile"
                        @click="uploadAvatar"
                    />
                </q-card-actions>
            </q-card>
        </q-dialog>

        <!-- 修改密码对话框 -->
        <q-dialog v-model="showPasswordDialog">
            <q-card class="password-dialog">
                <q-card-section class="dialog-header">
                    <div class="header-left">
                        <q-avatar
                            size="32px"
                            class="header-icon"
                            color="primary"
                            text-color="white"
                        >
                            <q-icon name="lock" />
                        </q-avatar>
                        <div class="titles">
                            <div class="title">修改密码</div>
                            <div class="subtitle">为了账号安全，请使用强密码</div>
                        </div>
                    </div>
                    <q-btn icon="close" flat round dense v-close-popup />
                </q-card-section>

                <q-card-section>
                    <q-form @submit="changePassword">
                        <q-input
                            v-model="passwordForm.currentPassword"
                            label="当前密码"
                            :type="showCurrentPwd ? 'text' : 'password'"
                            dense
                            :rules="[val => !!val || '请输入当前密码']"
                            class="q-mb-md"
                        >
                            <template #prepend>
                                <q-icon name="vpn_key" />
                            </template>
                            <template #append>
                                <q-btn
                                    flat
                                    round
                                    dense
                                    :icon="showCurrentPwd ? 'visibility_off' : 'visibility'"
                                    @click="showCurrentPwd = !showCurrentPwd"
                                />
                            </template>
                        </q-input>

                        <q-input
                            v-model="passwordForm.newPassword"
                            label="新密码"
                            :type="showNewPwd ? 'text' : 'password'"
                            dense
                            :rules="[
                                val => !!val || '请输入新密码',
                                val => val.length >= 8 || '密码长度至少8位',
                            ]"
                            class="q-mb-xs"
                            @focus="isPwdFocused = true"
                            @blur="isPwdFocused = false"
                        >
                            <template #prepend>
                                <q-icon name="lock" />
                            </template>
                            <template #append>
                                <q-btn
                                    flat
                                    round
                                    dense
                                    :icon="showNewPwd ? 'visibility_off' : 'visibility'"
                                    @click="showNewPwd = !showNewPwd"
                                />
                            </template>
                        </q-input>

                        <!-- 密码强度提示（与注册页一致的算法） -->
                        <div
                            v-if="passwordForm.newPassword && isPwdFocused"
                            class="password-strength-inline q-mb-md"
                        >
                            <div class="strength-line">
                                <div
                                    class="strength-progress"
                                    :class="getStrengthClass()"
                                    :style="{ width: `${(passwordStrength / 5) * 100}%` }"
                                ></div>
                            </div>
                            <div class="strength-text">{{ getStrengthText() }}</div>
                        </div>

                        <q-input
                            v-model="passwordForm.confirmPassword"
                            label="确认新密码"
                            :type="showConfirmPwd ? 'text' : 'password'"
                            dense
                            :rules="[
                                val => !!val || '请确认新密码',
                                val => val === passwordForm.newPassword || '两次输入的密码不一致',
                            ]"
                        >
                            <template #prepend>
                                <q-icon name="check_circle" />
                            </template>
                            <template #append>
                                <q-btn
                                    flat
                                    round
                                    dense
                                    :icon="showConfirmPwd ? 'visibility_off' : 'visibility'"
                                    @click="showConfirmPwd = !showConfirmPwd"
                                />
                            </template>
                        </q-input>

                        <q-separator spaced />

                        <div class="password-policy">
                            <div class="policy-title">密码要求</div>
                            <div class="policy-list">
                                <div class="policy-item" :class="{ ok: passwordPolicy.len }">
                                    <q-icon
                                        :name="
                                            passwordPolicy.len
                                                ? 'check_circle'
                                                : 'radio_button_unchecked'
                                        "
                                    />
                                    至少 8 个字符
                                </div>
                                <div class="policy-item" :class="{ ok: passwordPolicy.upper }">
                                    <q-icon
                                        :name="
                                            passwordPolicy.upper
                                                ? 'check_circle'
                                                : 'radio_button_unchecked'
                                        "
                                    />
                                    包含大写字母 (A-Z)
                                </div>
                                <div class="policy-item" :class="{ ok: passwordPolicy.lower }">
                                    <q-icon
                                        :name="
                                            passwordPolicy.lower
                                                ? 'check_circle'
                                                : 'radio_button_unchecked'
                                        "
                                    />
                                    包含小写字母 (a-z)
                                </div>
                                <div class="policy-item" :class="{ ok: passwordPolicy.number }">
                                    <q-icon
                                        :name="
                                            passwordPolicy.number
                                                ? 'check_circle'
                                                : 'radio_button_unchecked'
                                        "
                                    />
                                    包含数字 (0-9)
                                </div>
                                <div class="policy-item" :class="{ ok: passwordPolicy.special }">
                                    <q-icon
                                        :name="
                                            passwordPolicy.special
                                                ? 'check_circle'
                                                : 'radio_button_unchecked'
                                        "
                                    />
                                    包含特殊字符
                                </div>
                                <div class="policy-item" :class="{ ok: passwordPolicy.match }">
                                    <q-icon
                                        :name="
                                            passwordPolicy.match
                                                ? 'check_circle'
                                                : 'radio_button_unchecked'
                                        "
                                    />
                                    两次输入一致
                                </div>
                            </div>
                        </div>
                    </q-form>
                </q-card-section>

                <q-card-actions align="right">
                    <q-btn flat label="取消" v-close-popup />
                    <q-btn
                        color="primary"
                        label="确认修改"
                        icon="check_circle"
                        :disable="!canSubmit"
                        :loading="changingPassword"
                        @click="changePassword"
                    />
                </q-card-actions>
            </q-card>
        </q-dialog>
    </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { useAuthStore } from 'src/stores/auth';
import PageHeader from 'src/components/common/PageHeader.vue';
import LoadingState from 'src/components/skeletons/LoadingState.vue';
import type { User } from 'src/types';
import { usePasswordStrength } from 'src/composables/usePasswordStrength';
import { useGlobalConfirm } from 'src/composables/useGlobalConfirm';
import {
    getUserProfile as apiGetUserProfile,
    updateUserProfile as apiUpdateUserProfile,
    uploadAvatar as apiUploadAvatar,
    changePassword as apiChangePassword,
    logoutAllDevices as apiLogoutAllDevices,
} from 'src/services/profile';

const $q = useQuasar();
const authStore = useAuthStore();
const confirmDialog = useGlobalConfirm();
const router = useRouter();

// 响应式数据
const loading = ref(false);
const isEditing = ref(false);
const userInfo = ref<User | null>(null);
const showAvatarDialog = ref(false);
const showPasswordDialog = ref(false);
const avatarFile = ref<File | null>(null);
const uploadingAvatar = ref(false);
const changingPassword = ref(false);
const isPwdFocused = ref(false);
const showCurrentPwd = ref(false);
const showNewPwd = ref(false);
const showConfirmPwd = ref(false);

// 表单数据
const formData = ref({
    username: '',
    email: '',
    nickname: '',
    phone: '',
    bio: '',
});

// 密码修改表单
const passwordForm = ref({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
});

// 密码规则与提交可用性
const passwordPolicy = computed(() => {
    const newPwd = passwordForm.value.newPassword || '';
    const confirmPwd = passwordForm.value.confirmPassword || '';
    return {
        len: newPwd.length >= 8,
        upper: /[A-Z]/.test(newPwd),
        lower: /[a-z]/.test(newPwd),
        number: /[0-9]/.test(newPwd),
        special: /[^A-Za-z0-9]/.test(newPwd),
        match: newPwd.length > 0 && confirmPwd === newPwd,
    };
});

const canSubmit = computed(() => {
    return (
        !!passwordForm.value.currentPassword &&
        passwordPolicy.value.len &&
        passwordPolicy.value.match
    );
});

// 集成密码强度计算（与注册页一致）
const { passwordStrength, getStrengthClass, getStrengthText } = usePasswordStrength(
    computed(() => passwordForm.value.newPassword),
);

// 已移除偏好设置选项数据

// 计算属性
const completionRate = computed(() => {
    if (!userInfo.value?.profile) return 0;
    const { task_count, completed_task_count } = userInfo.value.profile;
    return task_count > 0 ? Math.round((completed_task_count / task_count) * 100) : 0;
});

const activeDays = computed(() => {
    if (!userInfo.value?.date_joined) return 0;
    const joinDate = new Date(userInfo.value.date_joined);
    const today = new Date();
    const diffTime = Math.abs(today.getTime() - joinDate.getTime());
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
});

const avatarPreview = computed(() => {
    if (!avatarFile.value) return '';
    return URL.createObjectURL(avatarFile.value);
});

// 方法
const loadUserProfile = async () => {
    loading.value = true;
    try {
        // 确保auth store已经初始化
        authStore.initAuth();

        // 检查用户是否已登录
        if (!authStore.isAuthenticated) {
            console.warn('用户未登录，无法加载用户信息');
            // 如果有本地存储的用户信息，先使用本地数据
            if (authStore.user) {
                userInfo.value = authStore.user;
                loadFormData();
                console.info('使用本地缓存的用户信息');
            } else {
                $q.notify({
                    type: 'warning',
                    message: '请先登录以查看个人资料',
                    position: 'top',
                });
            }
            return;
        }

        console.log('正在从API加载用户信息...');
        // 从API获取最新的用户信息
        const userData = await apiGetUserProfile();
        userInfo.value = userData;

        // 同时更新auth store中的用户信息
        authStore.user = userData;

        if (userInfo.value) {
            loadFormData();
            console.log('用户信息加载成功');
        }
    } catch (error) {
        console.error('加载用户信息失败:', error);

        // 详细的错误信息
        let errorMessage = '加载用户信息失败';
        if (error instanceof Error) {
            errorMessage = error.message;
            console.error('错误详情:', {
                name: error.name,
                message: error.message,
                stack: error.stack,
            });
        }

        // 如果API调用失败，尝试使用本地缓存的用户信息
        if (authStore.user) {
            userInfo.value = authStore.user;
            loadFormData();
            console.warn('API调用失败，使用本地缓存的用户信息');
            $q.notify({
                type: 'warning',
                message: '使用缓存数据，某些信息可能不是最新的',
                position: 'top',
            });
        } else {
            $q.notify({
                type: 'negative',
                message: errorMessage,
                position: 'top',
            });
        }
    } finally {
        loading.value = false;
    }
};

const loadFormData = () => {
    if (!userInfo.value) return;

    formData.value = {
        username: userInfo.value.username || '',
        email: userInfo.value.email || '',
        nickname: userInfo.value.profile?.nickname || '',
        phone: userInfo.value.profile?.phone || '',
        bio: userInfo.value.profile?.bio || '',
    };
};

const handlePrimaryAction = async () => {
    if (isEditing.value) {
        await saveProfile();
    } else {
        isEditing.value = true;
    }
};

const handleSecondaryAction = (actionName: string) => {
    switch (actionName) {
        case 'refresh':
            loadUserProfile();
            break;
        case 'avatar':
            openAvatarUpload();
            break;
        default:
            console.log(`未知操作: ${actionName}`);
    }
};

const saveProfile = async () => {
    loading.value = true;
    try {
        console.log('开始保存个人信息...');
        console.log('表单数据:', formData.value);

        // 调用API保存用户信息
        const updatedUser = await apiUpdateUserProfile(formData.value);
        console.log('API调用成功，返回数据:', updatedUser);

        // 更新本地用户信息并写入本地缓存，避免后续从缓存读取旧数据
        userInfo.value = updatedUser;
        authStore.user = updatedUser;
        // 将最新用户信息持久化
        try {
            // 直接使用 Quasar LocalStorage，避免依赖 store 私有方法
            const { LocalStorage } = await import('quasar');
            LocalStorage.set('user_info', updatedUser);
        } catch (e) {
            // 忽略本地持久化失败
            console.warn('本地缓存写入失败:', e);
        }

        isEditing.value = false;
        $q.notify({
            type: 'positive',
            message: '个人信息保存成功',
            position: 'top',
        });

        console.log('个人信息保存成功');
    } catch (error) {
        console.error('保存失败，错误详情:', error);

        let errorMessage = '保存失败，请重试';
        if (error instanceof Error) {
            errorMessage = error.message;
            console.error('错误信息:', {
                name: error.name,
                message: error.message,
                stack: error.stack,
            });
        }

        $q.notify({
            type: 'negative',
            message: errorMessage,
            position: 'top',
        });
    } finally {
        loading.value = false;
    }
};

const openAvatarUpload = () => {
    showAvatarDialog.value = true;
};

const onAvatarRejected = () => {
    $q.notify({
        type: 'negative',
        message: '头像文件大小不能超过5MB',
        position: 'top',
    });
};

const uploadAvatar = async () => {
    if (!avatarFile.value) return;

    uploadingAvatar.value = true;
    try {
        // 调用API上传头像
        const avatarUrl = await apiUploadAvatar(avatarFile.value);

        // 更新用户头像URL
        if (userInfo.value?.profile) {
            userInfo.value.profile.avatar_url = avatarUrl;
        }

        // 同步更新auth store
        if (authStore.user?.profile) {
            authStore.user.profile.avatar_url = avatarUrl;
        }

        showAvatarDialog.value = false;
        avatarFile.value = null;
        $q.notify({
            type: 'positive',
            message: '头像上传成功',
            position: 'top',
        });
    } catch (error) {
        console.error('头像上传失败:', error);
        $q.notify({
            type: 'negative',
            message: '头像上传失败，请重试',
            position: 'top',
        });
    } finally {
        uploadingAvatar.value = false;
    }
};

const openPasswordDialog = () => {
    showPasswordDialog.value = true;
    passwordForm.value = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
    };
};

const changePassword = async () => {
    if (!canSubmit.value) {
        $q.notify({
            type: 'warning',
            message: '请按要求填写并确认新密码',
            position: 'top',
        });
        return;
    }
    changingPassword.value = true;
    try {
        // 调用API修改密码
        await apiChangePassword({
            current_password: passwordForm.value.currentPassword,
            new_password: passwordForm.value.newPassword,
            confirm_password: passwordForm.value.confirmPassword,
        });

        showPasswordDialog.value = false;
        passwordForm.value = {
            currentPassword: '',
            newPassword: '',
            confirmPassword: '',
        };

        $q.notify({
            type: 'positive',
            message: '密码修改成功，请重新登录',
            position: 'top',
        });

        // 清理当前登录状态并跳转到登录页
        await authStore.logout();
        await router.push('/login');
    } catch (error) {
        console.error('密码修改失败:', error);
        $q.notify({
            type: 'negative',
            message: '密码修改失败，请重试',
            position: 'top',
        });
    } finally {
        changingPassword.value = false;
    }
};

const logoutAllDevices = async () => {
    const confirmed = await confirmDialog.confirmWarning(
        '登出所有设备',
        '确定要在所有设备上退出登录吗？这将使您在其他设备上的登录失效。',
        {
            confirmText: '登出所有设备',
            confirmIcon: 'logout',
            persistent: true,
        },
    );

    if (!confirmed) return;

    try {
        confirmDialog.setLoading(true, '正在登出所有设备...');
        await apiLogoutAllDevices();
        confirmDialog.setLoading(false);

        $q.notify({
            type: 'positive',
            message: '已登出所有设备',
            position: 'top',
        });
    } catch (error) {
        console.error('操作失败:', error);
        confirmDialog.setLoading(false);
        $q.notify({
            type: 'negative',
            message: '操作失败，请重试',
            position: 'top',
        });
    }
};

const formatDate = (dateString: string | undefined): string => {
    if (!dateString) return '';
    try {
        return new Date(dateString).toLocaleDateString('zh-CN');
    } catch {
        return '';
    }
};

const formatDateTime = (dateString: string): string => {
    try {
        return new Date(dateString).toLocaleString('zh-CN');
    } catch {
        return '';
    }
};

// 生命周期
onMounted(() => {
    // 确保auth store已经初始化
    authStore.initAuth();
    loadUserProfile();
});
</script>

<style lang="scss" scoped>
.profile-page {
    background: #f8fafc;
    min-height: calc(100vh - 50px);
    padding: 1.5rem;

    @media (max-width: 768px) {
        padding: 1rem;
    }
}

.content-container {
    margin-top: 2rem;
}

.profile-content {
    display: grid;
    grid-template-columns: 350px 1fr;
    gap: 2rem;

    @media (max-width: 1200px) {
        grid-template-columns: 300px 1fr;
        gap: 1.5rem;
    }

    @media (max-width: 1024px) {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }
}

// 侧边栏样式
.profile-sidebar {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

/* 新的头像信息卡片样式 */
.identity-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
    border: 1px solid rgba(226, 232, 240, 0.8);
}

.identity-body {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
}

.avatar-wrap {
    position: relative;
}

.avatar-wrap .avatar {
    box-shadow: 0 8px 24px rgba(59, 130, 246, 0.15);
}

.avatar-wrap .avatar-edit-btn {
    position: absolute;
    bottom: 0;
    right: 0;
    transform: translate(15%, 15%);
    z-index: 2;
}

.identity-info {
    text-align: center;
}

.identity-info .name {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1e293b;
    margin: 0 0 0.25rem 0;
}

.identity-info .info-row {
    display: flex;
    align-items: center;
    gap: 8px;
    justify-content: center;
    color: #64748b;
    font-size: 0.95rem;
}

.identity-info .info-text {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 220px;
}

.stats-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
    border: 1px solid rgba(226, 232, 240, 0.8);

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e2e8f0;

        h4 {
            margin: 0;
            font-size: 1.125rem;
            font-weight: 600;
            color: #1e293b;
        }
    }

    .stats-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
    }

    .stat-item {
        text-align: center;
        padding: 1rem;
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(14, 165, 233, 0.03));
        border: 1px solid rgba(59, 130, 246, 0.1);

        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #3b82f6;
            margin-bottom: 0.25rem;
        }

        .stat-label {
            font-size: 0.875rem;
            color: #64748b;
        }
    }
}

// 主要内容样式
.profile-main {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.info-card,
.security-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
    border: 1px solid rgba(226, 232, 240, 0.8);

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e2e8f0;

        h4 {
            margin: 0;
            font-size: 1.125rem;
            font-weight: 600;
            color: #1e293b;
        }
    }
}

.info-form {
    .form-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin: 0 0 16px 0;

        @media (max-width: 768px) {
            grid-template-columns: 1fr;
        }
    }

    .form-field {
        margin: 0; /* 间距统一由父级 grid gap 控制 */
    }

    /* 单行时的修饰（如个人简介） */
    .form-row--single {
        grid-template-columns: 1fr;
        margin-bottom: 0; /* 最后一行不再额外留白 */
    }
}

.security-actions {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;

    .security-btn {
        flex: 1;

        @media (max-width: 768px) {
            flex: none;
            width: 100%;
        }
    }

    @media (max-width: 768px) {
        flex-direction: column;
    }
}

.last-login {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #64748b;
    font-size: 0.9rem;
    padding: 1rem;
    background: #f8fafc;
    border-radius: 8px;
}

// 对话框样式
.avatar-upload-dialog,
.password-dialog {
    min-width: 400px;

    .dialog-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #e2e8f0;
    }

    .header-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .header-icon {
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.25);
    }
    .titles {
        display: flex;
        flex-direction: column;
        .title {
            font-size: 1.125rem;
            font-weight: 600;
            color: #1e293b;
        }
        .subtitle {
            font-size: 12px;
            color: #64748b;
            margin-top: 2px;
        }
    }

    .avatar-preview {
        margin-top: 1rem;
        text-align: center;

        img {
            max-width: 200px;
            max-height: 200px;
            border-radius: 8px;
        }
    }
}

/* 密码强度条（紧凑版，沿用注册页算法与色彩） */
.password-strength-inline {
    display: flex;
    align-items: center;
    gap: 8px;
    .strength-line {
        flex: 1;
        height: 6px;
        background: #e2e8f0;
        border-radius: 6px;
        overflow: hidden;
    }
    .strength-progress {
        height: 100%;
        width: 0%;
        transition: width 0.3s ease;
        &.weak {
            background: #ef4444;
        }
        &.fair {
            background: #f59e0b;
        }
        &.medium {
            background: #3b82f6;
        }
        &.strong {
            background: #10b981;
        }
        &.very-strong {
            background: #14b8a6;
        }
    }
    .strength-text {
        min-width: 42px;
        font-size: 12px;
        color: #64748b;
        text-align: right;
    }
}

/* 密码规则说明块 */
.password-policy {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px;
    .policy-title {
        font-size: 12px;
        color: #475569;
        margin-bottom: 8px;
    }
    .policy-list {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 6px 12px;
    }
    .policy-item {
        display: flex;
        align-items: center;
        gap: 6px;
        color: #94a3b8;
        font-size: 12px;
        &.ok {
            color: #16a34a;
        }
        :deep(.q-icon) {
            font-size: 16px;
        }
    }
}

@media (max-width: 480px) {
    .password-policy {
        .policy-list {
            grid-template-columns: 1fr;
        }
    }
}

// 动画
@keyframes float {
    0%,
    100% {
        transform: translateY(0px) rotate(0deg);
        opacity: 0.7;
    }
    50% {
        transform: translateY(-8px) rotate(180deg);
        opacity: 1;
    }
}

// 响应式设计
@media (max-width: 480px) {
    .profile-page {
        padding: 0.75rem;
    }

    .avatar-card {
        padding: 1.5rem;
    }

    .stats-grid {
        grid-template-columns: 1fr;
    }

    .preference-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;

        .preference-control {
            margin-left: 0;
            width: 100%;
        }
    }
}
</style>

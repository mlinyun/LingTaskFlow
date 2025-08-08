/**
 * 个人资料相关API接口
 */
import { api } from '../boot/axios';
import { apiGet, apiPatch } from 'src/utils/api';
import type { User } from '../types';

interface ProfileUpdateData {
    // 用户基本信息
    username?: string;
    email?: string;
    first_name?: string;
    // 档案信息
    phone?: string;
    bio?: string;
    nickname?: string;
    timezone?: string;
    theme_preference?: string;
    language?: string;
    email_notifications?: boolean;
}

interface PasswordChangeData {
    current_password: string;
    new_password: string;
    confirm_password: string;
}

/**
 * 获取用户个人资料（拦截器已将响应data标准化为实际数据）
 */
export const getUserProfile = async (): Promise<User> => {
    const data = await apiGet<{ user: User }>('/auth/profile/');
    return data.user;
};

/**
 * 更新用户个人资料（返回完整的用户对象）
 */
export const updateUserProfile = async (profileData: ProfileUpdateData): Promise<User> => {
    const data = await apiPatch<{ user: User }>('/auth/profile/update/', profileData);
    return data.user;
};

/**
 * 上传用户头像（返回头像URL）
 */
export const uploadAvatar = async (file: File): Promise<string> => {
    const formData = new FormData();
    formData.append('avatar', file);

    const response = await api.post<{ avatar_url: string }>('/auth/profile/avatar/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });

    // 响应拦截器已将 response.data 设为 { avatar_url }
    return response.data.avatar_url;
};

/**
 * 修改密码（成功不返回数据，失败由拦截器抛错）
 */
export const changePassword = async (passwordData: PasswordChangeData): Promise<void> => {
    await api.post('/auth/profile/change-password/', passwordData);
};

/**
 * 登出所有设备（成功不返回数据，失败由拦截器抛错）
 */
export const logoutAllDevices = async (): Promise<void> => {
    await api.post('/auth/profile/logout-all/');
};

import { computed, type Ref } from 'vue';

// 计算密码强度（0-5），算法与注册页一致
export function usePasswordStrength(password: Ref<string>) {
    const strength = computed(() => {
        const pwd = password.value;
        if (!pwd) return 0;

        let score = 0;

        // 长度评分 (0-25分)
        if (pwd.length >= 8) score += 5;
        if (pwd.length >= 12) score += 5;
        if (pwd.length >= 16) score += 5;
        if (pwd.length >= 20) score += 5;
        if (pwd.length >= 24) score += 5;

        // 字符类型评分 (0-40分)
        if (/[a-z]/.test(pwd)) score += 8; // 小写字母
        if (/[A-Z]/.test(pwd)) score += 8; // 大写字母
        if (/[0-9]/.test(pwd)) score += 8; // 数字
        if (/[!@#$%^&*(),.?":{}|<>]/.test(pwd)) score += 8; // 特殊字符
        if (/[^\w\s]/.test(pwd)) score += 8; // 其他符号

        // 复杂度评分 (0-25分)
        const uniqueChars = new Set(pwd).size;
        if (uniqueChars >= 8) score += 5; // 字符多样性
        if (uniqueChars >= 12) score += 5;
        if (uniqueChars >= 16) score += 5;

        // 模式检测 (0-10分)
        if (!/(.)\1{2,}/.test(pwd)) score += 5; // 无连续重复字符
        if (
            !/012|123|234|345|456|567|678|789|890/.test(pwd) &&
            !/abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz/i.test(
                pwd,
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

    const getStrengthText = () => {
        switch (strength.value) {
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

    const getStrengthClass = () => {
        return {
            0: '',
            1: 'weak',
            2: 'fair',
            3: 'medium',
            4: 'strong',
            5: 'very-strong',
        }[strength.value] as 'weak' | 'fair' | 'medium' | 'strong' | 'very-strong' | '';
    };

    return {
        passwordStrength: strength,
        getStrengthText,
        getStrengthClass,
    };
}

# Django 媒体文件服务配置说明

## 配置概述

本项目已成功配置Django媒体文件服务，支持前端上传的头像和其他用户文件的访问。

## 配置详情

### 1. settings.py 配置

```python
# 静态文件配置
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### 2. URL 路由配置 (urls.py)

```python
from django.conf import settings
from django.conf.urls.static import static

# 在开发环境中提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

### 3. 用户头像模型配置

在 `UserProfile` 模型中已配置头像字段：

```python
avatar = models.ImageField(
    upload_to='avatars/%Y/%m/',
    null=True,
    blank=True,
    verbose_name='头像',
    help_text='用户头像图片'
)
```

## 访问方式

### 开发环境

- 媒体文件访问URL: `http://127.0.0.1:8000/media/`
- 头像文件示例: `http://127.0.0.1:8000/media/avatars/2025/01/user_avatar.jpg`

### 前端集成

前端可以通过以下方式访问用户头像：

```javascript
// 假设用户数据中包含头像路径
const avatarUrl = `${API_BASE_URL}${user.profile.avatar}`;
// 例如: http://127.0.0.1:8000/media/avatars/2025/01/avatar.jpg
```

## 目录结构

```
ling-task-flow-backend/
├── media/
│   ├── avatars/
│   │   ├── 2025/
│   │   │   ├── 01/
│   │   │   ├── 02/
│   │   │   └── ...
│   └── task_attachments/
│       ├── 2025/
│       └── ...
└── staticfiles/ (生产环境静态文件)
```

## 注意事项

1. **开发环境**: Django开发服务器会自动提供媒体文件服务
2. **生产环境**: 需要配置Nginx或Apache来提供静态文件和媒体文件服务
3. **安全性**: 媒体文件目录应该有适当的权限设置
4. **依赖**: 确保已安装 `Pillow` 库来支持图像处理

## 测试验证

配置已通过以下方式验证：

- ✅ Django服务器成功启动
- ✅ 媒体文件URL可正常访问 (HTTP 200)
- ✅ 头像上传目录结构正确
- ✅ ImageField配置正确

## 相关文件

- `ling_task_flow_backend/settings.py` - 媒体文件配置
- `ling_task_flow_backend/urls.py` - URL路由配置
- `LingTaskFlow/models.py` - 用户头像模型定义
- `requirements.txt` - 包含Pillow依赖
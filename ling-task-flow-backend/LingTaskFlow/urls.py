"""
LingTaskFlow应用的URL配置
"""
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from . import views

# 健康检查视图
def health_check(request):
    return JsonResponse({'status': 'ok', 'message': 'LingTaskFlow API is running'})

# 创建DRF路由器
router = DefaultRouter()

# 注册TaskViewSet
router.register(r'tasks', views.TaskViewSet, basename='task')

app_name = 'LingTaskFlow'

urlpatterns = [
    # API根路径
    path('', include(router.urls)),
    
    # 健康检查端点
    path('health/', health_check, name='health_check'),
    
    # 认证相关端点
    path('auth/register/', views.register_view, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/token/refresh/', views.token_refresh_view, name='token_refresh'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/profile/', views.user_profile_view, name='user_profile'),
    path('auth/profile/update/', views.update_profile_view, name='update_profile'),
]

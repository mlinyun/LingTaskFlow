# LingTaskFlow 功能扩展技术实现指南

## 📋 文档概览

**制定时间**: 2025年8月12日  
**技术负责人**: 开发团队  
**适用版本**: v2.0 功能扩展  
**技术栈**: Django + Vue 3 + Quasar + PostgreSQL

---

## 🏗️ 技术架构升级

### 后端架构扩展

```
LingTaskFlow Backend v2.0
├── 核心模块 (已完成)
│   ├── 用户认证系统
│   ├── 任务管理 API
│   └── 基础数据模型
├── 新增模块 (待开发)
│   ├── 通知系统 (Notification Engine)
│   ├── 活动追踪 (Activity Tracking)
│   ├── 团队协作 (Team Collaboration)
│   ├── 实时通信 (WebSocket)
│   └── 智能推荐 (AI Recommendations)
└── 基础设施升级
    ├── Django Channels (WebSocket)
    ├── Celery (异步任务)
    ├── Redis (缓存 + 消息队列)
    └── Elasticsearch (可选搜索)
```

### 前端架构扩展

```
LingTaskFlow Frontend v2.0
├── 核心组件 (已完成)
│   ├── 任务管理界面
│   ├── 用户认证
│   └── 统计仪表板
├── 新增组件 (待开发)
│   ├── 通知中心 (NotificationCenter)
│   ├── 活动流 (ActivityStream)
│   ├── 团队协作 (TeamCollaboration)
│   ├── 实时聊天 (RealTimeChat)
│   └── 个性化设置 (PersonalizationSettings)
└── 技术升级
    ├── Socket.IO Client (实时通信)
    ├── PWA 支持 (离线功能)
    ├── Workbox (Service Worker)
    └── Chart.js (高级图表)
```

---

## 🔔 智能通知系统技术实现

### 1. 后端通知引擎

#### 1.1 数据模型设计

```python
# models/notification.py
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class NotificationTemplate(models.Model):
    """通知模板"""
    name = models.CharField(max_length=100, unique=True)
    title_template = models.CharField(max_length=200)
    content_template = models.TextField()
    notification_type = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class NotificationPreference(models.Model):
    """用户通知偏好"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    task_due_reminder = models.BooleanField(default=True)
    task_assigned_notification = models.BooleanField(default=True)
    task_completed_notification = models.BooleanField(default=True)
    
class Notification(models.Model):
    """通知记录"""
    NOTIFICATION_TYPES = [
        ('task_due', '任务到期'),
        ('task_assigned', '任务分配'),
        ('task_completed', '任务完成'),
        ('task_commented', '任务评论'),
        ('system_update', '系统更新'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # 关联对象 (任务、评论等)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # 通知渠道状态
    email_sent = models.BooleanField(default=False)
    push_sent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]
```

#### 1.2 通知服务类

```python
# services/notification_service.py
from typing import List, Dict, Any
from django.contrib.auth.models import User
from django.template import Template, Context
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification, NotificationTemplate, NotificationPreference

class NotificationService:
    """通知服务"""
    
    def __init__(self):
        self.channel_layer = get_channel_layer()
    
    def create_notification(
        self, 
        recipient: User,
        notification_type: str,
        context: Dict[str, Any],
        sender: User = None,
        related_object = None
    ) -> Notification:
        """创建通知"""
        template = NotificationTemplate.objects.get(
            notification_type=notification_type,
            is_active=True
        )
        
        # 渲染通知内容
        title = Template(template.title_template).render(Context(context))
        content = Template(template.content_template).render(Context(context))
        
        # 创建通知记录
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            title=title,
            content=content,
            content_object=related_object
        )
        
        # 发送通知
        self._send_notification(notification)
        
        return notification
    
    def _send_notification(self, notification: Notification):
        """发送通知到各个渠道"""
        preference = NotificationPreference.objects.get_or_create(
            user=notification.recipient
        )[0]
        
        # 检查免打扰时间
        if self._is_quiet_hours(preference):
            return
        
        # 站内实时通知
        if preference.in_app_enabled:
            self._send_realtime_notification(notification)
        
        # 邮件通知
        if preference.email_enabled:
            self._send_email_notification(notification)
        
        # 推送通知
        if preference.push_enabled:
            self._send_push_notification(notification)
    
    def _send_realtime_notification(self, notification: Notification):
        """发送实时通知"""
        async_to_sync(self.channel_layer.group_send)(
            f"user_{notification.recipient.id}",
            {
                "type": "notification_message",
                "notification": {
                    "id": notification.id,
                    "title": notification.title,
                    "content": notification.content,
                    "type": notification.notification_type,
                    "created_at": notification.created_at.isoformat(),
                }
            }
        )
    
    def _is_quiet_hours(self, preference: NotificationPreference) -> bool:
        """检查是否在免打扰时间"""
        if not preference.quiet_hours_start or not preference.quiet_hours_end:
            return False
        
        from datetime import datetime
        now = datetime.now().time()
        return preference.quiet_hours_start <= now <= preference.quiet_hours_end
```

#### 1.3 WebSocket 消费者

```python
# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User

class NotificationConsumer(AsyncWebsocketConsumer):
    """通知 WebSocket 消费者"""
    
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return
        
        self.group_name = f"user_{self.user.id}"
        
        # 加入用户组
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # 发送未读通知数量
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': unread_count
        }))
    
    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def notification_message(self, event):
        """处理通知消息"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))
    
    @database_sync_to_async
    def get_unread_count(self):
        from .models import Notification
        return Notification.objects.filter(
            recipient=self.user,
            is_read=False
        ).count()
```

### 2. 前端通知系统

#### 2.1 通知中心组件

```vue
<!-- components/notification/NotificationCenter.vue -->
<template>
  <q-menu 
    v-model="showMenu" 
    anchor="bottom right" 
    self="top right"
    max-width="400px"
    class="notification-menu"
  >
    <q-card class="notification-card">
      <q-card-section class="notification-header">
        <div class="row items-center justify-between">
          <div class="text-h6">通知中心</div>
          <q-btn 
            flat 
            dense 
            icon="mark_email_read" 
            @click="markAllAsRead"
            :disable="unreadCount === 0"
          >
            <q-tooltip>全部标记为已读</q-tooltip>
          </q-btn>
        </div>
      </q-card-section>
      
      <q-separator />
      
      <q-card-section class="notification-filters">
        <q-btn-toggle
          v-model="filter"
          :options="filterOptions"
          dense
          flat
          class="full-width"
        />
      </q-card-section>
      
      <q-scroll-area 
        class="notification-list" 
        style="height: 400px"
      >
        <div v-if="filteredNotifications.length === 0" class="text-center q-pa-md text-grey">
          <q-icon name="notifications_none" size="48px" />
          <div class="q-mt-sm">暂无通知</div>
        </div>
        
        <notification-item
          v-for="notification in filteredNotifications"
          :key="notification.id"
          :notification="notification"
          @read="handleNotificationRead"
          @click="handleNotificationClick"
        />
      </q-scroll-area>
      
      <q-separator />
      
      <q-card-actions align="center">
        <q-btn 
          flat 
          label="查看全部" 
          @click="viewAllNotifications"
        />
      </q-card-actions>
    </q-card>
  </q-menu>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useNotificationStore } from 'src/stores/notification'
import NotificationItem from './NotificationItem.vue'
import { Notification } from 'src/types/notification'

interface Props {
  modelValue: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const notificationStore = useNotificationStore()

const showMenu = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const filter = ref('all')
const filterOptions = [
  { label: '全部', value: 'all' },
  { label: '未读', value: 'unread' },
  { label: '已读', value: 'read' }
]

const filteredNotifications = computed(() => {
  const notifications = notificationStore.notifications
  switch (filter.value) {
    case 'unread':
      return notifications.filter(n => !n.is_read)
    case 'read':
      return notifications.filter(n => n.is_read)
    default:
      return notifications
  }
})

const unreadCount = computed(() => notificationStore.unreadCount)

const markAllAsRead = async () => {
  await notificationStore.markAllAsRead()
}

const handleNotificationRead = (notification: Notification) => {
  notificationStore.markAsRead(notification.id)
}

const handleNotificationClick = (notification: Notification) => {
  // 处理通知点击，跳转到相关页面
  if (!notification.is_read) {
    handleNotificationRead(notification)
  }
  
  // 根据通知类型跳转
  if (notification.content_object) {
    // 跳转到相关任务或页面
  }
}

const viewAllNotifications = () => {
  showMenu.value = false
  // 跳转到通知页面
}

onMounted(() => {
  notificationStore.fetchNotifications()
  notificationStore.connectWebSocket()
})

onUnmounted(() => {
  notificationStore.disconnectWebSocket()
})
</script>
```

#### 2.2 通知状态管理

```typescript
// stores/notification.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from 'src/boot/axios'
import { Notification, NotificationPreference } from 'src/types/notification'

export const useNotificationStore = defineStore('notification', () => {
  // 状态
  const notifications = ref<Notification[]>([])
  const preferences = ref<NotificationPreference | null>(null)
  const socket = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  
  // 计算属性
  const unreadCount = computed(() => 
    notifications.value.filter(n => !n.is_read).length
  )
  
  const unreadNotifications = computed(() => 
    notifications.value.filter(n => !n.is_read)
  )
  
  // WebSocket 连接
  const connectWebSocket = () => {
    const wsUrl = `ws://localhost:8000/ws/notifications/`
    socket.value = new WebSocket(wsUrl)
    
    socket.value.onopen = () => {
      isConnected.value = true
      console.log('通知 WebSocket 连接成功')
    }
    
    socket.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleWebSocketMessage(data)
    }
    
    socket.value.onclose = () => {
      isConnected.value = false
      console.log('通知 WebSocket 连接关闭')
      // 重连逻辑
      setTimeout(connectWebSocket, 5000)
    }
    
    socket.value.onerror = (error) => {
      console.error('通知 WebSocket 错误:', error)
    }
  }
  
  const disconnectWebSocket = () => {
    if (socket.value) {
      socket.value.close()
      socket.value = null
      isConnected.value = false
    }
  }
  
  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'notification':
        // 新通知
        notifications.value.unshift(data.notification)
        showNotificationToast(data.notification)
        break
      case 'unread_count':
        // 未读数量更新
        break
    }
  }
  
  const showNotificationToast = (notification: Notification) => {
    // 显示通知提示
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(notification.title, {
        body: notification.content,
        icon: '/icons/icon-192x192.png'
      })
    }
  }
  
  // API 方法
  const fetchNotifications = async (page = 1, limit = 20) => {
    try {
      const response = await api.get('/api/notifications/', {
        params: { page, limit }
      })
      
      if (page === 1) {
        notifications.value = response.data.results
      } else {
        notifications.value.push(...response.data.results)
      }
    } catch (error) {
      console.error('获取通知失败:', error)
    }
  }
  
  const markAsRead = async (notificationId: number) => {
    try {
      await api.patch(`/api/notifications/${notificationId}/read/`)
      
      const notification = notifications.value.find(n => n.id === notificationId)
      if (notification) {
        notification.is_read = true
        notification.read_at = new Date().toISOString()
      }
    } catch (error) {
      console.error('标记通知已读失败:', error)
    }
  }
  
  const markAllAsRead = async () => {
    try {
      await api.post('/api/notifications/mark-all-read/')
      
      notifications.value.forEach(notification => {
        if (!notification.is_read) {
          notification.is_read = true
          notification.read_at = new Date().toISOString()
        }
      })
    } catch (error) {
      console.error('标记全部已读失败:', error)
    }
  }
  
  const fetchPreferences = async () => {
    try {
      const response = await api.get('/api/notifications/preferences/')
      preferences.value = response.data
    } catch (error) {
      console.error('获取通知偏好失败:', error)
    }
  }
  
  const updatePreferences = async (newPreferences: Partial<NotificationPreference>) => {
    try {
      const response = await api.patch('/api/notifications/preferences/', newPreferences)
      preferences.value = response.data
    } catch (error) {
      console.error('更新通知偏好失败:', error)
    }
  }
  
  return {
    // 状态
    notifications,
    preferences,
    isConnected,
    
    // 计算属性
    unreadCount,
    unreadNotifications,
    
    // 方法
    connectWebSocket,
    disconnectWebSocket,
    fetchNotifications,
    markAsRead,
    markAllAsRead,
    fetchPreferences,
    updatePreferences
  }
})
```

---

## 📊 活动追踪系统技术实现

### 1. 活动记录模型

```python
# models/activity.py
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import json

class Activity(models.Model):
    """活动记录"""
    ACTIVITY_TYPES = [
        ('task_created', '创建任务'),
        ('task_updated', '更新任务'),
        ('task_completed', '完成任务'),
        ('task_deleted', '删除任务'),
        ('user_login', '用户登录'),
        ('user_logout', '用户登出'),
        ('search_performed', '执行搜索'),
        ('page_visited', '访问页面'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    description = models.TextField()
    
    # 关联对象
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # 额外数据
    metadata = models.JSONField(default=dict, blank=True)
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 会话信息
    session_id = models.CharField(max_length=100, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['activity_type', '-created_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"
```

### 2. 活动追踪服务

```python
# services/activity_service.py
from typing import Dict, Any, Optional
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from .models import Activity

class ActivityService:
    """活动追踪服务"""
    
    @staticmethod
    def log_activity(
        user: User,
        activity_type: str,
        description: str,
        related_object = None,
        metadata: Dict[str, Any] = None,
        request = None
    ) -> Activity:
        """记录活动"""
        activity_data = {
            'user': user,
            'activity_type': activity_type,
            'description': description,
            'metadata': metadata or {}
        }
        
        # 关联对象
        if related_object:
            activity_data['content_object'] = related_object
        
        # 请求信息
        if request:
            activity_data.update({
                'session_id': request.session.session_key,
                'ip_address': ActivityService._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')
            })
        
        return Activity.objects.create(**activity_data)
    
    @staticmethod
    def _get_client_ip(request) -> str:
        """获取客户端IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def get_user_activities(
        user: User, 
        activity_type: str = None,
        limit: int = 50
    ):
        """获取用户活动"""
        queryset = Activity.objects.filter(user=user)
        
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        
        return queryset[:limit]
    
    @staticmethod
    def get_activity_stats(user: User, days: int = 30):
        """获取活动统计"""
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count
        
        start_date = timezone.now() - timedelta(days=days)
        
        stats = Activity.objects.filter(
            user=user,
            created_at__gte=start_date
        ).values('activity_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return list(stats)
```

---

## 👥 团队协作功能技术实现

### 1. 团队模型设计

```python
# models/team.py
from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    """团队"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_teams')
    members = models.ManyToManyField(User, through='TeamMember', related_name='teams')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 团队设置
    is_public = models.BooleanField(default=False)
    allow_member_invite = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class TeamMember(models.Model):
    """团队成员"""
    ROLE_CHOICES = [
        ('owner', '所有者'),
        ('admin', '管理员'),
        ('member', '成员'),
        ('viewer', '观察者'),
    ]
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['team', 'user']
        ordering = ['joined_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.team.name} ({self.get_role_display()})"

class Comment(models.Model):
    """评论"""
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    
    # 提及用户
    mentioned_users = models.ManyToManyField(User, blank=True, related_name='mentioned_comments')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.author.username} - {self.task.title[:50]}"
```

### 2. 团队协作 API

```python
# views/team_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Team, TeamMember, Comment
from .serializers import TeamSerializer, CommentSerializer
from .permissions import TeamPermission

class TeamViewSet(viewsets.ModelViewSet):
    """团队视图集"""
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated, TeamPermission]
    
    def get_queryset(self):
        return Team.objects.filter(
            Q(members=self.request.user) | Q(is_public=True)
        ).distinct()
    
    def perform_create(self, serializer):
        team = serializer.save(owner=self.request.user)
        # 创建者自动成为团队成员
        TeamMember.objects.create(
            team=team,
            user=self.request.user,
            role='owner'
        )
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """加入团队"""
        team = self.get_object()
        
        if TeamMember.objects.filter(team=team, user=request.user).exists():
            return Response(
                {'error': '您已经是团队成员'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        TeamMember.objects.create(
            team=team,
            user=request.user,
            role='member'
        )
        
        return Response({'message': '成功加入团队'})
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """离开团队"""
        team = self.get_object()
        
        try:
            member = TeamMember.objects.get(team=team, user=request.user)
            if member.role == 'owner':
                return Response(
                    {'error': '团队所有者不能离开团队'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            member.delete()
            return Response({'message': '成功离开团队'})
        except TeamMember.DoesNotExist:
            return Response(
                {'error': '您不是团队成员'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """获取团队成员"""
        team = self.get_object()
        members = TeamMember.objects.filter(team=team, is_active=True)
        
        data = [{
            'id': member.user.id,
            'username': member.user.username,
            'email': member.user.email,
            'role': member.role,
            'joined_at': member.joined_at
        } for member in members]
        
        return Response(data)

class CommentViewSet(viewsets.ModelViewSet):
    """评论视图集"""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        task_id = self.request.query_params.get('task_id')
        if task_id:
            return Comment.objects.filter(
                task_id=task_id,
                is_deleted=False
            )
        return Comment.objects.none()
    
    def perform_create(self, serializer):
        comment = serializer.save(author=self.request.user)
        
        # 处理@提及
        self._handle_mentions(comment)
        
        # 发送通知
        self._send_comment_notifications(comment)
    
    def _handle_mentions(self, comment):
        """处理@提及"""
        import re
        from django.contrib.auth.models import User
        
        # 提取@用户名
        mentions = re.findall(r'@(\w+)', comment.content)
        
        for username in mentions:
            try:
                user = User.objects.get(username=username)
                comment.mentioned_users.add(user)
            except User.DoesNotExist:
                continue
    
    def _send_comment_notifications(self, comment):
        """发送评论通知"""
        from .services import NotificationService
        
        notification_service = NotificationService()
        
        # 通知任务负责人
        if comment.task.assignee and comment.task.assignee != comment.author:
            notification_service.create_notification(
                recipient=comment.task.assignee,
                notification_type='task_commented',
                context={
                    'task_title': comment.task.title,
                    'comment_author': comment.author.username,
                    'comment_content': comment.content[:100]
                },
                sender=comment.author,
                related_object=comment.task
            )
        
        # 通知被@的用户
        for user in comment.mentioned_users.all():
            if user != comment.author:
                notification_service.create_notification(
                    recipient=user,
                    notification_type='task_commented',
                    context={
                        'task_title': comment.task.title,
                        'comment_author': comment.author.username,
                        'comment_content': comment.content[:100]
                    },
                    sender=comment.author,
                    related_object=comment.task
                )
```

---

## 📱 PWA 与移动端优化

### 1. Service Worker 配置

```javascript
// public/sw.js
const CACHE_NAME = 'lingtaskflow-v2.0'
const urlsToCache = [
  '/',
  '/static/css/app.css',
  '/static/js/app.js',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png'
]

// 安装事件
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(urlsToCache)
      })
  )
})

// 激活事件
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName)
          }
        })
      )
    })
  )
})

// 拦截请求
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // 缓存命中，返回缓存
        if (response) {
          return response
        }
        
        // 网络请求
        return fetch(event.request).then((response) => {
          // 检查是否是有效响应
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response
          }
          
          // 克隆响应
          const responseToCache = response.clone()
          
          caches.open(CACHE_NAME)
            .then((cache) => {
              cache.put(event.request, responseToCache)
            })
          
          return response
        })
      })
  )
})

// 后台同步
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync())
  }
})

function doBackgroundSync() {
  // 处理离线时的数据同步
  return new Promise((resolve) => {
    // 同步逻辑
    resolve()
  })
}
```

### 2. 离线数据管理

```typescript
// utils/offline-manager.ts
import { openDB, DBSchema, IDBPDatabase } from 'idb'

interface OfflineDB extends DBSchema {
  tasks: {
    key: number
    value: {
      id: number
      title: string
      description: string
      status: string
      created_at: string
      updated_at: string
      sync_status: 'synced' | 'pending' | 'conflict'
    }
  }
  
  operations: {
    key: number
    value: {
      id: number
      type: 'create' | 'update' | 'delete'
      entity: 'task' | 'comment'
      entity_id: number
      data: any
      timestamp: string
      sync_status: 'pending' | 'synced' | 'failed'
    }
  }
}

class OfflineManager {
  private db: IDBPDatabase<OfflineDB> | null = null
  
  async init() {
    this.db = await openDB<OfflineDB>('LingTaskFlowDB', 1, {
      upgrade(db) {
        // 创建任务表
        const taskStore = db.createObjectStore('tasks', {
          keyPath: 'id'
        })
        taskStore.createIndex('sync_status', 'sync_status')
        
        // 创建操作队列表
        const operationStore = db.createObjectStore('operations', {
          keyPath: 'id',
          autoIncrement: true
        })
        operationStore.createIndex('sync_status', 'sync_status')
        operationStore.createIndex('timestamp', 'timestamp')
      }
    })
  }
  
  // 保存任务到离线存储
  async saveTask(task: any) {
    if (!this.db) await this.init()
    
    await this.db!.put('tasks', {
      ...task,
      sync_status: 'synced'
    })
  }
  
  // 获取离线任务
  async getTasks() {
    if (!this.db) await this.init()
    return await this.db!.getAll('tasks')
  }
  
  // 添加操作到队列
  async addOperation(operation: Omit<OfflineDB['operations']['value'], 'id'>) {
    if (!this.db) await this.init()
    
    await this.db!.add('operations', {
      ...operation,
      sync_status: 'pending'
    })
  }
  
  // 获取待同步操作
  async getPendingOperations() {
    if (!this.db) await this.init()
    
    const index = this.db!.transaction('operations').store.index('sync_status')
    return await index.getAll('pending')
  }
  
  // 同步数据
  async syncData() {
    const operations = await this.getPendingOperations()
    
    for (const operation of operations) {
      try {
        await this.syncOperation(operation)
        
        // 标记为已同步
        await this.db!.put('operations', {
          ...operation,
          sync_status: 'synced'
        })
      } catch (error) {
        console.error('同步操作失败:', error)
        
        // 标记为失败
        await this.db!.put('operations', {
          ...operation,
          sync_status: 'failed'
        })
      }
    }
  }
  
  private async syncOperation(operation: OfflineDB['operations']['value']) {
    // 根据操作类型执行同步
    switch (operation.type) {
      case 'create':
        // 创建操作
        break
      case 'update':
        // 更新操作
        break
      case 'delete':
        // 删除操作
        break
    }
  }
}

export const offlineManager = new OfflineManager()
```

---

## 🎨 个性化主题系统

### 1. 主题引擎

```typescript
// utils/theme-engine.ts
interface ThemeConfig {
  name: string
  colors: {
    primary: string
    secondary: string
    accent: string
    background: string
    surface: string
    text: string
  }
  typography: {
    fontFamily: string
    fontSize: {
      small: string
      medium: string
      large: string
    }
  }
  spacing: {
    small: string
    medium: string
    large: string
  }
  borderRadius: string
  shadows: {
    small: string
    medium: string
    large: string
  }
}

class ThemeEngine {
  private currentTheme: ThemeConfig | null = null
  private customThemes: Map<string, ThemeConfig> = new Map()
  
  // 预设主题
  private presetThemes: Map<string, ThemeConfig> = new Map([
    ['default', {
      name: 'Default',
      colors: {
        primary: '#1976d2',
        secondary: '#424242',
        accent: '#82b1ff',
        background: '#fafafa',
        surface: '#ffffff',
        text: '#212121'
      },
      typography: {
        fontFamily: 'Roboto, sans-serif',
        fontSize: {
          small: '12px',
          medium: '14px',
          large: '16px'
        }
      },
      spacing: {
        small: '8px',
        medium: '16px',
        large: '24px'
      },
      borderRadius: '4px',
      shadows: {
        small: '0 1px 3px rgba(0,0,0,0.12)',
        medium: '0 4px 6px rgba(0,0,0,0.16)',
        large: '0 10px 20px rgba(0,0,0,0.19)'
      }
    }],
    ['dark', {
      name: 'Dark',
      colors: {
        primary: '#bb86fc',
        secondary: '#03dac6',
        accent: '#cf6679',
        background: '#121212',
        surface: '#1e1e1e',
        text: '#ffffff'
      },
      typography: {
        fontFamily: 'Roboto, sans-serif',
        fontSize: {
          small: '12px',
          medium: '14px',
          large: '16px'
        }
      },
      spacing: {
        small: '8px',
        medium: '16px',
        large: '24px'
      },
      borderRadius: '4px',
      shadows: {
        small: '0 1px 3px rgba(0,0,0,0.24)',
        medium: '0 4px 6px rgba(0,0,0,0.32)',
        large: '0 10px 20px rgba(0,0,0,0.38)'
      }
    }]
  ])
  
  // 应用主题
  applyTheme(themeName: string) {
    const theme = this.presetThemes.get(themeName) || this.customThemes.get(themeName)
    
    if (!theme) {
      console.error(`主题 ${themeName} 不存在`)
      return
    }
    
    this.currentTheme = theme
    this.updateCSSVariables(theme)
    this.saveThemePreference(themeName)
  }
  
  // 更新 CSS 变量
  private updateCSSVariables(theme: ThemeConfig) {
    const root = document.documentElement
    
    // 颜色变量
    Object.entries(theme.colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value)
    })
    
    // 字体变量
    root.style.setProperty('--font-family', theme.typography.fontFamily)
    Object.entries(theme.typography.fontSize).forEach(([key, value]) => {
      root.style.setProperty(`--font-size-${key}`, value)
    })
    
    // 间距变量
    Object.entries(theme.spacing).forEach(([key, value]) => {
      root.style.setProperty(`--spacing-${key}`, value)
    })
    
    // 其他变量
    root.style.setProperty('--border-radius', theme.borderRadius)
    Object.entries(theme.shadows).forEach(([key, value]) => {
      root.style.setProperty(`--shadow-${key}`, value)
    })
  }
  
  // 创建自定义主题
  createCustomTheme(name: string, config: Partial<ThemeConfig>) {
    const baseTheme = this.presetThemes.get('default')!
    const customTheme: ThemeConfig = {
      ...baseTheme,
      ...config,
      name,
      colors: { ...baseTheme.colors, ...config.colors },
      typography: { ...baseTheme.typography, ...config.typography },
      spacing: { ...baseTheme.spacing, ...config.spacing }
    }
    
    this.customThemes.set(name, customTheme)
    this.saveCustomTheme(name, customTheme)
  }
  
  // 获取所有主题
  getAllThemes(): ThemeConfig[] {
    return [
      ...Array.from(this.presetThemes.values()),
      ...Array.from(this.customThemes.values())
    ]
  }
  
  // 保存主题偏好
  private saveThemePreference(themeName: string) {
    localStorage.setItem('theme-preference', themeName)
  }
  
  // 加载主题偏好
  loadThemePreference() {
    const savedTheme = localStorage.getItem('theme-preference')
    if (savedTheme) {
      this.applyTheme(savedTheme)
    } else {
      this.applyTheme('default')
    }
  }
  
  // 保存自定义主题
  private saveCustomTheme(name: string, theme: ThemeConfig) {
    const customThemes = JSON.parse(localStorage.getItem('custom-themes') || '{}')
    customThemes[name] = theme
    localStorage.setItem('custom-themes', JSON.stringify(customThemes))
  }
  
  // 加载自定义主题
  loadCustomThemes() {
    const customThemes = JSON.parse(localStorage.getItem('custom-themes') || '{}')
    Object.entries(customThemes).forEach(([name, theme]) => {
      this.customThemes.set(name, theme as ThemeConfig)
    })
  }
}

export const themeEngine = new ThemeEngine()
```

---

## 📋 总结

本技术实现指南详细描述了 LingTaskFlow v2.0 功能扩展的技术架构和实现方案，包括：

### 🎯 核心技术升级

1. **智能通知系统**: Django Channels + WebSocket 实现实时通知
2. **活动追踪分析**: 完整的用户行为记录和数据洞察
3. **团队协作功能**: 多用户协作、实时评论、权限管理
4. **PWA 移动优化**: Service Worker + IndexedDB 离线支持
5. **个性化主题**: 动态主题引擎和自定义配置

### 🚀 技术亮点

- **实时通信**: WebSocket 双向通信，毫秒级响应
- **离线支持**: 完整的离线数据管理和同步机制
- **智能推荐**: 基于用户行为的个性化推荐算法
- **模块化设计**: 高内聚低耦合的组件架构
- **性能优化**: 缓存策略、懒加载、虚拟滚动

### 📊 开发效率

- **代码复用**: 组件化开发，提高开发效率
- **类型安全**: TypeScript 全覆盖，减少运行时错误
- **测试覆盖**: 单元测试 + 集成测试，保证代码质量
- **文档完善**: 详细的 API 文档和使用指南

这些技术实现将使 LingTaskFlow 成为一个功能完整、性能优秀、用户体验出色的现代化任务管理平台。

---

**文档制定者**: 技术团队  
**制定时间**: 2025年8月12日  
**版本**: v1.0  
**下次更新**: 根据开发进度调整
"""
LingTaskFlow 权限类
定义API访问权限控制规则
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    自定义权限类：只有对象的所有者才能进行写操作，其他用户只能读取
    
    使用场景：
    - 任务管理：用户只能编辑自己的任务
    - 用户资料：用户只能修改自己的资料
    - 评论系统：用户只能编辑自己的评论
    
    权限规则：
    - 未认证用户：拒绝所有访问
    - 已认证用户：可以读取所有内容，但只能修改自己拥有的对象
    - 管理员用户：拥有所有权限
    """
    
    def has_permission(self, request, view):
        """
        检查用户是否有权限访问视图
        """
        # 只允许已认证用户访问
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        检查用户是否有权限操作特定对象
        """
        # 管理员拥有所有权限
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # 读权限允许任何已认证用户
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 写权限只允许对象的所有者
        # 检查对象是否有owner属性，如果没有则检查user属性
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        else:
            # 如果对象没有明确的所有者属性，拒绝写操作
            return False


class IsOwner(permissions.BasePermission):
    """
    严格的所有者权限：只有对象的所有者才能进行任何操作
    """
    
    def has_permission(self, request, view):
        """检查用户是否已认证"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """检查用户是否为对象所有者"""
        # 管理员拥有所有权限
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # 只有所有者才能操作
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        else:
            return False


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    作者权限：作者可以编辑，其他人只能读取
    """
    
    def has_permission(self, request, view):
        """所有已认证用户都有基本权限"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """检查读写权限"""
        # 管理员拥有所有权限
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # 读权限对所有已认证用户开放
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 写权限只给作者
        if hasattr(obj, 'author'):
            return obj.author == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        else:
            return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    管理员写权限：只有管理员能写，其他人只能读
    """
    
    def has_permission(self, request, view):
        """检查基本权限"""
        # 读权限对所有已认证用户开放
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # 写权限只给管理员
        return (request.user and request.user.is_authenticated and 
                (request.user.is_staff or request.user.is_superuser))
    
    def has_object_permission(self, request, view, obj):
        """检查对象权限"""
        # 读权限对所有已认证用户开放
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 写权限只给管理员
        return request.user.is_staff or request.user.is_superuser


class IsSelfOrReadOnly(permissions.BasePermission):
    """
    用户自身权限：用户只能修改自己的信息
    """
    
    def has_permission(self, request, view):
        """检查用户是否已认证"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """检查是否为用户自身"""
        # 管理员拥有所有权限
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # 读权限对所有已认证用户开放
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 写权限只给用户本人
        # 如果obj是User对象
        if hasattr(obj, 'username'):
            return obj == request.user
        # 如果obj是关联到User的对象（如UserProfile）
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        else:
            return False

"""
LingTaskFlow 过滤器
提供任务查询过滤功能
"""
import django_filters
from django.db.models import Q

from .models import Task


class TaskFilter(django_filters.FilterSet):
    """
    任务过滤器
    支持多种过滤条件和搜索功能
    """

    # 搜索功能
    search = django_filters.CharFilter(method='filter_search')

    # 状态过滤
    status = django_filters.ChoiceFilter(choices=Task.STATUS_CHOICES)
    status__in = django_filters.BaseInFilter(field_name='status', lookup_expr='in')

    # 优先级过滤
    priority = django_filters.ChoiceFilter(choices=Task.PRIORITY_CHOICES)
    priority__in = django_filters.BaseInFilter(field_name='priority', lookup_expr='in')

    # 分类过滤
    category = django_filters.CharFilter(lookup_expr='icontains')
    category__in = django_filters.BaseInFilter(field_name='category', lookup_expr='in')

    # 分配相关过滤
    assigned_to = django_filters.ModelChoiceFilter(
        queryset=None  # 在__init__中设置
    )
    is_assigned = django_filters.BooleanFilter(method='filter_is_assigned')

    # 时间范围过滤
    created_at = django_filters.DateTimeFromToRangeFilter()
    due_date = django_filters.DateFromToRangeFilter()
    start_date = django_filters.DateFromToRangeFilter()

    # 逾期任务
    is_overdue = django_filters.BooleanFilter(method='filter_is_overdue')

    # 即将到期任务（未来N天内）
    due_soon = django_filters.NumberFilter(method='filter_due_soon')

    # 进度范围
    progress_min = django_filters.NumberFilter(field_name='progress', lookup_expr='gte')
    progress_max = django_filters.NumberFilter(field_name='progress', lookup_expr='lte')

    # 标签过滤
    tags = django_filters.CharFilter(method='filter_tags')

    # 软删除状态（仅限管理员或所有者）
    include_deleted = django_filters.BooleanFilter(method='filter_include_deleted')

    class Meta:
        model = Task
        fields = [
            'status', 'priority', 'category', 'assigned_to',
            'created_at', 'due_date', 'start_date'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 动态设置assigned_to的查询集
        if hasattr(self, 'request') and self.request.user.is_authenticated:
            from django.contrib.auth.models import User
            self.filters['assigned_to'].queryset = User.objects.filter(
                Q(assigned_tasks__isnull=False) | Q(owned_tasks__isnull=False)
            ).distinct()
        else:
            from django.contrib.auth.models import User
            self.filters['assigned_to'].queryset = User.objects.none()

    def filter_search(self, queryset, name, value):
        """
        全文搜索功能
        搜索标题、描述、分类和标签
        """
        if not value:
            return queryset

        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(category__icontains=value) |
            Q(tags__icontains=value)
        )

    def filter_is_assigned(self, queryset, name, value):
        """过滤是否已分配任务"""
        if value is True:
            return queryset.filter(assigned_to__isnull=False)
        elif value is False:
            return queryset.filter(assigned_to__isnull=True)
        return queryset

    def filter_is_overdue(self, queryset, name, value):
        """过滤逾期任务"""
        if value is True:
            from django.utils import timezone
            return queryset.filter(
                due_date__lt=timezone.now(),
                status__in=['PENDING', 'IN_PROGRESS', 'ON_HOLD']
            )
        elif value is False:
            from django.utils import timezone
            return queryset.exclude(
                due_date__lt=timezone.now(),
                status__in=['PENDING', 'IN_PROGRESS', 'ON_HOLD']
            )
        return queryset

    def filter_due_soon(self, queryset, name, value):
        """过滤即将到期的任务（未来N天内）"""
        if value and value > 0:
            from django.utils import timezone
            from datetime import timedelta

            end_date = timezone.now() + timedelta(days=value)
            return queryset.filter(
                due_date__lte=end_date,
                due_date__gte=timezone.now(),
                status__in=['PENDING', 'IN_PROGRESS', 'ON_HOLD']
            )
        return queryset

    def filter_tags(self, queryset, name, value):
        """根据标签过滤"""
        if not value:
            return queryset

        # 支持多个标签搜索，用逗号分隔
        tags = [tag.strip() for tag in value.split(',')]
        q_objects = Q()

        for tag in tags:
            if tag:
                q_objects |= Q(tags__icontains=tag)

        return queryset.filter(q_objects)

    def filter_include_deleted(self, queryset, name, value):
        """
        包含软删除的任务
        只有任务所有者可以查看自己的软删除任务
        """
        if value is True and self.request.user.is_authenticated:
            # 返回包含软删除的查询集，但仍然限制为用户相关的任务
            return Task.all_objects.filter(
                Q(owner=self.request.user) | Q(assigned_to=self.request.user)
            )
        return queryset

    @property
    def qs(self):
        """
        重写查询集，确保用户只能看到自己相关的任务
        """
        parent = super().qs
        user = getattr(self.request, 'user', None)

        if not user or not user.is_authenticated:
            return parent.none()

        # 用户只能看到自己拥有或被分配的任务
        return parent.filter(
            Q(owner=user) | Q(assigned_to=user)
        ).distinct()

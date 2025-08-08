# LingTaskFlow 拖拽排序功能开发任务

## 📋 任务基本信息

| 项目名称 | LingTaskFlow - 凌云任务管理平台 |
| -------- | ------------------------------- |
| 任务编号 | 5.2.4 |
| 任务名称 | 实现任务列表拖拽排序功能 |
| 优先级 | P1 (高优先级) |
| 预估工期 | 2-3天 |
| 创建日期 | 2025年8月9日 |
| 负责人 | GitHub Copilot |

---

## 🎯 任务目标

### 主要目标
实现任务列表的拖拽排序功能，允许用户通过拖拽操作重新排列任务顺序，提升任务管理的交互体验。

### 具体目标
1. **前端拖拽交互** - 实现流畅的任务卡片拖拽操作
2. **视觉反馈** - 提供清晰的拖拽状态指示和预览效果
3. **后端数据持久化** - 保存用户自定义的任务排序
4. **移动端适配** - 支持触摸设备的拖拽操作
5. **性能优化** - 确保大量任务时的拖拽性能

---

## 📊 当前项目完成状态

### ✅ 已完成的主要阶段 (77% 总体完成度)

#### 第一阶段：基础架构与认证系统 (100%)
- Django + JWT认证系统
- 用户注册、登录、Token刷新
- 权限控制和数据隔离

#### 第二阶段：任务管理API开发 (100%)
- 完整的RESTful API (18个端点)
- 任务CRUD操作 + 软删除机制
- 高级搜索、分页、排序功能
- 统计分析API

#### 第三阶段：前端基础框架搭建 (100%)
- Vue 3 + Quasar + TypeScript架构
- Pinia状态管理 + Vue Router
- HTTP客户端 + 认证拦截器

#### 第四阶段：任务管理前端界面 (100%)
- 完整的任务管理界面系统
- 任务卡片、对话框、回收站
- 搜索过滤、批量操作功能

#### 第五阶段：统计与优化功能 (85%)
- ✅ 统计仪表板 (100%) - 数据可视化图表
- ✅ 用户体验优化 (90%) - 加载状态、错误处理、确认对话框、快捷键系统
- ❌ **拖拽排序功能 (0%)** - 本任务目标

### 🚧 技术债务状态
- ✅ 前端认证阻塞 - 已解决
- ✅ 用户体验缺失 - 已解决
- ✅ 操作确认缺失 - 已解决
- ✅ 快捷键支持 - 已解决
- ❌ **拖拽排序功能** - 待解决 (本任务)

---

## 🔧 技术实现方案

### 前端技术栈
- **拖拽库**: vue3-draggable-next (Vue 3兼容的拖拽库)
- **状态管理**: Pinia (taskStore扩展)
- **UI框架**: Quasar Framework
- **类型系统**: TypeScript

### 后端技术栈
- **框架**: Django REST Framework
- **数据库字段**: 新增 `sort_order` 字段
- **API端点**: 扩展现有任务API

---

## 📋 详细开发计划

### 阶段一：后端数据模型扩展 (0.5天)

#### 1.1 数据库模型修改
```python
# LingTaskFlow/models.py
class Task(models.Model):
    # ... 现有字段 ...
    
    # 新增排序字段
    sort_order = models.PositiveIntegerField(
        default=0, 
        db_index=True,
        help_text="用户自定义排序顺序，数值越小越靠前"
    )
    
    class Meta:
        db_table = 'tasks'
        ordering = ['sort_order', '-created_at']  # 优先按sort_order排序
        indexes = [
            # ... 现有索引 ...
            models.Index(fields=['user', 'sort_order', 'is_deleted']),
        ]
```

#### 1.2 数据库迁移
- 创建迁移文件添加 `sort_order` 字段
- 为现有任务设置默认排序值
- 更新数据库索引

#### 1.3 序列化器更新
```python
# LingTaskFlow/serializers.py
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            # ... 现有字段 ...
            'sort_order',
        ]
        
class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            # ... 现有字段 ...
            'sort_order',
        ]
```

### 阶段二：后端API扩展 (0.5天)

#### 2.1 批量排序更新API
```python
# LingTaskFlow/views.py
@action(detail=False, methods=['patch'])
def batch_update_sort_order(self, request):
    """
    批量更新任务排序
    
    Request Body:
    {
        "tasks": [
            {"id": "uuid1", "sort_order": 1},
            {"id": "uuid2", "sort_order": 2},
            ...
        ]
    }
    """
    pass
```

#### 2.2 查询集排序优化
- 更新 `get_queryset` 方法，优先按 `sort_order` 排序
- 保持向后兼容性，支持原有排序参数

### 阶段三：前端拖拽组件开发 (1天)

#### 3.1 安装依赖
```bash
npm install vue3-draggable-next
```

#### 3.2 拖拽组件实现
```vue
<!-- components/task-list/DraggableTaskList.vue -->
<template>
  <draggable
    v-model="localTasks"
    item-key="id"
    :animation="200"
    :disabled="loading"
    ghost-class="task-ghost"
    chosen-class="task-chosen"
    drag-class="task-drag"
    @start="onDragStart"
    @end="onDragEnd"
  >
    <template #item="{ element: task, index }">
      <CyberTaskCard
        :task="task"
        :dragging="isDragging"
        @edit="$emit('edit', task)"
        @delete="$emit('delete', task.id)"
        @status-change="$emit('status-change', task.id, $event)"
      />
    </template>
  </draggable>
</template>
```

#### 3.3 拖拽样式设计
```scss
// 拖拽状态样式
.task-ghost {
  opacity: 0.5;
  background: rgba(var(--q-primary), 0.1);
  border: 2px dashed rgba(var(--q-primary), 0.5);
}

.task-chosen {
  transform: scale(1.02);
  box-shadow: 0 8px 32px rgba(0, 255, 255, 0.3);
}

.task-drag {
  transform: rotate(5deg);
  opacity: 0.8;
}
```

### 阶段四：状态管理集成 (0.5天)

#### 4.1 TaskStore扩展
```typescript
// stores/task.ts
export const useTaskStore = defineStore('task', () => {
  // ... 现有状态 ...
  
  // 拖拽相关状态
  const isDragging = ref(false)
  const draggedTask = ref<Task | null>(null)
  
  // 批量更新排序
  async function updateTasksOrder(tasks: Array<{id: string, sort_order: number}>) {
    try {
      await taskApi.batchUpdateSortOrder(tasks)
      // 更新本地状态
      tasks.forEach(({ id, sort_order }) => {
        const task = tasks.value.find(t => t.id === id)
        if (task) {
          task.sort_order = sort_order
        }
      })
    } catch (error) {
      console.error('Failed to update tasks order:', error)
      throw error
    }
  }
  
  return {
    // ... 现有返回 ...
    isDragging,
    draggedTask,
    updateTasksOrder,
  }
})
```

#### 4.2 API客户端扩展
```typescript
// utils/api.ts
export const taskApi = {
  // ... 现有方法 ...
  
  async batchUpdateSortOrder(tasks: Array<{id: string, sort_order: number}>) {
    const response = await apiClient.patch('/api/tasks/batch_update_sort_order/', {
      tasks
    })
    return response.data
  },
}
```

### 阶段五：UI集成和优化 (0.5天)

#### 5.1 TaskListPage集成
- 替换现有任务列表为拖拽组件
- 添加拖拽状态指示器
- 集成错误处理和加载状态

#### 5.2 移动端适配
- 添加触摸事件支持
- 优化移动设备拖拽体验
- 添加长按拖拽功能

#### 5.3 性能优化
- 防抖处理批量更新请求
- 优化大量任务时的渲染性能
- 添加拖拽操作的撤销功能

---

## 🎨 用户体验设计

### 视觉反馈
1. **拖拽开始** - 任务卡片轻微放大，添加阴影效果
2. **拖拽中** - 半透明预览，目标位置高亮
3. **拖拽结束** - 平滑动画过渡到新位置
4. **保存状态** - 显示保存指示器和成功提示

### 交互设计
1. **拖拽手柄** - 任务卡片左侧添加拖拽图标
2. **拖拽区域** - 整个任务卡片可拖拽
3. **禁用状态** - 加载时禁用拖拽，显示禁用样式
4. **错误处理** - 拖拽失败时恢复原位置，显示错误提示

### 快捷键支持
- **Ctrl + ↑/↓** - 键盘方式调整任务顺序
- **Ctrl + Shift + ↑/↓** - 移动到列表顶部/底部

---

## 📝 实现细节

### 数据流程
1. **用户拖拽** → 前端组件状态更新
2. **拖拽结束** → 计算新的排序值
3. **API调用** → 批量更新后端数据
4. **响应处理** → 更新本地状态，显示反馈

### 排序算法
```typescript
// 计算新的排序值
function calculateSortOrder(
  draggedIndex: number,
  targetIndex: number,
  tasks: Task[]
): number {
  if (targetIndex === 0) {
    return tasks[0].sort_order - 1000
  }
  
  if (targetIndex === tasks.length - 1) {
    return tasks[tasks.length - 1].sort_order + 1000
  }
  
  const prevOrder = tasks[targetIndex - 1].sort_order
  const nextOrder = tasks[targetIndex].sort_order
  return Math.floor((prevOrder + nextOrder) / 2)
}
```

### 错误处理策略
1. **网络错误** - 恢复原始顺序，显示重试选项
2. **权限错误** - 显示权限不足提示
3. **数据冲突** - 重新获取最新数据，提示用户

---

## 🧪 测试计划

### 单元测试
- [ ] 拖拽组件渲染测试
- [ ] 排序算法逻辑测试
- [ ] API调用测试
- [ ] 错误处理测试

### 集成测试
- [ ] 拖拽操作端到端测试
- [ ] 多用户并发排序测试
- [ ] 移动端触摸测试
- [ ] 性能压力测试

### 用户测试
- [ ] 拖拽交互体验测试
- [ ] 移动端可用性测试
- [ ] 无障碍访问测试

---

## 📚 参考文档

### 技术文档
- [vue3-draggable-next 官方文档](https://github.com/anish2690/vue-draggable-next)
- [Quasar Framework 拖拽组件](https://quasar.dev/vue-components/intersection)
- [Django REST Framework 批量更新](https://www.django-rest-framework.org/api-guide/viewsets/#custom-viewset-actions)

### 项目文档
- [LingTaskFlow 架构设计文档](./ling_task_flow_architecture.md)
- [任务管理API规范](./ling_task_flow_pro.md#api-接口规范)
- [前端组件设计规范](./development_tasks.md#第四阶段任务管理前端界面)

### 相关报告
- [开发进度汇总报告](../report/development_progress_summary_2025_08_07.md)
- [任务列表技术重构报告](../report/task-list-tech-redesign-report.md)

---

## ✅ 验收标准

### 功能验收
- [ ] 用户可以通过拖拽重新排列任务顺序
- [ ] 拖拽操作有清晰的视觉反馈
- [ ] 排序结果正确保存到后端
- [ ] 页面刷新后排序保持不变
- [ ] 支持移动端触摸拖拽

### 性能验收
- [ ] 拖拽操作响应时间 < 100ms
- [ ] 100个任务时拖拽仍然流畅
- [ ] 批量更新API响应时间 < 500ms
- [ ] 内存使用无明显增长

### 兼容性验收
- [ ] 支持Chrome、Firefox、Safari、Edge
- [ ] 支持iOS Safari、Android Chrome
- [ ] 支持触摸屏和鼠标操作
- [ ] 支持键盘辅助操作

---

## 🚀 部署计划

### 开发环境测试
1. 本地开发环境功能测试
2. 多浏览器兼容性测试
3. 移动端模拟器测试

### 预生产环境
1. 集成测试环境部署
2. 性能压力测试
3. 用户体验测试

### 生产环境发布
1. 数据库迁移执行
2. 前后端代码部署
3. 功能验证和监控

---

## 📈 后续优化计划

### 短期优化 (1周内)
- 添加拖拽操作的撤销/重做功能
- 优化大量任务时的虚拟滚动
- 添加拖拽操作的快捷键支持

### 中期优化 (1个月内)
- 实现跨状态拖拽 (TODO → IN_PROGRESS)
- 添加拖拽排序的历史记录
- 支持多选任务批量拖拽

### 长期优化 (3个月内)
- 实现智能排序建议
- 添加拖拽操作的数据分析
- 支持自定义拖拽规则

---

## 🎯 成功指标

### 用户体验指标
- 拖拽操作成功率 > 95%
- 用户满意度评分 > 4.5/5
- 拖拽功能使用率 > 60%

### 技术指标
- 拖拽响应时间 < 100ms
- API成功率 > 99%
- 错误恢复率 > 95%

### 业务指标
- 任务管理效率提升 20%
- 用户活跃度提升 15%
- 功能完成度达到 80%

---

**任务创建时间**: 2025年8月9日  
**预计开始时间**: 2025年8月9日  
**预计完成时间**: 2025年8月12日  
**任务状态**: 待开始  
**优先级**: P1 (高优先级)

---

_本文档将随着开发进度持续更新_
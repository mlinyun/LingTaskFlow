<template>
  <div class="draggable-task-list">
    <!-- 拖拽提示 -->
    <div v-if="isDragging" class="drag-hint">
      <q-icon name="drag_indicator" size="sm" />
      <span>拖拽任务卡片来重新排序</span>
    </div>

    <!-- 拖拽任务列表 -->
    <draggable
      v-model="localTasks"
      item-key="id"
      :animation="200"
      :disabled="loading || tasks.length === 0"
      ghost-class="task-ghost"
      chosen-class="task-chosen"
      drag-class="task-drag"
      handle=".drag-handle"
      @start="onDragStart"
      @end="onDragEnd"
      @change="onDragChange"
    >
      <template #item="{ element: task, index }">
        <div class="draggable-task-item" :key="task.id">
          <!-- 拖拽手柄 -->
          <div class="drag-handle" :class="{ 'drag-handle-disabled': loading }">
            <q-icon 
              name="drag_indicator" 
              size="sm" 
              :color="loading ? 'grey-5' : 'primary'"
            />
          </div>

          <!-- 任务卡片 -->
          <div class="task-card-wrapper">
            <CyberTaskCard
              :task="task"
              :dragging="isDragging"
              :index="index"
              @edit="$emit('edit', task)"
              @delete="$emit('delete', task.id)"
              @status-change="$emit('status-change', task.id, $event)"
              @view="$emit('view', task)"
            />
          </div>
        </div>
      </template>

      <!-- 空状态 -->
      <template #footer>
        <div v-if="tasks.length === 0" class="empty-state">
          <q-icon name="inbox" size="xl" color="grey-5" />
          <p class="text-grey-6 q-mt-md">暂无任务</p>
        </div>
      </template>
    </draggable>

    <!-- 保存状态指示器 -->
    <div v-if="saving" class="saving-indicator">
      <q-spinner color="primary" size="sm" />
      <span class="q-ml-sm">正在保存排序...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useQuasar } from 'quasar'
import draggable from 'vue3-draggable-next'
import CyberTaskCard from './CyberTaskCard.vue'
import type { Task } from '../../types/task'
import { useTaskStore } from '../../stores/task'

// Props
interface Props {
  tasks: Task[]
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

// Emits
interface Emits {
  (e: 'edit', task: Task): void
  (e: 'delete', taskId: string): void
  (e: 'status-change', taskId: string, status: string): void
  (e: 'view', task: Task): void
  (e: 'sort-change', tasks: Task[]): void
}

const emit = defineEmits<Emits>()

// Composables
const $q = useQuasar()
const taskStore = useTaskStore()

// State
const localTasks = ref<Task[]>([])
const isDragging = ref(false)
const saving = ref(false)
const draggedTask = ref<Task | null>(null)

// Watch props.tasks changes
watch(
  () => props.tasks,
  (newTasks) => {
    if (!isDragging.value) {
      localTasks.value = [...newTasks]
    }
  },
  { immediate: true, deep: true }
)

// 拖拽事件类型定义
interface DragEvent {
  oldIndex: number
  newIndex: number
}

// Methods
const onDragStart = (evt: DragEvent) => {
  isDragging.value = true
  const task = localTasks.value[evt.oldIndex]
  if (task) {
    draggedTask.value = task
  }
  
  // 添加拖拽开始的视觉反馈
  document.body.classList.add('dragging-active')
  
  console.log('拖拽开始:', draggedTask.value?.title)
}

const onDragEnd = async (evt: DragEvent) => {
  isDragging.value = false
  document.body.classList.remove('dragging-active')
  
  const { oldIndex, newIndex } = evt
  
  // 如果位置没有变化，不需要更新
  if (oldIndex === newIndex) {
    draggedTask.value = null
    return
  }
  
  console.log(`任务从位置 ${oldIndex} 移动到 ${newIndex}`)
  
  try {
    await updateTasksOrder()
    
    // 通知父组件排序已更改
    emit('sort-change', localTasks.value)
    
    $q.notify({
      type: 'positive',
      message: '任务排序已更新',
      timeout: 2000,
      position: 'top'
    })
  } catch (error) {
    console.error('更新任务排序失败:', error)
    
    // 恢复原始顺序
    localTasks.value = [...props.tasks]
    
    $q.notify({
      type: 'negative',
      message: '排序更新失败，已恢复原始顺序',
      timeout: 3000,
      position: 'top'
    })
  } finally {
    draggedTask.value = null
  }
}

const onDragChange = (evt: DragEvent) => {
  // 可以在这里添加拖拽过程中的实时反馈
  console.log('拖拽变化:', evt)
}

const updateTasksOrder = async () => {
  if (!localTasks.value.length) return
  
  saving.value = true
  
  try {
    // 计算新的排序值
    const tasksWithNewOrder = localTasks.value.map((task, index) => ({
      id: task.id,
      sort_order: index + 1
    }))
    
    // 调用API更新排序
    await taskStore.updateTasksOrder(tasksWithNewOrder)
    
    console.log('任务排序更新成功')
  } catch (error) {
    console.error('更新任务排序失败:', error)
    throw error
  } finally {
    saving.value = false
  }
}

// 键盘快捷键支持
const moveTaskUp = (index: number) => {
  if (index > 0) {
    const task = localTasks.value[index]
    if (task) {
      localTasks.value.splice(index, 1)
      localTasks.value.splice(index - 1, 0, task)
      updateTasksOrder()
    }
  }
}

const moveTaskDown = (index: number) => {
  if (index < localTasks.value.length - 1) {
    const task = localTasks.value[index]
    if (task) {
      localTasks.value.splice(index, 1)
      localTasks.value.splice(index + 1, 0, task)
      updateTasksOrder()
    }
  }
}

// 暴露方法给父组件
defineExpose({
  moveTaskUp,
  moveTaskDown
})
</script>

<style lang="scss" scoped>
.draggable-task-list {
  position: relative;
  min-height: 200px;
}

.drag-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
  margin-bottom: 16px;
  background: rgba(var(--q-primary), 0.1);
  border: 2px dashed rgba(var(--q-primary), 0.3);
  border-radius: 8px;
  color: var(--q-primary);
  font-size: 14px;
  animation: pulse 2s infinite;

  .q-icon {
    margin-right: 8px;
  }
}

.draggable-task-item {
  display: flex;
  align-items: stretch;
  margin-bottom: 16px;
  position: relative;
  transition: all 0.3s ease;

  &:hover {
    .drag-handle {
      opacity: 1;
      transform: translateX(0);
    }
  }
}

.drag-handle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  margin-right: 12px;
  cursor: grab;
  opacity: 0.6;
  transform: translateX(-4px);
  transition: all 0.2s ease;
  border-radius: 4px;
  background: rgba(var(--q-primary), 0.1);

  &:hover {
    background: rgba(var(--q-primary), 0.2);
    opacity: 1;
  }

  &:active {
    cursor: grabbing;
  }

  &.drag-handle-disabled {
    cursor: not-allowed;
    opacity: 0.3;
    background: rgba(0, 0, 0, 0.05);
  }
}

.task-card-wrapper {
  flex: 1;
  min-width: 0;
}

// 拖拽状态样式
:deep(.task-ghost) {
  opacity: 0.5;
  background: rgba(var(--q-primary), 0.1);
  border: 2px dashed rgba(var(--q-primary), 0.5);
  transform: scale(0.98);

  .cyber-task-card {
    background: transparent !important;
    box-shadow: none !important;
  }
}

:deep(.task-chosen) {
  transform: scale(1.02);
  box-shadow: 0 8px 32px rgba(0, 255, 255, 0.3);
  z-index: 1000;

  .drag-handle {
    opacity: 1;
    background: rgba(var(--q-primary), 0.3);
  }
}

:deep(.task-drag) {
  transform: rotate(2deg) scale(1.05);
  opacity: 0.9;
  z-index: 1001;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.saving-indicator {
  position: fixed;
  top: 80px;
  right: 20px;
  display: flex;
  align-items: center;
  padding: 8px 16px;
  background: rgba(var(--q-primary), 0.9);
  color: white;
  border-radius: 20px;
  font-size: 14px;
  z-index: 2000;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

// 全局拖拽状态
:global(.dragging-active) {
  cursor: grabbing !important;
  
  * {
    cursor: grabbing !important;
  }
}

// 动画
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .drag-handle {
    width: 28px;
    margin-right: 8px;
    opacity: 1;
    transform: none;
  }

  .draggable-task-item {
    margin-bottom: 12px;
  }

  .drag-hint {
    font-size: 13px;
    padding: 10px;
  }
}
</style>
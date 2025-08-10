<template>
  <q-page class="task-list-page">
    <div class="q-pa-md">
      <div class="row q-mb-md">
        <div class="col">
          <h4 class="q-my-none">任务列表</h4>
        </div>
        <div class="col-auto">
          <q-btn
            color="primary"
            icon="add"
            label="新建任务"
            @click="showCreateDialog = true"
          />
        </div>
      </div>

      <!-- 任务过滤面板 -->
      <TaskFilterPanel
        :search-query="searchQuery"
        :status-filter="filterStatus"
        :priority-filter="filterPriority"
        :sort-by="'created_at'"
        @update:search-query="searchQuery = $event"
        @update:status-filter="filterStatus = $event"
        @update:priority-filter="filterPriority = $event"
        @clear-filters="resetFilters"
      />

      <!-- 任务统计 -->
      <TaskStatistics 
        :total-tasks="filteredTasks.length"
        :active-tasks="filteredTasks.filter(t => !t.is_deleted && t.status !== 'COMPLETED').length"
        :completed-tasks="filteredTasks.filter(t => t.status === 'COMPLETED').length"
        class="q-mb-md" 
      />

      <!-- 可拖拽任务列表 -->
      <DraggableTaskList
        :tasks="filteredTasks"
        :loading="loading"
        @sort-change="handleUpdateOrder"
        @edit="handleEditTask"
        @delete="handleDeleteTask"
        @status-change="handleToggleStatus"
      />

      <!-- 创建/编辑任务对话框 -->
      <TaskDialogForm
        v-model="showCreateDialog"
        :task="editingTask"
        @save="handleSaveTask"
        @cancel="handleCancelEdit"
      />

      <!-- 任务详情查看对话框 -->
      <TaskViewDialog
        v-model="showViewDialog"
        :task="viewingTask"
      />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useTaskStore } from 'src/stores/task'
import type { Task, TaskStatus, TaskPriority } from 'src/types/task'
import DraggableTaskList from 'src/components/task-list/DraggableTaskList.vue'
import TaskFilterPanel from 'src/components/task-list/TaskFilterPanel.vue'
import TaskStatistics from 'src/components/task-list/TaskStatistics.vue'
import TaskDialogForm from 'src/components/task-list/TaskDialogForm.vue'
import TaskViewDialog from 'src/components/task-list/TaskViewDialog.vue'

const taskStore = useTaskStore()

// 响应式数据
const loading = ref(false)
const showCreateDialog = ref(false)
const showViewDialog = ref(false)
const editingTask = ref<Task | null>(null)
const viewingTask = ref<Task | null>(null)

// 过滤条件
const filterStatus = ref<TaskStatus | null>(null)
const filterPriority = ref<TaskPriority | null>(null)
const searchQuery = ref('')

// 计算属性
const filteredTasks = computed(() => {
  let tasks = taskStore.tasks

  // 状态过滤
  if (filterStatus.value) {
    tasks = tasks.filter(task => task.status === filterStatus.value)
  }

  // 优先级过滤
  if (filterPriority.value) {
    tasks = tasks.filter(task => task.priority === filterPriority.value)
  }

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    tasks = tasks.filter(task =>
      task.title.toLowerCase().includes(query) ||
      (task.description ? task.description.toLowerCase().includes(query) : false) ||
      task.tags.toLowerCase().includes(query)
    )
  }

  return tasks
})

// 方法
const resetFilters = () => {
  filterStatus.value = null
  filterPriority.value = null
  searchQuery.value = ''
}

const handleUpdateOrder = async (tasks: Task[]) => {
  try {
    loading.value = true
    // 转换为API需要的格式
    const tasksWithOrder = tasks.map((task, index) => ({
      id: task.id,
      sort_order: index + 1
    }))
    await taskStore.updateTasksOrder(tasksWithOrder)
  } catch (error) {
    console.error('更新任务顺序失败:', error)
  } finally {
    loading.value = false
  }
}

const handleEditTask = (task: Task) => {
  editingTask.value = task
  showCreateDialog.value = true
}

const handleDeleteTask = async (taskId: string) => {
  try {
    loading.value = true
    await taskStore.deleteTask(taskId)
  } catch (error) {
    console.error('删除任务失败:', error)
  } finally {
    loading.value = false
  }
}

const handleToggleStatus = async (taskId: string, status: string) => {
  try {
    await taskStore.updateTask(taskId, { status: status as TaskStatus })
  } catch (error) {
    console.error('更新任务状态失败:', error)
  }
}

const handleSaveTask = async (taskData: Partial<Task>) => {
  try {
    loading.value = true
    if (editingTask.value) {
      await taskStore.updateTask(editingTask.value.id, taskData)
    } else {
      await taskStore.createTask(taskData as Omit<Task, 'id' | 'created_at' | 'updated_at'>)
    }
    handleCancelEdit()
  } catch (error) {
    console.error('保存任务失败:', error)
  } finally {
    loading.value = false
  }
}

const handleCancelEdit = () => {
  editingTask.value = null
  showCreateDialog.value = false
}

// 生命周期
onMounted(async () => {
  try {
    loading.value = true
    await taskStore.fetchTasks()
  } catch (error) {
    console.error('获取任务列表失败:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.task-list-page {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
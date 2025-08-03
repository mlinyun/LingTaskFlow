<template>
    <q-drawer v-model="drawerOpen" show-if-above bordered class="bg-grey-1" :width="280">
        <q-list padding>
            <!-- 任务统计概览 -->
            <q-item-label header class="text-weight-bold text-primary"> 任务概览 </q-item-label>

            <q-item v-if="authStore.user?.profile" class="q-mb-md">
                <q-item-section>
                    <div class="row q-gutter-sm">
                        <q-card flat bordered class="col">
                            <q-card-section class="text-center q-pa-sm">
                                <div class="text-h6 text-primary">
                                    {{ authStore.user.profile.task_count }}
                                </div>
                                <div class="text-caption">总任务</div>
                            </q-card-section>
                        </q-card>
                        <q-card flat bordered class="col">
                            <q-card-section class="text-center q-pa-sm">
                                <div class="text-h6 text-positive">
                                    {{ authStore.user.profile.completed_task_count }}
                                </div>
                                <div class="text-caption">已完成</div>
                            </q-card-section>
                        </q-card>
                    </div>
                    <q-linear-progress
                        :value="authStore.completionRate / 100"
                        color="positive"
                        class="q-mt-sm"
                        size="8px"
                        rounded
                    />
                    <div class="text-center text-caption q-mt-xs">
                        完成率 {{ authStore.completionRate }}%
                    </div>
                </q-item-section>
            </q-item>

            <q-separator class="q-mb-md" />

            <!-- 导航菜单 -->
            <q-item-label header class="text-weight-bold text-primary"> 导航菜单 </q-item-label>

            <navigation-link v-for="link in navigationLinks" :key="link.title" v-bind="link" />
        </q-list>
    </q-drawer>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useAuthStore } from 'stores/auth';
import NavigationLink from 'components/NavigationLink.vue';

// Props
interface Props {
    modelValue: boolean;
    navigationLinks: Array<{
        title: string;
        caption: string;
        icon: string;
        link: string;
        color: string;
    }>;
}

const props = defineProps<Props>();

// Emits
const emit = defineEmits<{
    'update:modelValue': [value: boolean];
}>();

// Store
const authStore = useAuthStore();

// Computed
const drawerOpen = computed({
    get: () => props.modelValue,
    set: (value: boolean) => emit('update:modelValue', value),
});
</script>

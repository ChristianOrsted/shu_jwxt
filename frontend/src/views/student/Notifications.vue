<script setup>
import { ref, onMounted } from 'vue'
import { studentApi } from '@/api/services'

const loading = ref(false)
const list = ref([])

const typeColor = {
    选课: 'success',
    退课: 'info',
    成绩: 'primary',
    重修: 'warning',
    审批: 'primary',
}

async function load() {
    loading.value = true
    try {
        list.value = await studentApi.notifications()
    } finally {
        loading.value = false
    }
}

function markRead(item) {
    item.is_read = true
}
onMounted(load)
</script>

<template>
    <div>
        <div class="page-header">
            <div>
                <h2>消息通知</h2>
                <div class="subtitle">选课、退课、成绩发布、重修提醒等系统消息</div>
            </div>
        </div>

        <el-card v-loading="loading" shadow="never">
            <el-empty v-if="!list.length" description="暂无通知" />
            <div v-for="item in list" :key="item.notification_id" class="notice" @click="markRead(item)">
                <div class="notice-head">
                    <el-badge :is-dot="!item.is_read">
                        <span class="notice-title">{{ item.title }}</span>
                    </el-badge>
                    <el-tag size="small" :type="typeColor[item.notification_type] || 'info'" effect="plain">
                        {{ item.notification_type }}
                    </el-tag>
                    <span class="notice-time">{{ item.created_at.replace('T', ' ') }}</span>
                </div>
                <div class="notice-body">{{ item.content }}</div>
            </div>
        </el-card>
    </div>
</template>

<style scoped>
.notice {
    padding: 14px 6px;
    border-bottom: 1px solid #f0f0f0;
    cursor: pointer;
}
.notice:last-child {
    border-bottom: none;
}
.notice-head {
    display: flex;
    align-items: center;
    gap: 12px;
}
.notice-title {
    font-weight: 600;
    font-size: 15px;
}
.notice-time {
    margin-left: auto;
    color: #b0b3b8;
    font-size: 12px;
}
.notice-body {
    color: #5a5f66;
    margin-top: 6px;
    padding-left: 2px;
}
</style>

<script setup>
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api/services'

const loading = ref(false)
const list = ref([])

async function load() {
    loading.value = true
    try {
        list.value = await adminApi.classrooms()
    } finally {
        loading.value = false
    }
}
onMounted(load)
</script>

<template>
    <div>
        <div class="page-header">
            <div>
                <h2>教室资源管理</h2>
                <div class="subtitle">维护教室、容量与可用状态，用于排课和扩容判断</div>
            </div>
        </div>

        <el-table :data="list" v-loading="loading" border stripe>
            <el-table-column prop="classroom_id" label="编号" width="80" align="center" />
            <el-table-column prop="building" label="教学楼" min-width="160" />
            <el-table-column prop="room_no" label="教室号" width="120" />
            <el-table-column prop="capacity" label="容量" width="100" align="center" />
            <el-table-column label="状态" width="110" align="center">
                <template #default="{ row }">
                    <el-tag :type="row.status === '可用' ? 'success' : 'danger'">{{ row.status }}</el-tag>
                </template>
            </el-table-column>
        </el-table>
    </div>
</template>

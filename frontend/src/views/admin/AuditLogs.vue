<script setup>
import { ref, computed, onMounted } from 'vue'
import { adminApi } from '@/api/services'

const loading = ref(false)
const logs = ref([])
const keyword = ref('')

const filtered = computed(() =>
    logs.value.filter((l) => !keyword.value || `${l.operation_type}${l.target_type}${l.reason}`.includes(keyword.value)),
)

const opType = {
    强制退课: 'danger',
    发布成绩: 'success',
    审批通过: 'primary',
    取消开课: 'warning',
}

async function load() {
    loading.value = true
    try {
        logs.value = await adminApi.auditLogs()
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
                <h2>操作日志</h2>
                <div class="subtitle">审计管理员强制选课/退课、成绩修改、课程取消、审批等关键操作</div>
            </div>
        </div>

        <div class="toolbar">
            <el-input v-model="keyword" placeholder="搜索操作类型/对象/原因" :prefix-icon="'Search'" clearable style="width: 260px" />
        </div>

        <el-table :data="filtered" v-loading="loading" border stripe>
            <el-table-column prop="log_id" label="日志号" width="80" align="center" />
            <el-table-column prop="operator" label="操作人" width="110" />
            <el-table-column label="操作类型" width="120" align="center">
                <template #default="{ row }"><el-tag :type="opType[row.operation_type] || 'info'">{{ row.operation_type }}</el-tag></template>
            </el-table-column>
            <el-table-column prop="target_type" label="操作对象" width="120" />
            <el-table-column prop="target_id" label="对象ID" width="90" align="center" />
            <el-table-column prop="reason" label="原因 / 说明" min-width="240" />
            <el-table-column label="操作时间" width="180">
                <template #default="{ row }">{{ row.created_at.replace('T', ' ') }}</template>
            </el-table-column>
        </el-table>
    </div>
</template>

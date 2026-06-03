<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '@/api/services'

const loading = ref(false)
const list = ref([])

async function load() {
    loading.value = true
    try {
        list.value = await adminApi.retake()
    } finally {
        loading.value = false
    }
}

function arrange(row) {
    row.has_retake_class = true
    ElMessage.success(`已为《${row.course_name}》安排重修班`)
}
onMounted(load)
</script>

<template>
    <div>
        <div class="page-header">
            <div>
                <h2>重修管理</h2>
                <div class="subtitle">查看挂科名单、待重修人数，按需安排重修班</div>
            </div>
        </div>

        <el-table :data="list" v-loading="loading" border stripe>
            <el-table-column prop="course_name" label="课程" min-width="160" />
            <el-table-column prop="failed_count" label="挂科人数" width="110" align="center" />
            <el-table-column prop="pending_count" label="待重修" width="100" align="center">
                <template #default="{ row }"><span class="capacity-full">{{ row.pending_count }}</span></template>
            </el-table-column>
            <el-table-column prop="retaking_count" label="重修中" width="100" align="center" />
            <el-table-column prop="passed_count" label="重修通过" width="100" align="center">
                <template #default="{ row }"><span class="capacity-ok">{{ row.passed_count }}</span></template>
            </el-table-column>
            <el-table-column label="重修班" width="120" align="center">
                <template #default="{ row }">
                    <el-tag :type="row.has_retake_class ? 'success' : 'info'">{{ row.has_retake_class ? '已开设' : '未开设' }}</el-tag>
                </template>
            </el-table-column>
            <el-table-column label="操作" width="140" align="center" fixed="right">
                <template #default="{ row }">
                    <el-button size="small" type="primary" :disabled="row.has_retake_class" @click="arrange(row)">
                        安排重修班
                    </el-button>
                </template>
            </el-table-column>
        </el-table>
    </div>
</template>

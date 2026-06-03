<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi } from '@/api/services'

const loading = ref(false)
const list = ref([])

async function load() {
    loading.value = true
    try {
        list.value = await adminApi.approvals()
    } finally {
        loading.value = false
    }
}

async function handle(row, result) {
    try {
        const { value } = await ElMessageBox.prompt(
            `请填写审批意见（${result}）`,
            result === '通过' ? '同意申请' : '驳回申请',
            { confirmButtonText: '确认', cancelButtonText: '取消', inputType: 'textarea' },
        )
        await adminApi.approve(row.request_id, result, value)
        list.value = list.value.filter((r) => r.request_id !== row.request_id)
        ElMessage.success(`已${result}该申请`)
    } catch {
        // 取消
    }
}
onMounted(load)
</script>

<template>
    <div>
        <div class="page-header">
            <div>
                <h2>申请审批</h2>
                <div class="subtitle">审批教师的开课/扩容/调课/停课/成绩修改申请，含冲突检测结果</div>
            </div>
            <el-tag type="warning" size="large">待审批 {{ list.length }} 项</el-tag>
        </div>

        <el-table :data="list" v-loading="loading" border stripe>
            <el-table-column prop="teacher_name" label="申请人" width="90" />
            <el-table-column prop="request_type" label="类型" width="120">
                <template #default="{ row }"><el-tag effect="plain">{{ row.request_type }}</el-tag></template>
            </el-table-column>
            <el-table-column prop="course_name" label="课程" min-width="130" />
            <el-table-column prop="content" label="申请内容" min-width="170" />
            <el-table-column prop="conflict_check_result" label="冲突检测" min-width="200">
                <template #default="{ row }">
                    <span :style="{ color: row.conflict_check_result.includes('无冲突') || row.conflict_check_result.includes('充足') ? '#52c41a' : '#5a5f66' }">
                        {{ row.conflict_check_result }}
                    </span>
                </template>
            </el-table-column>
            <el-table-column label="操作" width="180" align="center" fixed="right">
                <template #default="{ row }">
                    <el-button size="small" type="success" @click="handle(row, '通过')">通过</el-button>
                    <el-button size="small" type="danger" @click="handle(row, '驳回')">驳回</el-button>
                </template>
            </el-table-column>
        </el-table>
        <el-empty v-if="!loading && !list.length" description="暂无待审批申请" />
    </div>
</template>

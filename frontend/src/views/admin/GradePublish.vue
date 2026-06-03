<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi } from '@/api/services'

const loading = ref(false)
const list = ref([])

async function load() {
    loading.value = true
    try {
        list.value = await adminApi.gradePublish()
    } finally {
        loading.value = false
    }
}

async function publish(row) {
    try {
        await ElMessageBox.confirm(
            `确认发布《${row.course_name}》的成绩吗？发布后学生即可查看，并自动生成挂科/重修记录。`,
            '发布成绩',
            { confirmButtonText: '确认发布', cancelButtonText: '取消', type: 'warning' },
        )
        await adminApi.publishGrade(row.offering_id)
        row.score_status = '已发布'
        row.can_publish = false
        ElMessage.success('成绩已发布')
    } catch (e) {
        if (e !== 'cancel') ElMessage.error(e.message || '发布失败')
    }
}
onMounted(load)
</script>

<template>
    <div>
        <div class="page-header">
            <div>
                <h2>成绩发布</h2>
                <div class="subtitle">审核教师已提交的成绩并发布，未发布前学生不可见</div>
            </div>
        </div>

        <el-table :data="list" v-loading="loading" border stripe>
            <el-table-column prop="course_name" label="课程" min-width="140" />
            <el-table-column prop="teacher_name" label="任课教师" width="110" />
            <el-table-column prop="term_name" label="学期" min-width="180" />
            <el-table-column label="录入进度" width="120" align="center">
                <template #default="{ row }">{{ row.submitted_count }}/{{ row.total_count }}</template>
            </el-table-column>
            <el-table-column label="成绩状态" width="110" align="center">
                <template #default="{ row }">
                    <el-tag :type="row.score_status === '已提交' ? 'warning' : row.score_status === '已发布' ? 'success' : 'info'">
                        {{ row.score_status }}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column label="操作" width="140" align="center" fixed="right">
                <template #default="{ row }">
                    <el-button size="small" type="primary" :disabled="!row.can_publish" @click="publish(row)">
                        发布
                    </el-button>
                </template>
            </el-table-column>
        </el-table>
    </div>
</template>

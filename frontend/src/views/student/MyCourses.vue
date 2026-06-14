<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { studentApi } from '@/api/services'
import { term, loadCurrentTerm } from '@/store/term'

const loading = ref(false)
const list = ref([])

const totalCredits = computed(() =>
    list.value.filter((c) => c.status === '已选').reduce((s, c) => s + c.credits, 0),
)

async function load() {
    loading.value = true
    try {
        list.value = await studentApi.myCourses()
    } finally {
        loading.value = false
    }
}

async function drop(row) {
    if (!row.can_drop) {
        ElMessage.warning('该课程已锁定（重修班/已录成绩/超过退课时间），不能退课')
        return
    }
    try {
        await ElMessageBox.confirm(
            `确认退选《${row.course_name}》吗？退课后将释放容量。`,
            '退课确认',
            { confirmButtonText: '确认退课', cancelButtonText: '取消', type: 'warning' },
        )
        await studentApi.drop(row.offering_id)
        ElMessage.success('退课成功')
        row.status = '已退'
    } catch (e) {
        if (e !== 'cancel') ElMessage.error(e.message || '退课失败')
    }
}
onMounted(() => {
    load()
    loadCurrentTerm()
})
</script>

<template>
    <div>
        <div class="page-header">
            <div>
                <h2>已选课程</h2>
                <div class="subtitle">{{ term.current?.term_name || '当前学期' }}</div>
            </div>
            <el-tag type="primary" size="large">已选学分合计：{{ totalCredits }}</el-tag>
        </div>

        <el-table :data="list" v-loading="loading" border stripe>
            <el-table-column prop="course_code" label="课程号" width="90" />
            <el-table-column label="课程名称" min-width="160">
                <template #default="{ row }">
                    {{ row.course_name }}
                    <el-tag v-if="row.is_retake" size="small" type="warning" effect="plain" style="margin-left: 6px">重修</el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="credits" label="学分" width="70" />
            <el-table-column prop="teacher_name" label="教师" width="90" />
            <el-table-column prop="schedule_text" label="上课时间" min-width="170" />
            <el-table-column prop="location" label="地点" width="140" />
            <el-table-column prop="enroll_time" label="选课时间" width="170">
                <template #default="{ row }">{{ row.enroll_time.replace('T', ' ') }}</template>
            </el-table-column>
            <el-table-column label="状态" width="90" align="center">
                <template #default="{ row }">
                    <el-tag :type="row.status === '已选' ? 'success' : 'info'">{{ row.status }}</el-tag>
                </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center" fixed="right">
                <template #default="{ row }">
                    <el-button
                        v-if="row.status === '已选'"
                        type="danger"
                        size="small"
                        :disabled="!row.can_drop"
                        @click="drop(row)"
                    >
                        退课
                    </el-button>
                    <span v-else>—</span>
                </template>
            </el-table-column>
        </el-table>
    </div>
</template>

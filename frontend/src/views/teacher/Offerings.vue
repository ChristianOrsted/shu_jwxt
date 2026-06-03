<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { teacherApi } from '@/api/services'

const router = useRouter()
const loading = ref(false)
const list = ref([])

const statusType = {
    开放选课: 'success',
    关闭选课: 'info',
    待审批: 'warning',
    已结课: 'info',
    已取消: 'danger',
}

async function load() {
    loading.value = true
    try {
        list.value = await teacherApi.offerings()
    } finally {
        loading.value = false
    }
}

function viewRoster() {
    router.push('/teacher/roster')
}
function inputGrade() {
    router.push('/teacher/grade-input')
}
onMounted(load)
</script>

<template>
    <div>
        <div class="page-header">
            <div>
                <h2>授课任务</h2>
                <div class="subtitle">本人承担的全部教学班（含历史学期）</div>
            </div>
        </div>

        <el-table :data="list" v-loading="loading" border stripe>
            <el-table-column prop="term_name" label="学年学期" min-width="180" />
            <el-table-column prop="course_name" label="课程" min-width="130">
                <template #default="{ row }">
                    {{ row.course_name }}
                    <el-tag v-if="row.is_retake_class" size="small" type="warning" effect="plain">重修班</el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="teaching_class_name" label="教学班" min-width="150" />
            <el-table-column prop="schedule_text" label="上课时间" min-width="170" />
            <el-table-column prop="location" label="地点" width="90" />
            <el-table-column label="容量" width="100" align="center">
                <template #default="{ row }">
                    <span :class="row.selected_count >= row.capacity ? 'capacity-full' : 'capacity-ok'">
                        {{ row.selected_count }}/{{ row.capacity }}
                    </span>
                </template>
            </el-table-column>
            <el-table-column label="状态" width="100" align="center">
                <template #default="{ row }">
                    <el-tag :type="statusType[row.status] || 'info'">{{ row.status }}</el-tag>
                </template>
            </el-table-column>
            <el-table-column label="操作" width="180" align="center" fixed="right">
                <template #default>
                    <el-button size="small" @click="viewRoster">名单</el-button>
                    <el-button size="small" type="primary" @click="inputGrade">录成绩</el-button>
                </template>
            </el-table-column>
        </el-table>
    </div>
</template>

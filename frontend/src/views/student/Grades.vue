<script setup>
import { ref, onMounted } from 'vue'
import { studentApi } from '@/api/services'

const loading = ref(false)
const grades = ref([])
const avg = ref({})

async function load() {
    loading.value = true
    try {
        const [g, a] = await Promise.all([studentApi.grades(), studentApi.averageScore()])
        grades.value = g
        avg.value = a
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
                <h2>成绩查询</h2>
                <div class="subtitle">仅显示已发布成绩</div>
            </div>
        </div>

        <el-row :gutter="16" style="margin-bottom: 16px">
            <el-col :span="6">
                <el-card class="stat-card" shadow="never">
                    <div class="num">{{ avg.simple_average }}</div>
                    <div class="label">普通平均分</div>
                </el-card>
            </el-col>
            <el-col :span="6">
                <el-card class="stat-card" shadow="never">
                    <div class="num">{{ avg.weighted_average }}</div>
                    <div class="label">学分加权平均分</div>
                </el-card>
            </el-col>
            <el-col :span="6">
                <el-card class="stat-card" shadow="never">
                    <div class="num">{{ avg.average_gpa }}</div>
                    <div class="label">平均绩点 GPA</div>
                </el-card>
            </el-col>
            <el-col :span="6">
                <el-card class="stat-card" shadow="never">
                    <div class="num">{{ avg.earned_credits }}/{{ avg.total_credits }}</div>
                    <div class="label">已获 / 修读学分</div>
                </el-card>
            </el-col>
        </el-row>

        <el-table :data="grades" v-loading="loading" border stripe>
            <el-table-column prop="term_name" label="学年学期" min-width="190" />
            <el-table-column prop="course_name" label="课程名称" min-width="150" />
            <el-table-column prop="credits" label="学分" width="70" />
            <el-table-column prop="teacher_name" label="教师" width="90" />
            <el-table-column label="总评成绩" width="90" align="center">
                <template #default="{ row }">
                    <span :class="row.is_passed ? '' : 'capacity-full'">{{ row.total_score }}</span>
                </template>
            </el-table-column>
            <el-table-column prop="grade_point" label="绩点" width="70" align="center" />
            <el-table-column label="是否通过" width="90" align="center">
                <template #default="{ row }">
                    <el-tag :type="row.is_passed ? 'success' : 'danger'">{{ row.is_passed ? '通过' : '未通过' }}</el-tag>
                </template>
            </el-table-column>
            <el-table-column label="重修" width="70" align="center">
                <template #default="{ row }">
                    <el-tag v-if="row.is_retake" type="warning" size="small">重修</el-tag>
                    <span v-else>—</span>
                </template>
            </el-table-column>
            <el-table-column prop="score_status" label="状态" width="90" align="center" />
        </el-table>
    </div>
</template>

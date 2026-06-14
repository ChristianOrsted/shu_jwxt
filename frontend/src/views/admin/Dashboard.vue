<script setup>
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api/services'
import { term, loadCurrentTerm } from '@/store/term'

const loading = ref(false)
const data = ref({ cards: {}, capacity: [] })

async function load() {
    loading.value = true
    try {
        data.value = await adminApi.statistics()
    } finally {
        loading.value = false
    }
}
onMounted(() => {
    load()
    loadCurrentTerm()
})
</script>

<template>
    <div v-loading="loading">
        <div class="page-header">
            <div>
                <h2>系统总览</h2>
                <div class="subtitle">{{ term.current?.term_name || '当前学期' }} · 教务运行概况</div>
            </div>
        </div>

        <el-row :gutter="16" style="margin-bottom: 18px">
            <el-col :span="6">
                <el-card class="stat-card" shadow="never">
                    <div class="num" style="color: #2f54eb">{{ data.cards.total_students }}</div>
                    <div class="label"><el-icon><User /></el-icon> 在校学生</div>
                </el-card>
            </el-col>
            <el-col :span="6">
                <el-card class="stat-card" shadow="never">
                    <div class="num" style="color: #52c41a">{{ data.cards.total_teachers }}</div>
                    <div class="label"><el-icon><Avatar /></el-icon> 在职教师</div>
                </el-card>
            </el-col>
            <el-col :span="6">
                <el-card class="stat-card" shadow="never">
                    <div class="num" style="color: #fa8c16">{{ data.cards.total_courses }}</div>
                    <div class="label"><el-icon><Collection /></el-icon> 课程库课程</div>
                </el-card>
            </el-col>
            <el-col :span="6">
                <el-card class="stat-card" shadow="never">
                    <div class="num" style="color: #eb2f96">{{ data.cards.total_offerings }}</div>
                    <div class="label"><el-icon><Notebook /></el-icon> 本学期开课班</div>
                </el-card>
            </el-col>
        </el-row>

        <el-card shadow="never">
            <template #header><strong>本学期课程容量 / 满员率</strong></template>
            <el-table :data="data.capacity" border>
                <el-table-column prop="course_name" label="课程" min-width="160" />
                <el-table-column prop="teacher_name" label="教师" width="100" />
                <el-table-column label="选课情况" width="120" align="center">
                    <template #default="{ row }">{{ row.selected_count }}/{{ row.capacity }}</template>
                </el-table-column>
                <el-table-column prop="remain" label="剩余名额" width="100" align="center" />
                <el-table-column label="满员率" min-width="220">
                    <template #default="{ row }">
                        <el-progress
                            :percentage="row.fill_rate"
                            :status="row.fill_rate >= 100 ? 'exception' : row.fill_rate >= 80 ? 'warning' : 'success'"
                        />
                    </template>
                </el-table-column>
            </el-table>
        </el-card>
    </div>
</template>

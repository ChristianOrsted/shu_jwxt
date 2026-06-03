<script setup>
import { ref, onMounted } from 'vue'
import { teacherApi } from '@/api/services'

const loading = ref(false)
const stats = ref([])

async function load() {
    loading.value = true
    try {
        stats.value = await teacherApi.gradeStats()
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
                <h2>成绩统计</h2>
                <div class="subtitle">本人各教学班的成绩分布与挂科率</div>
            </div>
        </div>

        <el-card v-for="s in stats" :key="s.offering_id" shadow="never" style="margin-bottom: 16px" v-loading="loading">
            <template #header>
                <strong>{{ s.course_name }} · {{ s.teaching_class_name }}</strong>
            </template>
            <el-row :gutter="16">
                <el-col :span="4"><el-statistic title="选课人数" :value="s.enrolled" /></el-col>
                <el-col :span="4"><el-statistic title="参考人数" :value="s.attended" /></el-col>
                <el-col :span="4"><el-statistic title="及格人数" :value="s.passed" /></el-col>
                <el-col :span="4"><el-statistic title="不及格人数" :value="s.failed" /></el-col>
                <el-col :span="4"><el-statistic title="重修人数" :value="s.retake_count" /></el-col>
                <el-col :span="4"><el-statistic title="挂科率(%)" :value="s.fail_rate" /></el-col>
            </el-row>
            <el-divider />
            <el-row :gutter="16">
                <el-col :span="8"><el-statistic title="平均分" :value="s.avg" /></el-col>
                <el-col :span="8"><el-statistic title="最高分" :value="s.max" /></el-col>
                <el-col :span="8"><el-statistic title="最低分" :value="s.min" /></el-col>
            </el-row>
        </el-card>
        <el-empty v-if="!loading && !stats.length" description="暂无已结课的成绩统计" />
    </div>
</template>

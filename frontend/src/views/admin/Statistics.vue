<script setup>
import { ref, computed, onMounted } from 'vue'
import { adminApi } from '@/api/services'

const loading = ref(false)
const data = ref({ score_distribution: [], retake: [], capacity: [] })

const maxCount = computed(() =>
    Math.max(1, ...data.value.score_distribution.map((d) => d.count)),
)

const barColor = {
    '90-100': '#52c41a',
    '80-89': '#73d13d',
    '70-79': '#40a9ff',
    '60-69': '#faad14',
    '0-59': '#ff4d4f',
}

async function load() {
    loading.value = true
    try {
        data.value = await adminApi.statistics()
    } finally {
        loading.value = false
    }
}
onMounted(load)
</script>

<template>
    <div v-loading="loading">
        <div class="page-header">
            <div>
                <h2>统计分析</h2>
                <div class="subtitle">成绩分布、挂科重修、课程满员率等全局统计</div>
            </div>
        </div>

        <el-row :gutter="16">
            <el-col :span="12">
                <el-card shadow="never">
                    <template #header><strong>全校成绩分布</strong></template>
                    <div class="dist">
                        <div v-for="d in data.score_distribution" :key="d.range" class="dist-row">
                            <span class="dist-label">{{ d.range }}</span>
                            <div class="dist-bar-wrap">
                                <div
                                    class="dist-bar"
                                    :style="{ width: (d.count / maxCount) * 100 + '%', background: barColor[d.range] }"
                                />
                            </div>
                            <span class="dist-count">{{ d.count }} 人</span>
                        </div>
                    </div>
                </el-card>
            </el-col>

            <el-col :span="12">
                <el-card shadow="never">
                    <template #header><strong>挂科与重修统计</strong></template>
                    <el-table :data="data.retake" border size="small">
                        <el-table-column prop="course_name" label="课程" min-width="120" />
                        <el-table-column prop="failed" label="挂科人数" align="center" />
                        <el-table-column prop="pending_retake" label="待重修" align="center" />
                        <el-table-column prop="retaking" label="重修中" align="center" />
                        <el-table-column prop="passed_retake" label="重修通过" align="center" />
                    </el-table>
                </el-card>
            </el-col>
        </el-row>

        <el-card shadow="never" style="margin-top: 16px">
            <template #header><strong>课程满员率排行</strong></template>
            <el-table :data="data.capacity" border>
                <el-table-column prop="course_name" label="课程" min-width="160" />
                <el-table-column prop="teacher_name" label="教师" width="100" />
                <el-table-column label="选课/容量" width="120" align="center">
                    <template #default="{ row }">{{ row.selected_count }}/{{ row.capacity }}</template>
                </el-table-column>
                <el-table-column label="满员率" min-width="240">
                    <template #default="{ row }">
                        <el-progress :percentage="row.fill_rate" :status="row.fill_rate >= 100 ? 'exception' : ''" />
                    </template>
                </el-table-column>
            </el-table>
        </el-card>
    </div>
</template>

<style scoped>
.dist-row {
    display: flex;
    align-items: center;
    margin-bottom: 14px;
    gap: 10px;
}
.dist-label {
    width: 64px;
    text-align: right;
    font-size: 13px;
    color: #5a5f66;
}
.dist-bar-wrap {
    flex: 1;
    background: #f0f2f5;
    border-radius: 4px;
    height: 20px;
    overflow: hidden;
}
.dist-bar {
    height: 100%;
    border-radius: 4px;
    transition: width 0.4s;
}
.dist-count {
    width: 56px;
    font-size: 13px;
}
</style>

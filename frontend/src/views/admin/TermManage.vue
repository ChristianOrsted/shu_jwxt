<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '@/api/services'

const loading = ref(false)
const years = ref([])
const windows = ref([])

const winType = { 选课: 'success', 退课: 'warning', 成绩录入: 'primary', 成绩公布: 'info' }
const winStatus = { 进行中: 'success', 未开始: 'info', 已结束: 'danger' }

async function load() {
    loading.value = true
    try {
        const [t, w] = await Promise.all([adminApi.terms(), adminApi.businessWindows()])
        years.value = t
        windows.value = w
    } finally {
        loading.value = false
    }
}

function setCurrent(term) {
    years.value.forEach((y) => y.terms.forEach((t) => (t.is_current = false)))
    term.is_current = true
    ElMessage.success(`已将「${term.term_name}」设为当前学期`)
}
onMounted(load)
</script>

<template>
    <div v-loading="loading">
        <div class="page-header">
            <div>
                <h2>学年学期管理</h2>
                <div class="subtitle">每个学年包含第一、第二两个学期，并设置当前学期</div>
            </div>
            <el-button type="primary" :icon="'Plus'" @click="ElMessage.info('演示环境：新建学年功能占位')">新建学年</el-button>
        </div>

        <el-card v-for="y in years" :key="y.academic_year_name" shadow="never" style="margin-bottom: 16px">
            <template #header><strong>{{ y.academic_year_name }}</strong></template>
            <el-table :data="y.terms" border>
                <el-table-column prop="term_name" label="学期" min-width="180" />
                <el-table-column prop="term_no" label="学期序号" width="100" align="center" />
                <el-table-column prop="start_date" label="开始日期" width="130" />
                <el-table-column prop="end_date" label="结束日期" width="130" />
                <el-table-column label="当前学期" width="110" align="center">
                    <template #default="{ row }">
                        <el-tag v-if="row.is_current" type="success">当前</el-tag>
                        <span v-else>—</span>
                    </template>
                </el-table-column>
                <el-table-column label="操作" width="140" align="center">
                    <template #default="{ row }">
                        <el-button v-if="!row.is_current" size="small" type="primary" @click="setCurrent(row)">设为当前</el-button>
                    </template>
                </el-table-column>
            </el-table>
        </el-card>

        <el-card shadow="never">
            <template #header><strong>当前学期业务时间窗口</strong></template>
            <el-table :data="windows" border>
                <el-table-column label="业务类型" width="120" align="center">
                    <template #default="{ row }"><el-tag :type="winType[row.window_type]">{{ row.window_type }}</el-tag></template>
                </el-table-column>
                <el-table-column prop="term_name" label="学期" min-width="180" />
                <el-table-column label="开始时间" width="180">
                    <template #default="{ row }">{{ row.start_time.replace('T', ' ') }}</template>
                </el-table-column>
                <el-table-column label="结束时间" width="180">
                    <template #default="{ row }">{{ row.end_time.replace('T', ' ') }}</template>
                </el-table-column>
                <el-table-column label="状态" width="100" align="center">
                    <template #default="{ row }"><el-tag :type="winStatus[row.status]">{{ row.status }}</el-tag></template>
                </el-table-column>
            </el-table>
        </el-card>
    </div>
</template>

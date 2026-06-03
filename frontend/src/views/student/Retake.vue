<script setup>
import { ref, onMounted } from 'vue'
import { studentApi } from '@/api/services'

const loading = ref(false)
const list = ref([])

const statusType = {
    待重修: 'danger',
    重修中: 'warning',
    重修通过: 'success',
    重修未通过: 'danger',
}

async function load() {
    loading.value = true
    try {
        list.value = await studentApi.retakeStatus()
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
                <h2>挂科与重修</h2>
                <div class="subtitle">不及格课程会保留原始成绩，并生成重修记录</div>
            </div>
        </div>

        <el-alert
            v-if="list.length"
            type="warning"
            :closable="false"
            show-icon
            title="您有待处理的重修课程，请在本学期选课时选择对应的重修班。"
            style="margin-bottom: 16px"
        />
        <el-empty v-else description="暂无挂科记录，继续保持！" />

        <el-table v-if="list.length" :data="list" v-loading="loading" border stripe>
            <el-table-column prop="course_name" label="课程名称" min-width="150" />
            <el-table-column prop="source_term" label="挂科学期" min-width="190" />
            <el-table-column label="原成绩" width="90" align="center">
                <template #default="{ row }"><span class="capacity-full">{{ row.source_score }}</span></template>
            </el-table-column>
            <el-table-column label="当前状态" width="120" align="center">
                <template #default="{ row }">
                    <el-tag :type="statusType[row.status] || 'info'">{{ row.status }}</el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="current_offering" label="关联重修班" min-width="200" />
        </el-table>
    </div>
</template>

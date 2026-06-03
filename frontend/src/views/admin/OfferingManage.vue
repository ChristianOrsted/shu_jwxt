<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '@/api/services'

const loading = ref(false)
const list = ref([])

const statusType = { 开放选课: 'success', 关闭选课: 'info', 已取消: 'danger', 待审批: 'warning', 已结课: 'info' }

async function load() {
    loading.value = true
    try {
        list.value = await adminApi.offerings()
    } finally {
        loading.value = false
    }
}

function toggleSelect(row) {
    row.status = row.status === '开放选课' ? '关闭选课' : '开放选课'
    ElMessage.success(`已${row.status === '开放选课' ? '开放' : '关闭'}该课程选课`)
}

function cancelOffering(row) {
    row.status = '已取消'
    ElMessage.warning('课程已取消，将通知已选学生重新选课')
}
onMounted(load)
</script>

<template>
    <div>
        <div class="page-header">
            <div>
                <h2>开课管理</h2>
                <div class="subtitle">安排开课班、开放/关闭选课、取消低于最低开课人数的课程</div>
            </div>
            <el-button type="primary" :icon="'Plus'" @click="ElMessage.info('演示环境：新增开课班功能占位')">新增开课</el-button>
        </div>

        <el-table :data="list" v-loading="loading" border stripe>
            <el-table-column prop="course_name" label="课程" min-width="140">
                <template #default="{ row }">
                    {{ row.course_name }}
                    <el-tag v-if="row.is_retake_class" size="small" type="warning" effect="plain">重修班</el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="teacher_name" label="教师" width="90" />
            <el-table-column prop="teaching_class_name" label="教学班" min-width="150" />
            <el-table-column label="选课/容量" width="110" align="center">
                <template #default="{ row }">
                    <span :class="row.selected_count >= row.capacity ? 'capacity-full' : 'capacity-ok'">
                        {{ row.selected_count }}/{{ row.capacity }}
                    </span>
                </template>
            </el-table-column>
            <el-table-column prop="min_enrollment" label="最低人数" width="90" align="center" />
            <el-table-column label="状态" width="100" align="center">
                <template #default="{ row }"><el-tag :type="statusType[row.status]">{{ row.status }}</el-tag></template>
            </el-table-column>
            <el-table-column label="操作" width="200" align="center" fixed="right">
                <template #default="{ row }">
                    <template v-if="row.status !== '已取消'">
                        <el-button size="small" @click="toggleSelect(row)">
                            {{ row.status === '开放选课' ? '关闭选课' : '开放选课' }}
                        </el-button>
                        <el-button
                            size="small"
                            type="danger"
                            :disabled="row.selected_count >= row.min_enrollment"
                            @click="cancelOffering(row)"
                        >
                            取消
                        </el-button>
                    </template>
                    <span v-else>—</span>
                </template>
            </el-table-column>
        </el-table>
        <el-alert
            type="info"
            :closable="false"
            style="margin-top: 12px"
            title="提示：只有当前选课人数低于最低开课人数的课程才允许取消（取消按钮可用）。"
        />
    </div>
</template>

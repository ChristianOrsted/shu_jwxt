<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { studentApi } from '@/api/services'

const loading = ref(false)
const courses = ref([])

const filters = ref({
    keyword: '',
    type: '',
    onlyAvailable: false,
    onlyRetake: false,
})

const detailVisible = ref(false)
const detail = ref({})

// 选课状态 -> 标签
const statusMeta = {
    available: { text: '可选', type: 'success' },
    selected: { text: '已选', type: 'primary' },
    full: { text: '已满', type: 'danger' },
    conflict: { text: '时间冲突', type: 'warning' },
    passed: { text: '已通过', type: 'info' },
    retake: { text: '待重修可选', type: 'warning' },
}

const filtered = computed(() => {
    return courses.value.filter((c) => {
        const kw = filters.value.keyword.trim()
        if (kw && !(`${c.course_name}${c.course_code}${c.teacher_name}`.includes(kw))) return false
        if (filters.value.type && c.course_type !== filters.value.type) return false
        if (filters.value.onlyAvailable && c.selected_count >= c.capacity) return false
        if (filters.value.onlyRetake && !c.is_retake_class) return false
        return true
    })
})

async function load() {
    loading.value = true
    try {
        courses.value = await studentApi.courses()
    } finally {
        loading.value = false
    }
}

function capacityClass(c) {
    return c.selected_count >= c.capacity ? 'capacity-full' : 'capacity-ok'
}

function canEnroll(c) {
    return c.select_status === 'available' || c.select_status === 'retake'
}

async function enroll(c) {
    try {
        await ElMessageBox.confirm(
            `确认选择《${c.course_name}》（${c.teacher_name}，${c.schedule_text}）吗？`,
            '选课确认',
            { confirmButtonText: '确认选课', cancelButtonText: '取消', type: 'info' },
        )
        await studentApi.enroll(c.offering_id)
        ElMessage.success('选课成功')
        c.select_status = 'selected'
        c.selected_count += 1
    } catch (e) {
        if (e !== 'cancel') ElMessage.error(e.message || '选课失败')
    }
}

function showDetail(c) {
    detail.value = c
    detailVisible.value = true
}

onMounted(load)
</script>

<template>
    <div>
        <div class="page-header">
            <div>
                <h2>选课中心</h2>
                <div class="subtitle">2025-2026学年第二学期 · 选课进行中</div>
            </div>
        </div>

        <div class="toolbar">
            <el-input
                v-model="filters.keyword"
                placeholder="搜索课程名 / 课程号 / 教师"
                :prefix-icon="'Search'"
                clearable
                style="width: 260px"
            />
            <el-select v-model="filters.type" placeholder="课程类型" clearable style="width: 140px">
                <el-option label="必修课" value="必修课" />
                <el-option label="选修课" value="选修课" />
                <el-option label="通识课" value="通识课" />
                <el-option label="实践课" value="实践课" />
            </el-select>
            <el-checkbox v-model="filters.onlyAvailable">只看有余量</el-checkbox>
            <el-checkbox v-model="filters.onlyRetake">只看重修班</el-checkbox>
            <el-button :icon="'Refresh'" @click="load">刷新</el-button>
        </div>

        <el-table :data="filtered" v-loading="loading" border stripe>
            <el-table-column prop="course_code" label="课程号" width="90" />
            <el-table-column label="课程名称" min-width="160">
                <template #default="{ row }">
                    <el-link type="primary" @click="showDetail(row)">{{ row.course_name }}</el-link>
                    <el-tag v-if="row.is_retake_class" size="small" type="warning" effect="plain" style="margin-left: 6px">重修班</el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="course_type" label="类型" width="90" />
            <el-table-column prop="credits" label="学分" width="70" />
            <el-table-column prop="teacher_name" label="教师" width="90" />
            <el-table-column prop="schedule_text" label="上课时间" min-width="170" />
            <el-table-column prop="location" label="地点" width="140" />
            <el-table-column label="容量" width="100" align="center">
                <template #default="{ row }">
                    <span :class="capacityClass(row)">{{ row.selected_count }}/{{ row.capacity }}</span>
                </template>
            </el-table-column>
            <el-table-column label="状态" width="110" align="center">
                <template #default="{ row }">
                    <el-tag :type="statusMeta[row.select_status]?.type" effect="light">
                        {{ statusMeta[row.select_status]?.text }}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center" fixed="right">
                <template #default="{ row }">
                    <el-button
                        v-if="row.select_status !== 'selected'"
                        type="primary"
                        size="small"
                        :disabled="!canEnroll(row)"
                        @click="enroll(row)"
                    >
                        选课
                    </el-button>
                    <el-tag v-else type="success" size="small">已选</el-tag>
                </template>
            </el-table-column>
        </el-table>

        <el-dialog v-model="detailVisible" :title="detail.course_name" width="520px">
            <el-descriptions :column="1" border>
                <el-descriptions-item label="课程号">{{ detail.course_code }}</el-descriptions-item>
                <el-descriptions-item label="课程类型">{{ detail.course_type }}</el-descriptions-item>
                <el-descriptions-item label="学分 / 学时">{{ detail.credits }} 学分 / {{ detail.hours }} 学时</el-descriptions-item>
                <el-descriptions-item label="考核方式">{{ detail.assessment_type }}</el-descriptions-item>
                <el-descriptions-item label="授课教师">{{ detail.teacher_name }}</el-descriptions-item>
                <el-descriptions-item label="教学班">{{ detail.teaching_class_name }}</el-descriptions-item>
                <el-descriptions-item label="上课时间">{{ detail.schedule_text }}</el-descriptions-item>
                <el-descriptions-item label="上课地点">{{ detail.location }}</el-descriptions-item>
                <el-descriptions-item label="容量">{{ detail.selected_count }}/{{ detail.capacity }}</el-descriptions-item>
                <el-descriptions-item label="课程简介">{{ detail.description }}</el-descriptions-item>
            </el-descriptions>
        </el-dialog>
    </div>
</template>

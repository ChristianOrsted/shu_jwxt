<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '@/api/services'

const loading = ref(false)
const courses = ref([])
const keyword = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)

const blank = () => ({ course_id: null, course_code: '', course_name: '', credits: 3, hours: 48, course_type: '必修课', assessment_type: '考试', allow_retake: true, is_enabled: true })
const form = reactive(blank())

const filtered = computed(() =>
    courses.value.filter((c) => !keyword.value || `${c.course_code}${c.course_name}`.includes(keyword.value)),
)

async function load() {
    loading.value = true
    try {
        const list = await adminApi.courses()
        // MySQL 的 BOOLEAN 会以 0/1 返回，转成真正的布尔值，el-switch 才能正确显示
        courses.value = list.map((c) => ({
            ...c,
            is_enabled: Boolean(c.is_enabled),
            allow_retake: Boolean(c.allow_retake),
        }))
    } finally {
        loading.value = false
    }
}

function openCreate() {
    isEdit.value = false
    Object.assign(form, blank())
    dialogVisible.value = true
}
function openEdit(row) {
    isEdit.value = true
    Object.assign(form, row)
    dialogVisible.value = true
}

async function save() {
    if (!form.course_code || !form.course_name) {
        ElMessage.warning('请填写课程号与课程名')
        return
    }
    await adminApi.saveCourse({ ...form })
    dialogVisible.value = false
    ElMessage.success('保存成功')
    await load()
}

async function toggleEnabled(row) {
    try {
        await adminApi.toggleCourse(row.course_id, row.is_enabled)
        ElMessage.success(row.is_enabled ? '课程已启用' : '课程已停用')
    } catch (e) {
        // 调用失败时回滚开关状态，保持与后端一致
        row.is_enabled = !row.is_enabled
        ElMessage.error('操作失败，请重试')
    }
}
onMounted(load)
</script>

<template>
    <div>
        <div class="page-header">
            <div>
                <h2>课程库管理</h2>
                <div class="subtitle">维护课程编号、学分、学时、类型、是否允许重修</div>
            </div>
            <el-button type="primary" :icon="'Plus'" @click="openCreate">新增课程</el-button>
        </div>

        <div class="toolbar">
            <el-input v-model="keyword" placeholder="搜索课程号/课程名" :prefix-icon="'Search'" clearable style="width: 240px" />
        </div>

        <el-table :data="filtered" v-loading="loading" border stripe>
            <el-table-column prop="course_code" label="课程号" width="100" />
            <el-table-column prop="course_name" label="课程名称" min-width="160" />
            <el-table-column prop="credits" label="学分" width="80" align="center" />
            <el-table-column prop="hours" label="学时" width="80" align="center" />
            <el-table-column prop="course_type" label="类型" width="100" align="center" />
            <el-table-column prop="assessment_type" label="考核方式" width="100" align="center" />
            <el-table-column label="允许重修" width="90" align="center">
                <template #default="{ row }">
                    <el-tag :type="row.allow_retake ? 'success' : 'info'" size="small">{{ row.allow_retake ? '是' : '否' }}</el-tag>
                </template>
            </el-table-column>
            <el-table-column label="启用" width="90" align="center">
                <template #default="{ row }"><el-switch v-model="row.is_enabled" @change="toggleEnabled(row)" /></template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center" fixed="right">
                <template #default="{ row }"><el-button size="small" @click="openEdit(row)">编辑</el-button></template>
            </el-table-column>
        </el-table>

        <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑课程' : '新增课程'" width="480px">
            <el-form :model="form" label-width="90px">
                <el-form-item label="课程号"><el-input v-model="form.course_code" /></el-form-item>
                <el-form-item label="课程名称"><el-input v-model="form.course_name" /></el-form-item>
                <el-form-item label="学分"><el-input-number v-model="form.credits" :min="0.5" :max="10" :step="0.5" /></el-form-item>
                <el-form-item label="学时"><el-input-number v-model="form.hours" :min="8" :max="200" :step="8" /></el-form-item>
                <el-form-item label="课程类型">
                    <el-select v-model="form.course_type" style="width: 100%">
                        <el-option label="必修课" value="必修课" />
                        <el-option label="选修课" value="选修课" />
                        <el-option label="专业课" value="专业课" />
                        <el-option label="通识课" value="通识课" />
                    </el-select>
                </el-form-item>
                <el-form-item label="考核方式">
                    <el-radio-group v-model="form.assessment_type">
                        <el-radio value="考试">考试</el-radio>
                        <el-radio value="考查">考查</el-radio>
                    </el-radio-group>
                </el-form-item>
                <el-form-item label="允许重修"><el-switch v-model="form.allow_retake" /></el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="dialogVisible = false">取消</el-button>
                <el-button type="primary" @click="save">保存</el-button>
            </template>
        </el-dialog>
    </div>
</template>

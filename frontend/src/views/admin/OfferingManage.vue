<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '@/api/services'

const loading = ref(false)
const list = ref([])
const dialogVisible = ref(false)
const saving = ref(false)
const courses = ref([])
const teachers = ref([])
const terms = ref([])

const blank = () => ({
    course_id: null, teacher_id: null, term_id: null,
    teaching_class_name: '', capacity: 40, min_enrollment: 10, is_retake_class: false,
})
const form = reactive(blank())

const statusType = { 开放选课: 'success', 关闭选课: 'info', 已取消: 'danger', 待审批: 'warning', 已结课: 'info' }

async function load() {
    loading.value = true
    try {
        list.value = await adminApi.offerings()
    } finally {
        loading.value = false
    }
}

async function openCreate() {
    Object.assign(form, blank())
    dialogVisible.value = true
    const [c, t, yr] = await Promise.all([adminApi.courses(), adminApi.teachers(), adminApi.terms()])
    courses.value = c
    teachers.value = t
    terms.value = yr.flatMap((y) => y.terms)
}

async function save() {
    if (!form.course_id || !form.teacher_id || !form.term_id || !form.teaching_class_name) {
        ElMessage.warning('请填写所有必填项')
        return
    }
    saving.value = true
    try {
        await adminApi.saveOffering({ ...form })
        ElMessage.success('开课班创建成功')
        dialogVisible.value = false
        await load()
    } finally {
        saving.value = false
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
            <el-button type="primary" :icon="'Plus'" @click="openCreate">新增开课</el-button>
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

        <el-dialog v-model="dialogVisible" title="新增开课班" width="500px">
            <el-form :model="form" label-width="100px">
                <el-form-item label="课程" required>
                    <el-select v-model="form.course_id" filterable placeholder="请选择课程" style="width: 100%">
                        <el-option
                            v-for="c in courses" :key="c.course_id"
                            :label="`${c.course_code} ${c.course_name}`"
                            :value="c.course_id"
                        />
                    </el-select>
                </el-form-item>
                <el-form-item label="授课教师" required>
                    <el-select v-model="form.teacher_id" filterable placeholder="请选择教师" style="width: 100%">
                        <el-option
                            v-for="t in teachers" :key="t.teacher_id"
                            :label="`${t.real_name}（${t.department_name || ''}）`"
                            :value="t.teacher_id"
                        />
                    </el-select>
                </el-form-item>
                <el-form-item label="学期" required>
                    <el-select v-model="form.term_id" placeholder="请选择学期" style="width: 100%">
                        <el-option
                            v-for="t in terms" :key="t.term_id"
                            :label="t.term_name"
                            :value="t.term_id"
                        />
                    </el-select>
                </el-form-item>
                <el-form-item label="教学班名称" required>
                    <el-input v-model="form.teaching_class_name" placeholder="如：数据库原理-02班" />
                </el-form-item>
                <el-form-item label="课程容量">
                    <el-input-number v-model="form.capacity" :min="1" :max="500" />
                </el-form-item>
                <el-form-item label="最低开课人数">
                    <el-input-number v-model="form.min_enrollment" :min="1" :max="form.capacity" />
                </el-form-item>
                <el-form-item label="重修班">
                    <el-switch v-model="form.is_retake_class" />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="dialogVisible = false">取消</el-button>
                <el-button type="primary" :loading="saving" @click="save">创建</el-button>
            </template>
        </el-dialog>
    </div>
</template>

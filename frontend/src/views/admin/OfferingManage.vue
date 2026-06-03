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
const classrooms = ref([])

const weekdayOptions = [
    { label: '周一', value: 1 }, { label: '周二', value: 2 }, { label: '周三', value: 3 },
    { label: '周四', value: 4 }, { label: '周五', value: 5 }, { label: '周六', value: 6 },
    { label: '周日', value: 7 },
]
// 一段上课时间：星期/起止节次/起止周次/教室（教室可空）
const blankSchedule = () => ({
    weekday: 1, start_section: 1, end_section: 2, week_start: 1, week_end: 18, classroom_id: null,
})
const blank = () => ({
    course_id: null, teacher_id: null, term_id: null,
    teaching_class_name: '', capacity: 40, min_enrollment: 10, is_retake_class: false,
    schedules: [blankSchedule()],
})
const form = reactive(blank())

function addSchedule() {
    form.schedules.push(blankSchedule())
}
function removeSchedule(i) {
    form.schedules.splice(i, 1)
}

// 编辑（仅容量与最低开课人数）
const editVisible = ref(false)
const editSaving = ref(false)
const editForm = reactive({
    offering_id: null, teaching_class_name: '', selected_count: 0, capacity: 40, min_enrollment: 10,
})

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
    const [c, t, yr, rooms] = await Promise.all([
        adminApi.courses(), adminApi.teachers(), adminApi.terms(), adminApi.classrooms(),
    ])
    // 已停用的课程不允许新开课，下拉里直接过滤掉
    courses.value = c.filter((x) => x.is_enabled)
    teachers.value = t
    terms.value = yr.flatMap((y) => y.terms)
    classrooms.value = rooms
}

async function save() {
    if (!form.course_id || !form.teacher_id || !form.term_id || !form.teaching_class_name) {
        ElMessage.warning('请填写所有必填项')
        return
    }
    for (const [i, s] of form.schedules.entries()) {
        if (s.start_section > s.end_section) {
            ElMessage.warning(`第 ${i + 1} 段上课时间：起始节次不能大于结束节次`)
            return
        }
        if (s.week_start > s.week_end) {
            ElMessage.warning(`第 ${i + 1} 段上课时间：起始周不能大于结束周`)
            return
        }
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

async function toggleSelect(row) {
    try {
        const res = await adminApi.toggleOfferingEnrollment(row.offering_id)
        row.status = res.status
        ElMessage.success(`已${row.status === '开放选课' ? '开放' : '关闭'}该课程选课`)
    } catch (e) {
        // 拦截器已弹出错误提示，这里重新拉取以保持与后端一致
        await load()
    }
}

async function cancelOffering(row) {
    try {
        await adminApi.cancelOffering(row.offering_id)
        row.status = '已取消'
        ElMessage.warning('课程已取消，将通知已选学生重新选课')
    } catch (e) {
        await load()
    }
}

function openEdit(row) {
    Object.assign(editForm, {
        offering_id: row.offering_id,
        teaching_class_name: row.teaching_class_name,
        selected_count: row.selected_count,
        capacity: row.capacity,
        min_enrollment: row.min_enrollment,
    })
    editVisible.value = true
}

async function saveEdit() {
    if (editForm.min_enrollment > editForm.capacity) {
        ElMessage.warning('最低开课人数不能大于容量')
        return
    }
    if (editForm.capacity < editForm.selected_count) {
        ElMessage.warning(`容量不能小于已选人数（已选 ${editForm.selected_count} 人）`)
        return
    }
    editSaving.value = true
    try {
        await adminApi.updateOffering(editForm.offering_id, {
            capacity: editForm.capacity,
            min_enrollment: editForm.min_enrollment,
        })
        ElMessage.success('开课班已更新')
        editVisible.value = false
        await load()
    } finally {
        editSaving.value = false
    }
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
            <el-table-column label="上课时间" min-width="180">
                <template #default="{ row }">
                    <span>{{ row.schedule_text || '未排课' }}</span>
                </template>
            </el-table-column>
            <el-table-column label="状态" width="100" align="center">
                <template #default="{ row }"><el-tag :type="statusType[row.status]">{{ row.status }}</el-tag></template>
            </el-table-column>
            <el-table-column label="操作" width="260" align="center" fixed="right">
                <template #default="{ row }">
                    <template v-if="row.status !== '已取消'">
                        <el-button
                            v-if="row.status === '开放选课' || row.status === '关闭选课'"
                            size="small"
                            @click="openEdit(row)"
                        >
                            编辑
                        </el-button>
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

        <el-dialog v-model="dialogVisible" title="新增开课班" width="720px">
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
                <el-form-item label="上课时间">
                    <div style="width: 100%">
                        <div v-for="(s, i) in form.schedules" :key="i" class="schedule-row">
                            <el-select v-model="s.weekday" placeholder="星期" style="width: 88px">
                                <el-option v-for="w in weekdayOptions" :key="w.value" :label="w.label" :value="w.value" />
                            </el-select>
                            <span class="sep">第</span>
                            <el-input-number v-model="s.start_section" :min="1" :max="10" controls-position="right" style="width: 92px" />
                            <span class="sep">—</span>
                            <el-input-number v-model="s.end_section" :min="1" :max="10" controls-position="right" style="width: 92px" />
                            <span class="sep">节</span>
                            <el-input-number v-model="s.week_start" :min="1" :max="30" controls-position="right" style="width: 92px" />
                            <span class="sep">—</span>
                            <el-input-number v-model="s.week_end" :min="1" :max="30" controls-position="right" style="width: 92px" />
                            <span class="sep">周</span>
                            <el-select v-model="s.classroom_id" placeholder="教室(可选)" clearable filterable style="width: 150px">
                                <el-option
                                    v-for="r in classrooms" :key="r.classroom_id"
                                    :label="`${r.building}${r.room_no}`"
                                    :value="r.classroom_id"
                                />
                            </el-select>
                            <el-button
                                size="small" type="danger" text
                                :disabled="form.schedules.length <= 1"
                                @click="removeSchedule(i)"
                            >
                                删除
                            </el-button>
                        </div>
                        <el-button size="small" type="primary" text @click="addSchedule">+ 添加上课时间</el-button>
                    </div>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="dialogVisible = false">取消</el-button>
                <el-button type="primary" :loading="saving" @click="save">创建</el-button>
            </template>
        </el-dialog>

        <el-dialog v-model="editVisible" title="编辑开课班" width="460px">
            <el-form :model="editForm" label-width="100px">
                <el-form-item label="教学班">
                    <span>{{ editForm.teaching_class_name }}（已选 {{ editForm.selected_count }} 人）</span>
                </el-form-item>
                <el-form-item label="课程容量">
                    <el-input-number v-model="editForm.capacity" :min="editForm.selected_count || 1" :max="500" />
                </el-form-item>
                <el-form-item label="最低开课人数">
                    <el-input-number v-model="editForm.min_enrollment" :min="1" :max="editForm.capacity" />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="editVisible = false">取消</el-button>
                <el-button type="primary" :loading="editSaving" @click="saveEdit">保存</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<style scoped>
.schedule-row {
    display: flex;
    align-items: center;
    gap: 4px;
    margin-bottom: 8px;
    flex-wrap: wrap;
}
.schedule-row .sep {
    color: var(--el-text-color-secondary);
    padding: 0 2px;
}
</style>

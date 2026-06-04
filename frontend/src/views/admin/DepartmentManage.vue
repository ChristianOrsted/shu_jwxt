<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi } from '@/api/services'

const loading = ref(false)
const departments = ref([])
const majors = ref([])
const keyword = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)

const blank = () => ({ department_id: null, department_name: '' })
const form = reactive(blank())

// 专业管理（在学院展开行内操作）
const majorDialogVisible = ref(false)
const majorIsEdit = ref(false)
const majorSaving = ref(false)
const majorBlank = () => ({ major_id: null, major_name: '', department_id: null, department_name: '' })
const majorForm = reactive(majorBlank())

function formatTime(val) {
    if (!val) return ''
    const d = new Date(val)
    return d.toLocaleString('zh-CN', { hour12: false }).replace(/\//g, '-')
}

const filtered = computed(() =>
    departments.value.filter((d) => !keyword.value || `${d.department_name}`.includes(keyword.value)),
)

function majorsByDept(departmentId) {
    return majors.value.filter((m) => m.department_id === departmentId)
}

async function load() {
    loading.value = true
    try {
        const [deps, mjs] = await Promise.all([adminApi.departments(), adminApi.majors()])
        departments.value = deps
        majors.value = mjs
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
    Object.assign(form, blank(), row)
    dialogVisible.value = true
}

async function save() {
    if (!form.department_name.trim()) {
        ElMessage.warning('请填写学院名称')
        return
    }
    await adminApi.saveDepartment({ ...form })
    dialogVisible.value = false
    ElMessage.success('保存成功')
    await load()
}

async function remove(row) {
    try {
        await ElMessageBox.confirm(`确定删除学院「${row.department_name}」吗？`, '提示', {
            type: 'warning',
            confirmButtonText: '删除',
            cancelButtonText: '取消',
        })
    } catch {
        return
    }
    try {
        await adminApi.deleteDepartment(row.department_id)
        ElMessage.success('删除成功')
        await load()
    } catch {
        await load()
    }
}

// ---- 专业 ----
function openCreateMajor(dept) {
    majorIsEdit.value = false
    Object.assign(majorForm, majorBlank(), {
        department_id: dept.department_id,
        department_name: dept.department_name,
    })
    majorDialogVisible.value = true
}
function openEditMajor(dept, major) {
    majorIsEdit.value = true
    Object.assign(majorForm, majorBlank(), {
        major_id: major.major_id,
        major_name: major.major_name,
        department_id: dept.department_id,
        department_name: dept.department_name,
    })
    majorDialogVisible.value = true
}

async function saveMajor() {
    if (!majorForm.major_name.trim()) {
        ElMessage.warning('请填写专业名称')
        return
    }
    majorSaving.value = true
    try {
        await adminApi.saveMajor({
            major_id: majorForm.major_id,
            major_name: majorForm.major_name.trim(),
            department_id: majorForm.department_id,
        })
        ElMessage.success('保存成功')
        majorDialogVisible.value = false
        await load()
    } finally {
        majorSaving.value = false
    }
}

async function removeMajor(major) {
    try {
        await ElMessageBox.confirm(`确定删除专业「${major.major_name}」吗？`, '删除专业', {
            type: 'warning',
            confirmButtonText: '删除',
            cancelButtonText: '取消',
        })
    } catch {
        return
    }
    try {
        await adminApi.deleteMajor(major.major_id)
        ElMessage.success('删除成功')
        await load()
    } catch {
        // 拦截器已提示（如仍有班级/学生），重新拉取保持一致
        await load()
    }
}

onMounted(load)
</script>

<template>
    <div>
        <div class="page-header">
            <div>
                <h2>学院管理</h2>
                <div class="subtitle">维护学院（院系），展开可管理下设专业</div>
            </div>
            <el-button type="primary" :icon="'Plus'" @click="openCreate">新增学院</el-button>
        </div>

        <div class="toolbar">
            <el-input v-model="keyword" placeholder="搜索学院名称" :prefix-icon="'Search'" clearable style="width: 240px" />
        </div>

        <el-table :data="filtered" v-loading="loading" border stripe row-key="department_id">
            <el-table-column type="expand">
                <template #default="{ row }">
                    <div class="major-panel">
                        <div class="major-panel-header">
                            <strong>{{ row.department_name }} · 下设专业</strong>
                            <el-button size="small" type="primary" :icon="'Plus'" @click="openCreateMajor(row)">
                                新增专业
                            </el-button>
                        </div>
                        <el-table :data="majorsByDept(row.department_id)" border size="small" empty-text="暂无专业">
                            <el-table-column prop="major_id" label="ID" width="80" align="center" />
                            <el-table-column prop="major_name" label="专业名称" min-width="200" />
                            <el-table-column prop="class_count" label="班级数" width="90" align="center" />
                            <el-table-column prop="student_count" label="学生数" width="90" align="center" />
                            <el-table-column label="操作" width="160" align="center">
                                <template #default="{ row: major }">
                                    <el-button size="small" @click="openEditMajor(row, major)">编辑</el-button>
                                    <el-button size="small" type="danger" @click="removeMajor(major)">删除</el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </div>
                </template>
            </el-table-column>
            <el-table-column prop="department_id" label="ID" width="80" align="center" />
            <el-table-column prop="department_name" label="学院名称" min-width="200" />
            <el-table-column prop="major_count" label="专业数" width="90" align="center" />
            <el-table-column prop="teacher_count" label="教师数" width="90" align="center" />
            <el-table-column prop="student_count" label="学生数" width="90" align="center" />
            <el-table-column label="创建时间" width="180" align="center">
                <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="160" align="center" fixed="right">
                <template #default="{ row }">
                    <el-button size="small" @click="openEdit(row)">编辑</el-button>
                    <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
                </template>
            </el-table-column>
        </el-table>

        <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑学院' : '新增学院'" width="420px">
            <el-form :model="form" label-width="90px">
                <el-form-item label="学院名称">
                    <el-input v-model="form.department_name" placeholder="如：计算机工程与科学学院" />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="dialogVisible = false">取消</el-button>
                <el-button type="primary" @click="save">保存</el-button>
            </template>
        </el-dialog>

        <el-dialog v-model="majorDialogVisible" :title="majorIsEdit ? '编辑专业' : '新增专业'" width="420px">
            <el-form :model="majorForm" label-width="90px">
                <el-form-item label="所属学院">
                    <span>{{ majorForm.department_name }}</span>
                </el-form-item>
                <el-form-item label="专业名称">
                    <el-input v-model="majorForm.major_name" placeholder="如：软件工程" />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="majorDialogVisible = false">取消</el-button>
                <el-button type="primary" :loading="majorSaving" @click="saveMajor">保存</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<style scoped>
.major-panel {
    padding: 12px 16px;
}
.major-panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
}
</style>

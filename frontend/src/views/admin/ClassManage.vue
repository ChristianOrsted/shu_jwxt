<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi } from '@/api/services'

const loading = ref(false)
const list = ref([])
const departments = ref([])
const majors = ref([])

const keyword = ref('')
const deptFilter = ref(null)
const majorFilter = ref(null)

const dialogVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const blank = () => ({ class_id: null, class_name: '', department_id: null, major_id: null, grade_year: 2025 })
const form = reactive(blank())

// 按所选学院过滤专业（筛选栏 / 表单各一份）
const majorFilterOptions = computed(() =>
    majors.value.filter((m) => !deptFilter.value || m.department_id === deptFilter.value),
)
const formMajorOptions = computed(() =>
    majors.value.filter((m) => !form.department_id || m.department_id === form.department_id),
)

const filtered = computed(() =>
    list.value.filter((r) => {
        const kw = keyword.value.trim()
        const matchKw = !kw || `${r.class_name}`.includes(kw)
        const matchDept = !deptFilter.value || r.department_id === deptFilter.value
        const matchMajor = !majorFilter.value || r.major_id === majorFilter.value
        return matchKw && matchDept && matchMajor
    }),
)

function onDeptFilterChange() {
    // 学院变化时，若已选专业不属于该学院则清空
    if (majorFilter.value && !majorFilterOptions.value.some((m) => m.major_id === majorFilter.value)) {
        majorFilter.value = null
    }
}
function onFormDeptChange() {
    if (form.major_id && !formMajorOptions.value.some((m) => m.major_id === form.major_id)) {
        form.major_id = null
    }
}

async function load() {
    loading.value = true
    try {
        const [cls, deps, mjs] = await Promise.all([
            adminApi.classes(), adminApi.departments(), adminApi.majors(),
        ])
        list.value = cls
        departments.value = deps
        majors.value = mjs
    } finally {
        loading.value = false
    }
}

function openCreate() {
    isEdit.value = false
    Object.assign(form, blank(), {
        department_id: deptFilter.value || null,
        major_id: majorFilter.value || null,
    })
    dialogVisible.value = true
}
function openEdit(row) {
    isEdit.value = true
    Object.assign(form, blank(), {
        class_id: row.class_id,
        class_name: row.class_name,
        department_id: row.department_id,
        major_id: row.major_id,
        grade_year: row.grade_year ?? 2025,
    })
    dialogVisible.value = true
}

async function save() {
    if (!form.class_name.trim()) {
        ElMessage.warning('请填写班级名称')
        return
    }
    if (!form.major_id) {
        ElMessage.warning('请选择所属专业')
        return
    }
    saving.value = true
    try {
        await adminApi.saveClass({
            class_id: form.class_id,
            class_name: form.class_name.trim(),
            major_id: form.major_id,
            grade_year: form.grade_year,
        })
        ElMessage.success('保存成功')
        dialogVisible.value = false
        await load()
    } finally {
        saving.value = false
    }
}

async function remove(row) {
    try {
        await ElMessageBox.confirm(`确定删除班级「${row.class_name}」吗？`, '删除班级', {
            type: 'warning',
            confirmButtonText: '删除',
            cancelButtonText: '取消',
        })
    } catch {
        return
    }
    try {
        await adminApi.deleteClass(row.class_id)
        ElMessage.success('删除成功')
        await load()
    } catch {
        // 拦截器已提示（如仍有学生），重新拉取保持一致
        await load()
    }
}

onMounted(load)
</script>

<template>
    <div>
        <div class="page-header">
            <div>
                <h2>班级管理</h2>
                <div class="subtitle">维护班级及其所属专业、年级，按学院/专业筛选</div>
            </div>
            <el-button type="primary" :icon="'Plus'" @click="openCreate">新增班级</el-button>
        </div>

        <div class="toolbar">
            <el-input v-model="keyword" placeholder="搜索班级名称" :prefix-icon="'Search'" clearable style="width: 220px" />
            <el-select
                v-model="deptFilter" placeholder="全部学院" clearable filterable
                style="width: 200px" @change="onDeptFilterChange"
            >
                <el-option
                    v-for="d in departments" :key="d.department_id"
                    :label="d.department_name" :value="d.department_id"
                />
            </el-select>
            <el-select v-model="majorFilter" placeholder="全部专业" clearable filterable style="width: 200px">
                <el-option
                    v-for="m in majorFilterOptions" :key="m.major_id"
                    :label="m.major_name" :value="m.major_id"
                />
            </el-select>
        </div>

        <el-table :data="filtered" v-loading="loading" border stripe>
            <el-table-column prop="class_id" label="ID" width="80" align="center" />
            <el-table-column prop="class_name" label="班级名称" min-width="180" />
            <el-table-column prop="major_name" label="所属专业" min-width="160">
                <template #default="{ row }">{{ row.major_name || '—' }}</template>
            </el-table-column>
            <el-table-column prop="department_name" label="所属学院" min-width="180">
                <template #default="{ row }">{{ row.department_name || '—' }}</template>
            </el-table-column>
            <el-table-column prop="grade_year" label="年级" width="90" align="center">
                <template #default="{ row }">{{ row.grade_year || '—' }}</template>
            </el-table-column>
            <el-table-column prop="student_count" label="学生数" width="90" align="center" />
            <el-table-column label="操作" width="160" align="center" fixed="right">
                <template #default="{ row }">
                    <el-button size="small" @click="openEdit(row)">编辑</el-button>
                    <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
                </template>
            </el-table-column>
        </el-table>

        <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑班级' : '新增班级'" width="460px">
            <el-form :model="form" label-width="90px">
                <el-form-item label="所属学院" required>
                    <el-select
                        v-model="form.department_id" placeholder="请选择学院" filterable
                        style="width: 100%" @change="onFormDeptChange"
                    >
                        <el-option
                            v-for="d in departments" :key="d.department_id"
                            :label="d.department_name" :value="d.department_id"
                        />
                    </el-select>
                </el-form-item>
                <el-form-item label="所属专业" required>
                    <el-select
                        v-model="form.major_id" placeholder="请先选择学院再选专业" filterable
                        :disabled="!form.department_id" style="width: 100%"
                    >
                        <el-option
                            v-for="m in formMajorOptions" :key="m.major_id"
                            :label="m.major_name" :value="m.major_id"
                        />
                    </el-select>
                </el-form-item>
                <el-form-item label="班级名称" required>
                    <el-input v-model="form.class_name" placeholder="如：软件工程2025级1班" />
                </el-form-item>
                <el-form-item label="年级">
                    <el-input-number v-model="form.grade_year" :min="2000" :max="2100" />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="dialogVisible = false">取消</el-button>
                <el-button type="primary" :loading="saving" @click="save">保存</el-button>
            </template>
        </el-dialog>
    </div>
</template>

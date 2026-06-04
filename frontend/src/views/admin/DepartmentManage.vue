<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi } from '@/api/services'

const loading = ref(false)
const departments = ref([])
const keyword = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)

const blank = () => ({ department_id: null, department_name: '' })
const form = reactive(blank())

function formatTime(val) {
    if (!val) return ''
    const d = new Date(val)
    return d.toLocaleString('zh-CN', { hour12: false }).replace(/\//g, '-')
}

const filtered = computed(() =>
    departments.value.filter((d) => !keyword.value || `${d.department_name}`.includes(keyword.value)),
)

async function load() {
    loading.value = true
    try {
        departments.value = await adminApi.departments()
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
    await adminApi.deleteDepartment(row.department_id)
    ElMessage.success('删除成功')
    await load()
}

onMounted(load)
</script>

<template>
    <div>
        <div class="page-header">
            <div>
                <h2>学院管理</h2>
                <div class="subtitle">维护学院（院系），可新增、重命名、删除</div>
            </div>
            <el-button type="primary" :icon="'Plus'" @click="openCreate">新增学院</el-button>
        </div>

        <div class="toolbar">
            <el-input v-model="keyword" placeholder="搜索学院名称" :prefix-icon="'Search'" clearable style="width: 240px" />
        </div>

        <el-table :data="filtered" v-loading="loading" border stripe>
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
    </div>
</template>

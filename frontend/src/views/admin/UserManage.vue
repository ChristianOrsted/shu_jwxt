<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi } from '@/api/services'

const loading = ref(false)
const users = ref([])
const keyword = ref('')
const roleFilter = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)

const form = reactive({ user_id: null, username: '', real_name: '', role: 'student', phone: '', status: '正常' })

const roleLabel = { student: '学生', teacher: '教师', admin: '管理员' }

const filtered = computed(() =>
    users.value.filter((u) => {
        if (keyword.value && !`${u.username}${u.real_name}`.includes(keyword.value)) return false
        if (roleFilter.value && u.role !== roleFilter.value) return false
        return true
    }),
)

async function load() {
    loading.value = true
    try {
        users.value = await adminApi.users()
    } finally {
        loading.value = false
    }
}

function openCreate() {
    isEdit.value = false
    Object.assign(form, { user_id: null, username: '', real_name: '', role: 'student', phone: '', status: '正常' })
    dialogVisible.value = true
}
function openEdit(row) {
    isEdit.value = true
    Object.assign(form, row)
    dialogVisible.value = true
}

async function save() {
    if (!form.username || !form.real_name) {
        ElMessage.warning('请填写用户名和姓名')
        return
    }
    await adminApi.saveUser({ ...form })
    if (isEdit.value) {
        const idx = users.value.findIndex((u) => u.user_id === form.user_id)
        if (idx > -1) users.value[idx] = { ...form, role_name: roleLabel[form.role] }
    } else {
        users.value.unshift({ ...form, user_id: Date.now(), role_name: roleLabel[form.role] })
    }
    dialogVisible.value = false
    ElMessage.success('保存成功')
}

function toggleStatus(row) {
    row.status = row.status === '正常' ? '禁用' : '正常'
    ElMessage.success(`已${row.status === '正常' ? '启用' : '禁用'}该账号`)
}

async function resetPwd(row) {
    await ElMessageBox.confirm(`将 ${row.username} 的密码重置为 123456？`, '重置密码', { type: 'warning' })
    ElMessage.success('密码已重置为 123456')
}
onMounted(load)
</script>

<template>
    <div>
        <div class="page-header">
            <div>
                <h2>用户管理</h2>
                <div class="subtitle">学生 / 教师 / 管理员账号的增删改查</div>
            </div>
            <el-button type="primary" :icon="'Plus'" @click="openCreate">新增用户</el-button>
        </div>

        <div class="toolbar">
            <el-input v-model="keyword" placeholder="搜索用户名/姓名" :prefix-icon="'Search'" clearable style="width: 220px" />
            <el-select v-model="roleFilter" placeholder="角色" clearable style="width: 130px">
                <el-option label="学生" value="student" />
                <el-option label="教师" value="teacher" />
                <el-option label="管理员" value="admin" />
            </el-select>
        </div>

        <el-table :data="filtered" v-loading="loading" border stripe>
            <el-table-column prop="username" label="用户名" width="130" />
            <el-table-column prop="real_name" label="姓名" width="120" />
            <el-table-column prop="role_name" label="角色" width="100" align="center" />
            <el-table-column prop="phone" label="手机号" width="150" />
            <el-table-column label="状态" width="90" align="center">
                <template #default="{ row }">
                    <el-tag :type="row.status === '正常' ? 'success' : 'danger'">{{ row.status }}</el-tag>
                </template>
            </el-table-column>
            <el-table-column label="操作" width="260" fixed="right">
                <template #default="{ row }">
                    <el-button size="small" @click="openEdit(row)">编辑</el-button>
                    <el-button size="small" type="warning" @click="resetPwd(row)">重置密码</el-button>
                    <el-button size="small" :type="row.status === '正常' ? 'danger' : 'success'" @click="toggleStatus(row)">
                        {{ row.status === '正常' ? '禁用' : '启用' }}
                    </el-button>
                </template>
            </el-table-column>
        </el-table>

        <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑用户' : '新增用户'" width="440px">
            <el-form :model="form" label-width="80px">
                <el-form-item label="用户名"><el-input v-model="form.username" :disabled="isEdit" /></el-form-item>
                <el-form-item label="姓名"><el-input v-model="form.real_name" /></el-form-item>
                <el-form-item label="角色">
                    <el-select v-model="form.role" style="width: 100%" :disabled="isEdit">
                        <el-option label="学生" value="student" />
                        <el-option label="教师" value="teacher" />
                        <el-option label="管理员" value="admin" />
                    </el-select>
                </el-form-item>
                <el-form-item label="手机号"><el-input v-model="form.phone" /></el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="dialogVisible = false">取消</el-button>
                <el-button type="primary" @click="save">保存</el-button>
            </template>
        </el-dialog>
    </div>
</template>

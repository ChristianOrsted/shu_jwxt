<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { studentApi } from '@/api/services'

const loading = ref(false)
const info = ref({})
const editVisible = ref(false)
const form = reactive({ phone: '', email: '' })

async function load() {
    loading.value = true
    try {
        info.value = await studentApi.profile()
    } finally {
        loading.value = false
    }
}

function openEdit() {
    form.phone = info.value.phone
    form.email = info.value.email
    editVisible.value = true
}

function save() {
    info.value.phone = form.phone
    info.value.email = form.email
    editVisible.value = false
    ElMessage.success('资料已更新')
}
onMounted(load)
</script>

<template>
    <div>
        <div class="page-header">
            <div>
                <h2>个人信息</h2>
                <div class="subtitle">学籍信息只读，联系方式可自行维护</div>
            </div>
            <el-button type="primary" :icon="'Edit'" @click="openEdit">修改联系方式</el-button>
        </div>

        <el-card v-loading="loading" shadow="never">
            <el-descriptions :column="2" border>
                <el-descriptions-item label="学号">{{ info.student_no }}</el-descriptions-item>
                <el-descriptions-item label="姓名">{{ info.real_name }}</el-descriptions-item>
                <el-descriptions-item label="性别">{{ info.gender }}</el-descriptions-item>
                <el-descriptions-item label="学籍状态">
                    <el-tag type="success">{{ info.student_status }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="学院">{{ info.department_name }}</el-descriptions-item>
                <el-descriptions-item label="专业">{{ info.major_name }}</el-descriptions-item>
                <el-descriptions-item label="班级">{{ info.class_name }}</el-descriptions-item>
                <el-descriptions-item label="年级">{{ info.grade_year }} 级</el-descriptions-item>
                <el-descriptions-item label="手机号">{{ info.phone }}</el-descriptions-item>
                <el-descriptions-item label="邮箱">{{ info.email }}</el-descriptions-item>
            </el-descriptions>
        </el-card>

        <el-dialog v-model="editVisible" title="修改联系方式" width="420px">
            <el-form :model="form" label-width="80px">
                <el-form-item label="手机号"><el-input v-model="form.phone" /></el-form-item>
                <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="editVisible = false">取消</el-button>
                <el-button type="primary" @click="save">保存</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { teacherApi } from '@/api/services'

const loading = ref(false)
const info = ref({})

async function load() {
    loading.value = true
    try {
        info.value = await teacherApi.profile()
    } finally {
        loading.value = false
    }
}
onMounted(load)
</script>

<template>
    <div>
        <div class="page-header">
            <div>
                <h2>个人信息</h2>
                <div class="subtitle">教师基本信息</div>
            </div>
        </div>
        <el-card v-loading="loading" shadow="never">
            <el-descriptions :column="2" border>
                <el-descriptions-item label="工号">{{ info.teacher_no }}</el-descriptions-item>
                <el-descriptions-item label="姓名">{{ info.real_name }}</el-descriptions-item>
                <el-descriptions-item label="性别">{{ info.gender }}</el-descriptions-item>
                <el-descriptions-item label="职称">
                    <el-tag type="primary">{{ info.title }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="所属学院">{{ info.department_name }}</el-descriptions-item>
                <el-descriptions-item label="手机号">{{ info.phone }}</el-descriptions-item>
                <el-descriptions-item label="邮箱">{{ info.email }}</el-descriptions-item>
            </el-descriptions>
        </el-card>
    </div>
</template>

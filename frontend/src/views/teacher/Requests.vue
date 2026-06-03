<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { teacherApi } from '@/api/services'

const loading = ref(false)
const list = ref([])
const dialogVisible = ref(false)

const statusType = { 待审批: 'warning', 已通过: 'success', 已驳回: 'danger' }

const form = reactive({
    request_type: '开课申请',
    course_name: '',
    content: '',
    reason: '',
})

async function load() {
    loading.value = true
    try {
        list.value = await teacherApi.requests()
    } finally {
        loading.value = false
    }
}

function openDialog() {
    Object.assign(form, { request_type: '开课申请', course_name: '', content: '', reason: '' })
    dialogVisible.value = true
}

async function submit() {
    if (!form.course_name || !form.content) {
        ElMessage.warning('请填写课程与申请内容')
        return
    }
    await teacherApi.submitRequest({ ...form })
    list.value.unshift({
        request_id: Date.now(),
        ...form,
        term_name: '2025-2026学年第二学期',
        status: '待审批',
        created_at: new Date().toISOString().slice(0, 19),
    })
    dialogVisible.value = false
    ElMessage.success('申请已提交，等待管理员审批')
}
onMounted(load)
</script>

<template>
    <div>
        <div class="page-header">
            <div>
                <h2>教学申请</h2>
                <div class="subtitle">开课 / 扩容 / 调课 / 停课 / 成绩修改申请及审批进度</div>
            </div>
            <el-button type="primary" :icon="'Plus'" @click="openDialog">发起申请</el-button>
        </div>

        <el-table :data="list" v-loading="loading" border stripe>
            <el-table-column prop="request_type" label="申请类型" width="120">
                <template #default="{ row }"><el-tag effect="plain">{{ row.request_type }}</el-tag></template>
            </el-table-column>
            <el-table-column prop="course_name" label="课程" min-width="140" />
            <el-table-column prop="term_name" label="学期" min-width="170" />
            <el-table-column prop="content" label="申请内容" min-width="200" />
            <el-table-column prop="reason" label="理由" min-width="140" />
            <el-table-column prop="created_at" label="提交时间" width="170">
                <template #default="{ row }">{{ row.created_at.replace('T', ' ') }}</template>
            </el-table-column>
            <el-table-column label="审批状态" width="100" align="center">
                <template #default="{ row }">
                    <el-tag :type="statusType[row.status] || 'info'">{{ row.status }}</el-tag>
                </template>
            </el-table-column>
        </el-table>

        <el-dialog v-model="dialogVisible" title="发起教学申请" width="480px">
            <el-form :model="form" label-width="90px">
                <el-form-item label="申请类型">
                    <el-select v-model="form.request_type" style="width: 100%">
                        <el-option label="开课申请" value="开课申请" />
                        <el-option label="扩容申请" value="扩容申请" />
                        <el-option label="调课申请" value="调课申请" />
                        <el-option label="停课申请" value="停课申请" />
                        <el-option label="成绩修改申请" value="成绩修改申请" />
                    </el-select>
                </el-form-item>
                <el-form-item label="课程名称">
                    <el-input v-model="form.course_name" placeholder="如：数据库原理" />
                </el-form-item>
                <el-form-item label="申请内容">
                    <el-input v-model="form.content" type="textarea" :rows="2" placeholder="如：容量 40→50 / 调整到周四3-4节" />
                </el-form-item>
                <el-form-item label="申请理由">
                    <el-input v-model="form.reason" type="textarea" :rows="2" placeholder="请说明申请原因" />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="dialogVisible = false">取消</el-button>
                <el-button type="primary" @click="submit">提交申请</el-button>
            </template>
        </el-dialog>
    </div>
</template>

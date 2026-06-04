<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '@/api/services'

const loading = ref(false)
const years = ref([])
const windows = ref([])

const winType = { 选课: 'success', 退课: 'warning', 成绩录入: 'primary', 成绩公布: 'info' }
const winStatus = { 进行中: 'success', 未开始: 'info', 已结束: 'danger' }
const windowTypeOptions = Object.keys(winType)

// 当前学期（跨学年查找 is_current 的那个）及其业务时间窗口
const currentTerm = computed(() => {
    for (const y of years.value) {
        const t = (y.terms || []).find((x) => x.is_current)
        if (t) return t
    }
    return null
})
const currentWindows = computed(() =>
    currentTerm.value ? windows.value.filter((w) => w.term_id === currentTerm.value.term_id) : [],
)

// 编辑业务时间窗口起止时间
const editVisible = ref(false)
const editSaving = ref(false)
const editForm = reactive({ window_id: null, window_type: '', term_name: '', start_time: '', end_time: '' })

// 后端可能返回 ISO（含 T）或空格分隔，统一规整为 'YYYY-MM-DD HH:mm:ss' 供日期选择器使用
function toPickerStr(val) {
    if (!val) return ''
    return String(val).replace('T', ' ').slice(0, 19)
}

function openEditWindow(row) {
    Object.assign(editForm, {
        window_id: row.window_id,
        window_type: row.window_type,
        term_name: row.term_name,
        start_time: toPickerStr(row.start_time),
        end_time: toPickerStr(row.end_time),
    })
    editVisible.value = true
}

async function saveWindow() {
    if (!editForm.start_time || !editForm.end_time) {
        ElMessage.warning('请选择开始时间与结束时间')
        return
    }
    if (editForm.start_time >= editForm.end_time) {
        ElMessage.warning('开始时间必须早于结束时间')
        return
    }
    editSaving.value = true
    try {
        await adminApi.updateBusinessWindow(editForm.window_id, {
            window_type: editForm.window_type,
            start_time: editForm.start_time,
            end_time: editForm.end_time,
        })
        ElMessage.success('业务时间窗口已更新')
        editVisible.value = false
        await load()
    } finally {
        editSaving.value = false
    }
}

async function load() {
    loading.value = true
    try {
        const [t, w] = await Promise.all([adminApi.terms(), adminApi.businessWindows()])
        years.value = t
        windows.value = w
    } finally {
        loading.value = false
    }
}

async function setCurrent(term) {
    try {
        await adminApi.setCurrentTerm(term.term_id)
        ElMessage.success(`已将「${term.term_name}」设为当前学期`)
        await load()
    } catch (e) {
        await load()
    }
}
onMounted(load)

function formatTime(val) {
    if (!val) return ''
    const d = new Date(val)
    return d.toLocaleString('zh-CN', { hour12: false }).replace(/\//g, '-')
}
</script>

<template>
    <div v-loading="loading">
        <div class="page-header">
            <div>
                <h2>学年学期管理</h2>
                <div class="subtitle">每个学年包含第一、第二两个学期，并设置当前学期</div>
            </div>
            <el-button type="primary" :icon="'Plus'" @click="ElMessage.info('演示环境：新建学年功能占位')">新建学年</el-button>
        </div>

        <el-card v-for="y in years" :key="y.academic_year_name" shadow="never" style="margin-bottom: 16px">
            <template #header><strong>{{ y.academic_year_name }}</strong></template>
            <el-table :data="y.terms" border>
                <el-table-column prop="term_name" label="学期" min-width="180" />
                <el-table-column prop="term_no" label="学期序号" width="100" align="center" />
                <el-table-column prop="start_date" label="开始日期" width="130" />
                <el-table-column prop="end_date" label="结束日期" width="130" />
                <el-table-column label="当前学期" width="110" align="center">
                    <template #default="{ row }">
                        <el-tag v-if="row.is_current" type="success">当前</el-tag>
                        <span v-else>—</span>
                    </template>
                </el-table-column>
                <el-table-column label="操作" width="140" align="center">
                    <template #default="{ row }">
                        <el-button v-if="!row.is_current" size="small" type="primary" @click="setCurrent(row)">设为当前</el-button>
                    </template>
                </el-table-column>
            </el-table>
        </el-card>

        <el-card shadow="never">
            <template #header>
                <strong>当前学期业务时间窗口</strong>
                <el-tag v-if="currentTerm" type="success" effect="plain" style="margin-left: 8px">
                    {{ currentTerm.term_name }}
                </el-tag>
            </template>
            <el-table :data="currentWindows" border empty-text="当前学期暂无业务时间窗口">
                <el-table-column label="业务类型" width="120" align="center">
                    <template #default="{ row }"><el-tag :type="winType[row.window_type]">{{ row.window_type }}</el-tag></template>
                </el-table-column>
                <el-table-column prop="term_name" label="学期" min-width="180" />
                <el-table-column label="开始时间" width="180">
                    <template #default="{ row }">{{ formatTime(row.start_time) }}</template>
                </el-table-column>
                <el-table-column label="结束时间" width="180">
                    <template #default="{ row }">{{ formatTime(row.end_time) }}</template>
                </el-table-column>
                <el-table-column label="状态" width="100" align="center">
                    <template #default="{ row }"><el-tag :type="winStatus[row.status]">{{ row.status }}</el-tag></template>
                </el-table-column>
                <el-table-column label="操作" width="120" align="center">
                    <template #default="{ row }">
                        <el-button size="small" @click="openEditWindow(row)">修改时间</el-button>
                    </template>
                </el-table-column>
            </el-table>
        </el-card>

        <el-dialog v-model="editVisible" title="修改业务时间窗口" width="460px">
            <el-form :model="editForm" label-width="90px">
                <el-form-item label="业务类型">
                    <el-select v-model="editForm.window_type" style="width: 160px">
                        <el-option v-for="ty in windowTypeOptions" :key="ty" :label="ty" :value="ty" />
                    </el-select>
                    <span style="margin-left: 8px; color: var(--el-text-color-secondary)">{{ editForm.term_name }}</span>
                </el-form-item>
                <el-form-item label="开始时间">
                    <el-date-picker
                        v-model="editForm.start_time" type="datetime"
                        value-format="YYYY-MM-DD HH:mm:ss" placeholder="选择开始时间" style="width: 100%"
                    />
                </el-form-item>
                <el-form-item label="结束时间">
                    <el-date-picker
                        v-model="editForm.end_time" type="datetime"
                        value-format="YYYY-MM-DD HH:mm:ss" placeholder="选择结束时间" style="width: 100%"
                    />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="editVisible = false">取消</el-button>
                <el-button type="primary" :loading="editSaving" @click="saveWindow">保存</el-button>
            </template>
        </el-dialog>
    </div>
</template>

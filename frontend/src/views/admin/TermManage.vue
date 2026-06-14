<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
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

// 新建学年（自动创建第一、第二两个学期）
const addVisible = ref(false)
const addSaving = ref(false)
const addForm = reactive({ academic_year_name: '', term1: null, term2: null })

// 依据最新学年推算下一学年名，如 2025-2026学年 → 2026-2027学年
function suggestYearName() {
    const m = (years.value[0]?.academic_year_name || '').match(/^(\d{4})-(\d{4})/)
    if (m) return `${+m[1] + 1}-${+m[2] + 1}学年`
    const y = new Date().getFullYear()
    return `${y}-${y + 1}学年`
}

function openAddYear() {
    Object.assign(addForm, { academic_year_name: suggestYearName(), term1: null, term2: null })
    addVisible.value = true
}

async function saveYear() {
    if (!addForm.academic_year_name.trim()) {
        ElMessage.warning('请填写学年名称')
        return
    }
    addSaving.value = true
    try {
        await adminApi.createAcademicYear({
            academic_year_name: addForm.academic_year_name.trim(),
            term1_start: addForm.term1?.[0] || '',
            term1_end: addForm.term1?.[1] || '',
            term2_start: addForm.term2?.[0] || '',
            term2_end: addForm.term2?.[1] || '',
        })
        ElMessage.success('学年已创建')
        addVisible.value = false
        await load()
    } finally {
        addSaving.value = false
    }
}

// 删除学年（仅限未开始、无开课记录的学年；具体规则由后端校验）
async function removeYear(y) {
    try {
        await ElMessageBox.confirm(
            `确定删除学年「${y.academic_year_name}」吗？将一并删除其下的学期，此操作不可恢复。`,
            '删除学年',
            { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' },
        )
    } catch {
        return // 取消
    }
    try {
        await adminApi.deleteAcademicYear(y.academic_year_id)
        ElMessage.success('学年已删除')
        await load()
    } catch (e) {
        // 后端拒绝（如已开始/有开课记录）时给出提示
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
            <el-button type="primary" :icon="'Plus'" @click="openAddYear">新建学年</el-button>
        </div>

        <el-card v-for="y in years" :key="y.academic_year_id" shadow="never" style="margin-bottom: 16px">
            <template #header>
                <div style="display: flex; align-items: center; justify-content: space-between">
                    <strong>{{ y.academic_year_name }}</strong>
                    <el-button size="small" type="danger" plain :icon="'Delete'" @click="removeYear(y)">
                        删除学年
                    </el-button>
                </div>
            </template>
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

        <el-dialog v-model="addVisible" title="新建学年" width="480px">
            <el-form :model="addForm" label-width="100px">
                <el-form-item label="学年名称" required>
                    <el-input v-model="addForm.academic_year_name" placeholder="如：2026-2027学年" />
                </el-form-item>
                <el-form-item label="第一学期">
                    <el-date-picker
                        v-model="addForm.term1" type="daterange"
                        value-format="YYYY-MM-DD" range-separator="至"
                        start-placeholder="开始日期" end-placeholder="结束日期" style="width: 100%"
                    />
                </el-form-item>
                <el-form-item label="第二学期">
                    <el-date-picker
                        v-model="addForm.term2" type="daterange"
                        value-format="YYYY-MM-DD" range-separator="至"
                        start-placeholder="开始日期" end-placeholder="结束日期" style="width: 100%"
                    />
                </el-form-item>
                <div style="color: var(--el-text-color-secondary); font-size: 12px; line-height: 1.5">
                    将自动创建该学年的第一、第二两个学期；日期可留空，之后再补。
                </div>
            </el-form>
            <template #footer>
                <el-button @click="addVisible = false">取消</el-button>
                <el-button type="primary" :loading="addSaving" @click="saveYear">创建</el-button>
            </template>
        </el-dialog>
    </div>
</template>

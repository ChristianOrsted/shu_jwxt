<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { teacherApi } from '@/api/services'

const loading = ref(false)
const offerings = ref([])
const currentOffering = ref(null)
const rows = ref([])

// 总评比例：平时30% 实验20% 期末50%
const weights = { usual: 0.3, experiment: 0.2, final: 0.5 }

async function load() {
    offerings.value = (await teacherApi.offerings()).filter((o) => o.status !== '已取消')
    if (offerings.value.length) {
        currentOffering.value = offerings.value[0].offering_id
        await loadSheet()
    }
}

async function loadSheet() {
    if (!currentOffering.value) return
    loading.value = true
    try {
        rows.value = await teacherApi.gradeSheet(currentOffering.value)
    } finally {
        loading.value = false
    }
}

function recalc(row) {
    const { usual_score: u, experiment_score: e, final_score: f } = row
    if (u == null || e == null || f == null) {
        row.total_score = null
        return
    }
    row.total_score = Math.round(u * weights.usual + e * weights.experiment + f * weights.final)
}

const locked = (row) => ['已提交', '已发布', '已冻结'].includes(row.score_status)

async function saveDraft() {
    await teacherApi.saveGrades(currentOffering.value, rows.value)
    rows.value.forEach((r) => {
        if (!locked(r) && r.total_score != null) r.score_status = '已录入'
    })
    ElMessage.success('成绩已保存为草稿')
}

async function submitAll() {
    const unfilled = rows.value.filter((r) => r.total_score == null)
    if (unfilled.length) {
        ElMessage.warning(`还有 ${unfilled.length} 名学生成绩未录入完整`)
        return
    }
    try {
        await ElMessageBox.confirm(
            '提交后成绩将不可随意修改，如需更改需向管理员申请。确认提交？',
            '提交成绩',
            { confirmButtonText: '确认提交', cancelButtonText: '取消', type: 'warning' },
        )
        await teacherApi.submitGrades(currentOffering.value)
        rows.value.forEach((r) => (r.score_status = '已提交'))
        ElMessage.success('成绩已提交，等待管理员发布')
    } catch (e) {
        if (e !== 'cancel') ElMessage.error(e.message || '提交失败')
    }
}
onMounted(load)
</script>

<template>
    <div>
        <div class="page-header">
            <div>
                <h2>成绩录入</h2>
                <div class="subtitle">总评 = 平时×30% + 实验×20% + 期末×50%（≥60 通过）</div>
            </div>
        </div>

        <div class="toolbar">
            <span>选择教学班：</span>
            <el-select v-model="currentOffering" style="width: 320px" @change="loadSheet">
                <el-option
                    v-for="o in offerings"
                    :key="o.offering_id"
                    :label="`${o.term_name} · ${o.teaching_class_name}`"
                    :value="o.offering_id"
                />
            </el-select>
            <div style="margin-left: auto">
                <el-button :icon="'DocumentChecked'" @click="saveDraft">保存草稿</el-button>
                <el-button type="primary" :icon="'Upload'" @click="submitAll">提交成绩</el-button>
            </div>
        </div>

        <el-table :data="rows" v-loading="loading" border stripe>
            <el-table-column type="index" label="序号" width="60" align="center" />
            <el-table-column prop="student_no" label="学号" width="120" />
            <el-table-column prop="real_name" label="姓名" width="100" />
            <el-table-column label="平时(30%)" width="130">
                <template #default="{ row }">
                    <el-input-number v-model="row.usual_score" :min="0" :max="100" :disabled="locked(row)" size="small" controls-position="right" @change="recalc(row)" style="width: 100px" />
                </template>
            </el-table-column>
            <el-table-column label="实验(20%)" width="130">
                <template #default="{ row }">
                    <el-input-number v-model="row.experiment_score" :min="0" :max="100" :disabled="locked(row)" size="small" controls-position="right" @change="recalc(row)" style="width: 100px" />
                </template>
            </el-table-column>
            <el-table-column label="期末(50%)" width="130">
                <template #default="{ row }">
                    <el-input-number v-model="row.final_score" :min="0" :max="100" :disabled="locked(row)" size="small" controls-position="right" @change="recalc(row)" style="width: 100px" />
                </template>
            </el-table-column>
            <el-table-column label="总评" width="90" align="center">
                <template #default="{ row }">
                    <span v-if="row.total_score != null" :class="row.total_score >= 60 ? 'capacity-ok' : 'capacity-full'">
                        {{ row.total_score }}
                    </span>
                    <span v-else>—</span>
                </template>
            </el-table-column>
            <el-table-column label="是否通过" width="90" align="center">
                <template #default="{ row }">
                    <el-tag v-if="row.total_score != null" :type="row.total_score >= 60 ? 'success' : 'danger'" size="small">
                        {{ row.total_score >= 60 ? '通过' : '挂科' }}
                    </el-tag>
                    <span v-else>—</span>
                </template>
            </el-table-column>
            <el-table-column prop="score_status" label="状态" width="90" align="center">
                <template #default="{ row }">
                    <el-tag :type="locked(row) ? 'info' : 'warning'" size="small">{{ row.score_status }}</el-tag>
                </template>
            </el-table-column>
        </el-table>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi } from '@/api/services'

const loading = ref(false)
const list = ref([])
const detailMap = ref({})          // offering_id -> 学生成绩明细数组
const detailLoading = ref({})      // offering_id -> 是否加载中

async function load() {
    loading.value = true
    try {
        list.value = await adminApi.gradePublish()
    } finally {
        loading.value = false
    }
}

async function loadDetail(row) {
    const id = row.offering_id
    if (detailMap.value[id] || detailLoading.value[id]) return
    detailLoading.value = { ...detailLoading.value, [id]: true }
    try {
        detailMap.value = { ...detailMap.value, [id]: await adminApi.gradeDetail(id) }
    } catch (e) {
        ElMessage.error(e.message || '获取成绩明细失败')
    } finally {
        detailLoading.value = { ...detailLoading.value, [id]: false }
    }
}

function onExpand(row, expandedRows) {
    if (expandedRows.includes(row)) loadDetail(row)
}

function fmt(v) {
    return v === null || v === undefined || v === '' ? '—' : v
}

async function publish(row) {
    try {
        await ElMessageBox.confirm(
            `确认发布《${row.course_name}》的成绩吗？发布后学生即可查看，并自动生成挂科/重修记录。`,
            '发布成绩',
            { confirmButtonText: '确认发布', cancelButtonText: '取消', type: 'warning' },
        )
        await adminApi.publishGrade(row.offering_id)
        row.score_status = '已发布'
        row.can_publish = false
        // 失效明细缓存，下次展开重新拉取最新状态
        const { [row.offering_id]: _omit, ...rest } = detailMap.value
        detailMap.value = rest
        ElMessage.success('成绩已发布')
    } catch (e) {
        if (e !== 'cancel') ElMessage.error(e.message || '发布失败')
    }
}
onMounted(load)
</script>

<template>
    <div>
        <div class="page-header">
            <div>
                <h2>成绩发布</h2>
                <div class="subtitle">审核教师已提交的成绩并发布，未发布前学生不可见</div>
            </div>
        </div>

        <el-table :data="list" v-loading="loading" border stripe row-key="offering_id" @expand-change="onExpand">
            <el-table-column type="expand">
                <template #default="{ row }">
                    <div class="detail-wrap" v-loading="detailLoading[row.offering_id]">
                        <el-table :data="detailMap[row.offering_id] || []" size="small" border>
                            <el-table-column prop="student_no" label="学号" width="130" />
                            <el-table-column prop="real_name" label="姓名" width="110" />
                            <el-table-column label="平时成绩" width="100" align="center">
                                <template #default="{ row: r }">{{ fmt(r.usual_score) }}</template>
                            </el-table-column>
                            <el-table-column label="实验成绩" width="100" align="center">
                                <template #default="{ row: r }">{{ fmt(r.experiment_score) }}</template>
                            </el-table-column>
                            <el-table-column label="期末成绩" width="100" align="center">
                                <template #default="{ row: r }">{{ fmt(r.final_score) }}</template>
                            </el-table-column>
                            <el-table-column label="总评" width="100" align="center">
                                <template #default="{ row: r }">
                                    <strong>{{ fmt(r.total_score) }}</strong>
                                </template>
                            </el-table-column>
                            <el-table-column label="状态" width="100" align="center">
                                <template #default="{ row: r }">
                                    <el-tag size="small" :type="r.score_status === '已发布' ? 'success' : r.score_status === '已提交' ? 'warning' : 'info'">
                                        {{ r.score_status }}
                                    </el-tag>
                                </template>
                            </el-table-column>
                        </el-table>
                        <el-empty
                            v-if="!detailLoading[row.offering_id] && (detailMap[row.offering_id] || []).length === 0"
                            description="暂无学生成绩" :image-size="60" />
                    </div>
                </template>
            </el-table-column>
            <el-table-column prop="course_name" label="课程" min-width="140" />
            <el-table-column prop="teacher_name" label="任课教师" width="110" />
            <el-table-column prop="term_name" label="学期" min-width="180" />
            <el-table-column label="录入进度" width="120" align="center">
                <template #default="{ row }">{{ row.submitted_count }}/{{ row.total_count }}</template>
            </el-table-column>
            <el-table-column label="成绩状态" width="110" align="center">
                <template #default="{ row }">
                    <el-tag :type="row.score_status === '已提交' ? 'warning' : row.score_status === '已发布' ? 'success' : 'info'">
                        {{ row.score_status }}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column label="操作" width="140" align="center" fixed="right">
                <template #default="{ row }">
                    <el-button size="small" type="primary" :disabled="!row.can_publish" @click="publish(row)">
                        发布
                    </el-button>
                </template>
            </el-table-column>
        </el-table>
    </div>
</template>

<style scoped>
.detail-wrap {
    padding: 12px 16px 16px 48px;
    min-height: 60px;
}
</style>

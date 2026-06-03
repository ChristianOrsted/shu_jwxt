<script setup>
import { ref, onMounted } from 'vue'
import { teacherApi } from '@/api/services'

const loading = ref(false)
const offerings = ref([])
const currentOffering = ref(null)
const roster = ref([])

async function load() {
    offerings.value = (await teacherApi.offerings()).filter((o) => o.status !== '已取消')
    if (offerings.value.length) {
        currentOffering.value = offerings.value[0].offering_id
        await loadRoster()
    }
}

async function loadRoster() {
    if (!currentOffering.value) return
    loading.value = true
    try {
        roster.value = await teacherApi.roster(currentOffering.value)
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
                <h2>选课名单</h2>
                <div class="subtitle">查看本人课程下的学生名单</div>
            </div>
        </div>

        <div class="toolbar">
            <span>选择教学班：</span>
            <el-select v-model="currentOffering" style="width: 320px" @change="loadRoster">
                <el-option
                    v-for="o in offerings"
                    :key="o.offering_id"
                    :label="`${o.term_name} · ${o.teaching_class_name}`"
                    :value="o.offering_id"
                />
            </el-select>
            <el-tag type="primary">共 {{ roster.length }} 人</el-tag>
        </div>

        <el-table :data="roster" v-loading="loading" border stripe>
            <el-table-column type="index" label="序号" width="60" align="center" />
            <el-table-column prop="student_no" label="学号" width="120" />
            <el-table-column prop="real_name" label="姓名" width="100" />
            <el-table-column prop="major_name" label="专业" min-width="160" />
            <el-table-column prop="class_name" label="班级" min-width="130" />
            <el-table-column label="重修" width="80" align="center">
                <template #default="{ row }">
                    <el-tag v-if="row.is_retake" type="warning" size="small">重修</el-tag>
                    <span v-else>—</span>
                </template>
            </el-table-column>
            <el-table-column prop="enroll_time" label="选课时间" width="170">
                <template #default="{ row }">{{ row.enroll_time.replace('T', ' ') }}</template>
            </el-table-column>
            <el-table-column prop="score_status" label="成绩状态" width="100" align="center" />
        </el-table>
    </div>
</template>

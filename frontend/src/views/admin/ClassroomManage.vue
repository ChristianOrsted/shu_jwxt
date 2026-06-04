<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi } from '@/api/services'

const loading = ref(false)
const list = ref([])
const keyword = ref('')
const statusFilter = ref('')
const dialogVisible = ref(false)
const saving = ref(false)
const isEdit = ref(false)

const statusOptions = ['可用', '维修中', '停用']
const statusType = { 可用: 'success', 维修中: 'warning', 停用: 'danger' }

const blank = () => ({ classroom_id: null, building: '', room_no: '', capacity: 40, status: '可用' })
const form = reactive(blank())

const filtered = computed(() =>
    list.value.filter((r) => {
        const kw = keyword.value.trim()
        const matchKw = !kw || `${r.building}${r.room_no}`.includes(kw)
        const matchStatus = !statusFilter.value || r.status === statusFilter.value
        return matchKw && matchStatus
    }),
)

async function load() {
    loading.value = true
    try {
        list.value = await adminApi.classrooms()
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
    if (!form.building.trim() || !form.room_no.trim()) {
        ElMessage.warning('请填写教学楼与教室号')
        return
    }
    if (form.capacity < 1) {
        ElMessage.warning('容量必须大于 0')
        return
    }
    saving.value = true
    try {
        await adminApi.saveClassroom({ ...form })
        ElMessage.success('保存成功')
        dialogVisible.value = false
        await load()
    } finally {
        saving.value = false
    }
}

async function remove(row) {
    try {
        await ElMessageBox.confirm(`确定删除教室「${row.building}${row.room_no}」吗？`, '删除教室', {
            type: 'warning',
            confirmButtonText: '删除',
            cancelButtonText: '取消',
        })
    } catch {
        return
    }
    try {
        await adminApi.deleteClassroom(row.classroom_id)
        ElMessage.success('删除成功')
        await load()
    } catch (e) {
        // 拦截器已提示（如被排课占用），重新拉取保持一致
        await load()
    }
}

onMounted(load)
</script>

<template>
    <div>
        <div class="page-header">
            <div>
                <h2>教室资源管理</h2>
                <div class="subtitle">维护教室、容量与可用状态，用于排课和扩容判断</div>
            </div>
            <el-button type="primary" :icon="'Plus'" @click="openCreate">新增教室</el-button>
        </div>

        <div class="toolbar">
            <el-input
                v-model="keyword" placeholder="搜索教学楼 / 教室号"
                :prefix-icon="'Search'" clearable style="width: 240px"
            />
            <el-select v-model="statusFilter" placeholder="全部状态" clearable style="width: 140px">
                <el-option v-for="s in statusOptions" :key="s" :label="s" :value="s" />
            </el-select>
        </div>

        <el-table :data="filtered" v-loading="loading" border stripe>
            <el-table-column prop="classroom_id" label="编号" width="80" align="center" />
            <el-table-column prop="building" label="教学楼" min-width="160" />
            <el-table-column prop="room_no" label="教室号" width="120" />
            <el-table-column prop="capacity" label="容量" width="100" align="center" />
            <el-table-column label="状态" width="110" align="center">
                <template #default="{ row }">
                    <el-tag :type="statusType[row.status]">{{ row.status }}</el-tag>
                </template>
            </el-table-column>
            <el-table-column label="操作" width="160" align="center" fixed="right">
                <template #default="{ row }">
                    <el-button size="small" @click="openEdit(row)">编辑</el-button>
                    <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
                </template>
            </el-table-column>
        </el-table>

        <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑教室' : '新增教室'" width="460px">
            <el-form :model="form" label-width="90px">
                <el-form-item label="教学楼" required>
                    <el-input v-model="form.building" placeholder="如：东区教学楼 A" />
                </el-form-item>
                <el-form-item label="教室号" required>
                    <el-input v-model="form.room_no" placeholder="如：305" />
                </el-form-item>
                <el-form-item label="容量" required>
                    <el-input-number v-model="form.capacity" :min="1" :max="1000" />
                </el-form-item>
                <el-form-item label="状态">
                    <el-select v-model="form.status" style="width: 160px">
                        <el-option v-for="s in statusOptions" :key="s" :label="s" :value="s" />
                    </el-select>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="dialogVisible = false">取消</el-button>
                <el-button type="primary" :loading="saving" @click="save">保存</el-button>
            </template>
        </el-dialog>
    </div>
</template>

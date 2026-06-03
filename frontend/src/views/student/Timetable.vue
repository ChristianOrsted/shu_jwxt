<script setup>
import { ref, computed, onMounted } from 'vue'
import { studentApi } from '@/api/services'
import { sections, weekdayNames } from '@/api/mock'

const loading = ref(false)
const entries = ref([])
const weekdays = [1, 2, 3, 4, 5, 6, 7]
const colors = ['#e6f4ff', '#f6ffed', '#fff7e6', '#fff0f6', '#f9f0ff', '#e6fffb']

// 构建 节次 x 星期 网格，记录每个单元被哪个课程占用
const grid = computed(() => {
    // cell[section][weekday] = entry | null
    const cell = {}
    entries.value.forEach((e, idx) => {
        for (let s = e.start_section; s <= e.end_section; s++) {
            if (!cell[s]) cell[s] = {}
            cell[s][e.weekday] = { ...e, isStart: s === e.start_section, span: e.end_section - e.start_section + 1, color: colors[idx % colors.length] }
        }
    })
    return cell
})

async function load() {
    loading.value = true
    try {
        entries.value = await studentApi.timetable()
    } finally {
        loading.value = false
    }
}

function printPage() {
    window.print()
}

function cellAt(section, weekday) {
    return grid.value[section]?.[weekday] || null
}
// 如果该单元属于跨节次课程的非起始行，则跳过渲染
function shouldRender(section, weekday) {
    const c = cellAt(section, weekday)
    if (!c) return true
    return c.isStart
}
onMounted(load)
</script>

<template>
    <div>
        <div class="page-header">
            <div>
                <h2>我的课表</h2>
                <div class="subtitle">2025-2026学年第二学期</div>
            </div>
            <el-button :icon="'Printer'" @click="printPage">打印 / 导出</el-button>
        </div>

        <el-card v-loading="loading" shadow="never">
            <table class="timetable">
                <thead>
                    <tr>
                        <th class="time-col">节次</th>
                        <th v-for="w in weekdays" :key="w">{{ weekdayNames[w] }}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="sec in sections" :key="sec.no">
                        <td class="time-col">
                            <div class="sec-no">第{{ sec.no }}节</div>
                            <div class="sec-time">{{ sec.time }}</div>
                        </td>
                        <template v-for="w in weekdays" :key="w">
                            <td
                                v-if="shouldRender(sec.no, w)"
                                :rowspan="cellAt(sec.no, w)?.span || 1"
                                :class="{ 'has-course': cellAt(sec.no, w) }"
                            >
                                <div
                                    v-if="cellAt(sec.no, w)"
                                    class="course-block"
                                    :style="{ background: cellAt(sec.no, w).color }"
                                >
                                    <div class="cname">{{ cellAt(sec.no, w).course_name }}</div>
                                    <div class="cmeta">{{ cellAt(sec.no, w).teacher_name }}</div>
                                    <div class="cmeta">{{ cellAt(sec.no, w).location }}</div>
                                </div>
                            </td>
                        </template>
                    </tr>
                </tbody>
            </table>
        </el-card>
    </div>
</template>

<style scoped>
.timetable {
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
}
.timetable th,
.timetable td {
    border: 1px solid #ebeef5;
    text-align: center;
    height: 56px;
    vertical-align: middle;
    font-size: 13px;
}
.timetable th {
    background: #fafafa;
    padding: 8px 0;
}
.time-col {
    width: 90px;
    background: #fafafa;
}
.sec-no {
    font-weight: 600;
}
.sec-time {
    color: #8a8f99;
    font-size: 11px;
}
.course-block {
    border-radius: 6px;
    padding: 6px 4px;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 2px;
}
.cname {
    font-weight: 600;
    color: #1f2329;
}
.cmeta {
    color: #5a5f66;
    font-size: 12px;
}
</style>

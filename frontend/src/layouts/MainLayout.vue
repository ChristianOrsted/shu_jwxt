<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { auth, clearAuth, currentRole } from '@/store/auth'

const route = useRoute()
const router = useRouter()

const role = computed(() => currentRole())

const roleLabel = computed(
    () => ({ student: '学生', teacher: '教师', admin: '管理员' }[role.value] || ''),
)

// 各角色菜单
const menus = {
    student: [
        { index: '/student/courses', title: '选课中心', icon: 'Search' },
        { index: '/student/my-courses', title: '已选课程', icon: 'List' },
        { index: '/student/timetable', title: '我的课表', icon: 'Calendar' },
        { index: '/student/grades', title: '成绩查询', icon: 'Document' },
        { index: '/student/retake', title: '挂科重修', icon: 'RefreshRight' },
        { index: '/student/notifications', title: '消息通知', icon: 'Bell' },
        { index: '/student/profile', title: '个人信息', icon: 'User' },
    ],
    teacher: [
        { index: '/teacher/offerings', title: '授课任务', icon: 'Notebook' },
        { index: '/teacher/roster', title: '选课名单', icon: 'UserFilled' },
        { index: '/teacher/grade-input', title: '成绩录入', icon: 'EditPen' },
        { index: '/teacher/statistics', title: '成绩统计', icon: 'DataAnalysis' },
        { index: '/teacher/requests', title: '教学申请', icon: 'Promotion' },
        { index: '/teacher/profile', title: '个人信息', icon: 'User' },
    ],
    admin: [
        { index: '/admin/dashboard', title: '总览', icon: 'Odometer' },
        { index: '/admin/users', title: '用户管理', icon: 'User' },
        { index: '/admin/departments', title: '学院管理', icon: 'OfficeBuilding' },
        { index: '/admin/classes', title: '班级管理', icon: 'UserFilled' },
        { index: '/admin/terms', title: '学年学期', icon: 'Calendar' },
        { index: '/admin/courses', title: '课程库', icon: 'Collection' },
        { index: '/admin/classrooms', title: '教室资源', icon: 'School' },
        { index: '/admin/offerings', title: '开课管理', icon: 'Notebook' },
        { index: '/admin/approvals', title: '申请审批', icon: 'Stamp' },
        { index: '/admin/grade-publish', title: '成绩发布', icon: 'Upload' },
        { index: '/admin/retake', title: '重修管理', icon: 'RefreshRight' },
        { index: '/admin/statistics', title: '统计分析', icon: 'DataAnalysis' },
        { index: '/admin/logs', title: '操作日志', icon: 'Tickets' },
    ],
}

const menuItems = computed(() => menus[role.value] || [])
const activeMenu = computed(() => route.path)
const pageTitle = computed(() => route.meta.title || '')

function handleSelect(index) {
    router.push(index)
}

async function logout() {
    try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
            confirmButtonText: '退出',
            cancelButtonText: '取消',
            type: 'warning',
        })
        clearAuth()
        router.replace('/login')
    } catch {
        // 取消
    }
}
</script>

<template>
    <el-container class="layout">
        <el-aside width="220px" class="aside">
            <div class="logo">
                <el-icon><Reading /></el-icon>
                <span>教务选课系统</span>
            </div>
            <el-menu
                :default-active="activeMenu"
                class="side-menu"
                background-color="#001529"
                text-color="#c0c4cc"
                active-text-color="#ffffff"
                @select="handleSelect"
            >
                <el-menu-item v-for="m in menuItems" :key="m.index" :index="m.index">
                    <el-icon><component :is="m.icon" /></el-icon>
                    <span>{{ m.title }}</span>
                </el-menu-item>
            </el-menu>
        </el-aside>

        <el-container>
            <el-header class="header">
                <div class="crumb">
                    <span class="role-tag">{{ roleLabel }}端</span>
                    <el-divider direction="vertical" />
                    <span class="title">{{ pageTitle }}</span>
                </div>
                <el-dropdown @command="(c) => c === 'logout' && logout()">
                    <span class="user">
                        <el-icon><Avatar /></el-icon>
                        {{ auth.user?.real_name || auth.user?.username }}
                        <el-icon><ArrowDown /></el-icon>
                    </span>
                    <template #dropdown>
                        <el-dropdown-menu>
                            <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                        </el-dropdown-menu>
                    </template>
                </el-dropdown>
            </el-header>

            <el-main class="main">
                <router-view v-slot="{ Component }">
                    <component :is="Component" />
                </router-view>
            </el-main>
        </el-container>
    </el-container>
</template>

<style scoped>
.layout {
    height: 100vh;
}
.aside {
    background: #001529;
    overflow-x: hidden;
}
.logo {
    height: 60px;
    display: flex;
    align-items: center;
    gap: 8px;
    padding-left: 20px;
    color: #fff;
    font-size: 17px;
    font-weight: 600;
    background: #00203f;
}
.logo .el-icon {
    font-size: 22px;
}
.side-menu {
    border-right: none;
}
.header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #fff;
    border-bottom: 1px solid #ebeef5;
}
.crumb {
    display: flex;
    align-items: center;
}
.role-tag {
    color: var(--shu-primary);
    font-weight: 600;
}
.crumb .title {
    font-size: 16px;
    font-weight: 600;
}
.user {
    display: flex;
    align-items: center;
    gap: 6px;
    cursor: pointer;
    color: #1f2329;
}
.main {
    padding: 20px;
    background: #f5f7fa;
}
</style>

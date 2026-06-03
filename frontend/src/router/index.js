import { createRouter, createWebHistory } from 'vue-router'
import { isLoggedIn, currentRole, roleHome } from '@/store/auth'

const routes = [
    { path: '/', redirect: '/login' },
    { path: '/login', name: 'login', component: () => import('@/views/Login.vue'), meta: { public: true } },

    // 学生端
    {
        path: '/student',
        component: () => import('@/layouts/MainLayout.vue'),
        meta: { role: 'student' },
        children: [
            { path: 'profile', name: 'student-profile', component: () => import('@/views/student/Profile.vue'), meta: { title: '个人信息' } },
            { path: 'courses', name: 'student-courses', component: () => import('@/views/student/CourseList.vue'), meta: { title: '选课中心' } },
            { path: 'my-courses', name: 'student-my-courses', component: () => import('@/views/student/MyCourses.vue'), meta: { title: '已选课程' } },
            { path: 'timetable', name: 'student-timetable', component: () => import('@/views/student/Timetable.vue'), meta: { title: '我的课表' } },
            { path: 'grades', name: 'student-grades', component: () => import('@/views/student/Grades.vue'), meta: { title: '成绩查询' } },
            { path: 'retake', name: 'student-retake', component: () => import('@/views/student/Retake.vue'), meta: { title: '挂科重修' } },
            { path: 'notifications', name: 'student-notifications', component: () => import('@/views/student/Notifications.vue'), meta: { title: '消息通知' } },
        ],
    },

    // 教师端
    {
        path: '/teacher',
        component: () => import('@/layouts/MainLayout.vue'),
        meta: { role: 'teacher' },
        children: [
            { path: 'profile', name: 'teacher-profile', component: () => import('@/views/teacher/Profile.vue'), meta: { title: '个人信息' } },
            { path: 'offerings', name: 'teacher-offerings', component: () => import('@/views/teacher/Offerings.vue'), meta: { title: '授课任务' } },
            { path: 'roster', name: 'teacher-roster', component: () => import('@/views/teacher/Roster.vue'), meta: { title: '选课名单' } },
            { path: 'grade-input', name: 'teacher-grade-input', component: () => import('@/views/teacher/GradeInput.vue'), meta: { title: '成绩录入' } },
            { path: 'requests', name: 'teacher-requests', component: () => import('@/views/teacher/Requests.vue'), meta: { title: '教学申请' } },
            { path: 'statistics', name: 'teacher-statistics', component: () => import('@/views/teacher/Statistics.vue'), meta: { title: '成绩统计' } },
        ],
    },

    // 管理员端
    {
        path: '/admin',
        component: () => import('@/layouts/MainLayout.vue'),
        meta: { role: 'admin' },
        children: [
            { path: 'dashboard', name: 'admin-dashboard', component: () => import('@/views/admin/Dashboard.vue'), meta: { title: '总览' } },
            { path: 'users', name: 'admin-users', component: () => import('@/views/admin/UserManage.vue'), meta: { title: '用户管理' } },
            { path: 'terms', name: 'admin-terms', component: () => import('@/views/admin/TermManage.vue'), meta: { title: '学年学期' } },
            { path: 'courses', name: 'admin-courses', component: () => import('@/views/admin/CourseManage.vue'), meta: { title: '课程库' } },
            { path: 'classrooms', name: 'admin-classrooms', component: () => import('@/views/admin/ClassroomManage.vue'), meta: { title: '教室资源' } },
            { path: 'offerings', name: 'admin-offerings', component: () => import('@/views/admin/OfferingManage.vue'), meta: { title: '开课管理' } },
            { path: 'approvals', name: 'admin-approvals', component: () => import('@/views/admin/Approvals.vue'), meta: { title: '申请审批' } },
            { path: 'grade-publish', name: 'admin-grade-publish', component: () => import('@/views/admin/GradePublish.vue'), meta: { title: '成绩发布' } },
            { path: 'retake', name: 'admin-retake', component: () => import('@/views/admin/RetakeManage.vue'), meta: { title: '重修管理' } },
            { path: 'statistics', name: 'admin-statistics', component: () => import('@/views/admin/Statistics.vue'), meta: { title: '统计分析' } },
            { path: 'logs', name: 'admin-logs', component: () => import('@/views/admin/AuditLogs.vue'), meta: { title: '操作日志' } },
        ],
    },

    { path: '/:pathMatch(.*)*', redirect: '/login' },
]

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes,
})

// 路由守卫：未登录跳转登录页；登录后访问错误角色区域跳回自己首页
router.beforeEach((to) => {
    if (to.meta.public) {
        if (to.path === '/login' && isLoggedIn()) {
            return roleHome[currentRole()] || '/login'
        }
        return true
    }
    if (!isLoggedIn()) {
        return { path: '/login', query: { redirect: to.fullPath } }
    }
    if (to.meta.role && to.meta.role !== currentRole()) {
        return roleHome[currentRole()] || '/login'
    }
    return true
})

export default router

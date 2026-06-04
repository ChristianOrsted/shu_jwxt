// ============================================================================
// 业务接口封装
// ----------------------------------------------------------------------------
// USE_MOCK = true ：使用 mock.js 的假数据，前端可脱离后端独立运行（开发期）。
// USE_MOCK = false：走真实 Axios 请求（联调期），接口路径与 TEAM_DEVISION.md 一致。
// 每个函数返回 Promise，页面调用方式完全一致，切换时无需改动页面代码。
// ============================================================================
import http from './index'
import * as M from './mock'

export const USE_MOCK = false

// 模拟网络延迟，返回数据副本
function mock(data, delay = 200) {
    return new Promise((resolve) => {
        setTimeout(() => resolve(JSON.parse(JSON.stringify(data))), delay)
    })
}

// --------------------------- 认证 ---------------------------
export const authApi = {
    login(username, password, role) {
        if (USE_MOCK) {
            const acc = M.demoAccounts.find(
                (a) => a.username === username && a.password === password && a.role === role,
            )
            if (!acc) {
                return Promise.reject(new Error('用户名、密码或角色不正确'))
            }
            return mock({
                token: `mock-token-${role}`,
                user: { user_id: 1, username: acc.username, real_name: acc.real_name, role: acc.role },
            })
        }
        return http.post('/auth/login', { username, password, role })
    },
    currentTerm() {
        if (USE_MOCK) return mock(M.currentTerm)
        return http.get('/common/current-term')
    },
}

// --------------------------- 学生端 ---------------------------
export const studentApi = {
    profile() {
        return USE_MOCK ? mock(M.profiles.student) : http.get('/student/profile')
    },
    courses() {
        return USE_MOCK ? mock(M.availableCourses) : http.get('/student/courses')
    },
    enroll(offeringId) {
        return USE_MOCK ? mock({ offering_id: offeringId }) : http.post('/student/enroll', { offering_id: offeringId })
    },
    drop(offeringId) {
        return USE_MOCK ? mock({ offering_id: offeringId }) : http.delete(`/student/enroll/${offeringId}`)
    },
    myCourses() {
        return USE_MOCK ? mock(M.myCourses) : http.get('/student/my-courses')
    },
    timetable() {
        return USE_MOCK ? mock(M.timetable) : http.get('/student/timetable')
    },
    grades() {
        return USE_MOCK ? mock(M.grades) : http.get('/student/grades')
    },
    averageScore() {
        return USE_MOCK ? mock(M.averageScore) : http.get('/student/average-score')
    },
    retakeStatus() {
        return USE_MOCK ? mock(M.retakeStatus) : http.get('/student/retake')
    },
    notifications() {
        return USE_MOCK ? mock(M.notifications) : http.get('/student/notifications')
    },
}

// --------------------------- 教师端 ---------------------------
export const teacherApi = {
    profile() {
        return USE_MOCK ? mock(M.profiles.teacher) : http.get('/teacher/profile')
    },
    offerings() {
        return USE_MOCK ? mock(M.teacherOfferings) : http.get('/teacher/offerings')
    },
    roster(offeringId) {
        return USE_MOCK ? mock(M.rosters[offeringId] || []) : http.get(`/teacher/roster/${offeringId}`)
    },
    gradeSheet(offeringId) {
        return USE_MOCK ? mock(M.gradeSheets[offeringId] || []) : http.get(`/teacher/grade-sheet/${offeringId}`)
    },
    saveGrades(offeringId, rows) {
        return USE_MOCK ? mock({ ok: true }) : http.post('/teacher/grade', { offering_id: offeringId, rows })
    },
    submitGrades(offeringId) {
        return USE_MOCK ? mock({ ok: true }) : http.post('/teacher/grade/submit', { offering_id: offeringId })
    },
    requests() {
        return USE_MOCK ? mock(M.teacherRequests) : http.get('/teacher/requests')
    },
    submitRequest(payload) {
        return USE_MOCK ? mock({ ok: true }) : http.post('/teacher/requests', payload)
    },
    gradeStats() {
        return USE_MOCK ? mock(M.teacherGradeStats) : http.get('/teacher/grade-stats')
    },
}

// --------------------------- 管理员端 ---------------------------
export const adminApi = {
    statistics() {
        return USE_MOCK ? mock(M.adminStats) : http.get('/admin/statistics')
    },
    users() {
        return USE_MOCK ? mock(M.adminUsers) : http.get('/admin/users')
    },
    saveUser(payload) {
        return USE_MOCK ? mock({ ok: true }) : http.post('/admin/users', payload)
    },
    deleteUser(userId) {
        return USE_MOCK ? mock({ ok: true }) : http.delete(`/admin/users/${userId}`)
    },
    terms() {
        return USE_MOCK ? mock(M.adminTerms) : http.get('/admin/terms')
    },
    businessWindows() {
        return USE_MOCK ? mock(M.businessWindows) : http.get('/admin/business-windows')
    },
    courses() {
        return USE_MOCK ? mock(M.adminCourses) : http.get('/admin/courses')
    },
    saveCourse(payload) {
        return USE_MOCK ? mock({ ok: true }) : http.post('/admin/courses', payload)
    },
    toggleCourse(courseId, isEnabled) {
        return USE_MOCK ? mock({ ok: true }) : http.post(`/admin/courses/${courseId}/toggle`, { is_enabled: isEnabled })
    },
    classrooms() {
        return USE_MOCK ? mock(M.adminClassrooms) : http.get('/admin/classrooms')
    },
    saveClassroom(payload) {
        return USE_MOCK ? mock({ ok: true }) : http.post('/admin/classrooms', payload)
    },
    deleteClassroom(classroomId) {
        return USE_MOCK ? mock({ ok: true }) : http.delete(`/admin/classrooms/${classroomId}`)
    },
    teachers() {
        return USE_MOCK ? mock([]) : http.get('/admin/teachers')
    },
    departments() {
        return USE_MOCK ? mock([]) : http.get('/admin/departments')
    },
    saveDepartment(payload) {
        return USE_MOCK ? mock({ ok: true }) : http.post('/admin/departments', payload)
    },
    deleteDepartment(departmentId) {
        return USE_MOCK ? mock({ ok: true }) : http.delete(`/admin/departments/${departmentId}`)
    },
    majors() {
        return USE_MOCK ? mock([]) : http.get('/admin/majors')
    },
    classes() {
        return USE_MOCK ? mock([]) : http.get('/admin/classes')
    },
    offerings() {
        return USE_MOCK ? mock(M.adminOfferings) : http.get('/admin/offerings')
    },
    saveOffering(payload) {
        return USE_MOCK ? mock({ ok: true }) : http.post('/admin/offerings', payload)
    },
    toggleOfferingEnrollment(offeringId) {
        return USE_MOCK ? mock({ ok: true }) : http.post(`/admin/offerings/${offeringId}/toggle-enrollment`)
    },
    cancelOffering(offeringId) {
        return USE_MOCK ? mock({ ok: true }) : http.post(`/admin/offerings/${offeringId}/cancel`)
    },
    restoreOffering(offeringId) {
        return USE_MOCK ? mock({ ok: true }) : http.post(`/admin/offerings/${offeringId}/restore`)
    },
    updateOffering(offeringId, payload) {
        return USE_MOCK ? mock({ ok: true }) : http.put(`/admin/offerings/${offeringId}`, payload)
    },
    deleteOffering(offeringId) {
        return USE_MOCK ? mock({ ok: true }) : http.delete(`/admin/offerings/${offeringId}`)
    },
    approvals() {
        return USE_MOCK ? mock(M.adminApprovals) : http.get('/admin/approvals')
    },
    approve(requestId, result, comment) {
        return USE_MOCK ? mock({ ok: true }) : http.post('/admin/approve', { request_id: requestId, result, comment })
    },
    gradePublish() {
        return USE_MOCK ? mock(M.adminGradePublish) : http.get('/admin/grade-publish')
    },
    publishGrade(offeringId) {
        return USE_MOCK ? mock({ ok: true }) : http.post('/admin/grade/publish', { offering_id: offeringId })
    },
    retake() {
        return USE_MOCK ? mock(M.adminRetake) : http.get('/admin/retake')
    },
    auditLogs() {
        return USE_MOCK ? mock(M.auditLogs) : http.get('/admin/audit-logs')
    },
}

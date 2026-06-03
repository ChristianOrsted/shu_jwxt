import { reactive } from 'vue'

// 登录态：保存在内存中并持久化到 localStorage，刷新后自动恢复
const STORAGE_KEY = 'shu_auth'

function load() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY)
        return raw ? JSON.parse(raw) : null
    } catch {
        return null
    }
}

const saved = load()

export const auth = reactive({
    token: saved?.token || '',
    user: saved?.user || null, // { user_id, username, real_name, role }
})

export function setAuth(token, user) {
    auth.token = token
    auth.user = user
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ token, user }))
}

export function clearAuth() {
    auth.token = ''
    auth.user = null
    localStorage.removeItem(STORAGE_KEY)
}

export function isLoggedIn() {
    return !!auth.token
}

export function currentRole() {
    return auth.user?.role || ''
}

// 角色 -> 首页路由
export const roleHome = {
    student: '/student/courses',
    teacher: '/teacher/offerings',
    admin: '/admin/dashboard',
}

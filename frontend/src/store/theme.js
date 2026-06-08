import { ref } from 'vue'

// 主题（白天/黑夜）：切换 <html> 上的 dark 类并持久化到 localStorage，
// 首次进入时跟随系统偏好。
const STORAGE_KEY = 'shu_theme'

export const isDark = ref(false)

function apply(dark) {
    isDark.value = dark
    document.documentElement.classList.toggle('dark', dark)
}

export function initTheme() {
    const saved = localStorage.getItem(STORAGE_KEY)
    const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches
    apply(saved ? saved === 'dark' : !!prefersDark)
}

export function toggleTheme() {
    const next = !isDark.value
    apply(next)
    localStorage.setItem(STORAGE_KEY, next ? 'dark' : 'light')
}

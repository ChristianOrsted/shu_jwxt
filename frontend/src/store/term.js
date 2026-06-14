import { reactive } from 'vue'
import { authApi } from '@/api/services'

// 当前学年学期（全局共享）：由管理员在「学年学期」中设置，各角色页面据此展示，
// 切换当前学期后各页面重新加载即可联动，无需在每个页面写死学期名。
export const term = reactive({ current: null })

export async function loadCurrentTerm() {
    try {
        term.current = await authApi.currentTerm()
    } catch {
        term.current = null
    }
    return term.current
}

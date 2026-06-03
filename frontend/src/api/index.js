import axios from 'axios'
import { ElMessage } from 'element-plus'
import { auth, clearAuth } from '@/store/auth'
import router from '@/router'

// 统一 Axios 实例，baseURL 与 vite 代理约定一致
const http = axios.create({
    baseURL: '/api',
    timeout: 15000,
})

// 请求拦截器：自动附加 JWT Token
http.interceptors.request.use((config) => {
    if (auth.token) {
        config.headers.Authorization = `Bearer ${auth.token}`
    }
    return config
})

// 响应拦截器：统一处理后端 { code, message, data } 格式
http.interceptors.response.use(
    (response) => {
        const res = response.data
        // 后端约定格式
        if (res && typeof res.code !== 'undefined') {
            if (res.code === 200) return res.data
            if (res.code === 401) {
                clearAuth()
                router.replace('/login')
                ElMessage.error('登录已过期，请重新登录')
                return Promise.reject(new Error(res.message || '未登录'))
            }
            ElMessage.error(res.message || '请求失败')
            return Promise.reject(new Error(res.message || '请求失败'))
        }
        return res
    },
    (error) => {
        const status = error.response?.status
        if (status === 401) {
            clearAuth()
            router.replace('/login')
            ElMessage.error('登录已过期，请重新登录')
        } else {
            ElMessage.error(error.response?.data?.message || error.message || '网络错误')
        }
        return Promise.reject(error)
    },
)

export default http

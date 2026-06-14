<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api/services'
import { setAuth, roleHome } from '@/store/auth'
import { isDark } from '@/store/theme'
import { demoAccounts } from '@/api/mock'

const router = useRouter()
const route = useRoute()
const formRef = ref()
const loading = ref(false)

const form = reactive({
    role: 'student',
    username: 'S2023001',
    password: '123456',
})

const rules = {
    username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
    password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

// 登录页是「蓝底 + 白卡片」的亮色设计，不随应用的夜间模式走：
// 进入时临时移除 <html> 的 dark 类，离开时按用户真实偏好还原
// （不写 localStorage，登录后应用仍保持用户选择的主题）。
onMounted(() => {
    document.documentElement.classList.remove('dark')
})
onUnmounted(() => {
    if (isDark.value) document.documentElement.classList.add('dark')
})

// 选择角色时自动填入对应演示账号，便于答辩演示
function onRoleChange(role) {
    const acc = demoAccounts.find((a) => a.role === role)
    if (acc) {
        form.username = acc.username
        form.password = acc.password
    }
}

async function onSubmit() {
    await formRef.value.validate(async (valid) => {
        if (!valid) return
        loading.value = true
        try {
            const { token, user } = await authApi.login(form.username, form.password, form.role)
            setAuth(token, user)
            ElMessage.success('登录成功')
            const redirect = route.query.redirect
            router.replace(redirect || roleHome[user.role] || '/login')
        } catch (e) {
            ElMessage.error(e.message || '登录失败')
        } finally {
            loading.value = false
        }
    })
}
</script>

<template>
    <div class="login-page">
        <div class="login-card">
            <div class="brand">
                <el-icon class="brand-icon"><Reading /></el-icon>
                <h1>学分制教务选课管理系统</h1>
                <p>Credit-based Course Selection & Academic Affairs</p>
            </div>

            <el-form ref="formRef" :model="form" :rules="rules" size="large" @submit.prevent>
                <el-form-item>
                    <el-radio-group v-model="form.role" @change="onRoleChange" class="role-group">
                        <el-radio-button value="student">学生</el-radio-button>
                        <el-radio-button value="teacher">教师</el-radio-button>
                        <el-radio-button value="admin">管理员</el-radio-button>
                    </el-radio-group>
                </el-form-item>

                <el-form-item prop="username">
                    <el-input v-model="form.username" placeholder="用户名 / 学号 / 工号" :prefix-icon="'User'" />
                </el-form-item>

                <el-form-item prop="password">
                    <el-input
                        v-model="form.password"
                        type="password"
                        placeholder="密码"
                        :prefix-icon="'Lock'"
                        show-password
                        @keyup.enter="onSubmit"
                    />
                </el-form-item>

                <el-form-item>
                    <el-button type="primary" class="login-btn" :loading="loading" @click="onSubmit">
                        登录
                    </el-button>
                </el-form-item>
            </el-form>

            <el-alert type="info" :closable="false" class="demo-tip">
                <template #title>
                    演示账号（密码均为 123456）：学生 S2023001 / 教师 T1001 / 管理员 admin
                </template>
            </el-alert>
        </div>
        <div class="footer">SHU 数据库课程设计 · B/S 结构教学事务管理系统</div>
    </div>
</template>

<style scoped>
.login-page {
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #1d39c4 0%, #2f54eb 50%, #597ef7 100%);
}
.login-card {
    width: 400px;
    background: #fff;
    border-radius: 14px;
    padding: 36px 32px 28px;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.18);
}
.brand {
    text-align: center;
    margin-bottom: 24px;
}
.brand-icon {
    font-size: 40px;
    color: var(--shu-primary);
}
.brand h1 {
    font-size: 20px;
    margin: 10px 0 4px;
}
.brand p {
    color: #b0b3b8;
    font-size: 12px;
    margin: 0;
}
.role-group {
    width: 100%;
    display: flex;
}
.role-group :deep(.el-radio-button) {
    flex: 1;
}
.role-group :deep(.el-radio-button__inner) {
    width: 100%;
}
.login-btn {
    width: 100%;
}
.demo-tip {
    margin-top: 4px;
}
.footer {
    margin-top: 22px;
    color: rgba(255, 255, 255, 0.85);
    font-size: 13px;
}
</style>

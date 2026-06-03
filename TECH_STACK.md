# 学分制教务管理系统 — 技术栈说明

> 项目路径：`~/Playground/SHU/`
> 最后更新：2026-06-03

---

## 一、项目结构

```
~/Playground/SHU/
├── backend/                # Flask 后端
│   ├── .venv/              # Python 虚拟环境
│   ├── app/
│   │   ├── __init__.py     # Flask 应用工厂
│   │   ├── db.py           # 数据库连接
│   │   ├── auth.py         # 登录 / JWT 鉴权
│   │   └── routes/
│   │       ├── student.py  # 学生端 API
│   │       ├── teacher.py  # 教师端 API
│   │       └── admin.py    # 管理员端 API
│   ├── run.py              # 启动入口
│   ├── .env                # 环境变量（数据库密码等，不提交 git）
│   └── requirements.txt    # Python 依赖清单
└── frontend/               # Vue 3 前端
    ├── src/
    │   ├── main.js         # 入口
    │   ├── App.vue
    │   ├── router/
    │   │   └── index.js    # 路由定义
    │   ├── views/
    │   │   ├── Login.vue
    │   │   ├── student/    # 学生页面
    │   │   ├── teacher/    # 教师页面
    │   │   └── admin/      # 管理员页面
    │   ├── components/     # 公共组件
    │   └── api/
    │       └── index.js    # Axios 请求封装
    ├── package.json
    └── vite.config.js
```

---

## 二、技术栈总览

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 前端框架 | Vue 3 | 3.x | 响应式 UI |
| 前端构建 | Vite | 6.x | 开发服务器 + 打包 |
| UI 组件库 | Element Plus | 2.x | 表格、表单、对话框等组件 |
| 前端路由 | Vue Router | 4.x | 多角色页面路由 |
| HTTP 请求 | Axios | 1.x | 前后端通信 |
| 后端框架 | Flask | 3.x | RESTful API |
| 登录管理 | Flask-Login | 0.6.x | Session 管理 |
| 跨域处理 | Flask-CORS | 6.x | 允许前端跨域请求 |
| 身份认证 | PyJWT | 2.x | 生成 / 验证 JWT Token |
| 数据库驱动 | PyMySQL | 1.x | Python 连接 MySQL |
| 环境配置 | python-dotenv | 1.x | 读取 `.env` 配置文件 |
| 数据库 | MySQL | 8.x | 主数据库 |
| 运行环境 | Python | 3.14 | 后端运行时 |
| 包管理 | npm | - | 前端包管理 |
| 虚拟环境 | venv (.venv) | - | Python 环境隔离 |

---

## 三、后端说明

### 虚拟环境

```bash
# 激活
cd ~/Playground/SHU
source backend/.venv/bin/activate

# 退出
deactivate
```

### 安装依赖

```bash
pip install flask flask-cors flask-login PyJWT pymysql python-dotenv
```

### 启动后端

```bash
cd ~/Playground/SHU/backend
source .venv/bin/activate
python run.py
# 默认监听 http://localhost:5000
```

### 环境变量配置（`.env`）

```ini
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的密码
DB_NAME=school
SECRET_KEY=随机字符串用于JWT签名
```

### API 设计约定

- 所有接口以 `/api` 为前缀，例如 `/api/student/courses`
- 请求和响应均为 JSON 格式
- 需要登录的接口在请求头携带 Token：`Authorization: Bearer <token>`
- 统一响应格式：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

### 角色鉴权逻辑

登录后由后端签发 JWT，Payload 中包含 `user_id` 和 `role`（`student` / `teacher` / `admin`），每个路由通过装饰器校验角色：

```python
@student_bp.route('/courses', methods=['GET'])
@login_required
@role_required('student')
def get_courses():
    ...
```

---

## 四、前端说明

### 启动前端开发服务器

```bash
cd ~/Playground/SHU/frontend
npm run dev
# 默认监听 http://localhost:5173
```

### 路由结构

| 路径 | 组件 | 说明 |
|------|------|------|
| `/login` | `Login.vue` | 统一登录页，按角色跳转 |
| `/student/*` | `views/student/` | 学生端页面 |
| `/teacher/*` | `views/teacher/` | 教师端页面 |
| `/admin/*` | `views/admin/` | 管理员端页面 |

路由守卫：未登录访问受保护路由时自动跳转到 `/login`。

### Axios 封装约定

在 `src/api/index.js` 中统一配置：

- `baseURL` 设为 `http://localhost:5000/api`
- 请求拦截器自动在 Header 中附加 JWT Token
- 响应拦截器统一处理 401（未登录跳回登录页）

### Element Plus 引入方式

推荐按需引入，在 `main.js` 中：

```js
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
app.mount('#app')
```

---

## 五、数据库说明

### 数据库名

```
school
```

在 School 原始数据库基础上扩展，保留原有的 `student`、`teacher`、`course`、`class`、`course selection` 五张表，新增约 18 张业务表。

### 关键数据库对象

| 对象 | 名称 | 说明 |
|------|------|------|
| 存储过程 | `sp_StudentSelectCourse` | 学生选课，含容量/冲突/重修等全套校验 |
| 存储过程 | `sp_StudentDropCourse` | 学生退课并释放容量 |
| 存储过程 | `sp_TeacherSubmitGrade` | 教师提交成绩 |
| 触发器 | `trg_UpdateOfferingSelectedCount` | 选课/退课后自动同步课程当前人数 |

### 常用 MySQL 操作

```bash
# 登录
mysql -u root -p

# 查看所有数据库
SHOW DATABASES;

# 使用 school 数据库
USE school;

# 查看所有表
SHOW TABLES;
```

---

## 六、开发流程

1. 激活虚拟环境：`source backend/.venv/bin/activate`
2. 启动 MySQL：`sudo systemctl start mysql`
3. 启动后端：`cd backend && python run.py`
4. 启动前端：`cd frontend && npm run dev`
5. 浏览器访问：`http://localhost:5173`

前端 `vite.config.js` 中配置代理，将 `/api` 请求转发到 `http://localhost:5000`，开发时无需处理跨域：

```js
export default {
  server: {
    proxy: {
      '/api': 'http://localhost:5000'
    }
  }
}
```

---

## 七、三类角色功能速查

### 学生端

- 查看 / 搜索可选课程，查看容量（如 `10/40`）
- 在线选课 / 退课
- 查看个人课表、已选课程
- 查看成绩、平均绩点、挂科重修状态

### 教师端

- 查看授课任务、选课学生名单
- 录入 / 提交成绩，查看成绩统计
- 提交开课 / 扩容 / 调课 / 停课申请
- 查看审批进度

### 管理员端

- 用户 / 角色 / 权限管理
- 学年学期 / 课程库 / 教室管理
- 审批教师申请
- 发布成绩、管理重修
- 统计报表导出、操作日志查看

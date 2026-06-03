# 学分制教务选课管理系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.3-green.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 基于 Flask + Vue 3 + MySQL 的现代化教务选课管理系统，支持学生选课、教师成绩管理、管理员系统管理等完整功能。

## 📸 项目预览

- **学生端**：选课中心、已选课程、个人课表、成绩查询、挂科重修
- **教师端**：授课任务、学生名单、成绩录入、成绩统计、教学申请
- **管理员端**：用户管理、开课管理、成绩发布、统计分析、审批管理

## ✨ 核心特性

- 🔐 **JWT 认证**：基于 Token 的安全认证机制
- 👥 **三角色权限**：学生、教师、管理员完全隔离
- 📊 **实时统计**：课程容量、成绩分布、重修情况一目了然
- 🔔 **消息通知**：选课成功、成绩发布等自动推送
- 📝 **存储过程**：选课、退课、成绩提交业务逻辑封装
- ⚡ **触发器**：选课人数自动同步更新
- 🎯 **完整校验**：时间冲突、容量限制、重修资格全面检测
- 📱 **响应式设计**：前端基于 Element Plus 组件库

## 🏗️ 技术架构

### 后端技术栈
- **框架**：Flask 3.1.3
- **数据库**：MySQL 8.0+
- **数据库驱动**：PyMySQL 1.2.0
- **认证**：JWT (PyJWT 2.13.0)
- **跨域**：Flask-CORS 6.0.2
- **密码加密**：Werkzeug 3.1.8

### 前端技术栈
- **框架**：Vue 3
- **UI 组件库**：Element Plus
- **构建工具**：Vite
- **HTTP 客户端**：Axios

## 📁 项目结构

```
shu_jwxt/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── __init__.py     # Flask 应用工厂
│   │   ├── db.py           # 数据库连接
│   │   ├── auth.py         # JWT 认证
│   │   ├── utils.py        # 工具函数
│   │   └── routes/         # 路由模块
│   │       ├── auth_routes.py
│   │       ├── student_routes.py
│   │       ├── teacher_routes.py
│   │       └── admin_routes.py
│   ├── sql/
│   │   ├── 01_schema.sql    # 建表脚本
│   │   ├── 02_routines.sql  # 存储过程和触发器
│   │   └��─ 03_seed.sql      # 测试数据
│   ├── run.py               # 应用入口
│   ├── init_db.py           # 数据库初始化
│   ├── test_api.py          # API 测试脚本
│   └── requirements.txt     # Python 依赖
│
├── frontend/                # 前端应用
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── api/            # API 接口
│   │   ├── router/         # 路由配置
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
│
└── docs/                    # 项目文档
    ├── API.md              # 接口文档
    ├── DB_DESIGN.md        # 数据库设计
    ├── BACKEND_TASKS.md    # 后端开发指南
    └── TECH_STACK.md       # 技术栈说明
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- MySQL 8.0+
- Node.js 16+

### 后端部署

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/shu_jwxt.git
cd shu_jwxt/backend

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置数据库连接信息

# 4. 初始化数据库
python init_db.py

# 5. 启动服务
python run.py
```

服务将运行在 `http://localhost:5000`

### 前端部署

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将运行在 `http://localhost:5173`

### 一键部署（推荐）

**Windows：**
```bash
cd backend
deploy.bat
```

**Linux/Mac：**
```bash
cd backend
chmod +x deploy.sh
./deploy.sh
```

## 🧪 测试

### 自动化测试

```bash
cd backend
python test_api.py
```

### 手动测试

```bash
# 健康检查
curl http://localhost:5000/health

# 学生登录
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"S2023001","password":"123456","role":"student"}'
```

### 演示账号

| 角色 | 用户名 | 密码 | 姓名 |
|------|--------|------|------|
| 学生 | S2023001 | 123456 | 张小明 |
| 教师 | T1001 | 123456 | 李教授 |
| 管理员 | admin | 123456 | 系统管理员 |

## 📖 API 文档

完整的 API 文档请查看 [API.md](API.md)

### 核心接口

- `POST /api/auth/login` - 用户登录
- `GET /api/student/courses` - 获取可选课程
- `POST /api/student/enroll` - 选课
- `GET /api/teacher/offerings` - 获取授课任务
- `POST /api/teacher/grade/submit` - 提交成绩
- `GET /api/admin/statistics` - 获取统计数据

所有接口统一返回格式：
```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

## 🗄️ 数据库设计

### 核心表结构

- **Users** - 用户表（登录账号）
- **Students** - 学生信息表
- **Teachers** - 教师信息表
- **Courses** - 课程库
- **CourseOfferings** - 开课班表
- **Enrollments** - 选课记录表
- **Grades** - 成绩表
- **RetakeRecords** - 重修记录表

详细设计请查看 [DB_DESIGN.md](DB_DESIGN.md)

### 存储过程

- `sp_StudentSelectCourse` - 学生选课（含全套校验）
- `sp_StudentDropCourse` - 学生退课
- `sp_TeacherSubmitGrade` - 教师提交成绩
- `sp_CreateRetakeRecords` - 生成重修记录

### 触发器

- `trg_UpdateOfferingSelectedCount` - 自动更新选课人数缓存

## 🔧 配置说明

### 后端配置 (.env)

```ini
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=christian
DB_PASSWORD=123456
DB_NAME=school
SECRET_KEY=your-secret-key-change-in-production
JWT_EXPIRATION_HOURS=24
```

### 前端配置

编辑 `frontend/src/api/services.js`：
```javascript
export const USE_MOCK = false  // false 使用真实后端，true 使用 Mock 数据
```

## 📝 开发指南

### 添加新接口

1. 在 `backend/app/routes/` 下对应文件添加路由
2. 使用 `@role_required` 装饰器进行权限控制
3. 使用 `success_response` / `error_response` 返回统一格式
4. 在 `API.md` 中补充接口文档

### 添加新表

1. 在 `backend/sql/01_schema.sql` 添加建表语句
2. 在 `backend/sql/03_seed.sql` 添加测试数据
3. 在 `DB_DESIGN.md` 中补充设计说明

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - ���见 [LICENSE](LICENSE) 文件

## 👨‍💻 作者

- **项目作者** - [YOUR_NAME](https://github.com/YOUR_USERNAME)

## 🙏 致谢

- Flask 框架
- Element Plus UI 组件库
- Vue.js 团队
- 所有贡献者

## 📮 联系方式

- 项目主页：https://github.com/YOUR_USERNAME/shu_jwxt
- 问题反馈：https://github.com/YOUR_USERNAME/shu_jwxt/issues
- 邮箱：your.email@example.com

---

⭐ 如果这个项目对你有帮助，请给个 Star！

# 学分制教务选课管理系统

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.3-green.svg)](https://flask.palletsprojects.com/)
[![Vue](https://img.shields.io/badge/Vue-3.5-42b883.svg)](https://vuejs.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

基于 Flask + Vue 3 + MySQL 的教务选课管理系统，覆盖学生选课、教师成绩管理、管理员系统管理等完整业务流程。

## 功能概览

- **学生端**：选课中心、已选课程、个人课表、成绩查询、挂科重修
- **教师端**：授课任务、学生名单、成绩录入、成绩统计、教学申请
- **管理员端**：用户管理、学年学期管理（新建 / 删除学年）、开课管理、成绩发布、统计分析、申请审批

## 核心特性

- **JWT 认证**：基于 Token 的登录与接口鉴权
- **三角色权限**：学生、教师、管理员权限隔离，由装饰器统一校验
- **业务逻辑下沉**：选课、退课、成绩提交、生成重修记录均由存储过程封装
- **数据一致性**：触发器自动同步开课班的选课人数缓存
- **完整校验**：时间冲突、容量上限、重修资格等在选课时全面检测
- **统一响应**：所有接口返回 `{ code, message, data }` 结构
- **前端组件化**：Vue 3 + Element Plus，支持日间/夜间主题切换

## 技术栈

### 后端

- 框架：Flask 3.1.3
- 数据库：MySQL 8.0+
- 驱动：PyMySQL 1.2.0
- 认证：PyJWT 2.13.0
- 跨域：Flask-CORS 6.0.2
- 密码哈希：Werkzeug 3.1.8

### 前端

- 框架：Vue 3.5
- UI 组件库：Element Plus 2.14
- 构建工具：Vite 8
- HTTP 客户端：Axios 1.17
- 路由：Vue Router 5

## 项目结构

```
shu_jwxt/
├── backend/                          # 后端服务（Flask）
│   ├── app/
│   │   ├── __init__.py               # 应用工厂、/health 健康检查
│   │   ├── db.py                     # 数据库连接（上下文管理器）
│   │   ├── auth.py                   # JWT 认证与角色校验
│   │   ├── utils.py                  # 统一响应等工具
│   │   └── routes/                   # 按角色拆分的路由
│   │       ├── auth_routes.py
│   │       ├── common_routes.py
│   │       ├── student_routes.py
│   │       ├── teacher_routes.py
│   │       └── admin_routes.py
│   ├── sql/
│   │   ├── 01_schema.sql             # 建表脚本
│   │   ├── 02_routines.sql           # 存储过程与触发器
│   │   └── 03_seed.sql               # 测试数据
│   ├── run.py                        # 启动入口（:5000）
│   ├── init_db.py                    # 一键建库并写入测试数据
│   ├── migrate_teaching_requests.py  # 教学申请字段迁移脚本
│   ├── test_api.py                   # 接口自测脚本
│   └── requirements.txt
│
├── frontend/                         # 前端应用（Vue 3 + Vite）
│   ├── src/
│   │   ├── views/                    # 页面（admin / teacher / student）
│   │   ├── layouts/                  # 布局
│   │   ├── api/                      # 接口封装（index / services / mock）
│   │   ├── router/                   # 路由配置
│   │   ├── store/                    # 状态（auth / theme）
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
│
├── API.md                            # 接口文档
├── DB_DESIGN.md                      # 数据库设计
├── BACKEND_TASKS.md                  # 后端开发指南
├── TECH_STACK.md                     # 技术栈说明
└── TEAM_DEVISION.md                  # 团队分工
```

## 快速开始

### 环境要求

- Python 3.9+
- MySQL 8.0+
- Node.js 20.19+ 或 22.12+

### 后端部署

```bash
# 1. 克隆仓库
git clone https://github.com/ChristianOrsted/shu_jwxt.git
cd shu_jwxt/backend

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，填入本地数据库连接信息

# 4. 初始化数据库（建表 + 存储过程 + 测试数据）
python init_db.py

# 5. 启动服务
python run.py
```

服务运行在 `http://localhost:5000`。

> 说明：`init_db.py` 会重建全部表。若数据库已有数据、只想为「教学申请」补充新增字段而不清库，请运行 `python migrate_teaching_requests.py`（可重复执行）。

### 前端部署

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端运行在 `http://localhost:5173`，开发环境通过 Vite 代理将 `/api` 转发到后端 `:5000`。

### 一键部署脚本

Windows：

```bash
cd backend
deploy.bat
```

Linux / macOS：

```bash
cd backend
chmod +x deploy.sh
./deploy.sh
```

## 测试

### 自动化测试

```bash
cd backend
python test_api.py
```

### 手动验证

```bash
# 健康检查
curl http://localhost:5000/health

# 学生登录
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"S2023001","password":"123456","role":"student"}'
```

### 演示账号

| 角色   | 用户名   | 密码   | 姓名       |
| ------ | -------- | ------ | ---------- |
| 学生   | S2023001 | 123456 | 张小明     |
| 教师   | T1001    | 123456 | 李教授     |
| 管理员 | admin    | 123456 | 系统管理员 |

## API 文档

完整接口说明见 [API.md](API.md)。

常用接口：

- `POST /api/auth/login` — 用户登录
- `GET /api/common/terms` — 学期列表
- `GET /api/student/courses` — 可选课程
- `POST /api/student/enroll` — 选课
- `GET /api/teacher/offerings` — 授课任务
- `POST /api/teacher/grade/submit` — 提交成绩
- `GET /api/admin/statistics` — 统计数据
- `GET /api/admin/terms` — 学年学期列表
- `POST /api/admin/academic-years` — 新建学年（自动生成两个学期）
- `DELETE /api/admin/academic-years/:id` — 删除学年（未开始且无开课记录时）

统一响应格式：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

## 数据库设计

核心表：

- **Users** — 登录账号
- **Students** — 学生信息
- **Teachers** — 教师信息
- **Courses** — 课程库
- **CourseOfferings** — 开课班
- **Enrollments** — 选课记录
- **Grades** — 成绩
- **RetakeRecords** — 重修记录

详细设计见 [DB_DESIGN.md](DB_DESIGN.md)。

### 存储过程

- `sp_StudentSelectCourse` — 学生选课（含全套校验）
- `sp_StudentDropCourse` — 学生退课
- `sp_TeacherSubmitGrade` — 教师提交成绩
- `sp_CreateRetakeRecords` — 生成重修记录

### 触发器

- `trg_UpdateOfferingSelectedCount` — 自动更新选课人数缓存

## 配置说明

### 后端（.env）

```ini
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=christian
DB_PASSWORD=123456
DB_NAME=school
SECRET_KEY=your-secret-key-change-in-production
JWT_EXPIRATION_HOURS=24
```

### 前端

在 `frontend/src/api/services.js` 中切换数据源：

```javascript
export const USE_MOCK = false // false 走真实后端，true 使用 Mock 数据
```

## 开发指南

### 新增接口

1. 在 `backend/app/routes/` 对应文件中添加路由
2. 用 `@role_required` 或 `@login_required` 装饰器做权限控制
3. 用 `success_response` / `error_response` 返回统一格式
4. 在 [API.md](API.md) 中补充文档

### 新增数据表

1. 在 `backend/sql/01_schema.sql` 添加建表语句
2. 在 `backend/sql/03_seed.sql` 补充测试数据
3. 在 [DB_DESIGN.md](DB_DESIGN.md) 更新设计说明
4. 如需在已有数据库上变更，另写幂等迁移脚本（参考 `migrate_teaching_requests.py`）

## 贡献

欢迎提交 Issue 与 Pull Request：

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m '描述本次改动'`
4. 推送分支：`git push origin feature/your-feature`
5. 发起 Pull Request

## 维护者

- [ChristianOrsted](https://github.com/ChristianOrsted)
- fargrafunk
- alex

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE)。

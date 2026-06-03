# 后端系统部署和测试指南

## 📋 目录

1. [环境要求](#环境要求)
2. [快速开始](#快速开始)
3. [详细部署步骤](#详细部署步骤)
4. [测试指南](#测试指南)
5. [常见问题](#常见问题)
6. [API 接口文档](#api-接口文档)

---

## 环境要求

### 必需软件
- **Python**: 3.8 或更高版本
- **MySQL**: 8.0 或更高版本
- **pip**: Python 包管理工具

### Python 依赖包
所有依赖已列在 `requirements.txt` 中：
```
Flask==3.1.3
flask-cors==6.0.2
PyJWT==2.13.0
PyMySQL==1.2.0
python-dotenv==1.2.2
Werkzeug==3.1.8
```

---

## 快速开始

### 一键部署（推荐）

```bash
# 1. 进入 backend 目录
cd backend

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置数据库连接信息

# 4. 初始化数据库
python init_db.py

# 5. 启动服务
python run.py

# 6. 测试接口（新开一个终端）
python test_api.py
```

---

## 详细部署步骤

### 步骤 1: 安装 Python 依赖

```bash
cd backend
pip install -r requirements.txt
```

**验证安装：**
```bash
python -c "import flask; print('Flask:', flask.__version__)"
python -c "import pymysql; print('PyMySQL:', pymysql.__version__)"
python -c "import jwt; print('PyJWT installed')"
```

### 步骤 2: 配置环境变量

创建 `.env` 文件（从模板复制）：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置数据库连接：

```ini
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=christian
DB_PASSWORD=123456
DB_NAME=school
SECRET_KEY=your-secret-key-change-this-in-production
JWT_EXPIRATION_HOURS=24
```

**重要：** 确保 MySQL 数据库已启动，且用户 `christian` 有权限创建数据库和表。

### 步骤 3: 初始化数据库

运行初始化脚本：

```bash
python init_db.py
```

该脚本会：
1. 创建 `school` 数据库
2. 创建所有数据表（9 大模块，15+ 张表）
3. 创建触发器和存储过程
4. 插入测试数据（3 个演示账号、课程、开课班等）
5. 生成真实的密码哈希（基于 werkzeug）

**预期输出：**
```
============================================================
开始初始化数据库...
============================================================

生成的密码哈希（用于 123456）:
scrypt:32768:8:1$...

✓ 成功连接到 MySQL

1. 执行建表脚本 (01_schema.sql)...
   ✓ 建表完成

2. 执行存储过程和触发器脚本 (02_routines.sql)...
   ✓ 存储过程和触发器创建完成

3. 执行测试数据脚本 (03_seed.sql)...
   ✓ 测试数据插入完成

4. 验证数据插入...
   用户数量: 6
   学生数量: 3
   教师数量: 2
   课程数量: 5
   当前学期开课数: 5

============================================================
✓ 数据库初始化成功！
============================================================

演示账号：
  管理员: admin / 123456
  教师:   T1001 / 123456
  学生:   S2023001 / 123456
```

**手动初始化（可选）：**

如果 `init_db.py` 脚本失败，可以手动执行 SQL 文件：

```bash
# 方法 1: 使用 MySQL 命令行
mysql -u christian -p123456 < sql/01_schema.sql
mysql -u christian -p123456 < sql/02_routines.sql
mysql -u christian -p123456 < sql/03_seed.sql

# 方法 2: 使用 MySQL Workbench
# 打开 SQL 文件并执行
```

**注意：** 手动执行 `03_seed.sql` 前，需要先用 Python 生成真实的密码哈希：

```bash
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('123456'))"
```

然后将输出的哈希值替换 `03_seed.sql` 中的占位符。

### 步骤 4: 启动后端服务

```bash
python run.py
```

**预期输出：**
```
============================================================
学分制教务选课管理系统 - 后端服务
服务地址: http://localhost:5000
API 前缀: /api
============================================================
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
```

**服务启动成功标志：**
- 看到 `Running on http://127.0.0.1:5000`
- 没有错误信息
- 可以在浏览器访问 `http://localhost:5000/health`

---

## 测试指南

### 自动化测试脚本

我们提供了完整的自动化测试脚本 `test_api.py`，涵盖三种角色的核心功能。

**运行测试：**

```bash
# 确保后端服务已启动（在另一个终端）
python test_api.py
```

**测试覆盖：**

1. ✓ 健康检查 (`/health`)
2. ✓ 学生登录 (`POST /api/auth/login`)
3. ✓ 获取可选课程列表 (`GET /api/student/courses`)
4. ✓ 获取已选课程 (`GET /api/student/my-courses`)
5. ✓ 测试选课 (`POST /api/student/enroll`)
6. ✓ 教师登录
7. ✓ 获取授课任务 (`GET /api/teacher/offerings`)
8. ✓ 管理员登录
9. ✓ 获取统计数据 (`GET /api/admin/statistics`)

**预期输出示例：**

```
============================================================
后端 API 接口测试
============================================================

============================================================
1. 健康检查
============================================================
状态码: 200
响应: {'status': 'ok'}

============================================================
2. 学生登录测试
============================================================
状态码: 200
响应: {
  "code": 200,
  "message": "success",
  "data": {
    "token": "eyJhbGci...",
    "user": {
      "user_id": 4,
      "username": "S2023001",
      "real_name": "张小明",
      "role": "student"
    }
  }
}
✓ 学生登录成功

============================================================
3. 获取可选课程列表
============================================================
状态码: 200
返回课程数量: 5

第一门课程详情:
{
  "offering_id": 101,
  "course_code": "CS201",
  "course_name": "数据库原理",
  ...
}
```

### 手动测试（使用 curl）

#### 1. 健康检查

```bash
curl http://localhost:5000/health
```

**预期响应：**
```json
{"status": "ok"}
```

#### 2. 学生登录

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "S2023001",
    "password": "123456",
    "role": "student"
  }'
```

**预期响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "token": "eyJhbGciOi...",
    "user": {
      "user_id": 4,
      "username": "S2023001",
      "real_name": "张小明",
      "role": "student"
    }
  }
}
```

**保存 Token：**
```bash
TOKEN="复制上面返回的 token 值"
```

#### 3. 获取可选课程（需要 Token）

```bash
curl http://localhost:5000/api/student/courses \
  -H "Authorization: Bearer $TOKEN"
```

#### 4. 选课

```bash
curl -X POST http://localhost:5000/api/student/enroll \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "offering_id": 104
  }'
```

**成功响应：**
```json
{
  "code": 200,
  "message": "选课成功",
  "data": null
}
```

**失败响应（课程已满）：**
```json
{
  "code": 400,
  "message": "课程已满",
  "data": null
}
```

#### 5. 教师登录

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "T1001",
    "password": "123456",
    "role": "teacher"
  }'
```

#### 6. 管理员登录

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "123456",
    "role": "admin"
  }'
```

### 使用 Postman 测试

1. **导入环境变量：**
   - Base URL: `http://localhost:5000`
   - Token: `{{token}}`（从登录接口获取）

2. **创建请求集合：**
   - 认证 → 登录
   - 学生端 → 可选课程、选课、退课、课表、成绩
   - 教师端 → 授课任务、成绩录入、成绩提交
   - 管理员端 → 统计、用户管理、成绩发布

3. **设置 Token：**
   - 在 Authorization 标签页选择 "Bearer Token"
   - 输入登录后获取的 token

---

## 常见问题

### Q1: `python` 命令不可用

**解决方法：**
```bash
# Windows 用户可能需要使用 py 或 python3
py run.py
# 或
python3 run.py
```

### Q2: `pip install` 失败

**解决方法：**
```bash
# 使用清华镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用阿里云镜像
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### Q3: MySQL 连接失败

**错误信息：**
```
pymysql.err.OperationalError: (2003, "Can't connect to MySQL server...")
```

**解决方法：**
1. 检查 MySQL 服务是否启动
2. 确认 `.env` 文件中的连接信息正确
3. 测试 MySQL 连接：
```bash
mysql -u christian -p123456 -e "SELECT 1"
```

### Q4: 数据库初始化失败

**错误信息：**
```
Access denied for user 'christian'@'localhost'
```

**解决方法：**
```sql
-- 登录 MySQL 并创建用户
CREATE USER 'christian'@'localhost' IDENTIFIED BY '123456';
GRANT ALL PRIVILEGES ON *.* TO 'christian'@'localhost';
FLUSH PRIVILEGES;
```

### Q5: 端口 5000 被占用

**错误信息：**
```
OSError: [Errno 48] Address already in use
```

**解决方法：**
```bash
# 方法 1: 修改端口
# 编辑 run.py，将 port=5000 改为 port=5001

# 方法 2: 杀死占用端口的进程（Windows）
netstat -ano | findstr :5000
taskkill /PID <进程ID> /F

# 方法 2: 杀死占用端口的进程（Linux/Mac）
lsof -ti:5000 | xargs kill -9
```

### Q6: CORS 跨域错误

**错误信息（浏览器控制台）：**
```
Access to XMLHttpRequest at 'http://localhost:5000/api/...' 
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**解决方法：**
已在 `app/__init__.py` 中配置 CORS。如果仍有问题，检查：
1. 前端端口是否为 5173
2. 重启后端服务

### Q7: Token 失效

**错误响应：**
```json
{
  "code": 401,
  "message": "Token 已失效或无效"
}
```

**解决方法：**
1. 重新登录获取新 Token
2. 检查 Token 是否正确携带在请求头中
3. Token 默认有效期 24 小时（可在 `.env` 中调整）

---

## API 接口文档

详细的 API 文档请参考项目根目录的 `API.md` 文件。

### 核心接口速览

#### 认证接口
- `POST /api/auth/login` - 用户登录

#### 学生端接口
- `GET /api/student/profile` - 个人信息
- `GET /api/student/courses` - 可选课程列表
- `POST /api/student/enroll` - 选课
- `DELETE /api/student/enroll/{offering_id}` - 退课
- `GET /api/student/my-courses` - 已选课程
- `GET /api/student/timetable` - 个人课表
- `GET /api/student/grades` - 成绩查询
- `GET /api/student/average-score` - 平均成绩统计
- `GET /api/student/retake` - 挂科重修状态
- `GET /api/student/notifications` - 消息通知

#### 教师端接口
- `GET /api/teacher/profile` - 个人信息
- `GET /api/teacher/offerings` - 授课任务
- `GET /api/teacher/roster/{offering_id}` - 选课学生名单
- `GET /api/teacher/grade-sheet/{offering_id}` - 成绩录入表
- `POST /api/teacher/grade` - 保存成绩（草稿）
- `POST /api/teacher/grade/submit` - 提交成绩
- `GET /api/teacher/requests` - 教学申请列表
- `POST /api/teacher/requests` - 提交申请
- `GET /api/teacher/grade-stats` - 成绩统计

#### 管理员端接口
- `GET /api/admin/statistics` - 总览统计
- `GET /api/admin/users` - 用户列表
- `POST /api/admin/users` - 新增/编辑用户
- `GET /api/admin/terms` - 学年学期
- `GET /api/admin/business-windows` - 业务时间窗口
- `GET /api/admin/courses` - 课程库
- `GET /api/admin/classrooms` - 教室资源
- `GET /api/admin/offerings` - 开课管理
- `GET /api/admin/approvals` - 待审批列表
- `POST /api/admin/approve` - 审批操作
- `GET /api/admin/grade-publish` - 待发布成绩
- `POST /api/admin/grade/publish` - 发布成绩
- `GET /api/admin/retake` - 重修管理
- `GET /api/admin/audit-logs` - 操作日志

### 统一响应格式

所有接口返回格式统一：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

**状态码说明：**
- `200` - 成功
- `400` - 参数错误 / 业务校验失败
- `401` - 未登录 / Token 失效
- `403` - 无权限
- `500` - 服务器错误

---

## 演示账号

| 角色 | 用户名 | 密码 | 姓名 |
|------|--------|------|------|
| 学生 | S2023001 | 123456 | 张小明 |
| 教师 | T1001 | 123456 | 李教授 |
| 管理员 | admin | 123456 | 系统管理员 |

---

## 前后端联调

### 前端配置

编辑 `frontend/src/api/services.js`：

```javascript
// 切换为真实后端
export const USE_MOCK = false  // 改为 false
```

### Vite 代理配置

前端已配置代理（`vite.config.js`），自动将 `/api/*` 请求转发到后端：

```javascript
proxy: {
  '/api': {
    target: 'http://localhost:5000',
    changeOrigin: true
  }
}
```

### 联调步骤

1. **启动后端**（终端 1）：
   ```bash
   cd backend
   python run.py
   ```

2. **启动前端**（终端 2）：
   ```bash
   cd frontend
   npm run dev
   ```

3. **浏览器访问**：
   ```
   http://localhost:5173
   ```

4. **使用演示账号登录并测试功能**

---

## 技术栈

- **后端框架**: Flask 3.1.3
- **数据库**: MySQL 8.x
- **数据库驱动**: PyMySQL 1.2.0
- **认证**: JWT (PyJWT 2.13.0)
- **跨域**: Flask-CORS 6.0.2
- **密码加密**: Werkzeug 3.1.8

---

## 项目结构

```
backend/
├── app/
│   ├── __init__.py          # Flask 应用工厂
│   ├── db.py                # 数据库连接
│   ├── auth.py              # JWT 认证
│   ├── utils.py             # 工具函数
│   └── routes/              # 路由模块
│       ├── __init__.py
│       ├── auth_routes.py   # 认证路由
│       ├── common_routes.py # 公共路由
│       ├── student_routes.py # 学生路由
│       ├── teacher_routes.py # 教师路由
│       └── admin_routes.py   # 管理员路由
├── sql/
│   ├── 01_schema.sql        # 建表脚本
│   ├── 02_routines.sql      # 存储过程和触发器
│   └── 03_seed.sql          # 测试数据
├── .env.example             # 环境变量模板
├── .env                     # 环境变量（需创建）
├── requirements.txt         # Python 依赖
├── run.py                   # 应用入口
├── init_db.py               # 数据库初始化脚本
├── test_api.py              # API 测试脚本
└── README.md                # 本文档
```

---

## 支持

如有问题，请查阅：
1. 本文档的「常见问题」章节
2. 项目根目录的 `API.md` 和 `DB_DESIGN.md`
3. 代码注释

---

**祝你部署顺利！** 🎉

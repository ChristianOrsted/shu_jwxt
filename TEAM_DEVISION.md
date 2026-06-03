# 学分制教务管理系统 — 分工说明

> 项目路径：`~/Playground/SHU/`
> 验收时间：2026 年 6 月 18 日 20:00

---

## 一、总体分工

| | 同学 A | 同学 B |
|---|---|---|
| **负责层** | 后端 + 数据库 | 前端 |
| **目录** | `backend/` | `frontend/` |
| **技术** | Python Flask + MySQL | Vue 3 + Element Plus |
| **验收时主讲** | 数据库设计、存储过程、API | 页面功能、选课流程演示 |

两人目录完全隔离，正常情况下不会产生 Git 冲突。

---

## 二、同学 A 的任务清单（后端 + 数据库）

### 阶段一：数据库建库（优先完成，B 依赖此阶段产出接口文档）

- [ ] 在 MySQL 中创建 `School` 数据库，建立全部数据表
- [ ] 录入初始测试数据（至少 3 个学生、2 个教师、1 个管理员、5 门课、3 个开课班）
- [ ] 编写触发器 `trg_UpdateOfferingSelectedCount`（选课/退课后自动同步课程人数）
- [ ] 编写存储过程 `sp_StudentSelectCourse`（选课全套校验：容量、冲突、重修资格等）
- [ ] 编写存储过程 `sp_StudentDropCourse`（退课并释放容量）
- [ ] 编写存储过程 `sp_TeacherSubmitGrade`（教师提交成绩，自动判断是否通过）

### 阶段二：Flask API 开发

- [ ] 搭建 Flask 项目骨架（工厂模式、Blueprint 分模块）
- [ ] 配置 MySQL 连接池（`db.py`）
- [ ] 实现登录接口，签发 JWT Token，区分三种角色
- [ ] 实现角色鉴权装饰器 `@role_required`

**学生端 API**

- [ ] `GET /api/student/courses` — 查询当前学期可选课程列表（含容量显示）
- [ ] `POST /api/student/enroll` — 选课（调用存储过程）
- [ ] `DELETE /api/student/enroll/<offering_id>` — 退课
- [ ] `GET /api/student/my-courses` — 查看已选课程
- [ ] `GET /api/student/timetable` — 个人课表
- [ ] `GET /api/student/grades` — 查看成绩

**教师端 API**

- [ ] `GET /api/teacher/offerings` — 查看授课任务
- [ ] `GET /api/teacher/roster/<offering_id>` — 查看选课学生名单
- [ ] `POST /api/teacher/grade` — 录入成绩
- [ ] `POST /api/teacher/grade/submit` — 提交成绩

**管理员端 API**

- [ ] `GET/POST /api/admin/users` — 用户管理
- [ ] `GET/POST /api/admin/offerings` — 开课管理
- [ ] `POST /api/admin/grade/publish` — 发布成绩
- [ ] `GET /api/admin/statistics` — 统计数据

### 阶段三：联调配合

- [ ] 启动后端服务确保 `http://localhost:5000` 可访问
- [ ] 配合 B 处理接口返回格式问题
- [ ] 补充缺失接口

---

## 三、同学 B 的任务清单（前端）

### 阶段一：项目初始化（可与 A 的阶段一并行）

- [ ] 配置 `vite.config.js` 代理（`/api` → `http://localhost:5000`）
- [ ] 配置 `main.js`，引入 Element Plus 和 Vue Router
- [ ] 封装 `src/api/index.js`（Axios 实例、请求拦截器自动附加 Token、响应拦截器处理 401）
- [ ] 配置路由 `src/router/index.js`，含路由守卫（未登录跳转 `/login`）
- [ ] 编写统一登录页 `Login.vue`（用户名/密码/角色选择，登录后按角色跳转）

### 阶段二：页面开发（用 Mock 数据先跑通，不依赖后端）

**学生端页面**

- [ ] `student/CourseList.vue` — 可选课程列表，含搜索筛选、容量显示（`10/40`）、选课按钮
- [ ] `student/MyCourses.vue` — 已选课程列表，含退课按钮
- [ ] `student/Timetable.vue` — 个人课表（按星期/节次展示）
- [ ] `student/Grades.vue` — 成绩查询，显示各学期成绩、是否通过、绩点

**教师端页面**

- [ ] `teacher/Offerings.vue` — 授课任务列表
- [ ] `teacher/Roster.vue` — 选课学生名单
- [ ] `teacher/GradeInput.vue` — 成绩录入表格（平时/实验/期末/总评，支持批量录入）

**管理员端页面**

- [ ] `admin/UserManage.vue` — 用户管理（增删改查）
- [ ] `admin/OfferingManage.vue` — 开课管理
- [ ] `admin/GradePublish.vue` — 成绩发布
- [ ] `admin/Statistics.vue` — 统计图表（使用 Element Plus 的图表或简单表格）

### 阶段三：联调对接

- [ ] 将 Mock 数据替换为真实 Axios 请求
- [ ] 处理接口返回的错误提示（如选课失败原因：已满/时间冲突等，用 `ElMessage` 弹出）
- [ ] 调整页面细节

---

## 四、共同负责

| 任务 | 说明 |
|------|------|
| 接口文档 `API.md` | **第一天两人一起定好**，后续所有开发以此为准 |
| Git 仓库 | A 初始化并推送到 GitHub/Gitee，B clone 后各自在自己目录工作 |
| 测试数据 | A 负责数据库测试数据，B 负责 Mock 数据格式与 A 保持一致 |
| 最终联调 | 预留 1 天，前端替换 Mock、处理边界情况 |

---

## 五、关键约定

### 统一接口响应格式

后端所有接口均返回以下格式，前端按 `code` 判断：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

常用 code：`200` 成功，`400` 参数错误，`401` 未登录，`403` 无权限，`500` 服务器错误。

### JWT Token 传递方式

```
请求头：Authorization: Bearer <token>
```

前端 Axios 拦截器自动附加，后端装饰器统一校验。

### 选课失败返回格式

存储过程失败时，后端统一返回：

```json
{
  "code": 400,
  "message": "课程已满 / 时间冲突 / 已选过该课程",
  "data": null
}
```

前端用 `ElMessage.error(res.message)` 弹出提示。

### 日期 / 时间格式

统一使用 ISO 8601：`"2026-06-03T15:30:00"`，前端显示时自行格式化。

---

## 六、推进时间线（参考）

| 时间 | A（后端） | B（前端） |
|------|-----------|-----------|
| 第 1 天 上午 | 两人一起定接口文档 `API.md` | 同左 |
| 第 1 天 下午 | 建库、写存储过程和触发器 | 项目初始化、登录页、路由守卫 |
| 第 2 天 上午 | 写全部 API 接口 | 用 Mock 数据写完所有页面 |
| 第 2 天 中午 | 后端自测，启动服务 | 替换 Mock，开始联调 |
| 第 2 天 下午 | 配合修 Bug | 配合修 Bug |
| 验收前 | 准备主讲：数据库设计 + 存储过程演示 | 准备主讲：页面功能演示 |

---

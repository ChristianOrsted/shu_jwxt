# 教务选课管理系统 — 后端接口文档（API.md）

> 本文档由前端按实际调用整理，**前端代码已严格按此结构消费数据**。
> 后端（同学 A）只要让每个接口返回此处描述的 `data` 结构，前端把 `src/api/services.js`
> 顶部的 `USE_MOCK = true` 改为 `false` 即可无缝联调，页面代码无需改动。
>
> - 所有接口以 `/api` 为前缀（前端通过 Vite 代理转发到 `http://localhost:5000`）。
> - 字段命名全部用 snake_case，与数据库列名保持一致。
> - 所有示例数据可在前端 `src/api/mock.js` 中找到对应来源。

---

## 一、通用约定

### 1.1 统一响应格式

所有接口**必须**返回如下 JSON 信封，前端响应拦截器只取 `data` 返回给页面：

```json
{
    "code": 200,
    "message": "success",
    "data": {}
}
```

| code | 含义 | 前端行为 |
|------|------|----------|
| 200 | 成功 | 取 `data` 返回给页面 |
| 400 | 参数错误 / 业务校验失败（如选课已满） | `ElMessage.error(message)` 弹出 |
| 401 | 未登录 / Token 失效 | 清除登录态，跳转 `/login` |
| 403 | 已登录但无权限 | `ElMessage.error(message)` |
| 500 | 服务器错误 | `ElMessage.error(message)` |

> **业务失败（如选课冲突）请用 `code=400` + 明确的 `message`**，例如
> `{"code":400,"message":"课程已满","data":null}`。前端会直接把 `message` 弹给用户。

### 1.2 鉴权

- 登录成功后前端保存 `token`，此后每个请求自动携带请求头：

  ```
  Authorization: Bearer <token>
  ```

- 后端用 JWT 校验，Payload 建议包含 `user_id` 和 `role`（`student` / `teacher` / `admin`）。
- 各接口的「角色」列表示该接口要求的访问角色。

### 1.3 时间格式

统一 ISO 8601 字符串：`"2026-02-20T10:12:00"`。前端自行格式化展示。

---

## 二、认证模块

### 2.1 登录

| | |
|---|---|
| 方法 | `POST` |
| 路径 | `/api/auth/login` |
| 角色 | 公开 |

**请求体**

```json
{
    "username": "S2023001",
    "password": "123456",
    "role": "student"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| username | string | 用户名 / 学号 / 工号 |
| password | string | 密码 |
| role | string | `student` / `teacher` / `admin`，需与账号实际角色一致 |

**成功响应 `data`**

```json
{
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
        "user_id": 4,
        "username": "S2023001",
        "real_name": "张小明",
        "role": "student"
    }
}
```

> 登录失败（用户名/密码/角色不匹配）返回 `code=400`，`message` 如「用户名、密码或角色不正确」。

### 2.2 获取当前学年学期

| | |
|---|---|
| 方法 | `GET` |
| 路径 | `/api/common/current-term` |
| 角色 | 登录用户 |

**成功响应 `data`**

```json
{
    "term_id": 4,
    "term_name": "2025-2026学年第二学期",
    "academic_year_name": "2025-2026学年",
    "term_no": 2,
    "is_current": true
}
```

---

## 三、学生端

### 3.1 个人信息

`GET /api/student/profile` ，角色：student

```json
{
    "student_no": "S2023001",
    "real_name": "张小明",
    "gender": "男",
    "department_name": "计算机学院",
    "major_name": "软件工程",
    "class_name": "软工2301班",
    "grade_year": 2023,
    "enroll_year": 2023,
    "student_status": "在读",
    "phone": "13800000001",
    "email": "zhangxm@shu.edu.cn"
}
```

> 维护手机号/邮箱可另开 `PUT /api/student/profile`（前端当前为本地更新，联调时按需新增）。

### 3.2 可选课程列表

`GET /api/student/courses` ，角色：student
返回当前学期对该学生可见的开课班数组。

```json
[
    {
        "offering_id": 101,
        "course_code": "CS201",
        "course_name": "数据库原理",
        "credits": 3.5,
        "hours": 64,
        "course_type": "必修课",
        "teacher_name": "李教授",
        "teaching_class_name": "数据库原理-01班",
        "schedule_text": "周一 1-2节 / 周三 3-4节",
        "location": "东区教学楼 A305",
        "capacity": 40,
        "selected_count": 38,
        "is_retake_class": false,
        "select_status": "available",
        "description": "系统讲授关系数据库理论、SQL、事务、索引与查询优化。",
        "assessment_type": "考试"
    }
]
```

| 字段 | 说明 |
|------|------|
| selected_count / capacity | 前端显示为 `38/40`，达到容量显示红色 |
| select_status | **由后端计算每门课对当前学生的状态**：`available` 可选 / `selected` 已选 / `full` 已满 / `conflict` 时间冲突 / `passed` 已通过不可选 / `retake` 待重修可选 |
| is_retake_class | 是否重修班，前端打「重修班」标签 |

### 3.3 选课

| | |
|---|---|
| 方法 | `POST` |
| 路径 | `/api/student/enroll` |
| 角色 | student |

**请求体** `{ "offering_id": 101 }`

后端应调用存储过程 `sp_StudentSelectCourse` 完成全套校验（时间窗口、容量、同课程重复、已通过、重修资格、时间冲突等）。

- 成功：`code=200`，`data` 可为 `null` 或新选课记录摘要。
- 失败：`code=400` + 明确 `message`，例如：`课程已满` / `上课时间冲突` / `已选过该课程` / `该课程你已通过，无需重选` / `不在选课时间内`。前端直接弹出 `message`。

### 3.4 退课

| | |
|---|---|
| 方法 | `DELETE` |
| 路径 | `/api/student/enroll/{offering_id}` |
| 角色 | student |

后端调用 `sp_StudentDropCourse`。成功 `code=200`；不可退（已录成绩/超时/锁定）返回 `code=400` + 原因。

### 3.5 已选课程

`GET /api/student/my-courses` ，角色：student

```json
[
    {
        "enrollment_id": 5001,
        "offering_id": 101,
        "course_code": "CS201",
        "course_name": "数据库原理",
        "credits": 3.5,
        "teacher_name": "李教授",
        "schedule_text": "周一 1-2节 / 周三 3-4节",
        "location": "东区教学楼 A305",
        "is_retake": false,
        "enroll_time": "2026-02-20T10:12:00",
        "status": "已选",
        "can_drop": true
    }
]
```

| 字段 | 说明 |
|------|------|
| status | `已选` / `已退` / `已完成` / `因课程取消失效` |
| can_drop | 是否允许退课（重修班/已录成绩/超时 → false），前端据此禁用退课按钮 |

### 3.6 个人课表

`GET /api/student/timetable` ，角色：student
返回结构化时间段数组，前端按「节次 × 星期」渲染网格。

```json
[
    {
        "offering_id": 101,
        "course_name": "数据库原理",
        "teacher_name": "李教授",
        "location": "A305",
        "weekday": 1,
        "start_section": 1,
        "end_section": 2
    }
]
```

| 字段 | 说明 |
|------|------|
| weekday | 1-7（周一到周日） |
| start_section / end_section | 起止节次（1-10），前端用于跨节次合并单元格 |

### 3.7 成绩查询

`GET /api/student/grades` ，角色：student（**仅返回已发布成绩**）

```json
[
    {
        "grade_id": 9001,
        "term_name": "2024-2025学年第二学期",
        "course_name": "高等数学（下）",
        "credits": 5.0,
        "teacher_name": "孙老师",
        "total_score": 52,
        "grade_point": 0,
        "is_passed": false,
        "is_retake": false,
        "included_in_average": true,
        "score_status": "已发布"
    }
]
```

### 3.8 平均成绩统计

`GET /api/student/average-score` ，角色：student

```json
{
    "simple_average": 78.0,
    "weighted_average": 79.6,
    "average_gpa": 2.74,
    "total_credits": 18.5,
    "earned_credits": 13.5
}
```

### 3.9 挂科与重修状态

`GET /api/student/retake` ，角色：student

```json
[
    {
        "retake_id": 7001,
        "course_name": "高等数学（下）",
        "source_term": "2024-2025学年第二学期",
        "source_score": 52,
        "status": "重修中",
        "current_offering": "高数下-重修班（本学期）"
    }
]
```

> `status`：`待重修` / `重修中` / `重修通过` / `重修未通过`。

### 3.10 消息通知

`GET /api/student/notifications` ，角色：student

```json
[
    {
        "notification_id": 1,
        "title": "选课成功",
        "content": "您已成功选择《数据库原理》，请按时上课。",
        "notification_type": "选课",
        "is_read": false,
        "created_at": "2026-02-20T10:12:30"
    }
]
```

> `notification_type`：`选课` / `退课` / `成绩` / `重修` / `审批`。

---

## 四、教师端

### 4.1 个人信息

`GET /api/teacher/profile` ，角色：teacher

```json
{
    "teacher_no": "T1001",
    "real_name": "李教授",
    "gender": "男",
    "department_name": "计算机学院",
    "title": "教授",
    "phone": "13900000001",
    "email": "lijs@shu.edu.cn"
}
```

### 4.2 授课任务

`GET /api/teacher/offerings` ，角色：teacher（含历史学期）

```json
[
    {
        "offering_id": 101,
        "course_code": "CS201",
        "course_name": "数据库原理",
        "term_name": "2025-2026学年第二学期",
        "teaching_class_name": "数据库原理-01班",
        "schedule_text": "周一 1-2节 / 周三 3-4节",
        "location": "A305",
        "capacity": 40,
        "selected_count": 38,
        "is_retake_class": false,
        "status": "开放选课"
    }
]
```

> `status`：`待审批` / `已通过` / `开放选课` / `关闭选课` / `已取消` / `已结课`。

### 4.3 选课学生名单

`GET /api/teacher/roster/{offering_id}` ，角色：teacher（仅本人课程）

```json
[
    {
        "student_no": "S2023001",
        "real_name": "张小明",
        "major_name": "软件工程",
        "class_name": "软工2301班",
        "is_retake": false,
        "enroll_time": "2026-02-20T10:12:00",
        "score_status": "未录入"
    }
]
```

### 4.4 成绩录入表

`GET /api/teacher/grade-sheet/{offering_id}` ，角色：teacher

```json
[
    {
        "enrollment_id": 5001,
        "student_no": "S2023001",
        "real_name": "张小明",
        "usual_score": 85,
        "experiment_score": 90,
        "final_score": 80,
        "total_score": 83,
        "score_status": "草稿"
    }
]
```

| 字段 | 说明 |
|------|------|
| usual/experiment/final_score | 平时/实验/期末成绩，未录入为 `null` |
| total_score | 总评；前端按 平时×30%+实验×20%+期末×50% 实时计算，提交时以后端为准 |
| score_status | `未录入` / `草稿` / `已录入` / `已提交` / `已发布` / `已冻结`；后三者前端禁止编辑 |

### 4.5 保存成绩（草稿）

| | |
|---|---|
| 方法 | `POST` |
| 路径 | `/api/teacher/grade` |
| 角色 | teacher |

**请求体**

```json
{
    "offering_id": 101,
    "rows": [
        { "enrollment_id": 5001, "usual_score": 85, "experiment_score": 90, "final_score": 80 }
    ]
}
```

> 后端可在保存时计算并落库 `total_score`、`is_passed`。

### 4.6 提交成绩

| | |
|---|---|
| 方法 | `POST` |
| 路径 | `/api/teacher/grade/submit` |
| 角色 | teacher |

**请求体** `{ "offering_id": 101 }`
后端调用 `sp_TeacherSubmitGrade`：计算总评、判断是否通过、将状态置为 `已提交`（之后教师不可改）。

### 4.7 教学申请列表

`GET /api/teacher/requests` ，角色：teacher

```json
[
    {
        "request_id": 301,
        "request_type": "扩容申请",
        "course_name": "数据库原理",
        "term_name": "2025-2026学年第二学期",
        "content": "当前 40/40 已满，申请扩容至 50 人",
        "reason": "选课需求旺盛",
        "status": "待审批",
        "created_at": "2026-02-22T09:00:00"
    }
]
```

> `request_type`：`开课申请` / `扩容申请` / `调课申请` / `停课申请` / `成绩修改申请`。
> `status`：`待审批` / `已通过` / `已驳回`。

### 4.8 提交申请

`POST /api/teacher/requests` ，角色：teacher

**请求体**

```json
{
    "request_type": "扩容申请",
    "course_name": "数据库原理",
    "content": "容量 40 → 50",
    "reason": "选课需求旺盛"
}
```

### 4.9 成绩统计（按本人教学班）

`GET /api/teacher/grade-stats` ，角色：teacher

```json
[
    {
        "offering_id": 90,
        "course_name": "数据结构",
        "teaching_class_name": "数据结构-01班",
        "enrolled": 40,
        "attended": 40,
        "passed": 36,
        "failed": 4,
        "avg": 78.5,
        "max": 96,
        "min": 41,
        "fail_rate": 10.0,
        "retake_count": 4
    }
]
```

---

## 五、管理员端

### 5.1 总览 / 统计分析

`GET /api/admin/statistics` ，角色：admin
（同时供「总览」和「统计分析」两个页面使用）

```json
{
    "cards": {
        "total_students": 1280,
        "total_teachers": 96,
        "total_courses": 64,
        "total_offerings": 38
    },
    "capacity": [
        { "course_name": "数据库原理", "teacher_name": "李教授", "capacity": 40, "selected_count": 38, "remain": 2, "fill_rate": 95 }
    ],
    "score_distribution": [
        { "range": "90-100", "count": 120 },
        { "range": "80-89", "count": 260 },
        { "range": "70-79", "count": 310 },
        { "range": "60-69", "count": 180 },
        { "range": "0-59", "count": 60 }
    ],
    "retake": [
        { "course_name": "高等数学（下）", "failed": 60, "pending_retake": 45, "retaking": 12, "passed_retake": 30 }
    ]
}
```

### 5.2 用户管理

**列表** `GET /api/admin/users` ，角色：admin

```json
[
    {
        "user_id": 4,
        "username": "S2023001",
        "real_name": "张小明",
        "role": "student",
        "role_name": "学生",
        "phone": "13800000001",
        "status": "正常"
    }
]
```

**新增 / 编辑** `POST /api/admin/users` ，角色：admin

```json
{
    "user_id": null,
    "username": "S2023099",
    "real_name": "新同学",
    "role": "student",
    "phone": "13800000099"
}
```

> `user_id` 为 `null` 表示新增，否则为编辑。
> 建议另提供：`POST /api/admin/users/{id}/reset-password`（重置为 123456）、
> `POST /api/admin/users/{id}/toggle-status`（启用/禁用）。

### 5.3 学年学期

`GET /api/admin/terms` ，角色：admin

```json
[
    {
        "academic_year_name": "2025-2026学年",
        "terms": [
            { "term_id": 3, "term_no": 1, "term_name": "2025-2026学年第一学期", "start_date": "2025-09-01", "end_date": "2026-01-18", "is_current": false },
            { "term_id": 4, "term_no": 2, "term_name": "2025-2026学年第二学期", "start_date": "2026-02-24", "end_date": "2026-07-05", "is_current": true }
        ]
    }
]
```

> 设为当前学期建议：`POST /api/admin/terms/{term_id}/set-current`。

### 5.4 业务时间窗口

`GET /api/admin/business-windows` ，角色：admin

```json
[
    {
        "window_id": 1,
        "term_name": "2025-2026学年第二学期",
        "window_type": "选课",
        "start_time": "2026-02-18T09:00:00",
        "end_time": "2026-03-01T22:00:00",
        "status": "进行中"
    }
]
```

> `window_type`：`选课` / `退课` / `成绩录入` / `成绩公布`。
> `status`：`未开始` / `进行中` / `已结束`。

### 5.5 课程库

**列表** `GET /api/admin/courses` ，角色：admin

```json
[
    {
        "course_id": 1,
        "course_code": "CS201",
        "course_name": "数据库原理",
        "credits": 3.5,
        "hours": 64,
        "course_type": "必修课",
        "assessment_type": "考试",
        "allow_retake": true,
        "is_enabled": true
    }
]
```

**新增 / 编辑** `POST /api/admin/courses` ，角色：admin（请求体同上结构，`course_id=null` 为新增）。

### 5.6 教室资源

`GET /api/admin/classrooms` ，角色：admin

```json
[
    { "classroom_id": 1, "building": "东区教学楼", "room_no": "A305", "capacity": 60, "status": "可用" }
]
```

> `status`：`可用` / `维修中` / `停用`。

### 5.7 开课管理

**列表** `GET /api/admin/offerings` ，角色：admin

```json
[
    {
        "offering_id": 101,
        "course_name": "数据库原理",
        "teacher_name": "李教授",
        "term_name": "2025-2026学年第二学期",
        "teaching_class_name": "数据库原理-01班",
        "capacity": 40,
        "selected_count": 38,
        "min_enrollment": 10,
        "is_retake_class": false,
        "status": "开放选课"
    }
]
```

**新增开课** `POST /api/admin/offerings` ，角色：admin
建议字段：`term_id`、`course_id`、`teacher_id`、`teaching_class_name`、`capacity`、`min_enrollment`、`is_retake_class`、时间段列表。

> 另建议：`POST /api/admin/offerings/{id}/toggle-select`（开放/关闭选课）、
> `POST /api/admin/offerings/{id}/cancel`（取消开课，需低于最低人数，并通知学生）。

### 5.8 申请审批

**待审批列表** `GET /api/admin/approvals` ，角色：admin

```json
[
    {
        "request_id": 301,
        "teacher_name": "李教授",
        "request_type": "扩容申请",
        "course_name": "数据库原理",
        "term_name": "2025-2026学年第二学期",
        "content": "40 → 50 人",
        "conflict_check_result": "教室容量充足（A305=60），无冲突",
        "status": "待审批",
        "created_at": "2026-02-22T09:00:00"
    }
]
```

**审批** `POST /api/admin/approve` ，角色：admin

```json
{
    "request_id": 301,
    "result": "通过",
    "comment": "同意扩容"
}
```

> `result`：`通过` / `驳回`。后端调用 `sp_AdminApproveRequest`，通过后据申请类型落地（如改容量、生成开课班、更新时间段）并写审批记录、发送通知。

### 5.9 成绩发布

**待发布列表** `GET /api/admin/grade-publish` ，角色：admin

```json
[
    {
        "offering_id": 90,
        "course_name": "数据结构",
        "teacher_name": "李教授",
        "term_name": "2024-2025学年第二学期",
        "submitted_count": 40,
        "total_count": 40,
        "score_status": "已提交",
        "can_publish": true
    }
]
```

**发布** `POST /api/admin/grade/publish` ，角色：admin
**请求体** `{ "offering_id": 90 }`
后端将该班成绩状态置为 `已发布`，触发挂科/重修记录生成（`sp_CreateRetakeRecords`），并写审计日志。

### 5.10 重修管理

`GET /api/admin/retake` ，角色：admin

```json
[
    {
        "course_name": "高等数学（下）",
        "failed_count": 60,
        "pending_count": 45,
        "retaking_count": 12,
        "passed_count": 30,
        "has_retake_class": true
    }
]
```

> 安排重修班建议：`POST /api/admin/retake/arrange`（创建重修开课班）。

### 5.11 操作日志

`GET /api/admin/audit-logs` ，角色：admin

```json
[
    {
        "log_id": 1,
        "operator": "admin",
        "operation_type": "强制退课",
        "target_type": "选课记录",
        "target_id": "5099",
        "reason": "学生休学，特殊处理",
        "created_at": "2026-02-22T16:20:00"
    }
]
```

---

## 六、接口与页面对照表

| 页面 | 接口 |
|------|------|
| 登录 | `POST /auth/login` |
| 学生·选课中心 | `GET /student/courses`、`POST /student/enroll` |
| 学生·已选课程 | `GET /student/my-courses`、`DELETE /student/enroll/{id}` |
| 学生·我的课表 | `GET /student/timetable` |
| 学生·成绩查询 | `GET /student/grades`、`GET /student/average-score` |
| 学生·挂科重修 | `GET /student/retake` |
| 学生·消息通知 | `GET /student/notifications` |
| 学生·个人信息 | `GET /student/profile` |
| 教师·授课任务 | `GET /teacher/offerings` |
| 教师·选课名单 | `GET /teacher/roster/{id}` |
| 教师·成绩录入 | `GET /teacher/grade-sheet/{id}`、`POST /teacher/grade`、`POST /teacher/grade/submit` |
| 教师·成绩统计 | `GET /teacher/grade-stats` |
| 教师·教学申请 | `GET /teacher/requests`、`POST /teacher/requests` |
| 教师·个人信息 | `GET /teacher/profile` |
| 管理员·总览 / 统计 | `GET /admin/statistics` |
| 管理员·用户管理 | `GET/POST /admin/users` |
| 管理员·学年学期 | `GET /admin/terms`、`GET /admin/business-windows` |
| 管理员·课程库 | `GET/POST /admin/courses` |
| 管理员·教室资源 | `GET /admin/classrooms` |
| 管理员·开课管理 | `GET/POST /admin/offerings` |
| 管理员·申请审批 | `GET /admin/approvals`、`POST /admin/approve` |
| 管理员·成绩发布 | `GET /admin/grade-publish`、`POST /admin/grade/publish` |
| 管理员·重修管理 | `GET /admin/retake` |
| 管理员·操作日志 | `GET /admin/audit-logs` |

---

## 七、联调切换说明

1. 后端启动并监听 `http://localhost:5000`，所有接口加 `/api` 前缀。
2. 前端把 `frontend/src/api/services.js` 顶部：

   ```js
   export const USE_MOCK = true   // 改为 false 即走真实后端
   ```

3. 前端开发服务器已配置代理（`vite.config.js`），`/api/*` 自动转发到 5000 端口，无需处理跨域。
4. 若个别接口字段暂未对齐，可临时把对应函数留在 mock，逐个接口替换，互不影响。

# 后端开发与对接要求（BACKEND_TASKS.md）

> 面向同学 A（后端 + 数据库）。本文件说明**要做什么、怎么自测、要和前端对齐哪些点**。
> 配套文档：
> - 接口字段细节 → `API.md`（前端已严格按它消费数据，**这是契约，以它为准**）
> - 数据库表结构 / 触发器 / 存储过程设计 → `DB_DESIGN.md`
> - 技术栈与项目结构 → `TECH_STACK.md`
> - 分工与时间线 → `TEAM_DEVISION.md`

---

## 一、目标与交付物

后端需交付一个监听 `http://localhost:5000`、所有接口以 `/api` 为前缀的 Flask 服务，使前端把
`frontend/src/api/services.js` 顶部的 `USE_MOCK` 改为 `false` 后能直接跑通全部页面。

交付清单：

- [ ] MySQL `school` 数据库：按 `DB_DESIGN.md` 建表 + 初始测试数据
- [ ] 至少 1 个触发器：`trg_UpdateOfferingSelectedCount`
- [ ] 至少 3 个存储过程：`sp_StudentSelectCourse`、`sp_StudentDropCourse`、`sp_TeacherSubmitGrade`
- [ ] Flask 服务：登录 + JWT + 角色鉴权 + `API.md` 中全部接口
- [ ] 自测通过（见第六节清单），并能配合前端联调

---

## 二、环境（已就绪，确认即可）

| 项 | 值 |
|---|---|
| Python | 3.14（venv 在 `backend/.venv/`） |
| 依赖 | 已固定在 `backend/requirements.txt` |
| 数据库 | MySQL 8.x，库名 `school` |
| 数据库账号 | 用户 `christian`，密码 `123456` |
| 服务端口 | `5000` |
| 前端开发端口 | `5173`（已配 Vite 代理转发 `/api`） |

```bash
# 激活环境并安装依赖
cd ~/Playground/SHU/backend
source .venv/bin/activate
pip install -r requirements.txt

# 登录数据库（验证账号可用）
mysql -u christian -p123456
```

> `.env`（不提交 git，已在 `.gitignore` 忽略）建议内容：
> ```ini
> DB_HOST=127.0.0.1
> DB_PORT=3306
> DB_USER=christian
> DB_PASSWORD=123456
> DB_NAME=school
> SECRET_KEY=任意随机字符串用于JWT签名
> ```

---

## 三、数据库任务

### 3.1 建库与建表

- 按 `DB_DESIGN.md` 第四节的表结构建表（用户权限、组织人员、学年学期、课程资源、开课排课、选课退课、成绩重修、申请审批、通知审计九大模块）。
- 建议把全部建表语句放在 `backend/sql/01_schema.sql`，触发器/存储过程放 `02_routines.sql`，初始数据放 `03_seed.sql`，方便重建和答辩演示。

### 3.2 初始测试数据（必须与前端测试账号对齐）

前端登录页和 mock 数据写死了演示账号，**后端 seed 数据必须能让这三个账号登录成功**：

| 角色 | 用户名 | 密码 | 姓名 |
|---|---|---|---|
| 学生 | `S2023001` | `123456` | 张小明 |
| 教师 | `T1001` | `123456` | 李教授 |
| 管理员 | `admin` | `123456` | 系统管理员 |

另需满足 `TEAM_DEVISION.md` 要求：≥3 学生、≥2 教师、1 管理员、≥5 门课、≥3 个开课班，且要造出可演示的：
- 至少 1 个**已满**的开课班（容量演示 `40/40`）
- 至少 1 个**重修班**和 1 名**有挂科记录**的学生（重修流程演示）
- 至少 1 个**已提交待发布**成绩的开课班（成绩发布演示）
- 至少 1 条**待审批**的教师申请（审批演示）

> 密码请存哈希（`werkzeug.security.generate_password_hash`），不要明文。

### 3.3 触发器（实验要求第 8 条）

`trg_UpdateOfferingSelectedCount`：在 `Enrollments` 表 INSERT/UPDATE/DELETE 后，按**有效选课记录**（状态为「已选」或「已完成」）重新统计该开课班人数，写回 `CourseOfferings.selected_count_cached`。

> 注意：容量判断仍以实时统计有效记录为准，缓存字段只用于展示，避免不一致（见 `DB_DESIGN.md` 11 节）。

### 3.4 存储过程

| 名称 | 触发场景 | 关键校验 / 动作 |
|---|---|---|
| `sp_StudentSelectCourse(student_id, offering_id)` | 学生选课 | 选课时间窗口、学籍、课程状态、容量、同学期同课程不重复、当前未在修、历史未通过、重修资格、时间冲突、（可选）专业年级/先修；失败用明确错误信息返回 |
| `sp_StudentDropCourse(student_id, offering_id)` | 学生退课 | 当前学期、未录成绩、未锁定、退课时间内；成功则状态置「已退」并释放容量 |
| `sp_TeacherSubmitGrade(offering_id)` | 教师提交成绩 | 计算总评（平时30%+实验20%+期末50%）、判断 `is_passed`（≥60）、状态置「已提交」 |

> 选做（加分，呼应 `DB_DESIGN.md` 7.3）：`sp_AdminPublishGrades`、`sp_CreateRetakeRecords`、`sp_AdminApproveRequest`、`sp_CheckScheduleConflict`。

> 存储过程返回错误的方式：建议用 `SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='课程已满'`，
> 后端捕获 PyMySQL 异常的 `args[1]` 作为 `message`，以 `code=400` 返回（见第五节）。

---

## 四、Flask 任务

按 `TECH_STACK.md` 的结构搭建（工厂模式 + Blueprint 分模块）：

```
backend/app/
├── __init__.py      # create_app() 工厂；注册 CORS、蓝图
├── db.py            # PyMySQL 连接（建议连接池 / 每请求连接），统一游标
├── auth.py          # 登录、JWT 签发与校验、@login_required、@role_required
└── routes/
    ├── student.py   # /api/student/*
    ├── teacher.py   # /api/teacher/*
    └── admin.py     # /api/admin/*
```

要点：

1. **CORS**：放行前端来源（开发期 `http://localhost:5173`）。即使有 Vite 代理，直接访问 5000 调试时也需要。
2. **JWT**：登录签发 `{user_id, role, exp}`；`@role_required('student')` 校验角色，不符返回 `code=403`，未带/失效 Token 返回 `code=401`。
3. **统一返回**：封装 `ok(data)` / `fail(code, message)` 两个 helper，所有接口走它们。
4. **接口清单**：以 `API.md` 第六节「页面↔接口对照表」为准，逐个实现。

---

## 五、必须对齐的契约（最容易联调踩坑，重点看）

前端是按这些约定写死的，后端不一致会直接导致页面报错或显示空白：

1. **响应信封**：固定 `{ "code": 200, "message": "...", "data": ... }`。前端拦截器只在 `code===200` 时取 `data`；其余 `code` 弹 `message`。
2. **角色值**：必须是小写 `student` / `teacher` / `admin`（登录返回的 `user.role` 和 JWT 里都用它）。
3. **业务失败**：选课/退课等校验失败用 **`code=400` + 明确中文 `message`**（如「课程已满」「上课时间冲突」「已选过该课程」），前端直接弹给用户，**不要**用 200 包一个 success=false。
4. **字段名 snake_case**：与 `API.md` / mock 完全一致，例如 `selected_count`、`offering_id`、`enroll_time`、`total_score`。少一个或拼错前端取不到。
5. **枚举值必须一字不差**（前端用它判断标签颜色 / 按钮可用性）：
   - 可选课程 `select_status`：`available` / `selected` / `full` / `conflict` / `passed` / `retake`
   - 成绩 `score_status`：`未录入` / `草稿` / `已录入` / `已提交` / `已发布` / `已冻结`
   - 开课班 `status`：`待审批` / `已通过` / `开放选课` / `关闭选课` / `已取消` / `已结课`
   - 选课 `status`：`已选` / `已退` / `已完成` / `因课程取消失效`
   - 申请 `request_type`：`开课申请` / `扩容申请` / `调课申请` / `停课申请` / `成绩修改申请`；`status`：`待审批` / `已通过` / `已驳回`
   - 业务窗口 `window_type`：`选课` / `退课` / `成绩录入` / `成绩公布`
   - 通知 `notification_type`：`选课` / `退课` / `成绩` / `重修` / `审批`
6. **时间格式**：ISO 8601 字符串 `"2026-02-20T10:12:00"`（前端会把 `T` 替换成空格显示）。
7. **课表**：`weekday` 用 1-7，`start_section`/`end_section` 用节次号（1-10）。
8. **布尔字段**返回真正的 `true/false`（如 `is_passed`、`can_drop`、`allow_retake`），不要返回 0/1 字符串。
9. **`select_status` 与 `can_drop` 由后端计算**：这两个是「针对当前登录学生」的判断结果，前端不会自己算。

---

## 六、自测清单（联调前后端先各自跑通）

启动：

```bash
cd ~/Playground/SHU/backend && source .venv/bin/activate && python run.py
```

用 curl 逐项验证（替换 `<TOKEN>`）：

```bash
# 1. 登录拿 token（三种角色都试）
curl -s -X POST http://localhost:5000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"S2023001","password":"123456","role":"student"}'

# 2. 带 token 取可选课程，确认 select_status / selected_count 字段在
curl -s http://localhost:5000/api/student/courses \
  -H 'Authorization: Bearer <TOKEN>'

# 3. 选课：故意选一个已满的班，确认返回 code=400 + "课程已满"
curl -s -X POST http://localhost:5000/api/student/enroll \
  -H 'Authorization: Bearer <TOKEN>' -H 'Content-Type: application/json' \
  -d '{"offering_id":102}'

# 4. 不带 token 访问受保护接口，确认返回 code=401
curl -s http://localhost:5000/api/student/courses
```

逐项确认：

- [ ] 三个演示账号都能登录，返回正确的 `role`
- [ ] 角色越权访问（学生调 `/admin/*`）返回 403
- [ ] 选课成功后，再查 `/student/courses` 该班 `selected_count` +1（验证触发器生效）
- [ ] 退课后 `selected_count` -1
- [ ] 已满 / 时间冲突 / 重复选 分别返回 `code=400` + 对应中文 message
- [ ] 教师提交成绩后，成绩 `score_status` 变「已提交」、`total_score`/`is_passed` 计算正确
- [ ] 管理员发布成绩后，挂科学生生成待重修记录
- [ ] 所有列表接口返回的是**数组**（前端 `v-for`），对象接口返回**对象**，不要混
- [ ] 每个接口返回都是 `{code,message,data}` 信封

---

## 七、联调流程

1. 后端 `python run.py` 跑起来，先用第六节 curl 自测通过。
2. 前端改 `frontend/src/api/services.js`：`export const USE_MOCK = false`。
3. 前端 `npm run dev`，逐页点过去；浏览器 F12 → Network 看哪个接口红了。
4. 字段对不上时，**以 `API.md` 为准**调整后端；可临时把个别函数留在 mock，单接口逐个替换，互不影响（见 `services.js` 写法）。
5. 联调常见问题排查顺序：CORS 报错 → 检查 flask-cors 放行；401 → 检查 token 是否签发/校验一致；data 取不到 → 对字段名和信封结构。

---

## 八、答辩 / 验收要点（对照实验要求）

| 实验要求 | 后端需能演示 |
|---|---|
| 触发器 ≥1 | 选课/退课时 `trg_UpdateOfferingSelectedCount` 自动改人数，现场查 `selected_count_cached` 变化 |
| 存储过程 ≥1 | `sp_StudentSelectCourse` 现场调用，展示各类校验失败信息 |
| 三角色不同权限 | 用 `@role_required` + 越权 403 演示 |
| 学分制教务功能 | 学年学期、开课、选课、成绩、重修、审批闭环 |
| 统计分析 | `/admin/statistics`、`/teacher/grade-stats`、学生平均绩点 |

> 建议保留可重跑的 SQL 脚本（schema / routines / seed），答辩时能一键重建库并演示存储过程调用。

---

## 九、易错业务逻辑（来自 DB_DESIGN.md 第 11 节，务必在存储过程里实现）

- 同一学期同一课程只能有一条有效选课记录（不能同时选不同老师的同一门课）
- 已通过的课程不能再选；当前在修不能重复选
- 上学期挂科必须等成绩发布、进入后续学期才能重修
- 时间冲突用「星期 + 周次交集 + 节次交集」判断
- 人数以有效选课记录统计，缓存字段只用于显示
- 退课不物理删除，状态改「已退」并释放容量
- 重修成绩新增记录，不覆盖原始挂科成绩
- 成绩未发布学生不可见；教师提交后改成绩须走申请
- 管理员强制处理（补选/退课/改成绩）必须写 `AuditLogs`

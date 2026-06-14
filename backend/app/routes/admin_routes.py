#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
管理员端路由模块
"""
from datetime import datetime
from flask import request
from app.routes import admin_bp
from app.utils import success_response, error_response, sync_offering_status_by_window
from app.auth import role_required
from app.db import get_db_cursor
import pymysql


@admin_bp.route('/statistics', methods=['GET'])
@role_required('admin')
def get_statistics():
    """获取总览统计"""
    with get_db_cursor(commit=False) as cursor:
        # 基础统计卡片
        cursor.execute("SELECT COUNT(*) as total FROM Students")
        total_students = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM Teachers")
        total_teachers = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM Courses")
        total_courses = cursor.fetchone()['total']

        cursor.execute("""
            SELECT COUNT(*) as total FROM CourseOfferings
            WHERE term_id = (SELECT term_id FROM Terms WHERE is_current = TRUE)
        """)
        total_offerings = cursor.fetchone()['total']

        # 课程容量统计
        cursor.execute("""
            SELECT c.course_name, t.real_name as teacher_name,
                   co.capacity, co.selected_count_cached as selected_count,
                   (co.capacity - co.selected_count_cached) as remain,
                   ROUND(co.selected_count_cached * 100.0 / co.capacity, 0) as fill_rate
            FROM CourseOfferings co
            JOIN Courses c ON co.course_id = c.course_id
            JOIN Teachers t ON co.teacher_id = t.teacher_id
            WHERE co.term_id = (SELECT term_id FROM Terms WHERE is_current = TRUE)
            AND co.status = '开放选课'
            ORDER BY fill_rate DESC
            LIMIT 10
        """)
        capacity = cursor.fetchall()

        # 成绩分布
        cursor.execute("""
            SELECT
                CASE
                    WHEN g.total_score >= 90 THEN '90-100'
                    WHEN g.total_score >= 80 THEN '80-89'
                    WHEN g.total_score >= 70 THEN '70-79'
                    WHEN g.total_score >= 60 THEN '60-69'
                    ELSE '0-59'
                END as `range`,
                COUNT(*) as count
            FROM Grades g
            WHERE g.score_status = '已发布'
            GROUP BY `range`
            ORDER BY MIN(g.total_score) DESC
        """)
        score_distribution = cursor.fetchall()

        # 重修统计
        cursor.execute("""
            SELECT c.course_name,
                   SUM(CASE WHEN r.status IN ('待重修', '重修中', '重修通过', '重修未通过') THEN 1 ELSE 0 END) as failed,
                   SUM(CASE WHEN r.status = '待重修' THEN 1 ELSE 0 END) as pending_retake,
                   SUM(CASE WHEN r.status = '重修中' THEN 1 ELSE 0 END) as retaking,
                   SUM(CASE WHEN r.status = '重修通过' THEN 1 ELSE 0 END) as passed_retake
            FROM RetakeRecords r
            JOIN Enrollments e ON r.source_enrollment_id = e.enrollment_id
            JOIN CourseOfferings co ON e.offering_id = co.offering_id
            JOIN Courses c ON co.course_id = c.course_id
            GROUP BY c.course_id
            HAVING failed > 0
            ORDER BY failed DESC
            LIMIT 10
        """)
        retake = cursor.fetchall()

        return success_response({
            'cards': {
                'total_students': total_students,
                'total_teachers': total_teachers,
                'total_courses': total_courses,
                'total_offerings': total_offerings
            },
            'capacity': capacity,
            'score_distribution': score_distribution,
            'retake': retake
        })


@admin_bp.route('/users', methods=['GET'])
@role_required('admin')
def get_users():
    """获取用户列表"""
    with get_db_cursor(commit=False) as cursor:
        sql = """
        SELECT u.user_id, u.username, u.real_name, u.role,
               CASE u.role
                   WHEN 'student' THEN '学生'
                   WHEN 'teacher' THEN '教师'
                   WHEN 'admin' THEN '管理员'
               END as role_name,
               COALESCE(s.phone, t.phone, '') as phone,
               COALESCE(s.gender, t.gender) as gender,
               COALESCE(s.department_id, t.department_id) as department_id,
               COALESCE(d.department_name, '') as department_name,
               t.title,
               s.major_id, COALESCE(m.major_name, '') as major_name,
               s.class_id, COALESCE(cl.class_name, '') as class_name,
               u.status
        FROM Users u
        LEFT JOIN Students s ON u.user_id = s.user_id
        LEFT JOIN Teachers t ON u.user_id = t.user_id
        LEFT JOIN Departments d ON COALESCE(s.department_id, t.department_id) = d.department_id
        LEFT JOIN Majors m ON s.major_id = m.major_id
        LEFT JOIN Classes cl ON s.class_id = cl.class_id
        ORDER BY u.user_id
        """
        cursor.execute(sql)
        users = cursor.fetchall()

        return success_response(users)


@admin_bp.route('/users', methods=['POST'])
@role_required('admin')
def create_or_update_user():
    """新增或编辑用户"""
    data = request.get_json()
    user_id = data.get('user_id')
    username = data.get('username')
    real_name = data.get('real_name')
    role = data.get('role')
    phone = data.get('phone')
    # 角色相关字段
    gender = data.get('gender') or None
    department_id = data.get('department_id') or None
    title = data.get('title') or None          # 教师职称
    major_id = data.get('major_id') or None     # 学生专业
    class_id = data.get('class_id') or None      # 学生班级

    if not all([username, real_name, role]):
        return error_response(400, "参数不完整")

    with get_db_cursor(commit=True) as cursor:
        if user_id:
            # 编辑：更新 Users，并把信息同步到对应的角色表
            cursor.execute("""
                UPDATE Users SET username=%s, real_name=%s, role=%s
                WHERE user_id=%s
            """, (username, real_name, role, user_id))
            cursor.execute("""
                UPDATE Teachers
                SET real_name=%s, phone=%s, gender=%s, department_id=%s, title=%s
                WHERE user_id=%s
            """, (real_name, phone, gender, department_id, title, user_id))
            cursor.execute("""
                UPDATE Students
                SET real_name=%s, phone=%s, gender=%s,
                    department_id=%s, major_id=%s, class_id=%s
                WHERE user_id=%s
            """, (real_name, phone, gender, department_id, major_id, class_id, user_id))
        else:
            # 新增：先查重，避免插入一半留下孤儿数据
            cursor.execute("SELECT user_id FROM Users WHERE username=%s", (username,))
            if cursor.fetchone():
                return error_response(400, f"用户名 {username} 已存在")

            from werkzeug.security import generate_password_hash
            password_hash = generate_password_hash('123456')

            cursor.execute("""
                INSERT INTO Users (username, password_hash, real_name, role, status)
                VALUES (%s, %s, %s, %s, '正常')
            """, (username, password_hash, real_name, role))
            new_user_id = cursor.lastrowid

            if role == 'teacher':
                # 工号沿用用户名
                cursor.execute("""
                    INSERT INTO Teachers
                        (user_id, teacher_no, real_name, phone, gender, department_id, title)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (new_user_id, username, real_name, phone, gender, department_id, title))
            elif role == 'student':
                # 学号沿用用户名
                cursor.execute("""
                    INSERT INTO Students
                        (user_id, student_no, real_name, phone, gender,
                         department_id, major_id, class_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (new_user_id, username, real_name, phone, gender,
                      department_id, major_id, class_id))

        return success_response(message="操作成功")


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@role_required('admin')
def delete_user(user_id):
    """删除用户（级联删除对应的 Teachers/Students 记录）"""
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("SELECT role FROM Users WHERE user_id=%s", (user_id,))
        row = cursor.fetchone()
        if not row:
            return error_response(404, "用户不存在")
        if row['role'] == 'admin':
            return error_response(400, "管理员账号不可删除")

        # 教师若已有开课班，禁止删除（避免级联清空开课/选课/成绩数据）
        if row['role'] == 'teacher':
            cursor.execute("""
                SELECT COUNT(*) AS cnt
                FROM CourseOfferings co
                JOIN Teachers t ON co.teacher_id = t.teacher_id
                WHERE t.user_id = %s
            """, (user_id,))
            if cursor.fetchone()['cnt'] > 0:
                return error_response(400, "该教师已有开课班，请先取消其开课后再删除")

        # 删除 Users，外键 ON DELETE CASCADE 会自动清理 Teachers/Students
        cursor.execute("DELETE FROM Users WHERE user_id=%s", (user_id,))
        return success_response(message="删除成功")


@admin_bp.route('/terms', methods=['GET'])
@role_required('admin')
def get_terms():
    """获取学年学期列表"""
    with get_db_cursor(commit=False) as cursor:
        sql = """
        SELECT ay.academic_year_name,
               JSON_ARRAYAGG(
                   JSON_OBJECT(
                       'term_id', t.term_id,
                       'term_no', t.term_no,
                       'term_name', t.term_name,
                       'start_date', DATE_FORMAT(t.start_date, '%Y-%m-%d'),
                       'end_date', DATE_FORMAT(t.end_date, '%Y-%m-%d'),
                       'is_current', t.is_current
                   )
               ) as terms
        FROM AcademicYears ay
        JOIN Terms t ON ay.academic_year_id = t.academic_year_id
        GROUP BY ay.academic_year_id
        ORDER BY ay.academic_year_id DESC
        """
        cursor.execute(sql)
        result = cursor.fetchall()

        # 解析 JSON
        for row in result:
            import json
            row['terms'] = json.loads(row['terms'])

        return success_response(result)


@admin_bp.route('/terms/<int:term_id>/set-current', methods=['PUT'])
@role_required('admin')
def set_current_term(term_id):
    """将指定学期设为当前学期（互斥：其余学期自动取消当前标记）"""
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("SELECT term_name FROM Terms WHERE term_id=%s", (term_id,))
        row = cursor.fetchone()
        if not row:
            return error_response(404, "学期不存在")

        # 一条语句完成互斥：匹配的学期置 1，其余置 0
        cursor.execute("UPDATE Terms SET is_current = (term_id=%s)", (term_id,))
        return success_response(message=f"已将「{row['term_name']}」设为当前学期")


@admin_bp.route('/business-windows', methods=['GET'])
@role_required('admin')
def get_business_windows():
    """获取业务时间窗口"""
    with get_db_cursor(commit=False) as cursor:
        sql = """
        SELECT bw.window_id, bw.term_id, t.term_name, bw.window_type,
               DATE_FORMAT(bw.start_time, '%Y-%m-%d %H:%i:%s') AS start_time,
               DATE_FORMAT(bw.end_time,   '%Y-%m-%d %H:%i:%s') AS end_time,
               CASE
                   WHEN NOW() < bw.start_time THEN '未开始'
                   WHEN NOW() > bw.end_time THEN '已结束'
                   ELSE '进行中'
               END as status
        FROM BusinessWindows bw
        JOIN Terms t ON bw.term_id = t.term_id
        ORDER BY bw.start_time DESC
        """
        cursor.execute(sql)
        windows = cursor.fetchall()

        return success_response(windows)


WINDOW_TYPES = ('选课', '退课', '成绩录入', '成绩公布')


@admin_bp.route('/business-windows/<int:window_id>', methods=['PUT'])
@role_required('admin')
def update_business_window(window_id):
    """修改业务时间窗口的业务类型与开始/结束时间"""
    data = request.get_json() or {}
    window_type = (data.get('window_type') or '').strip()
    start_time = (data.get('start_time') or '').strip()
    end_time = (data.get('end_time') or '').strip()

    if window_type not in WINDOW_TYPES:
        return error_response(400, f"业务类型不合法（应为：{'/'.join(WINDOW_TYPES)}）")
    if not start_time or not end_time:
        return error_response(400, "请填写开始时间与结束时间")
    try:
        st = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        et = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return error_response(400, "时间格式不正确（应为 YYYY-MM-DD HH:MM:SS）")
    if st >= et:
        return error_response(400, "开始时间必须早于结束时间")

    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "SELECT term_id FROM BusinessWindows WHERE window_id=%s", (window_id,),
        )
        row = cursor.fetchone()
        if not row:
            return error_response(404, "业务时间窗口不存在")

        # 同一学期下同类型窗口不可重复，避免业务逻辑匹配到多条
        cursor.execute(
            "SELECT window_id FROM BusinessWindows "
            "WHERE term_id=%s AND window_type=%s AND window_id<>%s",
            (row['term_id'], window_type, window_id),
        )
        if cursor.fetchone():
            return error_response(400, f"该学期已存在「{window_type}」窗口，不能重复")

        cursor.execute(
            "UPDATE BusinessWindows SET window_type=%s, start_time=%s, end_time=%s "
            "WHERE window_id=%s",
            (window_type, start_time, end_time, window_id),
        )
        return success_response(message="业务时间窗口已更新")


@admin_bp.route('/courses', methods=['GET'])
@role_required('admin')
def get_courses():
    """获取课程库列表"""
    with get_db_cursor(commit=False) as cursor:
        sql = """
        SELECT course_id, course_code, course_name, credits, hours,
               course_type, assessment_type, allow_retake, is_enabled
        FROM Courses
        ORDER BY course_id
        """
        cursor.execute(sql)
        courses = cursor.fetchall()

        return success_response(courses)


@admin_bp.route('/courses', methods=['POST'])
@role_required('admin')
def create_or_update_course():
    """新增或编辑课程"""
    data = request.get_json()
    course_id = data.get('course_id')
    course_code = (data.get('course_code') or '').strip()
    course_name = (data.get('course_name') or '').strip()
    credits = data.get('credits')
    hours = data.get('hours')
    course_type = data.get('course_type')
    assessment_type = data.get('assessment_type', '考试')
    allow_retake = bool(data.get('allow_retake', True))
    is_enabled = bool(data.get('is_enabled', True))

    if not all([course_code, course_name, credits, hours, course_type]):
        return error_response(400, "请填写完整的课程信息")

    with get_db_cursor(commit=True) as cursor:
        try:
            if course_id:
                # 编辑
                cursor.execute("""
                    UPDATE Courses
                    SET course_code=%s, course_name=%s, credits=%s, hours=%s,
                        course_type=%s, assessment_type=%s, allow_retake=%s, is_enabled=%s
                    WHERE course_id=%s
                """, (course_code, course_name, credits, hours, course_type,
                      assessment_type, allow_retake, is_enabled, course_id))
            else:
                # 新增
                cursor.execute("""
                    INSERT INTO Courses
                        (course_code, course_name, credits, hours,
                         course_type, assessment_type, allow_retake, is_enabled)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (course_code, course_name, credits, hours, course_type,
                      assessment_type, allow_retake, is_enabled))
            return success_response(message="操作成功")
        except pymysql.err.IntegrityError:
            return error_response(400, f"课程号 {course_code} 已存在")


@admin_bp.route('/courses/<int:course_id>/toggle', methods=['POST'])
@role_required('admin')
def toggle_course_enabled(course_id):
    """启用/停用课程"""
    data = request.get_json() or {}
    is_enabled = bool(data.get('is_enabled'))

    with get_db_cursor(commit=True) as cursor:
        cursor.execute("SELECT course_code FROM Courses WHERE course_id=%s", (course_id,))
        row = cursor.fetchone()
        if not row:
            return error_response(404, "课程不存在")

        cursor.execute(
            "UPDATE Courses SET is_enabled=%s WHERE course_id=%s",
            (is_enabled, course_id),
        )

        # 写入审计日志，便于追溯启停操作
        cursor.execute("""
            INSERT INTO AuditLogs (operator, operation_type, target_type, target_id, reason)
            VALUES ('admin', %s, '课程', %s, %s)
        """, ('启用课程' if is_enabled else '停用课程', course_id,
              f"管理员{'启用' if is_enabled else '停用'}课程 {row['course_code']}"))

        return success_response(message="课程已启用" if is_enabled else "课程已停用")


@admin_bp.route('/classrooms', methods=['GET'])
@role_required('admin')
def get_classrooms():
    """获取教室资源"""
    with get_db_cursor(commit=False) as cursor:
        sql = """
        SELECT classroom_id, building, room_no, capacity, status
        FROM Classrooms
        ORDER BY building, room_no
        """
        cursor.execute(sql)
        classrooms = cursor.fetchall()

        return success_response(classrooms)


@admin_bp.route('/classrooms', methods=['POST'])
@role_required('admin')
def create_or_update_classroom():
    """新增或编辑教室"""
    data = request.get_json() or {}
    classroom_id = data.get('classroom_id')
    building = (data.get('building') or '').strip()
    room_no = (data.get('room_no') or '').strip()
    status = data.get('status') or '可用'
    try:
        capacity = int(data.get('capacity'))
    except (TypeError, ValueError):
        return error_response(400, "容量必须为整数")

    if not building or not room_no:
        return error_response(400, "请填写教学楼与教室号")
    if capacity < 1:
        return error_response(400, "容量必须大于 0")
    if status not in ('可用', '维修中', '停用'):
        return error_response(400, "教室状态不合法")

    with get_db_cursor(commit=True) as cursor:
        # 教学楼+教室号查重（排除自身），对应唯一约束 uk_building_room
        cursor.execute(
            "SELECT classroom_id FROM Classrooms "
            "WHERE building=%s AND room_no=%s AND classroom_id<>%s",
            (building, room_no, classroom_id or 0),
        )
        if cursor.fetchone():
            return error_response(400, f"教室 {building}{room_no} 已存在")

        if classroom_id:
            cursor.execute(
                "UPDATE Classrooms SET building=%s, room_no=%s, capacity=%s, status=%s "
                "WHERE classroom_id=%s",
                (building, room_no, capacity, status, classroom_id),
            )
        else:
            cursor.execute(
                "INSERT INTO Classrooms (building, room_no, capacity, status) "
                "VALUES (%s, %s, %s, %s)",
                (building, room_no, capacity, status),
            )
        return success_response(message="操作成功")


@admin_bp.route('/classrooms/<int:classroom_id>', methods=['DELETE'])
@role_required('admin')
def delete_classroom(classroom_id):
    """删除教室——仍被排课引用时禁止删除"""
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "SELECT COUNT(*) AS c FROM ClassSchedules WHERE classroom_id=%s",
            (classroom_id,),
        )
        used = cursor.fetchone()['c']
        if used:
            return error_response(400, f"该教室仍被 {used} 条排课使用，无法删除")

        cursor.execute("DELETE FROM Classrooms WHERE classroom_id=%s", (classroom_id,))
        return success_response(message="删除成功")


@admin_bp.route('/offerings', methods=['GET'])
@role_required('admin')
def get_offerings():
    """获取开课管理列表"""
    with get_db_cursor(commit=True) as cursor:
        # 惰性同步：选课窗口已结束的「开放选课」自动关闭
        sync_offering_status_by_window(cursor)
        sql = """
        SELECT
            co.offering_id, c.course_name, t.real_name as teacher_name,
            term.term_name, co.teaching_class_name,
            co.capacity, co.selected_count_cached as selected_count,
            co.min_enrollment, co.is_retake_class, co.status,
            ew.enroll_end,
            CASE
                WHEN co.status = '已结课' THEN '已结课'
                WHEN ew.enroll_end IS NOT NULL AND NOW() > ew.enroll_end THEN '选课已截止'
                ELSE '可操作'
            END AS term_phase,
            (co.status <> '已结课'
             AND (ew.enroll_end IS NULL OR NOW() <= ew.enroll_end)) AS can_operate,
            GROUP_CONCAT(
                CONCAT('周', cs.weekday, ' ', cs.start_section, '-', cs.end_section,
                       '节[', cs.week_start, '-', cs.week_end, '周]')
                ORDER BY cs.weekday, cs.start_section SEPARATOR ' / '
            ) as schedule_text
        FROM CourseOfferings co
        JOIN Courses c ON co.course_id = c.course_id
        JOIN Teachers t ON co.teacher_id = t.teacher_id
        JOIN Terms term ON co.term_id = term.term_id
        LEFT JOIN (
            SELECT term_id, MAX(end_time) AS enroll_end
            FROM BusinessWindows WHERE window_type = '选课'
            GROUP BY term_id
        ) ew ON ew.term_id = co.term_id
        LEFT JOIN ClassSchedules cs ON co.offering_id = cs.offering_id
        GROUP BY co.offering_id, ew.enroll_end
        ORDER BY term.term_id DESC, co.offering_id
        """
        cursor.execute(sql)
        offerings = cursor.fetchall()

        return success_response(offerings)


@admin_bp.route('/departments', methods=['GET'])
@role_required('admin')
def get_departments():
    """获取学院（院系）列表，附带专业/教师/学生数量便于管理"""
    with get_db_cursor(commit=False) as cursor:
        cursor.execute("""
            SELECT d.department_id, d.department_name, d.created_at,
                   (SELECT COUNT(*) FROM Majors   m WHERE m.department_id = d.department_id) AS major_count,
                   (SELECT COUNT(*) FROM Teachers  t WHERE t.department_id = d.department_id) AS teacher_count,
                   (SELECT COUNT(*) FROM Students  s WHERE s.department_id = d.department_id) AS student_count
            FROM Departments d
            ORDER BY d.department_id
        """)
        return success_response(cursor.fetchall())


@admin_bp.route('/departments', methods=['POST'])
@role_required('admin')
def create_or_update_department():
    """新增或编辑学院（院系）"""
    data = request.get_json()
    department_id = data.get('department_id')
    department_name = (data.get('department_name') or '').strip()

    if not department_name:
        return error_response(400, "请填写学院名称")

    with get_db_cursor(commit=True) as cursor:
        # 同名查重（排除自身），避免出现重复学院
        cursor.execute(
            "SELECT department_id FROM Departments WHERE department_name=%s AND department_id<>%s",
            (department_name, department_id or 0),
        )
        if cursor.fetchone():
            return error_response(400, f"学院 {department_name} 已存在")

        if department_id:
            cursor.execute(
                "UPDATE Departments SET department_name=%s WHERE department_id=%s",
                (department_name, department_id),
            )
        else:
            cursor.execute(
                "INSERT INTO Departments (department_name) VALUES (%s)",
                (department_name,),
            )
        return success_response(message="操作成功")


@admin_bp.route('/departments/<int:department_id>', methods=['DELETE'])
@role_required('admin')
def delete_department(department_id):
    """删除学院（院系）——存在关联的专业/教师/学生时禁止删除"""
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("SELECT COUNT(*) AS c FROM Majors   WHERE department_id=%s", (department_id,))
        major_count = cursor.fetchone()['c']
        cursor.execute("SELECT COUNT(*) AS c FROM Teachers WHERE department_id=%s", (department_id,))
        teacher_count = cursor.fetchone()['c']
        cursor.execute("SELECT COUNT(*) AS c FROM Students WHERE department_id=%s", (department_id,))
        student_count = cursor.fetchone()['c']

        if major_count or teacher_count or student_count:
            return error_response(
                400,
                f"该学院下仍有 {major_count} 个专业、{teacher_count} 名教师、{student_count} 名学生，无法删除",
            )

        cursor.execute("DELETE FROM Departments WHERE department_id=%s", (department_id,))
        return success_response(message="删除成功")


@admin_bp.route('/majors', methods=['GET'])
@role_required('admin')
def get_majors():
    """获取专业列表（含所属院系与班级/学生数量，便于级联筛选与管理）"""
    with get_db_cursor(commit=False) as cursor:
        cursor.execute("""
            SELECT m.major_id, m.major_name, m.department_id,
                   (SELECT COUNT(*) FROM Classes  c WHERE c.major_id = m.major_id) AS class_count,
                   (SELECT COUNT(*) FROM Students s WHERE s.major_id = m.major_id) AS student_count
            FROM Majors m ORDER BY m.major_id
        """)
        return success_response(cursor.fetchall())


@admin_bp.route('/majors', methods=['POST'])
@role_required('admin')
def create_or_update_major():
    """新增或编辑专业"""
    data = request.get_json() or {}
    major_id = data.get('major_id')
    major_name = (data.get('major_name') or '').strip()
    department_id = data.get('department_id')

    if not major_name:
        return error_response(400, "请填写专业名称")
    if not department_id:
        return error_response(400, "请选择所属学院")

    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "SELECT department_id FROM Departments WHERE department_id=%s", (department_id,),
        )
        if not cursor.fetchone():
            return error_response(400, "所属学院不存在")

        # 同一学院下专业名查重（排除自身）
        cursor.execute(
            "SELECT major_id FROM Majors "
            "WHERE major_name=%s AND department_id=%s AND major_id<>%s",
            (major_name, department_id, major_id or 0),
        )
        if cursor.fetchone():
            return error_response(400, f"该学院下已存在专业 {major_name}")

        if major_id:
            cursor.execute(
                "UPDATE Majors SET major_name=%s, department_id=%s WHERE major_id=%s",
                (major_name, department_id, major_id),
            )
        else:
            cursor.execute(
                "INSERT INTO Majors (major_name, department_id) VALUES (%s, %s)",
                (major_name, department_id),
            )
        return success_response(message="操作成功")


@admin_bp.route('/majors/<int:major_id>', methods=['DELETE'])
@role_required('admin')
def delete_major(major_id):
    """删除专业——仍有班级/学生时禁止删除"""
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("SELECT COUNT(*) AS c FROM Classes  WHERE major_id=%s", (major_id,))
        class_count = cursor.fetchone()['c']
        cursor.execute("SELECT COUNT(*) AS c FROM Students WHERE major_id=%s", (major_id,))
        student_count = cursor.fetchone()['c']

        if class_count or student_count:
            return error_response(
                400,
                f"该专业下仍有 {class_count} 个班级、{student_count} 名学生，无法删除",
            )

        cursor.execute("DELETE FROM Majors WHERE major_id=%s", (major_id,))
        return success_response(message="删除成功")


@admin_bp.route('/classes', methods=['GET'])
@role_required('admin')
def get_classes():
    """获取班级列表（含所属专业/学院与学生数量，便于级联筛选与管理）"""
    with get_db_cursor(commit=False) as cursor:
        cursor.execute("""
            SELECT c.class_id, c.class_name, c.major_id, c.grade_year,
                   m.major_name, m.department_id, d.department_name,
                   (SELECT COUNT(*) FROM Students s WHERE s.class_id = c.class_id) AS student_count
            FROM Classes c
            LEFT JOIN Majors m ON c.major_id = m.major_id
            LEFT JOIN Departments d ON m.department_id = d.department_id
            ORDER BY c.class_id
        """)
        return success_response(cursor.fetchall())


@admin_bp.route('/classes', methods=['POST'])
@role_required('admin')
def create_or_update_class():
    """新增或编辑班级"""
    data = request.get_json() or {}
    class_id = data.get('class_id')
    class_name = (data.get('class_name') or '').strip()
    major_id = data.get('major_id')
    grade_year = data.get('grade_year')

    if not class_name:
        return error_response(400, "请填写班级名称")
    if not major_id:
        return error_response(400, "请选择所属专业")
    try:
        grade_year = int(grade_year) if grade_year not in (None, '') else None
    except (TypeError, ValueError):
        return error_response(400, "年级必须为整数")

    with get_db_cursor(commit=True) as cursor:
        cursor.execute("SELECT major_id FROM Majors WHERE major_id=%s", (major_id,))
        if not cursor.fetchone():
            return error_response(400, "所属专业不存在")

        # 同一专业下班级名查重（排除自身）
        cursor.execute(
            "SELECT class_id FROM Classes "
            "WHERE class_name=%s AND major_id=%s AND class_id<>%s",
            (class_name, major_id, class_id or 0),
        )
        if cursor.fetchone():
            return error_response(400, f"该专业下已存在班级 {class_name}")

        if class_id:
            cursor.execute(
                "UPDATE Classes SET class_name=%s, major_id=%s, grade_year=%s WHERE class_id=%s",
                (class_name, major_id, grade_year, class_id),
            )
        else:
            cursor.execute(
                "INSERT INTO Classes (class_name, major_id, grade_year) VALUES (%s, %s, %s)",
                (class_name, major_id, grade_year),
            )
        return success_response(message="操作成功")


@admin_bp.route('/classes/<int:class_id>', methods=['DELETE'])
@role_required('admin')
def delete_class(class_id):
    """删除班级——仍有学生时禁止删除"""
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("SELECT COUNT(*) AS c FROM Students WHERE class_id=%s", (class_id,))
        student_count = cursor.fetchone()['c']
        if student_count:
            return error_response(400, f"该班级下仍有 {student_count} 名学生，无法删除")

        cursor.execute("DELETE FROM Classes WHERE class_id=%s", (class_id,))
        return success_response(message="删除成功")


@admin_bp.route('/teachers', methods=['GET'])
@role_required('admin')
def get_teachers():
    """获取教师列表（用于下拉选择）"""
    with get_db_cursor(commit=False) as cursor:
        cursor.execute("""
            SELECT t.teacher_id, t.real_name, t.teacher_no, d.department_name
            FROM Teachers t
            LEFT JOIN Departments d ON t.department_id = d.department_id
            ORDER BY t.teacher_id
        """)
        return success_response(cursor.fetchall())


@admin_bp.route('/offerings', methods=['POST'])
@role_required('admin')
def create_offering():
    """新增开课"""
    data = request.get_json()
    course_id = data.get('course_id')
    teacher_id = data.get('teacher_id')
    term_id = data.get('term_id')
    teaching_class_name = data.get('teaching_class_name', '').strip()
    capacity = data.get('capacity')
    min_enrollment = data.get('min_enrollment', 10)
    is_retake_class = data.get('is_retake_class', False)
    # 上课时间（可多段），每段：weekday/start_section/end_section/week_start/week_end/classroom_id
    schedules = data.get('schedules') or []

    if not all([course_id, teacher_id, term_id, teaching_class_name, capacity]):
        return error_response(400, "请填写完整信息")

    # 先校验排课明细，避免插入一半再回滚
    cleaned_schedules = []
    for idx, s in enumerate(schedules, start=1):
        try:
            weekday = int(s.get('weekday'))
            start_section = int(s.get('start_section'))
            end_section = int(s.get('end_section'))
            week_start = int(s.get('week_start', 1))
            week_end = int(s.get('week_end', 18))
        except (TypeError, ValueError):
            return error_response(400, f"第 {idx} 个上课时间填写不完整")
        classroom_id = s.get('classroom_id') or None

        if not (1 <= weekday <= 7):
            return error_response(400, f"第 {idx} 个上课时间的星期不合法")
        if not (1 <= start_section <= end_section <= 10):
            return error_response(400, f"第 {idx} 个上课时间的节次不合法")
        if not (1 <= week_start <= week_end <= 30):
            return error_response(400, f"第 {idx} 个上课时间的周次不合法")
        cleaned_schedules.append(
            (weekday, start_section, end_section, week_start, week_end, classroom_id)
        )

    with get_db_cursor(commit=True) as cursor:
        # 已停用的课程不允许新开课
        cursor.execute(
            "SELECT course_name, is_enabled FROM Courses WHERE course_id=%s",
            (course_id,),
        )
        course = cursor.fetchone()
        if not course:
            return error_response(404, "课程不存在")
        if not course['is_enabled']:
            return error_response(400, f"课程「{course['course_name']}」已停用，不能开课")

        cursor.execute("""
            INSERT INTO CourseOfferings
                (course_id, teacher_id, term_id, teaching_class_name,
                 capacity, min_enrollment, is_retake_class, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, '开放选课')
        """, (course_id, teacher_id, term_id, teaching_class_name,
              capacity, min_enrollment, is_retake_class))
        offering_id = cursor.lastrowid

        # 写入排课明细
        for (weekday, start_section, end_section,
             week_start, week_end, classroom_id) in cleaned_schedules:
            cursor.execute("""
                INSERT INTO ClassSchedules
                    (offering_id, classroom_id, weekday,
                     start_section, end_section, week_start, week_end)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (offering_id, classroom_id, weekday,
                  start_section, end_section, week_start, week_end))

        return success_response(message="开课班创建成功")


@admin_bp.route('/offerings/<int:offering_id>/toggle-enrollment', methods=['POST'])
@role_required('admin')
def toggle_offering_enrollment(offering_id):
    """开放/关闭开课班的选课"""
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("""
            SELECT co.status, co.teaching_class_name
            FROM CourseOfferings co WHERE co.offering_id=%s
        """, (offering_id,))
        row = cursor.fetchone()
        if not row:
            return error_response(404, "开课班不存在")
        if row['status'] not in ('开放选课', '关闭选课'):
            return error_response(400, f"当前状态为「{row['status']}」，不能切换选课开关")

        new_status = '关闭选课' if row['status'] == '开放选课' else '开放选课'
        cursor.execute(
            "UPDATE CourseOfferings SET status=%s WHERE offering_id=%s",
            (new_status, offering_id),
        )

        # 写入审计日志，便于追溯开放/关闭操作
        cursor.execute("""
            INSERT INTO AuditLogs (operator, operation_type, target_type, target_id, reason)
            VALUES ('admin', %s, '开课班', %s, %s)
        """, ('开放选课' if new_status == '开放选课' else '关闭选课', offering_id,
              f"管理员{'开放' if new_status == '开放选课' else '关闭'}教学班 {row['teaching_class_name']} 的选课"))

        return success_response(
            {'status': new_status},
            message="已开放该课程选课" if new_status == '开放选课' else "已关闭该课程选课",
        )


@admin_bp.route('/offerings/<int:offering_id>/cancel', methods=['POST'])
@role_required('admin')
def cancel_offering(offering_id):
    """取消开课班（仅当选课人数低于最低开课人数时允许）"""
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("""
            SELECT status, teaching_class_name,
                   selected_count_cached, min_enrollment
            FROM CourseOfferings WHERE offering_id=%s
        """, (offering_id,))
        row = cursor.fetchone()
        if not row:
            return error_response(404, "开课班不存在")
        if row['status'] == '已取消':
            return error_response(400, "该开课班已取消")
        # 服务端再次校验，防止绕过前端按钮的 disabled 限制
        if row['selected_count_cached'] >= row['min_enrollment']:
            return error_response(
                400,
                f"选课人数已达最低开课人数（{row['min_enrollment']}人），不能取消",
            )

        cursor.execute(
            "UPDATE CourseOfferings SET status='已取消' WHERE offering_id=%s",
            (offering_id,),
        )

        # 写入审计日志
        cursor.execute("""
            INSERT INTO AuditLogs (operator, operation_type, target_type, target_id, reason)
            VALUES ('admin', '取消开课', '开课班', %s, %s)
        """, (offering_id,
              f"管理员取消教学班 {row['teaching_class_name']}（选课{row['selected_count_cached']}人 < 最低{row['min_enrollment']}人）"))

        return success_response(message="课程已取消")


@admin_bp.route('/offerings/<int:offering_id>/restore', methods=['POST'])
@role_required('admin')
def restore_offering(offering_id):
    """恢复已取消的开课班（恢复到「关闭选课」，由管理员确认后再手动开放）"""
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("""
            SELECT status, teaching_class_name
            FROM CourseOfferings WHERE offering_id=%s
        """, (offering_id,))
        row = cursor.fetchone()
        if not row:
            return error_response(404, "开课班不存在")
        if row['status'] != '已取消':
            return error_response(400, f"当前状态为「{row['status']}」，无需恢复")

        cursor.execute(
            "UPDATE CourseOfferings SET status='关闭选课' WHERE offering_id=%s",
            (offering_id,),
        )

        # 写入审计日志
        cursor.execute("""
            INSERT INTO AuditLogs (operator, operation_type, target_type, target_id, reason)
            VALUES ('admin', '恢复开课', '开课班', %s, %s)
        """, (offering_id,
              f"管理员恢复教学班 {row['teaching_class_name']}（恢复为关闭选课）"))

        return success_response(
            {'status': '关闭选课'},
            message="开课班已恢复为关闭选课状态",
        )


@admin_bp.route('/offerings/<int:offering_id>', methods=['DELETE'])
@role_required('admin')
def delete_offering(offering_id):
    """删除开课班（仅限选课窗口未截止的开课班；级联清除排课与选课记录）"""
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("""
            SELECT co.status, co.teaching_class_name,
                   (SELECT MAX(bw.end_time) FROM BusinessWindows bw
                    WHERE bw.term_id = co.term_id AND bw.window_type = '选课') AS enroll_end
            FROM CourseOfferings co
            WHERE co.offering_id=%s
        """, (offering_id,))
        row = cursor.fetchone()
        if not row:
            return error_response(404, "开课班不存在")

        # 服务端再次判定选课窗口，防止绕过前端限制
        if row['status'] == '已结课':
            return error_response(400, "课程已结课，不能删除")
        if row['enroll_end'] is not None and datetime.now() > row['enroll_end']:
            return error_response(400, "选课已截止，该开课班不能删除")

        # ClassSchedules / Enrollments / Grades 均为 ON DELETE CASCADE，随之自动清除
        cursor.execute("DELETE FROM CourseOfferings WHERE offering_id=%s", (offering_id,))

        # 写入审计日志
        cursor.execute("""
            INSERT INTO AuditLogs (operator, operation_type, target_type, target_id, reason)
            VALUES ('admin', '删除开课', '开课班', %s, %s)
        """, (offering_id,
              f"管理员删除教学班 {row['teaching_class_name']}（选课未截止）"))

        return success_response(message="开课班已删除")


@admin_bp.route('/offerings/<int:offering_id>', methods=['PUT'])
@role_required('admin')
def update_offering(offering_id):
    """编辑开课班（仅容量与最低开课人数）"""
    data = request.get_json() or {}
    try:
        capacity = int(data.get('capacity'))
        min_enrollment = int(data.get('min_enrollment'))
    except (TypeError, ValueError):
        return error_response(400, "容量与最低开课人数必须为整数")

    if capacity < 1 or min_enrollment < 1:
        return error_response(400, "容量与最低开课人数必须大于 0")
    if min_enrollment > capacity:
        return error_response(400, "最低开课人数不能大于容量")

    with get_db_cursor(commit=True) as cursor:
        cursor.execute("""
            SELECT status, teaching_class_name,
                   selected_count_cached, capacity, min_enrollment
            FROM CourseOfferings WHERE offering_id=%s
        """, (offering_id,))
        row = cursor.fetchone()
        if not row:
            return error_response(404, "开课班不存在")
        # 仅开放/关闭选课状态允许编辑
        if row['status'] not in ('开放选课', '关闭选课'):
            return error_response(400, f"当前状态为「{row['status']}」，不能编辑")
        # 容量不能小于已选人数
        if capacity < row['selected_count_cached']:
            return error_response(
                400,
                f"容量不能小于已选人数（已选 {row['selected_count_cached']} 人）",
            )

        cursor.execute("""
            UPDATE CourseOfferings SET capacity=%s, min_enrollment=%s
            WHERE offering_id=%s
        """, (capacity, min_enrollment, offering_id))

        # 写入审计日志，记录调整前后的值
        cursor.execute("""
            INSERT INTO AuditLogs (operator, operation_type, target_type, target_id, reason)
            VALUES ('admin', '编辑开课', '开课班', %s, %s)
        """, (offering_id,
              f"管理员编辑教学班 {row['teaching_class_name']}："
              f"容量 {row['capacity']}→{capacity}，最低人数 {row['min_enrollment']}→{min_enrollment}"))

        return success_response(message="开课班已更新")


@admin_bp.route('/approvals', methods=['GET'])
@role_required('admin')
def get_approvals():
    """获取待审批列表"""
    with get_db_cursor(commit=False) as cursor:
        sql = """
        SELECT
            tr.request_id, t.real_name as teacher_name, tr.request_type,
            COALESCE(tr.course_name, c.course_name) AS course_name,
            COALESCE(rterm.term_name, term.term_name) AS term_name,
            tr.content,
            tr.reason, tr.status, tr.created_at,
            '无冲突' as conflict_check_result
        FROM TeachingRequests tr
        LEFT JOIN Teachers t ON tr.teacher_id = t.teacher_id
        LEFT JOIN CourseOfferings co ON tr.offering_id = co.offering_id
        LEFT JOIN Courses c ON co.course_id = c.course_id
        LEFT JOIN Terms term ON co.term_id = term.term_id
        LEFT JOIN Terms rterm ON tr.term_id = rterm.term_id
        WHERE tr.status = '待审批'
        ORDER BY tr.created_at
        """
        cursor.execute(sql)
        approvals = cursor.fetchall()

        return success_response(approvals)


@admin_bp.route('/approve', methods=['POST'])
@role_required('admin')
def approve_request():
    """审批操作"""
    data = request.get_json()
    request_id = data.get('request_id')
    result = data.get('result')  # '通过' 或 '驳回'
    comment = data.get('comment', '')

    if not all([request_id, result]):
        return error_response(400, "参数不完整")

    with get_db_cursor(commit=True) as cursor:
        status = '已通过' if result == '通过' else '已驳回'

        cursor.execute("""
            UPDATE TeachingRequests
            SET status = %s, admin_comment = %s, processed_at = NOW()
            WHERE request_id = %s
        """, (status, comment, request_id))

        # 如果通过，根据申请类型执行相应操作（这里简化）
        if status == '已通过':
            # TODO: 根据 request_type 执行对应操作
            pass

        return success_response(message="审批成功")


@admin_bp.route('/grade-publish', methods=['GET'])
@role_required('admin')
def get_grade_publish():
    """获取待发布成绩列表"""
    with get_db_cursor(commit=False) as cursor:
        sql = """
        SELECT
            co.offering_id, c.course_name, t.real_name as teacher_name,
            term.term_name,
            COUNT(g.grade_id) as submitted_count,
            COUNT(e.enrollment_id) as total_count,
            '已提交' as score_status,
            (COUNT(g.grade_id) = COUNT(e.enrollment_id) AND COUNT(g.grade_id) > 0) as can_publish
        FROM CourseOfferings co
        JOIN Courses c ON co.course_id = c.course_id
        JOIN Teachers t ON co.teacher_id = t.teacher_id
        JOIN Terms term ON co.term_id = term.term_id
        LEFT JOIN Enrollments e ON co.offering_id = e.offering_id AND e.status = '已选'
        LEFT JOIN Grades g ON e.enrollment_id = g.enrollment_id AND g.score_status = '已提交'
        WHERE term.is_current = TRUE
        GROUP BY co.offering_id
        HAVING submitted_count > 0
        ORDER BY co.offering_id
        """
        cursor.execute(sql)
        offerings = cursor.fetchall()

        return success_response(offerings)


@admin_bp.route('/grade-detail/<int:offering_id>', methods=['GET'])
@role_required('admin')
def get_grade_detail(offering_id):
    """获取某开课班的学生成绩明细（供成绩发布页下拉查看）"""
    with get_db_cursor(commit=False) as cursor:
        sql = """
        SELECT
            e.enrollment_id, s.student_no, s.real_name,
            g.usual_score, g.experiment_score, g.final_score,
            g.total_score, g.score_status
        FROM Enrollments e
        JOIN Students s ON e.student_id = s.student_id
        LEFT JOIN Grades g ON e.enrollment_id = g.enrollment_id
        WHERE e.offering_id = %s AND e.status = '已选'
        ORDER BY s.student_no
        """
        cursor.execute(sql, (offering_id,))
        grades = cursor.fetchall()

        # 未录入成绩的统一显示为“未录入”
        for grade in grades:
            if not grade['score_status']:
                grade['score_status'] = '未录入'

        return success_response(grades)


@admin_bp.route('/grade/publish', methods=['POST'])
@role_required('admin')
def publish_grade():
    """发布成绩"""
    data = request.get_json()
    offering_id = data.get('offering_id')

    if not offering_id:
        return error_response(400, "开课班ID不能为空")

    with get_db_cursor(commit=True) as cursor:
        try:
            # 更新成绩状态为已发布
            cursor.execute("""
                UPDATE Grades g
                JOIN Enrollments e ON g.enrollment_id = e.enrollment_id
                SET g.score_status = '已发布'
                WHERE e.offering_id = %s AND g.score_status = '已提交'
            """, (offering_id,))

            # 创建重修记录（调用存储过程）
            try:
                cursor.callproc('sp_CreateRetakeRecords', (offering_id,))
            except:
                pass  # 存储过程可能不存在，忽略

            # 成绩发布即课程教学完成，自动结课（已取消的班不复活）
            cursor.execute("""
                UPDATE CourseOfferings SET status='已结课'
                WHERE offering_id=%s AND status <> '已取消'
            """, (offering_id,))

            # 写入审计日志
            cursor.execute("""
                INSERT INTO AuditLogs (operator, operation_type, target_type, target_id, reason)
                VALUES ('admin', '发布成绩', '开课班', %s, '管理员发布成绩，课程自动结课')
            """, (offering_id,))

            return success_response(message="成绩发布成功，课程已结课")
        except Exception as e:
            return error_response(500, f"发布失败: {str(e)}")


@admin_bp.route('/retake', methods=['GET'])
@role_required('admin')
def get_retake():
    """获取重修管理"""
    with get_db_cursor(commit=False) as cursor:
        sql = """
        SELECT
            c.course_name,
            COUNT(DISTINCT CASE WHEN r.status IN ('待重修', '重修中', '重修通过', '重修未通过') THEN r.retake_id END) as failed_count,
            COUNT(DISTINCT CASE WHEN r.status = '待重修' THEN r.retake_id END) as pending_count,
            COUNT(DISTINCT CASE WHEN r.status = '重修中' THEN r.retake_id END) as retaking_count,
            COUNT(DISTINCT CASE WHEN r.status = '重修通过' THEN r.retake_id END) as passed_count,
            MAX(CASE WHEN co.is_retake_class = TRUE THEN TRUE ELSE FALSE END) as has_retake_class
        FROM Courses c
        LEFT JOIN CourseOfferings co ON c.course_id = co.course_id
        LEFT JOIN Enrollments e ON co.offering_id = e.offering_id
        LEFT JOIN RetakeRecords r ON e.enrollment_id = r.source_enrollment_id
        GROUP BY c.course_id
        HAVING failed_count > 0
        ORDER BY failed_count DESC
        """
        cursor.execute(sql)
        retakes = cursor.fetchall()

        return success_response(retakes)


@admin_bp.route('/audit-logs', methods=['GET'])
@role_required('admin')
def get_audit_logs():
    """获取操作日志"""
    with get_db_cursor(commit=False) as cursor:
        sql = """
        SELECT log_id, operator, operation_type, target_type,
               target_id, reason, created_at
        FROM AuditLogs
        ORDER BY created_at DESC
        LIMIT 100
        """
        cursor.execute(sql)
        logs = cursor.fetchall()

        return success_response(logs)

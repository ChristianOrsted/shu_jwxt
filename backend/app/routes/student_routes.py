#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
学生端路由模块
"""
from flask import request
from app.routes import student_bp
from app.utils import success_response, error_response
from app.auth import role_required
from app.db import get_db_cursor
import pymysql


@student_bp.route('/profile', methods=['GET'])
@role_required('student')
def get_profile():
    """获取学生个人信息"""
    user = request.current_user

    with get_db_cursor(commit=False) as cursor:
        sql = """
        SELECT s.student_no, s.real_name, s.gender,
               d.department_name, m.major_name, c.class_name,
               s.grade_year, s.enroll_year, s.student_status,
               s.phone, s.email
        FROM Students s
        LEFT JOIN Departments d ON s.department_id = d.department_id
        LEFT JOIN Majors m ON s.major_id = m.major_id
        LEFT JOIN Classes c ON s.class_id = c.class_id
        WHERE s.user_id = %s
        """
        cursor.execute(sql, (user['user_id'],))
        profile = cursor.fetchone()

        if not profile:
            return error_response(404, "学生信息不存在")

        return success_response(profile)


@student_bp.route('/courses', methods=['GET'])
@role_required('student')
def get_courses():
    """获取可选课程列表"""
    user = request.current_user

    with get_db_cursor(commit=False) as cursor:
        # 获取学生ID
        cursor.execute("SELECT student_id FROM Students WHERE user_id = %s", (user['user_id'],))
        student = cursor.fetchone()
        if not student:
            return error_response(404, "学生信息不存在")

        student_id = student['student_id']

        # 获取当前学期
        cursor.execute("SELECT term_id FROM Terms WHERE is_current = TRUE")
        current_term = cursor.fetchone()
        if not current_term:
            return error_response(404, "未找到当前学期")

        term_id = current_term['term_id']

        # 获取可选课程列表
        sql = """
        SELECT
            co.offering_id, c.course_code, c.course_name,
            c.credits, c.hours, c.course_type,
            t.real_name as teacher_name,
            co.teaching_class_name,
            co.capacity, co.selected_count_cached as selected_count,
            co.is_retake_class, co.description,
            c.assessment_type,
            GROUP_CONCAT(
                CONCAT('周', cs.weekday, ' ', cs.start_section, '-', cs.end_section, '节')
                SEPARATOR ' / '
            ) as schedule_text,
            GROUP_CONCAT(DISTINCT CONCAT(cr.building, ' ', cr.room_no) SEPARATOR ', ') as location
        FROM CourseOfferings co
        JOIN Courses c ON co.course_id = c.course_id
        JOIN Teachers t ON co.teacher_id = t.teacher_id
        LEFT JOIN ClassSchedules cs ON co.offering_id = cs.offering_id
        LEFT JOIN Classrooms cr ON cs.classroom_id = cr.classroom_id
        WHERE co.term_id = %s AND co.status IN ('开放选课')
        GROUP BY co.offering_id
        """
        cursor.execute(sql, (term_id,))
        offerings = cursor.fetchall()

        # 为每个课程计算 select_status
        for offering in offerings:
            offering['select_status'] = calculate_select_status(
                cursor, student_id, offering['offering_id'],
                offering['course_code'], offering['selected_count'], offering['capacity']
            )

        return success_response(offerings)


def calculate_select_status(cursor, student_id, offering_id, course_code, selected_count, capacity):
    """计算选课状态"""
    # 检查是否已选
    cursor.execute("""
        SELECT status FROM Enrollments
        WHERE student_id = %s AND offering_id = %s
    """, (student_id, offering_id))
    enrollment = cursor.fetchone()

    if enrollment and enrollment['status'] == '已选':
        return 'selected'

    # 检查是否已满
    cursor.execute("""
        SELECT COUNT(*) as count FROM Enrollments
        WHERE offering_id = %s AND status IN ('已选', '已完成')
    """, (offering_id,))
    actual_count = cursor.fetchone()['count']

    if actual_count >= capacity:
        return 'full'

    # 检查是否已通过
    cursor.execute("""
        SELECT g.is_passed FROM Grades g
        JOIN Enrollments e ON g.enrollment_id = e.enrollment_id
        JOIN CourseOfferings co ON e.offering_id = co.offering_id
        JOIN Courses c ON co.course_id = c.course_id
        WHERE e.student_id = %s AND c.course_code = %s AND g.is_passed = TRUE
    """, (student_id, course_code))

    if cursor.fetchone():
        return 'passed'

    # 检查时间冲突（简化版）
    cursor.execute("""
        SELECT COUNT(*) as count FROM Enrollments e
        JOIN ClassSchedules cs1 ON e.offering_id = cs1.offering_id
        JOIN ClassSchedules cs2 ON cs2.offering_id = %s
        WHERE e.student_id = %s AND e.status = '已选'
        AND cs1.weekday = cs2.weekday
        AND cs1.start_section <= cs2.end_section
        AND cs1.end_section >= cs2.start_section
    """, (offering_id, student_id))

    if cursor.fetchone()['count'] > 0:
        return 'conflict'

    return 'available'


@student_bp.route('/enroll', methods=['POST'])
@role_required('student')
def enroll_course():
    """选课"""
    user = request.current_user
    data = request.get_json()
    offering_id = data.get('offering_id')

    if not offering_id:
        return error_response(400, "开课班ID不能为空")

    with get_db_cursor(commit=True) as cursor:
        # 获取学生ID
        cursor.execute("SELECT student_id FROM Students WHERE user_id = %s", (user['user_id'],))
        student = cursor.fetchone()
        if not student:
            return error_response(404, "学生信息不存在")

        try:
            # 调用存储过程
            cursor.callproc('sp_StudentSelectCourse', (student['student_id'], offering_id))
            return success_response(message="选课成功")
        except pymysql.Error as e:
            # 捕获存储过程抛出的错误
            error_msg = str(e.args[1]) if len(e.args) > 1 else "选课失败"
            return error_response(400, error_msg)


@student_bp.route('/enroll/<int:offering_id>', methods=['DELETE'])
@role_required('student')
def drop_course(offering_id):
    """退课"""
    user = request.current_user

    with get_db_cursor(commit=True) as cursor:
        # 获取学生ID
        cursor.execute("SELECT student_id FROM Students WHERE user_id = %s", (user['user_id'],))
        student = cursor.fetchone()
        if not student:
            return error_response(404, "学生信息不存在")

        try:
            # 调用存储过程
            cursor.callproc('sp_StudentDropCourse', (student['student_id'], offering_id))
            return success_response(message="退课成功")
        except pymysql.Error as e:
            error_msg = str(e.args[1]) if len(e.args) > 1 else "退课失败"
            return error_response(400, error_msg)


@student_bp.route('/my-courses', methods=['GET'])
@role_required('student')
def get_my_courses():
    """获取已选课程"""
    user = request.current_user

    with get_db_cursor(commit=False) as cursor:
        cursor.execute("SELECT student_id FROM Students WHERE user_id = %s", (user['user_id'],))
        student = cursor.fetchone()
        if not student:
            return error_response(404, "学生信息不存在")

        sql = """
        SELECT
            e.enrollment_id, e.offering_id,
            c.course_code, c.course_name, c.credits,
            t.real_name as teacher_name,
            e.is_retake, e.enroll_time, e.status,
            GROUP_CONCAT(
                CONCAT('周', cs.weekday, ' ', cs.start_section, '-', cs.end_section, '节')
                SEPARATOR ' / '
            ) as schedule_text,
            GROUP_CONCAT(DISTINCT CONCAT(cr.building, ' ', cr.room_no) SEPARATOR ', ') as location
        FROM Enrollments e
        JOIN CourseOfferings co ON e.offering_id = co.offering_id
        JOIN Courses c ON co.course_id = c.course_id
        JOIN Teachers t ON co.teacher_id = t.teacher_id
        JOIN Terms term ON co.term_id = term.term_id
        LEFT JOIN ClassSchedules cs ON co.offering_id = cs.offering_id
        LEFT JOIN Classrooms cr ON cs.classroom_id = cr.classroom_id
        WHERE e.student_id = %s AND term.is_current = TRUE
        GROUP BY e.enrollment_id
        ORDER BY e.enroll_time DESC
        """
        cursor.execute(sql, (student['student_id'],))
        courses = cursor.fetchall()

        # 计算是否可以退课
        for course in courses:
            course['can_drop'] = check_can_drop(cursor, course['enrollment_id'])

        return success_response(courses)


def check_can_drop(cursor, enrollment_id):
    """检查是否可以退课"""
    # 检查退课时间窗口
    cursor.execute("""
        SELECT bw.window_id FROM BusinessWindows bw
        JOIN Terms t ON bw.term_id = t.term_id
        WHERE t.is_current = TRUE
        AND bw.window_type = '退课'
        AND NOW() BETWEEN bw.start_time AND bw.end_time
    """)
    if not cursor.fetchone():
        return False

    # 检查是否已录成绩
    cursor.execute("""
        SELECT g.grade_id FROM Grades g
        WHERE g.enrollment_id = %s AND g.score_status NOT IN ('未录入')
    """, (enrollment_id,))
    if cursor.fetchone():
        return False

    return True


@student_bp.route('/timetable', methods=['GET'])
@role_required('student')
def get_timetable():
    """获取个人课表"""
    user = request.current_user

    with get_db_cursor(commit=False) as cursor:
        cursor.execute("SELECT student_id FROM Students WHERE user_id = %s", (user['user_id'],))
        student = cursor.fetchone()
        if not student:
            return error_response(404, "学生信息不存在")

        sql = """
        SELECT
            co.offering_id, c.course_name, t.real_name as teacher_name,
            CONCAT(cr.building, ' ', cr.room_no) as location,
            cs.weekday, cs.start_section, cs.end_section
        FROM Enrollments e
        JOIN CourseOfferings co ON e.offering_id = co.offering_id
        JOIN Courses c ON co.course_id = c.course_id
        JOIN Teachers t ON co.teacher_id = t.teacher_id
        JOIN Terms term ON co.term_id = term.term_id
        JOIN ClassSchedules cs ON co.offering_id = cs.offering_id
        LEFT JOIN Classrooms cr ON cs.classroom_id = cr.classroom_id
        WHERE e.student_id = %s AND term.is_current = TRUE AND e.status = '已选'
        ORDER BY cs.weekday, cs.start_section
        """
        cursor.execute(sql, (student['student_id'],))
        timetable = cursor.fetchall()

        return success_response(timetable)


@student_bp.route('/grades', methods=['GET'])
@role_required('student')
def get_grades():
    """获取成绩查询"""
    user = request.current_user

    with get_db_cursor(commit=False) as cursor:
        cursor.execute("SELECT student_id FROM Students WHERE user_id = %s", (user['user_id'],))
        student = cursor.fetchone()
        if not student:
            return error_response(404, "学生信息不存在")

        sql = """
        SELECT
            g.grade_id, term.term_name, c.course_name, c.credits,
            t.real_name as teacher_name,
            g.total_score, g.grade_point, g.is_passed,
            e.is_retake, g.included_in_average, g.score_status
        FROM Grades g
        JOIN Enrollments e ON g.enrollment_id = e.enrollment_id
        JOIN CourseOfferings co ON e.offering_id = co.offering_id
        JOIN Courses c ON co.course_id = c.course_id
        JOIN Teachers teach ON co.teacher_id = teach.teacher_id
        JOIN Terms term ON co.term_id = term.term_id
        WHERE e.student_id = %s AND g.score_status = '已发布'
        ORDER BY term.term_id DESC, c.course_name
        """
        cursor.execute(sql, (student['student_id'],))
        grades = cursor.fetchall()

        return success_response(grades)


@student_bp.route('/average-score', methods=['GET'])
@role_required('student')
def get_average_score():
    """获取平均成绩统计"""
    user = request.current_user

    with get_db_cursor(commit=False) as cursor:
        cursor.execute("SELECT student_id FROM Students WHERE user_id = %s", (user['user_id'],))
        student = cursor.fetchone()
        if not student:
            return error_response(404, "学生信息不存在")

        sql = """
        SELECT
            AVG(g.total_score) as simple_average,
            SUM(g.total_score * c.credits) / SUM(c.credits) as weighted_average,
            AVG(g.grade_point) as average_gpa,
            SUM(c.credits) as total_credits,
            SUM(CASE WHEN g.is_passed = TRUE THEN c.credits ELSE 0 END) as earned_credits
        FROM Grades g
        JOIN Enrollments e ON g.enrollment_id = e.enrollment_id
        JOIN CourseOfferings co ON e.offering_id = co.offering_id
        JOIN Courses c ON co.course_id = c.course_id
        WHERE e.student_id = %s
        AND g.score_status = '已发布'
        AND g.included_in_average = TRUE
        """
        cursor.execute(sql, (student['student_id'],))
        stats = cursor.fetchone()

        # 格式化结果
        result = {
            'simple_average': round(float(stats['simple_average'] or 0), 1),
            'weighted_average': round(float(stats['weighted_average'] or 0), 1),
            'average_gpa': round(float(stats['average_gpa'] or 0), 2),
            'total_credits': float(stats['total_credits'] or 0),
            'earned_credits': float(stats['earned_credits'] or 0)
        }

        return success_response(result)


@student_bp.route('/retake', methods=['GET'])
@role_required('student')
def get_retake():
    """获取挂科与重修状态"""
    user = request.current_user

    with get_db_cursor(commit=False) as cursor:
        cursor.execute("SELECT student_id FROM Students WHERE user_id = %s", (user['user_id'],))
        student = cursor.fetchone()
        if not student:
            return error_response(404, "学生信息不存在")

        sql = """
        SELECT
            r.retake_id, c.course_name,
            source_term.term_name as source_term,
            g.total_score as source_score, r.status,
            CASE
                WHEN r.retake_offering_id IS NOT NULL
                THEN CONCAT(c2.course_name, '-重修班（', current_term.term_name, '）')
                ELSE NULL
            END as current_offering
        FROM RetakeRecords r
        JOIN Enrollments e ON r.source_enrollment_id = e.enrollment_id
        JOIN CourseOfferings co ON e.offering_id = co.offering_id
        JOIN Courses c ON co.course_id = c.course_id
        JOIN Terms source_term ON co.term_id = source_term.term_id
        LEFT JOIN Grades g ON g.enrollment_id = e.enrollment_id
        LEFT JOIN CourseOfferings co2 ON r.retake_offering_id = co2.offering_id
        LEFT JOIN Courses c2 ON co2.course_id = c2.course_id
        LEFT JOIN Terms current_term ON co2.term_id = current_term.term_id
        WHERE r.student_id = %s
        ORDER BY r.created_at DESC
        """
        cursor.execute(sql, (student['student_id'],))
        retakes = cursor.fetchall()

        return success_response(retakes)


@student_bp.route('/notifications', methods=['GET'])
@role_required('student')
def get_notifications():
    """获取消息通知"""
    user = request.current_user

    with get_db_cursor(commit=False) as cursor:
        sql = """
        SELECT
            notification_id, title, content,
            notification_type, is_read, created_at
        FROM Notifications
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 50
        """
        cursor.execute(sql, (user['user_id'],))
        notifications = cursor.fetchall()

        return success_response(notifications)

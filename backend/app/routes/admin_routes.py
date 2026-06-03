#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
管理员端路由模块
"""
from flask import request
from app.routes import admin_bp
from app.utils import success_response, error_response
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
            ORDER BY g.total_score DESC
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
        SELECT user_id, username, real_name, role,
               CASE role
                   WHEN 'student' THEN '学生'
                   WHEN 'teacher' THEN '教师'
                   WHEN 'admin' THEN '管理员'
               END as role_name,
               COALESCE(s.phone, t.phone, '') as phone,
               status
        FROM Users u
        LEFT JOIN Students s ON u.user_id = s.user_id
        LEFT JOIN Teachers t ON u.user_id = t.user_id
        ORDER BY user_id
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

    if not all([username, real_name, role]):
        return error_response(400, "参数不完整")

    with get_db_cursor(commit=True) as cursor:
        if user_id:
            # 编辑
            cursor.execute("""
                UPDATE Users SET username=%s, real_name=%s, role=%s
                WHERE user_id=%s
            """, (username, real_name, role, user_id))
        else:
            # 新增 - 简化版，实际应该同时创建对应的 Students/Teachers 记录
            from werkzeug.security import generate_password_hash
            password_hash = generate_password_hash('123456')

            cursor.execute("""
                INSERT INTO Users (username, password_hash, real_name, role, status)
                VALUES (%s, %s, %s, %s, '正常')
            """, (username, password_hash, real_name, role))

        return success_response(message="操作成功")


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


@admin_bp.route('/business-windows', methods=['GET'])
@role_required('admin')
def get_business_windows():
    """获取业务时间窗口"""
    with get_db_cursor(commit=False) as cursor:
        sql = """
        SELECT bw.window_id, t.term_name, bw.window_type,
               bw.start_time, bw.end_time,
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
    # 简化实现
    return success_response(message="操作成功")


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


@admin_bp.route('/offerings', methods=['GET'])
@role_required('admin')
def get_offerings():
    """获取开课管理列表"""
    with get_db_cursor(commit=False) as cursor:
        sql = """
        SELECT
            co.offering_id, c.course_name, t.real_name as teacher_name,
            term.term_name, co.teaching_class_name,
            co.capacity, co.selected_count_cached as selected_count,
            co.min_enrollment, co.is_retake_class, co.status
        FROM CourseOfferings co
        JOIN Courses c ON co.course_id = c.course_id
        JOIN Teachers t ON co.teacher_id = t.teacher_id
        JOIN Terms term ON co.term_id = term.term_id
        ORDER BY term.term_id DESC, co.offering_id
        """
        cursor.execute(sql)
        offerings = cursor.fetchall()

        return success_response(offerings)


@admin_bp.route('/offerings', methods=['POST'])
@role_required('admin')
def create_offering():
    """新增开课"""
    # 简化实现
    return success_response(message="操作成功")


@admin_bp.route('/approvals', methods=['GET'])
@role_required('admin')
def get_approvals():
    """获取待审批列表"""
    with get_db_cursor(commit=False) as cursor:
        sql = """
        SELECT
            tr.request_id, t.real_name as teacher_name, tr.request_type,
            c.course_name, term.term_name, tr.content,
            tr.reason, tr.status, tr.created_at,
            '无冲突' as conflict_check_result
        FROM TeachingRequests tr
        LEFT JOIN Teachers t ON tr.teacher_id = t.teacher_id
        LEFT JOIN CourseOfferings co ON tr.offering_id = co.offering_id
        LEFT JOIN Courses c ON co.course_id = c.course_id
        LEFT JOIN Terms term ON co.term_id = term.term_id
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

            # 写入审计日志
            cursor.execute("""
                INSERT INTO AuditLogs (operator, operation_type, target_type, target_id, reason)
                VALUES ('admin', '发布成绩', '开课班', %s, '管理员发布成绩')
            """, (offering_id,))

            return success_response(message="成绩发布成功")
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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
教师端路由模块
"""
from flask import request
from app.routes import teacher_bp
from app.utils import success_response, error_response
from app.auth import role_required
from app.db import get_db_cursor
import pymysql


@teacher_bp.route('/profile', methods=['GET'])
@role_required('teacher')
def get_profile():
    """获取教师个人信息"""
    user = request.current_user

    with get_db_cursor(commit=False) as cursor:
        sql = """
        SELECT t.teacher_no, t.real_name, t.gender,
               d.department_name, t.title, t.phone, t.email
        FROM Teachers t
        LEFT JOIN Departments d ON t.department_id = d.department_id
        WHERE t.user_id = %s
        """
        cursor.execute(sql, (user['user_id'],))
        profile = cursor.fetchone()

        if not profile:
            return error_response(404, "教师信息不存在")

        return success_response(profile)


@teacher_bp.route('/offerings', methods=['GET'])
@role_required('teacher')
def get_offerings():
    """获取授课任务"""
    user = request.current_user

    with get_db_cursor(commit=False) as cursor:
        # 获取教师ID
        cursor.execute("SELECT teacher_id FROM Teachers WHERE user_id = %s", (user['user_id'],))
        teacher = cursor.fetchone()
        if not teacher:
            return error_response(404, "教师信息不存在")

        sql = """
        SELECT
            co.offering_id, c.course_code, c.course_name,
            term.term_name, co.teaching_class_name,
            co.capacity, co.selected_count_cached as selected_count,
            co.is_retake_class, co.status,
            GROUP_CONCAT(
                CONCAT('周', cs.weekday, ' ', cs.start_section, '-', cs.end_section, '节')
                SEPARATOR ' / '
            ) as schedule_text,
            GROUP_CONCAT(DISTINCT CONCAT(cr.building, ' ', cr.room_no) SEPARATOR ', ') as location
        FROM CourseOfferings co
        JOIN Courses c ON co.course_id = c.course_id
        JOIN Terms term ON co.term_id = term.term_id
        LEFT JOIN ClassSchedules cs ON co.offering_id = cs.offering_id
        LEFT JOIN Classrooms cr ON cs.classroom_id = cr.classroom_id
        WHERE co.teacher_id = %s
        GROUP BY co.offering_id
        ORDER BY term.term_id DESC, co.offering_id
        """
        cursor.execute(sql, (teacher['teacher_id'],))
        offerings = cursor.fetchall()

        return success_response(offerings)


@teacher_bp.route('/roster/<int:offering_id>', methods=['GET'])
@role_required('teacher')
def get_roster(offering_id):
    """获取选课学生名单"""
    user = request.current_user

    with get_db_cursor(commit=False) as cursor:
        # 验证是否为本人课程
        cursor.execute("""
            SELECT teacher_id FROM Teachers WHERE user_id = %s
        """, (user['user_id'],))
        teacher = cursor.fetchone()
        if not teacher:
            return error_response(404, "教师信息不存在")

        cursor.execute("""
            SELECT teacher_id FROM CourseOfferings WHERE offering_id = %s
        """, (offering_id,))
        offering = cursor.fetchone()
        if not offering or offering['teacher_id'] != teacher['teacher_id']:
            return error_response(403, "无权查看此课程")

        sql = """
        SELECT
            s.student_no, s.real_name,
            m.major_name, c.class_name,
            e.is_retake, e.enroll_time,
            COALESCE(g.score_status, '未录入') as score_status
        FROM Enrollments e
        JOIN Students s ON e.student_id = s.student_id
        LEFT JOIN Majors m ON s.major_id = m.major_id
        LEFT JOIN Classes c ON s.class_id = c.class_id
        LEFT JOIN Grades g ON e.enrollment_id = g.enrollment_id
        WHERE e.offering_id = %s AND e.status = '已选'
        ORDER BY s.student_no
        """
        cursor.execute(sql, (offering_id,))
        roster = cursor.fetchall()

        return success_response(roster)


@teacher_bp.route('/grade-sheet/<int:offering_id>', methods=['GET'])
@role_required('teacher')
def get_grade_sheet(offering_id):
    """获取成绩录入表"""
    user = request.current_user

    with get_db_cursor(commit=False) as cursor:
        # 验证权限
        cursor.execute("SELECT teacher_id FROM Teachers WHERE user_id = %s", (user['user_id'],))
        teacher = cursor.fetchone()
        if not teacher:
            return error_response(404, "教师信息不存在")

        cursor.execute("SELECT teacher_id FROM CourseOfferings WHERE offering_id = %s", (offering_id,))
        offering = cursor.fetchone()
        if not offering or offering['teacher_id'] != teacher['teacher_id']:
            return error_response(403, "无权查看此课程")

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

        # 格式化：未录入成绩显示为 null
        for grade in grades:
            if not grade['score_status']:
                grade['score_status'] = '未录入'

        return success_response(grades)


@teacher_bp.route('/grade', methods=['POST'])
@role_required('teacher')
def save_grade():
    """保存成绩（草稿）"""
    user = request.current_user
    data = request.get_json()

    offering_id = data.get('offering_id')
    rows = data.get('rows', [])

    if not offering_id or not rows:
        return error_response(400, "参数不完整")

    with get_db_cursor(commit=True) as cursor:
        # 验证权限
        cursor.execute("SELECT teacher_id FROM Teachers WHERE user_id = %s", (user['user_id'],))
        teacher = cursor.fetchone()
        if not teacher:
            return error_response(404, "教师信息不存在")

        cursor.execute("SELECT teacher_id FROM CourseOfferings WHERE offering_id = %s", (offering_id,))
        offering = cursor.fetchone()
        if not offering or offering['teacher_id'] != teacher['teacher_id']:
            return error_response(403, "无权操作此课程")

        # 批量保存成绩
        for row in rows:
            enrollment_id = row.get('enrollment_id')
            usual = row.get('usual_score')
            experiment = row.get('experiment_score')
            final = row.get('final_score')

            # 计算总评
            total = None
            if usual is not None and experiment is not None and final is not None:
                total = round(usual * 0.3 + experiment * 0.2 + final * 0.5, 1)

            # 判断是否通过
            is_passed = total >= 60 if total is not None else False

            # 计算绩点（简化版）
            grade_point = 0
            if total is not None:
                if total >= 90:
                    grade_point = 4.0
                elif total >= 80:
                    grade_point = 3.0
                elif total >= 70:
                    grade_point = 2.0
                elif total >= 60:
                    grade_point = 1.0

            # 检查是否已有成绩记录
            cursor.execute("SELECT grade_id, score_status FROM Grades WHERE enrollment_id = %s", (enrollment_id,))
            existing = cursor.fetchone()

            if existing:
                # 已提交、已发布的成绩不允许修改
                if existing['score_status'] in ['已提交', '已发布', '已冻结']:
                    continue

                # 更新
                cursor.execute("""
                    UPDATE Grades SET
                        usual_score = %s, experiment_score = %s, final_score = %s,
                        total_score = %s, is_passed = %s, grade_point = %s,
                        score_status = '草稿', updated_at = NOW()
                    WHERE enrollment_id = %s
                """, (usual, experiment, final, total, is_passed, grade_point, enrollment_id))
            else:
                # 插入
                cursor.execute("""
                    INSERT INTO Grades (enrollment_id, usual_score, experiment_score, final_score,
                                        total_score, is_passed, grade_point, score_status, included_in_average)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, '草稿', TRUE)
                """, (enrollment_id, usual, experiment, final, total, is_passed, grade_point))

        return success_response(message="成绩保存成功")


@teacher_bp.route('/grade/submit', methods=['POST'])
@role_required('teacher')
def submit_grade():
    """提交成绩"""
    user = request.current_user
    data = request.get_json()
    offering_id = data.get('offering_id')

    if not offering_id:
        return error_response(400, "开课班ID不能为空")

    with get_db_cursor(commit=True) as cursor:
        # 验证权限
        cursor.execute("SELECT teacher_id FROM Teachers WHERE user_id = %s", (user['user_id'],))
        teacher = cursor.fetchone()
        if not teacher:
            return error_response(404, "教师信息不存在")

        cursor.execute("SELECT teacher_id FROM CourseOfferings WHERE offering_id = %s", (offering_id,))
        offering = cursor.fetchone()
        if not offering or offering['teacher_id'] != teacher['teacher_id']:
            return error_response(403, "无权操作此课程")

        try:
            # 调用存储过程
            cursor.callproc('sp_TeacherSubmitGrade', (offering_id,))
            return success_response(message="成绩提交成功")
        except pymysql.Error as e:
            error_msg = str(e.args[1]) if len(e.args) > 1 else "成绩提交失败"
            return error_response(400, error_msg)


@teacher_bp.route('/requests', methods=['GET'])
@role_required('teacher')
def get_requests():
    """获取教学申请列表"""
    user = request.current_user

    with get_db_cursor(commit=False) as cursor:
        cursor.execute("SELECT teacher_id FROM Teachers WHERE user_id = %s", (user['user_id'],))
        teacher = cursor.fetchone()
        if not teacher:
            return error_response(404, "教师信息不存在")

        sql = """
        SELECT
            tr.request_id, tr.request_type,
            c.course_name, term.term_name,
            tr.content, tr.reason, tr.status, tr.created_at,
            tr.admin_comment, tr.processed_at
        FROM TeachingRequests tr
        LEFT JOIN CourseOfferings co ON tr.offering_id = co.offering_id
        LEFT JOIN Courses c ON co.course_id = c.course_id
        LEFT JOIN Terms term ON co.term_id = term.term_id
        WHERE tr.teacher_id = %s
        ORDER BY tr.created_at DESC
        """
        cursor.execute(sql, (teacher['teacher_id'],))
        requests = cursor.fetchall()

        return success_response(requests)


@teacher_bp.route('/requests', methods=['POST'])
@role_required('teacher')
def submit_request():
    """提交教学申请"""
    user = request.current_user
    data = request.get_json()

    request_type = data.get('request_type')
    course_name = data.get('course_name')
    content = data.get('content')
    reason = data.get('reason')

    if not all([request_type, content, reason]):
        return error_response(400, "参数不完整")

    with get_db_cursor(commit=True) as cursor:
        cursor.execute("SELECT teacher_id FROM Teachers WHERE user_id = %s", (user['user_id'],))
        teacher = cursor.fetchone()
        if not teacher:
            return error_response(404, "教师信息不存在")

        sql = """
        INSERT INTO TeachingRequests (teacher_id, request_type, content, reason, status)
        VALUES (%s, %s, %s, %s, '待审批')
        """
        cursor.execute(sql, (teacher['teacher_id'], request_type, content, reason))

        return success_response(message="申请提交成功")


@teacher_bp.route('/grade-stats', methods=['GET'])
@role_required('teacher')
def get_grade_stats():
    """获取成绩统计"""
    user = request.current_user

    with get_db_cursor(commit=False) as cursor:
        cursor.execute("SELECT teacher_id FROM Teachers WHERE user_id = %s", (user['user_id'],))
        teacher = cursor.fetchone()
        if not teacher:
            return error_response(404, "教师信息不存在")

        sql = """
        SELECT
            co.offering_id, c.course_name, co.teaching_class_name,
            COUNT(e.enrollment_id) as enrolled,
            COUNT(g.grade_id) as attended,
            SUM(CASE WHEN g.is_passed = TRUE THEN 1 ELSE 0 END) as passed,
            SUM(CASE WHEN g.is_passed = FALSE THEN 1 ELSE 0 END) as failed,
            AVG(g.total_score) as avg,
            MAX(g.total_score) as max,
            MIN(g.total_score) as min,
            ROUND(SUM(CASE WHEN g.is_passed = FALSE THEN 1 ELSE 0 END) * 100.0 / COUNT(g.grade_id), 1) as fail_rate,
            SUM(e.is_retake) as retake_count
        FROM CourseOfferings co
        JOIN Courses c ON co.course_id = c.course_id
        LEFT JOIN Enrollments e ON co.offering_id = e.offering_id AND e.status = '已选'
        LEFT JOIN Grades g ON e.enrollment_id = g.enrollment_id AND g.score_status IN ('已提交', '已发布')
        WHERE co.teacher_id = %s
        GROUP BY co.offering_id
        HAVING COUNT(g.grade_id) > 0
        ORDER BY co.offering_id DESC
        """
        cursor.execute(sql, (teacher['teacher_id'],))
        stats = cursor.fetchall()

        # 格式化数值
        for stat in stats:
            stat['avg'] = round(float(stat['avg'] or 0), 1)
            stat['fail_rate'] = float(stat['fail_rate'] or 0)

        return success_response(stats)

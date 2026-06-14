#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
公共路由模块
"""
from app.routes import common_bp
from app.utils import success_response, error_response
from app.auth import login_required
from app.db import get_db_cursor


@common_bp.route('/current-term', methods=['GET'])
@login_required
def get_current_term():
    """获取当前学年学期"""
    with get_db_cursor(commit=False) as cursor:
        sql = """
        SELECT t.term_id, t.term_name,
               ay.academic_year_name, t.term_no, t.is_current
        FROM Terms t
        JOIN AcademicYears ay ON t.academic_year_id = ay.academic_year_id
        WHERE t.is_current = TRUE
        LIMIT 1
        """
        cursor.execute(sql)
        term = cursor.fetchone()

        if not term:
            return error_response(404, "未找到当前学期")

        return success_response(term)


@common_bp.route('/terms', methods=['GET'])
@login_required
def get_terms():
    """获取全部学期列表（供下拉选择，按时间倒序）"""
    with get_db_cursor(commit=False) as cursor:
        sql = """
        SELECT t.term_id, t.term_name, t.term_no, t.is_current,
               ay.academic_year_name
        FROM Terms t
        JOIN AcademicYears ay ON t.academic_year_id = ay.academic_year_id
        ORDER BY t.term_id DESC
        """
        cursor.execute(sql)
        return success_response(cursor.fetchall())

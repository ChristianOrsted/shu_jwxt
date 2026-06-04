#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工具函数模块
"""
from flask import jsonify
from functools import wraps


def success_response(data=None, message="success"):
    """成功响应"""
    return jsonify({
        "code": 200,
        "message": message,
        "data": data
    }), 200


def error_response(code=400, message="操作失败", data=None):
    """错误响应"""
    return jsonify({
        "code": code,
        "message": message,
        "data": data
    }), 200  # HTTP 状态码仍为 200，业务错误通过 code 区分


def sync_offering_status_by_window(cursor):
    """根据「选课」业务窗口惰性同步开课班状态。

    选课窗口已结束的「开放选课」教学班自动改为「关闭选课」（单向收口：
    只关不开，避免误重开已人工关闭/取消的班）。在管理员开课列表、学生选课
    列表、学生选课动作等入口调用，使 CourseOfferings.status 成为唯一事实来源，
    下游一切按 status 判断的逻辑（选课、展示等）自动保持一致。

    需要在 commit=True 的游标上调用。返回受影响的行数。
    """
    cursor.execute("""
        UPDATE CourseOfferings co
        JOIN (
            SELECT term_id, MAX(end_time) AS enroll_end
            FROM BusinessWindows WHERE window_type = '选课'
            GROUP BY term_id
        ) ew ON ew.term_id = co.term_id
        SET co.status = '关闭选课'
        WHERE co.status = '开放选课'
          AND ew.enroll_end IS NOT NULL
          AND NOW() > ew.enroll_end
    """)
    return cursor.rowcount

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工具函数模块
"""
from datetime import datetime, timedelta
from flask import jsonify
from functools import wraps


# 学期固定包含的四类业务窗口
WINDOW_TYPES = ('选课', '退课', '成绩录入', '成绩公布')


def default_business_windows(start_date, end_date, now=None):
    """推算某学期四个业务窗口的默认起止时间。

    - 有学期起止日期时按日期推算：选课/退课围绕开学日，成绩录入/公布围绕结课日；
    - 缺少对应日期时退化为「立即开放」——区间覆盖当前时间，保证学期切过去即可用。

    入参 start_date / end_date 为 datetime.date 或 None。
    返回 [(window_type, start_time, end_time), ...]，时间均为 datetime。
    """
    now = now or datetime.now()
    open_start = now - timedelta(days=30)

    if start_date:
        s = datetime.combine(start_date, datetime.min.time())
        enroll = (s - timedelta(days=7), s + timedelta(days=14))
        withdraw = (s - timedelta(days=7), s + timedelta(days=28))
    else:
        enroll = (open_start, now + timedelta(days=60))
        withdraw = (open_start, now + timedelta(days=75))

    if end_date:
        e = datetime.combine(end_date, datetime.min.time())
        grade_input = (e - timedelta(days=14), e + timedelta(days=1))
        grade_publish = (e - timedelta(days=7), e + timedelta(days=14))
    else:
        grade_input = (open_start, now + timedelta(days=120))
        grade_publish = (open_start, now + timedelta(days=150))

    return [
        ('选课', *enroll),
        ('退课', *withdraw),
        ('成绩录入', *grade_input),
        ('成绩公布', *grade_publish),
    ]


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

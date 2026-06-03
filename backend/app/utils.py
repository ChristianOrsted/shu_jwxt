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

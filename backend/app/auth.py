#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JWT 认证模块
"""
import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request
from werkzeug.security import check_password_hash
from app.utils import error_response
from app.db import get_db_cursor

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))


def generate_token(user_id, role):
    """生成 JWT Token"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def verify_token(token):
    """验证 JWT Token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return error_response(401, "未登录或 Token 缺失")

        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != 'Bearer':
            return error_response(401, "Token 格式错误")

        token = parts[1]
        payload = verify_token(token)

        if not payload:
            return error_response(401, "Token 已失效或无效")

        request.current_user = payload
        return f(*args, **kwargs)

    return decorated_function


def role_required(*roles):
    """角色验证装饰器"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user = request.current_user
            if user['role'] not in roles:
                return error_response(403, "无权限访问")
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def authenticate_user(username, password, role):
    """验证用户登录"""
    with get_db_cursor(commit=False) as cursor:
        # 查询用户
        sql = """
        SELECT u.user_id, u.username, u.password_hash, u.role,
               u.real_name, u.status
        FROM Users u
        WHERE u.username = %s AND u.role = %s
        """
        cursor.execute(sql, (username, role))
        user = cursor.fetchone()

        if not user:
            return None, "用户名、密码或角色不正确"

        if user['status'] != '正常':
            return None, "账号已被禁用"

        # 验证密码
        if not check_password_hash(user['password_hash'], password):
            return None, "用户名、密码或角色不正确"

        return user, None

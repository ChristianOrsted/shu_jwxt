#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证路由模块
"""
from flask import request
from app.routes import auth_bp
from app.utils import success_response, error_response
from app.auth import authenticate_user, generate_token


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if not all([username, password, role]):
        return error_response(400, "用户名、密码和角色不能为空")

    if role not in ['student', 'teacher', 'admin']:
        return error_response(400, "角色参数错误")

    # 验证用户
    user, error = authenticate_user(username, password, role)

    if error:
        return error_response(400, error)

    # 生成 Token
    token = generate_token(user['user_id'], user['role'])

    # 返回用户信息
    return success_response({
        'token': token,
        'user': {
            'user_id': user['user_id'],
            'username': user['username'],
            'real_name': user['real_name'],
            'role': user['role']
        }
    })

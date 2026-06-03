#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
路由模块初始化
"""
from flask import Blueprint

# 创建蓝图
auth_bp = Blueprint('auth', __name__)
common_bp = Blueprint('common', __name__)
student_bp = Blueprint('student', __name__)
teacher_bp = Blueprint('teacher', __name__)
admin_bp = Blueprint('admin', __name__)

# 导入路由（避免循环导入）
from app.routes import auth_routes, common_routes, student_routes
from app.routes import teacher_routes, admin_routes

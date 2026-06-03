#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Flask 应用工厂函数
"""
from flask import Flask
from flask_cors import CORS
import os


def create_app():
    """创建并配置 Flask 应用"""
    app = Flask(__name__)

    # 加载配置
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JSON_AS_ASCII'] = False  # 支持中文返回
    app.config['JSON_SORT_KEYS'] = False

    # 配置 CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    # 注册蓝图
    from app.routes import auth_bp, student_bp, teacher_bp, admin_bp, common_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(common_bp, url_prefix='/api/common')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(teacher_bp, url_prefix='/api/teacher')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # 健康检查
    @app.route('/health')
    def health():
        return {'status': 'ok'}

    return app

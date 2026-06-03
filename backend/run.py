#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Flask 应用启动入口
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("学分制教务选课管理系统 - 后端服务")
    print("服务地址: http://localhost:5000")
    print("API 前缀: /api")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)

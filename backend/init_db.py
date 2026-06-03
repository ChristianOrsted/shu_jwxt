#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库初始化和测试脚本
用于初始化数据库并生成真实的密码哈希
"""

import pymysql
from werkzeug.security import generate_password_hash

# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'christian',
    'password': '123456',
    'charset': 'utf8mb4'
}

def init_database():
    """初始化数据库"""
    print("=" * 60)
    print("开始初始化数据库...")
    print("=" * 60)

    # 生成真实的密码哈希
    password_hash = generate_password_hash('123456')
    print(f"\n生成的密码哈希（用于 123456）:")
    print(password_hash)
    print()

    try:
        # 连接 MySQL（不指定数据库）
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        print("✓ 成功连接到 MySQL")

        # 读取并执行建表脚本
        print("\n1. 执行建表脚本 (01_schema.sql)...")
        with open('sql/01_schema.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # 分割并执行 SQL 语句
        for statement in schema_sql.split(';'):
            if statement.strip():
                cursor.execute(statement)
        connection.commit()
        print("   ✓ 建表完成")

        # 使用 school 数据库
        cursor.execute("USE school")

        # 执行存储过程和触发器脚本
        print("\n2. 执行存储过程和触发器脚本 (02_routines.sql)...")
        with open('sql/02_routines.sql', 'r', encoding='utf-8') as f:
            routines_sql = f.read()

        # 执行整个脚本（包含 DELIMITER）
        cursor.execute(routines_sql)
        connection.commit()
        print("   ✓ 存储过程和触发器创建完成")

        # 读取测试数据脚本并替换密码哈希
        print("\n3. 执行测试数据脚本 (03_seed.sql)...")
        with open('sql/03_seed.sql', 'r', encoding='utf-8') as f:
            seed_sql = f.read()

        # 替换为真实的密码哈希
        seed_sql = seed_sql.replace(
            'scrypt:32768:8:1$lK9ZJY3M7vGF2nLt$6e5d8f7a9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0',
            password_hash
        )

        # 分割并执行
        for statement in seed_sql.split(';'):
            if statement.strip() and not statement.strip().startswith('--'):
                try:
                    cursor.execute(statement)
                except Exception as e:
                    if 'SELECT' not in statement.upper():  # 忽略 SELECT 语句的错误
                        print(f"   警告: {str(e)[:100]}")

        connection.commit()
        print("   ✓ 测试数据插入完成")

        # 验证数据
        print("\n4. 验证数据插入...")
        cursor.execute("SELECT COUNT(*) as count FROM Users")
        user_count = cursor.fetchone()['count']
        print(f"   用户数量: {user_count}")

        cursor.execute("SELECT COUNT(*) as count FROM Students")
        student_count = cursor.fetchone()['count']
        print(f"   学生数量: {student_count}")

        cursor.execute("SELECT COUNT(*) as count FROM Teachers")
        teacher_count = cursor.fetchone()['count']
        print(f"   教师数量: {teacher_count}")

        cursor.execute("SELECT COUNT(*) as count FROM Courses")
        course_count = cursor.fetchone()['count']
        print(f"   课程数量: {course_count}")

        cursor.execute("SELECT COUNT(*) as count FROM CourseOfferings WHERE term_id = 4")
        offering_count = cursor.fetchone()['count']
        print(f"   当前学期开课数: {offering_count}")

        print("\n" + "=" * 60)
        print("✓ 数据库初始化成功！")
        print("=" * 60)

        print("\n演示账号：")
        print("  管理员: admin / 123456")
        print("  教师:   T1001 / 123456")
        print("  学生:   S2023001 / 123456")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        raise


if __name__ == '__main__':
    init_database()

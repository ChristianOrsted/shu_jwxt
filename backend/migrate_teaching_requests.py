#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
迁移脚本：为 TeachingRequests 表补充 term_id / course_name 字段。

背景：教师提交的教学申请此前丢失了「课程名称」和「学期」，
本脚本在不清空数据的前提下为现有数据库补齐这两个字段，可重复执行。

用法：
    python migrate_teaching_requests.py
"""

import os
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'christian'),
    'password': os.getenv('DB_PASSWORD', '123456'),
    'database': os.getenv('DB_NAME', 'school'),
    'charset': 'utf8mb4',
    'cursorclass': DictCursor,
}


def column_exists(cursor, table, column):
    cursor.execute(
        """
        SELECT COUNT(*) AS n FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s
        """,
        (table, column),
    )
    return cursor.fetchone()['n'] > 0


def fk_exists(cursor, table, column):
    cursor.execute(
        """
        SELECT COUNT(*) AS n FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
          AND COLUMN_NAME = %s AND REFERENCED_TABLE_NAME IS NOT NULL
        """,
        (table, column),
    )
    return cursor.fetchone()['n'] > 0


def main():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            if not column_exists(cursor, 'TeachingRequests', 'term_id'):
                cursor.execute(
                    "ALTER TABLE TeachingRequests "
                    "ADD COLUMN term_id INT COMMENT '申请学期' AFTER offering_id"
                )
                print("✓ 已新增列 TeachingRequests.term_id")
            else:
                print("· TeachingRequests.term_id 已存在，跳过")

            if not column_exists(cursor, 'TeachingRequests', 'course_name'):
                cursor.execute(
                    "ALTER TABLE TeachingRequests "
                    "ADD COLUMN course_name VARCHAR(100) "
                    "COMMENT '课程名称（教师自由填写）' AFTER term_id"
                )
                print("✓ 已新增列 TeachingRequests.course_name")
            else:
                print("· TeachingRequests.course_name 已存在，跳过")

            if not fk_exists(cursor, 'TeachingRequests', 'term_id'):
                try:
                    cursor.execute(
                        "ALTER TABLE TeachingRequests "
                        "ADD FOREIGN KEY (term_id) REFERENCES Terms(term_id) "
                        "ON DELETE SET NULL"
                    )
                    print("✓ 已为 term_id 添加外键约束")
                except pymysql.Error as e:
                    # 外键非必需，失败不影响本次修复
                    print(f"· term_id 外键添加跳过：{e}")
            else:
                print("· term_id 外键已存在，跳过")

        conn.commit()
        print("\n迁移完成。")
    finally:
        conn.close()


if __name__ == '__main__':
    main()

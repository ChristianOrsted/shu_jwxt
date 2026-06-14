#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
迁移脚本：为现有数据库补齐业务时间窗口。

背景：早期数据里只有「当前学期」配了业务窗口，其它学期一个都没有，
导致切换到这些学期后学生选课/退课会提示「不在选课时间内」。本脚本：
  1. 为每个学期补齐缺失的四类窗口（选课/退课/成绩录入/成绩公布），
     时间按学期起止日期推算，缺日期则退化为「立即开放」；
  2. 把「当前学期」的选课/退课窗口顺延到覆盖今天，使现在就能选课/退课演示。

可重复执行（已存在的窗口不会重复插入）。

用法：
    python migrate_business_windows.py
"""

import os
from datetime import datetime, timedelta

import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

from app.utils import default_business_windows, WINDOW_TYPES

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


def main():
    now = datetime.now()
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT term_id, term_name, start_date, end_date, is_current FROM Terms"
            )
            terms = cursor.fetchall()

            cursor.execute("SELECT term_id, window_type FROM BusinessWindows")
            existing = {(r['term_id'], r['window_type']) for r in cursor.fetchall()}

            inserted = 0
            for t in terms:
                defaults = default_business_windows(t['start_date'], t['end_date'], now)
                for wtype, wstart, wend in defaults:
                    if (t['term_id'], wtype) in existing:
                        continue
                    cursor.execute(
                        "INSERT INTO BusinessWindows (term_id, window_type, start_time, end_time) "
                        "VALUES (%s, %s, %s, %s)",
                        (t['term_id'], wtype, wstart, wend),
                    )
                    inserted += 1
                    print(f"✓ 补齐 {t['term_name']} 的「{wtype}」窗口")

            # 当前学期的选课/退课窗口顺延到覆盖今天（区间两端向外扩，幂等）
            current = next((t for t in terms if t['is_current']), None)
            if current:
                cursor.execute(
                    "UPDATE BusinessWindows "
                    "SET start_time = LEAST(start_time, %s), end_time = GREATEST(end_time, %s) "
                    "WHERE term_id = %s AND window_type IN ('选课', '退课')",
                    (now - timedelta(days=1), now + timedelta(days=30), current['term_id']),
                )
                print(f"✓ 已顺延当前学期「{current['term_name']}」的选课/退课窗口至覆盖今天")

        conn.commit()
        print(f"\n迁移完成，新增 {inserted} 个业务窗口。")
    finally:
        conn.close()


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库连接模块
"""
import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'christian'),
    'password': os.getenv('DB_PASSWORD', '123456'),
    'database': os.getenv('DB_NAME', 'school'),
    'charset': 'utf8mb4',
    'cursorclass': DictCursor,
    'autocommit': False
}


@contextmanager
def get_db_connection():
    """获取数据库连接（上下文管理器）"""
    connection = None
    try:
        connection = pymysql.connect(**DB_CONFIG)
        yield connection
        connection.commit()
    except Exception as e:
        if connection:
            connection.rollback()
        raise e
    finally:
        if connection:
            connection.close()


@contextmanager
def get_db_cursor(commit=True):
    """获取数据库游标（上下文管理器）"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

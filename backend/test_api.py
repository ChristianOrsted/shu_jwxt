#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API 接口测试脚本
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def print_section(title):
    """打印分隔符"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def test_health():
    """测试健康检查"""
    print_section("1. 健康检查")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ 错误: {str(e)}")
        return False

def test_login(username, password, role):
    """测试登录"""
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "username": username,
        "password": password,
        "role": role
    }

    try:
        response = requests.post(url, json=data, timeout=5)
        result = response.json()

        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")

        if result.get('code') == 200:
            return result['data']['token']
        return None
    except Exception as e:
        print(f"✗ 错误: {str(e)}")
        return None

def test_student_courses(token):
    """测试获取可选课程列表"""
    url = f"{BASE_URL}/api/student/courses"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        result = response.json()

        print(f"状态码: {response.status_code}")
        print(f"返回课程数量: {len(result.get('data', []))}")

        if result.get('code') == 200 and result.get('data'):
            # 只打印第一门课程作为示例
            first_course = result['data'][0]
            print("\n第一门课程详情:")
            print(json.dumps(first_course, ensure_ascii=False, indent=2))

        return result.get('code') == 200
    except Exception as e:
        print(f"✗ 错误: {str(e)}")
        return False

def test_student_enroll(token, offering_id):
    """测试选课"""
    url = f"{BASE_URL}/api/student/enroll"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "offering_id": offering_id
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=5)
        result = response.json()

        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")

        return result.get('code') == 200
    except Exception as e:
        print(f"✗ 错误: {str(e)}")
        return False

def test_student_my_courses(token):
    """测试获取已选课程"""
    url = f"{BASE_URL}/api/student/my-courses"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        result = response.json()

        print(f"状态码: {response.status_code}")
        print(f"已选课程数量: {len(result.get('data', []))}")

        if result.get('code') == 200 and result.get('data'):
            for course in result['data']:
                print(f"  - {course['course_name']} ({course['teacher_name']})")

        return result.get('code') == 200
    except Exception as e:
        print(f"✗ 错误: {str(e)}")
        return False

def test_teacher_offerings(token):
    """测试教师授课任务"""
    url = f"{BASE_URL}/api/teacher/offerings"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        result = response.json()

        print(f"状态码: {response.status_code}")
        print(f"授课任务数量: {len(result.get('data', []))}")

        if result.get('code') == 200 and result.get('data'):
            for offering in result['data']:
                print(f"  - {offering['course_name']} - {offering['teaching_class_name']} ({offering['selected_count']}/{offering['capacity']})")

        return result.get('code') == 200
    except Exception as e:
        print(f"✗ 错误: {str(e)}")
        return False

def test_admin_statistics(token):
    """测试管理员统计"""
    url = f"{BASE_URL}/api/admin/statistics"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        result = response.json()

        print(f"状态码: {response.status_code}")

        if result.get('code') == 200:
            cards = result['data']['cards']
            print(f"\n统计数据:")
            print(f"  学生总数: {cards['total_students']}")
            print(f"  教师总数: {cards['total_teachers']}")
            print(f"  课程总数: {cards['total_courses']}")
            print(f"  开课数量: {cards['total_offerings']}")

        return result.get('code') == 200
    except Exception as e:
        print(f"✗ 错误: {str(e)}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("后端 API 接口测试")
    print("=" * 60)

    # 1. 健康检查
    if not test_health():
        print("\n✗ 后端服务未启动，请先运行: python run.py")
        return

    # 2. 学生登录
    print_section("2. 学生登录测试")
    student_token = test_login("S2023001", "123456", "student")

    if student_token:
        print("✓ 学生登录成功")

        # 3. 获取可选课程
        print_section("3. 获取可选课程列表")
        test_student_courses(student_token)

        # 4. 获取已选课程
        print_section("4. 获取已选课程")
        test_student_my_courses(student_token)

        # 5. 测试选课（操作系统）
        print_section("5. 测试选课（操作系统 - offering_id: 104）")
        test_student_enroll(student_token, 104)

    # 6. 教师登录
    print_section("6. 教师登录测试")
    teacher_token = test_login("T1001", "123456", "teacher")

    if teacher_token:
        print("✓ 教师登录成功")

        # 7. 获取授课任务
        print_section("7. 获取授课任务")
        test_teacher_offerings(teacher_token)

    # 8. 管理员登录
    print_section("8. 管理员登录测试")
    admin_token = test_login("admin", "123456", "admin")

    if admin_token:
        print("✓ 管理员登录成功")

        # 9. 获取统计数据
        print_section("9. 获取统计数据")
        test_admin_statistics(admin_token)

    print("\n" + "=" * 60)
    print("✓ 测试完成")
    print("=" * 60)

if __name__ == '__main__':
    run_all_tests()

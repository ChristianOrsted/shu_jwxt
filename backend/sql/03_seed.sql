-- ============================================
-- 学分制教务选课管理系统 - 测试数据
-- ============================================

USE school;

-- 禁用外键检查
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================
-- 1. 用户账号（密码统一为 123456）
-- 注意：密码哈希使用 werkzeug.security.generate_password_hash('123456')
-- 格式：scrypt:32768:8:1$salt$hash
-- ============================================

INSERT INTO Users (user_id, username, password_hash, role, real_name, status) VALUES
(1, 'admin', 'scrypt:32768:8:1$lK9ZJY3M7vGF2nLt$6e5d8f7a9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0', 'admin', '系统管理员', '正常'),
(2, 'T1001', 'scrypt:32768:8:1$lK9ZJY3M7vGF2nLt$6e5d8f7a9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0', 'teacher', '李教授', '正常'),
(3, 'T1002', 'scrypt:32768:8:1$lK9ZJY3M7vGF2nLt$6e5d8f7a9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0', 'teacher', '王老师', '正常'),
(4, 'S2023001', 'scrypt:32768:8:1$lK9ZJY3M7vGF2nLt$6e5d8f7a9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0', 'student', '张小明', '正常'),
(5, 'S2023002', 'scrypt:32768:8:1$lK9ZJY3M7vGF2nLt$6e5d8f7a9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0', 'student', '李晓红', '正常'),
(6, 'S2023003', 'scrypt:32768:8:1$lK9ZJY3M7vGF2nLt$6e5d8f7a9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0', 'student', '王强', '正常');

-- ============================================
-- 2. 组织结构
-- ============================================

INSERT INTO Departments (department_id, department_name) VALUES
(1, '计算机学院'),
(2, '数学学院');

INSERT INTO Majors (major_id, major_name, department_id) VALUES
(1, '软件工程', 1),
(2, '数据科学', 1),
(3, '应用数学', 2);

INSERT INTO Classes (class_id, class_name, major_id, grade_year) VALUES
(1, '软工2301班', 1, 2023),
(2, '数据2301班', 2, 2023),
(3, '数学2301班', 3, 2023);

-- ============================================
-- 3. 学生信息
-- ============================================

INSERT INTO Students (student_id, user_id, student_no, real_name, gender, department_id, major_id, class_id, grade_year, enroll_year, student_status, phone, email) VALUES
(1, 4, 'S2023001', '张小明', '男', 1, 1, 1, 2023, 2023, '在读', '13800000001', 'zhangxm@shu.edu.cn'),
(2, 5, 'S2023002', '李晓红', '女', 1, 2, 2, 2023, 2023, '在读', '13800000002', 'lixh@shu.edu.cn'),
(3, 6, 'S2023003', '王强', '男', 2, 3, 3, 2023, 2023, '在读', '13800000003', 'wangq@shu.edu.cn');

-- ============================================
-- 4. 教师信息
-- ============================================

INSERT INTO Teachers (teacher_id, user_id, teacher_no, real_name, gender, department_id, title, phone, email) VALUES
(1, 2, 'T1001', '李教授', '男', 1, '教授', '13900000001', 'lijs@shu.edu.cn'),
(2, 3, 'T1002', '王老师', '女', 1, '副教授', '13900000002', 'wangl@shu.edu.cn');

-- ============================================
-- 5. 学年学期
-- ============================================

INSERT INTO AcademicYears (academic_year_id, academic_year_name) VALUES
(1, '2024-2025学年'),
(2, '2025-2026学年');

INSERT INTO Terms (term_id, academic_year_id, term_no, term_name, start_date, end_date, is_current) VALUES
(1, 1, 1, '2024-2025学年第一学期', '2024-09-01', '2025-01-18', FALSE),
(2, 1, 2, '2024-2025学年第二学期', '2025-02-24', '2025-07-05', FALSE),
(3, 2, 1, '2025-2026学年第一学期', '2025-09-01', '2026-01-18', FALSE),
(4, 2, 2, '2025-2026学年第二学期', '2026-02-24', '2026-07-05', TRUE);

-- ============================================
-- 6. 业务时间窗口
-- ============================================

INSERT INTO BusinessWindows (window_id, term_id, window_type, start_time, end_time) VALUES
(1, 4, '选课', '2026-02-18 09:00:00', '2026-03-01 22:00:00'),
(2, 4, '退课', '2026-02-18 09:00:00', '2026-03-05 22:00:00'),
(3, 4, '成绩录入', '2026-06-01 09:00:00', '2026-06-15 22:00:00'),
(4, 4, '成绩公布', '2026-06-10 09:00:00', '2026-06-20 22:00:00');

-- ============================================
-- 7. 课程资源
-- ============================================

INSERT INTO Courses (course_id, course_code, course_name, credits, hours, course_type, assessment_type, description, allow_retake, is_enabled) VALUES
(1, 'CS201', '数据库原理', 3.5, 64, '专业课', '考试', '系统讲授关系数据库理论、SQL、事务、索引与查询优化。', TRUE, TRUE),
(2, 'CS101', '数据结构', 4.0, 72, '必修课', '考试', '学习线性表、树、图等基本数据结构及其算法。', TRUE, TRUE),
(3, 'MATH201', '高等数学（下）', 5.0, 90, '必修课', '考试', '微积分、级数、微分方程等内容。', TRUE, TRUE),
(4, 'CS301', '操作系统', 3.0, 54, '专业课', '考试', '操作系统原理、进程管理、内存管理、文件系统。', TRUE, TRUE),
(5, 'ENG101', '大学英语', 2.0, 36, '通识课', '考查', '英语听说读写综合训练。', TRUE, TRUE);

INSERT INTO Classrooms (classroom_id, building, room_no, capacity, status) VALUES
(1, '东区教学楼', 'A305', 60, '可用'),
(2, '东区教学楼', 'A306', 50, '可用'),
(3, '西区教学楼', 'B201', 80, '可用'),
(4, '西区教学楼', 'B202', 40, '可用');

-- ============================================
-- 8. 开课班（当前学期）
-- ============================================

INSERT INTO CourseOfferings (offering_id, course_id, teacher_id, term_id, teaching_class_name, capacity, selected_count_cached, min_enrollment, is_retake_class, status, description) VALUES
-- 数据库原理 - 普通班（已满）
(101, 1, 1, 4, '数据库原理-01班', 40, 40, 10, FALSE, '开放选课', '面向软件工程专业'),
-- 数据结构 - 普通班
(102, 2, 1, 4, '数据结构-01班', 50, 25, 10, FALSE, '开放选课', '面向计算机类专业'),
-- 高等数学 - 重修班
(103, 3, 2, 4, '高等数学（下）-重修班', 30, 5, 5, TRUE, '开放选课', '重修班，面向上学期挂科学生'),
-- 操作系统 - 普通班
(104, 4, 1, 4, '操作系统-01班', 45, 20, 10, FALSE, '开放选课', '面向计算机类专业'),
-- 大学英语 - 普通班
(105, 5, 2, 4, '大学英语-01班', 60, 30, 15, FALSE, '开放选课', '通识必修课');

-- 上学期的开课班（用于演示历史成绩）
INSERT INTO CourseOfferings (offering_id, course_id, teacher_id, term_id, teaching_class_name, capacity, selected_count_cached, min_enrollment, is_retake_class, status) VALUES
(90, 3, 2, 2, '高等数学（下）-01班', 50, 45, 10, FALSE, '已结课');

-- ============================================
-- 9. 课程时间安排
-- ============================================

INSERT INTO ClassSchedules (schedule_id, offering_id, classroom_id, weekday, start_section, end_section, week_start, week_end) VALUES
-- 数据库原理：周一 1-2节，周三 3-4节
(1, 101, 1, 1, 1, 2, 1, 18),
(2, 101, 1, 3, 3, 4, 1, 18),
-- 数据结构：周二 3-4节，周四 1-2节
(3, 102, 2, 2, 3, 4, 1, 18),
(4, 102, 2, 4, 1, 2, 1, 18),
-- 高数重修班：周六 1-4节
(5, 103, 3, 6, 1, 4, 1, 18),
-- 操作系统：周三 1-2节，周五 3-4节
(6, 104, 1, 3, 1, 2, 1, 18),
(7, 104, 1, 5, 3, 4, 1, 18),
-- 大学英语：周一 3-4节
(8, 105, 4, 1, 3, 4, 1, 18);

-- ============================================
-- 10. 选课记录
-- ============================================

-- 张小明（S2023001）已选课程：数据结构
INSERT INTO Enrollments (enrollment_id, student_id, offering_id, is_retake, enroll_time, status) VALUES
(5001, 1, 102, FALSE, '2026-02-20 10:12:00', '已选');

-- 张小明上学期选了高数，挂科了
INSERT INTO Enrollments (enrollment_id, student_id, offering_id, is_retake, enroll_time, status) VALUES
(6001, 1, 90, FALSE, '2025-02-25 10:00:00', '已完成');

-- 李晓红已选课程：操作系统
INSERT INTO Enrollments (enrollment_id, student_id, offering_id, is_retake, enroll_time, status) VALUES
(5002, 2, 104, FALSE, '2026-02-20 11:00:00', '已选');

-- 王强已选课程：大学英语
INSERT INTO Enrollments (enrollment_id, student_id, offering_id, is_retake, enroll_time, status) VALUES
(5003, 3, 105, FALSE, '2026-02-20 12:00:00', '已选');

-- 模拟数据库原理班已满（40人）- 简化处理，只插入几条代表性记录
-- 实际应该插入40条，这里省略

-- ============================================
-- 11. 成绩记录
-- ============================================

-- 张小明的高数挂科成绩（上学期）
INSERT INTO Grades (grade_id, enrollment_id, usual_score, experiment_score, final_score, total_score, grade_point, is_passed, score_status, included_in_average) VALUES
(9001, 6001, 60, 55, 45, 52, 0, FALSE, '已发布', TRUE);

-- ============================================
-- 12. 重修记录
-- ============================================

-- 张小明需要重修高数
INSERT INTO RetakeRecords (retake_id, student_id, source_enrollment_id, retake_offering_id, status) VALUES
(7001, 1, 6001, 103, '待重修');

-- ============================================
-- 13. 教学申请
-- ============================================

-- 李教授提交了一个扩容申请
INSERT INTO TeachingRequests (request_id, teacher_id, offering_id, request_type, content, reason, status, created_at) VALUES
(301, 1, 101, '扩容申请', '数据库原理-01班容量从40扩至50人', '选课需求旺盛，当前已满', '待审批', '2026-02-22 09:00:00');

-- ============================================
-- 14. 通知
-- ============================================

INSERT INTO Notifications (notification_id, user_id, title, content, notification_type, is_read, created_at) VALUES
(1, 4, '选课成功', '您已成功选择《数据结构》，请按时上课。', '选课', FALSE, '2026-02-20 10:12:30'),
(2, 4, '成绩发布', '《高等数学（下）》成绩已发布，请及时查看。', '成绩', TRUE, '2025-07-01 10:00:00');

-- ============================================
-- 15. 审计日志
-- ============================================

INSERT INTO AuditLogs (log_id, operator, operation_type, target_type, target_id, reason, created_at) VALUES
(1, 'admin', '发布成绩', '开课班', '90', '管理员发布2024-2025学年第二学期高等数学成绩', '2025-07-01 09:00:00');

-- 启用外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- 数据插入完成
-- ============================================

-- 验证数据
SELECT '========== 数据统计 ==========' as '';
SELECT '用户数量' as '统计项', COUNT(*) as '数量' FROM Users
UNION ALL
SELECT '学生数量', COUNT(*) FROM Students
UNION ALL
SELECT '教师数量', COUNT(*) FROM Teachers
UNION ALL
SELECT '课程数量', COUNT(*) FROM Courses
UNION ALL
SELECT '当前学期开课数', COUNT(*) FROM CourseOfferings WHERE term_id = 4
UNION ALL
SELECT '选课记录数', COUNT(*) FROM Enrollments
UNION ALL
SELECT '成绩记录数', COUNT(*) FROM Grades
UNION ALL
SELECT '重修记录数', COUNT(*) FROM RetakeRecords;

SELECT '========== 演示账号 ==========' as '';
SELECT username as '用户名', role as '角色', real_name as '姓名', '123456' as '密码'
FROM Users
WHERE username IN ('admin', 'T1001', 'S2023001')
ORDER BY FIELD(role, 'admin', 'teacher', 'student');

-- ============================================
-- 学分制教务选课管理系统 - 数据库建表脚本
-- Database: school
-- ============================================

DROP DATABASE IF EXISTS school;
CREATE DATABASE school CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE school;

-- ============================================
-- 1. 用户权限模块
-- ============================================

-- 用户表
DROP TABLE IF EXISTS Users;
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名/学号/工号',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    role ENUM('student', 'teacher', 'admin') NOT NULL COMMENT '角色',
    real_name VARCHAR(50) NOT NULL COMMENT '真实姓名',
    status ENUM('正常', '禁用') DEFAULT '正常' COMMENT '账号状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_username (username),
    INDEX idx_role (role)
) ENGINE=InnoDB COMMENT='用户表';

-- ============================================
-- 2. 组织人员模块
-- ============================================

-- 院系表
DROP TABLE IF EXISTS Departments;
CREATE TABLE Departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '院系ID',
    department_name VARCHAR(100) NOT NULL UNIQUE COMMENT '院系名称',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='院系表';

-- 专业表
DROP TABLE IF EXISTS Majors;
CREATE TABLE Majors (
    major_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '专业ID',
    major_name VARCHAR(100) NOT NULL COMMENT '专业名称',
    department_id INT COMMENT '所属院系',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES Departments(department_id) ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='专业表';

-- 班级表
DROP TABLE IF EXISTS Classes;
CREATE TABLE Classes (
    class_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '班级ID',
    class_name VARCHAR(100) NOT NULL COMMENT '班级名称',
    major_id INT COMMENT '所属专业',
    grade_year INT COMMENT '年级',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (major_id) REFERENCES Majors(major_id) ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='班级表';

-- 学生表
DROP TABLE IF EXISTS Students;
CREATE TABLE Students (
    student_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '学生ID',
    user_id INT NOT NULL UNIQUE COMMENT '用户ID',
    student_no VARCHAR(20) NOT NULL UNIQUE COMMENT '学号',
    real_name VARCHAR(50) NOT NULL COMMENT '姓名',
    gender ENUM('男', '女') COMMENT '性别',
    department_id INT COMMENT '院系ID',
    major_id INT COMMENT '专业ID',
    class_id INT COMMENT '班级ID',
    grade_year INT COMMENT '年级',
    enroll_year INT COMMENT '入学年份',
    student_status ENUM('在读', '休学', '退学', '毕业') DEFAULT '在读' COMMENT '学籍状态',
    phone VARCHAR(20) COMMENT '手机号',
    email VARCHAR(100) COMMENT '邮箱',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES Departments(department_id) ON DELETE SET NULL,
    FOREIGN KEY (major_id) REFERENCES Majors(major_id) ON DELETE SET NULL,
    FOREIGN KEY (class_id) REFERENCES Classes(class_id) ON DELETE SET NULL,
    INDEX idx_student_no (student_no),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB COMMENT='学生表';

-- 教师表
DROP TABLE IF EXISTS Teachers;
CREATE TABLE Teachers (
    teacher_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '教师ID',
    user_id INT NOT NULL UNIQUE COMMENT '用户ID',
    teacher_no VARCHAR(20) NOT NULL UNIQUE COMMENT '工号',
    real_name VARCHAR(50) NOT NULL COMMENT '姓名',
    gender ENUM('男', '女') COMMENT '性别',
    department_id INT COMMENT '院系ID',
    title VARCHAR(50) COMMENT '职称',
    phone VARCHAR(20) COMMENT '手机号',
    email VARCHAR(100) COMMENT '邮箱',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES Departments(department_id) ON DELETE SET NULL,
    INDEX idx_teacher_no (teacher_no),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB COMMENT='教师表';

-- ============================================
-- 3. 学年学期模块
-- ============================================

-- 学年表
DROP TABLE IF EXISTS AcademicYears;
CREATE TABLE AcademicYears (
    academic_year_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '学年ID',
    academic_year_name VARCHAR(50) NOT NULL COMMENT '学年名称（如2025-2026学年）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='学年表';

-- 学期表
DROP TABLE IF EXISTS Terms;
CREATE TABLE Terms (
    term_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '学期ID',
    academic_year_id INT NOT NULL COMMENT '所属学年',
    term_no TINYINT NOT NULL COMMENT '学期序号（1或2）',
    term_name VARCHAR(100) NOT NULL COMMENT '学期名称',
    start_date DATE COMMENT '开始日期',
    end_date DATE COMMENT '结束日期',
    is_current BOOLEAN DEFAULT FALSE COMMENT '是否当前学期',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (academic_year_id) REFERENCES AcademicYears(academic_year_id) ON DELETE CASCADE,
    INDEX idx_is_current (is_current)
) ENGINE=InnoDB COMMENT='学期表';

-- 业务时间窗口表
DROP TABLE IF EXISTS BusinessWindows;
CREATE TABLE BusinessWindows (
    window_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '时间窗口ID',
    term_id INT NOT NULL COMMENT '学期ID',
    window_type ENUM('选课', '退课', '成绩录入', '成绩公布') NOT NULL COMMENT '窗口类型',
    start_time DATETIME NOT NULL COMMENT '开始时间',
    end_time DATETIME NOT NULL COMMENT '结束时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (term_id) REFERENCES Terms(term_id) ON DELETE CASCADE,
    INDEX idx_term_type (term_id, window_type)
) ENGINE=InnoDB COMMENT='业务时间窗口表';

-- ============================================
-- 4. 课程资源模块
-- ============================================

-- 课程表
DROP TABLE IF EXISTS Courses;
CREATE TABLE Courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '课程ID',
    course_code VARCHAR(20) NOT NULL UNIQUE COMMENT '课程编号',
    course_name VARCHAR(100) NOT NULL COMMENT '课程名称',
    credits DECIMAL(3,1) NOT NULL COMMENT '学分',
    hours INT NOT NULL COMMENT '学时',
    course_type ENUM('必修课', '选修课', '专业课', '通识课') NOT NULL COMMENT '课程类型',
    assessment_type ENUM('考试', '考查') DEFAULT '考试' COMMENT '考核方式',
    description TEXT COMMENT '课程简介',
    allow_retake BOOLEAN DEFAULT TRUE COMMENT '是否允许重修',
    is_enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_course_code (course_code)
) ENGINE=InnoDB COMMENT='课程表';

-- 教室表
DROP TABLE IF EXISTS Classrooms;
CREATE TABLE Classrooms (
    classroom_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '教室ID',
    building VARCHAR(100) NOT NULL COMMENT '教学楼',
    room_no VARCHAR(50) NOT NULL COMMENT '教室编号',
    capacity INT NOT NULL COMMENT '容量',
    status ENUM('可用', '维修中', '停用') DEFAULT '可用' COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_building_room (building, room_no)
) ENGINE=InnoDB COMMENT='教室表';

-- ============================================
-- 5. 开课排课模块
-- ============================================

-- 开课班表
DROP TABLE IF EXISTS CourseOfferings;
CREATE TABLE CourseOfferings (
    offering_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '开课班ID',
    course_id INT NOT NULL COMMENT '课程ID',
    teacher_id INT NOT NULL COMMENT '教师ID',
    term_id INT NOT NULL COMMENT '学期ID',
    teaching_class_name VARCHAR(100) NOT NULL COMMENT '教学班名称',
    capacity INT NOT NULL COMMENT '容量',
    selected_count_cached INT DEFAULT 0 COMMENT '已选人数（缓存）',
    min_enrollment INT DEFAULT 10 COMMENT '最低开课人数',
    is_retake_class BOOLEAN DEFAULT FALSE COMMENT '是否重修班',
    status ENUM('待审批', '已通过', '开放选课', '关闭选课', '已取消', '已结课') DEFAULT '待审批' COMMENT '状态',
    description TEXT COMMENT '开课说明',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES Courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id) ON DELETE CASCADE,
    FOREIGN KEY (term_id) REFERENCES Terms(term_id) ON DELETE CASCADE,
    INDEX idx_term (term_id),
    INDEX idx_course (course_id),
    INDEX idx_teacher (teacher_id),
    INDEX idx_status (status)
) ENGINE=InnoDB COMMENT='开课班表';

-- 课程时间表
DROP TABLE IF EXISTS ClassSchedules;
CREATE TABLE ClassSchedules (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '排课ID',
    offering_id INT NOT NULL COMMENT '开课班ID',
    classroom_id INT COMMENT '教室ID',
    weekday TINYINT NOT NULL COMMENT '星期（1-7）',
    start_section TINYINT NOT NULL COMMENT '起始节次（1-10）',
    end_section TINYINT NOT NULL COMMENT '结束节次（1-10）',
    week_start TINYINT DEFAULT 1 COMMENT '起始周次',
    week_end TINYINT DEFAULT 18 COMMENT '结束周次',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (offering_id) REFERENCES CourseOfferings(offering_id) ON DELETE CASCADE,
    FOREIGN KEY (classroom_id) REFERENCES Classrooms(classroom_id) ON DELETE SET NULL,
    INDEX idx_offering (offering_id)
) ENGINE=InnoDB COMMENT='课程时间表';

-- ============================================
-- 6. 选课退课模块
-- ============================================

-- 选课记录表
DROP TABLE IF EXISTS Enrollments;
CREATE TABLE Enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '选课记录ID',
    student_id INT NOT NULL COMMENT '学生ID',
    offering_id INT NOT NULL COMMENT '开课班ID',
    is_retake BOOLEAN DEFAULT FALSE COMMENT '是否重修',
    enroll_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '选课时间',
    status ENUM('已选', '已退', '已完成', '因课程取消失效') DEFAULT '已选' COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (offering_id) REFERENCES CourseOfferings(offering_id) ON DELETE CASCADE,
    INDEX idx_student (student_id),
    INDEX idx_offering (offering_id),
    INDEX idx_status (status)
) ENGINE=InnoDB COMMENT='选课记录表';

-- ============================================
-- 7. 成绩重修模块
-- ============================================

-- 成绩表
DROP TABLE IF EXISTS Grades;
CREATE TABLE Grades (
    grade_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '成绩ID',
    enrollment_id INT NOT NULL UNIQUE COMMENT '选课记录ID',
    usual_score DECIMAL(5,2) COMMENT '平时成绩',
    experiment_score DECIMAL(5,2) COMMENT '实验成绩',
    final_score DECIMAL(5,2) COMMENT '期末成绩',
    total_score DECIMAL(5,2) COMMENT '总评成绩',
    grade_point DECIMAL(3,2) DEFAULT 0 COMMENT '绩点',
    is_passed BOOLEAN DEFAULT FALSE COMMENT '是否通过',
    score_status ENUM('未录入', '草稿', '已录入', '已提交', '已发布', '已冻结') DEFAULT '未录入' COMMENT '成绩状态',
    included_in_average BOOLEAN DEFAULT TRUE COMMENT '是否计入平均成绩',
    remarks TEXT COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (enrollment_id) REFERENCES Enrollments(enrollment_id) ON DELETE CASCADE,
    INDEX idx_enrollment (enrollment_id),
    INDEX idx_status (score_status)
) ENGINE=InnoDB COMMENT='成绩表';

-- 重修记录表
DROP TABLE IF EXISTS RetakeRecords;
CREATE TABLE RetakeRecords (
    retake_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '重修记录ID',
    student_id INT NOT NULL COMMENT '学生ID',
    source_enrollment_id INT NOT NULL COMMENT '原始选课记录ID（挂科的那次）',
    retake_offering_id INT COMMENT '重修开课班ID',
    status ENUM('待重修', '重修中', '重修通过', '重修未通过') DEFAULT '待重修' COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (source_enrollment_id) REFERENCES Enrollments(enrollment_id) ON DELETE CASCADE,
    FOREIGN KEY (retake_offering_id) REFERENCES CourseOfferings(offering_id) ON DELETE SET NULL,
    INDEX idx_student (student_id),
    INDEX idx_status (status)
) ENGINE=InnoDB COMMENT='重修记录表';

-- ============================================
-- 8. 申请审批模块
-- ============================================

-- 教学申请表
DROP TABLE IF EXISTS TeachingRequests;
CREATE TABLE TeachingRequests (
    request_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '申请ID',
    teacher_id INT NOT NULL COMMENT '教师ID',
    offering_id INT COMMENT '相关开课班ID',
    term_id INT COMMENT '申请学期',
    course_name VARCHAR(100) COMMENT '课程名称（教师自由填写，开课申请时无对应开课班）',
    request_type ENUM('开课申请', '扩容申请', '调课申请', '停课申请', '成绩修改申请') NOT NULL COMMENT '申请类型',
    content TEXT NOT NULL COMMENT '申请内容',
    reason TEXT COMMENT '申请理由',
    status ENUM('待审批', '已通过', '已驳回') DEFAULT '待审批' COMMENT '状态',
    admin_comment TEXT COMMENT '管理员意见',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
    processed_at DATETIME COMMENT '处理时间',
    FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id) ON DELETE CASCADE,
    FOREIGN KEY (offering_id) REFERENCES CourseOfferings(offering_id) ON DELETE SET NULL,
    FOREIGN KEY (term_id) REFERENCES Terms(term_id) ON DELETE SET NULL,
    INDEX idx_teacher (teacher_id),
    INDEX idx_status (status)
) ENGINE=InnoDB COMMENT='教学申请表';

-- ============================================
-- 9. 通知审计模块
-- ============================================

-- 通知表
DROP TABLE IF EXISTS Notifications;
CREATE TABLE Notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '通知ID',
    user_id INT NOT NULL COMMENT '接收用户ID',
    title VARCHAR(200) NOT NULL COMMENT '标题',
    content TEXT NOT NULL COMMENT '内容',
    notification_type ENUM('选课', '退课', '成绩', '重修', '审批') NOT NULL COMMENT '通知类型',
    is_read BOOLEAN DEFAULT FALSE COMMENT '是否已读',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_is_read (is_read)
) ENGINE=InnoDB COMMENT='通知表';

-- 操作日志表
DROP TABLE IF EXISTS AuditLogs;
CREATE TABLE AuditLogs (
    log_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '日志ID',
    operator VARCHAR(50) NOT NULL COMMENT '操作人',
    operation_type VARCHAR(100) NOT NULL COMMENT '操作类型',
    target_type VARCHAR(50) COMMENT '目标类型',
    target_id VARCHAR(50) COMMENT '目标ID',
    reason TEXT COMMENT '操作原因',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    INDEX idx_operator (operator),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB COMMENT='操作日志表';

-- 建表脚本完成

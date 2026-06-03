// ============================================================================
// Mock 数据层
// ----------------------------------------------------------------------------
// 前端在后端尚未就绪时使用本文件提供的假数据跑通全部页面。
// 联调阶段把 services.js 中的 USE_MOCK 置为 false 即可切换到真实接口，
// 本文件可以保留作为接口返回结构的参考。
// ============================================================================

// 当前学年学期
export const currentTerm = {
    term_id: 4,
    term_name: '2025-2026学年第二学期',
    academic_year_name: '2025-2026学年',
    term_no: 2,
    is_current: true,
}

// 节次定义（用于课表）
export const sections = [
    { no: 1, time: '08:00-08:45' },
    { no: 2, time: '08:55-09:40' },
    { no: 3, time: '10:00-10:45' },
    { no: 4, time: '10:55-11:40' },
    { no: 5, time: '13:30-14:15' },
    { no: 6, time: '14:25-15:10' },
    { no: 7, time: '15:30-16:15' },
    { no: 8, time: '16:25-17:10' },
    { no: 9, time: '18:30-19:15' },
    { no: 10, time: '19:25-20:10' },
]

export const weekdayNames = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日']

// 演示账号（登录页提示用）
export const demoAccounts = [
    { role: 'student', username: 'S2023001', password: '123456', real_name: '张小明' },
    { role: 'teacher', username: 'T1001', password: '123456', real_name: '李教授' },
    { role: 'admin', username: 'admin', password: '123456', real_name: '系统管理员' },
]

// 当前登录用户的个人信息（按角色）
export const profiles = {
    student: {
        student_no: 'S2023001',
        real_name: '张小明',
        gender: '男',
        department_name: '计算机学院',
        major_name: '软件工程',
        class_name: '软工2301班',
        grade_year: 2023,
        enroll_year: 2023,
        student_status: '在读',
        phone: '13800000001',
        email: 'zhangxm@shu.edu.cn',
    },
    teacher: {
        teacher_no: 'T1001',
        real_name: '李教授',
        gender: '男',
        department_name: '计算机学院',
        title: '教授',
        phone: '13900000001',
        email: 'lijs@shu.edu.cn',
    },
    admin: {
        username: 'admin',
        real_name: '系统管理员',
        role_name: '系统管理员',
        phone: '13700000001',
        email: 'admin@shu.edu.cn',
    },
}

// ---------------------------------------------------------------------------
// 学生端：可选课程（开课班）
// status 提示：available 可选 / selected 已选 / full 已满 / conflict 时间冲突 /
//             passed 已通过不可选 / retake 待重修可选
// ---------------------------------------------------------------------------
export const availableCourses = [
    {
        offering_id: 101,
        course_code: 'CS201',
        course_name: '数据库原理',
        credits: 3.5,
        hours: 64,
        course_type: '必修课',
        teacher_name: '李教授',
        teaching_class_name: '数据库原理-01班',
        schedule_text: '周一 1-2节 / 周三 3-4节',
        location: '东区教学楼 A305',
        capacity: 40,
        selected_count: 38,
        is_retake_class: false,
        select_status: 'available',
        description: '系统讲授关系数据库理论、SQL、事务、索引与查询优化。',
        assessment_type: '考试',
    },
    {
        offering_id: 102,
        course_code: 'CS305',
        course_name: '操作系统',
        credits: 4.0,
        hours: 72,
        course_type: '必修课',
        teacher_name: '王老师',
        teaching_class_name: '操作系统-01班',
        schedule_text: '周二 3-4节 / 周四 1-2节',
        location: '东区教学楼 B201',
        capacity: 40,
        selected_count: 40,
        is_retake_class: false,
        select_status: 'full',
        description: '进程管理、内存管理、文件系统、I/O 与并发控制。',
        assessment_type: '考试',
    },
    {
        offering_id: 103,
        course_code: 'CS210',
        course_name: '计算机网络',
        credits: 3.0,
        hours: 56,
        course_type: '必修课',
        teacher_name: '赵老师',
        teaching_class_name: '计算机网络-01班',
        schedule_text: '周一 1-2节 / 周五 5-6节',
        location: '东区教学楼 A210',
        capacity: 45,
        selected_count: 20,
        is_retake_class: false,
        select_status: 'conflict',
        description: '五层模型、TCP/IP、路由与拥塞控制。',
        assessment_type: '考试',
    },
    {
        offering_id: 104,
        course_code: 'GE101',
        course_name: '大学英语（四）',
        credits: 2.0,
        hours: 36,
        course_type: '通识课',
        teacher_name: '陈老师',
        teaching_class_name: '大学英语四-03班',
        schedule_text: '周三 5-6节',
        location: '西区外语楼 301',
        capacity: 60,
        selected_count: 45,
        is_retake_class: false,
        select_status: 'available',
        description: '听说读写综合训练，对接四级考试。',
        assessment_type: '考查',
    },
    {
        offering_id: 105,
        course_code: 'CS150',
        course_name: '高等数学（下）',
        credits: 5.0,
        hours: 80,
        course_type: '必修课',
        teacher_name: '孙老师',
        teaching_class_name: '高数下-重修班',
        schedule_text: '周四 7-8节',
        location: '东区教学楼 C101',
        capacity: 50,
        selected_count: 12,
        is_retake_class: true,
        select_status: 'retake',
        description: '面向上学期挂科学生开设的重修班。',
        assessment_type: '考试',
    },
    {
        offering_id: 106,
        course_code: 'CS220',
        course_name: '数据结构',
        credits: 4.0,
        hours: 72,
        course_type: '必修课',
        teacher_name: '李教授',
        teaching_class_name: '数据结构-02班',
        schedule_text: '周五 1-2节',
        location: '东区教学楼 A305',
        capacity: 40,
        selected_count: 30,
        is_retake_class: false,
        select_status: 'passed',
        description: '线性表、树、图、排序与查找算法。',
        assessment_type: '考试',
    },
]

// 学生已选课程
export const myCourses = [
    {
        enrollment_id: 5001,
        offering_id: 101,
        course_code: 'CS201',
        course_name: '数据库原理',
        credits: 3.5,
        teacher_name: '李教授',
        schedule_text: '周一 1-2节 / 周三 3-4节',
        location: '东区教学楼 A305',
        is_retake: false,
        enroll_time: '2026-02-20T10:12:00',
        status: '已选',
        can_drop: true,
    },
    {
        enrollment_id: 5002,
        offering_id: 104,
        course_code: 'GE101',
        course_name: '大学英语（四）',
        credits: 2.0,
        teacher_name: '陈老师',
        schedule_text: '周三 5-6节',
        location: '西区外语楼 301',
        is_retake: false,
        enroll_time: '2026-02-20T10:15:00',
        status: '已选',
        can_drop: true,
    },
    {
        enrollment_id: 5003,
        offering_id: 105,
        course_code: 'CS150',
        course_name: '高等数学（下）',
        credits: 5.0,
        teacher_name: '孙老师',
        schedule_text: '周四 7-8节',
        location: '东区教学楼 C101',
        is_retake: true,
        enroll_time: '2026-02-21T09:02:00',
        status: '已选',
        can_drop: false, // 重修班已锁定
    },
]

// 学生课表条目（weekday 1-7, section 节次）
export const timetable = [
    { offering_id: 101, course_name: '数据库原理', teacher_name: '李教授', location: 'A305', weekday: 1, start_section: 1, end_section: 2 },
    { offering_id: 101, course_name: '数据库原理', teacher_name: '李教授', location: 'A305', weekday: 3, start_section: 3, end_section: 4 },
    { offering_id: 104, course_name: '大学英语（四）', teacher_name: '陈老师', location: '外语楼301', weekday: 3, start_section: 5, end_section: 6 },
    { offering_id: 105, course_name: '高等数学（下）[重修]', teacher_name: '孙老师', location: 'C101', weekday: 4, start_section: 7, end_section: 8 },
]

// 学生成绩
export const grades = [
    { grade_id: 9001, term_name: '2024-2025学年第二学期', course_name: '高等数学（下）', credits: 5.0, teacher_name: '孙老师', total_score: 52, grade_point: 0, is_passed: false, is_retake: false, included_in_average: true, score_status: '已发布' },
    { grade_id: 9002, term_name: '2024-2025学年第二学期', course_name: '线性代数', credits: 3.0, teacher_name: '周老师', total_score: 88, grade_point: 3.7, is_passed: true, is_retake: false, included_in_average: true, score_status: '已发布' },
    { grade_id: 9003, term_name: '2024-2025学年第二学期', course_name: '数据结构', credits: 4.0, teacher_name: '李教授', total_score: 91, grade_point: 4.0, is_passed: true, is_retake: false, included_in_average: true, score_status: '已发布' },
    { grade_id: 9004, term_name: '2025-2026学年第一学期', course_name: '面向对象程序设计', credits: 3.5, teacher_name: '吴老师', total_score: 76, grade_point: 2.7, is_passed: true, is_retake: false, included_in_average: true, score_status: '已发布' },
    { grade_id: 9005, term_name: '2025-2026学年第一学期', course_name: '概率论与数理统计', credits: 3.0, teacher_name: '郑老师', total_score: 83, grade_point: 3.3, is_passed: true, is_retake: false, included_in_average: true, score_status: '已发布' },
]

// 学生平均成绩统计
export const averageScore = {
    simple_average: 78.0,
    weighted_average: 79.6,
    average_gpa: 2.74,
    total_credits: 18.5,
    earned_credits: 13.5,
}

// 学生挂科与重修
export const retakeStatus = [
    { retake_id: 7001, course_name: '高等数学（下）', source_term: '2024-2025学年第二学期', source_score: 52, status: '重修中', current_offering: '高数下-重修班（本学期）' },
]

// 通知
export const notifications = [
    { notification_id: 1, title: '选课成功', content: '您已成功选择《数据库原理》，请按时上课。', notification_type: '选课', is_read: false, created_at: '2026-02-20T10:12:30' },
    { notification_id: 2, title: '重修提醒', content: '您有 1 门课程（高等数学下）处于待重修状态，本学期已开设重修班。', notification_type: '重修', is_read: false, created_at: '2026-02-18T09:00:00' },
    { notification_id: 3, title: '成绩发布', content: '2025-2026学年第一学期成绩已发布，请查看。', notification_type: '成绩', is_read: true, created_at: '2026-01-15T16:00:00' },
]

// ---------------------------------------------------------------------------
// 教师端
// ---------------------------------------------------------------------------
export const teacherOfferings = [
    { offering_id: 101, course_code: 'CS201', course_name: '数据库原理', term_name: '2025-2026学年第二学期', teaching_class_name: '数据库原理-01班', schedule_text: '周一 1-2节 / 周三 3-4节', location: 'A305', capacity: 40, selected_count: 38, is_retake_class: false, status: '开放选课' },
    { offering_id: 106, course_code: 'CS220', course_name: '数据结构', term_name: '2025-2026学年第二学期', teaching_class_name: '数据结构-02班', schedule_text: '周五 1-2节', location: 'A305', capacity: 40, selected_count: 30, is_retake_class: false, status: '开放选课' },
    { offering_id: 90, course_code: 'CS220', course_name: '数据结构', term_name: '2024-2025学年第二学期', teaching_class_name: '数据结构-01班', schedule_text: '周二 1-2节', location: 'A301', capacity: 40, selected_count: 40, is_retake_class: false, status: '已结课' },
]

// 某开课班的学生名单（key: offering_id）
export const rosters = {
    101: [
        { student_no: 'S2023001', real_name: '张小明', major_name: '软件工程', class_name: '软工2301班', is_retake: false, enroll_time: '2026-02-20T10:12:00', score_status: '未录入' },
        { student_no: 'S2023002', real_name: '王丽', major_name: '软件工程', class_name: '软工2301班', is_retake: false, enroll_time: '2026-02-20T10:13:00', score_status: '未录入' },
        { student_no: 'S2023015', real_name: '陈强', major_name: '计算机科学与技术', class_name: '计科2301班', is_retake: true, enroll_time: '2026-02-20T11:02:00', score_status: '未录入' },
    ],
    106: [
        { student_no: 'S2024001', real_name: '刘洋', major_name: '软件工程', class_name: '软工2401班', is_retake: false, enroll_time: '2026-02-21T08:30:00', score_status: '未录入' },
        { student_no: 'S2024008', real_name: '赵敏', major_name: '软件工程', class_name: '软工2401班', is_retake: false, enroll_time: '2026-02-21T08:35:00', score_status: '未录入' },
    ],
}

// 成绩录入表（key: offering_id）—— 含平时/实验/期末/总评
export const gradeSheets = {
    101: [
        { enrollment_id: 5001, student_no: 'S2023001', real_name: '张小明', usual_score: 85, experiment_score: 90, final_score: 80, total_score: 83, score_status: '草稿' },
        { enrollment_id: 5101, student_no: 'S2023002', real_name: '王丽', usual_score: 90, experiment_score: 88, final_score: 92, total_score: 90, score_status: '草稿' },
        { enrollment_id: 5102, student_no: 'S2023015', real_name: '陈强', usual_score: 60, experiment_score: 55, final_score: 50, total_score: 54, score_status: '草稿' },
    ],
    106: [
        { enrollment_id: 5201, student_no: 'S2024001', real_name: '刘洋', usual_score: null, experiment_score: null, final_score: null, total_score: null, score_status: '未录入' },
        { enrollment_id: 5202, student_no: 'S2024008', real_name: '赵敏', usual_score: null, experiment_score: null, final_score: null, total_score: null, score_status: '未录入' },
    ],
}

// 教师申请记录
export const teacherRequests = [
    { request_id: 301, request_type: '扩容申请', course_name: '数据库原理', term_name: '2025-2026学年第二学期', content: '当前 40/40 已满，申请扩容至 50 人', reason: '选课需求旺盛', status: '待审批', created_at: '2026-02-22T09:00:00' },
    { request_id: 302, request_type: '调课申请', course_name: '数据结构', term_name: '2025-2026学年第二学期', content: '周五1-2节 → 周四3-4节', reason: '与学院会议冲突', status: '已通过', created_at: '2026-02-19T14:00:00' },
    { request_id: 303, request_type: '开课申请', course_name: '数据库系统实现', term_name: '2025-2026学年第二学期', content: '容量40，周二5-6节，A305', reason: '新增专业选修课', status: '已驳回', created_at: '2026-02-10T10:00:00' },
]

// 教师成绩统计（按开课班）
export const teacherGradeStats = [
    { offering_id: 90, course_name: '数据结构', teaching_class_name: '数据结构-01班', enrolled: 40, attended: 40, passed: 36, failed: 4, avg: 78.5, max: 96, min: 41, fail_rate: 10.0, retake_count: 4 },
]

// ---------------------------------------------------------------------------
// 管理员端
// ---------------------------------------------------------------------------
export const adminStats = {
    cards: {
        total_students: 1280,
        total_teachers: 96,
        total_courses: 64,
        total_offerings: 38,
    },
    capacity: [
        { course_name: '数据库原理', teacher_name: '李教授', capacity: 40, selected_count: 38, remain: 2, fill_rate: 95 },
        { course_name: '操作系统', teacher_name: '王老师', capacity: 40, selected_count: 40, remain: 0, fill_rate: 100 },
        { course_name: '计算机网络', teacher_name: '赵老师', capacity: 45, selected_count: 20, remain: 25, fill_rate: 44 },
        { course_name: '大学英语（四）', teacher_name: '陈老师', capacity: 60, selected_count: 45, remain: 15, fill_rate: 75 },
        { course_name: '高等数学（下）[重修]', teacher_name: '孙老师', capacity: 50, selected_count: 12, remain: 38, fill_rate: 24 },
    ],
    score_distribution: [
        { range: '90-100', count: 120 },
        { range: '80-89', count: 260 },
        { range: '70-79', count: 310 },
        { range: '60-69', count: 180 },
        { range: '0-59', count: 60 },
    ],
    retake: [
        { course_name: '高等数学（下）', failed: 60, pending_retake: 45, retaking: 12, passed_retake: 30 },
        { course_name: '大学物理', failed: 38, pending_retake: 20, retaking: 8, passed_retake: 18 },
    ],
}

export const adminUsers = [
    { user_id: 1, username: 'admin', real_name: '系统管理员', role: 'admin', role_name: '管理员', phone: '13700000001', status: '正常' },
    { user_id: 2, username: 'T1001', real_name: '李教授', role: 'teacher', role_name: '教师', phone: '13900000001', status: '正常' },
    { user_id: 3, username: 'T1002', real_name: '王老师', role: 'teacher', role_name: '教师', phone: '13900000002', status: '正常' },
    { user_id: 4, username: 'S2023001', real_name: '张小明', role: 'student', role_name: '学生', phone: '13800000001', status: '正常' },
    { user_id: 5, username: 'S2023002', real_name: '王丽', role: 'student', role_name: '学生', phone: '13800000002', status: '正常' },
    { user_id: 6, username: 'S2023015', real_name: '陈强', role: 'student', role_name: '学生', phone: '13800000015', status: '禁用' },
]

export const adminTerms = [
    { academic_year_name: '2025-2026学年', terms: [
        { term_id: 3, term_no: 1, term_name: '2025-2026学年第一学期', start_date: '2025-09-01', end_date: '2026-01-18', is_current: false },
        { term_id: 4, term_no: 2, term_name: '2025-2026学年第二学期', start_date: '2026-02-24', end_date: '2026-07-05', is_current: true },
    ]},
    { academic_year_name: '2024-2025学年', terms: [
        { term_id: 1, term_no: 1, term_name: '2024-2025学年第一学期', start_date: '2024-09-02', end_date: '2025-01-19', is_current: false },
        { term_id: 2, term_no: 2, term_name: '2024-2025学年第二学期', start_date: '2025-02-24', end_date: '2025-07-06', is_current: false },
    ]},
]

export const businessWindows = [
    { window_id: 1, term_name: '2025-2026学年第二学期', window_type: '选课', start_time: '2026-02-18T09:00:00', end_time: '2026-03-01T22:00:00', status: '进行中' },
    { window_id: 2, term_name: '2025-2026学年第二学期', window_type: '退课', start_time: '2026-02-18T09:00:00', end_time: '2026-03-08T22:00:00', status: '进行中' },
    { window_id: 3, term_name: '2025-2026学年第二学期', window_type: '成绩录入', start_time: '2026-06-20T00:00:00', end_time: '2026-07-05T22:00:00', status: '未开始' },
    { window_id: 4, term_name: '2025-2026学年第二学期', window_type: '成绩公布', start_time: '2026-07-08T00:00:00', end_time: '2026-07-15T22:00:00', status: '未开始' },
]

export const adminCourses = [
    { course_id: 1, course_code: 'CS201', course_name: '数据库原理', credits: 3.5, hours: 64, course_type: '必修课', assessment_type: '考试', allow_retake: true, is_enabled: true },
    { course_id: 2, course_code: 'CS305', course_name: '操作系统', credits: 4.0, hours: 72, course_type: '必修课', assessment_type: '考试', allow_retake: true, is_enabled: true },
    { course_id: 3, course_code: 'CS210', course_name: '计算机网络', credits: 3.0, hours: 56, course_type: '必修课', assessment_type: '考试', allow_retake: true, is_enabled: true },
    { course_id: 4, course_code: 'CS150', course_name: '高等数学（下）', credits: 5.0, hours: 80, course_type: '必修课', assessment_type: '考试', allow_retake: true, is_enabled: true },
    { course_id: 5, course_code: 'GE101', course_name: '大学英语（四）', credits: 2.0, hours: 36, course_type: '通识课', assessment_type: '考查', allow_retake: true, is_enabled: true },
]

export const adminClassrooms = [
    { classroom_id: 1, building: '东区教学楼', room_no: 'A305', capacity: 60, status: '可用' },
    { classroom_id: 2, building: '东区教学楼', room_no: 'B201', capacity: 45, status: '可用' },
    { classroom_id: 3, building: '东区教学楼', room_no: 'C101', capacity: 120, status: '可用' },
    { classroom_id: 4, building: '西区外语楼', room_no: '301', capacity: 80, status: '维修中' },
]

export const adminOfferings = [
    { offering_id: 101, course_name: '数据库原理', teacher_name: '李教授', term_name: '2025-2026学年第二学期', teaching_class_name: '数据库原理-01班', capacity: 40, selected_count: 38, min_enrollment: 10, is_retake_class: false, status: '开放选课' },
    { offering_id: 102, course_name: '操作系统', teacher_name: '王老师', term_name: '2025-2026学年第二学期', teaching_class_name: '操作系统-01班', capacity: 40, selected_count: 40, min_enrollment: 10, is_retake_class: false, status: '开放选课' },
    { offering_id: 103, course_name: '计算机网络', teacher_name: '赵老师', term_name: '2025-2026学年第二学期', teaching_class_name: '计算机网络-01班', capacity: 45, selected_count: 20, min_enrollment: 25, is_retake_class: false, status: '开放选课' },
    { offering_id: 105, course_name: '高等数学（下）', teacher_name: '孙老师', term_name: '2025-2026学年第二学期', teaching_class_name: '高数下-重修班', capacity: 50, selected_count: 12, min_enrollment: 5, is_retake_class: true, status: '开放选课' },
]

export const adminApprovals = [
    { request_id: 301, teacher_name: '李教授', request_type: '扩容申请', course_name: '数据库原理', term_name: '2025-2026学年第二学期', content: '40 → 50 人', conflict_check_result: '教室容量充足（A305=60），无冲突', status: '待审批', created_at: '2026-02-22T09:00:00' },
    { request_id: 304, teacher_name: '王老师', request_type: '开课申请', course_name: '分布式系统', term_name: '2025-2026学年第二学期', content: '容量40，周三7-8节，B201', conflict_check_result: '教师周三7-8节无冲突，教室空闲', status: '待审批', created_at: '2026-02-23T10:30:00' },
    { request_id: 305, teacher_name: '李教授', request_type: '成绩修改申请', course_name: '数据结构', term_name: '2024-2025学年第二学期', content: '陈强：54 → 61（漏登实验分）', conflict_check_result: '—', status: '待审批', created_at: '2026-02-23T15:00:00' },
]

// 待发布成绩（管理员）
export const adminGradePublish = [
    { offering_id: 90, course_name: '数据结构', teacher_name: '李教授', term_name: '2024-2025学年第二学期', submitted_count: 40, total_count: 40, score_status: '已提交', can_publish: true },
    { offering_id: 95, course_name: '线性代数', teacher_name: '周老师', term_name: '2024-2025学年第二学期', submitted_count: 38, total_count: 40, score_status: '录入中', can_publish: false },
]

// 重修管理
export const adminRetake = [
    { course_name: '高等数学（下）', failed_count: 60, pending_count: 45, retaking_count: 12, passed_count: 30, has_retake_class: true },
    { course_name: '大学物理', failed_count: 38, pending_count: 20, retaking_count: 8, passed_count: 18, has_retake_class: false },
]

// 操作日志
export const auditLogs = [
    { log_id: 1, operator: 'admin', operation_type: '强制退课', target_type: '选课记录', target_id: '5099', reason: '学生休学，特殊处理', created_at: '2026-02-22T16:20:00' },
    { log_id: 2, operator: 'admin', operation_type: '发布成绩', target_type: '开课班', target_id: '90', reason: '2024-2025第二学期数据结构成绩发布', created_at: '2026-01-15T15:55:00' },
    { log_id: 3, operator: 'admin', operation_type: '审批通过', target_type: '调课申请', target_id: '302', reason: '无冲突，同意调课', created_at: '2026-02-19T14:30:00' },
    { log_id: 4, operator: 'admin', operation_type: '取消开课', target_type: '开课班', target_id: '120', reason: '选课人数 3 低于最低开课人数 10', created_at: '2026-03-02T09:10:00' },
]

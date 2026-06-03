-- ============================================
-- 学分制教务选课管理系统 - 存储过程和触发器
-- ============================================

USE school;

DELIMITER $$

-- ============================================
-- 1. 触发器：更新开课班选课人数缓存
-- ============================================

DROP TRIGGER IF EXISTS trg_UpdateOfferingSelectedCount$$

CREATE TRIGGER trg_UpdateOfferingSelectedCount
AFTER INSERT ON Enrollments
FOR EACH ROW
BEGIN
    UPDATE CourseOfferings
    SET selected_count_cached = (
        SELECT COUNT(*) FROM Enrollments
        WHERE offering_id = NEW.offering_id
        AND status IN ('已选', '已完成')
    )
    WHERE offering_id = NEW.offering_id;
END$$

DROP TRIGGER IF EXISTS trg_UpdateOfferingSelectedCount_Update$$

CREATE TRIGGER trg_UpdateOfferingSelectedCount_Update
AFTER UPDATE ON Enrollments
FOR EACH ROW
BEGIN
    UPDATE CourseOfferings
    SET selected_count_cached = (
        SELECT COUNT(*) FROM Enrollments
        WHERE offering_id = NEW.offering_id
        AND status IN ('已选', '已完成')
    )
    WHERE offering_id = NEW.offering_id;
END$$

DROP TRIGGER IF EXISTS trg_UpdateOfferingSelectedCount_Delete$$

CREATE TRIGGER trg_UpdateOfferingSelectedCount_Delete
AFTER DELETE ON Enrollments
FOR EACH ROW
BEGIN
    UPDATE CourseOfferings
    SET selected_count_cached = (
        SELECT COUNT(*) FROM Enrollments
        WHERE offering_id = OLD.offering_id
        AND status IN ('已选', '已完成')
    )
    WHERE offering_id = OLD.offering_id;
END$$

-- ============================================
-- 2. 存储过程：学生选课
-- ============================================

DROP PROCEDURE IF EXISTS sp_StudentSelectCourse$$

CREATE PROCEDURE sp_StudentSelectCourse(
    IN p_student_id INT,
    IN p_offering_id INT
)
BEGIN
    DECLARE v_term_id INT;
    DECLARE v_course_id INT;
    DECLARE v_course_code VARCHAR(20);
    DECLARE v_capacity INT;
    DECLARE v_current_count INT;
    DECLARE v_student_status VARCHAR(20);
    DECLARE v_offering_status VARCHAR(20);
    DECLARE v_window_count INT;
    DECLARE v_existing_count INT;
    DECLARE v_passed_count INT;
    DECLARE v_conflict_count INT;

    -- 检查学生是否存在且学籍正常
    SELECT student_status INTO v_student_status
    FROM Students WHERE student_id = p_student_id;

    IF v_student_status IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '学生不存在';
    END IF;

    IF v_student_status != '在读' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '学籍状态异常，无法选课';
    END IF;

    -- 检查开课班是否存在
    SELECT term_id, course_id, capacity, status
    INTO v_term_id, v_course_id, v_capacity, v_offering_status
    FROM CourseOfferings WHERE offering_id = p_offering_id;

    IF v_course_id IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '开课班不存在';
    END IF;

    IF v_offering_status != '开放选课' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '该课程未开放选课';
    END IF;

    -- 检查选课时间窗口
    SELECT COUNT(*) INTO v_window_count
    FROM BusinessWindows
    WHERE term_id = v_term_id
    AND window_type = '选课'
    AND NOW() BETWEEN start_time AND end_time;

    IF v_window_count = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '不在选课时间内';
    END IF;

    -- 检查容量（实时统计）
    SELECT COUNT(*) INTO v_current_count
    FROM Enrollments
    WHERE offering_id = p_offering_id
    AND status IN ('已选', '已完成');

    IF v_current_count >= v_capacity THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '课程已满';
    END IF;

    -- 获取课程编号
    SELECT course_code INTO v_course_code
    FROM Courses WHERE course_id = v_course_id;

    -- 检查是否已选过该课程（同学期）
    SELECT COUNT(*) INTO v_existing_count
    FROM Enrollments e
    JOIN CourseOfferings co ON e.offering_id = co.offering_id
    JOIN Courses c ON co.course_id = c.course_id
    WHERE e.student_id = p_student_id
    AND co.term_id = v_term_id
    AND c.course_code = v_course_code
    AND e.status = '已选';

    IF v_existing_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '已选过该课程';
    END IF;

    -- 检查是否已通过该课程
    SELECT COUNT(*) INTO v_passed_count
    FROM Grades g
    JOIN Enrollments e ON g.enrollment_id = e.enrollment_id
    JOIN CourseOfferings co ON e.offering_id = co.offering_id
    JOIN Courses c ON co.course_id = c.course_id
    WHERE e.student_id = p_student_id
    AND c.course_code = v_course_code
    AND g.is_passed = TRUE;

    IF v_passed_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '该课程你已通过，无需重选';
    END IF;

    -- 检查时间冲突
    SELECT COUNT(*) INTO v_conflict_count
    FROM Enrollments e
    JOIN ClassSchedules cs1 ON e.offering_id = cs1.offering_id
    JOIN ClassSchedules cs2 ON cs2.offering_id = p_offering_id
    WHERE e.student_id = p_student_id
    AND e.status = '已选'
    AND cs1.weekday = cs2.weekday
    AND cs1.start_section <= cs2.end_section
    AND cs1.end_section >= cs2.start_section;

    IF v_conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '上课时间冲突';
    END IF;

    -- 选课成功：插入选课记录
    INSERT INTO Enrollments (student_id, offering_id, is_retake, status)
    VALUES (p_student_id, p_offering_id, FALSE, '已选');

    -- 发送通知（可选）
    INSERT INTO Notifications (user_id, title, content, notification_type)
    SELECT u.user_id, '选课成功',
           CONCAT('您已成功选择《', c.course_name, '》'),
           '选课'
    FROM Students s
    JOIN Users u ON s.user_id = u.user_id
    JOIN Courses c ON c.course_id = v_course_id
    WHERE s.student_id = p_student_id;

END$$

-- ============================================
-- 3. 存储过程：学生退课
-- ============================================

DROP PROCEDURE IF EXISTS sp_StudentDropCourse$$

CREATE PROCEDURE sp_StudentDropCourse(
    IN p_student_id INT,
    IN p_offering_id INT
)
BEGIN
    DECLARE v_enrollment_id INT;
    DECLARE v_term_id INT;
    DECLARE v_window_count INT;
    DECLARE v_grade_status VARCHAR(20);

    -- 查找选课记录
    SELECT e.enrollment_id, co.term_id
    INTO v_enrollment_id, v_term_id
    FROM Enrollments e
    JOIN CourseOfferings co ON e.offering_id = co.offering_id
    WHERE e.student_id = p_student_id
    AND e.offering_id = p_offering_id
    AND e.status = '已选';

    IF v_enrollment_id IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '未找到有效的选课记录';
    END IF;

    -- 检查退课时间窗口
    SELECT COUNT(*) INTO v_window_count
    FROM BusinessWindows
    WHERE term_id = v_term_id
    AND window_type = '退课'
    AND NOW() BETWEEN start_time AND end_time;

    IF v_window_count = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '不在退课时间内';
    END IF;

    -- 检查是否已录成绩
    SELECT score_status INTO v_grade_status
    FROM Grades WHERE enrollment_id = v_enrollment_id;

    IF v_grade_status IS NOT NULL AND v_grade_status != '未录入' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '已录入成绩，无法退课';
    END IF;

    -- 退课成功：更新状态
    UPDATE Enrollments
    SET status = '已退'
    WHERE enrollment_id = v_enrollment_id;

    -- 发送通知
    INSERT INTO Notifications (user_id, title, content, notification_type)
    SELECT u.user_id, '退课成功', '退课操作已完成', '退课'
    FROM Students s
    JOIN Users u ON s.user_id = u.user_id
    WHERE s.student_id = p_student_id;

END$$

-- ============================================
-- 4. 存储过程：教师提交成绩
-- ============================================

DROP PROCEDURE IF EXISTS sp_TeacherSubmitGrade$$

CREATE PROCEDURE sp_TeacherSubmitGrade(
    IN p_offering_id INT
)
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_enrollment_id INT;
    DECLARE v_usual DECIMAL(5,2);
    DECLARE v_experiment DECIMAL(5,2);
    DECLARE v_final DECIMAL(5,2);
    DECLARE v_total DECIMAL(5,2);
    DECLARE v_is_passed BOOLEAN;
    DECLARE v_grade_point DECIMAL(3,2);

    DECLARE cur CURSOR FOR
        SELECT e.enrollment_id, g.usual_score, g.experiment_score, g.final_score
        FROM Enrollments e
        LEFT JOIN Grades g ON e.enrollment_id = g.enrollment_id
        WHERE e.offering_id = p_offering_id AND e.status = '已选';

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO v_enrollment_id, v_usual, v_experiment, v_final;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- 计算总评（平时30% + 实验20% + 期末50%）
        IF v_usual IS NOT NULL AND v_experiment IS NOT NULL AND v_final IS NOT NULL THEN
            SET v_total = v_usual * 0.3 + v_experiment * 0.2 + v_final * 0.5;
            SET v_is_passed = IF(v_total >= 60, TRUE, FALSE);

            -- 计算绩点
            IF v_total >= 90 THEN
                SET v_grade_point = 4.0;
            ELSEIF v_total >= 80 THEN
                SET v_grade_point = 3.0;
            ELSEIF v_total >= 70 THEN
                SET v_grade_point = 2.0;
            ELSEIF v_total >= 60 THEN
                SET v_grade_point = 1.0;
            ELSE
                SET v_grade_point = 0;
            END IF;

            -- 更新成绩状态为已提交
            UPDATE Grades
            SET total_score = v_total,
                is_passed = v_is_passed,
                grade_point = v_grade_point,
                score_status = '已提交'
            WHERE enrollment_id = v_enrollment_id;
        END IF;
    END LOOP;

    CLOSE cur;

END$$

-- ============================================
-- 5. 存储过程：创建重修记录（可选）
-- ============================================

DROP PROCEDURE IF EXISTS sp_CreateRetakeRecords$$

CREATE PROCEDURE sp_CreateRetakeRecords(
    IN p_offering_id INT
)
BEGIN
    -- 为挂科学生创建重修记录
    INSERT INTO RetakeRecords (student_id, source_enrollment_id, status)
    SELECT e.student_id, e.enrollment_id, '待重修'
    FROM Enrollments e
    JOIN Grades g ON e.enrollment_id = g.enrollment_id
    WHERE e.offering_id = p_offering_id
    AND g.is_passed = FALSE
    AND g.score_status = '已发布'
    AND NOT EXISTS (
        SELECT 1 FROM RetakeRecords r
        WHERE r.source_enrollment_id = e.enrollment_id
    );
END$$

DELIMITER ;

-- 存储过程和触发器创建完成

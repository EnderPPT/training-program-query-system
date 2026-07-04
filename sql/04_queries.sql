-- 子模块 A：培养方案数据库系统典型查询
-- 所有示例均可按 school/college/entry_year 进一步消歧，适配后续跨校数据。

-- A1. 查询某专业的必修课列表
SELECT
    s.name AS school,
    col.name AS college,
    m.name AS major,
    tp.entry_year,
    c.name AS course_name,
    pc.course_type,
    pc.semester,
    pc.credits,
    pc.hours
FROM program_courses pc
JOIN training_programs tp ON pc.program_id = tp.id
JOIN majors m ON tp.major_id = m.id
JOIN colleges col ON m.college_id = col.id
JOIN schools s ON col.school_id = s.id
JOIN courses c ON pc.course_id = c.id
WHERE s.name = '西南财经大学'
  AND m.name = '计算机科学与技术'
  AND tp.entry_year = 2025
  AND pc.course_type ILIKE '%必修%'
ORDER BY pc.semester, c.name;

-- A2. 查询某门课程的学分、学时信息
SELECT
    name AS course_name,
    default_credits,
    default_hours
FROM courses
WHERE name = '高等数学Ⅰ'
ORDER BY default_credits, default_hours
LIMIT 1;

-- A3. 查询某专业的总学分要求
SELECT
    s.name AS school,
    col.name AS college,
    m.name AS major,
    tp.entry_year,
    tp.total_credits,
    COALESCE(SUM(pc.credits), 0) AS explicit_course_credits,
    tp.total_credits - COALESCE(SUM(pc.credits), 0) AS rule_based_credits
FROM training_programs tp
JOIN majors m ON tp.major_id = m.id
JOIN colleges col ON m.college_id = col.id
JOIN schools s ON col.school_id = s.id
LEFT JOIN program_courses pc ON pc.program_id = tp.id
WHERE s.name = '西南财经大学'
  AND m.name = '计算机科学与技术'
GROUP BY s.name, col.name, m.name, tp.entry_year, tp.total_credits
ORDER BY tp.entry_year;

-- A4. 查询开设某门课程的所有专业
SELECT DISTINCT
    s.name AS school,
    col.name AS college,
    c.name AS course_name,
    m.name AS major,
    tp.entry_year
FROM program_courses pc
JOIN courses c ON pc.course_id = c.id
JOIN training_programs tp ON pc.program_id = tp.id
JOIN majors m ON tp.major_id = m.id
JOIN colleges col ON m.college_id = col.id
JOIN schools s ON col.school_id = s.id
WHERE c.name = '高等数学Ⅰ'
ORDER BY s.name, tp.entry_year, m.name;

-- A5. 查询某学院下所有专业的培养方案概览
SELECT
    s.name AS school,
    col.name AS college,
    m.name AS major,
    tp.entry_year,
    tp.total_credits,
    COUNT(pc.id) AS course_count,
    COALESCE(SUM(pc.credits), 0) AS explicit_course_credits,
    tp.total_credits - COALESCE(SUM(pc.credits), 0) AS rule_based_credits
FROM colleges col
JOIN schools s ON col.school_id = s.id
JOIN majors m ON m.college_id = col.id
JOIN training_programs tp ON tp.major_id = m.id
LEFT JOIN program_courses pc ON pc.program_id = tp.id
WHERE s.name = '西南财经大学'
  AND col.name = '计算机与人工智能学院'
GROUP BY s.name, col.name, m.name, tp.entry_year, tp.total_credits
ORDER BY m.name, tp.entry_year;

-- A6. 支持关键词模糊搜索课程名称
SELECT
    id,
    name AS course_name,
    default_credits,
    default_hours
FROM courses
WHERE name ILIKE '%' || '数学' || '%'
ORDER BY name, default_credits, default_hours;


-- 子模块 B：跨校培养方案对比分析查询示例

-- B1. 对比两校同名专业的总学分、必修课数量和显式课程学分
SELECT
    s.name AS school,
    col.name AS college,
    m.name AS major,
    tp.entry_year,
    tp.total_credits,
    COUNT(pc.id) FILTER (WHERE pc.course_type ILIKE '%必修%') AS required_course_count,
    COALESCE(SUM(pc.credits) FILTER (WHERE pc.course_type ILIKE '%必修%'), 0) AS required_course_credits,
    COUNT(pc.id) AS course_count,
    COALESCE(SUM(pc.credits), 0) AS explicit_course_credits
FROM training_programs tp
JOIN majors m ON tp.major_id = m.id
JOIN colleges col ON m.college_id = col.id
JOIN schools s ON col.school_id = s.id
LEFT JOIN program_courses pc ON pc.program_id = tp.id
WHERE m.name = '计算机科学与技术'
  AND s.name IN ('西南财经大学', '上海财经大学')
GROUP BY s.name, col.name, m.name, tp.entry_year, tp.total_credits
ORDER BY s.name, tp.entry_year;

-- B2. 查询两校同名专业的共同课程
WITH scoped AS (
    SELECT s.name AS school, c.name AS course_name, pc.course_type, pc.credits, pc.hours
    FROM program_courses pc
    JOIN courses c ON pc.course_id = c.id
    JOIN training_programs tp ON pc.program_id = tp.id
    JOIN majors m ON tp.major_id = m.id
    JOIN colleges col ON m.college_id = col.id
    JOIN schools s ON col.school_id = s.id
    WHERE m.name = '计算机科学与技术'
      AND s.name IN ('西南财经大学', '上海财经大学')
)
SELECT
    course_name,
    ARRAY_AGG(DISTINCT school ORDER BY school) AS schools,
    ARRAY_AGG(DISTINCT course_type ORDER BY course_type) AS course_types
FROM scoped
GROUP BY course_name
HAVING COUNT(DISTINCT school) = 2
ORDER BY course_name;

-- B3. 查询西南财经大学某专业相对上海财经大学的独有课程
SELECT DISTINCT
    c.name AS course_name,
    pc.course_type,
    pc.semester,
    pc.credits,
    pc.hours
FROM program_courses pc
JOIN courses c ON pc.course_id = c.id
JOIN training_programs tp ON pc.program_id = tp.id
JOIN majors m ON tp.major_id = m.id
JOIN colleges col ON m.college_id = col.id
JOIN schools s ON col.school_id = s.id
WHERE s.name = '西南财经大学'
  AND m.name = '计算机科学与技术'
  AND NOT EXISTS (
      SELECT 1
      FROM program_courses pc2
      JOIN courses c2 ON pc2.course_id = c2.id
      JOIN training_programs tp2 ON pc2.program_id = tp2.id
      JOIN majors m2 ON tp2.major_id = m2.id
      JOIN colleges col2 ON m2.college_id = col2.id
      JOIN schools s2 ON col2.school_id = s2.id
      WHERE s2.name = '上海财经大学'
        AND m2.name = '计算机科学与技术'
        AND c2.name = c.name
  )
ORDER BY pc.semester, c.name;

-- B4. 对比某门课程在两校各专业中的学分学时
SELECT DISTINCT
    s.name AS school,
    col.name AS college,
    m.name AS major,
    tp.entry_year,
    c.name AS course_name,
    pc.course_type,
    pc.semester,
    pc.credits,
    pc.hours
FROM program_courses pc
JOIN courses c ON pc.course_id = c.id
JOIN training_programs tp ON pc.program_id = tp.id
JOIN majors m ON tp.major_id = m.id
JOIN colleges col ON m.college_id = col.id
JOIN schools s ON col.school_id = s.id
WHERE c.name = '高等数学Ⅰ'
  AND s.name IN ('西南财经大学', '上海财经大学')
ORDER BY s.name, m.name, tp.entry_year;

-- B5. 对比两校同专业课程类型分布
SELECT
    s.name AS school,
    m.name AS major,
    pc.course_type,
    COUNT(*) AS course_count,
    COALESCE(SUM(pc.credits), 0) AS credits_sum
FROM program_courses pc
JOIN training_programs tp ON pc.program_id = tp.id
JOIN majors m ON tp.major_id = m.id
JOIN colleges col ON m.college_id = col.id
JOIN schools s ON col.school_id = s.id
WHERE m.name = '计算机科学与技术'
  AND s.name IN ('西南财经大学', '上海财经大学')
GROUP BY s.name, m.name, pc.course_type
ORDER BY s.name, pc.course_type;

INSERT INTO schools (name)
SELECT DISTINCT school
FROM staging_courses
ON CONFLICT (name) DO NOTHING;

INSERT INTO colleges (school_id, name)
SELECT DISTINCT s.id, sc.college
FROM staging_courses sc
JOIN schools s ON s.name = sc.school
ON CONFLICT (school_id, name) DO NOTHING;

INSERT INTO majors (college_id, name)
SELECT DISTINCT c.id, sc.major
FROM staging_courses sc
JOIN schools s ON s.name = sc.school
JOIN colleges c ON c.school_id = s.id AND c.name = sc.college
ON CONFLICT (college_id, name) DO NOTHING;

INSERT INTO training_programs (major_id, entry_year, version, total_credits)
SELECT DISTINCT
    m.id,
    sc.entry_year,
    'default',
    sc.total_credits
FROM staging_courses sc
JOIN schools s ON s.name = sc.school
JOIN colleges c ON c.school_id = s.id AND c.name = sc.college
JOIN majors m ON m.college_id = c.id AND m.name = sc.major
ON CONFLICT (major_id, entry_year, version) DO NOTHING;

INSERT INTO courses (name, default_credits, default_hours)
SELECT DISTINCT
    course_name,
    credits,
    hours
FROM staging_courses
ON CONFLICT (name, default_credits, default_hours) DO NOTHING;

INSERT INTO program_courses (
    program_id,
    course_id,
    course_type,
    semester,
    credits,
    hours
)
SELECT DISTINCT
    tp.id,
    c.id,
    sc.course_type,
    sc.semester,
    sc.credits,
    sc.hours
FROM staging_courses sc
JOIN schools s ON s.name = sc.school
JOIN colleges co ON co.school_id = s.id AND co.name = sc.college
JOIN majors m ON m.college_id = co.id AND m.name = sc.major
JOIN training_programs tp
    ON tp.major_id = m.id
   AND tp.entry_year = sc.entry_year
   AND tp.version = 'default'
JOIN courses c
    ON c.name = sc.course_name
   AND c.default_credits IS NOT DISTINCT FROM sc.credits
   AND c.default_hours IS NOT DISTINCT FROM sc.hours
ON CONFLICT (program_id, course_id, course_type, semester) DO NOTHING;
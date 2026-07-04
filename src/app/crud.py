from .db import get_connection

DEFAULT_COMPARE_SCHOOLS = ("西南财经大学", "上海财经大学")


def _add_optional_filter(conditions, params, sql_expression, value):
    if value is not None:
        conditions.append(sql_expression)
        params.append(value)


def _limit_offset(limit: int, offset: int):
    return [max(1, min(limit, 200)), max(0, offset)]


def fetch_all_major_courses(
    major_name: str,
    school_name: str | None = None,
    college_name: str | None = None,
    entry_year: int | None = None,
    limit: int = 200,
    offset: int = 0,
):
    conditions = ["m.name = %s"]
    params = [major_name]
    _add_optional_filter(conditions, params, "s.name = %s", school_name)
    _add_optional_filter(conditions, params, "col.name = %s", college_name)
    _add_optional_filter(conditions, params, "tp.entry_year = %s", entry_year)
    params.extend(_limit_offset(limit, offset))
    sql = f"""
    SELECT
        s.name AS school,
        col.name AS college,
        m.name AS major,
        tp.entry_year,
        co.name AS course_name,
        pc.course_type,
        pc.semester,
        pc.credits,
        pc.hours
    FROM program_courses pc
    JOIN training_programs tp ON pc.program_id = tp.id
    JOIN majors m ON tp.major_id = m.id
    JOIN colleges col ON m.college_id = col.id
    JOIN schools s ON col.school_id = s.id
    JOIN courses co ON pc.course_id = co.id
    WHERE {' AND '.join(conditions)}
    ORDER BY s.name, col.name, tp.entry_year, pc.semester, pc.course_type, co.name
    LIMIT %s OFFSET %s;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def fetch_required_courses(
    major_name: str,
    school_name: str | None = None,
    college_name: str | None = None,
    entry_year: int | None = None,
    limit: int = 200,
    offset: int = 0,
):
    conditions = ["m.name = %s", "pc.course_type ILIKE %s"]
    params = [major_name, "%必修%"]
    _add_optional_filter(conditions, params, "s.name = %s", school_name)
    _add_optional_filter(conditions, params, "col.name = %s", college_name)
    _add_optional_filter(conditions, params, "tp.entry_year = %s", entry_year)
    params.extend(_limit_offset(limit, offset))
    sql = f"""
    SELECT
        s.name AS school,
        col.name AS college,
        m.name AS major,
        tp.entry_year,
        co.name AS course_name,
        pc.course_type,
        pc.semester,
        pc.credits,
        pc.hours
    FROM program_courses pc
    JOIN training_programs tp ON pc.program_id = tp.id
    JOIN majors m ON tp.major_id = m.id
    JOIN colleges col ON m.college_id = col.id
    JOIN schools s ON col.school_id = s.id
    JOIN courses co ON pc.course_id = co.id
    WHERE {' AND '.join(conditions)}
    ORDER BY s.name, col.name, tp.entry_year, pc.semester, co.name
    LIMIT %s OFFSET %s;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def fetch_major_summary(
    major_name: str,
    school_name: str | None = None,
    college_name: str | None = None,
    entry_year: int | None = None,
):
    conditions = ["m.name = %s"]
    params = [major_name]
    _add_optional_filter(conditions, params, "s.name = %s", school_name)
    _add_optional_filter(conditions, params, "col.name = %s", college_name)
    _add_optional_filter(conditions, params, "tp.entry_year = %s", entry_year)
    sql = f"""
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
    WHERE {' AND '.join(conditions)}
    GROUP BY s.name, col.name, m.name, tp.entry_year, tp.total_credits
    ORDER BY s.name, col.name, tp.entry_year;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def fetch_course_detail(course_name: str):
    sql = """
    SELECT
        name,
        default_credits,
        default_hours
    FROM courses
    WHERE name = %s
    ORDER BY default_credits, default_hours
    LIMIT 1;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (course_name,))
            return cur.fetchone()


def fetch_course_majors(
    course_name: str,
    school_name: str | None = None,
    major_name: str | None = None,
    entry_year: int | None = None,
    limit: int = 200,
    offset: int = 0,
):
    conditions = ["co.name = %s"]
    params = [course_name]
    _add_optional_filter(conditions, params, "s.name = %s", school_name)
    _add_optional_filter(conditions, params, "m.name = %s", major_name)
    _add_optional_filter(conditions, params, "tp.entry_year = %s", entry_year)
    params.extend(_limit_offset(limit, offset))
    sql = f"""
    SELECT DISTINCT
        s.name AS school,
        col.name AS college,
        co.name AS course_name,
        m.name AS major,
        tp.entry_year
    FROM program_courses pc
    JOIN courses co ON pc.course_id = co.id
    JOIN training_programs tp ON pc.program_id = tp.id
    JOIN majors m ON tp.major_id = m.id
    JOIN colleges col ON m.college_id = col.id
    JOIN schools s ON col.school_id = s.id
    WHERE {' AND '.join(conditions)}
    ORDER BY s.name, col.name, tp.entry_year, m.name
    LIMIT %s OFFSET %s;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def fetch_college_summary(
    college_name: str,
    school_name: str | None = None,
    entry_year: int | None = None,
):
    conditions = ["c.name = %s"]
    params = [college_name]
    _add_optional_filter(conditions, params, "s.name = %s", school_name)
    _add_optional_filter(conditions, params, "tp.entry_year = %s", entry_year)
    sql = f"""
    SELECT
        s.name AS school,
        c.name AS college,
        m.name AS major,
        tp.entry_year,
        tp.total_credits,
        COUNT(pc.id) AS course_count,
        COALESCE(SUM(pc.credits), 0) AS explicit_course_credits,
        tp.total_credits - COALESCE(SUM(pc.credits), 0) AS rule_based_credits
    FROM colleges c
    JOIN schools s ON c.school_id = s.id
    JOIN majors m ON m.college_id = c.id
    JOIN training_programs tp ON tp.major_id = m.id
    LEFT JOIN program_courses pc ON pc.program_id = tp.id
    WHERE {' AND '.join(conditions)}
    GROUP BY s.name, c.name, m.name, tp.entry_year, tp.total_credits
    ORDER BY s.name, c.name, m.name, tp.entry_year;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def search_courses(keyword: str, limit: int = 100, offset: int = 0):
    params = [keyword]
    params.extend(_limit_offset(limit, offset))
    sql = """
    SELECT
        id,
        name,
        default_credits,
        default_hours
    FROM courses
    WHERE name ILIKE '%%' || %s || '%%'
    ORDER BY name, default_credits, default_hours
    LIMIT %s OFFSET %s;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def compare_major_summary(
    major_name: str,
    schools: tuple[str, str] = DEFAULT_COMPARE_SCHOOLS,
    entry_year: int | None = None,
):
    conditions = ["m.name = %s", "s.name = ANY(%s)"]
    params = [major_name, list(schools)]
    _add_optional_filter(conditions, params, "tp.entry_year = %s", entry_year)
    sql = f"""
    SELECT
        s.name AS school,
        col.name AS college,
        m.name AS major,
        tp.entry_year,
        tp.total_credits,
        COUNT(pc.id) FILTER (WHERE pc.course_type ILIKE '%%必修%%') AS required_course_count,
        COALESCE(SUM(pc.credits) FILTER (WHERE pc.course_type ILIKE '%%必修%%'), 0) AS required_course_credits,
        COUNT(pc.id) AS course_count,
        COALESCE(SUM(pc.credits), 0) AS explicit_course_credits
    FROM training_programs tp
    JOIN majors m ON tp.major_id = m.id
    JOIN colleges col ON m.college_id = col.id
    JOIN schools s ON col.school_id = s.id
    LEFT JOIN program_courses pc ON pc.program_id = tp.id
    WHERE {' AND '.join(conditions)}
    GROUP BY s.name, col.name, m.name, tp.entry_year, tp.total_credits
    ORDER BY s.name, tp.entry_year;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def compare_major_common_courses(
    major_name: str,
    schools: tuple[str, str] = DEFAULT_COMPARE_SCHOOLS,
    entry_year: int | None = None,
):
    year_filter = "AND tp.entry_year = %s" if entry_year is not None else ""
    params = [major_name, list(schools)]
    if entry_year is not None:
        params.append(entry_year)
    sql = f"""
    WITH scoped AS (
        SELECT
            s.name AS school,
            co.name AS course_name,
            pc.course_type,
            pc.credits,
            pc.hours
        FROM program_courses pc
        JOIN courses co ON pc.course_id = co.id
        JOIN training_programs tp ON pc.program_id = tp.id
        JOIN majors m ON tp.major_id = m.id
        JOIN colleges col ON m.college_id = col.id
        JOIN schools s ON col.school_id = s.id
        WHERE m.name = %s
          AND s.name = ANY(%s)
          {year_filter}
    )
    SELECT
        course_name,
        ARRAY_AGG(DISTINCT school ORDER BY school) AS schools,
        COUNT(DISTINCT school) AS school_count,
        ARRAY_AGG(DISTINCT course_type ORDER BY course_type) AS course_types,
        ARRAY_AGG(DISTINCT credits ORDER BY credits) FILTER (WHERE credits IS NOT NULL) AS credits,
        ARRAY_AGG(DISTINCT hours ORDER BY hours) FILTER (WHERE hours IS NOT NULL) AS hours
    FROM scoped
    GROUP BY course_name
    HAVING COUNT(DISTINCT school) = CARDINALITY(%s::text[])
    ORDER BY course_name;
    """
    params.append(list(schools))
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def compare_major_school_only_courses(
    major_name: str,
    school_name: str,
    other_school_name: str,
    entry_year: int | None = None,
):
    year_filter_a = "AND tp.entry_year = %s" if entry_year is not None else ""
    year_filter_b = "AND tp2.entry_year = %s" if entry_year is not None else ""
    params = [school_name, major_name]
    if entry_year is not None:
        params.append(entry_year)
    params.extend([other_school_name, major_name])
    if entry_year is not None:
        params.append(entry_year)
    sql = f"""
    SELECT DISTINCT
        s.name AS school,
        co.name AS course_name,
        pc.course_type,
        pc.semester,
        pc.credits,
        pc.hours
    FROM program_courses pc
    JOIN courses co ON pc.course_id = co.id
    JOIN training_programs tp ON pc.program_id = tp.id
    JOIN majors m ON tp.major_id = m.id
    JOIN colleges col ON m.college_id = col.id
    JOIN schools s ON col.school_id = s.id
    WHERE s.name = %s
      AND m.name = %s
      {year_filter_a}
      AND NOT EXISTS (
          SELECT 1
          FROM program_courses pc2
          JOIN courses co2 ON pc2.course_id = co2.id
          JOIN training_programs tp2 ON pc2.program_id = tp2.id
          JOIN majors m2 ON tp2.major_id = m2.id
          JOIN colleges col2 ON m2.college_id = col2.id
          JOIN schools s2 ON col2.school_id = s2.id
          WHERE s2.name = %s
            AND m2.name = %s
            {year_filter_b}
            AND co2.name = co.name
      )
    ORDER BY pc.semester, co.name;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def compare_course_across_schools(
    course_name: str,
    schools: tuple[str, str] = DEFAULT_COMPARE_SCHOOLS,
    major_name: str | None = None,
):
    conditions = ["co.name = %s", "s.name = ANY(%s)"]
    params = [course_name, list(schools)]
    _add_optional_filter(conditions, params, "m.name = %s", major_name)
    sql = f"""
    SELECT DISTINCT
        s.name AS school,
        col.name AS college,
        m.name AS major,
        tp.entry_year,
        co.name AS course_name,
        pc.course_type,
        pc.semester,
        pc.credits,
        pc.hours
    FROM program_courses pc
    JOIN courses co ON pc.course_id = co.id
    JOIN training_programs tp ON pc.program_id = tp.id
    JOIN majors m ON tp.major_id = m.id
    JOIN colleges col ON m.college_id = col.id
    JOIN schools s ON col.school_id = s.id
    WHERE {' AND '.join(conditions)}
    ORDER BY s.name, m.name, tp.entry_year;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

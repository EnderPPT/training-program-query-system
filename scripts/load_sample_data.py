import argparse
from pathlib import Path
import sys

import psycopg

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from app.config import DATABASE_URL

FIELDNAMES = [
    "school",
    "college",
    "major",
    "entry_year",
    "course_name",
    "course_type",
    "credits",
    "hours",
    "semester",
    "total_credits",
]

CREATE_STAGING_SQL = """
CREATE TABLE IF NOT EXISTS staging_courses (
    school TEXT NOT NULL,
    college TEXT NOT NULL,
    major TEXT NOT NULL,
    entry_year INT NOT NULL,
    course_name TEXT NOT NULL,
    course_type TEXT NOT NULL,
    credits NUMERIC(4,1),
    hours INT,
    semester INT,
    total_credits NUMERIC(5,1)
);
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="导入 data/samples 下的培养方案 CSV 到 PostgreSQL")
    parser.add_argument("--database-url", default=DATABASE_URL, help="PostgreSQL 连接串，默认读取 DATABASE_URL")
    parser.add_argument("--samples-dir", default=str(ROOT_DIR / "data" / "samples"), help="CSV 样例目录")
    parser.add_argument("--pattern", default="*.csv", help="CSV 文件匹配模式")
    parser.add_argument("--init-schema", action="store_true", help="先执行 sql/01_schema.sql，适用于空数据库")
    parser.add_argument("--reset-staging", action="store_true", help="导入前清空 staging_courses")
    parser.add_argument("--reset-data", action="store_true", help="导入前清空正式业务表，避免旧样例数据残留")
    return parser.parse_args()


def execute_sql_file(conn: psycopg.Connection, path: Path) -> None:
    with path.open(encoding="utf-8") as file:
        sql = file.read()
    with conn.cursor() as cur:
        cur.execute(sql)


def ensure_staging(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute(CREATE_STAGING_SQL)


def reset_staging(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE staging_courses;")


def reset_data(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE schools RESTART IDENTITY CASCADE;")


def load_csv(conn: psycopg.Connection, path: Path) -> int:
    copy_sql = f"COPY staging_courses ({', '.join(FIELDNAMES)}) FROM STDIN WITH (FORMAT CSV, HEADER true)"
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        content = file.read()
    with conn.cursor() as cur:
        with cur.copy(copy_sql) as copy:
            copy.write(content)
    return max(0, content.count("\n") - 1)


def main() -> None:
    args = parse_args()
    samples_dir = Path(args.samples_dir)
    csv_files = sorted(samples_dir.glob(args.pattern))
    if not csv_files:
        raise SystemExit(f"未找到 CSV 文件：{samples_dir / args.pattern}")

    with psycopg.connect(args.database_url) as conn:
        if args.init_schema:
            execute_sql_file(conn, ROOT_DIR / "sql" / "01_schema.sql")
        ensure_staging(conn)
        if args.reset_data:
            reset_data(conn)
        if args.reset_staging:
            reset_staging(conn)

        total_rows = 0
        for path in csv_files:
            rows = load_csv(conn, path)
            total_rows += rows
            print(f"loaded {rows:>4} rows from {path}")

        execute_sql_file(conn, ROOT_DIR / "sql" / "03_load_from_staging.sql")
        conn.commit()

    print(f"import complete: {len(csv_files)} files, {total_rows} staging rows")


if __name__ == "__main__":
    main()

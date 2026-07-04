CREATE TABLE staging_courses (
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
CREATE TABLE schools (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE colleges (
    id BIGSERIAL PRIMARY KEY,
    school_id BIGINT NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    UNIQUE (school_id, name)
);

CREATE TABLE majors (
    id BIGSERIAL PRIMARY KEY,
    college_id BIGINT NOT NULL REFERENCES colleges(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    UNIQUE (college_id, name)
);

CREATE TABLE training_programs (
    id BIGSERIAL PRIMARY KEY,
    major_id BIGINT NOT NULL REFERENCES majors(id) ON DELETE CASCADE,
    entry_year INT NOT NULL,
    version TEXT NOT NULL DEFAULT 'default',
    total_credits NUMERIC(5,1),
    UNIQUE (major_id, entry_year, version)
);

CREATE TABLE courses (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    default_credits NUMERIC(4,1),
    default_hours INT,
    UNIQUE (name, default_credits, default_hours)
);

CREATE TABLE program_courses (
    id BIGSERIAL PRIMARY KEY,
    program_id BIGINT NOT NULL REFERENCES training_programs(id) ON DELETE CASCADE,
    course_id BIGINT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    course_type TEXT NOT NULL,
    semester INT,
    credits NUMERIC(4,1),
    hours INT,
    UNIQUE (program_id, course_id, course_type, semester)
);

CREATE INDEX idx_colleges_school_id ON colleges(school_id);
CREATE INDEX idx_majors_college_id ON majors(college_id);
CREATE INDEX idx_training_programs_major_id ON training_programs(major_id);
CREATE INDEX idx_courses_name ON courses(name);
CREATE INDEX idx_program_courses_program_id ON program_courses(program_id);
CREATE INDEX idx_program_courses_course_id ON program_courses(course_id);
CREATE INDEX idx_program_courses_semester ON program_courses(semester);
CREATE INDEX idx_program_courses_course_type ON program_courses(course_type);

CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_courses_name_trgm ON courses USING gin (name gin_trgm_ops);
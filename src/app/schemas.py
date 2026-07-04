from decimal import Decimal

from pydantic import BaseModel, Field


class CourseDetail(BaseModel):
    name: str
    default_credits: Decimal | None = None
    default_hours: int | None = None


class CourseSearchItem(BaseModel):
    id: int
    name: str
    default_credits: Decimal | None = None
    default_hours: int | None = None


class MajorCourse(BaseModel):
    school: str
    college: str
    major: str
    entry_year: int
    course_name: str
    course_type: str
    semester: int | None = None
    credits: Decimal | None = None
    hours: int | None = None


class MajorSummary(BaseModel):
    school: str
    college: str
    major: str
    entry_year: int
    total_credits: Decimal | None = None
    explicit_course_credits: Decimal
    rule_based_credits: Decimal | None = None


class CourseMajor(BaseModel):
    school: str
    college: str
    course_name: str
    major: str
    entry_year: int


class CollegeSummary(BaseModel):
    school: str
    college: str
    major: str
    entry_year: int
    total_credits: Decimal | None = None
    course_count: int
    explicit_course_credits: Decimal
    rule_based_credits: Decimal | None = None


class MajorComparisonSummary(BaseModel):
    school: str
    college: str
    major: str
    entry_year: int
    total_credits: Decimal | None = None
    required_course_count: int
    required_course_credits: Decimal
    course_count: int
    explicit_course_credits: Decimal


class ComparedCourse(BaseModel):
    course_name: str
    schools: list[str]
    school_count: int
    course_types: list[str]
    credits: list[Decimal]
    hours: list[int]


class SchoolOnlyCourse(BaseModel):
    school: str
    course_name: str
    course_type: str
    semester: int | None = None
    credits: Decimal | None = None
    hours: int | None = None


class CourseSchoolComparison(BaseModel):
    school: str
    college: str
    major: str
    entry_year: int
    course_name: str
    course_type: str
    semester: int | None = None
    credits: Decimal | None = None
    hours: int | None = None


class NaturalLanguageQuery(BaseModel):
    question: str = Field(min_length=2, max_length=200)


class NaturalLanguageResult(BaseModel):
    intent: str
    params: dict[str, str]
    data: list[dict] | dict | None

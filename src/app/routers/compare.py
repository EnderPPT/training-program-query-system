from fastapi import APIRouter, HTTPException

from ..crud import (
    DEFAULT_COMPARE_SCHOOLS,
    compare_course_across_schools,
    compare_major_common_courses,
    compare_major_school_only_courses,
    compare_major_summary,
    fetch_required_courses,
)
from ..nl_query import parse_question
from ..schemas import (
    ComparedCourse,
    CourseSchoolComparison,
    MajorComparisonSummary,
    MajorCourse,
    NaturalLanguageQuery,
    NaturalLanguageResult,
    SchoolOnlyCourse,
)

router = APIRouter(prefix="/compare", tags=["compare"])


def _schools(school_a: str, school_b: str) -> tuple[str, str]:
    return (school_a, school_b)


@router.get("/majors/{major_name}/summary", response_model=list[MajorComparisonSummary])
def get_major_comparison_summary(
    major_name: str,
    school_a: str = DEFAULT_COMPARE_SCHOOLS[0],
    school_b: str = DEFAULT_COMPARE_SCHOOLS[1],
    entry_year: int | None = None,
):
    rows = compare_major_summary(major_name, _schools(school_a, school_b), entry_year)
    if not rows:
        raise HTTPException(status_code=404, detail="未找到可对比的专业培养方案")
    return rows


@router.get("/majors/{major_name}/common-courses", response_model=list[ComparedCourse])
def get_major_common_courses(
    major_name: str,
    school_a: str = DEFAULT_COMPARE_SCHOOLS[0],
    school_b: str = DEFAULT_COMPARE_SCHOOLS[1],
    entry_year: int | None = None,
):
    rows = compare_major_common_courses(major_name, _schools(school_a, school_b), entry_year)
    if not rows:
        raise HTTPException(status_code=404, detail="未找到两校共同课程")
    return rows


@router.get("/majors/{major_name}/school-only-courses", response_model=list[SchoolOnlyCourse])
def get_major_school_only_courses(
    major_name: str,
    school_name: str = DEFAULT_COMPARE_SCHOOLS[0],
    other_school_name: str = DEFAULT_COMPARE_SCHOOLS[1],
    entry_year: int | None = None,
):
    rows = compare_major_school_only_courses(
        major_name,
        school_name,
        other_school_name,
        entry_year,
    )
    if not rows:
        raise HTTPException(status_code=404, detail="未找到该校独有课程")
    return rows


@router.get("/courses/{course_name}", response_model=list[CourseSchoolComparison])
def get_course_comparison(
    course_name: str,
    school_a: str = DEFAULT_COMPARE_SCHOOLS[0],
    school_b: str = DEFAULT_COMPARE_SCHOOLS[1],
    major_name: str | None = None,
):
    rows = compare_course_across_schools(course_name, _schools(school_a, school_b), major_name)
    if not rows:
        raise HTTPException(status_code=404, detail="未找到课程对比数据")
    return rows


@router.post("/nl-query", response_model=NaturalLanguageResult)
def nl_query(payload: NaturalLanguageQuery):
    parsed = parse_question(payload.question)
    if parsed is None:
        raise HTTPException(status_code=400, detail="暂不支持该问题，请使用总学分、共同课程、独有课程或课程学分学时对比类问题")

    if parsed.intent == "compare_major_summary":
        data = compare_major_summary(parsed.params["major_name"])
    elif parsed.intent == "compare_major_common_courses":
        data = compare_major_common_courses(parsed.params["major_name"])
    elif parsed.intent == "compare_major_school_only_courses":
        data = compare_major_school_only_courses(
            parsed.params["major_name"],
            DEFAULT_COMPARE_SCHOOLS[0],
            DEFAULT_COMPARE_SCHOOLS[1],
        )
    elif parsed.intent == "compare_course":
        data = compare_course_across_schools(parsed.params["course_name"])
    elif parsed.intent == "required_courses":
        data = fetch_required_courses(
            parsed.params["major_name"],
            school_name=parsed.params["school_name"],
        )
    else:
        raise HTTPException(status_code=400, detail="未识别的查询意图")

    return NaturalLanguageResult(intent=parsed.intent, params=parsed.params, data=data)

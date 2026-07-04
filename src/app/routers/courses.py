from fastapi import APIRouter, HTTPException, Query

from ..crud import fetch_course_detail, fetch_course_majors, search_courses
from ..schemas import CourseDetail, CourseMajor, CourseSearchItem

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/search", response_model=list[CourseSearchItem])
def get_search_courses(
    keyword: str = Query(min_length=1),
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    rows = search_courses(keyword, limit=limit, offset=offset)
    if not rows:
        raise HTTPException(status_code=404, detail="课程未找到")
    return rows


@router.get("/{course_name}", response_model=CourseDetail)
def get_course_detail(course_name: str):
    row = fetch_course_detail(course_name)
    if not row:
        raise HTTPException(status_code=404, detail="课程未找到")
    return row


@router.get("/{course_name}/majors", response_model=list[CourseMajor])
def get_course_majors(
    course_name: str,
    school_name: str | None = None,
    major_name: str | None = None,
    entry_year: int | None = None,
    limit: int = Query(default=200, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    rows = fetch_course_majors(
        course_name,
        school_name=school_name,
        major_name=major_name,
        entry_year=entry_year,
        limit=limit,
        offset=offset,
    )
    if not rows:
        raise HTTPException(status_code=404, detail="课程未找到")
    return rows

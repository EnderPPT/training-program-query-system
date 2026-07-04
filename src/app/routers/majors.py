from fastapi import APIRouter, HTTPException, Query

from ..crud import (
    fetch_all_major_courses,
    fetch_college_summary,
    fetch_major_summary,
    fetch_required_courses,
)
from ..schemas import CollegeSummary, MajorCourse, MajorSummary

router = APIRouter(tags=["majors"])


@router.get("/majors/{major_name}/courses", response_model=list[MajorCourse])
def get_major_courses(
    major_name: str,
    school_name: str | None = None,
    college_name: str | None = None,
    entry_year: int | None = None,
    limit: int = Query(default=200, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    rows = fetch_all_major_courses(
        major_name,
        school_name=school_name,
        college_name=college_name,
        entry_year=entry_year,
        limit=limit,
        offset=offset,
    )
    if not rows:
        raise HTTPException(status_code=404, detail="专业未找到或没有课程")
    return rows


@router.get("/majors/{major_name}/required-courses", response_model=list[MajorCourse])
def get_required_courses(
    major_name: str,
    school_name: str | None = None,
    college_name: str | None = None,
    entry_year: int | None = None,
    limit: int = Query(default=200, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    rows = fetch_required_courses(
        major_name,
        school_name=school_name,
        college_name=college_name,
        entry_year=entry_year,
        limit=limit,
        offset=offset,
    )
    if not rows:
        raise HTTPException(status_code=404, detail="专业未找到或没有必修课程")
    return rows


@router.get("/majors/{major_name}/summary", response_model=list[MajorSummary])
def get_major_summary(
    major_name: str,
    school_name: str | None = None,
    college_name: str | None = None,
    entry_year: int | None = None,
):
    rows = fetch_major_summary(
        major_name,
        school_name=school_name,
        college_name=college_name,
        entry_year=entry_year,
    )
    if not rows:
        raise HTTPException(status_code=404, detail="专业未找到")
    return rows


@router.get("/colleges/{college_name}/summary", response_model=list[CollegeSummary])
def get_college_summary(
    college_name: str,
    school_name: str | None = None,
    entry_year: int | None = None,
):
    rows = fetch_college_summary(
        college_name,
        school_name=school_name,
        entry_year=entry_year,
    )
    if not rows:
        raise HTTPException(status_code=404, detail="学院未找到")
    return rows

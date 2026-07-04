import re
from dataclasses import dataclass

DEFAULT_SCHOOLS = ("西南财经大学", "上海财经大学")
KNOWN_MAJORS = (
    "信息管理与信息系统",
    "数据科学与大数据技术",
    "计算机科学与技术",
    "人工智能",
    "网络空间安全",
    "电子商务",
    "物流管理",
    "金融数学",
    "金融学",
)


@dataclass(frozen=True)
class ParsedQuery:
    intent: str
    params: dict[str, str]


def parse_question(question: str) -> ParsedQuery | None:
    normalized = re.sub(r"\s+", "", question)
    major = _match_major(normalized)
    course = _match_quoted_or_after_keyword(normalized, "课程")

    if "对比" in normalized and major and "总学分" in normalized:
        return ParsedQuery("compare_major_summary", {"major_name": major})

    if "对比" in normalized and major and ("共同课程" in normalized or "相同课程" in normalized or "课程交集" in normalized):
        return ParsedQuery("compare_major_common_courses", {"major_name": major})

    if "对比" in normalized and major and ("独有课程" in normalized or "差异课程" in normalized or "不同课程" in normalized):
        return ParsedQuery("compare_major_school_only_courses", {"major_name": major})

    if major and ("共同课程" in normalized or "相同课程" in normalized or "课程交集" in normalized):
        return ParsedQuery("compare_major_common_courses", {"major_name": major})

    if major and "总学分" in normalized and ("两校" in normalized or "西财" in normalized or "上财" in normalized):
        return ParsedQuery("compare_major_summary", {"major_name": major})

    if "对比" in normalized and course and ("学分" in normalized or "学时" in normalized):
        return ParsedQuery("compare_course", {"course_name": course})

    if "上海财经大学" in normalized and major and "必修" in normalized:
        return ParsedQuery(
            "required_courses",
            {"school_name": "上海财经大学", "major_name": major},
        )

    return None


def _match_major(question: str) -> str | None:
    for major in KNOWN_MAJORS:
        if major in question:
            return major
    match = re.search(r"(?:两校|西财|上财|上海财经大学|西南财经大学)([^的，。？?]+?)(?:总学分|共同课程|相同课程|课程交集|独有课程|差异课程|不同课程|必修课|必修)", question)
    if match:
        return match.group(1)
    return None


def _match_quoted_or_after_keyword(question: str, keyword: str) -> str | None:
    quoted = re.search(r"[《'\"]([^《》'\"]+)[》'\"]", question)
    if quoted:
        return quoted.group(1)
    match = re.search(rf"{keyword}([^，。？?]+?)(?:学分|学时|差异|对比)", question)
    if match:
        return match.group(1)
    return None

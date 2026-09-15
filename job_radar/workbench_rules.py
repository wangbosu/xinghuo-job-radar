"""信息台的公开展示分类。"""
from __future__ import annotations

from .candidate_rules import has_explicit_2027

C27_KW = ("2027届", "2027 届", "27届", "27 届", "2027校招", "2027校园", "2027秋招")
CONVERT_KW = ("可转正", "转正机会", "留用", "return offer")


def kind(sid: str, title: str) -> str:
    t = title or ""
    if any(k in t.lower() for k in ("实习", "intern")):
        return "实习"
    if has_explicit_2027(t) or any(k in t for k in ("校招", "校园招聘", "应届", "管培")):
        return "校招"
    if any(k in t for k in ("社招", "社会招聘", "资深", "高级")):
        return "社招"
    return "其他"


def stage(title: str, jd: str) -> str:
    text = f"{title or ''} {jd or ''}"
    if any(k in text for k in ("秋招", "秋季校园招聘", "正式批")):
        return "秋招"
    if "春招" in text:
        return "春招/补录"
    if any(k in text for k in ("提前批", "预招聘", "预招")):
        return "提前批"
    if any(k in text.lower() for k in ("实习", "intern")):
        return "实习"
    return "校招" if kind("", title) == "校招" else "其他"


def is_2027_cycle(sid: str, job_kind: str, title: str, jd: str, publish: str, job_stage: str) -> bool:
    return has_explicit_2027(f"{title or ''} {jd or ''}")


def category(sid: str) -> str:
    if sid.startswith("gov-"):
        return "国家平台"
    if sid.startswith("edu-"):
        return "高校就业网"
    if sid.startswith(("nk-", "sxs-")):
        return "社区线索"
    if sid == "cn-iguopin":
        return "国聘"
    if sid.startswith(("gh-", "ashby-", "wd-")):
        return "官方ATS"
    return "企业官网"


def industry_display(ind: str) -> str:
    return ind or "其他"


def region(loc: str) -> str:
    text = (loc or "").lower()
    for city in ("深圳", "广州", "成都", "东莞", "佛山", "惠州", "珠海", "中山"):
        if city in text:
            return city
    return "其他"


def region_of(cat: str, loc: str) -> str:
    return region(loc)

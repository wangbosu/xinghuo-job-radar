"""星火秋招雷达的确定性、可解释粗排。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .candidate_rules import LEAD, VERIFIED, role_family
from .models import Job
from .normalize import normalize_city
from .role_rules import employer_tier


@dataclass
class ScoreResult:
    score: int = 0
    tags: List[str] = field(default_factory=list)
    risk_flags: List[str] = field(default_factory=list)


CITY_POINTS = {
    "深圳": 45,
    "广州": 32,
    "成都": 26,
    "东莞": 22,
    "佛山": 22,
    "惠州": 22,
    "珠海": 18,
    "中山": 16,
}


def _city_score(location: str) -> tuple[int, str]:
    text = location or ""
    for city, points in CITY_POINTS.items():
        if city in text or normalize_city(text) == normalize_city(city):
            return points, city
    return (8, "其他重点城市") if text else (0, "")


def score_job(job: Job, profile: Dict) -> ScoreResult:
    text = f"{job.title or ''} {job.jd_text or ''}".lower()
    tags: List[str] = []
    risk: List[str] = []
    score = int(job.source_confidence * 0.12)

    if job.verification_status == VERIFIED:
        score += 45
        tags.append("2027正式秋招")
    elif job.verification_status == LEAD:
        score += 5
        tags.append("待核实")

    fam = job.role_family or role_family(job.title, job.jd_text)
    family_points = {
        "供应链/计划/交付": 48,
        "运营/项目": 45,
        "市场/品牌/电商": 38,
        "综合职能/人力行政": 34,
        "重技术": -120,
        "强销售/客服": -180,
    }
    score += family_points.get(fam, 0)
    if fam != "其他":
        tags.append(fam)

    cscore, city = _city_score(job.location)
    score += cscore
    if city:
        tags.append(city)

    tier, boost = employer_tier(job.company_name, job.industry, job.source_id)
    if tier:
        score += boost
        tags.append(tier)
        if city in ("深圳", "广州", "成都"):
            score += 12
            tags.append("重点城市央国企")

    must = [k for k in profile.get("must_keywords", []) if k.lower() in text]
    nice = [k for k in profile.get("nice_keywords", []) if k.lower() in text]
    score += min(len(must), 3) * 5 + min(len(nice), 3) * 3
    tags += must[:3] + nice[:3]

    for kw in ("劳务派遣", "劳务外包", "第三方外包"):
        if kw in text:
            score -= 45
            risk.append(kw)

    return ScoreResult(
        score=max(0, min(200, score)),
        tags=list(dict.fromkeys(tags)),
        risk_flags=list(dict.fromkeys(risk)),
    )

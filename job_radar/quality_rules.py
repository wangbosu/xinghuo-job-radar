"""低质与污染岗位标签；缺字段只提示，不默认隐藏。"""
from __future__ import annotations

from typing import List, Tuple

from .candidate_rules import has_explicit_2027, is_heavy_tech, is_strong_sales

LOW_QUALITY_TAGS = {"代招/委托", "猎头", "劳务派遣", "强销售/客服", "重技术", "非2027正式秋招"}


def quality_tags(job) -> Tuple[List[str], List[str]]:
    title = getattr(job, "title", "") or ""
    company = getattr(job, "company_name", "") or ""
    jd = getattr(job, "jd_text", "") or ""
    url = getattr(job, "official_url", "") or ""
    deadline = getattr(job, "deadline", "") or ""
    text = f"{title} {company} {jd}"
    tags: List[str] = []
    risks: List[str] = []
    if any(k in f"{title} {company}" for k in ("代招", "委托招聘", "人力资源管理有限公司", "人才服务有限公司")):
        tags.append("代招/委托")
    if "猎头" in text.lower() or "headhunter" in text.lower():
        tags.append("猎头")
    if "劳务派遣" in text or "劳务外包" in text:
        tags.append("劳务派遣")
        risks.append("劳务派遣")
    if is_strong_sales(title, jd):
        tags.append("强销售/客服")
    if is_heavy_tech(title, jd):
        tags.append("重技术")
    if not has_explicit_2027(text):
        tags.append("非2027正式秋招")
    if not deadline:
        tags.append("缺截止")
    if not url:
        tags.append("缺官网链接")
    return list(dict.fromkeys(tags)), list(dict.fromkeys(risks))


def is_low_quality(tags: List[str]) -> bool:
    return bool(LOW_QUALITY_TAGS & set(tags or []))

"""星火雷达的 2027 正式秋招准入、岗位分类与降噪规则。

正式池宁缺毋滥：必须有明确 2027 届信号、正式校招语义，并来自官方或可信平台。
非官方线索只进 lead；社招、实习、兼职、校园大使、强销售和重技术岗位排除。
"""
from __future__ import annotations

import re
from typing import Tuple

VERIFIED = "verified"
LEAD = "lead"
EXCLUDED = "excluded"

_CYCLE_2027 = re.compile(r"(?:2027\s*届|27\s*届|2027(?:年)?(?:校园招聘|校招|秋招|graduate|campus))", re.I)
_CAMPUS = re.compile(r"校园招聘|校招|应届|毕业生|管培生|管理培训生|秋招|秋季招聘|正式批|招聘全面启动", re.I)
_AUTUMN_FORMAL = re.compile(r"秋招|秋季校园招聘|正式批|正式岗位|全职|校招|校园招聘|管培生|管理培训生", re.I)
_INTERNSHIP = re.compile(r"暑期实习|日常实习|实习生|实习岗位|summer\s+intern|internship|\bintern\b", re.I)
_SOCIAL = re.compile(r"社会招聘|社招|有经验者|[1-9]\d*\s*年(?:以上)?(?:工作)?经验|experienced\s+hire", re.I)
_NON_JOB = re.compile(r"校园大使|兼职|志愿者|训练营|夏令营|开放日|体验营", re.I)
_EVENT = re.compile(r"招聘公告|招聘启事|招聘全面启动|宣讲会|空中宣讲|双选会|专场招聘", re.I)

_SUPPORT = re.compile(r"业务支持|销售运营|渠道运营|数据分析|数据支持|订单管理|项目协调|交付|流程|计划|运营", re.I)
_SALES = re.compile(
    r"电话销售|地推|门店销售|保险销售|销售代表|销售顾问|销售工程师|招商主管|招商经理|催收|"
    r"纯客服|呼叫中心|拓展客户|陌生拜访|客户开发|拉新成交|完成销售额|销售指标|销售业绩|销售\s*KPI",
    re.I,
)
_AMBIGUOUS_SALES = re.compile(r"客户经理|营销岗|商务岗|商务专员", re.I)
_TECH_TITLE = re.compile(
    r"算法(?:工程师|研究员)?|机器学习|深度学习|数据科学家|开发工程师|软件工程师|后端|前端|客户端|"
    r"测试开发|运维开发|架构师|程序员|java|golang|嵌入式|芯片设计|编译器|computer\s+vision|data\s+scientist",
    re.I,
)
_TECH_HEAVY = re.compile(r"熟练掌握\s*(?:sql|python)|精通\s*(?:sql|python)|机器学习模型|深度学习框架|算法设计", re.I)

_OPS = re.compile(
    r"数据运营|业务运营|销售运营|渠道运营|订单运营|项目运营|运营管理|经营管理|项目管理|项目助理|"
    r"商务支持|商务专员|客户成功|产品运营|内容运营|用户运营|新媒体运营|流程管理|综合管理|运营管培",
    re.I,
)
_SUPPLY = re.compile(r"供应链|物流运营|物流管理|计划管理|生产计划|物料计划|需求计划|\bPMC\b|交付运营|采购|订单管理", re.I)
_MARKET = re.compile(r"市场运营|市场专员|市场管理|品牌运营|品牌专员|电商运营|电商管培|市场管培|营销策划|市场营销", re.I)
_GENERAL = re.compile(r"职能管培|综合职能|人力资源|招聘运营|招聘专员|行政综合|行政管理|综合管理|经营管理|商务管理", re.I)

_TRUSTED_AGGREGATORS = {"gov-ncss", "gov-sasac", "gov-qyzp", "gov-mohrss", "cn-iguopin", "gov-sz-sasac"}


def blob(job) -> str:
    extra = getattr(job, "extra", {}) or {}
    values = " ".join(str(v or "") for v in extra.values() if isinstance(v, (str, int, float)))
    return " ".join((getattr(job, "title", "") or "", getattr(job, "jd_text", "") or "", values))


def has_explicit_2027(text: str) -> bool:
    return bool(_CYCLE_2027.search(text or ""))


def is_strong_sales(title: str, jd: str) -> bool:
    text = f"{title or ''} {jd or ''}"
    if _SALES.search(text):
        return True
    return bool(_AMBIGUOUS_SALES.search(title or "") and not _SUPPORT.search(text))


def is_heavy_tech(title: str, jd: str) -> bool:
    if _TECH_TITLE.search(title or ""):
        return True
    return bool(re.search(r"数据分析师|数据工程", title or "", re.I) and _TECH_HEAVY.search(jd or ""))


def role_family(title: str, jd: str) -> str:
    text = f"{title or ''} {jd or ''}"
    if is_strong_sales(title, jd):
        return "强销售/客服"
    if is_heavy_tech(title, jd):
        return "重技术"
    if _SUPPLY.search(text):
        return "供应链/计划/交付"
    if _OPS.search(text):
        return "运营/项目"
    if _MARKET.search(text):
        return "市场/品牌/电商"
    if _GENERAL.search(text):
        return "综合职能/人力行政"
    return "其他"


def recruitment_status(job) -> Tuple[str, str]:
    text = blob(job)
    title = getattr(job, "title", "") or ""
    sid = getattr(job, "source_id", "") or ""
    stype = getattr(job, "source_type", "") or ""
    if _INTERNSHIP.search(text):
        return EXCLUDED, "实习岗位"
    if _SOCIAL.search(text):
        return EXCLUDED, "社会招聘/经验岗"
    if _NON_JOB.search(text):
        return EXCLUDED, "非正式全职岗位"
    if is_strong_sales(title, getattr(job, "jd_text", "")):
        return EXCLUDED, "强销售/客服岗位"
    if is_heavy_tech(title, getattr(job, "jd_text", "")):
        return EXCLUDED, "重技术岗位"
    if not has_explicit_2027(text):
        if _CAMPUS.search(text):
            return LEAD, "有校招信号但无法确认 2027 届"
        return EXCLUDED, "无法确认 2027 届正式秋招"
    if not (_CAMPUS.search(text) and _AUTUMN_FORMAL.search(text)):
        return LEAD, "明确 2027，但正式秋招性质待核实"
    if stype in {"official", "ats", "public_notice"} or sid in _TRUSTED_AGGREGATORS:
        return VERIFIED, "官方/可信平台明确 2027 正式校招"
    return LEAD, "非官方来源，等待官网二次确认"


def enrich_job(job):
    status, reason = recruitment_status(job)
    job.verification_status = status
    job.verification_reason = reason
    job.role_family = role_family(job.title, job.jd_text)
    text = blob(job)
    job.recruitment_type = "2027届正式校园招聘" if status == VERIFIED else ("待核实线索" if status == LEAD else "排除")
    job.job_type = "campus" if status in (VERIFIED, LEAD) else job.job_type
    job.entry_type = "招聘公告/活动" if _EVENT.search(job.title or "") else "岗位"
    extra = job.extra or {}
    job.education = str(extra.get("education") or extra.get("degree") or extra.get("degreeName") or "")
    job.major = str(extra.get("major") or extra.get("profession") or "")
    return job

"""星火秋招雷达的岗位方向和央国企识别规则。"""
from __future__ import annotations

from typing import List, Tuple

from .candidate_rules import role_family

TARGET_ROLE_SIGNAL = (
    "数据运营", "业务运营", "销售运营", "渠道运营", "订单运营", "项目运营", "运营管理",
    "项目管理", "项目助理", "商务支持", "商务专员", "市场运营", "市场专员", "品牌运营",
    "电商运营", "用户运营", "内容运营", "新媒体运营", "供应链", "物流运营", "计划管理",
    "生产计划", "物料计划", "pmc", "交付运营", "流程管理", "采购", "职能管培",
    "运营管培", "人力资源", "招聘运营", "行政综合", "客户成功", "综合管理", "经营管理",
)

CENTRAL_SOE = (
    "国家电网", "南方电网", "中国移动", "中国电信", "中国联通", "中国邮政", "招商局",
    "华润", "中信集团", "中国建筑", "中国中铁", "中国铁建", "中国交建", "中国能建",
    "中国电建", "中核集团", "中广核", "中国航天", "航空工业", "中国航发", "中国船舶",
    "中国电科", "中国电子", "国家能源", "国家电投", "中国华能", "中国华电", "中国大唐",
    "中国石油", "中国石化", "中国海油", "中粮集团", "中国中化", "中国物流",
)
SHENZHEN_SOE = (
    "深圳市投资控股", "深投控", "深圳地铁", "深业集团", "深圳能源", "深圳燃气", "深圳机场",
    "深圳巴士", "深圳水务", "深圳环境水务", "深圳国际", "特区建工", "深圳交易集团",
    "深圳人才集团", "深圳出版集团", "深圳免税", "深圳港集团", "盐田港", "深粮控股",
)
LOCAL_SOE = (
    "广州地铁", "广州发展", "广州港", "越秀集团", "广汽集团", "广州公交", "广州城投",
    "成都城投", "成都交投", "成都轨道", "成都产业集团", "成都环境集团", "成都兴城",
)
BANKS = (
    "工商银行", "建设银行", "农业银行", "中国银行", "交通银行", "招商银行", "平安银行",
    "邮储银行", "广发银行", "浦发银行", "中信银行", "兴业银行", "深圳农商银行",
)


def has_target_role_signal(title: str) -> bool:
    low = (title or "").lower()
    return any(k.lower() in low for k in TARGET_ROLE_SIGNAL)


def role_signal_score(title: str, jd_text: str) -> Tuple[int, List[str]]:
    fam = role_family(title, jd_text)
    boosts = {
        "运营/项目": 45,
        "供应链/计划/交付": 48,
        "市场/品牌/电商": 38,
        "综合职能/人力行政": 34,
        "重技术": -120,
        "强销售/客服": -180,
    }
    return boosts.get(fam, 0), ([] if fam == "其他" else [fam])


def employer_tier(company: str, industry: str, sid: str) -> Tuple[str, int]:
    c = company or ""
    if any(k in c for k in SHENZHEN_SOE):
        return "深圳市属国企", 42
    if any(k in c for k in CENTRAL_SOE):
        return "央企", 38
    if any(k in c for k in LOCAL_SOE):
        return "地方国企", 32
    if any(k in c for k in BANKS):
        return "银行校招", 25
    if sid in ("gov-sasac", "gov-qyzp", "gov-sz-sasac"):
        return "央国企", 30
    return "", 0

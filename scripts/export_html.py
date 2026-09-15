#!/usr/bin/env python3
"""生成零后端的星火秋招雷达 GitHub Pages 页面。"""
from __future__ import annotations

import html
import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from job_radar import sync

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def _records():
    with open(os.path.join(DATA, "jobs.json"), encoding="utf-8") as f:
        rows = json.load(f)
    names = {s["source_id"]: s.get("company_name", s["source_id"]) for s in sync.read_sources()}
    out = []
    for j in rows:
        if j.get("gone"):
            continue
        status = j.get("verification_status") or ("verified" if "2027" in (j.get("title", "") + j.get("jd_text", "")) else "lead")
        role = j.get("role_family") or "其他"
        tags = j.get("tags") or []
        tier = next((x for x in tags if "央企" in x or "国企" in x or "银行" in x), "")
        out.append({
            "id": j.get("dedup_key") or j.get("job_id", ""),
            "company": j.get("company_name", ""), "title": j.get("title", ""),
            "location": j.get("location", ""), "status": status,
            "status_label": "2027届正式秋招" if status == "verified" else "待核实线索",
            "recruitment_type": j.get("recruitment_type", ""),
            "publish": str(j.get("publish_time", ""))[:10], "deadline": str(j.get("deadline", ""))[:10],
            "education": j.get("education", "") or (j.get("extra") or {}).get("degree", ""),
            "major": j.get("major", "") or (j.get("extra") or {}).get("major", ""),
            "role": role, "source": names.get(j.get("source_id", ""), j.get("source_id", "")),
            "source_id": j.get("source_id", ""), "url": j.get("official_url", ""),
            "score": int(j.get("match_score", 0) or 0), "tags": tags, "tier": tier,
            "new": str(j.get("first_seen", ""))[:10] == date.today().isoformat(),
            "jd": (j.get("jd_text", "") or "")[:800],
        })
    return sorted(out, key=lambda x: (-x["score"], x["deadline"] or "9999-12-31"))


def _health():
    try:
        with open(os.path.join(DATA, "health_report.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"sources": []}


def main():
    records = _records()
    health = _health()
    payload = json.dumps(records, ensure_ascii=False).replace("</", "<\\/")
    health_payload = json.dumps(health, ensure_ascii=False).replace("</", "<\\/")
    generated = date.today().isoformat()
    page = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>星火秋招雷达</title>
<style>
:root{{--ink:#263238;--muted:#6b7280;--line:#e5e7eb;--bg:#f7f8fa;--brand:#e05d44;--green:#26734d;--blue:#245b9e}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.6 system-ui,-apple-system,"Microsoft YaHei",sans-serif}}.wrap{{max-width:1280px;margin:auto;padding:24px 18px}}header{{background:linear-gradient(135deg,#fff7f1,#fff);border:1px solid #f3ded5;border-radius:18px;padding:22px;margin-bottom:15px}}h1{{margin:0 0 4px;font-size:28px}}.sub{{color:var(--muted)}}.stats{{display:flex;gap:10px;flex-wrap:wrap;margin-top:15px}}.stat{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:8px 13px}}.stat b{{font-size:20px;margin-right:4px}}nav{{position:sticky;top:0;z-index:2;background:#fff;border:1px solid var(--line);border-radius:14px;padding:8px;display:flex;gap:7px;overflow:auto;margin-bottom:12px}}nav button{{border:0;background:#f1f3f5;border-radius:9px;padding:8px 12px;white-space:nowrap;cursor:pointer}}nav button.active{{background:var(--brand);color:#fff}}.toolbar{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}}input,select{{border:1px solid var(--line);border-radius:9px;padding:9px;background:#fff}}input{{min-width:260px;flex:1}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:12px}}.card{{background:#fff;border:1px solid var(--line);border-radius:15px;padding:15px;box-shadow:0 4px 12px #1f29370b}}.card h3{{font-size:16px;margin:0 0 3px}}.company{{font-weight:600;color:#374151}}.meta{{color:var(--muted);font-size:13px;margin:8px 0}}.badge{{display:inline-block;border-radius:999px;padding:2px 8px;margin:2px 3px 2px 0;background:#eef2ff;color:#334e9b;font-size:12px}}.verified{{background:#e8f6ed;color:var(--green)}}.lead{{background:#fff2d9;color:#8a5a00}}.score{{float:right;color:var(--brand);font-weight:700;font-size:20px}}.actions{{margin-top:10px;display:flex;gap:8px;align-items:center}}a.btn{{text-decoration:none;background:#263238;color:#fff;padding:6px 10px;border-radius:8px}}button.save{{border:1px solid var(--line);background:#fff;padding:6px 10px;border-radius:8px;cursor:pointer}}.empty{{padding:35px;text-align:center;color:var(--muted)}}.health{{background:#fff;border:1px solid var(--line);border-radius:14px;padding:15px;margin-top:15px}}.health table{{width:100%;border-collapse:collapse}}.health td,.health th{{padding:6px;border-bottom:1px solid var(--line);text-align:left;font-size:12px}}footer{{color:var(--muted);margin-top:18px;font-size:12px}}
</style></head><body><main class="wrap"><header><h1>星火秋招雷达</h1><div class="sub">只把明确的 2027 届正式校园招聘放入正式推荐池；不确定的职位进入待核实线索池。更新时间：{generated}</div><div class="stats"><span class="stat"><b id="formalCount">0</b>正式岗位</span><span class="stat"><b id="leadCount">0</b>待核实</span><span class="stat"><b id="szCount">0</b>深圳</span><span class="stat"><b id="soeCount">0</b>央国企/市属国企</span></div></header>
<nav id="tabs"></nav><div class="toolbar"><input id="q" placeholder="搜索公司、岗位、城市、专业…"><select id="sort"><option value="score">匹配分优先</option><option value="deadline">截止日期优先</option><option value="new">今日新增优先</option></select></div><section id="list" class="grid"></section><section class="health"><b>信源状态</b><div id="health"></div></section><footer>公开页面不保存个人姓名、学校、简历或联系方式；投递看板仅保存在当前浏览器 localStorage。原始岗位链接均指向来源页面。</footer></main>
<script>const DATA={payload};const HEALTH={health_payload};const tabs=[['all','今日新增'],['sz','深圳优先'],['gz','广州'],['cd','成都'],['soe','央企/国企/深圳市属国企'],['运营/项目','运营/项目'],['供应链/计划/交付','供应链/计划/交付'],['市场/品牌/电商','市场/品牌/电商'],['综合职能/人力行政','综合职能/人力行政'],['lead','待核实线索'],['deadline','即将截止'],['board','投递看板']];let current='all';const $=id=>document.getElementById(id);function formal(x){{return x.status==='verified'}}function visible(x){{if(current==='lead')return x.status==='lead';if(current==='all')return formal(x)&&x.new;if(current==='sz')return formal(x)&&x.location.includes('深圳');if(current==='gz')return formal(x)&&x.location.includes('广州');if(current==='cd')return formal(x)&&x.location.includes('成都');if(current==='soe')return formal(x)&&!!x.tier;if(current==='deadline')return formal(x)&&x.deadline&&x.deadline>='{generated}'&&x.deadline<='9999-12-31';if(current==='board')return (JSON.parse(localStorage.getItem('xinghuo-board')||'{{}}')[x.id]);return formal(x)&&x.role===current}}function esc(s){{return String(s||'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]))}}function renderTabs(){{$('tabs').innerHTML=tabs.map(t=>`<button class="${{current===t[0]?'active':''}}" data-tab="${{t[0]}}">${{t[1]}}</button>`).join('');document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>{{current=b.dataset.tab;renderTabs();render()}})}}function render(){{let q=$('q').value.trim().toLowerCase();let arr=DATA.filter(visible).filter(x=>!q||JSON.stringify(x).toLowerCase().includes(q));let sort=$('sort').value;if(sort==='deadline')arr.sort((a,b)=>(a.deadline||'9999').localeCompare(b.deadline||'9999'));if(sort==='new')arr.sort((a,b)=>Number(b.new)-Number(a.new)||b.score-a.score);$('list').innerHTML=arr.length?arr.map(card).join(''):'<div class="empty">当前栏目暂无符合条件的岗位</div>';document.querySelectorAll('[data-save]').forEach(b=>b.onclick=()=>{{let s=JSON.parse(localStorage.getItem('xinghuo-board')||'{{}}');s[b.dataset.save]=!s[b.dataset.save];localStorage.setItem('xinghuo-board',JSON.stringify(s));render()}})}}function card(x){{let cls=x.status==='verified'?'verified':'lead';return `<article class="card"><span class="score">${{x.score}}</span><h3>${{esc(x.title)}}</h3><div class="company">${{esc(x.company)}} · ${{esc(x.location||'地点待核')}}</div><div class="meta">${{esc(x.status_label)}} · 发布 ${{esc(x.publish||'未知')}} · 截止 ${{esc(x.deadline||'未标注')}}</div><span class="badge ${{cls}}">${{esc(x.status_label)}}</span><span class="badge">${{esc(x.role)}}</span>${{x.tier?`<span class="badge verified">${{esc(x.tier)}}</span>`:''}}<div class="meta">学历：${{esc(x.education||'未标注')}}　专业：${{esc(x.major||'未标注')}}<br>来源：${{esc(x.source)}}</div><div class="actions">${{x.url?`<a class="btn" target="_blank" rel="noopener noreferrer" href="${{esc(x.url)}}">官方投递链接</a>`:''}}<button class="save" data-save="${{esc(x.id)}}">${{JSON.parse(localStorage.getItem('xinghuo-board')||'{{}}')[x.id]?'已加入投递看板':'加入投递看板'}}</button></div></article>`}}$('q').oninput=render;$('sort').onchange=render;const formalN=DATA.filter(formal).length;$('formalCount').textContent=formalN;$('leadCount').textContent=DATA.filter(x=>x.status==='lead').length;$('szCount').textContent=DATA.filter(x=>formal(x)&&x.location.includes('深圳')).length;$('soeCount').textContent=DATA.filter(x=>formal(x)&&x.tier).length;renderTabs();render();$('health').innerHTML=`<small>目录信源 ${{(HEALTH.sources||[]).length}} 个；本次入库 ${{HEALTH.store_total||DATA.length}} 条。${{(HEALTH.sources||[]).filter(x=>x.status==='blocked'||x.status==='unstable').length}} 个信源需关注。</small>`;</script></body></html>'''
    with open(os.path.join(DATA, "jobs.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print(f"✅ 导出 {len(records)} 条岗位记录 → data/jobs.html")


if __name__ == "__main__":
    main()

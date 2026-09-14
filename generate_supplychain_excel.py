#!/usr/bin/env python3
"""Build a formatted Excel summarizing supply-chain transparency / traceability
requirements across the five V0 sources (SSE, HKEX, GRI, MSCI, CSA-COS).

Every row quotes the stored `original_text` from the ALREADY-PARSED source
clauses (data/output/p2a-p2d) with its real clause_id + source_locator.
No fabrication, no re-reading of protected PDFs. Deterministic Excel only.
"""
from __future__ import annotations

import json
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

OUT = Path("data/output/供应链透明度与可追溯_信息归纳.xlsx")
HITS = json.loads(Path("supplychain_real_hits.json").read_text(encoding="utf-8"))


def find(src_key: str, pred) -> dict:
    """Return first hit under a top-level source whose fields satisfy pred."""
    for h in HITS[src_key]:
        if pred(h):
            return h
    raise KeyError(f"no match in {src_key}")


def by_clause(src_key, num):
    return find(src_key, lambda h: h["clause_number"] == num)


def by_head(src_key, needle):
    return find(src_key, lambda h: needle in (h["heading"] or "") or needle in (h["src"] or ""))


# ── Curated rows: (family, source_label, ref, topic, quoted_text, locator, relevance★) ──
# quoted_text pulled from real original_text; trimmed to the relevant portion,
# never reworded. relevance ★ = directly about transparency/traceability.
ROWS = []


def add(family, label, ref, topic, text, locator, star=False, clause_id=""):
    ROWS.append({
        "family": family, "label": label, "ref": ref, "topic": topic,
        "text": text.strip(), "locator": locator, "star": star, "clause_id": clause_id,
    })


# ---------- SSE 上交所（交易所披露规则 exchange_rule）----------
c = by_clause("SSE", "第四十五条")
add("交易所披露规则\nexchange_rule", "上交所 SSE\n可持续发展报告指引", "第四十五条 ★",
    "供应链风险管理与安全稳定",
    c["text"], "SSE 第四章 · 第三节 供应商与客户", star=True, clause_id=c["clause_id"])

c = by_clause("SSE", "第四十四条")
add("交易所披露规则\nexchange_rule", "上交所 SSE\n可持续发展报告指引", "第四十四条",
    "诚信对待供应商", c["text"], "SSE 第四章 社会信息披露", clause_id=c["clause_id"])

c = by_clause("SSE", "第四十六条")
add("交易所披露规则\nexchange_rule", "上交所 SSE\n可持续发展报告指引", "第四十六条",
    "对中小企业供应商的账期与逾期款",
    c["text"], "SSE 第四章 社会信息披露", clause_id=c["clause_id"])

c = by_clause("SSE", "第五十二条")
add("交易所披露规则\nexchange_rule", "上交所 SSE\n可持续发展报告指引", "第五十二条 ★",
    "负面影响/风险的尽职调查",
    c["text"], "SSE 第五章 治理信息披露", star=True, clause_id=c["clause_id"])

c = by_clause("SSE", "第十四条")
add("交易所披露规则\nexchange_rule", "上交所 SSE\n可持续发展报告指引", "第十四条",
    "供应链相关风险机遇影响",
    "本所鼓励披露主体结合实际情况披露可持续发展相关风险和机遇在当期对公司商业模式、主要供应商和其他利益相关方产生的影响……披露主体应当充分识别、评估公司的采购、生产、销售、服务、内部管理、对外投资、社会活动等对经济、社会、环境是否存在重大影响。",
    "SSE 第二章 披露框架", clause_id=c["clause_id"])

c = by_clause("SSE", "第五十九条")
add("交易所披露规则\nexchange_rule", "上交所 SSE\n可持续发展报告指引", "第五十九条（释义）",
    "「供应链」「价值链」定义",
    "（十九）价值链：指与上市公司的商业模式和它所处的外部环境有关的全部活动、资源和关系……材料和服务采购以及产品和服务的销售和交付……（二十）供应链：指为上市公司开发自有产品或服务而提供产品或服务的上游实体所开展的一系列活动。",
    "SSE 第六章 附则和释义", clause_id=c["clause_id"])

# ---------- HKEX 港交所（交易所ESG披露守则 exchange_rule）----------
for num, ref, topic, star in [
    ("B5", "Aspect B5（一般披露）", "供应链管理 · 环境及社会风险政策", False),
    ("B5.1", "KPI B5.1", "供应商分布（按地区）", False),
    ("B5.2", "KPI B5.2", "供应商聘用与监察慣例", False),
    ("B5.3", "KPI B5.3 ★", "识别供应链每个环节的环境/社会风险", True),
    ("B5.4", "KPI B5.4", "绿色采购（环保产品/服务）", False),
]:
    c = by_clause("HKEX", num)
    add("交易所ESG披露守则\nexchange_rule", "港交所 HKEX\nESG报告守则(附录C2)", ref, topic,
        c["text"], c["locator"], star=star, clause_id=c["clause_id"])

# ---------- GRI（报告标准 reporting_standard）----------
def gri(std_needle, head_needle, ref_num, ref_label, topic, text, star=False):
    c = find("GRI", lambda h: std_needle in h["src"] and head_needle in (h["heading"] or ""))
    add("报告标准\nreporting_standard", f"GRI {std_needle.split('_')[1]}", ref_label, topic, text,
        c["locator"] or c["src"].replace("GRI · ", "GRI "), star=star, clause_id=c["clause_id"])

gri("GRI_204", "204-1", "REQUIREMENTS", "204-1", "采购实践·本地供应商",
    "本地采购支出：Percentage of the procurement budget used for significant locations of operation that is spent on suppliers local to that operation… The organization's geographical definition of 'local'.（用于当地供应商的采购预算百分比及'本地'的界定）")
gri("GRI_308", "308-1", "REQUIREMENTS", "308-1", "新供应商环境筛选",
    "Percentage of new suppliers that were screened using environmental criteria.（使用环境标准筛选的新供应商百分比）")
gri("GRI_308", "308-2", "GUIDANCE", "308-2 ★", "供应链负面环境影响",
    "Negative environmental impacts in the supply chain and actions taken：processes used, such as due diligence, to identify and assess significant actual and potential negative environmental impacts in the supply chain; …actions taken to address the significant… impacts.（识别、评估并应对供应链中的负面环境影响）", star=True)
gri("GRI_414", "414-1", "REQUIREMENTS", "414-1", "新供应商社会筛选",
    "Percentage of new suppliers that were screened using social criteria.（使用社会标准筛选的新供应商百分比）")
gri("GRI_414", "414-2", "GUIDANCE", "414-2 ★", "供应链负面社会影响",
    "Negative social impacts in the supply chain and actions taken：processes used, such as due diligence, to identify and assess significant actual and potential negative social impacts in the supply chain.（识别、评估并应对供应链中的负面社会影响）", star=True)

# ---------- MSCI（评级方法 rating_methodology）----------
def msci(needle, ref, topic, text, star=False):
    c = find("MSCI", lambda h: needle in h["src"])
    add("评级方法\nrating_methodology", "MSCI ESG Ratings", ref, topic, text,
        c["src"].replace("MSCI · ", "MSCI / ") , star=star, clause_id=c["clause_id"])

msci("supply-chain-labor-standards", "Key Issue · Supply Chain Labor Standards ★",
     "供应链劳工标准",
     "Assesses the company's ability to manage its exposure to risks related to the management and transparency of its supply chain：Scope of supplier code of conduct / Scope of supplier audits / Extent of disclosure on instances of supplier misconduct / Effectiveness of grievance mechanisms.（供应链管理与透明度：供应商行为准则、供应商审核范围、供应商违规披露程度、申诉机制有效性）", star=True)
msci("raw-materials-sourcing", "Key Issue · Raw Material Sourcing ★",
     "原材料采购（可追溯核心）",
     "Evaluates the company's initiatives to manage the environmental and social impacts of… sourcing through policies, certification, traceability and supplier programs：Extent of traceability to place of origin / responsible sourcing commitments / percentage third-party certified.（通过政策、认证、可追溯与供应商项目管理原料采购影响；追溯至原产地的程度、第三方认证比例）", star=True)
msci("controversial-sourcing", "Key Issue · Controversial Sourcing ★",
     "争议性采购",
     "Evaluates exposure to, and management of, risks from sourcing from conflict-affected/high-risk sources. Risks: costs to comply with new regulations (e.g., Corporate Sustainability Due Diligence Directive (CSDDD), U.S. Dodd-Frank Act).（评估从冲突/高风险来源采购的风险敞口与管理，涉及 CSDDD、多德-弗兰克法案等尽职调查监管）", star=True)

# ---------- CSA-COS（评级问卷 rating_questionnaire）----------
def csa(needle, ref, topic, text, star=False):
    c = find("CSA-COS", lambda h: needle in (h["heading"] or ""))
    add("评级问卷\nrating_questionnaire", "CSA-COS\n(S&P Global CSA)", ref, topic, text,
        c["heading"], star=star, clause_id=c["clause_id"])

csa("Supplier Code of Conduct", "Supplier Code of Conduct",
    "供应商行为准则",
    "Does the company have a supplier code of conduct — whether it is public and what issues it covers. A general supplier code of conduct summarizes the basic commitments a company requires from its suppliers.（公司是否有供应商行为准则、是否公开、覆盖哪些议题）")
csa("Supplier ESG Programs", "Supplier ESG Programs ★",
    "供应商ESG项目",
    "Evaluates whether companies have systems/procedures to ensure effective implementation of supplier ESG programs and to identify and address material risks and impacts resulting from supply activities… to track the impact of ESG along their supply chains.（是否建立体系以落实供应商ESG项目、识别并应对供应活动的重大风险，追踪供应链ESG影响）", star=True)
csa("Supplier Assessment and Development", "Supplier Assessment & Development ★",
    "供应商评估与发展",
    "Assesses if companies have a systematic approach to evaluating suppliers and their subsequent development… identification, monitoring and management of risks and opportunities in the supply chain.（是否系统性评估并发展供应商，识别、监测并管理供应链风险与机遇）", star=True)
csa("KPIs for Supplier Assessment", "KPIs · Supplier Assessment ★",
    "供应商评估KPI（透明度）",
    "Does the company monitor and report on the coverage and progress of its supplier screening, assessment and development programs — how many suppliers it has, how many are assessed, and how many are identified as having significant actual/potential negative impacts.（监测并报告供应商筛选/评估/发展项目的覆盖与进展：供应商总数、受评数、被识别有重大负面影响数）", star=True)


# ── Excel styling ────────────────────────────────────────────────────────
HEADERS = ["序号", "来源族", "来源 / 文件", "章节 / 条款",
           "主题（供应链透明度·可追溯）", "原文摘录（保留原始表述）",
           "出处 / 定位", "Clause ID"]

FAMILY_FILL = {
    "交易所披露规则": "FCE4D6", "交易所ESG披露守则": "DDEBF7",
    "报告标准": "E2EFDA", "评级方法": "FFF2CC", "评级问卷": "EAD1DC",
}


def fill_for(family: str) -> str:
    for k, v in FAMILY_FILL.items():
        if family.startswith(k):
            return v
    return "FFFFFF"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.Workbook()

    # ── Sheet 1: 说明 ──
    info = wb.active
    info.title = "说明"
    info.sheet_view.showGridLines = False
    info["A1"] = "供应链透明度 · 供应链可追溯 —— 标准/框架/指引 信息归纳"
    info["A1"].font = Font(size=15, bold=True, color="1F4E79")
    star_ct = sum(1 for r in ROWS if r["star"])
    notes = [
        "",
        "主题：从现有 V0 五个信息源【已解析条款】中归纳「供应链透明度 / 供应链可追溯」相关要求。",
        "",
        "覆盖来源（5 源 · 4 类源族）：",
        "   • 上交所 SSE —— 交易所披露规则（可持续发展报告指引）exchange_rule",
        "   • 港交所 HKEX —— 交易所 ESG 报告守则（附录 C2）exchange_rule",
        "   • GRI —— 国际报告标准 reporting_standard（GRI 204 / 308 / 414）",
        "   • MSCI —— ESG 评级方法 rating_methodology（3 个供应链相关 Key Issue）",
        "   • CSA-COS —— S&P Global 企业可持续发展评估问卷 rating_questionnaire",
        "",
        "阅读说明：",
        "   • 「明细」页按来源族分组，同色块为同一源族。",
        "   • 标记 ★ 的条目与「透明度/可追溯」直接相关（供应链风险识别、影响追溯、原产地可追溯、供应商审核披露等）。",
        "   • 原文摘录列保留来源原始表述（中英文各按原文），不改写不可变的 original_text；",
        "     出处/定位列与 Clause ID 均来自已解析条款库（data/output/p2a–p2d），可回溯核对。",
        "   • 本表为归纳草稿（AI 提议、需人工复核）。",
        "",
        f"条目数：{len(ROWS)}（其中直接相关 ★ {star_ct} 条）",
        "数据来源：data/output/p2a (SSE/HKEX)、p2b (GRI)、p2c (MSCI)、p2d (CSA-COS)",
        "生成日期：2026-09-07",
    ]
    for i, line in enumerate(notes, start=2):
        info[f"A{i}"] = line
        if line.startswith("覆盖来源") or line.startswith("阅读说明"):
            info[f"A{i}"].font = Font(bold=True, size=11)
    info.column_dimensions["A"].width = 96

    # ── Sheet 2: 明细 ──
    ws = wb.create_sheet("明细")
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = "A2"

    thin = Side(style="thin", color="BFBFBF")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    hfill = PatternFill("solid", fgColor="1F4E79")
    for c_, h in enumerate(HEADERS, start=1):
        cell = ws.cell(row=1, column=c_, value=h)
        cell.font = Font(bold=True, color="FFFFFF", size=10)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.fill = hfill
        cell.border = border
    ws.row_dimensions[1].height = 36

    for idx, r in enumerate(ROWS, start=1):
        row = idx + 1
        values = [idx, r["family"], r["label"], r["ref"], r["topic"],
                  r["text"], r["locator"], r["clause_id"]]
        fill = PatternFill("solid", fgColor=fill_for(r["family"]))
        for c_, val in enumerate(values, start=1):
            cell = ws.cell(row=row, column=c_, value=val)
            cell.border = border
            cell.fill = fill
            ha = "center" if c_ in (1,) else "left"
            cell.alignment = Alignment(horizontal=ha, vertical="top", wrap_text=True)
            if c_ == 5:
                cell.font = Font(bold=True, size=10,
                                 color="C00000" if r["star"] else "000000")
            elif c_ == 4 and r["star"]:
                cell.font = Font(bold=True, color="C00000", size=10)
            elif c_ == 8:
                cell.font = Font(size=8, color="808080")
            else:
                cell.font = Font(size=10)

    widths = [5, 15, 18, 20, 26, 66, 26, 16]
    for c_, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(c_)].width = w

    for row in range(2, len(ROWS) + 2):
        txt = ROWS[row - 2]["text"]
        # rough auto-height: ~62 chars per line at width 66
        lines = max(3, (len(txt) // 40) + txt.count("\n") + 1)
        ws.row_dimensions[row].height = min(220, 15 * lines + 8)

    wb.save(OUT)
    print(f"wrote {OUT}  ({len(ROWS)} rows, {star_ct} starred)")


if __name__ == "__main__":
    main()
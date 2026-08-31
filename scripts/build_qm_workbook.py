#!/usr/bin/env python3
"""Build the Quality Management Department collection workbook.

Generates data/output/final/数据收集表—质量管理部_ClaudeCode_Review.xlsx
with six sheets, from curated Claude-Code semantic analyst judgments
grounded in real ingested source evidence.

LOCAL output only (git-ignored). Not client-approved.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.pipeline.qm_collection import (
    QM_TOPICS,
    CollectionItem,
    InformationPoint,
    _verify_sources,
)

# --- Topic short codes ---
T_PSQ = "产品和服务安全与质量"
T_CHEM = "化学品安全与成分管理"
T_MKT = "负责任营销"

# ---------------------------------------------------------------------------
# Information Points — curated from semantic review of real evidence.
# source_unit_ids reference real ingested SourceClause codes.
# ---------------------------------------------------------------------------
INFORMATION_POINTS: list[InformationPoint] = [
    # ===== 产品和服务安全与质量 =====
    InformationPoint(
        "PSQ-IP-01", T_PSQ, "治理", "产品质量与安全治理结构与职责", "qualitative",
        ["第四十七条"], ["SSE"], "FRAMEWORK_AND_HUMAN_BASELINE",
        ["Q001"], semantic_reason="SSE 第47条要求披露产品和服务安全与质量管理基本情况，涵盖治理与责任主体。"),
    InformationPoint(
        "PSQ-IP-02", T_PSQ, "战略", "质量管理体系与制度建设", "qualitative",
        ["第四十七条", "GRI 416-1"], ["SSE", "GRI"], "FRAMEWORK_AND_HUMAN_BASELINE",
        ["Q002", "Q003"], semantic_reason="SSE 第47条(一)质量管理体系/制度建设；GRI 416-1关注产品全生命周期健康安全评估。"),
    InformationPoint(
        "PSQ-IP-03", T_PSQ, "影响、风险和机遇管理", "质量安全风险识别与检验放行控制", "qualitative",
        ["第四十七条", "GRI 416-1"], ["SSE", "GRI"], "FRAMEWORK_AND_HUMAN_BASELINE",
        ["Q004", "Q005", "Q006"], semantic_reason="产品从原料到放行的质量安全风险识别、评估、监测；GRI 416-1生命周期健康安全评估。"),
    InformationPoint(
        "PSQ-IP-04", T_PSQ, "指标与目标", "质量安全认证情况", "qualitative",
        ["第四十七条"], ["SSE"], "FRAMEWORK_BACKED",
        [], semantic_reason="SSE 第47条(二)质量管理相关认证及产品/服务体系认证情况。"),
    InformationPoint(
        "PSQ-IP-05", T_PSQ, "指标与目标", "重大质量安全事故", "quantitative",
        ["第四十七条"], ["SSE"], "FRAMEWORK_AND_HUMAN_BASELINE",
        ["Q007"], semantic_reason="SSE 第47条(三)报告期内产品/服务安全与质量重大责任事故，含性质、影响、金额、进展。"),
    InformationPoint(
        "PSQ-IP-06", T_PSQ, "指标与目标", "产品召回与客户投诉处理", "quantitative",
        ["第四十七条", "GRI 416-2"], ["SSE", "GRI"], "FRAMEWORK_AND_HUMAN_BASELINE",
        ["Q007"], semantic_reason="SSE 第47条(四)售后/召回制度与投诉处理；GRI 416-2产品服务健康安全违规事件。"),
    InformationPoint(
        "PSQ-IP-07", T_PSQ, "案例实践", "质量安全管理实践案例", "qualitative",
        ["第四十七条"], ["SSE"], "FRAMEWORK_AND_HUMAN_BASELINE",
        ["Q008"], semantic_reason="围绕质量安全的具体管理措施、执行过程与成效案例（人工基线保留）。"),

    # ===== 化学品安全与成分管理 =====
    InformationPoint(
        "CHM-IP-01", T_CHEM, "治理", "化学品与成分管理治理与职责", "qualitative",
        ["第四十七条"], ["SSE"], "FRAMEWORK_AND_HUMAN_BASELINE",
        ["Q009"], department_fit="OK",
        semantic_reason="化妆品成分/化学品安全属于产品质量安全治理范畴；SSE 第47条产品安全质量管理涵盖。"),
    InformationPoint(
        "CHM-IP-02", T_CHEM, "战略", "原料/成分准入与安全评估制度", "qualitative",
        ["GRI 301-2"], ["GRI"], "FRAMEWORK_AND_HUMAN_BASELINE",
        ["Q010", "Q011"], semantic_reason="GRI 301 Materials关注投入材料；化妆品原料准入、禁限用核验与安全评估制度。"),
    InformationPoint(
        "CHM-IP-03", T_CHEM, "影响、风险和机遇管理", "化学品风险识别与SDS/异常处置", "qualitative",
        ["MSCI Chemical Safety Key Issue | March 2026"], ["MSCI"], "FRAMEWORK_AND_HUMAN_BASELINE",
        ["Q012", "Q013", "Q014"], semantic_reason="MSCI Chemical Safety Key Issue评价企业对化学品暴露风险的管理能力（评级方法，非披露义务）。"),
    InformationPoint(
        "CHM-IP-04", T_CHEM, "指标与目标", "禁限用物质核验与合规指标", "quantitative",
        ["GRI 301-2"], ["GRI"], "FRAMEWORK_BACKED",
        ["Q015"], department_fit="REVIEW_REQUIRED",
        semantic_reason="成分合规/禁限用核验的量化跟踪；具体指标定义需顾问与部门确认。"),
    InformationPoint(
        "CHM-IP-05", T_CHEM, "案例实践", "化学品安全管理实践案例", "qualitative",
        ["MSCI Chemical Safety Key Issue | March 2026"], ["MSCI"], "FRAMEWORK_AND_HUMAN_BASELINE",
        ["Q016"], semantic_reason="化学品/成分安全管理具体案例（人工基线保留）。"),

    # ===== 负责任营销 =====
    InformationPoint(
        "MKT-IP-01", T_MKT, "治理", "营销合规治理与职责", "qualitative",
        ["GRI 417-1"], ["GRI"], "FRAMEWORK_AND_HUMAN_BASELINE",
        ["Q017"], department_fit="REVIEW_REQUIRED",
        semantic_reason="GRI 417 Marketing and Labeling关注产品信息与标签；治理归属需与市场/品牌部门界定。"),
    InformationPoint(
        "MKT-IP-02", T_MKT, "战略", "功效宣称与标签合规制度", "qualitative",
        ["GRI 417-1"], ["GRI"], "FRAMEWORK_AND_HUMAN_BASELINE",
        ["Q018", "Q019"], semantic_reason="GRI 417-1要求披露产品/服务信息与标签要求；化妆品功效宣称与标签真实合规。"),
    InformationPoint(
        "MKT-IP-03", T_MKT, "影响、风险和机遇管理", "营销/宣称合规风险与证据核验", "qualitative",
        ["GRI 417-1"], ["GRI"], "FRAMEWORK_AND_HUMAN_BASELINE",
        ["Q020", "Q021", "Q022"], department_fit="REVIEW_REQUIRED",
        semantic_reason="广告/直播/达人合作/功效宣称的合规风险识别与管理；部分执行归市场部门（department_fit待确认）。"),
    InformationPoint(
        "MKT-IP-04", T_MKT, "指标与目标", "营销合规违规事件", "quantitative",
        ["GRI 417-2", "GRI 417-3"], ["GRI"], "FRAMEWORK_AND_HUMAN_BASELINE",
        ["Q023"], semantic_reason="GRI 417-2/417-3产品信息标签与营销传播违规事件数量（Disclosure）。"),
    InformationPoint(
        "MKT-IP-05", T_MKT, "案例实践", "负责任营销实践案例", "qualitative",
        ["GRI 417-1"], ["GRI"], "FRAMEWORK_AND_HUMAN_BASELINE",
        ["Q024"], department_fit="REVIEW_REQUIRED",
        semantic_reason="负责任营销具体案例（人工基线保留）。"),
]


def build_collection_items() -> list[CollectionItem]:
    items: list[CollectionItem] = []
    n = 0

    def qid(prefix):
        nonlocal n
        n += 1
        return f"QM-{prefix}-{n:03d}"

    # Qualitative + quantitative items derived from information points.
    for ip in INFORMATION_POINTS:
        base = dict(
            topic=ip.topic, dimension=ip.dimension, ip_id=ip.ip_id,
            source_nature=ip.source_nature, human_question_ids=ip.human_question_ids,
            source_frameworks=ip.source_frameworks, source_unit_ids=ip.source_unit_ids,
            department_fit=ip.department_fit,
        )
        if ip.kind in ("qualitative", "both"):
            items.append(CollectionItem(
                item_id=qid("QL"), kind="qualitative",
                question=_qual_question(ip), guidance=_qual_guidance(ip), **base))
        if ip.kind in ("quantitative", "both"):
            items.append(CollectionItem(
                item_id=qid("QN"), kind="quantitative",
                question=_quant_question(ip), guidance="按报告期据实填报；无相关事项填0并说明。",
                **_quant_fields(ip), **base))
    return items


def _qual_question(ip: InformationPoint) -> str:
    m = {
        "PSQ-IP-01": "请说明公司在产品和服务安全与质量方面的治理结构与职责分工，包括负责管理、监督及重大事项决策的主体。",
        "PSQ-IP-02": "请说明公司已建立的产品质量与安全管理体系、制度或内部规范，及其在报告期内的建设与执行情况。",
        "PSQ-IP-03": "请说明公司在原料、配方、生产、检验、放行到上市后监测与召回各环节，识别、评估和监测质量安全风险的流程与关键控制措施。",
        "PSQ-IP-04": "请列示公司获得的质量管理相关认证，以及主要产品/服务的质量管理体系认证情况。",
        "PSQ-IP-07": "请提供报告期内围绕产品质量安全管理的具体实践案例，说明采取的措施、执行过程与实际成效。",
        "CHM-IP-01": "请说明公司在化学品安全与成分管理方面的治理结构与职责分工。",
        "CHM-IP-02": "请说明公司对化妆品原料、配方成分及研发生产用化学品的准入、禁限用核验与安全评估制度及其执行情况。",
        "CHM-IP-03": "请说明公司识别、评估和管理化学品/成分相关风险的流程，包括原料审核、安全评估、SDS管理与异常处置等安排。",
        "CHM-IP-05": "请提供报告期内化学品安全与成分管理的具体实践案例，说明措施、执行过程与成效。",
        "MKT-IP-01": "请说明公司在负责任营销方面的治理结构与职责分工（如涉及市场/品牌等其他部门，请一并说明协作关系）。",
        "MKT-IP-02": "请说明公司针对广告、功效宣称、标签与消费者沟通真实性与合规性建立的制度、审查与实施机制。",
        "MKT-IP-03": "请说明公司识别、评估和管理营销与功效宣称合规风险的流程，包括营销审查、达人/平台管理、功效证据核验与违规处置。",
        "MKT-IP-05": "请提供报告期内负责任营销的具体实践案例，说明措施、执行过程与成效。",
    }
    return m.get(ip.ip_id, f"请说明公司在「{ip.label}」方面的情况。")


def _qual_guidance(ip: InformationPoint) -> str:
    return f"对标{'/'.join(ip.source_frameworks)}；请提供具体制度/流程/证据，避免笼统描述。"


def _quant_question(ip: InformationPoint) -> str:
    m = {
        "PSQ-IP-05": "报告期内发生的产品和服务安全与质量重大责任事故数量及相关信息。",
        "PSQ-IP-06": "报告期内产品召回次数、涉及批次/数量，以及客户投诉受理与处理数量。",
        "CHM-IP-04": "报告期内禁限用物质核验/成分合规检查的相关量化指标。",
        "MKT-IP-04": "报告期内营销传播与产品信息标签相关违规事件数量。",
    }
    return m.get(ip.ip_id, f"{ip.label}相关量化数据。")


def _quant_fields(ip: InformationPoint) -> dict:
    m = {
        "PSQ-IP-05": dict(metric_name="重大质量安全责任事故数量", unit="起",
                          period="报告期(2026年度)", boundary="宜格集团合并范围",
                          breakdown="按事件性质(如行政处罚)", frequency="年度",
                          calc_guidance="列示每起事故性质、影响、涉及金额及应对进展；无则填0。"),
        "PSQ-IP-06": dict(metric_name="产品召回次数 / 客户投诉处理数量", unit="次 / 件",
                          period="报告期(2026年度)", boundary="宜格集团合并范围",
                          breakdown="召回批次数量；投诉受理/办结数量", frequency="年度",
                          calc_guidance="分别填报召回次数、涉及批次数量、投诉受理与办结数量。"),
        "CHM-IP-04": dict(metric_name="禁限用物质核验/成分合规指标", unit="待确认",
                          period="报告期(2026年度)", boundary="宜格集团合并范围",
                          frequency="年度",
                          calc_guidance="指标口径需顾问与质量管理部共同确认（REVIEW_REQUIRED）。"),
        "MKT-IP-04": dict(metric_name="营销/标签合规违规事件数量", unit="起",
                          period="报告期(2026年度)", boundary="宜格集团合并范围",
                          breakdown="按违规类型(法规/自愿准则)", frequency="年度",
                          calc_guidance="对标GRI 417-2/417-3口径统计违规事件；无则填0。"),
    }
    return m.get(ip.ip_id, dict(period="报告期(2026年度)", frequency="年度"))


# --- Human question transformation ledger (all 24) ---
HUMAN_TRANSFORM = [
    # (qid, topic, dim, diagnosis, action, ip_ids)
    ("Q001", T_PSQ, "治理", "MULTI_INFORMATION_POINT", "SPLIT→治理结构+职责+决策", "PSQ-IP-01"),
    ("Q002", T_PSQ, "治理", "制度建设，可支持", "REWRITE", "PSQ-IP-02"),
    ("Q003", T_PSQ, "战略", "TOO_BROAD(全价值链)", "REWRITE→聚焦体系融入", "PSQ-IP-02"),
    ("Q004", T_PSQ, "影响、风险和机遇管理", "风险识别依据", "MERGE→风险流程", "PSQ-IP-03"),
    ("Q005", T_PSQ, "影响、风险和机遇管理", "风险清单", "MERGE→风险流程", "PSQ-IP-03"),
    ("Q006", T_PSQ, "影响、风险和机遇管理", "风险管理流程", "MERGE→风险流程", "PSQ-IP-03"),
    ("Q007", T_PSQ, "指标与目标", "MULTI+隐藏定量", "SPLIT→认证/事故/召回投诉(定量)", "PSQ-IP-04;PSQ-IP-05;PSQ-IP-06"),
    ("Q008", T_PSQ, "案例实践", "案例", "RETAIN", "PSQ-IP-07"),
    ("Q009", T_CHEM, "治理", "MULTI_INFORMATION_POINT", "SPLIT→治理", "CHM-IP-01"),
    ("Q010", T_CHEM, "治理", "制度建设", "MERGE→准入制度", "CHM-IP-02"),
    ("Q011", T_CHEM, "战略", "TOO_BROAD", "MERGE→准入制度", "CHM-IP-02"),
    ("Q012", T_CHEM, "影响、风险和机遇管理", "风险依据", "MERGE→风险流程", "CHM-IP-03"),
    ("Q013", T_CHEM, "影响、风险和机遇管理", "风险清单", "MERGE→风险流程", "CHM-IP-03"),
    ("Q014", T_CHEM, "影响、风险和机遇管理", "风险管理流程", "MERGE→风险流程", "CHM-IP-03"),
    ("Q015", T_CHEM, "指标与目标", "隐藏定量", "REWRITE→合规指标(定量,待确认)", "CHM-IP-04"),
    ("Q016", T_CHEM, "案例实践", "案例", "RETAIN", "CHM-IP-05"),
    ("Q017", T_MKT, "治理", "MULTI+部门归属存疑", "SPLIT→治理(department_fit待确认)", "MKT-IP-01"),
    ("Q018", T_MKT, "治理", "制度建设", "MERGE→制度", "MKT-IP-02"),
    ("Q019", T_MKT, "战略", "TOO_BROAD", "MERGE→制度", "MKT-IP-02"),
    ("Q020", T_MKT, "影响、风险和机遇管理", "风险依据", "MERGE→合规风险", "MKT-IP-03"),
    ("Q021", T_MKT, "影响、风险和机遇管理", "风险清单", "MERGE→合规风险", "MKT-IP-03"),
    ("Q022", T_MKT, "影响、风险和机遇管理", "风险流程", "MERGE→合规风险", "MKT-IP-03"),
    ("Q023", T_MKT, "指标与目标", "隐藏定量", "REWRITE→违规事件(定量)", "MKT-IP-04"),
    ("Q024", T_MKT, "案例实践", "案例", "RETAIN", "MKT-IP-05"),
]


# ---------------------------------------------------------------------------
# Workbook generation
# ---------------------------------------------------------------------------
def _load_source_index(merged_jsonl: Path) -> dict:
    idx = {}
    if merged_jsonl.is_file():
        for l in merged_jsonl.open(encoding="utf-8"):
            c = json.loads(l)
            code = c.get("source_code") or c.get("clause_number") or ""
            if code:
                idx[code] = c
    return idx


def _style_header(ws, fill="1F4E78"):
    hf = PatternFill("solid", fgColor=fill)
    hfont = Font(bold=True, color="FFFFFF")
    for c in ws[1]:
        c.fill = hf
        c.font = hfont
        c.alignment = Alignment(vertical="center", wrap_text=True)


def build_workbook(items, source_idx, out: Path):
    wb = openpyxl.Workbook()

    # Sheet 1 — 填写说明
    ws = wb.active
    ws.title = "填写说明"
    for row in [
        ["宜格集团 ESG 信息收集表 — 质量管理部（Claude Code 分析师复核·暂定版）"],
        [""],
        ["部门", "质量管理部"],
        ["适用议题", "产品和服务安全与质量 / 化学品安全与成分管理 / 负责任营销"],
        ["填写方式", "定性问题请提供具体制度、流程与证据；定量指标请据实填报，无相关事项填0并说明。"],
        ["定性/定量", "定性信息收集见Sheet2；定量信息收集见Sheet3。"],
        ["附件证据", "请在相应列填写附件名称，并单独提供支撑文件。"],
        ["REVIEW_REQUIRED", "标注REVIEW_REQUIRED的项目为待顾问/部门确认项（口径、部门归属或来源相关性）。"],
        ["参考框架", "SSE、HKEX、GRI、MSCI、CSA-COS（详见Sheet4 来源对标）。"],
        ["重要说明", "本表为分析师复核暂定稿，非生产AI输出，未经客户最终确认。"],
    ]:
        ws.append(row)
    ws["A1"].font = Font(bold=True, size=13)

    # Sheet 2 — 定性信息收集
    ws = wb.create_sheet("定性信息收集")
    cols = ["编号", "议题", "信息维度", "信息点", "信息收集问题", "填写指引",
            "来源性质", "原人工问题编号", "参考框架", "来源要求编号", "审核状态",
            "内容填写", "附件/证据名称", "信息提供人", "备注"]
    ws.append(cols)
    for it in [i for i in items if i.kind == "qualitative"]:
        note = "部门归属待确认" if it.department_fit == "REVIEW_REQUIRED" else ""
        ws.append([it.item_id, it.topic, it.dimension, it.ip_id, it.question,
                   it.guidance, it.source_nature, ";".join(it.human_question_ids),
                   "/".join(it.source_frameworks), ";".join(it.source_unit_ids),
                   it.review_status, "", "", "", note])
    _style_header(ws)

    # Sheet 3 — 定量信息收集
    ws = wb.create_sheet("定量信息收集")
    cols = ["编号", "议题", "信息点", "指标名称", "数据收集要求", "指标定义",
            "数值", "单位", "报告期", "统计口径/边界", "拆分维度", "基准值",
            "基准年度", "目标值", "目标年度", "统计频率", "计算/填报说明",
            "原人工问题编号", "来源性质", "参考框架", "来源要求编号", "审核状态",
            "信息提供人", "备注"]
    ws.append(cols)
    for it in [i for i in items if i.kind == "quantitative"]:
        note = "指标口径待确认" if it.department_fit == "REVIEW_REQUIRED" else ""
        ws.append([it.item_id, it.topic, it.ip_id, it.metric_name, it.question,
                   it.metric_name, "", it.unit, it.period, it.boundary,
                   it.breakdown, it.baseline, "", it.target, it.target_year,
                   it.frequency, it.calc_guidance, ";".join(it.human_question_ids),
                   it.source_nature, "/".join(it.source_frameworks),
                   ";".join(it.source_unit_ids), it.review_status, "", note])
    _style_header(ws, "7030A0")

    # Sheet 4 — 来源对标
    ws = wb.create_sheet("来源对标")
    cols = ["收集项ID", "议题", "信息点", "框架", "来源类型", "来源编号",
            "要求/评价关注点摘要", "原文", "来源位置", "relevance", "semantic_reason"]
    ws.append(cols)
    for it in items:
        if it.source_nature == "BUSINESS_EXTENSION":
            continue
        for sid in it.source_unit_ids:
            c = source_idx.get(sid, {})
            ws.append([it.item_id, it.topic, it.ip_id, c.get("_framework", "?"),
                       c.get("source_item_type", ""), sid,
                       (c.get("heading") or "")[:80],
                       (c.get("original_text") or "")[:400],
                       c.get("source_locator") or "", "strong",
                       next((ip.semantic_reason for ip in INFORMATION_POINTS
                             if ip.ip_id == it.ip_id), "")])
    _style_header(ws, "1F6E43")

    # Sheet 5 — 原人工表优化对照
    ws = wb.create_sheet("原人工表优化对照")
    ws.append(["原问题编号", "议题", "原维度", "诊断", "优化动作", "对应信息点"])
    for qid, topic, dim, diag, action, ips in HUMAN_TRANSFORM:
        ws.append([qid, topic, dim, diag, action, ips])
    _style_header(ws, "C55A11")

    # Sheet 6 — 待确认事项
    ws = wb.create_sheet("待确认事项")
    ws.append(["类型", "议题", "信息点/收集项", "问题描述"])
    for ip in INFORMATION_POINTS:
        if ip.department_fit == "REVIEW_REQUIRED":
            ws.append(["部门归属", ip.topic, ip.ip_id,
                       f"{ip.label}：是否属质量管理部信息归属，或需与市场/品牌等部门协作，待确认。"])
    for it in items:
        if it.review_status == "REVIEW_REQUIRED" and "待确认" in it.calc_guidance:
            ws.append(["指标口径", it.topic, it.item_id, "定量指标口径需顾问与部门确认。"])
    _style_header(ws, "BF3030")

    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build QM department workbook.")
    ap.add_argument("--source-index",
                    default="/Users/zhouanjun/.claude/jobs/46174d16/tmp/all_clauses.jsonl")
    ap.add_argument("--out",
                    default="data/output/final/数据收集表—质量管理部_ClaudeCode_Review.xlsx")
    args = ap.parse_args(argv)

    source_idx = _load_source_index(Path(args.source_index))
    available = set(source_idx.keys())

    # No Source, No Claim — verify every framework-backed IP traces.
    missing = _verify_sources(INFORMATION_POINTS, available)
    if missing and source_idx:
        print("WARNING: source ids not found in corpus:", missing)

    items = build_collection_items()
    build_workbook(items, source_idx, Path(args.out))

    ql = [i for i in items if i.kind == "qualitative"]
    qn = [i for i in items if i.kind == "quantitative"]
    from collections import Counter
    print(json.dumps({
        "information_points": len(INFORMATION_POINTS),
        "collection_items": len(items),
        "qualitative": len(ql),
        "quantitative": len(qn),
        "by_topic_ip": dict(Counter(ip.topic for ip in INFORMATION_POINTS)),
        "source_nature": dict(Counter(i.source_nature for i in items)),
        "human_questions_transformed": len(HUMAN_TRANSFORM),
        "traceability_missing": missing,
        "out": args.out,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

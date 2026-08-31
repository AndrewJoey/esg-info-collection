#!/usr/bin/env python3
"""Claude Code Analyst review runner + human-baseline calibration.

Reads the RULE candidate matrix + the human QM questionnaire baseline,
applies the analyst review layer, compares against the human baseline,
and writes the analyst-reviewed provisional workbook + local artifacts.

All outputs are LOCAL (git-ignored). review_method=claude_code_analyst;
production provider remains NOT configured.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path

import openpyxl
from openpyxl.styles import Font, PatternFill

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.pipeline.analyst_review import review_all

QM_TOPICS = ["产品和服务安全与质量", "化学品安全与成分管理", "负责任营销"]


def load_matrix(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_human_baseline(path: Path) -> list[dict]:
    """Read the QM questionnaire; forward-fill the merged topic column."""
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["Sheet1"]
    rows = []
    last_topic = ""
    last_dim = ""
    for r in range(2, ws.max_row + 1):
        topic = ws.cell(row=r, column=1).value or last_topic
        if ws.cell(row=r, column=1).value:
            last_topic = ws.cell(row=r, column=1).value
        qid = ws.cell(row=r, column=2).value
        dim = ws.cell(row=r, column=3).value or last_dim
        if ws.cell(row=r, column=3).value:
            last_dim = ws.cell(row=r, column=3).value
        q = ws.cell(row=r, column=4).value or ""
        src = ws.cell(row=r, column=8).value or ""
        if qid:
            rows.append({"human_question_id": str(qid), "topic": topic,
                         "human_dimension": dim, "human_question": str(q),
                         "declared_source": str(src)})
    wb.close()
    return rows


# Compound-question detection: dimensions/patterns that bundle multiple
# independently collectible information points.
COMPOUND_CUES = [
    ("治理", ["治理结构", "职责分工", "决策"]),
    ("指标与目标", ["指标", "目标", "责任部门", "频率", "进展"]),
    ("影响、风险和机遇管理", ["影响", "风险", "机遇"]),
    ("案例实践", ["措施", "执行过程", "成效"]),
]


def analyze_human_question(row: dict) -> dict:
    """Classify a human question: compound?, quant-hidden?, breadth."""
    q = row["human_question"]
    dim = row["human_dimension"]
    info_points = []
    is_compound = False
    for d, parts in COMPOUND_CUES:
        if dim == d:
            present = [p for p in parts if p in q]
            if len(present) >= 2:
                is_compound = True
                info_points = present
    # Quantitative hidden inside narrative (指标与目标).
    quant_hidden = dim == "指标与目标"
    # Breadth heuristic: very long single question spanning a value chain.
    too_broad = len(q) > 80 and ("从原料" in q or "、" in q and q.count("、") >= 3)
    return {
        "is_compound": is_compound,
        "information_points": info_points,
        "quant_hidden": quant_hidden,
        "too_broad": too_broad,
    }


def build_comparison(human: list[dict], verdicts_by_topic: dict) -> list[dict]:
    """Compare each human question to source-derived positive evidence."""
    comp = []
    for hq in human:
        topic = hq["topic"]
        analysis = analyze_human_question(hq)
        positives = verdicts_by_topic.get(topic, [])
        strong = [v for v in positives if v.relevance == "strong"]
        partial = [v for v in positives if v.relevance == "partial"]
        n_support = len(strong) + len(partial)

        if n_support == 0:
            status = "NOT_SUPPORTED_BY_CURRENT_SOURCE_EVIDENCE"
        elif analysis["is_compound"]:
            status = "MULTI_INFORMATION_POINT"
        elif analysis["too_broad"]:
            status = "TOO_BROAD"
        elif n_support >= 3:
            status = "FULLY_SUPPORTED"
        else:
            status = "PARTIALLY_SUPPORTED"

        frameworks = sorted({v.source_framework for v in strong + partial})
        rec = []
        if analysis["is_compound"]:
            rec.append(f"split into information points: {analysis['information_points']}")
        if analysis["quant_hidden"]:
            rec.append("extract structured quantitative metric(s) from this narrative item")
        if analysis["too_broad"]:
            rec.append("narrow to specific value-chain stages")
        if not rec:
            rec.append("retain; refine wording to request specific evidence")

        comp.append({
            "human_question_id": hq["human_question_id"],
            "topic": topic,
            "human_dimension": hq["human_dimension"],
            "human_question": hq["human_question"],
            "matched_information_point_ids": ";".join(analysis["information_points"]),
            "matched_generated_item_ids": ";".join(
                v.source_code for v in (strong + partial)[:8] if v.source_code),
            "source_support_status": status,
            "source_frameworks": ";".join(frameworks),
            "comparison_status": status,
            "improvement_recommendation": " | ".join(rec),
            "department_evidence": "HUMAN_BASELINE",  # this workbook is QM
            "review_notes": (
                f"compound={analysis['is_compound']}, "
                f"quant_hidden={analysis['quant_hidden']}, "
                f"too_broad={analysis['too_broad']}"),
        })
    return comp


def write_jsonl(objs, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for o in objs:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")


def write_csv(rows, path: Path, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def export_review_workbook(verdicts, comparison, topics, out: Path):
    wb = openpyxl.Workbook()
    hf = PatternFill("solid", fgColor="1F4E78")
    hfont = Font(bold=True, color="FFFFFF")

    def style(ws):
        for c in ws[1]:
            c.fill = hf
            c.font = hfont

    ws = wb.active
    ws.title = "README"
    for row in [
        ["ESG Information Collection — Claude Code Analyst Review (PROVISIONAL)"],
        [""],
        ["Review method", "claude_code_analyst (temporary calibration)"],
        ["Production LLM provider", "NOT CONFIGURED — this is not a production AI run"],
        ["Framework evidence", "real, local, from SSE/HKEX/GRI/MSCI/CSA-COS"],
        ["Human baseline", "数据收集表—质量管理部 — a human questionnaire baseline, NOT framework truth"],
        ["Department assignment", "provisional except where HUMAN_BASELINE evidence exists (QM)"],
        ["Approval", "all rows REVIEW_REQUIRED — not client-approved"],
        ["No Source No Claim", "every framework-backed row traces to a real source unit"],
    ]:
        ws.append(row)
    ws["A1"].font = Font(bold=True, size=13)

    ws = wb.create_sheet("Topic_Master")
    ws.append(["topic_id", "topic_name"])
    for t in topics:
        ws.append([t["topic_id"], t["topic_name"]])
    style(ws)

    ws = wb.create_sheet("Reviewed_Requirement_Matrix")
    ws.append(["topic", "framework", "source_item", "relevance",
               "analyst_reason", "original_text_excerpt", "review_method",
               "review_status"])
    for v in verdicts:
        if v.relevance in ("strong", "partial"):
            ws.append([v.topic_name, v.source_framework, v.source_code,
                       v.relevance, v.analyst_reason, v.source_support,
                       v.review_method, v.review_status])
    style(ws)

    ws = wb.create_sheet("Human_Baseline_Comparison")
    fields = ["human_question_id", "topic", "human_dimension",
              "human_question", "source_support_status", "source_frameworks",
              "improvement_recommendation", "department_evidence"]
    ws.append(fields)
    for c in comparison:
        ws.append([c[k] for k in fields])
    style(ws)

    ws = wb.create_sheet("Review_Queue")
    ws.append(["type", "topic", "item", "issue"])
    for c in comparison:
        if c["source_support_status"] in (
            "NOT_SUPPORTED_BY_CURRENT_SOURCE_EVIDENCE", "TOO_BROAD",
            "MULTI_INFORMATION_POINT"):
            ws.append(["human_question", c["topic"], c["human_question_id"],
                       c["source_support_status"]])
    style(ws)

    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)


def write_review_report(verdicts, out: Path):
    """Per-topic relevance breakdown + method/limitations (local report)."""
    from collections import defaultdict
    byt = defaultdict(lambda: Counter())
    for v in verdicts:
        byt[v.topic_name][v.relevance] += 1
    lines = [
        "# Claude Code Analyst Review Report",
        "",
        "> LOCAL artifact. review_method=claude_code_analyst. Production "
        "LLM provider NOT configured. Do NOT commit.",
        "",
        "## Method",
        "",
        "- Deterministic, auditable analyst heuristics applied uniformly to "
        "all candidate Topic × SourceUnit mappings, plus explicit manual "
        "overrides recorded in `backend/pipeline/analyst_review.py`.",
        "- Conservative: glossary/definitions/sector-boilerplate matches "
        "demoted to not_relevant; rating sources (MSCI/CSA-COS) require the "
        "topic's core term in the Key Issue NAME (not just verbose body) "
        "for a positive.",
        "- Deduplicated to one verdict per (topic, framework, source_code).",
        "",
        "## Limitations (honest)",
        "",
        "- This is NOT a production LLM relevance run. Vocabulary bridging "
        "between Chinese topics and English rating-source item names is "
        "imperfect: CSA-COS criterion names did not match the Chinese core "
        "terms, so CSA-COS positives are 0 here — a known gap to revisit "
        "with a real bilingual LLM provider or an expanded bilingual "
        "lexicon, NOT evidence that CSA-COS is irrelevant.",
        "- All verdicts are REVIEW_REQUIRED; none approved.",
        "",
        "## Per-topic relevance breakdown",
        "",
        "| Topic | strong | partial | related | not_relevant |",
        "|---|---|---|---|---|",
    ]
    for t in sorted(byt):
        c = byt[t]
        lines.append(f"| {t} | {c['strong']} | {c['partial']} | "
                     f"{c['related']} | {c['not_relevant']} |")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_baseline_report(comparison, out: Path):
    status = Counter(c["source_support_status"] for c in comparison)
    compound = [c for c in comparison if "compound=True" in c["review_notes"]]
    lines = [
        "# Human Baseline Comparison Report (Quality Management)",
        "",
        "> LOCAL artifact. Human questionnaire is a HUMAN_AUTHORED baseline, "
        "not framework truth. Do NOT commit.",
        "",
        f"- Human questions: {len(comparison)}",
        f"- Compound (multi-information-point): {len(compound)}",
        "",
        "## Status distribution",
        "",
    ]
    for s, n in status.most_common():
        lines.append(f"- {s}: {n}")
    lines += [
        "",
        "## Key findings",
        "",
        "- The workbook is a fixed 5-dimension template (治理/战略/影响风险"
        "机遇管理/指标与目标/案例实践) applied identically to every topic — a "
        "reporting template, not a source-derived information need. Source "
        "evidence should drive the actual collection need per topic.",
        "- Most questions are compound and should be split into information "
        "points (e.g. 治理结构+职责分工+决策; 指标+目标+责任部门+频率+进展).",
        "- 指标与目标 questions hide structured quantitative metrics inside "
        "narrative prompts — these should become structured metric items.",
        "- Department evidence = HUMAN_BASELINE for these specific QM "
        "questions only; it does NOT make every source-derived question "
        "under these topics owned by Quality Management.",
        "",
        "## Per-question detail",
        "",
        "| QID | topic | dimension | status | recommendation |",
        "|---|---|---|---|---|",
    ]
    for c in comparison:
        lines.append(f"| {c['human_question_id']} | {c['topic']} | "
                     f"{c['human_dimension']} | {c['source_support_status']} | "
                     f"{c['improvement_recommendation']} |")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Claude Code analyst review + baseline calibration.")
    ap.add_argument("--matrix", default="data/output/p7/topic_source_requirement_matrix.csv")
    ap.add_argument("--human-baseline", default="数据收集表—质量管理部.xlsx")
    ap.add_argument("--topic-master", default="data/output/p1_5/topic_master.csv")
    ap.add_argument("--output-dir", default="data/output/claude_code_review")
    ap.add_argument("--master-out", default="data/output/final/ESG_Information_Collection_Master_ClaudeCode_Review.xlsx")
    ap.add_argument("--min-score", type=int, default=2)
    args = ap.parse_args(argv)

    rows = load_matrix(Path(args.matrix))
    verdicts = review_all(rows, args.min_score)

    # Dedup: MSCI/CSA page-level units repeat the same source_code across
    # many pages. Collapse to one verdict per (topic, source_code),
    # keeping the highest relevance. This prevents one Key Issue from
    # inflating positive counts. Units without a code keep their locator.
    rank = {"strong": 3, "partial": 2, "related": 1, "not_relevant": 0}
    best: dict[tuple, object] = {}
    for v in verdicts:
        key = (v.topic_name, v.source_framework, v.source_code or v.source_clause_id)
        if key not in best or rank[v.relevance] > rank[best[key].relevance]:
            best[key] = v
    verdicts = list(best.values())

    verdicts_by_topic = defaultdict(list)
    for v in verdicts:
        verdicts_by_topic[v.topic_name].append(v)

    out = Path(args.output_dir)
    write_jsonl([asdict(v) for v in verdicts], out / "relevance_verdicts.jsonl")

    # Reviewed matrix CSV (positives only).
    positives = [asdict(v) for v in verdicts if v.relevance in ("strong", "partial")]
    write_csv(positives, out / "reviewed_topic_requirement_matrix.csv",
              ["topic_name", "source_framework", "source_code", "relevance",
               "analyst_reason", "source_support", "review_method",
               "review_status"])

    # Human baseline comparison.
    human = load_human_baseline(Path(args.human_baseline))
    comparison = build_comparison(human, verdicts_by_topic)
    write_csv(comparison, out / "human_baseline_comparison.csv",
              ["human_question_id", "topic", "human_dimension",
               "human_question", "matched_information_point_ids",
               "matched_generated_item_ids", "source_support_status",
               "source_frameworks", "comparison_status",
               "improvement_recommendation", "department_evidence",
               "review_notes"])

    topics = load_matrix(Path(args.topic_master))
    export_review_workbook(verdicts, comparison, topics, Path(args.master_out))

    write_review_report(verdicts, out / "review_report.md")
    write_baseline_report(comparison, out / "human_baseline_comparison_report.md")

    # Summary stats.
    rel_counts = Counter(v.relevance for v in verdicts)
    by_fw_pos = Counter(v.source_framework for v in verdicts
                        if v.relevance in ("strong", "partial"))
    comp_status = Counter(c["source_support_status"] for c in comparison)
    print(json.dumps({
        "candidates_reviewed": len(verdicts),
        "relevance": dict(rel_counts),
        "retained_positive": rel_counts["strong"] + rel_counts["partial"],
        "positive_by_framework": dict(by_fw_pos),
        "human_questions": len(human),
        "human_comparison_status": dict(comp_status),
        "master_out": args.master_out,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

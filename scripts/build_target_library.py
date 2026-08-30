#!/usr/bin/env python3
"""P8/P10/P13 (partial) — Target ESG Collection Item Library.

Builds a review-ready target collection library from the five-source
Topic × Source candidate matrix produced by run_vertical_slice.py.

Each library item groups source evidence by (topic, framework-family)
and drafts a collection item with a qualitative/quantitative
classification inferred DETERMINISTICALLY from source-text cues (units,
metric words). It records framework evidence + source item ids +
locations + review status.

Honesty contract — what this does NOT do (blocked, not faked):
- does NOT set existing_or_new (needs existing department forms)
- does NOT assign final primary/supporting departments (needs forms)
- does NOT identify existing collection gaps (needs forms)
- does NOT approve any item (all REVIEW_REQUIRED)
- Topic × Department scope (from P1.5) is carried only as a candidate
  scope prior, never as final ownership.
- Quant/qual is a deterministic heuristic flagged for review, not a
  verdict.

Output (LOCAL): data/output/p10/target_collection_library.csv
                data/output/final/ESG_Information_Collection_Master.xlsx
                (adds Qualitative_Collection / Quantitative_Collection
                 / Target_Library sheets)
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import openpyxl
from openpyxl.styles import Font, PatternFill

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Cues that a source unit is quantitative (metric collection) vs
# qualitative (narrative). Deterministic heuristic, flagged for review.
QUANT_CUES = [
    "吨", "千瓦时", "百分比", "比率", "总量", "总额", "数量", "耗量", "排放量",
    "metric tons", "tonnes", "percentage", "ratio", "total", "kwh",
    "intensity", "amount", "number of", "rate", "quantity", "volume",
    "emissions", "consumption",
]


def load_matrix(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def classify_quant_qual(text: str) -> str:
    t = text.lower()
    hits = sum(1 for c in QUANT_CUES if c.lower() in t)
    return "quantitative" if hits >= 2 else "qualitative"


def build_library(rows: list[dict], min_score: int = 2) -> list[dict]:
    """Group candidate mappings into target collection items.

    One library item per (topic, framework-family, quant/qual bucket),
    aggregating the supporting source item ids/locations.
    """
    groups: dict[tuple, dict] = {}
    for r in rows:
        if int(r.get("retrieval_score", 0)) < min_score:
            continue
        qq = classify_quant_qual(r["original_text"])
        key = (r["topic_id"], r["framework"], qq)
        g = groups.setdefault(key, {
            "topic_id": r["topic_id"],
            "topic_name": r["topic_name"],
            "framework": r["framework"],
            "qualitative_or_quantitative": qq,
            "source_item_ids": [],
            "source_codes": [],
            "source_locations": [],
            "example_text": r["original_text"][:160],
            "review_status": "REVIEW_REQUIRED",
        })
        g["source_item_ids"].append(
            r.get("source_code") or r.get("clause_number") or r.get("source_locator", "")
        )
        code = r.get("source_code") or r.get("clause_number") or ""
        if code:
            g["source_codes"].append(code)
        loc = r.get("source_locator") or ""
        if loc:
            g["source_locations"].append(loc)
    return list(groups.values())


def write_library_csv(items: list[dict], out: Path):
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "topic_id", "topic_name", "framework",
            "qualitative_or_quantitative", "n_source_items",
            "source_codes", "example_requirement",
            "existing_or_new", "primary_department", "supporting_departments",
            "review_status",
        ])
        for it in items:
            w.writerow([
                it["topic_id"], it["topic_name"], it["framework"],
                it["qualitative_or_quantitative"], len(it["source_item_ids"]),
                "; ".join(sorted(set(it["source_codes"]))[:10]),
                it["example_text"],
                "BLOCKED_NEEDS_DEPT_FORMS",   # honest placeholder
                "BLOCKED_NEEDS_DEPT_FORMS",
                "BLOCKED_NEEDS_DEPT_FORMS",
                it["review_status"],
            ])


def append_workbook_sheets(items: list[dict], scope_csv: Path, master: Path):
    if not master.is_file():
        return
    wb = openpyxl.load_workbook(master)
    hdr_fill = PatternFill("solid", fgColor="1F4E78")
    hdr_font = Font(bold=True, color="FFFFFF")

    def fresh(name):
        if name in wb.sheetnames:
            del wb[name]
        ws = wb.create_sheet(name)
        return ws

    def style(ws):
        for c in ws[1]:
            c.fill = hdr_fill
            c.font = hdr_font

    qual = [i for i in items if i["qualitative_or_quantitative"] == "qualitative"]
    quant = [i for i in items if i["qualitative_or_quantitative"] == "quantitative"]

    ws = fresh("Qualitative_Collection")
    ws.append(["topic", "framework", "n_source_items", "source_codes",
               "draft_collection_item", "existing_or_new",
               "primary_department", "review_status"])
    for it in qual:
        ws.append([it["topic_name"], it["framework"], len(it["source_item_ids"]),
                   "; ".join(sorted(set(it["source_codes"]))[:8]),
                   it["example_text"], "BLOCKED_NEEDS_DEPT_FORMS",
                   "BLOCKED_NEEDS_DEPT_FORMS", it["review_status"]])
    style(ws)

    ws = fresh("Quantitative_Collection")
    ws.append(["topic", "framework", "metric_area", "n_source_items",
               "source_codes", "unit_note", "existing_or_new",
               "primary_department", "review_status"])
    for it in quant:
        ws.append([it["topic_name"], it["framework"], it["example_text"][:60],
                   len(it["source_item_ids"]),
                   "; ".join(sorted(set(it["source_codes"]))[:8]),
                   "unit per source text (review)", "BLOCKED_NEEDS_DEPT_FORMS",
                   "BLOCKED_NEEDS_DEPT_FORMS", it["review_status"]])
    style(ws)

    # Topic × Department scope prior (candidate only, NOT ownership)
    if scope_csv.is_file():
        ws = fresh("Topic_Department_Scope_Prior")
        ws.append(["department_name", "topic_name",
                   "note: SCOPE PRIOR — NOT question-level ownership"])
        with scope_csv.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                ws.append([r["department_name"], r["topic_name"],
                           "candidate scope only"])
        style(ws)

    wb.save(master)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build target collection library.")
    parser.add_argument("--matrix", default="data/output/p7/topic_source_requirement_matrix.csv")
    parser.add_argument("--scope", default="data/output/p1_5/topic_department_scope_mapping.csv")
    parser.add_argument("--master", default="data/output/final/ESG_Information_Collection_Master.xlsx")
    parser.add_argument("--output", default="data/output/p10/target_collection_library.csv")
    parser.add_argument("--min-score", type=int, default=2)
    args = parser.parse_args(argv)

    rows = load_matrix(Path(args.matrix))
    items = build_library(rows, args.min_score)
    write_library_csv(items, Path(args.output))
    append_workbook_sheets(items, Path(args.scope), Path(args.master))

    from collections import Counter
    by_qq = Counter(i["qualitative_or_quantitative"] for i in items)
    print(json.dumps({
        "library_items": len(items),
        "qualitative": by_qq.get("qualitative", 0),
        "quantitative": by_qq.get("quantitative", 0),
        "topics_covered": len({i["topic_id"] for i in items}),
        "output": args.output,
        "blocked_fields": ["existing_or_new", "primary_department",
                            "supporting_departments"],
        "blocked_reason": "requires existing department forms",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

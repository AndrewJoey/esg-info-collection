#!/usr/bin/env python3
"""P3–P7 + P14 — Vertical slice runner over SSE + HKEX.

Ties the pipeline together end-to-end for the currently ingested
exchange sources:

  P3  import project topics (from the P1.5 topic_master.csv)
  P4  deterministic candidate retrieval over ingested SourceClauses
  P5  rule-based candidate mapping (review_required; no LLM available)
  P7  Topic × Source Requirement matrix
  P14 export ESG_Information_Collection_Master.xlsx (review-ready)

Everything read/written here is LOCAL (git-ignored). The Excel is a
REVIEW-READY draft: mappings are RULE/REVIEW_REQUIRED, never APPROVED,
and every row traces to a real SourceClause id (No Source, No Claim).
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import openpyxl
from openpyxl.styles import Font, PatternFill

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.pipeline.retrieval import (
    candidate_to_mapping_dict,
    load_clauses,
    retrieve_candidates,
)

FRAMEWORK_OF_PREFIX = {"FW-SSE": "SSE", "FW-HKEX": "HKEX"}


def load_topics(topic_master: Path) -> list[dict]:
    topics = []
    with topic_master.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            topics.append(row)
    return topics


def load_doc_framework_map(doc_json_paths: list[Path]) -> dict[str, str]:
    """Map document_id -> framework code from ingested SourceDocument JSON."""
    mapping = {}
    for p in doc_json_paths:
        if not p.is_file():
            continue
        doc = json.loads(p.read_text(encoding="utf-8"))
        fw = doc["framework_id"].replace("FW-", "")
        mapping[doc["document_id"]] = fw
    return mapping


def build_clause_index(clauses: list[dict]) -> dict[str, dict]:
    return {c["clause_id"]: c for c in clauses}


def write_matrix_csv(mappings: list[dict], clause_index: dict, out: Path):
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "topic_id", "topic_name", "framework", "source_item_type",
            "source_code", "clause_number", "chapter", "requirement_summary",
            "original_text", "page_pdf", "source_locator",
            "retrieval_score", "matched_keywords",
            "decision_origin", "relevance", "review_status",
        ])
        for m in mappings:
            c = clause_index[m["clause_id"]]
            text = c["original_text"]
            w.writerow([
                m["topic_id"], m["topic_name"], m["framework"],
                c["source_item_type"], c.get("source_code") or "",
                c.get("clause_number") or "", c.get("chapter") or "",
                text[:120], text, c.get("page_pdf") or "",
                c.get("source_locator") or "", m["retrieval_score"],
                "; ".join(m["matched_keywords"]),
                m["decision_origin"], m["relevance"], m["review_status"],
            ])


def export_master_workbook(mappings: list[dict], clause_index: dict,
                           topics: list[dict], out: Path):
    wb = openpyxl.Workbook()
    hdr_fill = PatternFill("solid", fgColor="1F4E78")
    hdr_font = Font(bold=True, color="FFFFFF")

    def style_header(ws):
        for cell in ws[1]:
            cell.fill = hdr_fill
            cell.font = hdr_font

    # README
    ws = wb.active
    ws.title = "README"
    readme = [
        ["ESG Information Collection — Master Workbook (DRAFT)"],
        [""],
        ["Purpose", "Review-ready Topic × Source Requirement matrix for the pilot"],
        ["Scope", "SSE + HKEX exchange rules (vertical slice). GRI/MSCI/CSA-COS pending."],
        ["Source frameworks", "SSE (exchange_rule), HKEX (exchange_rule)"],
        ["Generation", "Deterministic keyword retrieval; NO LLM relevance judgment available"],
        ["Review status", "All mappings RULE / REVIEW_REQUIRED — NOT approved"],
        ["Traceability", "Every row references a real SourceClause id"],
        ["Limitations", "Retrieval candidates only; relevance requires human/AI review"],
        ["Field: relevance", "Provisional retrieval bucket ('related'), not a verdict"],
        ["Field: review_status", "AI_SUGGESTED/REVIEW_REQUIRED/APPROVED/REJECTED"],
    ]
    for row in readme:
        ws.append(row)
    ws["A1"].font = Font(bold=True, size=14)

    # Topic_Master
    ws = wb.create_sheet("Topic_Master")
    ws.append(["topic_id", "topic_name"])
    for t in topics:
        ws.append([t["topic_id"], t["topic_name"]])
    style_header(ws)

    # Source_Requirement_Matrix
    ws = wb.create_sheet("Source_Requirement_Matrix")
    ws.append([
        "topic", "framework", "source_item", "requirement_summary",
        "original_text", "source_location", "review_status",
    ])
    for m in mappings:
        c = clause_index[m["clause_id"]]
        src_item = c.get("source_code") or c.get("clause_number") or c["clause_id"]
        loc = c.get("source_locator") or (f"p.{c['page_pdf']}" if c.get("page_pdf") else "")
        ws.append([
            m["topic_name"], m["framework"], src_item,
            c["original_text"][:200], c["original_text"], loc,
            m["review_status"],
        ])
    style_header(ws)

    # Review_Queue (all mappings, since all are review_required)
    ws = wb.create_sheet("Review_Queue")
    ws.append([
        "topic_name", "framework", "source_item", "retrieval_score",
        "matched_keywords", "decision_origin", "review_status", "reason",
    ])
    for m in mappings:
        c = clause_index[m["clause_id"]]
        src_item = c.get("source_code") or c.get("clause_number") or c["clause_id"]
        ws.append([
            m["topic_name"], m["framework"], src_item, m["retrieval_score"],
            "; ".join(m["matched_keywords"]), m["decision_origin"],
            m["review_status"], "keyword candidate; needs relevance review",
        ])
    style_header(ws)

    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run five-source pipeline slice.")
    parser.add_argument("--topic-master", default="data/output/p1_5/topic_master.csv")
    parser.add_argument("--p2a-dir", default="data/output/p2a")
    parser.add_argument("--all-sources", action="store_true",
                        help="Include GRI (p2b), MSCI (p2c), CSA-COS (p2d)")
    parser.add_argument("--output-dir", default="data/output")
    parser.add_argument("--min-score", type=int, default=1)
    args = parser.parse_args(argv)

    p2a = Path(args.p2a_dir)
    topics = load_topics(Path(args.topic_master))

    clause_files = [
        p2a / "sse_source_clauses.jsonl",
        p2a / "hkex_source_clauses.jsonl",
    ]
    doc_files = [
        p2a / "sse_source_document.json",
        p2a / "hkex_source_document.json",
    ]
    if args.all_sources:
        base = Path(args.output_dir)
        for sub in ["p2b", "p2c", "p2d"]:
            d = base / sub
            if d.is_dir():
                clause_files.extend(sorted(d.glob("*_source_clauses.jsonl")))
                doc_files.extend(sorted(d.glob("*_source_document.json")))

    clauses = load_clauses(clause_files)
    framework_of = load_doc_framework_map(doc_files)
    clause_index = build_clause_index(clauses)

    candidates = retrieve_candidates(topics, clauses, framework_of, args.min_score)
    mappings = [candidate_to_mapping_dict(c) for c in candidates]

    out_dir = Path(args.output_dir)
    matrix_csv = out_dir / "p7" / "topic_source_requirement_matrix.csv"
    matrix_csv.parent.mkdir(parents=True, exist_ok=True)
    write_matrix_csv(mappings, clause_index, matrix_csv)

    master_xlsx = out_dir / "final" / "ESG_Information_Collection_Master.xlsx"
    export_master_workbook(mappings, clause_index, topics, master_xlsx)

    from collections import Counter
    by_fw = Counter(m["framework"] for m in mappings)
    topics_covered = len({m["topic_id"] for m in mappings})
    print(json.dumps({
        "topics_total": len(topics),
        "topics_with_candidates": topics_covered,
        "clauses_indexed": len(clauses),
        "candidate_mappings": len(mappings),
        "mappings_by_framework": dict(by_fw),
        "matrix_csv": str(matrix_csv),
        "master_xlsx": str(master_xlsx),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

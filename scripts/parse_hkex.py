#!/usr/bin/env python3
"""P2A — HKEX ESG Code PDF parser.

Deterministic extraction from the HKEX ESG Reporting Code PDF into P1
SourceDocument + SourceClause models, preserving page provenance.

The document has two granularities:
- numbered general provisions (1., 2., …) in the introduction and Part B
- Aspect / KPI entries (層面A1, 關鍵績效指標A1.1) in the mandatory and
  "comply or explain" parts — the canonical HKEX identifiers.

Both are captured. Aspect/KPI codes are stored in ``source_code`` and
``clause_number``; page numbers are preserved in ``page_pdf``. Page is
never the sole locator — chapter (Part) and code are kept too.

Outputs (LOCAL, git-ignored):
    data/output/p2a/hkex_source_document.json
    data/output/p2a/hkex_source_clauses.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import pdfplumber

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.models import (
    SourceClause,
    SourceClauseStatus,
    SourceDocument,
    SourceDocumentStatus,
    SourceItemType,
    generate_clause_id,
    generate_document_id,
)

FRAMEWORK_ID = "FW-HKEX"
PARSER_NAME = "hkex_pdf_parser"
PARSER_VERSION = "0.1.0"

# Part markers, e.g. "A部分：引言", "B部分：強制披露規定"
PART_RE = re.compile(r"^([A-D])部分[：:]\s*(.+)$")
# Numbered general provision, e.g. "13. 由董事會發出的聲明"
NUM_RE = re.compile(r"^(\d+)\.\s+(.+)$")
# Aspect, e.g. "層面A1： 一般披露" or "層面A2： 一般披露"
ASPECT_RE = re.compile(r"^層面\s*([A-B]\d+)[：:]\s*(.*)$")
# KPI, e.g. "關鍵績效 ... 指標A1.1" — code may trail; capture code tokens
KPI_INLINE_RE = re.compile(r"關鍵績效指標\s*([A-B]\d+\.\d+)")
KPI_CODE_RE = re.compile(r"指標\s*([A-B]\d+\.\d+)")


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def parse_hkex_pdf(path: Path) -> tuple[SourceDocument, list[SourceClause]]:
    doc_id = generate_document_id(FRAMEWORK_ID, "HKEX ESG Reporting Code", "2025")
    source_doc = SourceDocument(
        document_id=doc_id,
        framework_id=FRAMEWORK_ID,
        title="環境、社會及管治報告守則 (HKEX ESG Reporting Code, Appendix C2)",
        version="2025",
        language="zh-Hant",
        file_path=str(path),
        file_hash=_hash_file(path),
        document_type="pdf",
        status=SourceDocumentStatus.PARSED,
    )

    clauses: list[SourceClause] = []
    seen_codes: set[str] = set()
    current_part = ""

    with pdfplumber.open(path) as pdf:
        for page_index, page in enumerate(pdf.pages):
            page_no = page_index + 1
            text = page.extract_text() or ""
            lines = [ln.strip() for ln in text.split("\n") if ln.strip()]

            i = 0
            while i < len(lines):
                line = lines[i]

                m_part = PART_RE.match(line)
                if m_part:
                    current_part = f"{m_part.group(1)}部分：{m_part.group(2).strip()}"
                    i += 1
                    continue

                # Aspect marker -> a source unit keyed by aspect code
                m_aspect = ASPECT_RE.match(line)
                if m_aspect:
                    code = m_aspect.group(1)
                    # accumulate following lines until next anchor
                    body, i = _collect_body(lines, i + 1, m_aspect.group(2))
                    _add_clause(
                        clauses, seen_codes, doc_id, current_part, page_no,
                        code=f"HKEX {code}", clause_number=code,
                        item_type=SourceItemType.DISCLOSURE, text=body,
                        heading=f"層面{code}",
                    )
                    continue

                # KPI marker. The label "關鍵績效" often starts a line
                # with the code "指標AX.Y" wrapping onto the next line.
                if line.startswith("關鍵績效"):
                    # Look for the code on this line or the next 1-2 lines.
                    code = None
                    lookahead = " ".join(lines[i:i + 3])
                    m_kpi = KPI_INLINE_RE.search(lookahead) or KPI_CODE_RE.search(lookahead)
                    if m_kpi:
                        code = m_kpi.group(1)
                    body, i = _collect_body(lines, i + 1, line)
                    if code:
                        _add_clause(
                            clauses, seen_codes, doc_id, current_part, page_no,
                            code=f"HKEX {code}", clause_number=code,
                            item_type=SourceItemType.METRIC, text=body,
                            heading=f"關鍵績效指標{code}",
                        )
                    else:
                        _add_clause(
                            clauses, seen_codes, doc_id, current_part, page_no,
                            code=None, clause_number=None,
                            item_type=SourceItemType.METRIC, text=body,
                            heading="關鍵績效指標",
                        )
                    continue

                # Numbered general provision
                m_num = NUM_RE.match(line)
                if m_num:
                    num = m_num.group(1)
                    body, i = _collect_body(lines, i + 1, m_num.group(2))
                    _add_clause(
                        clauses, seen_codes, doc_id, current_part, page_no,
                        code=None, clause_number=num,
                        item_type=SourceItemType.CLAUSE, text=body,
                        heading=None,
                    )
                    continue

                i += 1

    return source_doc, clauses


def _collect_body(lines: list[str], start: int, first: str) -> tuple[str, int]:
    """Collect lines from `start` until the next structural anchor.

    Returns (joined_body, next_index).
    """
    body_parts = [first] if first else []
    i = start
    while i < len(lines):
        ln = lines[i]
        if (PART_RE.match(ln) or ASPECT_RE.match(ln) or NUM_RE.match(ln)
                or ln.startswith("關鍵績效")):
            break
        body_parts.append(ln)
        i += 1
    return "\n".join(p for p in body_parts if p).strip(), i


def _add_clause(clauses, seen_codes, doc_id, part, page_no, code,
                clause_number, item_type, text, heading) -> None:
    if not text or not text.strip():
        return
    dedup_key = code or f"num:{clause_number}:{page_no}"
    if dedup_key in seen_codes:
        return
    seen_codes.add(dedup_key)
    clause_id = generate_clause_id(
        doc_id, item_type.value, text,
        clause_number=clause_number, source_code=code, heading=heading,
    )
    clauses.append(
        SourceClause(
            clause_id=clause_id,
            document_id=doc_id,
            source_item_type=item_type,
            chapter=part or None,
            clause_number=clause_number,
            source_code=code,
            heading=heading,
            original_text=text,
            page_pdf=page_no,
            source_locator=f"{part} p.{page_no}" if part else f"p.{page_no}",
            parser_name=PARSER_NAME,
            parser_version=PARSER_VERSION,
            status=SourceClauseStatus.DRAFT,
        )
    )


def write_outputs(source_doc, clauses, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    doc_path = out_dir / "hkex_source_document.json"
    doc_path.write_text(source_doc.model_dump_json(indent=2), encoding="utf-8")
    clauses_path = out_dir / "hkex_source_clauses.jsonl"
    with clauses_path.open("w", encoding="utf-8") as f:
        for c in clauses:
            f.write(c.model_dump_json() + "\n")
    return doc_path, clauses_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parse HKEX ESG Code PDF.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", default="data/output/p2a")
    args = parser.parse_args(argv)

    path = Path(args.input)
    if not path.is_file():
        parser.error(f"input file not found: {path}")

    source_doc, clauses = parse_hkex_pdf(path)
    doc_path, clauses_path = write_outputs(source_doc, clauses, Path(args.output_dir))

    from collections import Counter
    types = Counter(c.source_item_type.value for c in clauses)
    print(json.dumps({
        "document_id": source_doc.document_id,
        "clause_count": len(clauses),
        "by_type": dict(types),
    }, ensure_ascii=False, indent=2))
    print(f"\nGenerated:\n  {doc_path}\n  {clauses_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

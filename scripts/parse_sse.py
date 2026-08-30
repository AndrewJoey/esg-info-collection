#!/usr/bin/env python3
"""P2A — SSE DOCX parser (上海证券交易所可持续发展报告指引).

Deterministic structure-based extraction of 章 (chapters) and 条
(articles/clauses) from the SSE DOCX, mapping to P1 SourceDocument +
SourceClause models.

Outputs (LOCAL, git-ignored):
    data/output/p2a/sse_source_document.json
    data/output/p2a/sse_source_clauses.jsonl (one clause per line)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import docx

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

FRAMEWORK_ID = "FW-SSE"
PARSER_NAME = "sse_docx_parser"
PARSER_VERSION = "0.1.0"

# Regex for章 (chapter): 第N章
CHAPTER_RE = re.compile(r"^第([一二三四五六七八九十百]+)章\s+(.+)$")
# Regex for条 (article/clause): 第N条
CLAUSE_RE = re.compile(r"^第([一二三四五六七八九十百]+)条\s+(.*)$")


def _chinese_num_to_int(s: str) -> int:
    """Convert Chinese numerals (一二三..十百) to int. Simplified."""
    mapping = {
        "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
        "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
    }
    if s in mapping:
        return mapping[s]
    # Handle 十N, N十, N十M patterns (up to 99)
    if "十" in s:
        if s == "十":
            return 10
        if s.startswith("十"):
            return 10 + mapping.get(s[1], 0)
        if s.endswith("十"):
            return mapping.get(s[0], 1) * 10
        parts = s.split("十")
        return mapping.get(parts[0], 1) * 10 + mapping.get(parts[1], 0)
    return 0  # fallback


def parse_sse_docx(path: Path) -> tuple[SourceDocument, list[SourceClause]]:
    """Parse the SSE DOCX into a SourceDocument + list of SourceClauses."""
    doc = docx.Document(path)

    # Build SourceDocument first.
    file_hash = f"sha256:{_hash_file(path)}"
    doc_id = generate_document_id(FRAMEWORK_ID, "SSE ESG Reporting Guideline", "2024-trial")

    source_doc = SourceDocument(
        document_id=doc_id,
        framework_id=FRAMEWORK_ID,
        title="上海证券交易所上市公司自律监管指引第14号——可持续发展报告（试行）",
        version="2024-trial",
        publication_date=None,  # not explicit in filename; would need doc read
        effective_date=None,
        language="zh",
        source_url=None,
        file_path=str(path),
        file_hash=file_hash,
        document_type="docx",
        status=SourceDocumentStatus.PARSED,
    )

    clauses: list[SourceClause] = []
    current_chapter = ""
    current_chapter_num = ""
    clause_buffer: list[str] = []
    current_clause_num = ""

    for para in doc.paragraphs:
        txt = para.text.strip()
        if not txt:
            continue

        # Check for章 (chapter marker)
        m_chap = CHAPTER_RE.match(txt)
        if m_chap:
            # Flush any prior clause
            if current_clause_num and clause_buffer:
                _flush_clause(
                    clauses, doc_id, current_chapter, current_chapter_num,
                    current_clause_num, clause_buffer
                )
            current_chapter = m_chap.group(2).strip()
            current_chapter_num = m_chap.group(1)
            clause_buffer = []
            current_clause_num = ""
            continue

        # Check for条 (article/clause marker)
        m_clause = CLAUSE_RE.match(txt)
        if m_clause:
            # Flush the prior clause
            if current_clause_num and clause_buffer:
                _flush_clause(
                    clauses, doc_id, current_chapter, current_chapter_num,
                    current_clause_num, clause_buffer
                )
            current_clause_num = m_clause.group(1)
            # The remainder of the match (after第N条) is the first line
            clause_buffer = [m_clause.group(2).strip()] if m_clause.group(2) else []
            continue

        # Otherwise accumulate text into the current clause
        if current_clause_num:
            clause_buffer.append(txt)

    # Flush the final clause
    if current_clause_num and clause_buffer:
        _flush_clause(
            clauses, doc_id, current_chapter, current_chapter_num,
            current_clause_num, clause_buffer
        )

    return source_doc, clauses


def _flush_clause(
    clauses: list[SourceClause],
    doc_id: str,
    chapter: str,
    chapter_num: str,
    clause_num: str,
    buffer: list[str],
) -> None:
    """Construct and append a SourceClause from the buffered text."""
    original_text = "\n".join(buffer).strip()
    if not original_text:
        return  # skip empty clauses

    clause_number = f"第{clause_num}条"
    clause_id = generate_clause_id(
        doc_id,
        SourceItemType.CLAUSE.value,
        original_text,
        clause_number=clause_number,
    )

    clauses.append(
        SourceClause(
            clause_id=clause_id,
            document_id=doc_id,
            source_item_type=SourceItemType.CLAUSE,
            chapter=f"第{chapter_num}章 {chapter}" if chapter else "",
            clause_number=clause_number,
            original_text=original_text,
            parser_name=PARSER_NAME,
            parser_version=PARSER_VERSION,
            status=SourceClauseStatus.DRAFT,
        )
    )


def _hash_file(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_outputs(source_doc: SourceDocument, clauses: list[SourceClause], out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)

    doc_path = out_dir / "sse_source_document.json"
    doc_path.write_text(source_doc.model_dump_json(indent=2), encoding="utf-8")

    clauses_path = out_dir / "sse_source_clauses.jsonl"
    with clauses_path.open("w", encoding="utf-8") as f:
        for c in clauses:
            f.write(c.model_dump_json() + "\n")

    return doc_path, clauses_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parse SSE DOCX to P1 models.")
    parser.add_argument("--input", required=True, help="Path to SSE DOCX")
    parser.add_argument("--output-dir", default="data/output/p2a", help="Output dir")
    args = parser.parse_args(argv)

    path = Path(args.input)
    if not path.is_file():
        parser.error(f"input file not found: {path}")

    source_doc, clauses = parse_sse_docx(path)
    doc_path, clauses_path = write_outputs(source_doc, clauses, Path(args.output_dir))

    print(json.dumps({
        "document_id": source_doc.document_id,
        "title": source_doc.title,
        "clause_count": len(clauses),
    }, ensure_ascii=False, indent=2))
    print(f"\nGenerated:\n  {doc_path}\n  {clauses_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

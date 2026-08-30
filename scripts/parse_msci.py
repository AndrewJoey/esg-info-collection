#!/usr/bin/env python3
"""P2C — MSCI methodology PDF parser (rating_methodology).

Deterministic extraction of MSCI ESG Ratings methodology documents
(core methodology + Key Issue files) into P1 SourceDocument +
SourceClause models.

MSCI semantics honored:
- MSCI is a rating methodology, NOT a disclosure standard. Units are
  ``criterion`` type with the Key Issue name as ``source_code``. No
  rule-style clause_number (stays null).
- RAW SOURCE INGESTION is kept separate from PROJECT APPLICABILITY:
  every supplied file is ingested; an ``applicability`` manifest marks
  each Key Issue ``pending_review`` (no Key Issue is assumed relevant).
- Methodology wording is preserved verbatim; it is never turned into a
  mandatory disclosure requirement.

Granularity: one unit per known section heading where detectable,
otherwise one unit per page — always with page provenance. Section
headings are matched against a known MSCI methodology heading set; this
does not fabricate structure, it only groups contiguous body text.

Outputs (LOCAL): data/output/p2c/<tag>_source_{document.json,clauses.jsonl}
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

FRAMEWORK_ID = "FW-MSCI"
PARSER_NAME = "msci_pdf_parser"
PARSER_VERSION = "0.1.0"

# Known MSCI methodology section headings (case-insensitive, line-exact).
KNOWN_HEADINGS = [
    "Introduction",
    "Risks associated with this Key Issue",
    "Opportunities associated with this Key Issue",
]
# Score-framework headings vary per Key Issue; match a generic pattern.
SCORE_HEADING_RE = re.compile(
    r"^[A-Z][\w &/,-]+ (Key Issue score|Management framework|"
    r"Management score|Mitigation score|Exposure score|score)$"
)
# Title on page 1, e.g. "Carbon Emissions" after "Methodology:"
TITLE_AFTER_RE = re.compile(r"Methodology:\s*(.+?)\s*(Key Issue)?\s*$")


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def _derive_title(pages_text: list[str], fallback: str) -> tuple[str, bool]:
    """Return (title, is_key_issue)."""
    head = "\n".join(pages_text[:2])
    is_ki = "Key Issue" in head
    for line in head.split("\n"):
        m = TITLE_AFTER_RE.search(line.strip())
        if m and m.group(1) and len(m.group(1)) < 60:
            return m.group(1).strip(), is_ki
    # Fallback to filename-derived label.
    label = fallback.replace("-key-issue", "").replace("-", " ").title()
    return label, is_ki


def _is_heading(line: str) -> bool:
    if line in KNOWN_HEADINGS:
        return True
    return bool(SCORE_HEADING_RE.match(line))


def parse_msci_pdf(path: Path) -> tuple[SourceDocument, list[SourceClause], dict]:
    with pdfplumber.open(path) as pdf:
        pages_text = [(pg.extract_text() or "") for pg in pdf.pages]

    title, is_ki = _derive_title(pages_text, path.stem)
    doc_title = f"MSCI ESG Ratings Methodology: {title}"
    role = "key_issue_methodology" if is_ki else "core_methodology"
    doc_id = generate_document_id(FRAMEWORK_ID, doc_title, "current")

    source_doc = SourceDocument(
        document_id=doc_id,
        framework_id=FRAMEWORK_ID,
        title=doc_title,
        version="current",
        language="en",
        file_path=str(path),
        file_hash=_hash_file(path),
        document_type="pdf",
        status=SourceDocumentStatus.PARSED,
    )

    source_code = f"MSCI {title}"
    clauses: list[SourceClause] = []
    seen: set[str] = set()

    current_section = "Introduction"
    buffer: list[str] = []
    section_page = 1

    def flush():
        nonlocal buffer
        text = "\n".join(buffer).strip()
        # Drop boilerplate-only fragments.
        if text and len(text) > 40:
            dedup = f"{current_section}:{section_page}"
            if dedup not in seen:
                seen.add(dedup)
                heading = f"{title} · {current_section}"
                clauses.append(SourceClause(
                    clause_id=generate_clause_id(
                        doc_id, SourceItemType.CRITERION.value, text,
                        source_code=source_code, heading=heading,
                    ),
                    document_id=doc_id,
                    source_item_type=SourceItemType.CRITERION,
                    source_code=source_code,
                    heading=heading,
                    original_text=text,
                    page_pdf=section_page,
                    source_locator=f"{doc_title} · {current_section} · p.{section_page}",
                    parser_name=PARSER_NAME,
                    parser_version=PARSER_VERSION,
                    status=SourceClauseStatus.DRAFT,
                ))
        buffer = []

    for page_index, text in enumerate(pages_text):
        page_no = page_index + 1
        for raw in text.split("\n"):
            line = raw.strip()
            if not line:
                continue
            # Skip running header/footer and TOC dotted lines.
            if line.startswith("MSCI ESG Ratings Methodology:") or "....." in line:
                continue
            if "All rights reserved" in line or line.startswith("©"):
                continue
            if _is_heading(line):
                flush()
                current_section = line
                section_page = page_no
                continue
            if not buffer:
                section_page = page_no
            buffer.append(line)
    flush()

    manifest = {
        "document_id": doc_id,
        "title": doc_title,
        "key_issue": title if is_ki else None,
        "source_role": role,
        "applicability_status": "pending_review",  # never auto-applied
        "clause_count": len(clauses),
    }
    return source_doc, clauses, manifest


def write_outputs(source_doc, clauses, out_dir: Path, tag: str):
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{tag}_source_document.json").write_text(
        source_doc.model_dump_json(indent=2), encoding="utf-8")
    with (out_dir / f"{tag}_source_clauses.jsonl").open("w", encoding="utf-8") as f:
        for c in clauses:
            f.write(c.model_dump_json() + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parse MSCI methodology PDFs.")
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", default="data/output/p2c")
    args = parser.parse_args(argv)

    src_dir = Path(args.input_dir)
    if not src_dir.is_dir():
        parser.error(f"input dir not found: {src_dir}")

    out_dir = Path(args.output_dir)
    manifests = []
    total = 0
    for pdf_path in sorted(src_dir.glob("*.pdf")):
        try:
            doc, clauses, manifest = parse_msci_pdf(pdf_path)
        except Exception as exc:  # pragma: no cover
            print(f"  SKIP {pdf_path.name}: {exc}")
            continue
        tag = pdf_path.stem.replace(" ", "_")[:60]
        write_outputs(doc, clauses, out_dir, tag)
        manifests.append(manifest)
        total += len(clauses)

    (out_dir / "msci_applicability_manifest.json").write_text(
        json.dumps(manifests, ensure_ascii=False, indent=2), encoding="utf-8")

    key_issues = [m["key_issue"] for m in manifests if m["key_issue"]]
    print(json.dumps({
        "documents_parsed": len(manifests),
        "total_units": total,
        "key_issue_files": len(key_issues),
        "core_methodology_files": len(manifests) - len(key_issues),
        "all_applicability": "pending_review (no Key Issue auto-applied)",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

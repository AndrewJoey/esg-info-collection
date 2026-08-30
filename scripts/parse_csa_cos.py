#!/usr/bin/env python3
"""P2D — CSA-COS methodology handbook parser (rating_questionnaire).

Deterministic extraction of the CSA (Corporate Sustainability
Assessment) COS-industry methodology handbook into P1 SourceDocument +
SourceClause models.

CSA semantics honored:
- Units are ``question`` type (CSA is a rating questionnaire, not a
  disclosure law); methodology/scoring context is preserved as source
  text, not restated as a legal requirement.
- The handbook organizes each criterion around recurring field labels
  ("Assessment Focus", "Question Rationale", "Applicable Industries",
  "Disclosure Requirements", "Data Requirements", "Scoring Concept").
  These labels are used as deterministic block boundaries.
- No question/criterion IDs are fabricated. The document exposes
  criterion *names* (headings), which are used as ``source_locator``;
  ``source_code`` is left null unless a real code is present, and a
  running sequence anchor is recorded via page + criterion name only.
- The two-column PDF layout is flattened by pdfplumber; text is
  preserved verbatim without reconstructing a false structure.

Outputs (LOCAL): data/output/p2d/csa_cos_source_{document.json,clauses.jsonl}
"""

from __future__ import annotations

import argparse
import hashlib
import json
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

FRAMEWORK_ID = "FW-CSA-COS"
PARSER_NAME = "csa_cos_pdf_parser"
PARSER_VERSION = "0.1.0"

# Recurring field labels that structure each CSA criterion block.
FIELD_LABELS = {
    "Assessment Focus",
    "Question Rationale",
    "Applicable Industries",
    "Disclosure Requirements",
    "Data Requirements",
    "Scoring Concept",
    "Change from Last Year",
}
# A criterion block starts when we see "Question Rationale" (the most
# consistent per-criterion anchor). The criterion name is the last
# non-label heading seen before it.
# Lines that are field values / boilerplate, never criterion names.
NON_HEADING_PREFIXES = (
    "No changes", "Change from", "New question", "Flexible", "All",
    "Assessment", "This ", "We ", "The ", "It ", "For ", "Please ",
    "Listed", "Non-listed", "Include", "State-owned", "Cooperatives",
)
BLOCK_ANCHOR = "Question Rationale"
FIRST_CONTENT_PAGE = 6  # skip cover + TOC (0-indexed)


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def parse_csa_pdf(path: Path) -> tuple[SourceDocument, list[SourceClause], dict]:
    with pdfplumber.open(path) as pdf:
        pages_text = [(pg.extract_text() or "") for pg in pdf.pages]

    doc_title = "CSA Methodology Handbook 2026 – COS industry"
    doc_id = generate_document_id(FRAMEWORK_ID, doc_title, "2026-COS")

    source_doc = SourceDocument(
        document_id=doc_id,
        framework_id=FRAMEWORK_ID,
        title=doc_title,
        version="2026-COS",
        language="en",
        file_path=str(path),
        file_hash=_hash_file(path),
        document_type="pdf",
        status=SourceDocumentStatus.PARSED,
    )

    clauses: list[SourceClause] = []
    seen: set[str] = set()

    current_criterion = "Introduction"
    recent_heading = "Introduction"
    buffer: list[str] = []
    block_page = FIRST_CONTENT_PAGE + 1

    def flush(criterion: str, page: int):
        nonlocal buffer
        text = "\n".join(buffer).strip()
        if text and len(text) > 60:
            dedup = f"{criterion}:{page}"
            if dedup not in seen:
                seen.add(dedup)
                heading = f"CSA-COS · {criterion}"
                clauses.append(SourceClause(
                    clause_id=generate_clause_id(
                        doc_id, SourceItemType.QUESTION.value, text,
                        heading=heading,
                    ),
                    document_id=doc_id,
                    source_item_type=SourceItemType.QUESTION,
                    heading=heading,
                    original_text=text,
                    page_pdf=page,
                    source_locator=f"{doc_title} · {criterion} · p.{page}",
                    parser_name=PARSER_NAME,
                    parser_version=PARSER_VERSION,
                    status=SourceClauseStatus.DRAFT,
                ))
        buffer = []

    for page_index in range(FIRST_CONTENT_PAGE, len(pages_text)):
        page_no = page_index + 1
        text = pages_text[page_index]
        for raw in text.split("\n"):
            line = raw.strip()
            if not line:
                continue
            if "/ 293" in line or line.isdigit():
                continue  # page footer
            # A short title-case line with no field label is a candidate
            # criterion name.
            if (line not in FIELD_LABELS and len(line) < 60
                    and not line.endswith(".") and line[:1].isupper()
                    and BLOCK_ANCHOR not in line
                    and not line.startswith(NON_HEADING_PREFIXES)):
                recent_heading = line
            if line.startswith(BLOCK_ANCHOR):
                # New criterion block: flush the previous, start fresh.
                flush(current_criterion, block_page)
                current_criterion = recent_heading
                block_page = page_no
            buffer.append(line)
    flush(current_criterion, block_page)

    manifest = {
        "document_id": doc_id,
        "title": doc_title,
        "industry_scope": "COS (Corporate Sustainability Assessment industry variant)",
        "criterion_blocks": len(clauses),
        "note": "criterion names extracted as headings; no IDs fabricated",
    }
    return source_doc, clauses, manifest


def write_outputs(source_doc, clauses, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "csa_cos_source_document.json").write_text(
        source_doc.model_dump_json(indent=2), encoding="utf-8")
    with (out_dir / "csa_cos_source_clauses.jsonl").open("w", encoding="utf-8") as f:
        for c in clauses:
            f.write(c.model_dump_json() + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parse CSA-COS handbook PDF.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", default="data/output/p2d")
    args = parser.parse_args(argv)

    path = Path(args.input)
    if not path.is_file():
        parser.error(f"input file not found: {path}")

    source_doc, clauses, manifest = parse_csa_pdf(path)
    out_dir = Path(args.output_dir)
    write_outputs(source_doc, clauses, out_dir)
    (out_dir / "csa_cos_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "document_id": source_doc.document_id,
        "criterion_blocks": len(clauses),
        "industry_scope": manifest["industry_scope"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

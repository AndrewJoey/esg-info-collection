#!/usr/bin/env python3
"""P2B — GRI Standards PDF parser (reporting_standard).

Deterministic extraction of GRI disclosures from a GRI Standard PDF into
P1 SourceDocument + SourceClause models.

GRI semantics honored:
- Disclosures are keyed by ``source_code`` (e.g. "GRI 305-1"); GRI has
  no rule-style clause_number, so clause_number stays null.
- The GRI content-type context (REQUIREMENTS / RECOMMENDATIONS /
  GUIDANCE) that the disclosure text sits under is captured in
  ``heading`` so a Recommendation/Guidance is never mislabeled as a
  Requirement. Only text under REQUIREMENTS is a true requirement.
- Supersession is read from the document's own in-text note (e.g.
  "Disclosures 305-1 to 305-5 have been superseded by GRI 102…") and
  recorded — never inferred from the filename.
- Sector Standards are ingested as source knowledge but flagged; they
  are not auto-applied to any project.

Outputs (LOCAL): data/output/p2b/<code>_source_document.json + .jsonl
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

FRAMEWORK_ID = "FW-GRI"
PARSER_NAME = "gri_pdf_parser"
PARSER_VERSION = "0.1.0"

# "GRI 305: Emissions 2016" — standard number, title, year.
STD_HEADER_RE = re.compile(r"GRI\s+(\d+)[:：]\s*(.+?)\s+(\d{4})")
# "Disclosure 305-1 Direct (Scope 1) GHG emissions"
DISCLOSURE_RE = re.compile(r"^Disclosure\s+(\d+-\d+)\s+(.+)$")
# GRI content-type section markers.
SECTION_MARKERS = {"REQUIREMENTS", "RECOMMENDATIONS", "GUIDANCE"}
# Supersession note.
SUPERSEDE_RE = re.compile(r"superseded by (GRI[^.\n]+)", re.IGNORECASE)
# Sector standard numbers are 11-99 (Topic standards 101+, but Universal
# 1-3). GRI 11-14 are known Sector Standards in this set.
SECTOR_NUMBERS = {"11", "12", "13", "14"}


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def parse_gri_pdf(path: Path) -> tuple[SourceDocument, list[SourceClause], dict]:
    std_number = ""
    std_title = ""
    std_year = ""
    supersession_notes: set[str] = set()

    with pdfplumber.open(path) as pdf:
        pages_text = [(pg.extract_text() or "") for pg in pdf.pages]

    # Identify the standard header + any supersession note from early pages.
    for text in pages_text[:4]:
        for line in text.split("\n"):
            if not std_number:
                m = STD_HEADER_RE.search(line)
                if m:
                    std_number, std_title, std_year = (
                        m.group(1), m.group(2).strip(), m.group(3)
                    )
            ms = SUPERSEDE_RE.search(line)
            if ms:
                supersession_notes.add(ms.group(1).strip())

    if not std_number:
        # Fallback to filename token only for the document title label
        # (NOT for supersession).
        std_title = path.stem
        std_number = "?"
        std_year = "?"

    is_sector = std_number in SECTOR_NUMBERS
    doc_title = f"GRI {std_number}: {std_title} {std_year}"
    doc_id = generate_document_id(FRAMEWORK_ID, doc_title, std_year)

    source_doc = SourceDocument(
        document_id=doc_id,
        framework_id=FRAMEWORK_ID,
        title=doc_title,
        version=std_year,
        language="en",
        file_path=str(path),
        file_hash=_hash_file(path),
        document_type="pdf",
        status=SourceDocumentStatus.PARSED,
    )

    clauses: list[SourceClause] = []
    seen: set[str] = set()

    current_code = None
    current_title = ""
    current_section = "INTRODUCTION"
    buffer: list[str] = []
    current_page = 1

    def flush():
        nonlocal buffer
        if current_code and buffer:
            text = "\n".join(buffer).strip()
            if text:
                code = f"GRI {current_code}"
                dedup = f"{code}:{current_section}"
                if dedup not in seen:
                    seen.add(dedup)
                    item_type = (
                        SourceItemType.REQUIREMENT
                        if current_section == "REQUIREMENTS"
                        else SourceItemType.GUIDANCE
                        if current_section in ("GUIDANCE", "RECOMMENDATIONS")
                        else SourceItemType.DISCLOSURE
                    )
                    heading = f"Disclosure {current_code} {current_title} [{current_section}]"
                    clauses.append(SourceClause(
                        clause_id=generate_clause_id(
                            doc_id, item_type.value, text,
                            source_code=code, heading=heading,
                        ),
                        document_id=doc_id,
                        source_item_type=item_type,
                        source_code=code,
                        heading=heading,
                        original_text=text,
                        page_pdf=current_page,
                        source_locator=f"{doc_title} · {code} · {current_section}",
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
            m_disc = DISCLOSURE_RE.match(line)
            if m_disc:
                flush()
                current_code = m_disc.group(1)
                current_title = m_disc.group(2).strip()
                current_section = "DISCLOSURE"
                current_page = page_no
                continue
            up = line.upper()
            if up in SECTION_MARKERS:
                flush()
                current_section = up
                current_page = page_no
                continue
            if current_code:
                buffer.append(line)
    flush()

    manifest = {
        "document_id": doc_id,
        "standard_number": std_number,
        "title": doc_title,
        "year": std_year,
        "is_sector_standard": is_sector,
        "supersession_notes": sorted(supersession_notes),
        "clause_count": len(clauses),
    }
    return source_doc, clauses, manifest


def write_outputs(source_doc, clauses, manifest, out_dir: Path, tag: str):
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{tag}_source_document.json").write_text(
        source_doc.model_dump_json(indent=2), encoding="utf-8")
    with (out_dir / f"{tag}_source_clauses.jsonl").open("w", encoding="utf-8") as f:
        for c in clauses:
            f.write(c.model_dump_json() + "\n")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parse GRI Standard PDF(s).")
    parser.add_argument("--input-dir", required=True,
                        help="Directory of GRI PDFs")
    parser.add_argument("--output-dir", default="data/output/p2b")
    args = parser.parse_args(argv)

    src_dir = Path(args.input_dir)
    if not src_dir.is_dir():
        parser.error(f"input dir not found: {src_dir}")

    out_dir = Path(args.output_dir)
    manifests = []
    total_clauses = 0
    pdfs = sorted(src_dir.glob("*.pdf"))
    for pdf_path in pdfs:
        if "Glossary" in pdf_path.name:
            continue  # glossary is reference, not disclosures
        try:
            doc, clauses, manifest = parse_gri_pdf(pdf_path)
        except Exception as exc:  # pragma: no cover
            print(f"  SKIP {pdf_path.name}: {exc}")
            continue
        tag = pdf_path.stem.replace(" ", "_").replace("/", "_")[:60]
        write_outputs(doc, clauses, manifest, out_dir, tag)
        manifests.append(manifest)
        total_clauses += len(clauses)

    # Aggregate GRI version/applicability manifest.
    (out_dir / "gri_manifest.json").write_text(
        json.dumps(manifests, ensure_ascii=False, indent=2), encoding="utf-8")

    superseded = [m for m in manifests if m["supersession_notes"]]
    sectors = [m for m in manifests if m["is_sector_standard"]]
    print(json.dumps({
        "standards_parsed": len(manifests),
        "total_clauses": total_clauses,
        "standards_with_supersession_notes": len(superseded),
        "sector_standards": [m["title"] for m in sectors],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

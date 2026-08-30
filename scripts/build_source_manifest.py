#!/usr/bin/env python3
"""P2.0 — Deterministic ESG source inventory / manifest.

Walks a source directory (default ``refer/``), computes a stable file
hash for every source document, infers framework / source family from
the known directory layout, and writes a local manifest plus a
human-readable inventory report.

This is deterministic bookkeeping only. It does NOT parse document
content, does NOT infer version/supersession from filenames, and does
NOT decide project applicability. Fields that cannot be established
without reading the document are written as ``unknown``.

Outputs (LOCAL, git-ignored):
    data/output/source_inventory/source_manifest.csv
    data/output/source_inventory/source_inventory_report.md
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

# Framework / source-family classification derived from the known
# refer/ layout. This maps *location*, not applicability.
SSE_DOC = "《上海证券交易所上市公司自律监管指引第14号——可持续发展报告（试行）》.docx"
HKEX_DOC = "HKEX港交所ESG守则.pdf"
CSA_DOC = "CSA_Methodology Handbook_COS.pdf"
GRI_DIR_PREFIX = "Full set of GRI Standards"
MSCI_DIR = "MSCI"

SOURCE_FAMILY = {
    "SSE": "exchange_rule",
    "HKEX": "exchange_rule",
    "GRI": "reporting_standard",
    "MSCI": "rating_methodology",
    "CSA-COS": "rating_questionnaire",
}

SOURCE_EXTENSIONS = {".pdf", ".docx"}


@dataclass
class ManifestRow:
    framework: str
    source_family: str
    relative_path: str
    filename: str
    file_type: str
    file_hash: str
    document_title: str
    publication_year: str
    effective_date: str
    version: str
    language: str
    source_role: str
    applicability_status: str
    supersession_status: str
    notes: str


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def _classify(path: Path, root: Path) -> tuple[str, str, str, str]:
    """Return (framework, source_family, source_role, language)."""
    rel = path.relative_to(root)
    parts = rel.parts
    name = path.name

    if name == SSE_DOC:
        return "SSE", SOURCE_FAMILY["SSE"], "primary_rule", "zh"
    if name == HKEX_DOC:
        return "HKEX", SOURCE_FAMILY["HKEX"], "primary_rule", "zh-Hant"
    if name == CSA_DOC:
        return "CSA-COS", SOURCE_FAMILY["CSA-COS"], "methodology_handbook", "en"
    if parts and parts[0].startswith(GRI_DIR_PREFIX):
        return "GRI", SOURCE_FAMILY["GRI"], "reporting_standard", "en"
    if parts and parts[0] == MSCI_DIR:
        # Core methodology vs Key Issue file.
        lower = name.lower()
        if "key-issue" in lower:
            role = "key_issue_methodology"
        else:
            role = "core_methodology"
        return "MSCI", SOURCE_FAMILY["MSCI"], role, "en"
    return "UNKNOWN", "unknown", "unknown", "unknown"


def build_manifest(root: Path) -> list[ManifestRow]:
    rows: list[ManifestRow] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        ext = path.suffix.lower()
        if ext not in SOURCE_EXTENSIONS:
            continue
        framework, family, role, language = _classify(path, root)
        rows.append(
            ManifestRow(
                framework=framework,
                source_family=family,
                relative_path=str(path.relative_to(root.parent)),
                filename=path.name,
                file_type=ext.lstrip("."),
                file_hash=_hash_file(path),
                document_title="unknown",  # requires reading the doc
                publication_year="unknown",
                effective_date="unknown",
                version="unknown",
                language=language,
                source_role=role,
                applicability_status="pending_manual_review",
                supersession_status="unknown",
                notes="",
            )
        )
    return rows


def write_manifest(rows: list[ManifestRow], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "source_manifest.csv"
    fields = list(ManifestRow.__dataclass_fields__.keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(asdict(r))
    return path


def write_report(rows: list[ManifestRow], out_dir: Path) -> Path:
    path = out_dir / "source_inventory_report.md"

    by_framework: Counter[str] = Counter(r.framework for r in rows)
    # Duplicate detection by hash.
    by_hash: dict[str, list[str]] = defaultdict(list)
    for r in rows:
        by_hash[r.file_hash].append(r.filename)
    dup_hashes = {h: fs for h, fs in by_hash.items() if len(fs) > 1}

    # GRI overlap heuristic: same GRI number, different files.
    gri = [r for r in rows if r.framework == "GRI"]
    gri_numbers: dict[str, list[str]] = defaultdict(list)
    for r in gri:
        # filename like "GRI 306_ Waste 2020.pdf" -> number token "306"
        toks = r.filename.replace("_", " ").split()
        num = toks[1] if len(toks) > 1 and toks[0] == "GRI" else "?"
        gri_numbers[num].append(r.filename)
    gri_overlaps = {n: fs for n, fs in gri_numbers.items() if len(fs) > 1}

    msci_core = [r for r in rows if r.source_role == "core_methodology"]
    msci_ki = [r for r in rows if r.source_role == "key_issue_methodology"]
    unknown = [r for r in rows if r.framework == "UNKNOWN"]

    lines = [
        "# ESG Source Inventory Report (P2.0)",
        "",
        "> LOCAL artifact. Lists licensed/proprietary source metadata. "
        "Do NOT commit.",
        "",
        f"Total source files: {len(rows)}",
        "",
        "## Files by framework",
        "",
    ]
    for fw in ["SSE", "HKEX", "GRI", "MSCI", "CSA-COS", "UNKNOWN"]:
        if by_framework.get(fw):
            lines.append(f"- {fw}: {by_framework[fw]}")
    lines += [
        "",
        "## Duplicate files (identical hash)",
        "",
    ]
    if dup_hashes:
        for h, fs in dup_hashes.items():
            lines.append(f"- {h[:20]}…: {', '.join(fs)}")
    else:
        lines.append("- none")

    lines += [
        "",
        "## GRI potential version overlaps (same standard number)",
        "",
        "These require reading the documents to establish supersession. "
        "Do NOT infer from filename alone.",
        "",
    ]
    if gri_overlaps:
        for num, fs in sorted(gri_overlaps.items()):
            lines.append(f"- GRI {num}: {', '.join(sorted(fs))}")
    else:
        lines.append("- none detected by standard number")

    lines += [
        "",
        "## MSCI core methodology vs Key Issue files",
        "",
        f"- core methodology / context: {len(msci_core)}",
        f"- key issue methodology: {len(msci_ki)}",
        "- All MSCI files may be ingested as source knowledge; only "
        "project-relevant Key Issues may influence questions "
        "(applicability decided later, per document).",
        "",
        "## Files requiring manual applicability judgment",
        "",
        "- All rows have `applicability_status = pending_manual_review`. "
        "GRI Sector Standards and MSCI Key Issues must be justified per "
        "project before influencing questions.",
        "",
        "## Documents not yet reliably identified",
        "",
    ]
    if unknown:
        for r in unknown:
            lines.append(f"- {r.relative_path}")
    else:
        lines.append("- none (all files classified by known layout)")

    lines += [
        "",
        "## Caveats",
        "",
        "- `document_title`, `publication_year`, `effective_date`, "
        "`version`, `supersession_status` are `unknown` here: they "
        "require reading document content (done in P2A–P2D), never "
        "inferred from filenames.",
    ]

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build ESG source manifest.")
    parser.add_argument("--source-dir", default="refer",
                        help="Root directory of source documents")
    parser.add_argument("--output-dir", default="data/output/source_inventory",
                        help="Directory for manifest artifacts")
    args = parser.parse_args(argv)

    root = Path(args.source_dir)
    if not root.is_dir():
        parser.error(f"source dir not found: {root}")

    rows = build_manifest(root)
    out_dir = Path(args.output_dir)
    manifest = write_manifest(rows, out_dir)
    report = write_report(rows, out_dir)

    summary = {
        "total_files": len(rows),
        "by_framework": dict(Counter(r.framework for r in rows)),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\nGenerated:\n  {manifest}\n  {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

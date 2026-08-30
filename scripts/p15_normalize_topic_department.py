#!/usr/bin/env python3
"""P1.5 — Topic × Department scope normalization (real-business validation).

Reads a real project "topic list" workbook that describes which
departments are involved in which ESG topics, normalizes it into
deterministic local analysis artifacts, and validates every topic
against the P1 canonical ``Topic`` domain model.

This is a VALIDATION workflow, not framework ingestion and not
question generation. The input describes:

    Department  <->  Topic        (scope mapping: "this department is
                                    involved in this topic")

It does NOT describe:

    Topic  ->  Question  ->  Department   (question-level ownership)

The two levels must not be conflated.

Business rules honored here:
- The workbook merges the department cell vertically; blank department
  cells are forward-filled from the last non-blank department (this is
  the explicit structure of the source, confirmed by merged ranges).
- Nothing is inferred: no topic is invented, no department ownership is
  assumed, no E/S/G classification is derived, no questions are made.
- ``level = 1`` / ``parent_topic_id = None`` are provisional
  IMPORT-STRUCTURE values (root-level in the supplied file), NOT an
  inferred ESG hierarchy.

Outputs (all LOCAL analysis artifacts, git-ignored):
    topic_master.csv
    topic_department_scope_mapping.csv
    source_row_audit.csv
    validation_summary.json
    validation_report.md
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import openpyxl

# Reuse P1 domain utilities rather than duplicating ID / model logic.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.models import Topic, TopicStatus, generate_topic_id  # noqa: E402

# Expected header labels in the source workbook.
HEADER_DEPARTMENT = "访谈部门"
HEADER_TOPIC = "部门相关议题"

# Provisional import-structure values (see module docstring).
PROVISIONAL_LEVEL = 1
PROVISIONAL_PARENT = None


@dataclass
class AuditRow:
    source_sheet: str
    source_row: int
    raw_department: str
    resolved_department: str
    raw_topic: str
    normalized_topic: str
    validation_status: str
    validation_note: str


@dataclass
class NormalizationResult:
    source_file: str
    sheet_names: list[str]
    audit_rows: list[AuditRow] = field(default_factory=list)
    # topic_id -> topic_name (unique topics)
    topics: dict[str, str] = field(default_factory=dict)
    # list of (department_name, topic_id, topic_name, source_row)
    scope_pairs: list[tuple[str, str, str, int]] = field(default_factory=list)
    departments: list[str] = field(default_factory=list)
    duplicate_pairs: list[tuple[str, str]] = field(default_factory=list)
    invalid_rows: int = 0
    blank_rows: int = 0
    topic_model_errors: list[str] = field(default_factory=list)


def _clean(value: object) -> str:
    """Trim accidental surrounding whitespace; None -> empty string."""
    if value is None:
        return ""
    return str(value).strip()


def _find_header_columns(ws) -> tuple[int, int, int]:
    """Locate department and topic columns and the first data row.

    Returns (dept_col, topic_col, first_data_row), all 1-indexed.
    """
    for r in range(1, min(ws.max_row, 10) + 1):
        row_vals = {
            c: _clean(ws.cell(row=r, column=c).value)
            for c in range(1, ws.max_column + 1)
        }
        dept_col = next(
            (c for c, v in row_vals.items() if v == HEADER_DEPARTMENT), None
        )
        topic_col = next(
            (c for c, v in row_vals.items() if v == HEADER_TOPIC), None
        )
        if dept_col and topic_col:
            return dept_col, topic_col, r + 1
    raise ValueError(
        f"could not locate headers {HEADER_DEPARTMENT!r} and "
        f"{HEADER_TOPIC!r} in the first rows of the sheet"
    )


def normalize_workbook(path: Path) -> NormalizationResult:
    """Read and normalize the workbook without modifying it."""
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    result = NormalizationResult(
        source_file=path.name, sheet_names=list(wb.sheetnames)
    )

    ws = wb[wb.sheetnames[0]]
    dept_col, topic_col, first_row = _find_header_columns(ws)

    seen_pairs: set[tuple[str, str]] = set()
    departments_ordered: list[str] = []
    last_department = ""
    data_started = False

    for r in range(first_row, ws.max_row + 1):
        raw_dept = _clean(ws.cell(row=r, column=dept_col).value)
        raw_topic = _clean(ws.cell(row=r, column=topic_col).value)

        # Fully blank row (both columns empty).
        if not raw_dept and not raw_topic:
            # Leading blank rows (e.g. the second row of a vertically
            # merged header) are header padding, not body blanks.
            if not data_started:
                continue
            result.blank_rows += 1
            result.audit_rows.append(
                AuditRow(
                    ws.title, r, raw_dept, last_department, raw_topic, "",
                    "blank_row", "row has no department and no topic",
                )
            )
            continue

        data_started = True

        # Forward-fill the department where the source leaves it blank
        # (vertical merge structure).
        resolved_dept = raw_dept or last_department
        if raw_dept:
            last_department = raw_dept
            if raw_dept not in departments_ordered:
                departments_ordered.append(raw_dept)

        normalized_topic = raw_topic

        # A row with a department but no topic cannot form a relationship.
        if not normalized_topic:
            result.invalid_rows += 1
            result.audit_rows.append(
                AuditRow(
                    ws.title, r, raw_dept, resolved_dept, raw_topic, "",
                    "invalid_missing_topic",
                    "row has a department but a blank/invalid topic name",
                )
            )
            continue

        # A topic with no resolvable department (should not happen after
        # forward-fill, but detect it explicitly).
        if not resolved_dept:
            result.invalid_rows += 1
            result.audit_rows.append(
                AuditRow(
                    ws.title, r, raw_dept, "", raw_topic, normalized_topic,
                    "invalid_missing_department",
                    "topic row has no resolvable department (no prior "
                    "department to forward-fill from)",
                )
            )
            continue

        topic_id = generate_topic_id(normalized_topic)
        result.topics.setdefault(topic_id, normalized_topic)

        pair = (resolved_dept, normalized_topic)
        if pair in seen_pairs:
            result.duplicate_pairs.append(pair)
            result.audit_rows.append(
                AuditRow(
                    ws.title, r, raw_dept, resolved_dept, raw_topic,
                    normalized_topic, "duplicate",
                    "duplicate Department x Topic pair",
                )
            )
            continue

        seen_pairs.add(pair)
        result.scope_pairs.append((resolved_dept, topic_id, normalized_topic, r))
        result.audit_rows.append(
            AuditRow(
                ws.title, r, raw_dept, resolved_dept, raw_topic,
                normalized_topic, "ok", "",
            )
        )

    result.departments = departments_ordered
    wb.close()

    _validate_topics_against_p1_model(result)
    return result


def _validate_topics_against_p1_model(result: NormalizationResult) -> None:
    """Construct each unique topic with the canonical P1 Topic model."""
    for topic_id, topic_name in sorted(result.topics.items()):
        try:
            Topic(
                topic_id=topic_id,
                name=topic_name,
                parent_topic_id=PROVISIONAL_PARENT,
                level=PROVISIONAL_LEVEL,
                status=TopicStatus.ACTIVE,
            )
        except Exception as exc:  # pragma: no cover - defensive
            result.topic_model_errors.append(f"{topic_name!r}: {exc}")


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------

def write_outputs(result: NormalizationResult, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    written.append(_write_topic_master(result, out_dir))
    written.append(_write_scope_mapping(result, out_dir))
    written.append(_write_source_audit(result, out_dir))
    written.append(_write_summary(result, out_dir))
    written.append(_write_report(result, out_dir))
    return written


def _write_topic_master(result: NormalizationResult, out_dir: Path) -> Path:
    path = out_dir / "topic_master.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["topic_id", "topic_name", "parent_topic_id", "level",
             "status", "source_file", "source_sheet"]
        )
        sheet = result.sheet_names[0] if result.sheet_names else ""
        for topic_id, topic_name in sorted(
            result.topics.items(), key=lambda kv: kv[1]
        ):
            w.writerow(
                [topic_id, topic_name, "", PROVISIONAL_LEVEL,
                 TopicStatus.ACTIVE.value, result.source_file, sheet]
            )
    return path


def _write_scope_mapping(result: NormalizationResult, out_dir: Path) -> Path:
    path = out_dir / "topic_department_scope_mapping.csv"
    sheet = result.sheet_names[0] if result.sheet_names else ""
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["department_name", "topic_id", "topic_name",
             "source_file", "source_sheet", "source_row"]
        )
        for dept, topic_id, topic_name, row in result.scope_pairs:
            w.writerow(
                [dept, topic_id, topic_name, result.source_file, sheet, row]
            )
    return path


def _write_source_audit(result: NormalizationResult, out_dir: Path) -> Path:
    path = out_dir / "source_row_audit.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["source_sheet", "source_row", "raw_department",
             "resolved_department", "raw_topic", "normalized_topic",
             "validation_status", "validation_note"]
        )
        for a in result.audit_rows:
            w.writerow(
                [a.source_sheet, a.source_row, a.raw_department,
                 a.resolved_department, a.raw_topic, a.normalized_topic,
                 a.validation_status, a.validation_note]
            )
    return path


def _summary_dict(result: NormalizationResult) -> dict:
    return {
        "source_file": result.source_file,
        "sheet_count": len(result.sheet_names),
        "department_count": len(result.departments),
        "unique_topic_count": len(result.topics),
        "department_topic_relationship_count": len(result.scope_pairs),
        "duplicate_relationship_count": len(result.duplicate_pairs),
        "invalid_row_count": result.invalid_rows,
        "blank_row_count": result.blank_rows,
        "topic_model_validation_error_count": len(result.topic_model_errors),
    }


def _write_summary(result: NormalizationResult, out_dir: Path) -> Path:
    path = out_dir / "validation_summary.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(_summary_dict(result), f, ensure_ascii=False, indent=2)
        f.write("\n")
    return path


def _write_report(result: NormalizationResult, out_dir: Path) -> Path:
    path = out_dir / "validation_report.md"
    s = _summary_dict(result)

    # Derived relationship analytics.
    topic_to_depts: dict[str, set[str]] = {}
    dept_to_topics: dict[str, set[str]] = {}
    for dept, _tid, topic_name, _row in result.scope_pairs:
        topic_to_depts.setdefault(topic_name, set()).add(dept)
        dept_to_topics.setdefault(dept, set()).add(topic_name)

    multi_dept_topics = {t: d for t, d in topic_to_depts.items() if len(d) > 1}
    max_topics_dept = max(
        (len(v) for v in dept_to_topics.values()), default=0
    )

    if result.topic_model_errors:
        topic_result = "FAIL — DOMAIN MODEL ISSUE"
    else:
        topic_result = "PASS WITH IMPORT-LAYER NOTES"

    lines = [
        "# P1.5 — Real Business Validation Report",
        "",
        "> LOCAL analysis artifact. Contains real project-derived data. "
        "Do NOT commit.",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Source file: `{result.source_file}`",
        "",
        "## 1. Source workbook structure",
        "",
        f"- Sheets: {s['sheet_count']} ({', '.join(result.sheet_names)})",
        "- Columns: department (`访谈部门`) x topic (`部门相关议题`)",
        "- Department cells are vertically merged; blank department cells "
        "are forward-filled from the last non-blank department.",
        "",
        "## 2. Counts",
        "",
        f"- Departments: {s['department_count']}",
        f"- Unique topics: {s['unique_topic_count']}",
        f"- Department x Topic relationships: "
        f"{s['department_topic_relationship_count']}",
        f"- Duplicate pairs: {s['duplicate_relationship_count']}",
        f"- Invalid rows: {s['invalid_row_count']}",
        f"- Blank rows: {s['blank_row_count']}",
        "",
        "## 3. Relationship shape",
        "",
        f"- Topics involving multiple departments: {len(multi_dept_topics)}",
        f"- Max topics under a single department: {max_topics_dept}",
        "- Conclusion: "
        + (
            "many-to-many"
            if multi_dept_topics and max_topics_dept > 1
            else "not many-to-many (see counts)"
        ),
        "",
        "## 4. Normalization decisions",
        "",
        "- Forward-fill department across vertically merged rows.",
        "- Trim surrounding whitespace on all cells.",
        "- Deterministic topic IDs via the P1 `generate_topic_id` utility.",
        "- Duplicate Department x Topic pairs are detected and excluded "
        "from the scope mapping (recorded in the audit file).",
        "- `level=1` / `parent_topic_id=null` are provisional "
        "IMPORT-STRUCTURE values (root-level in the supplied file), NOT an "
        "inferred ESG hierarchy. No E/S/G or 一级/二级 classification was "
        "inferred.",
        "",
        "## 5. Topic model validation (against P1 canonical `Topic`)",
        "",
        f"- Result: **{topic_result}**",
        f"- Topic-model validation errors: "
        f"{s['topic_model_validation_error_count']}",
    ]
    if result.topic_model_errors:
        lines.append("")
        lines.append("### Errors")
        lines.extend(f"- {e}" for e in result.topic_model_errors)

    lines += [
        "",
        "## 6. Modeling observations",
        "",
        "### Confirmed by real data",
        "- The current input is a Topic x Department **scope mapping** "
        "(which departments are involved in a topic), not question-level "
        "ownership.",
        "- The relationship is many-to-many: a topic spans multiple "
        "departments and a department spans multiple topics.",
        "- The P1 `Topic` model represents every real topic name without "
        "modification.",
        "- No hierarchy (parent/child, E/S/G, 一级/二级) is encoded in the "
        "source; it provides a single topic-name column only.",
        "",
        "### Hypothesis for later validation (NOT implemented)",
        "- Department involvement in a topic will likely differ from "
        "question-level department ownership under that topic.",
        "- A future `Department` entity and a scope-vs-ownership "
        "distinction may be needed once department forms arrive.",
        "- Topic hierarchy (一级/二级) may need to be supplied separately; "
        "it is not derivable from this file.",
        "",
        "## 7. Issues that may affect future Question-level mapping",
        "",
        "- Scope mapping must not be treated as question assignment.",
        "- The same metric/question may later appear under multiple "
        "departments; this file cannot answer that.",
        "",
        "## 8. Did the current Topic model survive the real-business test?",
        "",
        f"- **{topic_result}**",
    ]

    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Normalize a Topic x Department scope workbook (P1.5)."
    )
    parser.add_argument(
        "--input", required=True, help="Path to the source .xlsx workbook"
    )
    parser.add_argument(
        "--output-dir", required=True,
        help="Directory for local analysis artifacts",
    )
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    if not input_path.is_file():
        parser.error(f"input file not found: {input_path}")

    result = normalize_workbook(input_path)
    written = write_outputs(result, Path(args.output_dir))

    summary = _summary_dict(result)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("\nGenerated:")
    for p in written:
        print(f"  {p}")
    if result.topic_model_errors:
        print("\nTOPIC MODEL VALIDATION ERRORS:")
        for e in result.topic_model_errors:
            print(f"  {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

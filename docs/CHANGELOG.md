# Changelog

## Unreleased

### Added

- Initial repository structure
- AI development instructions
- Architecture baseline
- V0 data model
- Development roadmap
- Architecture decision records
- V0 task backlog
- ADR-017 — V0 Source Universe Expanded
- ADR-018 — Deterministic Canonical Domain IDs
- Source directories for `gri/`, `msci/` and `csa-cos/` under `data/sources/`
- P1 Core Domain Models (`backend/models/`): Framework, SourceDocument,
  SourceClause (generic atomic traceable source unit), Topic,
  TopicClauseMapping as typed Pydantic v2 models per `docs/DATA_MODEL.md`
- Explicit enums for all controlled values (framework category,
  document lifecycle, source item type, relevance, mapping method,
  decision origin, review lifecycle)
- Deterministic stable ID generation utilities with prefixes
  `FW-` / `DOC-` / `CL-` / `TOPIC-` / `MAP-` (`backend/models/ids.py`)
- 133 unit tests under `tests/unit/`
- P1.5 Real Business Validation: reusable Topic × Department scope
  normalization workflow (`scripts/p15_normalize_topic_department.py`)
  validating real project topics against the P1 `Topic` model
- Department-form input contract
  (`docs/P1_5_DEPARTMENT_FORM_INPUT_CONTRACT.md`)
- Synthetic-fixture tests for the P1.5 normalization workflow
- `.gitignore` rule protecting the real client input workbook from
  accidental commit
- Operating layer: `CLAUDE.md`, `docs/RUN_STATE.md`,
  `.claude/skills/esg-autopilot/SKILL.md` for resumable autonomous
  execution
- PDF/DOCX parsing dependencies: `pypdf`, `pdfplumber`, `python-docx`
- P2.0 Source Manifest: `scripts/build_source_manifest.py` — hashes and
  inventories all 80 ESG source documents (SSE/HKEX/GRI/MSCI/CSA-COS)
  under `refer/`, generates local
  `data/output/source_inventory/{source_manifest.csv, source_inventory_report.md}`
- P2A SSE + HKEX ingestion: deterministic parsers
  (`scripts/parse_sse.py`, `scripts/parse_hkex.py`) mapping source
  structure to P1 SourceDocument + SourceClause models (SSE 63 clauses;
  HKEX 101 units with aspect/KPI codes and page provenance);
  synthetic-fixture parser tests
- Pipeline scaffold (`backend/pipeline/retrieval.py`): deterministic
  keyword candidate retrieval (Retrieval != Analysis — RULE candidates,
  review_required, never approved; no LLM available in this environment)
- SSE+HKEX vertical slice runner (`scripts/run_vertical_slice.py`):
  P3 topic import → P4/P5 candidate mapping → P7 Topic × Source
  Requirement matrix → P14 review-ready
  `ESG_Information_Collection_Master.xlsx` (README / Topic_Master /
  Source_Requirement_Matrix / Review_Queue sheets); all outputs local
- P2B GRI ingestion (`scripts/parse_gri.py`): 41 standards → 599 units,
  Disclosure/Requirement/Recommendation/Guidance distinction,
  supersession read from document text, sector standards flagged
- P2C MSCI ingestion (`scripts/parse_msci.py`): 35 methodology docs →
  429 criterion units; raw ingestion separated from applicability (all
  Key Issues pending_review, none auto-applied)
- P2D CSA-COS ingestion (`scripts/parse_csa_cos.py`): 79 criterion
  blocks from the 2026 COS-industry handbook; no IDs fabricated
- Five-source retrieval: English keyword aliases added; runner
  `--all-sources` indexes 1271 units across SSE/HKEX/GRI/MSCI/CSA-COS
  and covers all 28 project topics (candidates only, review_required)

### Changed

- Expanded V0 source universe from HKEX/SSE to SSE, HKEX, GRI, MSCI and CSA-COS.
- Generalized SourceClause semantics to atomic traceable source units.
- Added multi-source-family architecture requirements.

### Current Milestone

V0 Pilot:

```text
Topic → Relevant Atomic Source Unit → Original Source
```

across SSE, HKEX, GRI, MSCI and CSA-COS.

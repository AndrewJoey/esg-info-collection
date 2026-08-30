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

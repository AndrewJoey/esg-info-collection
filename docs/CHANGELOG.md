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
- Source directories for `gri/`, `msci/` and `csa-cos/` under `data/sources/`

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

# Changelog

## Unreleased

### Added

- Reusable blind-generation QA gates (`backend/pipeline/blind_generation_qa.py`):
  framework/client-agnostic `TopicApplicabilityGate` (Gate A/B/C, with
  spanning-source + whitelist support), `evidence_directness`,
  `metric_exactness` (count↔percentage drift guard; qualitative-source→KPI
  fabrication guard via per-source `quantitative_components`), and
  `traceability` (No Source, No Claim). Plus `run_all_gates` aggregator.
- 19 synthetic unit tests (`tests/unit/test_blind_generation_qa.py`) covering
  every gate and the generic form of the five regression guards. Suite: 260 passed.
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
- AI relevance layer architecture (`backend/ai/relevance.py`):
  provider-agnostic interface, Pydantic verdict schema, prompt template,
  retry handling, deterministic `MockRelevanceProvider` for tests, and a
  production-provider gate. Live production run remains blocked (no key)
- Evaluation harness (`backend/pipeline/evaluation.py`):
  Precision/Recall/F1 overall and per source family; awaits real Gold
  labels (not fabricated)
- Target ESG Collection Item Library (`scripts/build_target_library.py`):
  158 review-ready items (76 qualitative / 82 quantitative) across all
  28 topics with source evidence + deterministic qual/quant
  classification; `existing_or_new` and department ownership fields
  explicitly BLOCKED pending department forms. Master workbook extended
  with Qualitative_Collection / Quantitative_Collection /
  Topic_Department_Scope_Prior sheets
- Claude Code analyst review layer (`backend/pipeline/analyst_review.py`,
  `scripts/run_analyst_review.py`): temporary, auditable, deterministic
  relevance calibration (review_method=claude_code_analyst,
  production_provider=false — NOT a production LLM run). Conservative
  demotion of glossary/boilerplate + rating-source name-match tightening
  reduces 2560 candidates to 149 defensible positives across 28 topics.
  Human QM questionnaire baseline calibration: 24 questions classified
  (18 compound / 3 too-broad), compound-question decomposition, and a
  Claude-Code-reviewed provisional workbook. All local outputs
  git-ignored; `.gitignore` protects the QM baseline file
- Quality Management single-department collection workbook
  (`backend/pipeline/qm_collection.py`, `scripts/build_qm_workbook.py`):
  scoped to the 3 client-confirmed QM topics; 17 information points →
  17 collection items (13 qualitative + 4 quantitative) with build-time
  No-Source-No-Claim verification (100% framework-backed traceability);
  all 24 human baseline questions transformed (retain/rewrite/split/
  merge); six-sheet workbook (填写说明/定性/定量/来源对标/优化对照/待确认).
  Bilingual semantic review recovered MSCI Chemical Safety + GRI 301/416/417
  evidence missed by the earlier lexical pass. review_method=
  claude_code_semantic_review, production_provider=false

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

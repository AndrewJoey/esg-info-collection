# RUN_STATE

Machine-and-human readable execution state for the autonomous V0 run.
Update after every milestone.

```yaml
current_phase: P2A
phase_status: done_uncommitted
branch: feat/p1-5-real-business-validation
last_completed_phase: P2A
last_commit: ae85dfbce9a17b004ae716daf4c618e0ad7cbccc
available_inputs:
  - 议题清单.xlsx (10 departments, 28 topics, 51 scope pairs) [LOCAL]
  - refer/ SSE docx (exchange_rule) [LOCAL, ignored]
  - refer/ HKEX pdf (exchange_rule) [LOCAL, ignored]
  - refer/ GRI 42 files (reporting_standard) [LOCAL, ignored]
  - refer/ MSCI 35 files (rating_methodology) [LOCAL, ignored]
  - refer/ CSA-COS pdf (rating_questionnaire) [LOCAL, ignored]
missing_inputs:
  - existing department information-collection forms (blocks P11 gap
    analysis, P12 question-level department ownership, final production
    department forms)
test_status: "172 passed (P1 + P1.5 + P2A parsers)"
quality_metrics:
  p1_5: "28/28 topics valid; 51 scope pairs; many-to-many confirmed"
  p2_0: "80 source files hashed (SSE 1, HKEX 1, GRI 42, MSCI 35, CSA-COS 1); GRI 306 overlap detected"
  p2a: "SSE 63 clauses (6 chapters); HKEX 101 units (12 aspects A1-A4/B1-B8 + 36 KPIs + numbered provisions), page provenance preserved"
unresolved_non_blocking_issues:
  - GRI version/supersession must be read from source text, not filename
  - MSCI Key Issue applicability must be justified per project, not
    assumed from folder presence
  - InformationPoint vs Question architecture pending real evidence
hard_stop_reason: null
next_action: >
  P3 topic import (reuse P1.5 topic_master) + P4 keyword retrieval over
  SSE+HKEX clauses + vertical slice: pick 1-3 project topics
  (climate/employee/anti-corruption), run retrieval and structured
  relevance mapping, before scaling to GRI/MSCI/CSA-COS. Build a small
  Gold set for evaluation. NOTE: P5 AI mapping needs an LLM provider;
  if none is configured, implement deterministic keyword-candidate
  mapping with review_status=REVIEW_REQUIRED and record the LLM
  dependency (not a hard stop for the pipeline scaffold).
```

## Phase ledger

- **P1** — Core Domain Models — DONE (commit 55eefc1)
- **P1.5** — Real Business Validation — DONE (commit 740b6d2)
- **P2.0** — Source Manifest — DONE (commit ae85dfb)
- **P2A** — SSE + HKEX Ingestion — DONE (uncommitted)
- **P2B–P2D** — GRI / MSCI / CSA-COS — pending
- P1.6 / P3–P15 — pending

## Notes on source structure (verified by probing)

- SSE docx: Chinese regulatory structure `第N章` (chapter) / `第N条`
  (article/clause); 231 paragraphs, 1 table. Structure recoverable from
  `第N条`/`第N章` text markers (paragraph styles are unreliable).
- HKEX pdf: 27 pages, Traditional Chinese; Parts A/B/C/D; numbered
  clauses 1..N; text extracts cleanly via pdfplumber with page numbers.
- GRI: 42 files, mixed publication years (2016–2025); overlaps exist
  (e.g. GRI 306 Effluents-and-Waste-2016 vs Waste-2020). Supersession
  must come from source text.
- MSCI: 35 files = 2 core methodology + 33 Key Issue files.
- CSA-COS: single methodology handbook pdf.

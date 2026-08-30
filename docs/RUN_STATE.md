# RUN_STATE

Machine-and-human readable execution state for the autonomous V0 run.
Update after every milestone.

```yaml
current_phase: P2A
phase_status: ready_to_start
branch: feat/p1-5-real-business-validation
last_completed_phase: P2.0
last_commit: 740b6d287f861267561e8820faa010e88d6dfee9
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
test_status: "145 passed (P1 + P1.5, before P2A work)"
quality_metrics:
  p1_5: "28/28 topics valid; 51 scope pairs; many-to-many confirmed"
  p2_0: "80 source files hashed (SSE 1, HKEX 1, GRI 42, MSCI 35, CSA-COS 1); GRI 306 overlap detected"
unresolved_non_blocking_issues:
  - GRI version/supersession must be read from source text, not filename
  - MSCI Key Issue applicability must be justified per project, not
    assumed from folder presence
  - InformationPoint vs Question architecture pending real evidence
hard_stop_reason: null
next_action: >
  SSE + HKEX ingestion (P2A): build deterministic parsers for SSE DOCX
  (章/条 structure) and HKEX PDF (numbered clauses, Parts A/B/C/D). Map
  to P1 SourceDocument + SourceClause models. Generate ingested outputs
  under data/output/p2a/. Then vertical slice: pick 1–3 project topics,
  run retrieval→mapping→evaluation before scaling to all topics/sources.
```

## Phase ledger

- **P1** — Core Domain Models — DONE (commit 55eefc1)
- **P1.5** — Real Business Validation — DONE (commit 740b6d2)
- **P2.0** — Source Manifest — DONE (uncommitted, about to commit)
- **P2A** — SSE + HKEX Ingestion — ready to start
- P1.6 / P2B–P2D / P3–P15 — pending

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

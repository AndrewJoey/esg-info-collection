# RUN_STATE

Machine-and-human readable execution state for the autonomous V0 run.
Update after every milestone.

```yaml
current_phase: QM Department Blind Bottom-Up V2 (source-driven, no human baseline)
phase_status: complete
branch: feat/p1-5-real-business-validation
last_completed_phase: QM Blind Bottom-Up V2 (3 topics, 2-sheet deliverable, blind)
last_commit: 9f3f631
available_inputs:
  - 议题清单.xlsx (10 departments, 28 topics, 51 scope pairs) [LOCAL]
  - refer/ SSE docx (exchange_rule) [LOCAL, ignored]
  - refer/ HKEX pdf (exchange_rule) [LOCAL, ignored]
  - refer/ GRI 42 files (reporting_standard) [LOCAL, ignored]
  - refer/ MSCI 35 files (rating_methodology) [LOCAL, ignored]
  - refer/ CSA-COS pdf (rating_questionnaire) [LOCAL, ignored]
missing_inputs:
  - existing department information-collection forms — for departments
    OTHER than Quality Management. The QM human questionnaire baseline
    (数据收集表—质量管理部.xlsx) is now available and used for QM
    question-level routing evidence. Other 9 departments still lack
    baselines (P11/P12 remain provisional for them).
  - configured production LLM provider — for the live production AI
    relevance run. A temporary Claude Code analyst layer
    (review_method=claude_code_analyst, production_provider=false) now
    provides auditable deterministic relevance review as calibration,
    WITHOUT faking a production provider.
hard_stop_reason: null
test_status: "241 passed (adds QM collection builder tests)"
quality_metrics:
  p1_5: "28/28 topics valid; 51 scope pairs; many-to-many confirmed"
  p2_0: "80 source files hashed (SSE 1, HKEX 1, GRI 42, MSCI 35, CSA-COS 1); GRI 306 overlap detected"
  p2a: "SSE 63 clauses (6 chapters); HKEX 101 units (12 aspects A1-A4/B1-B8 + 36 KPIs + numbered provisions), page provenance preserved"
  vertical_slice: "28/28 topics got candidates from 164 SSE+HKEX clauses; 277 RULE/REVIEW_REQUIRED candidate mappings; master workbook generated"
  p2b: "GRI 41 standards, 599 units; supersession from text (305/302/201); sector standards flagged not applied"
  p2c: "MSCI 35 docs, 429 units (criterion type); all applicability pending_review"
  p2d: "CSA-COS 79 criterion blocks (2026 COS handbook); no IDs fabricated"
  five_source_retrieval: "1271 units indexed; 28/28 topics; 2560 candidates (GRI 1197, MSCI 940, CSA-COS 352, SSE 58, HKEX 13) at min_score=2"
  ai_architecture: "provider interface + Pydantic verdict schema + prompt + MockRelevanceProvider + production gate; NO live provider (blocked)"
  evaluation_harness: "Precision/Recall/F1 overall + per-source-family; awaits real Gold labels"
  target_library: "158 items (76 qualitative, 82 quantitative), 28/28 topics; existing_or_new + department fields BLOCKED pending dept forms"
  claude_code_analyst: "1637 unique candidates reviewed across 28 topics; 149 positive (70 strong, 79 partial) after conservative demotion; MSCI tightened to name-match (11 genuine); CSA-COS 0 (CN/EN vocab gap, known limitation). QM baseline: 24 questions, 18 compound, 3 too_broad. review_method=claude_code_analyst, production_provider=false"
  qm_workbook: "质量管理部 deliverable: 3 topics, 17 information points, 17 collection items (13 qualitative + 4 quantitative), all 24 human questions transformed, 100% framework-backed traceability verified, 6 sheets. CSA/MSCI recovered via bilingual semantic review (CHM-IP-03/05 cite MSCI Chemical Safety). review_method=claude_code_semantic_review, production_provider=false"
  qm_blind_v2: "质量管理部 Blind Bottom-Up V2: source-driven, NO human questionnaire/quant table/A-C-D/comparison read during generation (blindness=YES, enforced by fresh per-topic analyst subagents seeing only topic boundary + faithful source text). 12 applicable source units after Topic Applicability Gate (SSE 1, HKEX 4, GRI 5, MSCI 2, CSA-COS 0 — honest zero, not padded). 15 collection items (8 qualitative + 7 quantitative) across 11 information points. Deterministic QA: 0 traceability / 0 applicability / 0 metric-exactness / 0 duplicate failures. 5 regression cases all PASS (no 投诉闭环率 KPI; HKEX B6.1 stays percentage; GRI 416-2 count+3way; GRI 301 excluded from chemical safety; GRI 418 excluded from responsible marketing). Independent 2nd Business Reviewer pass = APPROVE_WITH_MINOR (dept-fit flags + MKT-01 label rewrite applied). Final Excel data/output/final/质量管理部_Blind_BottomUp_V2.xlsx = exactly 2 sheets (定性/定量), fixed 10-field schema, 内容填写/附件/填写人 empty. Reusable QA gates + 19 tests committed (no client data). review_method=claude_code_semantic_analyst, production_provider=false"
unresolved_non_blocking_issues:
  - GRI version/supersession must be read from source text, not filename
  - MSCI Key Issue applicability must be justified per project, not
    assumed from folder presence
  - InformationPoint vs Question architecture pending real evidence
hard_stop_reason: null
next_action: >
  INDEPENDENT WORK EXHAUSTED. Two true blockers remain: (1) a configured
  LLM provider for the live P5 AI relevance run (architecture + mock are
  ready; flip is_production_provider_configured + add a real provider
  impl of RelevanceProvider); (2) existing department information-
  collection forms for P11 gap analysis and P12 question-level
  department ownership (normalize per docs/P1_5_DEPARTMENT_FORM_INPUT_
  CONTRACT.md, then join to the target library). Until then the maximum
  valid deliverable is the review-ready target question/metric library +
  topic-level department scope candidates, which now exist.
```

## Phase ledger

- **P1** — Core Domain Models — DONE (commit 55eefc1)
- **P1.5** — Real Business Validation — DONE (commit 740b6d2)
- **P2.0** — Source Manifest — DONE (commit ae85dfb)
- **P2A** — SSE + HKEX Ingestion — DONE (commit dc7fb9c)
- **P3/P4/P5-scaffold/P7/P14** — SSE+HKEX vertical slice — DONE (commit f7f037a)
- **P2B** — GRI ingestion — DONE (uncommitted): 41 standards, 599 units
- **P2C** — MSCI ingestion — DONE (uncommitted): 35 docs, 429 units
- **P2D** — CSA-COS ingestion — DONE (uncommitted): 79 blocks
- **Five-source retrieval** — DONE (uncommitted): 1271 units, 2560 candidates
- **Five-source retrieval** — DONE (commit 4e652e4): 1271 units, 2560 candidates
- **AI relevance architecture** — DONE (uncommitted): interface/schema/prompt/mock/gate
- **Evaluation harness** — DONE (uncommitted): P/R/F1 overall + per-family
- **Target collection library** — DONE (uncommitted): 158 items, master workbook 7 sheets
- **TRUE BLOCKERS remaining:**
    - P5 live AI relevance run → needs configured LLM provider
    - P11 gap analysis, P12 question-level department ownership,
      final department forms → needs existing department forms
- P1.6 pending (no department forms found in repo)

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

# Tasks

## Current Milestone

# V0 Pilot
## Topic → ESG Source Requirement → Original Source

V0 core goal:

> Given an ESG Topic, identify relevant disclosure requirements,
> standard requirements, rating criteria and questionnaire items across
> SSE, HKEX, GRI, MSCI and CSA-COS, while preserving exact source
> provenance.

V0 source universe:

| Source  | Source Category      | Typical Atomic Unit               |
| ------- | -------------------- | --------------------------------- |
| SSE     | exchange_rule        | clause / requirement              |
| HKEX    | exchange_rule        | clause / requirement              |
| GRI     | reporting_standard   | disclosure / requirement          |
| MSCI    | rating_methodology   | criterion / key-issue requirement |
| CSA-COS | rating_questionnaire | question / criterion              |

This is the only active product milestone unless explicitly changed.

---

# P0 — Repository Bootstrap

- [x] Create project folder structure
- [x] Create documentation skeleton
- [x] Add PRD to `docs/PRD.md`
- [x] Initialize Git repository
- [x] Create Python virtual environment
- [x] Add base Python dependencies
- [x] Add `.gitignore`
- [x] Add `.env.example`
- [x] Create initial commit

Definition of Done:
- repository opens cleanly
- required docs exist
- environment can run Python tests

---

# P1 — Core Domain Models

Implement:

- [x] Framework
- [x] SourceDocument
- [x] SourceClause
- [x] Topic
- [x] TopicClauseMapping

Requirements:
- `docs/DATA_MODEL.md` is the canonical implementation specification
  for domain entities; implement fields and enums exactly as defined
  there
- use Pydantic schemas
- use stable IDs
- preserve provenance
- add tests
- no LLM logic yet
- Framework must support the four source categories:
  `exchange_rule`, `reporting_standard`, `rating_methodology`,
  `rating_questionnaire`
- SourceClause is a generic atomic traceable source unit and must
  support `source_item_type`, `source_code` and `source_locator`
  (see `docs/DATA_MODEL.md`)
- `clause_number` must not be required (GRI / MSCI / CSA-COS units
  may have none)
- do NOT require `project_id`, `level_1_name` or `level_2_name` on
  Topic; hierarchical topics use `parent_topic_id` + `level`
- do not implement CanonicalRequirement, MetricDefinition, Project,
  Client, Materiality, Department, Question or QuestionTemplate in P1
- no database persistence, parser implementation, retrieval, LLM
  calls or frontend in P1 (domain models and tests only)

Definition of Done:
- models validate valid records
- invalid records fail validation
- relationships are explicit
- tests pass

---

# P1.5 — Real Business Validation

Validate the P1 domain architecture against a REAL project
topic/department mapping file before framework ingestion. This is not
framework ingestion and not question generation; it collects evidence
for future modeling decisions.

In execution order, **P1.5 precedes P2A**. It does not change P2 scope.

Real client input must never be committed (raw workbook or any
client-derived normalized output). Local analysis artifacts live under
`data/output/p1_5/` and stay git-ignored.

- [x] Protect real input file via exact `.gitignore` rule
- [x] Inspect the real workbook structure (openpyxl, read-only)
- [x] Reusable normalization workflow
      (`scripts/p15_normalize_topic_department.py`, CLI-driven, no
      hardcoded absolute paths)
- [x] Forward-fill department, whitespace trim, deterministic outputs
- [x] Detect duplicate Department × Topic pairs, blank rows, invalid
      rows (missing topic / missing department)
- [x] Validate every real topic against the canonical P1 `Topic` model
- [x] Local outputs: `topic_master.csv`,
      `topic_department_scope_mapping.csv`, `source_row_audit.csv`,
      `validation_summary.json`, `validation_report.md`
- [x] Department-form input contract
      (`docs/P1_5_DEPARTMENT_FORM_INPUT_CONTRACT.md`, generic, no client
      data)
- [x] Synthetic-fixture unit tests (no real client content)

Explicitly NOT done in P1.5 (evidence-gathering only):
- no `Department` / `DepartmentTopicMapping` domain model
- no `Question` / `InformationPoint` / `QuestionTemplate`
- no `CanonicalRequirement` / `Project` / `Client` / `Materiality`
- no E/S/G or 一级/二级 hierarchy inference
- `level=1` / `parent_topic_id=null` are provisional import-structure
  values, not an inferred ESG hierarchy

Definition of Done:
- real topic import validates against the P1 `Topic` model
- Topic × Department scope normalized with full source provenance
- normalization workflow covered by synthetic tests
- no real client data committed

---

# Source Ingestion Sequence

Source ingestion is split per source family. Develop P2A → P2B → P2C →
P2D sequentially. Do not develop the five parsers in parallel.

All parsers share one Parser Interface but use family-specific
implementations (see `docs/ARCHITECTURE.md` §8).

---

# P2A — SSE + HKEX Source Ingestion (exchange_rule)

Prepare and ingest:

- [ ] Add SSE source file under `data/sources/sse/`
- [ ] Add HKEX source file under `data/sources/hkex/`
- [ ] Add framework metadata in `config/frameworks.yaml`
- [ ] Add pilot project config in `config/project.yaml`
- [ ] source file discovery and file hash generation
- [ ] SourceDocument creation
- [ ] Exchange Parser implementation (SSE, HKEX) against the Parser
      Interface
- [ ] clause / requirement extraction
- [ ] chapter/section preservation
- [ ] page preservation when available
- [ ] parser validation

Definition of Done:
- both exchange sources can be parsed
- atomic units can be exported as structured JSON
- every unit traces to a source document
- original text is preserved
- source hashes can be calculated

---

# P2B — GRI Source Ingestion (reporting_standard)

- [ ] Add GRI source file under `data/sources/gri/`
- [ ] GRI parser implementation against the Parser Interface
- [ ] atomic units identified by `source_code` (e.g. `GRI 305-1`);
      `clause_number` not required
- [ ] distinguish at least:
      Requirement / Recommendation / Guidance / Disclosure
- [ ] never express a Recommendation or Guidance as "GRI requires ..."

Definition of Done:
- GRI units parse with correct `source_item_type`
- Requirement vs Recommendation vs Guidance vs Disclosure is preserved
- every unit traces to a source document

---

# P2C — MSCI Source Ingestion (rating_methodology)

- [ ] Add MSCI source file under `data/sources/msci/`
- [ ] MSCI parser implementation against the Parser Interface
- [ ] atomic units may come from Key Issue / Criterion /
      Methodology Statement / Relevant Metric / Expectation
- [ ] `clause_number` must not be required
- [ ] units without traditional clause numbering must be supported

Definition of Done:
- MSCI units parse and trace to a source document
- missing clause numbering is handled as null, not fabricated

---

# P2D — CSA-COS Source Ingestion (rating_questionnaire)

- [ ] Add CSA-COS source file under `data/sources/csa-cos/`
- [ ] CSA-COS parser implementation against the Parser Interface
- [ ] atomic units may include Question ID / Question / Criterion /
      Definition / Metric / Supporting Guidance
- [ ] must not reuse the HKEX/SSE clause parser structure

Definition of Done:
- CSA-COS units parse and trace to a source document
- questionnaire structure is preserved without clause-only forcing

---

# P3 — Topic Import

Prepare and implement:

- [ ] Add pilot topic list under `data/topics/`
- [ ] import topics from xlsx/csv
- [ ] validate topic structure
- [ ] create stable topic IDs
- [ ] reject duplicate topics safely

Definition of Done:
- pilot topic list loads successfully
- topics can be listed programmatically

---

# P4 — Candidate Retrieval

Implement baseline retrieval:

- [ ] metadata filtering
- [ ] keyword retrieval
- [ ] candidate ranking
- [ ] retrieval result schema

Optional after baseline:
- [ ] embedding retrieval
- [ ] hybrid retrieval

Definition of Done:
- a topic returns candidate source units
- retrieval does not mark candidates as approved
- results retain full provenance

---

# P5 — AI Relevance Mapping

Implement:

- [ ] relevance prompt
- [ ] structured output schema
- [ ] provider abstraction
- [ ] Pydantic validation
- [ ] relevance classification
- [ ] explanation
- [ ] confidence field
- [ ] failure handling

Output should support:

```text
strong
partial
related
not_relevant
```

Definition of Done:
- model cannot write directly to approved data
- invalid model output is rejected
- source unit ID is preserved
- prompt version is recorded

---

# P6 — Gold Evaluation

> P6 evaluates AI_SUGGESTED / machine-generated mappings against the
> human-created Gold Dataset. Gold evaluation does not require
> mappings to be APPROVED first.

Human Review (P7) evaluates operational publication decisions; Gold
Evaluation evaluates model / retrieval quality. This is why P6
precedes P7.

Prepare the Gold Dataset manually. It must cover all five sources:
SSE, HKEX, GRI, MSCI and CSA-COS.

- [ ] 20–50 atomic unit extraction examples across the five sources
- [ ] 20–50 positive topic mappings across the five sources
- [ ] negative mapping examples
- [ ] edge cases

Implement evaluation:

- [ ] extraction evaluation
- [ ] mapping precision
- [ ] mapping recall
- [ ] traceability coverage
- [ ] evaluation report

Evaluation must report:

- overall precision / recall
- precision / recall per source family:
  - SSE Precision / Recall
  - HKEX Precision / Recall
  - GRI Precision / Recall
  - MSCI Precision / Recall
  - CSA-COS Precision / Recall

An overall metric must not hide weak quality in one source family.

Do not auto-generate the Gold Dataset with the same model being
evaluated.

Initial targets:

```text
source traceability coverage = 100%
approved source-backed records with valid source = 100%
high-confidence mapping precision target >= 95%
atomic unit extraction recall target >= 98%
```

These are target acceptance criteria, not assumed current performance.

Definition of Done:
- evaluation is reproducible
- metrics are printed or written to file
- per-source-family metrics are reported separately
- failures can be inspected

---

# P7 — Human Review

Implement minimum review workflow:

- [ ] AI_SUGGESTED
- [ ] REVIEW_REQUIRED
- [ ] APPROVED
- [ ] REJECTED

CLI is acceptable for V0.

Definition of Done:
- reviewer can approve/reject mappings
- review decision persists
- approved mappings can be exported

---

# P8 — Unified Benchmark Matrix Export

Generate the Topic × ESG Source Requirement Matrix:

```text
Topic
Source Category
Source
Source Version
Source Item Type
Source Code / Clause
Requirement / Criterion Summary
Original Text
Chapter
Section
Page
Source Document
Review Status
```

Preferred output:
- XLSX

Definition of Done:
- export is deterministic
- every row traces to its original atomic source unit
- output can be reproduced from stored data

---

# V0 Release Gate

V0 is complete only when:

- [ ] SSE is parsed
- [ ] HKEX is parsed
- [ ] GRI is parsed
- [ ] MSCI is parsed
- [ ] CSA-COS is parsed
- [ ] pilot topics imported
- [ ] topic-to-source-unit mapping works
- [ ] human review works
- [ ] source traceability is complete
- [ ] evaluation exists, including per-source-family metrics
- [ ] unified benchmark matrix can be exported
- [ ] tests pass
- [ ] documentation is updated

---

# Explicitly Deferred

Do not start these until V0 is reviewed:

- [ ] Canonical Requirement
- [ ] Cross-framework requirement consolidation
- [ ] Department mapping automation
- [ ] Materiality
- [ ] L1/L2/L3 depth
- [ ] Question generation
- [ ] Qualitative questionnaire
- [ ] Quantitative questionnaire
- [ ] Client-facing Excel
- [ ] Client portal
- [ ] ESG Copilot
- [ ] Peer benchmarking expansion
- [ ] Automated framework monitoring

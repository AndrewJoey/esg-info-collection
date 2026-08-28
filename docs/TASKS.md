# Tasks

## Current Milestone

# V0 Pilot
## Topic → HKEX/SSE Requirement → Original Source

This is the only active product milestone unless explicitly changed.

---

# P0 — Repository Bootstrap

- [x] Create project folder structure
- [x] Create documentation skeleton
- [ ] Add PRD to `docs/PRD.md`
- [ ] Initialize Git repository
- [ ] Create Python virtual environment
- [ ] Add base Python dependencies
- [ ] Add `.gitignore`
- [ ] Add `.env.example`
- [ ] Create initial commit

Definition of Done:
- repository opens cleanly
- required docs exist
- environment can run Python tests

---

# P1 — Core Domain Models

Implement:

- [ ] Framework
- [ ] SourceDocument
- [ ] SourceClause
- [ ] Topic
- [ ] TopicClauseMapping

Requirements:
- use Pydantic schemas
- use stable IDs
- preserve provenance
- add tests
- no LLM logic yet

Definition of Done:
- models validate valid records
- invalid records fail validation
- relationships are explicit
- tests pass

---

# P2 — Pilot Input Data

Prepare:

- [ ] Add HKEX source file under `data/sources/hkex/`
- [ ] Add SSE source file under `data/sources/sse/`
- [ ] Add pilot topic list under `data/topics/`
- [ ] Add framework metadata in `config/frameworks.yaml`
- [ ] Add pilot project config in `config/project.yaml`

Definition of Done:
- all pilot inputs are stored locally
- files have identifiable versions
- source hashes can be calculated

---

# P3 — Source Ingestion

Implement:

- [ ] source file discovery
- [ ] file hash generation
- [ ] SourceDocument creation
- [ ] parser interface
- [ ] HKEX parsing
- [ ] SSE parsing
- [ ] SourceClause generation
- [ ] chapter/section preservation
- [ ] page preservation when available
- [ ] parser validation

Definition of Done:
- both pilot frameworks can be parsed
- clauses can be exported as structured JSON
- every clause traces to a source document
- original text is preserved

---

# P4 — Topic Import

Implement:

- [ ] import topics from xlsx/csv
- [ ] validate topic structure
- [ ] create stable topic IDs
- [ ] reject duplicate topics safely

Definition of Done:
- pilot topic list loads successfully
- topics can be listed programmatically

---

# P5 — Candidate Retrieval

Implement baseline retrieval:

- [ ] metadata filtering
- [ ] keyword retrieval
- [ ] candidate ranking
- [ ] retrieval result schema

Optional after baseline:
- [ ] embedding retrieval
- [ ] hybrid retrieval

Definition of Done:
- a topic returns candidate clauses
- retrieval does not mark candidates as approved
- results retain full provenance

---

# P6 — AI Relevance Judgment

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
- source clause ID is preserved
- prompt version is recorded

---

# P7 — Human Review Layer

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

# P8 — Gold Dataset

Prepare manually:

- [ ] 20–50 clause extraction examples
- [ ] 20–50 positive topic mappings
- [ ] negative mapping examples
- [ ] edge cases

Do not auto-generate the Gold Dataset with the same model being evaluated.

---

# P9 — Evaluation

Implement:

- [ ] extraction evaluation
- [ ] mapping precision
- [ ] mapping recall
- [ ] traceability coverage
- [ ] evaluation report

Initial targets:

```text
source traceability coverage = 100%
approved framework-backed records with valid source = 100%
high-confidence mapping precision target >= 95%
clause extraction recall target >= 98%
```

These are target acceptance criteria, not assumed current performance.

Definition of Done:
- evaluation is reproducible
- metrics are printed or written to file
- failures can be inspected

---

# P10 — Benchmark Export

Generate:

```text
Topic
Framework
Framework Version
Chapter
Clause Number
Requirement Summary
Original Text
Qualitative / Quantitative
PDF Page
Printed Page
Source Document
Review Status
```

Preferred output:
- XLSX

Definition of Done:
- export is deterministic
- every row traces to original clause
- output can be reproduced from stored data

---

# V0 Release Gate

V0 is complete only when:

- [ ] HKEX is parsed
- [ ] SSE is parsed
- [ ] pilot topics imported
- [ ] topic-to-clause mapping works
- [ ] human review works
- [ ] source traceability is complete
- [ ] evaluation exists
- [ ] benchmark Excel can be exported
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

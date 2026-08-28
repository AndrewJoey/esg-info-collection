# Roadmap

## Product Direction

The long-term direction is:

```text
ESG Knowledge Platform
        ↓
Benchmarking Studio
        ↓
Data Collection Studio
        ↓
Client Collaboration / ESG Intelligence
```

Development should proceed incrementally.

---

# Phase Beta — Proven Research Engine

Status:
Existing concept already validated through a real ESG benchmarking workflow.

Capabilities previously demonstrated:
- peer report acquisition
- paragraph retrieval
- agent relevance judgment
- Evidence Card generation
- source traceability
- review layer
- target extraction
- Excel / CSV delivery

Lesson:
The core pattern works:

```text
Deterministic Retrieval
+
AI Semantic Judgment
+
Evidence
+
Human Review
+
Deterministic Export
```

---

# V0 — Structured ESG Source Knowledge Pilot

Goal:

> Given an ESG Topic, identify relevant disclosure requirements,
> standard requirements, rating criteria and questionnaire items across
> SSE, HKEX, GRI, MSCI and CSA-COS, while preserving exact source
> provenance.

Validate:

```text
Topic
→ Relevant Atomic Source Unit
→ Original Source
```

V0 source universe:

| Source  | Source Category      |
| ------- | -------------------- |
| SSE     | exchange_rule        |
| HKEX    | exchange_rule        |
| GRI     | reporting_standard   |
| MSCI    | rating_methodology   |
| CSA-COS | rating_questionnaire |

V0 therefore validates one unified pipeline across exchange rules,
reporting standards, rating methodologies and rating questionnaires.

Pilot inputs:
- SSE
- HKEX
- GRI
- MSCI
- CSA-COS
- real project ESG topic list

Key capabilities:
- framework versioning
- source document ingestion for all five sources
- atomic source unit extraction (family-specific parsers behind one
  Parser Interface)
- provenance
- topic import
- candidate retrieval
- AI relevance judgment
- human review
- evaluation (overall and per source family)
- unified benchmark matrix export

Success criteria:
- accurate
- sufficiently complete
- traceable
- reproducible
- precision / recall reported per source family, so no source family's
  weakness is hidden by the overall score

No full UI required.

---

# V1 — Generalized Benchmarking Engine

Goal:

Move from pilot mapping to reusable benchmarking.

Potential additions:
- Canonical Requirement
- alias handling
- cross-framework mapping
- requirement deduplication
- framework coverage matrix
- peer evidence integration
- client baseline integration
- PostgreSQL persistence
- minimal review UI

Core model:

```text
Standard Clause
        │
        ├── Canonical Requirement
        │
Peer Evidence
        │
        └── Benchmark View
```

---

# V2 — ESG Data Collection Studio

Goal:

Convert approved ESG requirements into department-level information collection.

Inputs:
- approved project topics
- approved requirements
- department-topic mapping

Capabilities:
- qualitative questions
- quantitative data requests
- question guidance
- data type
- unit
- reporting period
- evidence request
- internal source mapping
- client-facing export

Output:
- master sheet
- department sheets
- internal source sheet
- client version

---

# V2.5 — Question Intelligence

Potential additions:
- question deduplication
- requirement-to-question transformation
- special handling for GHG activity data
- definitions
- formulas
- calculation guidance
- question QA

---

# V3 — Materiality and Depth

Goal:

Use project context to recommend information collection depth.

Potential logic:

```text
Compliance Floor
+
Materiality
+
Project Objective
→ Recommended Depth
```

Possible levels:
- L1 Basic
- L2 Standard
- L3 Full

Human override remains mandatory.

---

# V4 — Client Collaboration

Potential additions:
- online questionnaire
- evidence upload
- contributor assignment
- progress tracking
- clarification requests
- reminders
- answer completeness analysis

---

# V5 — Advanced ESG Intelligence

Potential additions:
- peer benchmark agent
- rating gap analysis
- ESG KPI library
- evidence validation
- ESG Copilot
- report drafting assistance
- framework update monitoring

---

# Long-Term Platform Model

```text
                ESG KNOWLEDGE PLATFORM
                         │
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
 Knowledge Hub     Benchmarking       Data Collection
                        Studio             Studio
        │                │                │
 Framework          Applicability      Department
 Clause             Crosswalk          Questions
 Requirement        Coverage           Metrics
 Topic              Peer Gap           Evidence
 Metric                                Export
        │                │                │
        └────────────────┼────────────────┘
                         ↓
                  Rules + AI Layer
                         ↓
                  Evidence Database
```

---

# Roadmap Principle

Do not build future phases merely because the architecture supports them.

Each phase begins only after the previous phase has produced a real, reviewed project output.

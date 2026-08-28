# ESG Info Collection

AI-assisted ESG framework benchmarking and information collection platform.

---

## Current Status

Current development stage:

# V0 Pilot

Primary workflow:

```text
Topic
↓
Relevant Atomic Source Unit
↓
SourceDocument
↓
Framework / Rating System
↓
Original Source
```

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

V0 is NOT only about exchange rules. It validates one unified ESG source
knowledge pipeline that simultaneously supports:

```text
Exchange Rules
+
Reporting Standards
+
Rating Methodologies
+
Rating Questionnaires
```

The first objective is not to build a complete ESG SaaS platform.

The first objective is to prove that the system can accurately and reproducibly map real ESG topics to relevant requirements across all five sources while preserving original source evidence.

---

## Product Direction

Long term:

```text
ESG Knowledge Platform
        ↓
Benchmarking Studio
        ↓
Data Collection Studio
```

Potential future capabilities:
- framework knowledge library
- cross-framework benchmarking
- canonical requirements
- department-level questionnaires
- quantitative data collection
- materiality-aware question depth
- peer benchmarking
- ESG Copilot

---

## Core Principles

1. Evidence First
2. No Source, No Claim
3. Retrieval != Analysis
4. Raw != Reviewed
5. AI Proposes, Human Publishes
6. Original source text is immutable
7. Deterministic logic stays deterministic

---

## Repository Structure

```text
.
├── AGENTS.md
├── README.md
├── config/
├── data/
│   ├── gold/
│   ├── output/
│   ├── sources/
│   │   ├── hkex/
│   │   ├── sse/
│   │   ├── gri/
│   │   ├── msci/
│   │   └── csa-cos/
│   └── topics/
├── docs/
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   ├── DATA_MODEL.md
│   ├── ROADMAP.md
│   ├── TASKS.md
│   ├── DECISIONS.md
│   └── CHANGELOG.md
├── backend/
├── frontend/
├── scripts/
├── tests/
└── infra/
```

---

## Documentation

Before development, read:

1. `AGENTS.md`
2. `docs/PRD.md`
3. `docs/ARCHITECTURE.md`
4. `docs/DATA_MODEL.md`
5. `docs/TASKS.md`
6. `docs/DECISIONS.md`
7. `docs/ROADMAP.md`

---

## V0 Data Model

```text
Framework
    ↓
SourceDocument
    ↓
SourceClause
    ↕
Topic
    ↓
TopicClauseMapping
```

`SourceClause` is a historical name. It represents a generic atomic
traceable source unit — a clause for exchange rules, a disclosure for
GRI, a criterion / key-issue requirement for MSCI, a question /
criterion for CSA-COS.

---

## Expected V0 Output

Topic × ESG Source Requirement Matrix. Example rows:

| Topic | Source Category | Source | Source Code / Clause | Requirement / Criterion Summary | Original Source |
|---|---|---|---|---|---|
| 应对气候变化 | exchange_rule | HKEX | ... | ... | ... |
| 应对气候变化 | exchange_rule | SSE | ... | ... | ... |
| 温室气体排放 | reporting_standard | GRI | GRI 305-1 | ... | ... |
| 人力资本发展 | rating_methodology | MSCI | Human Capital Development | ... | ... |
| 水资源管理 | rating_questionnaire | CSA-COS | 3.2.1 | ... | ... |

Every source-backed row must be traceable to its original atomic source
unit, and evaluation is reported both overall and per source family.

---

## Development

Recommended Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install baseline dependencies:

```bash
pip install \
  fastapi \
  uvicorn \
  pydantic \
  pydantic-settings \
  sqlalchemy \
  "psycopg[binary]" \
  pytest \
  pytest-asyncio \
  python-dotenv \
  pyyaml \
  openpyxl
```

Save dependencies:

```bash
pip freeze > requirements.txt
```

---

## Testing

Run:

```bash
pytest
```

AI-related changes must eventually also run the Gold Dataset evaluation.

---

## Project Rule

Do not ask an AI coding agent to implement the whole product at once.

Work from `docs/TASKS.md`, one milestone at a time.

The current milestone is V0 only.

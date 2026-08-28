# ESG Info Collection

AI-assisted ESG framework benchmarking and information collection platform.

---

## Current Status

Current development stage:

# V0 Pilot

Primary workflow:

```text
Topic
→ Framework Requirement
→ Original Source
```

Initial frameworks:
- HKEX
- SSE

The first objective is not to build a complete ESG SaaS platform.

The first objective is to prove that the system can accurately and reproducibly map real ESG topics to relevant disclosure requirements while preserving original source evidence.

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
│   │   └── sse/
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

---

## Expected V0 Output

Example benchmark output:

| Topic | Framework | Clause | Requirement | Original Source |
|---|---|---|---|---|
| 应对气候变化 | HKEX | ... | ... | ... |
| 应对气候变化 | SSE | ... | ... | ... |

Every framework-backed row must be traceable to its original source clause.

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

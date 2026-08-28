# AGENTS.md

## Purpose

This file defines how AI coding agents should work in this repository.

The project is an AI-assisted ESG benchmarking and data collection platform.

Current priority is NOT to build the full platform.
Current priority is to validate the V0 pilot workflow:

Topic → Relevant Atomic Source Unit → Original Source

The V0 source universe covers five sources across four source families:
- SSE — exchange disclosure rules (exchange_rule)
- HKEX — exchange disclosure rules (exchange_rule)
- GRI — reporting standard (reporting_standard)
- MSCI — rating methodology (rating_methodology)
- CSA-COS — rating questionnaire (rating_questionnaire)

The initial pilot is based on a real ESG information collection project.

---

## Source of Truth

Before making any change, always read the following files in this order:

1. `docs/PRD.md`
2. `docs/ARCHITECTURE.md`
3. `docs/DATA_MODEL.md`
4. `docs/TASKS.md`
5. `docs/DECISIONS.md`
6. `docs/ROADMAP.md`
7. `docs/CHANGELOG.md`

If these documents conflict:
- PRD defines product intent.
- DATA_MODEL defines current core domain objects.
- ARCHITECTURE defines technical boundaries.
- DECISIONS defines accepted architecture decisions.
- TASKS defines what should be implemented now.

Do not silently override any of them.

---

## Core Product Principles

The following principles are mandatory.

### 1. Evidence First
Every source-backed requirement must preserve provenance to its original source.

### 2. No Source, No Claim
The system must not claim that a source requires something unless the claim is backed by a stored atomic source unit (SourceClause).

### 3. Retrieval != Analysis
Retrieval finds candidate content.
AI or humans judge relevance.
Do not treat retrieval matches as approved knowledge.

### 4. Raw != Reviewed
AI-generated or automatically extracted outputs are drafts until reviewed or explicitly approved.

### 5. AI Proposes, Human Publishes
AI may recommend mappings, summaries, or question wording.
High-risk knowledge should not become published knowledge without review.

### 6. Original Source Is Immutable
Never rewrite, normalize, translate, or overwrite the stored `original_text`.

Derived text must be stored separately.

### 7. Deterministic Logic Stays Deterministic
Do not delegate deterministic tasks to an LLM when normal code is sufficient.

Examples:
- IDs
- file hashes
- sorting
- Excel generation
- version comparisons
- database joins
- mandatory schema validation

### 8. Preserve Traceability
Never remove provenance fields for convenience.

---

## Current Scope

Current milestone:

`V0 Pilot — Topic → ESG Source Requirement → Original Source`

V0 core goal:

> Given an ESG Topic, identify relevant disclosure requirements,
> standard requirements, rating criteria and questionnaire items across
> SSE, HKEX, GRI, MSCI and CSA-COS, while preserving exact source
> provenance.

In scope:
- source ingestion across all five sources (SSE, HKEX, GRI, MSCI, CSA-COS)
- source document metadata
- atomic source unit extraction (SourceClause)
- topic import
- topic-to-source-unit candidate retrieval
- AI-assisted relevance judgment
- source traceability
- review status
- evaluation (overall and per source family)
- unified benchmark matrix export

Out of scope unless explicitly requested:
- full SaaS frontend
- client portal
- materiality scoring engine
- L1/L2/L3 question depth engine
- automatic department inference
- online questionnaire collection
- report generation
- autonomous multi-agent system
- enterprise RBAC
- microservices
- Kubernetes
- Neo4j
- automatic rating score replication

---

## Architecture Rules

Use a modular monolith.

Default backend stack:
- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- pgvector where semantic search is needed

Do not introduce microservices unless explicitly approved in `docs/DECISIONS.md`.

Domain logic must not depend directly on a specific LLM provider.

Keep these concerns separated:

- `domain/` = ESG business logic
- `ai/` = model calls, prompts, schemas, context building
- `parsers/` = source parsing
- `repositories/` = persistence
- `services/` = application orchestration
- `api/` = HTTP interface
- `workers/` = background jobs

---

## AI Rules

All AI outputs that affect structured data must:
- use structured output
- pass Pydantic validation
- retain model metadata
- retain prompt version
- retain source references
- retain confidence where applicable
- be reviewable

Never let the model invent:
- clause numbers
- source codes
- page numbers
- framework names
- source URLs
- publication dates
- effective dates
- mandatory status

If a source field is unknown, store null or explicit unknown status.

---

## Data Rules

Every `SourceClause` must belong to a `SourceDocument`.

Every `TopicClauseMapping` must reference:
- a valid topic
- a valid source unit (SourceClause)

Raw source units must not be merged.

Normalization or consolidation must happen in a separate layer.

Do not create canonical requirements during V0 unless explicitly added to scope.

### Mandatory Source Modeling Constraints

Do not assume all source systems are clause-based.

SourceClause represents a generic atomic traceable source unit.

The system must support clauses, disclosures, requirements, rating
criteria and questionnaire items without destroying source-specific
semantics.

---

## Testing Rules

Every domain feature must have tests.

At minimum:
- unit tests for deterministic logic
- integration tests for ingestion flows
- evaluation tests for AI mapping logic

Changes to:
- retrieval logic
- prompts
- models
- mapping logic

must be checked against the Gold Dataset.

Do not consider an AI feature complete only because examples look reasonable.

---

## Development Workflow

Before coding:
1. Read the source-of-truth documents.
2. Read current code.
3. Identify the current task in `docs/TASKS.md`.
4. Do not expand scope.

During coding:
1. Make the smallest coherent change.
2. Preserve existing behavior unless change is required.
3. Add or update tests.
4. Avoid unrelated refactors.

After coding:
1. Run relevant tests.
2. Run evaluation if AI/retrieval changed.
3. Update `docs/TASKS.md`.
4. Update `docs/CHANGELOG.md`.
5. If architecture or data-model decisions changed, update `docs/DECISIONS.md`.
6. Summarize what changed and what remains.

---

## Definition of Done

A task is not complete unless:

- code works for the intended use case
- tests pass
- source traceability is preserved
- schema validation passes
- no out-of-scope feature was introduced
- documentation is updated
- relevant evaluation has been run

---

## Important Instruction for AI Agents

Do not attempt to build the entire PRD at once.

Work milestone by milestone.

If the current task is unclear:
- inspect `docs/TASKS.md`
- choose the highest-priority incomplete task
- do not start future-phase features

Prefer correctness, traceability, and maintainability over feature count.

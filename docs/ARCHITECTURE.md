# Architecture

## 1. Architecture Goal

The system should evolve from a research-oriented ESG benchmarking engine into a reusable ESG knowledge and data collection platform.

The V0 architecture only needs to support:

Source Document
→ Source Clause
→ Topic
→ Topic-Clause Mapping
→ Review
→ Export

The architecture must remain extensible for later:

Canonical Requirement
→ Applicability
→ Department Mapping
→ Question Generation
→ Data Collection

but these later layers are not part of current implementation scope.

---

## 2. High-Level Architecture

```text
                ┌─────────────────────────┐
                │       User / Admin      │
                └────────────┬────────────┘
                             │
                             ↓
                ┌─────────────────────────┐
                │        FastAPI API      │
                └────────────┬────────────┘
                             │
                             ↓
                ┌─────────────────────────┐
                │   Application Services  │
                └────────────┬────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ↓                  ↓                  ↓
   Source Domain       Taxonomy Domain     Mapping Domain
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ↓
                ┌─────────────────────────┐
                │      Repositories       │
                └────────────┬────────────┘
                             │
                             ↓
                ┌─────────────────────────┐
                │ PostgreSQL + pgvector   │
                └─────────────────────────┘

External processing:

PDF / DOCX / XBRL
        ↓
Parser Layer
        ↓
Structured Clause Candidate
        ↓
Validation
        ↓
Database

AI:

Candidate Retrieval
        ↓
Context Builder
        ↓
LLM Provider
        ↓
Structured Mapping Output
        ↓
Pydantic Validation
        ↓
Review
```

---

## 3. Architectural Style

Use a modular monolith.

Reasons:
- early-stage product
- one core team
- strongly related relational data
- easier schema evolution
- easier debugging
- lower operational complexity

Do not split into microservices during V0.

---

## 4. Backend Structure

```text
backend/
├── api/
├── domain/
│   ├── source/
│   ├── taxonomy/
│   ├── crosswalk/
│   ├── applicability/
│   ├── materiality/
│   ├── department/
│   ├── question/
│   ├── evidence/
│   └── export/
├── ai/
│   ├── prompts/
│   ├── schemas/
│   ├── providers/
│   └── context/
├── parsers/
│   ├── docling/
│   ├── arelle/
│   └── mineru/
├── models/
├── repositories/
├── services/
└── workers/
```

Only the following modules are required in V0:

- `domain/source`
- `domain/taxonomy`
- mapping logic under taxonomy or a dedicated V0 mapping module
- `domain/export`
- `ai`
- `parsers`
- `models`
- `repositories`
- `services`

Other domain folders are future placeholders.

---

## 5. Frontend

Frontend is not a V0 priority.

If a UI is added during V0, keep it minimal:

1. Source Documents
2. Source Clauses
3. Topics
4. Topic-Clause Mapping Review
5. Export

Do not build a full client-facing SaaS interface yet.

---

## 6. Database

Primary database:
- PostgreSQL

Optional semantic search extension:
- pgvector

Relational data should remain relational.

Use SQL for:
- exact source lookup
- framework filtering
- version filtering
- topic relationships
- review status
- export queries

Use vector search only for:
- semantic candidate retrieval
- similar clause retrieval
- fuzzy topic matching

---

## 7. File Storage

During local V0 development:

```text
data/sources/
```

may be used as raw source storage.

Source files must be treated as immutable inputs.

Each source document should have a SHA-256 hash.

Future production storage may move to:
- S3
- OSS
- COS
- Azure Blob

The database should store metadata and storage paths, not binary PDF content.

---

## 8. Parser Layer

Parser selection should depend on source type.

Preferred strategy:

1. machine-readable taxonomy / XBRL when available
2. structured HTML
3. DOCX
4. PDF with text layer
5. OCR fallback

Suggested parsers:
- Arelle for XBRL/taxonomy
- Docling for standard documents
- MinerU only as fallback for difficult PDFs/OCR

Parser output must preserve provenance.

---

## 9. AI Layer

AI is used for semantic tasks.

V0 AI responsibilities:
- topic relevance judgment
- optional clause classification
- optional requirement summarization

AI must not be responsible for:
- file identity
- source location invention
- ID generation
- persistence rules
- export formatting
- framework versioning

---

## 10. Retrieval Strategy

V0 may start with:

```text
metadata filter
+ keyword retrieval
+ optional embedding retrieval
```

Then AI judges relevance.

Core principle:

```text
Retrieval Candidate != Approved Mapping
```

---

## 11. Review Workflow

Recommended V0 lifecycle:

```text
AI_SUGGESTED
→ REVIEW_REQUIRED
→ APPROVED
or
→ REJECTED
```

AI results should remain distinguishable from human-reviewed results.

---

## 12. Background Jobs

Background task infrastructure can be introduced only when ingestion becomes slow enough to require it.

Preferred future stack:
- Celery
- Redis

Do not introduce it before needed.

---

## 13. API Direction

Initial REST endpoints may include:

```text
GET    /frameworks
POST   /source-documents
GET    /source-documents/{id}
GET    /source-documents/{id}/clauses

POST   /topics/import
GET    /topics

POST   /mappings/generate
GET    /mappings
PATCH  /mappings/{id}

POST   /exports/benchmark
```

Exact endpoint design may evolve.

---

## 14. Observability

AI calls should eventually capture:

- trace_id
- task_type
- model
- prompt_version
- latency
- token_usage
- output
- validation status
- review result

Langfuse may be introduced later.

---

## 15. Evaluation

AI mapping evaluation should live in:

```text
tests/eval/
data/gold/
```

Core V0 metrics:

- precision
- recall
- traceability coverage

The system should prefer measurable evaluation over subjective prompt tuning.

---

## 16. Future Architecture

Later phases may add:

```text
SourceClause
      ↓
CanonicalRequirement
      ↓
Applicability
      ↓
Materiality
      ↓
Department
      ↓
QuestionTemplate
      ↓
ProjectQuestion
```

Do not prematurely implement these layers in V0.

---

## 17. Non-Goals

V0 is not:
- a chatbot
- a report writer
- a rating score engine
- a full ESG SaaS
- a client portal
- a workflow automation suite

V0 is a traceable ESG framework-to-topic mapping engine.

# Architecture and Product Decisions

This file records decisions that should not be casually reversed by AI agents.

---

# ADR-001 — Evidence First

Status: Accepted

Decision:

All framework-backed outputs must retain a traceable source.

At minimum:

```text
Framework
SourceDocument
SourceClause
OriginalText
```

Reason:

The primary product risk is incorrect or unverifiable ESG framework attribution.

---

# ADR-002 — Raw Clauses Are Immutable

Status: Accepted

Decision:

Raw framework clauses must not be merged or overwritten.

Normalization happens in a separate future layer.

Reason:

Different frameworks may express similar requirements differently.
The original source must remain independently auditable.

---

# ADR-003 — No Source, No Claim

Status: Accepted

Decision:

The system cannot present a statement as a framework requirement unless it references an actual SourceClause.

Reason:

Avoid hallucinated or incorrect framework claims.

---

# ADR-004 — Modular Monolith

Status: Accepted

Decision:

V0 uses a modular monolith.

Do not implement microservices.

Reason:
- lower complexity
- easier debugging
- early-stage architecture
- strongly related domain data

---

# ADR-005 — PostgreSQL as Future Primary Database

Status: Accepted

Decision:

The production-oriented persistence layer should use PostgreSQL.

pgvector may be used for semantic retrieval.

Reason:

The domain is strongly relational and requires provenance, versioning, joins, and transactions.

Note:

Early V0 parsing experiments may temporarily use JSON/JSONL files before database persistence is complete.

---

# ADR-006 — AI Does Semantic Work Only

Status: Accepted

Decision:

LLMs should be used for:
- classification
- semantic matching
- summarization
- explanation
- constrained generation

LLMs should not perform deterministic responsibilities such as:
- IDs
- hashes
- version control
- export formatting
- sorting
- source identity

---

# ADR-007 — AI Proposes, Human Publishes

Status: Accepted

Decision:

AI-created mappings begin as suggestions.

They must be reviewable.

Reason:

ESG framework interpretation can be professionally consequential.

---

# ADR-008 — Pilot Frameworks

Status: Accepted

Decision:

V0 starts only with:
- HKEX
- SSE

Reason:

The immediate goal is to validate the workflow rather than maximize framework coverage.

---

# ADR-009 — Pilot Topics Are Provided

Status: Accepted

Decision:

The V0 system does not infer the company's ESG topic universe.

The topic list is provided by the project team.

Reason:

Topic identification and materiality assessment occur earlier in the consulting workflow.

---

# ADR-010 — Department Mapping Is Deferred

Status: Accepted

Decision:

Department-topic mapping is not inferred by AI in V0.

For the later pilot, mappings may be manually provided.

Reason:

Department responsibilities vary significantly by company and are normally aligned with the client.

---

# ADR-011 — Materiality Is Deferred

Status: Accepted

Decision:

Do not implement materiality-based question depth in V0.

Reason:

The current first validation target is framework retrieval accuracy and traceability.

---

# ADR-012 — Clause/Section Preferred Over Page-Only Traceability

Status: Accepted

Decision:

Source traceability should prefer:

```text
Framework
Version
Chapter
Section
Clause
Original Text
```

PDF page should be stored where available but should not be the only source locator.

Reason:

PDF physical pages and printed report pages may differ.

---

# ADR-013 — Qualitative and Quantitative Collection Will Be Separate Later

Status: Accepted

Decision:

Future information collection should distinguish:
- qualitative information
- quantitative data

Reason:

Their structures, guidance, units, and client workflows differ.

---

# ADR-014 — GHG Data Requires Special Transformation

Status: Accepted

Decision:

Future questionnaire generation should not blindly ask clients for calculated Scope 1/2/3 results.

It may need to request underlying activity data.

Reason:

Consultants often calculate emissions from activity data and emission factors.

This is deferred beyond V0.

---

# ADR-015 — Formula/Definition Extraction Is Not a V0 Requirement

Status: Accepted

Decision:

The schema may reserve fields for:
- definitions
- formulas
- calculation guidance

but full automatic extraction is not required in V0.

Reason:

These fields can initially be manually reviewed and added for high-value quantitative metrics.

---

# ADR-016 — Existing Benchmarking Beta Is a Precursor, Not a Separate Product

Status: Accepted

Decision:

The earlier peer benchmarking research engine should be treated as validated precursor logic.

Reusable principles:
- Evidence First
- Retrieval != Analysis
- Raw != Reviewed
- Late Structuring
- deterministic scripts + AI judgment

The new system generalizes this into a reusable platform.

---

# ADR-017 — V0 Source Universe Expanded

Status: Accepted

Date: 2026-08-28

Extends: ADR-008 (Pilot Frameworks). ADR-008 is kept unchanged as a
historical record; this ADR supersedes its scope.

Decision:

The V0 source universe is expanded from HKEX/SSE to five sources across
four source families:

| Source  | Source Category      |
| ------- | -------------------- |
| SSE     | exchange_rule        |
| HKEX    | exchange_rule        |
| GRI     | reporting_standard   |
| MSCI    | rating_methodology   |
| CSA-COS | rating_questionnaire |

Supporting decisions:

1. The five sources belong to different source families (exchange
   disclosure rules, reporting standards, rating methodologies, rating
   questionnaires). They must not be forced into a single clause-only
   shape.
2. `SourceClause` keeps its historical name but represents a generic
   atomic traceable source unit.
3. Raw source units must preserve their original source structure and
   wording (`original_text` remains immutable).
4. No cross-framework merging happens during ingestion. Raw units from
   different sources stay separate.
5. Normalization / CanonicalRequirement remains deferred to a later
   version (consistent with ADR-002 and the deferred backlog).

Reason:

The pilot must prove that one unified pipeline can handle exchange
rules, reporting standards, rating methodologies and rating
questionnaires while preserving exact source provenance — not just
clause-structured exchange rules.

---

# Decision Change Process

If an AI agent believes an accepted decision should change:

1. Do not silently change implementation direction.
2. Add a proposed ADR section.
3. Explain:
   - current limitation
   - proposed change
   - alternatives
   - migration impact
4. Wait for explicit approval before major architectural change.

# Data Model

## 1. Scope

This document defines the minimum domain model for V0.

This document is the canonical implementation specification for V0
domain entities. If another document (including the PRD) conflicts
with it on entity fields or enums, this document governs
implementation.

V0 covers five sources across four source families:

| Source  | Source Category      | Typical Atomic Unit               |
| ------- | -------------------- | --------------------------------- |
| SSE     | exchange_rule        | clause / requirement              |
| HKEX    | exchange_rule        | clause / requirement              |
| GRI     | reporting_standard   | disclosure / requirement          |
| MSCI    | rating_methodology   | criterion / key-issue requirement |
| CSA-COS | rating_questionnaire | question / criterion              |

Conceptual V0 workflow:

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

Persistent V0 domain model:

```text
Framework
→ SourceDocument
→ SourceClause
↔ Topic
→ TopicClauseMapping
```

`SourceClause` is a historical V0 name. Semantically it represents the
minimal independently traceable atomic source unit — a generic atomic
source unit. It does NOT imply that every source is a clause in the
legal / regulatory sense.

The model must preserve source traceability.

---

# 2. Framework

Represents a framework, reporting standard, rating system, or regulatory
disclosure system.

V0 examples:
- SSE
- HKEX
- GRI
- MSCI
- CSA-COS

Fields:

```text
framework_id
code
name
publisher
jurisdiction
framework_type
status
created_at
updated_at
```

Suggested `framework_type` values:

```text
exchange_rule
reporting_standard
rating_methodology
rating_questionnaire
```

V0 source-to-category mapping:

```text
SSE       → exchange_rule
HKEX      → exchange_rule
GRI       → reporting_standard
MSCI      → rating_methodology
CSA-COS   → rating_questionnaire
```

Example:

```json
{
  "framework_id": "FW-HKEX",
  "code": "HKEX",
  "name": "HKEX ESG Reporting Code",
  "publisher": "Hong Kong Exchanges and Clearing Limited",
  "jurisdiction": "Hong Kong",
  "framework_type": "exchange_rule",
  "status": "active"
}
```

```json
{
  "framework_id": "FW-GRI",
  "code": "GRI",
  "name": "GRI Universal Standards 2021",
  "publisher": "Global Reporting Initiative",
  "jurisdiction": "Global",
  "framework_type": "reporting_standard",
  "status": "active"
}
```

---

# 3. SourceDocument

Represents one specific version of one source document.

Fields:

```text
document_id
framework_id

title
version
publication_date
effective_date

language

source_url
file_path
file_hash

document_type

status

created_at
updated_at
```

Rules:
- one framework may have multiple SourceDocuments
- one SourceDocument represents one identifiable version
- file hash must be calculated when source is ingested
- old versions must not be overwritten

Suggested status values:

```text
draft
ingested
parsed
review_required
approved
published
deprecated
```

Status semantics:

- `draft`: metadata record exists but ingestion is incomplete
- `ingested`: original source registered and hashed
- `parsed`: parser produced structured source units
- `review_required`: extraction requires review
- `approved`: source extraction has been approved
- `published`: available for formal project use
- `deprecated`: superseded / no longer current but retained historically

Historical versions must not be overwritten or removed.

---

# 4. SourceClause

Represents a **generic atomic traceable source unit**.

`SourceClause` is a historical V0 name. It does not imply that every
source family uses legal / regulatory clauses. Depending on the source
family, one record represents a clause, disclosure, requirement,
criterion, question, metric, or guidance.

This is the most important V0 entity.

Fields:

```text
clause_id
document_id

source_item_type

chapter
section
subsection

clause_number
source_code
heading

original_text

page_pdf
page_printed
source_locator

qualitative_or_quantitative

parser_name
parser_version

status

created_at
updated_at
```

Suggested `source_item_type` values:

```text
clause
disclosure
requirement
criterion
question
metric
guidance
```

Field semantics:

- `source_item_type`: what kind of atomic unit this record is in its own
  source family.
- `clause_number`: identifier for rule-style numbered clauses. Suited to
  exchange rule sources such as HKEX and SSE. May be null.
- `source_code`: a more generic Source Unit Identifier, for example:

  ```text
  GRI 305-1
  MSCI Human Capital Development
  CSA-COS 3.2.1
  ```

  Both `clause_number` and `source_code` may be null, but neither may be
  fabricated by AI.
- `source_locator`: locator for sources that are not chapter/clause
  structured, e.g. questionnaire path, section anchor, Key Issue name.

Optional derived fields:

```text
summary
requirement_type
ai_classification
classification_confidence
```

Rules:

1. `original_text` is immutable.
2. AI-generated summaries must never overwrite `original_text`.
3. Every source unit must reference a valid `SourceDocument`.
4. Page number may be null if not reliable.
5. Use chapter / section / clause_number when the source family supports
   them; otherwise rely on `source_code` and `source_locator`.
6. Do not fabricate a clause number or source code.

Suggested `qualitative_or_quantitative` values:

```text
qualitative
quantitative
mixed
unknown
```

Suggested `status` values:

```text
draft
reviewed
approved
rejected
```

---

# 5. Source Family Modeling Rules

The five V0 sources must not be forced into a single clause-only shape.

## SSE and HKEX (exchange_rule)

- Atomic units are clauses / requirements.
- `clause_number`, chapter and section are normally available and should
  be preserved.

## GRI (reporting_standard)

- Atomic units are disclosures / requirements, typically identified by
  `source_code` (e.g. `GRI 305-1`) rather than `clause_number`.
- The future parser stage must distinguish at least:

  ```text
  Requirement
  Recommendation
  Guidance
  Disclosure
  ```

- A Recommendation or Guidance must never be expressed as
  "GRI requires ...".
- Only a true Requirement may be presented as a mandatory requirement.

This rule is defined at baseline level now; the parser implementing it
is built later (see TASKS P2B). No parser is implemented yet.

## MSCI (rating_methodology)

- MSCI is a rating methodology, not a disclosure standard.
- `clause_number` must not be required for MSCI units.
- Atomic units may come from:

  ```text
  Key Issue
  Criterion
  Methodology Statement
  Relevant Metric
  Expectation
  ```

- MSCI source units are allowed to have no traditional clause numbering.

## CSA-COS (rating_questionnaire)

- CSA-COS is a questionnaire / rating-type source.
- Atomic units may include:

  ```text
  Question ID
  Question
  Criterion
  Definition
  Metric
  Supporting Guidance
  ```

- CSA-COS must not be processed with the HKEX / SSE clause parser
  structure.

---

# 6. Topic

Represents a client or project ESG topic.

For V0, topics are imported from the pilot project rather than generated by AI.

Fields:

```text
topic_id
name
parent_topic_id
description
level

status

created_at
updated_at
```

Example:

```json
{
  "topic_id": "TOPIC-CLIMATE",
  "name": "应对气候变化",
  "level": 2,
  "status": "active"
}
```

---

# 7. TopicClauseMapping

Represents a proposed or approved relationship between a topic and a source clause.

Fields:

```text
mapping_id

topic_id
clause_id

relevance

mapping_method
decision_origin

ai_reason
ai_confidence

review_status
reviewer
reviewed_at

created_at
updated_at
```

Suggested `relevance` values:

```text
strong
partial
related
not_relevant
```

Suggested `mapping_method` values:

```text
keyword
embedding
hybrid
manual
```

Suggested `decision_origin` values:

```text
RULE
AI
HUMAN
```

Suggested `review_status` values:

```text
AI_SUGGESTED
REVIEW_REQUIRED
APPROVED
REJECTED
```

Rules:
- every mapping must point to a real topic
- every mapping must point to a real source clause
- source clause provenance must be retrievable through the mapping
- approved mappings must remain reproducible

---

# 8. Optional V0 AI Trace

If implemented, AI inference metadata may be stored separately.

Suggested fields:

```text
trace_id
task_type

model_provider
model_name
model_version

prompt_name
prompt_version

input_hash
output_json

latency_ms
token_input
token_output
estimated_cost

created_at
```

This is optional for first implementation but recommended.

---

# 9. Gold Dataset Schema

The V0 Gold Dataset must cover all five sources:
SSE, HKEX, GRI, MSCI and CSA-COS.

Evaluation must not hide behind a single overall score. It must report
both:

- overall precision / recall, and
- precision / recall per source family
  (SSE / HKEX / GRI / MSCI / CSA-COS),

so that weak performance in any one source family is visible.

Gold records identify the expected atomic source unit using whichever
identifier the source family supports: `clause_number` for exchange rule
sources and `source_code` for standard / rating sources.

## clauses.jsonl

Used to verify atomic source unit extraction.

Example (clause-based exchange source):

```json
{
  "document_id": "DOC-HKEX-001",
  "source": "HKEX",
  "expected_clause_number": "A1",
  "expected_source_item_type": "clause",
  "expected_text_contains": "governance",
  "expected_chapter": "Governance"
}
```

Example (code-based reporting standard source):

```json
{
  "document_id": "DOC-GRI-2021-305",
  "source": "GRI",
  "expected_source_code": "GRI 305-1",
  "expected_source_item_type": "disclosure",
  "expected_text_contains": "Scope 1"
}
```

Example (rating questionnaire source):

```json
{
  "document_id": "DOC-CSA-COS-2025",
  "source": "CSA-COS",
  "expected_source_code": "CSA-COS 3.2.1",
  "expected_source_item_type": "question",
  "expected_text_contains": "water"
}
```

---

## topic_mapping.jsonl

Used to evaluate topic-to-source-unit mapping.

Example positive (clause-based):

```json
{
  "topic_name": "应对气候变化",
  "source": "HKEX",
  "clause_number": "D1",
  "relevant": true
}
```

Example positive (code-based):

```json
{
  "topic_name": "温室气体排放",
  "source": "GRI",
  "source_code": "GRI 305-1",
  "relevant": true
}
```

Example negative:

```json
{
  "topic_name": "员工培训",
  "source": "HKEX",
  "clause_number": "D1",
  "relevant": false
}
```

---

# 10. Future Model

The following entities are planned but should NOT be implemented in V0 unless explicitly approved:

```text
CanonicalRequirement
RequirementClauseMapping
MetricDefinition
Client
Project
ProjectFramework
MaterialityAssessment
Department
DepartmentTopicMapping
QuestionTemplate
ProjectQuestion
QuestionSourceMapping
ExportSnapshot
AuditLog
```

---

# 11. Future Relationship Model

```text
Framework
    ↓
SourceDocument
    ↓
SourceClause
    ↓
CanonicalRequirement
    ↓
Topic / Metric
    ↓
QuestionTemplate
    ↓
ProjectQuestion
```

For V0, stop at:

```text
SourceClause ↔ Topic
```

---

# 12. Data Integrity Rules

Mandatory:

1. never delete source provenance silently
2. never overwrite old document versions
3. never overwrite source text with AI output
4. never merge raw source units
5. never store an AI-generated source claim without a source unit
   reference
6. use stable IDs
7. support reproducible export
8. never force non-clause source units into clause-only fields; use
   `source_item_type` / `source_code` / `source_locator` instead

---

# 13. IDs

Suggested stable ID formats:

```text
FW-SSE
FW-HKEX
FW-GRI
FW-MSCI
FW-CSA-COS

DOC-HKEX-2025-001
DOC-GRI-2021-001

CL-HKEX-2025-000001
CL-GRI-2021-000001

TOPIC-0001

MAP-000001
```

IDs should be generated by code, not by LLM.

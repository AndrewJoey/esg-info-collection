# P1.5 — Department Form Input Contract

Status: Draft analytical contract (NOT a domain entity)

This document defines the **minimum information** we should attempt to
extract from future department information-collection forms. It is an
analytical extraction contract used to plan the next real-business
validation step. It is **not** a formal domain model, and nothing here
should be implemented as a Pydantic entity during P1.5.

This file contains no real client rows or confidential project-derived
content.

---

## Why this exists

P1.5 validated the current real input, which is a **Topic × Department
scope mapping**:

```text
Department  ↔  Topic     ("this department is involved in this topic")
```

The next real input will be existing **department information-collection
forms**. Those forms operate at a finer grain than scope mapping. Before
they arrive, we fix a minimal extraction contract so the data can be
captured consistently without prematurely committing to a schema.

Scope mapping must never be treated as question-level ownership:

```text
Topic × Department Scope Mapping   ≠   Question × Department Assignment
```

A department being *involved* in a topic does not mean that department
must answer every future question under that topic.

---

## Minimum extraction fields

Each extracted collection item from a department form should capture at
least:

```text
department
source_form
source_sheet
source_row

original_collection_item
original_context

data_type
unit
frequency

topic_id
topic_name

mapping_status
notes
```

Field intent (analytical, not normative):

- `department` — the department the form belongs to.
- `source_form` / `source_sheet` / `source_row` — provenance back to the
  original form, mirroring the P1.5 audit approach.
- `original_collection_item` — the item exactly as written in the form
  (source-of-truth text; do not rewrite).
- `original_context` — any surrounding label / section text that gives
  the item meaning.
- `data_type` — observed nature of the item (e.g. qualitative vs
  quantitative); recorded as observed, not inferred.
- `unit` — measurement unit if the form states one.
- `frequency` — collection cadence if the form states one.
- `topic_id` / `topic_name` — link to a canonical Topic where the form
  makes the link explicit; left blank when not stated (do not infer).
- `mapping_status` — whether the topic link is explicit, ambiguous, or
  absent.
- `notes` — free-text audit notes.

Provenance and original text are mandatory; everything else is captured
only when the form states it. Nothing is inferred.

---

## Unresolved questions to test when department forms arrive

These are open questions to answer **from evidence**, not to decide now:

1. Can one existing question map to multiple Topics?
2. Can one Topic contain multiple questions? — expected **yes**.
3. Can the same metric appear in multiple department forms?
4. Are the data owner and the reporting owner the same?
5. Do we need a primary vs supporting department distinction?
6. Do qualitative questions and quantitative metrics need different
   structures?
7. Should `InformationPoint` exist separately from `Question`?
8. Is the future relationship:

   ```text
   Requirement → Question
   ```

   or:

   ```text
   Requirement → InformationPoint → Question
   ```

Do not answer these architecturally until the real department forms
provide evidence.

---

## Explicitly out of scope for P1.5

No entity below is created or modeled in P1.5:

```text
Department
DepartmentTopicMapping (as a domain model)
ExistingQuestion
InformationPoint
Question
QuestionTemplate
QuestionDepartmentMapping
CanonicalRequirement
Project
Client
Materiality
```

P1.5 collects evidence for a future modeling decision; it does not make
that decision.

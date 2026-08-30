---
name: esg-autopilot
description: Autonomous end-to-end V0 ESG information-collection delivery. Use to resume the multi-phase build (source ingestion → retrieval → AI mapping → evaluation → requirement consolidation → question generation → department Excel export) from docs/RUN_STATE.md.
---

# ESG Autopilot

Resumable operating instructions for the autonomous V0 delivery run.

## On resume

1. Read `docs/RUN_STATE.md` — it holds `current_phase`, `next_action`,
   `available_inputs`, `missing_inputs`, `hard_stop_reason`.
2. Read `AGENTS.md`, `docs/DATA_MODEL.md`, `docs/TASKS.md`,
   `docs/DECISIONS.md` for governance.
3. `git status && git branch --show-current && git log --oneline -5`.
4. Run `.venv/bin/python -m pytest` to confirm the baseline is green.
5. Continue from `next_action`.

## Guardrails (non-negotiable)

- Never commit `refer/**`, `/议题清单.xlsx`, `data/output/**`. Verify
  with `git diff --cached --name-only` before every commit.
- `original_text` immutable; No Source, No Claim; deterministic work in
  code, LLM for semantic judgment on retrieved candidates only.
- Do not merge to `main`. Push the feature branch.
- Only HARD STOP for: unreadable/unidentifiable source, an accepted ADR
  that real data breaks, missing department forms at a dependent phase,
  or evaluation too poor for a defensible deliverable.

## Phase sequence

```
P1.6 department form inventory (skip if no forms; record dependency)
P2.0 source manifest
P2A SSE+HKEX  → P2B GRI → P2C MSCI → P2D CSA-COS
P3 topic import → P4 retrieval → P5 AI mapping → P6 evaluation
P7 Topic×Requirement matrix
P8 consolidation → P9 InformationPoint → P10 questions
P11 gap analysis → P12 dept assignment → P13 qual/quant → P14 Excel
P15 traceability/QA
```

Vertical-slice first: after SSE+HKEX, run one E→S→G topic end-to-end
before scaling to all sources and topics.

## Output locations

- Ingested source units, mappings, matrices: `data/output/**` (local).
- Final workbook: `data/output/final/ESG_Information_Collection_Master.xlsx`.
- Reusable code: `backend/`, `scripts/`. Tests: `tests/` (synthetic
  fixtures only).

## After each milestone

Run tests → update `docs/TASKS.md`, `docs/CHANGELOG.md`,
`docs/RUN_STATE.md` → verify staged files → commit → push.

# CLAUDE.md

@AGENTS.md

## Persistent Claude-specific rules for this repository

- `docs/DATA_MODEL.md` is the canonical implementation spec for domain
  entities. `docs/TASKS.md` is the authoritative implementation
  sequence. Do not silently override accepted ADRs in
  `docs/DECISIONS.md`.
- **Never commit real / licensed / client data.** Protected:
  `/议题清单.xlsx`, `refer/**` (all source PDFs/DOCX), `data/output/**`.
  These are git-ignored; do not force-add them.
- Before every commit: run `python -m pytest`, then
  `git diff --cached --name-only` and confirm no protected path appears.
- Original source text (`original_text`) is immutable. Derived
  summaries live in a separate layer. No Source, No Claim: every
  requirement/question must trace to a real SourceClause.
- Deterministic work (IDs, hashes, parsing structure, Excel) stays in
  code. LLMs are for semantic judgment only, on retrieved candidates.
- Update `docs/RUN_STATE.md` after every milestone so the run is
  resumable after context compaction.
- Do not merge into `main`. Work on the feature branch and push.

## Environment

- Python 3.13 via `.venv/`. Parsing deps: `pypdf`, `pdfplumber`,
  `python-docx`, `openpyxl` (in `requirements.txt`).
- Run tests: `.venv/bin/python -m pytest`

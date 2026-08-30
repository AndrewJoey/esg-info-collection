"""SourceClause domain model (DATA_MODEL #4).

``SourceClause`` is a historical entity name. Semantically it is a
**generic atomic traceable source unit**: a clause for exchange rules
(SSE/HKEX), a disclosure / requirement for GRI, a criterion /
key-issue requirement for MSCI, a question / criterion for CSA-COS.

Immutability
------------
The whole record is ``frozen``. This protects ``original_text`` (the
source-of-truth content) from accidental in-place mutation, per the
"Original Source Is Immutable" principle. State transitions (e.g.
review status) are expressed deliberately by creating an updated copy:

    reviewed = clause.model_copy(
        update={"status": SourceClauseStatus.REVIEWED, "updated_at": ...}
    )

Tradeoff: no in-place mutation of any field, in exchange for a simple,
well-tested guarantee that stored source text cannot be silently
rewritten.

Identifier rules
----------------
- ``clause_number`` is NOT required (GRI / MSCI / CSA-COS units may
  have no rule-style numbering).
- ``source_code`` is NOT required either.
- The model supports locating units through chapter/section/subsection,
  clause_number, source_code, heading, pages, or ``source_locator``.
- Identifiers may be null when the source does not provide them, but
  they must never be fabricated.
"""

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .enums import QualitativeOrQuantitative, SourceClauseStatus, SourceItemType
from .ids import CLAUSE_PREFIX, DOCUMENT_PREFIX


class SourceClause(BaseModel):
    """Generic atomic traceable source unit (historical name:
    SourceClause)."""

    model_config = ConfigDict(frozen=True)

    clause_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)

    source_item_type: SourceItemType

    chapter: str | None = None
    section: str | None = None
    subsection: str | None = None

    clause_number: str | None = None
    source_code: str | None = None
    heading: str | None = None

    original_text: str = Field(min_length=1)

    page_pdf: int | None = Field(default=None, ge=1)
    page_printed: str | None = None
    source_locator: str | None = None

    qualitative_or_quantitative: QualitativeOrQuantitative = (
        QualitativeOrQuantitative.UNKNOWN
    )

    parser_name: str | None = None
    parser_version: str | None = None

    status: SourceClauseStatus = SourceClauseStatus.DRAFT

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("clause_id")
    @classmethod
    def _clause_id_shape(cls, value: str) -> str:
        if not value.startswith(CLAUSE_PREFIX):
            raise ValueError(f"clause_id must start with {CLAUSE_PREFIX!r}")
        return value

    @field_validator("document_id")
    @classmethod
    def _document_id_shape(cls, value: str) -> str:
        if not value.startswith(DOCUMENT_PREFIX):
            raise ValueError(f"document_id must start with {DOCUMENT_PREFIX!r}")
        return value

    @field_validator("original_text")
    @classmethod
    def _original_text_not_blank(cls, value: str) -> str:
        # Source fidelity: store the text as given; only reject records
        # with no content at all.
        if not value.strip():
            raise ValueError("original_text must contain non-whitespace text")
        return value

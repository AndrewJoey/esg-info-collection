"""SourceDocument domain model (DATA_MODEL #3).

A SourceDocument represents one specific, identifiable version of one
source document. Historical versions are distinct records: a new
version never overwrites an old one (enforced semantically in V0;
persistence-level enforcement belongs to a later milestone).
"""

from datetime import date, datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .enums import SourceDocumentStatus
from .ids import DOCUMENT_PREFIX, FRAMEWORK_PREFIX


class SourceDocument(BaseModel):
    """One version of one source document under a Framework."""

    model_config = ConfigDict(validate_assignment=True)

    document_id: str = Field(min_length=1)
    framework_id: str = Field(min_length=1)

    title: str = Field(min_length=1)
    version: str = Field(min_length=1)
    publication_date: date | None = None
    effective_date: date | None = None

    language: str | None = None

    source_url: str | None = None
    file_path: str | None = None
    file_hash: str | None = None

    document_type: str | None = None

    status: SourceDocumentStatus = SourceDocumentStatus.DRAFT

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("document_id")
    @classmethod
    def _document_id_shape(cls, value: str) -> str:
        if not value.startswith(DOCUMENT_PREFIX):
            raise ValueError(f"document_id must start with {DOCUMENT_PREFIX!r}")
        return value

    @field_validator("framework_id")
    @classmethod
    def _framework_id_shape(cls, value: str) -> str:
        if not value.startswith(FRAMEWORK_PREFIX):
            raise ValueError(
                f"framework_id must start with {FRAMEWORK_PREFIX!r}"
            )
        return value

    @model_validator(mode="after")
    def _hash_required_once_ingested(self) -> "SourceDocument":
        # DATA_MODEL #3: "file hash must be calculated when source is
        # ingested". Only `draft` may exist before the source file is
        # registered and hashed.
        if self.status is not SourceDocumentStatus.DRAFT:
            if not self.file_hash or not self.file_hash.strip():
                raise ValueError(
                    "file_hash is required once the document leaves the "
                    "draft status"
                )
        return self

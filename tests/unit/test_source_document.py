"""Tests for the SourceDocument domain model."""

import pytest
from pydantic import ValidationError

from backend.models import SourceDocumentStatus
from tests.unit.factories import document


class TestValidSourceDocument:
    def test_ingested_with_hash(self):
        doc = document()
        assert doc.status is SourceDocumentStatus.INGESTED
        assert doc.file_hash

    @pytest.mark.parametrize(
        "status",
        [
            SourceDocumentStatus.INGESTED,
            SourceDocumentStatus.PARSED,
            SourceDocumentStatus.REVIEW_REQUIRED,
            SourceDocumentStatus.APPROVED,
            SourceDocumentStatus.PUBLISHED,
            SourceDocumentStatus.DEPRECATED,
        ],
    )
    def test_every_post_draft_state_with_hash(self, status):
        doc = document(status=status)
        assert doc.status is status

    def test_draft_without_hash_is_allowed(self):
        doc = document(status=SourceDocumentStatus.DRAFT, file_hash=None)
        assert doc.status is SourceDocumentStatus.DRAFT

    def test_status_accepts_lowercase_string(self):
        doc = document(status="published")
        assert doc.status is SourceDocumentStatus.PUBLISHED


class TestInvalidSourceDocument:
    def test_invalid_status_rejected(self):
        with pytest.raises(ValidationError):
            document(status="INGESTED")  # wrong casing is not a value

    @pytest.mark.parametrize(
        "status",
        [
            SourceDocumentStatus.INGESTED,
            SourceDocumentStatus.PARSED,
            SourceDocumentStatus.REVIEW_REQUIRED,
            SourceDocumentStatus.APPROVED,
            SourceDocumentStatus.PUBLISHED,
            SourceDocumentStatus.DEPRECATED,
        ],
    )
    def test_hash_required_after_draft(self, status):
        with pytest.raises(ValidationError, match="file_hash"):
            document(status=status, file_hash=None)

    def test_whitespace_hash_treated_as_missing(self):
        with pytest.raises(ValidationError):
            document(status=SourceDocumentStatus.PARSED, file_hash="   ")

    def test_framework_reference_required(self):
        with pytest.raises(ValidationError):
            document(framework_id="")

    def test_framework_reference_shape(self):
        with pytest.raises(ValidationError):
            document(framework_id="HKEX")

    def test_document_id_shape(self):
        with pytest.raises(ValidationError):
            document(document_id="HKEX-2025-001")

    def test_title_required(self):
        with pytest.raises(ValidationError):
            document(title="")

    def test_assignment_validation(self):
        doc = document()
        with pytest.raises(ValidationError):
            doc.status = "not_a_status"

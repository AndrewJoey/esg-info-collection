"""Tests for the SourceClause (generic atomic traceable source unit) model."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from backend.models import SourceClauseStatus, SourceItemType
from tests.unit.factories import NOW, clause


class TestSourceFamilyShapes:
    def test_valid_hkex_sse_style_clause(self):
        c = clause(chapter="Governance", clause_number="A1")
        assert c.source_item_type is SourceItemType.CLAUSE
        assert c.clause_number == "A1"

    def test_valid_sse_style_clause(self):
        c = clause(
            document_id="DOC-ffeeddccbbaa",
            source_item_type=SourceItemType.REQUIREMENT,
            clause_number="4.1",
            chapter="第四章",
        )
        assert c.clause_number == "4.1"

    def test_valid_gri_style_disclosure(self):
        c = clause(
            document_id="DOC-gri305",
            source_item_type=SourceItemType.DISCLOSURE,
            clause_number=None,
            chapter=None,
            section=None,
            source_code="GRI 305-1",
            heading="Emissions",
            original_text="The organization shall report Scope 1 emissions.",
        )
        assert c.source_code == "GRI 305-1"
        assert c.clause_number is None

    def test_valid_msci_style_criterion_without_clause_number(self):
        c = clause(
            document_id="DOC-msci",
            source_item_type=SourceItemType.CRITERION,
            clause_number=None,
            source_code="MSCI Human Capital Development",
            source_locator="Key Issue: Human Capital / Criterion 2",
            original_text="Assess investment in workforce development.",
        )
        assert c.clause_number is None
        assert c.source_locator.startswith("Key Issue")

    def test_valid_csa_cos_style_question_without_clause_number(self):
        c = clause(
            document_id="DOC-csa",
            source_item_type=SourceItemType.QUESTION,
            clause_number=None,
            source_code="CSA-COS 3.2.1",
            source_locator="Environmental Dimension / Water Management",
            original_text="Does the company track water withdrawal?",
        )
        assert c.clause_number is None
        assert c.source_item_type is SourceItemType.QUESTION

    def test_neither_clause_number_nor_source_code_is_required(self):
        c = clause(clause_number=None, source_code=None, source_locator=None)
        assert c.clause_number is None
        assert c.source_code is None


class TestValidation:
    @pytest.mark.parametrize("text", ["", "   ", "\n\t"])
    def test_original_text_must_not_be_blank(self, text):
        with pytest.raises(ValidationError, match="original_text"):
            clause(original_text=text)

    def test_invalid_source_item_type_rejected(self):
        with pytest.raises(ValidationError):
            clause(source_item_type="paragraph")

    def test_all_seven_source_item_types_accepted(self):
        for value in [
            "clause",
            "disclosure",
            "requirement",
            "criterion",
            "question",
            "metric",
            "guidance",
        ]:
            assert clause(source_item_type=value).source_item_type.value == value

    def test_page_pdf_must_be_positive(self):
        with pytest.raises(ValidationError):
            clause(page_pdf=0)

    def test_clause_id_shape(self):
        with pytest.raises(ValidationError):
            clause(clause_id="CLAUSE-1")

    def test_document_id_shape(self):
        with pytest.raises(ValidationError):
            clause(document_id="HKEX-2025")

    def test_document_reference_required(self):
        with pytest.raises(ValidationError):
            clause(document_id="")


class TestImmutability:
    def test_original_text_cannot_be_mutated_in_place(self):
        c = clause()
        with pytest.raises(ValidationError):
            c.original_text = "rewritten by a derived operation"

    def test_frozen_record_cannot_be_mutated(self):
        c = clause()
        with pytest.raises(ValidationError):
            c.status = SourceClauseStatus.APPROVED

    def test_transition_happens_through_explicit_copy(self):
        c = clause()
        later = datetime(2026, 8, 29, tzinfo=timezone.utc)
        reviewed = c.model_copy(
            update={"status": SourceClauseStatus.REVIEWED, "updated_at": later}
        )
        # The original record keeps its source text and draft status.
        assert c.original_text == "The board should oversee climate-related risks."
        assert c.status is SourceClauseStatus.DRAFT
        # The copy carries the transition.
        assert reviewed.status is SourceClauseStatus.REVIEWED
        assert reviewed.original_text == c.original_text
        assert reviewed.clause_id == c.clause_id

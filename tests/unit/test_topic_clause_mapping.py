"""Tests for the TopicClauseMapping domain model."""

import pytest
from pydantic import ValidationError

from backend.models import (
    DecisionOrigin,
    MappingMethod,
    MappingReviewStatus,
    Relevance,
)
from tests.unit.factories import NOW, mapping


class TestRelevance:
    @pytest.mark.parametrize(
        "value", ["strong", "partial", "related", "not_relevant"]
    )
    def test_all_canonical_relevance_values(self, value):
        m = mapping(relevance=value)
        assert m.relevance.value == value

    @pytest.mark.parametrize("bad", ["STRONG", "MEDIUM", "WEAK", "NOT_RELEVANT", "high"])
    def test_non_canonical_relevance_rejected(self, bad):
        with pytest.raises(ValidationError):
            mapping(relevance=bad)


class TestMappingMethod:
    @pytest.mark.parametrize("value", ["keyword", "embedding", "hybrid", "manual"])
    def test_all_methods_accepted(self, value):
        assert mapping(mapping_method=value).mapping_method.value == value

    def test_invalid_method_rejected(self):
        with pytest.raises(ValidationError):
            mapping(mapping_method="vector")


class TestDecisionOrigin:
    @pytest.mark.parametrize("value", ["RULE", "AI", "HUMAN"])
    def test_all_origins_accepted(self, value):
        assert mapping(decision_origin=value).decision_origin is DecisionOrigin(value)

    def test_lowercase_origin_rejected(self):
        with pytest.raises(ValidationError):
            mapping(decision_origin="ai")


class TestReviewLifecycle:
    def test_default_is_ai_suggested(self):
        m = mapping()
        assert m.review_status is MappingReviewStatus.AI_SUGGESTED

    def test_ai_suggested_without_reviewer_allowed(self):
        m = mapping(review_status="AI_SUGGESTED", reviewer=None, reviewed_at=None)
        assert m.reviewer is None

    def test_review_required_without_reviewer_allowed(self):
        m = mapping(review_status="REVIEW_REQUIRED", reviewer=None, reviewed_at=None)
        assert m.review_status is MappingReviewStatus.REVIEW_REQUIRED

    def test_approved_with_decision_record_allowed(self):
        m = mapping(
            review_status="APPROVED",
            decision_origin=DecisionOrigin.HUMAN,
            reviewer="consultant-a",
            reviewed_at=NOW,
        )
        assert m.review_status is MappingReviewStatus.APPROVED
        assert m.reviewed_at == NOW

    def test_rejected_with_decision_record_allowed(self):
        m = mapping(review_status="REJECTED", reviewer="consultant-b", reviewed_at=NOW)
        assert m.review_status is MappingReviewStatus.REJECTED

    def test_approved_requires_reviewer(self):
        with pytest.raises(ValidationError, match="reviewer"):
            mapping(review_status="APPROVED", reviewer=None, reviewed_at=NOW)

    def test_approved_requires_reviewed_at(self):
        with pytest.raises(ValidationError, match="reviewed_at"):
            mapping(review_status="APPROVED", reviewer="consultant-a", reviewed_at=None)

    def test_rejected_requires_decision_record(self):
        with pytest.raises(ValidationError):
            mapping(review_status="REJECTED", reviewer=None, reviewed_at=None)

    def test_legacy_ai_draft_state_rejected(self):
        with pytest.raises(ValidationError):
            mapping(review_status="AI_DRAFT")

    def test_legacy_draft_state_rejected(self):
        with pytest.raises(ValidationError):
            mapping(review_status="DRAFT")


class TestMachineRecommendationPreserved:
    def test_ai_side_kept_next_to_review_side(self):
        m = mapping(
            review_status="APPROVED",
            reviewer="consultant-a",
            reviewed_at=NOW,
        )
        # Machine recommendation fields remain intact after the human
        # decision is recorded.
        assert m.decision_origin is DecisionOrigin.AI
        assert m.ai_reason is not None
        assert m.ai_confidence == pytest.approx(0.91)
        assert m.reviewer == "consultant-a"


class TestValidation:
    @pytest.mark.parametrize("confidence", [-0.1, 1.5])
    def test_confidence_out_of_range_rejected(self, confidence):
        with pytest.raises(ValidationError):
            mapping(ai_confidence=confidence)

    def test_confidence_bounds_accepted(self):
        assert mapping(ai_confidence=0.0).ai_confidence == 0.0
        assert mapping(ai_confidence=1.0).ai_confidence == 1.0

    def test_mapping_id_shape(self):
        with pytest.raises(ValidationError):
            mapping(mapping_id="M-1")

    def test_topic_id_shape(self):
        with pytest.raises(ValidationError):
            mapping(topic_id="T-1")

    def test_clause_id_shape(self):
        with pytest.raises(ValidationError):
            mapping(clause_id="HKEX-A1")

    def test_required_references(self):
        with pytest.raises(ValidationError):
            mapping(topic_id="")
        with pytest.raises(ValidationError):
            mapping(clause_id="")

    def test_assignment_validation(self):
        m = mapping()
        with pytest.raises(ValidationError):
            m.relevance = "MEDIUM"

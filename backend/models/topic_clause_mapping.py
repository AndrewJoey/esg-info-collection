"""TopicClauseMapping domain model (DATA_MODEL #7).

A proposed or approved relationship between a Topic and an atomic
source unit (SourceClause). The model preserves both sides:

- machine recommendation: ``decision_origin``, ``ai_reason``,
  ``ai_confidence``, ``mapping_method``
- eventual review decision: ``review_status``, ``reviewer``,
  ``reviewed_at``

Canonical review lifecycle:

    AI_SUGGESTED -> REVIEW_REQUIRED -> APPROVED or -> REJECTED

Review *workflow* logic (state transitions, approvals) is not
implemented in P1; only the model and its validation exist here.
"""

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .enums import DecisionOrigin, MappingMethod, MappingReviewStatus, Relevance
from .ids import CLAUSE_PREFIX, MAPPING_PREFIX, TOPIC_PREFIX

_TERMINAL_REVIEW_STATES = (
    MappingReviewStatus.APPROVED,
    MappingReviewStatus.REJECTED,
)


class TopicClauseMapping(BaseModel):
    """One topic-to-source-unit mapping candidate or decision."""

    model_config = ConfigDict(validate_assignment=True)

    mapping_id: str = Field(min_length=1)
    topic_id: str = Field(min_length=1)
    clause_id: str = Field(min_length=1)

    relevance: Relevance
    mapping_method: MappingMethod
    decision_origin: DecisionOrigin

    ai_reason: str | None = None
    ai_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    review_status: MappingReviewStatus = MappingReviewStatus.AI_SUGGESTED
    reviewer: str | None = None
    reviewed_at: datetime | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("mapping_id")
    @classmethod
    def _mapping_id_shape(cls, value: str) -> str:
        if not value.startswith(MAPPING_PREFIX):
            raise ValueError(f"mapping_id must start with {MAPPING_PREFIX!r}")
        return value

    @field_validator("topic_id")
    @classmethod
    def _topic_id_shape(cls, value: str) -> str:
        if not value.startswith(TOPIC_PREFIX):
            raise ValueError(f"topic_id must start with {TOPIC_PREFIX!r}")
        return value

    @field_validator("clause_id")
    @classmethod
    def _clause_id_shape(cls, value: str) -> str:
        if not value.startswith(CLAUSE_PREFIX):
            raise ValueError(f"clause_id must start with {CLAUSE_PREFIX!r}")
        return value

    @model_validator(mode="after")
    def _terminal_review_state_requires_decision_record(self) -> "TopicClauseMapping":
        # A terminal review decision must preserve who decided and when.
        if self.review_status in _TERMINAL_REVIEW_STATES:
            if not self.reviewer or not self.reviewer.strip():
                raise ValueError(
                    f"reviewer is required when review_status is "
                    f"{self.review_status.value}"
                )
            if self.reviewed_at is None:
                raise ValueError(
                    f"reviewed_at is required when review_status is "
                    f"{self.review_status.value}"
                )
        return self

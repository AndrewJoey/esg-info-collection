"""Explicit enums for controlled V0 domain values.

Every value matches ``docs/DATA_MODEL.md`` exactly, including casing.
DATA_MODEL is the canonical implementation specification for V0 domain
entities; do not invent alternative enum names or values here.
"""

from enum import StrEnum


class FrameworkType(StrEnum):
    """Source family / framework category (DATA_MODEL #2)."""

    EXCHANGE_RULE = "exchange_rule"
    REPORTING_STANDARD = "reporting_standard"
    RATING_METHODOLOGY = "rating_methodology"
    RATING_QUESTIONNAIRE = "rating_questionnaire"


class SourceDocumentStatus(StrEnum):
    """Canonical SourceDocument lifecycle (DATA_MODEL #3)."""

    DRAFT = "draft"
    INGESTED = "ingested"
    PARSED = "parsed"
    REVIEW_REQUIRED = "review_required"
    APPROVED = "approved"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"


class SourceItemType(StrEnum):
    """Kind of atomic source unit within its own source family
    (DATA_MODEL #4)."""

    CLAUSE = "clause"
    DISCLOSURE = "disclosure"
    REQUIREMENT = "requirement"
    CRITERION = "criterion"
    QUESTION = "question"
    METRIC = "metric"
    GUIDANCE = "guidance"


class QualitativeOrQuantitative(StrEnum):
    """Suggested values for ``qualitative_or_quantitative``
    (DATA_MODEL #4)."""

    QUALITATIVE = "qualitative"
    QUANTITATIVE = "quantitative"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class SourceClauseStatus(StrEnum):
    """Suggested status values for SourceClause (DATA_MODEL #4)."""

    DRAFT = "draft"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"


class TopicStatus(StrEnum):
    """Topic lifecycle status (DATA_MODEL #6 example uses ``active``)."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class Relevance(StrEnum):
    """Canonical topic-to-source-unit relevance values
    (DATA_MODEL #7)."""

    STRONG = "strong"
    PARTIAL = "partial"
    RELATED = "related"
    NOT_RELEVANT = "not_relevant"


class MappingMethod(StrEnum):
    """How a mapping candidate was produced (DATA_MODEL #7)."""

    KEYWORD = "keyword"
    EMBEDDING = "embedding"
    HYBRID = "hybrid"
    MANUAL = "manual"


class DecisionOrigin(StrEnum):
    """Who/what made the relevance decision (DATA_MODEL #7)."""

    RULE = "RULE"
    AI = "AI"
    HUMAN = "HUMAN"


class MappingReviewStatus(StrEnum):
    """Canonical TopicClauseMapping review lifecycle (DATA_MODEL #7).

    AI_SUGGESTED -> REVIEW_REQUIRED -> APPROVED or -> REJECTED
    """

    AI_SUGGESTED = "AI_SUGGESTED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

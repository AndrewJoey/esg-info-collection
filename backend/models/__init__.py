"""V0 core domain models (P1).

Canonical specification: ``docs/DATA_MODEL.md``.

Entities: Framework, SourceDocument, SourceClause (generic atomic
traceable source unit), Topic, TopicClauseMapping.
"""

from .enums import (
    DecisionOrigin,
    FrameworkType,
    MappingMethod,
    MappingReviewStatus,
    QualitativeOrQuantitative,
    Relevance,
    SourceClauseStatus,
    SourceDocumentStatus,
    SourceItemType,
    TopicStatus,
)
from .framework import Framework
from .ids import (
    generate_clause_id,
    generate_document_id,
    generate_framework_id,
    generate_mapping_id,
    generate_topic_id,
)
from .source_clause import SourceClause
from .source_document import SourceDocument
from .topic import Topic
from .topic_clause_mapping import TopicClauseMapping

__all__ = [
    "DecisionOrigin",
    "Framework",
    "FrameworkType",
    "MappingMethod",
    "MappingReviewStatus",
    "QualitativeOrQuantitative",
    "Relevance",
    "SourceClause",
    "SourceClauseStatus",
    "SourceDocument",
    "SourceDocumentStatus",
    "SourceItemType",
    "Topic",
    "TopicClauseMapping",
    "TopicStatus",
    "generate_clause_id",
    "generate_document_id",
    "generate_framework_id",
    "generate_mapping_id",
    "generate_topic_id",
]

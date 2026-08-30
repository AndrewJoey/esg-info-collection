"""Minimal valid-record factories for P1 domain model unit tests.

Each factory returns a record that passes all P1 validation; tests
override individual fields to exercise specific rules.
"""

from datetime import datetime, timezone

from backend.models import (
    DecisionOrigin,
    Framework,
    FrameworkType,
    MappingMethod,
    MappingReviewStatus,
    Relevance,
    SourceClause,
    SourceClauseStatus,
    SourceDocument,
    SourceDocumentStatus,
    SourceItemType,
    Topic,
    TopicClauseMapping,
    TopicStatus,
)

NOW = datetime(2026, 8, 28, tzinfo=timezone.utc)


def framework(**overrides) -> Framework:
    data = dict(
        framework_id="FW-HKEX",
        code="HKEX",
        name="HKEX ESG Reporting Code",
        publisher="Hong Kong Exchanges and Clearing Limited",
        jurisdiction="Hong Kong",
        framework_type=FrameworkType.EXCHANGE_RULE,
        status="active",
        created_at=NOW,
        updated_at=NOW,
    )
    data.update(overrides)
    return Framework(**data)


def document(**overrides) -> SourceDocument:
    data = dict(
        document_id="DOC-a1b2c3d4e5f6",
        framework_id="FW-HKEX",
        title="HKEX ESG Reporting Code",
        version="2025",
        language="en",
        file_path="data/sources/hkex/esg-code-2025.pdf",
        file_hash="sha256:0123456789abcdef",
        document_type="pdf",
        status=SourceDocumentStatus.INGESTED,
        created_at=NOW,
        updated_at=NOW,
    )
    data.update(overrides)
    return SourceDocument(**data)


def clause(**overrides) -> SourceClause:
    data = dict(
        clause_id="CL-0123456789ab",
        document_id="DOC-a1b2c3d4e5f6",
        source_item_type=SourceItemType.CLAUSE,
        chapter="Governance",
        section="Board Oversight",
        clause_number="A1",
        heading="Climate governance",
        original_text="The board should oversee climate-related risks.",
        page_pdf=12,
        status=SourceClauseStatus.DRAFT,
        created_at=NOW,
        updated_at=NOW,
    )
    data.update(overrides)
    return SourceClause(**data)


def topic(**overrides) -> Topic:
    data = dict(
        topic_id="TOPIC-fedcba987654",
        name="应对气候变化",
        description="Climate change response",
        level=1,
        status=TopicStatus.ACTIVE,
        created_at=NOW,
        updated_at=NOW,
    )
    data.update(overrides)
    return Topic(**data)


def mapping(**overrides) -> TopicClauseMapping:
    data = dict(
        mapping_id="MAP-123456789abc",
        topic_id="TOPIC-fedcba987654",
        clause_id="CL-0123456789ab",
        relevance=Relevance.STRONG,
        mapping_method=MappingMethod.KEYWORD,
        decision_origin=DecisionOrigin.AI,
        ai_reason="Clause addresses climate governance directly.",
        ai_confidence=0.91,
        review_status=MappingReviewStatus.AI_SUGGESTED,
        created_at=NOW,
        updated_at=NOW,
    )
    data.update(overrides)
    return TopicClauseMapping(**data)

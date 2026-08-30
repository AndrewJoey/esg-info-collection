"""Tests for deterministic stable ID generation (backend.models.ids)."""

import pytest

from backend.models.ids import (
    generate_clause_id,
    generate_document_id,
    generate_framework_id,
    generate_mapping_id,
    generate_topic_id,
)


class TestFrameworkId:
    def test_uppercases_code(self):
        assert generate_framework_id("hkex") == "FW-HKEX"
        assert generate_framework_id("csa-cos") == "FW-CSA-COS"

    def test_strips_whitespace(self):
        assert generate_framework_id("  gri ") == "FW-GRI"

    def test_same_input_same_output(self):
        assert generate_framework_id("sse") == generate_framework_id("sse")

    @pytest.mark.parametrize("bad", ["", "   ", None])
    def test_rejects_empty_code(self, bad):
        with pytest.raises(ValueError):
            generate_framework_id(bad)


class TestDocumentId:
    def test_prefix(self):
        doc_id = generate_document_id("FW-HKEX", "ESG Reporting Code", "2025")
        assert doc_id.startswith("DOC-")

    def test_same_input_same_output(self):
        a = generate_document_id("FW-HKEX", "ESG Reporting Code", "2025")
        b = generate_document_id("FW-HKEX", "ESG Reporting Code", "2025")
        assert a == b

    def test_different_version_different_id(self):
        a = generate_document_id("FW-HKEX", "ESG Reporting Code", "2025")
        b = generate_document_id("FW-HKEX", "ESG Reporting Code", "2024")
        assert a != b

    def test_different_framework_different_id(self):
        a = generate_document_id("FW-HKEX", "ESG Reporting Code", "2025")
        b = generate_document_id("FW-SSE", "ESG Reporting Code", "2025")
        assert a != b

    @pytest.mark.parametrize("bad", ["", None])
    def test_rejects_missing_meaningful_input(self, bad):
        with pytest.raises(ValueError):
            generate_document_id(bad, "title", "v1")


class TestClauseId:
    def test_prefix(self):
        clause_id = generate_clause_id("DOC-abc", "clause", "text", clause_number="A1")
        assert clause_id.startswith("CL-")

    def test_same_input_same_output(self):
        a = generate_clause_id("DOC-abc", "disclosure", "Report Scope 1.", source_code="GRI 305-1")
        b = generate_clause_id("DOC-abc", "disclosure", "Report Scope 1.", source_code="GRI 305-1")
        assert a == b

    def test_different_text_different_id(self):
        a = generate_clause_id("DOC-abc", "clause", "text one")
        b = generate_clause_id("DOC-abc", "clause", "text two")
        assert a != b

    def test_clause_number_participates(self):
        a = generate_clause_id("DOC-abc", "clause", "same text", clause_number="A1")
        b = generate_clause_id("DOC-abc", "clause", "same text", clause_number="A2")
        assert a != b

    def test_no_identifier_required(self):
        # MSCI / CSA-COS style units without clause numbers still get IDs.
        clause_id = generate_clause_id("DOC-abc", "criterion", "Develop human capital.")
        assert clause_id.startswith("CL-")

    def test_rejects_empty_original_text(self):
        with pytest.raises(ValueError):
            generate_clause_id("DOC-abc", "clause", "   ")


class TestTopicId:
    def test_prefix(self):
        assert generate_topic_id("应对气候变化").startswith("TOPIC-")

    def test_same_input_same_output(self):
        assert generate_topic_id("水资源管理") == generate_topic_id("水资源管理")

    def test_parent_participates(self):
        root = generate_topic_id("环境")
        child = generate_topic_id("水资源管理", parent_topic_id=root)
        other_parent = generate_topic_id("水资源管理", parent_topic_id="TOPIC-other")
        assert child != other_parent
        assert generate_topic_id("水资源管理") != child

    def test_rejects_empty_name(self):
        with pytest.raises(ValueError):
            generate_topic_id("   ")


class TestMappingId:
    def test_prefix_and_determinism(self):
        a = generate_mapping_id("TOPIC-1", "CL-1")
        b = generate_mapping_id("TOPIC-1", "CL-1")
        assert a == b
        assert a.startswith("MAP-")

    def test_order_matters(self):
        assert generate_mapping_id("TOPIC-1", "CL-1") != generate_mapping_id(
            "CL-1", "TOPIC-1"
        )

    def test_different_inputs_different_ids(self):
        assert generate_mapping_id("TOPIC-1", "CL-1") != generate_mapping_id(
            "TOPIC-1", "CL-2"
        )

    def test_rejects_missing_input(self):
        with pytest.raises(ValueError):
            generate_mapping_id("", "CL-1")

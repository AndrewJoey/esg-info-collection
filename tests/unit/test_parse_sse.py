"""Tests for P2A source parsers (SSE DOCX + HKEX helpers).

Synthetic fixtures only — no real source text.
"""

from __future__ import annotations

from pathlib import Path

import docx
import pytest

from backend.models import SourceClause, SourceDocument, SourceItemType
from scripts.parse_sse import _chinese_num_to_int, parse_sse_docx


def _make_sse_like_docx(path: Path) -> None:
    """Build a synthetic DOCX mimicking the SSE 章/条 structure."""
    d = docx.Document()
    d.add_paragraph("合成指引标题")           # title noise, ignored
    d.add_paragraph("第一章 总则")
    d.add_paragraph("第一条 这是第一条的合成正文内容。")
    d.add_paragraph("这是第一条的补充说明段落。")
    d.add_paragraph("第二条 这是第二条的合成正文。")
    d.add_paragraph("第二章 信息披露")
    d.add_paragraph("第三条 这是第三条的合成正文。")
    d.save(path)


class TestChineseNumerals:
    @pytest.mark.parametrize(
        ("s", "n"),
        [("一", 1), ("五", 5), ("十", 10), ("十一", 11),
         ("二十", 20), ("二十三", 23), ("九", 9)],
    )
    def test_conversion(self, s, n):
        assert _chinese_num_to_int(s) == n


class TestSSEParser:
    @pytest.fixture
    def parsed(self, tmp_path):
        p = tmp_path / "sse_like.docx"
        _make_sse_like_docx(p)
        return parse_sse_docx(p)

    def test_returns_document_and_clauses(self, parsed):
        doc, clauses = parsed
        assert isinstance(doc, SourceDocument)
        assert all(isinstance(c, SourceClause) for c in clauses)

    def test_document_metadata(self, parsed):
        doc, _ = parsed
        assert doc.framework_id == "FW-SSE"
        assert doc.document_id.startswith("DOC-")
        assert doc.file_hash and doc.file_hash.startswith("sha256:")
        assert doc.document_type == "docx"

    def test_three_clauses_extracted(self, parsed):
        _, clauses = parsed
        assert len(clauses) == 3
        assert [c.clause_number for c in clauses] == ["第一条", "第二条", "第三条"]

    def test_chapter_attribution(self, parsed):
        _, clauses = parsed
        assert clauses[0].chapter == "第一章 总则"
        assert clauses[1].chapter == "第一章 总则"
        assert clauses[2].chapter == "第二章 信息披露"

    def test_multiline_clause_body_preserved(self, parsed):
        _, clauses = parsed
        # First clause accumulates its supplementary paragraph.
        assert "补充说明" in clauses[0].original_text
        assert clauses[0].original_text.startswith("这是第一条")

    def test_all_clauses_are_clause_type(self, parsed):
        _, clauses = parsed
        assert all(c.source_item_type is SourceItemType.CLAUSE for c in clauses)

    def test_clause_ids_deterministic(self, tmp_path):
        p1 = tmp_path / "a.docx"
        p2 = tmp_path / "b.docx"
        _make_sse_like_docx(p1)
        _make_sse_like_docx(p2)
        _, c1 = parse_sse_docx(p1)
        _, c2 = parse_sse_docx(p2)
        # Same clause text + number + document identity -> same clause id.
        assert [c.clause_id for c in c1] == [c.clause_id for c in c2]

    def test_original_text_never_empty(self, parsed):
        _, clauses = parsed
        assert all(c.original_text.strip() for c in clauses)

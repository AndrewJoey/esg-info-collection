"""Tests for the QM collection builder (structure + provenance contract).

Uses the real curated IP definitions but a SYNTHETIC source index, so
no real source text is embedded in the test.
"""

import importlib.util
from pathlib import Path

from backend.pipeline.qm_collection import (
    QM_TOPICS,
    InformationPoint,
    _verify_sources,
)

_spec = importlib.util.spec_from_file_location(
    "qmb", Path(__file__).resolve().parent.parent.parent / "scripts" / "build_qm_workbook.py")
qmb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(qmb)


class TestScope:
    def test_exactly_three_topics(self):
        assert QM_TOPICS == ["产品和服务安全与质量", "化学品安全与成分管理", "负责任营销"]

    def test_all_ips_within_scope(self):
        assert all(ip.topic in QM_TOPICS for ip in qmb.INFORMATION_POINTS)


class TestProvenanceContract:
    def test_framework_backed_ips_have_source_ids(self):
        for ip in qmb.INFORMATION_POINTS:
            if ip.source_nature.startswith("FRAMEWORK"):
                assert ip.source_unit_ids, f"{ip.ip_id} lacks source evidence"

    def test_verify_sources_flags_missing(self):
        bad = [InformationPoint("X-IP", "产品和服务安全与质量", "治理", "l",
                                "qualitative", ["NONEXISTENT-CODE"], ["SSE"],
                                "FRAMEWORK_BACKED")]
        assert _verify_sources(bad, {"第四十七条"}) == ["X-IP:NONEXISTENT-CODE"]

    def test_verify_sources_passes_known(self):
        ok = [InformationPoint("Y-IP", "负责任营销", "治理", "l", "qualitative",
                               ["GRI 417-1"], ["GRI"], "FRAMEWORK_BACKED")]
        assert _verify_sources(ok, {"GRI 417-1"}) == []


class TestCollectionItems:
    def test_items_generated(self):
        items = qmb.build_collection_items()
        assert len(items) >= len(qmb.INFORMATION_POINTS)

    def test_qual_and_quant_present(self):
        items = qmb.build_collection_items()
        kinds = {i.kind for i in items}
        assert "qualitative" in kinds
        assert "quantitative" in kinds

    def test_every_item_has_source_nature(self):
        items = qmb.build_collection_items()
        from backend.pipeline.qm_collection import SOURCE_NATURE
        assert all(i.source_nature in SOURCE_NATURE for i in items)

    def test_all_items_review_required(self):
        items = qmb.build_collection_items()
        assert all(i.review_status == "REVIEW_REQUIRED" for i in items)

    def test_quant_items_have_period(self):
        items = qmb.build_collection_items()
        for i in items:
            if i.kind == "quantitative":
                assert i.period


class TestHumanTransform:
    def test_all_24_questions_covered(self):
        qids = {t[0] for t in qmb.HUMAN_TRANSFORM}
        assert len(qids) == 24
        assert qids == {f"Q{n:03d}" for n in range(1, 25)}

    def test_every_transform_has_action(self):
        for qid, topic, dim, diag, action, ips in qmb.HUMAN_TRANSFORM:
            assert action
            assert topic in QM_TOPICS

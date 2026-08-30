"""Tests for the target collection library builder (synthetic rows)."""

from scripts.build_target_library import build_library, classify_quant_qual


class TestQuantQualClassification:
    def test_quantitative_by_cues(self):
        # two quant cues -> quantitative
        assert classify_quant_qual("总量以吨计算的排放量") == "quantitative"
        assert classify_quant_qual("total emissions in metric tons") == "quantitative"

    def test_qualitative_default(self):
        assert classify_quant_qual("描述董事会的治理政策") == "qualitative"
        assert classify_quant_qual("describe the governance policy") == "qualitative"


def _rows():
    return [
        {"topic_id": "T1", "topic_name": "应对气候变化", "framework": "GRI",
         "source_code": "GRI 305-1", "clause_number": "",
         "original_text": "total GHG emissions in metric tons of CO2",
         "source_locator": "loc1", "retrieval_score": "3"},
        {"topic_id": "T1", "topic_name": "应对气候变化", "framework": "GRI",
         "source_code": "GRI 305-2", "clause_number": "",
         "original_text": "energy indirect emissions total in tonnes",
         "source_locator": "loc2", "retrieval_score": "2"},
        {"topic_id": "T1", "topic_name": "应对气候变化", "framework": "SSE",
         "source_code": "", "clause_number": "第二十七条",
         "original_text": "披露主体应当描述温室气体减排管理措施与政策",
         "source_locator": "loc3", "retrieval_score": "2"},
        {"topic_id": "T1", "topic_name": "应对气候变化", "framework": "SSE",
         "source_code": "", "clause_number": "第九条",
         "original_text": "low score row", "source_locator": "loc4",
         "retrieval_score": "1"},  # below min_score
    ]


class TestBuildLibrary:
    def test_min_score_filter(self):
        items = build_library(_rows(), min_score=2)
        # the score=1 row is excluded
        all_codes = [c for it in items for c in it["source_codes"]]
        assert "第九条" not in all_codes

    def test_groups_by_topic_framework_quantqual(self):
        items = build_library(_rows(), min_score=2)
        keys = {(i["topic_id"], i["framework"], i["qualitative_or_quantitative"])
                for i in items}
        # GRI quantitative group + SSE qualitative group
        assert ("T1", "GRI", "quantitative") in keys
        assert ("T1", "SSE", "qualitative") in keys

    def test_aggregates_source_items(self):
        items = build_library(_rows(), min_score=2)
        gri = next(i for i in items if i["framework"] == "GRI")
        assert len(gri["source_item_ids"]) == 2
        assert "GRI 305-1" in gri["source_codes"]

    def test_all_review_required(self):
        items = build_library(_rows(), min_score=2)
        assert all(i["review_status"] == "REVIEW_REQUIRED" for i in items)

    def test_topics_covered(self):
        items = build_library(_rows(), min_score=2)
        assert {i["topic_id"] for i in items} == {"T1"}

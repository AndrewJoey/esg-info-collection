"""Tests for deterministic candidate retrieval (synthetic data only)."""

from backend.pipeline.retrieval import (
    Candidate,
    candidate_to_mapping_dict,
    retrieve_candidates,
)


def _topics():
    return [
        {"topic_id": "TOPIC-clim01", "topic_name": "应对气候变化"},
        {"topic_id": "TOPIC-watr01", "topic_name": "水资源利用"},
        {"topic_id": "TOPIC-none01", "topic_name": "未知合成议题"},  # no lexicon
    ]


def _clauses():
    return [
        {"clause_id": "CL-a", "document_id": "DOC-sse",
         "original_text": "披露主体应当披露温室气体排放与碳减排。",
         "source_code": None, "clause_number": "第二十四条"},
        {"clause_id": "CL-b", "document_id": "DOC-hkex",
         "original_text": "總耗水量及密度。", "source_code": "HKEX A2.2",
         "clause_number": "A2.2"},
        {"clause_id": "CL-c", "document_id": "DOC-sse",
         "original_text": "本条与任何议题都不相关的合成文本。",
         "source_code": None, "clause_number": "第九十九条"},
    ]


FW = {"DOC-sse": "SSE", "DOC-hkex": "HKEX"}


class TestRetrieve:
    def test_climate_matches_ghg_clause(self):
        cands = retrieve_candidates(_topics(), _clauses(), FW)
        clim = [c for c in cands if c.topic_name == "应对气候变化"]
        assert any(c.clause_id == "CL-a" for c in clim)

    def test_water_matches_water_clause(self):
        cands = retrieve_candidates(_topics(), _clauses(), FW)
        water = [c for c in cands if c.topic_name == "水资源利用"]
        assert any(c.clause_id == "CL-b" for c in water)

    def test_irrelevant_clause_not_matched(self):
        cands = retrieve_candidates(_topics(), _clauses(), FW)
        assert all(c.clause_id != "CL-c" for c in cands)

    def test_topic_without_lexicon_yields_nothing(self):
        cands = retrieve_candidates(_topics(), _clauses(), FW)
        assert all(c.topic_name != "未知合成议题" for c in cands)

    def test_framework_resolved(self):
        cands = retrieve_candidates(_topics(), _clauses(), FW)
        a = next(c for c in cands if c.clause_id == "CL-a")
        assert a.framework == "SSE"

    def test_score_is_keyword_hit_count(self):
        cands = retrieve_candidates(_topics(), _clauses(), FW)
        a = next(c for c in cands if c.clause_id == "CL-a")
        # 温室, 碳, 排放, 减排 all present
        assert a.score >= 3

    def test_min_score_filter(self):
        low = retrieve_candidates(_topics(), _clauses(), FW, min_score=1)
        high = retrieve_candidates(_topics(), _clauses(), FW, min_score=99)
        assert len(high) == 0
        assert len(low) > 0

    def test_deterministic(self):
        a = retrieve_candidates(_topics(), _clauses(), FW)
        b = retrieve_candidates(_topics(), _clauses(), FW)
        assert [c.clause_id for c in a] == [c.clause_id for c in b]


class TestMappingDict:
    def test_provenance_and_review_contract(self):
        c = Candidate("TOPIC-x", "应对气候变化", "CL-a", "SSE", None,
                      "第二十四条", 3, ["温室", "碳", "排放"])
        m = candidate_to_mapping_dict(c)
        # No Source, No Claim: clause id present.
        assert m["clause_id"] == "CL-a"
        # Not an approved or AI verdict.
        assert m["decision_origin"] == "RULE"
        assert m["review_status"] == "REVIEW_REQUIRED"
        assert m["ai_reason"] is None
        assert m["ai_confidence"] is None

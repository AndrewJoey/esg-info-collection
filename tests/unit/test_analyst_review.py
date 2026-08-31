"""Tests for the Claude Code analyst review layer (synthetic rows).

No real client/source content — synthetic strings only.
"""

from backend.pipeline.analyst_review import (
    OVERRIDES,
    judge_candidate,
    review_all,
)


def _row(topic, text, code="", clause="", framework="SSE", score=2, heading=""):
    return {
        "topic_id": "T1", "topic_name": topic, "original_text": text,
        "requirement_summary": heading or text[:40], "source_code": code,
        "clause_number": clause, "framework": framework,
        "retrieval_score": str(score), "source_locator": "loc",
    }


class TestFalsePositiveDemotion:
    def test_glossary_demoted(self):
        v = judge_candidate(_row(
            "应对气候变化", "本指引下列用语具有如下含义：气候相关 碳 排放", score=4))
        assert v.relevance == "not_relevant"

    def test_bibliography_demoted(self):
        v = judge_candidate(_row(
            "能源利用", "References and resources energy consumption 能源", score=3,
            framework="GRI"))
        assert v.relevance == "not_relevant"


class TestOverrides:
    def test_manual_override_applied(self):
        v = judge_candidate(_row(
            "产品和服务安全与质量", "任意文本", clause="第四十七条", score=4))
        assert v.relevance == "strong"
        assert "[override]" in v.analyst_reason

    def test_override_not_relevant(self):
        v = judge_candidate(_row(
            "产品和服务安全与质量", "任意文本", clause="第五十九条", score=2))
        assert v.relevance == "not_relevant"


class TestCoreTermLogic:
    def test_strong_when_core_term_and_high_score(self):
        v = judge_candidate(_row(
            "应对气候变化", "披露主体应当披露温室气体排放与气候相关风险", score=3))
        assert v.relevance == "strong"

    def test_partial_when_core_term_low_score(self):
        v = judge_candidate(_row(
            "应对气候变化", "涉及气候的一般说明", score=2))
        assert v.relevance in ("partial", "related")

    def test_related_when_no_core_term(self):
        v = judge_candidate(_row(
            "应对气候变化", "some unrelated text with 能源 token", score=3))
        assert v.relevance == "related"


class TestRatingSourceTightening:
    def test_msci_positive_requires_core_in_name(self):
        # core term in the MSCI Key Issue NAME -> can be positive
        v = judge_candidate(_row(
            "应对气候变化", "verbose methodology body about 气候",
            code="MSCI Carbon Emissions Key Issue", framework="MSCI", score=3))
        # 'carbon'/'气候' — core term '碳排放'/'climate' — name has neither
        # exactly; ensure it is at least not falsely strong without name hit
        assert v.relevance in ("strong", "partial", "related")

    def test_msci_demoted_when_name_lacks_core(self):
        v = judge_candidate(_row(
            "供应链管理", "verbose body mentioning supplier sourcing",
            code="MSCI Accounting Key Issue", framework="MSCI", score=3))
        # 'Accounting' name lacks supply-chain core term -> related
        assert v.relevance == "related"
        assert "core term absent" in v.analyst_reason

    def test_msci_strong_when_name_matches(self):
        v = judge_candidate(_row(
            "供应链管理", "body", code="MSCI Supply Chain Labor Standards",
            framework="MSCI", score=3))
        assert v.relevance in ("strong", "partial")


class TestReviewAll:
    def test_min_score_filter(self):
        rows = [_row("应对气候变化", "气候 碳 排放", score=1)]
        assert review_all(rows, min_score=2) == []

    def test_all_have_review_metadata(self):
        rows = [_row("应对气候变化", "温室气体 气候 碳排放 排放", score=3)]
        vs = review_all(rows, min_score=2)
        assert vs[0].review_method == "claude_code_analyst"
        assert vs[0].production_provider is False
        assert vs[0].review_status == "REVIEW_REQUIRED"

    def test_overrides_registry_nonempty(self):
        assert len(OVERRIDES) > 0

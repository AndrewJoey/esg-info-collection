"""Tests for the AI relevance layer architecture (mock provider only)."""

import pytest
from pydantic import ValidationError

from backend.ai.relevance import (
    MockRelevanceProvider,
    RelevanceRequest,
    RelevanceVerdict,
    build_relevance_prompt,
    is_production_provider_configured,
)


def _req(text: str, topic="应对气候变化") -> RelevanceRequest:
    return RelevanceRequest(
        topic_name=topic, clause_id="CL-x", framework="SSE",
        original_text=text,
    )


KW = {"应对气候变化": ["气候", "温室", "碳", "排放"]}


class TestSchema:
    def test_verdict_rejects_bad_relevance(self):
        with pytest.raises(ValidationError):
            RelevanceVerdict(
                clause_id="CL-x", relevance="STRONG", reason="r",
                confidence=0.5, model_provider="mock", model_name="mock",
            )

    def test_verdict_confidence_bounds(self):
        with pytest.raises(ValidationError):
            RelevanceVerdict(
                clause_id="CL-x", relevance="strong", reason="r",
                confidence=1.5, model_provider="mock", model_name="mock",
            )

    def test_request_requires_text(self):
        with pytest.raises(ValidationError):
            RelevanceRequest(topic_name="t", clause_id="CL-x",
                             framework="SSE", original_text="")


class TestPrompt:
    def test_prompt_contains_topic_and_text(self):
        p = build_relevance_prompt(_req("温室气体排放核算"))
        assert "应对气候变化" in p
        assert "温室气体排放核算" in p
        # Constrains to canonical values + no fabrication.
        assert "not_relevant" in p
        assert "Do not invent" in p


class TestMockProvider:
    def test_strong_when_many_keywords(self):
        prov = MockRelevanceProvider(KW)
        v = prov.judge(_req("温室气体、碳排放与气候相关披露"))
        assert v.relevance == "strong"
        assert v.confidence == pytest.approx(0.9)
        assert v.model_name == "mock"  # clearly labeled, not real AI

    def test_not_relevant_when_no_keywords(self):
        prov = MockRelevanceProvider(KW)
        v = prov.judge(_req("本条与议题无关的合成文本"))
        assert v.relevance == "not_relevant"

    def test_clause_id_preserved(self):
        prov = MockRelevanceProvider(KW)
        v = prov.judge(_req("碳排放"))
        assert v.clause_id == "CL-x"  # No Source, No Claim

    def test_deterministic(self):
        prov = MockRelevanceProvider(KW)
        a = prov.judge(_req("温室气体 碳 排放"))
        b = prov.judge(_req("温室气体 碳 排放"))
        assert a.model_dump() == b.model_dump()

    def test_retry_returns_verdict(self):
        prov = MockRelevanceProvider(KW)
        v = prov.judge_with_retry(_req("碳排放"))
        assert v is not None


class TestProductionGate:
    def test_no_production_provider_in_this_env(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        assert is_production_provider_configured() is False

    def test_detects_configured_key(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        assert is_production_provider_configured() is True

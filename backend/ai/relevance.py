"""AI relevance-judgment layer architecture (P5).

Provider-agnostic interface for topic-to-source-unit relevance
judgment. Domain logic does not depend on any specific LLM provider
(AGENTS.md architecture rule).

IMPORTANT — honesty contract:
- No production LLM provider is configured in this environment, and the
  live production relevance run is BLOCKED until one is.
- This module implements the *architecture* (interface, schema, prompt,
  service, error handling) plus a deterministic ``MockRelevanceProvider``
  used ONLY for tests and pipeline wiring.
- The mock does NOT fabricate production AI results: its verdicts are
  clearly labeled ``model_name="mock"`` and it applies transparent
  keyword rules. Callers must not treat mock output as real AI judgment.
- Every produced mapping references a real SourceClause id (No Source,
  No Claim) and carries provider/prompt metadata for auditability.
"""

from __future__ import annotations

import abc
from typing import Literal

from pydantic import BaseModel, Field

RELEVANCE_VALUES = ("strong", "partial", "related", "not_relevant")
PROMPT_VERSION = "relevance/v1"


class RelevanceRequest(BaseModel):
    """Input to a relevance judgment for one (topic, source unit) pair."""

    topic_name: str = Field(min_length=1)
    clause_id: str = Field(min_length=1)
    framework: str
    source_code: str | None = None
    clause_number: str | None = None
    original_text: str = Field(min_length=1)


class RelevanceVerdict(BaseModel):
    """Structured, validated output of a relevance judgment.

    This is the schema an LLM provider must return (structured output).
    """

    clause_id: str = Field(min_length=1)
    relevance: Literal["strong", "partial", "related", "not_relevant"]
    reason: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    model_provider: str
    model_name: str
    prompt_version: str = PROMPT_VERSION


def build_relevance_prompt(req: RelevanceRequest) -> str:
    """Deterministic prompt template for relevance judgment.

    Constrains the model to the four canonical relevance values and to
    judging ONLY the supplied source text (No Source, No Claim).
    """
    ident = req.source_code or req.clause_number or req.clause_id
    return (
        "You are an ESG framework analyst. Judge whether the following "
        "source requirement is relevant to the given ESG topic.\n\n"
        f"ESG topic: {req.topic_name}\n"
        f"Source: {req.framework} {ident}\n"
        f"Source text:\n{req.original_text}\n\n"
        "Return one of exactly these relevance values: "
        "strong, partial, related, not_relevant.\n"
        "Judge only from the source text above. Do not invent facts, "
        "clause numbers, or requirements. Provide a short reason and a "
        "confidence in [0,1]."
    )


class RelevanceProvider(abc.ABC):
    """Provider interface. A real implementation calls an LLM; a mock
    applies deterministic rules for tests."""

    provider_name: str = "abstract"
    model_name: str = "abstract"

    @abc.abstractmethod
    def judge(self, req: RelevanceRequest) -> RelevanceVerdict:
        ...

    def judge_with_retry(
        self, req: RelevanceRequest, retries: int = 2
    ) -> RelevanceVerdict | None:
        """Call judge() with bounded retries. Returns None on failure —
        the pipeline then keeps the candidate as REVIEW_REQUIRED rather
        than dropping provenance."""
        last_exc: Exception | None = None
        for _ in range(retries + 1):
            try:
                return self.judge(req)
            except Exception as exc:  # pragma: no cover - defensive
                last_exc = exc
        return None


class MockRelevanceProvider(RelevanceProvider):
    """Deterministic, transparent stand-in for tests / pipeline wiring.

    NOT a real AI. Applies keyword-overlap rules so behavior is
    reproducible. Clearly labeled model_name='mock'.
    """

    provider_name = "mock"
    model_name = "mock"

    def __init__(self, topic_keywords: dict[str, list[str]] | None = None):
        self._kw = topic_keywords or {}

    def judge(self, req: RelevanceRequest) -> RelevanceVerdict:
        keywords = self._kw.get(req.topic_name, [])
        text = req.original_text.lower()
        hits = [k for k in keywords if k.lower() in text]
        n = len(hits)
        if n >= 3:
            relevance, conf = "strong", 0.9
        elif n == 2:
            relevance, conf = "partial", 0.7
        elif n == 1:
            relevance, conf = "related", 0.5
        else:
            relevance, conf = "not_relevant", 0.5
        return RelevanceVerdict(
            clause_id=req.clause_id,
            relevance=relevance,
            reason=f"[mock] matched {n} topic keyword(s): {hits}",
            confidence=conf,
            model_provider=self.provider_name,
            model_name=self.model_name,
        )


def is_production_provider_configured() -> bool:
    """Whether a real LLM provider is available.

    Returns False in this environment (no key / SDK). Used to gate the
    live production relevance run without faking it.
    """
    import os

    key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")
    return bool(key and key.strip())

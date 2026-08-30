"""Evaluation harness (P6) — Precision / Recall / F1.

Computes retrieval/mapping quality overall and per source family, given
a Gold Dataset of human-verified (topic, clause) relevance labels.

Honesty contract:
- This is the harness only. It does NOT fabricate Gold labels for the
  full production dataset; callers supply real manually-verified labels
  (or synthetic labels in tests).
- Per-source-family metrics are always reported so weak performance in
  one family cannot hide behind an overall score.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GoldLabel:
    """A human-verified relevance label for one (topic, clause) pair."""

    topic_id: str
    clause_id: str
    framework: str
    relevant: bool


@dataclass
class Metrics:
    tp: int = 0
    fp: int = 0
    fn: int = 0

    @property
    def precision(self) -> float:
        denom = self.tp + self.fp
        return self.tp / denom if denom else 0.0

    @property
    def recall(self) -> float:
        denom = self.tp + self.fn
        return self.tp / denom if denom else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0

    def as_dict(self) -> dict:
        return {
            "tp": self.tp, "fp": self.fp, "fn": self.fn,
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1": round(self.f1, 4),
        }


@dataclass
class EvaluationReport:
    overall: Metrics = field(default_factory=Metrics)
    per_family: dict[str, Metrics] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "overall": self.overall.as_dict(),
            "per_source_family": {
                fw: m.as_dict() for fw, m in sorted(self.per_family.items())
            },
        }


def evaluate(
    predicted_positive: set[tuple[str, str]],
    gold: list[GoldLabel],
) -> EvaluationReport:
    """Compare predicted-positive (topic_id, clause_id) pairs to gold.

    - TP: predicted positive AND gold relevant
    - FP: predicted positive AND gold not-relevant
    - FN: not predicted AND gold relevant

    Only pairs present in the gold set are scored (closed-world over the
    labeled set), so precision/recall are well-defined.
    """
    report = EvaluationReport()
    gold_by_pair = {(g.topic_id, g.clause_id): g for g in gold}

    for (topic_id, clause_id), g in gold_by_pair.items():
        fam = g.framework
        report.per_family.setdefault(fam, Metrics())
        predicted = (topic_id, clause_id) in predicted_positive
        if predicted and g.relevant:
            report.overall.tp += 1
            report.per_family[fam].tp += 1
        elif predicted and not g.relevant:
            report.overall.fp += 1
            report.per_family[fam].fp += 1
        elif not predicted and g.relevant:
            report.overall.fn += 1
            report.per_family[fam].fn += 1
        # not predicted & not relevant = TN (not counted in P/R)

    return report

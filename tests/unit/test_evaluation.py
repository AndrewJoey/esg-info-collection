"""Tests for the evaluation harness (synthetic labels only)."""

from backend.pipeline.evaluation import GoldLabel, Metrics, evaluate


class TestMetrics:
    def test_precision_recall_f1(self):
        m = Metrics(tp=8, fp=2, fn=2)
        assert m.precision == 0.8
        assert m.recall == 0.8
        assert round(m.f1, 4) == 0.8

    def test_zero_denominator_safe(self):
        m = Metrics()
        assert m.precision == 0.0
        assert m.recall == 0.0
        assert m.f1 == 0.0


class TestEvaluate:
    def _gold(self):
        return [
            GoldLabel("T1", "CL-a", "SSE", True),
            GoldLabel("T1", "CL-b", "SSE", False),
            GoldLabel("T1", "CL-c", "GRI", True),
            GoldLabel("T2", "CL-d", "GRI", True),
        ]

    def test_perfect_prediction(self):
        pred = {("T1", "CL-a"), ("T1", "CL-c"), ("T2", "CL-d")}
        rep = evaluate(pred, self._gold())
        assert rep.overall.tp == 3
        assert rep.overall.fp == 0
        assert rep.overall.fn == 0
        assert rep.overall.precision == 1.0
        assert rep.overall.recall == 1.0

    def test_false_positive(self):
        pred = {("T1", "CL-a"), ("T1", "CL-b")}  # CL-b is not relevant
        rep = evaluate(pred, self._gold())
        assert rep.overall.fp == 1
        assert rep.overall.tp == 1

    def test_false_negative(self):
        pred = {("T1", "CL-a")}  # missed CL-c, CL-d
        rep = evaluate(pred, self._gold())
        assert rep.overall.fn == 2

    def test_per_family_breakdown(self):
        pred = {("T1", "CL-a"), ("T1", "CL-c")}
        rep = evaluate(pred, self._gold())
        d = rep.as_dict()
        assert "SSE" in d["per_source_family"]
        assert "GRI" in d["per_source_family"]
        # SSE: CL-a TP, CL-b TN -> precision 1, recall 1
        assert d["per_source_family"]["SSE"]["tp"] == 1
        # GRI: CL-c TP, CL-d FN -> recall 0.5
        assert d["per_source_family"]["GRI"]["fn"] == 1

    def test_per_family_visible_when_one_family_weak(self):
        # SSE perfect, GRI all missed — overall must not hide GRI.
        pred = {("T1", "CL-a")}
        rep = evaluate(pred, self._gold())
        assert rep.per_family["GRI"].recall == 0.0
        assert rep.per_family["SSE"].recall == 1.0

"""Tests for the reusable blind-generation QA gates.

Uses SYNTHETIC evidence + items only — no real source text, no client
data. Verifies the framework-agnostic invariants that any Topic + Source
-> questionnaire generation must satisfy, including the generic form of
the five regression guards.
"""

from backend.pipeline.blind_generation_qa import (
    SourceEvidence,
    topic_applicability_gate,
    evidence_directness,
    metric_exactness,
    traceability,
    run_all_gates,
)


def _ev(**kw):
    base = dict(source_id="S", framework="FW", primary_topic="T",
                metric_shape="n/a", quantitative_components=set())
    base.update(kw)
    return SourceEvidence(**base)


TOPIC_A = "topic_a"
TOPIC_B = "topic_b"


class TestTopicApplicabilityGate:
    def test_primary_topic_passes(self):
        ev = {"S1": _ev(source_id="S1", primary_topic=TOPIC_A)}
        assert topic_applicability_gate(TOPIC_A, ["S1"], ev) == []

    def test_non_primary_topic_flagged(self):
        # a source whose primary home is topic_b must not back a topic_a item
        ev = {"S1": _ev(source_id="S1", primary_topic=TOPIC_B)}
        findings = topic_applicability_gate(TOPIC_A, ["S1"], ev)
        assert any(f.code == "APPLIC_NOT_PRIMARY" for f in findings)

    def test_spanning_source_via_slash(self):
        # a genuinely spanning disclosure "topic_a/topic_b" is allowed for both
        ev = {"S1": _ev(source_id="S1", primary_topic=f"{TOPIC_A}/{TOPIC_B}")}
        assert topic_applicability_gate(TOPIC_A, ["S1"], ev) == []
        assert topic_applicability_gate(TOPIC_B, ["S1"], ev) == []

    def test_whitelist_allows_cross_topic(self):
        ev = {"S1": _ev(source_id="S1", primary_topic=TOPIC_B)}
        wl = {f"S1|{TOPIC_A}"}
        assert topic_applicability_gate(TOPIC_A, ["S1"], ev, wl) == []

    def test_unknown_source_flagged(self):
        findings = topic_applicability_gate(TOPIC_A, ["S_missing"], {})
        assert any(f.code == "APPLIC_UNKNOWN_SOURCE" for f in findings)


class TestEvidenceDirectness:
    def test_no_source_flagged(self):
        assert any(f.code == "DIRECT_NONE" for f in evidence_directness([]))

    def test_has_source_ok(self):
        assert evidence_directness(["S1"]) == []


class TestMetricExactness:
    def test_qualitative_source_cannot_back_kpi(self):
        # a purely qualitative source (no quantitative_components) must not
        # back a quantitative item -> guards qualitative->KPI fabrication
        ev = {"S1": _ev(source_id="S1", metric_shape="qualitative_process_description",
                        quantitative_components=set())}
        findings = metric_exactness("定量", "count", "件", ["S1"], ev)
        assert any(f.code == "METRIC_NO_QUANT_SOURCE" for f in findings)

    def test_percentage_source_backs_percentage(self):
        ev = {"S1": _ev(source_id="S1", metric_shape="percentage",
                        quantitative_components={"percentage"})}
        assert metric_exactness("定量", "percentage", "%", ["S1"], ev) == []

    def test_percentage_item_from_count_source_flagged(self):
        # percentage<->count drift: a count-only source can't back a percentage
        ev = {"S1": _ev(source_id="S1", metric_shape="count",
                        quantitative_components={"count"})}
        findings = metric_exactness("定量", "percentage", "%", ["S1"], ev)
        assert any(f.code == "METRIC_PCT_DRIFT" for f in findings)

    def test_compound_source_backs_its_component(self):
        # a compound source (qualitative + percentage) can back a percentage item
        ev = {"S1": _ev(source_id="S1", metric_shape="qual_plus_pct",
                        quantitative_components={"percentage"})}
        assert metric_exactness("定量", "percentage", "%", ["S1"], ev) == []

    def test_qualitative_item_with_metric_shape_flagged(self):
        ev = {"S1": _ev(source_id="S1")}
        findings = metric_exactness("定性", "percentage", "%", ["S1"], ev)
        assert any(f.code == "METRIC_QUAL_HAS_SHAPE" for f in findings)

    def test_count_source_backs_count_item(self):
        ev = {"S1": _ev(source_id="S1", metric_shape="count_plus_qualitative_response",
                        quantitative_components={"count"})}
        assert metric_exactness("定量", "count", "件", ["S1"], ev) == []


class TestTraceability:
    def test_missing_code_flagged(self):
        findings = traceability(["X"], available_codes=set())
        assert any(f.code == "TRACE_MISSING" for f in findings)

    def test_present_code_ok(self):
        assert traceability(["X"], available_codes={"X"}) == []


class TestRegressionInvariantsGeneric:
    """The five regression guards expressed as generic properties."""

    def test_complaint_mechanism_source_cannot_yield_rate_kpi(self):
        # Case 1: a mechanism/process source cannot back a rate KPI
        ev = {"MECH": _ev(source_id="MECH",
                          metric_shape="count_plus_qualitative_response",
                          quantitative_components={"count"})}
        # trying to make a "rate" from it -> no source defines "rate"
        findings = metric_exactness("定量", "rate", "%", ["MECH"], ev)
        assert any(f.code == "METRIC_NO_QUANT_SOURCE" for f in findings)

    def test_percentage_kpi_stays_percentage(self):
        # Case 2: a percentage source backs a percentage, not a count
        ev = {"PCT": _ev(source_id="PCT", metric_shape="percentage",
                         quantitative_components={"percentage"})}
        # count item from a percentage-only source -> not backed
        findings = metric_exactness("定量", "count", "件", ["PCT"], ev)
        assert any(f.code == "METRIC_NO_QUANT_SOURCE" for f in findings)

    def test_wrong_topic_source_excluded(self):
        # Cases 4 & 5: a source whose primary home is another topic is excluded
        ev = {"MAT": _ev(source_id="MAT", primary_topic="materials_circular_economy")}
        findings = topic_applicability_gate("chemical_safety", ["MAT"], ev)
        assert any(f.code == "APPLIC_NOT_PRIMARY" for f in findings)

    def test_full_run_clean_item_passes(self):
        ev = {"S1": _ev(source_id="S1", primary_topic=TOPIC_A, metric_shape="percentage",
                        quantitative_components={"percentage"})}
        items = [{"item_id": "I1", "topic": TOPIC_A, "kind_cn": "定量",
                  "metric_shape": "percentage", "unit": "%", "source_ids": ["S1"]}]
        findings = run_all_gates(items, ev, available_codes={"S1"})
        assert [f for f in findings if f.level == "ERROR"] == []

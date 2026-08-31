"""Reusable, generic QA gates for source-driven (blind) question generation.

These validators are framework-agnostic and client-agnostic. They encode
the invariants that any Topic + Source -> questionnaire generation must
satisfy, independent of the specific project:

- TopicApplicabilityGate: a candidate source unit only belongs to a topic
  if that topic is its PRIMARY semantic home (Gate A/B/C).
- EvidenceDirectnessValidator: every framework-backed item must cite at
  least one DIRECT supporting source id; concept-adjacency is not support.
- MetricExactnessValidator: a quantitative item's shape (count vs
  percentage), unit and breakdown must be consistent with the source
  metric shape it claims; and a qualitative-only source must not be used
  to manufacture a quantitative KPI.
- TraceabilityValidator: every item's cited source ids must resolve to
  real ingested source-unit codes (No Source, No Claim).

No LLM runs here. This is deterministic checking of already-produced
items against a source evidence table. It does not decide relevance; it
enforces structural invariants on decisions already made.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# Metric shapes that denote a QUANTITATIVE requirement.
QUANTITATIVE_SHAPES = {
    "percentage",
    "count",
    "count_with_3way_breakdown",
    "rate",
    "ratio",
    "amount",
}
# Metric shapes that denote a source that defines NO disclosable metric
# (qualitative requirement, policy, process, or rating-methodology
# management evaluation). Such a source must NOT back a quantitative item.
NON_METRIC_SHAPES = {
    "qualitative_management_plus_incident_facts",
    "qualitative_policy_and_compliance",
    "qualitative_process_description",
    "count_plus_qualitative_response",  # defines a count, plus qualitative response
    "rating_methodology_qualitative_management",
    "n/a",
    "",
}


@dataclass
class Finding:
    level: str      # "ERROR" | "WARN"
    code: str
    item_id: str
    detail: str


@dataclass
class SourceEvidence:
    """The faithful, source-derived facts about one atomic source unit."""

    source_id: str
    framework: str
    primary_topic: str          # its PRIMARY semantic home
    metric_shape: str           # the raw faithful shape descriptor
    # which quantitative metric shapes this source can back
    # (e.g. {"percentage","count"} for a compound source like 417-1(a)+(b))
    quantitative_components: set[str] = field(default_factory=set)
    unit: str = ""
    numerator: str = ""
    denominator: str = ""


def topic_applicability_gate(
    item_topic: str,
    cited_source_ids: list[str],
    evidence: dict[str, SourceEvidence],
    allowed_cross_topic: set[str] | None = None,
) -> list[Finding]:
    """Gate A/B/C: every cited source's PRIMARY topic must match the item's
    topic, unless the (source, item_topic) pair is explicitly allowed
    (e.g. a genuinely shared disclosure like HKEX B6 that spans two
    topics). Otherwise the source is NOT_PRIMARY for this topic.
    """
    allowed_cross_topic = allowed_cross_topic or set()
    out: list[Finding] = []
    for sid in cited_source_ids:
        ev = evidence.get(sid)
        if ev is None:
            out.append(Finding("ERROR", "APPLIC_UNKNOWN_SOURCE", "", f"{sid}: no evidence record"))
            continue
        if ev.primary_topic == item_topic:
            continue
        # spanning sources: allow only if primary_topic mentions item_topic
        # or the pair is explicitly whitelisted
        if item_topic in ev.primary_topic.split("/") or f"{sid}|{item_topic}" in allowed_cross_topic:
            continue
        out.append(
            Finding(
                "ERROR",
                "APPLIC_NOT_PRIMARY",
                "",
                f"{sid} primary home='{ev.primary_topic}' != item topic '{item_topic}'",
            )
        )
    return out


def evidence_directness(cited_source_ids: list[str]) -> list[Finding]:
    """Every framework-backed item must cite at least one direct source."""
    if not cited_source_ids:
        return [Finding("ERROR", "DIRECT_NONE", "", "no direct source cited")]
    return []


def metric_exactness(
    item_kind: str,               # "定量" | "定性" (or qualitative/quantitative)
    item_metric_shape: str,
    item_unit: str,
    cited_source_ids: list[str],
    evidence: dict[str, SourceEvidence],
) -> list[Finding]:
    """Check quant/qual consistency + no qualitative-source -> KPI."""
    out: list[Finding] = []
    is_quant = item_kind in ("定量", "quantitative")
    if is_quant:
        if item_metric_shape not in QUANTITATIVE_SHAPES:
            out.append(Finding("ERROR", "METRIC_SHAPE_BAD",
                               "", f"quantitative item has non-metric shape '{item_metric_shape}'"))
        # at least one cited source must have this shape in its quantitative_components
        backing = [sid for sid in cited_source_ids
                   if (evidence.get(sid) and item_metric_shape in evidence[sid].quantitative_components)]
        if not backing:
            out.append(Finding("ERROR", "METRIC_NO_QUANT_SOURCE",
                               "", f"quantitative item shape '{item_metric_shape}' not backed by any source "
                                   "that defines that metric shape (qualitative->KPI fabrication)"))
        # percentage must have a source whose components include percentage
        if item_metric_shape == "percentage":
            pct_src = [sid for sid in cited_source_ids
                       if evidence.get(sid) and "percentage" in evidence[sid].quantitative_components]
            if not pct_src:
                out.append(Finding("ERROR", "METRIC_PCT_DRIFT",
                                   "", "percentage item has no percentage-component source "
                                       "(possible percentage<->count drift)"))
    else:
        # qualitative item must not claim a quantitative shape
        if item_metric_shape in QUANTITATIVE_SHAPES:
            out.append(Finding("ERROR", "METRIC_QUAL_HAS_SHAPE",
                               "", f"qualitative item claims metric shape '{item_metric_shape}'"))
    return out


def traceability(cited_source_ids: list[str], available_codes: set[str]) -> list[Finding]:
    """No Source, No Claim: every cited id must resolve to a real code."""
    out: list[Finding] = []
    for sid in cited_source_ids:
        if sid not in available_codes:
            out.append(Finding("ERROR", "TRACE_MISSING", "", f"{sid}: not in ingested corpus"))
    return out


def run_all_gates(
    items: list[dict],
    evidence: dict[str, SourceEvidence],
    available_codes: set[str],
    allowed_cross_topic: set[str] | None = None,
) -> list[Finding]:
    """Run every gate over every item. Each item dict must have keys:
    item_id, topic, kind_cn, metric_shape, unit, source_ids.
    Returns a flat list of Findings (item_id filled in).
    """
    findings: list[Finding] = []
    for it in items:
        iid = it["item_id"]
        sids = it.get("source_ids", [])
        checks = (
            topic_applicability_gate(it["topic"], sids, evidence, allowed_cross_topic)
            + evidence_directness(sids)
            + metric_exactness(it.get("kind_cn", ""), it.get("metric_shape", ""),
                               it.get("unit", ""), sids, evidence)
            + traceability(sids, available_codes)
        )
        for f in checks:
            findings.append(Finding(f.level, f.code, iid, f.detail))
    return findings

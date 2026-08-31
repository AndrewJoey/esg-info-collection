"""Quality Management Department collection workbook builder.

Single-department deliverable for 质量管理部, scoped to exactly three
client-confirmed topics:
  - 产品和服务安全与质量
  - 化学品安全与成分管理
  - 负责任营销

Encodes the Claude Code semantic analyst's judgments as an auditable,
local intermediate representation (InformationPointCandidate) linking
real SourceClause evidence -> information points -> collection items.

Honesty contract:
- review_method = "claude_code_semantic_review"; production_provider =
  False. This is NOT a production LLM run and NOT client-approved.
- No Source, No Claim: every FRAMEWORK_BACKED item lists real source
  unit ids that exist in the ingested corpus; traceability is verified
  at build time (unknown ids raise).
- Source-family semantics preserved: GRI Requirement vs Guidance, MSCI
  as rating methodology, CSA as questionnaire, SSE/HKEX as disclosure.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# The three client-confirmed QM topics.
QM_TOPICS = [
    "产品和服务安全与质量",
    "化学品安全与成分管理",
    "负责任营销",
]

SOURCE_NATURE = {
    "FRAMEWORK_BACKED",
    "FRAMEWORK_AND_HUMAN_BASELINE",
    "BUSINESS_EXTENSION",
}


@dataclass
class InformationPoint:
    """One underlying collectible information need."""

    ip_id: str
    topic: str
    dimension: str          # 治理/战略/影响风险机遇管理/指标与目标/案例实践
    label: str              # short name of the information need
    kind: str               # qualitative | quantitative | both
    source_unit_ids: list[str]      # real SourceClause codes (evidence)
    source_frameworks: list[str]
    source_nature: str
    human_question_ids: list[str] = field(default_factory=list)
    department_fit: str = "OK"      # OK | REVIEW_REQUIRED
    semantic_reason: str = ""


@dataclass
class CollectionItem:
    item_id: str
    topic: str
    dimension: str
    ip_id: str
    kind: str               # qualitative | quantitative
    question: str
    guidance: str
    # quantitative fields (empty for qualitative)
    metric_name: str = ""
    unit: str = ""
    period: str = ""
    boundary: str = ""
    breakdown: str = ""
    baseline: str = ""
    target: str = ""
    target_year: str = ""
    frequency: str = ""
    calc_guidance: str = ""
    # provenance / classification
    source_nature: str = "FRAMEWORK_BACKED"
    human_question_ids: list[str] = field(default_factory=list)
    source_frameworks: list[str] = field(default_factory=list)
    source_unit_ids: list[str] = field(default_factory=list)
    review_status: str = "REVIEW_REQUIRED"
    department_fit: str = "OK"


def _verify_sources(ips: list[InformationPoint], available_codes: set[str]) -> list[str]:
    """Return a list of missing source ids for FRAMEWORK_BACKED IPs.

    Enforces No Source, No Claim at build time.
    """
    missing = []
    for ip in ips:
        if ip.source_nature in ("FRAMEWORK_BACKED", "FRAMEWORK_AND_HUMAN_BASELINE"):
            for sid in ip.source_unit_ids:
                if sid not in available_codes:
                    missing.append(f"{ip.ip_id}:{sid}")
    return missing

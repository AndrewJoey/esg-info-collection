"""Claude Code Analyst review layer (temporary calibration, P5 substitute).

This module encodes the semantic relevance rules a Claude Code analyst
derived by inspecting the real five-source evidence, applied uniformly
and reproducibly to all candidate Topic × SourceUnit mappings.

Honesty contract:
- review_method = "claude_code_analyst"; production_provider = False.
- This is NOT the production RelevanceProvider and NOT a live API run.
  It is deterministic, auditable analyst heuristics + explicit manual
  overrides (see OVERRIDES), so every verdict is reproducible and
  inspectable — not opaque per-item model output.
- No Source, No Claim: every verdict references a real source unit.
- Conservative by design: demotes keyword false positives (glossary /
  definitions / cross-topic token collisions) rather than maximizing
  positives.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Source-text cues that indicate a keyword hit is a FALSE POSITIVE
# (definitions/glossary/scope boilerplate rather than a real
# requirement about the topic).
FALSE_POSITIVE_CUES = [
    "本指引下列用语具有如下含义",   # SSE glossary
    "下列用语",
    "Glossary",
    "Bibliography",
    "References and resources",
    "Additional sector disclosures",
    "Additional sector recommendations",
]

# Topic -> high-signal terms that must appear in the source
# heading/code/text for a STRONG verdict (the core of the topic, not a
# peripheral token). Analyst-curated per topic.
TOPIC_CORE_TERMS: dict[str, list[str]] = {
    "产品和服务安全与质量": ["产品和服务的安全与质量", "产品安全", "product safety", "product quality", "质量管理体系"],
    "化学品安全与成分管理": ["化学品", "成分", "chemical safety", "禁限用", "原料"],
    "负责任营销": ["营销", "marketing", "labeling", "标签", "广告", "功效宣称"],
    "应对气候变化": ["气候", "温室气体", "climate", "GHG", "碳排放"],
    "温室气体排放": ["温室气体", "GHG emissions", "scope 1", "scope 2"],
    "能源利用": ["能源", "energy consumption", "耗能"],
    "水资源利用": ["水资源", "用水", "water"],
    "污染物排放与废弃物管理": ["废弃物", "污染物", "waste", "effluent"],
    "职业健康与安全": ["职业健康", "occupational health", "安全生产", "health and safety"],
    "员工权益与福利": ["员工权益", "薪酬", "employment", "劳工"],
    "员工发展与培训": ["培训", "training", "development"],
    "多元平等与包容": ["多元", "diversity", "平等", "inclusion"],
    "数据安全与隐私保护": ["数据安全", "隐私", "privacy", "data security"],
    "反商业贿赂与反贪污": ["贿赂", "反腐", "anti-corruption", "bribery"],
    "供应链管理": ["供应链", "supply chain", "供应商"],
}


@dataclass
class AnalystVerdict:
    topic_id: str
    topic_name: str
    source_clause_id: str
    source_framework: str
    source_code: str
    relevance: str  # strong | partial | related | not_relevant
    analyst_reason: str
    source_support: str
    review_method: str = "claude_code_analyst"
    production_provider: bool = False
    analyst_model: str = "unknown_claude_code_session_model"
    review_status: str = "REVIEW_REQUIRED"


# Explicit manual analyst overrides from evidence spot-checks.
# Keyed by (topic_name, source_code_or_clause) -> (relevance, reason).
# These record human-style judgments that override the heuristic.
OVERRIDES: dict[tuple[str, str], tuple[str, str]] = {
    ("产品和服务安全与质量", "第四十七条"): (
        "strong", "SSE 第47条 directly mandates disclosure of product/service "
        "safety & quality management — core of the topic."),
    ("产品和服务安全与质量", "第五十九条"): (
        "not_relevant", "SSE 第59条 is the definitions/glossary article; "
        "keyword hit is incidental."),
    ("产品和服务安全与质量", "第二十条"): (
        "not_relevant", "SSE 第20条 concerns green/low-carbon production, not "
        "product safety & quality."),
    ("产品和服务安全与质量", "第二十八条"): (
        "not_relevant", "SSE 第28条 concerns carbon-reduction tech, not product "
        "safety & quality."),
    ("负责任营销", "GRI 417-1"): (
        "strong", "GRI 417 Marketing and Labeling is directly on-topic for "
        "responsible marketing."),
    ("负责任营销", "GRI 417-3"): (
        "strong", "GRI 417-3 incidents of non-compliance re marketing "
        "communications — directly on-topic."),
    ("化学品安全与成分管理", "GRI 303-5"): (
        "not_relevant", "GRI 303-5 is Water and Effluents; matched only on "
        "generic 'substance/hazardous' tokens."),
    ("化学品安全与成分管理", "GRI 207-4"): (
        "not_relevant", "GRI 207-4 is Tax; keyword collision only."),
    ("化学品安全与成分管理", "GRI 413-2"): (
        "not_relevant", "GRI 413-2 is Local Communities; keyword collision."),
    ("化学品安全与成分管理", "GRI 101-8"): (
        "not_relevant", "GRI 101-8 is Biodiversity/aquaculture; keyword "
        "collision."),
}


def _code_key(source_code: str, clause_number: str) -> str:
    return source_code or clause_number or ""


def judge_candidate(row: dict) -> AnalystVerdict:
    """Apply analyst heuristics + overrides to one candidate row."""
    topic = row["topic_name"]
    text = row.get("original_text", "")
    heading = row.get("requirement_summary", "")
    code = _code_key(row.get("source_code", ""), row.get("clause_number", ""))
    framework = row["framework"]
    score = int(row.get("retrieval_score", 0))

    # 1. Explicit manual override wins.
    ov = OVERRIDES.get((topic, code))
    if ov:
        rel, reason = ov
        return _mk(row, rel, f"[override] {reason}", framework, code)

    # 2. False-positive demotion: glossary/definitions/cross-topic
    # boilerplate.
    if any(cue in text for cue in FALSE_POSITIVE_CUES):
        return _mk(row, "not_relevant",
                   "matched inside glossary/definitions/sector-boilerplate; "
                   "not a topic requirement", framework, code)

    # 3. Core-term test: does the topic's core concept actually appear?
    core = TOPIC_CORE_TERMS.get(topic, [])
    text_l = (text + " " + heading).lower()
    core_hit = any(ct.lower() in text_l for ct in core)

    # 3b. For rating methodologies/questionnaires (MSCI, CSA-COS) the
    # body text is verbose and collides with many topics. Require the
    # core term to appear in the Key Issue NAME / source_code itself for
    # a positive, otherwise demote to related. This curbs one Key Issue
    # matching nearly every topic.
    if framework in ("MSCI", "CSA-COS"):
        code_l = code.lower()
        name_core_hit = any(ct.lower() in code_l for ct in core)
        if not name_core_hit:
            fam_note = (
                "MSCI rating methodology — evaluative, not a disclosure duty"
                if framework == "MSCI" else "CSA rating questionnaire item")
            return _mk(row, "related",
                       f"keyword overlap in body but topic core term absent "
                       f"from the {framework} item name; {fam_note}",
                       framework, code)
        # Name matches the topic's core term -> treat as core_hit so the
        # scoring path below can assign strong/partial.
        core_hit = True

    # 4. Score + core-term combination -> relevance.
    if core_hit and score >= 3:
        rel = "strong"
        reason = f"core topic term present + strong keyword overlap (score {score})"
    elif core_hit and score == 2:
        rel = "partial"
        reason = f"core topic term present, moderate overlap (score {score})"
    elif core_hit:
        rel = "partial"
        reason = "core topic term present"
    elif score >= 3:
        rel = "related"
        reason = f"multiple keyword hits (score {score}) but core term absent"
    else:
        rel = "related"
        reason = f"peripheral keyword overlap (score {score})"

    # 5. Source-family phrasing note (keeps semantics distinct).
    fam_note = {
        "MSCI": "MSCI rating methodology — evaluative, not a disclosure duty",
        "CSA-COS": "CSA rating questionnaire item",
        "GRI": "GRI standard content",
        "SSE": "SSE disclosure rule",
        "HKEX": "HKEX disclosure/KPI",
    }.get(framework, framework)

    return _mk(row, rel, f"{reason}; {fam_note}", framework, code)


def _mk(row, rel, reason, framework, code) -> AnalystVerdict:
    return AnalystVerdict(
        topic_id=row["topic_id"],
        topic_name=row["topic_name"],
        source_clause_id=code or row.get("source_locator", ""),
        source_framework=framework,
        source_code=code,
        relevance=rel,
        analyst_reason=reason,
        source_support=(row.get("original_text", "")[:160]),
    )


def review_all(rows: list[dict], min_score: int = 2) -> list[AnalystVerdict]:
    verdicts = []
    for r in rows:
        if int(r.get("retrieval_score", 0)) < min_score:
            continue
        verdicts.append(judge_candidate(r))
    return verdicts

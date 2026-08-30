#!/usr/bin/env python3
"""P4/P5 — Deterministic candidate retrieval + rule-based mapping.

Given project topics and ingested SourceClauses, produce Topic × Source
candidate mappings using deterministic keyword / token overlap scoring.

CRITICAL — Retrieval != Analysis, No Source No Claim:
- This module produces CANDIDATES only. It does NOT decide truth.
- No LLM runs here. Every mapping is ``decision_origin = RULE`` and
  ``review_status = REVIEW_REQUIRED``; none is APPROVED.
- Every mapping references a real SourceClause id (No Source, No Claim).
- Genuine AI relevance judgment (P5) requires a configured LLM provider,
  which is NOT available in this environment. When a provider is
  configured, an AI layer can re-score these candidates and set
  ``decision_origin = AI`` with confidence — without changing the
  provenance contract.

This is deterministic scaffolding, honestly labeled, not a substitute
for human/AI relevance judgment.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

# Topic-keyword lexicon: maps project topic names to Chinese keyword
# cues for candidate retrieval. This is deterministic retrieval
# vocabulary, NOT a relevance verdict. Extendable per project.
TOPIC_KEYWORDS: dict[str, list[str]] = {
    "应对气候变化": ["气候", "温室", "碳", "排放", "减排", "气候相关", "能源", "碳中和"],
    "温室气体排放": ["温室", "碳排放", "排放", "范围一", "范围二", "碳"],
    "能源利用": ["能源", "电", "用电", "耗能", "能耗", "可再生"],
    "水资源利用": ["水", "用水", "耗水", "水资源", "排水"],
    "污染物排放与废弃物管理": ["废弃物", "排放", "污染", "废气", "废水", "有害"],
    "资源利用与循环经济": ["资源", "循环", "回收", "再利用", "材料"],
    "绿色包装": ["包装", "包材", "材料"],
    "化学品安全与成分管理": ["化学", "成分", "有害物质", "安全"],
    "生物多样性保护": ["生物多样性", "生态", "土地"],
    "产品和服务安全与质量": ["产品", "质量", "安全", "服务"],
    "产品环境影响与评价": ["产品", "环境影响", "评价", "生命周期"],
    "绿色产品设计": ["绿色", "产品", "设计", "环保"],
    "产品研发创新": ["研发", "创新", "技术"],
    "供应链管理": ["供应链", "供应商", "采购"],
    "绿色采购": ["采购", "绿色", "供应商"],
    "员工权益与福利": ["员工", "权益", "福利", "薪酬", "雇佣"],
    "职业健康与安全": ["健康", "安全", "职业", "工伤"],
    "员工发展与培训": ["培训", "发展", "员工", "技能"],
    "多元平等与包容": ["多元", "平等", "包容", "性别", "歧视"],
    "负责任营销": ["营销", "广告", "标签", "宣传", "客户"],
    "数据安全与隐私保护": ["数据", "隐私", "信息安全", "个人信息"],
    "反商业贿赂与反贪污": ["贿赂", "贪污", "反腐", "廉洁"],
    "反不正当竞争": ["竞争", "垄断", "不正当"],
    "知识产权保护": ["知识产权", "专利", "商标", "版权"],
    "社区发展与社会公益": ["社区", "公益", "慈善", "捐赠"],
    "利益相关方沟通": ["利益相关", "持份者", "沟通", "参与"],
    "文化传承与保护": ["文化", "传承", "非遗"],
    "数字化建设": ["数字化", "信息化", "数字"],
    "绿色消费倡导": ["绿色消费", "消费者", "倡导"],
    "供应链管理": ["供应链", "供应商", "采购"],
}


# English keyword aliases for the same topics, to retrieve against
# English-language sources (GRI, MSCI, CSA-COS). Deterministic retrieval
# vocabulary only — not a relevance verdict.
TOPIC_KEYWORDS_EN: dict[str, list[str]] = {
    "应对气候变化": ["climate", "greenhouse", "GHG", "carbon", "emission", "net-zero"],
    "温室气体排放": ["greenhouse", "GHG", "scope 1", "scope 2", "scope 3", "emission", "carbon"],
    "能源利用": ["energy", "electricity", "fuel", "renewable", "consumption"],
    "水资源利用": ["water", "effluent", "withdrawal", "discharge"],
    "污染物排放与废弃物管理": ["waste", "effluent", "emission", "pollutant", "hazardous", "toxic"],
    "资源利用与循环经济": ["material", "circular", "recycl", "resource", "reuse"],
    "绿色包装": ["packaging", "material"],
    "化学品安全与成分管理": ["chemical", "substance", "hazardous", "safety"],
    "生物多样性保护": ["biodiversity", "land use", "ecosystem"],
    "产品和服务安全与质量": ["product safety", "quality", "customer health", "product responsibility"],
    "产品环境影响与评价": ["product", "life cycle", "environmental impact", "carbon footprint"],
    "绿色产品设计": ["product", "design", "eco", "green"],
    "产品研发创新": ["innovation", "research", "clean tech", "opportunit"],
    "供应链管理": ["supply chain", "supplier", "procurement", "sourcing"],
    "绿色采购": ["procurement", "supplier", "sourcing"],
    "员工权益与福利": ["employment", "labor", "compensation", "benefit", "wage", "employee"],
    "职业健康与安全": ["health and safety", "occupational", "injury", "safety"],
    "员工发展与培训": ["training", "education", "development", "employee"],
    "多元平等与包容": ["diversity", "equal", "inclusion", "gender", "discrimination"],
    "负责任营销": ["marketing", "labeling", "advertising", "customer"],
    "数据安全与隐私保护": ["privacy", "data security", "customer privacy", "data"],
    "反商业贿赂与反贪污": ["anti-corruption", "bribery", "corruption"],
    "反不正当竞争": ["anti-competitive", "competition", "antitrust"],
    "知识产权保护": ["intellectual property", "patent", "trademark"],
    "社区发展与社会公益": ["community", "local communities", "philanthrop", "social"],
    "利益相关方沟通": ["stakeholder", "engagement", "communication"],
    "文化传承与保护": ["culture", "heritage", "indigenous"],
    "数字化建设": ["digital", "technology", "digitization"],
    "绿色消费倡导": ["consumer", "green consumption", "sustainable consumption"],
}


@dataclass
class Candidate:
    topic_id: str
    topic_name: str
    clause_id: str
    framework: str
    source_code: str | None
    clause_number: str | None
    score: int
    matched_keywords: list[str] = field(default_factory=list)


def load_clauses(paths: list[Path]) -> list[dict]:
    clauses: list[dict] = []
    for p in paths:
        if not p.is_file():
            continue
        for line in p.open(encoding="utf-8"):
            line = line.strip()
            if line:
                clauses.append(json.loads(line))
    return clauses


def retrieve_candidates(
    topics: list[dict],
    clauses: list[dict],
    framework_of: dict[str, str],
    min_score: int = 1,
) -> list[Candidate]:
    """Score each (topic, clause) by keyword hits in original_text.

    ``framework_of`` maps document_id -> framework code.
    Returns candidates with score >= min_score.
    """
    candidates: list[Candidate] = []
    for topic in topics:
        name = topic["topic_name"]
        zh_keywords = TOPIC_KEYWORDS.get(name, [])
        en_keywords = TOPIC_KEYWORDS_EN.get(name, [])
        if not zh_keywords and not en_keywords:
            continue
        for clause in clauses:
            text = clause.get("original_text", "")
            text_lower = text.lower()
            hits = [kw for kw in zh_keywords if kw in text]
            hits += [kw for kw in en_keywords if kw.lower() in text_lower]
            if len(hits) >= min_score:
                candidates.append(
                    Candidate(
                        topic_id=topic["topic_id"],
                        topic_name=name,
                        clause_id=clause["clause_id"],
                        framework=framework_of.get(clause["document_id"], "?"),
                        source_code=clause.get("source_code"),
                        clause_number=clause.get("clause_number"),
                        score=len(hits),
                        matched_keywords=hits,
                    )
                )
    candidates.sort(key=lambda c: (c.topic_name, -c.score))
    return candidates


def candidate_to_mapping_dict(c: Candidate) -> dict:
    """Shape a candidate as a review-ready mapping record.

    decision_origin=RULE, review_status=REVIEW_REQUIRED: this is a
    retrieval candidate, not an approved or AI-judged relevance verdict.
    """
    return {
        "topic_id": c.topic_id,
        "topic_name": c.topic_name,
        "clause_id": c.clause_id,
        "framework": c.framework,
        "source_code": c.source_code,
        "clause_number": c.clause_number,
        "retrieval_score": c.score,
        "matched_keywords": c.matched_keywords,
        "decision_origin": "RULE",
        "relevance": "related",  # provisional retrieval bucket, not a verdict
        "review_status": "REVIEW_REQUIRED",
        "ai_reason": None,
        "ai_confidence": None,
    }

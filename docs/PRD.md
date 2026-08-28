# ESG 标准对标与信息收集工具 PRD

**文档版本**：v1.0  
**状态**：Development Baseline  
**适用阶段**：花西子 Pilot V0 → V2  
**主要使用者**：ESG 咨询顾问、知识库管理员、开发/AI Agent  
**开发原则**：先验证核心链路，再逐步产品化；任何新功能不得破坏来源可追溯性。

---

## 1. 文档目的

本 PRD 用于指导 ESG 标准对标与信息收集工具的持续开发，尤其适合由 Codex、Claude Code 等 AI Agent 持续迭代。

本文件同时承担以下作用：

1. 定义产品边界与阶段目标；
2. 统一核心业务对象和数据模型；
3. 明确 AI、规则、数据库和人工审核的职责边界；
4. 明确每个版本的功能、输入、输出和验收标准；
5. 作为开发 Agent 的长期上下文与变更基线；
6. 避免开发过程中出现“为了做功能而重构业务逻辑”的漂移。

> 核心原则：**标准原文是事实层，结构化 Requirement 是知识层，AI/规则是处理层，项目和信息收集表是应用层。**

---

# 2. 产品背景

ESG 咨询项目中，信息收集表通常不是凭空设计，而是需要回应多种来源：

- 交易所披露要求；
- GRI、ISSB、SASB 等披露框架；
- MSCI、CSA 等评级或评估要求；
- 同行业企业实践；
- 客户自身历史披露和管理实践。

当前人工流程存在以下问题：

- 同一标准被多个项目反复阅读；
- 标准要求和客户议题之间需要大量人工映射；
- 不同框架表达不同但要求可能重合；
- AI 直接读取整份 PDF 容易出现漏项、错引和来源不准确；
- 信息收集表需要按客户议题和部门重新组织；
- 项目完成后，研究成果很难沉淀成可复用资产。

已有 MUJI Benchmarking Beta 已验证一条可工作的基础链路：

`Source → Retrieval → Agent 判断 → Evidence → Review → Export`

新工具不从零开始，而是在原有 Evidence-first 思路上，重点补齐：

`Framework Clause → Topic Mapping → Requirement Mapping → Source Traceability → Client-facing Question`

---

# 3. 产品目标

## 3.1 近期目标：花西子 Pilot

第一阶段只验证一件事：

> **给定一份企业 ESG 议题清单，以及上交所、港交所两个披露框架，系统能否准确、完整、可追溯地识别每个议题对应的披露要求。**

第一阶段不以“生成最终信息收集表”为主要成功标准。

### Pilot V0 输入

- 花西子总 ESG 议题清单 / 二级议题清单；
- 港交所披露要求原文；
- 上交所披露要求原文。

### Pilot V0 输出

一张“议题 × 框架披露要求对标底稿”，至少包括：

- 议题；
- Framework；
- Framework Version；
- Section / Chapter；
- Clause；
- 原始披露要求；
- 简要要求摘要；
- 定性/定量；
- 来源定位；
- Review Status。

### Pilot V0 成功标准

重点验证：

1. Precision：召回内容是否真的相关；
2. Recall：框架相关要求是否存在漏项；
3. Traceability：每项结果能否回到原文；
4. Reproducibility：同一输入重复运行是否保持稳定结构和来源。

---

## 3.2 中期目标

在 V0 可靠后，实现：

`Topic → Framework Requirement → Department → Question → Excel`

系统根据项目中已经确认的“部门 × 议题”关系，将框架要求转化为面向客户填写的信息收集问题。

---

## 3.3 长期目标

形成可复用的 ESG Knowledge Platform，支持：

- ESG 标准知识库；
- 对标研究；
- 信息收集表；
- ESG KPI Library；
- Peer Benchmark；
- Gap Analysis；
- Rating Improvement；
- ESG Copilot / Knowledge QA。

长期目标不属于当前 Pilot 的交付承诺。

---

# 4. 非目标（当前明确不做）

以下能力在 Pilot V0 中明确不作为开发目标：

- 自动双重重要性判断；
- L1/L2/L3 复杂颗粒度引擎；
- AI 自动推测部门和议题归属；
- 客户在线填写 Portal；
- 自动写完整 ESG 报告；
- 自动计算 Scope 1/2/3；
- 自动抽取所有计算公式和注释；
- 自动实时监控所有框架更新；
- SaaS 计费；
- 多租户企业版权限体系；
- 大规模 autonomous agent；
- 全部 ESG 标准一次性入库；
- 完整知识图谱数据库。

除非 PRD 版本正式升级，否则 AI 开发 Agent 不得自行把以上内容扩入当前 Scope。

---

# 5. 用户与角色

## 5.1 Consultant

主要行为：

- 创建项目；
- 导入/选择企业议题；
- 选择框架；
- 查看 AI 召回要求；
- 审核、编辑、删除 Mapping；
- 查看原文；
- 导出对标底稿；
- 后续生成部门信息收集表。

## 5.2 Knowledge Reviewer

主要行为：

- 审核框架结构化结果；
- 修正 Clause；
- 确认 Topic Mapping；
- 确认框架版本；
- 将结果标记为 Approved。

Pilot 阶段 Consultant 与 Knowledge Reviewer 可以是同一人。

## 5.3 System / AI Agent

负责：

- 文档解析；
- 结构化抽取；
- 候选检索；
- Topic 相关性判断；
- 摘要；
- 定性/定量识别；
- QA 辅助；
- 后续问题生成。

AI 无权修改原始 Source Text。

---

# 6. 产品核心原则

## 6.1 Evidence First

任何对标结论必须有来源。

至少能够保存：

- source document；
- framework；
- version；
- chapter / section；
- clause；
- original text；
- page（如可靠）；
- source URL / file reference。

## 6.2 No Source, No Claim

没有明确 Source 的内容不得被系统标记为“框架要求”。

## 6.3 Raw ≠ Reviewed

AI 输出默认是 Draft。

只有经过人工确认后才能进入 Approved 数据集。

## 6.4 Retrieval ≠ Analysis

召回层只负责“找候选”。

是否真正相关由 AI 语义判断 + 人工 Review 决定。

## 6.5 原始层不合并

Raw Framework Clause 永远保持原始来源结构。

例如多个框架都要求 Scope 1：

- HKEX Clause A；
- SSE Clause B；

必须分别存在。

后续可以在 Normalized Layer 映射到同一 Canonical Requirement，但不能删除或覆盖原始条目。

## 6.6 AI Proposes, Human Publishes

AI 可以：

- 推荐；
- 分类；
- 摘要；
- 判断相关性。

但 Pilot 阶段人工审核是正式发布的必要条件。

---

# 7. 核心业务链路

## 7.1 V0 主链路

```text
Framework Document
        ↓
Document Parse
        ↓
Raw Clause / Requirement Extraction
        ↓
Framework Clause Database
        ↓
Company Topic List
        ↓
Candidate Retrieval
        ↓
AI Relevance Judgment
        ↓
Topic ↔ Clause Mapping Draft
        ↓
Human Review
        ↓
Approved Mapping
        ↓
Benchmark Excel
```

## 7.2 V1 主链路

```text
Approved Topic ↔ Clause Mapping
        ↓
Normalize Requirements
        ↓
Department ↔ Topic Mapping（人工输入）
        ↓
Question Transformation
        ↓
Qualitative / Quantitative Split
        ↓
Human Review
        ↓
Client Information Collection Excel
```

---

# 8. 数据层设计

## 8.1 SourceDocument

代表一个原始标准文件。

建议字段：

```yaml
id: UUID
framework_id: string
document_name: string
publisher: string
version: string
publication_date: date|null
effective_date: date|null
language: string
source_url: string|null
local_file_path: string|null
file_hash: string
parser_version: string|null
status: INGESTED|PARSED|REVIEW_REQUIRED|APPROVED|DEPRECATED
created_at: datetime
updated_at: datetime
```

要求：

- `file_hash` 必须存在；
- 新版本不得覆盖旧版本；
- 同一 Framework 可以存在多个 SourceDocument Version。

---

## 8.2 SourceClause

代表标准中的最小可引用要求单元。

```yaml
id: UUID
document_id: UUID
framework_id: string
section_path: string|null
clause_no: string|null
title: string|null
original_text: text
page_pdf: integer|null
page_printed: string|null
bbox: json|null
requirement_type: QUALITATIVE|QUANTITATIVE|MIXED|UNKNOWN
pillar: GOVERNANCE|STRATEGY|RISK_IMPACT|METRICS_TARGETS|OTHER|null
source_location_display: string
extraction_method: PARSER|AI|MANUAL
extraction_confidence: float|null
review_status: DRAFT|REVIEWED|APPROVED|REJECTED
created_at: datetime
updated_at: datetime
```

### 关于页码

PDF 实际页码可能与印刷页码不一致。

因此：

- `page_pdf` 保存 PDF 物理页；
- `page_printed` 如能识别则单独保存；
- `clause_no + section_path + original_text` 的优先级高于单独页码。

---

## 8.3 Topic

Pilot 阶段 Topic 由项目提供，不由系统自动创造。

```yaml
id: UUID
project_id: UUID
level_1_name: string|null
level_2_name: string
code: string|null
description: text|null
status: ACTIVE|INACTIVE
```

第一阶段不得自行对企业 Topic 进行合并或重命名。

---

## 8.4 TopicClauseMapping

这是 Pilot V0 的核心表。

```yaml
id: UUID
project_id: UUID
topic_id: UUID
clause_id: UUID
relevance: STRONG|MEDIUM|WEAK|NOT_RELEVANT
ai_reason: text|null
ai_confidence: float|null
decision_origin: AI|HUMAN|RULE
review_status: DRAFT|APPROVED|REJECTED
reviewer: string|null
reviewed_at: datetime|null
notes: text|null
```

Pilot 正式导出默认只使用 `APPROVED` Mapping。

---

## 8.5 CanonicalRequirement（V1 预留）

V0 可以不强制实施，但 Schema 应预留。

```yaml
id: UUID
canonical_name: string
description: text|null
requirement_type: QUALITATIVE|QUANTITATIVE|MIXED
definition: text|null
unit: string|null
calculation_formula: text|null
guidance: text|null
```

用途：

将不同来源但含义相近的 Clause 映射为统一 Requirement。

注意：Canonical Requirement 不替代 SourceClause。

---

## 8.6 Department（V1）

```yaml
id: UUID
project_id: UUID
name: string
description: text|null
```

---

## 8.7 DepartmentTopicMapping（V1）

部门与议题的关系由项目团队确认后录入。

```yaml
id: UUID
department_id: UUID
topic_id: UUID
relation: PRIMARY|SUPPORTING|GENERAL
source: HUMAN_CONFIRMED
```

当前版本不得使用 AI 自动创建正式 DepartmentTopicMapping。

---

## 8.8 Question（V1）

```yaml
id: UUID
project_id: UUID
department_id: UUID
topic_id: UUID
canonical_requirement_id: UUID|null
question_no: string|null
dimension: string|null
question_type: QUALITATIVE|QUANTITATIVE
question_text: text
guidance: text|null
unit: string|null
formula: text|null
expected_evidence: text|null
source_mapping_ids: UUID[]
review_status: DRAFT|APPROVED|REJECTED
```

---

# 9. Framework 数据入库要求

## 9.1 第一批 Framework

Pilot：

1. 港交所相关 ESG / Sustainability Disclosure Requirements；
2. 上交所相关可持续发展报告披露要求。

实际文件版本以项目团队提供的原文为准。

系统不得使用模型记忆代替项目提供的正式文件。

## 9.2 解析顺序

优先级：

1. 官方机器可读结构；
2. HTML / DOCX；
3. 带文字层 PDF；
4. 扫描 PDF → OCR / Vision Fallback。

## 9.3 Clause 拆分原则

优先按照：

- 编号；
- 标题；
- 列表项；
- 明确 disclosure requirement；

拆分。

不允许仅按固定 token 长度切 Chunk 作为正式 Clause。

## 9.4 混合条款

如果一个 Clause 中同时存在多个独立披露要求：

- `SourceClause` 可以保留完整原文；
- 可额外生成 `ClauseItem` 子项（后续版本）；
- V0 如未实现 ClauseItem，则在 Summary 中明确多要求，不得任意丢弃其中一项。

---

# 10. Topic → Framework Requirement 检索逻辑

## 10.1 检索方式

推荐 Hybrid Retrieval：

```text
Exact / Keyword Retrieval
+
Semantic Retrieval
+
Framework Metadata Filter
```

## 10.2 检索不得直接输出最终结论

检索阶段输出：

`Candidate Clauses`

AI 进行第二层判断：

- 是否真正回应 Topic；
- 是直接要求还是仅弱相关；
- 是否应保留。

## 10.3 AI 相关性输出 Schema

```json
{
  "topic_id": "...",
  "clause_id": "...",
  "relevance": "STRONG",
  "reason": "...",
  "confidence": 0.91
}
```

不得返回没有 `clause_id` 的 Mapping。

---

# 11. AI 能力设计

## 11.1 V0 必须能力

### AI-01 Clause Structuring

输入：原始标准章节 / Clause。  
输出：结构化 Clause Metadata。

必须保留原文，不得改写 `original_text`。

### AI-02 Topic Relevance Classification

输入：

- Topic 名称；
- Topic 描述（如有）；
- Candidate Clause。

输出：

- relevance；
- reason；
- confidence。

### AI-03 Requirement Summary

将标准要求转换成一句内部可读的中文摘要。

要求：

- 不得添加原文没有的义务；
- 不得删除影响实质的限定条件；
- Summary 与 Original Text 分栏保存。

### AI-04 QA Assistant

检查：

- Mapping 是否存在明显错配；
- 是否出现重复 Clause；
- 是否存在无 Source 的结果；
- 是否有结构字段缺失。

---

## 11.2 V1 能力

### AI-05 Canonical Requirement Recommendation

推荐不同框架 Clause 是否可以映射到同一 Requirement。

只产生 Draft，不自动合并原始 Source。

### AI-06 Question Transformation

输入：

- Topic；
- Requirement；
- Source；
- Department；
- Question Type。

输出：

- 客户可理解的问题；
- 填写说明；
- 单位 / Formula（如已有）。

---

# 12. AI Prompt 与结构化输出要求

所有生产 AI 调用应满足：

1. 使用固定任务 Prompt；
2. Prompt 有 version；
3. 输出符合 JSON Schema / Pydantic Schema；
4. Schema validation 失败自动重试或进入失败队列；
5. 不得将自由文本直接写入正式数据库核心字段；
6. 每次调用保留：
   - model；
   - prompt_version；
   - input IDs；
   - output；
   - latency；
   - token usage；
   - error；
   - review result。

---

# 13. 信息收集表设计（V1）

V1 输出建议至少包含：

## Sheet 01：填写说明

- 项目说明；
- 填写规则；
- 时间范围；
- 数据口径；
- 附件要求。

## Sheet 02：定性信息

建议字段：

- 议题；
- 维度；
- 问题编号；
- 问题；
- 填写说明；
- 客户填写内容；
- 是否有附件；
- 信息提供人；
- 备注。

## Sheet 03：定量数据

建议字段：

- 议题；
- 指标名称；
- 问题编号；
- 数据要求；
- 单位；
- 计算说明；
- 数据期间；
- 客户填写；
- 信息提供人；
- 附件；
- 备注。

## Internal View

内部版额外保留：

- Framework；
- Clause；
- Source Text；
- Mapping ID；
- Review Status。

Client View 默认隐藏以上内部 Source 字段。

---

# 14. 四支柱处理原则

会议中对“四支柱是否作为最终表格固定维度”尚未完全确定，因此本 PRD 规定：

- V0 不依赖四支柱；
- V1 Question Schema 中保留 `dimension` 字段；
- 可选值包括 Governance / Strategy / Risk & Impact Management / Metrics & Targets / Topic-specific；
- 是否强制展示由项目配置决定；
- 不得把所有专项要求机械塞入四支柱而造成语义失真。

---

# 15. Scope 1/2/3 特殊规则（V1+）

标准可能要求披露 Scope 1 / 2 / 3，但咨询项目可能需要客户提供活动数据而非最终排放值。

因此系统后续需要支持：

```text
Framework Requirement
        ↓
Calculation Requirement
        ↓
Activity Data Request
```

例如：

Scope 1 排放要求可转换为：

- 天然气使用量；
- 汽油使用量；
- 柴油使用量；
- 制冷剂补充量；
- 其他直接燃烧数据。

该逻辑暂不属于 V0。

---

# 16. Formula / Definition / Guidance

数据库 Schema 应预留：

- definition；
- calculation_formula；
- guidance；
- unit。

但 Pilot V0 不要求 AI 自动完整抽取。

推荐流程：

1. AI 提供初步候选；
2. 人工 Review 时补充必要公式；
3. 一旦 Approved 后作为知识资产长期复用。

---

# 17. 页面与交互设计

Pilot 不要求高保真 UI，但系统逻辑至少应支持以下页面/视图。

## 17.1 Project Setup

字段：

- Project Name；
- Client Name；
- Selected Frameworks；
- Topic List Import；
- Status。

## 17.2 Framework Library

展示：

- Framework；
- Version；
- Document；
- Status；
- Clause Count。

## 17.3 Clause Review

左右布局：

左侧：Source Document / Context。  
右侧：结构化 Clause。

操作：

- Approve；
- Edit Metadata；
- Reject。

原文正文只读。

## 17.4 Topic Mapping Workspace

按 Topic 展示：

- HKEX Candidate Clauses；
- SSE Candidate Clauses；
- Relevance；
- AI Reason；
- Original Text；
- Source Location。

操作：

- Approve；
- Reject；
- Change Relevance；
- Add Missing Clause；
- Note。

## 17.5 Export

V0：

- Benchmark Excel；
- CSV / JSON 可选。

V1：

- Internal Questionnaire；
- Client Questionnaire。

---

# 18. V0 Excel 输出 Schema

建议最终底稿字段顺序：

1. 一级议题；
2. 二级议题；
3. Framework；
4. Framework Version；
5. Section / Chapter；
6. Clause No.；
7. Requirement Summary；
8. Original Requirement；
9. Type（定性/定量/混合）；
10. Pillar（如适用）；
11. Source Location；
12. Source File；
13. Source URL；
14. AI Relevance；
15. Review Status；
16. Reviewer Note。

---

# 19. 状态机

## 19.1 SourceDocument

```text
INGESTED
→ PARSED
→ REVIEW_REQUIRED
→ APPROVED
→ DEPRECATED
```

## 19.2 SourceClause

```text
DRAFT
→ REVIEWED
→ APPROVED
or
→ REJECTED
```

## 19.3 TopicClauseMapping

```text
AI_DRAFT
→ APPROVED
or
→ REJECTED
```

不得物理删除 Approved Record；错误应通过状态或新 Version 修正。

---

# 20. 版本与审计

必须记录：

- Framework Version；
- Source File Hash；
- Parser Version；
- Schema Version；
- Model；
- Prompt Version；
- Review User；
- Review Time；
- Export Snapshot ID。

任何正式 Excel 导出都应形成 Snapshot。

后续数据库更新不得改变历史 Snapshot。

---

# 21. Framework 更新策略

Pilot 不做实时自动更新。

当前流程：

```text
New Framework Version Detected
↓
Upload New Source
↓
New Document Version
↓
Parse
↓
Diff / Review
↓
Approve
↓
Publish
```

旧版本保留。

不得覆盖。

---

# 22. 技术架构建议

当前推荐轻量架构：

```text
Frontend（可后置）
        ↓
FastAPI Backend
        ↓
Domain Services
        ↓
PostgreSQL
        +
pgvector
        ↓
Object Storage / Local Source Files
```

AI / Parser Sidecar：

- Document Parser；
- OCR fallback；
- Embedding；
- LLM Provider；
- Evaluation / tracing。

Pilot 可继续 Local-first，不要求先部署云服务。

---

# 23. 推荐模块边界

```text
src/
  source/
    ingestion
    parser
    provenance

  framework/
    documents
    clauses
    versions

  topic/
    import
    mapping
    retrieval

  ai/
    prompts
    schemas
    classification
    summarization

  review/
    workflow
    audit

  export/
    benchmark_excel
    questionnaire_excel

  project/
    setup
    topics
    departments

  eval/
    gold_set
    metrics
```

不建议 Pilot 阶段拆微服务。

使用 Modular Monolith。

---

# 24. 推荐 API（实现 Web UI 时）

```http
POST /projects
GET  /projects/{project_id}

POST /frameworks/documents
GET  /frameworks/documents/{document_id}
GET  /frameworks/documents/{document_id}/clauses

POST /projects/{project_id}/topics/import
GET  /projects/{project_id}/topics

POST /projects/{project_id}/mappings/generate
GET  /projects/{project_id}/mappings
PATCH /mappings/{mapping_id}

POST /clauses/{clause_id}/review

POST /projects/{project_id}/exports/benchmark

# V1
POST /projects/{project_id}/departments/import
POST /projects/{project_id}/questions/generate
POST /projects/{project_id}/exports/questionnaire
```

---

# 25. 质量与 Evaluation

## 25.1 Gold Set

在 V0 正式验收前建立人工 Gold Set。

建议：

- 选取 5–10 个代表性 ESG Topic；
- 人工标记 HKEX / SSE 全部相关 Clause；
- 覆盖定性、定量、复杂条款。

## 25.2 核心指标

### Precision

`正确召回 Mapping / 系统所有召回 Mapping`

### Recall

`系统召回的正确 Mapping / 人工 Gold Mapping 总量`

### Trace Accuracy

映射是否能正确回到真实 Clause。

### Source Completeness

正式 Mapping 是否 100% 带 Source。

## 25.3 V0 建议验收门槛

设计目标：

- Trace Accuracy：100%；
- Approved Mapping Source Completeness：100%；
- Precision：≥95%；
- Recall：≥95%（Pilot 首轮建议目标，可根据真实难度修订）；
- Excel 行与 Approved Mapping 一一对应：100%。

以上为项目验收目标，不代表当前能力已达到。

---

# 26. 错误处理

## 26.1 Parser Failure

状态：`PARSE_FAILED`

记录：

- error type；
- file；
- parser；
- log。

允许人工选择 OCR / Alternate Parser。

## 26.2 AI Schema Failure

自动重试有限次数。

仍失败则：

`AI_FAILED → Human Review Queue`

## 26.3 Missing Source

任何缺少 `clause_id` / `document_id` 的 Framework Claim 不能进入 Approved Mapping。

## 26.4 Duplicate Mapping

对 `(project_id, topic_id, clause_id)` 设置唯一约束。

---

# 27. 安全与数据边界

Pilot 主要处理公开标准和客户项目配置。

仍应遵守：

- API Key 不写入 Repo；
- 使用 `.env`；
- 客户资料与公开标准分目录/Scope；
- Logs 不打印敏感客户文本；
- AI Provider 调用必须可配置；
- 后续如引入客户未公开资料，应单独确认外部模型数据政策。

---

# 28. 从旧 Benchmarking Beta 继承的资产

原则上应优先复用已有工具，而不是全部重写。

### 可直接继承的思路

- Evidence First；
- Retrieval ≠ Analysis；
- Raw ≠ Reviewed；
- Late Structuring；
- Source document / location 追溯；
- Agent 负责语义判断，代码负责确定性处理；
- Excel 从结构化数据生成，而不是由 LLM 直接写。

### 可改造复用的模块

- 报告下载 / source acquisition；
- PDF parsing；
- candidate retrieval；
- staging → reviewed workflow；
- export scripts；
- Evidence Card 字段设计。

### 需要升级的部分

- Topic / Keyword 从代码写死 → 配置或数据库；
- JSONL 唯一数据库 → PostgreSQL；
- Evidence Card 统一承载所有来源 → 标准 Clause 与 Peer Evidence 分型；
- 人工逐次启动 Agent → 可复现 AI service / task；
- raw/reviewed/material 多 ID → 单一对象 + status/version。

---

# 29. 开发路线图

## Beta 0｜Engine Generalization

### 目标

把原 MUJI-specific Engine 变成通用 Project Engine。

### 必须完成

- [ ] Project Config 外置；
- [ ] Topic Import 通用化；
- [ ] Framework Source 通用化；
- [ ] 统一 Source / Clause Schema；
- [ ] 统一 Review Status；
- [ ] Export 使用稳定 Schema。

### Definition of Done

换一个项目名称、Topic List、Framework 文件，不需要修改核心代码即可运行。

---

## V0｜Topic × Framework Requirement

### 目标

跑通花西子 Pilot。

### 必须完成

- [ ] HKEX 文档入库；
- [ ] SSE 文档入库；
- [ ] Clause 拆分；
- [ ] 花西子 Topic Import；
- [ ] Candidate Retrieval；
- [ ] AI Relevance Classification；
- [ ] 人工 Review；
- [ ] Source Trace；
- [ ] Benchmark Excel；
- [ ] Gold Set / Accuracy Evaluation。

### Definition of Done

对 Pilot Topic，可以得到人工确认的 HKEX + SSE 披露要求清单，所有记录均能回到原文，且可稳定导出 Excel。

---

## V1｜Requirement Normalization + Questionnaire Beta

### 目标

从标准要求转成两个试点部门的信息收集表。

### 必须完成

- [ ] Canonical Requirement Draft；
- [ ] Department Import；
- [ ] DepartmentTopicMapping；
- [ ] Question Generation；
- [ ] Qualitative / Quantitative Split；
- [ ] Internal / Client View；
- [ ] Excel Export；
- [ ] 人工 Review。

### Definition of Done

两个试点部门可以生成可实际发送给客户的信息收集表草稿，并能够从每个问题回到原始框架要求。

---

## V2｜Knowledge Asset Reuse

### 目标

从“单项目工具”进入“可重复使用的知识资产”。

### 候选功能

- [ ] Canonical Requirement 审核；
- [ ] Framework Crosswalk；
- [ ] Definition / Formula Library；
- [ ] Question Template；
- [ ] Approved Mapping Reuse；
- [ ] Framework Version Compare。

---

# 30. AI Agent 持续开发协议

本节专门用于约束后续自动开发 Agent。

## 30.1 每次开发开始前

Agent 必须：

1. 阅读本 PRD；
2. 阅读当前 `CHANGELOG.md`；
3. 阅读相关 Schema / Migration；
4. 确认本次任务属于哪个版本和 Epic；
5. 不得默认扩大 Scope。

## 30.2 每个任务必须定义

- Goal；
- Inputs；
- Outputs；
- Files touched；
- Acceptance Criteria；
- Tests；
- Migration impact。

## 30.3 禁止行为

AI Agent 不得：

- 为方便开发删除 Source Trace 字段；
- 用 LLM summary 替换 original_text；
- 将 Draft AI Mapping 自动标记 Approved；
- 直接覆盖 Framework 旧版本；
- 无 Migration 修改核心 Schema；
- 无测试重写 Export Schema；
- 为减少代码复杂度合并 Raw Clause；
- 自动添加 PRD 未定义的大功能。

## 30.4 每次完成后

必须：

1. 更新 tests；
2. 更新 CHANGELOG；
3. 如 Schema 变化，更新本 PRD / data dictionary；
4. 运行 Evaluation；
5. 输出已完成 / 未完成 / 风险项。

---

# 31. 推荐 Epic Backlog

## EPIC-01 Framework Ingestion

- F-001 上传 Framework；
- F-002 Hash / Version；
- F-003 Parser Adapter；
- F-004 Clause Split；
- F-005 Provenance；
- F-006 Clause Review。

## EPIC-02 Project Topic

- T-001 Project 创建；
- T-002 Topic Excel/CSV Import；
- T-003 Topic 查看；
- T-004 Topic 数据验证。

## EPIC-03 Topic-Clause Mapping

- M-001 Candidate Retrieval；
- M-002 AI relevance；
- M-003 Mapping review；
- M-004 Add missing Clause；
- M-005 Reject / notes。

## EPIC-04 Export

- E-001 Benchmark table；
- E-002 Source columns；
- E-003 Snapshot；
- E-004 Excel format。

## EPIC-05 Evaluation

- Q-001 Gold set；
- Q-002 Precision；
- Q-003 Recall；
- Q-004 Trace audit；
- Q-005 Regression test。

## EPIC-06 Questionnaire（V1）

- I-001 Department；
- I-002 DepartmentTopic Mapping；
- I-003 Requirement normalization；
- I-004 Question generation；
- I-005 Internal vs Client View；
- I-006 Questionnaire Excel。

---

# 32. 第一轮 Sprint 建议

## Sprint 0｜项目骨架

目标：让 Engine 脱离 MUJI 特定配置。

交付：

- 通用 project config；
- Framework adapter interface；
- Topic import；
- 数据 Schema；
- 测试 fixture。

## Sprint 1｜HKEX / SSE Clause Library

交付：

- 两个 Framework 入库；
- Clause JSON / DB；
- Source Trace；
- 人工检查样本。

## Sprint 2｜Topic Mapping

交付：

- 花西子 Topic import；
- Retrieval；
- AI relevance；
- Review；
- Benchmark table。

## Sprint 3｜Evaluation / Fix

交付：

- Gold set；
- Precision / Recall；
- Mapping failure analysis；
- Prompt / Retrieval 调优。

通过后才进入 V1。

---

# 33. V0 验收用例

## AC-01 Source Trace

**Given** 一条系统认为与“应对气候变化”相关的 HKEX 要求  
**When** 用户点击 Source  
**Then** 必须展示原始 Clause、Section 和 SourceDocument。

## AC-02 No hallucinated clause

**Given** AI 生成 Requirement Summary  
**When** 对应 Clause 不存在  
**Then** 该记录不能写入 Mapping。

## AC-03 Raw immutable

**Given** Reviewer 修改 Requirement Summary  
**Then** `original_text` 不得发生变化。

## AC-04 Repeatable export

**Given** 同一个 Snapshot  
**When** 重复导出 Excel  
**Then** 核心数据行内容和来源保持一致。

## AC-05 Review gate

**Given** AI Draft Mapping  
**When** 尚未人工 Approve  
**Then** 正式 Approved Export 默认不包含该条。

## AC-06 Missing clause recovery

**Given** Reviewer 发现 AI 漏掉一条 Clause  
**Then** 用户可以人工添加 TopicClauseMapping，并标记 `decision_origin=HUMAN`。

---

# 34. 产品 KPI

Pilot 重点记录：

- 每 Topic 人工对标耗时；
- 系统对标耗时；
- Precision；
- Recall；
- 人工补漏数量；
- AI Mapping Reject Rate；
- Source Error Count；
- Excel 人工修改行数。

V1 再增加：

- Questionnaire Draft 时间；
- Question Acceptance Rate；
- 客户反馈修改次数。

---

# 35. 已明确的待决策项

以下不是开发 Agent 可自行决定的事项：

1. 四支柱是否是所有客户表格的固定维度；
2. Materiality 是否进入 Question Depth；
3. 部门相关度是否需要第二颗粒度维度；
4. Canonical Requirement 的正式 Taxonomy；
5. 定量指标 Formula 自动抽取程度；
6. Scope 1/2/3 Activity Data 模板；
7. 后续是否纳入 GRI / ISSB / MSCI / CSA；
8. UI 是否优先 Web 化；
9. 企业客户数据是否允许外部 LLM；
10. SaaS / 内部工具最终定位。

需要产品负责人明确决策后升级 PRD。

---

# 36. Definition of Product Success

## Pilot 成功

不是“AI 可以生成一个 Excel”。

而是：

> **系统能稳定地把企业 ESG Topic 映射到正确、完整、可核查的交易所披露要求，并显著减少人工查框架和做对标的时间。**

## 产品成功

长期而言：

> **将 ESG 咨询中重复的找、读、比、归类、溯源、转换和检查工作变成可复用的组织基础设施，同时让咨询师保留专业判断和最终交付控制权。**

---

# 37. 开发基线总结

当前开发必须围绕以下链路展开：

```text
花西子 ESG Topic List
        +
HKEX / SSE Source Documents
        ↓
Framework Clause Library
        ↓
Topic ↔ Clause Retrieval
        ↓
AI Relevance Judgment
        ↓
Human Review
        ↓
Traceable Benchmark Table
        ↓
[通过验收后]
        ↓
Department ↔ Topic
        ↓
Requirement → Question
        ↓
Information Collection Excel
```

**第一原则：先把 Topic → Requirement → Source 做准，再开发后续复杂能力。**


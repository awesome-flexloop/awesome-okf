---
okf_version: "0.2"
---

# Open Knowledge Format (OKF) 规范知识包

本 bundle 用 OKF 自身格式承载 OKF v0.2 规范（中文转译），以 dogfooding 方式将 OKF 规范本体转译为符合 OKF v0.2 规范的知识包：概念文档、frontmatter、溯源与信任字段均遵循同一份规范。

## 规范概念（concepts/）

### 核心规范转译（v0.2 SPEC §1–§13 中文转译）

* [OKF 规范动机](concepts/motivation.md) - OKF 的动机：人可读、可解析、可 diff、可移植，以及溯源、信任、新鲜度、生命周期、认证成为一级字段的理由。
* [OKF 术语表](concepts/terminology.md) - OKF v0.2 核心术语的中英对照与定义（知识包、概念、溯源、可信度信号、信任层级、可认证计算等）。
* [知识包结构](concepts/bundle-structure.md) - OKF v0.2 知识包的目录树结构、三种分发方式，以及保留文件名（index.md、log.md）。
* [概念文档](concepts/concept-documents.md) - OKF v0.2 概念文档结构：YAML frontmatter（必填 type，推荐 title/description/resource/tags）与正文约定标题。
* [溯源与信源（sources）](concepts/provenance-sources.md) - OKF v0.2 §5.1：`sources` 字段记录概念据以派生的信源，通过客观可信度信号（而非评分）推断信任。
* [信任：generated 与 verified 及信任层级](concepts/trust-generated-verified.md) - OKF v0.2 §5.2-§5.3：`generated` 记录内容如何产生，`verified` 记录核验事件，并由此派生三级信任层级。
* [生命周期：status 与 stale_after](concepts/lifecycle-status-stale.md) - OKF v0.2 §5.4-§5.5：`status` 标记概念状态（draft/stable/deprecated），`stale_after` 以绝对日期标记过期。
* [交叉链接与路径](concepts/cross-linking-paths.md) - 概念间的两种链接形式（bundle-relative 与相对路径）、路径值字段清单，以及 references/ 子目录约定。
* [参与者约定](concepts/actor-convention.md) - 记录身份字段所用的统一参与者约定：`<producer>/<version>`、`human:<id>`、`process:<id>` 三种形态及其信任分类用途。
* [索引文件](concepts/index-files.md) - `index.md` 的渐进披露用途、无 frontmatter 的默认约定（仅根 index.md 可含 okf_version），以及分组标题 + 条目列表格式。
* [日志文件](concepts/log-files.md) - `log.md` 的层级位置、日期分组扁平列表（最新在前）、`YYYY-MM-DD` 日期标题与前导粗体词约定。
* [可认证计算（Attested Computations）](concepts/attested-computations.md) - OKF v0.2 可认证计算概念：runtime/parameters/computation/executor/attester 契约字段、内联与文件两种计算方式、消费者的用法，以及 verification 与 attestation 之别。
* [合规性（Conformance）](concepts/conformance.md) - OKF v0.2 合规三要件，以及消费者对 trust/lifecycle/provenance/computation 字段族的处理要求与"不得拒绝"清单。
* [版本控制](concepts/versioning.md) - OKF v0.2 版本规则：<major>.<minor> 格式、次版本为向后兼容增量、主版本为破坏性变更，以及知识包声明目标版本方式与已推迟事项。
* [相对 v0.1 的变更](concepts/changes-from-v0.1.md) - OKF v0.2 相对 v0.1 的两处破坏性变更（timestamp 与 # Citations 的取代）与全部增量变更（新字段族、Attested Computation、# Computation、actor 约定）。

### 设计与实践

* [OKF 设计原则](concepts/design-principles.md) - 三大设计原则（最小意见化/生产者-消费者独立/格式而非平台）驱动规范中每一个设计决策。
* [OKF 实践指南](concepts/practical-guidance.md) - 10 条来自 v0.1 注释版和社区实践的使用建议：type 治理、扩展字段、自动化索引、断链即特性、结构化 Markdown、log vs git、Obsidian 对比、引用演进、目录放置、三规则验证。

### 生态工具

* [OKF Validator](concepts/tooling-validator.md) - 官方在线验证工具（okf.md/validator），上传目录即可检查合规性，浏览器端运行保护隐私。
* [OKF Agent Skill](concepts/tooling-agent-skill.md) - 为 AI 智能体（Claude Code/Codex/Gemini CLI）提供的技能包，含 SKILL.md 提示词和 validate.sh 验证脚本，支持"一句话创建知识包"。
* [OKF Knowledge Catalog CLI](concepts/tooling-knowledge-catalog.md) - Google Cloud Platform 官方维护的工具链仓库（knowledge-catalog），含 npm 包 @okf/okf、CLI 工具和规范源码。

## 示例（examples/）

* [绑定资源的概念示例：Customer Orders（BigQuery 表）](examples/concept-resource-bound.md) - 一个绑定到具体 BigQuery 资源的概念示例，frontmatter 含 resource、tags、generated 字段。
* [不绑定资源的概念示例：数据新鲜度告警（Playbook）](examples/concept-unbound.md) - 一个不绑定具体资源的概念示例，无 resource 字段，正文含指向其他概念的链接。
* [损益表工作示例：v0.1 → v0.2 迁移](examples/income-statement.md) - 展示同一张损益表（收入与毛利）从 v0.1 单文档形态迁移到 v0.2 可认证计算拆分形态。
* [SaaS 指标知识包快速入门](examples/saas-metrics-quickstart.md) - 来自 okf.md/quickstart 的"5分钟创建你的第一个 OKF 知识包"教程，包含 MRR/Churn/CAC/LTV 四个 SaaS 指标的完整知识包示例。

## 信源登记簿（references/）

* [Open Knowledge Format (OKF) 规范 v0.2](references/okf-spec.md) - OKF 开放知识格式 v0.2 完整英文规范原文（vendored third-party spec，1006 行），本 bundle 的权威信源。
* [OKF v0.1 注释版开发者指南](references/okf-annotated-v01.md) - v0.1 Draft 的带注释走查版，包含设计原则阐释、实践建议、代码示例与作者观点，作为 v0.2 规范的补充参考。
* [进程登记：seven-concepts-v（对抗审查）](references/processes/seven-concepts-v.md) - 本 bundle 各文档 `verified.by` 所用自动化进程的定义与复核路径，确立 machine-confirmed 信任层级。

## 信任与生命周期说明

* **status 判定依据**：原有 18 个核心规范转译文档（15 概念 + 3 示例）均 `status: stable`，由登记进程 `process:seven-concepts-v` 于 2026-08-21 执行对抗审查后确认。本次新增的 7 个文档（5 概念 + 1 示例 + 1 信源登记）状态为 `draft`：design-principles/practical-guidance/3 个 tooling-* 文档和 saas-metrics-quickstart 系基于 v0.1 注释版指南、okf.md 网站子页面（quickstart/validator/skill）的首次中文转译，okf-annotated-v01 为 v0.1 信源登记，尚未经过独立对抗审查，待后续复核后升级为 stable。
* **stale_after 解释**：核心规范转译文档统一设置为 `2027-12-31T00:00:00Z`，内容锚定于已发布的 OKF v0.2 规范，该日期作为针对 SPEC 未来可能修订的保守重新评估节点。新增文档设置为 `2027-06-30T00:00:00Z`，因网站工具页面（validator/skill/quickstart）可能随版本更新而变化，设置较早的过期检查点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（核心文档 2026-08-20，新增文档 2026-08-21）；核心文档 `verified.at` 为 2026-08-21 对抗审查核验时刻，新增文档待后续独立核验。

本知识包共收录 27 个内容文档（20 个概念 + 4 个示例 + 3 个信源/进程登记），另含 4 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:hidden:

concepts/index
examples/index
references/index
log
```

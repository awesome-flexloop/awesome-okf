# 规范概念

## 核心规范转译

* [OKF 规范动机](motivation.md) - OKF 的动机：人可读、可解析、可 diff、可移植，以及溯源、信任、新鲜度、生命周期、认证成为一级字段的理由。
* [OKF 术语表](terminology.md) - OKF v0.2 核心术语的中英对照与定义（知识包、概念、溯源、可信度信号、信任层级、可认证计算等）。
* [知识包结构](bundle-structure.md) - OKF v0.2 知识包的目录树结构、三种分发方式，以及保留文件名（index.md、log.md）。
* [概念文档](concept-documents.md) - OKF v0.2 概念文档结构：YAML frontmatter（必填 type，推荐 title/description/resource/tags）与正文约定标题。
* [溯源与信源（sources）](provenance-sources.md) - OKF v0.2 §5.1：`sources` 字段记录概念据以派生的信源，通过客观可信度信号（而非评分）推断信任。
* [信任：generated 与 verified 及信任层级](trust-generated-verified.md) - OKF v0.2 §5.2-§5.3：`generated` 记录内容如何产生，`verified` 记录核验事件，并由此派生三级信任层级。
* [生命周期：status 与 stale_after](lifecycle-status-stale.md) - OKF v0.2 §5.4-§5.5：`status` 标记概念状态（draft/stable/deprecated），`stale_after` 以绝对日期标记过期。
* [交叉链接与路径](cross-linking-paths.md) - 概念间的两种链接形式（bundle-relative 与相对路径）、路径值字段清单，以及 references/ 子目录约定。
* [参与者约定](actor-convention.md) - 记录身份字段所用的统一参与者约定：`<producer>/<version>`、`human:<id>`、`process:<id>` 三种形态及其信任分类用途。
* [索引文件](index-files.md) - `index.md` 的渐进披露用途、无 frontmatter 的默认约定（仅根 index.md 可含 okf_version），以及分组标题 + 条目列表格式。
* [日志文件](log-files.md) - `log.md` 的层级位置、日期分组扁平列表（最新在前）、`YYYY-MM-DD` 日期标题与前导粗体词约定。
* [可认证计算（Attested Computations）](attested-computations.md) - OKF v0.2 可认证计算概念：runtime/parameters/computation/executor/attester 契约字段、内联与文件两种计算方式、消费者的用法，以及 verification 与 attestation 之别。
* [合规性（Conformance）](conformance.md) - OKF v0.2 合规三要件，以及消费者对 trust/lifecycle/provenance/computation 字段族的处理要求与"不得拒绝"清单。
* [版本控制](versioning.md) - OKF v0.2 版本规则：<major>.<minor> 格式、次版本为向后兼容增量、主版本为破坏性变更，以及知识包声明目标版本方式与已推迟事项。
* [相对 v0.1 的变更](changes-from-v0.1.md) - OKF v0.2 相对 v0.1 的两处破坏性变更（timestamp 与 # Citations 的取代）与全部增量变更（新字段族、Attested Computation、# Computation、actor 约定）。

## 设计与实践

* [OKF 设计原则](design-principles.md) - 三大设计原则（最小意见化/生产者-消费者独立/格式而非平台）驱动规范中每一个设计决策。
* [OKF 实践指南](practical-guidance.md) - 10 条来自 v0.1 注释版和社区实践的使用建议：type 治理、扩展字段、自动化索引、断链即特性、结构化 Markdown、log vs git、Obsidian 对比、引用演进、目录放置、三规则验证。
* [使用场景与落地实践](adoption-scenarios.md) - 三种典型使用场景（数据目录/Agent 知识库/运维 Runbook）、Agent 四层架构中的知识层定位、渐进式文档化五阶段、Git 工作流结合与 Bundle SemVer 版本管理建议。

## 生态工具

* [OKF Validator](tooling-validator.md) - 官方在线验证工具（okf.md/validator），上传目录即可检查合规性，浏览器端运行保护隐私。
* [OKF Agent Skill](tooling-agent-skill.md) - 为 AI 智能体（Claude Code/Codex/Gemini CLI）提供的技能包，含 SKILL.md 提示词和 validate.sh 验证脚本，支持"一句话创建知识包"。
* [OKF Knowledge Catalog CLI](tooling-knowledge-catalog.md) - Google Cloud Platform 官方维护的工具链仓库（knowledge-catalog），含 npm 包 @okf/okf、CLI 工具和规范源码。

## Knowledge Catalog 平台实践（learning 合并增量）

* [Knowledge Catalog 平台概述与架构](knowledge-catalog-platform.md) - Google Cloud Knowledge Catalog（原 Dataplex）AI 驱动数据目录与元数据管理平台——背景动机、三大设计哲学、核心概念体系、四层平台架构与知识生产-消费闭环定位。
* [Knowledge Catalog 参考 Agent 实现](knowledge-catalog-reference-agent.md) - 参考 Agent 源码级解析——两阶段工作流架构、enrich 子命令参数、核心工具模块（bundle/source/web/context）、Python 实现细节、单概念迭代开发方法与 GCP 凭证配置。
* [Knowledge Catalog 元数据即代码（mdcode）](knowledge-catalog-metadata-as-code.md) - mdcode 元数据即代码工具链——元数据制品结构、init/pull/push/diff 双向同步命令、开发者工作流、BigQuery 集成与 mdcode 和 OKF 的关系。
* [Knowledge Catalog 官方示例解析](knowledge-catalog-samples.md) - GA4/Stack Overflow/比特币区块链/Acme Retail 四个示例 Bundle 结构解析、recipe 配方对应关系、Discovery/Enrichment 两个示例智能体的运行与组合使用。
* [Knowledge Catalog 集成模式与选型决策](knowledge-catalog-adoption.md) - 企业落地四阶段渐进式路径、三种典型集成场景、与既有数据目录共存、Git 工作流集成、8 种替代方案对比与选型决策树、五大反模式与编写检查清单。

```{toctree}
:hidden:
:maxdepth: 7

actor-convention
adoption-scenarios
attested-computations
bundle-structure
changes-from-v0.1
concept-documents
conformance
cross-linking-paths
design-principles
index-files
knowledge-catalog-adoption
knowledge-catalog-metadata-as-code
knowledge-catalog-platform
knowledge-catalog-reference-agent
knowledge-catalog-samples
lifecycle-status-stale
log-files
motivation
practical-guidance
provenance-sources
terminology
tooling-agent-skill
tooling-knowledge-catalog
tooling-validator
trust-generated-verified
versioning
```

---
type: Rationale
title: OKF 设计原则
description: OKF 三大设计原则——最小意见化、生产者/消费者独立、格式而非平台——驱动规范中每一个设计决策。
tags: [okf, design-principles, rationale]
generated: { by: reference_agent/trae-glm, at: 2026-08-21T08:00:00Z }
status: draft
stale_after: 2027-12-31T00:00:00Z
sources:
  - id: annotated-v01
    resource: /references/okf-annotated-v01.md
    title: OKF v0.1 Annotated Guide
  - id: okf-spec
    resource: /references/okf-spec.md
    title: OKF SPEC v0.2
---

# 设计原则

OKF 规范的每一个设计决策都经过三条原则过滤。这三条原则在 v0.1 注释版指南中明确提出，v0.2 正式规范继承了这些原则并贯穿始终。[^annotated-v01]

## 原则一：最小意见化（Minimally Opinionated）

OKF 对每个概念唯一强制要求的是 `type` 字段。除此之外——存在哪些类型、包含哪些其他字段、正文有哪些小节——全部交由生产者自行决定。规范定义的是互操作表面（interoperability surface），而非内容模型（content model）。[^annotated-v01]

**为什么这很重要？**

试图做太多的知识管理标准往往无人采用。OKF 押注于另一个极端：几乎没有规则，最大化采用面。[^annotated-v01]

这一原则在规范中的具体体现：

- `type` 是唯一始终必填的键（§4.1）；只携带 `type` 的概念即完全合规（§11）。
- 类型值不做集中注册，生产者自行选取描述性、自解释的值（§4.1）。
- 正文没有必填小节，只有约定（conventional）标题建议（§4.2）。
- 所有可选字段族（provenance、trust、lifecycle、computation）缺失时消费者不得拒绝文档（§11）。

## 原则二：生产者/消费者独立（Producer/Consumer Independence）

OKF 清晰地分离了知识的编写者和消费者。[^annotated-v01]

- 人工编写的知识包可以被 AI 智能体消费。
- 元数据导出流水线生成的知识包可以在可视化工具中浏览。
- 一个 LLM 合成的知识包可以被另一个 LLM 查询。

格式是契约，两端的工具可以独立替换。

这一原则在规范中的具体体现：

- `generated` 和 `verified` 字段分离——谁写了概念和谁确认了概念不必是同一方（§5.2）。
- 消费者必须容忍未知 `type` 值、未知 frontmatter 键、断链、缺失可选字段（§11）。
- 信任层级（trust tier）由消费者从 `verified` 字段推导，而非由生产者直接声明信任分数（§5.3）。
- 可信度信号（credibility signals）是客观记录，可信度评分（score）由消费者自行推断（§5.1）。

## 原则三：格式而非平台（Format, Not Platform）

OKF 不绑定任何特定的云平台、数据库、模型提供商或智能体框架。它永远不会要求专有账户或 SDK 来读取、编写或服务知识。[^annotated-v01]

知识格式的价值在于有多少方使用它，而不在于谁拥有它。

这一原则在规范中的具体体现：

- 载体是纯 Markdown 文件 + YAML frontmatter，`cat` 即可阅读，`git clone` 即可分发。
- 没有 schema 注册中心、中心权威机构或强制工具链。
- 分发方式开放：git 仓库（推荐）、tarball/zip 归档、大仓库中的子目录均可（§3）。
- 可认证计算（Attested Computation）固定的是接口（runtime/parameters/executor/attester），而非打包方式——executor/attester 背后是 Skill、脚本还是容器由生产者决定（§10.2）。
- v0.2 明确推迟了运行时协议、attester ABI、沙箱等平台相关内容到未来版本（§12.3）。

## 设计决策过滤器

当面临"是否应该将某某加入规范"的问题时，OKF 维护者会通过三条原则逐一检验：

1. 这个要求是否违反"最小意见化"？如果它强制了内容模型而非互操作表面，则拒绝。
2. 这个要求是否耦合了生产者和消费者？如果它要求两端使用特定工具或流程，则拒绝。
3. 这个要求是否绑定了特定平台？如果它只在特定云/工具/模型上工作，则拒绝。

只有同时满足三条原则的特性才会被考虑纳入规范。

## 相关概念

- [OKF 规范动机](./motivation.md) - 四条设计目标和非目标
- [概念文档](./concept-documents.md) - frontmatter 和正文的具体规范
- [合规性](./conformance.md) - 合规三要件与"不得拒绝"清单
- [版本控制](./versioning.md) - 版本规则与推迟事项

[^annotated-v01]: OKF v0.1 Annotated Guide（Design Principles），见 [references/okf-annotated-v01.md](/references/okf-annotated-v01.md)。
[^okf-spec]: OKF SPEC v0.2 规范，见 [references/okf-spec.md](/references/okf-spec.md)。

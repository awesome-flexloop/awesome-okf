---
type: Guide
title: OKF 实践指南
description: 来自 v0.1 注释版开发者指南和社区实践的 OKF 使用建议、陷阱规避与实操技巧。
tags: [okf, practical, guidance, best-practices]
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
  - id: quickstart
    resource: https://okf.md/quickstart
    title: Your First OKF Bundle in 5 Minutes
---

# 实践指南

本概念文档收录来自 OKF v0.1 注释版开发者指南（Annotated Guide）、官方 Quickstart 教程和社区实践的使用建议。这些内容不是规范性要求（MUST/SHOULD），而是帮助生产者和消费者更好地使用 OKF 的经验总结。[^annotated-v01]

## 1. type 字段治理：自由但危险

`type` 字段不做集中注册，你可以自由创建 `type: dbt Model` 或 `type: Kafka Topic` 而无需征得任何人同意。但这种自由是有代价的——没有治理，同一公司的两个团队可能用 `type: Table` 和 `type: BigQuery Table` 描述同一种东西。[^annotated-v01]

**实践建议：**

- 在设计文档（design doc）中提前约定 type 命名规范，避免分歧。
- type 值应描述性且自解释（如 `BigQuery Table` 而非 `table_v2`）。
- 消费者必须优雅地容忍未知 type 值，通常将其作为通用概念处理。

## 2. 扩展字段实用示例

生产者可以在 frontmatter 中添加任意自定义键。以下是一些实用扩展示例：[^annotated-v01]

```yaml
---
type: BigQuery Table
title: Customer Orders
# ... 标准字段 ...
owner: data-team@company.com
freshness_sla: 30m
data_governance_classification: internal
slack_channel: "#data-incidents"
---
```

智能的消费者（智能体）可以利用这些额外元数据做决策，例如：
- `owner` 字段用于确定问题时联系谁
- `freshness_sla` 用于驱动数据新鲜度告警
- 这些扩展不影响合规性——缺少它们的文档仍然完全合规。

## 3. 自动化生成 index.md

实践中，你会希望用脚本遍历知识包自动生成 `index.md`。以下是一个快速简陋但适用于 90% 场景的 bash 脚本：[^annotated-v01]

```bash
for f in tables/*.md; do
  [ "$(basename $f)" = "index.md" ] && continue
  title=$(grep '^title:' "$f" | sed 's/title: //')
  desc=$(grep '^description:' "$f" | sed 's/description: //')
  echo "* [$title]($(basename $f)) - $desc"
done
```

这个脚本从每个概念的 `title` 和 `description` 字段提取信息生成索引条目。更成熟的实现可以处理子目录分组、frontmatter YAML 解析等。

## 4. 断链即特性，而非 Bug

消费者必须容忍断链（broken links）——目标不存在的链接不是格式错误，它可能只是代表"尚未编写的知识"。[^annotated-v01]

**为什么这很重要？**

你可以在 `refunds table` 存在之前就写 `[refunds table](/tables/refunds.md)`。先引用，后补全。在很多系统中，你不能在某物完全定义之前引用它——这会扼杀团队渐进式文档化的动力。OKF 允许断链，正是为了支持渐进式知识构建。

消费者构建图谱视图时通常将所有链接视为无类型有向边，断链只是指向一个尚未创建的节点。

## 5. 结构化 Markdown 对 LLM + RAG 的重要性

生产者应当优先使用结构化 Markdown（标题、列表、表格、围栏代码块）而非自由散文。结构同时有助于人类浏览和智能体检索。[^annotated-v01]

**实证经验：**

使用 RAG 的 LLM 在文档有清晰标题时表现明显更好。问"orders 表的 schema 是什么"，智能体可以直接跳到 `# Schema` 小节，而不是解析一堵文字墙。无结构化文档会导致 LLM 幻觉出不存在的 schema。标题是廉价的保险。

约定标题（conventional headings）包括：

| 标题 | 用途 |
|---|---|
| `# Schema` | 资产列/字段的结构化描述 |
| `# Examples` | 具体使用示例，通常为围栏代码块 |
| `# Computation` | 可认证计算的受认可计算（v0.2 新增） |

## 6. log.md 与 git log 的区别

`log.md` 不替代 `git log`。两者受众不同：[^annotated-v01]

- **log.md**：面向人类或智能体快速浏览的高层变更记录。读者想知道"他们在5月添加了指标表"这种级别的信息。是手工编写的知识库 CHANGELOG。
- **git log**：细粒度的提交历史，记录每一行代码级别的变更。

**格式约定：**

- 日期标题使用 ISO 8601 `YYYY-MM-DD` 格式。
- 条目以粗体词开头（`**Update**`、`**Create**`、`**Deprecation**`）是惯例而非要求。
- 最新日期在前。

## 7. Obsidian 用户对比指南

如果你使用 Obsidian，大部分概念是熟悉的：[^annotated-v01]

| OKF 概念 | Obsidian 近似 | 区别 |
|---|---|---|
| Bundle（知识包） | Vault（仓库） | OKF 增加了最小互操作规则 |
| Concept（概念） | Note（笔记） | OKF 要求 `type` 字段 |
| Frontmatter | 那个 YAML 块 | OKF 标准化了可选字段族 |
| Link（链接） | Wikilink | OKF 使用标准 Markdown 链接 |

关键区别在于 OKF 正式化了工具间互操作的最小规则集。

## 8. 引用机制的演进：v0.1 Citations → v0.2 sources + Footnotes

v0.1 使用正文中的 `# Citations` 列表引用外部信源：

```markdown
# Citations
[1] [BigQuery public dataset announcement](https://...)
[2] [Internal data quality runbook](https://...)
```

v0.2 进行了两项重要改进：

1. **信源移至 frontmatter**：`sources` 字段以结构化方式记录信源，包含可信度信号（author、usage_count、last_modified）。
2. **逐声明归因用脚注**：使用 `[^source-id]` Markdown 脚注对正文中的具体声明做逐一声明归因，而非依赖位置编号。

**为什么用稳定 id 而非位置索引？**

智能体频繁重写这些文档。位置索引（`sources[0]`）在列表重排时会静默地错误归因，而稳定的 `id` 在重排后依然正确。

## 9. 实践中的目录放置建议

最常见的 setup 是将知识包放在 monorepo 内的 `knowledge/` 或 `docs/catalog/` 目录中。[^annotated-v01]

独立仓库当然也可以，但将知识放在代码附近的便利性非常显著——智能体可以在同一个 `git clone` 中同时查看 dbt schema 和 OKF 文档。

三种分发方式：

| 方式 | 适用场景 |
|---|---|
| Git 仓库（推荐） | 需要历史、归属、diff 能力 |
| Tarball/ZIP 归档 | 一次性分发或离线使用 |
| 大仓库子目录 | 与代码同仓管理 |

## 10. 快速验证：三规则合规检查

一个知识包是否合规，只需要检查三个条件：[^quickstart]

1. ✅ 每个非 `index.md`/`log.md` 的 `.md` 文件有可解析的 YAML frontmatter
2. ✅ 每个 frontmatter 有非空的 `type` 字段
3. ✅ `index.md` 和 `log.md` 遵循各自的结构约定

其余字段（title、description、tags、sources、generated、verified 等）是推荐的，但缺失不会导致不合规。

## 相关概念

- [概念文档](./concept-documents.md) - frontmatter 和正文的规范要求
- [溯源与信源](./provenance-sources.md) - sources 字段和逐声明归因
- [索引文件](./index-files.md) - index.md 的格式约定
- [日志文件](./log-files.md) - log.md 的格式约定
- [合规性](./conformance.md) - 正式合规三要件
- [相对 v0.1 的变更](./changes-from-v0.1.md) - v0.1 到 v0.2 的字段迁移
- [设计原则](./design-principles.md) - 三大设计原则如何驱动规范决策
- [生态工具：Validator](./tooling-validator.md) - 在线验证工具
- [生态工具：Agent Skill](./tooling-agent-skill.md) - 智能体技能和 validate.sh

[^annotated-v01]: OKF v0.1 Annotated Guide，见 [references/okf-annotated-v01.md](/references/okf-annotated-v01.md)。
[^okf-spec]: OKF SPEC v0.2 规范，见 [references/okf-spec.md](/references/okf-spec.md)。
[^quickstart]: OKF Quickstart 教程，见 [okf.md/quickstart](https://okf.md/quickstart)。

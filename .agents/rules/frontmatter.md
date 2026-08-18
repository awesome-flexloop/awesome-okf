# 文档元数据（frontmatter）规范

awesome-okf-xs 文档库的 Markdown 文档采用 **OKF（Open Knowledge Format）v0.2** 规定的 YAML frontmatter 作为唯一元数据来源。元数据**内嵌**于每个 Markdown 文件顶部的 YAML frontmatter，文档自包含，不引入外置元数据文件。

> OKF 的设计原则是「极简、自包含」：一个由 Markdown 文件 + YAML frontmatter 构成的目录，即可被人类阅读、被智能体解析、被版本控制 diff；无需 schema 注册中心、中心权威或强制工具链。本规范对齐 OKF v0.2 官方规范（SPEC.md）。

## 1. 结构总则

每个概念文档由两部分组成：

1. **YAML frontmatter**：以文件首行 `---` 开始、独立一行 `---` 结束的 YAML 块。
2. **Markdown 正文**：自由形式的内容。

**唯一必填字段是 `type`**。一个只携带 `type` 的文档，即为完全符合 OKF v0.2 的文档。

```yaml
---
type: <类型名>                  # 必填（唯一必填字段）
title: <可选显示名>
description: <可选单行摘要>
resource: <底层资产的可选规范 URI>
tags: [<标签>, ...]             # 可选
# ... 溯源、信任、生命周期、计算字段（见后续章节）
# ... 其他生产者自定义键值对
---
```

## 2. 必填字段：`type`

- 标识概念类型的短字符串，供路由、过滤与展示使用。
- 取值**不集中注册**，生产者应选择描述性、自解释的值。
- 示例：`BigQuery Table`、`API Endpoint`、`Metric`、`Playbook`、`Reference`、`Attested Computation`。
- 消费者必须容忍未知的 `type` 值，通常将其视为通用概念处理。

## 3. 推荐字段

| 字段 | 说明 |
|---|---|
| `title` | 人类可读的显示名；缺省时消费者可从文件名推导 |
| `description` | 单句摘要，供 index.md 生成器、搜索片段与预览使用 |
| `resource` | 底层资产的唯一标识 URI；描述抽象概念（非具体资源）时可省略 |
| `tags` | 短字符串的 YAML 列表，用于横向归类（OKF 的一等公民概念） |

## 4. 溯源字段（Provenance）：`sources`

`sources` 记录概念派生的材料（外部或 bundle 内部）：

```yaml
sources:
  - id: ga4-schema
    resource: https://developers.google.com/analytics/bigquery/export-schema
    title: GA4 BigQuery Export schema
    author: team:ga4-docs
    usage_count: 5000
    last_modified: 2026-05-30
usage_window: { from: 2026-06-01, to: 2026-06-30 }
```

- `sources[].resource`：条目内**必填**，可指向绝对 URL、bundle 相对路径（`/` 开头）、相对路径，或范围描述符（如「X 项目中的所有查询」）。
- `sources[].id`：可选。稳定键，用于逐声明归因（与脚注标签对应）。
- `sources[].title`：可选。来源的可读标签。
- 可信度信号（均可选，挂在对应 `sources` 条目上）：`author`、`usage_count`、`last_modified`；`usage_window` 作为 `sources` 的兄弟字段，为 `usage_count` 提供 `{ from, to }` 时间框。
- **逐声明归因**：用标签等于 `sources[].id` 的 Markdown 脚注引用来源。

## 5. 信任字段（Trust）：`generated` 与 `verified`

```yaml
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-06-20T22:53:05Z }
verified:
  - { by: human:ahormati, at: 2026-06-25T09:00:00Z }
  - { by: process:finance-nightly, at: 2026-06-26T02:00:00Z }
```

- `generated.by`：`generated` 内**必填**，使用 actor 约定（见第 7 节）。
- `generated.at`：ISO 8601 时间，标记内容最后一次有意义的变更。
- `verified`：验证事件列表，每项含 `by`（actor）与 `at`（时间）；多项可记录独立校验。单个验证可写成裸映射 `{ by, at }`，消费者应视为单元素列表。

## 6. 生命周期字段（Lifecycle）：`status` 与 `stale_after`

```yaml
status: stable             # draft | stable | deprecated
stale_after: 2026-09-23    # 绝对日期；当日或之后内容视为过期
```

- `status` 取值：`draft`（未审查）、`stable`（默认，可消费）、`deprecated`（保留链接与历史）。
- 缺省 `status` 视为 `stable`。
- `stale_after`：可选，绝对日期（`YYYY-MM-DD`）。

## 7. Actor 约定

记录身份标识的字段（`generated.by`、`verified[].by`）使用统一约定：

- `<producer>/<version>`：智能体或工具，如 `reference_agent/gemini-2.5-pro`
- `human:<id>`：人工，如 `human:ahormati`
- `process:<id>`：自动化流程，如 `process:finance-nightly`

信任分层按 `human:` 前缀判定——人工编写或人工确认的内容必须使用 `human:` 前缀。

## 8. 计算概念字段（Attested Computation）

`type: Attested Computation` 概念额外携带以下字段（用于「可证计算」）：`runtime`（该类型必填）、`parameters`（含 `{ name, type, required }` 的列表）、`computation`（可选，指向计算文件的路径）、`executor`（含 `resource` 与 `receipt`）、`attester`（含 `resource`）。

## 9. 扩展字段

生产者**可以**添加任意额外字段；消费者**必须**在往返（round-trip）时保留未知键，且**不得**因未识别字段而拒绝文档。

## 10. 保留文件名

以下文件名在任意层级有固定含义，**不得**用作概念文档名：

| 文件名 | 用途 |
|---|---|
| `index.md` | 目录列表，支持渐进式披露；通常无 frontmatter，仅 bundle 根可带 `okf_version` |
| `log.md` | 更新历史；日期分组的倒序列表，日期标题用 `YYYY-MM-DD` |

## 11. 交叉引用与路径

- 概念间链接优先使用 **bundle 相对绝对路径**（以 `/` 开头，相对 bundle 根），文档在子目录内移动时更稳定。
- 也支持标准相对路径。
- 消费者必须容忍断链（目标不存在不代表格式错误）。

## 12. 版本声明

用 `okf_version: "0.2"` 声明目标版本，仅允许出现在 bundle 根 `index.md` 的 frontmatter 中。

## 13. 符合性（Conformance）

一个 bundle 符合 OKF v0.2 当且仅当：

1. 每个非保留 `.md` 文件包含可解析的 YAML frontmatter。
2. 每个 frontmatter 包含非空的 `type` 字段。
3. 每个保留文件名（`index.md`、`log.md`）遵循对应结构。

消费者**不得**因下述原因拒绝 bundle：缺少可选字段、未知 `type` 值、未知额外字段、断链、缺少 `index.md`。
---
type: reference
title: "信源索引：官方发布页与采集通道"
tags: [anthropic, claude, system-prompts, sources]
sources:
  - id: claude-system-prompts-docs
    title: "Anthropic System Prompts Release Notes (platform.claude.com)"
---

# 信源索引：官方发布页与采集通道

本文档登记本束全部事实的信源构成：官方发布页的入口结构、18 个模型子页完整清单、页面结构模板、采集通道与采集过程记录，以及第三方交叉印证源的定位声明。本束全部 F 编号事实（检索视图见[条目事实登记表](entry-registry.md)）均以下文登记的信源为唯一事实主源。

## 信源层级总览

| 层级 | 信源 | 用途 |
|---|---|---|
| 事实主源 | platform.claude.com 官方 System Prompts Release Notes（en 版：overview 导航页 + 18 个模型子页） | 全部事实主张的登记与引用依据 |
| 官方印证源 | Anthropic 官方博客与新闻页（fable-mythos-access 声明、safeguards routing 博客引文、Fable/Mythos 差异说明页） | 交叉印证，不独立承载事实主张 |
| 第三方媒体 | 未采集 | 不列名、不引用（见"第三方交叉印证源"一节） |

## 官方信源总入口

- en 总入口（overview 导航页）：[System Prompts overview](https://platform.claude.com/docs/en/release-notes/system-prompts/overview)
- zh-CN 对应入口：[System Prompts overview（zh-CN）](https://platform.claude.com/docs/zh-CN/release-notes/system-prompts/overview)

overview 页为卡片导航页（`<CardGroup cols={3}>`），列出全部 18 个模型子页面，本页不含提示词正文（F-OV-001）。官方在页面首段给出定位声明：系统提示词是 claude.ai 网页端与移动端在每次会话开始时注入的"产品级配置"，承担两项职责——提供实时信息（当前日期）与引导特定行为（如代码片段一律用 Markdown）；更新节奏为"定期"，且明确不适用于 Claude API（F-OV-002）。

**内容基线声明**：本次采集实测 zh-CN 路径（HTML 与 .md 端点）均返回 "App unavailable in region"，en 路径 .md 端点可直连（存在间歇性地域拦截，重试可过），故本束以 en 版为内容基线（18 页全量采集成功），zh-CN 仅作页面结构佐证（F-OV-005）。

## 18 个模型子页完整清单

下表为 overview 卡片列表的完整清单，排列顺序与官方一致（新→旧，F-OV-001）；"日期条目数"经全量采集逐页核对（F-OV-006）；"本地采集文件名"为 raw markdown 落盘文件（overview 页落盘为 `sp-en.md`，模型页位于 `sp-docs\` 目录，见"采集方法"一节）。

| # | 模型 | 官方 URL（en） | 日期条目数 | 本地采集文件名 |
|---|------|---------------|-----------|---------------|
| 1 | Claude Fable 5.1 | [claude-fable-5-1](https://platform.claude.com/docs/en/release-notes/system-prompts/claude-fable-5-1) | 1 | sp-docs/claude-fable-5-1.md |
| 2 | Claude Opus 5 | [claude-opus-5](https://platform.claude.com/docs/en/release-notes/system-prompts/claude-opus-5) | 1 | sp-docs/claude-opus-5.md |
| 3 | Claude Fable 5 | [claude-fable-5](https://platform.claude.com/docs/en/release-notes/system-prompts/claude-fable-5) | 1 | sp-docs/claude-fable-5.md |
| 4 | Claude Opus 4.8 | [claude-opus-4-8](https://platform.claude.com/docs/en/release-notes/system-prompts/claude-opus-4-8) | 1 | sp-docs/claude-opus-4-8.md |
| 5 | Claude Opus 4.7 | [claude-opus-4-7](https://platform.claude.com/docs/en/release-notes/system-prompts/claude-opus-4-7) | 1 | sp-docs/claude-opus-4-7.md |
| 6 | Claude Sonnet 4.6 | [claude-sonnet-4-6](https://platform.claude.com/docs/en/release-notes/system-prompts/claude-sonnet-4-6) | 1 | sp-docs/claude-sonnet-4-6.md |
| 7 | Claude Opus 4.6 | [claude-opus-4-6](https://platform.claude.com/docs/en/release-notes/system-prompts/claude-opus-4-6) | 1 | sp-docs/claude-opus-4-6.md |
| 8 | Claude Opus 4.5 | [claude-opus-4-5](https://platform.claude.com/docs/en/release-notes/system-prompts/claude-opus-4-5) | 2 | sp-docs/claude-opus-4-5.md |
| 9 | Claude Haiku 4.5 | [claude-haiku-4-5](https://platform.claude.com/docs/en/release-notes/system-prompts/claude-haiku-4-5) | 3 | sp-docs/claude-haiku-4-5.md |
| 10 | Claude Sonnet 4.5 | [claude-sonnet-4-5](https://platform.claude.com/docs/en/release-notes/system-prompts/claude-sonnet-4-5) | 3 | sp-docs/claude-sonnet-4-5.md |
| 11 | Claude Opus 4.1 | [claude-opus-4-1](https://platform.claude.com/docs/en/release-notes/system-prompts/claude-opus-4-1) | 1 | sp-docs/claude-opus-4-1.md |
| 12 | Claude Opus 4 | [claude-opus-4](https://platform.claude.com/docs/en/release-notes/system-prompts/claude-opus-4) | 3 | sp-docs/claude-opus-4.md |
| 13 | Claude Sonnet 4 | [claude-sonnet-4](https://platform.claude.com/docs/en/release-notes/system-prompts/claude-sonnet-4) | 3 | sp-docs/claude-sonnet-4.md |
| 14 | Claude Sonnet 3.7 | [claude-sonnet-3-7](https://platform.claude.com/docs/en/release-notes/system-prompts/claude-sonnet-3-7) | 1 | sp-docs/claude-sonnet-3-7.md |
| 15 | Claude Sonnet 3.5 | [claude-sonnet-3-5](https://platform.claude.com/docs/en/release-notes/system-prompts/claude-sonnet-3-5) | 4 | sp-docs/claude-sonnet-3-5.md |
| 16 | Claude Haiku 3.5 | [claude-haiku-3-5](https://platform.claude.com/docs/en/release-notes/system-prompts/claude-haiku-3-5) | 1 | sp-docs/claude-haiku-3-5.md |
| 17 | Claude Opus 3 | [claude-opus-3](https://platform.claude.com/docs/en/release-notes/system-prompts/claude-opus-3) | 1 | sp-docs/claude-opus-3.md |
| 18 | Claude Haiku 3 | [claude-haiku-3](https://platform.claude.com/docs/en/release-notes/system-prompts/claude-haiku-3) | 1 | sp-docs/claude-haiku-3.md |
| — | 合计（18 页） | — | 30 | — |

条目数的时代分布（F-OV-006）：3.x 时代 8 条（上表 #14-18，其中 Sonnet 3.5 一页独占 4 条）+ 4.0/4.1 时代 7 条（#11-13）+ 4.5 代 8 条（#8-10）+ 固定快照时代 7 条（#1-7）。固定快照机制指自 Claude 4.6 代起每个模型 ID 是单一固定快照，提示词不再随时间演进，故每模型仅一个条目；4.6 之前的模型页面保留多个日期条目（F-OV-004）。

## 页面结构模板

18 个模型子页共享同一页面结构，采集与核对时按此定位内容：

1. YAML frontmatter：`title` / `url` / `description` 三字段——本束各"页面元信息"条目（如 F-3X-001、F-40-001）逐字抄录的对象；
2. 日期条目：以 `## <日期>` 标题分节，多条目页面按日期倒序（新→旧）排列（F-3X-005、F-40-001、F-45-001）；
3. 提示词正文：每个日期条目下以 text wrap 围栏代码块承载完整正文；固定快照时代（4.6 起）正文为 `<claude_behavior>` XML，其中 Opus 4.8、Opus 5、Fable 5.1 三页额外在收尾标签之后带 `<tone_preference>` 尾块；
4. 页面级叙述文字极少：仅部分页面在条目前带差异标注说明句——已登记者为 Sonnet 3.5 页与 4.5 代三页（Sonnet/Haiku/Opus 4.5），说明句为 "Changes between the following dated versions are marked with `**` around the changed text."（F-3X-005、F-45-001）；4.0 时代页面（以 claude-sonnet-4.md 为登记样本）无任何页面级叙述文字与加粗差异标注（F-40-001）。

frontmatter 三字段的通用形态（`<模型名>`/`<slug>` 为占位符示意）：

```yaml
title: <模型名> system prompts
url: https://platform.claude.com/docs/en/release-notes/system-prompts/<slug>
description: See updates to the core system prompt for <模型名> on [claude.ai](https://claude.ai) and the [Claude iOS app](https://anthropic.com/ios) and [Claude Android app](https://anthropic.com/android).
```

### 编号段与信源页面对应关系

各 F 编号段采信的具体落盘页面如下（与[条目事实登记表](entry-registry.md)的登记总览一一对应）：

| 编号段 | 采信源落盘页面 | 覆盖条目数 |
|---|---|---|
| F-OV | sp-en.md（overview 页） | — |
| F-3X | sp-docs/ 下 claude-opus-3、claude-haiku-3、claude-sonnet-3-5、claude-haiku-3-5、claude-sonnet-3-7 共 5 个 .md | 8 |
| F-40 | sp-docs/ 下 claude-sonnet-4、claude-opus-4、claude-opus-4-1 共 3 个 .md | 7 |
| F-45 | sp-docs/ 下 claude-sonnet-4-5、claude-haiku-4-5、claude-opus-4-5 共 3 个 .md | 8 |
| F-46 | sp-docs/ 下 claude-opus-4-6、claude-sonnet-4-6、claude-opus-4-7、claude-opus-4-8、claude-fable-5、claude-opus-5、claude-fable-5-1 共 7 个 .md | 7 |

## 采集方法（过程性记录）

本节如实登记 2026-09-02 的采集过程。本节属过程性记录而非事实主张；事实主张一律登记在 facts 系列文件并由[条目事实登记表](entry-registry.md)索引。

### .md 原文端点技巧

在任意页面 URL 后追加 `.md` 即可取得 raw markdown 原文，例如：

- overview 页：`https://platform.claude.com/docs/en/release-notes/system-prompts/overview.md`
- 模型子页：`https://platform.claude.com/docs/en/release-notes/system-prompts/claude-opus-3.md`

raw markdown 的构成与用途：

- frontmatter 三字段逐字可核对——"页面元信息"条目的 title/url/description 引文均出于此；
- 日期标题与代码块正文——本束全部逐字引文与行号（Lxxx）均以落盘 md 文件为准；行号为本地落盘文件的绝对行号，与线上渲染页码无关；
- 逐字引用约定：官方原文自带的重复词、标点与排版瑕疵（如 "can't or won't with"）一律保留、不做修正，作为各版本文本指纹使用。

### 地域拦截与重试策略

- en 路径：curl 直取 .md 端点存在**间歇性**地域拦截（返回 "App unavailable in region"），重试可过；本次采集逐页重试，直至 18 页全部成功落盘（F-OV-005）；
- zh-CN 路径：HTML 与 .md 端点均**稳定**返回 "App unavailable in region"（WebFetch 与 curl 结果一致），未采得任何 zh-CN 正文；
- 双通道验证：对可达性存疑的路径以 WebFetch 与 curl 两种通道交叉验证，避免把瞬时故障误判为稳定拦截。

### 采集范围与落盘

- 范围：overview 1 页 + 18 个模型子页，共 19 个 .md 文件；
- 落盘命名：overview 页为 `sp-en.md`，模型页为 `sp-docs\<slug>.md`；
- 落盘位置为采集环境临时目录（`%TEMP%`）下的过程性文件，长期引用以本束登记的编号与快照日期为准；
- 完整性结论：18 页 30 条目全覆盖、无"（待补）"项（抽查核验记录见[条目事实登记表](entry-registry.md)）。

## 第三方交叉印证源（仅作印证，不作事实主源）

以下信源仅用于交叉印证；任何事实主张的登记与引用一律以官方发布页为主源：

1. 官方博客 fable-mythos-access 声明：[Fable, Mythos and export controls](https://www.anthropic.com/news/fable-mythos-access)——Opus 5 提示词 export controls 通知段内引用的官方声明链接（F-46-012）；
2. safeguards routing 官方博客：其引文已内嵌于 Opus 5 提示词 `<fable_safeguards_routing>` 章节（保守调校、平均在不到 5% 的会话中触发等，F-46-012）；该博客原文 URL 未在本束事实登记中落盘，引用时以提示词内逐字引文为准；
3. Fable/Mythos 差异说明官方页：[claude-fable-5-mythos-5 发布稿](https://www.anthropic.com/news/claude-fable-5-mythos-5)（Fable 5 提示词内出口链接，F-46-010）与 [anthropic.com/claude/fable](https://www.anthropic.com/claude/fable)（Fable 5.1 提示词内出口链接，F-46-014）——同为官方自证源，两链接的新旧交替本身亦是登记事实。

关于公开技术媒体报道：本束事实登记未采集任何第三方媒体报道，故不列名——未经核验的媒体转述不入册；后续如需补充，应先与官方页面核对一致性，且仍不得替代官方主源。

## 引用规范

官方发布页是人工维护的活文档（I-07），本束已实测存在三类失真：

1. 差异标注执行不严格：Sonnet 3.5 页声明以 `**` 加粗标注版本差异，实际 4 个条目中仅 1 处生效（F-OV-003、F-3X-007）；
2. 旧条目被就地更新而不改日期：Haiku 3.5 页 "Text and images" 变体内容含 2025-02 才存在的 Sonnet 3.7 信息（F-3X-010）；
3. 官方笔误跨版本沿用："can't or won't with"、"but as as a request" 等原文瑕疵逐字留存于多个版本（F-40-011、F-40-013）。

因此引用官方页面须遵守：

- **注日期**：必须注明所引快照的采集日期；本束全部引文以 2026-09-02 的 .md 端点快照为准，不代表页面当前状态；
- **自行存档**：建议用 .md 端点下载原文自行存档并逐行 diff，勿依赖页面加粗标记判断版本差异（I-07 影响条款）；
- **以实测为准**："页面声称"（如加粗约定）不等于"页面所示"（实际差异规模），版本对比结论一律以逐行 diff 实测为准（facts-era-40-41.md 登记了 7 组程序化行级对比的完整方法）。

引用任一事实的操作路径：

1. 检索定位：先查[条目事实登记表](entry-registry.md)定位 F 编号与一句话含义；
2. 原文核对：回 spec 目录对应 facts 文件核对逐字引文与本地行号；
3. 线上对照（可选）：如需对照官方页面现状，用 .md 端点取原文并注明对照日期，勿以渲染页为准。

## 更新预期

- Fable 5.1 页面于 2026-09-01 上线，是本束采集前最新加入的模型子页（F-46-013）；
- 后续新模型将出现在 overview 卡片列表中；固定快照机制下新页面预期仍为"每模型 1 条目"形态（F-OV-004）；
- 新页面同样可通过 .md 端点采集；
- 本束事实的时效边界为 2026-09-02 快照：官方页面更新后，本索引与[条目事实登记表](entry-registry.md)不自动更新，需重新采集并核对。

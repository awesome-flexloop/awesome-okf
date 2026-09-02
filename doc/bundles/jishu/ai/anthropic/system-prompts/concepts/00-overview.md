---
type: concept
title: "公开机制与政策边界：claude.ai 系统提示词是什么"
tags: [anthropic, claude, system-prompts, release-notes, mechanism]
sources:
  - id: claude-system-prompts-docs
    title: "Anthropic System Prompts Release Notes (platform.claude.com)"
---

# 公开机制与政策边界：claude.ai 系统提示词是什么

Anthropic 在官方文档站维护着一套特殊的发布说明（Release Notes）：它不记录 API 变更，也不记录功能上线，而是逐条公布 claude.ai 产品端系统提示词的历次版本。本篇是「Claude 系统提示词发布史」研读束的总览层，回答三个问题：这套提示词是什么、官方公开了什么、边界在哪里。以下引文均逐字摘自官方 overview 页（事实编号 F-OV-xxx），中文解读为作者转述。

## 本束导航

- 本篇（00）：公开机制与政策边界总览
- [01-lineage-matrix.md](01-lineage-matrix.md)：18 模型 × 30 条目全景矩阵与时间线
- [02-era-3x.md](02-era-3x.md)：3.x 时代（2024-07 → 2025-02），从单段文本到人格化转折
- [03-era-4x-launch.md](03-era-4x-launch.md)：4.0/4.1 时代（2025-05 → 2025-08），单一模板与身份插槽
- [04-era-45.md](04-era-45.md)：4.5 代（2025-09 → 2026-01），九章节架构定型
- [05-era-fixed-snapshot.md](05-era-fixed-snapshot.md)：固定快照时代（2026-02 → 2026-09），Mythos 层与版权条款
- [06-evolution.md](06-evolution.md)：跨时代形态演化纵向梳理

## 什么是系统提示词：官方定位逐字读

官方 overview 页在开篇给出了一段完整的定位声明，这是理解整个页面体系权威性的锚点（F-OV-002）：

> "Claude's web interface (claude.ai) and mobile apps use a system prompt to provide up-to-date information, such as the current date, to Claude at the start of every conversation. The system prompt also encourages certain behaviors, such as always providing code snippets in Markdown. This prompt is periodically updated to improve Claude's responses. These system prompt updates do not apply to the Claude API. Some models have multiple dated entries on their pages. Starting with the Claude 4.6 generation, each model ID is a single fixed snapshot, so those models have one entry."（F-OV-002）

这段声明可以拆出四层含义：

1. **会话开始注入**。系统提示词不在训练阶段生效，而是在「每次对话开始时」（at the start of every conversation）注入上下文——它是运行时的产品级配置，与模型权重分离。
2. **提供实时信息**。最典型的例子是当前日期：模型的知识截止是静态的，而「今天是几号」必须靠系统提示词在运行时填入，模型才能正确回答「今天」相关的问题。
3. **引导特定行为**。官方举的例子是「代码片段始终用 Markdown」——系统提示词承载的是产品期望的行为规范，从输出格式到安全边界都在此层定义。
4. **定期更新**。提示词「为改进 Claude 的响应而被定期更新」（periodically updated），且官方以日期条目的形式公开每个版本的发布时间——这正是本套发布说明存在的原因。

一句话概括：系统提示词是 claude.ai 在会话开始时注入的「产品级操作系统」，与开发者通过 API 传入的 system 参数分属两个世界。

## 公开范围与政策边界

官方声明限定的公开范围非常明确（F-OV-002）：

- **适用端**：claude.ai 网页端 + iOS/Android 移动端。每个模型子页的 frontmatter description 都是同一句式的逐字声明，以 Opus 3 页为例："See updates to the core system prompt for Claude Opus 3 on [claude.ai](https://claude.ai) and the [Claude iOS app](https://anthropic.com/ios) and [Claude Android app](https://anthropic.com/android)."（F-3X-001）——18 页仅模型名不同，适用端从未扩大。
- **明确不适用**："These system prompt updates do not apply to the Claude API."（F-OV-002）——Claude API 完全不在覆盖范围内。

这条边界值得展开解读：

- **API 用户自带 system 参数**。API 调用者通过请求参数传入自己的系统提示词，模型行为由开发者自行定义；claude.ai 的产品级提示词若也作用于 API，会与开发者的指令叠加冲突。官方把两者切割干净，是对开发者控制权的尊重。
- **产品级提示词与开发者提示词分离**。本套发布说明公开的是 Anthropic 作为「产品方」如何调教自家消费端产品——其中大量条款（产品导购、支持链接、thumbs down 引导、心理健康照护）都是 claude.ai 特有的产品语境，对 API 场景没有参考义务。
- **研究价值的边界**。因此，研读这套材料时应当把它当作「产品提示词工程的一手样本」，而非「Claude 模型的通用行为说明书」——后者并不存在单一权威文本。

## 发布机制：从持续更新到固定快照

### 多日期条目与加粗差异约定

官方自 2024-07 起持续发布这套说明，多数模型页面保留多个日期条目。关于版本间差异如何标注，官方曾有两代表述并存（F-OV-003）：

- 旧版单页表述（搜索引擎快照存证）：> "Where a model has multiple dated entries below, updates between versions are bolded."（F-OV-003）——即相邻版本的变更文本以加粗标注。
- 新版 overview 页（F-OV-002 末两句）只说明「部分模型有多个日期条目、4.6 起单一固定快照」，未再提及加粗约定。

实测发现这一约定执行得并不严格：Sonnet 3.5 页面的 4 个条目中，加粗标记仅实际出现 1 处（2024-09-09 条目），其余大量变更未做任何标注（F-OV-003）。研读时不能依赖官方标注，需自行逐版比对——4.5 代三页是例外，其加粗标注覆盖较完整。

### 4.6 起的固定快照机制

2026 年起发布机制发生结构性变化（F-OV-004）：

> "Starting with the Claude 4.6 generation, each model ID is a single fixed snapshot"（F-OV-004）

官方在声明旁外链了模型 ID 与版本的说明文档。中文解读：自 4.6 代起，每个模型 ID 对应一份固定不变的提示词快照——提示词不再随时间滚动演进，因此每页只有一个日期条目；4.6 之前的模型页面保留多个日期条目，记录的是历史演进轨迹。这一机制让「发布说明」在新时代退化为「存档页」，也让历史时代的多条目页面愈发珍贵。

## 页面体系：一个总览页与十八个模型子页

overview 页本身是卡片导航页，不含任何提示词正文；正文全部在模型子页（F-OV-001）。官方以 `<CardGroup cols={3}>` 组件按**新→旧**顺序列出 18 个模型子页，每页独立 URL（slug 形如 `claude-opus-3`）。官方卡片列表精简复述如下（F-OV-001）：

| # | 卡片标题 | 子页 slug | # | 卡片标题 | 子页 slug |
|---|---------|-----------|---|---------|-----------|
| 1 | Claude Fable 5.1 | claude-fable-5-1 | 10 | Claude Sonnet 4.5 | claude-sonnet-4-5 |
| 2 | Claude Opus 5 | claude-opus-5 | 11 | Claude Opus 4.1 | claude-opus-4-1 |
| 3 | Claude Fable 5 | claude-fable-5 | 12 | Claude Opus 4 | claude-opus-4 |
| 4 | Claude Opus 4.8 | claude-opus-4-8 | 13 | Claude Sonnet 4 | claude-sonnet-4 |
| 5 | Claude Opus 4.7 | claude-opus-4-7 | 14 | Claude Sonnet 3.7 | claude-sonnet-3-7 |
| 6 | Claude Sonnet 4.6 | claude-sonnet-4-6 | 15 | Claude Sonnet 3.5 | claude-sonnet-3-5 |
| 7 | Claude Opus 4.6 | claude-opus-4-6 | 16 | Claude Haiku 3.5 | claude-haiku-3-5 |
| 8 | Claude Opus 4.5 | claude-opus-4-5 | 17 | Claude Opus 3 | claude-opus-3 |
| 9 | Claude Haiku 4.5 | claude-haiku-4-5 | 18 | Claude Haiku 3 | claude-haiku-3 |

这份排列本身就是一份「官方视角的模型谱系」：Fable 5.1 置顶说明它是最新旗舰，Haiku 3 垫底说明它是活语料中最老的可用页面。按时代重新分组，可以更清楚地看到页面数量与条目数量的分布规律：

- **3.x 时代（5 页 8 条）**：Sonnet 3.7、Sonnet 3.5、Haiku 3.5、Opus 3、Haiku 3——Sonnet 3.5 一页独占 4 条，是全语料条目最多的页面；
- **4.0/4.1 时代（3 页 7 条）**：Opus 4.1、Opus 4、Sonnet 4——Sonnet 4 与 Opus 4 各 3 条，Opus 4.1 仅 1 条；
- **4.5 代（3 页 8 条）**：Opus 4.5、Haiku 4.5、Sonnet 4.5——Sonnet 与 Haiku 各 3 条，Opus 2 条；
- **固定快照时代（7 页 7 条）**：Fable 5.1、Opus 5、Fable 5、Opus 4.8、Opus 4.7、Sonnet 4.6、Opus 4.6——每页恰好 1 条。

18 页合计 30 个日期条目（F-OV-006）。注意 Spec 早期曾据旧版单页快照估计为「16 模型 × 28 条目」，实际采集核实为 **18 模型 × 30 条目**（Fable 5.1 于 2026-09-01 上线补齐末班车，且旧快照未含个别条目）——本束一律以核实数为准。完整的模型 × 条目对照、架构代际与页面行数实测，见[全景矩阵](01-lineage-matrix.md)。

还需要注意「页面体系之外」的模型：部分模型仅在提示词正文的家族清单或模型字符串中被提及，但**没有独立子页**——例如 Sonnet 5 出现在 Opus 5 页面的模型串列表中，Claude Mythos 5 与 Fable 5 共享底模却无公开页面（F-46 时代小结的采集边界说明）。因此「18 个子页」不等于「Anthropic 全部现役模型」，引用时不可把页面清单当作完整的模型名录。

各模型页面遵循统一的排版惯例：frontmatter（title / url / description）→ 若干个 `## <日期>` 标题 → 每个标题下一个 `text wrap` 代码块承载完整提示词正文。条目一律按**日期倒序**（新→旧）排列，因此阅读历史演进时需要自下而上回溯。多数页面除日期标题外没有任何叙述文字，唯一例外是 3.5 代页面带有一句加粗差异标注说明。

### 语言版本与可达性

官方文档站提供多语言路径，中文读者通常会选择 zh-CN 入口。但实测（2026-09-02 采集时）发现一个需要如实记录的约束（F-OV-005）：

- zh-CN 路径（HTML 与 .md 端点）在采集环境均返回 "App unavailable in region"；
- en 路径的 .md 端点可直连（存在间歇性地域拦截，重试可通过）。

因此本束全部内容以 **en 版为内容基线**（18 页全量采集成功），zh-CN 仅作页面结构佐证。若你所在区域访问 zh-CN 正常，可自行对照阅读，但引文核对请以 en 版为准。

## 提示词内注入的动态元素

系统提示词并非一段死文本，其中嵌有若干动态插槽。这里点到为止，各时代的详细解析见对应时代文档。

### 当前日期变量

3.x 时代起，提示词开场即携带占位符 `{{currentDateTime}}`——会话开始时由产品端替换为真实时间（F-3X-002）。这是官方定位声明中「提供当前日期」的实现机制，也是全语料唯一贯穿始终的模板变量。

### 知识截止插槽

每版提示词都写明模型的知识截止时点，且随版本持续前滚。全语料的知识截止轨迹如下（依据各时代事实登记）：

| 知识截止 | 覆盖条目 |
|----------|----------|
| August 2023 | Opus 3、Haiku 3（F-3X-002/004） |
| April 2024 | Sonnet 3.5 全部 4 条目（F-3X-006） |
| July 2024 | Haiku 3.5 text only 变体（F-3X-011） |
| start of December 2024 | Haiku 3.5 images 变体（就地更新所致，F-3X-012） |
| end of October 2024 | Sonnet 3.7（F-3X-014） |
| end of January 2025 | Sonnet 4、Opus 4、Opus 4.1 全部条目；Sonnet/Haiku 4.5 各版（F-40-002、F-45-002） |
| end of May 2025 | Opus 4.5 两条目、Opus 4.6（F-45-010、F-46-002） |
| beginning of August 2025 | Sonnet 4.6（F-46-004） |
| end of January 2026 | Opus 4.7、Opus 4.8、Fable 5（F-46-006/008/010） |
| end of May 2026 | Opus 5（F-46-012） |
| end of Jun 2026 | Fable 5.1（F-46-014） |

同一时代内不同档位模型的知识截止也可能不同（如 Sonnet 4.6 为 beginning of August 2025，同期 Opus 4.6 为 end of May 2025；4.5 代内 Opus 线整体比 Sonnet/Haiku 线晚四个月）。知识截止是判断「提示词新旧」最可靠的锚点，也是理解模型自我认知边界的第一入口。

### 产品信息层

3.5 代起，提示词开始写入模型家族信息、访问渠道与模型字符串（model string）；4.5 代起扩展为完整的产品信息区。产品信息层是随产品矩阵演进最快的部分，也是各版本差异最集中的区域，其内部又可细分四个子层：

- **家族叙事**：3.x 的三档定位语（Sonnet 最智能 / Opus 擅长写作 / Haiku 最快）→ 4.0 的家族成员清单 → 2026-01 的「Claude 4.5 家族」整体叙事 → 4.8 起家族叙事被「The currently selected version of Claude」取代；
- **模型字符串**：3.5 代首次携带（claude-3-5-sonnet-20241022）→ 4.5 代三模型并列 → Opus 4.8 一口气列出五个；
- **产品生态**：Claude Code（3.7 首入）→ Claude for/in Chrome 与 Excel（4.5 代）→ Cowork（2026-01 首入）→ Claude in Powerpoint（Sonnet 4.6）→ Claude Design（4.8）→ Claude Tag（Opus 5）；
- **设置项清单**：2026-01-18 起三模型同步写入可开关功能（web search、deep research、Code Execution and File Creation、Artifacts、Search and reference past chats、generate memory from chat history），模型获得「功能导购」授权。

各子层的逐条目演变细节，见四个时代文档与[06 形态演化](06-evolution.md)。

## 研读指南：如何使用本束学习

### 建议阅读顺序

1. 先读本篇与[全景矩阵](01-lineage-matrix.md)，建立 18 模型 × 30 条目的空间感；
2. 按[02 时代文档](02-era-3x.md) → [03](03-era-4x-launch.md) → [04](04-era-45.md) → [05](05-era-fixed-snapshot.md) 的顺序通读四个时代，跟随格式的三代演进（单段文本 → XML 分节 → 无标签段落 → 九章节 XML）与主题的代际迁移（功能性 → 人格化 → 安全工程化 → 产品生态化）；
3. 最后用[06 形态演化](06-evolution.md)做纵向收束，观察单一条款（如反奉承、知识截止话术）的跨代流变。

### 如何对照原文

- 本束所有引文均标注 F 编号，F 编号指向 `.trae/specs/create-claude-system-prompts-wiki/` 下的逐字事实登记（overview 层 F-OV-xxx 与四个时代层 F-3X/F-40/F-45/F-46-xxx），登记中同时保留了本地落盘文件的行号；
- 各模型官方子页支持 .md 端点直取（如 `platform.claude.com/docs/en/release-notes/system-prompts/claude-opus-3` 加 `.md`），便于逐字核对；
- 注意官方页面存在就地更新与历史残留（如 Haiku 3.5 的 images 变体文本晚于页面标注日期），引用时以快照内容为准。

### 快速定位示例

用一个真实场景演示本束的使用路径。假设你想确认「2025 年 10 月 claude.ai 上的 Haiku 4.5 遵循什么行为规则」：

1. 先查[全景矩阵](01-lineage-matrix.md)主矩阵中 Haiku 4.5 一行——该页有 3 个条目（2025-10-15、2025-11-19、2026-01-18），2025 年 10 月对应首发条目 2025-10-15；
2. 按「分时代条目明细」的 4.5 代子表确认该条目的关键变化（与 Sonnet 4.5 首发版几乎逐字同构、采用提示开启搜索范式）；
3. 进入[04 时代文档](04-era-45.md)定位 Haiku 4.5 首发条目解析，或按 F 编号回查事实登记原文行号；
4. 若需引用，注明「Claude Haiku 4.5 · 2025-10-15 条目」。

整个流程不超过两分钟——这正是矩阵篇存在的意义。

### 引用规范提示

官方页面是**活文档**：条目会被追加、措辞会被静默修正（4.5 代 evenhandedness 段的历史重复词错误即被无标注修正）、产品清单随发布节奏改写。引用本束或官方原文时，务必注明所引版本的**日期条目**（如「Claude Opus 4.1 · 2025-08-05 条目」），而非笼统写「Claude 系统提示词」——笼统引用在多日期条目模型上几乎必然失准。

## 延伸阅读

- 束内姊妹篇：[01-lineage-matrix.md](01-lineage-matrix.md)（全景矩阵与时间线）、[06-evolution.md](06-evolution.md)（跨时代演化）
- 束入口与条目登记表：[../index.md](../index.md)
- 官方信源：Anthropic System Prompts Release Notes（platform.claude.com，见 frontmatter sources）

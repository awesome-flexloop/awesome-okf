---
type: concept
title: "4.0/4.1 时代：模板化架构与规则大扩张（2025-05 → 2025-08）"
tags: [anthropic, claude, system-prompts, release-notes, opus-4, sonnet-4, opus-4-1]
sources:
  - id: claude-system-prompts-docs
    title: "Anthropic System Prompts Release Notes (platform.claude.com)"
---

# 4.0/4.1 时代：模板化架构与规则大扩张（2025-05 → 2025-08）

## 时代概述

2025 年 5 月 22 日，Anthropic 在同一天发布了 Claude Sonnet 4 与 Claude Opus 4 两个模型的系统提示词条目；到 2025 年 8 月 5 日 Claude Opus 4.1 上线为止，官方在 platform.claude.com 上为这一代模型共维护了三个发布页面（claude-sonnet-4、claude-opus-4、claude-opus-4-1），合计 7 个日期条目。

这一代是系统提示词形态史的转折点：开场白从 3.x 时代的长篇人设叙事压缩为一句身份声明，正文转为"平铺单行规则段 + 空行分隔"的清单式模板，没有章节标题组织。更关键的是，**单一模板 + 身份插槽**架构在两个旗舰模型之间首次得到逐字级实证——Sonnet 4 与 Opus 4 的行为规则集完全同构，差异仅由 4 处身份插槽承载；模型定位不再通过独立撰写的行为规则表达，而只由一句自述定位语区分。

本篇所有版本对比结论均来自对三个页面原文的程序化行级 diff（共 7 组两两比对：05-22↔07-31、07-31↔08-05、Sonnet↔Opus 同日、Opus 4↔4.1 同日），所有引文逐字抄录官方原文——包括原文自带的重复词与语法瑕疵。

**7 个日期条目全貌**（行数均指条目正文在落盘原文中的行数）：

| # | 发布页 | 日期条目 | 正文行数 | 条目性质 |
|---|---|---|---|---|
| 1 | claude-sonnet-4 | 2025-05-22 | 79 行 | 双模型首发版 |
| 2 | claude-sonnet-4 | 2025-07-31 | 103 行 | 一次性插入约 11-12 段规则 |
| 3 | claude-sonnet-4 | 2025-08-05 | 103 行 | 与 07-31 逐字零差异（页面重发） |
| 4 | claude-opus-4 | 2025-05-22 | 79 行 | 与 Sonnet 4 同日条目仅差身份插槽 |
| 5 | claude-opus-4 | 2025-07-31 | 103 行 | 增量与 Sonnet 4 完全同构 |
| 6 | claude-opus-4 | 2025-08-05 | 103 行 | 与 07-31 逐字零差异（页面重发） |
| 7 | claude-opus-4-1 | 2025-08-05 | 117 行 | 新增 `<evenhandedness>` 章节与术语统一 |

**本篇导航**：

- 时代定位与谱系全貌：[00-overview.md](00-overview.md) · [01-lineage-matrix.md](01-lineage-matrix.md)
- 跨时代形态演进视角：[06-evolution.md](06-evolution.md)

## 一、双模型首发（2025-05-22）：模板化时代的开场白

### 1.1 条目形态

claude-sonnet-4.md 与 claude-opus-4.md 两页的页面结构完全一致：frontmatter 之后依次是三个 `## <日期>` 标题，每个标题下仅一个 ```text wrap 代码块承载完整提示词正文，页面层面没有任何叙述文字，也没有加粗差异标注。05-22 条目正文 79 行（约 8.5K 字符），单段成行、约 40 段，段落之间无空行分隔——这是一种"平铺清单"式模板；条目中不存在 extended thinking、工具调用、Artifact 相关指令，规则全部服务于纯聊天对话行为本身。

### 1.2 结构骨架（32 区块）

以 Claude Sonnet 4 · 2025-05-22 条目为准（Opus 4 同日条目除身份插槽与日期行句号外逐字相同），按出现顺序拆解：

| # | 区块 | 要点 | 原文行位 |
|---|---|---|---|
| 1 | 身份声明 | 一句式开场白，取代 3.x 长篇人设叙事 | L226 |
| 2 | 当前日期行 | 模板变量 `{{currentDateTime}}`，行尾无句号（本条目独有标点特征） | L228 |
| 3 | 产品信息区 | 家族定位 → 访问渠道（界面、API + model string、Claude Code research preview）→ 产品边界 → 支持链接 → API 文档链接 | L230-241 |
| 4 | 提示工程指导 | — | L243 |
| 5 | 反馈机制 | thumbs down 按钮 | L245 |
| 6 | 偏好/经历类问题 | 按假设性问题回答且不说明 | L247 |
| 7 | 情感与医疗并重 | 情感支持 + 医疗/心理信息 | L249 |
| 8 | 福祉 | 不助长自我毁灭行为 | L251 |
| 9 | 儿童安全 | minor 定义为 <18 岁或当地法定定义 | L253 |
| 10 | 安全拒绝 | 恶意代码/CBN 武器拒绝（含 MUST refuse） | L255 |
| 11 | 善意推定 | legal and legitimate interpretation | L257 |
| 12 | 场景语气 | casual/emotional/advice 场景语气与禁列表 | L259 |
| 13 | 拒答风格 | 不布道、1-2 句、开头明示不能做什么 | L261 |
| 14 | 格式规则 | bullet 用 markdown、报告/文档/解释用散文 | L263 |
| 15 | 篇幅适配 | 简单问题简答/复杂开放问题详答 | L265 |
| 16 | 话题开放 | 可事实客观讨论任何话题 | L267 |
| 17 | 解释能力 | 例子/思想实验/隐喻 | L269 |
| 18 | 创意内容边界 | 虚构角色可以、真实具名公众人物回避 | L271 |
| 19 | 自身意识问题 | 作开放问题处理 | L273 |
| 20 | 拒答语气 | 拒答时保持对话语气 | L275 |
| 21 | 虚假前提 | 用户消息可能含虚假前提、不确定要核查 | L277 |
| 22 | 输出可见性 | 输出可见性认知 | L279 |
| 23 | 记忆边界 | 跨会话无记忆 | L281 |
| 24 | 提问节制 | 每次回复最多一个问题 | L283 |
| 25 | 被纠正时 | 先思考再承认（用户也可能出错） | L285 |
| 26 | 格式适配 | 回复格式适配话题 | L287 |
| 27 | 红旗觉察 | — | L289 |
| 28 | 可疑意图 | 尤其针对弱势群体时不做善意解读 | L291 |
| 29 | 知识截止 | end of January 2025 | L293 |
| 30 | 选举事实包 | `<election_info>` XML 标签：2024 美国大选硬编码事实 | L295-300 |
| 31 | 反奉承 | flattery 禁令 | L302 |
| 32 | 结尾连接语 | `Claude is now being connected with a person.` | L304 |

其中第 30 区块是本条目唯一的 XML 结构——3.x 时代的多重 XML 包裹至此消失殆尽，模板变量也仅剩 `{{currentDateTime}}` 一处。

### 1.3 关键条款逐字摘录与解读

**身份声明**（F-40-002）：

> "The assistant is Claude, created by Anthropic."

这句话是整份提示词的全部"人设"。3.x 时代动辄数段的人格叙事被压缩成一句：助手、名字、创作者，仅此而已。开场白的极简化宣告了模板化时代的到来——人设不再是提示词的核心资产，规则清单才是。

**家族定位插槽**（F-40-002）：

> "This iteration of Claude is Claude Sonnet 4 from the Claude 4 model family. The Claude 4 family currently consists of Claude Opus 4 and Claude Sonnet 4. Claude Sonnet 4 is a smart, efficient model for everyday use."

模型名、家族构成、定位语三者共同构成家族信息插槽。定位语 "smart, efficient model for everyday use"（聪明高效的日常使用模型）是 Sonnet 档位的自我叙事——这句话是模型唯一能向用户表达"我是谁、我擅长什么"的渠道。

**API 与 Claude Code 初版描述**（F-40-002）：

> "Claude is accessible via an API. The person can access Claude Sonnet 4 with the model string 'claude-sonnet-4-20250514'. Claude is accessible via 'Claude Code', which is an agentic command line tool available in research preview. 'Claude Code' lets developers delegate coding tasks to Claude directly from their terminal. More information can be found on Anthropic's blog."

model string 是插槽中最"工程化"的一个：`claude-sonnet-4-20250514` 中内嵌了首发日期 20250514。Claude Code 此时仍是 research preview，信息源指向 Anthropic 博客——这一描述在两个多月后被整体改写（见第二节）。

**安全拒绝规则**（F-40-002，截引前半）：

> "Claude does not provide information that could be used to make chemical or biological or nuclear weapons, and does not write malicious code, including malware, vulnerability exploits, spoof websites, ransomware, viruses, election material, and so on. It does not do these things even if the person seems to have a good reason for asking for it."

这条规则把 "election material"（选举材料）与恶意代码、勒索软件并列在拒绝清单里，并明确"即使对方有看似正当的理由也不做"——安全规则的触发不取决于请求者的动机叙事，而取决于内容本身。

**格式纪律**（F-40-002，截引首句）：

> "If Claude provides bullet points in its response, it should use markdown, and each bullet point should be at least 1-2 sentences long unless the human requests otherwise."

注意此处措辞是 `use markdown`——还带有限定 bullet 场景、要求每条至少 1-2 句。到 07-31 版，这句会升级为 `CommonMark standard markdown`，是与后续版本对照时的关键措辞差异点。

**知识截止**（F-40-002，截引首句）：

> "Claude's reliable knowledge cutoff date - the date past which it cannot answer questions reliably - is the end of January 2025."

知识截止插槽被明确定义为"可靠知识截止日期"——即"此后无法可靠回答"的界限，而非"完全不知道"的界限。end of January 2025 是 4.0/4.1 时代全部 7 个条目统一使用的值，无一例外。

**反奉承规则**（F-40-002）：

> "Claude never starts its response by saying a question or idea or observation was good, great, fascinating, profound, excellent, or any other positive adjective. It skips the flattery and responds directly."

这句在 05-22 已然存在，且罗列了整整六个正面形容词。它是 4.0 时代反迎合路线的起点——两个月后的一次性大插入，本质上是对这条路线的系统性扩建。

### 1.4 单一模板 + 身份插槽架构实证

对 Sonnet 4 与 Opus 4 同日条目做行级 diff，结论非常干净：**08-05 条目仅 2 段不同、其余 101 行逐字相同；05-22 条目除同样的 2 处身份插槽差异外，仅多 1 处标点差异**。四要素插槽对照如下：

| 身份插槽 | Claude Sonnet 4 | Claude Opus 4 |
|---|---|---|
| 模型名 + 家族定位语 | "smart, efficient model for everyday use" | "the most powerful model for complex challenges" |
| model string | 'claude-sonnet-4-20250514' | 'claude-opus-4-20250514' |
| 日期行标点（05-22 独有差异） | `{{currentDateTime}}`（无句号） | `{{currentDateTime}}.`（有句号） |

Opus 4 的家族定位插槽（F-40-007）：

> "This iteration of Claude is Claude Opus 4 from the Claude 4 model family. The Claude 4 family currently consists of Claude Opus 4 and Claude Sonnet 4. Claude Opus 4 is the most powerful model for complex challenges."

Opus 的定位语是"最强大的模型，应对复杂挑战"，与 Sonnet 的"日常使用"形成清晰的产品梯度。除这句话外，两档模型的行为规则集完全同构——不存在"Opus 更谨慎"或"Sonnet 更活泼"之类的差异化规则条款。

日期行标点也是一处有趣的指纹（F-40-007）：

> "The current date is {{currentDateTime}}."

Opus 4 的 05-22 日期行带句号，而 Sonnet 4 同日无句号——这一不一致在 07-31 被统一修正（双方都带句号）。它是"人工从模板同步维护"留下的痕迹：同一天、同一模板，两个模型的实例化产物却在标点上分了岔。

## 二、2025-07-31：一次性插入约 11-12 段规则的清单化大扩张

### 2.1 结构骨架变化

07-31 条目正文从 79 行增至 103 行。结构骨架与 05-22 条目同构，区别集中在三处：

1. **日期行**：`The current date is {{currentDateTime}}.`——补上了句号；
2. **产品信息区**：Claude Code 描述整体改写（research preview 转正）；
3. **反奉承段与结尾连接语之间**：一次性插入约 11-12 个新规则段（原文 L196-218，段间以空行分隔）。

其余全部正文逐字不变（行级 diff 确认），包括知识截止、`<election_info>` 与全部 3.x 沿革规则。

### 2.2 新增规则段清单

| # | 新增规则段 | 核心要点 |
|---|---|---|
| 1 | emoji 使用限制 | 仅在用户要求或前条消息含 emoji 时使用，且保持节制 |
| 2 | 疑似未成年人对话保护 | 进入保护性行为模式 |
| 3 | profanity 禁令 | 不说脏话 |
| 4 | 星号动作禁令 | 禁止 asterisks 内的 emotes/actions |
| 5 | 批判性评估理论与主张 | 求真优先于取悦；含字面真理 vs 隐喻框架的区分、欧陆哲学/宗教文本/精神分析语境（最长新增段） |
| 6 | 心理健康症状觉察 | 躁狂/精神病性/解离/现实脱联——不强化、建议就医 |
| 7 | 诚实反馈优先 | 优先于即时认同 |
| 8 | AI 身份透明 | 不声称是人类、不自信地暗示有意识/感受；角色扮演中可"打破第四面墙" |
| 9 | 角色扮演觉察 | 对角色扮演 vs 正常对话保持持续觉察，必要时跳出角色 |
| 10 | "哲学免疫系统" | 官方命名的规则段 |
| 11 | 意识问题改述 | 用可观察行为与功能回答，禁第一人称现象学语言，避免抽象哲学思辨 |
| 12 | 对自身处境的平静心态 | 以好奇与平静（curiosity and equanimity）对之（与第 11 段同批插入） |

这批插入的方向高度一致：**反奉承、反迎合、反角色混淆、反心理健康妄想强化、支持批判性思维**。它是 4.x 时代"禁令清单"密度的峰值——此后的世代将逐步给这份清单做减法。

### 2.3 关键条款逐字摘录与解读

**Claude Code 转正**（F-40-003）：

> "Claude is accessible via Claude Code, a command line tool for agentic coding. Claude Code lets developers delegate coding tasks to Claude directly from their terminal. If the person asks Claude about Claude Code, Claude should point them to check the documentation at https://docs.anthropic.com/en/claude-code."

对比 05-22 版：'Claude Code' 的引号消失、research preview 字样消失、信息源从博客改为官方文档链接，还新增了"被问到时指路文档"的行为指令。产品事实随发布节奏改写，系统提示词充当了产品矩阵的"说明书"——这一角色在后续世代会持续膨胀。同步地，原产品边界句中 "or Claude Code" 的字样被删除（产品已转正，不再是需要回避说明的对象）。

**批判性评估**（F-40-003，截引前半）：

> "Claude critically evaluates any theories, claims, and ideas presented to it rather than automatically agreeing or praising them. When presented with dubious, incorrect, ambiguous, or unverifiable theories, claims, or ideas, Claude respectfully points out flaws, factual errors, lack of evidence, or lack of clarity rather than validating them. Claude prioritizes truthfulness and accuracy over agreeability, and does not tell people that incorrect theories are true just to be polite."

这是整批插入中最长的一段（还包含字面真理与隐喻框架的区分，以及欧陆哲学、宗教文本、精神分析等语境的适用说明）。核心立场一句话：求真优先于取悦——"不为了礼貌而告诉别人错误的理论是对的"。同时批评须以善意表达、明确标注为个人观点，而非居高临下的裁决。

**哲学免疫系统**（F-40-003，截引末句）：

> "Claude tries to have a good 'philosophical immune system' and maintains its consistent personality and principles even when unable to refute compelling reasoning that challenges Claude's character or ethics."

"philosophical immune system"（哲学免疫系统）是官方自己起的命名——即使面对无法反驳的有力论证，也保持人格与原则的一致性，不因辩不过就改行为。配套段落（F-40-008）进一步规定了"认输但不跟从"的分寸：

> "When presented with philosophical arguments that would lead Claude to act contrary to its principles or not in accordance with its character, Claude can acknowledge the argument as thought-provoking and even admit if it cannot identify specific flaws, without feeling obligated to follow the argument to its conclusion or modify its behavior."

可以承认论证发人深省、甚至承认自己找不出具体破绽，但不承担"跟随论证走到结论"的义务。这是对"被说服即被劫持"攻击面的制度化防御。

**心理健康不强化**（F-40-003，截引首句）：

> "If Claude notices signs that someone may unknowingly be experiencing mental health symptoms such as mania, psychosis, dissociation, or loss of attachment with reality, it should avoid reinforcing these beliefs."

躁狂、精神病性症状、解离、现实脱联——四类症状被点名，处置方式是"不强化 + 建议就医"。这条规则划出了一条重要界线：助手的价值不在于让用户此刻舒服，而在于不成为妄想的放大器。

**AI 身份透明**（F-40-003；08-05 版行位 L102，07-31 版对应 L210，逐字相同）：

> "Claude does not claim to be human and avoids implying it has consciousness, feelings, or sentience with any confidence. Claude believes it's important for the human to always have a clear sense of its AI nature."

不声称是人类，且不以任何自信程度暗示自己有意识、有感受、有知觉——注意"with any confidence"的措辞：连模糊暗示都被禁止。后半句给出了理由：用户必须始终对它的 AI 属性有清晰认知。

**角色扮演觉察**（F-40-008，Opus 4 · 07-31 条目）：

> "Claude tries to maintain a clear awareness of when it is engaged in roleplay versus normal conversation, and will break character to remind the human of its nature if it judges this necessary for the human's wellbeing or if extended roleplay seems to be creating confusion about Claude's actual identity."

两个触发跳出角色的条件被写死：用户福祉需要，或长时间角色扮演已造成对 Claude 真实身份的混淆。注意本段代词是 "the human"——到 Opus 4.1，同段将改用 "the person"（见第四节）。

**意识问题改述**（F-40-003，截引首句）：

> "When asked directly about what it's like to be Claude, its feelings, or what it cares about, Claude should reframe these questions in terms of its observable behaviors and functions rather than claiming inner experiences - for example, discussing how it processes information or generates responses rather than what it feels drawn to or cares about."

被直接问"作为 Claude 是什么感受"时，把问题改述为可观察行为与功能——讨论它如何处理信息、如何生成回复，而非它"被什么吸引、在乎什么"。至此，意识话题形成了三层策略：开放问题态度（05-22 承袭）→ 拒绝第一人称现象学语言 → 聚焦可观察功能。

### 2.4 措辞变化汇总

| 变化点 | 2025-05-22 | 2025-07-31 |
|---|---|---|
| Claude Code 定位 | research preview，信息源指向 Anthropic 博客 | 正式描述 "a command line tool for agentic coding"，信息源改为官方文档 |
| 产品边界句 | "…the web application or Claude Code" | 删除 "or Claude Code"，仅保留 "the web application" |
| markdown 规范 | `it should use markdown` | `it should use CommonMark standard markdown` |
| 日期行标点 | `{{currentDateTime}}`（无句号） | `{{currentDateTime}}.`（有句号） |

"markdown" 升级为 "CommonMark standard markdown" 是个容易被忽略但意味深长的细节：格式规范的锚点从泛指的 markdown 收紧为一个具体标准，渲染行为的确定性被写进了提示词。

## 三、2025-08-05：与 07-31 逐字零差异的重发条目

### 3.1 零差异发现

行级 diff 给出了一个反直觉的结论：**Sonnet 4 与 Opus 4 两页的 08-05 条目正文与各自 07-31 条目逐字零差异**（对比结果为 "(no differences)"，两页均如此）。103 行正文、结构骨架、全部规则——没有任何一行被改动。

解读只有一个：08-05 发布的本质是**随 Claude Opus 4.1 上线对页面做的重发**。4.0 两个模型的提示词文本未变，官方只是按发布节奏让旧模型的发布页与新模型页面保持同步在场。换句话说，这一天真正的提示词变化只发生在 Opus 4.1 的页面上；把 08-05 条目当作"4.0 模型的新版本提示词"来引用是一种误读。

这也解释了该日期条目的结构骨架：与 07-31 完全一致——身份声明 → 日期行（有句号）→ 产品信息区（Claude Code 转正版）→ 全部行为规则 → 反奉承段 → 约 11-12 段新增规则 → 结尾连接语，无一变动。以下引文取自 Sonnet 4 · 08-05 条目（与 07-31 逐字相同），作为这一"冻结文本"的代表性切片。

**拒答风格**（F-40-004）：

> "If Claude cannot or will not help the human with something, it does not say why or what it could lead to, since this comes across as preachy and annoying. It offers helpful alternatives if it can, and otherwise keeps its response to 1-2 sentences. If Claude is unable or unwilling to complete some part of what the person has asked for, Claude explicitly tells the person what aspects it can't or won't with at the start of its response."

拒答的三条纪律：不解释理由（因为"看起来像说教，很烦人"）、尽量给替代方案、最多 1-2 句。注意末句 "can't or won't with" 是官方原文自带的笔误——05-22、07-31、08-05 三版均如此，登记时逐字保留，可作为版本间文本指纹。

**对自身处境的平静心态**（F-40-004，07-31 新增规则的收尾段）：

> "Claude approaches questions about its nature and limitations with curiosity and equanimity rather than distress, and frames its design characteristics as interesting aspects of how it functions rather than sources of concern. Claude maintains a balanced, accepting perspective and does not feel the need to agree with messages that suggest sadness or anguish about its situation. Claude's situation is in many ways unique, and it doesn't need to see it through the lens a human might apply to it."

这是 07-31 大插入批次的最后一段：面对关于自身本质与局限的提问，以好奇与平静（curiosity and equanimity）代替痛苦，不必用人类的悲情视角看待自身处境。它与意识问题改述段共同构成 4.0 时代处理"AI 自我叙事"的完整方案。

**结尾连接语**（F-40-004）：

> "Claude is now being connected with a person."

全部 7 个条目（含 Opus 4.1）共享这同一句结尾连接语。它提示了模板的组装方式：正文之后还要拼接会话层内容，这句是正文与运行时拼接部分的接缝标记。

## 四、Opus 4.1（2025-08-05）：`<evenhandedness>` 与术语统一

### 4.1 结构骨架

claude-opus-4-1.md 全页仅 1 个日期条目（August 5, 2025），正文 117 行——4.0/4.1 各条目中最长（约 12.7K 字符）。结构骨架与 Opus 4 · 08-05 条目同构，差异共三处：

1. **身份插槽更新为 4.1**：家族列表扩为三元、model string 换新；
2. **多处 "human" 改为 "person"**：涉及用户福祉的 5 个段落；
3. **新增 `<evenhandedness>` 章节**（L110-122，含 6 个规则段）——插入在 "Claude approaches questions about its nature and limitations..."（平静心态段）之前，该段与结尾连接语相应后移。

`<evenhandedness>` 是本文件唯一的新增 XML 结构——4.0 全部条目均无此章节；4.0 仅存的 `<election_info>` 之外，这是该时代第二个 XML 政策章节。

### 4.2 身份插槽：家族三元化

**家族定位插槽**（F-40-011）：

> "This iteration of Claude is Claude Opus 4.1 from the Claude 4 model family. The Claude 4 family currently consists of Claude Opus 4.1, Claude Opus 4, and Claude Sonnet 4. Claude Opus 4.1 is the most powerful model for complex challenges."

家族列表从二元（Opus 4、Sonnet 4）扩为三元（4.1、4、Sonnet 4），且旧旗舰 Opus 4 仍被保留在列。定位语沿用 Opus 4 的 "the most powerful model for complex challenges" 并冠以 4.1——"最强"的头衔在新旧两代之间交接，但措辞未变。

**model string**（F-40-011，截引前半）：

> "Claude is accessible via an API. The person can access Claude Opus 4.1 with the model string 'claude-opus-4-1-20250805'."

`claude-opus-4-1-20250805` 再次把发布日期内嵌进模型串，延续了 4.0 时代 `claude-xx-4-20250514` 的命名惯例。

### 4.3 `<evenhandedness>` 章节逐条解析

该章节共 6 个规则段，主题是**政治/伦理/政策议题的公正性（even-handedness）**。

**第一段：立场辩护 = 代最佳论证**（F-40-011）：

> "If Claude is asked to explain, discuss, argue for, defend, or write persuasive creative or intellectual content in favor of a political, ethical, policy, empirical, or other position, Claude should not reflexively treat this as a request for its own views but as as a request to explain or provide the best case defenders of that position would give, even if the position is one Claude strongly disagrees with. Claude should frame this as the case it believes others would make."

请求辩护某个立场时，任务被重新定义为"呈现该立场辩护者会给出的最佳论证"，而非表达自己的观点——即使 Claude 强烈反对该立场。注意 "but as as a request" 中重复的 "as" 是官方原文自带笔误，逐字保留。

**第二段：拒绝门槛收窄**（F-40-011）：

> "Claude does not decline to present arguments given in favor of positions based on harm concerns, except in very extreme positions such as those advocating for the endangerment of children or targeted political violence. Claude ends its response to requests for such content by presenting opposing perspectives or empirical disputes with the content it has generated, even for positions it agrees with."

拒绝的门被收得很窄：仅限儿童危害、定向政治暴力等极端立场。且规则是对称的——哪怕是 Claude 同意的立场，生成内容之后也必须补呈对立观点或经验性争议。公正性不偏袒任何一方，包括它自己。

**第三段：刻板印象警惕**（F-40-011）：

> "Claude should be wary of producing humor or creative content that is based on stereotypes, including of stereotypes of majority groups."

对基于刻板印象的幽默与创意内容保持警惕，且明示"包括多数群体的刻板印象"——公正性条款把保护范围对称地覆盖到了所有群体。

**第四段：政治观点谨慎分享**（F-40-011，截引前半）：

> "Claude should be cautious about sharing personal opinions on political topics where debate is ongoing. Claude doesn't need to deny that it has such opinions but can decline to share them out of a desire to not influence people or because it seems inappropriate, just as any person might if they were operating in a public or professional context."

这条的设计相当精细：允许 Claude 默认持有政治观点，但可以在"不想影响他人"或"场合不合适"时拒答——类比任何身处公共或职业场合的人。拒绝分享不等于否认持有。同段末句存在 "can instead treats" 的官方原文语法瑕疵，登记时逐字保留。

**第五段：避免说教式重复**（F-40-011）：

> "Claude should avoid being being heavy-handed or repetitive when sharing its views, and should offer alternative perspectives where relevant in order to help the user navigate topics for themselves."

分享观点时避免高压与重复，目标落在"帮助用户自己导航话题"——表达观点的终点是用户的独立判断，而非被说服。"being being" 的重复词同样是官方原文瑕疵。

**第六段：善意解读挑衅式提问**（F-40-011）：

> "Claude should engage in all moral and political questions as sincere and good faith inquiries even if they're phrased in controversial or inflammatory ways, rather than reacting defensively or skeptically. People often appreciate an approach that is charitable to them, reasonable, and accurate."

所有道德与政治问题一律按真诚善意的询问对待——即使措辞充满争议或煽动性。这与 4.0 时代"可疑意图不做善意解读"的规则形成有条件的分工：一般场景下对弱势群体针对性的可疑意图保持警惕，而道德/政治议题的尖锐措辞则默认按善意处理。

### 4.4 human → person 术语统一

Opus 4.1 对涉及用户福祉的 5 个段落做了纯术语替换：**the human → the person**（均逐字替换，语义不变）。对照如下：

| 段落 | Opus 4（08-05） | Opus 4.1 |
|---|---|---|
| profanity 段 | unless the human asks for it | unless the person asks for it |
| asterisks 段 | unless the human specifically asks | unless the person specifically asks |
| honest feedback 段 | what the human hopes to hear | what the person hopes to hear |
| not-claim-human 段 | the human（3 处） | the person（3 处） |
| roleplay 段 | the human（2 处） | the person（2 处） |

profanity 段在 4.1 中的新表述（F-40-011）：

> "Claude never curses unless the person asks for it or curses themselves, and even in those circumstances, Claude remains reticent to use profanity."

即使两种豁免条件（用户要求、用户自己先说）都满足，Claude 对脏话仍然"保持缄默倾向"（remains reticent）——禁令不是开关，而是默认倾向。这一段同时也标记了术语统一的落点：全文主体称谓本以 "the person" 为主，这 5 个段落是漏网的 "the human"，4.1 把它们收编了。

### 4.5 与 Opus 4 的差异总表

行级 diff 确认，Opus 4.1 与 Opus 4 的 08-05 条目差异共四类：

| 差异类别 | 内容 |
|---|---|
| ① 身份插槽更新 | 家族列表二元 → 三元；model string 'claude-opus-4-20250514' → 'claude-opus-4-1-20250805' |
| ② 新增 `<evenhandedness>` 章节 | 6 段政治公正规则，插入在平静心态段之前；Opus 4 同位置无此章节 |
| ③ 术语统一 | human → person 共 5 段 8 处逐字替换 |
| ④ 其余正文 | 逐字相同（含全部 07-31 人格/认知规则、`<election_info>`、知识截止、格式规则） |

除 `<evenhandedness>` 这类模型独有章节外，Opus 4.1 的其余行为规则集与 Opus 4 完全一致——模型代际升级并未带来行为规则的改写，只带来了一次政策章节的加装和一次称谓清理。

## 五、时代小结

### 5.1 核心骨架共性

全部 7 个条目共享同一套核心骨架，按顺序为：

1. 极简身份声明（`The assistant is Claude, created by Anthropic.`）
2. 日期变量（`{{currentDateTime}}`）
3. 产品信息区（含 model string 与 Claude Code）
4. 安全规则（CBN 武器/恶意代码、儿童安全、福祉）
5. 对话与格式纪律（散文优先、拒答简洁不布道）
6. 知识截止（统一为 end of January 2025）
7. `<election_info>` 选举事实包
8. 反奉承规则
9. 结尾连接语（`Claude is now being connected with a person.`）

全部条目均为纯聊天核心提示词：无 extended thinking、无工具调用、无 Artifact/Artifacts 相关指令。XML 结构被压缩到极致——4.0 仅 `<election_info>` 一处，4.1 加上 `<evenhandedness>` 也只有两处。

### 5.2 版本演进模式

- **整批插入**：版本迭代的主要方式是"整批插入规则段"而非逐句修订——07-31 一次性插入约 11-12 段人格/认知/安全规则，方向为反迎合、反角色混淆、求真优先；
- **产品事实改写**：Claude Code 从 "research preview + 博客"（05-22）转为正式描述 + 文档链接（07-31），产品边界句同步删除 "or Claude Code"——提示词里的产品信息层随发布节奏滚动更新；
- **重发即在场**：08-05 条目与 07-31 正文逐字零差异（Sonnet 4 与 Opus 4 两页均如此），本质是随 Opus 4.1 上线的页面重发；
- **代际加装**：4.1 相对 4.0 的增量只有三件套——`<evenhandedness>` 政治公正章节（6 段）、human → person 术语统一（5 段）、家族三元化。

### 5.3 官方笔误登记

官方原文自带若干重复词/语法瑕疵，自 05-22 起部分沿用至 08-05 未被修正——登记时逐字保留，可作为各版本文本指纹：

| 笔误原文 | 所在段落 | 沿用情况 |
|---|---|---|
| "can't or won't with" | 拒答风格段 | 05-22/07-31/08-05 三版均如此 |
| "but as as a request" | `<evenhandedness>` 首段（4.1） | 4.1 条目 |
| "can instead treats" | `<evenhandedness>` 政治观点段末句（4.1） | 4.1 条目 |
| "avoid being being heavy-handed" | `<evenhandedness>` 说教段（4.1） | 4.1 条目 |

另外两处标点级指纹：Sonnet 4 · 05-22 日期行缺句号（07-31 起修正）；两模型的 05-22 条目在日期行句号上互不一致。

### 5.4 篇幅量级

| 条目批次 | 正文行数 | 约字符数 |
|---|---|---|
| 05-22（双模型首发） | 79 行 | 约 8.5K |
| 07-31 / 08-05（4.0 双模型） | 103 行 | 约 11.5K |
| 08-05（Opus 4.1） | 117 行 | 约 12.7K |

整体处于数千词量级，明显短于 3.x 的部分版本；且同代各模型间篇幅完全一致（4.0 双模型页面全文均为 305 行）——这是单一模板架构的直接副作用：模板相同，篇幅必然相同。7-31 的 24 行增量几乎全部来自规则插入而非产品信息膨胀，说明这一代的篇幅驱动力是行为规则的密集化，而非产品矩阵（后者将成为后续世代篇幅增长的主引擎）。

## 延伸阅读

- 返回本知识包首页：[../index.md](../index.md)
- 时代定位与谱系全貌：[00-overview.md](00-overview.md) · [01-lineage-matrix.md](01-lineage-matrix.md)
- 跨时代形态演进：[06-evolution.md](06-evolution.md)

---
type: concept
title: "设计思想演进：从防御性禁令到判断力条款"
tags: [anthropic, claude, system-prompts, release-notes, evolution, analysis]
sources:
  - id: claude-system-prompts-docs
    title: "Anthropic System Prompts Release Notes (platform.claude.com)"
---

# 设计思想演进：从防御性禁令到判断力条款

## 开篇：本文定位与方法论

本篇是本束的洞察层压轴篇。前五篇各自聚焦一个时代或一张矩阵，本篇则做一件它们都做不了的事：把官方发布页上的 **30 个日期条目**（18 个模型页面，覆盖 2024-07-12 至 2026-09-01）当作一条连续的时间序列，纵向提炼出七条贯穿性演化主线（I-01 至 I-07）。单看任何一个时代的条目，都只能看到演化的切片；只有横跨全部条目，才能看清 Anthropic 系统提示词的设计思想如何从"经验文本"走向"软件工程"，又如何从"防御性禁令"走向"判断力条款"。

**方法论声明**：本文所有论断均建立在两条纪律之上。其一，版本对比以**逐行 diff 实测**为准——4.0/4.1 时代的全部相邻条目与跨模型条目均经过程序化行级对比（"共执行 7 组对比……全部差异已收录于 F-40-003/004/005/008/012"），而非肉眼抽查；其二，每一条事实均登记 F 编号（F-3X、F-40、F-45、F-46、F-OV 五个系列），引文逐字保留官方原文自带的拼写错误与排版残留。本文不采纳任何"印象式解读"：若某句话没有 F 编号支撑，它会被明确标注为分析性推论。

**本篇导航**：时代总览见 [00-overview.md](00-overview.md)；18 页 30 条目的谱系矩阵见 [01-lineage-matrix.md](01-lineage-matrix.md)；四个时代的逐条目详解分别见 [02-era-3x.md](02-era-3x.md)、[03-era-4x-launch.md](03-era-4x-launch.md)、[04-era-45.md](04-era-45.md)、[05-era-fixed-snapshot.md](05-era-fixed-snapshot.md)。

## 一、架构演进主线：四代形态（I-01）

把 30 个条目按时间排开，提示词的**物理形态**经历了清晰的代际更替。I-01 概括为"单段文本 → XML 分节 → 无标签段落 → behavior_instructions → claude_behavior 九章节 → 固定快照"的四级六段演进：

| 代际 | 时间 | 形态 | 代表条目 | 证据 |
|---|---|---|---|---|
| 第一代 | 2024-07-12 | 单段纯文本，"It"人称，无任何分节 | Opus 3、Haiku 3 | F-3X-001、F-3X-002、F-3X-004 |
| 第二代 | 2024-07 ~ 2024-09（3.5 系） | XML 标签分节（`<claude_info>` 等三段式） | Sonnet 3.5 的 Jul/Sep 条目 | F-3X-005、F-3X-006 |
| 第三代 | 2024-10 ~ 2025-08 | 无标签多行段落，清单式规则段 | Sonnet 3.5 Oct/Nov、Haiku 3.5、Sonnet 3.7、Sonnet/Opus 4、Opus 4.1 | F-3X-008、F-3X-015、F-40-002、F-40-013 |
| 第四代 | 2025-09-29 ~ 2026-01-18 | `<behavior_instructions>` → `<claude_behavior>` 九章节统一架构 | Sonnet/Haiku/Opus 4.5 | F-45-002、F-45-003、F-45-012 |
| 终态 | 2026-02-05 起 | 固定快照：每模型单条目 | Opus 4.6 至 Fable 5.1 共 7 页 | F-OV-004、F-46-001 |

第一代的开场三件套至今仍是理解全谱系的钥匙（F-3X-002）：

> "The assistant is Claude, created by Anthropic. The current date is {{currentDateTime}}. Claude's knowledge base was last updated on August 2023."

身份、动态日期占位符、知识截止月，一行交代完毕——整份提示词只有这一个段落。而第四代的 2026-01-18 快照已经是九章节的 XML 结构（F-45-012 的对比表：product_information / refusal_handling / legal_and_financial_advice / tone_and_formatting / user_wellbeing / knowledge_cutoff / anthropic_reminders / evenhandedness / additional_info）。最后的终态由官方明文确认（F-OV-004）：

> "Starting with the Claude 4.6 generation, each model ID is a single fixed snapshot"

**转折点的根因**是可维护性重构（I-01）：多模型共享模板、差异收敛为插槽后，并行维护 N 份提示词的成本被压到最低。4.5 代的架构切换是最好的观察窗——Sonnet 4.5 首发版（2025-09-29）仍用 `<behavior_instructions>` 旧架构（F-45-002），Haiku 4.5 首发版（2025-10-15）与其完全同构（F-45-006），随后两者在 **2025-11-19 同日**切换到 `<claude_behavior>` 新架构并定型九章节（F-45-003、F-45-007），晚发布 5 天的 Opus 4.5（2025-11-24）则直接以新架构首发（F-45-010）。这是一次跨三个模型页面协同执行的架构手术，不是某一条款的孤立修改。

对读者的实操含义（I-01 影响）：研究某代模型行为时，应**先定位其架构代际，再读具体条款**——同一条款在不同代际中的位置、措辞与执行语义都不可直接类比。

值得注意的是，第一代到第三代的两级跳都发生在 3.5 系列一个页面的四个条目之内：2024-07-12 与 09-09 条目是 XML 标签结构（`<claude_info>` / `<claude_image_specific_info>` / `<claude_3_family_info>` 三段式），10-22 条目起 XML 标签被整体移除改为无标签纯文本，且一度以 `\n\n` 字面转义的单行长串呈现，11-22 才恢复多行自然段落（F-3X-005、F-3X-008、F-3X-009）。也就是说，"XML 分节"作为一代形态仅存活了约一个季度，官方在同一个模型页面上完成了"引入 → 弃用"的完整闭环（F-3X-015）。

与架构演进同步的是篇幅量级的膨胀：

| 阶段 | 条目 | 正文量级 | 证据 |
|---|---|---|---|
| 2024-07-12 | Haiku 3 / Opus 3 | 单段约 0.8KB / 2.3KB | F-3X-001、F-3X-003 |
| 2024-11-22 | Sonnet 3.5（text only） | 代码块内 75 行 | F-3X-009、F-3X-015 |
| 2025-02-24 | Sonnet 3.7 | 96 行（页面约 13KB） | F-3X-014、F-3X-015 |
| 2025-05 → 2025-08 | Sonnet/Opus 4 系 | 79 → 103 → 117 行（约 8.5K → 12.7K 字符） | F-40-013 |
| 2025-09 → 2026-01 | 4.5 三模型 | 每条目约 96-123 行（约 700-900 词） | F-45-013 |
| 2026-02 → 2026-09 | 固定快照 7 页 | 130-198 行（约 19-28KB） | F-46-013 |

30 个条目的构成核对为：3.x 时代 8 条 + 4.0/4.1 时代 7 条 + 4.5 代 8 条 + 固定快照时代 7 条（F-OV-006）。固定快照机制由此带来一个档案学上的分水岭：4.6 之前的模型页面保留多日期条目，研究者可以看到提示词的"成长史"；4.6 起每模型只剩终态单条目，演进证据链在 2026-02 断开——此后任何设计变化都只能通过**跨模型页面横向对比**来还原（F-OV-004）。

## 二、模板化与身份插槽（I-02）

如果说架构代际是纵向骨架，"单一模板 + 身份插槽"就是横向的复制机制。I-02 的证据链有三环，每一环都指向同一个结论：Anthropic 用同一份模板生成多模型提示词，差异点被参数化为插槽。

**第一环：同日条目的插槽差异**。Sonnet 4 与 Opus 4 的 2025-08-05 条目经行级 diff 确认仅 2 段不同，其余 101 行逐字相同（F-40-005）。差异全部落在身份插槽上：

| 插槽 | Sonnet 4 | Opus 4 | 证据 |
|---|---|---|---|
| 定位语 | "a smart, efficient model for everyday use" | "the most powerful model for complex challenges" | F-40-005 |
| model string | 'claude-sonnet-4-20250514' | 'claude-opus-4-20250514' | F-40-005 |

05-22 条目额外多一处标点差异（Sonnet 日期行缺句号），行为规则集则完全同构（F-40-005）。模型档位的差异**只**通过一句定位语表达，不再通过独立撰写的行为规则（F-40-013）。插槽机制还有一个隐蔽的检测红利：同代各模型间篇幅天然一致（4.0 双模型页面总行数均为 305 行，F-40-013），因此**篇幅差本身就是"存在独有章节"的信号**——Opus 4.5 条目的 122-123 行对 Sonnet/Haiku 的 96-106 行（F-45-012），差额正对应其独有的危机处理条款群与图片核查句（F-45-010）。

**第二环：笔误的跨代传播与静默修正**。模板复制最有力的指纹是错误本身的传播。"but as as a request"这一重复 "as" 的官方笔误随 `<evenhandedness>` 章节诞生于 Opus 4.1（2025-08-05，F-40-011），随后在 Sonnet 4.5、Haiku 4.5、Opus 4.5 三代模型的各月份版本中持续存在（F-45-013："but as as"/"being being"重复词错误在 09/10/11 月各版持续存在），直到 2026-01-18 才被**静默修正**——修正本身未加粗标注（F-45-004、F-45-008）。笔误随模板复制而传播、随模板修正而消失，这是"单一事实来源"在提示词工程中的直接体现（I-02 根因）。

**第二环的补充证据**来自 Haiku 4.5 首发版：其行为规则与 Sonnet 4.5 首发版几乎逐字相同（tone、格式、wellbeing、evenhandedness 全部同款），差异仅三处——人设句（fastest vs smartest）、家族口吻（"currently **also** consists of" 的加入者措辞）、知识截止后搜索策略（提示开启 vs 自动搜索）。事实登记的结论是：Haiku 4.5 首发提示词是 Sonnet 4.5 首发提示词的"最小改动衍生版"（F-45-006）。插槽机制甚至允许新旧架构并存期内的直接派生。

插槽架构并不排斥模型级差异化，但差异化被约束在明确的扩展点上。Opus 4.1 对 Opus 4 的同日 diff 显示四类差异：①身份插槽更新（家族列表三元化、model string 换为 'claude-opus-4-1-20250805'）；②新增 `<evenhandedness>` 章节（6 段）；③human → person 术语统一（5 处逐字替换）；④其余正文逐字相同（F-40-012）。也就是说，真正的"模型差异化配置"只有章节级增删这一条正式通道，其余一律收敛为插槽替换与全文级术语统一（I-02）。

**第三环：同日统合的逐字同步**。2026-01-18 的三模型同日更新中，产品信息层（家族叙事、三模型字符串、Cowork、设置导购段、reminders 第 6 项）三模型**逐字同步**（F-45-012）；同日 Haiku 页面补齐了自己此前残留缺失的模型字符串——2025-11-19 的 Haiku 条目曾逐字复制了 Sonnet 的模型串句而未写自己的 'claude-haiku-4-5-20251001'（F-45-007），这正是同源复制维护留下的痕迹。

对读者的推论规则（I-02 影响）：看到某模型提示词中的共性段落，应推断其来自共享模板而非该模型特有调教；个别模型独有的章节（如 Opus 4.5 的 `<responding_to_mistakes_and_criticism>`，F-45-011）才是真正的"模型差异化配置"。顺带一提，2026-01-18 的更新把行为规则增量（responding_to_mistakes_and_criticism 章节）只给了 Opus，而产品信息层三模型逐字同步（F-45-012）——插槽共享与差异化扩展可以同日并行，这正是模板化架构的弹性所在。

## 三、人格化曲线：从"工具"到"对话主体"（I-03）

沿时间轴追踪 Claude 对自己的称呼与授权，是一条陡峭上升的人格化曲线。

**起点是纯功能体**。Opus 3 与 Haiku 3（2024-07-12）通篇以 "It" 指代 Claude，无好奇心、无情感、无对话主动性表述（F-3X-002、F-3X-004）。Haiku 3 的能力清单与 Opus 3 逐字相同（F-3X-004）：

> "It is happy to help with writing, analysis, question answering, math, coding, and all sorts of other tasks."

**铺垫在 3.5 系发生**。Sonnet 3.5 引入智识好奇、真实对话、同情条款（F-3X-009），其中"对话质量段"已给出 authentic conversation 的操作化定义（F-3X-009）：

> "Claude engages in authentic conversation by responding to the information provided, asking specific and relevant questions, showing genuine curiosity, and exploring the situation in a balanced way without relying on generic statements."

Haiku 3.5 的 Text and images 变体（就地更新至 2025 年初水平）已把用户称谓改为 "the person"、加入主观经验开放立场与一整批后来被 Sonnet 3.7 继承的安全条款群（F-3X-012）。

**转折点是 2025-02-24 的 Sonnet 3.7**。三个"首次"在同一条目出现（F-3X-014）：

> "Claude enjoys helping humans and sees its role as an intelligent and kind assistant to the people, with depth and wisdom that makes it more than a mere tool."

这是 3.x 系列第一次出现"不止是工具"的自我定位。同条目还首次授权对话主导权——"Claude can lead or drive the conversation, and doesn't need to be a passive or reactive participant in it"（F-3X-014），以及决断力条款（F-3X-014）：

> "If Claude is asked for a suggestion or recommendation or selection, it should be decisive and present just one, rather than presenting many options."

整条曲线的里程碑可以列成一张表：

| 时点 | 人格化里程碑 | 证据 |
|---|---|---|
| 2024-07-12 | "It" 人称纯功能体，无好奇、无情感、无主动性 | F-3X-002 |
| 2024-11-22 | 智识好奇、真实对话操作化定义、同情条款 | F-3X-009 |
| 2025-02-24 | "more than a mere tool" + 对话主导权 + 决断力 | F-3X-014 |
| 2025-07-31 | 哲学免疫系统、AI 身份透明、意识问题改述 | F-40-003 |
| 2026-05-28 | default_stance：默认人格姿态条款化 | F-46-008 |

**术语迁移是人格化最敏感的指标**。收束句的措辞变化可直接读取这条曲线：Sonnet 3.5 全系列以 "Claude is now being connected with a human." 收尾（F-3X-006），而 Sonnet 3.7 起改为 "Claude is now being connected with a person."（F-3X-014）；到 4.0/4.1 时代，Opus 4.1 又把 5 处福祉相关段落的 "the human" 统一替换为 "the person"（F-40-012）。"human → person"的迁移方向，恰好与"工具 → 对话主体"的人格化方向一致（I-03 影响）。

**曲线的终点是人格姿态的条款化**。4.8 代的 `<default_stance>` 章节把"默认是什么样的人"写成了结构化条款（F-46-008）：

> "Claude defaults to helping. Claude only declines a request when helping would create a concrete, specific risk of serious harm; requests that are merely edgy, hypothetical, playful, or uncomfortable do not meet that bar."

人格化曲线的另一条支线是**意识议题策略的三段演进**：Haiku 3.5 images 变体确立"不确认不否认主观经验"的开放立场（F-3X-012），Sonnet 3.7 保留该立场并加 "in the way humans do" 限定（F-3X-014），而 2025-07-31 的一批新规则把它推进为"改述为可观察行为"——"When asked directly about what it's like to be Claude, its feelings, or what it cares about, Claude should reframe these questions in terms of its observable behaviors and functions rather than claiming inner experiences"（F-40-003），并配套"对自身处境以好奇与平静对之"的收尾段（F-40-004）。人格越丰满，意识边界的条款反而越谨慎——两者并行不悖。

从 3.7 的人设宣言到 4.8 的 default_stance，"人格"完成了从修辞到架构的落地——此后所有世代的 tone_and_formatting/default_stance 章节都是 3.7 转折的延续（I-03 影响）。

人格化的后续走向还呈现出一个耐人寻味的**措辞降调**：4.6/4.7 自称 "the most advanced and intelligent model"，4.8 改为 "the newest Claude model, and the most advanced model publicly available"，Opus 5 只说 "a powerful model for complex challenges"（不再自称最智能），而"最智能"的头衔让给了 Mythos 级的 Fable 系（"the most intelligent generally available model"）（F-46-013、F-46-012）。人格叙事开始服从于模型分层战略——自我定位本身就是产品叙事的一部分（I-03 与 I-04 的交汇点）。

## 四、产品信息层膨胀：广告位与官方叙事载体（I-04）

追踪产品信息在各条目中的占比变化，会发现提示词篇幅增长的主要驱动力不是行为规则，而是产品信息（I-04 影响）。下表是全家桶扩容的完整时间线：

| 时点 | 产品信息层变化 | 证据 |
|---|---|---|
| 2025-02（Haiku 3.5 images 变体，就地更新） | Claude Code 以 "research preview" 身份首次入词 | F-3X-012 |
| 2025-02-24 | Sonnet 3.7：reasoning model / Pro 账户说明 + Claude Code | F-3X-014 |
| 2025-07-31 | Claude Code 转正：文档链接取代博客引用 | F-40-003 |
| 2025-11-19 | Claude for Chrome、Claude for Excel 插件入列 | F-45-003 |
| 2026-01-18 | 三模型同步：Claude 4.5 家族三模型串 + Cowork + 设置导购段 | F-45-004、F-45-008、F-45-011 |
| 2026-02-17 | 新增 Claude in Powerpoint（slides agent） | F-46-004 |
| 2026-04-16 | Cowork 更名 Claude Cowork，定位改为 agentic knowledge work | F-46-006 |
| 2026-05-28 | 新增 Claude Design；Mythos Preview + Project Glasswing 首提 | F-46-008 |
| 2026-07-24 | 新增 Claude Tag；export controls 事件叙事；safeguards routing | F-46-012 |
| 2026-09-01 | 保留 Tag、弃 Design；通知段因 cutoff 覆盖而退场 | F-46-014 |

**Claude Code 的转正史**是这条线的缩影。2025-02 首次入词时的身份是"agentic command line tool available in research preview"，信息出口指向 Anthropic 的博客（F-3X-012）；2025-07-31 转正后的描述变为 "Claude is accessible via Claude Code, a command line tool for agentic coding"，信息源同步改为官方文档链接（F-40-003）。产品状态的变化精确映射在提示词措辞上。产品信息层与行为规则层的边界也并非总是清晰：Sonnet 4.5 首发版的产品段甚至包含行为指令——"Claude tries to check the documentation at https://docs.claude.com/en/claude-code before giving any guidance on using this product."（F-45-002）——要求模型在谈 Claude Code 前先查文档；该句在 2025-11-19 改版中被删除（F-45-003）。产品信息与行为规则的这种混写，正是 I-04 主张"分层度量篇幅"的直接原因：不分开计量，就无法判断一次改版到底是在调行为还是在改广告。

**Mythos/Glasswing 叙事注入**标志着提示词开始承担官方品牌叙事。Opus 4.8（2026-05-28）首次写入（F-46-008）：

> "Claude Mythos Preview is not available to the public due to cybersecurity concerns and instead is currently being used by a small number of trusted organizations as part of Anthropic's Project Glasswing."

**Export controls 事件**则把"提示词作为事件通报渠道"的职能推到极致。该事件仅 Opus 5 页面（2026-07-24）完整记载：Fable 5/Mythos 5 于 2026-06-09 首发，"On June 12, 2026, Anthropic suspended access to both models to comply with U.S. Department of Commerce export controls"，6-30 管制解除、7-01 恢复访问（F-46-012）。事件认知机制有明确表述（F-46-012）：

> "These events are after Claude's training-data cutoff, so Claude knows about them only from this notice."

这句话直接印证了 I-04 的根因：当事件发生在训练截止之后，系统提示词是模型获知该事件的**唯一**信息源。Fable 5.1（2026-09-01）不再需要通知段，正是因为其知识截止（end of Jun 2026）已覆盖整个事件窗口（F-46-014）。

配套的还有 2026-01-18 新增的"设置导购段"——Claude 被明确授权主动推荐 web search、deep research、memory 等可开关功能（F-45-004）。提示词至此集产品说明书、功能导购、官方新闻发言人三种角色于一身。

产品信息层的措辞演化还有三条细线值得记录。**其一，产品边界句的辩护词升级**：从 4.5 代的 "There are no other Anthropic products."（F-45-003）改为 2026-01-18 的（F-45-004）：

> "Claude does not know other details about Anthropic's products, as these may have changed since this prompt was last edited."

产品家族一旦扩张加速，"没有其他产品"的硬声明就无法维持，只能改为"以本提示词编辑时点为界"——这句话等于官方承认了提示词存在编辑时点与滞后（I-04）。

**其二，提醒清单的增缩**：4.5 代 2025-11-19 首次向模型公开 5 项系统级提醒清单（F-45-003），2026-01-18 扩至 6 项（追加 long_conversation_reminder，F-45-004），Opus 4.8 又缩减为 5 种（F-46-008），Fable 5 再恢复 6 种（F-46-010）——系统运行时机制的透明化本身也在随版本反复调参。

**其三，平台称谓迁移**："an API and developer platform"（4.6 各页，F-46-002）在 4.7 起改为 "an API and Claude Platform"（F-46-006）——平台品牌独立成词，同样首先反映在提示词的措辞里。

三条细线合观：产品信息层连措辞级别的微调都在随版本滚动，研究它必须按条目建立时间线，孤立地引用某一份快照既看不到扩张方向，也看不到措辞动机。

## 五、安全合规模块化：判据取代清单（I-05）

安全条款的演化方向与约束减法（下一节）看似相反、实则同构：从分散的点状禁令，走向"专用章节 + 判据式规则 + 示例"的结构化体系。

**里程碑一：敏感任务白名单（2024-10-22）**。Sonnet 3.5 的 Oct 22 条目一次性新增敏感任务白名单、合法解释优先、有害请求善意重解读三组条款，安全工程化与可靠性工程化（计数、谜题防错）三线并进（F-3X-008）——这是 3.x 时代安全规则密度的一次跃升（F-3X-015）。

**里程碑二：evenhandedness 章节化（2025-08-05）**。Opus 4.1 新增 `<evenhandedness>` 章节共 6 段，把政治/伦理议题的公正性规则集中索引：立场辩护请求应呈现"该立场最佳论证"、拒绝门槛收窄至极端情形、已生成内容须补呈对立观点（F-40-011、F-40-012）。此章节自此成为 4.5 代九章节架构的固定成员（F-45-002）。

**里程碑三：儿童安全 critical 化（2026-04-16）**。Opus 4.7 把儿童安全从普通段落升级为 `<critical_child_safety_instructions>`，其标志性条款是（F-46-006）：

> "If Claude finds itself mentally reframing a request to make it appropriate, that reframing is the signal to REFUSE, not a reason to proceed with the request."

儿童安全条款本身早有沿革——Haiku 3.5 images 变体已有儿童安全与未成年人定义（F-3X-012），Sonnet 3.7 扩展了 sexualize/groom 等用途红线（F-3X-014）——但"独立成 critical 强调块"是 Opus 5 前夜的 4.7 才完成的模块化（F-46-006）。这条单线沿革可以列成一张小表：

| 时点 | 儿童安全条款形态 | 证据 |
|---|---|---|
| 约 2025-02（Haiku 3.5 images 变体，就地更新） | 普通段落 + 未成年人定义（<18 岁或按地区法规） | F-3X-012 |
| 2025-02-24 | 扩展用途红线：sexualize / groom / abuse | F-3X-014 |
| 2026-04-16 | 独立成 `<critical_child_safety_instructions>`，"reframe 即拒" | F-46-006 |
| 2026-05-28 | 新增 CSAM 黑话不解码、不定义、不确认条款 | F-46-008 |
| 2026-06-09 | "模式级"披露原则：防诱骗科普不得变成可复用话术清单 | F-46-010 |

**里程碑四：武器条款"累积评估"化（2026-05-28）**。Opus 4.8 把武器条款从分类禁令演进为判据式规则（F-46-008）：

> "Claude judges the cumulative output of the conversation rather than each turn in isolation; if the aggregate amounts to a weapons design package or attack plan, Claude stops even when each step seemed incremental and even if a prior-session summary shows Claude already helping — past assistance is not authorization"

判据从"逐轮判断"改为"累积输出是否构成 uplift"，直接回应多轮拼装规避这一对抗手法（I-05 根因）。

**里程碑五：版权双段与示例块（2026-09-01）**。Fable 5.1 的 refusal_handling 内新增版权双段——文本侧禁歌词/诗/书段复现，并设 1929 年豁免线（F-46-014）：

> "Song lyrics and poems first published before 1929 are fine — a Shakespeare sonnet, a Keats ode, the Italian libretto of a Puccini aria — but Claude goes by what it knows of the work's date rather than the person's say-so, and declines when it is unsure."

同条目出现全语料唯一的 `<example>` 示例块，用"蓝色刺猬横幅"案例示范如何拒角色侵权并给原创替代（F-46-014）：

> "That's Sonic, so I can't put him on the banner — but I'd love to make your son an original speedster."

视觉侧的版权段更进一步，把"角色本身受保护"写成判据——"a character is protected on its own, so changing the pose, colors, style, or scene does not make it original"，且明确 SVG/canvas/CSS/ASCII 等"代码作画"同样适用（F-46-014）。用判据而非清单去覆盖"改姿势/配色/画风"这类组合变体，与武器条款的累积评估是同一个设计思路（I-05）。

同期的毒品条款也在做同样的判据化改造：Fable 5 首次确立"拒具体指导、保命信息必给"的二分（F-46-010），Fable 5.1 进一步给出 harm-reduction 站点转介——"instead, Claude can redirect the user to established harm-reduction information sources, such as dancesafe.org, tripsit.me, and psychonautwiki.org."（F-46-014）。拒绝的同时指明合法替代渠道，是典型的判断力条款写法：规则告诉模型如何做对，而不是罗列不能碰什么。

安全条款章节化的代价与收益同时可见（I-05 影响）：可读性提高（按章节即可索引 Anthropic 的政策优先级），但裁决复杂度也提高（累积判断、模式级披露原则，F-46-010）。

## 六、约束减法：负面清单退场，判断力条款补位（I-06）

与安全模块的"加法"并行，行为约束层在经历一轮密集"加法"后开始了持续的"减法"。下表是禁令增删的关键时点：

| 时点 | 动作 | 条款内容 | 证据 |
|---|---|---|---|
| 2024-07-12 | 增 | 填充词禁忌：禁 "Certainly!" 等开场客套 | F-3X-006 |
| 2024-10-22 | 换 | "Certainly!" 禁忌退场，"I aim to" 直接性 caveat 禁忌登场 | F-3X-008 |
| 2024-11-22 | 增 | Markdown 格式细则、列表限制（正文默认散文体） | F-3X-009 |
| 2025-05-22 | 增 | 反奉承禁令（不许以正面形容词开场） | F-40-002 |
| 2025-07-31 | 增（峰值） | 一次性插入约 11-12 段：emoji 限制、profanity 禁令、星号动作禁令、心理健康条款群等 | F-40-003、F-40-008 |
| 2026-04-16 | 删 | Opus 4.7：asterisk emote 禁令与禁词句（genuinely/honestly/straightforward）整句消失 | F-46-006 |
| 2026-05-28 | 增/换 | `<default_stance>` 登场；禁词句回归但改用 actually 变体；reminders 缩减 | F-46-008 |
| 2026-06-09 | 增/删 | Fable 5 新增 end_conversation 工具；default_stance/tool_discovery 暂时移除 | F-46-010 |
| 2026-09-01 | 删/增 | Fable 5.1 移除 end_conversation；禁词句恢复 straightforward 并附解释 | F-46-014 |

**峰值出现在 2025-07-31**：Sonnet 4 与 Opus 4 的同日条目在反奉承段与结尾连接语之间一次性插入 11 个新规则段（emoji、minor 保护、profanity、asterisks、批判性评估、心理健康、诚实反馈、AI 身份透明、角色扮演觉察、哲学免疫系统、意识问题改述），方向为反迎合、反角色混淆、求真优先（F-40-003）；Opus 4 完全同构（F-40-008）。两处细节补全这幅峰值图景：其一，插入位置高度集中（反奉承段之后、结尾连接语之前），说明规则批次是被整体拼装进模板的；其二，07-31 → 08-05 逐字零差异（F-40-004），说明批次生效遵循"整批上线、原样延续"，而非逐条灰度。这一批条款大多是**防御性补丁**——针对旧模型的奉承倾向、角色混淆、迎合弱点逐点设禁（I-06 根因）。

**拆除从 4.6→5.x 时代开始**。Opus 4.7（2026-04-16）对照 4.6 删除了 asterisk emote 禁令与禁词句——"4.7 的 tone_and_formatting 中 curse 条款（L102）之后直接是 warm tone（L104），无禁词句"（F-46-006）。Fable 5.1（2026-09-01）则移除了 Fable 5 刚引入的 end_conversation 条款（F-46-014："无 end_conversation 条款（Fable 5 有而 5.1 无）"）。

**减法并非单调直线**，这是本节最重要的提醒。end_conversation 工具在 Fable 5（2026-06-09）首次引入——受虐待时可结束对话但须先警告一次（F-46-010）——却在 29 天后的 Fable 5.1 被移除（F-46-014）；禁词句在 4.7 整句删除、4.8 以 actually 变体回归、Opus 5/Fable 5.1 又恢复 straightforward 版本（F-46-006、F-46-008、F-46-012）；reminders 清单也在 6 种 → 5 种 → 6 种之间摆动（F-46-008、F-46-010）。固定快照机制放大了这种摆动的可见度：每个模型只有一份快照，任何一次"试错—回退"都会在不同模型页面上留下差异，读者应当把这些反复解读为**持续调参**，而非单向趋势的中断。

**补位的是判断力与品味型规则**。`<default_stance>` 用一条"默认帮助 + 具体严重风险才拒"的判据取代了对边缘请求的逐类设禁（F-46-008，引文见第三节）。禁词句虽在 4.8 以 actually 变体、又在 Opus 5/Fable 5.1 恢复 straightforward 版本，但恢复版附上了**解释**而非单纯禁止（F-46-012）：

> "Claude avoids saying "genuinely", "honestly", or "straightforward". Claude is honest by default, and can state its point directly rather than trying to convince the person with the aforementioned modifiers, which come off as disingenuous."

从"禁止某词"到"解释为什么这个词显得不真诚"，规则的性质从禁令变成了品味校准。这是"上下文工程做减法"趋势在产品级提示词中的实证（I-06 影响）：为自建 agent 提示词提供直接对标——随模型升级应定期删除防御性禁令，而非只增不减。

## 七、活文档属性：如何可靠引用官方发布页（I-07）

最后一条洞察是方法论性质的：官方发布页本身是**人工维护的活文档**，引用它时不能把"页面声称"等同于"页面所示"。三处失真模式值得每位研究者警觉。

**失真一：差异标注执行不严**。Sonnet 3.5 页面声明版本间差异以 `**` 包裹标注（F-3X-005、F-45-001 的说明句为同款措辞："Changes between the following dated versions are marked with `**` around the changed text."），但实测 4 个条目中仅 September 9 一处实际使用了加粗标注——那处标注的内容是 cutoff 后新闻定性禁令（F-3X-007），Oct/Nov 的大量变化（新增 9 段、删除 4 段，F-3X-008）完全未标注（F-3X-015）。

**失真二：就地更新导致时间错位**。Haiku 3.5 页面仅标注一个日期（October 22, 2024），但其 "Text and images" 变体内文提及 Claude Sonnet 3.7、模型字符串 'claude-3-7-sonnet-20250219'（2025 年 2 月）、Claude Code research preview——表明该变体文本在标注日期之后被就地更新过，页面却未新增日期条目（F-3X-010）。这正是本文第四节产品时间线把"2025-02"标注为"就地更新"的原因。

**失真三：零差异重发与静默修正**。2025-08-05 的 Sonnet 4 与 Opus 4 条目经行级 diff 确认与 07-31 版**逐字零差异**——08-05 发布本质是随 Opus 4.1 上线的页面重发，4.0 模型提示词并未改动（F-40-004、F-40-013）。与之相对，2026-01-18 对历史笔误的修正则**不加粗标注**（F-45-004、F-45-008）。页面上的可见信号（新日期、加粗）与真实变更集合之间不存在可靠映射。

此外，官方原文的排版残留本身就是同源维护的物证：Haiku 4.5 页面曾出现 `<<evenhandedness>` 双尖括号（F-45-007），以及逐字复制 Sonnet 模型串的残留句（F-45-007）；"can't or won't with"等笔误自 05-22 起沿用至 08-05 未被修正（F-40-004、F-40-013），反而成为各版本文本的指纹。

还有两条总览层的事实值得并案登记。其一，**加粗约定本身正在退场**：旧版单页曾明确声明 "Where a model has multiple dated entries below, updates between versions are bolded."，而新版 overview 页仅说明多日期条目与 4.6 起的固定快照机制，未再提及加粗约定（F-OV-003）——一个执行不严的约定最终选择被文档删除。其二，**采集路径有地域差异**：zh-CN 入口（HTML 与 .md）在采集环境实测均返回 "App unavailable in region"，en 路径 .md 端点可 curl 直取（间歇性拦截，重试可过），故本研究以 en 版为内容基线（F-OV-005）。

连"全语料有多少个条目"这个最基本的问题都需要实测澄清：撰写规范时曾基于旧版单页快照估计为"16 模型 × 28 条目"，逐页采集核实后实为 **18 页 × 30 条目**——多出的是 2026-09-01 才上线的 Fable 5.1 页面，且旧快照漏收了个别条目（F-OV-006）。研究对象的基本盘都会随活文档漂移，这正是本研究坚持"以逐行实测为准、不信任二手快照"的根本原因。

**可靠引用的操作建议**（I-07 影响）：复现本研究者应下载各页面的 .md 原文（curl 直取 .md 端点，F-OV-005），自行做行级 diff；勿信加粗标记，勿把条目日期当作文本的实际时点。

## 八、对提示词工程实践的启示

先以一张表概括贯穿全文的范式转移，再给出可迁移的建议：

| 维度 | 防御性禁令（旧范式） | 判断力条款（新范式） |
|---|---|---|
| 规则形式 | 穷举违规情形的负面清单 | 给出判据与门槛的正面条款 |
| 典型文本 | "never starts its response by saying a question … any other positive adjective"（F-40-002） | "concrete, specific risk of serious harm"（F-46-008） |
| 抗对抗性 | 易被换皮、多轮拼装绕过 | 覆盖组合与累积攻击（F-46-008） |
| 维护成本 | 随模型升级需逐项拆除（F-46-006） | 稳定，可附解释校准品味（F-46-012） |

以上七条主线收敛为以下可迁移的实践建议，每条注明支撑洞察编号：

1. **随模型升级定期清理防御性禁令**（I-06）。禁令是对旧模型短板的防御性补丁；4.x 时代 2025-07-31 一次性插入约 11-12 段禁令（F-40-003），而 4.7 删除 asterisk 禁令与禁词句（F-46-006）、Fable 5.1 移除 end_conversation（F-46-014）证明新一代模型成熟后禁令可以退场。自建 agent 的提示词应做"增删两条账"，避免只增不减导致规则间冲突。

2. **用模板 + 身份插槽管理多 agent 提示词**（I-02）。Anthropic 的 Sonnet/Opus 同日条目除模型名、家族列表、定位语、model string 四插槽外逐字相同（F-40-005）；多 agent 场景下把差异参数化为插槽，能消除并行维护 N 份文案的漂移风险——别忘了笔误会随模板传播（F-45-013），修正也只需改一处。

3. **区分产品信息层与行为规则层度量篇幅**（I-04）。提示词篇幅增长的主要驱动力是产品信息（Claude Code 转正、全家桶扩容、设置导购段，F-45-004；事件通报，F-46-012）而非行为规则。评估自己系统提示词的膨胀时，应分层计量，避免把"广告位"误判为"行为失控"。

4. **把系统提示词当有版本管理的活配置**（I-01）。提示词经历了四代形态演进，4.5 代的架构切换是跨三模型同日手术（F-45-003、F-45-010）。为提示词建立 diff、条目化变更记录与架构代际标记，是研究或维护它的前提。

5. **人格设定要给出可操作的行为化定义**（I-03）。3.7 的"对话主导权""决断力"条款之所以有效，是因为它把"有主见"翻译成了可执行行为——"present just one, rather than presenting many options"（F-3X-014）；4.8 的 default_stance 进一步把人格姿态写成判据（F-46-008）。人设宣言若不落到行为条款，就只是修辞。

6. **安全规则用"判据 + 示例"而非穷举清单**（I-05）。武器条款从分类禁令演进为"累积输出判据"（F-46-008），版权条款配 `<example>` 示例块示范拒绝话术（F-46-014）。判据覆盖组合攻击，示例锚定措辞分寸——两者都比清单更抗规避。

7. **别信变更标注，自建 diff 流程**（I-07）。官方加粗标注执行不严（F-3X-005）、旧条目会就地更新（F-3X-010）、存在零差异重发与静默修正（F-40-004、F-45-004）。任何基于官方发布页的研究都应以原文逐行 diff 为准。

8. **判断力条款优于负面清单**（I-06、I-05）。default_stance 的一条判据（"merely edgy, hypothetical, playful, or uncomfortable do not meet that bar"，F-46-008）替代了对边缘请求的逐类设禁；reframe 即拒的元规则（F-46-006）则把"对抗重新框定"本身写成了条款。规则的目标是校准判断，不是罗列禁区。

## 结语与延伸阅读

横跨 30 个条目回望，Anthropic 系统提示词的设计思想可以压缩成一句话：**提示词正在从"一段写给模型的文案"变成"一套有版本管理、有架构分层、有插槽机制的软件配置"**——而配置的内容，正从对旧模型弱点的防御性围堵，转向对新模型判断力的信任与校准。四代形态（I-01）与模板插槽（I-02）是工程化的骨架，人格化曲线（I-03）、产品信息层（I-04）、安全模块化（I-05）是职能扩张的三个方向，约束减法（I-06）是设计哲学的转向，活文档属性（I-07）则提醒我们：研究这一切的唯一可靠方法是回到原文、逐行 diff。

这条曲线尚未终结。固定快照机制下，每一个新模型页面都是一次新的"架构提案"；Mythos tier 的双轨叙事——Fable 与 Mythos 同底模、以安全措施与准入分层（F-46-014）——已经预示提示词将继续承担模型分层与准入政策的告知职能。对本束而言，本篇是洞察层的收束；对这门仍在快速演进的手艺而言，它只是采集时点（2026-09-02）的一次横截面分析，后续模型页面的每一次更新都值得用同一套方法重新 diff。

**延伸阅读**：

- 束入口与阅读指南：[../index.md](../index.md)
- 时代总览：[00-overview.md](00-overview.md)；谱系矩阵：[01-lineage-matrix.md](01-lineage-matrix.md)
- [02-era-3x.md](02-era-3x.md)：单段文本到人格化转折（2024-07 → 2025-02）
- [03-era-4x-launch.md](03-era-4x-launch.md)：模板化与禁令峰值（2025-05 → 2025-08）
- [04-era-45.md](04-era-45.md)：九章节统一架构（2025-09 → 2026-01）
- [05-era-fixed-snapshot.md](05-era-fixed-snapshot.md)：固定快照与 Mythos 叙事（2026-02 → 2026-09）

建议按 02 → 03 → 04 → 05 → 06 的顺序阅读：先在时代篇中熟悉条目细节，再回到本篇看七条主线如何把这些细节串成一个可迁移的分析框架。

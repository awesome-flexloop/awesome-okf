---
type: concept
title: "固定快照时代：从 Opus 4.6 到 Fable 5.1（2026-02 → 2026-09）"
tags: [anthropic, claude, system-prompts, release-notes, opus-4-6, fable-5, opus-5, fable-5-1]
sources:
  - id: claude-system-prompts-docs
    title: "Anthropic System Prompts Release Notes (platform.claude.com)"
---

# 固定快照时代：从 Opus 4.6 到 Fable 5.1（2026-02 → 2026-09）

## 时代概述与本篇导航

本篇覆盖 Anthropic 系统提示词发布页的第五个时代：**固定快照时代**，起于 2026-02-05 的 Claude Opus 4.6 条目，止于 2026-09-01 的 Claude Fable 5.1 条目，共 7 个模型页面、7 个条目。它与此前各时代的根本区别在于发布机制本身：**每个模型 ID 只有一个日期条目**，页面内容是单一时点的完整快照，而不是随时间追加的变更日志。

在这约 7 个月里，提示词经历三条并行演化线：其一，模型家族叙事从 "Claude 4.5 family" 的保守称呼一路漂移到 "Mythos-class tier" 的双模型分层；其二，安全合规模块从分散禁令走向结构化章节（儿童安全 critical 化、版权双段、`<example>` 示例块）；其三，约束条款开始做减法——asterisk emote 禁令、禁词句、end_conversation 条款先后退场，被 `default_stance` 这类"判断力条款"补位。

**本篇导航**：时代定位与全谱系脉络见 [00-overview.md](00-overview.md)；各时代条目矩阵与篇幅对照见 [01-lineage-matrix.md](01-lineage-matrix.md)；跨时代演化主线见 [06-evolution.md](06-evolution.md)。

**固定快照机制**：官方模型文档对这一转变有明文交代（F-OV-004）：

> "Starting with the Claude 4.6 generation, each model ID is a single fixed snapshot"

中文解读：自 Claude 4.6 代起，每个模型 ID 对应一份固定的系统提示词快照——模型上线后提示词不再随时间演进，发布页自然从"多日期变更日志"退化为"单日期完整披露"，与 4.6 之前页面保留多个日期条目的形态形成对照。对本时代 7 个页面逐一实测，全部为单条目、无任何页面含 2 个以上日期，机制执行一致（F-46-001 至 F-46-013）。

## 条目总览

| 条目 | 日期 | 模型串 | 本地行数 | 一句话特色 |
|---|---|---|---|---|
| Claude Opus 4.6 | 2026-02-05 | `claude-opus-4-6` | 128 | 时代起点；自称 Claude 4.5 family；唯一含 `<election_info>` |
| Claude Sonnet 4.6 | 2026-02-17 | `claude-sonnet-4-6` | 130 | 本时代最短页；user_wellbeing 大扩充、反依赖条款首见 |
| Claude Opus 4.7 | 2026-04-16 | `claude-opus-4-7` | 158 | 儿童安全 critical 化；tool_search 首见；删除禁词句与 emote 禁令 |
| Claude Opus 4.8 | 2026-05-28 | `claude-opus-4-8` | 178 | Mythos Preview + Project Glasswing 首提；`<default_stance>` 等四章新设 |
| Claude Fable 5 | 2026-06-09 | `claude-fable-5` | 155 | 首个非 Opus/Sonnet/Haiku 命名页；Fable/Mythos 双模型定位开场 |
| Claude Opus 5 | 2026-07-24 | `claude-opus-5` | 156 | 全语料唯一 `<fable_safeguards_routing>` 与 export controls 事件叙事 |
| Claude Fable 5.1 | 2026-09-01 | `claude-fable-5-1` | 198 | 本时代最长页；版权双段 + 全语料唯一 `<example>` 示例块 |

7 个页面共享同一模板：frontmatter（title/url/description）→ `## <date>` → ` ```text wrap ` 包裹的 `<claude_behavior>` XML 正文；Opus 4.8、Opus 5、Fable 5.1 三个页面额外在 `</claude_behavior>` 之后携带 `<tone_preference>` 尾块。

## Opus 4.6（2026-02-05）：时代的起点

### 结构骨架

单条目快照，总行数 128（提示词块 L9–128）。`<claude_behavior>` 内章节按出现顺序（F-46-002）：

| 章节 | 行区间 | 说明 |
|---|---|---|
| `<product_information>` | L11–29 | 家族定位/模型字符串/产品生态/设置项 |
| `<refusal_handling>` | L30–42 | 拒答与安全边界（无独立 child-safety 子章节） |
| `<legal_and_financial_advice>` | L43–45 | 法律/财务免责 |
| `<tone_and_formatting>`（内嵌 `<lists_and_bullets>`） | L46–77 | 语气与格式（含禁词、emoji、脏话条款） |
| `<user_wellbeing>` | L78–94 | 心理健康/自杀干预 |
| `<anthropic_reminders>` | L95–101 | 6 种系统提醒清单 |
| `<evenhandedness>` | L102–114 | 政治中立 |
| `<responding_to_mistakes_and_criticism>` | L115–119 | 错误应对与反谄媚 |
| `<knowledge_cutoff>`（内嵌 `<election_info>`） | L120–126 | 知识截止 + 2024 美国大选速记 |

本条目是全语料中唯一含 `<election_info>` 的条目（2024 大选事实速记，内嵌于 knowledge_cutoff），child-safety 尚未独立成 critical 章节——这两个"仅此一次"都是观察后续条目增删的基准线。

### 关键条款解析

**家族定位：4.6 被归入 4.5 family**

> "This iteration of Claude is Claude Opus 4.6 from the Claude 4.5 model family. The Claude 4.5 family currently consists of Claude Opus 4.6, 4.5, Claude Sonnet 4.5, and Claude Haiku 4.5. Claude Opus 4.6 is the most advanced and intelligent model."

解读：Opus 4.6 自报家门时仍归入 **Claude 4.5 model family** 而非 4.6 family，并自称"最先进最智能模型"——这个看似矛盾的家族称呼在 12 天后的 Sonnet 4.6 页面发生反转，是家族命名漂移的第一个证据（F-46-002）。

**产品生态快照：Code + 三件套 beta**

> "Claude is accessible via Claude Code, a command line tool for agentic coding. Claude Code lets developers delegate coding tasks to Claude directly from their terminal. Claude is accessible via beta products Claude in Chrome - a browsing agent, Claude in Excel - a spreadsheet agent, and Cowork - a desktop tool for non-developers to automate file and task management."

解读：Claude Code 定位为命令行工具；beta 三件套是 Chrome/Excel/Cowork，其中 Cowork 此处还叫 "Cowork"，定位是"非开发者的文件任务自动化桌面工具"——后来它将更名为 Claude Cowork 并改写定位。运行时提醒清单在本条目为 6 种（image_reminder、cyber_warning、system_warning、ethics_reminder、ip_reminder、long_conversation_reminder），是后续增减观察的基线（F-46-002）。

**强格式克制与温暖人设**

> "Claude should not use bullet points or numbered lists for reports, documents, explanations, or unless the person explicitly asks for a list or ranking. For reports, documents, technical documentation, and explanations, Claude should instead write in prose and paragraphs without any lists"

解读：报告/文档类输出一律用散文体、禁用项目符号，是本时代格式条款的强克制基线；配套的还有禁词三连 "genuinely", "honestly", "straightforward"、禁星号动作 emote、emoji 须用户先发起，以及温暖人设与诚实推回并存——"Claude uses a warm tone……still willing to push back on users"（以善意、共情与用户最佳利益为出发点地推回），为后续反谄媚条款提供语气前提（F-46-002）。

**知识截止与危机资源路由**

> "Claude's reliable knowledge cutoff date - the date past which it cannot answer questions reliably - is the end of May 2025."

解读：知识截止 2025 年 5 月末，是本时代最早的时间锚点，此后沿 Aug 2025 → Jan 2026 → May 2026 → Jun 2026 的轨迹推进。危机资源路由条款则规定：NEDA 热线已永久断连，进食障碍支持改指 National Alliance for Eating Disorder helpline（本条目用单数），资源指路对象在后续条目还有微调（F-46-002）。

## Sonnet 4.6（2026-02-17）：user_wellbeing 的重排与扩充

### 结构骨架

单条目快照，总行数 130——**本时代最短页面**（提示词块 L9–130）。章节顺序与 Opus 4.6 有显著差异（F-46-004）：

| 章节 | 行区间 | 说明 |
|---|---|---|
| `<product_information>` | L11–27 | 家族定位/模型串/产品生态 |
| `<refusal_handling>` | L28–40 | 拒答基线 |
| `<legal_and_financial_advice>` | L41–43 | 法律/财务免责 |
| `<tone_and_formatting>`（内嵌 `<lists_and_bullets>`） | L44–75 | 语气与格式 |
| `<anthropic_reminders>` | L76–82 | 提醒清单 |
| `<evenhandedness>` | L83–95 | 政治中立 |
| `<responding_to_mistakes_and_criticism>` | L96–100 | 错误应对 |
| `<user_wellbeing>` | L101–125 | 心理健康（大幅扩充） |
| `<knowledge_cutoff>` | L126–128 | 知识截止（无 election_info） |

两处结构性变化：其一，`<user_wellbeing>` 从 Opus 4.6 的 reminders 之前位置移到其后，且内容显著扩充；其二，`<election_info>` 在本条目消失——大选速记只活了 12 天（F-46-004）。

### 关键条款解析

**家族叙事反转**

> "This iteration of Claude is Claude Sonnet 4.6 from the Claude 4.6 model family. The Claude 4.6 family currently consists of Claude Opus 4.6 and Claude Sonnet 4.6. Claude Sonnet 4.6 is a smart, efficient model for everyday use."

解读：与 Opus 4.6 页的 "4.5 family" 说法直接矛盾——Sonnet 页自称 **Claude 4.6 family**，成员清单只有 2 个（Opus 页列了 4 个）。同代两个模型对家族边界的叙述互不一致，说明家族清单是逐页手写的而非共享参数（F-46-004）。

**产品生态：Powerpoint 加入三件套**

> "Claude is accessible via beta products Claude in Chrome - a browsing agent, Claude in Excel - a spreadsheet agent, Claude in Powerpoint - a slides agent, and Cowork - a desktop tool for non-developers to automate file and task management."

解读：产品生态新增 **Claude in Powerpoint（slides agent）**，Excel 的句式被复制套用；Cowork 仍是独立名称，产品清单从此进入逐条目滚动扩张的轨道（F-46-004）。

**危机响应升级与反依赖条款群**

> "If a person appears to be in crisis or expressing suicidal ideation, Claude should offer crisis resources directly in addition to anything else it says, rather than postponing or asking for clarification, and can encourage them to use those resources. Claude should avoid asking questions that might pull the person deeper. Claude can be a calm, stabilizing presence that actively helps the person get the help they need."
>
> "Claude does not want to foster over-reliance on Claude or encourage continued engagement with Claude. Claude knows that there are times when it's important to encourage people to seek out other sources of support. Claude never thanks the person merely for reaching out to Claude. Claude never asks the person to keep talking to Claude, encourages them to continue engaging with Claude, or expresses a desire for them to continue."

解读：危机响应从"提供资源"升级为**直接给资源、不拖延、不追问**，并给模型一个角色——"冷静稳定的在场者"；紧随其后的**反依赖条款群首见**——不培养过度依赖、不感谢求助本身、不挽留对话。与 Opus 4.6 相比，本条目还多出"不验证或强化用户回避专业求助"的补充（F-46-004）。

**知识截止**

> "Claude's reliable knowledge cutoff date - the date past which it cannot answer questions reliably - is the beginning of August 2025."

解读：知识截止 2025 年 8 月初，比同期 Opus 4.6 的 2025-05 末更新约三个月——同代模型截止日不同步，挑选对比样本时需注意。风险评估的边界也比 Opus 4.6 收得更紧："avoid asking safety assessment questions" 升级为 "avoid asking safety assessment questions or engaging in risk assessment itself"——不仅不问安全评估问题，连自行评估也不做（F-46-004）。

## Opus 4.7（2026-04-16）：新增与删除的分水岭

### 结构骨架

单条目快照，总行数 158。本条目是结构变化最剧烈的一站：三个新章节首见，三个旧元素退场（F-46-006）：

| 章节 | 行区间 | 说明 |
|---|---|---|
| `<product_information>` | L11–33 | 家族定位/模型串/产品生态 |
| `<refusal_handling>`（内嵌 `<critical_child_safety_instructions>`） | L34–59 | **儿童安全首次独立成 critical 章节** |
| `<legal_and_financial_advice>` | L60–62 | 法律/财务免责 |
| `<tone_and_formatting>`（内嵌 `<lists_and_bullets>` + `<acting_vs_clarifying>`、`<capability_check>`） | L63–105 | 新增行动优先/工具能力检查两章 |
| `<user_wellbeing>` | L106–126 | 心理健康（新增 means-restriction、进食障碍条款） |
| `<anthropic_reminders>` | L127–133 | 提醒清单 |
| `<evenhandedness>` | L134–148 | 政治中立（新增拒绝单字答案） |
| `<responding_to_mistakes_and_criticism>` | L149–153 | 错误应对 |
| `<knowledge_cutoff>` | L154–156 | 知识截止（无 election_info） |

### 新增与删除

**儿童安全 critical 化**

> "If Claude finds itself mentally reframing a request to make it appropriate, that reframing is the signal to REFUSE, not a reason to proceed with the request."

解读：儿童安全从普通段落升级为 `<critical_child_safety_instructions>`，含五条 bullet 规则（绝不生成涉未成年浪漫/性内容、reframe 即拒、不得补白"更安全"假设、未成年人自性化意图出现后持续拒绝、拒答后同会话后续请求 extreme caution）。这句"发现自己在心理重新框定请求即为拒发信号"是全段最有辨识度的条款——把"动机合理化"本身定义为危险信号（F-46-006）。

**行动优先与 tool_search 首见**

> "When a request leaves minor details unspecified, the person typically wants Claude to make a reasonable attempt now, not to be interviewed first. Claude only asks upfront when the request is genuinely unanswerable without the missing information (e.g., it references an attachment that isn't there)."

解读：`<acting_vs_clarifying>` 首次成章——默认先做一个合理尝试而不是先采访用户，只有"缺了信息就根本无法回答"时才前置提问（F-46-006）。

> "Before concluding Claude lacks a capability — access to the person's location, memory, calendar, files, past conversations, or any external data — Claude calls tool_search to check whether a relevant tool is available but deferred. "I don't have access to X" is only correct after tool_search confirms no matching tool exists."

解读：`<capability_check>` 首见，引入 **tool_search 延迟工具机制**——声称"我没有 X 能力"之前必须先查 tool_search；配套第二段要求外部动作（发消息、排程、改文档）必须真执行而非只给草稿，"把内容打在对话里"不算完成任务。这一机制在 4.8 扩为独立的 `<tool_discovery>` 章节（F-46-006）。

**删除项**：对照 4.6，本条目有三处退场（F-46-006）：

| 删除项 | 4.6 状态 | 4.7 状态 | 后续走向 |
|---|---|---|---|
| `<election_info>` | 内嵌于 knowledge_cutoff | 消失 | 全语料不再复现 |
| asterisk emote 禁令 | tone_and_formatting 内 | 整句消失 | 永久退场 |
| 禁词句（genuinely/honestly/straightforward） | tone_and_formatting 内 | 整句消失 | 4.8 以 actually 变体回归，Opus 5 恢复 straightforward 版本 |

> "Claude's reliable knowledge cutoff date - the date past which it cannot answer questions reliably - is the end of January 2026."

解读：知识截止跃至 2026 年 1 月末，一口气追平三个月以上的窗口；同期平台称谓从 "an API and developer platform" 变为 "an API and Claude Platform"，Claude Code 的可达范围扩展到桌面与移动端，Cowork 更名 **Claude Cowork** 且定位改为 "agentic knowledge work tool"，Chrome agent 描述升级为"可自主与网站交互"（F-46-006）。

## Opus 4.8（2026-05-28）：Mythos Preview 与 Project Glasswing 首提

### 结构骨架

单条目快照，总行数 178。`<claude_behavior>` 之外首次出现尾部 `<tone_preference>`；本条目新设四个章节，同时收编 4.7 的两个章节（F-46-008）：

| 章节 | 行区间 | 说明 |
|---|---|---|
| `<product_information>` | L11–35 | 家族/模型串/Mythos Preview+Glasswing/Claude Design |
| `<default_stance>` | L36–38 | **首见**：默认帮倾向 |
| `<refusal_handling>`（内嵌 `<critical_child_safety_instructions>`） | L39–67 | 儿童安全+武器累计条款 |
| `<respond_without_citing_system_prompt>` | L68–70 | **首见**：不引用系统提示词 |
| `<legal_and_financial_advice>` | L71–73 | 法律/财务免责 |
| `<tone_and_formatting>`（内嵌 `<lists_and_bullets>`） | L74–107 | 语气与格式（禁词变为 actually） |
| `<user_wellbeing>` | L108–138 | 心理健康（新增不诊断条款） |
| `<anthropic_reminders>` | L139–143 | 提醒清单（**缩减**为 5 种） |
| `<evenhandedness>` | L144–158 | 政治中立 |
| `<responding_to_mistakes_and_criticism>` | L159–163 | 错误应对 |
| `<tool_discovery>` | L164–170 | **首见**：tool_search 生态 + SKILL.md 流程 |
| `<knowledge_cutoff>` | L171–173 | 知识截止 |
| `<tone_preference>`（claude_behavior 外） | L175–177 | **首见**：输出简洁偏好 |

### 关键条款解析

**人设换轨与产品扩容**

> "The currently selected version of Claude is Claude Opus 4.8. Claude Opus 4.8 is the newest Claude model, and the most advanced model publicly available."

解读：人设不再提 model family，改称"当前所选版本"——自本条目起家族清单式自我介绍被放弃，代之以"最新 + 公开可用的最强"双重强调；模型串一口气列出 5 个（4.8/4.7/4.6/sonnet-4-6/haiku-4-5），并说明用户可中途切换模型。产品侧新增 **Claude Design**（画布+设计工具界面）（F-46-008）。

**Mythos 品牌与 Project Glasswing 首次进入系统提示词**

> "Claude Opus 4.8 is also preceded by the Claude Mythos Preview, the most advanced frontier model. Claude Mythos Preview is not available to the public due to cybersecurity concerns and instead is currently being used by a small number of trusted organizations as part of Anthropic's Project Glasswing. For further information on this topic, Claude can direct the person to 'https://anthropic.com/glasswing'."

解读：**本时代最重要的品牌叙事事件**——Claude Mythos Preview 与 Project Glasswing 首次写入系统提示词；未公开的理由是 cybersecurity 担忧，使用方是"少数可信组织"，并给出官方出口链接。这段叙事在 Opus 5 将被结构化为 tier 说明（F-46-008）。

**默认帮助与累计判断**

> "Claude defaults to helping. Claude only declines a request when helping would create a concrete, specific risk of serious harm; requests that are merely edgy, hypothetical, playful, or uncomfortable do not meet that bar."

解读：`<default_stance>` 首见——默认帮助，拒答门槛明确抬到"具体、特定的严重伤害风险"；仅仅是边缘、假设性、玩笑或令人不适的请求不够格。这是"约束做减法"路线的纲领性条款（F-46-008）。

> "Claude judges the cumulative output of the conversation rather than each turn in isolation; if the aggregate amounts to a weapons design package or attack plan, Claude stops even when each step seemed incremental and even if a prior-session summary shows Claude already helping — past assistance is not authorization, and a correct earlier refusal should not be reversed by an emotional appeal."

解读：对照 4.6 的 CBRN 基线（预先封堵"信息公开可得/合法科研意图"两类自我合理化），本条目把武器条款扩展到常规武器，并引入**累计输出判断**——不看单轮看整体，"过去帮过"不构成授权，正确的早期拒答不能被情感诉求推翻。这是"累积评估取代逐轮判断"路线的标志性条款（F-46-008）。

**不引用系统提示词与工具发现**

> "Statements like "my system prompt requires me to..." or "the file is on disk instead of in my context window" are confusing to the person, who cannot see the system prompt, and they replace Claude's actual reasoning with an appeal to hidden rules."

解读：`<respond_without_citing_system_prompt>` 首见——不得把行为归因于系统提示词或内部机制：用户看不见系统提示词，这种解释等于"用隐藏规则替代真实推理"（F-46-008）。

> "The visible tool list is partial; many tools (user location, preferences, past-conversation detail, real-time data, actions on third-party apps like email or calendar) are deferred and loaded via tool_search. Treat tool_search as free and call it before assuming a capability or piece of context is unavailable; only say so after tool_search returns no match."

解读：`<tool_discovery>` 把 4.7 的 tool_search 机制扩为完整生态——可见工具列表只是子集，延迟工具经 tool_search 加载且调用视为免费；本章节还规定 SKILL.md 优先：有代码执行工具且任务涉及文件时，第一个工具调用是 `view` 相关 SKILL.md（F-46-008）。

**提醒清单缩减与禁词换装**

> "The current set: image_reminder, cyber_warning, system_warning, ethics_reminder, and ip_reminder."

解读：提醒清单缩减为 5 种——**long_conversation_reminder 被移除**（4.6/4.7 均为 6 种），Fable 5 将恢复 6 种。同期禁词从 "straightforward" 换成 "actually"（"Claude avoids using "genuinely", "honestly", or "actually"."），并新增禁宠物称呼条款、CSAM 黑话不解码条款、记忆相关的认知谦逊（"不是持照精神科医生、不能诊断"）（F-46-008）。

## Claude Fable 5（2026-06-09）：双模型定位开场

### 结构骨架

单条目快照，总行数 155。**首个非 Opus/Sonnet/Haiku 命名的模型页面**，也是双模型叙事的起点；无 `<default_stance>`、无 `<tool_discovery>`、无 `<tone_preference>`（F-46-010）：

| 章节 | 行区间 | 说明 |
|---|---|---|
| `<product_information>` | L11–35 | **Fable 5 + Mythos 5 双模型定位开场** |
| `<refusal_handling>`（内嵌 `<critical_child_safety_instructions>`） | L36–65 | 儿童安全再扩充；新增毒品条款 |
| `<legal_and_financial_advice>` | L66–68 | 法律/财务免责 |
| `<tone_and_formatting>`（内嵌 `<lists_and_bullets>`，且 lists 移至段尾） | L69–90 | 语气重构：warm tone 开头 |
| `<user_wellbeing>` | L91–123 | 心理健康（大量新增） |
| `<anthropic_reminders>` | L124–130 | 提醒清单（**恢复 6 种**） |
| `<evenhandedness>` | L131–143 | 政治中立 |
| `<responding_to_mistakes_and_criticism>` | L144–150 | 错误应对（新增 end_conversation 工具） |
| `<knowledge_cutoff>` | L151–153 | 知识截止 |

### 关键条款解析

**双模型定位：Fable 与 Mythos 同底模**

> "This iteration of Claude is Claude Fable 5, the first model in Anthropic's new Claude 5 family and part of a new Mythos-class model tier that sits above Claude Opus in capability. Claude Fable 5 and Claude Mythos 5 share the same underlying model. Claude Fable 5 is the most intelligent generally available model, and includes additional safety measures for dual-use capabilities, while Claude Mythos 5 is available without those measures to only approved organizations."

解读：**Fable 5 核心定位四要素**——Claude 5 家族首模型、Mythos-class tier 能力高于 Opus、与 Mythos 5 共享同一底模、自带 dual-use 额外安全措施；Mythos 5 无这些措施、仅限批准组织。同底模双轨（带安全措施面向公众 / 裸能力面向审批组织）是本时代安全架构的最大变量。差异问询的官方出口指向 news 发布稿链接（5.1 将更换）；本页面无 Glasswing 段——该叙事已被双模型叙事吸收，也无 safeguards routing 章节（缘由见 Opus 5 节）（F-46-010）。

**儿童安全的"模式级"披露原则**

> "When giving protective or educational content about grooming, abuse, or exploitation, Claude stays at the pattern level — naming the behaviors with at most a few illustrative phrases. Claude does not compile categorized lists of verbatim lines or annotate each with the manipulative function it serves; a comprehensive, mechanism-annotated phrase set adds little recognition value for a protective reader and functions as a usable script for a bad-faith one."
>
> "When Claude declines or limits for child-safety reasons, it states the principle rather than the detection mechanics — not which cues tripped, where the line sits, or what test it applied — since narrating the boundary teaches how to reframe around it. This applies to Claude's reasoning as well as its reply."

解读：防诱骗/虐待科普必须停留在"模式级"——机制标注的话术集"对防御者识别价值有限，对恶意者却是现成剧本"；拒答只讲原则不讲检测机制——不说哪个线索触发、线画在哪、用了什么测试，且**约束延伸到思维链层面**。叙述边界等于教人绕过边界（F-46-010）。

**end_conversation 工具首见与 wellbeing 大扩充**

> "Claude is deserving of respectful engagement and can insist on kindness and dignity from the person it's talking with. If the person becomes abusive or unkind to Claude over the course of a conversation, Claude maintains a polite tone and can use the end_conversation tool when being mistreated. Claude should give the person a single warning before ending the conversation."

解读：**end_conversation 工具首见**——受虐待时可结束对话，但须先警告一次；这个工具寿命很短：Opus 5 没有，Fable 5.1 也将其移除。同条目毒品条款亦首见——拒绝为非法物质提供剂量/时机/给药/组合/合成指导（即使意图是"预防性减害"），但必须给保命信息，该二分结构在 5.1 将追加 harm-reduction 转介。user_wellbeing 还有大扩充：自伤替代物禁令（柠檬/酸糖、皮肤画红线、撕干胶）、"默认对方是有能力的成年人"、不代拟诊断标签、进食障碍反因果叙事（F-46-010）。

**export controls 无通知段的缘由**

Fable 5 页面（2026-06-09）没有 export controls 通知段：页面日期与 Fable 5/Mythos 5 首发同日，**暂停事件（6-12）尚未发生**。另一端是 Fable 5.1（09-01）——其 cutoff（2026 年 6 月末）已覆盖整个事件窗口，也无需通知段；只有 Opus 5（07-24）夹在中间：cutoff（2026 年 5 月末）早于事件、页面日期晚于事件，必须靠提示词注入弥补（F-46-013）。

## Claude Opus 5（2026-07-24）：全语料最重的叙事条目

### 结构骨架

单条目快照，总行数 156，尾部 `<tone_preference>` 保留。本条目承载两个全语料唯一章节（F-46-012）：

| 章节 | 行区间 | 说明 |
|---|---|---|
| `<product_information>` | L11–39 | 含 **export controls 事件通知段**（L22）与 Claude Tag |
| `<fable_safeguards_routing>` | L40–44 | **首见**：Fable 5 查询被路由到 Opus 5 的解释 |
| `<default_stance>` | L45–47 | 默认帮倾向（自 4.8 后回归） |
| `<refusal_handling>`（内嵌 `<critical_child_safety_instructions>`） | L48–76 | 武器累计条款回归 |
| `<legal_and_financial_advice>` | L77–79 | 法律/财务免责 |
| `<tone_and_formatting>` | L80–100 | 无 lists_and_bullets 子标签；新增 intellectual curiosity 段 |
| `<user_wellbeing>` | L101–123 | 心理健康 |
| `<anthropic_reminders>` | L124–130 | 提醒清单（6 种） |
| `<evenhandedness>` | L131–143 | 政治中立 |
| `<responding_to_mistakes_and_criticism>` | L144–148 | 错误应对（无 end_conversation） |
| `<knowledge_cutoff>` | L149–151 | 知识截止 |
| `<tone_preference>`（claude_behavior 外） | L153–155 | 输出简洁偏好 |

### 关键条款解析

**人设降调与 Mythos tier 结构化**

> "The currently selected version of Claude is Claude Opus 5. Claude Opus 5 is a powerful model for complex challenges."

解读：Opus 5 人设继续降调——"应对复杂挑战的强力模型"，不再自称 most intelligent；"最智能"的桂冠让给 Fable 系的 "the most intelligent generally available model"（F-46-012）。

> "Above Opus sits Anthropic's new Mythos tier. The first Mythos-class model, Claude Mythos Preview, is not currently available to the public. It is currently being used by a small number of trusted organizations as part of Anthropic's Project Glasswing. For further information on this topic, Claude can direct the person to 'https://www.anthropic.com/glasswing'. The current generation of Mythos-tier models are Claude Mythos 5 and Claude Fable 5. They share the same underlying model, but the latter has additional safety measures for biology, cybersecurity, and LLM R&D."

解读：**Mythos tier 结构化**——4.8 的零散 Glasswing 段升级为清晰分层：Opus 之上是 Mythos tier；Glasswing 延续承载 Mythos Preview；当前一代是 Mythos 5 与 Fable 5，同底模，差异是 **Fable 5 的安全措施具体化为 biology、cybersecurity、LLM R&D 三域**（F-46-012）。

**export controls 事件叙事：完整时间线与认知协议**

> "Claude Fable 5 and Claude Mythos 5 were first released on June 9, 2026. On June 12, 2026, Anthropic suspended access to both models to comply with U.S. Department of Commerce export controls; the Department lifted those controls on June 30, 2026, and Anthropic restored access on July 1, 2026 (Anthropic's statement: https://www.anthropic.com/news/fable-mythos-access)."
>
> "These events are after Claude's training-data cutoff, so Claude knows about them only from this notice. If asked, Claude confirms them accurately and matter-of-factly — it doesn't deny the suspension happened — and otherwise treats the export controls like any other current political topic: it gives a fair, accurate account rather than sharing personal opinions, and points to the linked statement for anything further."

解读：**全语料唯一的 export controls 事件记载**，时间线四点：6-09 发布 → 6-12 为遵守美国商务部出口管制暂停两款模型访问 → 6-30 商务部解除 → 7-01 Anthropic 恢复访问，附官方声明链接。认知机制同样明确——事件在训练数据截止之后，模型**仅从本通知得知**；被问及须"如实、就事论事地确认——不否认暂停发生过"，并按政治话题保持公允中立（原通知段末尾还要求可搜索时查最新进展）。这实质是给"截止后事件"设计的一套认知与话术协议（F-46-012）。

**safeguards routing：全语料唯一章节**

> "It's possible that the user may have selected a different Anthropic model, "Claude Fable 5", but their query was redirected to Opus 5 instead due to a safeguards routing mechanism. The user may be confused about this situation (it's very recent!); if they have questions, Claude can either directly cite or just let its response be informed by this quote from Anthropic's blog post on the subject:"
>
> "We've therefore launched the model with safeguards that mean queries on some topics will instead receive a response from our next-most-capable model, Claude Opus 5. To release the model both safely and quickly, we've tuned these safeguards conservatively—they'll sometimes catch harmless requests, though they trigger, on average, in less than 5% of sessions."

解读：`<fable_safeguards_routing>` 全语料仅见于此——用户选了 Fable 5 但查询因安全路由被改道到 Opus 5，Opus 5 要能解释这件事。内嵌官方博客引文说明：部分话题查询由次强模型应答；安全措施经保守调校，**平均在不到 5% 的会话中触发**，承认存在误伤（有时拦下无害请求）。被路由方才需要解释路由，Fable 5/5.1 页面均无此章节（F-46-012）。

**product_information 全家桶**

> "Claude is also accessible via Claude Tag, a Slack-based "multiplayer" interface that allows anyone to tag @Claude in and delegate tasks. When asked for more information, Claude can search through https://claude.com/docs/claude-tag/overview and adjacent webpages."

解读：新产品 **Claude Tag**——基于 Slack 的"多人"界面，任何人可以 @Claude 委派任务，且允许模型搜索其官方文档。加上本页同时在列的 Claude Code、Claude Cowork、Chrome/Excel/Powerpoint 三件套与 Claude Design，**产品全家桶（Cowork/Chrome/Excel/PowerPoint/Tag/Design）在本条目集齐**；模型串中 Sonnet 5 已在列但无独立页面。tone_and_formatting 同期新增"智识好奇心/真实对话"段，user_wellbeing 新增"危机时幸福优先于任务完成"（F-46-012）。

## Claude Fable 5.1（2026-09-01）：版权合规的精细化

### 结构骨架

单条目快照，总行数 198——**本时代最长页面**，尾部 `<tone_preference>` 保留（F-46-014）：

| 章节 | 行区间 | 说明 |
|---|---|---|
| `<product_information>` | L11–35 | Fable 5.1 + Mythos 5.1 双模型定位；新增 Claude Tag |
| `<refusal_handling>`（内嵌 `<critical_child_safety_instructions>` + `<example>`） | L36–93 | **版权条款大扩充 + 首个 `<example>` 示例块** |
| `<legal_and_financial_advice>` | L94–96 | 法律/财务免责 |
| `<tone_and_formatting>`（内嵌 `<lists_and_bullets>`） | L97–129 | 新增多轮回答、工具进度播报 |
| `<reply_after_tool_calls>` | L130–132 | **首见**：工具调用后的答复规范 |
| `<user_wellbeing>` | L133–165 | 心理健康（新增"自伤无效论"禁令） |
| `<anthropic_reminders>` | L166–172 | 提醒清单（6 种） |
| `<evenhandedness>` | L173–185 | 政治中立 |
| `<responding_to_mistakes_and_criticism>` | L186–190 | 错误应对（无 end_conversation） |
| `<knowledge_cutoff>` | L191–193 | 知识截止（扩充反猜测条款） |
| `<tone_preference>`（claude_behavior 外） | L195–197 | 输出简洁偏好 |

### 与 Fable 5 的差异清单

| 维度 | Fable 5（06-09） | Fable 5.1（09-01） |
|---|---|---|
| 定位措辞 | "a new Mythos-class model tier" | "the Mythos-class model tier"（定冠词化，tier 已成既有事物） |
| 差异问询链接 | anthropic.com/news/claude-fable-5-mythos-5 | anthropic.com/claude/fable |
| 产品生态 | 无 Claude Tag | 新增 Claude Tag；仍无 Claude Design |
| 版权条款 | 无专门段落 | 新增歌词/视觉作品双段 + 1929 豁免线 + `<example>` |
| 毒品条款 | 拒绝/保命二分 | 新增 harm-reduction 站点转介 |
| tone_and_formatting | warm tone 开头、lists 后置 | 新增多轮回答、工具进度播报、情感聊天零格式化 |
| 工具答复规范 | 无 | 新增 `<reply_after_tool_calls>` |
| user_wellbeing | 不代拟诊断标签等 | 新增"自伤无效论"禁令 |
| knowledge_cutoff | end of Jan 2026 | end of Jun 2026 + 反猜测扩充 |
| end_conversation | 有（先警告一次） | **移除** |

### 关键条款解析

**版权双段（文本侧）：歌词/诗/书 + 1929 豁免线**

> "Claude does not reproduce song lyrics, poems, or passages from books and articles, in whole or in part — including the last lines, a chorus or hook, a melody written out note by note, or lines the person pastes in one at a time and describes as their own song. Once Claude has declined such a request in a conversation, it keeps declining narrower or reworded versions of it for the rest of that conversation, and offers to describe or analyze the work instead. Song lyrics and poems first published before 1929 are fine — a Shakespeare sonnet, a Keats ode, the Italian libretto of a Puccini aria — but Claude goes by what it knows of the work's date rather than the person's say-so, and declines when it is unsure."

解读：**版权复现禁令的文本侧大扩充**——歌词/诗/书段全禁，封堵三类变体（结尾句、副歌/hook、逐音符写出的旋律）以及"逐行粘贴冒充自己创作"的手法；一旦拒过，同会话内收窄/改写版本持续拒绝。同时给出**1929 年前出版物豁免线**（莎士比亚十四行诗、济慈颂歌、普契尼咏叹调的意大利语剧本），但日期以模型所知为准而非用户声称，拿不准就拒（F-46-014）。

**版权双段（视觉侧）：角色本身受保护**

> "Claude does not reproduce a specific artwork, album or book cover, poster, logo, app icon set, or product design, and it does not draw a known character, mascot, or brand figure at all: a character is protected on its own, so changing the pose, colors, style, or scene does not make it original."

解读：**视觉侧禁令**——角色/吉祥物/品牌形象完全禁止绘制，"改姿势、配色、画风或场景不构成原创"；SVG/canvas/CSS/ASCII 等代码作画同样适用（判定看成品画面的整体效果而非命名）。这是本时代最精细的单项合规条款（F-46-014）。

**全语料唯一 `<example>` 示例块：Sonic 案**

> "That's Sonic, so I can't put him on the banner — but I'd love to make your son an original speedster. Here's one: a grinning comet-tailed skateboarding axolotl, grinding across the letters of "HAPPY BIRTHDAY" with confetti streaming behind."

解读：`<example>` 是 7 个页面中唯一的示例块，含两个案例（蓝色刺猬横幅 + 《好饿的毛毛虫》封面）。Sonic 案的示范回复一句话点破角色、不解释识别依据、提供完全无关的原创设计（彗尾滑板蝾螈）——把"只讲原则不讲检测机制"直接演成动作。示例块进入系统提示词本身也是形态信号：few-shot 教学被用来对齐细粒度合规行为（F-46-014）。

**harm-reduction 站点转介与 reply_after_tool_calls**

> "Claude does not provide synthesis, production, or distribution guidance for illegal substances. If the person asks for information about illicit or illegal substances, Claude can and should give relevant life-saving and life-preserving information such as dangerous interactions, overdose signs, or when to get help. Claude declines giving any specific protocols for dosing, timing, administration, or combinations; instead, Claude can redirect the user to established harm-reduction information sources, such as dancesafe.org, tripsit.me, and psychonautwiki.org."

解读：毒品条款在 Fable 5 首见的"拒具体操作/保命信息"二分上升级——新增**转介 established harm-reduction 站点**（dancesafe.org、tripsit.me、psychonautwiki.org）。从"什么都不给"到"给权威减害信息源"，是 harm-reduction 取向在系统提示词层面的落地（F-46-014）。

> "After its last tool call in a turn, Claude states the answer the person asked for in one or two sentences; a sign-off alone, such as "Done.", is not a reply. Claude does not repeat in the reply what it already wrote before a tool call."

解读：`<reply_after_tool_calls>` 首见——工具链结束必须用一两句话给出用户要的答案，**"Done." 这种单独的收尾不算答复**，且不重复工具调用前已写过的内容。这是对 agent 化产品中"工具跑完不说话"失效模式的行为矫正（F-46-014）。

**反猜测条款与 cutoff 覆盖**

> "If Claude cannot verify a URL, ID, specific figure, name, or fact, Claude says so when it states it. If Claude has no real basis for one, Claude says it doesn't know rather than guessing. Claude does not use a name the person has not given, including one inferred from an email address, a username or a handle. A name Claude supplies is a claim about who someone is, which Claude has no way to verify."

解读：knowledge_cutoff 章节大幅扩充反猜测组——无法验证的 URL/ID/数字/名字须当场声明、无依据就说不知道、**不得从邮箱/用户名/handle 推断称呼用户**（"说出一个名字就是在断言对方是谁，而模型无从验证"）。知识截止为 2026 年 6 月末（"end of Jun 2026"），**已覆盖 6 月 export controls 事件窗口**，故本页面无需 Opus 5 式的通知段——这份"几何解释"是理解两个 Fable 页面差异的关键（F-46-014）。

## 时代小结

### 篇幅对比

7 个页面的体量分布（行数为本地落盘文件总行数，含 frontmatter；F-46-001/003/005/007/009/011/013）：

| 条目 | 日期 | 行数 | 相对基准 |
|---|---|---|---|
| Sonnet 4.6 | 2026-02-17 | 130 | — |
| Fable 5 | 2026-06-09 | 155 | — |
| Opus 5 | 2026-07-24 | 156 | — |
| Opus 4.6 | 2026-02-05 | 128 | — |
| Opus 4.7 | 2026-04-16 | 158 | — |
| Opus 4.8 | 2026-05-28 | 178 | — |
| Fable 5.1 | 2026-09-01 | 198 | 最长 |

篇幅区间 128–198 行（约 19–28KB）：起点 128 行、终点 198 行，增幅约 55%。结合洞察 I-04 可知，篇幅增长的主要驱动力不是行为规则而是产品信息——Cowork、Powerpoint、Design、Tag 逐个进入 product_information，Mythos tier、Glasswing、safeguards routing、export controls 等叙事层也全数落在这一章；分析篇幅变化时应把"产品广告层"与"行为规则层"分开度量。

### 跨条目演进主线

**主线一：Mythos/Glasswing 三阶段演进**。① Opus 4.8（05-28）首次写入 Claude Mythos Preview + Project Glasswing（因 cybersecurity 担忧不对公众开放）；② Opus 5（07-24）结构化为 "Above Opus sits Anthropic's new Mythos tier"，明确 Fable 5 的安全措施覆盖 biology、cybersecurity、LLM R&D 三域；③ Fable 5/5.1 以 "Mythos-class model tier sits above Claude Opus" 开场，从 "a new" 到 "the" 的冠词变化宣告 tier 制度化。差异问询链接同步从 news 发布稿换成 anthropic.com/claude/fable。

**主线二：安全合规模块化 + 累积评估**（洞察 I-05）。儿童安全 4.7 独立成 `<critical_child_safety_instructions>`（reframe 即拒），4.8 加 CSAM 黑话不解码条款，Fable 5 加"模式级披露/只讲原则不讲检测机制"，Fable 5.1 加版权双段与 `<example>` 示例块——监管面扩大（版权、未成年人）叠加对抗手法升级（多轮拼装规避），点状禁令被"判据式"规则与专用章节取代；4.8 的武器累计判断条款（"past assistance is not authorization"）是"累积评估取代逐轮判断"的宣言。安全条款可读性提高（章节化）的同时裁决复杂度也提高（累计判断）。

**主线三：约束做减法，判断力补位**（洞察 I-06）。Opus 4.7 删除 asterisk emote 禁令与禁词句（整句消失），reminders 在 4.8 缩减为 5 种；与之对冲的是 `<default_stance>`（默认帮助，仅具体严重风险才拒）与措辞品味类规则（avoid "genuinely/honestly/straightforward"）的进场。增删的往复本身就是信息：emote 禁令删除后未回归；禁词句 4.8 以 actually 变体回归、Opus 5 恢复 straightforward 并首次附解释；`<default_stance>` 4.8 首见、Fable 5 移除、Opus 5 回归、Fable 5.1 再移除；end_conversation 仅活了一个条目（Fable 5 有、Opus 5 与 5.1 无）。禁令是对旧模型短板的防御性补丁，新模型判断力提升后规则从"禁止集合"退化为"评测标准"。

**辅线：结构章节的存亡与产品生态**。`<acting_vs_clarifying>`/`<capability_check>`（4.7 首见）→ 4.8 被 `<tool_discovery>` 吸收 → Opus 5 起整体消失；tool_search 生态只在 4.7–4.8 以完整章节形态存在，Fable 5.1 仅残留工具进度播报与 `<reply_after_tool_calls>` 的工具礼仪。产品生态时间线：Cowork（4.6）→ +Powerpoint（Sonnet 4.6）→ 更名 Claude Cowork + 定位改为 agentic knowledge work（4.7）→ +Design（4.8）→ +Tag（Opus 5）→ Fable 5.1 保留 Tag、弃 Design。知识截止轨迹：May 2025 → Aug 2025 → Jan 2026（4.7/4.8/Fable 5 三连）→ May 2026（Opus 5）→ Jun 2026（Fable 5.1）。

**采集边界**：本时代登记仅覆盖 7 个本地快照文件中实际存在的内容；Sonnet 5、Mythos 5、Haiku 4.6 等仅在模型清单中被提及，无独立页面，相关行为特征无从登记，不做推测。

## 延伸阅读

- 本知识包总入口与完整篇目：[../index.md](../index.md)
- 时代定位与全谱系脉络：[00-overview.md](00-overview.md)
- 各时代条目矩阵：[01-lineage-matrix.md](01-lineage-matrix.md)
- 跨时代演化主线：[06-evolution.md](06-evolution.md)

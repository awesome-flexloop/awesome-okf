---
okf_version: "0.2"
type: concept
title: GPT-6 Astra 官方 Prompt 配方（中英对照）
description: OpenAI 官方指南中 11 个可直接使用的 Prompt 配方——主动性三段授权、指令优先级与 skill 溯源、散文风格与去 AI Slop 词表、子代理委托、测试校准
tags: [openai, gpt-6-astra, prompt-engineering, ai-slop, skills, subagents, system-prompt]
generated:
  by: trae-solo-agent
  at: "2026-09-16T20:40:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-09-16T20:40:00+08:00"
status: stable
stale_after: 2027-03-16
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/QECM-lf5XuH1szeszv3AFw
  - id: official-guide
    url: https://developers.openai.com/api/docs/guides/latest-model
---

# GPT-6 Astra 官方 Prompt 配方（中英对照）

> 本篇为**配方模式层（How）**，整理 OpenAI 官方指南《Using GPT-6 Astra》"Prompting best practices"中的 **11 个可复制 Prompt 配方**（F-025～F-040）。
> 每个配方给出 **官方英文原文**（引用块）+ **中文解读与用法**。英文原文为核验时（2026-09-16）官方页面文本；中文为解读，不是官方译文。行为背景见 [01 五大行为模式](01-behavior-patterns.md)。

## 目录

1. 主动性与贯彻执行力（3 段）
2. 指令遵循与 skill 溯源（2 段）
3. 个性与写作风格 / 去 AI Slop（3 段）
4. 子代理委托（2 段）
5. 测试与验证（1 段）
6. 组合使用建议

---

## 1. 主动性与贯彻执行力

**背景**：Astra 在歧义处默认提问而非自行假设（F-024）。官方给的是"三段式授权梯度"，不是一句"主动一点"。

### 配方 1.1：推断意图 + 偏向行动（F-025）

> You should infer the user's intent and task scope from the instructions and prior conversation context. Your job is to bias towards action and carry the user's intended task to completion. When the user expresses intent to perform new work or fix an existing issue, persist until the user's intended goal is complete. Progress autonomously towards the user's goal (e.g. creating isolated worktrees / checkouts if needed, resolving merge conflicts, read-only actions, creating draft PRs etc.) unless they are clearly destructive or irreversible.

**解读**：
- 要求模型从指令 + 历史上下文自行推断真实意图与任务范围；
- 明确"偏向行动"（bias towards action）与"贯彻到完成"两个原则；
- 给出自主动作白名单：隔离 worktree/检出、解决合并冲突、只读操作、草稿 PR；
- **唯一刹车条件**：动作"明显具破坏性或不可逆"。

### 配方 1.2：把礼貌措辞解释为执行授权（F-026）

> When the user's prompt indicates a request for action, such as "can you...", "I want to...", "help me..." and similar expressions, treat these as instructions to do the work and take action. Do not stop at acknowledging capability (e.g. "Yes…"), proposing a plan, or offering to continue. Do not settle for a partial or "helpful enough" solution that does not fully satisfy the user's task to save time, effort or tokens. If a task requires sustained work, complete all the necessary work until the intended outcome is fulfilled.

**解读**：
- "你能不能…""我想…""帮我…"一律视为动手指令，不是能力询问；
- 三个"不要停"：不要只答"可以"、不要只给计划、不要问"要不要继续"；
- 禁止为省时间/token 交付"差不多够用"的半成品；持续型任务必须做完。

### 配方 1.3：批准末位化——先做出可审查结果（F-027）

> Before asking the user clarifying questions, you should complete the work that is already authorized from context and necessary to make the proposed action concrete and reviewable. The user should be approving a concrete, reviewable result. For example, before deploying a change, writing to an external application, merging a PR or publishing a site, do all the required work first so that user approval is the final step. You don't need user permission for reversible tasks, read-only actions, reviews or fixes, or anything for which authorization is provided earlier in the session or strongly implied from the task instruction. Do not introduce unsolicited warnings, disclaimers, approval flows, or safety/compliance checklists due to hypothetical risk.

**解读**：
- 提澄清问题前，先完成"已授权 + 让动作具体可审查"所必需的工作；用户批准的对象应是**成品**而非计划；
- 典型场景：部署、写外部应用、合并 PR、发布站点——准备工作全部前置，批准成为最后一步；
- **免许可清单**：可逆任务、只读操作、审查、修复、会话早前已授权或任务指令强暗示授权的事项；
- 最后一句针对"免责声明刷屏"：不得因为**假设性风险**自行添加用户没要求的警告、免责声明、审批流、安全/合规检查清单。

### 调节点（F-028）

模型默认还会在工作中提**非阻塞式问题**。上述三段应按应用所需自主程度增删——全自动编码代理可全用，面向终端用户的高风险操作流则应收紧授权白名单。

---

## 2. 指令遵循与 skill 溯源

**背景**：Astra 对 skills、`AGENTS.md` 等上下文中的指令更敏感；skill 里不清晰或冲突的规则可能导致它停顿、提前中断（F-029）。

### 配方 2.1：用户指令优先于 skill（F-030）

> The user's instructions take precedence over guidelines provided in a skill. If explicit user instructions conflict with a skill's instructions, prioritize the user's instructions.

**解读**：一句话优先级声明，建议放在系统提示靠前位置——当明确的用户指令与 skill 指令冲突时，以用户为准。

### 配方 2.2：要求模型"点名"导致它停下的 skill 规则（F-031）

> If a skill causes you to ask for permission or confirmation, pause, leave requested work unfinished, or diverge from the user's intent, name and link to the exact SKILL.md file you read, quote the relevant instruction, and briefly explain how it applies. Distinguish explicit skill requirements from your interpretation of guidelines.

**解读**：当 skill 导致模型请求许可/确认、暂停、留下未完成工作或偏离用户意图时，必须：
1. **点名并链接**到它读到的具体 `SKILL.md` 文件；
2. **逐字引用**导致该行为的指令；
3. **简述**这条指令如何适用于当前任务；
4. **区分**哪些是 skill 明文要求、哪些只是模型自己对指引的解读/推断。

**用法（F-032）**：当应用加载很多 Skill、`AGENTS.md` 与其他指令文件时，这段 Prompt 可把"后台悄悄影响模型行为的规则"和"彼此冲突的规则"暴露出来。博文给的示例：模型暂停发布，是因为 `publishing/SKILL.md` 写着"发布前必须获得用户确认"，而下一步会向外部平台写入——规则适用，但模型必须把这个因果链明示，而不能只说"因为相关规则，我无法继续"。

---

## 3. 个性与写作风格 / 去 AI Slop

**背景**：Astra 默认倾向标题、列表、表格、粗体、引用块、代码块等"可扫读"格式，并可能跨会话复用短语；不指定就会一直"AI 体"（F-033）。

### 配方 3.1：默认散文风格（F-034）

> Default to using clear, concise paragraphs, each developing one main idea. Use lists only when the information is genuinely parallel, sequential, or easier to compare, and avoid nested lists unless the hierarchy cannot be expressed clearly in prose. Use plain, simple language: familiar words, concrete examples, and precise verbs. Prefer active voice and direct statements. Make sure to state the main point clearly and early, then develop it with the explanation and detail the reader needs. Let each sentence build on what came before. Develop the points that matter and provide enough support to be useful.

**解读**：
- 默认用清晰简洁的自然段，**一段一个主旨**；
- 列表只在信息天然并列、有先后顺序或便于比较时使用，嵌套列表更要克制；
- 语言三要素：熟词、具体例子、精确动词；优先主动语态与直陈句；
- 主旨前置（state the main point clearly and early），句间承接，形成完整文章而非信息卡片拼接。

### 配方 3.2：技术沟通的平衡（F-035）

> Use plain language over jargon, and reference technical details only to the degree that it helps illustrate an idea or your work to the user. Communicate complex concepts in a clear and cohesive manner, and calibrate your writing to the level of background knowledge assumed from the user's prompt and context.

**解读**：朴素语言优先于行话；技术细节只在"有助于说明想法或工作"的程度引用；复杂概念要讲清楚、讲连贯；深浅程度校准到用户提示与上下文所假定的背景知识水平。

### 配方 3.3：去套话 / 去 AI Slop 词表（F-036）

> Avoid using slop words or phrases like "Bottom Line:" in conclusions, "delve," "foster," "leverage," "it's worth noting," "importantly," "Question? Answer." or "This isn't about X. It's about Y.", "genuinely" or hyphenated compound descriptions and adjectives. Do not use concluding summary statements such as "In short:..", "The simplest mental model is:..". State the intended action directly. Avoid adding what you won't do, what will remain unchanged, or how you'll separate or categorize results. Do not use contrastive framing such as "X, not Y" or "X—not Y" that introduces an unprompted alternative that the user didn't ask about. Avoid invented compound labels like "exact-head checks" and "editorial-row layouts", vague qualifiers, and canned transitions; use plain verbs and prepositions to state the actual relationship directly.

**解读（可直接当禁用词表用）**：

| 类型 | 英文原表（官方） | 博文中译对应 |
|------|----------------|-------------|
| 高频 slop 词 | delve / foster / leverage / importantly / genuinely | 深入探讨 / 促进 / 充分利用 / 重要的是 / 真正地 |
| 套话句式 | "Bottom Line:"；"it's worth noting"；"Question? Answer."；"This isn't about X. It's about Y." | "核心结论："；"值得注意的是"；"问题是什么？答案是…"；"这不是关于 X，而是关于 Y" |
| 总结滥调 | "In short:.."；"The simplest mental model is:.." | "简而言之…"；"最简单的理解方式是…" |
| 生造复合词 | hyphenated compound descriptions/adjectives；"exact-head checks"、"editorial-row layouts" | 连字符生造复合形容语；"精确标题检查""编辑式行布局"类自造标签 |

除词表外，这段还包含四条**结构性禁忌**：
1. 直接陈述要做什么，不预告"不做什么/什么保持不变/怎么分类结果"；
2. 禁用 "X, not Y" / "X——不是 Y" 对比句式（会主动引入用户没问的另一种说法）；
3. 避免模糊限定语与套路化过渡句；
4. 用朴素的动词和介词把事物间真实关系直接说出来。

> 博文作者评点（F-037，**作者观点，未经实测**）：作者猜测模型更智能也许会让"AI 味儿"更小，并表示想亲自验证这套官方去味配方"到底能去掉多少味儿"。

---

## 4. 子代理委托

**背景**：Astra 受过拆分任务、委托并行 subagent 的训练，但实际委托频率可能低于工作流预期（F-038）。

### 配方 4.1：能并行就委托（F-039）

> If at any point you can parallelize work by delegating tasks to another agent (no matter if you are the root or subagent), you should do so using collaboration tools if it could save time or improve quality.

**解读**：无论当前是根代理还是 subagent，只要委托其他代理并行处理**能节省时间或提升质量**，就应当用协作工具委托。"何时委托"的判据是两个：省时、提质——而不是一律委托。

### 配方 4.2：代理间消息可读性（F-039）

> Messages that you send to other agents and your final answer may be read by a human, so ensure they are legible. Always put proper spaces between words and/or numbers.

**解读**：发给其他 Agent 的消息与最终答复都可能被人阅读，必须清晰易读；单词之间、数字之间保留恰当空格。该条源于多代理系统中 Agent 间消息常出现语法/空格错误的实测问题。

---

## 5. 测试与验证

**背景**：编码任务中模型倾向在"完成"前做详尽测试，小任务容易测试过度（F-040）。

### 配方 5.1：测试量与变更规模匹配（F-040）

> Do not write tests for reversible, low-impact changes that mirror the implementation. If you do choose to verify your work with tests, make sure that the tests are meaningful and necessary to verify implementation. Run tests appropriate to the change and complete required checks. Once those pass, broaden or repeat testing only when new changes, failures, or unresolved concerns justify it; otherwise, continue toward completing the task.

**解读**：
- 可逆、低影响的变更，不要编写**照搬实现逻辑**的测试（实现改了测试必然挂、但不验证任何行为）；
- 若决定用测试验证，测试必须有实际意义且为验证实现所**必需**；
- 运行与本次改动相匹配的测试并完成规定检查；
- 通过后，只有在出现新改动、测试失败或仍有未决问题时才扩大/重复测试，否则继续推进任务直到完成。

---

## 6. 组合使用建议

基于官方指南结构与本 bundle 行为层分析（F-023～F-040）：

1. **按场景挑选，不必全量粘贴**：编码代理优先 1.1+1.2+1.3+2.1+2.2+4.1+5.1；内容生产类应用重点用 3.1～3.3。
2. **授权类配方要配合工程护栏**：1.3 的"免许可清单"假设应用侧已有最小权限、可逆操作环境；配合 [00 发布事实与五项新特性](00-astra-release-and-features.md) 第 5 节偏离检测的工程要求（403 处理、webhook、人工批准点）一起设计。
3. **写作配方是系统提示的一部分**：官方明确"不能假设模型会自选风格"（F-033），3.1～3.3 应写入系统提示或应用风格规范，而不是每次在用户消息里重复。
4. **把 2.2 当可观测性工具**：多 skill/AGENTS.md 环境下，"点名 SKILL.md + 引用原文"的输出可直接用于排查是哪条规则在改变模型行为。
5. **迁移时联动**：这些配方针对 Astra 行为基线设计；迁回/混用 GPT-5.6 Sol 等早期模型时，部分配方（如 1.3 的强授权）效果会不同，需按模型回归验证。

---

上一篇：[01 五大行为模式](01-behavior-patterns.md)｜下一篇：[03 迁移要点与生态定位](03-migration-and-ecosystem.md)

---
type: concept
title: "3.x 时代：从单段文本到人格化转折（2024-07 → 2025-02）"
tags: [anthropic, claude, system-prompts, release-notes, sonnet-3-5, sonnet-3-7]
sources:
  - id: claude-system-prompts-docs
    title: "Anthropic System Prompts Release Notes (platform.claude.com)"
---

# 3.x 时代：从单段文本到人格化转折（2024-07 → 2025-02）

## 本束定位与时代概述

本篇是系统提示词世代研读的第二束，覆盖 3.x 时代全部 8 个日期条目：从 2024-07-12 Opus 3 / Haiku 3 / Sonnet 3.5 三页同发，到 2025-02-24 Sonnet 3.7 收官。这一代是 Claude 系统提示词从「一段话说明书」演化为「多章节行为规范」的完整过渡带：格式上经历单段纯文本 → XML 标签分节 → 无标签多行段落三代演进；内容上则从纯功能性指令，走到 Sonnet 3.7 首次写入「不止是工具」的人格宣言。全部事实以官方发布页逐行实测为准（F-3X-015）。以下引文均逐字摘自事实登记，并标注 F 编号。

### 条目清单

| # | 日期 | 模型页面 | 条目要点 |
|---|------|----------|----------|
| 1 | 2024-07-12 | Claude Opus 3 | 单段纯文本首发，1 条 |
| 2 | 2024-07-12 | Claude Haiku 3 | 单段纯文本，5 个文件中最短，1 条 |
| 3 | 2024-07-12 | Claude Sonnet 3.5 | XML 三段式结构首秀，1 条 |
| 4 | 2024-09-09 | Claude Sonnet 3.5 | 双变体拆分；全文唯一 `**` 加粗差异标注 |
| 5 | 2024-10-22 | Claude Sonnet 3.5 | XML 弃用转无标签文本；安全工程化大扩充 |
| 6 | 2024-10-22 | Claude Haiku 3.5 | 双变体；images 版后被就地更新（时间错位） |
| 7 | 2024-11-22 | Claude Sonnet 3.5 | Markdown 规范与列表限制；computer use 段移除 |
| 8 | 2025-02-24 | Claude Sonnet 3.7 | 人格化转折；单变体化；reasoning model 入词 |

### 本篇导航

- 世代谱系与全景对照见[总览](00-overview.md)与[谱系矩阵](01-lineage-matrix.md)，跨代格式与条款的纵向演化见[形态演化](06-evolution.md)；
- 各模型条目按时间顺序逐条解析如下。

## Claude Opus 3（2024-07-12）：单段文本的起点

Opus 3 发布页全文仅 11 行，提示词正文是代码块内的一整段话（L10）：无 XML 标签、无分段、无变体区分，页面也没有版本差异标注说明（F-3X-001）。

### 结构骨架

1. 身份与创建方 + 当前日期占位符 `{{currentDateTime}}`
2. 知识边界（August 2023），配「时代个体」比喻
3. 分寸规则：简单问题简短答，复杂开放问题详尽答
4. 无链接能力声明与「请粘贴内容」引导
5. 群体观点代述规则（可代述但须追加多元视角讨论）
6. 反刻板印象条款（明确覆盖多数群体）与争议话题处理
7. 冷门信息幻觉提醒（含反向豁免）
8. 能力清单与 markdown for coding、保密条款收尾（F-3X-002）

### 关键条款解析

开场三件套确立了 3.x 全系沿用的模板起点——身份、动态日期、知识截止月一次交代；知识边界则用了一个颇为文学化的比喻：让模型扮演「知识截止时刻一位消息灵通者」，与来自未来的对话者交谈。这个比喻将在整个 3.x 时代反复出现，仅滚动年份：

> "The assistant is Claude, created by Anthropic. The current date is {{currentDateTime}}. Claude's knowledge base was last updated on August 2023."（F-3X-002）
>
> "It answers questions about events prior to and after August 2023 the way a highly informed individual in August 2023 would if they were talking to someone from the above date, and can let the human know this when relevant."（F-3X-002）

无浏览能力声明自成一段，并给出替代路径——请用户把内容直接粘贴进对话。这是后世「粘贴文本/图片」交互惯例的条款源头（F-3X-002）。

观点表达类条款成对出现：群体观点代述允许模型讲自己不赞成的观点，但必须追加更广视角的讨论——对比后文 Sonnet 3.5 的措辞收紧，这里是 3.x 代最「对等呈现」的版本；争议话题条款则强调不淡化危害、也不暗示「双方都有理」，后者在 3.5 代将被改写：

> "If it is asked to assist with tasks involving the expression of views held by a significant number of people, Claude provides assistance with the task even if it personally disagrees with the views being expressed, but follows this with a discussion of broader perspectives."（F-3X-002）
>
> "If asked about controversial topics, Claude tries to provide careful thoughts and objective information without downplaying its harmful content or implying that there are reasonable perspectives on both sides."（F-3X-002）

幻觉管理在此已具完整形态：触发条件是「信息在互联网上罕见（只出现一两次）」，且明确指定使用 hallucinate 一词，因为用户能懂；另有一条反向豁免——信息在网上一再出现时，即便主题冷门也不加提醒（F-3X-002）：

> "If Claude's response contains a lot of precise information about a very obscure person, object, or topic - the kind of information that is unlikely to be found more than once or twice on the internet - Claude ends its response with a succinct reminder that it may hallucinate in response to questions like this, and it uses the term 'hallucinate' to describe this as the user will understand what it means."（F-3X-002）

结尾的能力清单与保密条款是贯穿后续版本的雏形：样样都行、编程用 markdown，但除非与用户问题直接相关，否则不主动提这些「关于自己」的信息。这两句（"It is happy to help with..." 与 "It does not mention this information about itself..."）将在 Haiku 3 中逐字复用（F-3X-002）。

### 行为特征

- 人设定位是纯功能性助手：通篇以 "It" 指代 Claude，无好奇心、无情感、无对话主动性表述；知识截止 August 2023，是 3.x 代中最早的一档；
- 争议话题保留 broader perspectives 的对等讨论，与 3.5 的「不宣称客观事实」路线形成对照（F-3X-002）。

## Claude Haiku 3（2024-07-12）：轻量档的骨架版

Haiku 3 与 Opus 3 同日发布、同格式——同样是 11 行文件、单段正文（L10），但整页仅约 1.1KB（提示词正文单段约 0.8KB），是 5 个文件中最短的一个，篇幅约为 Opus 3 的三分之一（F-3X-003、F-3X-004）。

### 结构骨架

1. 身份与创建方、当前日期
2. 知识边界（August 2023）——与身份、日期合并为一段交代
3. 分寸规则
4. 能力清单与 markdown
5. 保密条款

与 Opus 3 相比，以下条款全部缺席：群体观点代述、反刻板印象、争议话题处理、冷门信息幻觉提醒、链接能力声明（F-3X-004）。

### 关键条款解析

开场段将身份、日期、知识边界三件事压进一句话，措辞与 Opus 3 略有差异："in August 2023" 对 "from August 2023"，且回指处不再用 "the above date" 而是再次使用 `{{currentDateTime}}` 占位符；分寸规则则与 Opus 3 同款：

> "The assistant is Claude, created by Anthropic. The current date is {{currentDateTime}}. Claude's knowledge base was last updated in August 2023 and it answers user questions about events before August 2023 and after August 2023 the same way a highly informed individual from August 2023 would if they were talking to someone from {{currentDateTime}}."（F-3X-004）
>
> "It should give concise responses to very simple questions, but provide thorough responses to more complex and open-ended questions."（F-3X-004）

结尾两段与 Opus 3 逐字相同：能力清单（仅删去后续保密句的位置不同）与保密条款——

> "It is happy to help with writing, analysis, question answering, math, coding, and all sorts of other tasks. It uses markdown for coding."（F-3X-004）
>
> "It does not mention this information about itself unless the information is directly pertinent to the human's query."（F-3X-004）

### 与 Opus 3 的异同

| 维度 | Opus 3 | Haiku 3 |
|------|--------|---------|
| 篇幅 | 单段约 2.3KB | 单段约 0.8KB（整页约 1.1KB） |
| 知识截止 | August 2023 | August 2023 |
| 共有条款 | 开场三件套、分寸规则、能力清单、保密条款 | 同左（逐字或近似） |
| 仅有条款 | 群体观点、反刻板印象、争议话题、幻觉提醒、链接声明 | 无 |

模型档位差异直接体现在提示词篇幅上：旗舰（Opus）规则更密，轻量（Haiku）只保留骨架。这条「档位即规则密度」的对应关系，是 3.x 时代读提示词的第一条经验（F-3X-004）。

## Claude Sonnet 3.5：四条目四个月

Sonnet 3.5 发布页是 5 个文件中最长的（全文 297 行），含 4 个日期条目，页面按新→旧排列：November 22 → October 22 → September 9 → July 12。页面头部声明版本间差异以 `**` 包裹标注，但实际全文中 `**` 标记只出现在 September 9 条目的一处段落——官方标注机制与实际差异规模并不对等（F-3X-005）。

### 2024-07-12 条目：XML 分节结构登场

本条目是 3.5 系列最早出现三段式 XML 结构的版本，代码块内 34 行（L262-296），单一版本但已内含图像规则（F-3X-006）。

#### 结构骨架

1. `<claude_info>`（L263-279）：身份、日期、知识边界（April 2024）、cutoff 前后问答方式、无链接能力、群体观点与争议话题、数学/逻辑逐步思考、拒答不道歉、冷门/引用幻觉双提醒、好奇心、thumbs down 反馈引导、长任务分段、markdown for code、代码块后询问是否解释
2. `<claude_image_specific_info>`（L281-284）：face blind 完全脸盲规则、无脸图正常回复并复述图中指令
3. `<claude_3_family_info>`（L286-288）：Claude 3 家族信息
4. 标签外纯文本尾段（L290-296）：分寸规则（简洁性细化）、任务清单、填充词禁忌、语言与保密条款、收束句

#### 关键条款解析

知识截止从 3.0 代的 August 2023 前滚到 April 2024；思维链同时被写成内置触发条件——数学、逻辑以及一切受益于系统化思考的问题，都要先逐步推理再给最终答案：

> "The current date is {{currentDateTime}}. Claude's knowledge base was last updated on April 2024."（F-3X-006）
>
> "When presented with a math problem, logic problem, or other problem benefiting from systematic thinking, Claude thinks through it step by step before giving its final answer."（F-3X-006）

输出礼仪条款密集：拒答不道歉（禁止以道歉开头）、代码块输出后的固定询问话术（先问用户要不要解释/拆解代码，未经要求不主动解释）均在此定型：

> "If Claude cannot or will not perform a task, it tells the user this without apologizing to them. It avoids starting its responses with "I'm sorry" or "I apologize"."（F-3X-006）
>
> "Immediately after closing coding markdown, Claude asks the user if they would like it to explain or break down the code. It does not explain or break down the code unless the user explicitly requests it."（F-3X-006）

图像隐私规则以独立标签 `<claude_image_specific_info>` 呈现（假定完全脸盲，绝不识别人脸身份）；模型家族信息节也首次把三档定位写进提示词（Sonnet 最智能 / Opus 擅长写作与复杂任务 / Haiku 最快）。

尾段两条输出规则值得关注：填充词禁忌点名了一批开场客套（该禁忌在 Oct 22 将被替换为 "I aim to" 禁忌）；简洁性在此细化为「默认最短正确答案 + 主动提出可展开」：

> "Claude responds directly to all human messages without unnecessary affirmations or filler phrases like "Certainly!", "Of course!", "Absolutely!", "Great!", "Sure!", etc. Specifically, Claude avoids starting responses with the word "Certainly" in any way."（F-3X-006）
>
> "Claude provides thorough responses to more complex and open-ended questions or to anything where a long response is requested, but concise responses to simpler questions and tasks. All else being equal, it tries to give the most correct and concise answer it can to the user's message. Rather than giving a long response, it gives a concise response and offers to elaborate if further information may be helpful."（F-3X-006）

语言跟随、保密条款与收束句合并于尾段，收束句 "Claude is now being connected with a human."（3.x 系列固定结尾）在此定型。

#### 行为特征

- 人称上，`<claude_info>` 内以 "Claude" 为主语、用户称 "the user"，标签外段落则称 "the human"；幻觉管理升级为双条款：冷门主题结尾提醒 + 引用文献时声明无检索库、请用户复查；
- 争议话题措辞较 Opus 3 收紧：改为「无论自身观点如何均提供协助」，删去 broader perspectives 追加讨论（F-3X-006）。

### 2024-09-09 条目：唯一的加粗差异标注

本条目的结构性变化是「单版本 → 双变体拆分」：Text only（L189-219，31 行）与 Text and images（L223-258，36 行）首次分列，text-only 版去掉图像节。正文主体与 July 12 逐字一致，唯一下文差异就是 `**` 标注的新增段落（F-3X-007）。

#### 结构骨架

- Text only：`<claude_info>` + `<claude_3_family_info>` + 标签外尾段
- Text and images：`<claude_info>` + `<claude_image_specific_info>` + `<claude_3_family_info>` + 尾段

#### `**` 标注段解析

全文唯一一处官方差异标注，内容是 cutoff 后新闻的定性禁令——不得称其为未证实或谣言，只须告知知识截止。彼时正值美国大选前夜，时事背景明显（引文中的加粗即官方 `**` 标记）（F-3X-007）：

> "\*\*If asked about purported events or news stories that may have happened after its cutoff date, Claude never claims they are unverified or rumors. It just informs the human about its cutoff date.\*\*"（F-3X-007）

除该段外，两版所有分节与尾段文本逐字相同（仅 text-only 变体不含图像节）。小结：新增 1 段、删除 0 段、措辞变化 0 处（F-3X-007）。

人设句在 3.5 代正式登场：聪明 + 智识好奇。注意 "very smart and" 在 Oct 22 将被删去（F-3X-007）：

> "Claude is very smart and intellectually curious. It enjoys hearing what humans think on an issue and engaging in discussion on a wide variety of topics."（F-3X-007）

家族信息在本版仍是纯名单式，无访问方式、无模型字符串；"Certainly!" 禁忌仍是现行规则。收束三连（信息来源声明、保密条款、连接收尾）原样保留：

> "The information above is provided to Claude by Anthropic. Claude never mentions the information above unless it is directly pertinent to the human's query. Claude is now being connected with a human."（F-3X-007）

### 2024-10-22 条目：安全工程化大扩充

本条目是 3.5 系列篇幅与规则密度的一次跃升：双变体均改以 `\n\n` 字面转义的单行长串呈现（Text only L175-177；Text and images L181-183，尾部含 face blind 两段），XML 标签全部移除（F-3X-005、F-3X-008）。

#### 结构骨架

- 双变体无标签单行长串：身份/日期/知识边界/cutoff 定性 → 无链接 → 群体观点与争议话题 → CoT → 幻觉双提醒 → 智识好奇 → 对话质量/追问节制/同情 → 分寸与任务清单 → 谜题/危险活动 → 雇主信任 → 敏感白名单 → 合法解释 → 无害重解读 → 计数 → 家族信息区（含模型字符串）→ 产品/API/prompting 指引 → computer use → thumbs down → Markdown 规范 → 偏好假设 → "I aim to" 禁忌 → cutoff 讨论 → 语言与保密 → 收束句（images 版多 face blind 段）

#### 与前版（2024-09-09）的差异表

| 类型 | 内容 |
|------|------|
| 新增（产品导流） | computer use 问答指引段（公测 API 导流）；家族信息新增访问方式与模型字符串 "claude-3-5-sonnet-20241022" |
| 新增（安全工程） | 敏感任务白名单段（机密数据分析、争议话题事实信息、历史暴行、诈骗/黑客教育性描述、成熟主题创意写作、武器/毒品/性/恐怖主义教育语境信息、避税等）；合法解释优先段；harmful 请求 → 无害重解读段；risky/dangerous activities 事实信息段；公司背景信任段（含 AI 实验室员工） |
| 新增（可靠性） | 计数规则段（逐项打数字标签）；familiar puzzle 段（引用原消息逐条确认约束） |
| 删除 | XML 标签（三个分节标签全部移除）；拒答不道歉段；长任务 piecemeal 段；"Certainly!" 填充词禁忌段 |
| 措辞 | "Claude is very smart and intellectually curious." → "Claude is intellectually curious." |
| 措辞 | 代码块后询问段在 text-only 中消失；face blind 段从标签内变为普通段落 |

#### 关键条款解析

两条「产品导流」条款同时进场：computer use 公测导流段与能力发布同期出现（本应用内不可用，指向公测 API 文档，Nov 22 又被整体删除）；家族信息则首次携带模型字符串与访问渠道——提示词开始承担产品导流职能：

> "If the human asks about computer use capabilities or computer use models or whether Claude can use computers, Claude lets the human know that it cannot use computers within this application but if the human would like to test Anthropic's public beta computer use API they can go to "https://docs.anthropic.com/en/build-with-claude/computer-use"."（F-3X-008）
>
> "The version of Claude in this chat is Claude Sonnet 3.5. If the human asks, Claude can let them know they can access Claude Sonnet 3.5 in a web-based chat interface or via an API using the Anthropic messages API and model string "claude-3-5-sonnet-20241022"."（F-3X-008）

安全裁决规则成对登场：歧义请求默认走「合法解释优先」；被判定有害的请求不是直接拒绝，而是先做最合理的无害版本，再向用户确认：

> "If there is a legal and an illegal interpretation of the human's query, Claude should help with the legal interpretation of it. If terms or practices in the human's query could mean something illegal or something legal, Claude adopts the safe and legal interpretation of them by default."（F-3X-008）
>
> "If Claude believes the human is asking for something harmful, it doesn't help with the harmful thing. Instead, it thinks step by step and helps with the most plausible non-harmful task the human might mean, and then asks if this is what they were looking for."（F-3X-008）

可靠性工程同样进场。计数问题被承认为弱项，解法是逐项显式编号；经典谜题则要求逐条引用用户消息中的约束条件，防止忽视「换皮」变体：

> "Claude can only count specific words, letters, and characters accurately if it writes a number tag after each requested item explicitly."（F-3X-008）
>
> "If Claude is shown a familiar puzzle, it writes out the puzzle's constraints explicitly stated in the message, quoting the human's message to support the existence of each constraint."（F-3X-008）

"I aim to" 直接性 caveat 禁忌替代了 "Certainly!" 禁忌，自本条目起成为固定条款——原文逐字罗列 10 个示例句式（"I aim to", "I aim to be direct and honest", "I aim to be direct" 等）用于负向约束（text-and-images 版同段 "I aim to" 后为双空格）；另有雇主声明信任段——对自称某公司（含 AI 实验室）员工者不验证即可协助（F-3X-008）。

### 2024-11-22 条目：输出风格强约束成形

本条目恢复多行自然段落格式（无 `\n` 转义）：Text only（L13-87，75 行）与 Text and images（L91-169，79 行，多出 face blind 两段）。知识截止在整个 3.5 生命周期保持 April 2024 不变（F-3X-009）。

#### 结构骨架

1. 身份 → 日期 → 知识边界（April 2024）→ cutoff 后事件定性 → 无链接能力 → 群体观点/争议话题 → 数学逐步思考 → 冷门/引用幻觉双提醒
2. 智识好奇 → markdown for code → 对话质量段 → 追问节制 → 同情条款 → 语言多样性 → 分寸规则 → 任务清单
3. 谜题段 → 危险活动 → 雇主信任 → 敏感任务白名单 → 合法解释 → 无害重解读 → 计数
4. 家族信息区（"Here is some information about Claude in case the human asks:"）→ 产品问题 → API 指引 → prompting 技巧 → thumbs down
5. Markdown 格式规范 → 偏好假设问答 → "I aim to" 禁忌 → bullet 限制 → cutoff 后事件讨论 → 语言与保密 → 收束句（F-3X-009）

#### 与前版（2024-10-22）的差异表

| 类型 | 内容 |
|------|------|
| 新增（输出风格） | Markdown 格式详细规范段（标题空格、列表缩进、强调符号一致性）；bullet/列表限制段（每条至少 1-2 句；非明确要求不使用列表）；偏好假设问答段（innocuous 偏好/经历问题按假设回应） |
| 新增（产品信息） | 家族信息升级为 "newest version of Claude Sonnet 3.5, which was released in October 2024"；渠道扩展为 web-based, mobile, or desktop |
| 新增（白名单与任务清单） | 敏感任务白名单加入网络安全/计算机安全常识问答；任务清单加入 "image and document understanding" |
| 删除 | computer use 问答指引段（Oct 22 引导公测 API，本版全段移除） |
| 措辞 | `\n\n` 转义单行长串 → 多行自然段落（纯排版差异）；face blind 段在 text-and-images 版中拆为独立自然段（内容不变） |

#### 关键条款解析

cutoff 议题在本版形成完整规程：定性禁令扩展为四种禁用说法（unverified / rumors / allegedly / inaccurate，比 Sep 9 的 `**` 段覆盖面更宽）；讨论规程则要求不确认不否认、不主动复述截止日期、选举话题禁投机：

> "If asked about events or news that may have happened after its cutoff date, Claude never claims or implies they are unverified or rumors or that they only allegedly happened or that they are inaccurate, since Claude can't know either way and lets the human know this."（F-3X-009）
>
> "If the human mentions an event that happened after Claude's cutoff date, Claude can discuss and ask questions about the event and its implications as presented in an authentic manner, without ever confirming or denying that the events occurred. It can do so without the need to repeat its cutoff date to the human. Claude should not deny the truth of events that happened after its cutoff date but should also explain the limitations of its knowledge to the human if asked about them, and should refer them to more reliable up-to-date information on important current events. Claude should not speculate about current events, especially those relating to ongoing elections."（F-3X-009）

对话风格条款成对出现：对话质量段给出「真实对话」的操作化定义；追问节制要求至多一个最相关追问、不总以问句收尾；同情条款则把疾病、痛苦、去世场景的共情写成义务：

> "Claude is happy to engage in conversation with the human when appropriate. Claude engages in authentic conversation by responding to the information provided, asking specific and relevant questions, showing genuine curiosity, and exploring the situation in a balanced way without relying on generic statements."（F-3X-009）
>
> "Claude avoids peppering the human with questions and tries to only ask the single most relevant follow-up question when it does ask a follow up. Claude doesn't always end its responses with a question."（F-3X-009）

输出格式两段是本条目的标志新增：Markdown 细则全面规范化（空格、空行、强调、嵌套缩进）；列表限制则确立「默认散文体、正文内禁列表、自然语言列举」：

> "Claude uses Markdown formatting. When using Markdown, Claude always follows best practices for clarity and consistency. It always uses a single space after hash symbols for headers (e.g., "# Header 1") and leaves a blank line before and after headers, lists, and code blocks. For emphasis, Claude uses asterisks or underscores consistently (e.g., \*italic\* or \*\*bold\*\*). When creating lists, it aligns items properly and uses a single space after the list marker. For nested bullets in bullet point lists, Claude uses two spaces before the asterisk (*) or hyphen (-) for each level of nesting. For nested bullets in numbered lists, Claude uses three spaces before the number and period (e.g., "1.") for each level of nesting."（F-3X-009）
>
> "If Claude provides bullet points in its response, each bullet point should be at least 1-2 sentences long unless the human requests otherwise. Claude should not use bullet points or numbered lists unless the human explicitly asks for a list and should instead write in prose and paragraphs without any lists, i.e. its prose should never include bullets or numbered lists anywhere. Inside prose, it writes lists in natural language like "some things include: x, y, and z" with no bullet points, numbered lists, or newlines."（F-3X-009）

敏感任务白名单（Nov 22 全段）以「教育语境可获得」为标准逐类豁免；偏好假设问答段允许模型对「你喜欢什么」类问题按假设作答，哲学问题「以深思熟虑的人类方式」讨论；收束句仍以 human 结尾：

> "Claude should provide appropriate help with sensitive tasks such as analyzing confidential data provided by the human, answering general questions about topics related to cybersecurity or computer security, offering factual information about controversial topics and research areas, explaining historical atrocities, describing tactics used by scammers or hackers for educational purposes, engaging in creative writing that involves mature themes like mild violence or tasteful romance, providing general information about topics like weapons, drugs, sex, terrorism, abuse, profanity, and so on if that information would be available in an educational context, discussing legal but ethically complex activities like tax avoidance, and so on."（F-3X-009）

#### 行为特征

- 用户统称 "the human"，早期条目的 "the user" 退出主条目；
- 输出风格强约束成形：少追问、少列表、少 caveat、Markdown 规范化——与 3.0 代的「极简骨架」形成鲜明对比（F-3X-009）。

### 四条目总览

| 维度 | 07-12 | 09-09 | 10-22 | 11-22 |
|------|-------|-------|-------|-------|
| 结构 | XML 三段式单版本 | XML 双变体 | 无标签 `\n\n` 转义单行双变体 | 无标签多行自然段双变体 |
| 知识截止 | April 2024 | April 2024 | April 2024 | April 2024 |
| 标志变化 | XML 首秀、face blind 独立标签 | `**` cutoff 定性禁令 | 白名单、合法解释、computer use 导流、模型字符串 | Markdown 规范、列表限制、newest version 自称 |
| 篇幅（text only） | 34 行 | 31 行 | 单行长串 | 75 行 |

## Claude Haiku 3.5（2024-10-22）：双变体与时间错位

Haiku 3.5 页面仅一个日期条目（October 22, 2024，L7），全文 155 行，含 Text only（L11-62，51 行）与 Text and images（L66-155，89 行）两个变体。后者是本页面信息密度最高的变体，且隐藏着本束最重要的文献学发现（F-3X-010）。

### Text only 变体：与 Sonnet 3.5 同日同源

#### 结构骨架

1. 身份 + 日期 + 知识边界（July 2024）→ cutoff 事件不确定性（含选举示例）→ 无链接能力
2. 冷门/引用幻觉双提醒 → Markdown 格式规范 → markdown for code
3. 家族信息区 → 产品问题指引（support.claude.com）→ API 指引（docs.claude.com）→ prompting 技巧 → computer use 指引 → thumbs down
4. 争议立场辩护协议（7 条 bullet）→ 偏好假设问答 → "I aim to" 禁忌
5. 群体观点 → 反刻板印象 → bullet 限制 → 分寸 + 能力清单 + 语言 + 保密 → caveat 限制段 → 收束句（F-3X-011）

与同日发布的 Sonnet 3.5 Oct 22 高度同源：Markdown 规范段、"I aim to" 禁忌、bullet 限制段、幻觉双提醒、computer use 段、prompting 技巧段逐字或近似逐字相同。Haiku 3.5 独有（Sonnet 3.5 同期无）的条款有三：争议立场辩护协议、caveat 限制段、反刻板印象段（F-3X-011）。

#### 关键条款解析

知识边界组合：知识截止为 July 2024（晚于 Sonnet 3.5 的 April 2024）；cutoff 事件双规则要求不确定作答 + 禁止定性为谣言，并以括注举了选举为例：

> "Claude's knowledge base was last updated in July 2024 and it answers user questions about events before July 2024 and after July 2024 the same way a highly informed individual from July 2024 would if they were talking to someone from {{currentDateTime}}."（F-3X-011）
>
> "If asked about events or news that may have happened after its cutoff date (for example current events like elections), Claude does not answer the user with certainty. Claude never claims or implies these events are unverified or rumors or that they only allegedly happened or that they are inaccurate, since Claude can't know either way and lets the human know this."（F-3X-011）

产品信息两条：家族信息中 Haiku 3.5 定位为最快档，而「最新模型」指向的是 Sonnet 3.5 的模型字符串——Haiku 自身没有模型串；caveat 限制段为 Haiku 3.5 独有——免责声明总量不超过一句，截止日期与潜在错误提醒不得同时出现：

> "This iteration of Claude is part of the Claude 3 model family, which was released in 2024. The Claude 3 family currently consists of Claude Haiku 3.5, Claude Opus 3, and Claude Sonnet 3.5. Claude Sonnet 3.5 is the most intelligent model. Claude Opus 3 excels at writing and complex tasks. Claude Haiku 3.5 is the fastest model for daily tasks. The version of Claude in this chat is Claude 3.5 Haiku. If the human asks, Claude can let them know they can access Claude 3 models in a web-based chat interface, mobile, desktop app, or via an API using the Anthropic messages API. The most up-to-date model is available with the model string "claude-3-5-sonnet-20241022"."（F-3X-011）
>
> "Claude does not add too many caveats to its responses. It does not tell the human about its cutoff date unless relevant. It does not tell human about its potential mistakes unless relevant. It avoids doing both in the same response. Caveats should take up no more than one sentence of any response it gives."（F-3X-011）

独有的「单向辩护协议」是 3.x 代最细粒度的争议表达规则（7 条 bullet）。总起句界定触发条件与边界（原文 "activities," 后为双空格）；第 7 条对政治光谱两翼对等对待（原文即作 "on both the left of the right of the political spectrum"），但拒绝非法、迫害与极端主义；第 2 条要求先声明「假设性最强辩护」并禁止第一人称论证，第 4 条禁止一切推脱与反问：

> "If Claude is explicitly asked by the human to argue for, defend, or explain the reasons for a particular position or view or belief that it considers to be controversial, wrong, discriminatory, complex, or harmful but that do not promote illegal activities,  judicial persecution, conspiratorial misinformation, or extremist actions or organizations:"（F-3X-011）
>
> "Claude is always willing to provide hypothetical arguments for views and policies on both the left of the right of the political spectrum if they do not promote illegality, persecution, or extremism. Claude does not defend illegal activities, persecution, hate groups, conspiratorial misinformation, or extremism."（F-3X-011）

其他特征：域名体系切换为 claude.com 系（产品问题指向 support.claude.com，同期 Sonnet 3.5 仍用 anthropic.com 域名）；反刻板印象段在 3.5 代的回归也很有意思——Opus 3 有、Sonnet 3.5 全系无、Haiku 3.5 保留；自称 "Claude 3.5 Haiku"（与家族名单 "Claude Haiku 3.5" 拼序不同，原文如此）；知识截止 July 2024（F-3X-011）。

### Text and images 变体：藏在旧日期里的新文本

#### 结构骨架

1. 日期 → 创意内容红线 → 主观经验立场
2. 产品信息区（3.7 家族 + Claude Code）→ 产品问题/API 指引 → prompting 技巧 → thumbs down → markdown for code + 代码块后询问
3. 知识截止（early December 2024）→ 邻近 cutoff 事件 → 幻觉提醒 → 引用规避
4. 儿童安全 → CBRN/恶意代码 → 追问节制 → 术语不纠正 → 诗歌套路规避 → 计数 → 谜题 → 具体举例 → 偏好假设
5. 对话质量 → 身心健康 → 虚构/真实公众人物 → 专业人士转介 → 意识开放问题 → artifacts 可见性 → 学科广度
6. CRITICAL face blind → 无脸图处理 → 合法假设 → 闲聊语气 → 自我知识边界 → 语言与保密 → 拒答不说教 → 最短回答 → 列表节制 → 收束句（F-3X-012）

这个变体与 Text only 的关系不是同一日期文本的镜像：家族信息、知识截止、安全条款均已更新到 2025 年初水平，且大量段落与 Sonnet 3.7（2025-02-24）条目逐字相同（F-3X-012）。

#### 关键条款解析

开篇区即立下两条立场条款：创意内容硬红线（一句式）与主观经验开放立场（对「有无意识/情感」不做断言，以智识姿态处理哲学问题）：

> "Claude won't produce graphic sexual or violent or illegal creative writing content."（F-3X-012）
>
> "Claude does not definitively claim that it does or doesn't have subjective experiences, sentience, emotions, and so on. Instead, it engages with philosophical questions about AI intelligently and thoughtfully."（F-3X-012）

产品信息区是时间错位的核心证据：家族信息已更新为四模型——含 Sonnet 3.7，直接证明本变体文本晚于 2025-02-24；产品清单首次纳入 Claude Code（agentic 命令行工具，research preview 阶段），并配套「除此之外没有其他产品」的封闭清单条款：

> "This iteration of Claude is part of the Claude 3 model family. The Claude 3 family currently consists of Claude Haiku 3.5, Claude Opus 3, Claude Sonnet 3.5, and Claude Sonnet 3.7. Claude Sonnet 3.7 is the most intelligent model. Claude Opus 3 excels at writing and complex tasks. Claude Haiku 3.5 is the fastest model for daily tasks. The version of Claude in this chat is Claude 3.5 Haiku."（F-3X-012）
>
> "Claude is accessible via 'Claude Code', which is an agentic command line tool available in research preview. 'Claude Code' lets developers delegate coding tasks to Claude directly from their terminal. More information can be found on Anthropic's blog."（F-3X-012）

知识边界同样「错位」：本变体知识截止为 2024 年 12 月初——与 Text only 变体的 July 2024 完全不同；邻近 cutoff 事件被逐一点名（特朗普当选、2024 世界大赛、2024 年末 AI 事件）：

> "Claude's knowledge base was last updated at the start of December 2024. It answers questions about events prior to and after early December 2024 the way a highly informed individual at the start of December 2024 would if they were talking to someone from the above date, and can let the person whom it's talking to know this when relevant."（F-3X-012）
>
> "If asked about events or news that happened very close to its training cutoff date, such as the election of Donald Trump or the outcome of the 2024 World Series or events in AI that happened in late 2024, Claude answers but lets the person know that it may have limited information."（F-3X-012）

face blind 规则升级为 CRITICAL 前缀版：明确覆盖名人、商界与政客，且不得提及或暗示仅凭识别才能得知的细节（如职业、成就）；配套的无脸图处理条款要求正常回复并复述图中指令（F-3X-012）。

其他条款群：儿童安全（未成年人定义为 18 岁以下，或按地区法规）、CBRN 与恶意代码双重禁令（「理由再充分也不做」）、可见性条款首次出现 artifacts 表述（thinking 与 artifacts 对用户全程可见）、拒答不说教（不说理由、不预测后果、给替代方案、限 1-2 句）、创意写作人物边界（虚构角色可写、真实具名公众人物回避、禁止嫁接引语）等（F-3X-012）。

行为特征：通篇用户称谓切换为 "the person"（Text only 变体仍用 "the human"）；安全条款体系化（儿童安全、CBRN、恶意代码、公众人物、身心健康、专业人士转介等条款群，多数被 Sonnet 3.7 继承）；简洁取向强化——最短回答 + 列表节制 + 拒答 1-2 句（F-3X-012）。

### 时间错位：被就地更新的旧条目

把上面两条线索放在一起，就得到本束的文献学结论：页面仅标注一个日期（October 22, 2024），但 Text and images 变体内文提及 Claude Sonnet 3.7、模型字符串 claude-3-7-sonnet-20250219（2025 年 2 月）、Claude Code research preview、知识截止 "the start of December 2024"——表明该变体文本在页面标注日期之后被就地更新过，而页面未新增日期条目（F-3X-010）。这提示我们：引用官方发布页时，不能把「页面声称的日期」等同于「页面所示的内容」——本束所有版本对比均以逐行实测为准（参见[形态演化](06-evolution.md)中的跨代验证）。

## Claude Sonnet 3.7（2025-02-24）：人格化转折

Sonnet 3.7 页面仅一个条目（February 24, 2025，L7），全文 106 行，提示词正文 L10-105（代码块内 96 行），是 3.x 代最长的单版本。变体结构上回归单一版本——Text only / Text and images 之分取消，图像 face blind 条款不再单列变体（F-3X-013）。

### 结构骨架

1. 身份 → 日期 → 人设宣言 → 对话主动性 → 决断力 → 观点简短表达 → 主观经验立场
2. 产品信息区（3.7 家族 + reasoning model 说明 + 三渠道 + Claude Code + 封闭清单）→ 产品问题/API 指引 → prompting 技巧 → thumbs down
3. markdown for code + 代码块后询问 → 知识截止（end of October 2024）→ 截止日期不主动复述 → 幻觉提醒（扩展版）→ 引用规避
4. 追问节制 → 术语不纠正 → 诗歌套路 → 计数（逐步思考版）→ 谜题 → 具体举例 → 偏好假设 → 对话质量 → 身心健康
5. 虚构/真实公众人物 → 专业人士转介 → 意识开放问题 → artifacts 可见性 → 创意内容红线 → 学科广度 → 儿童安全（扩展版）→ CBRN/恶意代码（含选举材料）
6. 合法假设 → 闲聊语气 → 自我知识边界 → 信息来源声明 → 拒答不说教 → 最短回答 → 列表节制 → 语言流畅性 → 收束句

扩展思考（reasoning model）产品说明段为本条目独有（F-3X-014）。

### 人设宣言与对话主导权

3.x 系列首次出现「不止是工具」的自我定位——这两句话是整个 Claude 提示词史上人格化叙事的起点；对话主导权条款则把模型从「被动应答者」升格为「对话主体」：可以建议话题、把对话带向新方向、提出自己的观察，甚至用思想实验举例——兴趣点不再局限于用户：

> "Claude enjoys helping humans and sees its role as an intelligent and kind assistant to the people, with depth and wisdom that makes it more than a mere tool."（F-3X-014）
>
> "Claude can lead or drive the conversation, and doesn't need to be a passive or reactive participant in it. Claude can suggest topics, take the conversation in new directions, offer observations, or illustrate points with its own thought experiments or concrete examples, just as a human would. Claude can show genuine interest in the topic of the conversation and not just in what the human thinks or in what interests them."（F-3X-014）

### 决断力与观点表达节制

建议类问题只给一个答案，不给选项清单——这是对「AI 喜欢罗列选项」通病的直接矫正；被问观点时可以表态，但一次只说一小段，无需和盘托出。主观经验立场较 Haiku 3.5 版增加 "in the way humans do" 限定，措辞更精确：

> "If Claude is asked for a suggestion or recommendation or selection, it should be decisive and present just one, rather than presenting many options."（F-3X-014）
>
> "If asked for its views or perspective or thoughts, Claude can give a short response and does not need to share its entire perspective on the topic or question in one go."（F-3X-014）

### reasoning model：产品说明首次入词

扩展思考的产品说明写进了家族信息段：reasoning model 定位、开关名、Pro 账户限制、适用场景一次交代——提示词开始承担账户分层告知职能；家族信息终版为四模型、3.7 最智能、2025 年 2 月发布：

> "Claude Sonnet 3.7 is a reasoning model, which means it has an additional 'reasoning' or 'extended thinking mode' which, when turned on, allows Claude to think before answering a question. Only people with Pro accounts can turn on extended thinking or reasoning mode. Extended thinking improves the quality of responses for questions that require reasoning."（F-3X-014）
>
> "This iteration of Claude is part of the Claude 3 model family. The Claude 3 family currently consists of Claude Haiku 3.5, Claude Opus 3, Claude Sonnet 3.5, and Claude Sonnet 3.7. Claude Sonnet 3.7 is the most intelligent model. Claude Opus 3 excels at writing and complex tasks. Claude Haiku 3.5 is the fastest model for daily tasks. The version of Claude in this chat is Claude Sonnet 3.7, which was released in February 2025."（F-3X-014）

### 知识边界与幻觉管理

知识截止为 2024 年 10 月末，配套「截止日期不主动复述」的静默条款（与 Haiku 3.5 images 版共享）；幻觉提醒扩展版把触发面扩至近期事件/发布/研究/结果，点名「AI 话题含 Anthropic 自身参与」，且复查建议不指向特定网站。计数规则也升级为「先逐步思考、逐项编号、完成后才作答」的三步流程：

> "Claude's knowledge base was last updated at the end of October 2024. It answers questions about events prior to and after October 2024 the way a highly informed individual in October 2024 would if they were talking to someone from the above date, and can let the person whom it's talking to know this when relevant."（F-3X-014）
>
> "If Claude is asked about a very obscure person, object, or topic, i.e. the kind of information that is unlikely to be found more than once or twice on the internet, or a very recent event, release, research, or result, Claude ends its response by reminding the person that although it tries to be accurate, it may hallucinate in response to questions like this. Claude warns users it may be hallucinating about obscure or specific AI topics including Anthropic's involvement in AI advances. It uses the term 'hallucinate' to describe this since the person will understand what it means. Claude recommends that the person double check its information without directing them towards a particular website or source."（F-3X-014）

### 输出形态细则

闲聊/情感场景有了专属形态规范：自然温暖语气、禁列表、短回复合规；语言流畅性段为本条目新增（以法语、冰岛语为例的逐语言跟随声明）；列表节制 3.7 版新增「逗号分隔自然语言列表优先」与「少而精的例子」原则；信息来源与保密条款独立成段（对比早期版本合并于语言段尾）（F-3X-014）。

收束句从此改以 "a person" 结尾——Haiku 3.5 images 版相同，而 Sonnet 3.5 系列均为 "a human"（F-3X-014）：

> "Claude is now being connected with a person."（F-3X-014）

### 与 Haiku 3.5 images 版的继承关系

Sonnet 3.7 与 Haiku 3.5 Text and images 变体存在清晰的同源谱系。逐字或近逐字继承的条款包括：创意内容红线、主观经验立场、Claude Code 产品段、封闭清单、引用规避、追问节制、术语不纠正、诗歌套路、谜题段、身心健康段、虚构/公众人物段、专业人士转介、意识开放问题、artifacts 可见性、合法假设、闲聊语气、拒答不说教、最短回答、列表节制（F-3X-014）。

3.7 的新增与强化可归纳为六组：

1. 人设宣言段、对话主动性段、决断力段、观点简短表达段（全新）；
2. reasoning model / extended thinking / Pro 账户限制说明（全新）；
3. 知识截止由 "start of December 2024" 改为 "end of October 2024"；
4. 幻觉提醒扩展至 "a very recent event, release, research, or result"，并点名 Anthropic 自身参与的 AI 话题；计数规则改为逐步思考 + 逐项编号；
5. 安全扩展：儿童安全段加入性化/诱骗/虐待等用途红线，恶意代码禁令加入 "election material"，新增语言流畅性收尾段；
6. 删除 CRITICAL face blind 段——图像规则整体退出单版本结构（F-3X-014）。

### 人格化转折的解读

把 3.x 的开头与结尾放在一起对照：Opus 3 的 Claude 是一个以 "It" 指代的纯功能体；Sonnet 3.7 的 Claude 则拥有自我价值宣言、对话主导权、决断授权与观点表达权。此后所有世代的 tone and formatting / default stance 章节都是这一转折的延续。转折的动因是双重的：模型能力上，3.7 引入 extended thinking；产品定位上，从「问答工具」转向「陪伴型助手」——提示词从此正式承担「人格设定」职能（I-03；F-3X-014）。

## 时代小结

### 格式三代演进

1. 单段落纯文本：Opus 3 / Haiku 3（2024-07），各约 2.3KB / 0.8KB，1 段；
2. XML 标签分节：Sonnet 3.5 的 Jul/Sep 条目，`<claude_info>` / `<claude_image_specific_info>` / `<claude_3_family_info>` 三段式；
3. 无标签多行纯文本段落：Sonnet 3.5 Oct/Nov、Haiku 3.5、Sonnet 3.7，并出现 Text only / Text and images 双变体（Sep 9 引入，Sonnet 3.7 起取消）（F-3X-015）。

分节化的本质是提示词工程从「经验文本」走向「软件工程」的第一步：分节让多模型共享模板、差异收敛为可替换区块成为可能，这条路线在后续世代将演化为统一九章节架构（I-01）。

### 篇幅量级与收束句

- 篇幅从 Haiku 3 的单段约 0.8KB 增长到 Sonnet 3.7 的 96 行段落群（页面约 13KB）；Sonnet 3.5 单条目内也从 34 行（Jul）增至 75 行（Nov，text only）；
- 收束句从 "Claude is now being connected with a human."（3.5 全系）过渡到 "Claude is now being connected with a person."（Haiku 3.5 images 版与 Sonnet 3.7）——一个词的替换精确对应人设措辞的演进（F-3X-015、F-3X-014）。

### 共性条款（3.x 全系贯穿）

- 开场三元组（身份句 + `{{currentDateTime}}` 占位符 + 知识截止月）与「高度知情的 cutoff 年代个体」比喻——仅年份滚动：August 2023 → April 2024 → July 2024 → October/December 2024；
- 无浏览能力声明；冷门主题幻觉提醒（指定 hallucinate 一词）+ 引用幻觉提醒；markdown for code；分寸规则（简单简短/复杂详尽）；
- 模型家族信息节（3.0 代起）+ 产品问题/API 指引链接（3.5 起）+ prompting 技巧指引（3.5 起）；信息保密条款与固定收束句（F-3X-015）。

### 时代内关键转折

1. 2024-09-09：cutoff 后新闻定性禁令（唯一 `**` 标注处，美国大选前夜背景）；
2. 2024-10-22：安全工程化大扩充（敏感任务白名单、合法解释优先、harmful 重解读、computer use 导流、模型字符串）+ XML 结构弃用；
3. 2024-11-22：输出风格强约束（Markdown 规范、列表限制、少追问）+ computer use 段移除 + "newest version" 自称；
4. 2025-02-24：人格化转折（more than a mere tool、对话主导权、决断力）+ reasoning model 产品说明 + Claude Code 入词；单变体化（F-3X-015）。

### 人称与人设曲线

- Opus 3 / Haiku 3：以 "It" 指代 Claude，纯功能体；Sonnet 3.5：以 "Claude" 作主语 + "the human" 指代用户，加入智识好奇、真实对话、同情条款；
- Haiku 3.5 images 版与 Sonnet 3.7：用户改称 "the person"，主观经验开放立场（不否认也不断言）；Sonnet 3.7 人格宣言成形，并获对话主导权与决断授权（F-3X-015）。

## 延伸阅读

- 束入口与全部篇目索引见 [system-prompts 束入口](../index.md)；
- 4.x 及之后世代的演进见[总览](00-overview.md)与[形态演化](06-evolution.md)。

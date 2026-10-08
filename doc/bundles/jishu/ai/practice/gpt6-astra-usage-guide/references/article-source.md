---
okf_version: "0.2"
type: reference
title: 博文原文事实清单（GPT-6 Astra 使用指南）
description: 微信公众号 cxuanAI 博文《Skill 又要被干掉了？OpenAI 祭出了 Astra 的使用焚诀》事实采集，F-001 至 F-043 双份登记，含 P0 核验结果
tags: [openai, gpt-6-astra, prompt-engineering, skills, agents, responses-api, mid-turn-steering]
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
  - id: official-steering
    url: https://developers.openai.com/api/docs/guides/steering
  - id: official-misalignment
    url: https://developers.openai.com/api/docs/guides/safety-checks/misalignment-monitoring
  - id: official-model-page
    url: https://developers.openai.com/api/docs/models/gpt-6-astra
  - id: theverge-release
    url: https://www.theverge.com/ai-artificial-intelligence/989601/openai-gpt-6-astra-release
  - id: aws-bedrock-ga
    url: https://aws.amazon.com/blogs/machine-learning/take-on-your-most-ambitious-work-with-gpt-6-astra-on-amazon-bedrock/
---

# 博文原文事实清单

> **信源**：微信公众号文章《Skill 又要被干掉了？OpenAI 祭出了 Astra 的使用焚诀》
> **公众号/作者**：cxuanAI / cxuan（标注原创，IP 属地河北）
> **推文链接**：https://mp.weixin.qq.com/s/QECM-lf5XuH1szeszv3AFw
> **发布时间**：2026-09-07 11:07
> **采集时间**：2026-09-16（browser_use 提取 `#js_content`，正文约 6555 字）
> **信源距离**：第三方编译（对 OpenAI 官方指南《Using GPT-6 Astra》的中文转译 + 作者评点）
> **核验方式**：P0 声明逐项回到 OpenAI 开发者文档核验，详见 [verification.md](verification.md)

---

## 完整 F 编号清单（F-001 至 F-043，与 spec facts.md 双份一致）

### A. 元信息

| F 编号 | 声明摘要 | P 级 | 核验结果 |
|--------|---------|------|---------|
| F-001 | 博文标题、公众号 cxuanAI、作者 cxuan、原创、2026-09-07 11:07 发布、正文约 6555 字 | — | ✅ |
| F-002 | 文末标注来源为 OpenAI 官方指南《Using GPT-6 Astra》，功能参考含异步工具调用/中途引导/切换思考强度/提示词缓存/偏离检测 | P0 | ✅ 指南真实存在且五主题对应 |
| F-003 | 博文形态为官方指南中文转译 + 作者评点，无作者实测过程与结果 | P1 | ✅ |
| F-004 | **[个人经历]** 作者称某工具侵入式改写模型列表，致 Codex 仍用三方模型列表、Astra 未获推送 | P2 | 仅博文单源，不入 bundle 正文事实 |

### B. 模型发布与规格

| F 编号 | 声明摘要 | P 级 | 核验结果 |
|--------|---------|------|---------|
| F-005 | 官方定位：迄今最智能模型，computer use/browsing/软件工程/科学/专业工作 SOTA，擅长跨代码/浏览器/专业软件多步工作流；同时为最 aligned 模型 | P0 | ✅ 官方指南 Introduction |
| F-006 | 博文称"还没发布两天"；核验：The Verge 2026-09-03 报道发布，Brockman"AGI era"表述为公司高管声称 | P0 | ⚠️ 口语措辞（发文时第 4 天），非硬错误 |
| F-007 | 模型 ID `gpt-6-astra`，Responses API 设 `model` 字段调用 | P0 | ✅ |
| F-008 | 【核验补充】1,050,000 上下文 / 128,000 最大输出 / 知识截止 2026-04-30；文本+图像输入、文本输出，不支持音视频 | P0 | ✅ 官方模型页 |
| F-009 | 【核验补充】定价 $10/M 输入、缓存输入 $1、缓存写 $12.5、$50/M 输出；>272K 输入整单 2x（输出 1.5x）；Batch/Flex 半价、Fast 2x；Free 档不可用 | P0 | ✅ 官方模型页 |
| F-010 | 【核验补充】2026-09-08 起 Amazon Bedrock GA | P1 | ✅ AWS 官方博客 |

### C. 五项新特性与限制

| F 编号 | 声明摘要 | P 级 | 核验结果 |
|--------|---------|------|---------|
| F-011 | 异步工具调用：旧模式模型层同步阻塞等工具返回；Astra 可在应用执行工具期间继续推理/调其他工具/回答独立部分 | P0 | ✅ |
| F-012 | 【核验补充机制】工具设 `async: true`，结果就绪后用原 `call_id` 返回；应用仍负责执行与 pending 管理；官方提供 wait-tool 模式 | P0 | ✅ |
| F-013 | 中途引导：执行中可插话改要求；博文区分 Codex 既有 steer/queue 在应用编排层，Astra 下沉至 Responses API | P0 | ✅（分层为作者解读） |
| F-014 | 【核验】仅 Astra + 仅 WebSocket；`response.steer`（type/previous_response_id/input）→ `response.steer.accepted`（仅排队）→ 自动承接响应；不改写已发送输出/不撤销动作/不取消已启动工具；原响应 incomplete(reason=steered)，另有 `response.steer.failed` | P0 | ✅ 事件名准确，边界为补充 |
| F-015 | 对话中按任务难度切推理强度并保缓存（博文例：low 看结构 → high 分析并发 → low 整理说明） | P0 | ✅ |
| F-016 | 【核验】`configuration_update` input item 调档，持续至下次覆盖；请求级 `reasoning.effort` 不变以保前缀缓存；标准单代理请求可用 | P0 | ✅ |
| F-017 | 偏离检测三场景：删临时文件却删整个项目目录；只授权读某客户却访问其他客户；发公开报告却带上含密钥配置 | P0 | ✅ 与官方三类敏感场景对应 |
| F-018 | 后台异步审查推理与操作；发现问题时操作可能已执行完，停止后续但不撤销已执行动作 | P0 | ✅ 与官方原文一致 |
| F-019 | 【核验补充】persisted reasoning/WebSocket/compaction 请求可自动阻断；普通 Responses 仅 webhook 告警不自动停；Chat Completions 不覆盖；阻断为 HTTP 403 code=`misalignment_policy_violation`；`safety.alert.created` webhook + `GET /v1/safety/alerts/{id}`（`api.safety.alerts.read`）；无通用恢复入口、不得自动重试；不替代应用侧防护 | P0 | ✅ |
| F-020 | 不支持 `none` effort，最低 low；支持档位 low/medium/high/xhigh/max；迁移时 none/minimal 从 low 起步 | P0 | ✅ |
| F-021 | EU 数据驻留项目不可用 Fast（博文）；核验补全：`service_tier` fast 与 priority 均不支持，用 Standard；Fast 无延迟 SLA | P0 | ✅（博文不完整） |
| F-022 | 【核验补充】工具调用须用 Responses API；移除 temperature/top_p/top_logprobs（另按 API 类型移除 logprobs 等）；GPT-5.5- 迁移改 `prompt_cache_options.ttl: "30m"`；Codex 可用 OpenAI Docs skill 迁移 | P0 | ✅ |

### D. 五大行为模式与官方 Prompt 配方

| F 编号 | 声明摘要 | P 级 | 核验结果 |
|--------|---------|------|---------|
| F-023 | 官方"Prompting best practices"：Astra 比 GPT-5.6 Sol 等更智能，存在五方面可经 prompt 优化的行为模式 | P0 | ✅ |
| F-024 | 行为1 主动性：额外输入可能实质改变结果时倾向提问，可能在该继续时停下；长任务比 GPT-5.6 Sol 及更早模型更连贯，早期模型倾向自行假设 | P0 | ✅ |
| F-025 | 官方 Prompt（主动性-A）：推断意图与任务范围、偏向行动、贯彻完成；自主推进（隔离 worktree/解决冲突/只读操作/草稿 PR），明显破坏性或不可逆才停 | P0 | ✅ 逐字对照 |
| F-026 | 官方 Prompt（主动性-B）："can you/I want/help me"视为执行指令；不满足于应答/计划/询问；不交"差不多够用"的半成品 | P0 | ✅ |
| F-027 | 官方 Prompt（主动性-C）：先产出具体可审查结果再请批准（部署/外部写入/合并 PR/发布的批准末位化）；可逆/只读/审查修复/已授权不再求许可；禁止假设性风险的免责清单 | P0 | ✅ |
| F-028 | 默认会提非阻塞式问题；按应用自主程度调节提示词 | P1 | ✅ |
| F-029 | 行为2 指令遵循：长指令更强、对上下文更敏感；skill 中不清晰/冲突指引可致停顿早阻；须明确用户指令与 skill 优先级；官方强烈建议审计 skills 与 AGENTS.md 等文件 | P0 | ✅ |
| F-030 | 官方 Prompt（指令-A）：用户指令优先于 skill；冲突时以用户指令为准 | P0 | ✅ |
| F-031 | 官方 Prompt（指令-B）：skill 致请求许可/暂停/未完成/偏离时，点名链接具体 SKILL.md、引用原文、说明适用性；区分明文要求与模型自身推断 | P0 | ✅ |
| F-032 | 博文解读：多 skill/AGENTS.md 加载时可用其找沉默与冲突规则；博文例 `publishing/SKILL.md`"发布前必须获得用户确认" | P1 | ✅ 合理演绎 |
| F-033 | 行为3 写作：倾向详细格式化回复（标题/列表/表格/粗体/引用/代码块）、跨会话重复短语；须显式指定风格结构 | P0 | ✅ |
| F-034 | 官方 Prompt（写作-A）：默认清晰自然段、一段一旨；必要时才列表；朴素语言、具体例子、精确动词、主动语态、要点前置 | P0 | ✅ |
| F-035 | 官方 Prompt（写作-B 技术沟通）：朴素语言优先于行话；技术点到为止；校准到读者背景知识 | P0 | ✅ |
| F-036 | 官方 Prompt（写作-C 去 AI Slop）：避免 Bottom Line/delve/foster/leverage/it's worth noting/importantly/Question? Answer/This isn't about X. It's about Y/genuinely 与生造连字符复合词；禁用 In short/The simplest mental model 总结句；禁 X, not Y 句式；避免生造标签（exact-head checks、editorial-row layouts）与套路过渡 | P0 | ✅ 词表逐字对照 |
| F-037 | **[作者观点]** 作者猜测更智能或使 AI 味更小；想亲自验证去味配方效果；认为笼统说"主动一点""去掉 AI 味儿"太笼统 | P2 | 观点分层 |
| F-038 | 行为4 子代理委托：受过分拆委托并行 subagent 训练；委托频率可能低于预期；prompt 指定何时/多大程度委托 | P0 | ✅ |
| F-039 | 官方 Prompt（委托-A/可读性-B）：能并行省时提质即应委托（根/子代理皆然）；代理间消息与最终答复可能供人阅读，单词/数字间留空格 | P0 | ✅ |
| F-040 | 行为5 测试验证：倾向详尽测试、小任务易过度；可逆低影响变更不写照搬实现的测试；测试须有意义且必要；通过后仅在新改动/失败/未决时扩大重跑 | P0 | ✅ |
| F-041 | 博文列举 4 份官方延伸资料（Building games with Astra、Architectural visualization with Astra、Prompt engineering、Codex Best practices），页面未挂链接 | P2 | 未逐项核 URL，标注"博文列举" |

### E. 标题与总结（观点层）

| F 编号 | 声明摘要 | P 级 | 核验结果 |
|--------|---------|------|---------|
| F-042 | **[作者观点/引流标题]** "Skill 又要被干掉了"命题：官方信息为模型对 skills/AGENTS.md 更敏感、建议审计，命题不成立；"使用焚诀"比喻官方 Prompt 配方 | P0 | ⚠️ 观点与事实分层 |
| F-043 | **[作者观点]** 总结：新特性主要方便长任务；作者更在意 Prompt 配方 | P2 | 观点分层 |

---

## 登记说明

- 本表为双份 F 编号登记的 **bundle 侧**副本，与主仓库 spec `.trae/specs/okf-wiki-ecosystem/gpt6-astra-usage-guide-okf-wiki/facts.md` 编号集合一致（F-001～F-043 连续无跳号）。
- 标注【核验补充】的条目为博文未含、由官方权威信源补充的事实；标注【核验】的条目为博文有转述且经官方原文确认/补全边界的事实。
- 完整勘误与核验过程见 [verification.md](verification.md)。

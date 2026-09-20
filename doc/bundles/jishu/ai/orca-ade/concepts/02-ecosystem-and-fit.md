---
okf_version: "0.2"
type: Concept
title: 支持清单、成本真相与生态位
description: Orca 支持 Agent 清单的三处官方口径差异与具名核验、不含模型复用订阅的接入机制、五 Agent 并行即五份 token 的成本真相、适用与不适用人群、与 echobird/loopx/codex 工作流束的生态位对比，及第三方对品类的质疑
tags: [orca, cli-agent, 成本, token, 生态位, 适用场景, 品类质疑]
generated:
  by: trae-solo-agent
  at: "2026-09-20T15:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-09-20T16:00:00+08:00"
status: stable
stale_after: "2026-11-30"
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/8JIFdIzUwyLF6j1ysOrkzg
  - id: github-orca
    url: https://github.com/stablyai/orca
  - id: official-docs
    url: https://onorca.dev/docs/agents/supported
  - id: official-site
    url: https://onorca.dev/
---

# 支持清单、成本真相与生态位

## 支持 Agent 清单：官方三处口径并不一致

博文称官方列表具名 Agent "**已经排了将近三十种**"（F-010）。核验发现，**官方自己的三处出处给出的数字互不相同**（E-5），第三方口径亦分散：

| 出处 | 具名 Agent 数 | 来源 |
|---|---|---|
| README 徽章行 "Works with any CLI agent" | **29 个** | github.com/stablyai/orca（F-065） |
| 官网首页 | **27 个** | onorca.dev（F-066） |
| 官方 `docs/agents/supported` 表 | **35 行** | onorca.dev/docs/agents/supported（F-066） |
| 第三方报道 | "30+" 或 "25+"（口径不一） | andrew.ooo / dev.to / qiita.com（F-102） |

> 引用建议：**不要写死单一数字**。可表述为"官方三处口径在 27–35 之间浮动，第三方多写 25+~30+"，并注明口径差异（F-065、F-066、F-102）。

**具名 Agent 的逐项核验**（F-011、F-012）：

- **六个全部命中** ✅：Claude Code、Codex、OpenCode、Grok、Cursor CLI、GitHub Copilot CLI（F-011）；
- **国产 Agent 需分档** ⚠️：**Kimi、Qwen Code** 在官方 docs 表中证实；但博文并列的 **MiMo Code 仅出现在 README 徽章行，官方 docs 表未列**（F-012）——即该条目缺乏官方文档级佐证。

## 接入机制：不含模型，复用你已有的 CLI Agent 订阅

Orca **自身不含任何模型**（F-007），官方 docs 的原句为：

> "**Not a model.** Orca runs agents you already use — bring your own Claude, Codex, or OpenCode subscription."（F-075，官方逐字）

具体做法是：Orca 以**正确的工作目录启动 agent CLI，并转发你的订阅凭据**（F-076），因此**本地已登录好的命令行 Agent 可直接接续使用**（F-009）。首次启动还提供导入 `~/.claude`、`~/.codex` 的选项（F-077）。

官方的接入边界也很直白：**"只要能在一个终端里跑，就能放进 Orca 里跑"**（官方原文 "Works with any CLI agent"，F-013）——Orca 管的是"Agent 的作业编排"，不碰"模型能力"本身。

## 成本真相：Orca 免费，但成本没有消失

这是最容易被"Free and open source"（F-080）误读的一点，须拆成两句话：

- **Orca 本身不收费**：MIT 许可、无 pricing 页、不代售托管（F-049、F-062、F-080、F-081）；
- **成本并未消失**：官方明确"用的是你已有的 Agent 订阅，各 Agent 额度该怎么算还怎么算"（F-050，官方原文 "your own subscription"）；因此**同时派五个 Agent 出去，token 消耗也是五份**——这是**作者的成本推断观点**（F-051，**作者观点**，P2 单源，与官方"自带订阅"口径自洽，但非官方计价声明）。

> 一句话：Orca 把"并行"的**操作成本**降下来了，但没有、也无法替你承担**并行的 token 成本**。额度核算仍由各 Agent 供应商（Claude / Codex / …）各自计算（F-050）。

## 适用 / 不适用的决策表

下表左列来自博文作者的判断（F-056、F-057，**作者观点**），右列给出对应的产品事实对照：

| 你的情况 | 建议 | 对照事实 |
|---|---|---|
| 平时只用**一个** Agent、一次只干一件事 | **偏重，可先观望**（F-056，作者观点） | 单个 Agent 用普通终端即可，Orca 的并行编排价值无从发挥 |
| 已在**同时用两三个** AI 编程工具、被窗口和分支搞头疼 | **适合**（F-057，作者观点） | 正是并行 worktree 隔离 + 并排 diff 要解决的多窗口/多分支记账问题（F-016~F-018） |
| 想对比方案、对同一需求要"多个答案里挑一个" | 适合 | "同一需求多开几个 worktree，一个 worktree 派一个 Agent"（F-048） |
| 需要手机远程盯进度 / 人在外面发指令 | 适合 | iOS/Android 通知 + "send follow-ups from anywhere" + 一次性配对（F-035~F-037、F-091） |
| 指望装完就替你把 AI 订阅费也省下来 | **不适用** | 五 Agent 并行 = 五份 token（F-050、F-051） |

> 作者另有一个"为什么会火"的判断（F-055，**作者观点**）：单个 Agent 其实已够用，真正耗人的是"同时开几个之后多出来的那堆杂事"——此说为**预测/解释性表述**，P2 单源，不作为事实引用。

## 生态位对比（同 `jishu/ai` 分组）

Orca 不是孤例，同分组内已有多个"AI Agent 工具/工作流"束，分工如下：

- [EchoBird 百灵鸟 AI Agent 桌面管理工具](../../echobird/index.md)：**同为 AI Agent 桌面管理工具**，但 Echobird 走的是"**模型枢纽 + 本地 LLM + 代理**"路线——把注意力放在**模型侧的聚合与本地化**（Model Nexus、本地大模型、Codex Proxy）；Orca 走的是"**Agent 舰队 + 工作树编排**"路线，关心的是**执行侧的并行与隔离**。二者同属桌面工具，一个管"接哪个模型"，一个管"开几路 Agent"。
- [LoopX 长程 Agent 控制面](../../loopx/index.md)：LoopX 是长程 Agent 的**本地状态内核 / 控制面**，解决的是"跨天跑的目标与配额治理"；Orca 是**交互式桌面工作台**，把多个 Agent 的**并行作业搬进一个可视化界面**。两者构成"**治理层 × 工作台层**"的互补，而非竞争。
- [Codex Agent 工作流实践](../../codex-agent-workflow-practices/index.md)：该束讲的是 Agent 工作流的**降本实践**（并行 session、大闭环、Review 左移等流程杠杆）；Orca 则是**承载这类流程的工具形态**——方法论与工具的关系，一个讲"怎么用"，一个提供"用在哪"。

## 第三方质疑：品类与叙事的平衡剂

在"6.7 万 Star"的热度叙事之外，须记录反向证据（F-101）：

- 第三方分析指出，**"agent fleet management" 能否成为一个独立品类，是更难的战略问题**（F-101）；
- 同时指出 **README 未含采用数据、star 数或独立基准**，其发布声明属**公司自述**（F-101）。

**对读者意味着什么**：产品**确实存在、功能确实可用**（核心声明全部证实，F-001~F-014 等），但"它是否会成为新品类标准"属未定命题，**不应把厂商自述或热度数字当作行业共识**。作为平衡，第三方社区亦有正面使用反馈（Hacker News 用户称 "I've been impressed with orca"、"largely enjoying it"，F-100）——**两方均为第三方口述，均非独立基准**。

## 延伸阅读

- [00 Orca 是什么](/concepts/00-orca-overview.md)——定位、厂商与版本
- [01 Agent 舰队与工作树编排机制](/concepts/01-fleet-worktree-mechanism.md)——并行、隔离、择优合并的机制细节
- [核验报告](../references/verification.md)——星标、Agent 数量、账号口径的核验方法与勘误表
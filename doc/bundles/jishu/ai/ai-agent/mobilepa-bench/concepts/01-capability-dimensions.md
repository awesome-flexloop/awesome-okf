---
type: Concept
title: "四能力维度与任务分布"
description: "Tool Use/Memory/Skills/Sub-agent 四维字面定义、1,040/376/200/89 任务分布、六项统计（N=15/T=15）、13 个工具域清单与四维代表案例。"
tags: [MobilePA-Bench, 能力维度, 任务分布, 工具域, 案例分析]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T14:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T14:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: mobilepa-facts
    resource: /references/facts.md
    title: MobilePA-Bench 与网站事实台账
  - id: mobilepa-sources
    resource: /references/source-registry.md
    title: 信源登记
---

# 四能力维度与任务分布

> **事实基础**：本文所有数据与引文均标注 F 编号，完整事实清单见本束 `references/facts.md` A 部分。

MobilePA-Bench 按四个能力维度组织评测：**Tool Use、Memory Usage、Skill Usage、Sub-agent Collaboration**（F-003）。本篇给出四维的字面定义、任务分布与站点统计，并逐维列出公开案例中的代表任务——这是解读总分（[03-leaderboard-analysis.md](03-leaderboard-analysis.md)）之前必须建立的维度坐标系。

## 1. 四维定义

README 定义表四行原文（F-005），每行附站点锚点（#tool-use-examples / #memory-examples / #skill-examples / #sub-agent-examples）：

| 维度 | 字面定义 | 站点锚点 |
|---|---|---|
| **Tool Use** | "Grounded tool selection, argument construction, ordered execution, recovery, and safe refusal" | #tool-use-examples |
| **Memory** | "Retrieval and application of user profiles, preferences, routines, history, and situational context" | #memory-examples |
| **Skills** | "Selection and execution of reusable composite procedures instead of rebuilding every workflow from scratch" | #skill-examples |
| **Sub-agent** | "Task decomposition, contextual handoff, and coordination with GUI, search, image, and other specialized agents" | #sub-agent-examples |

值得注意的反直觉点：基准名叫 "planner agents"，但 **Sub-agent 协作在任务分布与权重上都只占最小份额**（见 §2 与 03 篇权重公式）——规划的主角是工具调度与状态推理，多智能体协作只是其中一环。

## 2. 任务分布：Tool Use 独占六成

站点 Tasks per capability dimension（F-018）：

| 维度 | 任务数 | 占比（按 1,705 计） |
|---|---|---|
| Tool Use | 1,040 | 约 61% |
| Memory Usage | 376 | 约 22% |
| Skill Usage | 200 | 约 12% |
| Sub-agent Collaboration | 89 | 约 5% |
| **合计** | **1,705** | 100% |

四项合计恰为 1,705（F-018、F-004）。任务分布与 Overall 权重公式（Tool 50% / Memory 20% / Skills 20% / Sub-agent 10%，F-011/F-013）同向倾斜——只看 Overall 会抹平 Memory/Skills 维度的模型分化。

## 3. Benchmark Statistics 六项统计

站点 Benchmark Statistics 六个 pill（F-017）：

```text
1,705 Evaluation Tasks    212 Realistic Tools     13 Functional Domains
89 Subcategories          N=15 Candidate Recall   T=15 Max Steps
```

其中 **N=15 Candidate Recall / T=15 Max Steps** 是理解任务难度设置的关键参数：候选工具召回池为 15，最大步数为 15（F-017）。

## 4. 13 个工具域及工具数

站点域-工具数表（F-019），共 13 域 212 工具（F-004）：

| 工具域 | 工具数 | 工具域 | 工具数 |
|---|---|---|---|
| Audio & Entertainment | 25 | Network & Connectivity | 14 |
| Apps & Storage | 23 | Travel & Lifestyle | 13 |
| Display & Sound | 22 | Devices & Cross-device | 13 |
| System Settings | 22 | Input & Interaction | 12 |
| Time Management | 16 | Utilities & Productivity | 11 |
| AI Assistant | 16 | Security & Privacy | 10 |
| Calls & Communication | 15 | — | — |

工具数最多的域是 Audio & Entertainment（25），最少的是 Security & Privacy（10）（F-019）。

## 5. 案例组织方式

站点 Task Examples 按四维组织案例：四个 case tab 按钮携带 `data-anchor` 属性（basic→tool-use-examples、memory→memory-examples、skills→skill-examples、subagent→sub-agent-examples），各标 "3" 个案例计数（F-016）。数据文件 `case_studies_data.js` 中 `window.TASK_EXAMPLES_DATA.dimensions` 含 basic/memory/skills/subagent 四键，每键 cases 数组 3 条，每条含 id/title/query/checker/subtype/interactions/finalResponse 字段（F-020）。

## 6. 四维代表案例

### Tool Use（basic 维）

| 案例 id | 标题 | subtype | 要点 |
|---|---|---|---|
| BTU-204 | "Payment sequence under real state changes" | Ordered execution | interactions 依次调用 control_flashlight / open_app / manage_nfc（F-022） |
| BTU-622 | "Conflicting network goals" | Conflict intent | 模型判定"关流量"与"4K 流播"冲突后**反问用户**——识别冲突后停手才是最优行为（F-022） |
| BTU-863 | （Compound state change） | Compound state change | dark mode + repeat one + 30 分钟倒计时三连调用（F-022） |

### Memory 维

| 案例 id | subtype | 要点 |
|---|---|---|
| MEM-0043 | Memory update | 把睡前单词 App 从 Anki 改为 Quizlet（F-022） |
| MEM-0054 | Multi-memory composition | 多条记忆组合应用（F-022） |
| MEM-MT0421 | Multi-turn memory | Bluetooth 发送会议纪要到 MacBook Pro（F-022） |

### Skills 维

维度 summary："Loading reusable skills before executing a safe and complete business-tool plan."，三个案例 checker 均为 Skill routing + execution（F-032）。

### Sub-agent 维

维度 summary："Delegation to specialized agents, recovery from tool boundaries, and transparent fallbacks."；三个案例标题分别为 "Recover into a GUI handoff"、"Keep an automation when media is unavailable"、"Delegate open-domain lookup without fabrication"，checker 均为 Behavior judge（F-032）。GUI 能力在此仅以**子代理交接对象**出现——"Recover into a GUI handoff" 即工具边界处回退到 GUI 交接的案例。

各案例的 checker 类型谱系与判分机制在 [02-verification-policy.md](02-verification-policy.md) 展开。

## 相关概念

- [00-benchmark-overview.md](00-benchmark-overview.md)——基准定义与仓库性质
- [02-verification-policy.md](02-verification-policy.md)——六类 checker 与固定验证策略
- [03-leaderboard-analysis.md](03-leaderboard-analysis.md)——维度权重与榜单解读
- [../mai-ui/index.md](../../mai-ui/index.md)——同生态 Agent 基座模型（本基准的被测对象形态之一）

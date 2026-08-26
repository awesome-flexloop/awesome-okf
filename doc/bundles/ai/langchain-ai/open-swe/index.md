---
type: bundle
okf_version: "0.2"
scope: open-swe
name: open-swe
version: "0.1.0"
source: https://github.com/langchain-ai/open-swe
description: Open SWE——基于 LangGraph 与 Deep Agents 的开源多图编码 Agent 框架，五个图工厂（agent/reviewer/analyzer/chat/scheduler）、持久化分发契约、findings 评审模型与每线程隔离沙箱
---

# Open SWE

**Open SWE** 是一个开源的编码 Agent 框架，构建在 **LangGraph** 与 **Deep Agents**（`deepagents.create_deep_agent`）之上。它以 LangGraph 应用形式运行：每个线程拥有一个隔离的云沙箱，Agent 可从 Slack、Linear、GitHub（PR 评论、PR 打开/ready-for-review 自动评审）或 Dashboard 触发。系统还包含只读 PR 评审者、评审风格学习器、PR 对话助手和 cron 调度器共五个独立图。

- **包名**：`open-swe-agent` 0.1.0
- **Python**：`>=3.11`（运行时固定 3.12）
- **核心依赖**：`deepagents==0.7.6`、`langgraph>=1.2.10`、`langchain>=1.3.9`、`fastapi`、`uvicorn`
- **许可证**：MIT

## 核心特性

- **五个 LangGraph 图工厂**：主编码 Agent、只读 PR reviewer、评审风格 analyzer、无沙箱 PR chat、cron scheduler，每个工厂每次运行构造全新 `create_deep_agent` 实例，Agent 自身无状态。
- **Durable Dispatch 单一契约**：所有外部触发汇聚到 `dispatch_agent_run`，默认 `multitask_strategy="interrupt"`（跟进中断恢复）、`durability="sync"`（每步 checkpoint）、`stream_resumable=True`（事件流可重放）、completion webhook 终态信号。
- **Findings 评审模型**：reviewer 围绕一组持续演进的 finding 对象工作，diff-anchor 纪律强制只申报 PR diff 内的问题，`reconcile_findings_with_review_threads` 与 GitHub review thread 双向同步。
- **每线程隔离沙箱**：`ensure_sandbox_for_thread` 三态生命周期（命中/重连/新建），不可达时拒绝替换以保护未提交工作；支持 LangSmith/Modal/Daytona/Runloop/E2B/Local 多提供商。
- **洋葱圈中间件栈**：严格有序的 middleware 处理工具消毒、模型调用限额、消息队列注入、空消息补刀、沙箱熔断、模型降级、调用超时等横切关注点。
- **Baby-sit CI 监控**：opt-in 的 PR CI 持续监控，签名 webhook 即时评估 + 每 10 分钟 cron 兜底，新失败时恢复原 Agent 线程诊断，flaky 重跑有上限。

## 五个图

| 图 | 工厂 | 职责 |
|---|---|---|
| agent | `agent.server:get_agent` | 主编码 Agent，沙箱内读写/执行/提交/开 PR |
| reviewer | `agent.reviewer:get_reviewer_agent` | 只读 PR 评审，产出 findings |
| analyzer | `agent.analyzer:get_analyzer` | 学习每仓库评审风格（bootstrap/continual） |
| chat | `agent.chat:get_chat_agent` | 无沙箱"与 PR 对话"只读助手 |
| scheduler | `agent.scheduler:get_scheduler` | cron 扇出为调度运行/reconcile/baby-sit |

## 快速导航

### 核心概念

- [总览](/ai/langchain-ai/open-swe/concepts/overview) — Open SWE 是什么、五个图、核心运行机制
- [Agent 架构](/ai/langchain-ai/open-swe/concepts/agent-architecture) — 图工厂、无状态 Agent、模型优先级、middleware 洋葱圈
- [Dispatch-Review 循环](/ai/langchain-ai/open-swe/concepts/dispatch-review-cycle) — durable dispatch、findings 模型、GitHub thread 协调
- [Scheduler 与 Reconcile](/ai/langchain-ai/open-swe/concepts/scheduler-reconcile) — cron 扇出、陈旧运行清理、baby-sit 状态机

### 参考

- [架构参考](/ai/langchain-ai/open-swe/references/architecture) — 图入口、工厂签名、常量、工具集、Finding 模型、FastAPI 装配

### 示例

- [触发 Agent 运行与评审循环](/ai/langchain-ai/open-swe/examples/triggering-agent-run) — dispatch_agent_run、reviewer 评审、scheduler 任务、baby-sit、webhook 配置

### 溯源

- [事实清单](/ai/langchain-ai/open-swe/spec/facts) — 70 条带文件路径与行号的编号事实
- [架构洞察](/ai/langchain-ai/open-swe/spec/insights) — 4 个核心架构洞察

## 目录结构

```
open-swe/
├── index.md              # 本文件（含 okf_version: "0.2"）
├── log.md                # 变更日志
├── spec/
│   ├── facts.md          # 源码事实验证清单（70 条）
│   └── insights.md       # 设计决策与深度洞察（4 个）
├── concepts/             # 核心概念（4 篇）
│   ├── overview.md
│   ├── agent-architecture.md
│   ├── dispatch-review-cycle.md
│   └── scheduler-reconcile.md
├── references/           # 技术参考（1 篇）
│   └── architecture.md
└── examples/             # 使用示例（1 篇）
    └── triggering-agent-run.md
```

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```

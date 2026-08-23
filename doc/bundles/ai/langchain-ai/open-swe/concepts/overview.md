---
type: concept
scope: open-swe
name: overview
version: "0.1.0"
source: https://github.com/langchain-ai/open-swe
description: Open SWE 总览——基于 LangGraph 与 Deep Agents 的多图编码 Agent 框架，五个图工厂、持久化分发与沙箱生命周期
---

# Open SWE 总览

## 什么是 Open SWE

Open SWE 是一个开源的编码 Agent 框架，构建在 **LangGraph** 与 **Deep Agents**（`deepagents.create_deep_agent`）之上。它以 LangGraph 应用形式运行：每个线程（thread）拥有一个隔离的云沙箱，Agent 可从 Slack、Linear、GitHub（PR 评论、PR 打开/ready-for-review 时的自动评审）或 Dashboard 触发。

- **包名**：`open-swe-agent`，版本 `0.1.0`（F-001）
- **Python**：`>=3.11`（`langgraph.json` 运行时固定为 3.12，F-005）
- **核心依赖**：`deepagents==0.7.6`、`langgraph>=1.2.10`、`langchain>=1.3.9`、`fastapi`、`uvicorn`（F-002）
- **许可证**：MIT

## 五个图，而非一个 Agent

Open SWE 由 `langgraph.json` 注册的五个独立 LangGraph 图组成（F-005）：

| 图 | 职责 |
|---|---|
| **agent** | 主编码 Agent，能在沙箱中读写文件、执行命令、提交、开 PR、回复 Slack/Linear |
| **reviewer** | 只读 PR 评审者，产出 findings 并发布到 GitHub |
| **analyzer** | 从历史 PR 评审和 finding 结果中学习每个仓库的评审风格 |
| **chat** | 无沙箱的"与 PR 对话"只读助手，基于 diff 和已发布 findings 回答问题 |
| **scheduler** | 将确定性 cron 滴答扇出为调度运行、reconcile 清理、baby-sit CI 检查 |

每个图都是一个工厂函数（`get_agent` / `get_reviewer_agent` / `get_analyzer` / `get_chat_agent` / `get_scheduler`），在每次运行时构造一个全新的 `create_deep_agent(...)` 实例。Agent 自身无状态——所有 per-thread 状态寄居在沙箱和线程元数据中。详见 [Agent 架构](/ai/langchain-ai/open-swe/concepts/agent-architecture)。

## 核心运行机制

```
Slack/Linear/GitHub/Dashboard
        │  (webhook → 确定性 thread_id)
        ▼
┌──────────────────────┐
│  FastAPI (webapp)    │  webhook 验签、thread_id 推导、触发运行
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  dispatch.py         │  单一持久化分发契约
│  create_durable_run  │  interrupt + sync checkpoint + webhook
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  LangGraph runtime   │  按 thread_id 路由到对应图工厂
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  图工厂 get_*        │  解析 token/模型/沙箱，装配 tools+middleware
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  隔离沙箱 (per-thread)│  文件系统 + git worktree + gh proxy
└──────────────────────┘
```

### 持久化分发

所有外部触发都汇聚到 `dispatch_agent_run` → `create_durable_run`。它默认 `multitask_strategy="interrupt"`（跟进消息中断活跃运行并带完整历史恢复）、`durability="sync"`（每步前 checkpoint）、`stream_resumable=True`（事件流可重放），并通过 completion webhook 保证每次运行都有终态信号。详见 [Dispatch-Review 循环](/ai/langchain-ai/open-swe/concepts/dispatch-review-cycle)。

### Review-Reconcile 循环

Reviewer 围绕一个持续演进的 findings 列表工作：`add_finding` 记录、`update_finding` 更新、`publish_review` 发布、`resolve_finding_thread` 关闭。每次评审前，`reconcile_findings_with_review_threads` 把本地 findings 与 GitHub 上的实际 review thread 状态双向同步。另有一个独立的 `reconcile_stale_runs` 安全网清理卡在 pending 的运行。详见 [Dispatch-Review 循环](/ai/langchain-ai/open-swe/concepts/dispatch-review-cycle) 与 [Scheduler 与 Reconcile](/ai/langchain-ai/open-swe/concepts/scheduler-reconcile)。

### 沙箱生命周期

每个线程对应一个隔离沙箱（LangSmith/Modal/Daytona/Runloop/E2B/Local）。`ensure_sandbox_for_thread` 处理三种情况：内存命中则 ping 刷新、元数据有 id 则重连、都没有则新建。沙箱不可达时抛 `SandboxUnreachableError` 而非替换——替换会清空未提交工作。唯一例外是 reviewer，其沙箱只含可重新派生的 checkout，允许 `allow_replacement=True`。

## 技术栈角色

| 组件 | 在 Open SWE 中的角色 |
|---|---|
| LangGraph | 图编排、checkpoint、线程/运行模型、流式协议 |
| Deep Agents | `create_deep_agent` 提供文件系统工具、子 Agent、skills、backend 抽象 |
| FastAPI | Webhook 入口、Dashboard API、OAuth |
| langgraph_sdk | 服务端自调用，触发/流式传输运行 |
| 沙箱提供商 | 隔离执行环境（默认 LangSmith） |
| GitHub App / OAuth | 双模式认证，沙箱内通过 proxy 注入凭证 |

## 模块地图

```
agent/
├── server.py          # 主 Agent 图工厂、沙箱生命周期、模型解析
├── reviewer.py        # PR 评审图工厂、reviewer prompt
├── analyzer.py        # 评审风格学习图
├── chat.py            # 无沙箱 PR 对话图
├── scheduler.py       # cron 扇出图
├── dispatch.py        # 持久化运行分发契约
├── reconcile.py       # 陈旧运行清理
├── baby_sit.py        # PR CI 监控
├── prompt.py          # 系统提示构造
├── desktop.py         # 本地桌面后端
├── webapp.py          # FastAPI 兼容入口
├── api/app.py         # FastAPI 应用装配
├── graphs/            # langgraph.json 指向的薄转发层
├── runtime/           # 常量、执行判断、沙箱装配
├── middleware/        # 洋葱圈中间件
├── tools/             # 自定义工具
├── review/            # findings、diff、publish、reconcile
├── dashboard/         # Dashboard API、OAuth、管理
├── webhooks/          # GitHub/Linear/Slack webhook
├── integrations/      # 沙箱与 MCP 集成
└── skills/            # 内置 SKILL.md playbooks
```

完整的函数与常量清单见 [架构参考](/ai/langchain-ai/open-swe/references/architecture)。

## 进一步阅读

- [Agent 架构](/ai/langchain-ai/open-swe/concepts/agent-architecture) — 图工厂、模型优先级、middleware 洋葱圈
- [Dispatch-Review 循环](/ai/langchain-ai/open-swe/concepts/dispatch-review-cycle) — durable dispatch、findings 模型、GitHub thread 协调
- [Scheduler 与 Reconcile](/ai/langchain-ai/open-swe/concepts/scheduler-reconcile) — cron 扇出、陈旧运行清理、baby-sit

# Pi Agent Harness — 设计理念、竞品对比与 OpenClaw 关系

> **类型**：Concept | **F引用**：F-016~F-033 | **生成时间**：2026-09-09

---

## 为什么 Pi "快"

Agent 总速度由四部分组成（F-016）：

```
Agent总速度 = 模型生成速度 + 网络延迟 + 工具执行时间 + Agent外壳开销
                ↑              ↑              ↑              ↑
            不受Pi影响     不受Pi影响     不受Pi影响    Pi能明显影响
```

Pi 的核心策略是**做减法**（F-017~F-019）：

| Pi 的特点 | 具体表现 |
|---------|---------|
| 默认工具少 | 仅 read/write/edit/bash，不搞大而全 |
| 核心很薄 | 没有把 MCP/多Agent/计划模式/待办系统/复杂权限工作流全部塞进默认路径 |
| 增量渲染 | 终端界面采用增量渲染，流式输出和工具状态出现及时 |
| 边跑边输入 | 可在 Pi 运行时继续输入，普通回车排入"纠偏消息"，等当前一轮工具调用结束后送入 |

> **作者结论**（F-021）：Pi 不会让同一个大模型凭空提高推理速度，它只是因为非常轻所以快。Pi 的"快"，是因为轻，因为不做没有必要的事。

---

## 竞品横向对比

| 工具 | 定位 | 与 Pi 的差异 |
|------|------|------------|
| **Pi** | 给你一副骨架 | 不替用户规定工作流；默认无MCP/子Agent/计划模式/待办/权限确认；轻、透明、可改造；需自己负责组装 |
| **Claude Code** | Anthropic 编程工作台 | 完成度高的成品；权限控制/MCP/计划模式/自动化接口已形成工作方式；与 Claude 模型结合紧；适合"装好就用" |
| **Codex** | OpenAI 完整 Agent 环境 | 覆盖桌面端/IDE/云端任务/Skills/MCP/子Agent/沙箱/审批；强调完整工作流、安全边界、跨环境协作 |
| **OpenCode** | 多模型开源 Agent | 默认提供 Build/Plan/子Agent/细粒度权限/MCP 等完整能力；开源+开箱即用；Pi 更坚持"核心越小越好" |
| **LangGraph / Agents SDK** | 应用框架 | 关注工作流编排/状态/分支/追踪/生产系统集成；本身不是打开终端就能干活的编程 Agent |

> **作者归纳**（F-028）：Pi 夹在两者之间——比纯框架更接近产品，又比完整产品更像可以拆开的工程零件。

---

## Pi 与 OpenClaw 的关系

> ⚠️ **时效声明**：以下信息截至 2026 年 8 月 25 日，以 OpenClaw 官方最新架构为准。

### 历史依赖（截至 2026 年 4 月）

OpenClaw 早期深度使用过 Pi 的组件（F-029~F-030）：

| Pi 组件 | OpenClaw 中的体现 |
|--------|-----------------|
| `pi-agent-core` | 嵌入 Pi Agent Core |
| `pi-coding-agent` | 嵌入 Pi Coding Agent |
| `pi-ai` | 嵌入 Pi AI 包 |
| `pi-tui` | 嵌入 Pi TUI |
| — | 内部运行器长期叫 `pi-embedded-runner` |

### 当前架构（截至 2026 年 8 月 25 日）

OpenClaw 官方最新架构已明确（F-031~F-032）：

| 变更项 | 现状 |
|--------|------|
| Agent Runtime | 由 OpenClaw 自己维护，不再依赖外部 Agent Framework |
| `pi` runtime 名称 | 仅为兼容别名保留 |
| 第三方 Pi 依赖 | 当前保留的主要是 `pi-tui` |

> **作者归纳**（F-033）：Pi 曾经是 OpenClaw 非常重要的 Agent 底座，OpenClaw 后来把这套运行时逐步内化成了自己的架构。

---

## 跨束引用

| 方向 | 目标知识包 | 关系 |
|------|----------|------|
| ← | [pi-cli](../pi-cli/index.md) | pi-cli 知识包提供 Pi monorepo 源码级细节；本文提供高层定位与竞品视角 |
| → | [openai-codex](../openai-codex/index.md) | Codex 为 Pi 竞品之一，提供更完整的开箱即用 Agent 工作环境 |
| → | [opencode](../opencode/index.md) | OpenCode 为 Pi 竞品之一，开源多模型但功能更全 |

```{toctree}
:hidden:
:maxdepth: 2

```

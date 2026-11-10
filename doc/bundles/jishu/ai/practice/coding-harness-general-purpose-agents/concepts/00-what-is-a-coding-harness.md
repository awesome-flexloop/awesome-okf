---
okf_version: "0.2"
type: Concept
title: "什么是 Coding Harness：把编码 Agent 的运行时借给通用任务"
description: "从 agent loop、工具、上下文与会话四个职责定义 coding harness，并区分它与 agent framework、模型 API、终端产品的层次。"
tags: [coding-harness, agent-loop, agent-framework, runtime, definition]
generated: { by: "lobsterai/main", at: "2026-11-10T15:05:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T15:05:00+08:00" }
status: stable
stale_after: "2027-04-30"
sources:
  - id: radar
    resource: https://www.thoughtworks.com/radar/techniques/coding-harness-for-general-purpose-agents
  - id: claude-sdk
    resource: https://code.claude.com/docs/en/agent-sdk/overview
  - id: pi-readme
    resource: https://github.com/earendil-works/pi/blob/main/packages/coding-agent/README.md
---

# 什么是 Coding Harness：把编码 Agent 的运行时借给通用任务

> **一句话定义**：coding harness 是包在模型外面的一层运行时，负责跑 agent loop、调用工具、管理上下文与会话；所谓“通用任务的 coding harness”，就是把这层已经为编码场景打磨过的运行时，复用到文档处理、运营支持、迁移规划等非编码任务上（F-006）。

## 1. 问题从哪里来

非编码任务的团队过去通常走三条路。

1. 选一个 agent framework，自己写循环、工具调用、状态与重试。
2. 直接调模型 API，把编排逻辑写进业务代码。
3. 用某个终端产品，接受它固定的交互方式。

Thoughtworks 观察到的变化是：越来越多团队转向第四种做法——不再自己组装 agent loop，而是复用一个成熟编码 agent 的运行时（F-005、F-006）。原因不复杂：编码 agent 为了处理长任务、反复改文件、跑命令、恢复会话，已经把 agent loop 里最脏最累的部分做完了。

## 2. 四个层次不要混

| 层次 | 负责什么 | 例子 |
|---|---|---|
| 模型 | 生成 token、推理、调用工具 | Claude、GPT、开源模型 |
| Coding harness | agent loop、工具执行、上下文压缩、会话持久化、权限 | Claude Agent SDK、Codex SDK/app-server、OpenCode server/SDK、Pi SDK/RPC（F-007～F-010） |
| Agent framework | 让开发者自己搭 loop、状态机、编排与集成 | 各类 graph/workflow 框架 |
| 终端产品 | 面向人的界面与工作流 | CLI、IDE 插件、桌面应用 |

文章讨论的是第二层。它既不是模型，也不是“又一个框架”，而是“已经跑起来的运行时，开放了编程入口”。

## 3. Harness 的职责边界

一个 coding harness 通常接管以下五件事。

1. **Agent loop**：把用户目标拆成多轮“模型思考 → 工具调用 → 观察结果 → 继续”的循环（F-037）。
2. **工具执行**：读写文件、跑命令、搜索、调用 MCP 服务等；工具是内置的，不是让业务代码从零实现（F-038）。
3. **上下文管理**：在长任务中压缩历史、保留关键状态，避免上下文窗口被撑爆（F-011）。
4. **会话生命周期**：持久化、恢复、分叉会话，让任务可以跨进程、跨请求继续（F-012）。
5. **运行控制**：无头运行、权限审批、沙箱、日志与可观测性（F-013、F-017）。

这五件事合起来，才是“运行时”三个字的分量。只提供一个模型调用封装，不叫 harness。

## 4. 复用的到底是什么

文章列出的复用项可以整理成一张清单。

| 复用项 | 对通用任务的价值 | 事实 |
|---|---|---|
| 长任务上下文压缩 | 文档批处理、迁移规划往往跨很多轮，不会因上下文耗尽而中断 | F-011 |
| 会话持久化 | 任务可以暂停、恢复、审计，不必每次从零开始 | F-012 |
| 无头运行 | 能放进队列、CI、定时任务或后端服务 | F-013 |
| Agent skills | 把领域知识、操作手册、脚本打包成按需加载的技能 | F-013、F-036 |
| 子代理 | 把检索、审阅、批处理拆给独立上下文，降低主会话压力 | F-013 |
| 指令文件 | 复用 `CLAUDE.md`、`AGENTS.md` 一类的项目级约定 | F-013 |
| 工具生态 | MCP、插件、hook 等现成集成 | F-038 |

关键点不是“这些能力很新”，而是“这些能力已经在编码场景被大量使用和打磨过”。复用它们，等于跳过了自建 loop 的试错期（F-014）。

## 5. 与 Agent Framework 的取舍

| 维度 | Coding harness | Agent framework |
|---|---|---|
| 控制力 | 较低：loop、工具、提示有既定实现 | 较高：循环、状态、工具都可自定义 |
| 成熟度 | 较高：运行时已被大量编码任务测试（F-014） | 取决于框架与团队实现 |
| 上手速度 | 快：接 SDK 即可跑 | 慢：先搭骨架再填业务 |
| 领域适配 | 需要覆盖编码偏向的提示与工具（F-020、F-021） | 从零按领域设计 |
| 差异化 | 更多落在技能、工具、领域层 | 可以差异化到 loop 本身 |
| 运维 | 会话、压缩、无头运行自带 | 需要自己补 |

一句话：**用控制力换成熟度**（F-014）。这不是绝对优劣，而是项目阶段的取舍。

## 6. 什么时候值得选

适合选 coding harness 的信号。

1. 任务本身就是“多轮工具调用 + 读写文件/系统 + 长时运行”。
2. 团队不想维护 agent loop、上下文压缩和会话恢复。
3. 希望复用现成的 skills、子代理、MCP 与指令文件。
4. 能接受在既定运行时外面加一层领域适配，而不是重写内核。

更适合 agent framework 的信号。

1. 业务流程是强确定性的状态机，工具调用顺序必须严格可控。
2. 需要深度定制 loop、调度、记忆或多人协作协议。
3. 任务很短、成本极敏感，承受不了编码 agent 的内置提示开销（F-023、F-024）。
4. 组织要求所有运行时行为可审计、可替换，不能依赖单一厂商实现。

## 7. 三个常见误解

**误解一：coding harness 只能写代码。** 文章讨论的正是“general-purpose agents”——运行时来自编码场景，任务可以完全不是编码（F-005、F-006）。限制不在能力，而在默认提示与工具偏向（F-020）。

**误解二：用了 harness 就不用框架。** 两者可以叠加：harness 负责 loop 与运行时，框架负责业务流程、状态机与外部系统集成。

**误解三：harness 越全越好。** 功能越全，内置提示与工具越多，每轮 token 开销越大（F-024）。Pi 这类最小 harness 的吸引力正来自“只保留必要部分”（F-025）。

## 8. 小结

Coding harness 的本质是**运行时复用**：把编码 agent 已经解决的 agent loop、工具、上下文、会话与运行控制，借给通用任务。它用控制力换成熟度（F-014），适合“工具调用密集、长时运行、希望快速上线”的场景；不适合“流程必须完全确定、成本极敏感、需要重写内核”的场景。

下一篇拆开四个具体入口，看看 Claude Agent SDK、Codex SDK/app-server、OpenCode server/SDK、Pi SDK/RPC 各自长什么样。

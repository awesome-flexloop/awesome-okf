---
type: concept
title: "架构总览——一切皆插件与能力缝"
description: "DeepSeek Harness 0.2 的架构主干：插件树装配、profile 与组合包分层、核心包与 ctx 键、三个事件域、能力 seam 三角色，以及新增行为该挂在哪里。"
tags: [deepseek-harness, architecture, plugin, seam, event-domain]
generated: { by: "process:seven-concepts-cmd+source-code-to-okf-wiki", at: "2026-10-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-22T00:00:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: dsh-upstream
    resource: https://github.com/deepseek-ai/deepseek-harness
    title: DeepSeek Harness 官方仓库 docs/architecture.zh.md
---

# 架构总览：一切皆插件与能力缝

## 1. 一句话主张

> 运行中的 `dsh` 是一棵**插件树**；产品每一部分都是插件——模型适配器、工具注册表、会话日志，乃至 agent loop 本身——因此每个都可以从配置里替换。

没有需要打补丁的特权内核。扩展 dsh 的方式不是"改内核"，而是**把插件挂到其他插件旁边**；各项注册都是副作用，会在其插件卸载时撤销。

## 2. 装配：profile → 组合包 → patch

**组合包（bundle）** 是 Cordis 配置项及其挂载代码的分发格式，它插入的内容始终可被上层 patch 覆盖。**profile** 是存放在 Harness home 中的具名组装，列出自己叠放的组合包。

从**空条目列表**起，配置树依次叠加（后应用者胜）：

1. profile manifest 中 `dsh.profile.bundles` 列表里的各组合包 patch（按列表顺序）
2. profile 自身的 `$DSH_HOME/profiles/<name>/cordis.patch.yml`
3. home 级 `$DSH_HOME/cordis.patch.yml`（机器共享偏好，优先级高于 profile 层）
4. 每个 `--patch <path>` overlay（按 argv 顺序）

patch 按 `id` 定位某个条目并**替换其整个 `config`**（不做深度合并），或 `insert` 新条目。行序无语义——激活由服务可用性驱动。详见 [Profile 与组合包](03-profile-and-bundle.md)。

内置组合包：`dsh-base`（共享第一层：模型适配器、工具、持久化、沙箱与审批策略、设置、凭据、遥测）、`dsh-web-app`、`dsh-headless`、`dsh-sdk-app`、`dsh-sdk-minimal`（刻意不叠 base 的例外）、`dsh-acp-app`。

## 3. 核心包与 ctx 键

| 包 | 职责 | `ctx` 键 |
|---|---|---|
| `core/session` | 仅追加的 `SessionEvent` 日志与内存存储 | `ctx.sessions` |
| `core/system-prompt` | 提示词片段与工具 schema 的组装 | `ctx.systemPrompt` |
| `core/tools` | 作用域化的工具注册表与带把关的执行流水线 | `ctx.tools` |
| `core/agent` | `Agent` 接口、活跃 agent 注册表、`agent/*` 事件 | `ctx.agents` |
| `core/agent-loop` | 实现该接口的默认驱动器 | `ctx.agentLoop` |
| `core/scope` | 按 agent 划分作用域的注册原语 | 库，无 ctx 键 |
| `llm/llm` | 消息与流式词汇表，以及适配器 seam | `ctx.llm` |

## 4. 三个事件域

选对事件域，是大多数改动的第一个决定。

| 事件域 | 代表事件 | 语义 |
|---|---|---|
| **持久会话事件** | `turn/*`、`step/*`、`system/message`、`user/message`、`assistant/message`、`assistant/attempt`、`tool/*` | 追加进日志并通过 `session/event` 广播的持久事实——必须在重载后仍存在的事实用它 |
| **Agent 事件** | `agent/*`（inbox、步骤、状态、请求、验证、续跑） | 携带活跃 `Agent` 的实时事件——观察或拦截进行中的工作时用它 |
| **能力事件** | `fs/*`、`tools/*`、`telemetry/*` | 无需导入循环即可向某个 seam 附加策略与适配器 |

其中 `agent/pre-step`、`agent/request`、`llm/stream` 与三个 `tools/*` 事件是**瀑布（waterfall）事件**：监听器必须调用 `next()` 才能委托下去。`agent/turn-stopping` 是 serial 事件，没有 `next()`。

## 5. 轮次与步骤

> 一个**步骤**是一次模型请求加上它调用的工具；一个**轮次**包含零个或多个步骤：它在领取首条输入之前打开，在不再欠下任何工作时关闭。

```text
turn/start
  领取 next-step 输入 + 一条排队消息
  组装 prompt 段 + 工具 schema
  → agent/pre-step（可改写或拒绝）
  → step/start → agent/request → 提交系统提示词与已接纳用户消息
  → 冻结请求 → llm/stream → agent/assistant-stream(start/chunk*/end)
  → tool/call* → tools/pre-execute → tools/execute → tools/post-execute → tool/result*
  → step/end
  → agent/turn-stopping → turn/end
```

细节见 [Agent 循环](04-agent-loop.md)。

## 6. 能力 seam：可替换能力的三角色

一个 **seam** 是一项可替换能力，由三个角色构成：

- **Service Definition**：声明接口
- **Service Provider**：实现它
- **Consumer**：使用它（通常是面向模型的工具）

一个包可以同时承担多个角色，但单一角色本身不是 seam；**添加一项能力意味着把三者一并设计**。

seam 正是"替换一个提供方就能改变整个产品"的原因。文件系统与进程提供方共享同一个执行世界，因此把它们指向远程沙箱，也就把 Bash、PTY 和 LSP 一并搬了过去——不需要提供方专用 fork。子 agent 提供方同理：从新建子 agent，到把一个轮次委派给另一个产品。

## 7. 新行为的归属位置

| 目标 | 机制 |
|------|------|
| 添加模型提供方 | 在 `ctx.llm` 上注册其适配器 |
| 添加面向模型的能力 | 在 `ctx.tools` 上注册；其 schema 加入提示词组装 |
| 让某个会话拥有不同的能力集合 | 组装一个 agent preset；其中的服务行需要 `isolate` realm |

## 8. 贯穿全局的三条纪律

1. **模型可见即已记录**——每个模型请求都必须能从会话日志重建；新增模型可见输入需要新的会话事件。
2. **日志 ≠ transcript**——`approval/*`、`permission/preset`、`plan/mode`、`todo/write`、`job/*` 等是"仅记日志、不进模型上下文"的事件，靠运行时上下文快照把状态告诉模型。
3. **schema 稳定性**——几乎所有 seam 都刻意把"提供方选择"置于 `ctx.X` 之后，使模型可见 schema 在换后端时保持不变（`lsp`、`web`、`browser-use` 均明确写出此点）。

## 下一步

- [Cordis 插件模型](02-cordis-plugin-model.md)——四个抽象如何撑起上面的一切
- [能力 seam 与子系统地图](08-capability-seams.md)——seam 的具体清单

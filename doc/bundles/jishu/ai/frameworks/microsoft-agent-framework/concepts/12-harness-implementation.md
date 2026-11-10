---
okf_version: "0.2"
type: Concept
title: "Harness 源码：一个工厂函数如何装配十几项能力"
description: "create_harness_agent 的参数与默认值、AgentLoopMiddleware 的 10 次上限、后台代理 300 秒等待、压缩策略接线、Python Shell 预发布边界与 .NET HarnessAgentOptions 对照"
tags: [源码, Harness, create_harness_agent, 压缩, 循环, Shell]
generated: { by: "source-code-to-okf-wiki", at: "2026-11-10T16:31:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T16:31:00+08:00" }
status: stable
stale_after: 2027-05-31
sources:
  - id: source-map
    resource: /references/source-code-map.md
  - id: src-harness
    resource: https://github.com/microsoft/agent-framework/blob/098214127/python/packages/core/agent_framework/_harness/_agent.py
  - id: src-loop
    resource: https://github.com/microsoft/agent-framework/blob/098214127/python/packages/core/agent_framework/_harness/_loop.py
---

# Harness 源码：一个工厂函数如何装配十几项能力

文档说 Harness 是“组合而非新运行时”。源码给出了组合的具体形态：`create_harness_agent` 是一个很长的工厂函数，把十几个参数翻译成 `Agent` 的中间件、上下文提供程序与循环配置。

## 工厂函数在做什么

`_harness/_agent.py` 的 `create_harness_agent` 文档字符串列出它自动接线的能力（F-138）：

1. 函数调用（自动工具调用循环）。
2. 每次服务调用的历史持久化。
3. 压缩（运行前/后）。
4. `TodoProvider`。
5. `AgentModeProvider`。
6. `FileMemoryProvider`（默认开）。
7. `FileAccessProvider`（通过 `file_access_store` 选择加入）。
8. `SkillsProvider`。
9. `BackgroundAgentsProvider`。
10. 工具审批（“不再询问”规则 + 启发式自动审批）。
11. 循环（按 `should_continue` 谓词重复运行）。

这不是“一个开关打开所有”，而是**一组默认值 + 一组可关闭开关**。理解参数，比记住能力清单更有用。

## 参数地图

`create_harness_agent` 的参数可以分成六组（F-139）：

| 组 | 参数 | 说明 |
|----|------|------|
| 身份 | `id`、`name`、`description` | 代理标识 |
| 指令 | `harness_instructions`、`agent_instructions` | 两段指令分开 |
| 预算 | `max_context_window_tokens`、`max_output_tokens` | 压缩与输出预算 |
| 压缩 | `disable_compaction`、`before_compaction_strategy`、`after_compaction_strategy`、`tokenizer` | 策略可替换 |
| 能力开关 | `disable_todo`、`disable_mode`、`disable_file_memory`、`disable_web_search`、`disable_tool_auto_approval` | 默认开，可关 |
| 扩展 | `tools`、`skills_provider`、`skills_paths`、`background_agents`、`shell_executor`、`history_provider`、`context_providers`、`middleware` | 注入点 |
| 循环 | `loop_should_continue`、`loop_next_message`、`loop_max_iterations` | 有界循环 |

关键默认值：

1. `loop_max_iterations = DEFAULT_MAX_ITERATIONS = 10`（F-141）。
2. 后台代理等待 `300` 秒（F-142）。
3. `harness_instructions` 为 `None` 时使用 `DEFAULT_HARNESS_INSTRUCTIONS`（F-140）。

第 1 条值得单独说：Harness 的循环不是无限自主，默认最多 10 轮。要更长，显式调大，并想清楚退出条件。

## 两段指令，不是一个提示词

源码把指令拆成 `harness_instructions` 与 `agent_instructions`（F-140）。这对应文档的“Harness 指令在前，自定义指令在后”（F-042）。合并顺序在实现上不是字符串拼接的巧合，而是两个独立参数；你可以只覆盖其中一段。

实践建议：

1. 保留默认 `harness_instructions`，除非你要改工作方式（任务拆解、工具使用、推理模式）。
2. 业务约束写进 `agent_instructions`，不要塞进 Harness 段。
3. 想完全接管时传 `harness_instructions=""`，但要接受代理失去默认工作模式。

## 循环：AgentLoopMiddleware

`_harness/_loop.py` 定义 `AgentLoopMiddleware` 与一组循环谓词（F-143）：

1. `background_tasks_running(...)`：还有后台任务时继续。
2. `todos_remaining(...)`：还有待办时继续。
3. `JudgeVerdict`：模型裁判的结构化判定。
4. `DEFAULT_MAX_ITERATIONS = 10`（F-141）。

这解释了 Harness 的“自主”从哪来：不是模型自己决定再跑一轮，而是中间件在每轮结束后调用谓词，满足条件才继续。**可预测性来自谓词，不是来自提示词。**

## 压缩接线：策略 + Provider

Harness 的压缩不是硬编码，而是把 `CompactionProvider` 接到上下文管道（F-137）。源码提供九个策略（F-136），Harness 允许你在运行前后分别指定：

1. `before_compaction_strategy`：进入模型前压缩。
2. `after_compaction_strategy`：运行结束后压缩，减轻下一轮负担。
3. `disable_compaction=True`：完全关闭。

这也解释了文档与博文的口径差（F-037）：**“自动压缩”需要预算或策略；没有预算时，框架没有依据决定何时压。**

## 文件记忆与文件访问

`_harness/` 下有独立的 `_file_memory.py` 与 `_file_access.py`（F-144）。两者的默认值不同：

1. 文件记忆默认开（`disable_file_memory=False`）。
2. 文件访问通过 `file_access_store` 选择加入，且有 `file_access_session_scoped`、`file_access_disable_write_tools`、`file_access_disable_readonly_tool_approval`、`file_access_disable_write_tool_approval` 等细粒度开关（F-139）。

安全含义：默认写盘的是“记忆”，不是“任意文件访问”。评审时不要把两者混为一谈。

## Python 也能跑 Shell——但要走预发布包

这是源码与文档最明显的一处差异。文档写“Shell 执行仅 .NET”（F-040）；源码 `_harness/_agent.py` 从 `agent_framework_tools.shell` 导入 `ShellExecutor` 与 `ShellEnvironmentProviderOptions`，并在 `shell_executor` 非空时装配 `ShellEnvironmentProvider`（F-145）。

该包 `agent-framework-tools` 的版本是 `1.0.0b261106`（F-146），即预发布。正确表述是：

1. 截至该 commit，Python Harness **有** Shell 能力。
2. 它依赖预发布包，不在稳定安装面内。
3. 文档的“仅 .NET”描述对应更早的版本，属于文档滞后（F-163）。

## .NET 对照：HarnessAgentOptions

`dotnet/src/Microsoft.Agents.AI.Harness/` 含 `HarnessAgent.cs`、`HarnessAgentOptions.cs`、`ChatClientHarnessExtensions.cs`（F-159）。`HarnessAgentOptions` 公开（F-160）：

1. `MaxContextWindowTokens` / `MaxOutputTokens`。
2. `CompactionStrategy` / `DisableCompaction`。
3. `HarnessInstructions`。
4. `ChatHistoryProvider` / `AIContextProviders`。
5. `LoopEvaluators` / `LoopAgentOptions`。
6. `MaximumIterationsPerRequest`。
7. `DisableToolAutoApproval`。

两组 API 的参数名不同，但能力面一一对应。跨语言迁移时，按“预算/压缩/循环/审批/扩展”五组映射，比逐字翻译参数更可靠。

## 一个最小装配示例（源码形态）

```python
from agent_framework import create_harness_agent

agent = create_harness_agent(
    client=client,
    agent_instructions="Help users plan and complete multi-step tasks.",
    max_context_window_tokens=128_000,
    max_output_tokens=16_384,
    disable_file_memory=True,
    disable_web_search=True,
    loop_max_iterations=20,
)
```

这段代码的每个参数都能在 `create_harness_agent` 签名中找到（F-139）。`loop_max_iterations=20` 是对默认 10 的显式放宽。

## 已知边界

1. 本文只读 `_harness/` 的类与签名，未逐行分析每个 Provider 的实现。
2. Python Shell 依赖预发布 `agent-framework-tools`，API 可能变化。
3. 默认值以 1.25.0 源码为准；1.21 发布版可能不同。
4. 循环谓词的判定细节需读 `_loop.py` 全文。

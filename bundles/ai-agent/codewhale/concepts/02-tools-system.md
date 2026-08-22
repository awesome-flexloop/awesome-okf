---
type: concept
title: 工具系统（Tools System）
description: CodeWhale 用校验、资源调度、终态三层类型解耦工具调用，并以 ResourceClaim 冲突规则做并行安全分批
tags: [codewhale, tools, tool-registry, resource-claim]
sources:
  - resource: "/references/tools-mcp-api.md"
    title: "Tools 与 MCP API 参考"
generated: { by: "okf-wiki-bot", at: "2026-08-23T12:00:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-23T12:00:00+08:00" }
status: draft
stale_after: 2027-08-23
---

# 工具系统

`crates/tools` 是 CodeWhale 的 provider 中立工具执行层。它把一次工具调用拆成三个关注点分离的层级。

## 三层模型

1. **原始请求** `ToolCall`：未校验的调用，含 `name`、`payload`、`source`（`Direct`/`JsRepl`）、`raw_tool_call_id`（见 [F-055][F-056]）。
2. **准备态** `PreparedToolCall`：校验后的决策，含 `read_only`、`supports_parallel`、`approval`、`resources: Vec<ResourceClaim>`（见 [F-061]）。
3. **终态** `ToolExecutionOutcome`：机器可读结果，含 `status: ToolTerminalStatus` 与 `result`/`error` 二选一（见 [F-065]）。

## 注册表与分派

`ToolRegistry`（`#[derive(Default)]`，见 [F-058]）把「工具名 → 处理器」与「工具名 → 描述符」分开存储，`Arc<dyn ToolHandler>` 承载具体实现。`ToolHandler` trait 需要实现 `kind()`、可选覆盖 `is_mutating()`，以及核心的 `async fn handle(invocation)`（见 [F-057]）。

`dispatch` 的执行次序（见 [F-059]）：

```text
查找 handler → 校验 payload kind → MutatingToolRejected 守卫 → Runtime 加锁 → execute_with_timeout
```

分派契约用 `FunctionCallError` 表达：`ToolNotFound`、`KindMismatch`、`MutatingToolRejected`、`TimedOut`、`Cancelled`、`ExecutionFailed`。类型校验由 `required_str` / `optional_str` / `required_u64` / `optional_bool` 等提取器完成——错误的类型永远报错，只有 JSON `null` 被当作「缺省」（见 [F-053]）。

## 资源声明与并行调度

`ResourceClaim`（见 [F-062]）是执行前的保守资源声明，含 `ReadPath` / `WritePath` / `ReadTree` / `WriteTree` / `Terminal` / `GlobalExclusive` 七种。其 `conflicts_with` 规则的要点：

- `GlobalExclusive` 与任何 claim 冲突；
- 同名 `Terminal` 冲突；
- 写与「路径重叠」的读写冲突；
- 纯读之间不冲突。

`schedule_non_conflicting`（见 [F-063]）利用这些规则把一批工具调用按「无冲突共享一批、冲突保持原序」打包，供产品调度器安全并行执行。

## 终态语义

`ToolTerminalStatus` 区分六种终态：`Succeeded`、`Failed`、`Denied`、`InvalidArguments`、`Cancelled`、`TimedOut`（见 [F-064]）。它与用户可见的 `ToolResult::success` 刻意分离——被取消的调用仍需要一个合规的旧式结果来闭合转录，但运行时不能把它误报为普通失败。

## 相关概念

- [Agent 主循环](/concepts/01-agent-loop.md)
- [MCP 集成](/concepts/03-mcp-integration.md)
- [Tools 与 MCP API](/references/tools-mcp-api.md)
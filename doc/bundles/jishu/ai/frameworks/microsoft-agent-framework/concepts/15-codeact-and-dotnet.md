---
okf_version: "0.2"
type: Concept
title: "CodeAct 与 .NET 实现：Hyperlight 沙箱、LocalCodeAct 与项目对照"
description: "HyperlightCodeActProvider 的参数与沙箱边界、HyperlightExecuteCodeTool、wasm 后端与文件/域名限制、.NET 的 Hyperlight/LocalCodeAct/Workflows 项目布局"
tags: [源码, CodeAct, Hyperlight, 沙箱, .NET, LocalCodeAct]
generated: { by: "source-code-to-okf-wiki", at: "2026-11-10T16:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T16:40:00+08:00" }
status: stable
stale_after: 2027-05-31
sources:
  - id: source-map
    resource: /references/source-code-map.md
  - id: src-hyperlight
    resource: https://github.com/microsoft/agent-framework/blob/098214127/python/packages/hyperlight/agent_framework_hyperlight/_provider.py
  - id: src-dotnet
    resource: https://github.com/microsoft/agent-framework/tree/098214127/dotnet/src
---

# CodeAct 与 .NET 实现：Hyperlight 沙箱、LocalCodeAct 与项目对照

文档篇把 CodeAct 讲成“模型写一段程序，在沙箱里跑一次”。源码篇要回答：沙箱的边界由哪些参数控制，Python 与 .NET 各自提供了什么。

## Hyperlight 包的两个入口

`python/packages/hyperlight/agent_framework_hyperlight/` 定义（F-156）：

1. `HyperlightCodeActProvider(ContextProvider)`：推荐入口，自动注入 `execute_code` 工具与 CodeAct 指令。
2. `HyperlightExecuteCodeTool(FunctionTool)`：独立工具，适合“混用沙箱工具与直接工具”的场景。

这与 README 的说法一致：Provider 注册的工具在沙箱内通过 `call_tool(...)` 可用，但不作为直接代理工具暴露（F-107）。

## Provider 的参数就是沙箱策略

`HyperlightCodeActProvider` 的构造参数（F-157）可以分成四组：

| 组 | 参数 | 含义 |
|----|------|------|
| 工具 | `tools` | 沙箱内可调用的工具 |
| 审批 | `approval_mode` | 是否要求批准 |
| 文件 | `workspace_root`、`file_mounts`、`max_output_files`、`max_output_file_bytes`、`max_output_total_bytes` | 工作目录、挂载、输出限制 |
| 网络 | `allowed_domains` | 允许访问的域名 |
| 运行时 | `backend="wasm"`、`module`、`module_path` | 沙箱后端与 guest 模块 |

这张表比文档更可操作：文档说“全新 micro-VM”，源码说“默认 wasm 后端 + 可选模块路径 + 域名/文件限制”。**安全评审应逐项确认这些限制，而不是只看“有沙箱”。**

三个容易忽略的默认值：

1. `include_detailed_errors=False`：默认不把宿主异常与沙箱诊断暴露给生成代码；开启后可能泄露敏感数据（README 警告）。
2. 输出文件有数量与字节上限；超出会失败，不会静默截断。
3. `backend` 默认 `"wasm"`，不是“随便一个容器”。

## 沙箱内部：注册表与工作线程

`_execute_code_tool.py` 定义了一组内部类（F-156 的文件清单）：

1. `SandboxRuntime`（Protocol）：沙箱运行时接口。
2. `_SandboxRegistry`：沙箱注册表。
3. `_SandboxWorker` / `_SandboxEntry`：工作线程与条目。
4. `_ValidatedOutputFile` / `_NormalizedFileMount`：输出与挂载的校验结构。
5. `_RunConfig`：单次运行配置。

这说明“每次调用一个全新沙箱”不是一句口号：注册表管理沙箱生命周期，运行配置把文件挂载、域名、输出限制带进沙箱。

## 测试里的 fake sandbox

`tests/hyperlight/test_hyperlight_codeact.py` 定义了 `_FakeSandbox`、`_FakeRuntime`、`_FakeSandboxWithoutOutputListing` 等测试替身（F-158）。这给了一个可复用的测试思路：不需要真沙箱，也能验证“输出文件列出/未列出”“清理失败”等边界。

## .NET 侧：两种 CodeAct 后端

`dotnet/src` 同时有（F-162）：

1. `Microsoft.Agents.AI.Hyperlight`：Hyperlight 后端。
2. `Microsoft.Agents.AI.LocalCodeAct`：本地 CodeAct 后端。

这与文档的“Hyperlight 与本地 CodeAct 提供程序”对应（F-065）。两者的共同边界是：生成代码内的宿主工具调用绕过函数中间件，FIDES 不覆盖（F-065）。

## .NET 工作流项目：文件级结构

`Microsoft.Agents.AI.Workflows/` 含（F-161）：

| 文件 | 作用 |
|------|------|
| `Executor.cs` | 执行器基类 |
| `Edge.cs` / `FanOutEdgeData.cs` / `FanInEdgeData.cs` | 边与扇出/扇入 |
| `CheckpointManager.cs` / `CheckpointInfo.cs` | 检查点管理 |
| `AgentWorkflowBuilder.cs` | 代理工作流构建器 |
| `ConcurrentWorkflowBuilder.cs` | 并发编排构建器 |

这与 Python 的 builder/runner 是两套实现，但概念对齐：执行器、边、检查点、编排构建器。跨语言迁移时按概念映射，不要按方法名映射。

## 项目清单告诉你的架构选择

`dotnet/src` 的 38 个项目（F-126）体现了 .NET 侧的架构选择：**每个能力一个包**。这对部署有实际影响：

1. 只用代理 → 装 `Microsoft.Agents.AI` + provider。
2. 用 Harness → 加 `Microsoft.Agents.AI.Harness`。
3. 用工作流 → 加 `Microsoft.Agents.AI.Workflows`。
4. 用 CodeAct → 加 `.Hyperlight` 或 `.LocalCodeAct`。
5. 用 Shell → 加 `.Tools.Shell`。

Python 侧则是“元包 + 可选依赖”的模式（F-006）。两种分发策略没有优劣，只影响依赖体积与升级节奏。

## Go 仍然是独立仓库

`go/` 只有 README，指向 `microsoft/agent-framework-go`（F-127）。所以“三语言一致”是概念一致，不是同一仓库、同一发布节奏。

## 一张对照表

| 能力 | Python | .NET |
|------|--------|------|
| CodeAct（Hyperlight） | `agent-framework-hyperlight` | `Microsoft.Agents.AI.Hyperlight` |
| CodeAct（本地） | `monty` 包 | `Microsoft.Agents.AI.LocalCodeAct` |
| Shell | `agent-framework-tools`（预发布） | `Microsoft.Agents.AI.Tools.Shell` |
| 工作流 | `agent_framework._workflows` | `Microsoft.Agents.AI.Workflows` |
| Harness | `agent_framework._harness` | `Microsoft.Agents.AI.Harness` |
| Go | 独立仓库 | — |

（F-146、F-156、F-162、F-127）

## 已知边界

1. 未运行 Hyperlight 沙箱；平台支持与后端行为以包 README 为准。
2. .NET 项目只做目录与文件名级核验，未读 C# 实现细节。
3. `LocalCodeAct` 的隔离强度未在本文比较；不要假设它与 Hyperlight 等价。
4. CodeAct 与 FIDES 的缺口是当前实现边界，不是永久结论。

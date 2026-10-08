---
type: Concept
title: 运行模式与嵌入式集成
description: DeepSeek Harness 的用户侧使用指南：四种运行模式（Standard/Code/Minimal/Creator）能力对比与选型、Headless 无头模式与 CI 自动化、Python SDK（自带 Node 运行时）、JSON-RPC 跨语言集成、ACP 服务端用途、嵌入应用的典型场景与配置共享机制。
tags: [deepseek-harness, modes, headless, sdk, embedding, json-rpc, acp]
generated: { by: agent:learning-bundles-merge, at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: 2027-09-02
sources:
  - id: learning-harness-wiki
    resource: SpecWeave docs/knowledge/learning/03-agent-platforms-tools/deepseek-harness-wiki/（04-four-modes.md、12-headless-sdk.md）
    title: DeepSeek Harness 完全指南（learning 侧合并来源，基于 v0.1.0-rc.6 实测）
---

# 运行模式与嵌入式集成

本篇覆盖 DeepSeek Harness（dsh）的用户侧使用实践。架构层面的机制详见：Agent 主循环见 [agent-runtime-loop](agent-runtime-loop.md)，Code Mode 与工具系统见 [tool-and-subagent](tool-and-subagent.md)，Cordis 插件体系见 [cordis-plugin-architecture](cordis-plugin-architecture.md)，ACP 协议细节见 [acp-agent-protocol](acp-agent-protocol.md)。

> **版本提示**：本篇基于 v0.1.0-rc.6 开发者预览版实测整理。官方明确声明核心插件与基础接口会快速迭代，可能存在破坏兼容的变更，不建议直接用于生产环境。

## 四种运行模式

dsh 提供四种预设运行模式，每种模式对应不同的插件树与工具集。每种模式本质上是不同的 Profile 配置（对应不同的 Bundle 组合与补丁叠加），切换模式不需要修改代码，仅需切换配置。

| 模式 | 核心能力 | 适用场景 | 启动方式 |
|------|----------|----------|----------|
| **Standard（标准模式）** | 完整编程 Agent 能力：文件编辑、Shell 执行、文件与网页搜索、Skills、计划管理、目标追踪、子 Agent 委派、工作流编排 | 日常写代码、通用编程任务、默认使用场景 | Web UI 默认模式，或 `--profile web` |
| **Code（代码模式 / PTC）** | Standard 全部能力 + 程序化工具调用（Programmatic Tool Calling），模型通过 TypeScript 编排多步操作 | 多步操作密集场景，希望减少轮次往返、提升执行效率 | Web UI 模式切换，或启动时指定 |
| **Minimal（极简模式）** | 仅保留两个工具：持久化 `bash` 和 `str_replace_editor` | 模型基准评测、需要极简可控环境的研究场景 | `--profile minimal` |
| **Creator（创造模式）** | Standard 全部能力 + 运行时自省、内存中试验插件、Preset 编写指导（源码层称 Cordis 模式） | 定制 Agent 形态、开发插件、自定义 Profile | Web UI 模式切换，或 `--profile creator` |

### Code 模式（PTC）核心机制

传统 ReAct 模式下，Agent 每调用一次工具就需要一次完整的模型请求往返，一个包含 5 次工具调用的序列需要 5 轮模型请求。Code 模式下，模型不再逐个输出工具调用，而是**编写一段 TypeScript 代码，将多个工具调用编排进一次程序中**——可以顺序调用多个工具、用变量传递中间结果、进行条件判断与循环、处理错误与异常。原本需要 5 轮往返的操作序列，只需 1 次模型请求生成代码，随后一次性执行完成。

适用场景：批量文件处理、多步骤数据处理流水线、重复执行相似操作、需要复杂控制流（条件、循环）的任务、对延迟敏感的场景。

### Minimal 模式为何存在

在模型评测（Benchmark）场景下，过多的工具和复杂的循环逻辑会引入额外变量（不同模型在不同工具集下表现不可比、复杂插件逻辑干扰能力测量、难以复现）。Minimal 模式提供**最小且标准化**的工具面：工具数量固定且简单便于控制变量、环境干净易于复现、与主流基准评测框架（如 SWE-bench）的工具设置对齐。

```bash
npx @deepseek-ai/dsh --profile minimal "你的评测任务"
```

### Creator 模式典型流程

1. 启动 Creator/Cordis 模式：`npx @deepseek-ai/dsh web --profile creator`
2. 在对话中描述想要的 Agent 形态（如「我想要一个专门做代码审查的 Agent，不需要文件写入权限，但要能调用静态分析工具」）
3. 模型帮助生成对应的 Profile 配置和补丁
4. 在内存中试验加载这些配置，实时调整
5. 满意后将配置保存到 `~/.dsh/profiles/` 下，成为一个新的可用模式

### 模式选型速查

| 你的需求 | 选择模式 |
|----------|----------|
| 日常写代码、完成通用编程任务 | Standard（默认） |
| 大量批量操作、重复步骤，觉得轮次太慢 | Code |
| 做模型评测、需要干净可控的基准环境 | Minimal |
| 想开发插件、定制自己的 Agent 形态 | Creator |

四种内置模式本质上就是四个预置的 Profile 名称，可以创建自定义 Profile 实现第五种、第六种模式。

## Headless 无头模式

Headless 模式是最简单的非交互式运行方式：命令行传入任务描述，dsh 一次性执行任务，把结果打印到 stdout 后退出，不启动 Web 服务器。dsh 的设计从一开始就考虑了嵌入场景——无头模式不是事后补丁，而是一等公民；Web UI 本身就是建立在无头运行时之上的前端壳。

```bash
# 基本用法
npx @deepseek-ai/dsh --profile headless "你的任务描述"

# 指定工作目录与模型
npx @deepseek-ai/dsh --profile headless --workspace /path/to/project --model deepseek-v4-pro "重构任务"

# 从文件读取任务
cat task.txt | npx @deepseek-ai/dsh --profile headless

# 非交互模式（自动批准所有工具调用，仅在完全信任的环境使用）
npx @deepseek-ai/dsh --profile headless --yes "自动修复所有 ESLint 错误"

# JSON 格式输出，方便程序解析
npx @deepseek-ai/dsh --profile headless --output json "列出当前目录所有文件"
```

| 特点 | 说明 |
|------|------|
| **一次性执行** | 任务完成后进程直接退出，不驻留后台 |
| **无 Web UI** | 不启动 HTTP 服务器，不占用端口 |
| **结果打印到 stdout** | 最终输出直接打印到标准输出，方便脚本捕获 |
| **日志到 stderr** | 执行过程、工具调用日志输出到 stderr，不污染 stdout |
| **退出码语义** | 0 = 任务成功，非 0 = 执行出错 |
| **共享配置** | 与 Web 模式完全共享 `~/.dsh/` 配置 |
| **会话留存** | 会话同样保存到 `~/.dsh/sessions/`，事后可在 Web UI 查看 Trajectory、回放、分叉 |

### CI 自动化示例

```bash
#!/bin/bash
set -e
npx eslint src/ --format json > eslint-errors.json || true
if [ -s eslint-errors.json ]; then
    npx @deepseek-ai/dsh --profile headless --yes \
      "当前目录有 eslint-errors.json 包含 ESLint 错误。请逐个修复这些错误，修改对应的源文件，确保修复后代码逻辑不变。修复完成后再次运行 eslint 验证。"
fi
```

## Python SDK：自带 Node 运行时

官方 Python SDK 是最推荐的嵌入方式，最大特点是**自带打包好的 Node.js 运行时**——目标机器不需要预先安装 Node.js 或 npx，SDK 自动管理 dsh 版本和 Node 版本保证兼容性。

```bash
pip install deepseek-harness-sdk
```

核心概念只有三个：**DshRuntime**（运行时实例，管理 dsh 进程生命周期）、**DshSession**（一次会话，对应一个任务执行）、**DshEvent**（执行过程事件流）。

```python
from deepseek_harness_sdk import DshRuntime

runtime = DshRuntime()  # 自动下载/启动内置的 dsh
result = runtime.run(
    task="帮我写一个计算斐波那契数列的 Python 函数，带缓存优化",
    workspace="./my-project",   # 可选
    model="deepseek-v4-pro",    # 可选
)
if result.success:
    print(result.output)
```

流式获取执行过程用 `runtime.run_stream(task=...)`，迭代事件流并按 `event.type`（`assistant_message`/`tool_call`/`tool_result`/`complete`/`error`）分派处理。

Python SDK 默认使用与 CLI 相同的 `~/.dsh/` 配置目录；多租户等需要隔离配置的场景可通过 `DshRuntime(config_dir=...)` 指定独立目录。

## JSON-RPC SDK：跨语言进程间通信

非 Python 语言（Go、Java、Rust、C#）或需要独立常驻进程的场景，使用 JSON-RPC SDK。dsh 作为 JSON-RPC 服务器启动，通过 stdio 或 TCP 暴露服务：

```bash
npx @deepseek-ai/dsh --rpc                  # stdio（适合子进程通信）
npx @deepseek-ai/dsh --rpc --rpc-port 9000  # TCP（适合跨进程/跨机器）
```

核心方法：`dsh.startSession`（启动会话）、`dsh.sendEvent`（向会话发送事件）、`dsh.getSession`（获取会话状态）、`dsh.cancelSession`（取消会话）、`dsh.listSessions`（列出历史会话）、`dsh.subscribe`（订阅事件流）。

### Python SDK vs JSON-RPC 选型

| 维度 | Python SDK | JSON-RPC |
|------|-----------|----------|
| **语言限制** | 只能 Python | 任何语言 |
| **部署模式** | 嵌入到进程内 | 独立常驻进程 |
| **自带 Node** | 是 | 需要系统装 Node |
| **性能开销** | 低（直接管理子进程） | 略高（序列化/网络开销） |
| **多会话共享** | 每次 run 启动新进程 | 一个进程可同时跑多个会话 |
| **适合场景** | 简单嵌入、脚本、单会话 | 服务端、多租户、多语言环境 |

## ACP 服务端：Agent 间通信

dsh 还支持 ACP（Agent Communication Protocol）。如果说 MCP 是 Agent 调用工具的标准协议（见 [mcp-protocol-integration](mcp-protocol-integration.md)），ACP 就是 Agent 和 Agent 之间通信的标准协议。`npx @deepseek-ai/dsh --acp` 启动后，dsh 在本地启动 ACP 服务并通过 mDNS 在局域网广播自己的存在，其他支持 ACP 的 Agent 可自动发现并连接。协议机制详见 [acp-agent-protocol](acp-agent-protocol.md)。

用途展望：①多 Agent 协同（一台机器上多个不同 Agent 通过 ACP 互相通信协作）；②团队共享 Agent（服务器上跑一个配置完整的 dsh 实例，团队成员通过 ACP 连接使用）；③异构 Agent 编排（用编排框架作主控，把具体任务通过 ACP 委托给 dsh）。

## 嵌入应用的典型场景

| 场景 | 要点 |
|------|------|
| **内部 Agent 平台** | 前端做企业自己的 UI（SSO、审批流），后端用 Python SDK/JSON-RPC 调用 dsh 作为执行引擎，专注业务逻辑与企业定制 |
| **IDE 插件** | 前端是 IDE 原生界面，后端本地启动 dsh 运行时通过 JSON-RPC 通信，复用多模型、MCP、插件、Trajectory 调试全部能力 |
| **自动化工作流节点** | 代码提交后自动代码审查评论到 PR；数据管道出错时自动拉日志分析修复；发布前自动生成 release notes |
| **模型评测与基准测试** | Minimal 模式 + Headless 模式组合：干净可控的工具面 + 批量跑评测用例 + 完整 SessionLog 便于事后分析横向对比 |
| **自定义 CLI 工具** | 基于 dsh 封装领域特定 CLI，底层调用 `--profile headless --load-plugin` 执行，用户无感知 |

## 配置共享机制

所有运行方式（Web UI、Headless、Python SDK、JSON-RPC、ACP）完全共享同一个配置目录 `~/.dsh/`：API Key、模型配置与自定义模型、Profile 配置、MCP 服务器配置、插件安装与配置、AGENTS.md 规则（按工作目录读取）、历史会话记录均共享。

这带来的体验：先在 Web UI 调通任务（工具、模型、权限配置好），再把同样任务放到 Headless 或 Python SDK 里跑，行为完全一致；自动化任务出问题时可打开 Web UI 在历史会话里查看无头模式那次的完整轨迹；一次配置处处生效。需要隔离配置（测试/生产分开）时，所有 SDK 和 CLI 支持 `--config-dir` 参数或环境变量 `DSH_CONFIG_DIR` 指定独立配置目录。

## 相关概念

- [Agent 运行时主循环](agent-runtime-loop.md)
- [工具系统与子 Agent](tool-and-subagent.md)
- [Cordis 插件核心架构](cordis-plugin-architecture.md)
- [ACP Agent 通信协议](acp-agent-protocol.md)
- [Web 客户端架构](web-client.md)

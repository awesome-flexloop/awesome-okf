---
type: Example
title: "基本使用示例"
description: "从安装、配置 Provider 到基本对话和模式切换的完整入门指南，涵盖 codewhale doctor、config.toml 配置和 TUI 三种模式。"
tags: [codewhale, example, installation, configuration, basic-usage, tui, modes]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# 基本使用示例

本示例演示 CodeWhale 的安装、Provider 配置、基本对话和模式切换的完整流程。

## 1. 安装

### 通过 npm 安装

```bash
npm install -g codewhale
```

### 通过 crates.io 安装

```bash
cargo install codewhale-cli
```

### 验证安装

安装完成后，运行 `codewhale doctor` 进行离线健康检查：

```bash
codewhale doctor
```

添加 `--json` 标志可输出机器可读报告：

```bash
codewhale doctor --json
```

`doctor` 命令会检查配置文件、Provider 凭证、工具可用性和运行时环境。

## 2. 配置 Provider

CodeWhale 的配置文件存储在 `~/.codewhale/config.toml`。旧版 `~/.deepseek/config.toml` 仍受支持（项目起源于 `deepseek-tui`）。

### 基本配置

编辑 `~/.codewhale/config.toml`：

```toml
api_provider = "deepseek"
model = "deepseek-v4-flash"

[deepseek]
api_key = "sk-your-api-key-here"
```

默认 Provider 是 DeepSeek，默认模型为 `deepseek-v4-flash`。该模型在 `ModelRegistry` 中注册了多个别名：

```rust
ModelInfo {
    id: "deepseek-v4-flash".to_string(),
    provider: ProviderKind::Deepseek,
    aliases: vec![
        "deepseek-chat".to_string(),
        "deepseek-reasoner".to_string(),
        "deepseek-r1".to_string(),
        "deepseek-v3".to_string(),
        "deepseek-v3.2".to_string(),
    ],
    supports_tools: true,
    supports_reasoning: true,
}
```

### 配置其他 Provider

CodeWhale 支持 42 个 ProviderKind，包括 OpenAI、Anthropic、Google、Ollama、OpenRouter、Moonshot、ZAI、XAI 等。

```toml
[openai]
api_key = "sk-your-openai-key"

[anthropic]
api_key = "sk-ant-your-key"

[ollama]
base_url = "http://localhost:11434"
```

### 模型选择

在 TUI 中可以通过 `/model` 命令切换模型，或在配置中指定：

```toml
model = "deepseek-v4-pro"
```

`ModelFamily` 枚举支持 11 个家族：DeepSeek、Anthropic、OpenAI、Google、Meta、Mistral、Qwen、Grok、Cohere、GptOss、Inferencer。

## 3. 启动 TUI 并开始对话

在项目目录中启动 TUI：

```bash
cd your-project
codewhale
```

CLI 二进制名称为 `codewhale`，入口点为 `crates/cli/src/main.rs`。启动后直接输入消息即可开始对话：

```
> 解释一下这个项目的架构
```

CodeWhale 会分析项目上下文并回复。会话通过 `Thread` 持久化，`Thread` 拥有 append-only 的 `Journal` 和 `leaf_id` 游标：

```rust
pub struct Thread {
    pub thread_id: ThreadId,
    pub leaf_id: Option<String>,
    pub journal: Journal,
    pub model: String,
    pub reasoning_effort: Option<String>,
    pub workspace: PathBuf,
    pub ephemeral: bool,
}
```

这意味着你可以随时关闭 TUI，下次启动时恢复之前的会话。

### Headless 执行

除了 TUI，还可以使用 headless 模式直接执行单条命令：

```bash
codewhale exec "列出当前目录的文件"
```

headless 模式和 TUI 共享同一个 `EngineHandle`（Op-in / EventMsg-out channel API），但不触发 Hooks。

## 4. 模式切换

TUI 提供三种运行模式，通过 **Tab** 键循环切换：

### Plan（计划模式）

只读模式，拒绝文件修改和 shell 执行。适用于代码审查、架构讨论和规划方案。模型可以读取文件和搜索代码，但不能写入或执行命令。

### Work（工作模式）

普通多步执行模式。适用于日常编码任务、Bug 修复和功能实现。模型可以读取/写入文件、执行 shell 命令，但受执行策略和审批控制。

### Operate（操作模式）

多任务调度姿态。适用于复杂的多步骤任务、后台 Job 管理和 Fleet 多 Agent 编排。

### 权限姿态切换

通过 **Shift+Tab** 循环权限姿态：

1. **Ask** — 需要审批时询问用户
2. **Auto-Review** — 自动审查后执行
3. **Full Access** — 完全访问（谨慎使用）

### 推理力度切换

通过 **Ctrl+T** 循环推理力度，控制模型的推理深度。

## 5. 工具调用

CodeWhale 在 Work/Operate 模式下可以调用工具。工具通过 `ToolRegistry` 注册和调度：

```rust
pub struct ToolRegistry {
    handlers: HashMap<String, Arc<dyn ToolHandler>>,
    specs: HashMap<String, ConfiguredToolDescriptor>,
    runtime: ToolCallRuntime,
}
```

当模型决定调用工具时，`dispatch` 方法执行验证和执行流程：

```rust
pub async fn dispatch(
    &self,
    call: ToolCall,
    allow_mutating: bool,
) -> std::result::Result<ToolOutput, FunctionCallError>
```

调度流程包括按名称查找处理器、验证 payload kind、检查 mutating 权限、获取执行锁（并行工具读锁，串行工具写锁），然后执行并返回结果。

## 6. MCP 服务器配置

CodeWhale 可以连接外部 MCP 服务器。在 `~/.codewhale/mcp.json` 中配置：

```json
{
  "servers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"],
      "enabled": true,
      "filter": {
        "allow": [],
        "deny": ["write_file"]
      }
    }
  }
}
```

MCP 工具通过限定名 `mcp__<server>__<tool>` 寻址。例如 `mcp__filesystem__read_file`。

也可以让 CodeWhale 自身作为 MCP 服务器运行：

```bash
codewhale mcp-server
```

## 7. 常用命令

| 命令 | 说明 |
|------|------|
| `codewhale` | 启动 TUI |
| `codewhale exec "<prompt>"` | Headless 执行单条提示 |
| `codewhale doctor` | 离线健康检查 |
| `codewhale mcp-server` | 启动 MCP stdio 服务器 |
| `codewhale web` | 在 127.0.0.1:7878 启动本地浏览器客户端 |
| `codewhale fleet run` | 启动 Fleet 多 Agent 运行 |

`codewhale web` 使用一次性 bootstrap URL 和 HttpOnly SameSite=Strict cookie 认证。

## 8. 会话管理

会话状态通过 SQLite 数据库和 append-only JSONL 索引持久化。`StateStore` 管理五类数据：threads（会话线程）、messages（树形分支消息）、checkpoints（检查点）、jobs（后台任务）和 dynamic tools（动态工具）。

在 TUI 中可以使用 `/threads` 查看和切换会话，使用 `/fork` 从当前会话分叉创建新线程。`InitialHistory` 支持三种初始化方式：

```rust
pub enum InitialHistory {
    New,
    Forked(Vec<Value>),
    Resumed {
        conversation_id: String,
        history: Vec<Value>,
        rollout_path: PathBuf,
    },
}
```

## 相关概念

- [CodeWhale 简介](../concepts/00-introduction.md) — 项目概述与功能特性
- [Agent 核心运行时](../concepts/02-agent-core.md) — Thread/Session 和 Engine 架构
- [工具系统](../concepts/04-tool-system.md) — ToolRegistry 和工具调度
- [MCP 协议集成](../concepts/03-mcp-protocol.md) — MCP 服务器配置和工具代理
- [沙箱与执行策略](../concepts/07-sandbox-execpolicy.md) — 权限模式和安全控制
- [Fleet 工作流示例](02-fleet-workflow.md) — 多 Agent 编排和 Workflow

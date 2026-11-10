---
okf_version: "0.2"
type: concept
title: 安装、最小 Agent 与七项配置
description: TypeScript/Python 安装、API key、query() 最小 agent、7 项配置、工具三档与版本/打包边界
tags: [claude-agent-sdk, installation, quickstart, query, configuration, python, typescript]
generated:
  by: process:blog-article-to-okf-wiki R→I→E→V
  at: "2026-11-10T15:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-11-10T15:00:00+08:00"
status: stable
stale_after: 2027-01-31
sources:
  - id: blog
    url: https://stackademic.com/blog/building-production-ai-agents-with-anthropic-s-claude-agent-sdk
  - id: agent-sdk-quickstart
    url: https://code.claude.com/docs/en/agent-sdk/quickstart
  - id: agent-sdk-overview
    url: https://code.claude.com/docs/en/agent-sdk/overview
  - id: pypi-claude-agent-sdk
    url: https://pypi.org/project/claude-agent-sdk/
  - id: npm-claude-agent-sdk
    url: https://www.npmjs.com/package/@anthropic-ai/claude-agent-sdk
---

# 安装、最小 Agent 与七项配置

> **代码说明**：以下片段来自博文与官方 quickstart，**本库环境未执行**。它们用于说明 API 形状与配置语义，不构成“实测通过”的证明。

## 1. 前置条件

| 项 | 要求 | 依据 |
|---|---|---|
| Node.js | 18.14+（TypeScript SDK） | F-025、F-027 |
| Python | 3.10+（Python SDK） | F-021、F-025 |
| 账号 | Anthropic 账号与 API key | F-024、F-025 |
| 运行位置 | agent 进程能访问它要操作的项目目录 | F-039 |

## 2. 安装

### TypeScript

```bash
npm install @anthropic-ai/claude-agent-sdk
```

TypeScript SDK 通过 npm optional dependencies 打包原生 Claude Code 二进制（F-022）。如果安装时跳过 optional dependencies（例如 `npm ci --omit=optional`），二进制不会安装（F-026）。

### Python

```bash
pip install claude-agent-sdk
```

Python SDK 在多数平台以 wheel 形式附带 CLI，无需单独安装 Claude Code（F-023）。例外是 pip 安装到源码分发（例如 ARM64 Windows）时不含二进制，需要另装 Claude Code 并确保它在 `PATH` 上（F-026）。

### API key

```bash
export ANTHROPIC_API_KEY=your-api-key
```

SDK 从运行 agent 的进程环境读取 key，**不会自动加载 `.env`**；若把 key 放在 `.env`，需要自己用 `dotenv` 等工具先加载（F-029）。

> **认证边界**：除非事先获批，第三方产品不得提供 claude.ai 登录或速率限制，应使用 API key（F-030）。

## 3. 最小 Agent

博文给出的 Python 最小示例（F-031~F-035）：

```python
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="Find and fix the bug in auth.py",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Edit", "Bash"],
            permission_mode="acceptEdits",
        ),
    ):
        print(message)
```

三个部分：

1. `query()` 创建 agentic loop，返回异步消息流（F-035）。
2. `prompt` 是任务描述；agent 自己决定用哪些工具、按什么顺序用。
3. `options` 控制工具、权限、模型、工作目录、轮数、系统提示与 MCP。

官方 quickstart 的版本多了消息类型过滤，便于看到“思考 / 工具调用 / 最终结果”（F-043~F-045）：

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

async def main():
    async for message in query(
        prompt="Review utils.py for bugs that would cause crashes. Fix any issues you find.",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Edit", "Glob"],
            permission_mode="acceptEdits",
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)
                elif hasattr(block, "name"):
                    print(f"Tool: {block.name}")
        elif isinstance(message, ResultMessage):
            print(f"Done: {message.subtype}")

asyncio.run(main())
```

官方说明这段代码会读取文件、分析逻辑、编辑文件，结束时输出 `Done: success`（F-045）。SDK 负责编排、工具执行、上下文管理与重试，调用方只消费消息流（F-084）。

## 4. 七项配置

| 配置（Python / TS） | 作用 | 生产提示 | 依据 |
|---|---|---|---|
| `allowed_tools` / `allowedTools` | 预批准工具；支持 `Read`、`Edit`、`Bash`、`Glob`、`Grep`、`WebSearch` 等 | 它是“自动批准清单”，不是工具白名单；未列出的工具仍然存在 | F-036、F-053 |
| `permission_mode` / `permissionMode` | 控制权限请求处理；示例 `acceptEdits`、`ask` | 完整模式与评估顺序见 [02-permissions-and-hooks.md](02-permissions-and-hooks.md) | F-037、F-051 |
| `model` | 指定 Claude 模型 | 文章建议 `claude-sonnet-4-5`；该建议已过期，见 E-2 | F-038、F-066 |
| `cwd` | 设置文件操作的工作目录 | agent 默认可访问该目录及其子目录；生产应限定到工作区 | F-039、F-087 |
| `max_turns` / `maxTurns` | 限制对话轮数 | 防失控循环的第一道闸；与超时、预算一起设 | F-040 |
| `system_prompt` | 自定义系统指令 | 系统提示影响工具选择与行为边界；首次请求后会被记录复用，变更需新会话或 `snapshot=False` | F-041、F-086 |
| `mcp_servers` | 连接 MCP 服务器扩展工具 | 每个 MCP server 都是新的攻击面与权限面 | F-042 |

### 工具三档

官方 quickstart 给了三档工具组合，可作为最小权限上线的起点（F-085）：

| 档位 | 工具组合 | 能力 | 适用阶段 |
|---|---|---|---|
| 只读分析 | `Read`、`Glob`、`Grep` | 读代码、找文件、搜内容 | 观察期、审计、代码问答 |
| 分析并修改 | `Read`、`Edit`、`Glob` | 在只读基础上改文件 | 受控修复、文档更新 |
| 全自动化 | `Read`、`Edit`、`Bash`、`Glob`、`Grep` | 跑命令、测试、安装依赖 | 沙箱内的完整 agent |

> `Bash` 是权限面最大的一档：它能绕过 `Write|Edit` hook（F-057），也能执行 `rm`、`curl` 等命令。上线顺序应是“只读 → 改文件 → 沙箱内 Bash”，不要一步到位。

## 5. 版本与打包快照

| 项 | 2026-11-10 查询值 | 依据 |
|---|---|---|
| npm 包 | `@anthropic-ai/claude-agent-sdk` 0.3.322 | F-027 |
| npm engines | `node >=18.14.0` | F-027 |
| PyPI 包 | `claude-agent-sdk` 0.2.180 | F-028 |
| PyPI Python | 3.10–3.13 | F-028 |
| PyPI 状态 | Development Status 3 - Alpha | F-028 |

**版本策略**：生产环境锁定具体版本，不使用浮动 `latest`；升级前在沙箱跑回归与权限边界测试。Python 包仍标注 Alpha，意味着 API 可能变化，升级需要读 changelog。

## 6. 运行前检查清单

1. `node --version` ≥ 18.14 或 `python --version` ≥ 3.10（F-025）。
2. SDK 版本已锁定，且 `claude` 二进制可执行（F-026）。
3. `ANTHROPIC_API_KEY` 在当前进程环境中可见（F-029）。
4. `cwd` 指向专用工作目录，不是家目录或生产仓库根（F-039）。
5. `max_turns`、超时、token 预算已设置（F-040）。
6. 工具档位从只读开始，`Bash` 默认关闭（F-085）。
7. 权限模式不是 `bypassPermissions`（除非在一次性沙箱中）（F-078）。

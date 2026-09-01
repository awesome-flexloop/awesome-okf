---
type: Example
title: 基础使用
description: 从安装 nanobot 到运行代理、发送第一条消息、使用 WebUI 和 Python SDK 的完整入门示例。
tags: [nanobot, installation, quickstart, sdk, webui]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: nanobot 源码信源
---

# 基础使用

本示例展示 nanobot 的安装、首次配置和基本交互方式。

## 前置条件

- Python 3.11 或更高版本
- 一个受支持的 AI 提供商凭证（API 密钥或本地模型服务器）
- 从源码安装还需要 Git 和 [Bun](https://bun.sh/)

来源：`docs/quick-start.md:9-15`、`pyproject.toml:6`

## 安装

### 方式一：一键安装脚本

macOS / Linux：

```bash
curl -fsSL https://raw.githubusercontent.com/HKUDS/nanobot/main/scripts/install.sh | sh
```

Windows PowerShell：

```powershell
irm https://raw.githubusercontent.com/HKUDS/nanobot/main/scripts/install.ps1 | iex
```

安装器会选择活动的虚拟环境、`uv`、`pipx` 或 `~/.nanobot/venv` 下的托管环境，从 PyPI 安装稳定版。

### 方式二：使用 uv

```bash
uv tool install nanobot-ai
```

### 方式三：使用 pip

```bash
python -m pip install nanobot-ai
```

### 方式四：从源码安装

```bash
git clone https://github.com/HKUDS/nanobot.git
cd nanobot
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
python -m pip install -e .
```

从源码安装需要 Bun，因为检出代码直接运行匹配的 TUI，而非下载旧版二进制。

验证安装：

```bash
nanobot --version
```

来源：`README.md:71-159`、`docs/quick-start.md:17-35`

## 配置模型

推荐通过 WebUI 配置：

```bash
nanobot webui
```

浏览器打开后，进入 **Settings → Models**：

1. 选择拥有凭证的提供商
2. 输入 API 密钥或 base URL
3. 创建或选择一个模型预设（model preset），使用该提供商可运行的模型 ID
4. 保存配置

也可手动编辑 `~/.nanobot/config.json`：

```json
{
  "providers": {
    "openrouter": {
      "apiKey": "${OPENROUTER_API_KEY}"
    }
  },
  "modelPresets": {
    "primary": {
      "provider": "openrouter",
      "model": "anthropic/claude-opus-4.5",
      "maxTokens": 8192,
      "contextWindowTokens": 65536
    }
  },
  "agents": {
    "defaults": {
      "modelPreset": "primary"
    }
  }
}
```

配置文件路径默认为 `~/.nanobot/config.json`，工作区默认为 `~/.nanobot/workspace/`。

来源：`docs/quick-start.md:37-64`、`docs/providers.md:28-52`、`AGENTS.md:48`

## 验证安装

```bash
nanobot status
```

应看到 Config 和 Workspace 的勾选标记、所选模型或预设、以及该模型所用提供商的已配置状态。

然后发送一条测试消息：

```bash
nanobot agent -m "Hello!"
```

任何正常的助手回复都表示安装、配置、提供商/模型选择和工作区访问均正常工作。

来源：`docs/quick-start.md:66-107`

## 使用 WebUI

```bash
nanobot webui
```

启动器会：
1. 在需要时创建配置和工作区
2. 安全启用本地 WebSocket 通道
3. 启动或加入共享本地网关
4. 打开 `http://127.0.0.1:8765`

首次运行的 WebUI 默认绑定 localhost，不暴露到局域网。浏览器界面中可以：

- 为不同任务和项目保持独立话题
- 使用临时聊天（不保存到历史或记忆）
- 查看推理、工具调用、文件编辑、diff 和生成产物
- 在对话中切换模型和工作区
- 配置提供商、聊天通道、应用、技能和自动化

开发模式（带热更新）：

```bash
nanobot webui --dev
```

这会启动 Vite 开发服务器（`127.0.0.1:5173`），代理 API/WS 流量到网关。

来源：`README.md:163-220`、`nanobot/cli/webui.py:73-99`、`nanobot/webui/dev.py:19-20`

## 使用终端 TUI

```bash
nanobot agent
```

这将打开原生终端客户端，使用配置的模型和工具，以启动目录作为工作区。

常用操作：

| 操作 | 方式 |
|------|------|
| 发送消息 | `Enter` |
| 换行 | `Shift+Enter`（或 `Ctrl+J`） |
| 切换会话 | `/sessions` |
| 新聊天 | `/new-chat` |
| 查看上下文 | `/context` |
| 查看文件变更 | `/diff` |
| 从回复分叉 | `/branch` |
| 分离（保持网关运行） | `/detach` |
| 退出 | `exit` 或 `Ctrl+C` |

轮次运行中，`Enter` 引导当前轮次，`Tab` 将可见的后续消息排入队列，`Option+Up`（macOS）/`Alt+Up`（Windows/Linux）返回最新排队消息进行编辑。

使用 `--classic` 标志可恢复旧版 Python 提示符：

```bash
nanobot agent --classic
```

来源：`README.md:206-220`、`tui/src/app.ts:167-210`

## 使用 Python SDK

### 单次提问

```python
import asyncio
from nanobot import Nanobot

async def main() -> None:
    async with Nanobot.from_config() as bot:
        result = await bot.run("What time is it in Tokyo?")
    print(result.content)

asyncio.run(main())
```

`Nanobot.from_config()` 复用默认的 `~/.nanobot/config.json` 和 `~/.nanobot/workspace/`。

来源：`docs/python-sdk.md:63-76`、`nanobot/nanobot.py:90-140`

### 检查运行结果

```python
result = await bot.run("Review this repository")

print(result.content)      # 最终回答
print(result.tools_used)   # 使用的工具列表
print(result.usage)        # token 使用量
print(result.stop_reason)  # 停止原因
```

来源：`docs/python-sdk.md:89-98`、`nanobot/sdk/types.py:49-59`

### 连续对话

使用 `session_key` 在多轮之间保持历史：

```python
await bot.run("My name is Alice.", session_key="user:alice")
result = await bot.run("What is my name?", session_key="user:alice")
print(result.content)  # 应回答 "Alice"
```

不同的 `session_key` 拥有独立的对话历史。产品代码应使用稳定的键，如 `user:<id>`、`project:<id>` 或 `eval:<case-id>`。

来源：`docs/python-sdk.md:100-113,300-319`

### 流式输出

```python
from nanobot import STREAM_EVENT_TEXT_DELTA

async for event in bot.stream("Write a migration plan"):
    if event.type == STREAM_EVENT_TEXT_DELTA:
        print(event.delta, end="", flush=True)
```

流式事件包括文本增量、推理增量、工具开始/完成/失败、运行完成/失败等 10 种类型。

来源：`docs/python-sdk.md:116-128`、`nanobot/sdk/types.py:11-46`

### 完整流式示例

```python
import asyncio
import sys
from nanobot import (
    STREAM_EVENT_RUN_COMPLETED,
    STREAM_EVENT_RUN_FAILED,
    STREAM_EVENT_TEXT_DELTA,
    STREAM_EVENT_TOOL_STARTED,
    Nanobot,
)

async def main() -> None:
    prompt = " ".join(sys.argv[1:]) or "Explain nanobot in one paragraph."

    async with Nanobot.from_config() as bot:
        async for event in bot.stream(prompt, session_key="sdk:demo"):
            if event.type == STREAM_EVENT_TEXT_DELTA:
                print(event.delta, end="", flush=True)
            elif event.type == STREAM_EVENT_TOOL_STARTED:
                print(f"\n[tool] {event.name}", flush=True)
            elif event.type == STREAM_EVENT_RUN_COMPLETED:
                result = event.result
                print(f"\nstop_reason: {result.stop_reason}")
                print(f"tools_used: {result.tools_used}")
                print(f"usage: {result.usage}")
            elif event.type == STREAM_EVENT_RUN_FAILED:
                raise RuntimeError(event.error or "run failed")

asyncio.run(main())
```

来源：`docs/python-sdk.md:130-176`

### 指定工作区或模型

```python
# 指定工作区
async with Nanobot.from_config(workspace="/my/project") as bot:
    result = await bot.run("Explain the project structure")

# 指定实例默认模型
bot = Nanobot.from_config(model="openai/gpt-4.1")

# 单次运行覆盖模型
result = await bot.run("Summarize", model="openai/gpt-4.1-mini")

# 使用模型预设
bot = Nanobot.from_config(model_preset="fast")
```

`model` 和 `model_preset` 互斥，不能同时提供。

来源：`docs/python-sdk.md:243-291`、`nanobot/nanobot.py:90-140`

## 后台网关

关闭终端后保持 nanobot 运行：

```bash
nanobot gateway --background
```

管理命令：

```bash
nanobot gateway status
nanobot gateway logs
nanobot gateway restart
nanobot gateway stop
```

网关运行时连接已启用的聊天通道、WebSocket（供 TUI/WebUI 连接）、Dream 记忆整合和 heartbeat 定时任务。网关健康端点默认在 `127.0.0.1:18790`，WebUI/WebSocket 默认在 `8765`。

来源：`README.md:181-204`、`docs/concepts.md:77-87`

## 相关概念

- [nanobot 简介](../concepts/00-introduction.md)
- [整体架构](../concepts/01-architecture.md)
- [Agent 运行时](../concepts/02-agent-runtime.md)
- [多接口架构](../concepts/05-multi-interface.md)

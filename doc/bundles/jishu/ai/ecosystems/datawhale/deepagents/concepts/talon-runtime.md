---
title: Talon 运行时宿主
type: concept
bundle: /datawhale/deepagents
related:
  - /datawhale/deepagents/concepts/core-sdk
  - /datawhale/deepagents/concepts/code-module
  - /datawhale/deepagents/concepts/monorepo-architecture
sources:
  - https://github.com/datawhalechina/deepagents/blob/main/libs/talon/README.md
  - https://github.com/datawhalechina/deepagents/blob/main/libs/talon/pyproject.toml
  - https://github.com/datawhalechina/deepagents/blob/main/libs/talon/deepagents_talon/
---

# Talon 运行时宿主

`deepagents-talon`（位于 `libs/talon/`）是长运行 Deep Agents 的**本地运行时宿主**。它在单个事件循环中拥有通道适配器、cron 调度器和 Agent 运行时的进程生命周期。

> 状态：实验性 Alpha（版本 0.0.3），可能随时变更或移除。不提供生产级安全控制，不接受关于已知未实现安全功能的漏洞报告。

## 核心能力

- **宿主进程**：优雅关闭、每会话序列化、`/stop` 取消
- **通用通道协议**：可扩展的消息通道抽象
- **WhatsApp 适配器**：通过本地 Node bridge（仅 loopback 通信）
- **Telegram 适配器**：通过 Bot API 长轮询
- **持久化 cron 调度器**：带 Agent 可调用的 cron 工具助手
- **MCP 工具加载**：从显式配置路径或 `~/.deepagents/.mcp.json`
- **可选 LangSmith tracing**：每个通道或 cron 触发的运行

## 快速开始

```bash
cd libs/talon
uv sync --group test
AGENT_ASSISTANT_ID=local AGENT_MODEL=<provider>:<model-id> uv run deepagents-talon --once
```

如果未设置 `AGENT_MODEL`，Talon 以 echo 运行时启动（原样返回入站文本），用于检查宿主生命周期和通道连接。

## 状态目录

助手状态默认存储在 `~/.deepagents/<assistant_id>/`，权限 0700：

- `AGENTS.md`、`skills/`、`agents/` — 物化的助手指令、技能和子 Agent 定义
- `cron/jobs.json` — cron 提示、来源会话 ID、消息 ID、运行状态和错误（权限 0600）
- `channels/whatsapp/` — WhatsApp LocalAuth 凭据和 Chromium 配置状态
- `media/inbound/` — 下载的入站媒体（默认 24 小时后清理）

## 通道配置

### WhatsApp

WhatsApp 通道使用打包的本地 Node bridge，Python 适配器通过 loopback 与其通信：

```bash
cd deepagents_talon/channels/whatsapp_bridge
npm install
cd ../../..

DEEPAGENTS_TALON_WHATSAPP_ENABLED=true \
DEEPAGENTS_TALON_WHATSAPP_START_BRIDGE=true \
AGENT_ASSISTANT_ID=whatsapp-local \
AGENT_MODEL=<provider>:<model-id> \
uv run deepagents-talon --whatsapp
```

**暴露模式**：
- `self`（默认）：仅配对账户的消息触发 Agent
- `allowlist`：通过 `DEEPAGENTS_TALON_WHATSAPP_ALLOWLIST_CHATS` 或 `DEEPAGENTS_TALON_WHATSAPP_MENTION_PATTERNS` 允许特定聊天
- `open`：允许任意 WhatsApp 发送者触发 Agent，需要显式确认 `DEEPAGENTS_TALON_WHATSAPP_OPEN_ACK=allow-arbitrary-senders`

**媒体限制**：
- 全局 `DEEPAGENTS_TALON_MAX_MEDIA_BYTES` 默认 1 GiB
- WhatsApp 进一步限制为 64 MiB（bridge 在内存中物化下载）

**语音转录**（可选）：
```bash
DEEPAGENTS_TALON_VOICE_TRANSCRIPTION_ENABLED=true
```
默认使用 NVIDIA Parakeet 模型（`nvidia/parakeet-tdt-0.6b-v3`）通过 Transformers，ffmpeg 转换为 16kHz 单声道 WAV。设置 `DEEPAGENTS_TALON_VOICE_TRANSCRIPTION_DEVICE=cuda` 使用 GPU。

### Telegram

Telegram 通道使用 Bot API 长轮询：

```bash
DEEPAGENTS_TALON_TELEGRAM_ENABLED=true \
DEEPAGENTS_TALON_TELEGRAM_BOT_TOKEN=... \
DEEPAGENTS_TALON_TELEGRAM_EXPOSURE=allowlist \
DEEPAGENTS_TALON_TELEGRAM_ALLOWLIST_USERS=123456789 \
DEEPAGENTS_TALON_TELEGRAM_ALLOWLIST_CHATS=-1001234567890 \
AGENT_ASSISTANT_ID=telegram-local \
AGENT_MODEL=<provider>:<model-id> \
uv run deepagents-talon --telegram
```

`allowlist` 模式下，`ALLOWLIST_USERS` 允许特定用户的私聊，`ALLOWLIST_CHATS` 允许特定频道的帖子。

## MCP 工具

Talon 从一个配置文件加载 MCP 服务器，查找顺序：
1. `DEEPAGENTS_TALON_MCP_CONFIG` 环境变量
2. `MCP_CONFIG` 环境变量
3. `~/.deepagents/.mcp.json`

```json
{
  "mcpServers": {
    "linear": {
      "type": "http",
      "url": "https://mcp.example/mcp"
    }
  }
}
```

命令：
- `deepagents-talon mcp config` — 打印解析的配置路径
- `deepagents-talon mcp login <server>` — 为 OAuth 支持的服务器登录

## Fleet 导入

Talon 可将 Fleet zip 导出物化为本地 Agent 目录：

```bash
deepagents-talon import-fleet <fleet-export.zip> [--assistant-id <id>] [--target-dir <dir>]
```

导入器写入：
- Fleet 提示、技能和子 Agent 提示到助手目录
- `.mcp.json`（运行时 MCP 配置，包含清理后的 OAuth 条目）
- `.mcp.json.setup`（人类可读的配置交接）

Fleet `tools.json` 仅作为导入输入读取，不复制到 Talon Agent 目录。Fleet `config.json` 被忽略。

## 工具审批覆盖

`DEEPAGENTS_TALON_INTERRUPT_ON_TOOLS` 设置需要通道审批流程的工具名称逗号分隔列表，与 Agent 提供的 HITL 配置叠加：

```bash
DEEPAGENTS_TALON_INTERRUPT_ON_TOOLS=bash,execute,github_create_pr
```

## Cron 可观测性

Cron 作业持久化在 `cron/jobs.json`。调度器生命周期事件通过标准 Python logger 以 `talon_event` JSON 记录发出：

- `cron.tick`
- `cron.dispatch`
- `cron.success`
- `cron.failure`
- `cron.delivery`
- `cron.delivery_suppressed`
- `cron.delivery_failure`

活动作业在启用期间保留，完成作业在启动后按 `DEEPAGENTS_TALON_CRON_RETENTION_DAYS`（默认 30 天）删除。

## 安全边界

Talon 为**单操作者设计**，明确不提供：
- 多租户隔离
- 沙箱支持的执行隔离
- 生产级 HITL 策略执行
- 通道管理员边界

通道访问应被视为对操作者的 Agent、模型凭据、MCP 工具和本地主机资源的直接访问。

攻击者可影响的输入包括：通道消息文本、语音转录、通道媒体元数据、下载的媒体文件、Web/搜索结果内容、MCP 工具结果和导入的清单指令——均视为不可信内容进入 Agent 上下文。

对话持久化目前不是持久的——运行时对话状态在内存中，除非未来后端显式添加线程持久化。

## 源码结构

```text
libs/talon/deepagents_talon/
  __init__.py
  __main__.py
  host.py              # 宿主进程
  runtime.py           # Agent 运行时
  config.py            # 配置
  interfaces.py        # 通道协议接口
  channels/
    base.py            # 通道基类
    telegram.py        # Telegram 适配器
    whatsapp.py        # WhatsApp 适配器
    whatsapp_bridge/   # Node.js bridge
  cron/
    scheduler.py       # cron 调度器
    jobs.py            # 作业模型
    tools.py           # Agent 可调用的 cron 工具
  mcp.py               # MCP 工具加载
  speech.py            # 语音转录
  media.py             # 媒体处理
  observability.py     # 可观测性
  data_lifecycle.py    # 数据生命周期
  fleet_import.py      # Fleet zip 导入
  async_subagents.py   # 异步子 Agent
```

## 依赖

```toml
dependencies = [
    "deepagents>=0.7.0",
    "deepagents-code>=0.1.30,<1.0.0",
    "langchain-mcp-adapters>=0.3.0,<1.0.0",
]
```

## 与其他概念的关系

- 核心SDK与三层架构 提供 Agent 运行时基础。
- Code终端编码Agent 是 Talon 的 Agent 运行时依赖（`deepagents-code>=0.1.30`）。
- Monorepo 架构 描述了 talon 包在仓库中的位置。

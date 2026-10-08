---
title: Talon 启动 Telegram Agent
type: example
bundle: /datawhale/deepagents
sources:
  - https://github.com/datawhalechina/deepagents/blob/main/libs/talon/README.md
---

# Talon 启动 Telegram Agent

配置并启动 Talon Telegram 通道，让 Agent 通过 Telegram Bot 响应消息。

## 安装与同步

```bash
cd libs/talon
uv sync --group test
```

## 启动 Telegram Agent

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

## 从仓库根目录运行

```bash
DEEPAGENTS_TALON_TELEGRAM_ENABLED=true \
DEEPAGENTS_TALON_TELEGRAM_BOT_TOKEN=... \
AGENT_ASSISTANT_ID=telegram-local \
AGENT_MODEL=<provider>:<model-id> \
uv run --directory libs/talon deepagents-talon --telegram
```

## 关键环境变量

| 变量 | 说明 |
|------|------|
| `DEEPAGENTS_TALON_TELEGRAM_ENABLED` | 启用 Telegram 通道 |
| `DEEPAGENTS_TALON_TELEGRAM_BOT_TOKEN` | BotFather 获取的 Bot Token |
| `DEEPAGENTS_TALON_TELEGRAM_EXPOSURE` | 暴露模式：`self`/`allowlist`/`open` |
| `DEEPAGENTS_TALON_TELEGRAM_ALLOWLIST_USERS` | 允许的用户 ID（逗号分隔） |
| `DEEPAGENTS_TALON_TELEGRAM_ALLOWLIST_CHATS` | 允许的频道 ID（逗号分隔） |
| `AGENT_ASSISTANT_ID` | 助手标识符，决定状态目录 |
| `AGENT_MODEL` | 模型标识符，未设置时使用 echo 运行时 |
| `DEEPAGENTS_TALON_WORKSPACE` | 本地执行工作目录（默认当前目录） |
| `DEEPAGENTS_TALON_MCP_CONFIG` | MCP 配置文件路径 |
| `DEEPAGENTS_TALON_INTERRUPT_ON_TOOLS` | 需要审批的工具列表 |

## Echo 运行时

如果不设置 `AGENT_MODEL` 和 `DEEPAGENTS_TALON_MODEL`，Talon 使用 echo 运行时，原样返回入站文本，可用于测试通道连接。

## 相关概念

- Talon运行时宿主

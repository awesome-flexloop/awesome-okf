---
title: libs/talon/README.md
type: reference
bundle: /datawhale/deepagents
source_path: libs/talon/README.md
source_url: https://github.com/datawhalechina/deepagents/blob/main/libs/talon/README.md
---

# libs/talon/README.md 引用

Deep Agents Talon 运行时宿主的完整文档。

## 核心内容

- **定位**：长运行 Deep Agents 的本地运行时宿主，在单个事件循环中管理通道适配器、cron 调度器和 Agent 运行时的进程生命周期
- **实验性声明**：Alpha 状态，可能随时变更/移除；不提供生产级安全控制（HITL、通道管理员、沙箱隔离、多租户边界）
- **核心能力**：宿主进程（优雅关闭/会话序列化/stop 取消）、通用通道协议、WhatsApp 适配器（Node bridge）、持久化 cron 调度器、MCP 工具加载、可选 LangSmith tracing
- **快速开始**：`uv sync --group test`，设置 AGENT_ASSISTANT_ID 和 AGENT_MODEL，`uv run deepagents-talon --once`
- **状态目录**：`~/.deepagents/<assistant_id>/`，0700 权限，包含 AGENTS.md/skills/agents/、cron/jobs.json、channels/、media/inbound/
- **WhatsApp 通道**：本地 Node bridge（仅 loopback），三种暴露模式 self/allowlist/open（open 需显式确认），媒体限制全局 1GiB/WhatsApp 64MiB，可选语音转录（Parakeet/OpenAI）
- **Telegram 通道**：Bot API 长轮询，allowlist 用户/聊天 ID
- **MCP 工具**：配置查找顺序 DEEPAGENTS_TALON_MCP_CONFIG → MCP_CONFIG → ~/.deepagents/.mcp.json；`mcp config` 和 `mcp login` 命令
- **Fleet 导入**：`import-fleet <zip>` 物化提示/技能/子 Agent/.mcp.json，忽略 tools.json 和 config.json
- **工具审批**：DEEPAGENTS_TALON_INTERRUPT_ON_TOOLS 逗号分隔列表，与 Agent HITL 叠加
- **Cron 可观测性**：jobs.json 持久化，talon_event JSON 日志（tick/dispatch/success/failure/delivery）
- **安全说明**：单操作者设计，不可信输入包括通道消息/语音/媒体/MCP结果/导入清单；对话状态非持久（内存中）
- **数据生命周期**：cron 保留 30 天（DEEPAGENTS_TALON_CRON_RETENTION_DAYS），入站媒体 24 小时（DEEPAGENTS_TALON_INBOUND_MEDIA_RETENTION_HOURS）
- **开发**：`uv sync --group test`，`uv run --group test pytest tests/`，`make lint`，`make test`

## 相关概念

- Talon运行时宿主

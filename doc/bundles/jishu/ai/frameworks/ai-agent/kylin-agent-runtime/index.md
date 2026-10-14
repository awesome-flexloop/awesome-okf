---
type: bundle
okf_version: "0.2"
scope: kylin-agent-runtime
name: kylin-agent-runtime
version: "0.1.0"
source: gitee.com/openkylin/agent-runtime@ee0c170
description: openKylin Kylin Agent Runtime（基于 Hermes 改进的自进化智能体运行时）源码教程——核心对话环、工具体系、多模型 Provider、技能插件、记忆上下文、消息网关与 ACP/MCP/LSP 协议。
generated: { by: "process:seven-concepts-e/trae-cn", at: 2026-10-14T00:00:00+08:00 }
---

# Kylin Agent Runtime 麒麟智能体运行时

Kylin Agent Runtime（包名 `kylin-agent-runtime`，仓库 openkylin/agent-runtime）是 openKylin 社区基于 Hermes Agent 改进的**自进化智能体运行时**：从经验中创建技能、在使用中改进技能、持久化用户与会话知识、跨会话检索历史对话，并以 CLI、Ink TUI、Web 控制台、消息网关、ACP 编辑器协议与 OpenAI 兼容 API 等多种形态运行（F-010、F-017）。

- **仓库**：https://gitee.com/openkylin/agent-runtime.git
- **本教程快照**：commit `ee0c1709199b37ebccdc69b545f266e52e5ed6c9`（2026-10-13，`V0.9.4-52`）；打包版本 1.0.1
- **Python 要求**：>= 3.11
- **许可证**：MIT
- **社区归属**：openKylin AISubsystem SIG（SIG 120，"打造麒麟 OS Agent"）

## 与 Hermes 的关系

本项目是 Hermes Agent 的 openKylin 下游：分发与品牌层已麒麟化（包名/主命令/`~/.kylin-agent-runtime/` 配置目录/KylinAgent ACP 注册），代码符号层保留大量 Hermes 血缘（`HermesCLI`、`HermesACPAgent`、`hermes_agent.plugins` entry-points、`HERMES_*` 环境变量、三个 hermes 兼容命令别名）。下游增量集中在国产消息平台（钉钉/飞书/企业微信/微信/QQ/元宝）、KylinAgent 桌面审批协同、中文网络指引与国内镜像、kylin-cua 桌面控制技能。详见 [00 总览](concepts/00-overview.md)，上游架构可对照同簇的 [hermes-agent](../hermes-agent/index.md) 束。

## 导航

### 概念文档（10 篇）

| 文档 | 说明 |
|------|------|
| [00 总览](concepts/00-overview.md) | 定位、自进化三回路、多版本号、Hermes 血缘与 openKylin 增量、SIG 归属 |
| [01 整体架构与模块地图](concepts/01-architecture-module-map.md) | 三代架构、入口依赖链、模块规模与技术栈 |
| [02 Agent 核心对话环](concepts/02-agent-core-loop.md) | AIAgent 转发壳、init_agent、工具迭代、护栏、重试预算、安全纵深 |
| [03 CLI/TUI/Web 控制台](concepts/03-cli-and-tui.md) | 双 CLI、48 子命令、setup、dashboard、Ink TUI 与 JSON-RPC 后端 |
| [04 工具系统](concepts/04-tool-system.md) | 自注册发现链、31 工具集、8 终端环境、computer_use |
| [05 模型与 Provider](concepts/05-model-providers.md) | 4 传输、中央路由、凭证池、懒安装、元数据定价 |
| [06 技能与插件](concepts/06-skills-and-plugins.md) | 技能树、curator、17 钩插件、四类能力 Provider |
| [07 记忆与上下文](concepts/07-memory-and-context.md) | SessionDB 双 FTS5、压缩引擎、记忆 ABC、用户画像治理 |
| [08 消息网关与定时调度](concepts/08-gateway-and-cron.md) | GatewayRunner、21 平台适配器、会话模型、cron |
| [09 ACP/MCP/LSP 协议](concepts/09-acp-mcp-protocols.md) | ACP stdio、FastMCP、26 LSP 服务器 |

### 示例（2 篇）

| 文档 | 说明 |
|------|------|
| [安装、初始化与首次运行](examples/01-install-setup-first-run.md) | uv 安装、setup、四种运行方式、测试与更新 |
| [网关服务化与定时任务](examples/02-gateway-and-cron-usage.md) | systemd 服务、gateway 命令、cron 作业字段 |

### 参考与规格

| 文档 | 说明 |
|------|------|
| [源码信源索引](references/source-code-map.md) | 快照元数据、文件→事实 F-001~F-150 映射、计数口径 |
| [AISubsystem SIG 信源](references/community-sig.md) | SIG 120 使命与社区生态 |
| [事实清单](spec/facts.md) | 150 条编号事实 + 10 条数量卡 + 勘误审计 |
| [架构洞察](spec/insights.md) | 5 条四元组洞察与知识地图 |

## 目录结构

```text
kylin-agent-runtime/
├── index.md
├── log.md
├── concepts/          # 10 篇概念文档 + index
├── examples/          # 2 篇示例 + index
├── references/        # 2 份信源登记 + index
└── spec/              # facts.md（150 F/10 Q）+ insights.md（5 洞察）
```

## 技术栈

| 层 | 技术 |
|----|------|
| 语言/运行时 | Python >= 3.11、setuptools（14 个 py-modules + 9 个包） |
| 模型接入 | openai 2.24、Anthropic/Bedrock SDK、4 类自研传输（anthropic_messages/bedrock_converse/chat_completions/codex_responses） |
| 数据存储 | SQLite（9+2 表）、FTS5 + trigram 全文检索、JSONL 回退 |
| 网关 | asyncio、httpx、python-telegram-bot/discord.py/slack/飞书/钉钉等平台 SDK（extras 懒安装） |
| Web 控制台 | FastAPI + uvicorn（127.0.0.1:9119）、React 19 + Vite + Tailwind v4 + xterm.js |
| TUI | Node/TypeScript、ink 6 + React 19、tui_gateway JSON-RPC 2.0 |
| 协议 | ACP（agent-client-protocol 0.9，stdio）、MCP（FastMCP）、LSP（26 服务器）、croniter |
| 打包分发 | pip extras（[all] 收敛策略）、Docker、docker-compose、Nix、Homebrew、systemd |

## 学习路径

主干 `00 → 01 → 02`；运行与能力展开读 `03 / 04 / 05`；自进化深水区读 `06 / 07`；对外连接读 `08 / 09`；上手操作跟随两篇 examples。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```

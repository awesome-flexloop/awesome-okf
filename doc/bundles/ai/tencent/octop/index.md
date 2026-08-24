---
type: bundle
title: Octop 自托管 AI 助手平台
okf_version: "0.2"
---

# Octop 源码知识束

本知识包是腾讯 WorkBuddy 团队开源的自托管多用户、多 Agent AI 助手平台 [Octop](https://github.com/Tencent/WorkBuddy)（MIT 许可证，v0.9.25）的系统化中文源码教程。Octop 以单个 Python wheel 分发，集成 FastAPI 后端、React Dashboard 和 Click CLI，核心 AI 能力委托给 `orcakit-harness-agent`（LangGraph）、`harness-gateway`、`harness-memory`、`harness-browser` 四个外部包。

所有内容均溯源至 `external/libs/ai/Tencent/WorkBuddy/Octop/` 源码，遵循 [OKF v0.2 规范](concepts/00-architecture.md)，经 R→I→E→V 四阶段流程生成，共 133 条源码事实（F-001~F-133）和 5 个架构洞察（I-01~I-05）。

## 核心概念（concepts/）

* [Octop 四层架构与依赖禁令](concepts/00-architecture.md) — dashboard→api→infra→utils 四层分层、六条硬禁令、launch.py 独占组合根、单进程 asyncio 模型、frozen dataclass 配置体系。
* [服务器生命周期：OctopServer](concepts/01-server-lifecycle.md) — start/stop 流程、_boot_runtime 12 步装配顺序、Greenfield 延迟绑定（全新安装不先开 DB）、AppRuntime 五个运行时单例、热替换机制、JWT 密钥与日志轮转。
* [Agent 运行时：AgentManager 与 HarnessAgent](concepts/02-agent-runtime.md) — AgentManager 进程级单例、HarnessAgent 委托、Agent CRUD、stream/call/HITL、有界并行热重载（并发 6）、MCP 用户级工具缓存、MBTI 16 种人格、专家库与子代理、安全 guardrails。
* [Gateway 与通道：IM 消息路由](concepts/03-gateway-channels.md) — GlobalProcessor、ChannelManager（harness-gateway）、WebSocket/CLI 内置 Hub、飞书/钉钉/QQ/Discord/企微 IM 通道、Cron 投递、Slash 抢占式 `/stop` 取消、ThreadRegistry。
* [数据库层与 DI](concepts/04-db-di.md) — DatabasePool Protocol、SqlitePool（WAL+RLock）、PostgresPool（psycopg_pool）、RepoBundle 22 个 Repository、SharedServices 手动 DI 容器、迁移 schema v7。
* [ACP 双向集成](concepts/05-acp-protocol.md) — 入站（`octop acp` stdio 服务器，Zed 等 IDE 驱动）与出站（`acp_runner` 工具委托 OpenCode/CodeBuddy/Claude Code/Codex）、per-user runner + per-agent 开关。
* [CLI 命令体系](concepts/06-cli-commands.md) — _LazyCLI 延迟加载、20 个子命令、Offline/Embedded/External 三层传输、Windows UTF-8 兼容、CLI 状态文件。

## 实战示例（examples/）

* [自托管部署：从安装到运行](examples/self-hosted-setup.md) — pip 安装、`octop init`、SQLite/PostgreSQL 配置、`octop run`（含 HTTPS）、环境变量、systemd 服务、备份恢复。
* [创建自定义 Agent](examples/custom-agent.md) — CLI/HTTP API 创建 Agent、MBTI 人格、系统提示词、技能包、MCP 连接器、ACP runner、工作区目录、共享 Agent、JWT/argon2/guardrails 安全。
* [ACP 集成：Zed 入站与 Runner 出站](examples/acp-integration.md) — Zed settings.json 配置、四个内置 runner 安装与启用、acp_runner 六种 action、权限处理、自定义 runner、双向架构。

## 信源登记簿（references/）

* [服务器启动与组合根](references/server-launch.md) — `infra/server.py` + `launch.py`：OctopServer、AppRuntime、start/stop/_boot_runtime、Greenfield 延迟绑定、bind_control_plane。
* [AgentManager](references/agent-manager.md) — `infra/agents/manager.py`：CRUD、生命周期、热重载、MCP 缓存、settings stores。
* [Gateway](references/gateway.md) — `infra/gateway/gateway.py`：ChannelManager、GlobalProcessor、WS/CLI Hub、IM 通道、Cron 投递、抢占取消。
* [数据库层](references/db-layer.md) — `infra/db/pool.py` + `services.py` + `factory.py`：DatabasePool、SqlitePool/PostgresPool、RepoBundle（22 Repo）、SharedServices、迁移。
* [CLI 与 HTTP API](references/cli-api.md) — `cli/main.py` + `registry.py` + `commands/run.py` + `api/app.py`：_LazyCLI、20 子命令、三层传输、FastAPI 工厂、50+ 路由、SPA fallback。
* [Harness 技术栈](references/harness-stack.md) — `pyproject.toml` + `config.py` + `infra/utils/paths.py` + `AGENTS.md`：四个 harness 外部包、OctopConfig、PathLayout、模块边界禁令。

## 工作文档（spec/）

* [源码事实清单](spec/facts.md) — R 阶段产出：133 条编号事实 F-001~F-133，零推测纯客观描述。
* [架构洞察](spec/insights.md) — I 阶段产出：5 个核心架构洞察 I-01~I-05（Greenfield 延迟绑定、组合根独占、Harness 委托、CLI 延迟加载+三层传输、单进程有界并行热重载）。

## 信任与生命周期说明

* **status 判定依据**：全部 16 个内容文档（7 个概念 + 3 个示例 + 6 个信源登记）均 `status: stable`。内容基于对 Octop v0.9.25 源码核心模块的逐文件阅读与事实提取（133 条事实），经 R→I→E→V 四阶段流程生成，V 阶段通过 Grep 验证关键类名、命令数和 ACP runner 一致性。
* **stale_after 解释**：统一设置为 `2027-08-23`。Octop 核心架构（四层依赖禁令、组合根独占、Harness 委托、Greenfield 延迟绑定、单进程 asyncio）在 0.9.x 系列保持稳定；该日期作为对未来大版本（如 1.0 引入 breaking change 或 harness 包 API 重构）的保守重新评估节点。
* **外部包边界**：harness-agent/gateway/memory/browser 是腾讯内部包，本文档只描述 Octop 如何调用它们的公共 API，不虚构其内部实现。

```{toctree}
:hidden:

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```

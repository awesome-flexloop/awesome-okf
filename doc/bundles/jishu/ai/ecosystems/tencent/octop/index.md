---
type: bundle
title: Octop 自托管 AI 助手平台
okf_version: "0.2"
---

# Octop 源码知识包

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

## v1.0.2b5 增量轮（2026-10-04）

2026-10-04 基于上游 GA 后版本 **v1.0.2b5**（commit `e473dd3c`，信源 `external/dao/runtime/tencent/Octop/`；旧信源 `external/libs/ai/Tencent/WorkBuddy/Octop/` 已失效）完成增量扩展：新增 **459 条事实**（F-134~F-592，全量 592 条）与 **10 个洞察**（I-06~I-15），新增 4 篇信源登记、15 篇概念（07-21）、5 篇示例。1.0 系列品牌独立，AI 能力委托包更名为 `octop-harness`/`octop-memory`/`octop-gateway`/`octop-browser`（`>=1.0.0`），数据库 schema 演进至 v19，`_boot_runtime` 装配由 12 步扩为 17 步、RepoBundle 由 22 扩为 25。上文 00-06 旧文档描述的 v0.9.25 口径作为历史版本事实保留，新口径以 07-21 与四篇新信源为准。

### 新概念（concepts/07-21）

* [07 连接器系统：25 连接器与 MCP 三模式网关](concepts/07-connector-system.md) · [08 知识库 RAG：每库 SQLite 与全表内存余弦](concepts/08-knowledge-rag.md) · [09 消息网关进阶](concepts/09-gateway-advanced.md) · [10 专家团队：主持人剥权隔离](concepts/10-agent-teams.md) · [11 专家市场、子代理库与 MBTI](concepts/11-agent-marketplace.md)
* [12 Agent 运行时内部](concepts/12-agent-runtime-internals.md) · [13 插件与技能包](concepts/13-plugin-system.md) · [14 Octop↔Octop 联邦桥接](concepts/14-bridge-federation.md) · [15 自动备份与存储后端](concepts/15-backup-and-storage.md) · [16 版本化历史与轨迹流](concepts/16-history-trajectory.md)
* [17 用户、RBAC、SSO 与验证码](concepts/17-users-auth-security.md) · [18 云手机、桌面会话与主动关怀](concepts/18-mobile-desktop-proactive.md) · [19 Dashboard 前端架构](concepts/19-dashboard-frontend.md) · [20 API 装配面与 CLI 22 命令](concepts/20-api-cli-surface.md) · [21 打包与部署](concepts/21-packaging-deployment.md)

### 新示例（examples/）

* [插件开发：tool 插件从骨架到 UI 卡片](examples/plugin-development.md) · [知识库实战：建库、入库、检索调参](examples/knowledge-base-use.md) · [联邦桥接：远程专家接入本地](examples/bridge-remote-expert.md) · [组建专家团队](examples/expert-team-setup.md) · [Docker Compose 部署三套环境](examples/docker-compose-deploy.md)

### 新信源（references/）

* [v1.0.2b5 源码地图与构建清单](references/source-v1-map.md)（F-134~F-205、F-556~F-592） · [HTTP API 挂载总表与端点计数](references/api-surface.md)（F-503~F-555） · [连接器目录与 MCP 三模式网关](references/connectors-catalog.md)（F-276~F-315、F-382~F-383） · [Octop↔Octop 桥接协议](references/bridge-protocol.md)（F-384~F-401）

### 新洞察（I-06~I-15）

品牌独立更名 octop-* · 17 步装配膨胀与不可逆服务 · 25 连接器三模式 MCP 网关 · 每库 SQLite 全表内存余弦 RAG · team host 剥权 5 工具 · bridge 影子 ID+白名单 SSRF 联邦 · history v2 内容寻址归档 · 插件三 API 官方只用 tool · SSO×验证码×26 权限 · 异构数据面统一容灾。详见 [spec/insights.md](spec/insights.md)。

## 信任与生命周期说明

* **status 判定依据**：全部 16 个内容文档（7 个概念 + 3 个示例 + 6 个信源登记）均 `status: stable`。内容基于对 Octop v0.9.25 源码核心模块的逐文件阅读与事实提取（133 条事实），经 R→I→E→V 四阶段流程生成，V 阶段通过 Grep 验证关键类名、命令数和 ACP runner 一致性。
* **stale_after 解释**：统一设置为 `2027-08-23`。Octop 核心架构（四层依赖禁令、组合根独占、Harness 委托、Greenfield 延迟绑定、单进程 asyncio）在 0.9.x 系列保持稳定；该日期作为对未来大版本（如 1.0 引入 breaking change 或 harness 包 API 重构）的保守重新评估节点。
* **外部包边界**：harness-agent/gateway/memory/browser 是腾讯内部包，本文档只描述 Octop 如何调用它们的公共 API，不虚构其内部实现。
* **v1.0.2b5 增量轮信任说明（2026-10-04）**：新增 24 个内容文档（15 概念 + 5 示例 + 4 信源登记）均 `status: stable`、`stale_after: 2027-10-04`，基于 v1.0.2b5（commit e473dd3c）源码逐文件取证（F-134~F-592，459 条），V 阶段经 Grep 验证关键类名、逐表计数（25 连接器、28 桥接白名单、60 router 挂载、472 HTTP+9 WS、26 权限、CLI 22 命令）与相对链接。旧 16 个文档维持 `2027-08-23` 生命周期不变；其 v0.9.25 口径（harness-* 包名、schema v7、12 步装配、22 Repo、20 CLI 命令）作为历史版本事实保留，与 v1 新口径并存，阅读时以文档标注的版本为准。

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

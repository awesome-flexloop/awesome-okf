# 实战示例

本目录包含 8 个 Octop 实战示例：前 3 个基于 v0.9.25（自托管部署、自定义 Agent、ACP 集成），后 5 个为 2026-10-04 v1.0.2b5 增量轮新增。

* [自托管部署：从安装到运行](self-hosted-setup.md) — pip 安装、octop init 初始化、SQLite/PostgreSQL 配置、octop run 启动（含 HTTPS/自签名证书）、环境变量覆盖、systemd/launchd 系统服务、备份恢复、首次登录向导。
* [创建自定义 Agent：从 CLI 到 API](custom-agent.md) — CLI/HTTP API 创建 Agent、MBTI 人格配置、系统提示词、技能包、MCP 连接器、ACP runner 委托、工作区目录结构、共享 Agent、安全审批（JWT/argon2/guardrails/HITL）。
* [ACP 集成：Zed 入站与 Runner 出站](acp-integration.md) — 配置 Octop 作为 ACP stdio 服务器接入 Zed、四个内置 runner 安装与配置、acp_runner 工具六种 action、权限处理、自定义 runner、双向集成架构、故障排查。

**v1.0.2b5 增量轮（2026-10-04）新增：**

* [插件开发：tool 插件从骨架到 UI 卡片](plugin-development.md) — 四件套目录（main.py/plugin.yaml/icon.svg/ui/index.js）、ctx.tool 注册与 config_fields、octop_ui 信封消息、seed/默认开关/legacy 兼容、安装启用与排错。
* [知识库实战：建库、入库、检索调参](knowledge-base-use.md) — 功能开关、22 入库扩展名与 14 黑名单、文档/库上限、chunk 800/overlap 120/top-k 调参、ONNX 本地 embedding、search_knowledge 与引用标记。
* [联邦桥接：把远程 Octop 专家接入本地](bridge-remote-expert.md) — 双侧配置与 Fernet、出站连接注册、握手与 5 次退避、28 白名单资源授权、bridge: 前缀代理、超时对照与 SSRF 排错。
* [组建专家团队：主持人与成员编排](expert-team-setup.md) — POST /api/teams 创建（kind="team"/team-host/member_ids≥2）、18 内置专家选员、主持人 5 工具与 45 秒空闲收尾、IM 投递与排错。
* [Docker Compose 部署：单机/Postgres/云手机三套](docker-compose-deploy.md) — 两阶段 Dockerfile 与 8088/healthcheck、基础 compose、pgvector:pg16 + init-vector.sql、mobile compose（privileged/binderfs/redroid）、升级备份与排错。

```{toctree}
:hidden:
:maxdepth: 7

acp-integration
bridge-remote-expert
custom-agent
docker-compose-deploy
expert-team-setup
knowledge-base-use
plugin-development
self-hosted-setup
```

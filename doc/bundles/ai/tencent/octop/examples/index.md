# 实战示例

本目录包含 3 个 Octop 实战示例，覆盖自托管部署、自定义 Agent 创建和 ACP 集成。

* [自托管部署：从安装到运行](self-hosted-setup.md) — pip 安装、octop init 初始化、SQLite/PostgreSQL 配置、octop run 启动（含 HTTPS/自签名证书）、环境变量覆盖、systemd/launchd 系统服务、备份恢复、首次登录向导。
* [创建自定义 Agent：从 CLI 到 API](custom-agent.md) — CLI/HTTP API 创建 Agent、MBTI 人格配置、系统提示词、技能包、MCP 连接器、ACP runner 委托、工作区目录结构、共享 Agent、安全审批（JWT/argon2/guardrails/HITL）。
* [ACP 集成：Zed 入站与 Runner 出站](acp-integration.md) — 配置 Octop 作为 ACP stdio 服务器接入 Zed、四个内置 runner 安装与配置、acp_runner 工具六种 action、权限处理、自定义 runner、双向集成架构、故障排查。

```{toctree}
:hidden:

acp-integration
custom-agent
self-hosted-setup
```

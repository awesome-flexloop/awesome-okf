---
type: Changelog
title: octop 变更日志
description: 记录文档生成与更新历史
generated: true
verified: grep
status: stable
stale_after: 2027-08-23
---

# Bundle Update Log

## 2026-08-23

* **Creation**: 建立 Octop（v0.9.25，MIT）源码 OKF 知识包脚手架（spec/concepts/examples/references 四目录），遵循 OKF v0.2 规范。
* **Add**: R阶段完成——深度阅读 `external/libs/ai/Tencent/WorkBuddy/Octop/` 源码核心模块：`src/octop/__init__.py`（版本 0.9.25）、`src/octop/config.py`（OctopConfig/DatabaseConfig/TlsConfig/BackupConfig frozen dataclass、load_config 环境变量覆盖）、`src/octop/launch.py`（run_foreground/run_foreground_blocking 组合根、TLS 双端口）、`src/octop/infra/server.py`（OctopServer、AppRuntime、start/stop/_boot_runtime/bind_control_plane、Greenfield 延迟绑定、JWT 密钥、日志轮转、Wizard 密码）、`src/octop/infra/errors.py`（ErrorCode StrEnum 83 个错误码、OctopError 异常、HTTP 状态映射、本地化）、`src/octop/infra/agents/manager.py`（AgentManager、HarnessAgent 委托、CRUD、热重载、MCP 缓存、settings stores）、`src/octop/infra/gateway/gateway.py`（Gateway、ChannelRuntimeStatus、GlobalProcessor、ChannelManager、WS/CLI Hub、IM 通道、Slash 抢占取消）、`src/octop/infra/db/pool.py`（DatabasePool Protocol、SqlitePool WAL+RLock、PostgresPool psycopg_pool）、`src/octop/infra/db/services.py`（RepoBundle 22 Repo、SharedServices DI）、`src/octop/infra/db/factory.py`（open_database、should_defer_control_plane_db）、`src/octop/infra/utils/paths.py`（PathLayout ~/.octop/）、`src/octop/api/app.py`（build_app FastAPI 工厂、50+ 路由、异常处理、SPA fallback）、`src/octop/cli/main.py`（_LazyCLI 延迟加载）、`src/octop/cli/registry.py`（COMMANDS 20 子命令）、`src/octop/cli/commands/run.py`（octop run 选项、自签名证书）、`docs/acp.md`（ACP 双向集成、4 个 runner）、`docs/cli.md`（CLI 参考、三层传输）、`pyproject.toml`（依赖版本、Python>=3.12、hatchling）、`AGENTS.md`（模块边界禁令），提取 133 条源码事实（F-001~F-133）。
* **Add**: I阶段完成——提炼 5 个核心架构洞察：I-01 Greenfield 延迟绑定（全新安装不先开 DB，HTTP 先启动等向导热绑定）、I-02 组合根独占（launch.py 是唯一同时接触 infra 与 api 的模块）、I-03 Harness 三件套委托（Octop 自身不实现 Agent 运行时，AI 能力全委托 harness-agent/gateway/memory/browser）、I-04 CLI 延迟加载+三层传输（_LazyCLI 按需 import，Offline/Embedded/External 三种执行路径）、I-05 单进程多 Agent+有界并行热重载（asyncio 单进程承载所有用户和 Agent，Semaphore(6) 控制重载并发）。
* **Add**: E阶段完成——references/ 下 6 个信源登记（server-launch/agent-manager/gateway/db-layer/cli-api/harness-stack），concepts/ 下 7 个概念文档（00-architecture/01-server-lifecycle/02-agent-runtime/03-gateway-channels/04-db-di/05-acp-protocol/06-cli-commands），examples/ 下 3 个实战示例（self-hosted-setup/custom-agent/acp-integration），加上 references/concepts/examples 三个子目录 index.md（无 frontmatter）和根 index.md（含 okf_version:"0.2"）、log.md。
* **Verify**: V阶段完成——Grep 验证 OctopServer/AgentManager/Gateway/SharedServices/RepoBundle/_LazyCLI/PathLayout/AppRuntime/ChannelRuntimeStatus 等关键类名在 src/octop/ 中存在；COMMANDS 字典包含 20 个子命令与 registry.py 一致；ACP 4 个 runner（opencode/codebuddy/claude_code/codex）与 docs/acp.md 一致；ErrorCode 枚举 83 个值。

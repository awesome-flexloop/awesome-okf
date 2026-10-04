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

## 2026-10-04

* **Update**: 信源升级——基于上游 v1.0.2b5（commit `e473dd3c4a4741618ffde1a42a3492341a189e8e`，MIT）完成多轮增量扩展，新信源 `external/dao/runtime/tencent/Octop/`，旧信源 `external/libs/ai/Tencent/WorkBuddy/Octop/` 已失效；1.0 系列品牌独立（外部包更名为 octop-harness/octop-memory/octop-gateway/octop-browser，钉扎 `>=1.0.0`，旧 harness_* 包名零命中），schema v7→v19，`_boot_runtime` 12→17 步，RepoBundle 22→25，CLI 20→22 命令。
* **Add**: R 阶段增量——五路分工采集 459 条事实 F-134~F-592（全量 F-001~F-592 共 592 条，机械校验 total=uniq=592）；G1 禁词全量清零（含旧轮 F-033/F-081/F-117 与本轮 F-146 措辞修复）。
* **Add**: I 阶段增量——10 个四元组洞察 I-06~I-15：品牌独立更名、17 步装配膨胀与不可逆服务、25 连接器三模式 MCP 网关、每库 SQLite 全表内存余弦 RAG、team host 剥权 5 工具、bridge 影子 ID+28 白名单 SSRF 联邦、history v2 内容寻址归档、插件三 API 官方仅用 tool、SSO×验证码×26 权限、异构数据面统一容灾；附增量知识地图。
* **Add**: E 阶段增量——references 4 篇（source-v1-map/api-surface/connectors-catalog/bridge-protocol），concepts 15 篇（07-connector-system 至 21-packaging-deployment），examples 5 篇（plugin-development/knowledge-base-use/bridge-remote-expert/expert-team-setup/docker-compose-deploy）；concepts/examples/references 三个子目录 index 与束根 index 同步登记（旧 16 文档内容一字不改，新旧口径分段并存）。
* **Fix**: F-138 extras 计数由「4 个」订正为 5 组（dev/browser/desktop/local-embedding/knowledge-ocr，源码为准）；F-414 BackupConfig 路径由 `infra/backup/config.py` 订正为 `src/octop/config.py`。
* **Verify**: V 阶段——24 个新文档 frontmatter 完整性与 stale_after: 2027-10-04、相对链接零 file:///、关键类名 Grep、计数断言对账（25 连接器/13 适配器、28 桥接白名单、入站扩展名 142+别名 37、60 router 挂载、472 HTTP+9 WS、26 权限、CLI 22 命令、docker 透传 18 键等）。

## 2026-08-23

* **Creation**: 建立 Octop（v0.9.25，MIT）源码 OKF 知识包脚手架（spec/concepts/examples/references 四目录），遵循 OKF v0.2 规范。
* **Add**: R阶段完成——深度阅读 `external/libs/ai/Tencent/WorkBuddy/Octop/` 源码核心模块：`src/octop/__init__.py`（版本 0.9.25）、`src/octop/config.py`（OctopConfig/DatabaseConfig/TlsConfig/BackupConfig frozen dataclass、load_config 环境变量覆盖）、`src/octop/launch.py`（run_foreground/run_foreground_blocking 组合根、TLS 双端口）、`src/octop/infra/server.py`（OctopServer、AppRuntime、start/stop/_boot_runtime/bind_control_plane、Greenfield 延迟绑定、JWT 密钥、日志轮转、Wizard 密码）、`src/octop/infra/errors.py`（ErrorCode StrEnum 83 个错误码、OctopError 异常、HTTP 状态映射、本地化）、`src/octop/infra/agents/manager.py`（AgentManager、HarnessAgent 委托、CRUD、热重载、MCP 缓存、settings stores）、`src/octop/infra/gateway/gateway.py`（Gateway、ChannelRuntimeStatus、GlobalProcessor、ChannelManager、WS/CLI Hub、IM 通道、Slash 抢占取消）、`src/octop/infra/db/pool.py`（DatabasePool Protocol、SqlitePool WAL+RLock、PostgresPool psycopg_pool）、`src/octop/infra/db/services.py`（RepoBundle 22 Repo、SharedServices DI）、`src/octop/infra/db/factory.py`（open_database、should_defer_control_plane_db）、`src/octop/infra/utils/paths.py`（PathLayout ~/.octop/）、`src/octop/api/app.py`（build_app FastAPI 工厂、50+ 路由、异常处理、SPA fallback）、`src/octop/cli/main.py`（_LazyCLI 延迟加载）、`src/octop/cli/registry.py`（COMMANDS 20 子命令）、`src/octop/cli/commands/run.py`（octop run 选项、自签名证书）、`docs/acp.md`（ACP 双向集成、4 个 runner）、`docs/cli.md`（CLI 参考、三层传输）、`pyproject.toml`（依赖版本、Python>=3.12、hatchling）、`AGENTS.md`（模块边界禁令），提取 133 条源码事实（F-001~F-133）。
* **Add**: I阶段完成——提炼 5 个核心架构洞察：I-01 Greenfield 延迟绑定（全新安装不先开 DB，HTTP 先启动等向导热绑定）、I-02 组合根独占（launch.py 是唯一同时接触 infra 与 api 的模块）、I-03 Harness 三件套委托（Octop 自身不实现 Agent 运行时，AI 能力全委托 harness-agent/gateway/memory/browser）、I-04 CLI 延迟加载+三层传输（_LazyCLI 按需 import，Offline/Embedded/External 三种执行路径）、I-05 单进程多 Agent+有界并行热重载（asyncio 单进程承载所有用户和 Agent，Semaphore(6) 控制重载并发）。
* **Add**: E阶段完成——references/ 下 6 个信源登记（server-launch/agent-manager/gateway/db-layer/cli-api/harness-stack），concepts/ 下 7 个概念文档（00-architecture/01-server-lifecycle/02-agent-runtime/03-gateway-channels/04-db-di/05-acp-protocol/06-cli-commands），examples/ 下 3 个实战示例（self-hosted-setup/custom-agent/acp-integration），加上 references/concepts/examples 三个子目录 index.md（无 frontmatter）和根 index.md（含 okf_version:"0.2"）、log.md。
* **Verify**: V阶段完成——Grep 验证 OctopServer/AgentManager/Gateway/SharedServices/RepoBundle/_LazyCLI/PathLayout/AppRuntime/ChannelRuntimeStatus 等关键类名在 src/octop/ 中存在；COMMANDS 字典包含 20 个子命令与 registry.py 一致；ACP 4 个 runner（opencode/codebuddy/claude_code/codex）与 docs/acp.md 一致；ErrorCode 枚举 83 个值。

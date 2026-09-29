---
type: Reference
title: "Harness 技术栈：外部包依赖与 PathLayout"
description: "orcakit-harness-agent/harness-gateway/harness-memory/harness-browser 外部包版本与调用点、PathLayout 文件系统布局、config.py 配置体系、AGENTS.md 模块边界禁令。"
tags: [octop, harness-agent, harness-gateway, harness-memory, harness-browser, paths, config, boundaries]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /spec/facts.md
    title: Octop 源码事实清单 F-001~F-023, F-101~F-107, F-128~F-133
---

# Harness 技术栈：外部包依赖与 PathLayout

本信源登记 Octop 所依赖的外部 harness 包、配置体系、文件系统布局和模块边界规范。

## 外部 Harness 包

Octop 的核心 AI 能力委托给四个腾讯内部/外部包（F-007）：

| 包 | 最低版本 | 职责 | Octop 调用点 |
|----|---------|------|-------------|
| `orcakit-harness-agent[all]` | >=0.9.23 | Agent 运行时（LangGraph）、HarnessAgent/HarnessAgentManager、MCP 工具加载、ACP server/client、SecurityPolicy | `infra/agents/manager.py` |
| `harness-memory` | >=0.9.7 | Agent 记忆提取与存储（SQLite 表 `agent_<id>_*`） | `infra/agents/memory_backend.py` |
| `harness-gateway` | >=0.9.3 | IM 通道管理（ChannelManager/ChannelKind/ChannelSubject）、WS/CLI channel | `infra/gateway/gateway.py` |
| `harness-browser` | >=0.7.5 | 浏览器自动化（Playwright 封装） | `api/routers/browser/` |

### harness-agent 导入点

```python
# infra/agents/manager.py
from harness_agent import HarnessAgent, HarnessAgentConfig, HarnessAgentManager
from harness_agent.security.models import SecurityPolicy
from harness_agent.mcp import aload_mcp_tools
```

Octop 通过这些公共 API 与 Agent 运行时交互（F-052、F-068），不直接访问 LangGraph 内部。

### harness-gateway 导入点

```python
# infra/gateway/gateway.py
from harness_gateway.channel import ChannelCredentialsError
from harness_gateway.channels import ChannelKind
from harness_gateway.manager import ChannelManager
from harness_gateway.models import ChannelSubject
```

来源：F-074。

### 其他关键依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| `fastapi` | >=0.110 | Web 框架 |
| `uvicorn[standard]` | >=0.27 | ASGI 服务器 |
| `pydantic` | >=2.6,<2.14 | 数据验证 |
| `langchain-core` | >=1.4.8 | LLM 抽象 |
| `click` | >=8.1 | CLI 框架 |
| `argon2-cffi` | >=23.1 | 密码哈希 |
| `pyjwt` | >=2.8 | JWT 认证 |
| `psycopg[binary]` | >=3.2 | PostgreSQL 驱动 |
| `langgraph-checkpoint-postgres` | >=2.0 | PG checkpointer |
| `mcp` | >=1.9,<2 | Model Context Protocol |
| `cryptography` | >=41 | TLS/自签名证书 |
| `acme`/`josepy` | >=5.6/>=2.2 | Let's Encrypt |
| `boto3` | >=1.40.61 | S3/COS 存储后端 |
| `playwright` | >=1.40 | 浏览器自动化 |
| `apscheduler` | >=3.10,<4 | 定时任务 |

来源：F-008~F-013。

## 配置体系（config.py）

### OctopConfig

frozen dataclass，进程级配置（F-016）：

```python
@dataclass(frozen=True)
class OctopConfig:
    bind_host: str = "127.0.0.1"
    port: int = 8088
    log_level: str = "info"
    access_token_ttl_seconds: int = 86400
    login_max_attempts: int = 5
    login_lockout_seconds: int = 900
    cors_origins: list[str] = field(default_factory=list)
    default_timezone: str = "Asia/Shanghai"
    enable_dashboard: bool = True
    enable_api_docs: bool = False
    require_setup_password: bool = True
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    database_in_file: bool = False
    tls: TlsConfig = field(default_factory=TlsConfig)
    backup: BackupConfig = field(default_factory=BackupConfig)
```

### 嵌套配置

- **DatabaseConfig**：driver（sqlite/postgresql）、sqlite_path、host、port、database、user、password、url；提供 `is_sqlite`/`is_postgresql`、`resolve_sqlite_path()`、`postgresql_conninfo()`（F-017）
- **TlsConfig**：enabled、mode、domains、cert_file、key_file、issued_at、expires_at、acme_staging、http_port（F-018）
- **BackupConfig**：auto_enabled、schedule（默认 `cron:0 4 * * *`）、retention_count（默认 7）（F-019）

### load_config 合并优先级

```
config.json 文件 → 环境变量覆盖 → 默认值
```

支持的环境变量（F-021、F-023）：
- `OCTOP_BIND_HOST`、`OCTOP_PORT`、`OCTOP_LOG_LEVEL`
- `OCTOP_DATABASE_URL`、`OCTOP_DATABASE_DRIVER`、`OCTOP_DATABASE_SQLITE_PATH`、`OCTOP_DATABASE_HOST/PORT/NAME/USER/PASSWORD`
- `OCTOP_ACCESS_TOKEN_TTL`、`OCTOP_LOGIN_MAX_ATTEMPTS`、`OCTOP_LOGIN_LOCKOUT_SECONDS`
- `OCTOP_DEFAULT_TIMEZONE`（兼容 `OCTOP_CRON_TIMEZONE`）
- `OCTOP_CORS_ORIGINS`（逗号分隔）
- `OCTOP_ENABLE_DASHBOARD`、`OCTOP_ENABLE_API_DOCS`、`OCTOP_REQUIRE_SETUP_PASSWORD`
- `OCTOP_BACKUP_AUTO_ENABLED`、`OCTOP_BACKUP_SCHEDULE`、`OCTOP_BACKUP_RETENTION_COUNT`

config.json 不存在时自动写入默认值（F-021）。

## PathLayout 文件系统布局

`PathLayout`（frozen dataclass）定义 `~/.octop/` 目录结构（F-101~F-107）：

```
~/.octop/                              # root（可通过 OCTOP_HOME 覆盖）
├── config.json                        # 进程配置
├── octop.db                           # SQLite 数据库（WAL 模式）
├── logs/
│   └── octop.log                      # 每日轮转日志
├── agents/
│   └── <agent_id>/                    # Agent 工作区
├── users/
│   └── <username>/                    # 用户目录
├── expert_market/                     # SkillHub 专家模板缓存
├── published_experts/                 # 用户发布的专家快照
├── skill-packages/                    # 全局技能包
├── knowledge/                         # 全局知识库文件
├── plugins/                           # 第三方插件
├── security/
│   └── tool_guard/
│       └── dangerous_shell_commands.yaml
├── backups/                           # 备份归档
├── ssl/                               # TLS 证书和 ACME 密钥
└── connector-cli/                     # 连接器 CLI 实例配置
    └── <kind>/<instance_key>/
```

关键路径属性：
- `PathLayout.from_env()`：从 `OCTOP_HOME` 或 `~/.octop` 解析（F-101）
- `db` → `root/octop.db`（F-102）
- `config` → `root/config.json`（F-104）
- `agent_workspace(agent_id)` → `root/agents/<agent_id>/`（F-105）
- `tool_guard_rules_file` → `root/security/tool_guard/dangerous_shell_commands.yaml`（F-107）

## 模块边界禁令

AGENTS.md §5 定义了严格的依赖方向（F-128~F-131）：

### 依赖流向

```
dashboard/ ──HTTP──► api/ ──► infra/ ──► infra/utils/, octop.config
cli/ ──► launch.py ──► api/ + infra/
```

### 硬禁令

| 禁止 | 说明 |
|------|------|
| `infra/` → `api/`、`cli/`、`launch.py` | 领域层不得感知传输层 |
| `api/` → `cli/`、`launch.py` | HTTP 层不得导入 CLI |
| `cli/` → `api/` | CLI 使用 launch.py 启动服务器，不直接导入 api |
| `infra/db/repos/` → 非 DB `infra` 包 | Repo 只做 SQL，不编排 |
| `infra/utils/` → 非 utils `infra` 包 | 工具函数保持纯净 |
| 只有 `launch.py` 同时导入 `infra/server` + `api/app` | 唯一组合根 |
| 直接编辑 `src/octop/dashboard/` | 构建产物，源码在 `dashboard/` |

### infra 子包所有权

| 子包 | 拥有 |
|------|------|
| `infra/agents/` | Agent 注册表、harness 运行时、provider store、security/acp/langfuse 设置、MBTI 人格、专家目录 |
| `infra/backend/` | 工作区存储适配器、resolver、远程探测（COS/S3） |
| `infra/connectors/` | 连接器目录、OAuth、MCP 网关、凭证加密 |
| `infra/cron/` | Cron 任务、触发器、agent 工具钩子 |
| `infra/db/` | SqlitePool、迁移、RepoBundle/SharedServices |
| `infra/gateway/` | IM 入口、threads、slash 命令、bot setup |
| `infra/setup/` | 首次运行向导、系统服务安装、TLS/Let's Encrypt |
| `infra/users/` | 用户、角色、密码哈希、UserManager |
| `infra/errors.py` | ErrorCode、OctopError |
| `infra/server.py` | OctopServer.start() 装配 |

## i18n 与时区

- 支持 locale：`zh` 和 `en`（`en` 为 fallback）（F-132）
- 服务端用户可见文本必须来自 i18n bundle，不硬编码英文
- 时区使用 `config.default_timezone`（默认 `Asia/Shanghai`），不使用浏览器本地时区

## 前端技术栈

- React 18 + TypeScript + Vite + Ant Design（F-014）
- 前端仅通过 `/api` HTTP 与后端通信，不直接导入 Python 模块
- 构建产物在 `src/octop/dashboard/`，源码在 `dashboard/`

## 相关概念

- [/concepts/00-architecture.md](../concepts/00-architecture.md)
- [/concepts/02-agent-runtime.md](../concepts/02-agent-runtime.md)
- [/concepts/03-gateway-channels.md](../concepts/03-gateway-channels.md)

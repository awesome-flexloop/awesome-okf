---
type: Example
title: "自托管部署：从安装到运行"
description: "从零开始部署 Octop 自托管 AI 助手：pip 安装、octop init 初始化、配置数据库、octop run 启动服务、systemd 服务安装。"
tags: [octop, deployment, self-hosted, setup, systemd]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: cli
    resource: /concepts/06-cli-commands.md
    title: CLI 命令体系
  - id: lifecycle
    resource: /concepts/01-server-lifecycle.md
    title: 服务器生命周期
---

# 自托管部署：从安装到运行

本示例演示如何从零开始部署一个 Octop 自托管实例。

## 环境要求

- Python 3.12+
- pip 或 uv 包管理器
- 现代浏览器（访问 Dashboard）
- 可选：PostgreSQL 12+（生产环境推荐）、外部 LLM Provider API key

## 1. 安装

```bash
pip install octop
```

或使用 uv：

```bash
uv pip install octop
```

安装后 `octop` 命令可用。验证安装：

```bash
octop --version
# octop v0.9.25
```

## 2. 初始化

```bash
octop init
```

`octop init` 执行以下操作（Offline 传输层）：

1. 创建 `~/.octop/` 目录结构
2. 生成默认 `config.json`
3. 打开数据库（默认 SQLite `~/.octop/octop.db`，WAL 模式）
4. 运行数据库迁移（当前 schema v7）
5. 生成 JWT 签名密钥（32 字节随机值，存入 `secrets` 表）
6. 创建首个管理员用户

非交互式初始化：

```bash
octop init \
  --admin-username admin \
  --admin-password 'your-secure-password' \
  --admin-display-name 'Administrator' \
  --yes
```

也可以通过环境变量传递：

```bash
export OCTOP_ADMIN_USERNAME=admin
export OCTOP_ADMIN_PASSWORD='your-secure-password'
octop init --yes
```

使用 `--force` 可在初始化前擦除现有 `~/.octop/`（危险操作）。

## 3. 启动服务

```bash
octop run
```

默认监听 `http://127.0.0.1:8088`。首次启动时：

1. OctopServer 加载 config.json 和 .env
2. 配置日志（`~/.octop/logs/octop.log`，每日轮转，保留 14 天）
3. 打开数据库并运行迁移
4. 装配 AgentManager、Gateway、CronManager、UserManager 等运行时单例
5. 启动 uvicorn ASGI 服务器
6. 打开浏览器访问 Dashboard

### 自定义绑定地址和端口

```bash
octop run --host 0.0.0.0 --port 9000
```

传入的 `--host`/`--port` 会持久化到 `~/.octop/config.json`，后续启动无需重复指定。

### 开发模式（自动重载）

```bash
octop run --reload
```

### HTTPS（自签名证书）

```bash
octop run --ssl
```

首次使用 `--ssl` 时自动生成自签名证书（RSA 2048，CN=octop-self-signed，SAN=127.0.0.1，有效期 365 天），存放于 `~/.octop/ssl/`。

生产环境建议使用 Let's Encrypt（Dashboard 中 TLS 设置或配置 TLS 段）。

## 4. 通过环境变量配置

Octop 支持通过环境变量覆盖 config.json 中的配置：

```bash
# 网络
export OCTOP_BIND_HOST=0.0.0.0
export OCTOP_PORT=8088
export OCTOP_LOG_LEVEL=info

# 数据库（PostgreSQL）
export OCTOP_DATABASE_URL=postgresql://octop:password@db.internal:5432/octop

# 或分项配置
export OCTOP_DATABASE_DRIVER=postgresql
export OCTOP_DATABASE_HOST=db.internal
export OCTOP_DATABASE_PORT=5432
export OCTOP_DATABASE_NAME=octop
export OCTOP_DATABASE_USER=octop
export OCTOP_DATABASE_PASSWORD=secret

# 安全
export OCTOP_ACCESS_TOKEN_TTL=86400
export OCTOP_LOGIN_MAX_ATTEMPTS=5
export OCTOP_LOGIN_LOCKOUT_SECONDS=900

# 时区
export OCTOP_DEFAULT_TIMEZONE=Asia/Shanghai

# CORS
export OCTOP_CORS_ORIGINS=https://app.example.com,https://admin.example.com

# 备份
export OCTOP_BACKUP_AUTO_ENABLED=true
export OCTOP_BACKUP_SCHEDULE="cron:0 4 * * *"
export OCTOP_BACKUP_RETENTION_COUNT=7

# 数据目录（默认 ~/.octop）
export OCTOP_HOME=/data/octop
```

## 5. 使用 PostgreSQL（生产推荐）

编辑 `~/.octop/config.json`：

```json
{
  "bind_host": "0.0.0.0",
  "port": 8088,
  "database": {
    "driver": "postgresql",
    "host": "db.internal",
    "port": 5432,
    "database": "octop",
    "user": "octop",
    "password": "secret"
  }
}
```

或使用 `OCTOP_DATABASE_URL`：

```bash
export OCTOP_DATABASE_URL=postgresql://octop:secret@db.internal:5432/octop
```

PostgreSQL 使用 `psycopg_pool.ConnectionPool`（min_size=1, max_size=8），支持 `langgraph-checkpoint-postgres` 作为 LangGraph checkpointer 后端。SQLite 和 PostgreSQL 共享同一 schema，迁移文件成对提供（`.sql` + `.pg.sql`）。

## 6. 系统服务安装

```bash
# Linux（systemd）
octop service start

# macOS（launchd）
octop service start
```

`octop service` 自动检测系统服务管理器：
- Linux：systemd（user 或 system scope）
- macOS：launchd

管理命令：

```bash
octop service status
octop service restart
octop service stop
```

Scope 可通过 `--scope` 或 `OCTOP_SERVICE_SCOPE` 强制指定（user vs system）。

## 7. 备份

```bash
# 创建手动备份
octop backup create

# 恢复备份
octop backup restore <backup-file.tar.gz>

# 查看自动备份状态
octop backup auto status

# 立即执行一次自动备份
octop backup auto run
```

备份包含数据库 + Agent 工作区 + config.json，归档命名：
- 手动：`octop-backup-*.tar.gz`
- 自动：`octop-auto-backup-*.tar.gz`（保留策略仅清理自动备份）

自动备份在运行中的 `octop run` 进程内调度（默认每日 04:00），配置在 config.json 的 `backup` 段。

## 8. 首次登录

1. 打开 `http://127.0.0.1:8088`
2. 使用 init 时设置的管理员账号登录
3. 进入 **Settings → Providers** 配置 LLM Provider（OpenAI、Anthropic、本地 Ollama 等）
4. 进入 **Agents** 创建第一个 Agent
5. 开始聊天

如果 `require_setup_password` 为 true（默认），首次访问会进入 setup wizard，终端会打印一次性向导密码（也写入 `~/octop-login.txt`）。

## 相关概念

- [/concepts/01-server-lifecycle.md](../concepts/01-server-lifecycle.md)
- [/concepts/04-db-di.md](../concepts/04-db-di.md)
- [/concepts/06-cli-commands.md](../concepts/06-cli-commands.md)

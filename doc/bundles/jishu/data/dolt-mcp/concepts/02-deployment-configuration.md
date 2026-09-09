---
type: Concept
title: "dolt-mcp 部署与配置"
description: "dolt-mcp 的两种传输模式（stdio/HTTP）与三类部署方式——从源码构建、原生二进制、Docker 镜像：CLI 标志、环境变量、方言选择、JWT 认证与 HTTPS 配置完整参考"
tags: [dolt-mcp, deployment, docker, cli, configuration, jwt, https]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-09" }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: dolt-mcp-source
    resource: /references/source.md
    title: dolt-mcp 源码事实登记
---

# dolt-mcp 部署与配置

> 本文覆盖 dolt-mcp 的启动参数、环境变量与部署形态。对应 [F-020~F-035、F-080~F-085](/references/source.md)。

## 两种传输模式

dolt-mcp 二选一指定运行模式（F-022）：

| 模式 | 标志 | 适用场景 |
|------|------|---------|
| **stdio** | `--stdio` | AI 助手（Claude Desktop/CLI）以子进程直接拉起，标准输入输出通信 |
| **HTTP** | `--http` | Web 应用/自定义集成；独立监听 `--mcp-port`（默认 8080），端点须为 `/mcp` |

HTTP 模式支持 HTTPS 与 JWT bearer 认证；stdio 模式不支持（进程内认证无意义）。

## 方言选择（必选其一，互斥）

| 方言 | 标志 | 后端 | 默认端口 |
|------|------|------|---------|
| Dolt（默认） | `--dolt` | MySQL 兼容版本化库 | 3306 |
| DoltgreSQL | `--doltgres` | PostgreSQL 兼容版本化库 | 5432 |
| DoltLite（内嵌） | `--doltlite` | SQLite fork 单文件 | 无（内嵌） |

三个标志互斥，同时出现即报错（F-025）；DoltLite 还要求 `--db-file` 与特殊构建（F-027/F-090）。

## 核心 CLI 标志

### 连接参数（非 DoltLite 必需）

| 标志 | 说明 |
|------|------|
| `--host` | Dolt/DoltgreSQL 服务器主机名（必填） |
| `--user` | 认证用户名（必填） |
| `--port` | 端口；缺省按方言（3306/5432） |
| `--password` | 密码；缺省读 `DOLT_PASSWORD` 环境变量 |
| `--database` | 初始数据库名 |
| `--tls` | 数据库连接 TLS：`true`/`false`/`skip-verify`/`preferred` |
| `--tls-ca` | CA 证书路径（自定义 TLS） |

兼容旧式 `--dolt-host/--dolt-port/...` 别名，新参数优先（F-021）。

### DoltLite 参数

| 标志 | 说明 |
|------|------|
| `--doltlite` | 使用内嵌 DoltLite 方言 |
| `--db-file` | 数据库文件路径（必填，不存在则创建） |
| `--commit-name` / `--commit-email` | 提交作者身份（推荐设置） |
| `--doltlite-busy-timeout` | 锁等待时间（默认 5s；0 立即失败） |

### HTTP/认证参数

| 标志 | 说明 |
|------|------|
| `--mcp-port` | HTTP 端口（默认 8080，仅 HTTP） |
| `--http-cert-file` / `--http-key-file` / `--http-ca-file` | HTTPS 证书三件套 |
| `--jwk-url` + `--jwk-claims` | JWT 认证（JWKS URL + `iss/aud/sub` claims，须同时提供） |
| `--log-level` | `debug`/`info`/`warn`/`error`（默认 info） |

> **debug + stdio 日志落盘**：stdio 模式开 debug 时，日志写入 `~/.dolt-mcp-server/logs/<时间戳>.log`，避免污染 stdout 破坏 MCP 协议（F-024）。

## 从源码构建

```bash
git clone https://github.com/dolthub/dolt-mcp
cd dolt-mcp
go build -o dolt-mcp-server ./mcp/cmd/dolt-mcp-server   # 纯 Go，可交叉编译
```

默认构建不含 DoltLite（`--doltlite` 报错）；DoltLite 支持需 cgo + `-tags "doltlite libsqlite3"` + libdoltlite，见 [DoltLite 内嵌模式](06-doltlite-mode.md)。

## 原生二进制示例

### 连 Dolt（stdio，给 Claude Desktop）

```bash
./dolt-mcp-server --stdio --dolt \
  --host 0.0.0.0 --port 3306 --user root --database mydb
```

### 连 DoltgreSQL（HTTP）

```bash
./dolt-mcp-server --http --mcp-port 8080 --doltgres \
  --host 0.0.0.0 --port 5432 --user postgres --database mydb
```

### Claude Desktop 配置（stdio）

```json
{
  "mcpServers": {
    "dolt-mcp": {
      "command": "/path/to/dolt-mcp-server",
      "args": ["--stdio", "--dolt", "--host", "0.0.0.0",
               "--port", "3306", "--user", "root", "--database", "testdb"],
      "env": { "DOLT_PASSWORD": "your_password_if_needed" }
    }
  }
}
```

### Claude CLI 连 HTTP（须带 `/mcp`）

```bash
claude mcp add --transport http dolt-mcp \
  https://your-dolt-host:8080/mcp --header "Authorization: Bearer <token>"
```

## Docker 部署

官方镜像 `dolthub/dolt-mcp`，两个变体（F-033）：`latest`（纯 Go，外接 Dolt/Doltgres）与 `<version>-doltlite`（内嵌 DoltLite）。镜像以非 root 用户 `doltmcp:1001` 运行（F-033）。

### HTTP + 外接 Dolt

```bash
docker run -d --name dolt-mcp-server -p 8080:8080 \
  -e MCP_MODE=http \
  -e DOLT_HOST=your-dolt-host -e DOLT_USER=root \
  -e DOLT_DATABASE=your_database -e DOLT_PASSWORD=your_password \
  dolthub/dolt-mcp:latest
```

### DoltLite（单文件，推荐入门）

```bash
docker run -d --name dolt-mcp-doltlite -p 8080:8080 \
  -v dolt_mcp_data:/data \
  -e MCP_MODE=http -e DOLT_DB_FILE=/data/mydb.db \
  -e DOLT_COMMIT_NAME="Your Name" -e DOLT_COMMIT_EMAIL=you@example.com \
  dolthub/dolt-mcp:latest-doltlite
```

### 关键环境变量

| 变量 | 说明 |
|------|------|
| `MCP_MODE` | `http`/`stdio`（默认 stdio） |
| `MCP_DIALECT` | `dolt`/`doltgres`/`doltlite`（默认 dolt） |
| `MCP_PORT` | HTTP 端口（默认 8080） |
| `DOLT_HOST` / `DOLT_USER` | 必填（doltlite 除外） |
| `DOLT_PORT` / `DOLT_DATABASE` / `DOLT_PASSWORD` | 可选 |
| `DOLT_DB_FILE` / `DOLT_COMMIT_NAME` / `DOLT_COMMIT_EMAIL` | DoltLite 专用 |
| `DOLTLITE_BUSY_TIMEOUT` | DoltLite 锁等待（默认 5s） |
| `DOLTLITE_CREDS_DIR` / `DOLTLITE_CREDS_KID` / `DOLTLITE_CA_FILE` | DoltLite 远程凭据 |

Docker 官方 compose 示例同时起 dolt-mcp-server 与 dolt-sql-server，并对 HTTP 做 `/health` wget healthcheck（F-034）。

## JWT 认证机制（HTTP 模式）

启用条件：`--jwk-url` 与 `--jwk-claims` **必须同时提供**，否则报错（F-023）。认证中间件逻辑（F-083~F-084）：

1. 从 `Authorization: Bearer <token>` 头取 token；否则尝试 URL query `?jwt=<token>`；
2. 两者皆无 → 401；
3. 用 JWKS URL 构建 `JWTProvider`（仅支持 `iss`/`aud`/`sub` claims 校验）；
4. `ValidateJWT(token, now)` 失败 → 401。

典型用法：

```bash
./dolt-mcp-server --http --mcp-port 8080 --dolt \
  --host dbhost --user root --database mydb \
  --jwk-url "https://your-idp/.well-known/jwks.json" \
  --jwk-claims "iss=https://your-idp,aud=dolt-mcp"
```

## HTTPS

提供证书三件套后自动启用 HTTPS：加载 X.509 密钥对、最低 TLS 1.2、可选客户端 CA（`VerifyClientCertIfGiven`），内部 `ListenAndServeTLS("","")`（F-082）。HTTP/HTTPS 服务均实现优雅关闭（信号或 context 取消 → 10s 内 Shutdown，F-081）。

## 部署决策速查

| 需求 | 推荐路径 |
|------|---------|
| Claude Desktop/CLI 直连 | 原生二进制 stdio |
| 局域网多客户端 / Web 集成 | Docker HTTP + 可选 JWT |
| 没有现成 Dolt 服务器、想最快体验 | `-doltlite` 镜像或预编译 DoltLite 二进制 |
| 生产高可用 | Docker compose：dolt-mcp + dolt-sql-server 双容器 + healthcheck |

## 相关概念

* [架构分层](/concepts/01-architecture.md)
* [工具全景](/concepts/03-tools-overview.md)
* [DoltLite 内嵌模式](/concepts/06-doltlite-mode.md)
* 实操见 [examples/00-query-and-exec](../examples/00-query-and-exec.md)

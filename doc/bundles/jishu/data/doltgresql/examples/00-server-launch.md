---
okf_version: "0.2"
type: example
id: "examples-server-launch"
title: "启动 DoltgreSQL 服务器"
x-toml-ref: "../../../../../../../../.meta/toml/projects/awesome-okf-xs/doc/bundles/jishu/data/doltgresql/examples/00-server-launch.toml"
description: "RunOnDisk（持久化）与 RunInMemory（临时测试）两种启动模式的环境变量配置、TLS 设置与连接字符串示例"
tags: [doltgresql, example]
generated:
  at: "2026-09-09"
verified:
  at: "2026-09-09"
  by: process:seven-concepts-v
  status: stable
stale_after: "2027-03-09"
sources:
  - path: "server/server.go"
    type: source-code
    title: "server/server.go"
    distance: 1
  - path: "server/listener.go"
    type: source-code
    title: "server/listener.go"
    distance: 1
  - id: server-source
    resource: /references/source.md
    title: "DoltgreSQL 源码事实登记"
---
# 启动 DoltgreSQL 服务器

> 本文档提供 DoltgreSQL 服务器的两种启动模式及连接方式，覆盖环境变量、TLS 配置与客户端连接字符串。

---

## 示例 1：磁盘模式启动（持久化存储）

### 命令行启动

```bash
# 基本启动：默认监听 localhost:5432，数据库名使用 DOLTGRES_DB 环境变量
DOLTGRES_DB=mydb doltgresql

# 指定端口和地址
DOLTGRES_DB=mydb PGPORT=5433 doltgresql --host 0.0.0.0 --port 5433
```

### 源码锚点

| 步骤 | 源码位置 | 说明 |
|------|---------|------|
| 主入口 | [server/server.go L200](../../../../../external/dao/action/DoltHub/doltgresql/server/server.go) | `RunOnDisk()` 函数，持久化模式入口 |
| 数据库名 | [server/server.go L335](../../../../../external/dao/action/DoltHub/doltgresql/server/server.go) | `DefaultDbNameEnvVar = "DOLTGRES_DB"` 环境变量覆盖默认库名 |
| 用户名常量 | [server/server.go L10](../../../../../external/dao/action/DoltHub/doltgresql/server/server.go) | `DefUserName = "postres"`（注意拼写，为历史原因保留） |
| Hook 注册 | [core/init.go L10](../../../../../external/dao/action/DoltHub/doltgresql/core/init.go) | `Init()` 注册 6 个 Doltdb hook，初始化存储内核 |
| 配置加载 | [core/context.go L50](../../../../../external/dao/action/DoltHub/doltgresql/core/context.go) | `syntheticRoot` 创建虚拟 RootValue，关联到磁盘目录 |

### 产出物

执行后在当前目录（或 `DOLTGRES_REPO` 指定的路径）生成 `.doltgresql/` 目录：

```
.mydb.doltgresql/
├── config.json         # 用户配置（name/email/password）
├── remotes.db          # 远程仓库列表
├── heads/              # 分支引用
│   ├── main
│   └── feature/pg-test
└── ...
```

### 连接客户端

```bash
# psql 连接
psql "host=127.0.0.1 port=5432 dbname=mydb user=postres"

# Go/Python 等驱动连接
# PostgreSQL URI: postgresql://postres@localhost:5432/mydb
```

---

## 示例 2：内存模式启动（测试/临时使用）

### 命令行启动

```bash
# 内存模式：所有数据存在内存中，进程退出后丢失
doltgresql --in-memory
```

### 源码锚点

| 步骤 | 源码位置 | 说明 |
|------|---------|------|
| 内存入口 | [server/server.go L250](../../../../../external/dao/action/DoltHub/doltgresql/server/server.go) | `RunInMemory()` 函数，临时模式入口 |
| 虚拟 RootValue | [core/context.go L80](../../../../../external/dao/action/DoltHub/doltgresql/core/context.go) | `syntheticRoot` 不关联真实数据库，仅用于内存操作 |
| 资源清理 | [core/context.go L100](../../../../../external/dao/action/DoltHub/doltgresql/core/context.go) | `CloseContextRootFinalizer()` 在上下文关闭时清理 RootValue |

### 适用场景

```bash
# 单元测试：快速启动/关闭
go test ./... -run TestPgCatalog

# CI 环境：无需持久化数据
docker run --rm doltgresql:latest doltgresql --in-memory

# 临时探索：数据不保留
doltgresql --in-memory
```

---

## 示例 3：TLS 加密连接

### 服务器配置

```bash
# 指定 TLS 证书和密钥
doltgresql \
  --cert /path/to/server.crt \
  --key /path/to/server.key \
  --require-ssl

# 或通过环境变量
DOLTGRES_CERT=/path/to/server.crt \
DOLTGRES_KEY=/path/to/server.key \
DOLTGRES_REQUIRE_SSL=true \
doltgresql
```

### 源码锚点

| 步骤 | 源码位置 | 说明 |
|------|---------|------|
| TLS 选项 | [server/listener.go L30](../../../../../external/dao/action/DoltHub/doltgresql/server/listener.go) | `WithCertificate()` 选项注入 TLS 证书 |
| 监听封装 | [server/listener.go L50](../../../../../external/dao/action/DoltHub/doltgresql/server/listener.go) | `Listener` struct 封装 `net.Listener` + `mysql.ListenerConfig`（F-088） |
| 超时配置 | [server/listener.go L70](../../../../../external/dao/action/DoltHub/doltgresql/server/listener.go) | 连接级读/写超时，每个连接独立 goroutine（F-089） |

### 客户端连接（要求 SSL）

```bash
psql "host=127.0.0.1 port=5432 dbname=mydb user=postres sslmode=require"
```

---

## 示例 4：常用环境变量

| 环境变量 | 默认值 | 说明 | 对应 F 编号 |
|---------|--------|------|------------|
| `DOLTGRES_DB` | `"doltgres"` | 默认数据库名 | F-009、F-100 |
| `PGHOST` | `"localhost"` | 监听地址 | — |
| `PGPORT` | `5432` | 监听端口 | — |
| `PGUSER` | `"postres"` | 默认用户名 | F-008、F-099 |
| `DOLTGRES_REPO` | 当前目录 | 数据库仓库路径（磁盘模式） | — |
| `DOLTGRES_REQUIRE_SSL` | `"false"` | 是否强制 SSL 连接 | — |
| `DOLTGRES_EXTERNAL_DISABLE_USERS` | `true` | 禁用外部用户管理 | F-011 |
| `DOLTGRES_USE_SEARCH_PATH` | `true` | 启用 PostgreSQL search_path | F-012 |

### 完整配置示例

```bash
export DOLTGRES_DB=production_db
export DOLTGRES_REPO=/data/doltgresql
export PGPORT=5432
export PGHOST=0.0.0.0
export DOLTGRES_EXTERNAL_DISABLE_USERS=true
export DOLTGRES_USE_SEARCH_PATH=true

doltgresql
```

---

## 示例 5：连接字符串汇总

```
# 基础连接（磁盘模式，默认端口）
postgresql://postres@localhost:5432/mydb

# 指定端口
postgresql://postres@localhost:5433/mydb

# SSL 连接
postgresql://postres@localhost:5432/mydb?sslmode=require

# 指定 search_path
postgresql://postres@localhost:5432/mydb?search_path=public,pg_catalog

# 内存模式连接（测试用）
postgresql://postres@localhost:5432/doltgres
```

---

## 相关概念

* [三层架构与数据流](/concepts/01-architecture.md) — Listener/Handler 接口与启动模式
* [RootValue 扩展与 RootObject 集合](/concepts/02-rootvalue-and-collections.md) — syntheticRoot 与磁盘持久化

> **注意**：当前环境未安装 `doltgresql` 二进制，本文档以源码锚点形式呈现，供查阅实现细节。实际运行时请确保 Go 1.26.2+ 已安装，并从源码编译（`go build ./cmd/doltgresql`）。

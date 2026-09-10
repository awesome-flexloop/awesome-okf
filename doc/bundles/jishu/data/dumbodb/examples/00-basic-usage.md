---
type: Example
title: 基本用法：Docker 启动与 mongosh 连接
description: "基于 README 与源码的完整使用路径：Docker 部署、mongosh 连接、自定义 dumbo 命令、分支查询。F-001、F-023、F-024。"
tags: [dumbodb, dolt, example, getting-started]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-10" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10" }
status: stable
stale_after: "2027-03-31"
sources:
  - id: dumbodb-repo
    resource: https://github.com/dolthub/dumbodb
    title: dolthub/dumbodb（官方仓库）
  - id: dumbodb-local
    resource: "本地克隆（tag v0.6.3，commit 7b226dac4ef1fe10ca90818a446a7cec6b458cd3）"
---

# 基本用法：Docker 启动与 mongosh 连接

> **对应 F 编号**：F-001、F-023、F-024

## Docker 快速启动

```bash
# 创建数据目录
mkdir -p ./dumbodb-data

# 启动容器
docker run -d \
  --name dumbodb \
  -p 27017:27017 \
  -v $(pwd)/dumbodb-data:/var/lib/dumbodb \
  dolthub/dumbodb:latest

# 验证运行
docker ps | grep dumbodb
```

## 连接与基本操作

```bash
# 使用 mongosh 连接
mongosh "mongodb://localhost:27017/mydb"
```

```javascript
// 插入文档
db.users.insertOne({ name: "Alice", age: 30, email: "alice@example.com" })
db.users.insertOne({ name: "Bob", age: 25, email: "bob@example.com" })

// 查询文档
db.users.find({})
db.users.findOne({ email: "alice@example.com" })

// 创建索引
db.users.createIndex({ email: 1 }, { unique: true })

// 更新文档
db.users.updateOne({ name: "Alice" }, { $set: { age: 31 } })

// 删除文档
db.users.deleteOne({ name: "Bob" })
```

## 分支查询（rootish 系统）

```javascript
// 当前在 main 分支工作
db.users.insertOne({ name: "Charlie", email: "charlie@example.com" })

// 创建分支
db.adminCommand({ dumboBranch: 1, action: "add", name: "feature/login" })

// 切换到 feature/login 分支查询
// （在 mongosh 中通过连接 URI 指定 rootish）
// mongosh "mongodb://localhost:27017/mydb@feature/login"
```

```bash
# 在另一个终端连接到 feature 分支
mongosh "mongodb://localhost:27017/mydb@feature/login"
```

## 版本控制操作（custom commands）

```javascript
// 查看工作集状态
db.adminCommand({ dumboStatus: 1 })

// 提交当前变更
db.adminCommand({
    dumboCommit: 1,
    branch: "main",
    message: "add charlie",
    author: "Alice <alice@example.com>"
})

// 查看提交历史
db.adminCommand({ dumboLog: 1, limit: 10 })

// 查看两个版本之间的差异
db.adminCommand({
    dumboDiff: 1,
    from: "abc1234",
    to: "HEAD"
})

// 创建标签
db.adminCommand({
    dumboTag: 1,
    name: "v1.0",
    hash: "HEAD",
    message: "release v1.0"
})

// 垃圾回收
db.adminCommand({ dumboGC: 1, mode: "default" })
```

## 使用 dolt 前缀别名

所有 `dumbo*` 命令也支持 `dolt*` 前缀：

```javascript
// 等价于 dumboCommit
db.adminCommand({ doltCommit: 1, message: "same thing" })

// 等价于 dumboBranch
db.adminCommand({ doltBranch: 1, action: "list" })
```

## 限制说明（F-023）

以下 MongoDB 功能**不支持**：

| 功能 | 状态 | 说明 |
|------|------|------|
| Replica Sets | ❌ | 单节点部署 |
| Sharding | ❌ | 单节点部署 |
| Capped Collections | ❌ | Dolt 无固定大小集合概念 |
| TTL Indexes | ❌ | expireAfterSeconds 会被拒绝 |
| admin 数据库 | ⚠️ | 未达完整 MongoDB parity |
| Atlas 专有功能 | ❌ | 不支持 |

系统数据库 `config` 和 `local` 被硬拒绝。

## 二进制启动（非 Docker）

```bash
# 下载二进制并启动
./dumbodb --data-dir /path/to/data

# 连接
mongosh "mongodb://localhost:27017/mydb"
```

## 运行方式

```bash
# 1. 启动 DumboDB（Docker 方式）
docker run -d --name dumbodb -p 27017:27017 \
  -v $(pwd)/dumbodb-data:/var/lib/dumbodb \
  dolthub/dumbodb:latest

# 2. 连接并操作
mongosh "mongodb://localhost:27017/mydb"
> db.users.insertOne({ name: "Test" })
> db.adminCommand({ dumboCommit: 1, message: "initial" })

# 3. 在另一个分支工作
mongosh "mongodb://localhost:27017/mydb@feature/x"
> db.users.insertOne({ name: "Feature User" })
> db.adminCommand({ dumboCommit: 1, message: "feature work" })

# 4. 合并回 main（使用 dumboMerge）
mongosh "mongodb://localhost:27017/mydb@main"
> db.adminCommand({ dumboMerge: 1, from: "feature/x" })
```

---
type: Concept
title: Rootish 编码系统
description: "dumbodb dbname@rootish 编码机制：@ 分隔符、resolveAM() AccessMethod 解析、percent-decoding、read-your-own-writes 保证。F-011~F-016。"
tags: [dumbodb, rootish, dolt, versioning]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-10" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10" }
status: stable
stale_after: "2027-03-31"
sources:
  - id: dumbodb-repo
    resource: https://github.com/dolthub/dumbodb
    title: dolthub/dumbodb
  - id: dumbodb-local
    resource: "本地克隆（tag v0.6.3，commit 7b226dac4ef1fe10ca90818a446a7cec6b458cd3）"
---

# Rootish 编码系统

> **对应 F 编号**：F-011 ~ F-016

## 编码格式

dumbodb 使用 `dbname@rootish` 格式把 Git 引用嵌入数据库命名空间：

```
mydb@main            → 查询 mydb 数据库的 main 分支（working set）
mydb@feature/foo     → 查询 feature/foo 分支
mydb@abc1234         → 查询指定 commit hash
mydb@v1.0            → 查询标签 v1.0
mydb@main~2          → 查询 main 分支的第 2 个祖先
feature%2Ffoo@dev    → percent-decoded：数据库名 "feature/foo"，rootish "dev"
```

其中 `@` 是 `DBRootishSep` 常量分隔符。

## 名称限制（F-016）

| 参数 | 最大长度 | 说明 |
|------|---------|------|
| database name | 128 bytes | MongoDB 标准限制 63 bytes，dumbodb 更宽松 |
| rootish | 512 bytes | 支持长 commit hash 和复杂表达式 |

**全-digit 后缀不被视为 rootish**：如 `mydb@12345` 中的 `12345` 被当作普通数据库名的一部分，不进行 rootish 解析——这防止了误判。

## resolveAM() 解析逻辑（F-012~F-014）

`resolveAM()` 是核心解析函数，将 rootish 字符串转换为 AccessMethod 树：

```mermaid
flowchart TD
    A["resolveAM(rootish)"] --> B{rootish == "main"?}
    B -->|是| C["working-set AM<br/>（默认工作集）"]
    B -->|否| D{isReadOnly?}
    D -->|是| E["amFromRootish<br/>（commit/tag/哈希）"]
    D -->|否| F{"以 'refs/tags/' 开头?"}
    F -->|是| G["GetDataset('refs/tags/<tag>')<br/>→ tag AM"]
    F -->|否| H["txnVisibleWS<br/>→ loadBranchWS<br/>→ amFromWorkingRoot"]
    H --> I["read-your-own-writes<br/>保证"]
```

详细规则：

| rootish 形式 | AccessMethod | 说明 |
|-------------|-------------|------|
| `main` | working-set AM | 默认分支，直接读写 |
| commit hash（如 `abc1234`） | `amFromRootish` | 只读，跳转到指定 commit |
| `refs/tags/v1.0` | `GetDataset("refs/tags/v1.0")` | 标签只读视图 |
| 其他分支名 | `txnVisibleWS` → `loadBranchWS` → `amFromWorkingRoot` | 可读写，支持 read-your-own-writes |

## percent-decoding（F-013）

rootish 支持 percent-decoding，使含特殊字符的分支名可以安全编码：

```
输入：feature%2Ffoo
解码后：feature/foo
```

这在 MongoDB URI 场景中尤其重要，因为 `/` 在 URI 路径中有特殊含义，需要 percent-encode 为 `%2F`。

## txnVisibleWS 与 read-your-own-writes（F-015）

`txnVisibleWS` 是 dumbodb 保证 read-your-own-writes 的关键机制：

```
Session 写入 → 写入 session 本地 working set（dirty）
Session 读取 → 先检查 session dirty？
                ├─ 是 → 使用 session WS（看到自己写的）
                └─ 否 → 使用当前 txn 可见 WS（看其他会话提交的）
```

这保证了：在同一 session 内写入的数据，立即对该 session 可见，即使尚未 commit 到分支。

## 系统数据库限制（F-023）

以下系统数据库名被硬拒绝：
- `config`：MongoDB 内部配置数据库
- `local`：MongoDB 内部本地数据库

这些保留名防止 dumbodb 与 MongoDB 内部机制冲突。

## 使用示例

```bash
# 连接 main 分支（默认）
mongosh "mongodb://localhost:27017/mydb"

# 连接 feature 分支
mongosh "mongodb://localhost:27017/mydb@feature/login"

# 连接指定 commit
mongosh "mongodb://localhost:27017/mydb@abc1234def5678"

# 连接含斜杠的分支（需 percent-encode）
mongosh "mongodb://localhost:27017/mydb@feature%2Flogin"
```

## 学习路径

继续阅读：
* [BSON 存储](03-bson-storage.md) — 解析后的 Database 如何映射到 Collection
* [版本化操作](04-versioning-ops.md) — 如何 commit/branch/merge 这些 rootish 引用

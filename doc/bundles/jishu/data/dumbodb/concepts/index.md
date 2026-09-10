---
type: ConceptIndex
title: 概念索引
description: "dumbodb 概念文档索引"
tags: [dumbodb, concepts]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-10" }
status: stable
sources:
  - id: dumbodb-repo
    resource: https://github.com/dolthub/dumbodb
    title: dolthub/dumbodb
---

# 概念索引（Concepts）

本目录收录 dumbodb（DumboDB）源码深度解读的 5 篇概念文档，按"认识→架构→rootish编码→BSON存储→版本化操作"递进。

## 概念列表

| 序号 | 文档 | 核心内容 | 对应 F 编号 |
|------|------|---------|------------|
| 00 | [DumboDB 概述](00-overview.md) | 产品定位、MongoDB wire 协议兼容、driver vs dumbodb 两条路径对比 | F-001~F-005 |
| 01 | [架构分层](01-architecture.md) | Backend→Database→Collection 三层接口、BackendContract wrapper、设计原则 | F-003~F-008 |
| 02 | [Rootish 编码系统](02-rootish-system.md) | `dbname@rootish` 格式、resolveAM() AccessMethod 解析、percent-decoding | F-011~F-016 |
| 03 | [BSON 存储与 prolly tree 适配](03-bson-storage.md) | bsonFormatVersion 0x01、docToBSON/bsonToDoc、prolly.Map 映射、key 排序规则 | F-017~F-021 |
| 04 | [版本化操作与冲突模型](04-versioning-ops.md) | VersioningBackend 40+ 方法、documentEdit/uniqueKeyCollision 冲突类型 | F-022~F-024 |

## 阅读路径建议

```
00-overview（认识产品全貌）
    ↓
01-architecture（理解三层接口与后端抽象）
    ↓
02-rootish-system（学会 dbname@rootish 编码与分支查询）
    ↓
03-bson-storage（理解 BSON↔prolly.Map 存储适配）
    ↓
04-versioning-ops（深入版本化操作与冲突模型）
```

## 概念依赖关系

```
00-overview
├── 01-architecture
│   ├── 02-rootish-system
│   ├── 03-bson-storage
│   └── 04-versioning-ops
```

```{toctree}
:hidden:
:maxdepth: 2

00-overview
01-architecture
02-rootish-system
03-bson-storage
04-versioning-ops
```

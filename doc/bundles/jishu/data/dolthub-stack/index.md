---
okf_version: "0.2"
type: bundle-index
title: "DoltHub SQL 引擎栈 — vitess / go-mysql-server / doltlite-android"
description: "DoltHub 维护的三层 SQL 引擎栈知识包：vitess SQL 解析器（Yacc 生成 LL(1) 解析器，DoltHub fork 扩展 DDL/存储过程/触发器）→ go-mysql-server MySQL 兼容执行引擎（Node/Expression/Catalog 三大接口，72 条分析规则，130+ 计划节点）→ doltlite-android Android JNA 绑定层（SQLite + Dolt 版本控制）"
tags:
  - dolt
  - vitess
  - go-mysql-server
  - doltlite
  - sql-parser
  - sql-engine
  - android
  - jna
  - kotlin
  - mysql
  - database
generated:
  at: "2026-09-09"
verified:
  at: "2026-09-09"
  by: process:seven-concepts-v
  status: stable
  noted: "2026-09-09 基于 DoltHub vitess (vitess-parent-3.0.0) / go-mysql-server (v0.20.0) / doltlite-android (v0.11.21) 源码生成，R→I→E→V 四阶段完成，86 条事实登记，4 个概念文档，3 个示例文档"
stale_after: "2027-03-09"
sources:
  - url: "https://github.com/dolthub/vitess"
    type: official
    title: "dolthub/vitess — GitHub (DoltHub fork)"
    distance: 1
  - url: "https://github.com/dolthub/go-mysql-server"
    type: official
    title: "dolthub/go-mysql-server — GitHub"
    distance: 1
  - url: "https://github.com/dolthub/doltlite-android"
    type: official
    title: "dolthub/doltlite-android — GitHub"
    distance: 1
---

# DoltHub SQL 引擎栈 知识包

## 概述

DoltHub SQL 引擎栈由三个核心仓库组成，形成从 SQL 语法解析到执行引擎再到移动端绑定的完整技术栈：

- **vitess (DoltHub fork)**：MySQL 兼容 SQL 语法解析器，基于 Yacc 生成 LL(1) 解析器，DoltHub 在其基础上扩展了 DDL/存储过程/触发器支持
- **go-mysql-server**：数据源无关的 MySQL 兼容 SQL 执行引擎，依赖 vitess 作为解析器，提供 Node/Expression/Catalog 三大核心接口和 72 条分析规则
- **doltlite-android**：Android 端 JNA 绑定层，将 SQLite + Dolt 版本控制封装为 Kotlin API，通过 `dolt_*` SQL 函数暴露版本控制功能

## Bundle 结构

```
dolthub-stack/
├── index.md                          # 本文件（Bundle 根索引）
├── concepts/                         # 核心概念文档
│   ├── 00-overview.md                # 三层架构概览
│   ├── 01-parser-architecture.md     # Yacc 生成式 SQL 解析器
│   ├── 02-sql-engine-architecture.md # Interface 驱动的计划树执行
│   └── 03-android-binding.md         # Android JNA 绑定层设计
├── examples/                         # 实战教程
│   ├── 00-go-mysql-server-basics.md  # go-mysql-server 基础使用
│   ├── 01-doltlite-android-basics.md # doltlite-android 移动端使用
│   └── 02-vitess-parser-basics.md    # vitess SQL 解析器使用
└── references/                       # 参考材料
    └── source.md                     # 源码事实登记 (F-001~F-086)
```

## 知识地图

### 概念层（Constituents）

- [00-overview](./concepts/00-overview.md) — 三层架构：vitess 解析器 → go-mysql-server 引擎 → doltlite-android 绑定
- [01-parser-architecture](./concepts/01-parser-architecture.md) — Yacc 生成式 SQL 解析器：sql.y → sql.go，AST 节点体系，Parser pooling
- [02-sql-engine-architecture](./concepts/02-sql-engine-architecture.md) — Interface 驱动计划树：Node/Expression/Catalog 接口，72 条分析规则，RowIter 执行
- [03-android-binding](./concepts/03-android-binding.md) — Android JNA 绑定：CDoltlite 接口映射，Doltlite 高层 API，dolt_* 函数调用

### 示例层（Examples）

- [00-go-mysql-server-basics](./examples/00-go-mysql-server-basics.md) — SQL 解析、内存数据库、自定义 Catalog、MySQL 服务器、时间旅行查询
- [01-doltlite-android-basics](./examples/01-doltlite-android-basics.md) — 依赖配置、初始化、CRUD、Dolt 版本控制操作、错误处理
- [02-vitess-parser-basics](./examples/02-vitess-parser-basics.md) — 基础解析、DDL 解析、查询标准化、参数化查询、AST 遍历重写

### 参考层（References）

- [source](./references/source.md) — 86 条源码事实登记（F-001~F-086），涵盖三个仓库的源码结构、接口定义与依赖关系

## 关键洞察

1. **三层解耦架构**：SQL 解析（vitess）→ 引擎执行（go-mysql-server）→ 移动端绑定（doltlite-android），每层可独立演进
2. **Interface 驱动设计**：`Node`/`Expression`/`Catalog` 三个核心接口使引擎与数据源完全解耦，支持自定义后端
3. **Yacc 生成解析器**：vitess 使用 goyacc 从 sql.y 生成 LL(1) 解析器，Parser pooling 提升并发性能
4. **DoltHub Fork 扩展**：在 AST 层面添加了 DDL/存储过程/触发器支持，剪枝了 90% 非核心代码
5. **dolt_* SQL 函数**：Dolt 版本控制功能通过 SQLite 扩展函数暴露，而非直接 JNI/JNA 调用，保持 API 简洁

## 信源信息

- **信源距离**: ① 本地源码目录（`external/dao/action/DoltHub/`）
- **固定版本**:
  - vitess: `vitess-parent-3.0.0`
  - go-mysql-server: `v0.20.0`
  - doltlite-android: `v0.11.21`
- **仓库地址**: `external/dao/action/DoltHub/{vitess, go-mysql-server, doltlite-android}`

```{toctree}
:maxdepth: 1

concepts/00-overview
concepts/01-parser-architecture
concepts/02-sql-engine-architecture
concepts/03-android-binding
examples/00-go-mysql-server-basics
examples/01-doltlite-android-basics
examples/02-vitess-parser-basics
references/source
```

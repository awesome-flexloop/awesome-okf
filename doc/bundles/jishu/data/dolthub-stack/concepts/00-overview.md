---
type: concept
title: DoltHub SQL 引擎栈概览
description: "DoltHub 维护的三层 SQL 引擎栈：vitess SQL 解析器 → go-mysql-server 执行引擎 → doltlite-android 移动端绑定；三者协同支持 MySQL 兼容 SQL 查询与 Dolt 版本控制"
tags: [dolt, sql-engine, architecture, vitess, go-mysql-server, doltlite]
status: stable
stale_after: 2027-03-09
generated:
  by: insight_agent/agnes-2.5-flash
  at: 2026-09-09T15:30:00Z
verified:
  at: "2026-09-09"
  by: process:seven-concepts-v
  status: verified
  noted: "基于 facts.md F-069~F-085 验证，三层架构与依赖关系确认"
sources:
  - id: source-1
    resource: d:\spaces\SpecWeave\external\dao\action\DoltHub\vitess
    title: vitess (DoltHub fork)
  - id: source-2
    resource: d:\spaces\SpecWeave\external\dao\action\DoltHub\go-mysql-server
    title: go-mysql-server
  - id: source-3
    resource: d:\spaces\SpecWeave\external\dao\action\DoltHub\doltlite-android
    title: doltlite-android
---

# DoltHub SQL 引擎栈概览

## 核心定义

DoltHub SQL 引擎栈是由 Dolthub, Inc. 维护的三个独立仓库组成的分层架构，从底层 SQL 语法解析到上层移动端绑定，覆盖服务器端和移动端两种部署场景。

## 三层架构

```
┌─────────────────────────────────────────────────────────┐
│  第 3 层：doltlite-android                               │
│  语言: Kotlin / JNA                                     │
│  职责: Android 移动端 SQLite + Dolt 版本控制绑定         │
│  产物: com.dolthub:doltlite-android:0.11.20 (.aar)      │
│  入口: Doltlite.kt (execute/query/doltCommit/doltBranch) │
└────────────────────────┬────────────────────────────────┘
                         │ 通过 dolt_* SQL 函数调用
┌────────────────────────▼────────────────────────────────┐
│  第 2 层：go-mysql-server                                │
│  语言: Go                                               │
│  职责: MySQL 兼容 SQL 执行引擎（内存后端）               │
│  入口: server/ (MySQL协议) → analyzer/ (分析) → plan/ (执行) │
│  依赖: github.com/dolthub/vitess (SQL 解析)              │
└────────────────────────┬────────────────────────────────┘
                         │ 通过 vitess sqlparser
┌────────────────────────▼────────────────────────────────┐
│  第 1 层：vitess (DoltHub fork)                          │
│  语言: Go                                               │
│  职责: MySQL 兼容 SQL 语法解析器                         │
│  入口: go/vt/sqlparser/ (sql.go/ast.go/token.go)        │
│  生成方式: goyacc -o sql.go sql.y                       │
└─────────────────────────────────────────────────────────┘
```

## 数据流

1. **客户端发送 SQL** → `server/` 接收 MySQL 协议包
2. **SQL 解析** → `vitess sqlparser.Parse()` → `Statement` AST
3. **语义分析** → `analyzer.Analyze()` → 72 条规则应用 → `sql.Node` 计划树
4. **计划执行** → `NodeExecBuilder.Build()` → `RowIter` 行迭代器
5. **结果返回** → MySQL 协议包 → 客户端

## 关键设计决策

- **SQL 解析与执行分离**：`go-mysql-server` 不自行实现 SQL 解析，依赖 `vitess` fork
- **Interface 驱动架构**：`Node`、`Expression`、`Catalog` 均为 interface，便于替换后端
- **不可变计划节点**：`WithChildren` 模式确保分析过程中不修改原节点
- **时间旅行支持**：`Catalog.TableAsOf()` 支持历史版本查询（Dolt 核心能力）
- **内存后端限制**：`memory/` 后端非线程安全、无事务，仅用于测试和嵌入式场景

## 信源信息

- **信源距离**: ① 源码目录（本地克隆）
- **固定版本**: vitess `vitess-parent-3.0.0` / go-mysql-server `v0.20.0` / doltlite-android `v0.11.21`
- **仓库地址**: `external/dao/action/DoltHub/{vitess,go-mysql-server,doltlite-android}`

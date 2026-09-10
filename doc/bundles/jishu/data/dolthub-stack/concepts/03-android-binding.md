---
type: concept
title: Android JNA 绑定层设计
description: "doltlite-android 通过 JNA 将 libdoltlite.so（SQLite + Dolt 扩展）封装为 Kotlin API；提供 execute/query/doltCommit/doltBranch 等高层方法；Dolt 功能通过 dolt_* SQL 函数暴露"
tags: [android, jna, kotlin, sqlite, dolt, mobile, native-binding]
status: stable
stale_after: 2027-03-09
generated:
  by: insight_agent/agnes-2.5-flash
  at: 2026-09-09T15:30:00Z
verified:
  at: "2026-09-09"
  by: process:seven-concepts-v
  status: verified
  noted: "基于 facts.md F-001~F-025 验证，JNA binding 接口确认"
sources:
  - id: doltlite-android
    resource: d:\spaces\SpecWeave\external\dao\action\DoltHub\doltlite-android
    title: doltlite-android Android JNA binding
---

# Android JNA 绑定层设计

## 架构概述

`doltlite-android` 是 DoltHub 官方维护的 Android 端 Dolt 数据库绑定库。它通过 JNA（Java Native Access）将 native 库 `libdoltlite.so`（SQLite + Dolt 版本控制扩展）封装为 Kotlin API，使 Android 开发者能够在移动端使用 SQLite 兼容的 SQL 语法访问 Dolt 版本化数据库。

## JNA Native Binding

`CDoltlite` 接口（继承 JNA `Library`）声明了 SQLite C API 的原生方法映射：

```kotlin
internal interface CDoltlite : Library {
    fun sqlite3_open_v2(filename: CPointer<ByteVar>?, db: CPointerPointer<SQLite3Var>?, flags: Int, zVmConfig: CPointer<ByteVar>?): Int
    fun sqlite3_close_v2(db: CPointer<SQLite3>?): Int
    fun sqlite3_exec(db: CPointer<SQLite3>?, sql: CPointer<ByteVar>?, callback: CPointer<CallbackVar>?, arg: CPointer<CallbackVar>?, errMsg: CPointerPointer<ByteVar>?): Int
    fun sqlite3_prepare_v2(db: CPointer<SQLite3>?, sql: CPointer<ByteVar>?, nByte: Int, stmt: CPointerPointer<StmtVar>?, tail: CPointerPointer<ByteVar>?): Int
    fun sqlite3_step(stmt: CPointer<Stmt>?): Int
    fun sqlite3_finalize(stmt: CPointer<Stmt>?): Int
    fun sqlite3_column_count(stmt: CPointer<Stmt>?): Int
    fun sqlite3_column_type(stmt: CPointer<Stmt>?, iCol: Int): Int
    fun sqlite3_column_int(stmt: CPointer<Stmt>?, iCol: Int): Int
    fun sqlite3_column_double(stmt: CPointer<Stmt>?, iCol: Int): Double
    fun sqlite3_column_text(stmt: CPointer<Stmt>?, iCol: Int): CPointer<ByteVar>?
    // bind 系列方法...
}
```

JNA 通过 `Native.load("doltlite", CDoltlite::class.java)` 加载 native 库，自动完成 C 函数到 Kotlin 接口的映射。

## 高层 Kotlin API

`Doltlite` 类提供面向开发者的简化 API：

| 方法 | 签名 | 功能 |
|---|---|---|
| `execute` | `(sql: String, vararg binds: Any?): Int` | 执行无返回行的 SQL（INSERT/UPDATE/DELETE/DDL） |
| `query` | `(sql: String, vararg binds: Any?): List<Map<String, Any?>>` | 执行查询，返回列名→值的映射列表 |
| `doltCommit` | `(message: String, all: Boolean = false): Int` | 提交变更 |
| `doltVersion` | `(): String` | 获取 Dolt 版本 |
| `doltBranch` | `(command: String, args: Array<String>): Int` | 执行分支操作 |
| `close` | `(): Unit` | 关闭数据库连接 |

## 参数绑定机制

`vararg binds: Any?` 支持多种类型，内部根据类型调用对应的 `sqlite3_bind_*`：
- `null` → `sqlite3_bind_null`
- `Int` → `sqlite3_bind_int`
- `Long` → `sqlite3_bind_int64`
- `Double`/`Float` → `sqlite3_bind_double`
- `String` → `sqlite3_bind_text`

## Dolt 功能暴露方式

Dolt 的版本控制功能（commit、branch、log、merge 等）**不**通过 JNA 直接暴露 C API，而是通过 SQLite 扩展提供的 `dolt_*` SQL 函数调用：

```kotlin
// 提交变更（通过 SQL 调用，非 JNA 直接调用）
doltlite.execute("CALL dolt_commit('-am', 'my commit message')")

// 创建分支
doltlite.execute("CALL dolt_branch('feature-branch')")
```

这种方式保持了 API 的简洁性，同时将 Dolt 版本控制语义封装在 native 层。

## 构建与发布

- **构建系统**：Gradle Kotlin DSL（`build.gradle.kts`），Android Library Plugin 8.5.2
- **发布目标**：Maven Central（`com.dolthub:doltlite-android:0.11.20`）
- **最小 SDK**：21，**目标 SDK**：34
- **Native 依赖**：`net.java.dev.jna:jna:5.14.0@aar`
- **签署**：`signAllPublications()` + Central Portal 发布

## 信源信息

- **信源距离**: ① 源码目录
- **固定版本**: `v0.11.21`
- **关键文件**: `src/main/kotlin/com/dolthub/doltlite/Doltlite.kt`、`CDoltlite.kt`、`build.gradle.kts`

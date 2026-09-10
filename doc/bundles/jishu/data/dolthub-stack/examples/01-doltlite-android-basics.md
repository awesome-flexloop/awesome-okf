---
type: example
title: doltlite-android 移动端使用示例
description: "展示 doltlite-android 在 Android Kotlin 项目中的初始化、CRUD 操作、Dolt 版本控制命令调用"
tags: [android, kotlin, doltlite, mobile, example, tutorial]
status: stable
stale_after: 2027-03-09
generated:
  by: example_agent/agnes-2.5-flash
  at: 2026-09-09T15:30:00Z
verified:
  at: "2026-09-09"
  by: process:seven-concepts-v
  status: verified
  noted: "基于 facts.md F-001~F-025 验证，API 签名与源码一致"
sources:
  - id: doltlite-readme
    resource: d:\spaces\SpecWeave\external\dao\action\DoltHub\doltlite-android
    title: doltlite-android README
---

# doltlite-android 移动端使用示例

## 示例一：添加依赖

```groovy
// build.gradle.kts (app level)
dependencies {
    implementation("com.dolthub:doltlite-android:0.11.20")
}
```

## 示例二：初始化数据库

```kotlin
import com.dolthub.doltlite.Doltlite

// 创建或打开数据库（路径为内部存储路径）
val doltlite = Doltlite(
    path = "$filesDir/my_database.dolt",
    create = true  // 数据库不存在时创建
)

// 使用 try-with-resources 自动关闭
use(closed = { doltlite.close() }) {
    // 执行数据库操作
}
```

## 示例三：创建表与插入数据

```kotlin
// 创建表
doltlite.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER,
        email TEXT
    )
""")

// 插入数据（使用参数绑定，防止 SQL 注入）
doltlite.execute(
    "INSERT INTO users (name, age, email) VALUES (?, ?, ?)",
    "Alice", 30, "alice@example.com"
)
doltlite.execute(
    "INSERT INTO users (name, age, email) VALUES (?, ?, ?)",
    "Bob", 25, "bob@example.com"
)
```

## 示例四：查询数据

```kotlin
// 简单查询
val results = doltlite.query("SELECT name, age FROM users WHERE age > 25")
// results: [["name" -> "Alice", "age" -> 30]]

// 遍历结果
for (row in results) {
    val name = row["name"] as? String
    val age = row["age"] as? Int
    Log.d("DoltLite", "User: $name, Age: $age")
}

// 使用 dolt_* 函数进行版本控制查询
val commits = doltlite.query("SELECT * FROM dolt_log()")
```

## 示例五：Dolt 版本控制操作

```kotlin
// 提交所有变更
val commitHash = doltlite.doltCommit("Add initial data", all = true)

// 创建分支
doltlite.doltBranch("create", arrayOf("feature-branch"))

// 查看分支列表
val branches = doltlite.query("CALL dolt_branch()")

// 切换分支
doltlite.execute("CALL dolt_checkout('feature-branch')")

// 查看版本
val version = doltlite.doltVersion()
Log.d("DoltLite", "Dolt version: $version")
```

## 示例六：错误处理

```kotlin
try {
    doltlite.execute("INSERT INTO users (name) VALUES (?)", "Charlie")
} catch (e: DoltliteException) {
    Log.e("DoltLite", "SQL error: ${e.sql}, message: ${e.message}")
}
```

## 示例七：完整使用流程

```kotlin
class MyDatabaseApplication : Application() {
    lateinit var doltlite: Doltlite

    override fun onCreate() {
        super.onCreate()
        doltlite = Doltlite(
            path = "$filesDir/app_data.dolt",
            create = true
        )
        initializeSchema()
    }

    private fun initializeSchema() {
        doltlite.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        doltlite.doltCommit("Initialize schema", all = false)
    }

    fun createUser(name: String, age: Int): Long {
        doltlite.execute(
            "INSERT INTO users (name, age) VALUES (?, ?)",
            name, age
        )
        doltlite.doltCommit("Add user: $name", all = false)
        // 返回最后插入的 ID（需通过 query 查询）
        val result = doltlite.query("SELECT last_insert_rowid()")
        return (result[0]["last_insert_rowid()"] as? Long) ?: -1
    }

    fun getAllUsers(): List<Map<String, Any?>> {
        return doltlite.query("SELECT * FROM users ORDER BY created_at DESC")
    }

    override fun onTerminate() {
        super.onTerminate()
        doltlite.close()
    }
}
```

## 注意事项

1. **线程安全**：`Doltlite` 实例不是线程安全的，多线程场景需自行同步
2. **路径管理**：数据库文件应存储在 `context.filesDir` 或 `getExternalFilesDir()`
3. **资源释放**：务必在 `onTerminate` 或合适时机调用 `close()`
4. **dolt_* 函数**：版本控制操作通过 SQL 调用（`CALL dolt_commit(...)`），非直接 API

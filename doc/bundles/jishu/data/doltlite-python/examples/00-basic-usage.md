---
type: Example
title: 基本用法：python 脚本中使用 doltlite
description: "标准 python script.py 调用方式：前置 import doltlite、sqlite3 连接、Dolt 版本控制操作。F-002、F-013、F-020、F-021。"
tags: [doltlite-python, example, getting-started]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-10" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10" }
status: stable
stale_after: "2027-03-31"
sources:
  - id: doltlite-python-repo
    resource: https://github.com/dolthub/doltlite-python
    title: dolthub/doltlite-python（官方仓库）
  - id: doltlite-python-local
    resource: "本地克隆（tag v0.50.7，commit ba3b46fa6f58e42aef4b929d97a28248832079cb）"
    title: doltlite-python 源码逐文件精读
---

# 基本用法：python 脚本中使用 doltlite

> **对应 F 编号**：F-002、F-013、F-020、F-021

## 最小可运行示例

以下是一个完整的 `app.py` 脚本，展示 doltlite 的标准用法：

```python
import doltlite     # 必须最先导入，触发 bootstrap()
import sqlite3
import os

# 1. 创建（或连接）Dolt 数据库目录
db_path = "/tmp/my-dolt-db"
os.makedirs(db_path, exist_ok=True)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 2. 验证 libdoltlite 路径（F-020: libdoltlite_path() API）
print(f"Using libdoltlite: {doltlite.libdoltlite_path()}")

# 3. 查询 Dolt 版本
version = cursor.execute("SELECT dolt_version()").fetchone()[0]
print(f"Dolt version: {version}")

# 4. 创建表并插入数据
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id    INT PRIMARY KEY,
        name  TEXT,
        age   INT
    )
""")
cursor.executemany(
    "INSERT INTO users VALUES (?, ?, ?)",
    [(1, "Alice", 30), (2, "Bob", 25), (3, "Carol", 35)]
)
conn.commit()

# 5. 执行 Dolt commit（自动追踪所有变更）
cursor.execute("DOLT_ADD('-A')")
cursor.execute("DOLT_COMMIT('-m', 'Initial commit with 3 users')")

# 6. 查询 dolt_log 虚拟表查看提交历史
rows = cursor.execute("SELECT hash, message FROM dolt_log() LIMIT 5").fetchall()
for h, msg in rows:
    print(f"  {h[:8]}  {msg}")

# 7. 创建分支并修改数据
cursor.execute("DOLT_BRANCH('feature/alice-update')")
cursor.execute("DOLT_CHECKOUT('feature/alice-update')")
cursor.execute("UPDATE users SET age = 31 WHERE name = 'Alice'")
cursor.execute("DOLT_ADD('-A')")
cursor.execute("DOLT_COMMIT('-m', 'Updated Alice age')")

# 8. 切换回 main 分支验证隔离
cursor.execute("DOLT_CHECKOUT('main')")
row = cursor.execute("SELECT age FROM users WHERE name = 'Alice'").fetchone()
print(f"Alice age on main: {row[0]}")  # 仍为 30，feature 分支的修改不可见

conn.close()
```

运行：

```bash
pip install doltlite
python app.py
```

输出示例：
```
Using libdoltlite: /usr/lib/python3.12/site-packages/doltlite/_lib/libdoltlite.so
Dolt version: v0.50.7
  abc12345  Initial commit with 3 users
  def67890  Updated Alice age
Alice age on main: 30
```

## 关键要点

1. **`import doltlite` 必须在 `import sqlite3` 之前**：否则 bootstrap re-exec 会失败（F-019）
2. **数据库路径是目录**：Dolt 以目录为单位管理 repo，每个子目录是一个独立数据库
3. **Dolt SQL 函数与普通 SQL 混用**：`DOLT_ADD`、`DOLT_COMMIT`、`DOLT_BRANCH`、`DOLT_CHECKOUT` 等是 libdoltlite 注入的 SQL 函数
4. **虚拟表 `dolt_log()`**：查询提交历史，无需 CLI

## 学习路径

* [Jupyter/REPL 绕过方案](01-jupyter-workaround.md) — 解决交互式环境无法 re-exec 的问题

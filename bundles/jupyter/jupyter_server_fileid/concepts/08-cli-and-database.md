---
okf_version: "0.2"
type: concept
title: "CLI 工具与数据库管理"
description: "了解 jupyter-fileid CLI 命令、SQLite 数据库文件位置和 schema、以及 pytest 测试插件提供的测试工具。"
tags: [jupyter, fileid, cli, sqlite, database, pytest, testing]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: cli-py
    resource: "../../../../../external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/cli.py"
    title: "cli.py"
  - id: pytest-plugin-py
    resource: "../../../../../external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/pytest_plugin.py"
    title: "pytest_plugin.py"
  - id: pyproject-toml
    resource: "../../../../../external/libs/jupyter/jupyter_server_fileid/pyproject.toml"
    title: "pyproject.toml"
---

# CLI 工具与数据库管理

## CLI 命令

jupyter_server_fileid 提供基于 [Click](https://click.palletsprojects.com/) 的命令行工具，通过 `jupyter-fileid` 入口点访问。

### 入口点注册

在 `pyproject.toml` 中定义：

```toml
[project.scripts]
jupyter-fileid = "jupyter_server_fileid.cli:main"
```

### 可用命令

```bash
jupyter-fileid --help
```

#### drop — 删除数据库表

```bash
jupyter-fileid drop
```

删除默认数据库路径下的 `Files` 表。这在索引损坏需要重建时很有用。

**注意**：
- 操作的是 `default_db_path()` 指向的数据库（`jupyter_data_dir()/file_id_manager.db`）
- 如果 Jupyter Server 正在运行，不要执行此操作（会导致数据库冲突）
- 删除后下次启动扩展会自动重建空表，但所有文件 ID 会丢失

**示例输出**：
```
Successfully dropped file ID table at path /home/user/.local/share/jupyter/file_id_manager.db
```

#### version — 查看版本

```bash
jupyter-fileid --version
```

## 数据库位置

### 默认路径

数据库文件默认存放在 Jupyter 数据目录下：

```python
from jupyter_core.application import JupyterApp
default_db_path = JupyterApp().data_dir / "file_id_manager.db"
```

| 平台 | 默认路径 |
|------|---------|
| Linux | `~/.local/share/jupyter/file_id_manager.db` |
| macOS | `~/Library/Jupyter/file_id_manager.db` |
| Windows | `%APPDATA%\jupyter\file_id_manager.db` |

### 自定义路径

通过配置 `db_path` traitlet 指定：

```python
c.ArbitraryFileIdManager.db_path = "/custom/path/fileid.db"
# 或
c.LocalFileIdManager.db_path = "/custom/path/fileid.db"
```

特殊值 `:memory:` 使用内存数据库（仅用于测试）。

### Journal Mode

SQLite 的 journal mode 通过 `db_journal_mode` 配置：

- **ArbitraryFileIdManager** 默认 `DELETE`：标准模式，每次事务后删除回滚日志
- **LocalFileIdManager** 默认 `WAL`：Write-Ahead Logging，支持并发读写，性能更好

```sql
-- 设置 journal mode
PRAGMA journal_mode = WAL;   -- 或 DELETE/TRUNCATE/PERSIST/MEMORY/OFF
```

## 数据库 Schema

### ArbitraryFileIdManager Schema

```sql
CREATE TABLE IF NOT EXISTS Files (
    id TEXT PRIMARY KEY NOT NULL,
    path TEXT NOT NULL UNIQUE
);

CREATE INDEX IF NOT EXISTS ix_Files_path ON Files (path);
```

简单的 UUID→路径映射表。`path` 列使用 `posixpath` 格式的规范化路径（始终正斜杠，以 root_dir 为前缀）。

### LocalFileIdManager Schema

```sql
CREATE TABLE IF NOT EXISTS Files (
    id TEXT PRIMARY KEY NOT NULL,
    path TEXT NOT NULL,
    ino INTEGER NOT NULL UNIQUE,
    crtime INTEGER,
    mtime INTEGER NOT NULL,
    is_dir TINYINT NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_Files_path ON Files (path);
CREATE INDEX IF NOT EXISTS ix_Files_is_dir ON Files (is_dir);
```

| 列 | 类型 | 说明 | 单位 |
|----|------|------|------|
| id | TEXT | UUID v4 字符串 | — |
| path | TEXT | 规范化路径（os.path 格式） | — |
| ino | INTEGER | 文件 inode 号 | stat.st_ino |
| crtime | INTEGER | 创建时间（纳秒），Linux 可为 NULL | st_birthtime_ns 或 st_ctime_ns |
| mtime | INTEGER | 修改时间（纳秒） | stat.st_mtime_ns |
| is_dir | TINYINT | 是否目录（0/1） | stat.S_ISDIR |

**时间精度**：所有时间戳使用纳秒精度（Python 3 的 `st_*time_ns` 属性），而非秒。

### 直接查询数据库

可以使用 SQLite 命令行工具直接查看数据库内容：

```bash
# 查看所有记录
sqlite3 ~/.local/share/jupyter/file_id_manager.db "SELECT * FROM Files;"

# 查询特定文件的 ID
sqlite3 ~/.local/share/jupyter/file_id_manager.db \
  "SELECT id FROM Files WHERE path LIKE '%notebook.ipynb';"

# 统计记录数
sqlite3 ~/.local/share/jupyter/file_id_manager.db "SELECT COUNT(*) FROM Files;"

# 查看脏目录（mtime 已过期的目录）
sqlite3 ~/.local/share/jupyter/file_id_manager.db \
  "SELECT path, mtime FROM Files WHERE is_dir = 1;"
```

## Pytest 测试插件

jupyter_server_fileid 内置了 pytest 插件（`jupyter_server_fileid.pytest_plugin`），为编写测试提供了便捷的 fixtures。

### 启用插件

pytest 会通过 entry point 自动发现该插件，无需额外配置。

### 提供的 Fixtures

| Fixture | 作用域 | 返回类型 | 说明 |
|---------|-------|---------|------|
| `jp_server_config` | function | dict | 配置 ServerApp 启用 jupyter_server_fileid 扩展 |
| `fid_db_path` | function | str | 返回测试用数据库路径（`jp_data_dir/fileidmanager_test.db`） |
| `delete_fid_db` | function (autouse) | — | 自动清理：每个测试后删除测试数据库文件 |
| `fid_manager` | function | LocalFileIdManager | 预配置的 LocalFileIdManager 实例（journal_mode=OFF） |
| `arbitrary_fid_manager` | function | ArbitraryFileIdManager | 预配置的 ArbitraryFileIdManager 实例（journal_mode=OFF） |
| `any_fid_manager_class` | function | Type[BaseFileIdManager] | 参数化 fixture，依次返回 Local/Arbitrary 两种类 |
| `any_fid_manager` | function | BaseFileIdManager | 参数化 fixture，依次返回两种管理器实例 |
| `fs_helpers` | function | FsHelpers | 文件系统操作辅助类，用于模拟文件操作 |

### jp_server_config Fixture

```python
@pytest.fixture
def jp_server_config(jp_server_config):
    return {"ServerApp": {"jpserver_extensions": {"jupyter_server_fileid": True}}}
```

自动配置 Jupyter Server 测试客户端启用 fileid 扩展。这是对 jupyter_server 提供的 `jp_server_config` fixture 的叠加。

### fs_helpers — 文件系统操作辅助类

`FsHelpers` 提供一组方法模拟文件操作，同时自动更新父目录 mtime（这对 LocalFileIdManager 的带外检测至关重要）：

| 方法 | 功能 | 额外操作 |
|------|------|---------|
| `touch(path, dir=False)` | 创建文件或目录 | 更新文件和父目录 mtime（唯一值） |
| `move(old_path, new_path)` | 移动/重命名文件 | 更新新父目录 mtime |
| `edit(path)` | 模拟编辑文件 | 更新文件 mtime |
| `delete(path)` | 删除文件/目录 | 更新父目录 mtime |
| `copy(old_path, new_path)` | 复制文件/目录 | 更新源父目录 mtime |

**为什么需要 fs_helpers？**

LocalFileIdManager 的带外检测依赖目录 mtime 变化来发现脏目录。如果在测试中直接使用 `os.rename()` 或 `Path.touch()`，父目录 mtime 可能不会立即变化（取决于文件系统时间精度），导致同步检测失败。`fs_helpers` 通过 `os.utime()` 手动设置递增的 mtime 值，确保每次操作后父目录 mtime 唯一变化。

**使用示例**：

```python
def test_oob_move(fid_manager, fs_helpers):
    # 创建文件
    fs_helpers.touch("test.ipynb")
    fid_manager.index("test.ipynb")
    file_id = fid_manager.get_id("test.ipynb")

    # 模拟带外移动（不经过事件系统）
    fs_helpers.move("test.ipynb", "renamed.ipynb")

    # get_path 应能检测移动并返回新路径
    path = fid_manager.get_path(file_id)
    assert path == "renamed.ipynb"
```

### 参数化测试两种管理器

使用 `any_fid_manager` fixture 可以对两种管理器运行相同测试：

```python
def test_index(any_fid_manager):
    # 这个测试会运行两次：一次 Local，一次 Arbitrary
    any_fid_manager.index("test.ipynb")
    file_id = any_fid_manager.get_id("test.ipynb")
    assert file_id is not None
    assert any_fid_manager.get_path(file_id) == "test.ipynb"
```

---

**相关文档：**
- [双管理器对比](04-arbitrary-vs-local.md) — 两种管理器 Schema 差异
- [扩展配置](07-extension-configuration.md) — db_path 和 journal_mode 配置
- [基本使用示例](../examples/01-basic-usage.md) — 编程接口使用

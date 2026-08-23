---
okf_version: "0.2"
type: reference
title: "cli.py 源码解析"
description: "命令行工具：基于 click 的 jupyter-fileid CLI，当前仅提供 drop 子命令删除数据库表。"
tags: [jupyter, fileid, cli, click, source]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: cli-py
    resource: "../../../../../external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/cli.py"
    title: "jupyter_server_fileid/cli.py"
---

# cli.py 源码解析

`cli.py` 约 22 行，提供一个简单的命令行工具 `jupyter-fileid`。

## 模块结构

```python
import sqlite3
import click
from .manager import default_db_path

@click.group()
@click.version_option()
def main() -> None:
    """Jupyter File ID server extension CLI."""
    pass

@main.command("drop")
def drop() -> None:
    """Drops the file ID table at the default path."""
    con = sqlite3.connect(default_db_path)
    con.execute("DROP TABLE Files;")
    con.commit()
    con.close()
    click.echo(f"Successfully dropped file ID table at path {default_db_path}")
```

## CLI 入口

通过 `pyproject.toml` 注册为脚本入口：

```toml
[project.scripts]
jupyter-fileid = "jupyter_server_fileid.cli:main"
```

```toml
[project.optional-dependencies]
cli = ["click"]
```

CLI 功能需要安装 `click` 可选依赖：`pip install jupyter_server_fileid[cli]`。

## 命令列表

| 命令 | 功能 |
|------|------|
| `jupyter-fileid --version` | 输出版本号（via click.version_option） |
| `jupyter-fileid drop` | 删除默认路径的 Files 表（重置索引） |

### drop 命令

直接连接到默认数据库路径（`jupyter_data_dir()/file_id_manager.db`），执行 `DROP TABLE Files;`，然后提交并关闭连接。

**用途**：当索引损坏或需要重建时，删除旧表后重启 Jupyter Server 即可重新索引。

**注意**：drop 命令不支持自定义数据库路径，仅操作默认路径。如果使用了自定义 `db_path`，需要手动删除数据库文件。

---

**相关文档：**
- [manager.py 源码解析](manager-source.md) — default_db_path 定义
- [CLI 工具与数据库](../concepts/08-cli-and-database.md) — CLI 使用与 DB 管理

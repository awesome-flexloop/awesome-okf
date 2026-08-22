---
okf_version: "0.2"
type: example
title: "编程接口基础使用"
description: "通过可运行的 Python 代码示例，学习直接使用 FileIdManager API 进行文件索引、查询、移动、复制和删除操作，以及处理带外文件移动。"
tags: [jupyter, fileid, example, api, manager, crud, oob-detection]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: manager-py
    resource: "../../../../../external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py"
    title: "manager.py"
  - id: test-manager-py
    resource: "../../../../../external/libs/jupyter/jupyter_server_fileid/tests/test_manager.py"
    title: "tests/test_manager.py"
---

# 编程接口基础使用

本示例展示如何直接使用 FileIdManager 的 Python API 进行文件 ID 的索引和查询。

## 前置条件

```bash
pip install jupyter_server_fileid
```

## 示例 1：使用 ArbitraryFileIdManager（默认）

ArbitraryFileIdManager 是默认管理器，通过纯路径映射工作，适用于任意文件系统（本地、远程、对象存储）。

```python
"""使用 ArbitraryFileIdManager 索引和查询文件 ID"""

import tempfile
import os
from pathlib import Path

from jupyter_server_fileid.manager import ArbitraryFileIdManager

# 创建临时目录作为 root_dir
with tempfile.TemporaryDirectory() as tmpdir:
    root_dir = tmpdir

    # 创建管理器实例（使用内存数据库以便演示）
    manager = ArbitraryFileIdManager(
        root_dir=root_dir,
        db_path=":memory:",
    )

    # --- 创建一些测试文件 ---
    (Path(root_dir) / "notebooks").mkdir()
    (Path(root_dir) / "notebooks" / "analysis.ipynb").write_text("{}")
    (Path(root_dir) / "data.csv").write_text("a,b,c\n1,2,3\n")

    # --- index()：获取或创建文件 ID ---
    # 首次调用创建 ID，后续调用返回相同 ID（幂等）
    id1 = manager.index("notebooks/analysis.ipynb")
    id2 = manager.index("data.csv")
    id1_again = manager.index("notebooks/analysis.ipynb")

    print(f"analysis.ipynb ID: {id1}")
    print(f"data.csv ID:         {id2}")
    print(f"幂等验证: {id1 == id1_again}")  # True

    # --- get_id()：仅查询（不创建）---
    id_existing = manager.get_id("data.csv")
    id_nonexist = manager.get_id("nonexistent.txt")
    print(f"已存在文件: {id_existing is not None}")   # True
    print(f"不存在文件: {id_nonexist is None}")        # True

    # --- get_path()：通过 ID 查路径 ---
    path1 = manager.get_path(id1)
    path2 = manager.get_path(id2)
    print(f"ID1 -> 路径: {path1}")   # "notebooks/analysis.ipynb"
    print(f"ID2 -> 路径: {path2}")   # "data.csv"

    # 无效 ID 返回 None
    fake_path = manager.get_path("00000000-0000-0000-0000-000000000000")
    print(f"无效 ID: {fake_path is None}")  # True

    # --- 清理（内存数据库无需关闭）---
    del manager
```

## 示例 2：文件移动、复制和删除

当通过 Jupyter 接口操作文件时，事件系统会自动调用这些方法。也可以手动调用：

```python
"""文件操作：移动、复制、删除"""

import tempfile
import os
from pathlib import Path

from jupyter_server_fileid.manager import ArbitraryFileIdManager

with tempfile.TemporaryDirectory() as tmpdir:
    root_dir = tmpdir
    manager = ArbitraryFileIdManager(root_dir=root_dir, db_path=":memory:")

    # 创建测试文件和目录
    proj_dir = Path(root_dir) / "project"
    proj_dir.mkdir()
    (proj_dir / "main.py").write_text("print('hello')")
    (proj_dir / "utils.py").write_text("def util(): pass")

    # 索引文件
    main_id = manager.index("project/main.py")
    utils_id = manager.index("project/utils.py")
    print(f"main.py ID:  {main_id}")
    print(f"utils.py ID: {utils_id}")

    # --- move()：模拟文件重命名/移动 ---
    # 在文件系统中实际移动文件
    os.rename(proj_dir / "main.py", proj_dir / "app.py")

    # 通知管理器更新索引
    manager.move("project/main.py", "project/app.py")
    new_path = manager.get_path(main_id)
    print(f"移动后: ID {main_id[:8]}... -> {new_path}")  # "project/app.py"

    # --- copy()：模拟文件复制 ---
    # 在文件系统中实际复制
    import shutil
    shutil.copy2(proj_dir / "utils.py", proj_dir / "helpers.py")

    # 通知管理器（copy 创建新 ID）
    helpers_id = manager.copy("project/utils.py", "project/helpers.py")
    print(f"utils.py ID: {utils_id}")
    print(f"helpers.py ID (新): {helpers_id}")
    print(f"ID 不同: {utils_id != helpers_id}")  # True - 复制产生新文件新ID

    # --- delete()：模拟文件删除 ---
    os.remove(proj_dir / "app.py")
    manager.delete("project/app.py")
    deleted_path = manager.get_path(main_id)
    print(f"删除后查询: {deleted_path is None}")  # True
```

## 示例 3：目录递归操作

move/copy/delete 对目录会自动递归处理所有子项：

```python
"""目录递归操作"""

import tempfile
import os
from pathlib import Path
import shutil

from jupyter_server_fileid.manager import ArbitraryFileIdManager

with tempfile.TemporaryDirectory() as tmpdir:
    root_dir = tmpdir
    manager = ArbitraryFileIdManager(root_dir=root_dir, db_path=":memory:")

    # 创建目录结构
    src = Path(root_dir) / "src"
    src.mkdir()
    (src / "__init__.py").write_text("")
    (src / "core").mkdir()
    (src / "core" / "base.py").write_text("# base")
    (src / "core" / "config.py").write_text("# config")

    # 索引所有文件
    init_id = manager.index("src/__init__.py")
    base_id = manager.index("src/core/base.py")
    config_id = manager.index("src/core/config.py")

    print(f"移动前:")
    print(f"  __init__.py -> {manager.get_path(init_id)}")
    print(f"  base.py     -> {manager.get_path(base_id)}")
    print(f"  config.py   -> {manager.get_path(config_id)}")

    # 递归移动目录（重命名 src -> lib）
    lib = Path(root_dir) / "lib"
    os.rename(src, lib)
    manager.move("src", "lib")

    print(f"移动后:")
    print(f"  __init__.py -> {manager.get_path(init_id)}")  # "lib/__init__.py"
    print(f"  base.py     -> {manager.get_path(base_id)}")  # "lib/core/base.py"
    print(f"  config.py   -> {manager.get_path(config_id)}")  # "lib/core/config.py"

    # 递归复制目录
    backup = Path(root_dir) / "backup"
    shutil.copytree(lib, backup)
    manager.copy("lib", "backup")

    # 递归删除目录
    shutil.rmtree(backup)
    manager.delete("backup")
```

## 示例 4：LocalFileIdManager 与带外移动检测

LocalFileIdManager 通过 inode 跟踪文件，能检测文件在 Jupyter 外部被移动的情况。

```python
"""LocalFileIdManager 带外移动检测"""

import tempfile
import os
from pathlib import Path
import time

from jupyter_server_fileid.manager import LocalFileIdManager

with tempfile.TemporaryDirectory() as tmpdir:
    root_dir = tmpdir
    manager = LocalFileIdManager(
        root_dir=root_dir,
        db_path=":memory:",
    )
    manager.con.execute("PRAGMA journal_mode = OFF")  # 加速测试

    # 创建文件并索引
    old_file = Path(root_dir) / "original.txt"
    old_file.write_text("important content")
    file_id = manager.index("original.txt")
    print(f"文件 ID: {file_id}")
    print(f"初始路径: {manager.get_path(file_id)}")  # "original.txt"

    # 模拟"带外移动"：直接用 os.rename，不通知 manager
    new_file = Path(root_dir) / "renamed.txt"
    os.rename(old_file, new_file)

    # 等待一下确保 mtime 变化（测试环境中需要）
    time.sleep(0.01)
    # 更新父目录 mtime 让带外检测能发现
    os.utime(root_dir, None)

    # get_path() 会检测到移动，自动同步并返回新路径
    detected_path = manager.get_path(file_id)
    print(f"带外移动后路径: {detected_path}")  # "renamed.txt"
    print(f"检测成功: {detected_path == 'renamed.txt'}")
```

## 示例 5：从 Jupyter Server Settings 获取管理器

在 Jupyter Server 扩展中，管理器通过 `self.settings` 获取：

```python
"""在 Jupyter Server RequestHandler 中使用 file_id_manager"""

from jupyter_server.base.handlers import APIHandler
from tornado import web

class MyFileHandler(APIHandler):
    @web.authenticated
    def get(self):
        # 获取 file_id_manager 实例
        fid_mgr = self.settings.get("file_id_manager")
        
        path = self.get_argument("path")
        file_id = fid_mgr.index(path)
        
        if file_id is None:
            raise web.HTTPError(404, f"File not found: {path}")
        
        self.write({"id": file_id, "path": path})
```

---

**下一步阅读：**
- [REST API 使用示例](02-rest-api-usage.md) — 通过 HTTP API 查询文件 ID
- [自定义管理器示例](03-custom-manager.md) — 创建自己的 File ID 管理器
- [REST API 端点](../concepts/06-http-api.md) — API 端点详解

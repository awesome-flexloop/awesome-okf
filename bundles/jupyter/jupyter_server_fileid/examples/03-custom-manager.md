---
okf_version: "0.2"
type: example
title: "自定义 File ID 管理器"
description: "通过实现 BaseFileIdManager 抽象基类，创建支持云存储（如 S3）的自定义文件 ID 管理器，包含完整实现代码和配置方法。"
tags: [jupyter, fileid, example, custom-manager, extension, s3, cloud-storage]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: manager-py
    resource: "../../../../../external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py"
    title: "manager.py"
---

# 自定义 File ID 管理器

本示例展示如何继承 `BaseFileIdManager` 创建一个支持 S3 风格对象存储的自定义文件 ID 管理器。

## 场景说明

假设你有一个基于 S3 的 ContentsManager，文件路径形如 `s3://bucket/prefix/notebook.ipynb`。你需要：
1. 维护 S3 路径与 UUID 的稳定映射
2. 监听 Jupyter 事件处理重命名/复制/删除
3. 使用 SQLite 持久化映射关系

## 完整实现

```python
"""s3_file_id_manager.py — S3 对象存储的 File ID 管理器示例"""

import posixpath
import sqlite3
import uuid
from typing import Any, Callable, Dict, Optional

from jupyter_server_fileid.manager import BaseFileIdManager
from traitlets import default, validate, TraitError


class S3FileIdManager(BaseFileIdManager):
    """S3 对象存储的 File ID 管理器。

    与 ArbitraryFileIdManager 类似，但路径格式为 s3://bucket/key，
    且支持通过 S3 API 验证文件存在性。
    """

    # --- Traitlets 配置 ---

    s3_bucket = ""  # 默认 bucket，由配置设置

    @default("db_journal_mode")
    def _default_db_journal_mode(self) -> str:
        """S3 场景下使用 WAL 以支持并发读写"""
        return "WAL"

    @validate("root_dir")
    def _validate_root_dir(self, proposal: Dict[str, Any]) -> str:
        """root_dir 应为 s3://bucket/prefix 格式"""
        value = proposal["value"]
        if value is None:
            raise TraitError("root_dir must not be None for S3FileIdManager")
        if not value.startswith("s3://"):
            raise TraitError(
                f"root_dir must start with 's3://', got '{value}'"
            )
        return value

    # --- 初始化 ---

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 连接 SQLite
        self.con = sqlite3.connect(self.db_path)
        self.con.execute(f"PRAGMA journal_mode = {self.db_journal_mode}")

        # 创建表（schema 与 ArbitraryFileIdManager 相同）
        self.con.execute(
            """CREATE TABLE IF NOT EXISTS Files(
                id TEXT PRIMARY KEY NOT NULL,
                path TEXT NOT NULL UNIQUE
            )"""
        )
        self.con.execute(
            "CREATE INDEX IF NOT EXISTS ix_Files_path ON Files (path)"
        )
        self.con.commit()

    def __del__(self):
        if hasattr(self, "con"):
            self.con.commit()
            self.con.close()

    # --- 路径归一化 ---

    def _normalize_path(self, path: str) -> str:
        """将 API 路径转为持久化格式。

        API 路径可能是：
        - "notebook.ipynb"（相对路径）
        - "s3://bucket/prefix/notebook.ipynb"（完整 S3 URI）
        - "prefix/notebook.ipynb"（相对于 bucket 的路径）

        持久化格式始终是完整的 posixpath 风格 S3 key（相对于 root_dir 的相对路径）。
        """
        # 确保使用正斜杠
        path = path.replace("\\", "/")

        # 如果已经是 s3:// URI，提取 key 部分
        if path.startswith("s3://"):
            # 去掉 s3://bucket/prefix/ 前缀
            prefix = self.root_dir.rstrip("/") + "/"
            if path.startswith(prefix):
                path = path[len(prefix):]
            else:
                # 不同 bucket，保持原样（或者按你的逻辑处理）
                return path
        else:
            # 相对路径，加上 root_dir 前缀后再标准化
            full = posixpath.join(self.root_dir.rstrip("/"), path)
            prefix = self.root_dir.rstrip("/") + "/"
            if full.startswith(prefix):
                path = full[len(prefix):]

        # 规范化路径（去除 ./ ../）
        path = posixpath.normpath(path)
        # 去掉前导斜杠
        path = path.lstrip("/")

        # 加上 root_dir 前缀作为持久化路径
        return posixpath.join(self.root_dir.rstrip("/"), path)

    def _from_normalized_path(self, path: Optional[str]) -> Optional[str]:
        """将持久化路径转为 API 路径（正斜杠相对路径）"""
        if path is None:
            return None

        root = self.root_dir.rstrip("/") + "/"
        if not path.startswith(root):
            return None

        # 去掉 root_dir 前缀，得到相对路径
        rel_path = path[len(root):]
        # 确保使用正斜杠
        rel_path = rel_path.replace("\\", "/")
        return rel_path or ""

    # --- CRUD 操作 ---

    def index(self, path: str) -> Optional[str]:
        """获取或创建文件 ID"""
        norm_path = self._normalize_path(path)

        with self.con:
            # 先查询是否已存在
            row = self.con.execute(
                "SELECT id FROM Files WHERE path = ?", (norm_path,)
            ).fetchone()
            if row:
                return row[0]

            # 不存在则创建新记录
            new_id = self._uuid()
            self.con.execute(
                "INSERT INTO Files (id, path) VALUES (?, ?)",
                (new_id, norm_path),
            )
            self.log.info(f"Indexed S3 object: {norm_path} -> {new_id}")
            return new_id

    def get_id(self, path: str) -> Optional[str]:
        """仅查询 ID，不创建"""
        norm_path = self._normalize_path(path)
        row = self.con.execute(
            "SELECT id FROM Files WHERE path = ?", (norm_path,)
        ).fetchone()
        return row[0] if row else None

    def get_path(self, id: str) -> Optional[str]:
        """通过 ID 查询路径"""
        row = self.con.execute(
            "SELECT path FROM Files WHERE id = ?", (id,)
        ).fetchone()
        if not row:
            return None
        return self._from_normalized_path(row[0])

    def move(self, old_path: str, new_path: str) -> Optional[str]:
        """处理文件移动/重命名"""
        old_norm = self._normalize_path(old_path)
        new_norm = self._normalize_path(new_path)

        with self.con:
            row = self.con.execute(
                "SELECT id FROM Files WHERE path = ?", (old_norm,)
            ).fetchone()
            if not row:
                # 未索引的路径，尝试索引新路径
                return self.index(new_path)

            file_id = row[0]
            self.con.execute(
                "UPDATE Files SET path = ? WHERE id = ?",
                (new_norm, file_id),
            )
            # 递归移动子路径（目录）
            self._move_recursive(old_norm, new_norm, path_mgr=posixpath)
            return file_id

    def copy(self, from_path: str, to_path: str) -> Optional[str]:
        """处理文件复制（创建新 ID）"""
        from_norm = self._normalize_path(from_path)
        to_norm = self._normalize_path(to_path)

        with self.con:
            row = self.con.execute(
                "SELECT id FROM Files WHERE path = ?", (from_norm,)
            ).fetchone()
            if not row:
                return None

            new_id = self._uuid()
            self.con.execute(
                "INSERT INTO Files (id, path) VALUES (?, ?)",
                (new_id, to_norm),
            )
            # 递归复制子路径
            self._copy_recursive(from_norm, to_norm, path_mgr=posixpath)
            return new_id

    def delete(self, path: str) -> None:
        """处理文件删除"""
        norm_path = self._normalize_path(path)
        with self.con:
            self.con.execute("DELETE FROM Files WHERE path = ?", (norm_path,))
            self._delete_recursive(norm_path, path_mgr=posixpath)

    def save(self, path: str) -> Optional[str]:
        """S3 场景下 save 不改变映射关系，返回现有 ID"""
        return self.get_id(path)

    # --- 事件处理器映射 ---

    def get_handlers_by_action(self) -> Dict[str, Optional[Callable[[Dict[str, Any]], Any]]]:
        return {
            "get": None,
            "save": lambda data: self.save(data["path"]),
            "rename": lambda data: self.move(data["source_path"], data["path"]),
            "copy": lambda data: self.copy(data["source_path"], data["path"]),
            "delete": lambda data: self.delete(data["path"]),
        }
```

## 配置使用

### 方式 1：配置文件

```python
# jupyter_server_config.py
from s3_file_id_manager import S3FileIdManager

c.FileIdExtension.file_id_manager_class = S3FileIdManager
c.S3FileIdManager.db_path = "/data/jupyter/s3_fileid.db"
c.S3FileIdManager.db_journal_mode = "WAL"
```

### 方式 2：包安装与 entry point

在 `pyproject.toml` 中注册：

```toml
[project]
name = "s3-fileid-manager"
version = "0.1.0"
dependencies = [
    "jupyter_server_fileid>=0.9",
]

[project.entry-points."jupyter_server_fileid.managers"]
s3 = "s3_file_id_manager:S3FileIdManager"
```

然后通过配置引用：

```python
c.FileIdExtension.file_id_manager_class = "s3-fileid-manager.s3_file_id_manager.S3FileIdManager"
```

## 增强版：添加 S3 存在性检查

实际生产中，可能需要验证 S3 对象是否真实存在：

```python
"""增强版：S3FileIdManager with existence check"""

# 需要安装 boto3
# pip install boto3

import boto3
from botocore.exceptions import ClientError


class S3FileIdManagerWithCheck(S3FileIdManager):
    """带 S3 存在性检查的 File ID 管理器"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._s3_client = None

    @property
    def s3_client(self):
        if self._s3_client is None:
            self._s3_client = boto3.client("s3")
        return self._s3_client

    def _s3_object_exists(self, bucket: str, key: str) -> bool:
        """检查 S3 对象是否存在"""
        try:
            self.s3_client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise

    def _parse_s3_path(self, norm_path: str) -> tuple[str, str]:
        """从 s3://bucket/key 解析 bucket 和 key"""
        path = norm_path[len("s3://"):]
        parts = path.split("/", 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ""
        return bucket, key

    def get_id(self, path: str) -> Optional[str]:
        """查询 ID 前先验证 S3 对象存在"""
        norm_path = self._normalize_path(path)
        if not norm_path.startswith("s3://"):
            return None

        bucket, key = self._parse_s3_path(norm_path)
        if key and not self._s3_object_exists(bucket, key):
            return None  # 对象不存在

        return super().get_id(path)
```

## 测试自定义管理器

```python
"""测试自定义管理器"""

import tempfile
import os

def test_s3_file_id_manager():
    """S3FileIdManager 基础测试"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")

        manager = S3FileIdManager(
            root_dir="s3://my-bucket/notebooks",
            db_path=db_path,
        )

        # 测试索引
        file_id = manager.index("analysis.ipynb")
        assert file_id is not None

        # 测试路径归一化
        assert manager.get_path(file_id) == "analysis.ipynb"

        # 测试完整 S3 URI
        full_id = manager.index("s3://my-bucket/notebooks/data/input.csv")
        assert manager.get_path(full_id) == "data/input.csv"

        # 测试移动
        manager.move("analysis.ipynb", "analysis_v2.ipynb")
        assert manager.get_path(file_id) == "analysis_v2.ipynb"

        # 测试复制
        copy_id = manager.copy("data/input.csv", "data/input_copy.csv")
        assert copy_id is not None
        assert copy_id != full_id  # 新 ID

        # 测试删除
        manager.delete("analysis_v2.ipynb")
        assert manager.get_path(file_id) is None

        print("✓ 所有测试通过")

if __name__ == "__main__":
    test_s3_file_id_manager()
```

---

**相关文档：**
- [扩展配置与自定义管理器](../concepts/07-extension-configuration.md) — 配置选项详解
- [抽象基类与核心 API](../concepts/03-file-id-manager.md) — 必须实现的抽象方法
- [事件驱动同步机制](../concepts/05-event-sync-mechanism.md) — 事件 handler 映射

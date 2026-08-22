---
okf_version: "0.2"
type: concept
title: "5分钟快速上手"
description: "安装 jupyter_server_fileid，配置管理器类型，通过 REST API 和 Python API 进行基本的文件 ID 查询操作。"
tags: [jupyter, fileid, getting-started, install, configuration]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pyproject-toml
    resource: "../../../../../external/libs/jupyter/jupyter_server_fileid/pyproject.toml"
    title: "pyproject.toml"
  - id: extension-py
    resource: "../../../../../external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/extension.py"
    title: "extension.py"
  - id: manager-py
    resource: "../../../../../external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py"
    title: "manager.py"
---

# 5分钟快速上手

## 安装

```bash
pip install jupyter_server_fileid

# 如需 CLI 工具
pip install "jupyter_server_fileid[cli]"

# 如需运行测试
pip install "jupyter_server_fileid[test]"
```

安装后扩展会自动注册到 Jupyter Server，无需手动启用。可以通过以下命令验证：

```bash
jupyter server extension list
```

应看到 `jupyter_server_fileid` 已启用。

## 基本配置

默认情况下，jupyter_server_fileid 使用 `ArbitraryFileIdManager`（纯路径映射模式）。如果需要 inode 级别的文件跟踪（推荐本地开发使用），在 Jupyter 配置文件中切换：

```python
# jupyter_server_config.py
c.FileIdExtension.file_id_manager_class = LocalFileIdManager
```

或通过命令行参数：

```bash
jupyter lab --FileIdExtension.file_id_manager_class=LocalFileIdManager
```

### 配置项

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `FileIdExtension.file_id_manager_class` | Type | `ArbitraryFileIdManager` | 管理器类 |
| `BaseFileIdManager.db_path` | str | `jupyter_data_dir()/file_id_manager.db` | SQLite 数据库路径，设为 `:memory:` 使用内存数据库 |
| `BaseFileIdManager.db_journal_mode` | str | 各实现不同 | SQLite journal mode |

**配置 LocalFileIdManager 示例**：

```python
# jupyter_server_config.py
c.FileIdExtension.file_id_manager_class = LocalFileIdManager
c.LocalFileIdManager.db_path = "/path/to/custom/file_id.db"
c.LocalFileIdManager.db_journal_mode = "WAL"
```

**内存数据库示例**（测试用，重启丢失索引）：

```python
c.ArbitraryFileIdManager.db_path = ":memory:"
```

## REST API 使用

启动 Jupyter Server 后，可以通过两个 REST 端点查询文件 ID：

### 路径查 ID

```bash
# 查询文件的 ID
curl "http://localhost:8888/api/fileid/id?path=notebooks/example.ipynb" \
  -H "Authorization: Token <your-token>"
```

响应：
```json
{"id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890", "path": "notebooks/example.ipynb"}
```

### ID 查路径

```bash
# 通过 ID 反查路径
curl "http://localhost:8888/api/fileid/path?id=a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
  -H "Authorization: Token <your-token>"
```

响应：
```json
{"id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890", "path": "notebooks/example.ipynb"}
```

### 错误响应

缺少参数返回 400：
```json
{"status": 400, "message": "'path' parameter was not provided in the request."}
```

未找到文件返回 404：
```json
{"status": 404, "message": "The ID for file, nonexistent.txt, could not be found."}
```

## Python API 使用

在 Jupyter Server 扩展代码中，可以直接访问 file_id_manager：

```python
# 在 Jupyter Server ExtensionApp 中
from jupyter_server_fileid.manager import LocalFileIdManager

# 获取管理器实例（从 settings）
fid_manager = self.settings["file_id_manager"]

# 索引文件并获取 ID
file_id = fid_manager.index("notebooks/example.ipynb")
print(f"File ID: {file_id}")

# 查询已有 ID
existing_id = fid_manager.get_id("notebooks/example.ipynb")

# 通过 ID 查询路径
path = fid_manager.get_path(file_id)
```

## CLI 工具

安装 `[cli]` 可选依赖后：

```bash
# 查看版本
jupyter-fileid --version

# 删除索引数据库（重置所有文件 ID）
jupyter-fileid drop
```

`drop` 命令会删除默认路径的 Files 表。重启 Jupyter Server 后将自动重建索引。

## 验证安装

1. 启动 Jupyter Lab：`jupyter lab`
2. 在浏览器中打开 Lab
3. 创建一个新 notebook
4. 访问 `http://localhost:8888/api/fileid/id?path=<notebook-name>.ipynb`
5. 如果返回 JSON 包含 `id` 字段，说明安装成功

---

**下一步阅读：**
- [架构总览](02-architecture-overview.md) — 理解模块关系与数据流
- [抽象基类与核心 API](03-file-id-manager.md) — BaseFileIdManager 详解

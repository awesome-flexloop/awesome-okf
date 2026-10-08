---
title: FetchRepo
type: reference
bundle: tutorial-codebase-knowledge
source: nodes.py
---

# FetchRepo

`FetchRepo` 是流水线的第一个节点，负责从 GitHub 仓库或本地目录抓取源代码文件。它继承自 PocketFlow 的 `Node` 类，根据输入源自动选择 GitHub API 爬取或本地目录遍历。

## 类定义

```python
class FetchRepo(Node):
```

源码位置：nodes.py#L22-L82

## 生命周期方法

### prep(shared)

从 `shared` 字典读取输入参数，组装爬虫配置。

**读取的 shared 键**：
- `repo_url` (str|None)：GitHub 仓库 URL
- `local_dir` (str|None)：本地目录路径
- `project_name` (str|None)：项目名称（为空时自动推导）
- `github_token` (str|None)：GitHub 访问令牌
- `include_patterns` (set)：文件包含模式（如 `{"*.py", "*.js"}`）
- `exclude_patterns` (set)：文件排除模式（如 `{"tests/*", "docs/*"}`）
- `max_file_size` (int)：最大文件大小（字节）

**返回值** (dict)：
- `repo_url`：仓库 URL
- `local_dir`：本地目录
- `token`：GitHub Token
- `include_patterns`：包含模式
- `exclude_patterns`：排除模式
- `max_file_size`：最大文件大小
- `use_relative_paths`：固定为 `True`

**项目名自动推导逻辑**：若 `project_name` 为空，从 URL 末尾取（去除 `.git` 后缀）或取本地目录的 basename，然后写回 `shared["project_name"]`。

### exec(prep_res)

根据 `prep_res["repo_url"]` 是否存在，选择不同的爬虫：

- **有 repo_url**：调用 [crawl_github_files()](utility-functions.md#crawl_github_files) 通过 GitHub API 或 SSH 克隆抓取
- **无 repo_url（有 local_dir）**：调用 [crawl_local_files()](utility-functions.md#crawl_local_files) 遍历本地目录

**返回值**：`files_list` —— `[(path, content), ...]` 元组列表，即文件名到源码内容的映射转换后的列表。

**异常**：若抓取到 0 个文件，抛出 `ValueError("Failed to fetch files")`。

### post(shared, prep_res, exec_res)

将文件列表写入 `shared["files"]`。

**写入的 shared 键**：
- `files`：`[(path, content), ...]` 元组列表

## 输入输出示例

**输入**（shared 字典初始状态）：
```python
shared = {
    "repo_url": "https://github.com/pallets/flask",
    "project_name": None,
    "github_token": None,
    "include_patterns": {"*.py"},
    "exclude_patterns": {"tests/*", "docs/*"},
    "max_file_size": 100000,
}
```

**输出**（执行后 shared 中新增的键）：
```python
shared["project_name"] = "flask"  # 自动推导
shared["files"] = [
    ("src/flask/app.py", "import os\n..."),
    ("src/flask/request.py", "..."),
    # ...
]
```

## 依赖的工具函数

- [crawl_github_files()](utility-functions.md#crawl_github_files) — GitHub 仓库文件爬取
- [crawl_local_files()](utility-functions.md#crawl_local_files) — 本地目录文件遍历

## 源码位置

nodes.py#L22-L82
